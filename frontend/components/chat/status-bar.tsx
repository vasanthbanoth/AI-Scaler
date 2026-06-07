"use client";

import { useEffect, useState } from "react";

type Health = {
  corpus_ready?: boolean;
  demo_mode?: boolean;
  chunks_loaded?: number;
  retrieval?: string;
  calendar_configured?: boolean;
};

export function StatusBar() {
  const [h, setH] = useState<Health | null>(null);

  useEffect(() => {
    const base = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
    fetch(`${base}/health`, { cache: "no-store" })
      .then((r) => r.json())
      .then(setH)
      .catch(() => setH(null));
  }, []);

  if (!h) return <span className="text-xs text-slate-400">Connecting…</span>;

  const label = h.corpus_ready ? "Full RAG" : h.demo_mode ? "Resume demo" : "No corpus";

  return (
    <div className="flex items-center gap-2 text-xs text-slate-500">
      <span
        className={
          h.corpus_ready
            ? "rounded-full bg-emerald-100 px-2 py-0.5 font-medium text-emerald-700"
            : "rounded-full bg-amber-100 px-2 py-0.5 font-medium text-amber-700"
        }
      >
        {label}
      </span>
      <span>{h.chunks_loaded ?? 0} chunks</span>
      {h.calendar_configured && <span>· Cal.com ✓</span>}
    </div>
  );
}
