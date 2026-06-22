"use client";

import React, { useRef } from "react";
import { motion, useInView } from "motion/react";
import { Database, TrendingUp, Layers, ShieldCheck } from "lucide-react";
import { BorderGlow } from "@/components/ui/border-glow";

const stages = [
  {
    num: "01",
    icon: <Database className="w-5 h-5 text-emerald-400" />,
    title: "Data Ingestion",
    body: "Live OHLCV price data, volume profiles, and market breadth pulled directly from yfinance.",
    stat: "· 2,000+ NSE symbols processed",
    align: "left",
  },
  {
    num: "02",
    icon: <TrendingUp className="w-5 h-5 text-emerald-400" />,
    title: "Multi-stage Filtering Funnel",
    body: "Eliminated: majority of market tickers based on predefined criteria.",
    stat: "· ~70% of tickers eliminated",
    align: "right",
  },
  {
    num: "03",
    icon: <Layers className="w-5 h-5 text-emerald-400" />,
    title: "Pattern Detection",
    body: "Mathematical detection of VCP, Cup & Handle, Flag & Pole. Multiple pattern algorithms running.",
    stat: "· Custom pattern engine active",
    align: "left",
  },
  {
    num: "04",
    icon: <ShieldCheck className="w-5 h-5 text-emerald-400" />,
    title: "AI Judge",
    body: "Specialized LLM agent reviews setups. Prioritizes best opportunities for dashboard delivery.",
    stat: "· Best setups surfaced",
    align: "right",
  },
];

export function UnderTheHood() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: "-100px 0px" });

  const headingText = "Under the Hood of Institutional Edge".split(" ");

  return (
    <section ref={containerRef} id="under-the-hood" className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden">
      {/* Background Radial Gradient */}
      <div 
        className="absolute inset-0 pointer-events-none"
        style={{
          background: "radial-gradient(ellipse 60% 50% at 15% 20%, rgba(26, 147, 111, 0.18) 0%, transparent 70%)"
        }}
      />
      


      <div className="relative z-10 max-w-5xl mx-auto px-6">
        
        {/* Header */}
        <div className="flex flex-col items-center text-center mb-20 md:mb-28">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={isInView ? { opacity: 1, scale: 1 } : {}}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-4 py-1.5 mb-6"
          >
            <span className="text-sm">⚙</span>
            <span className="text-xs font-medium text-emerald-400 tracking-widest uppercase">
              THE ENGINE
            </span>
          </motion.div>

          <h2 className="text-3xl md:text-5xl lg:text-6xl font-bold text-white tracking-tight flex flex-wrap justify-center gap-[0.25em]">
            {headingText.map((word, i) => (
              <motion.span
                key={i}
                initial={{ opacity: 0, y: 20 }}
                animate={isInView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.5, delay: i * 0.1 }}
                className="whitespace-nowrap"
              >
                {word}
              </motion.span>
            ))}
          </h2>
        </div>

        {/* Timeline Layout */}
        <div className="relative w-full max-w-4xl mx-auto">
          
          {/* Vertical Dotted Line */}
          <motion.div 
            initial={{ opacity: 0 }}
            animate={isInView ? { opacity: 1 } : {}}
            transition={{ duration: 0.8 }}
            className="absolute left-6 md:left-1/2 top-0 bottom-16 w-[2px] border-l-[2px] border-dotted border-emerald-500 md:-translate-x-1/2 z-0"
          />

          {/* Timeline Nodes & Cards */}
          <div className="relative z-10 flex flex-col gap-12 md:gap-20">
            {stages.map((stage, idx) => {
              const isLeft = stage.align === "left";
              
              return (
                <div key={idx} className={`relative flex w-full md:items-center ${isLeft ? "md:justify-start" : "md:justify-end"}`}>
                  
                  {/* Node Circle */}
                  <div className="absolute top-0 md:top-1/2 left-6 md:left-1/2 transform -translate-x-1/2 md:-translate-y-1/2 w-9 h-9 md:w-10 md:h-10 rounded-full bg-[#0a0a0c] border-2 border-emerald-500 flex items-center justify-center z-20">
                    <motion.span 
                      initial={{ opacity: 0 }}
                      animate={isInView ? { opacity: 1 } : {}}
                      transition={{ duration: 0.3, delay: idx * 0.12 }}
                      className="text-white text-xs md:text-sm font-mono font-bold"
                    >
                      {stage.num}
                    </motion.span>
                  </div>

                  {/* Horizontal Connector Line (Mobile) */}
                  <div className="md:hidden absolute top-[18px] left-6 w-8 border-t-[2px] border-dotted border-emerald-500 z-0" />

                  {/* Horizontal Connector Line (Desktop) */}
                  <div className={`hidden md:block absolute top-1/2 transform -translate-y-1/2 w-8 lg:w-12 border-t-[2px] border-dotted border-emerald-500 z-0 ${isLeft ? "right-[50%]" : "left-[50%]"}`} />

                  {/* Card Container */}
                  <div className={`w-full pl-16 md:pl-0 md:w-1/2 flex ${isLeft ? "md:justify-end md:pr-8 lg:pr-12" : "md:justify-start md:pl-8 lg:pl-12"}`}>
                    <motion.div
                      initial={{ opacity: 0, x: isLeft ? -20 : 20 }}
                      animate={isInView ? { opacity: 1, x: 0 } : {}}
                      transition={{ duration: 0.4, delay: idx * 0.12, ease: "easeOut" }}
                      className="w-full max-w-[420px] transition-transform hover:-translate-y-1"
                    >
                      <BorderGlow
                        className="w-full shadow-[0_4px_30px_rgba(0,0,0,0.1)]"
                        innerClassName="p-6 bg-[#121215]/80 backdrop-blur-md flex flex-col gap-2 h-full"
                        edgeSensitivity={30}
                        glowColor="160 84 39"
                        backgroundColor="#121215"
                        borderRadius={16}
                        glowRadius={30}
                        glowIntensity={1.0}
                        coneSpread={25}
                        animated={false}
                        colors={['#34d399', '#10b981', '#059669']}
                        fillOpacity={0.05}
                      >
                        <div className="flex items-center gap-2 mb-1">
                          {stage.icon}
                          <h3 className="text-white font-semibold text-lg">{stage.title}</h3>
                        </div>
                        <p className="text-white/60 text-sm leading-relaxed mb-1">
                          {stage.body}
                        </p>
                        <div className="pt-3 mt-1 border-t border-white/[0.04]">
                          <span className="text-xs font-mono text-emerald-400/80">{stage.stat}</span>
                        </div>
                      </BorderGlow>
                    </motion.div>
                  </div>

                </div>
              )
            })}
          </div>


        </div>
      </div>
    </section>
  );
}
