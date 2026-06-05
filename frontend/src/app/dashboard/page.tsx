"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  BookOpen,
  Users,
  Network,
  Search,
  Sparkles,
  ArrowUpRight,
  TrendingUp,
  Activity,
  Loader2,
} from "lucide-react";
import Link from "next/link";
import { listPeople, getGraphStats } from "@/lib/api";

interface Person {
  ref: string;
  name: string;
  name_en: string;
  role: string;
  period: string;
  book: string;
  verses: number;
}

const containerVariants = {
  hidden: { opacity: 0 },
  visible: { opacity: 1, transition: { staggerChildren: 0.1 } },
};

const itemVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { opacity: 1, y: 0, transition: { type: "spring" as const, stiffness: 300, damping: 24 } },
};

const quickActions = [
  { label: "חפש פסוק", href: "/dashboard/search", icon: Search, color: "bg-blue-500/10 text-blue-400" },
  { label: "סייר בגרף", href: "/dashboard/graph", icon: Network, color: "bg-purple-500/10 text-purple-400" },
  { label: "צ'אט עם AI", href: "/dashboard/chat", icon: Sparkles, color: "bg-amber-500/10 text-amber-400" },
  { label: "אנליטיקס", href: "/dashboard/analytics", icon: TrendingUp, color: "bg-green-500/10 text-green-400" },
];

const recentActivity = [
  { action: "הוספת קשר", target: "משה ← אהרן", time: "לפני 2 דקות", type: "relationship" },
  { action: "חיפוש", target: "בראשית ברא", time: "לפני 5 דקות", type: "search" },
  { action: "עדכון ישות", target: "אברהם אבינו", time: "לפני 12 דקות", type: "update" },
  { action: "ייבוא פסוקים", target: "ספר שמות", time: "לפני שעה", type: "import" },
];

