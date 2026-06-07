import { Calendar, Database, Mic } from "lucide-react";

const BENEFITS = [
  {
    icon: Database,
    title: "Grounded in Real Experience",
    desc: "Ask questions and get answers based strictly on my documented experience, resume, and GitHub repositories.",
  },
  {
    icon: Mic,
    title: "Full Stack Expertise",
    desc: "Built using modern technologies like Next.js and FastAPI, demonstrating end-to-end development skills.",
  },
  {
    icon: Calendar,
    title: "Transparent & Accurate",
    desc: "The assistant provides factual information without inventing details, ensuring you get an accurate picture of my background.",
  },
];

export function BenefitsSection() {
  return (
    <section id="work" className="section-pad">
      <div className="container-page">
        <p className="eyebrow text-center">Key Features</p>
        <h2 className="mx-auto mt-3 max-w-2xl text-center text-3xl font-bold tracking-tight md:text-[2.5rem]">
          Interactive AI Assistant
        </h2>
        <div className="mt-14 grid gap-10 md:grid-cols-3">
          {BENEFITS.map((b) => (
            <div key={b.title} className="relative pl-6">
              <div className="absolute left-0 top-0 h-full w-px bg-slate-200" />
              <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
                <b.icon className="h-5 w-5 text-slate-700" />
              </div>
              <h3 className="text-lg font-semibold text-slate-900">{b.title}</h3>
              <p className="mt-2 text-[0.9375rem] leading-relaxed text-slate-600">{b.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
