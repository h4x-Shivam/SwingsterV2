"use client";

import React from "react";
import { StickyScroll } from "@/components/ui/sticky-scroll-reveal";
import { patterns, type PatternData } from "@/data/patterns";

/* ── Pattern card shown on the right side of the StickyScroll ── */
function PatternCard({ pattern }: { pattern: PatternData }) {
  const [selected, setSelected] = React.useState(false);

  return (
    <div
      onClick={() => {
        setSelected(!selected);
        console.log(selected ? "Deselected pattern:" : "Selected pattern:", pattern.title);
      }}
      className={`pattern-card group relative flex h-full w-full cursor-pointer flex-col items-center justify-between p-6 transition-transform duration-300 ${
        selected ? "scale-[1.02]" : "hover:scale-[1.02]"
      }`}
      style={{ 
        background: "#0c0c10",
        borderColor: selected ? "#7C3AED" : undefined,
        boxShadow: selected ? "0 0 30px #7C3AED20" : undefined
      }}
    >
      {/* ── Glow ring on hover/select ── */}
      <div className={`pointer-events-none absolute inset-0 rounded-md transition-opacity duration-500 ${
        selected ? "opacity-100" : "opacity-0 group-hover:opacity-100"
      }`}
        style={{
          boxShadow: "inset 0 0 40px #7C3AED18, 0 0 60px #7C3AED10",
        }}
      />

      <div className="flex w-full flex-1 flex-col items-center justify-center">
        {/* ── Pattern name ── */}
        <span className="text-lg font-bold tracking-wide text-white/90 text-center leading-tight">
          {pattern.title}
        </span>

        {/* ── Signal badge ── */}
        <span className="mt-4 inline-flex items-center gap-1.5 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-[11px] font-semibold uppercase tracking-widest text-emerald-400">
          <span className="relative flex h-1.5 w-1.5">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-75" />
            <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
          </span>
          {pattern.signal}
        </span>

        {/* ── SVG illustration ── */}
        <svg
          viewBox={pattern.svgViewBox}
          className="mt-6 w-full max-w-[340px]"
          aria-hidden="true"
        >
          {/* Gradient area fill under the line */}
          <defs>
            <linearGradient
              id={`grad-${pattern.id}`}
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop offset="0%" stopColor="#7C3AED" stopOpacity={0.35} />
              <stop offset="100%" stopColor="#7C3AED" stopOpacity={0} />
            </linearGradient>
          </defs>

          {/* Area fill — close path at the bottom of the viewBox */}
          <path
            d={closePath(pattern.svgPath, pattern.svgViewBox)}
            fill={`url(#grad-${pattern.id})`}
          />

          {/* Main line */}
          <path
            d={pattern.svgPath}
            fill="none"
            stroke="#7C3AED"
            strokeWidth={2.5}
            strokeLinecap="round"
            strokeLinejoin="round"
            className="drop-shadow-[0_0_6px_#7C3AED80]"
          />
        </svg>
      </div>

      {/* ── Run Scan Button (Appears on selection) ── */}
      <div
        className={`w-full flex-shrink-0 transform overflow-hidden transition-all duration-500 ease-out ${
          selected
            ? "mt-6 max-h-[80px] translate-y-0 opacity-100"
            : "mt-0 max-h-0 translate-y-4 opacity-0"
        }`}
      >
        <button
          type="button"
          onClick={(e) => {
            e.stopPropagation();
            console.log("Running scan for:", pattern.title);
          }}
          className="relative flex w-full items-center justify-center gap-2 rounded-lg bg-gradient-to-r from-[#7C3AED] to-[#5B21B6] py-3.5 text-sm font-semibold tracking-wide text-white shadow-[0_0_20px_rgba(124,58,237,0.3)] transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_0_30px_rgba(124,58,237,0.6)] active:translate-y-0"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2" />
          </svg>
          RUN SCAN
        </button>
      </div>
    </div>
  );
}

/**
 * Close an SVG path along the bottom of its viewBox so we can fill the area
 * beneath the line with a gradient.
 */
function closePath(pathD: string, viewBox: string): string {
  const parts = viewBox.split(" ").map(Number);
  const vbWidth = parts[2] ?? 220;
  const vbHeight = parts[3] ?? 160;

  // Get the first M point's X
  const firstMatch = pathD.match(/M\s*([\d.]+)/);
  const firstX = firstMatch ? firstMatch[1] : "0";

  return `${pathD} L ${vbWidth} ${vbHeight} L ${firstX} ${vbHeight} Z`;
}

/* ── Build content array for StickyScroll from pattern data ── */
const stickyContent = patterns.map((p) => ({
  title: p.title,
  description: p.description,
  content: <PatternCard pattern={p} />,
}));

/* ── Slide 2 — Pattern Showcase section ── */
export function PatternShowcase() {
  return (
    <section
      id="pattern-showcase"
      className="relative w-full py-20 md:py-32"
      style={{ background: "#060606" }}
    >
      {/* ── Decorative top gradient divider ── */}
      <div
        className="pointer-events-none absolute inset-x-0 top-0 h-32"
        style={{
          background:
            "linear-gradient(to bottom, #060606 0%, transparent 100%)",
        }}
      />

      {/* ── Section header ── */}
      <div className="mx-auto max-w-5xl px-6 text-center mb-16">
        <div className="inline-flex items-center gap-2 rounded-full border border-[#7C3AED30] bg-[#7C3AED08] px-4 py-1.5 mb-6">
          <span
            className="h-2 w-2 rounded-full"
            style={{ background: "#7C3AED" }}
          />
          <span className="text-xs font-medium text-[#a78bfa] tracking-wide uppercase">
            Pattern Library
          </span>
        </div>
        <h2 className="text-3xl md:text-5xl font-bold text-white leading-tight">
          Detect the setups that{" "}
          <span
            className="bg-clip-text text-transparent"
            style={{
              backgroundImage: "linear-gradient(135deg, #7C3AED, #a78bfa)",
            }}
          >
            move markets
          </span>
        </h2>
        <p className="mt-4 text-base md:text-lg text-[#71717a] max-w-2xl mx-auto">
          Swingster scans thousands of charts in real-time, surfacing
          high-probability patterns the moment they form.
        </p>
      </div>

      {/* ── Sticky scroll content ── */}
      <div className="mx-auto max-w-6xl px-4">
        <StickyScroll content={stickyContent} />
      </div>
    </section>
  );
}
