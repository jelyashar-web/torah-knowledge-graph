#!/usr/bin/env python3
"""
Neo4j MCP Server for Torah Knowledge Graph.

Exposes Neo4j graph queries as MCP tools for LLM investigation.
Supports stdio transport for Claude Desktop, Cursor, and other MCP clients.

Tools:
  - search_verses: Full-text Hebrew/English verse search
  - get_verse_context: Get surrounding verses
  - get_book_structure: Get Book → Chapter → Verse tree
  - query_graph: Run arbitrary Cypher queries (read-only)
  - discover_cross_references: Find semantic connections between texts
  - get_entity_info: Get info about a person/place/concept in the graph

Usage:
    uv run python mcp/neo4j_mcp_server.py
    # Or for Claude Desktop: add to claude_desktop_config.json
"""

import json
import sys

from neo4j import GraphDatabase

NEO4J_URI = "bolt://localhost:7688"
NEO4J_AUTH = ("neo4j", "torah-graph-secure")


def get_driver():
    return GraphDatabase.driver(NEO4J_URI, auth=NEO4J_AUTH)


# ── Tool Implementations ─────────────────────────────────────────

def search_verses(query: str, book: str | None = None, limit: int = 10) -> dict:
    """Search verses using Neo4j full-text index (Hebrew or English)."""
    driver = get_driver()
    with driver.session() as session:
        # Try Hebrew normalized first, then English
        cypher = """
        CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $q) YIELD node, score
        """
        if book:
            cypher += " WHERE node.book = $book"
        cypher += """
        RETURN node.ref AS ref, node.text_hebrew AS text_he,
               node.text_english AS text_en, score
        ORDER BY score DESC LIMIT $limit
        """
        result = session.run(cypher, q=query, book=book, limit=limit)
        rows = [
            {
                "ref": r["ref"],
                "text_hebrew": r["text_he"][:200] + "..." if r["text_he"] and len(r["text_he"]) > 200 else r["text_he"],
                "text_english": r["text_en"][:200] + "..." if r["text_en"] and len(r["text_en"]) > 200 else r["text_en"],
                "score": round(r["score"], 3),
            }
            for r in result
        ]
    driver.close()
    return {"results": rows, "count": len(rows), "query": query}


def get_verse_context(ref: str, window: int = 3) -> dict:
    """Get verses before and after the target verse."""
    driver = get_driver()
    with driver.session() as session:
        # Parse ref
        result = session.run(
            "MATCH (v:Verse {ref: $ref}) RETURN v.book AS book, v.chapter AS chapter, v.verse_number AS vn",
            ref=ref,
        )
        record = result.single()
        if not record:
            return {"error": f"Verse {ref} not found"}

        book = record["book"]
        chapter = record["chapter"]
        vn = record["vn"]

        result = session.run(
            """
            MATCH (v:Verse)
            WHERE v.book = $book AND v.chapter = $chapter
              AND v.verse_number >= $start AND v.verse_number <= $end
            RETURN v.ref AS ref, v.text_hebrew AS text_he, v.verse_number AS vn
            ORDER BY v.verse_number
            """,
            book=book, chapter=chapter, start=max(1, vn - window), end=vn + window,
        )
        verses = [{"ref": r["ref"], "verse_number": r["vn"], "text": r["text_he"][:150]} for r in result]
    driver.close()
    return {"target": ref, "verses": verses}


def get_book_structure(book: str) -> dict:
    """Return Book → Chapters → Verses hierarchy."""
    driver = get_driver()
    with driver.session() as session:
        result = session.run(
            """
            MATCH (b:Book {title: $book})
            OPTIONAL MATCH (c:Chapter)-[:PART_OF]->(b)
            WITH b, c ORDER BY c.number
            RETURN b.title AS title,
                   collect(DISTINCT {number: c.number, ref: c.ref}) AS chapters
            """,
            book=book,
        )
        record = result.single()
        if not record:
            return {"error": f"Book {book} not found"}
    driver.close()
    return {"book": record["title"], "chapters": record["chapters"], "chapter_count": len(record["chapters"])}


def query_graph(cypher: str, parameters: dict | None = None) -> dict:
    """Execute a read-only Cypher query against the graph.

    SAFETY: Only MATCH, CALL, RETURN allowed. No WRITE operations.
    """
    # Safety check
    dangerous = ["CREATE", "DELETE", "REMOVE", "SET", "MERGE", "DROP", "LOAD"]
    upper = cypher.upper()
    for word in dangerous:
        if word in upper:
            return {"error": f"Query rejected: '{word}' is not allowed. Read-only queries only."}

    driver = get_driver()
    with driver.session() as session:
        result = session.run(cypher, parameters or {})
        rows = [dict(r) for r in result]
    driver.close()
    # Truncate long results
    if len(rows) > 50:
        rows = rows[:50]
        truncated = True
    else:
        truncated = False
    return {"results": rows, "count": len(rows), "truncated": truncated}


