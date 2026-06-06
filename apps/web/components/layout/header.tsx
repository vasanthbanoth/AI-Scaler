import Link from "next/link";
import { Github } from "lucide-react";
import { Logo } from "@/components/ui/logo";

const LINKS = [
  { href: "#work", label: "Work" },
  { href: "#stack", label: "Stack" },
  { href: "#faq", label: "FAQ" },
];

export function Header() {
  const voicePhone = process.env.NEXT_PUBLIC_VOICE_PHONE;

  return (
    <header className="sticky top-0 z-50 border-b border-slate-200/80 bg-white/90 backdrop-blur-lg">
      <div className="container-page flex h-[4.25rem] items-center justify-between gap-6">
        <Logo />

        <nav className="hidden items-center gap-8 text-[0.9375rem] font-medium text-slate-600 md:flex">
          {LINKS.map((l) => (
            <Link key={l.href} href={l.href} className="transition hover:text-slate-900">
              {l.label}
            </Link>
          ))}
        </nav>

        <div className="flex items-center gap-2 sm:gap-3">
          <Link
            href="https://github.com/vasanthbanoth"
            target="_blank"
            className="hidden items-center gap-1.5 text-sm font-medium text-slate-600 hover:text-slate-900 sm:flex"
          >
            <Github className="h-4 w-4" />
            GitHub
          </Link>
          {voicePhone ? (
            <a href={`tel:${voicePhone}`} className="btn-secondary hidden sm:inline-flex">
              Call
            </a>
          ) : null}
          <Link href="/chat" className="btn-primary">
            Chat with AI
          </Link>
        </div>
      </div>
    </header>
  );
}
