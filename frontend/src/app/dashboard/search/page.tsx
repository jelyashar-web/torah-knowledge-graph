"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { SearchBar } from "@/components/SearchBar";
import { VerseCard } from "@/components/VerseCard";
import { searchVerses } from "@/lib/api";
import { Book, Brain, Layers } from "lucide-react";

export default function SearchPage() {
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [query, setQuery] = useState("");
  const [searchMeta, setSearchMeta] = useState<any>(null);

  const handleSearch = async (q: string, options?: any) => {
    setLoading(true);
    setQuery(q);
    try {
      const data = await searchVerses(
        q,
        undefined,
        20,
        options?.searchType || "hybrid",
        options?.semanticWeight || 0.5
      );
      setResults(data.results || []);
      setSearchMeta({
        type: data.search_type || "hybrid",
        model: data.model,
        semanticWeight: data.semantic_weight,
      });
    } catch (e) {
      console.error(e);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const typeIcons: Record<string, typeof Book> = {
    fulltext: Book,
    semantic: Brain,
    hybrid: Layers,
  };

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-5xl mx-auto space-y-6"
    >
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-2xl font-bold text-white mb-2">חיפוש חכם בתנ"ך</h2>
        <p className="text-slate-400">Fulltext + Semantic + Hybrid — כל שיטה מניבה תוצאות</p>
      </div>

      {/* Search Bar */}
      <SearchBar onSearch={handleSearch} loading={loading} />

      {/* Results Meta */}
      {searchMeta && (
        <div className="flex items-center justify-center gap-4 text-sm">
          <span className="px-3 py-1 bg-white/5 rounded-full text-slate-400 border border-white/5">
            שיטה: {searchMeta.type === "fulltext" ? "Fulltext" : searchMeta.type === "semantic" ? "Semantic" : "Hybrid"}
          </span>
          {searchMeta.model && (
            <span className="px-3 py-1 bg-white/5 rounded-full text-slate-400 border border-white/5">
              מודל: {searchMeta.model}
            </span>
          )}
        </div>
      )}

      {/* Results */}
      <div className="space-y-3">
        {results.map((verse: any, i: number) => (
          <VerseCard key={`${verse.ref}-${i}`} verse={verse} />
        ))}
        {!loading && results.length === 0 && query && (
          <div className="text-center py-12">
            <Book className="w-12 h-12 mx-auto text-slate-600 mb-3" />
            <p className="text-slate-400">לא נמצאו תוצאות</p>
            <p className="text-sm text-slate-500 mt-1">נסה חיפוש אחר</p>
          </div>
        )}
      </div>
    </motion.div>
  );
}