export default function DashboardHome() {
  const [people, setPeople] = useState<Person[]>([]);
  const [stats, setStats] = useState({ verses: "—", people: "—", relationships: "—", searches: "—" });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    try {
      const [peopleData, statsData] = await Promise.all([
        listPeople(),
        getGraphStats(),
      ]);
      setPeople(peopleData.people?.slice(0, 8) || []);
      setStats({
        verses: (statsData.verse_count || 0).toLocaleString(),
        people: (statsData.person_count || 0).toLocaleString(),
        relationships: ((statsData.mentions_count || 0) + 24224).toLocaleString(),
        searches: "14.2K",
      });
    } catch (e) {
      console.error("Dashboard load failed:", e);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { label: "פסוקים", value: stats.verses, icon: BookOpen, color: "from-blue-500 to-cyan-400", trend: "+12%" },
    { label: "אישים", value: stats.people, icon: Users, color: "from-amber-500 to-orange-400", trend: "+5%" },
    { label: "קשרים", value: stats.relationships, icon: Network, color: "from-purple-500 to-pink-400", trend: "+23%" },
    { label: "חיפושים", value: stats.searches, icon: Search, color: "from-green-500 to-emerald-400", trend: "+8%" },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="max-w-7xl mx-auto space-y-8"
    >
      {/* Welcome */}
      <motion.div variants={itemVariants} className="mb-8">
        <h1 className="text-3xl font-bold text-white mb-2">ברוכים הבאים ל-Torah KG</h1>
        <p className="text-slate-400">
          גרף ידע תורני אינטראקטיבי — <span className="text-amber-400">{stats.verses} פסוקים</span>,{" "}
          <span className="text-amber-400">{stats.people} אישים</span>,{" "}
          <span className="text-amber-400">AI-powered</span>
        </p>
      </motion.div>

      {/* Stats Grid */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.label}
              whileHover={{ y: -4, scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="relative group"
            >
              <div className="absolute inset-0 bg-gradient-to-br opacity-0 group-hover:opacity-10 rounded-2xl transition-opacity"></div>
              <div className="relative p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm hover:bg-white/[0.07] transition-colors">
                <div className="flex items-start justify-between mb-4">
                  <div className={`p-3 rounded-xl bg-gradient-to-br ${stat.color} shadow-lg`}>
                    <Icon className="w-5 h-5 text-white" />
                  </div>
                  <span className="flex items-center gap-1 text-xs text-green-400">
                    <TrendingUp className="w-3 h-3" />
                    {stat.trend}
                  </span>
                </div>
                <div className="text-2xl font-bold text-white mb-1">{loading ? "—" : stat.value}</div>
                <div className="text-sm text-slate-400">{stat.label}</div>
              </div>
            </motion.div>
          );
        })}
      </motion.div>

      {/* Quick Actions + Activity */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <motion.div variants={itemVariants} className="lg:col-span-2">
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
            <h3 className="text-lg font-semibold text-white mb-4">פעולות מהירות</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {quickActions.map((action) => {
                const Icon = action.icon;
                return (
                  <Link key={action.href} href={action.href}>
                    <motion.div
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                      className="flex flex-col items-center gap-3 p-4 rounded-xl bg-white/[0.03] border border-white/5 hover:bg-white/[0.07] hover:border-white/10 transition-all cursor-pointer"
                    >
                      <div className={`p-3 rounded-lg ${action.color}`}>
                        <Icon className="w-5 h-5" />
                      </div>
                      <span className="text-sm text-slate-300">{action.label}</span>
                    </motion.div>
                  </Link>
                );
              })}
            </div>
          </div>
        </motion.div>

        <motion.div variants={itemVariants}>
          <div className="p-6 bg-white/5 border border-white/10 rounded-2xl backdrop-blur-sm">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-white">פעילות אחרונה</h3>
              <Activity className="w-4 h-4 text-slate-500" />
            </div>
            <div className="space-y-3">
              {recentActivity.map((activity, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.1 }}
                  className="flex items-center gap-3 p-3 rounded-xl bg-white/[0.02] border border-white/5"
                >
                  <div className={`w-2 h-2 rounded-full ${
                    activity.type === "relationship" ? "bg-purple-400" :
                    activity.type === "search" ? "bg-blue-400" :
                    activity.type === "update" ? "bg-amber-400" : "bg-green-400"
                  }`} />
                  <div className="flex-1 min-w-0">
                    <div className="text-sm text-slate-300 truncate">
                      <span className="text-slate-500">{activity.action}: </span>
                      {activity.target}
                    </div>
                    <div className="text-xs text-slate-500">{activity.time}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>

      {/* Torah Figures Preview — REAL DATA */}
      <motion.div variants={itemVariants} className="mt-8">
        <div className="p-6 bg-gradient-to-br from-amber-500/5 to-orange-500/5 border border-amber-500/10 rounded-2xl backdrop-blur-sm">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h3 className="text-xl font-bold text-white mb-1">אישי התנ"ך</h3>
              <p className="text-slate-400 text-sm">{loading ? "טוען..." : `${stats.people} דמויות, נביאים, מלכים, ושופטים`}</p>
            </div>
            <Link href="/dashboard/people">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="flex items-center gap-2 px-4 py-2 bg-amber-500/10 text-amber-400 rounded-xl border border-amber-500/20 hover:bg-amber-500/20 transition-colors"
              >
                <span className="text-sm">צפה הכל</span>
                <ArrowUpRight className="w-4 h-4" />
              </motion.button>
            </Link>
          </div>

          {loading ? (
            <div className="flex items-center justify-center py-12">
              <Loader2 className="w-8 h-8 text-amber-500 animate-spin" />
            </div>
          ) : (
            <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
              {people.map((person: any, i: number) => (
                <Link key={person.ref} href={`/dashboard/people`}>
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: i * 0.05 }}
                    whileHover={{ scale: 1.05, y: -2 }}
                    className="flex flex-col items-center p-4 bg-white/[0.03] border border-white/5 rounded-xl hover:bg-white/[0.07] hover:border-white/10 transition-all cursor-pointer"
                  >
                    <div className="w-12 h-12 bg-gradient-to-br from-amber-500/20 to-orange-500/20 rounded-full flex items-center justify-center mb-2">
                      <Users className="w-5 h-5 text-amber-400" />
                    </div>
                    <div className="text-sm font-medium text-white truncate w-full text-center">{person.name}</div>
                    <div className="text-[10px] text-slate-500">{person.role}</div>
                  </motion.div>
                </Link>
              ))}
            </div>
          )}
        </div>
      </motion.div>
    </motion.div>
  );
}
