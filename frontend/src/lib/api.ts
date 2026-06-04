/**
 * API client for Torah Knowledge Graph backend.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8002";

export interface VerseResult {
  ref: string;
  text_hebrew: string;
  text_english?: string;
  text_hebrew_normalized?: string;
  score?: number;
}

export interface Book {
  title: string;
  hebrew_title?: string;
  category?: string;
}

export interface Chapter {
  chapter: {
    ref: string;
    number: number;
    book: string;
  };
  verse_count: number;
}

export interface SearchResponse {
  query: string;
  results: VerseResult[];
  count: number;
}

export interface GraphNode {
  id: string;
  label: string;
  properties: Record<string, any>;
}

export interface GraphEdge {
  source: string;
  target: string;
  type: string;
  properties: Record<string, any>;
}

export interface DiscoveryResult {
  source_ref: string;
  provider: string;
  model: string;
  discovery: {
    entities?: Array<{
      name: string;
      nameHe?: string;
      type: string;
      role?: string;
    }>;
    relationships?: Array<{
      source: string;
      target: string;
      type: string;
      confidence: number;
      explanation: string;
      evidence: string;
    }>;
    cross_references?: Array<{
      ref: string;
      context: string;
    }>;
  };
}

async function apiFetch<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`API error ${res.status}: ${err}`);
  }
  return res.json();
}

export async function searchVerses(
  query: string,
  book?: string,
  limit: number = 20
): Promise<SearchResponse> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  if (book) params.set("book", book);
  return apiFetch<SearchResponse>(`/api/v1/search/fulltext?${params}`);
}

export async function getVerseContext(
  ref: string,
  window: number = 3
): Promise<{ target: string; verses: VerseResult[] }> {
  return apiFetch(`/api/v1/graph/verses/${encodeURIComponent(ref)}/context`);
}

export async function listBooks(): Promise<{ books: Book[] }> {
  return apiFetch("/api/v1/graph/books");
}

export async function getBookChapters(book: string): Promise<{ book: string; chapters: Chapter[] }> {
  return apiFetch(`/api/v1/graph/books/${encodeURIComponent(book)}/chapters`);
}

export async function getBookStructure(book: string): Promise<any> {
  return apiFetch(`/api/v1/graph/books/${encodeURIComponent(book)}/structure`);
}

export async function queryGraph(cypher: string): Promise<any> {
  return apiFetch("/api/v1/discover/relationships", {
    method: "POST",
    body: JSON.stringify({ verse_ref: "Genesis 1:1" }),
  });
}

export async function getCrossRefs(ref: string, limit: number = 5): Promise<any> {
  return apiFetch("/api/v1/discover/cross_refs", {
    method: "POST",
    body: JSON.stringify({ verse_ref: ref, limit }),
  });
}

export async function extractEntities(text: string): Promise<any> {
  return apiFetch("/api/v1/discover/entities", {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}
