"""WebSocket real-time updates for collaborative graph editing and live notifications."""

import asyncio
import json
from typing import Dict, Set
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import BaseModel
import structlog

logger = structlog.get_logger()
router = APIRouter(tags=["realtime"])

# Connection manager for multiple clients
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.room_subscribers: Dict[str, Set[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info("websocket_connected", client_id=client_id)

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        for room in self.room_subscribers.values():
            room.discard(client_id)
        logger.info("websocket_disconnected", client_id=client_id)

    async def send_personal_message(self, message: dict, client_id: str):
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_json(message)

    async def broadcast(self, message: dict, room: str = "global"):
        """Broadcast to all clients in a room."""
        if room == "global":
            targets = list(self.active_connections.values())
        else:
            targets = [
                self.active_connections[cid]
                for cid in self.room_subscribers.get(room, set())
                if cid in self.active_connections
            ]

        if not targets:
            return

        # Send concurrently
        await asyncio.gather(
            *[ws.send_json(message) for ws in targets],
            return_exceptions=True
        )

    async def join_room(self, client_id: str, room: str):
        if room not in self.room_subscribers:
            self.room_subscribers[room] = set()
        self.room_subscribers[room].add(client_id)

    async def leave_room(self, client_id: str, room: str):
        if room in self.room_subscribers:
            self.room_subscribers[room].discard(client_id)

manager = ConnectionManager()

class GraphUpdateEvent(BaseModel):
    event_type: str  # "node_created", "node_updated", "rel_created", "rel_deleted"
    node_id: str | None = None
    relationship_id: str | None = None
    data: dict | None = None
    user_id: str | None = None
    timestamp: str | None = None

@router.websocket("/ws/graph/{client_id}")
async def graph_websocket(websocket: WebSocket, client_id: str):
    """WebSocket for real-time graph collaboration."""
    await manager.connect(websocket, client_id)

    try:
        while True:
            data = await websocket.receive_json()
            action = data.get("action")

            if action == "ping":
                await websocket.send_json({"action": "pong", "timestamp": data.get("timestamp")})

            elif action == "join_room":
                room = data.get("room", "global")
                await manager.join_room(client_id, room)
                await websocket.send_json({"action": "joined", "room": room})

            elif action == "leave_room":
                room = data.get("room", "global")
                await manager.leave_room(client_id, room)
                await websocket.send_json({"action": "left", "room": room})

            elif action == "subscribe_graph":
                node_id = data.get("node_id")
                await manager.join_room(client_id, f"node:{node_id}")
                await websocket.send_json({"action": "subscribed", "node_id": node_id})

            elif action == "cursor_position":
                # Broadcast cursor position to room (collaborative cursors)
                room = data.get("room", "global")
                await manager.broadcast({
                    "action": "cursor_update",
                    "client_id": client_id,
                    "x": data.get("x"),
                    "y": data.get("y"),
                    "room": room,
                }, room=room)

            elif action == "graph_update":
                # Broadcast graph change to all subscribers
                event = data.get("event", {})
                room = data.get("room", "global")
                await manager.broadcast({
                    "action": "graph_updated",
                    "event": event,
                    "by_client": client_id,
                }, room=room)

            elif action == "search_request":
                # Real-time search streaming
                query = data.get("query", "")
                # Trigger search and stream results
                pass  # Implementation would stream results

    except WebSocketDisconnect:
        manager.disconnect(client_id)
    except Exception as e:
        logger.error("websocket_error", client_id=client_id, error=str(e))
        manager.disconnect(client_id)


async def broadcast_graph_update(event: GraphUpdateEvent):
    """Helper to broadcast graph updates from backend events."""
    message = {
        "action": "graph_updated",
        "event": event.model_dump(),
    }

    # Broadcast to global
    await manager.broadcast(message, room="global")

    # Also broadcast to specific node room if applicable
    if event.node_id:
        await manager.broadcast(message, room=f"node:{event.node_id}")


async def broadcast_notification(title: str, message: str, level: str = "info"):
    """Broadcast system notification to all connected clients."""
    await manager.broadcast({
        "action": "notification",
        "data": {
            "title": title,
            "message": message,
            "level": level,  # info, warning, error, success
            "timestamp": asyncio.get_event_loop().time(),
        },
    }, room="global")
