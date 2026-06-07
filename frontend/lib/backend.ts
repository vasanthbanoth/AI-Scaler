/**
 * Server-only backend client. API keys stay in env — never import in client components.
 */

const API = typeof window !== "undefined" ? "" : (process.env.API_BASE_URL || "http://localhost:8000");

export type RagHit = {
  text: string;
  source: string;
  score: number;
  meta?: Record<string, unknown>;
};

export async function searchCorpus(query: string, k = 8): Promise<RagHit[]> {
  const res = await fetch(`${API}/rag/search`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, k }),
    cache: "no-store",
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`RAG search failed: ${err}`);
  }
  const data = await res.json();
  return data.results || [];
}

export async function getSlots(days = 7) {
  const res = await fetch(`${API}/calendar/slots?days=${days}`, { cache: "no-store" });
  return res.json();
}

export async function bookSlot(payload: {
  start_iso: string;
  name: string;
  email: string;
  notes?: string;
}) {
  const res = await fetch(`${API}/calendar/book`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || data.error || "Booking failed");
  return data;
}

export async function healthCheck() {
  const res = await fetch(`${API}/health`, { cache: "no-store" });
  return res.json();
}