def discover_cross_references(ref: str, limit: int = 5) -> dict:
    """Find verses that share concepts with the given verse."""
    driver = get_driver()
    with driver.session() as session:
        # Get the verse text and find similar verses by shared words
        result = session.run(
            """
            MATCH (v:Verse {ref: $ref})
            RETURN v.text_hebrew_normalized AS text_norm
            """,
            ref=ref,
        )
        record = result.single()
        if not record:
            return {"error": f"Verse {ref} not found"}

        text_norm = record["text_norm"] or ""
        # Extract key words (3+ chars, not common words)
        words = [w for w in text_norm.split() if len(w) >= 3]
        if not words:
            return {"results": [], "note": "No searchable words found"}

        # Search for verses containing any of these words
        query = " OR ".join(words[:5])  # Top 5 words
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $q) YIELD node, score
            WHERE node.ref <> $ref
            RETURN node.ref AS ref, node.text_hebrew AS text_he, score
            ORDER BY score DESC LIMIT $limit
            """,
            q=query, ref=ref, limit=limit,
        )
        rows = [{"ref": r["ref"], "text_preview": r["text_he"][:120], "score": round(r["score"], 3)} for r in result]
    driver.close()
    return {"source_verse": ref, "cross_references": rows}


def get_entity_info(entity_name: str) -> dict:
    """Get information about an entity (person, place, concept) mentioned in the graph."""
    driver = get_driver()
    with driver.session() as session:
        # Search in verse texts
        result = session.run(
            """
            CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $name) YIELD node, score
            RETURN node.ref AS ref, node.text_hebrew AS text_he, score
            ORDER BY score DESC LIMIT 5
            """,
            name=entity_name,
        )
        mentions = [{"ref": r["ref"], "text_preview": r["text_he"][:120], "score": round(r["score"], 3)} for r in result]

        # Also check Book titles
        result = session.run(
            "MATCH (b:Book) WHERE b.title CONTAINS $name RETURN b.title AS title LIMIT 5",
            name=entity_name,
        )
        books = [r["title"] for r in result]
    driver.close()
    return {
        "entity": entity_name,
        "books": books,
        "mentions_in_verses": mentions,
    }


# ── MCP Protocol Handlers ────────────────────────────────────────

TOOLS = {
    "search_verses": {
        "description": "Search for verses in the Torah graph by Hebrew or English query",
        "parameters": {
            "query": {"type": "string", "description": "Search text (Hebrew or English)"},
            "book": {"type": "string", "description": "Optional: restrict to specific book"},
            "limit": {"type": "integer", "description": "Max results (default 10)"},
        },
    },
    "get_verse_context": {
        "description": "Get verses before and after a target verse (e.g., Genesis 1:1)",
        "parameters": {
            "ref": {"type": "string", "description": "Verse reference like 'Genesis 1:1'"},
            "window": {"type": "integer", "description": "Number of verses on each side (default 3)"},
        },
    },
    "get_book_structure": {
        "description": "Get the chapter structure of a book",
        "parameters": {
            "book": {"type": "string", "description": "Book title e.g. 'Genesis'"},
        },
    },
    "query_graph": {
        "description": "Run a read-only Cypher query against Neo4j",
        "parameters": {
            "cypher": {"type": "string", "description": "Cypher query (read-only: MATCH, RETURN, CALL only)"},
            "parameters": {"type": "object", "description": "Optional query parameters"},
        },
    },
    "discover_cross_references": {
        "description": "Find verses related to a given verse by shared Hebrew words",
        "parameters": {
            "ref": {"type": "string", "description": "Source verse reference"},
            "limit": {"type": "integer", "description": "Max results (default 5)"},
        },
    },
    "get_entity_info": {
        "description": "Get information about a person, place, or concept in the Torah",
        "parameters": {
            "entity_name": {"type": "string", "description": "Entity name in Hebrew or English"},
        },
    },
}


def handle_request(request: dict) -> dict:
    """Route MCP requests to the appropriate tool."""
    method = request.get("method", "")
    params = request.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "torah-neo4j-mcp", "version": "0.1.0"},
            },
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": [
                    {
                        "name": name,
                        "description": spec["description"],
                        "inputSchema": {
                            "type": "object",
                            "properties": spec["parameters"],
                        },
                    }
                    for name, spec in TOOLS.items()
                ],
            },
        }

    if method == "tools/call":
        tool_name = params.get("name", "")
        args = params.get("arguments", {})

        try:
            if tool_name == "search_verses":
                result = search_verses(args.get("query", ""), args.get("book"), args.get("limit", 10))
            elif tool_name == "get_verse_context":
                result = get_verse_context(args.get("ref", ""), args.get("window", 3))
            elif tool_name == "get_book_structure":
                result = get_book_structure(args.get("book", ""))
            elif tool_name == "query_graph":
                result = query_graph(args.get("cypher", ""), args.get("parameters"))
            elif tool_name == "discover_cross_references":
                result = discover_cross_references(args.get("ref", ""), args.get("limit", 5))
            elif tool_name == "get_entity_info":
                result = get_entity_info(args.get("entity_name", ""))
            else:
                result = {"error": f"Unknown tool: {tool_name}"}
        except Exception as e:
            result = {"error": str(e)}

        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
            },
        }

    return {"jsonrpc": "2.0", "id": request.get("id"), "error": {"code": -32601, "message": f"Method not found: {method}"}}


def main():
    print("Torah Neo4j MCP Server starting...", file=sys.stderr)
    print('{"jsonrpc": "2.0", "id": 1, "method": "initialize"}', file=sys.stderr)

    # Test connection
    try:
        driver = get_driver()
        with driver.session() as session:
            result = session.run("RETURN 1 AS ok")
            record = result.single()
            print(f"Neo4j connected: {record['ok']}", file=sys.stderr)
        driver.close()
    except Exception as e:
        print(f"Neo4j connection failed: {e}", file=sys.stderr)
        sys.exit(1)

    print("Ready for MCP requests.", file=sys.stderr)

    # Simple line-based JSON-RPC over stdio
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            response = handle_request(request)
            print(json.dumps(response, ensure_ascii=False))
            sys.stdout.flush()
        except json.JSONDecodeError:
            print(json.dumps({"jsonrpc": "2.0", "error": {"code": -32700, "message": "Parse error"}}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
