"use client";

import { useCallback, useEffect, useRef, useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
  sources?: { source: string; score: number }[];
  latency_ms?: number;
};

type Slot = { start: string; timezone?: string };

const STARTERS = [
  "Why is Vasanth a strong fit for Scaler's AI Engineer intern role?",
  "Walk me through Mail-InboxAI — stack and RAG design choices.",
  "What did you do differently in the Josh-AI-TASK Whisper pipeline?",
  "Show available interview slots this week.",
];

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: "assistant",
      content:
        "Hey — I'm Vasanth's AI rep. Ask about his resume, any public GitHub repo, or book a call. I only answer from ingested corpus; I won't invent project details.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [slots, setSlots] = useState<Slot[]>([]);
  const [bookOpen, setBookOpen] = useState(false);
  const [bookForm, setBookForm] = useState({
    start_iso: "",
    name: "",
    email: "",
    notes: "",
  });
  const bottomRef = useRef<HTMLDivElement>(null);

  const scrollDown = () =>
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });

  useEffect(() => {
    scrollDown();
  }, [messages, loading]);

  const loadSlots = useCallback(async () => {
    const res = await fetch("/api/slots");
    const data = await res.json();
    setSlots(data.slots || []);
    setBookOpen(true);
    if (data.slots?.[0]) {
      setBookForm((f) => ({ ...f, start_iso: data.slots[0].start }));
    }
  }, []);

  const send = async (text: string) => {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    if (/book|slot|availability|schedule|calendar/i.test(trimmed)) {
      await loadSlots();
    }

    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await fetch("/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: trimmed }),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || "Chat failed");
      }
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: data.reply,
          sources: data.sources?.map((s: { source: string; score: number }) => ({
            source: s.source,
            score: s.score,
          })),
          latency_ms: data.latency_ms,
        },
      ]);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Unknown error";
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content: `Backend isn't ready yet (${msg}). Deploy API + run ingest.py first.`,
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const confirmBook = async () => {
    const res = await fetch("/api/book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(bookForm),
    });
    const data = await res.json();
    setBookOpen(false);
    setMessages((m) => [
      ...m,
      {
        role: "assistant",
        content: res.ok
          ? `Booked ✓ — confirmation sent to ${bookForm.email} for ${bookForm.start_iso}.`
          : `Booking failed: ${data.detail || data.error || "check Cal.com keys"}`,
      },
    ]);
  };

  return (
    <main style={styles.shell}>
      <header style={styles.header}>
        <div>
          <h1 style={styles.title}>Vasanth Banoth</h1>
          <p style={styles.sub}>AI representative · RAG over resume + GitHub</p>
        </div>
        <div style={styles.links}>
          <a href="https://github.com/vasanthbanoth" target="_blank" rel="noreferrer">
            GitHub
          </a>
          <a href="https://vasanthdev.in" target="_blank" rel="noreferrer">
            Portfolio
          </a>
          <button type="button" style={styles.chipBtn} onClick={loadSlots}>
            Book call
          </button>
        </div>
      </header>

      <section style={styles.chat}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              ...styles.bubble,
              ...(m.role === "user" ? styles.userBubble : styles.aiBubble),
            }}
          >
            <div style={styles.role}>{m.role === "user" ? "You" : "AI rep"}</div>
            <div style={styles.content}>{m.content}</div>
            {m.sources && m.sources.length > 0 && (
              <div style={styles.sources}>
                Sources:{" "}
                {m.sources
                  .slice(0, 4)
                  .map((s) => `${s.source} (${s.score})`)
                  .join(" · ")}
              </div>
            )}
            {m.latency_ms != null && (
              <div style={styles.meta}>{m.latency_ms} ms end-to-end</div>
            )}
          </div>
        ))}
        {loading && <div style={styles.typing}>Thinking…</div>}
        <div ref={bottomRef} />
      </section>

      <div style={styles.starters}>
        {STARTERS.map((s) => (
          <button
            key={s}
            type="button"
            style={styles.starter}
            onClick={() => send(s)}
            disabled={loading}
          >
            {s}
          </button>
        ))}
      </div>

      <form
        style={styles.form}
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about a repo, resume, or role fit…"
          rows={2}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send(input);
            }
          }}
        />
        <button type="submit" style={styles.send} disabled={loading}>
          Send
        </button>
      </form>

      {bookOpen && (
        <div style={styles.modalBackdrop}>
          <div style={styles.modal}>
            <h3>Book interview (Cal.com)</h3>
            {slots.length === 0 ? (
              <p style={{ color: "var(--muted)" }}>
                No slots from API — configure CALCOM_* on backend.
              </p>
            ) : (
              <label>
                Slot
                <select
                  value={bookForm.start_iso}
                  onChange={(e) =>
                    setBookForm((f) => ({ ...f, start_iso: e.target.value }))
                  }
                  style={{ width: "100%", marginTop: 4 }}
                >
                  {slots.map((s) => (
                    <option key={s.start} value={s.start}>
                      {s.start}
                    </option>
                  ))}
                </select>
              </label>
            )}
            <input
              placeholder="Your name"
              value={bookForm.name}
              onChange={(e) => setBookForm((f) => ({ ...f, name: e.target.value }))}
            />
            <input
              placeholder="Email"
              type="email"
              value={bookForm.email}
              onChange={(e) =>
                setBookForm((f) => ({ ...f, email: e.target.value }))
              }
            />
            <textarea
              placeholder="Notes (optional)"
              value={bookForm.notes}
              onChange={(e) =>
                setBookForm((f) => ({ ...f, notes: e.target.value }))
              }
            />
            <div style={styles.modalActions}>
              <button type="button" onClick={() => setBookOpen(false)}>
                Cancel
              </button>
              <button type="button" style={styles.send} onClick={confirmBook}>
                Confirm booking
              </button>
            </div>
          </div>
        </div>
      )}
    </main>
  );
}

