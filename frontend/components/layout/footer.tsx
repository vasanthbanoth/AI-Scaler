import Link from "next/link";
import { Github, Mail } from "lucide-react";
import { Logo } from "@/components/ui/logo";

const FOOTER_LINKS = {
  Explore: [
    { href: "/chat", label: "Chat" },
    { href: "#work", label: "Work" },
    { href: "#stack", label: "Stack" },
  ],
  Projects: [
    { href: "https://github.com/vasanthbanoth/Mail-InboxAI", label: "Mail-InboxAI", external: true },
    { href: "https://github.com/vasanthbanoth/Multi-Modal-RAG", label: "Multi-Modal-RAG", external: true },
    { href: "https://github.com/vasanthbanoth/Josh-AI-TASK", label: "Josh-AI-TASK", external: true },
  ],
  Contact: [
    { href: "https://github.com/vasanthbanoth", label: "GitHub", external: true },
    { href: "mailto:thevasanthbanoth@gmail.com", label: "thevasanthbanoth@gmail.com", external: true },
  ],
};

export function Footer() {
  return (
    <footer className="bg-slate-950 text-slate-400">
      <div className="container-page section-pad">
        <div className="grid gap-10 md:grid-cols-[1.4fr_2fr]">
          <div>
            <Logo dark />
            <p className="mt-4 max-w-sm text-sm leading-relaxed">
              Full-stack AI engineer — RAG systems, speech ML, and production APIs.
              This site is the live demo.
            </p>
            <Link href="/chat" className="mt-5 inline-block text-sm font-medium text-white hover:underline">
              Open chat →
            </Link>
          </div>

          <div className="grid grid-cols-2 gap-8 sm:grid-cols-3">
            {Object.entries(FOOTER_LINKS).map(([title, links]) => (
              <div key={title}>
                <h4 className="mb-3 text-sm font-semibold text-white">{title}</h4>
                <ul className="space-y-2 text-sm">
                  {links.map((l) => (
                    <li key={l.label}>
                      {"external" in l && l.external ? (
                        <a href={l.href} target="_blank" rel="noreferrer" className="hover:text-white">
                          {l.label}
                        </a>
                      ) : (
                        <Link href={l.href} className="hover:text-white">
                          {l.label}
                        </Link>
                      )}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </div>

        <div className="mt-12 flex flex-wrap items-center justify-between gap-4 border-t border-slate-800 pt-6 text-xs">
          <p>© {new Date().getFullYear()} Vasanth Banoth</p>
          <div className="flex items-center gap-4">
            <a href="https://github.com/vasanthbanoth" target="_blank" rel="noreferrer" aria-label="GitHub">
              <Github className="h-4 w-4 hover:text-white" />
            </a>
            <a href="mailto:thevasanthbanoth@gmail.com" aria-label="Email">
              <Mail className="h-4 w-4 hover:text-white" />
            </a>
          </div>
        </div>
      </div>
    </footer>
  );
}
