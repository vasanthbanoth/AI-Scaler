import Image from "next/image";
import Link from "next/link";
import { ArrowRight, FileText } from "lucide-react";

export function HeroSection() {
  return (
    <section className="gradient-hero text-white">
      <div className="container-page grid items-center gap-14 py-20 md:grid-cols-2 md:py-28">
        <div>
          <p className="eyebrow mb-5 text-blue-200/80">AI Engineer · RAG & voice systems</p>
          <h1 className="text-[2.5rem] font-bold leading-[1.08] tracking-tight md:text-5xl lg:text-[3.5rem]">
            Hi, I'm Vasanth Banoth
            <br />
            Full Stack Developer
          </h1>
          <p className="mt-6 max-w-md text-[1.0625rem] leading-relaxed text-slate-200">
            Welcome to my interactive portfolio. You can chat with my integrated AI assistant to learn more about my experience, projects, and skills.
          </p>
          <div className="mt-9 flex flex-wrap gap-3">
            <Link
              href="/chat"
              className="inline-flex items-center gap-2 rounded-lg bg-white px-6 py-3 text-sm font-semibold text-slate-900 transition hover:bg-slate-100"
            >
              Start a conversation
              <ArrowRight className="h-4 w-4" />
            </Link>
            <a
              href="https://github.com/vasanthbanoth"
              target="_blank"
              rel="noreferrer"
              className="btn-white"
            >
              GitHub
            </a>
          </div>
        </div>

        <div className="relative">
          <div className="overflow-hidden rounded-xl border border-white/10 bg-white shadow-float">
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-4 py-3">
              <span className="text-sm font-semibold text-slate-800">Chat preview</span>
              <span className="rounded-full bg-emerald-100 px-2 py-0.5 text-[11px] font-medium text-emerald-700">
                Live
              </span>
            </div>
            <div className="space-y-4 p-5">
              <div className="flex justify-end">
                <div className="max-w-[85%] rounded-2xl rounded-tr-sm bg-slate-900 px-4 py-3 text-sm text-white">
                  Walk me through Mail-InboxAI — stack and RAG tradeoffs.
                </div>
              </div>
              <div className="flex gap-3">
                <div className="relative h-8 w-8 shrink-0 overflow-hidden rounded-full">
                  <Image
                    src="https://avatars.githubusercontent.com/u/119746958?v=4"
                    alt="Vasanth Banoth"
                    fill
                    className="object-cover"
                  />
                </div>
                <div className="flex-1 space-y-2">
                  <div className="rounded-2xl rounded-tl-sm border border-slate-100 bg-slate-50 px-4 py-3 text-sm leading-relaxed text-slate-700">
                    Unified IMAP inbox with Elasticsearch indexing, Groq categorization, and RAG
                    over a knowledge base before reply generation. Bun/Elysia backend, React 19 UI.
                  </div>
                  <div className="flex flex-wrap gap-1.5">
                    {["github:Mail-InboxAI", "resume"].map((s) => (
                      <span
                        key={s}
                        className="inline-flex items-center gap-1 rounded-md bg-slate-100 px-2 py-1 text-[11px] text-slate-600"
                      >
                        <FileText className="h-3 w-3" />
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
