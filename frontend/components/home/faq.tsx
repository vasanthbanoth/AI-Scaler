"use client";

import { useState } from "react";
import { ChevronDown } from "lucide-react";
import { cn } from "@/lib/utils";

const FAQS = [
  {
    q: "Where do answers come from?",
    a: "My resume and public GitHub READMEs — ingested into a searchable corpus. The agent cites [resume] or [github:RepoName] and won't invent details that aren't there.",
  },
  {
    q: "Can I book an interview?",
    a: "Yes. Chat and voice can pull live Cal.com slots and confirm a booking. Email works too: thevasanthbanoth@gmail.com.",
  },
  {
    q: "What makes this different from ChatGPT?",
    a: "Retrieval runs first. Hybrid BM25 + vector search, source labels, and explicit refusal when context is missing. It's scoped to my public work, not the open web.",
  },
  {
    q: "Which repos are indexed?",
    a: "Mail-InboxAI, Multi-Modal-RAG, Josh-AI-TASK, NewsScanAI-NLP, LogTrack, HirePath, and more — 12+ repos from github.com/vasanthbanoth.",
  },
];

export function FaqSection() {
  const [open, setOpen] = useState<number | null>(0);

  return (
    <section id="faq" className="section-pad bg-slate-50">
      <div className="container-page grid gap-12 md:grid-cols-[1fr_2fr]">
        <div>
          <h2 className="text-3xl font-bold tracking-tight">FAQ</h2>
          <p className="mt-3 text-sm text-slate-600">
            Common questions about how this agent works.
          </p>
          <a href="mailto:thevasanthbanoth@gmail.com" className="btn-secondary mt-6">
            Email me
          </a>
        </div>
        <div className="divide-y divide-slate-200 border-t border-slate-200">
          {FAQS.map((f, i) => (
            <div key={f.q}>
              <button
                type="button"
                onClick={() => setOpen(open === i ? null : i)}
                className="flex w-full items-center justify-between gap-4 py-5 text-left"
              >
                <span className="font-medium text-slate-900">{f.q}</span>
                <ChevronDown
                  className={cn("h-5 w-5 shrink-0 text-slate-400 transition", open === i && "rotate-180")}
                />
              </button>
              {open === i && (
                <p className="pb-5 text-sm leading-relaxed text-slate-600">{f.a}</p>
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
