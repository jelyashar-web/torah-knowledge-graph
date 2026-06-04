/**
 * API client for Torah Knowledge Graph backend.
 * Supports both FastAPI backend and direct Neo4j fallback.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const NEO4J_HTTP = "http://localhost:7475/db/neo4j/tx/commit";
const NEO4J_USER = "neo4j";
const NEO4J_PASS = "torah-graph-secure";
// ── Interfaces ──────────────────────────────────────────

export interface VerseResult {
  ref: string;
  text_hebrew: string;
  text_english?: string;
  text_hebrew_normalized?: string;
  score?: number;
}

export interface SearchResponse {
  query: string;
  results: VerseResult[];
  count: number;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

// ── Direct Neo4j Query ──────────────────────────────────

async function queryNeo4j(cypher: string, params: Record<string, any> = {}): Promise<any[]> {
  try {
    const res = await fetch(NEO4J_HTTP, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Basic " + btoa(`${NEO4J_USER}:${NEO4J_PASS}`),
      },
      body: JSON.stringify({
        statements: [{ statement: cypher, parameters: params }],
      }),
    });
    if (!res.ok) throw new Error(`Neo4j HTTP ${res.status}`);
    const data = await res.json();
    const rows = data?.results?.[0]?.data || [];
    return rows.map((r: any) => r.row[0]);
  } catch (e) {
    console.warn("Neo4j direct query failed:", e);
    return [];
  }
}

// ── Search (Neo4j Full-Text) ────────────────────────────

export async function searchVerses(
  query: string,
  book?: string,
  limit: number = 20
): Promise<SearchResponse> {
  try {
    // Try FastAPI first
    const params = new URLSearchParams({ q: query, limit: String(limit) });
    if (book) params.set("book", book);
    const res = await fetch(`${API_BASE}/api/v1/search/fulltext?${params}`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) return await res.json();
  } catch {
    // Fallback to Neo4j direct
  }

  // Direct Neo4j full-text search
  const cypher = book
    ? `CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $q) YIELD node, score
       WHERE node.book = $book
       RETURN node {.*, score: score} AS verse LIMIT $limit`
    : `CALL db.index.fulltext.queryNodes('verseHebrewNormalized', $q) YIELD node, score
       RETURN node {.*, score: score} AS verse LIMIT $limit`;

  const rows = await queryNeo4j(cypher, { q: query, book, limit });
  const results = rows.map((r: any) => ({
    ref: r.verse?.ref || r.ref,
    text_hebrew: r.verse?.text_hebrew || r.text_hebrew || "",
    text_english: r.verse?.text_english || r.text_english || "",
    score: r.verse?.score || r.score,
  }));

  return { query, results, count: results.length };
}

// ── Verse Context ──────────────────────────────────────

export async function getVerseContext(ref: string, window: number = 3): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/graph/verses/${encodeURIComponent(ref)}/context`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) return await res.json();
  } catch {}

  // Direct Neo4j
  const cypher = `
    MATCH (v:Verse {ref: $ref})
    WITH v.book AS book, v.chapter AS chapter, v.verse_number AS vn
    MATCH (ctx:Verse)
    WHERE ctx.book = book AND ctx.chapter = chapter
      AND ctx.verse_number >= $start AND ctx.verse_number <= $end
    RETURN ctx {.*} AS verse ORDER BY ctx.verse_number
  `;
  const verses = await queryNeo4j(cypher, { ref, start: Math.max(1, 1), end: 10 });
  return { target: ref, context: verses };
}

// ── Cross References ────────────────────────────────────

export async function getCrossRefs(ref: string, limit: number = 5): Promise<any> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/discover/cross_refs`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ verse_ref: ref, limit }),
      signal: AbortSignal.timeout(5000),
    });
    if (res.ok) return await res.json();
  } catch {}

  // Direct Neo4j: find verses sharing Hebrew words
  const cypher = `
    MATCH (v:Verse {ref: $ref})
    WITH v.text_hebrew_normalized AS text_norm
    CALL db.index.fulltext.queryNodes('verseHebrewNormalized',
      apoc.text.join(apoc.coll.randomItems(split(text_norm, ' '), 3), ' OR ')) YIELD node, score
    WHERE node.ref <> $ref
    RETURN node.ref AS ref, node.text_hebrew AS text_he, score
    ORDER BY score DESC LIMIT $limit
  `;
  const matches = await queryNeo4j(cypher, { ref, limit });
  return { source_ref: ref, matches };
}

// ── List Books ──────────────────────────────────────────

export async function listBooks(): Promise<{ books: any[] }> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/graph/books`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) return await res.json();
  } catch {}

  const cypher = `MATCH (b:Book) WHERE b.corpus = 'Tanakh' RETURN b {.*} AS book ORDER BY b.title`;
  const rows = await queryNeo4j(cypher);
  return { books: rows.map((r: any) => r.book || r) };
}

// ── Book Structure ─────────────────────────────────────

export async function getBookStructure(book: string): Promise<any> {
  const cypher = `
    MATCH (b:Book {title: $book})
    OPTIONAL MATCH (c:Chapter)-[:PART_OF]-(b)
    OPTIONAL MATCH (v:Verse)-[:PART_OF]-(c)
    WITH b, c, collect(v {.*}) AS verses
    RETURN b {.*} AS book, collect(DISTINCT {chapter: c {.*}, verses: verses}) AS chapters
  `;
  const rows = await queryNeo4j(cypher, { book });
  return rows[0] || { book: null, chapters: [] };
}

// ── Ollama Chat ─────────────────────────────────────────

export async function chatWithAI(
  message: string,
  context: string = "",
  provider: "ollama" | "kimi" = "ollama",
  model?: string
): Promise<{ response: string; provider: string }> {
  const systemPrompt = `You are a Torah scholar AI. Answer questions about Jewish texts, Hebrew Bible, and Jewish law. Always cite sources (book, chapter, verse). Answer in Hebrew or English as appropriate. Be thorough and accurate.`;

  const messages: Array<{ role: string; content: string }> = [
    { role: "system", content: systemPrompt },
  ];

  if (context) {
    messages.push({ role: "assistant", content: `Context: ${context}` });
  }
  messages.push({ role: "user", content: message });

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        messages,
        provider,
        model: model || (provider === "kimi" ? "kimi-k2-6" : "llama3.1:8b"),
      }),
      signal: AbortSignal.timeout(provider === "kimi" ? 60000 : 30000),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.error || `HTTP ${res.status}`);
    }

    const data = await res.json();
    return {
      response: data.response || "No response",
      provider: data.provider || provider,
    };
  } catch (e: any) {
    console.error(`${provider} error:`, e);
    return {
      response: `⚠️ ${provider} error: ${e.message}`,
      provider,
    };
  }
}

// Backward compat
export async function chatWithOllama(message: string, context: string = ""): Promise<string> {
  const result = await chatWithAI(message, context, "ollama");
  return result.response;
}

// ── Analytics ───────────────────────────────────────────

export async function getGraphStats(): Promise<any> {
  const cypher = `
    CALL {
      MATCH (v:Verse) RETURN count(v) AS verse_count
    }
    CALL {
      MATCH (c:Chapter) RETURN count(c) AS chapter_count
    }
      MATCH (b:Book) RETURN count(b) AS book_count, verse_count, chapter_count
  `;
  const rows = await queryNeo4j(cypher);
  return rows[0] || {};
}

export async function getCategoryDistribution(): Promise<any[]> {
  const cypher = `
    MATCH (b:Book)
    RETURN b.category AS category, count(b) AS count
    ORDER BY count DESC
  `;
  return await queryNeo4j(cypher);
}
