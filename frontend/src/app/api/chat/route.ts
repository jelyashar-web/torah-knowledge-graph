import { NextRequest, NextResponse } from "next/server";

const OLLAMA_HOST = process.env.OLLAMA_HOST || "http://localhost:11434";
const KIMI_BASE = process.env.KIMI_BASE_URL || "https://platform.kimi.ai/v1";
const KIMI_KEY = process.env.KIMI_API_KEY || "";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { messages, model, provider = "ollama" } = body;

    if (provider === "kimi") {
      // Kimi K2.6 via OpenAI-compatible API
      if (!KIMI_KEY) {
        return NextResponse.json(
          { error: "KIMI_API_KEY not configured" },
          { status: 500 }
        );
      }

      const res = await fetch(`${KIMI_BASE}/chat/completions`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${KIMI_KEY}`,
        },
        body: JSON.stringify({
          model: model || "kimi-k2-6",
          messages,
          temperature: 0.3,
          max_tokens: 4000,
        }),
      });

      if (!res.ok) {
        const err = await res.text();
        return NextResponse.json(
          { error: `Kimi error: ${err}` },
          { status: 502 }
        );
      }

      const data = await res.json();
      return NextResponse.json({
        response: data.choices?.[0]?.message?.content || "No response",
        provider: "kimi",
        model: data.model,
      });
    }

    // Default: Ollama
    const ollamaModel = model || "llama3.1:8b";

    // Try /api/chat first
    let res = await fetch(`${OLLAMA_HOST}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: ollamaModel, messages, stream: false }),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json({
        response: data.message?.content || data.response,
        provider: "ollama",
      });
    }

    // Fallback to /api/generate
    const prompt = messages.map((m: any) => `${m.role}: ${m.content}`).join("\n");
    res = await fetch(`${OLLAMA_HOST}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model: ollamaModel, prompt, stream: false }),
    });

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json(
        { error: `Ollama error: ${err}` },
        { status: 502 }
      );
    }

    const data = await res.json();
    return NextResponse.json({
      response: data.response,
      provider: "ollama",
    });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
