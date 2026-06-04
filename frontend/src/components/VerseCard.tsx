"use client";

import { useState } from "react";
import { ChevronDown, ChevronUp, Network, BookOpen } from "lucide-react";
import { getCrossRefs, getVerseContext } from "@/lib/api";

interface VerseCardProps {
  verse: {
    ref: string;
    text_hebrew: string;
    text_english?: string;
    score?: number;
  };
}

export function VerseCard({ verse }: VerseCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [context, setContext] = useState<any>(null);
  const [crossRefs, setCrossRefs] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleExpand = async () => {
    if (expanded) {
      setExpanded(false);
      return;
    }
    setLoading(true);
    setExpanded(true);
    try {
      const [ctx, refs] = await Promise.all([
        getVerseContext(verse.ref, 2),
        getCrossRefs(verse.ref, 3),
      ]);
      setContext(ctx);
      setCrossRefs(refs);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-md border border-slate-200 dark:border-slate-700 overflow-hidden transition-all">
      <div className="p-5">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <BookOpen className="w-4 h-4 text-blue-600" />
            <span className="text-sm font-semibold text-blue-600">{verse.ref}</span>
          </div>
          {verse.score && (
            <span className="text-xs text-slate-500">
              score: {verse.score.toFixed(3)}
            </span>
          )}
        </div>

        <div dir="rtl" className="text-xl leading-relaxed text-slate-900 dark:text-slate-100 font-serif mb-3">
          {verse.text_hebrew}
        </div>

        {verse.text_english && (
          <div className="text-sm text-slate-600 dark:text-slate-400 border-t border-slate-200 dark:border-slate-700 pt-3">
            {verse.text_english}
          </div>
        )}
      </div>

      <button
        onClick={handleExpand}
        className="w-full flex items-center justify-center gap-2 py-2 bg-slate-50 dark:bg-slate-700/50 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors text-sm text-slate-600 dark:text-slate-400"
      >
        {expanded ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
        {expanded ? "סגור" : "הצג הקשר וקשרים"}
        <Network className="w-4 h-4" />
      </button>

      {expanded && (
        <div className="px-5 pb-5 border-t border-slate-200 dark:border-slate-700">
          {loading && (
            <div className="py-4 text-center text-slate-500">טוען...</div>
          )}

          {context && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">הקשר</h4>
              <div className="space-y-2">
                {context.context?.map((v: any) => (
                  <div
                    key={v.ref}
                    className={`p-3 rounded-lg text-sm ${
                      v.ref === verse.ref
                        ? "bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800"
                        : "bg-slate-50 dark:bg-slate-700/30"
                    }`}
                    dir="rtl"
                  >
                    <span className="font-semibold text-xs text-slate-500">{v.ref}</span>
                    <p className="mt-1">{v.text?.substring(0, 150)}...</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {crossRefs?.matches?.length > 0 && (
            <div className="mt-4">
              <h4 className="text-sm font-semibold text-slate-700 dark:text-slate-300 mb-2">
                קישורים צולבים
              </h4>
              <div className="space-y-2">
                {crossRefs.matches.map((match: any, idx: number) => (
                  <div
                    key={`${match.ref || "ref"}-${idx}`}
                    className="p-3 bg-slate-50 dark:bg-slate-700/30 rounded-lg text-sm"
                    dir="rtl"
                  >
                    <span className="font-semibold text-blue-600">{match.ref}</span>
                    <p className="mt-1 text-slate-700 dark:text-slate-300">
                      {match.text_preview}...
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
