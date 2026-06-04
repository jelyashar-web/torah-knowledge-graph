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
