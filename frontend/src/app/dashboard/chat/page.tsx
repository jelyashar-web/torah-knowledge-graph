"use client";

import { motion } from "framer-motion";
import { AIChat } from "@/components/AIChat";

export default function ChatPage() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      className="max-w-4xl mx-auto"
    >
      <AIChat />
    </motion.div>
  );
}
