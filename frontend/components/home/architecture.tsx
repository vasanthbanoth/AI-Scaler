export function ArchitectureSection() {
  return (
    <section id="stack" className="section-pad border-t border-slate-100">
      <div className="container-page">
        <p className="eyebrow">Under the hood</p>
        <h2 className="mt-3 text-3xl font-bold tracking-tight">Stack</h2>
        <p className="mt-3 max-w-xl text-slate-600">
          Ingest once, serve on web and phone. No duplicate logic between channels.
        </p>
        <div className="mt-10 grid gap-5 md:grid-cols-3">
          {[
            { title: "Frontend", items: ["Next.js 15", "Tailwind", "Vercel"] },
            { title: "Backend", items: ["FastAPI", "Hybrid RAG", "Cal.com v2", "Vapi webhooks"] },
            { title: "ML / Data", items: ["BGE embeddings", "BM25 + vectors", "Groq / OpenAI"] },
          ].map((col) => (
            <div key={col.title} className="card-elevated p-6">
              <h3 className="font-semibold text-slate-900">{col.title}</h3>
              <ul className="mt-4 space-y-2 text-sm text-slate-600">
                {col.items.map((item) => (
                  <li key={item}>· {item}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
