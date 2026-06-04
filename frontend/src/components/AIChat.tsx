"use client";

import { useState, useRef, useEffect } from "react";
import { Send, Bot, User, Loader2, Zap, Server } from "lucide-react";
import { chatWithAI } from "@/lib/api";

interface Message {
  role: "user" | "assistant";
  content: string;
  provider?: string;
  timestamp: Date;
}

type Provider = "ollama" | "kimi";

const PROVIDERS: Record<Provider, { label: string; icon: typeof Zap; color: string; model: string }> = {
  ollama: { label: "Ollama (Local)", icon: Server, color: "from-green-600 to-teal-600", model: "llama3.1:8b" },
  kimi: { label: "Kimi K2.6", icon: Zap, color: "from-purple-600 to-pink-600", model: "kimi-k2-6" },
};

export function AIChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [provider, setProvider] = useState<Provider>("kimi");
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: Message = {
      role: "user",
      content: input.trim(),
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);

    const context = messages
      .slice(-4)
      .map((m) => `${m.role}: ${m.content}`)
      .join("\n");

    const result = await chatWithAI(userMsg.content, context, provider);

    const assistantMsg: Message = {
      role: "assistant",
      content: result.response,
      provider: result.provider,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, assistantMsg]);
    setLoading(false);
  };

  const activeProvider = PROVIDERS[provider];
  const ProviderIcon = activeProvider.icon;

  return (
    <div className="bg-white dark:bg-slate-800 rounded-xl shadow-lg border border-slate-200 dark:border-slate-700 overflow-hidden flex flex-col h-[500px]">
      {/* Header */}
      <div className={`px-4 py-3 bg-gradient-to-r ${activeProvider.color} flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          <ProviderIcon className="w-5 h-5 text-white" />
          <h3 className="font-bold text-white">Torah AI Chat</h3>
          <span className="text-xs text-white/70 bg-white/20 px-2 py-0.5 rounded-full">
            {activeProvider.label}
          </span>
        </div>

        {/* Provider Switcher */}
        <div className="flex gap-1">
          {(Object.keys(PROVIDERS) as Provider[]).map((p) => (
            <button
              key={p}
              onClick={() => setProvider(p)}
              className={`px-3 py-1 rounded-lg text-xs font-medium transition-all ${
                provider === p
                  ? "bg-white text-slate-900 shadow"
                  : "bg-white/20 text-white hover:bg-white/30"
              }`}
            >
              {PROVIDERS[p].label}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-slate-500 dark:text-slate-400 py-8">
            <Bot className="w-12 h-12 mx-auto mb-3 opacity-50" />
            <p>שאל אותי כל שאלה בתורה!</p>
            <p className="text-sm mt-1">למשל: "מה פירוש בראשית?" או "ספר לי על משה"</p>
            <div className="mt-4 flex gap-2 justify-center">
              <button
                onClick={() => {
                  setInput("מה פירוש הפסוק בראשית ברא אלהים?");
                }}
                className="px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-xs hover:bg-slate-200 transition-colors"
              >
                🤔 מה פירוש בראשית?
              </button>
              <button
                onClick={() => {
                  setInput("ספר לי על משה רבנו");
                }}
                className="px-3 py-1 bg-slate-100 dark:bg-slate-700 rounded-full text-xs hover:bg-slate-200 transition-colors"
              >
                📖 ספר לי על משה
              </button>
            </div>
          </div>
        )}

        {messages.map((msg, i) => (
          <div
            key={`${msg.role}-${i}-${msg.timestamp.getTime()}`}
            className={`flex gap-3 ${msg.role === "user" ? "flex-row-reverse" : ""}`}
          >
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
                msg.role === "user"
                  ? "bg-blue-100 dark:bg-blue-900"
                  : msg.provider === "kimi"
                  ? "bg-purple-100 dark:bg-purple-900"
                  : "bg-green-100 dark:bg-green-900"
              }`}
            >
              {msg.role === "user" ? (
                <User className="w-4 h-4 text-blue-600" />
              ) : msg.provider === "kimi" ? (
                <Zap className="w-4 h-4 text-purple-600" />
              ) : (
                <Bot className="w-4 h-4 text-green-600" />
              )}
            </div>
            <div
              className={`max-w-[80%] rounded-2xl px-4 py-2 text-sm ${
                msg.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-slate-100 dark:bg-slate-700 text-slate-900 dark:text-slate-100"
              }`}
              dir="auto"
            >
              <div className="whitespace-pre-wrap">{msg.content}</div>
              {msg.provider && msg.role === "assistant" && (
                <div className="mt-1 text-[10px] opacity-60">
                  {msg.provider === "kimi" ? "⚡ Kimi K2.6" : "🖥️ Ollama"}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
              {provider === "kimi" ? (
                <Zap className="w-4 h-4 text-purple-600 animate-pulse" />
              ) : (
                <Bot className="w-4 h-4 text-green-600" />
              )}
            </div>
            <div className="bg-slate-100 dark:bg-slate-700 rounded-2xl px-4 py-2">
              <Loader2 className="w-4 h-4 animate-spin" />
            </div>
          </div>
        )}

        <div ref={scrollRef} />
      </div>

      {/* Input */}
      <div className="px-4 py-3 border-t border-slate-200 dark:border-slate-700 bg-slate-50 dark:bg-slate-900">
        <div className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && handleSend()}
            placeholder={`שאל שאלה בתורה (${activeProvider.label})...`}
            className="flex-1 px-4 py-2 rounded-lg border border-slate-300 dark:border-slate-600 bg-white dark:bg-slate-800 text-sm outline-none focus:ring-2 focus:ring-blue-500"
            dir="rtl"
          />
          <button
            onClick={handleSend}
            disabled={loading}
            className={`px-4 py-2 text-white rounded-lg transition-colors disabled:opacity-50 bg-gradient-to-r ${activeProvider.color}`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}
