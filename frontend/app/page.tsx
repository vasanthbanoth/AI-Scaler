import { Header } from "@/components/layout/header";
import { Footer } from "@/components/layout/footer";
import { HeroSection } from "@/components/home/hero";
import { BenefitsSection } from "@/components/home/benefits";
import { ShowcaseSection } from "@/components/home/showcase";
import { ArchitectureSection } from "@/components/home/architecture";
import { FaqSection } from "@/components/home/faq";
import { CtaSection } from "@/components/home/cta";

export default function HomePage() {
  return (
    <>
      <Header />
      <main>
        <HeroSection />
        <BenefitsSection />
        <ShowcaseSection />
        <ArchitectureSection />
        <FaqSection />
        <CtaSection />
      </main>
      <Footer />
    </>
  );
}
