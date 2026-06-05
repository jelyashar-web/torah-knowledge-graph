"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Users,
  Search,
  Filter,
  BookOpen,
  Crown,
  Star,
  Sword,
  Scroll,
  ChevronDown,
  X,
  Network,
  ArrowRight,
} from "lucide-react";

interface Person {
  id: string;
  name: string;
  nameEn: string;
  role: string;
  period: string;
  book: string;
  description: string;
  verses: number;
  connections: number;
  color: string;
}

const people: Person[] = [
  { id: "1", name: "משה רבנו", nameEn: "Moses", role: "נביא", period: "היציאה ממצרים", book: "שמות", description: "גדול הנביאים, מקבל התורה", verses: 1467, connections: 342, color: "from-blue-500 to-indigo-600" },
  { id: "2", name: "אברהם אבינו", nameEn: "Abraham", role: "אב האומה", period: "דור האבות", book: "בראשית", description: "אבי האמונה, נבחן בעקידה", verses: 312, connections: 198, color: "from-amber-500 to-orange-600" },
  { id: "3", name: "דוד המלך", nameEn: "King David", role: "מלך", period: "מלכות בית דוד", book: "שמואל", description: "מלך ישראל, רועה הפסללים", verses: 1123, connections: 287, color: "from-purple-500 to-pink-600" },
  { id: "4", name: "שלמה המלך", nameEn: "King Solomon", role: "מלך", period: "מלכות בית דוד", book: "מלכים", description: "בונה המקדש, חכם מכל אדם", verses: 456, connections: 156, color: "from-emerald-500 to-teal-600" },
  { id: "5", name: "יוסף הצדיק", nameEn: "Joseph", role: "שליט", period: "דור האבות", book: "בראשית", description: "משנה למלך מצרים, הציל משפחתו", verses: 189, connections: 134, color: "from-cyan-500 to-blue-600" },
  { id: "6", name: "אהרן הכהן", nameEn: "Aaron", role: "כהן גדול", period: "היציאה ממצרים", book: "שמות", description: "אחי משה, כהן גדול ראשון", verses: 534, connections: 167, color: "from-rose-500 to-pink-600" },
  { id: "7", name: "יהושע בן נון", nameEn: "Joshua", role: "מנהיג", period: "כיבוש הארץ", book: "יהושע", description: "תלמיד משה, מכניס את ישראל לארץ", verses: 678, connections: 145, color: "from-green-500 to-emerald-600" },
  { id: "8", name: "שמשון הגיבור", nameEn: "Samson", role: "שופט", period: "שופטים", book: "שופטים", description: "נזיר אלהים, גיבור בעל כוח על-אנושי", verses: 96, connections: 67, color: "from-red-500 to-orange-600" },
  { id: "9", name: "שאול המלך", nameEn: "King Saul", role: "מלך", period: "מלכות שאול", book: "שמואל", description: "מלך ישראל הראשון", verses: 423, connections: 134, color: "from-slate-500 to-gray-600" },
  { id: "10", name: "שמואל הנביא", nameEn: "Samuel", role: "נביא", period: "שופטים", book: "שמואל", description: "שופט ונביא, משיח למלכות", verses: 345, connections: 178, color: "from-yellow-500 to-amber-600" },
  { id: "11", name: "אליהו הנביא", nameEn: "Elijah", role: "נביא", period: "מלכות ישראל", book: "מלכים", description: "נביא האש, נאבק בבעל", verses: 234, connections: 89, color: "from-orange-500 to-red-600" },
  { id: "12", name: "אלישע הנביא", nameEn: "Elisha", role: "נביא", period: "מלכות ישראל", book: "מלכים", description: "תלמיד אליהו, עושה נפלאות", verses: 198, connections: 76, color: "from-indigo-500 to-purple-600" },
  { id: "13", name: "חזקיהו המלך", nameEn: "Hezekiah", role: "מלך", period: "מלכות יהודה", book: "מלכים", description: "מלך צדיק, חידש עבודת המקדש", verses: 134, connections: 56, color: "from-teal-500 to-cyan-600" },
  { id: "14", name: "יואש המלך", nameEn: "Joash", role: "מלך", period: "מלכות יהודה", book: "מלכים", description: "מלך מגיל 7, חידש המקדש", verses: 89, connections: 45, color: "from-violet-500 to-purple-600" },
  { id: "15", name: "דבורה הנביאה", nameEn: "Deborah", role: "נביאה", period: "שופטים", book: "שופטים", description: "אישה נביאה, שופטת ומנהיגה", verses: 45, connections: 34, color: "from-fuchsia-500 to-pink-600" },
  { id: "16", name: "גדעון בן יואש", nameEn: "Gideon", role: "שופט", period: "שופטים", book: "שופטים", description: "שופט ישראל, מנצח המדיאנים", verses: 78, connections: 56, color: "from-lime-500 to-green-600" },
];

