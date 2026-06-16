import { Navbar } from "@/components/navbar";
import { HeroSection } from "@/components/hero-section";
import { HowItWorks } from "@/components/how-it-works";
import { PatternShowcase } from "@/components/pattern-showcase";
import { UnderTheHood } from "@/components/under-the-hood";
import { PricingSection } from "@/components/pricing-section";
import { QuoteSection } from "@/components/quote-section";
import { AboutSection } from "@/components/about-section";
import { Footer } from "@/components/footer";
import { LiquidEther } from "@/components/ui/liquid-ether";
import { createClient } from "@/utils/supabase/server";

export default async function Page() {
  const supabase = await createClient();
  const { data: { session } } = await supabase.auth.getSession();
  const isAuthenticated = !!session;

  return (
    <main id="top" className="bg-surface min-h-screen relative">
      <Navbar isAuthenticated={isAuthenticated} />
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
        <HowItWorks />
        <PatternShowcase isAuthenticated={isAuthenticated} />
        <UnderTheHood />
        <PricingSection />
        <QuoteSection />
        <AboutSection />
        <Footer />
      </div>
    </main>
  );
}
