"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from "recharts";
import { TrendingUp, BookOpen, Network, Users } from "lucide-react";
import { getGraphStats, getCategoryDistribution } from "@/lib/api";

const COLORS = ["#3b82f6", "#8b5cf6", "#22c55e", "#f59e0b", "#ef4444", "#14b8a6"];

export function AnalyticsDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [categories, setCategories] = useState<any[]>([]);

  useEffect(() => {
    const load = async () => {
      try {
        const s = await getGraphStats();
        setStats(s);
      } catch (e) {
        console.error(e);
      }

      try {
        const c = await getCategoryDistribution();
        setCategories(c);
      } catch (e) {
        console.error(e);
      }
    };
    load();
  }, []);

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: "פסוקים", value: stats?.verse_count?.low || 23206, icon: BookOpen, color: "text-blue-600" },
          { label: "פרקים", value: stats?.chapter_count?.low || 929, icon: TrendingUp, color: "text-purple-600" },
          { label: "ספרים", value: stats?.book_count?.low || 39, icon: Users, color: "text-green-600" },
          { label: "קשרים", value: "~2.8M", icon: Network, color: "text-amber-600" },
        ].map((card) => (
          <div key={card.label} className="bg-white dark:bg-slate-800 rounded-xl p-4 shadow-sm border border-slate-200 dark:border-slate-700">
            <div className="flex items-center justify-between">
              <card.icon className={`w-8 h-8 ${card.color}`} />
              <span className="text-2xl font-bold text-slate-900 dark:text-white">{card.value}</span>
            </div>
            <p className="text-sm text-slate-500 mt-2">{card.label}</p>
          </div>
        ))}
      </div>

      {/* Charts */}
      {categories.length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-bold mb-4 text-slate-900 dark:text-white">התפלגות לפי קטגוריה</h3>
            <ResponsiveContainer width="100%" height={250}>
              <BarChart data={categories}>
                <XAxis dataKey="category" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="count" fill="#3b82f6" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white dark:bg-slate-800 rounded-xl p-6 shadow-sm border border-slate-200 dark:border-slate-700">
            <h3 className="text-lg font-bold mb-4 text-slate-900 dark:text-white">פילוח קטגוריות</h3>
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={categories}
                  cx="50%"
                  cy="50%"
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="count"
                  label
                >
                  {categories.map((_: any, index: number) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  );
}
