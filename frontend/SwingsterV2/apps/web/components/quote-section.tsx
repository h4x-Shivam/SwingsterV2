"use client";

import React from "react";
import { SplitText } from "@/components/ui/split-text";

import ScrambledText from "./ScrambledText";

export function QuoteSection() {
  return (
    <section className="relative w-full min-h-[80vh] flex items-center justify-center bg-transparent py-20 px-4 overflow-hidden">
      
      {/* Subtle radial gradient background behind the quote */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <div className="w-[800px] h-[500px] bg-emerald-500/5 rounded-full blur-[120px]" />
      </div>

      <div className="relative z-10 max-w-6xl mx-auto text-center">
        <SplitText 
          tag="h2"
          className="text-5xl md:text-7xl lg:text-[100px] font-bold tracking-tighter text-white/90 leading-[1.05]"
          delay={50}
          duration={0.8}
          ease="power3.out"
          splitType="words"
          from={{ opacity: 0, y: 30 }}
          to={{ opacity: 1, y: 0 }}
          threshold={0.1}
          rootMargin="-20%"
          text=""
          onLetterAnimationComplete={() => {}}
        >
          The market rewards <br className="hidden md:block" />
          those who <ScrambledText className="text-[#10b981] drop-shadow-[0_0_30px_rgba(16,185,129,0.3)]">spot patterns</ScrambledText> <br className="hidden md:block" />
          before the crowd.
        </SplitText>
      </div>
    </section>
  );
}
