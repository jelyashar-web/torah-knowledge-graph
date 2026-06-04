import { NextRequest, NextResponse } from "next/server";

const OLLAMA_HOST = process.env.OLLAMA_HOST || "http://localhost:11434";

export async function POST(req: NextRequest) {
  try {
    const body = await req.json();
    const { messages, model = "llama3.1:8b" } = body;

    // Try /api/chat first
    let res = await fetch(`${OLLAMA_HOST}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, messages, stream: false }),
    });

    if (res.ok) {
      const data = await res.json();
      return NextResponse.json({ response: data.message?.content || data.response });
    }

    // Fallback to /api/generate
    const prompt = messages.map((m: any) => `${m.role}: ${m.content}`).join("\n");
    res = await fetch(`${OLLAMA_HOST}/api/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ model, prompt, stream: false }),
    });

    if (!res.ok) {
      const err = await res.text();
      return NextResponse.json({ error: `Ollama error: ${err}` }, { status: 502 });
    }

    const data = await res.json();
    return NextResponse.json({ response: data.response });
  } catch (e: any) {
    return NextResponse.json({ error: e.message }, { status: 500 });
  }
}
