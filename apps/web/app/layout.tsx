import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Vasanth Banoth — AI Persona",
  description:
    "RAG-grounded chat with Vasanth's AI representative. Resume + GitHub corpus. Book interviews via Cal.com.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
