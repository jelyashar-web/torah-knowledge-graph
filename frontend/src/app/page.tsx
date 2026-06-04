"use client";

import { useState } from "react";
import { SearchBar } from "@/components/SearchBar";
import { VerseCard } from "@/components/VerseCard";
import { GraphView } from "@/components/GraphView";
import { searchVerses } from "@/lib/api";
import { Book, Network, Database, Layers } from "lucide-react";

export default function Home() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"search" | "graph">("search");

  const handleSearch = async (q: string) => {
    setLoading(true);
    setQuery(q);
    try {
      const data = await searchVerses(q, undefined, 20);
      setResults(data.results || []);
    } catch (e) {
      console.error(e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-blue-600 rounded-xl flex items-center justify-center">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                  Torah Knowledge Graph
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  גרף ידע תורני חי — 1.4M+ nodes
                </p>
              </div>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => setActiveTab("search")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === "search"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                }`}
              >
                <Book className="w-4 h-4" />
                חיפוש
              </button>
              <button
                onClick={() => setActiveTab("graph")}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
                  activeTab === "graph"
                    ? "bg-blue-600 text-white"
                    : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                }`}
              >
                <Network className="w-4 h-4" />
                גרף
              </button>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === "search" && (
          <>
            {/* Search */}
            <div className="mb-8">
              <SearchBar onSearch={handleSearch} loading={loading} />
            </div>

            {/* Stats */}
            {query && (
              <div className="flex items-center gap-4 mb-6 text-sm text-slate-600 dark:text-slate-400">
                <Layers className="w-4 h-4" />
                <span>
                  {loading
                    ? "מחפש..."
                    : `${results.length} תוצאות עבור "${query}"`}
                </span>
              </div>
            )}

            {/* Results */}
            <div className="space-y-4">
              {results.map((verse: any, i: number) => (
                <VerseCard key={`${verse.ref}-${i}`} verse={verse} />
              ))}
              {!loading && results.length === 0 && query && (
                <div className="text-center py-12 text-slate-500">
                  לא נמצאו תוצאות
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === "graph" && (
          <div className="space-y-6">
            <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
              <h2 className="text-xl font-bold mb-4 text-slate-900 dark:text-white">
                ויזואליזציית גרף
              </h2>
              <p className="text-slate-600 dark:text-slate-400 mb-4">
                גרף אינטראקטיבי של ספרים, פרקים, פסוקים, וישויות.
                לחץ על נוד כדי לחקור קשרים.
              </p>
              <GraphView />
            </div>

            {/* Torah Domains */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                { name: "תנ״ך", count: "39 ספרים", color: "bg-blue-500" },
                { name: "חסידות", count: "~500 ספרים", color: "bg-purple-500" },
                { name: "הלכה", count: "~200 ספרים", color: "bg-green-500" },
                { name: "קבלה", count: "~100 ספרים", color: "bg-amber-500" },
              ].map((domain) => (
                <div
                  key={domain.name}
                  className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700 hover:shadow-md transition-shadow cursor-pointer"
                >
                  <div className={`w-3 h-3 rounded-full ${domain.color} mb-2`} />
                  <h3 className="font-bold text-slate-900 dark:text-white">{domain.name}</h3>
                  <p className="text-sm text-slate-500">{domain.count}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
