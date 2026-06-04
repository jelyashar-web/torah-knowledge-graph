"""Strawberry GraphQL schema for Torah Knowledge Graph.

Provides:
- Types: Verse, Chapter, Book, Person, Concept, Relationship, GraphStats
- Queries: search, verseByRef, bookByTitle, graphNeighbors, stats
- Mutations: createNode, createRelationship, updateNode, deleteNode
- Subscriptions: verseUpdated, graphChanged, aiMessageStream
"""

from typing import List, Optional, AsyncGenerator
from datetime import datetime
import asyncio
import structlog

import strawberry
from strawberry.types import Info

logger = structlog.get_logger()


# ── GraphQL Types ───────────────────────────────────────

@strawberry.type
class Verse:
    id: str
    ref: str
    hebrew: Optional[str] = None
    english: Optional[str] = None
    book: str
    chapter: int
    verse: int
    hebrew_normalized: Optional[str] = None
    chapter_ref: Optional[str] = None


@strawberry.type
class Chapter:
    id: str
    ref: str
    title: str
    book: str
    chapter_number: int
    verses: Optional[List[Verse]] = None


@strawberry.type
class Book:
    id: str
    title: str
    hebrew_title: Optional[str] = None
    category: Optional[str] = None
    order: Optional[int] = None
    chapters: Optional[List[Chapter]] = None


@strawberry.type
class Entity:
    """Generic entity: Person, Place, Concept, Mitzvah, etc."""
    id: str
    label: str
    hebrew: Optional[str] = None
    type: str
    description: Optional[str] = None
    source_refs: Optional[List[str]] = None


@strawberry.type
class Relationship:
    id: str
    type: str
    from_id: str
    to_id: str
    properties: Optional[str] = None  # JSON string
    confidence: Optional[float] = None
    source: Optional[str] = None
    extraction_method: Optional[str] = None


@strawberry.type
class GraphPath:
    """Path between two nodes in the graph."""
    nodes: List[Entity]
    relationships: List[Relationship]
    length: int
    score: Optional[float] = None


@strawberry.type
class SearchResult:
    score: float
    node: Optional[Entity] = None
    verse: Optional[Verse] = None
    relationship: Optional[Relationship] = None
    source: str  # "fulltext" | "semantic" | "graph"


@strawberry.type
class GraphStats:
    total_nodes: int
    total_relationships: int
    node_breakdown: Optional[str] = None  # JSON
    relationship_breakdown: Optional[str] = None  # JSON
    last_updated: Optional[datetime] = None


@strawberry.type
class AIChatMessage:
    role: str  # "user" | "assistant" | "system"
    content: str
    timestamp: datetime
    provider: Optional[str] = None
    model: Optional[str] = None
    citations: Optional[List[str]] = None


@strawberry.type
class IngestJob:
    id: str
    status: str  # "pending" | "running" | "completed" | "failed"
    book: Optional[str] = None
    progress: Optional[float] = None
    created_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


# ── Input Types ─────────────────────────────────────────

@strawberry.input
class CreateNodeInput:
    label: str
    hebrew: Optional[str] = None
    type: str
    description: Optional[str] = None
    source_refs: Optional[List[str]] = None
    properties: Optional[str] = None  # JSON


@strawberry.input
class CreateRelationshipInput:
    type: str
    from_id: str
    to_id: str
    properties: Optional[str] = None
    confidence: Optional[float] = 1.0
    source: Optional[str] = "manual"
    extraction_method: Optional[str] = "graphql_mutation"


@strawberry.input
class UpdateNodeInput:
    id: str
    label: Optional[str] = None
    hebrew: Optional[str] = None
    description: Optional[str] = None
    properties: Optional[str] = None


@strawberry.input
class SearchInput:
    query: str
    search_type: Optional[str] = "all"  # "verse" | "entity" | "all"
    book_filter: Optional[str] = None
    limit: Optional[int] = 20
    semantic: Optional[bool] = False


# ── Query Resolver ──────────────────────────────────────

