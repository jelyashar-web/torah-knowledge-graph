"use client";

import { useCallback, useEffect, useState } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Node,
  Edge,
  useNodesState,
  useEdgesState,
  Panel,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { Book, Scroll, Users, MapPin, Lightbulb, Scale } from "lucide-react";

const NODE_TYPES = {
  Book: { icon: Book, color: "#3b82f6" },
  Chapter: { icon: Scroll, color: "#6366f1" },
  Verse: { icon: Scroll, color: "#8b5cf6" },
  Person: { icon: Users, color: "#22c55e" },
  Place: { icon: MapPin, color: "#f59e0b" },
  Concept: { icon: Lightbulb, color: "#ec4899" },
  Mitzvah: { icon: Scale, color: "#ef4444" },
  TextUnit: { icon: Scroll, color: "#14b8a6" },
};

interface GraphViewProps {
  initialNodes?: Node[];
  initialEdges?: Edge[];
}

export function GraphView({ initialNodes, initialEdges }: GraphViewProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });

  // Build demo graph if no initial data
  useEffect(() => {
    if (initialNodes?.length) {
      setNodes(initialNodes);
      setEdges(initialEdges || []);
      setStats({ nodes: initialNodes.length, edges: initialEdges?.length || 0 });
      return;
    }

    // Demo: Genesis 1:1-3 subgraph
    const demoNodes: Node[] = [
      {
        id: "genesis",
        type: "default",
        position: { x: 0, y: 0 },
        data: { label: "בראשית", type: "Book", ref: "Genesis" },
        style: {
          background: NODE_TYPES.Book.color,
          color: "white",
          borderRadius: "12px",
          padding: "10px 20px",
          fontWeight: "bold",
          fontSize: "16px",
        },
      },
      {
        id: "gen-1",
        type: "default",
        position: { x: -100, y: 120 },
        data: { label: "פרק א", type: "Chapter", ref: "Genesis 1" },
        style: {
          background: NODE_TYPES.Chapter.color,
          color: "white",
          borderRadius: "8px",
          padding: "8px 16px",
        },
      },
      {
        id: "gen-1-1",
        type: "default",
        position: { x: -200, y: 240 },
        data: { label: "א:א", type: "Verse", ref: "Genesis 1:1" },
        style: {
          background: NODE_TYPES.Verse.color,
          color: "white",
          borderRadius: "6px",
          padding: "6px 12px",
          fontSize: "13px",
        },
      },
      {
        id: "gen-1-2",
        type: "default",
        position: { x: 0, y: 240 },
        data: { label: "א:ב", type: "Verse", ref: "Genesis 1:2" },
        style: {
          background: NODE_TYPES.Verse.color,
          color: "white",
          borderRadius: "6px",
          padding: "6px 12px",
          fontSize: "13px",
        },
      },
      {
        id: "gen-1-3",
        type: "default",
        position: { x: 200, y: 240 },
        data: { label: "א:ג", type: "Verse", ref: "Genesis 1:3" },
        style: {
          background: NODE_TYPES.Verse.color,
          color: "white",
          borderRadius: "6px",
          padding: "6px 12px",
          fontSize: "13px",
        },
      },
      {
        id: "elohim",
        type: "default",
        position: { x: 300, y: 0 },
        data: { label: "אלהים", type: "Concept", ref: "God" },
        style: {
          background: NODE_TYPES.Concept.color,
          color: "white",
          borderRadius: "12px",
          padding: "10px 20px",
          fontWeight: "bold",
        },
      },
    ];

    const demoEdges: Edge[] = [
      { id: "e1", source: "genesis", target: "gen-1", label: "PART_OF", animated: true },
      { id: "e2", source: "gen-1", target: "gen-1-1", label: "PART_OF" },
      { id: "e3", source: "gen-1", target: "gen-1-2", label: "PART_OF" },
      { id: "e4", source: "gen-1", target: "gen-1-3", label: "PART_OF" },
      { id: "e5", source: "gen-1-1", target: "elohim", label: "MENTIONS", animated: true },
      { id: "e6", source: "gen-1-1", target: "gen-1-2", label: "NEXT" },
      { id: "e7", source: "gen-1-2", target: "gen-1-3", label: "NEXT" },
    ];

    setNodes(demoNodes);
    setEdges(demoEdges);
    setStats({ nodes: demoNodes.length, edges: demoEdges.length });
  }, [initialNodes, initialEdges]);

  const onNodeClick = useCallback((_: React.MouseEvent, node: Node) => {
    console.log("Clicked:", node.data);
  }, []);

  return (
    <div className="h-[600px] w-full rounded-xl border border-slate-200 dark:border-slate-700 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onNodeClick={onNodeClick}
        fitView
        attributionPosition="bottom-left"
      >
        <Background gap={12} size={1} />
        <Controls />
        <MiniMap nodeStrokeWidth={3} />
        <Panel position="top-right" className="bg-white/90 dark:bg-slate-900/90 p-3 rounded-lg shadow-lg">
          <div className="text-xs space-y-1">
            <div className="font-semibold">Nodes: {stats.nodes}</div>
            <div className="font-semibold">Edges: {stats.edges}</div>
            <div className="mt-2 space-y-1">
              {Object.entries(NODE_TYPES).map(([type, { color }]) => (
                <div key={type} className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: color }} />
                  <span>{type}</span>
                </div>
              ))}
            </div>
          </div>
        </Panel>
      </ReactFlow>
    </div>
  );
}
