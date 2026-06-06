import { NextResponse } from "next/server";

export const maxDuration = 60;
export const dynamic = "force-dynamic";
export const runtime = "nodejs";

const API = process.env.API_BASE_URL || "http://localhost:8000";

export async function POST(req: Request) {
  try {
    const { messages, session_id, id } = await req.json();
    const lastUser = [...(messages || [])].reverse().find((m) => m.role === "user");
    if (!lastUser?.content) {
      return NextResponse.json({ error: "No message provided" }, { status: 400 });
    }

    let res: Response;
    try {
      res = await fetch(`${API}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          message: lastUser.content,
          session_id: session_id || id || "web-default",
        }),
        cache: "no-store",
      });
    } catch {
      return NextResponse.json(
        { error: "Backend offline. Run ./scripts/start_all.sh in the project folder." },
        { status: 503 }
      );
    }

    const contentType = res.headers.get("content-type") || "";
    const raw = await res.text();

    if (!res.ok) {
      return NextResponse.json(
        { error: raw.slice(0, 300) || `Backend error (${res.status})` },
        { status: res.status }
      );
    }

    if (!contentType.includes("application/json")) {
      return NextResponse.json(
        { error: "Unexpected backend response. Restart with ./scripts/start_all.sh" },
        { status: 502 }
      );
    }

    const data = JSON.parse(raw) as { reply?: string; sources?: { source: string }[] };
    let text: string = data.reply || "No reply generated.";
    const sources = data.sources || [];
    if (sources.length) {
      const chips = sources.slice(0, 5).map((s) => `[${s.source}]`).join(" ");
      text += `\n\n---\n*Sources: ${chips}*`;
    }

    return new Response(text, {
      headers: { "Content-Type": "text/plain; charset=utf-8" },
    });
  } catch (e) {
    const msg = e instanceof Error ? e.message : "Chat request failed";
    return NextResponse.json({ error: msg }, { status: 500 });
  }
}
