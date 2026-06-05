"use client";

import { motion } from "framer-motion";
import { GraphQLExplorer } from "@/components/GraphQLExplorer";

export default function GraphQLPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-5xl mx-auto"
    >
      <GraphQLExplorer />
    </motion.div>
  );
}