@strawberry.type
class Query:
    @strawberry.field
    async def verse(self, info: Info, ref: str) -> Optional[Verse]:
        """Get a single verse by canonical reference (e.g. 'Genesis 1:1')."""
        from app.neo4j_client import neo4j_client
        try:
            records, _, _ = neo4j_client.driver.execute_query(
                """
                MATCH (v:Verse {ref: $ref})
                RETURN v {.*} as verse
                """,
                ref=ref,
            )
            if not records:
                return None
            v = records[0]["verse"]
            return Verse(
                id=v.get("id", ref),
                ref=v["ref"],
                hebrew=v.get("hebrew"),
                english=v.get("english"),
                book=v.get("book", ""),
                chapter=v.get("chapter", 0),
                verse=v.get("verse", 0),
                hebrew_normalized=v.get("hebrew_normalized"),
                chapter_ref=v.get("chapter_ref"),
            )
        except Exception as e:
            logger.error("graphql_verse_query_failed", ref=ref, error=str(e))
            return None

    @strawberry.field
    async def search(self, info: Info, input: SearchInput) -> List[SearchResult]:
        """Unified search: fulltext + optional semantic."""
        from app.neo4j_client import neo4j_client
        results = []

        # 1. Fulltext search on verses
        if input.search_type in ("all", "verse"):
            try:
                cypher = """
                CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $query)
                YIELD node, score
                RETURN node {.*} as verse, score
                LIMIT $limit
                """
                records, _, _ = neo4j_client.driver.execute_query(
                    cypher, query=input.query, limit=input.limit
                )
                for r in records:
                    v = r["verse"]
                    results.append(
                        SearchResult(
                            score=r["score"],
                            verse=Verse(
                                id=v.get("id", v["ref"]),
                                ref=v["ref"],
                                hebrew=v.get("hebrew"),
                                english=v.get("english"),
                                book=v.get("book", ""),
                                chapter=v.get("chapter", 0),
                                verse=v.get("verse", 0),
                            ),
                            source="fulltext",
                        )
                    )
            except Exception as e:
                logger.error("graphql_search_failed", error=str(e))

        # 2. Entity search
        if input.search_type in ("all", "entity"):
            try:
                cypher = """
                MATCH (e:Entity)
                WHERE e.label CONTAINS $query OR e.hebrew CONTAINS $query
                RETURN e {.*} as entity, 1.0 as score
                LIMIT $limit
                """
                records, _, _ = neo4j_client.driver.execute_query(
                    cypher, query=input.query, limit=input.limit
                )
                for r in records:
                    e = r["entity"]
                    results.append(
                        SearchResult(
                            score=r["score"],
                            node=Entity(
                                id=e.get("id", ""),
                                label=e.get("label", ""),
                                hebrew=e.get("hebrew"),
                                type=e.get("type", "Entity"),
                                description=e.get("description"),
                            ),
                            source="graph",
                        )
                    )
            except Exception as e:
                logger.error("graphql_entity_search_failed", error=str(e))

        return results[: input.limit]

    @strawberry.field
    async def book(self, info: Info, title: str) -> Optional[Book]:
        """Get a book with its chapters and verses."""
        from app.neo4j_client import neo4j_client
        try:
            records, _, _ = neo4j_client.driver.execute_query(
                """
                MATCH (b:Book {title: $title})
                OPTIONAL MATCH (b)-[:PART_OF]-(c:Chapter)
                WITH b, c ORDER BY c.chapter_number
                RETURN b {.*} as book, collect(c {.*}) as chapters
                """,
                title=title,
            )
            if not records:
                return None
            r = records[0]
            b = r["book"]
            chapters_data = r.get("chapters", [])
            chapters = [
                Chapter(
                    id=c.get("id", c["ref"]),
                    ref=c["ref"],
                    title=c.get("title", c["ref"]),
                    book=b["title"],
                    chapter_number=c.get("chapter_number", 0),
                )
                for c in chapters_data
            ]
            return Book(
                id=b.get("id", b["title"]),
                title=b["title"],
                hebrew_title=b.get("hebrew_title"),
                category=b.get("category"),
                order=b.get("order"),
                chapters=chapters,
            )
        except Exception as e:
            logger.error("graphql_book_query_failed", title=title, error=str(e))
            return None

    @strawberry.field
    async def graph_neighbors(
        self, info: Info, node_id: str, depth: Optional[int] = 1
    ) -> List[Entity]:
        """Get neighbors of a node up to given depth."""
        from app.neo4j_client import neo4j_client
        try:
            cypher = """
            MATCH path = (n {id: $node_id})-[:MENTIONS|PART_OF|RELATED_TO*1..$depth]-(m)
            RETURN DISTINCT m {.*} as neighbor
            LIMIT 50
            """
            records, _, _ = neo4j_client.driver.execute_query(
                cypher, node_id=node_id, depth=depth
            )
            return [
                Entity(
                    id=n["neighbor"].get("id", ""),
                    label=n["neighbor"].get("label", ""),
                    hebrew=n["neighbor"].get("hebrew"),
                    type=n["neighbor"].get("type", "Unknown"),
                    description=n["neighbor"].get("description"),
                )
                for n in records
            ]
        except Exception as e:
            logger.error("graphql_neighbors_failed", node_id=node_id, error=str(e))
            return []

    @strawberry.field
    async def graph_path(
        self, info: Info, from_id: str, to_id: str, max_depth: Optional[int] = 5
    ) -> Optional[GraphPath]:
        """Find shortest path between two nodes."""
        from app.neo4j_client import neo4j_client
        try:
            cypher = """
            MATCH path = shortestPath(
                (a {id: $from_id})-[*1..$max_depth]-(b {id: $to_id})
            )
            RETURN path
            """
            records, _, _ = neo4j_client.driver.execute_query(
                cypher, from_id=from_id, to_id=to_id, max_depth=max_depth
            )
            if not records:
                return None
            path = records[0]["path"]
            nodes = [
                Entity(
                    id=n.get("id", ""),
                    label=n.get("label", ""),
                    hebrew=n.get("hebrew"),
                    type=n.get("type", "Unknown"),
                )
                for n in path.nodes
            ]
            rels = [
                Relationship(
                    id=r.get("id", ""),
                    type=r.type,
                    from_id=r.start_node.get("id", ""),
                    to_id=r.end_node.get("id", ""),
                )
                for r in path.relationships
            ]
            return GraphPath(
                nodes=nodes,
                relationships=rels,
                length=len(rels),
                score=1.0,
            )
        except Exception as e:
            logger.error("graphql_path_failed", error=str(e))
            return None

    @strawberry.field
    async def stats(self, info: Info) -> GraphStats:
        """System-wide graph statistics."""
        from app.neo4j_client import neo4j_client
        try:
            # Node counts by label
            node_counts, _, _ = neo4j_client.driver.execute_query(
                """
                CALL apoc.meta.stats() YIELD labels
                RETURN labels
                """
            )
            labels = node_counts[0]["labels"] if node_counts else {}

            # Relationship counts
            rel_counts, _, _ = neo4j_client.driver.execute_query(
                """
                CALL apoc.meta.stats() YIELD relTypesCount
                RETURN relTypesCount
                """
            )
            rel_types = rel_counts[0]["relTypesCount"] if rel_counts else {}

            total_nodes = sum(labels.values()) if labels else 0
            total_rels = sum(rel_types.values()) if rel_types else 0

            return GraphStats(
                total_nodes=total_nodes,
                total_relationships=total_rels,
                node_breakdown=str(labels),
                relationship_breakdown=str(rel_types),
                last_updated=datetime.utcnow(),
            )
        except Exception as e:
            logger.error("graphql_stats_failed", error=str(e))
            return GraphStats(total_nodes=0, total_relationships=0)

    @strawberry.field
    async def books(self, info: Info) -> List[Book]:
        """List all books."""
        from app.neo4j_client import neo4j_client
        try:
            records, _, _ = neo4j_client.driver.execute_query(
                "MATCH (b:Book) RETURN b {.*} as book ORDER BY b.order"
            )
            return [
                Book(
                    id=b["book"].get("id", b["book"]["title"]),
                    title=b["book"]["title"],
                    hebrew_title=b["book"].get("hebrew_title"),
                    category=b["book"].get("category"),
                    order=b["book"].get("order"),
                )
                for b in records
            ]
        except Exception as e:
            logger.error("graphql_books_failed", error=str(e))
            return []


