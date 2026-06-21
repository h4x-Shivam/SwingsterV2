"use client";

import React, { useRef } from "react";
import { motion, useInView } from "motion/react";
import Link from "next/link";
import CountUp from "react-countup";

const tickers = [
  "RELIANCE", "TCS", "HDFCBANK", "INFY", "SBIN", "ITC", "LT", "ICICIBANK", 
  "BHARTIARTL", "AXISBANK", "ASIANPAINT", "BAJFINANCE", "NTPC", "TATAMOTORS", 
  "ONGC", "GRASIM", "ULTRACEMCO", "JSWSTEEL", "JIOFIN", "SUNPHARMA", "TECHM", 
  "WIPRO", "ADANIENT", "TITAN", "BEL", "IOC", "BPCL", "M&M"
];

const headlineText = "The Market Generates Noise. We Surface Opportunity.";
const headlineWords = headlineText.split(" ");

export function HowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);
  const isInView = useInView(containerRef, { once: true, margin: "-10%" });

  return (
    <section id="how-it-works" className="relative w-full pt-24 md:pt-32 bg-[#0a0a0a] overflow-hidden text-white flex flex-col items-center">
      {/* Background Grid */}
      <div className="absolute inset-0 z-0 pointer-events-none opacity-50" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px)', backgroundSize: '28px 28px' }} />
      
      {/* Faint green radial gradient behind funnel column ONLY */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-[rgba(26,147,111,0.06)] rounded-full blur-[80px] pointer-events-none z-0" />

      <div className="relative z-10 w-full max-w-7xl mx-auto px-6" ref={containerRef}>
        
        {/* Section Header */}
        <div className="text-center mb-20 md:mb-28 flex flex-col items-center">
           <h2 className="text-4xl md:text-6xl lg:text-[4rem] font-bold tracking-tight mb-8 max-w-5xl mx-auto flex flex-wrap justify-center gap-x-3 md:gap-x-4 gap-y-2 leading-tight">
              {headlineWords.map((word, i) => (
                 <motion.span
                   key={i}
                   initial={{ opacity: 0, y: 20 }}
                   animate={isInView ? { opacity: 1, y: 0 } : {}}
                   transition={{ duration: 0.5, delay: i * 0.04 }}
                   className={word.includes("Opportunity") ? "text-emerald-400 drop-shadow-[0_0_12px_rgba(16,185,129,0.4)]" : "text-white"}
                 >
                   {word}
                 </motion.span>
              ))}
           </h2>
           <motion.p
             initial={{ opacity: 0, y: 20 }}
             animate={isInView ? { opacity: 1, y: 0 } : {}}
             transition={{ duration: 0.6, delay: 0.5 }}
             className="text-base md:text-xl text-[#a1a1aa] max-w-3xl mx-auto leading-relaxed font-normal tracking-wide"
           >
              Every day, Swingster scans thousands of stocks,<br className="hidden md:block"/> filters out weak setups, and highlights only the<br className="hidden md:block"/> highest-conviction chart patterns.
           </motion.p>
        </div>

        {/* Three Columns */}
        <div className="flex flex-col md:flex-row gap-16 md:gap-8 lg:gap-12 relative items-stretch pb-16">
          
          {/* Column 1: SCAN EVERYTHING */}
          <div className="flex-1 flex flex-col relative z-10 pt-4 md:pt-0">
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="text-[10px] md:text-xs font-bold tracking-[0.2em] text-emerald-500 uppercase mb-4"
            >
              Scan Everything
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 0.9 }}
              className="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 leading-tight"
            >
              Every stock.<br/>Every day.
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 1.0 }}
              className="text-white/50 text-sm md:text-base mb-8"
            >
              No watchlists required.
            </motion.p>
            
            <div className="relative w-full flex-1 flex flex-wrap content-start gap-2 md:gap-3 opacity-70">
               {tickers.map((ticker, i) => (
                  <motion.span
                    key={ticker}
                    initial={{ opacity: 0 }}
                    animate={isInView ? { opacity: 0.5 } : {}}
                    transition={{ duration: 0.5, delay: 1.2 + (i * 0.03) }}
                    className={`text-[10px] md:text-xs font-mono bg-white/5 px-2 py-1 rounded border border-white/10 ${i > 9 ? 'hidden md:inline-block' : 'inline-block'}`}
                    style={{
                       animation: `float ${3 + (i % 3)}s ease-in-out infinite alternate`,
                       animationDelay: `${i * 0.1}s`
                    }}
                  >
                    {ticker}
                  </motion.span>
               ))}
               <motion.span 
                  initial={{ opacity: 0 }}
                  animate={isInView ? { opacity: 0.5 } : {}}
                  transition={{ duration: 0.5, delay: 1.2 + (tickers.length * 0.03) }}
                  className="text-[10px] md:text-xs font-mono text-emerald-500 mt-1 hidden md:inline-block w-full"
               >
                 ...AND 2,817 MORE
               </motion.span>
            </div>

            {/* Subtle Right Chevron */}
            <div className="hidden md:flex absolute right-0 top-1/2 -translate-y-1/2 text-white/10 pr-2 -mr-6">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </div>

          {/* Column 2: FILTER RUTHLESSLY */}
          <div className="flex-[1.2] flex flex-col items-center text-center relative z-20 md:border-x md:border-white/5 px-2 md:px-8">
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="text-[10px] md:text-xs font-bold tracking-[0.2em] text-emerald-500 uppercase mb-4"
            >
              Filter Ruthlessly
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 1.0 }}
              className="text-3xl md:text-4xl lg:text-5xl font-bold mb-12 leading-tight"
            >
              We remove<br/>the noise.
            </motion.h3>

            <div className="relative w-full max-w-[280px] mx-auto flex-1 flex flex-col items-center h-[380px]">
               {/* Funnel SVG Background */}
               <svg className="absolute inset-0 w-full h-full pointer-events-none" style={{ filter: "drop-shadow(0 0 8px rgba(26,147,111,0.6))" }} preserveAspectRatio="none" viewBox="0 0 200 400">
                  <motion.polygon 
                    points="0,0 200,0 130,380 70,380"
                    fill="rgba(10,10,10,0.8)"
                    stroke="#10b981"
                    strokeWidth="1.5"
                    initial={{ pathLength: 0, opacity: 0 }}
                    animate={isInView ? { pathLength: 1, opacity: 1 } : {}}
                    transition={{ duration: 1.5, delay: 1.4, ease: "easeInOut" }}
                  />
               </svg>
               
               {/* Funnel Content Layer */}
               <div className="relative z-10 w-full h-full flex flex-col items-center justify-between py-6">
                 
                 <div className="flex flex-col items-center">
                   <div className="text-2xl font-mono font-bold text-white">
                     {isInView ? <CountUp end={2847} duration={1} delay={1.8} separator="," useEasing /> : "0"}
                   </div>
                   <div className="text-[10px] text-white/50 uppercase tracking-wider mt-1">Stocks Scanned</div>
                 </div>

                 {/* Arrow 1 */}
                 <svg width="12" height="24" viewBox="0 0 12 24" fill="none">
                    <motion.path d="M6,0 L6,22 M2,18 L6,22 L10,18" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
                      initial={{ pathLength: 0, opacity: 0 }} animate={isInView ? { pathLength: 1, opacity: 1 } : {}} transition={{ duration: 0.4, delay: 2.6 }} />
                 </svg>

                 <div className="flex flex-col items-center">
                   <div className="text-xl font-mono font-bold text-white/90">
                     {isInView ? <CountUp end={312} duration={1} delay={2.2} separator="," useEasing /> : "0"}
                   </div>
                   <div className="text-[10px] text-white/50 uppercase tracking-wider mt-1">Potential Patterns</div>
                 </div>

                 {/* Arrow 2 */}
                 <svg width="12" height="24" viewBox="0 0 12 24" fill="none">
                    <motion.path d="M6,0 L6,22 M2,18 L6,22 L10,18" stroke="rgba(255,255,255,0.2)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
                      initial={{ pathLength: 0, opacity: 0 }} animate={isInView ? { pathLength: 1, opacity: 1 } : {}} transition={{ duration: 0.4, delay: 3.0 }} />
                 </svg>

                 <div className="flex flex-col items-center">
                   <div className="text-lg font-mono font-bold text-white/80">
                     {isInView ? <CountUp end={47} duration={1} delay={2.6} separator="," useEasing /> : "0"}
                   </div>
                   <div className="text-[10px] text-white/50 uppercase tracking-wider mt-1">Valid Patterns</div>
                 </div>

                 {/* Arrow 3 (Green) */}
                 <svg width="12" height="24" viewBox="0 0 12 24" fill="none">
                    <motion.path d="M6,0 L6,22 M2,18 L6,22 L10,18" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
                      initial={{ pathLength: 0, opacity: 0 }} animate={isInView ? { pathLength: 1, opacity: 1 } : {}} transition={{ duration: 0.4, delay: 3.4 }} />
                 </svg>

                 <div className="flex flex-col items-center pb-2">
                   <motion.div 
                     initial={{ scale: 0.8, textShadow: "none" }}
                     animate={isInView ? { scale: 1, textShadow: "0 0 20px rgba(16,185,129,0.8)" } : {}}
                     transition={{ duration: 0.5, delay: 3.8 }}
                     className="text-4xl font-mono font-black text-emerald-400"
                   >
                     {isInView ? <CountUp end={10} duration={1} delay={3.0} useEasing /> : "0"}
                   </motion.div>
                   <div className="text-[10px] text-emerald-400/80 uppercase tracking-widest font-bold mt-2">High-Conviction Setups</div>
                 </div>
                 
               </div>

               {/* Particle Emission */}
               <div className="absolute -bottom-8 left-1/2 -translate-x-1/2 w-[40px] h-[40px]">
                  {[...Array(4)].map((_, i) => (
                     <motion.div
                       key={i}
                       initial={{ opacity: 0, y: 0 }}
                       animate={isInView ? { opacity: [0, 1, 0], y: 30 } : {}}
                       transition={{ duration: 2, delay: 4.0 + i * 0.7, repeat: Infinity, ease: "linear" }}
                       className="absolute left-1/2 top-0 -translate-x-1/2 w-1.5 h-1.5 bg-emerald-400 rounded-full drop-shadow-[0_0_4px_rgba(16,185,129,0.8)]"
                     />
                  ))}
               </div>
            </div>

            {/* Subtle Right Chevron */}
            <div className="hidden md:flex absolute right-0 top-1/2 -translate-y-1/2 text-white/10 pr-2 -mr-6">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
            </div>
          </div>

          {/* Column 3: FOCUS INSTANTLY */}
          <div className="flex-1 flex flex-col md:items-end text-left md:text-right relative z-10 pt-8 md:pt-0">
            <motion.div
              initial={{ opacity: 0 }}
              animate={isInView ? { opacity: 1 } : {}}
              transition={{ duration: 0.5, delay: 0.8 }}
              className="text-[10px] md:text-xs font-bold tracking-[0.2em] text-emerald-500 uppercase mb-4"
            >
              Focus Instantly
            </motion.div>
            <motion.h3
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 1.1 }}
              className="text-3xl md:text-4xl lg:text-5xl font-bold mb-3 leading-tight"
            >
              See what<br/>deserves attention.
            </motion.h3>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.5, delay: 1.2 }}
              className="text-white/50 text-sm md:text-base mb-10"
            >
              Open the dashboard and<br className="hidden md:block"/> know what matters.
            </motion.p>

            {/* Terminal Card */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={isInView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.8, delay: 3.2 }}
              className="w-full max-w-[340px] md:max-w-none lg:max-w-[320px] bg-[#111113]/90 backdrop-blur-md border border-white/10 rounded-xl p-5 text-left font-mono relative overflow-hidden shadow-2xl mx-auto md:mx-0"
            >
              <div className="text-[10px] text-emerald-500 tracking-widest mb-5 font-bold">TOP CONVICTION SETUPS</div>
              
              <div className="flex flex-col gap-5">
                {/* Row 1 */}
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 3.4 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                     <div className="w-5 h-5 rounded-full bg-emerald-500/20 text-emerald-400 flex items-center justify-center text-[10px] border border-emerald-500/30">1</div>
                     <div>
                       <div className="text-white text-xs md:text-sm font-bold">ASHIANA</div>
                       <div className="text-[9px] md:text-[10px] text-white/40">VCP</div>
                     </div>
                  </div>
                  <div className="flex items-center gap-3 md:gap-4">
                     {/* Sparkline */}
                     <svg width="40" height="15" viewBox="0 0 40 15" fill="none">
                       <path d="M0,12 L10,10 L20,13 L30,5 L40,2" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                     </svg>
                     <div className="text-emerald-400 font-bold text-sm">92</div>
                  </div>
                </motion.div>

                {/* Row 2 */}
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 3.5 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                     <div className="w-5 h-5 rounded-full bg-white/5 text-white/60 flex items-center justify-center text-[10px] border border-white/10">2</div>
                     <div>
                       <div className="text-white text-xs md:text-sm font-bold">OBEROIRLTY</div>
                       <div className="text-[9px] md:text-[10px] text-white/40">CUP & HANDLE</div>
                     </div>
                  </div>
                  <div className="flex items-center gap-3 md:gap-4">
                     {/* Sparkline */}
                     <svg width="40" height="15" viewBox="0 0 40 15" fill="none">
                       <path d="M0,10 L10,12 L20,8 L30,6 L40,3" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                     </svg>
                     <div className="text-emerald-400/80 font-bold text-sm">89</div>
                  </div>
                </motion.div>

                {/* Row 3 */}
                <motion.div 
                  initial={{ opacity: 0, x: -10 }}
                  animate={isInView ? { opacity: 1, x: 0 } : {}}
                  transition={{ duration: 0.4, delay: 3.6 }}
                  className="flex items-center justify-between"
                >
                  <div className="flex items-center gap-3">
                     <div className="w-5 h-5 rounded-full bg-white/5 text-white/60 flex items-center justify-center text-[10px] border border-white/10">3</div>
                     <div>
                       <div className="text-white text-xs md:text-sm font-bold">PIDILITIND</div>
                       <div className="text-[9px] md:text-[10px] text-white/40">FLAG</div>
                     </div>
                  </div>
                  <div className="flex items-center gap-3 md:gap-4">
                     {/* Sparkline */}
                     <svg width="40" height="15" viewBox="0 0 40 15" fill="none">
                       <path d="M0,14 L10,11 L20,9 L30,7 L40,4" stroke="#10b981" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                     </svg>
                     <div className="text-emerald-400/70 font-bold text-sm">87</div>
                  </div>
                </motion.div>
              </div>

              <div className="mt-6 pt-4 border-t border-white/5 flex justify-end">
                <Link href="/dashboard" className="text-[10px] md:text-xs text-white/50 hover:text-emerald-400 transition-colors flex items-center gap-1 group">
                  View All 10 Setups
                  <svg className="transition-transform group-hover:translate-x-1" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m9 18 6-6-6-6"/></svg>
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </div>

      {/* Full-width Bottom Bar */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={isInView ? { opacity: 1, y: 0 } : {}}
        transition={{ duration: 0.8, delay: 3.8 }}
        className="w-full bg-[#111113] border-t border-white/10 py-6 px-6 md:px-12 flex items-center z-20 relative"
      >
        <div className="w-full max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
           <div className="flex items-center gap-3 text-white/90 font-medium">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500"><circle cx="12" cy="12" r="10"/><line x1="22" y1="12" x2="18" y2="12"/><line x1="6" y1="12" x2="2" y2="12"/><line x1="12" y1="6" x2="12" y2="2"/><line x1="12" y1="22" x2="12" y2="18"/></svg>
              <span>Less Noise. <span className="text-emerald-400">More Opportunity.</span></span>
           </div>
           
           <div className="text-white/40 text-sm text-center">
              Clarity. Confidence. Edge. <span className="text-white/60">That's Swingster.</span>
           </div>
           
           <Link 
              href="/dashboard"
              className="px-6 py-3 rounded-full border border-white/20 text-white text-sm font-bold hover:bg-emerald-500 hover:text-[#0a0a0a] hover:border-emerald-500 transition-all duration-300 flex items-center gap-2 group"
           >
              Explore Dashboard
           </Link>
        </div>
      </motion.div>

      {/* Required CSS for floating animation */}
      <style dangerouslySetInnerHTML={{__html: `
        @keyframes float {
          0% { transform: translateY(0px); }
          100% { transform: translateY(-6px); }
        }
      `}} />
    </section>
  );
}
