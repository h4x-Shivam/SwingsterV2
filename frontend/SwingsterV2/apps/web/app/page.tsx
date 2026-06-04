import { HeroSection } from "@/components/hero-section";
import { PatternShowcase } from "@/components/pattern-showcase";

export default function Page() {
  return (
    <main className="bg-surface min-h-screen">
      <HeroSection />
      <PatternShowcase />
    </main>
  );
}
