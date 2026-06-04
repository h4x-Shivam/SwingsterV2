"use client";

import React from "react";
import { ContainerScroll } from "@/components/ui/container-scroll-animation";
import { HeroWatchlist } from "@/components/hero-watchlist";
import { LiquidEther } from "@/components/ui/liquid-ether";

export function HeroSection() {
  return (
    <section
      id="hero"
      className="relative w-full bg-surface overflow-hidden"
    >
      {/* ── Liquid Ether Background ── */}
      <div className="absolute inset-0 z-0 opacity-60 mix-blend-screen">
        <LiquidEther
          colors={['#7C3AED', '#00c896', '#5B21B6']}
          mouseForce={30}
          cursorSize={150}
          isViscous={true}
          viscous={25}
          resolution={0.4}
        />
      </div>

      <ContainerScroll
        titleComponent={
          <div className="flex flex-col items-center gap-5">
            {/* ── Badge ── */}
            <div className="inline-flex items-center gap-2 rounded-full border border-border-muted bg-surface-raised px-4 py-1.5 opacity-0 animate-fade-in-up">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-accent opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-accent" />
              </span>
              <span className="text-xs font-medium text-text-secondary tracking-wide">
                Live Pattern Detection
              </span>
            </div>

            {/* ── Headline ── */}
            <h1 className="text-center">
              <span className="block text-base md:text-lg text-text-muted font-medium opacity-0 animate-fade-in-up animation-delay-100">
                Unleash the power of
              </span>
              <span className="block text-5xl md:text-[6rem] font-bold text-text-primary leading-none mt-2 opacity-0 animate-fade-in-up animation-delay-200">
                SwingsterV2
              </span>
            </h1>
          </div>
        }
      >
        {/* ── Watchlist inside the MacBook frame ── */}
        <HeroWatchlist />
      </ContainerScroll>
    </section>
  );
}
