"use client";

import { useState } from "react";
import { useQuery, useLazyQuery } from "@apollo/client/react";
import { gql } from "graphql-tag";
import { Network, Search, BookOpen, GitBranch, Activity, Terminal } from "lucide-react";

// ── GraphQL Queries ─────────────────────────────────────

const GET_BOOKS = gql`
  query GetBooks {
    books {
      id
      title
      hebrewTitle
      category
      order
    }
  }
`;

const SEARCH = gql`
  query Search($input: SearchInput!) {
    search(input: $input) {
      score
      source
      verse {
        ref
        hebrew
        english
        book
        chapter
        verse
      }
      node {
        id
        label
        hebrew
        type
      }
    }
  }
`;

const GET_VERSE = gql`
  query GetVerse($ref: String!) {
    verse(ref: $ref) {
      ref
      hebrew
      english
      book
      chapter
      verse
    }
  }
`;

const GET_STATS = gql`
  query GetStats {
    stats {
      totalNodes
      totalRelationships
      nodeBreakdown
      relationshipBreakdown
      lastUpdated
    }
  }
`;

const GET_NEIGHBORS = gql`
  query GetNeighbors($nodeId: String!, $depth: Int) {
    graphNeighbors(nodeId: $nodeId, depth: $depth) {
      id
      label
      hebrew
      type
    }
  }
`;

// ── Component ───────────────────────────────────────────

