import Link from "next/link";

export function CtaSection() {
  return (
    <section className="gradient-cta text-white">
      <div className="container-page py-16 text-center md:py-20">
        <h2 className="text-3xl font-bold tracking-tight md:text-4xl">
          Have a question? Ask the agent.
        </h2>
        <p className="mx-auto mt-4 max-w-lg text-[0.9375rem] leading-relaxed text-white/90">
          Dig into project details, stack choices, or book time — grounded answers, no fluff.
        </p>
        <Link href="/chat" className="btn-white mt-8">
          Open chat
        </Link>
      </div>
    </section>
  );
}
