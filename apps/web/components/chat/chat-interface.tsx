"use client";

import { useChat } from "@ai-sdk/react";
import { AnimatePresence, motion } from "framer-motion";
import { ChevronDown, FileText, Send } from "lucide-react";
import Image from "next/image";
import Link from "next/link";
import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import { Logo } from "@/components/ui/logo";
import { StatusBar } from "@/components/chat/status-bar";
import { cn } from "@/lib/utils";

const STARTERS = [
  "What did you build in Mail-InboxAI?",
  "Explain the Josh-AI-TASK WER pipeline.",
  "Why are you a fit for an AI engineer role?",
  "Book a 30-minute interview slot.",
];

function parseSources(content: string): { body: string; sources: string[] } {
  const apiMarker = "\n\n---\n*Sources:";
  let body = content;
  let sources: string[] = [];

  const apiIdx = content.indexOf(apiMarker);
  if (apiIdx !== -1) {
    body = content.slice(0, apiIdx).trim();
    const tail = content.slice(apiIdx + apiMarker.length);
    sources = tail
      .replace(/\*$/g, "")
      .split(/\[|\]/)
      .map((s) => s.trim())
      .filter((s) => s && !s.startsWith("Sources"));
  }

  const inline = body.match(/\[([\w:.-]+)\]/g);
  if (inline) {
    for (const m of inline) {
      const s = m.slice(1, -1);
      if (!sources.includes(s)) sources.push(s);
    }
  }

  return { body, sources };
}

export function ChatInterface() {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [expandedSources, setExpandedSources] = useState<Record<string, boolean>>({});

  const { messages, input, handleInputChange, handleSubmit, isLoading, error, append } =
    useChat({
      api: "/api/chat",
      id: "vasanth-hiring-chat",
      streamProtocol: "text",
      body: { session_id: "vasanth-hiring-chat" },
      onError: (err) => {
        console.error("Chat error:", err);
      },
      initialMessages: [{
        id: "welcome",
        role: "assistant",
        content:
          "I'm Vasanth's AI representative — ask about my projects, stack, or book an interview. Answers come from my resume and GitHub, with sources cited.",
      }],
    });

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading]);

  return (
    <div className="flex min-h-screen flex-col bg-slate-50">
      <header className="border-b border-slate-200 bg-white">
        <div className="container-page flex h-[4.25rem] items-center justify-between">
          <Logo />
          <StatusBar />
        </div>
      </header>

      <div className="container-page flex flex-1 flex-col py-8 md:py-10">
        <div className="mx-auto w-full max-w-2xl flex-1">
          <div className="overflow-hidden rounded-xl border border-slate-200 bg-white shadow-card">
            <div className="flex items-center justify-between border-b border-slate-100 bg-slate-50 px-5 py-3">
              <span className="text-sm font-semibold text-slate-800">Chat</span>
              <Link href="/" className="text-xs font-medium text-slate-500 hover:text-slate-800">
                Close
              </Link>
            </div>

            <div className="max-h-[60vh] space-y-5 overflow-y-auto p-5 md:max-h-[65vh]">
              <AnimatePresence initial={false}>
                {messages.map((m) => {
                  const parsed =
                    m.role === "assistant" ? parseSources(m.content) : { body: m.content, sources: [] };
                  const showSources = expandedSources[m.id] ?? true;

                  return (
                    <motion.div
                      key={m.id}
                      initial={{ opacity: 0, y: 8 }}
                      animate={{ opacity: 1, y: 0 }}
                      className={cn("flex gap-3", m.role === "user" && "flex-row-reverse")}
                    >
                      <div className="relative h-8 w-8 shrink-0 overflow-hidden rounded-full bg-slate-100">
                        {m.role === "assistant" ? (
                          <Image
                            src="https://avatars.githubusercontent.com/u/119746958?v=4"
                            alt="Vasanth Banoth"
                            fill
                            className="object-cover"
                          />
                        ) : (
                          <div className="flex h-full w-full items-center justify-center text-[10px] font-bold text-slate-500">
                            You
                          </div>
                        )}
                      </div>

                      <div className={cn("min-w-0 flex-1", m.role === "user" && "text-right")}>
                        <div
                          className={cn(
                            "inline-block max-w-[95%] rounded-2xl px-4 py-3 text-left text-sm leading-relaxed",
                            m.role === "user"
                              ? "rounded-tr-sm bg-slate-900 text-white"
                              : "rounded-tl-sm border border-slate-100 bg-slate-50 text-slate-800 prose-chat"
                          )}
                        >
                          {m.role === "assistant" ? (
                            <ReactMarkdown>{parsed.body}</ReactMarkdown>
                          ) : (
                            parsed.body
                          )}
                        </div>

                        {parsed.sources.length > 0 && (
                          <div className="mt-2 text-left">
                            <button
                              type="button"
                              onClick={() =>
                                setExpandedSources((s) => ({ ...s, [m.id]: !showSources }))
                              }
                              className="inline-flex items-center gap-1 text-xs text-slate-500 hover:text-slate-700"
                            >
                              <ChevronDown
                                className={cn("h-3 w-3 transition", showSources && "rotate-180")}
                              />
                              {showSources ? "Hide sources" : "Show sources"}
                            </button>
                            {showSources && (
                              <div className="mt-2 flex flex-wrap gap-2">
                                {parsed.sources.map((src) => (
                                  <span
                                    key={src}
                                    className="inline-flex items-center gap-1 rounded-md border border-slate-200 bg-white px-2 py-1 text-xs text-slate-600"
                                  >
                                    <FileText className="h-3 w-3" />
                                    {src}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>

              {isLoading && (
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <span className="flex gap-1">
                    {[0, 1, 2].map((i) => (
                      <span
                        key={i}
                        className="h-1.5 w-1.5 animate-bounce rounded-full bg-blue-600"
                        style={{ animationDelay: `${i * 120}ms` }}
                      />
                    ))}
                  </span>
                  Looking that up…
                </div>
              )}

              {error && (
                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
                  {error.message?.startsWith("<!DOCTYPE")
                    ? "Server error — run ./scripts/start_all.sh to restart, then try again."
                    : error.message}
                </div>
              )}
              <div ref={bottomRef} />
            </div>

            {messages.length <= 2 && (
              <div className="border-t border-slate-100 px-5 py-4">
                <p className="mb-2 text-xs text-slate-500">Try asking</p>
                <div className="flex flex-wrap gap-2">
                  {STARTERS.map((s) => (
                    <button
                      key={s}
                      type="button"
                      onClick={() => append({ role: "user", content: s })}
                      className="rounded-lg border border-slate-200 bg-white px-3 py-2 text-left text-xs text-slate-600 transition hover:border-blue-300 hover:bg-blue-50"
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex gap-2 border-t border-slate-200 p-4">
              <input
                value={input}
                onChange={handleInputChange}
                placeholder="Ask about a project or book time…"
                className="flex-1 rounded-lg border border-slate-200 px-4 py-3 text-sm outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={isLoading || !input.trim()}
                className="btn-primary shrink-0 px-4 disabled:opacity-40"
                aria-label="Send"
              >
                <Send className="h-4 w-4" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}
