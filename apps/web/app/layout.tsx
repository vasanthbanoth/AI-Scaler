import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const jakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-sans",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Vasanth Banoth — AI Engineer",
  description:
    "Full-stack AI engineer portfolio with RAG-grounded chat, voice agent, and live interview booking.",
  openGraph: {
    title: "Vasanth Banoth — AI Engineer",
    description: "Ask about projects, stack, and experience — grounded in resume and GitHub.",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={jakarta.variable}>
      <body className="min-h-screen font-sans">{children}</body>
    </html>
  );
}
