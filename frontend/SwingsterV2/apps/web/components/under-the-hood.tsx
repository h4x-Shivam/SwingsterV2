"use client";

import React from "react";
import { motion } from "motion/react";
import { BorderGlow } from "@/components/ui/border-glow";

const stages = [
  {
    title: "Data Ingestion",
    subtitle: "2,000+ NSE Tickers",
    description: "Fetches live OHLCV price action, volume profiles, and real-time fundamental data directly from the National Stock Exchange.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="17 8 12 3 7 8"></polyline><line x1="12" y1="3" x2="12" y2="15"></line></svg>
    ),
    color: "from-blue-500 to-cyan-400",
    shadow: "shadow-[0_0_30px_rgba(56,189,248,0.2)]"
  },
  {
    title: "Trend Confirmation",
    subtitle: "Minervini Stage 2 Filter",
    description: "Harshly rejects any stock not in a confirmed, long-term institutional uptrend. We only trade assets with the wind at their back.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline><polyline points="16 7 22 7 22 13"></polyline></svg>
    ),
    color: "from-emerald-400 to-green-500",
    shadow: "shadow-[0_0_30px_rgba(16,185,129,0.2)]"
  },
  {
    title: "Quantitative Geometry",
    subtitle: "Algorithmic Pattern Engine",
    description: "Calculates precise moving average compressions, volatility contraction layers (VCP), and volume dry-up signatures to pinpoint exact breakout pivots.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 7 12 12 22 7 12 2"></polygon><polyline points="2 17 12 22 22 17"></polyline><polyline points="2 12 12 17 22 12"></polyline></svg>
    ),
    color: "from-purple-500 to-indigo-500",
    shadow: "shadow-[0_0_30px_rgba(168,85,247,0.2)]"
  },
  {
    title: "Qualitative Verdict",
    subtitle: "The Groq AI Judge",
    description: "A specialized AI agent acts as your co-pilot, evaluating Risk:Reward ratios, reading context, filtering false positives, and assigning a final High/Medium Conviction score.",
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path></svg>
    ),
    color: "from-rose-500 to-red-500",
    shadow: "shadow-[0_0_30px_rgba(244,63,94,0.2)]"
  }
];

export function UnderTheHood() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-6">
        <div className="text-center mb-20">
          <div className="inline-flex items-center gap-2 rounded-full border border-white/10 bg-white/5 px-4 py-1.5 mb-6">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-white/40"><circle cx="12" cy="12" r="3"></circle><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"></path></svg>
            <span className="text-xs font-medium text-white/60 tracking-widest uppercase">
              The Engine
            </span>
          </div>
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white tracking-tight leading-tight">
            Under the hood of <br/>
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-white to-white/40">Institutional Edge</span>
          </h2>
        </div>

        <div className="relative">
          {/* Vertical Line */}
          <div className="absolute left-[31px] md:left-1/2 top-0 bottom-0 w-[2px] bg-gradient-to-b from-transparent via-white/10 to-transparent transform md:-translate-x-1/2" />

          <div className="flex flex-col gap-12 md:gap-24">
            {stages.map((stage, index) => {
              const isEven = index % 2 === 0;
              return (
                <div key={index} className="relative flex flex-col md:flex-row items-center w-full">
                  
                  {/* Timeline Dot */}
                  <div className="absolute left-[32px] md:left-1/2 transform -translate-x-1/2 w-4 h-4 rounded-full bg-[#060608] border-[3px] border-emerald-500 z-10 shadow-[0_0_15px_rgba(16,185,129,0.5)]" />

                  {/* Desktop Content (Alternating sides) */}
                  <motion.div 
                    initial={{ opacity: 0, x: isEven ? -50 : 50 }}
                    whileInView={{ opacity: 1, x: 0 }}
                    viewport={{ once: true, margin: "-10%" }}
                    transition={{ duration: 0.6, delay: 0.1, ease: "easeOut" }}
                    className={`w-full md:w-1/2 pl-20 md:px-12 flex ${isEven ? "md:justify-end md:text-right" : "md:justify-start md:order-last"}`}
                  >
                    <BorderGlow
                      className="w-full max-w-sm"
                      innerClassName="p-6 md:p-8 bg-[#121216]/80 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-colors w-full h-full text-left rounded-2xl"
                      edgeSensitivity={30}
                      glowColor={
                        index === 0 ? "56 189 248" :
                        index === 1 ? "16 185 129" :
                        index === 2 ? "168 85 247" :
                        "244 63 94"
                      }
                      backgroundColor="#121216"
                      borderRadius={16}
                      glowRadius={40}
                      glowIntensity={0.6}
                      coneSpread={20}
                      animated={true}
                      fillOpacity={0.05}
                    >
                      <div className={`inline-flex items-center justify-center w-12 h-12 rounded-xl bg-gradient-to-br ${stage.color} text-white mb-6 ${isEven ? "md:float-right md:ml-6" : "mb-6"}`}>
                        {stage.icon}
                      </div>
                      <div className="clear-both" />
                      <h3 className="text-xl font-bold text-white mb-3">
                        {stage.title}
                      </h3>
                      <p className="text-sm text-white/60 leading-relaxed">
                        {stage.description}
                      </p>
                    </BorderGlow>
                  </motion.div>

                  {/* Empty space for alternating layout */}
                  <div className={`hidden md:block w-1/2 ${isEven ? "order-last" : ""}`} />
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
