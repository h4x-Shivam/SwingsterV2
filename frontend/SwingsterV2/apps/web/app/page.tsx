import { HeroSection } from "@/components/hero-section";
import { PatternShowcase } from "@/components/pattern-showcase";
import { LiquidEther } from "@/components/ui/liquid-ether";

export default function Page() {
  return (
    <main className="bg-surface min-h-screen relative">
      {/* ── Global Liquid Ether Background ── */}
      <div className="fixed inset-0 z-0 opacity-60 mix-blend-screen pointer-events-none">
        <LiquidEther
          colors={['#10b981', '#10b981', '#ef4444']}
          mouseForce={30}
          cursorSize={150}
          isViscous={true}
          viscous={25}
          resolution={0.4}
        />
      </div>

      <div className="relative z-10">
        <HeroSection />
        <PatternShowcase />
      </div>
    </main>
  );
}
