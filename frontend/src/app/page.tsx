"use client";

import { useState, useEffect } from "react";
import { SearchBar, SearchOptions } from "@/components/SearchBar";
import { VerseCard } from "@/components/VerseCard";
import { AdvancedGraphExplorer } from "@/components/AdvancedGraphExplorer";
import { AIChat } from "@/components/AIChat";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";
import { searchVerses, listBooks } from "@/lib/api";
import { Book, Network, Database, BarChart3, MessageSquare, ChevronRight, Code2 } from "lucide-react";
import { GraphQLExplorer } from "@/components/GraphQLExplorer";
import { ThemeToggle } from "@/components/ThemeToggle";
import { useI18n } from "@/components/I18nProvider";

export default function Home() {
  const { t, locale, setLocale } = useI18n();
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [activeTab, setActiveTab] = useState<"search" | "graph" | "chat" | "graphql" | "analytics">("search");
  const [books, setBooks] = useState<any[]>([]);
  const [selectedBook, setSelectedBook] = useState<string | null>(null);

  // Load books on mount
  useEffect(() => {
    listBooks().then((data) => {
      if (data.books) setBooks(data.books);
    }).catch(console.error);
  }, []);

  const handleSearch = async (q: string, options?: SearchOptions) => {
    setLoading(true);
    setQuery(q);
    try {
      const data = await searchVerses(
        q,
        selectedBook || undefined,
        20,
        options?.searchType || "hybrid",
        options?.semanticWeight || 0.5
      );
      setResults(data.results || []);
      setActiveTab("search");
    } catch (e) {
      console.error(e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: "search", label: "חיפוש", icon: Book },
    { id: "graph", label: "גרף", icon: Network },
    { id: "chat", label: "AI Chat", icon: MessageSquare },
    { id: "graphql", label: "GraphQL", icon: Code2 },
    { id: "analytics", label: "אנליטיקס", icon: BarChart3 },
  ];

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-slate-900">
      {/* Header */}
      <header className="bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl flex items-center justify-center shadow-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                  Torah Knowledge Graph
                </h1>
                <p className="text-sm text-slate-500 dark:text-slate-400">
                  Enterprise Graph-Native Torah Platform — 1.4M+ nodes | AI Chat | Real-time
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {/* Language Toggle */}
              <div className="flex items-center bg-slate-100 dark:bg-slate-700 rounded-lg p-1">
                <button
                  onClick={() => setLocale("he")}
                  className={`px-2 py-1 rounded-md text-xs font-bold transition-all ${
                    locale === "he" ? "bg-white dark:bg-slate-600 shadow-sm" : "text-slate-500"
                  }`}
                >
                  עברית
                </button>
                <button
                  onClick={() => setLocale("en")}
                  className={`px-2 py-1 rounded-md text-xs font-bold transition-all ${
                    locale === "en" ? "bg-white dark:bg-slate-600 shadow-sm" : "text-slate-500"
                  }`}
                >
                  EN
                </button>
              </div>

              <ThemeToggle />

              <div className="flex gap-1">
                {tabs.map((tab) => (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id as any)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
                      activeTab === tab.id
                        ? "bg-blue-600 text-white shadow-md"
                        : "bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-300 hover:bg-slate-200"
                    }`}
                  >
                    <tab.icon className="w-4 h-4" />
                    <span className="hidden sm:inline">{tab.label}</span>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Search Bar — always visible */}
        <div className="mb-6">
          <div className="flex gap-2 mb-4">
            <div className="flex-1">
              <SearchBar onSearch={handleSearch} loading={loading} />
            </div>
          </div>

          {/* Book Filter */}
          <div className="flex gap-2 overflow-x-auto pb-2">
            <button
              onClick={() => setSelectedBook(null)}
              className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors ${
                !selectedBook
                  ? "bg-blue-600 text-white"
                  : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
              }`}
            >
              הכל
            </button>
            {books.slice(0, 20).map((book: any) => (
              <button
                key={book.title}
                onClick={() => setSelectedBook(book.title)}
                className={`px-3 py-1 rounded-full text-sm whitespace-nowrap transition-colors ${
                  selectedBook === book.title
                    ? "bg-blue-600 text-white"
                    : "bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300"
                }`}
              >
                {book.title}
              </button>
            ))}
            {books.length > 20 && (
              <span className="text-sm text-slate-500 px-2">+{books.length - 20} עוד...</span>
            )}
          </div>
        </div>

        {/* Tab Content */}
        {activeTab === "search" && (
          <>
            {query && (
              <div className="flex items-center gap-2 mb-4 text-sm text-slate-600 dark:text-slate-400">
                <ChevronRight className="w-4 h-4" />
                <span>
                  {loading
                    ? "מחפש..."
                    : `${results.length} תוצאות עבור "${query}"${selectedBook ? ` בספר ${selectedBook}` : ""}`}
                </span>
              </div>
            )}

            <div className="space-y-4">
              {results.map((verse: any, i: number) => (
                <VerseCard key={`${verse.ref}-${i}`} verse={verse} />
              ))}
              {!loading && results.length === 0 && query && (
                <div className="text-center py-12">
                  <Book className="w-12 h-12 mx-auto text-slate-300 mb-3" />
                  <p className="text-slate-500">לא נמצאו תוצאות</p>
                  <p className="text-sm text-slate-400 mt-1">נסה חיפוש אחר או בדוק אם Neo4j רץ</p>
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === "graph" && (
          <div className="h-[calc(100vh-200px)]">
            <AdvancedGraphExplorer />
          </div>
        )}

        {activeTab === "chat" && (
          <div className="max-w-4xl mx-auto">
            <AIChat />
          </div>
        )}

        {activeTab === "graphql" && (
          <div className="max-w-5xl mx-auto">
            <GraphQLExplorer />
          </div>
        )}

        {activeTab === "analytics" && (
          <div>
            <AnalyticsDashboard />
          </div>
        )}
      </main>
    </div>
  );
}