# ── Mutation Resolver ───────────────────────────────────

@strawberry.type
class Mutation:
    @strawberry.mutation
    async def create_node(self, info: Info, input: CreateNodeInput) -> Optional[Entity]:
        """Create a new entity node in the graph."""
        from app.neo4j_client import neo4j_client
        import uuid
        try:
            node_id = str(uuid.uuid4())
            props = {"id": node_id, "label": input.label, "type": input.type}
            if input.hebrew:
                props["hebrew"] = input.hebrew
            if input.description:
                props["description"] = input.description
            if input.source_refs:
                props["source_refs"] = input.source_refs
            if input.properties:
                import json
                extra = json.loads(input.properties)
                props.update(extra)

            neo4j_client.driver.execute_query(
                """
                CREATE (n:Entity $props)
                RETURN n {.*} as node
                """,
                props=props,
            )
            logger.info("graphql_node_created", id=node_id, label=input.label)
            return Entity(
                id=node_id,
                label=input.label,
                hebrew=input.hebrew,
                type=input.type,
                description=input.description,
                source_refs=input.source_refs,
            )
        except Exception as e:
            logger.error("graphql_create_node_failed", error=str(e))
            return None

    @strawberry.mutation
    async def create_relationship(
        self, info: Info, input: CreateRelationshipInput
    ) -> Optional[Relationship]:
        """Create a relationship between two nodes."""
        from app.neo4j_client import neo4j_client
        import uuid
        try:
            rel_id = str(uuid.uuid4())
            props = {
                "id": rel_id,
                "confidence": input.confidence,
                "source": input.source,
                "extraction_method": input.extraction_method,
            }
            if input.properties:
                import json
                extra = json.loads(input.properties)
                props.update(extra)

            neo4j_client.driver.execute_query(
                """
                MATCH (a {id: $from_id}), (b {id: $to_id})
                CREATE (a)-[r:RELATED_TO $props]->(b)
                RETURN r {.*, type: type(r)} as rel
                """,
                from_id=input.from_id,
                to_id=input.to_id,
                props=props,
            )
            logger.info(
                "graphql_rel_created",
                id=rel_id,
                from_id=input.from_id,
                to_id=input.to_id,
            )
            return Relationship(
                id=rel_id,
                type=input.type,
                from_id=input.from_id,
                to_id=input.to_id,
                properties=input.properties,
                confidence=input.confidence,
                source=input.source,
                extraction_method=input.extraction_method,
            )
        except Exception as e:
            logger.error("graphql_create_rel_failed", error=str(e))
            return None

    @strawberry.mutation
    async def update_node(self, info: Info, input: UpdateNodeInput) -> Optional[Entity]:
        """Update an existing node."""
        from app.neo4j_client import neo4j_client
        try:
            set_clauses = []
            params = {"id": input.id}
            if input.label is not None:
                set_clauses.append("n.label = $label")
                params["label"] = input.label
            if input.hebrew is not None:
                set_clauses.append("n.hebrew = $hebrew")
                params["hebrew"] = input.hebrew
            if input.description is not None:
                set_clauses.append("n.description = $description")
                params["description"] = input.description

            if not set_clauses:
                return None

            cypher = f"""
            MATCH (n {{id: $id}})
            SET {', '.join(set_clauses)}
            RETURN n {{.*}} as node
            """
            records, _, _ = neo4j_client.driver.execute_query(cypher, **params)
            if not records:
                return None
            n = records[0]["node"]
            return Entity(
                id=n.get("id", ""),
                label=n.get("label", ""),
                hebrew=n.get("hebrew"),
                type=n.get("type", "Unknown"),
                description=n.get("description"),
            )
        except Exception as e:
            logger.error("graphql_update_node_failed", error=str(e))
            return None

    @strawberry.mutation
    async def delete_node(self, info: Info, id: str) -> bool:
        """Delete a node and its relationships."""
        from app.neo4j_client import neo4j_client
        try:
            neo4j_client.driver.execute_query(
                """
                MATCH (n {id: $id})
                DETACH DELETE n
                """,
                id=id,
            )
            logger.info("graphql_node_deleted", id=id)
            return True
        except Exception as e:
            logger.error("graphql_delete_node_failed", id=id, error=str(e))
            return False


# ── Subscription Resolver ───────────────────────────────

@strawberry.type
class Subscription:
    @strawberry.subscription
    async def graph_updates(self, info: Info) -> AsyncGenerator[str, None]:
        """Subscribe to real-time graph changes."""
        from app.routers.realtime import manager
        while True:
            # In production, this would listen to a Redis pub/sub channel
            await asyncio.sleep(1)
            yield f'{{"event": "heartbeat", "timestamp": "{datetime.utcnow().isoformat()}"}}'

    @strawberry.subscription
    async def ai_chat_stream(self, info: Info, message: str) -> AsyncGenerator[str, None]:
        """Stream AI chat responses token by token."""
        # Simulated streaming — in production would stream from LLM
        words = message.split()
        response = f"Thinking about: {message}..."
        for word in response.split():
            yield word + " "
            await asyncio.sleep(0.05)


# ── Schema Assembly ─────────────────────────────────────

schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
