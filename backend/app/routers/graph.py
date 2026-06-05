"""Graph traversal API for Book / Chapter / Verse hierarchy."""

from fastapi import APIRouter, HTTPException

from app.neo4j_client import get_driver

router = APIRouter(prefix="/api/v1/graph", tags=["graph"])


@router.get("/books")
async def list_books():
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            "MATCH (b:Book) RETURN b {.*} AS book ORDER BY b.title"
        )
        records = [record.data() async for record in result]
    return {"books": [r["book"] for r in records]}


@router.get("/books/{book}/chapters")
async def book_chapters(book: str):
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (b:Book {title: $book})
            MATCH (c:Chapter)-[:PART_OF]->(b)
            OPTIONAL MATCH (v:Verse)-[:PART_OF]->(c)
            WITH c, count(v) AS verse_count
            RETURN c {.*} AS chapter, verse_count
            ORDER BY c.number
            """,
            book=book,
        )
        records = [record.data() async for record in result]
    return {"book": book, "chapters": records}


@router.get("/verses/{verse_id}/context")
async def verse_context(verse_id: str):
    """Return 3 verses before and 3 verses after the given verse."""
    driver = await get_driver()
    async with driver.session() as session:
        # Get the target verse details
        target_result = await session.run(
            "MATCH (v:Verse {id: $id}) RETURN v.book AS book, v.chapter AS chapter, v.verse_number AS vn",
            id=verse_id,
        )
        target = await target_result.single()
        if not target:
            raise HTTPException(status_code=404, detail="Verse not found")

        book = target["book"]
        chapter = target["chapter"]
        vn = target["vn"]

        result = await session.run(
            """
            MATCH (v:Verse)
            WHERE v.book = $book AND v.chapter = $chapter
              AND v.verse_number >= $start AND v.verse_number <= $end
            RETURN v {.*} AS verse
            ORDER BY v.verse_number
            """,
            book=book,
            chapter=chapter,
            start=max(1, vn - 3),
            end=vn + 3,
        )
        records = [record.data() async for record in result]

    return {
        "target_verse_id": verse_id,
        "context": [r["verse"] for r in records],
    }


@router.get("/books/{book}/structure")
async def book_structure(book: str):
    """Return nested Book → Chapters → Verses tree."""
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (b:Book {title: $book})
            OPTIONAL MATCH (c:Chapter)-[:PART_OF]->(b)
            OPTIONAL MATCH (v:Verse)-[:PART_OF]->(c)
            WITH b, c, collect(v {.*}) AS verses
            RETURN b {.*} AS book,
                   collect(DISTINCT {
                     chapter: c {.*},
                     verses: verses
                   }) AS chapters
            """,
            book=book,
        )
        record = await result.single()
        if not record or not record["book"]:
            raise HTTPException(status_code=404, detail="Book not found")

    return {"book": record["book"], "chapters": record["chapters"]}


@router.get("/people")
async def list_people():
    """Return all Torah people (Person nodes)."""
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (p:Person)
            OPTIONAL MATCH (p)<-[:MENTIONS]-(v:Verse)
            WITH p, count(v) AS verse_count
            RETURN p {.*} AS person, verse_count
            ORDER BY p.name
            """
        )
        records = [record.data() async for record in result]
    return {"people": [{**r["person"], "verses": r["verse_count"]} for r in records]}


@router.get("/people/{person_ref}")
async def get_person(person_ref: str):
    """Get single person with relationships."""
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (p:Person {ref: $ref})
            OPTIONAL MATCH (p)<-[:MENTIONS]-(v:Verse)
            WITH p, count(v) AS verse_count, collect(v.ref)[0..5] AS verse_refs
            OPTIONAL MATCH (p)-[r]-(other:Person)
            WITH p, verse_count, verse_refs, collect({type: type(r), person: other {.*}})[0..10] AS relations
            RETURN p {.*} AS person, verse_count, verse_refs, relations
            """,
            ref=person_ref,
        )
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Person not found")
    return {
        **record["person"],
        "verses": record["verse_count"],
        "verse_refs": record["verse_refs"],
        "relations": record["relations"],
    }


@router.get("/subgraph")
async def get_subgraph(
    center_ref: str = "Genesis 1:1",
    depth: int = 2,
    limit: int = 100,
):
    """Return a subgraph around a central node (verse ref or person ref)."""
    driver = await get_driver()
    async with driver.session() as session:
        # Try Verse first, then Person
        result = await session.run(
            """
            MATCH path = (center)-[r*1..$depth]-(neighbor)
            WHERE (center:Verse AND center.ref = $ref)
               OR (center:Person AND center.ref = $ref)
               OR (center:Person AND center.name = $ref)
            WITH center, neighbor, r, path
            LIMIT $limit
            RETURN DISTINCT
                center {.*, label: center.ref, type: labels(center)[0]} AS center_node,
                neighbor {.*, label: COALESCE(neighbor.ref, neighbor.name, neighbor.title), type: labels(neighbor)[0]} AS neighbor_node,
                [rel IN r | {type: type(rel), from: startNode(rel).ref, to: endNode(rel).ref}] AS rels
            """,
            ref=center_ref,
            depth=depth,
            limit=limit,
        )
        records = [record.data() async for record in result]

    nodes = {}
    edges = []
    for r in records:
        c = r["center_node"]
        n = r["neighbor_node"]
        for node in [c, n]:
            if node and node.get("ref") and node["ref"] not in nodes:
                nodes[node["ref"]] = {
                    "id": node.get("ref", node.get("name", "")),
                    "label": node.get("label", ""),
                    "type": node.get("type", "Unknown"),
                    **{k: v for k, v in node.items() if k not in ["label", "type", "ref"]},
                }
        for rel in r.get("rels", []):
            edges.append(rel)

    return {
        "center": center_ref,
        "depth": depth,
        "nodes": list(nodes.values()),
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
    }


@router.get("/neighbors/{node_id}")
async def get_neighbors(node_id: str, depth: int = 1, limit: int = 50):
    """Get neighbors of any node by ID (ref)."""
    driver = await get_driver()
    async with driver.session() as session:
        result = await session.run(
            """
            MATCH (n)
            WHERE n.ref = $id OR n.name = $id
            MATCH path = (n)-[r*1..$depth]-(m)
            WHERE n <> m
            RETURN DISTINCT m {.*, label: COALESCE(m.ref, m.name, m.title), type: labels(m)[0]} AS neighbor,
                   [rel IN r | type(rel)] AS rel_types
            LIMIT $limit
            """,
            id=node_id,
            depth=depth,
            limit=limit,
        )
        records = [record.data() async for record in result]
    return {"node_id": node_id, "neighbors": records}
