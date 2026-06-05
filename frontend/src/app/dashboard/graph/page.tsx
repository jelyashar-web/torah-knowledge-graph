"use client";

import { motion } from "framer-motion";
import { GraphExplorer } from "@/components/GraphExplorer";

export default function GraphPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="h-[calc(100vh-140px)] -m-6"
    >
      <GraphExplorer />
    </motion.div>
  );
}
