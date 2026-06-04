"""Async Neo4j driver and schema management."""

import structlog
from neo4j import AsyncGraphDatabase

from app.config import settings

logger = structlog.get_logger()

_driver = None


async def get_driver():
    global _driver
    if _driver is None:
        _driver = AsyncGraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    return _driver


async def close_driver():
    global _driver
    if _driver:
        await _driver.close()
        _driver = None


SCHEMA_CYPHER = """
// Unique constraints
CREATE CONSTRAINT book_title IF NOT EXISTS
FOR (b:Book) REQUIRE b.title IS UNIQUE;

CREATE CONSTRAINT verse_ref IF NOT EXISTS
FOR (v:Verse) REQUIRE v.ref IS UNIQUE;

CREATE CONSTRAINT chapter_ref IF NOT EXISTS
FOR (c:Chapter) REQUIRE c.ref IS UNIQUE;

// Full-text indexes
CREATE FULLTEXT INDEX verseHebrewText IF NOT EXISTS
FOR (v:Verse) ON EACH [v.text_hebrew];

CREATE FULLTEXT INDEX verseEnglishText IF NOT EXISTS
FOR (v:Verse) ON EACH [v.text_english];

CREATE FULLTEXT INDEX bookTitle IF NOT EXISTS
FOR (b:Book) ON EACH [b.title, b.hebrew_title];
"""


async def init_schema():
    """Run idempotent schema initialization on startup."""
    driver = await get_driver()
    async with driver.session() as session:
        for statement in SCHEMA_CYPHER.split(";"):
            stmt = statement.strip()
            if stmt:
                try:
                    await session.run(stmt)
                    logger.info("neo4j_schema_executed", statement=stmt[:60])
                except Exception as e:
                    logger.warning("neo4j_schema_statement_failed", error=str(e), statement=stmt[:60])
    logger.info("neo4j_schema_init_complete")


async def check_health() -> dict:
    driver = await get_driver()
    try:
        async with driver.session() as session:
            result = await session.run("RETURN 1 AS ok")
            record = await result.single()
            return {"status": "ok", "latency_ms": 0}
    except Exception as e:
        return {"status": "error", "error": str(e)}
