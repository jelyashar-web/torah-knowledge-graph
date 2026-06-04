"use client";

import { useState } from "react";
import { Search, Brain, BookOpen, Layers, SlidersHorizontal } from "lucide-react";

export interface SearchOptions {
  searchType: "fulltext" | "semantic" | "hybrid";
  semanticWeight: number;
}

interface SearchBarProps {
  onSearch: (query: string, options: SearchOptions) => void;
  loading?: boolean;
}

export function SearchBar({ onSearch, loading }: SearchBarProps) {
  const [query, setQuery] = useState("");
  const [showOptions, setShowOptions] = useState(false);
  const [searchType, setSearchType] = useState<"fulltext" | "semantic" | "hybrid">("hybrid");
  const [semanticWeight, setSemanticWeight] = useState(0.5);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      onSearch(query.trim(), { searchType, semanticWeight });
    }
  };

  const typeConfig = {
    fulltext: { label: "Fulltext", icon: BookOpen, color: "text-blue-600", bg: "bg-blue-50" },
    semantic: { label: "Semantic", icon: Brain, color: "text-purple-600", bg: "bg-purple-50" },
    hybrid: { label: "Hybrid", icon: Layers, color: "text-indigo-600", bg: "bg-indigo-50" },
  };

  const activeConfig = typeConfig[searchType];

  return (
    <div className="w-full max-w-3xl mx-auto">
      <form onSubmit={handleSubmit}>
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="חפש בתנ״ך... (למשל: בראשית או In the beginning)"
            className="w-full px-6 py-4 pr-14 text-lg bg-white dark:bg-slate-800 border border-slate-300 dark:border-slate-600 rounded-2xl shadow-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
            dir="rtl"
          />
          <button
            type="submit"
            disabled={loading}
            className="absolute left-3 top-1/2 -translate-y-1/2 p-2 bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-colors disabled:opacity-50"
          >
            <Search className="w-5 h-5" />
          </button>

          {/* Search type indicator */}
          <button
            type="button"
            onClick={() => setShowOptions(!showOptions)}
            className={`absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium transition-colors ${activeConfig.bg} ${activeConfig.color}`}
          >
            <activeConfig.icon className="w-3.5 h-3.5" />
            <span>{activeConfig.label}</span>
          </button>
        </div>
      </form>

      {/* Options Panel */}
      {showOptions && (
        <div className="mt-3 p-4 bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700">
          <div className="flex items-center gap-2 mb-3">
            <SlidersHorizontal className="w-4 h-4 text-slate-500" />
            <span className="text-sm font-semibold text-slate-700 dark:text-slate-300">Search Options</span>
          </div>

          {/* Search Type Toggle */}
          <div className="flex gap-2 mb-4">
            {(Object.keys(typeConfig) as Array<keyof typeof typeConfig>).map((type) => {
              const config = typeConfig[type];
              const Icon = config.icon;
              return (
                <button
                  key={type}
                  type="button"
                  onClick={() => setSearchType(type)}
                  className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-xs font-medium transition-all ${
                    searchType === type
                      ? `${config.bg} ${config.color} ring-2 ring-offset-1 ring-slate-200`
                      : "bg-slate-100 dark:bg-slate-700 text-slate-600 dark:text-slate-400"
                  }`}
                >
                  <Icon className="w-3.5 h-3.5" />
                  {config.label}
                </button>
              );
            })}
          </div>

          {/* Semantic Weight Slider */}
          {searchType === "hybrid" && (
            <div className="flex items-center gap-3">
              <span className="text-xs text-slate-500">Fulltext</span>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={semanticWeight}
                onChange={(e) => setSemanticWeight(Number(e.target.value))}
                className="flex-1"
              />
              <span className="text-xs text-slate-500">Semantic</span>
              <span className="text-xs font-mono bg-slate-100 dark:bg-slate-700 px-2 py-0.5 rounded">
                {semanticWeight.toFixed(1)}
              </span>
            </div>
          )}

          {searchType === "semantic" && (
            <div className="text-xs text-slate-500">
              Uses Torah-specific embeddings (nomic-embed-text) for semantic similarity search via Qdrant vector DB.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
