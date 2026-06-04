"use client";

import { createContext, useContext, useState, ReactNode } from "react";

type Locale = "he" | "en";

const translations: Record<Locale, Record<string, string>> = {
  he: {
    "app.title": "Torah Knowledge Graph",
    "app.subtitle": "גרף ידע תורני חי — 1.4M+ צמתים",
    "search.placeholder": "חפש פסוק, מושג, או נושא...",
    "search.button": "חיפוש",
    "tab.search": "חיפוש",
    "tab.graph": "גרף",
    "tab.chat": "צ׳אט AI",
    "tab.analytics": "אנליטיקס",
    "verse.context": "הקשר",
    "verse.crossrefs": "קישורים צולבים",
    "graph.depth": "עומק",
    "graph.filter": "סינון",
    "chat.placeholder": "שאל שאלה בתורה...",
    "analytics.stats": "סטטיסטיקות",
    "theme.light": "בהיר",
    "theme.dark": "כהה",
    "theme.system": "מערכת",
    "lang.hebrew": "עברית",
    "lang.english": "English",
    "loading": "טוען...",
    "error": "שגיאה",
    "retry": "נסה שוב",
  },
  en: {
    "app.title": "Torah Knowledge Graph",
    "app.subtitle": "Live Torah Knowledge Graph — 1.4M+ nodes",
    "search.placeholder": "Search verse, concept, or topic...",
    "search.button": "Search",
    "tab.search": "Search",
    "tab.graph": "Graph",
    "tab.chat": "AI Chat",
    "tab.analytics": "Analytics",
    "verse.context": "Context",
    "verse.crossrefs": "Cross References",
    "graph.depth": "Depth",
    "graph.filter": "Filter",
    "chat.placeholder": "Ask a Torah question...",
    "analytics.stats": "Statistics",
    "theme.light": "Light",
    "theme.dark": "Dark",
    "theme.system": "System",
    "lang.hebrew": "עברית",
    "lang.english": "English",
    "loading": "Loading...",
    "error": "Error",
    "retry": "Retry",
  },
};

interface I18nContextType {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: string) => string;
  dir: "rtl" | "ltr";
}

const I18nContext = createContext<I18nContextType | undefined>(undefined);

export function I18nProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>("he");

  const setLocale = (l: Locale) => {
    setLocaleState(l);
    localStorage.setItem("tkg-locale", l);
    document.documentElement.lang = l;
    document.documentElement.dir = l === "he" ? "rtl" : "ltr";
  };

  const t = (key: string) => translations[locale][key] || key;
  const dir = locale === "he" ? "rtl" : "ltr";

  return (
    <I18nContext.Provider value={{ locale, setLocale, t, dir }}>
      {children}
    </I18nContext.Provider>
  );
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
