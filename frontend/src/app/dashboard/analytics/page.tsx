"use client";

import { motion } from "framer-motion";
import { AnalyticsDashboard } from "@/components/AnalyticsDashboard";

export default function AnalyticsPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
    >
      <AnalyticsDashboard />
    </motion.div>
  );
}
