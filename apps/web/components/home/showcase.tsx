import Link from "next/link";
import { ArrowRight } from "lucide-react";

const STEPS = [
  {
    num: "01",
    title: "Mail-InboxAI — production RAG",
    bullets: [
      "Unified IMAP inbox with Elasticsearch and Groq categorization",
      "Vector search over a knowledge base before every reply",
      "Bun/Elysia backend, React 19 dashboard",
    ],
    gradient: "gradient-card-purple",
    label: "github:Mail-InboxAI",
  },
  {
    num: "02",
    title: "Josh-AI-TASK — speech ML",
    bullets: [
      "Whisper-small fine-tuned on Hindi conversational audio",
      "WER evaluation on FLEURS with Devanagari cleanup",
      "Spelling taxonomy and synonym-tolerant scoring",
    ],
    gradient: "gradient-card-green",
    label: "github:Josh-AI-TASK",
  },
];

export function ShowcaseSection() {
  return (
    <section className="section-pad bg-slate-50">
      <div className="container-page">
        <p className="eyebrow">Selected work</p>
        <h2 className="mt-3 text-3xl font-bold tracking-tight md:text-[2.5rem]">
          Projects in the corpus
        </h2>
        <div className="mt-14 space-y-16">
          {STEPS.map((s) => (
            <div key={s.num} className="grid items-center gap-10 md:grid-cols-2">
              <div className={s.num === "02" ? "md:order-2" : ""}>
                <span className="text-sm font-medium text-slate-400">{s.num}</span>
                <h3 className="mt-2 text-2xl font-bold tracking-tight">{s.title}</h3>
                <ul className="mt-5 space-y-2.5 text-[0.9375rem] leading-relaxed text-slate-600">
                  {s.bullets.map((b) => (
                    <li key={b} className="flex gap-2">
                      <span className="text-blue-600">—</span>
                      {b}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/chat"
                  className="mt-6 inline-flex items-center gap-2 text-sm font-semibold text-slate-900 hover:underline"
                >
                  Ask about this project <ArrowRight className="h-4 w-4" />
                </Link>
              </div>
              <div
                className={`${s.gradient} flex min-h-[240px] items-center justify-center rounded-xl p-8 ${s.num === "02" ? "md:order-1" : ""}`}
              >
                <div className="rounded-lg bg-white/95 px-6 py-4 text-center shadow-card">
                  <p className="font-mono text-sm font-medium text-slate-800">{s.label}</p>
                  <p className="mt-1 text-xs text-slate-500">Indexed in RAG corpus</p>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