const roleIcons: Record<string, typeof Users> = {
  נביא: Star,
  "אב האומה": Users,
  מלך: Crown,
  שליט: Crown,
  "כהן גדול": Scroll,
  מנהיג: Sword,
  שופט: Sword,
  נביאה: Star,
};

const filters = [
  { key: "all", label: "הכל" },
  { key: "נביא", label: "נביאים" },
  { key: "מלך", label: "מלכים" },
  { key: "שופט", label: "שופטים" },
  { key: "כהן גדול", label: "כהנים" },
];

export default function PeopleDirectory() {
  const [search, setSearch] = useState("");
  const [activeFilter, setActiveFilter] = useState("all");
  const [selectedPerson, setSelectedPerson] = useState<Person | null>(null);
  const [sortBy, setSortBy] = useState<"name" | "verses" | "connections">("name");

  const filtered = people
    .filter((p) => {
      const matchesSearch =
        p.name.includes(search) ||
        p.nameEn.toLowerCase().includes(search.toLowerCase()) ||
        p.description.includes(search);
      const matchesRole = activeFilter === "all" || p.role === activeFilter;
      return matchesSearch && matchesRole;
    })
    .sort((a, b) => {
      if (sortBy === "verses") return b.verses - a.verses;
      if (sortBy === "connections") return b.connections - a.connections;
      return a.name.localeCompare(b.name);
    });

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex flex-col md:flex-row md:items-center justify-between gap-4"
      >
        <div>
          <h1 className="text-3xl font-bold text-white">אישי התנ"ך</h1>
          <p className="text-slate-400 mt-1">{people.length} דמויות מקראיות מוכרות — נביאים, מלכים, שופטים ומנהיגים</p>
        </div>
        <div className="flex items-center gap-2">
          {[
            { key: "name", label: "שם" },
            { key: "verses", label: "פסוקים" },
            { key: "connections", label: "קשרים" },
          ].map((s) => (
            <button
              key={s.key}
              onClick={() => setSortBy(s.key as any)}
              className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-colors ${
                sortBy === s.key
                  ? "bg-amber-500/10 text-amber-400 border border-amber-500/20"
                  : "bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10"
              }`}
            >
              {s.label}
            </button>
          ))}
        </div>
      </motion.div>

      {/* Search & Filters */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="flex flex-col md:flex-row gap-4"
      >
        <div className="relative flex-1">
          <Search className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="חפש אישיות... (למשל: משה, דוד, דבורה)"
            className="w-full pr-12 pl-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-slate-500 focus:ring-2 focus:ring-amber-500/50 focus:border-amber-500/50 transition-all outline-none"
          />
        </div>
      </motion.div>

      {/* Role Filters */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
        className="flex flex-wrap gap-2"
      >
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setActiveFilter(f.key)}
            className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${
              activeFilter === f.key
                ? "bg-amber-500 text-white shadow-lg shadow-amber-500/20"
                : "bg-white/5 text-slate-400 border border-white/5 hover:bg-white/10"
            }`}
          >
            {f.label}
          </button>
        ))}
      </motion.div>

      {/* Results Count */}
      <div className="text-sm text-slate-500">
        מציג {filtered.length} מתוך {people.length} אישים
      </div>

      {/* People Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
        <AnimatePresence mode="popLayout">
          {filtered.map((person, i) => {
            const RoleIcon = roleIcons[person.role] || Users;
            return (
              <motion.div
                key={person.id}
                layout
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ delay: i * 0.03 }}
                whileHover={{ y: -4, scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
                onClick={() => setSelectedPerson(person)}
                className="group cursor-pointer"
              >
                <div className="relative p-5 bg-white/[0.03] border border-white/5 rounded-2xl backdrop-blur-sm hover:bg-white/[0.07] hover:border-white/10 transition-all overflow-hidden">
                  {/* Gradient accent */}
                  <div className={`absolute top-0 right-0 w-full h-1 bg-gradient-to-l ${person.color}`} />

                  <div className="flex items-start justify-between mb-4">
                    <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${person.color} flex items-center justify-center shadow-lg`}>
                      <RoleIcon className="w-5 h-5 text-white" />
                    </div>
                    <span className="px-2 py-1 bg-white/5 rounded-lg text-[10px] text-slate-400 border border-white/5">
                      {person.book}
                    </span>
                  </div>

                  <h3 className="text-lg font-bold text-white mb-1 group-hover:text-amber-400 transition-colors">
                    {person.name}
                  </h3>
                  <p className="text-xs text-slate-500 mb-3">{person.nameEn}</p>

                  <p className="text-sm text-slate-400 mb-4 line-clamp-2">{person.description}</p>

                  <div className="flex items-center gap-4 text-xs text-slate-500">
                    <div className="flex items-center gap-1">
                      <BookOpen className="w-3.5 h-3.5" />
                      <span>{person.verses.toLocaleString()} פסוקים</span>
                    </div>
                    <div className="flex items-center gap-1">
                      <Network className="w-3.5 h-3.5" />
                      <span>{person.connections} קשרים</span>
                    </div>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </AnimatePresence>
      </div>

      {/* Detail Modal */}
      <AnimatePresence>
        {selectedPerson && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelectedPerson(null)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.9, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.9, y: 20 }}
              className="fixed inset-4 md:inset-auto md:top-1/2 md:left-1/2 md:-translate-x-1/2 md:-translate-y-1/2 md:w-[600px] md:max-h-[80vh] bg-[#0d1321] border border-white/10 rounded-2xl z-50 overflow-y-auto shadow-2xl"
            >
              <div className="p-6">
                <div className="flex items-start justify-between mb-6">
                  <div className="flex items-center gap-4">
                    <div className={`w-16 h-16 rounded-2xl bg-gradient-to-br ${selectedPerson.color} flex items-center justify-center shadow-lg`}>
                      <Users className="w-8 h-8 text-white" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold text-white">{selectedPerson.name}</h2>
                      <p className="text-slate-400">{selectedPerson.nameEn}</p>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedPerson(null)}
                    className="p-2 text-slate-400 hover:text-white transition-colors"
                  >
                    <X className="w-6 h-6" />
                  </button>
                </div>

                <div className="space-y-4">
                  <div className="grid grid-cols-3 gap-3">
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <div className="text-2xl font-bold text-amber-400">{selectedPerson.verses.toLocaleString()}</div>
                      <div className="text-xs text-slate-500">פסוקים</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <div className="text-2xl font-bold text-blue-400">{selectedPerson.connections}</div>
                      <div className="text-xs text-slate-500">קשרים</div>
                    </div>
                    <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                      <div className="text-2xl font-bold text-purple-400">{selectedPerson.book}</div>
                      <div className="text-xs text-slate-500">ספר ראשי</div>
                    </div>
                  </div>

                  <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-2">תיאור</div>
                    <p className="text-white">{selectedPerson.description}</p>
                  </div>

                  <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                    <div className="text-sm text-slate-400 mb-2">תקופה</div>
                    <p className="text-white">{selectedPerson.period}</p>
                  </div>

                  <div className="flex gap-3">
                    <button className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20 hover:bg-amber-500/20 transition-colors">
                      <BookOpen className="w-4 h-4" />
                      <span className="text-sm">צפה בפסוקים</span>
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-blue-500/10 text-blue-400 rounded-xl border border-blue-500/20 hover:bg-blue-500/20 transition-colors">
                      <Network className="w-4 h-4" />
                      <span className="text-sm">גרף קשרים</span>
                    </button>
                  </div>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