export function GraphQLExplorer() {
  const [activeQuery, setActiveQuery] = useState<"books" | "search" | "verse" | "stats" | "neighbors">("books");
  const [searchQuery, setSearchQuery] = useState("בראשית");
  const [verseRef, setVerseRef] = useState("Genesis 1:1");
  const [nodeId, setNodeId] = useState("");

  // Books query
  const { data: booksData, loading: booksLoading } = useQuery<any>(GET_BOOKS);

  // Search lazy query
  const [runSearch, { data: searchData, loading: searchLoading }] = useLazyQuery<any>(SEARCH);

  // Verse lazy query
  const [runVerse, { data: verseData, loading: verseLoading }] = useLazyQuery<any>(GET_VERSE);

  // Stats query
  const { data: statsData } = useQuery<any>(GET_STATS);

  // Neighbors lazy query
  const [runNeighbors, { data: neighborsData, loading: neighborsLoading }] = useLazyQuery<any>(GET_NEIGHBORS);

  const handleSearch = () => {
    runSearch({
      variables: {
        input: {
          query: searchQuery,
          searchType: "all",
          limit: 10,
        },
      },
    });
  };

  const handleVerse = () => {
    runVerse({ variables: { ref: verseRef } });
  };

  const handleNeighbors = () => {
    if (nodeId) runNeighbors({ variables: { nodeId, depth: 1 } });
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden">
      {/* Header */}
      <div className="px-4 py-3 bg-gradient-to-r from-indigo-600 to-purple-600 flex items-center gap-2">
        <Network className="w-5 h-5 text-white" />
        <h3 className="font-bold text-white">GraphQL Explorer</h3>
        <span className="text-xs text-white/70 bg-white/20 px-2 py-0.5 rounded-full">
          /graphql
        </span>
      </div>

      {/* Query Tabs */}
      <div className="flex gap-1 p-2 border-b border-slate-200 dark:border-slate-700 overflow-x-auto">
        {[
          { id: "books", label: "Books", icon: BookOpen },
          { id: "search", label: "Search", icon: Search },
          { id: "verse", label: "Verse", icon: Terminal },
          { id: "stats", label: "Stats", icon: Activity },
          { id: "neighbors", label: "Neighbors", icon: GitBranch },
        ].map((q) => (
          <button
            key={q.id}
            onClick={() => setActiveQuery(q.id as any)}
            className={`flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              activeQuery === q.id
                ? "bg-indigo-600 text-white"
                : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
            }`}
          >
            <q.icon className="w-3.5 h-3.5" />
            {q.label}
          </button>
        ))}
      </div>

      {/* Query Content */}
      <div className="p-4">
        {activeQuery === "books" && (
          <div>
            <h4 className="text-sm font-semibold mb-2 text-slate-700 dark:text-slate-300">All Books</h4>
            {booksLoading && <p className="text-sm text-slate-500">Loading...</p>}
            <div className="space-y-1 max-h-96 overflow-y-auto">
              {booksData?.books?.map((book: any) => (
                <div
                  key={book.id}
                  className="p-2 bg-slate-50 dark:bg-slate-700 rounded text-sm flex justify-between"
                >
                  <span className="font-medium">{book.title}</span>
                  <span className="text-slate-500 text-xs">{book.category}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeQuery === "search" && (
          <div>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleSearch()}
                placeholder="Search..."
                className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-sm"
                dir="rtl"
              />
              <button
                onClick={handleSearch}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm"
              >
                Search
              </button>
            </div>
            {searchLoading && <p className="text-sm text-slate-500">Searching...</p>}
            <div className="space-y-2">
              {searchData?.search?.map((result: any, i: number) => (
                <div key={i} className="p-3 bg-slate-50 dark:bg-slate-700 rounded-lg text-sm">
                  {result.verse && (
                    <div>
                      <span className="font-semibold text-indigo-600">{result.verse.ref}</span>
                      <p className="mt-1" dir="rtl">{result.verse.hebrew}</p>
                    </div>
                  )}
                  {result.node && (
                    <div>
                      <span className="font-semibold text-purple-600">{result.node.label}</span>
                      <span className="text-xs text-slate-500 ml-2">({result.node.type})</span>
                    </div>
                  )}
                  <span className="text-xs text-slate-400 mt-1 block">{result.source} — score: {result.score.toFixed(2)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeQuery === "verse" && (
          <div>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={verseRef}
                onChange={(e) => setVerseRef(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleVerse()}
                placeholder="Genesis 1:1"
                className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-sm"
              />
              <button
                onClick={handleVerse}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm"
              >
                Fetch
              </button>
            </div>
            {verseLoading && <p className="text-sm text-slate-500">Loading...</p>}
            {verseData?.verse && (
              <div className="p-4 bg-slate-50 dark:bg-slate-700 rounded-lg">
                <h5 className="font-bold text-lg mb-2">{verseData.verse.ref}</h5>
                <p className="text-base mb-2" dir="rtl">{verseData.verse.hebrew}</p>
                <p className="text-sm text-slate-600 dark:text-slate-400">{verseData.verse.english}</p>
                <div className="mt-2 text-xs text-slate-500">
                  {verseData.verse.book} {verseData.verse.chapter}:{verseData.verse.verse}
                </div>
              </div>
            )}
          </div>
        )}

        {activeQuery === "stats" && statsData?.stats && (
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gradient-to-br from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 rounded-xl">
              <div className="text-3xl font-bold text-blue-600">{statsData.stats.totalNodes.toLocaleString()}</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Total Nodes</div>
            </div>
            <div className="p-4 bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-xl">
              <div className="text-3xl font-bold text-purple-600">{statsData.stats.totalRelationships.toLocaleString()}</div>
              <div className="text-sm text-slate-600 dark:text-slate-400">Relationships</div>
            </div>
            <div className="col-span-2 p-3 bg-slate-50 dark:bg-slate-700 rounded-lg">
              <pre className="text-xs overflow-x-auto">{statsData.stats.nodeBreakdown}</pre>
            </div>
          </div>
        )}

        {activeQuery === "neighbors" && (
          <div>
            <div className="flex gap-2 mb-3">
              <input
                type="text"
                value={nodeId}
                onChange={(e) => setNodeId(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleNeighbors()}
                placeholder="Node ID..."
                className="flex-1 px-3 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-900 text-sm"
              />
              <button
                onClick={handleNeighbors}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg text-sm"
              >
                Explore
              </button>
            </div>
            {neighborsLoading && <p className="text-sm text-slate-500">Loading...</p>}
            <div className="space-y-1">
              {neighborsData?.graphNeighbors?.map((n: any) => (
                <div key={n.id} className="p-2 bg-slate-50 dark:bg-slate-700 rounded text-sm flex justify-between">
                  <span>{n.label || n.hebrew || n.id}</span>
                  <span className="text-xs text-slate-500">{n.type}</span>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