const styles: Record<string, React.CSSProperties> = {
  shell: {
    maxWidth: 820,
    margin: "0 auto",
    minHeight: "100vh",
    display: "flex",
    flexDirection: "column",
    padding: "1rem 1.25rem 1.5rem",
  },
  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    gap: "1rem",
    paddingBottom: "1rem",
    borderBottom: "1px solid var(--border)",
  },
  title: { margin: 0, fontSize: "1.35rem", fontWeight: 600 },
  sub: { margin: "0.25rem 0 0", color: "var(--muted)", fontSize: "0.9rem" },
  links: { display: "flex", gap: "0.75rem", alignItems: "center", fontSize: "0.9rem" },
  chipBtn: {
    background: "var(--panel)",
    border: "1px solid var(--accent-dim)",
    color: "var(--accent)",
    borderRadius: 999,
    padding: "0.35rem 0.85rem",
  },
  chat: {
    flex: 1,
    overflowY: "auto",
    padding: "1rem 0",
    display: "flex",
    flexDirection: "column",
    gap: "0.75rem",
  },
  bubble: {
    borderRadius: 12,
    padding: "0.75rem 1rem",
    border: "1px solid var(--border)",
  },
  userBubble: { background: "var(--user)", alignSelf: "flex-end", maxWidth: "92%" },
  aiBubble: { background: "var(--panel)", alignSelf: "flex-start", maxWidth: "96%" },
  role: {
    fontSize: "0.7rem",
    textTransform: "uppercase",
    letterSpacing: "0.06em",
    color: "var(--muted)",
    marginBottom: 4,
  },
  content: { lineHeight: 1.55, whiteSpace: "pre-wrap" },
  sources: { marginTop: 8, fontSize: "0.75rem", color: "var(--muted)" },
  meta: { marginTop: 4, fontSize: "0.7rem", color: "var(--accent-dim)" },
  typing: { color: "var(--muted)", fontSize: "0.9rem" },
  starters: {
    display: "flex",
    flexWrap: "wrap",
    gap: "0.5rem",
    marginBottom: "0.75rem",
  },
  starter: {
    background: "transparent",
    border: "1px solid var(--border)",
    color: "var(--muted)",
    borderRadius: 8,
    padding: "0.4rem 0.6rem",
    fontSize: "0.78rem",
    textAlign: "left",
  },
  form: {
    display: "grid",
    gridTemplateColumns: "1fr auto",
    gap: "0.5rem",
    alignItems: "end",
  },
  send: {
    background: "var(--accent-dim)",
    color: "#041018",
    border: "none",
    borderRadius: 8,
    padding: "0.65rem 1.1rem",
    fontWeight: 600,
  },
  modalBackdrop: {
    position: "fixed",
    inset: 0,
    background: "rgba(0,0,0,0.6)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    padding: "1rem",
  },
  modal: {
    background: "var(--panel)",
    border: "1px solid var(--border)",
    borderRadius: 12,
    padding: "1.25rem",
    width: "100%",
    maxWidth: 420,
    display: "flex",
    flexDirection: "column",
    gap: "0.6rem",
  },
  modalActions: { display: "flex", justifyContent: "flex-end", gap: "0.5rem" },
};
