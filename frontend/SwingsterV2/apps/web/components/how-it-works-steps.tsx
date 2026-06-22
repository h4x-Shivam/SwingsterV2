"use client";

import React, { useRef } from "react";
import { motion, useInView } from "motion/react";
import { LayoutGrid, Zap, BarChart2, TrendingUp, ChevronRight, ShieldCheck, Star } from "lucide-react";

const VCP_PATH = "M 0 120 C 20 20 40 110 65 110 C 90 110 100 50 125 50 C 150 50 160 90 180 90 C 200 90 205 70 215 70 C 225 70 230 80 240 80 C 250 80 260 20 280 10";
const VCP_AREA = `${VCP_PATH} L 280 160 L 0 160 Z`;

const rawCandles = [
  {o: 15, c: 35, h: 10, l: 40},
  {o: 35, c: 50, h: 30, l: 55},
  {o: 50, c: 75, h: 45, l: 80},
  {o: 75, c: 90, h: 70, l: 95},
  {o: 90, c: 75, h: 70, l: 95},
  {o: 75, c: 55, h: 50, l: 80},
  {o: 55, c: 40, h: 35, l: 60},
  {o: 40, c: 50, h: 35, l: 55},
  {o: 50, c: 65, h: 45, l: 70},
  {o: 65, c: 50, h: 45, l: 70},
  {o: 50, c: 43, h: 40, l: 55},
  {o: 43, c: 50, h: 40, l: 55},
  {o: 50, c: 35, h: 30, l: 55},
  {o: 35, c: 20, h: 15, l: 40},
  {o: 20, c: 10, h: 5, l: 25},
];
const candles = rawCandles.map((c, i) => ({ ...c, x: 10 + i * 9.5 }));

export function HowItWorksSteps() {
  const containerRef = useRef(null);
  const isInView = useInView(containerRef, { once: true, margin: "-100px 0px" });

  const cardVariants: any = {
    hidden: { opacity: 0, y: 30 },
    visible: (i: number) => ({
      opacity: 1,
      y: 0,
      transition: {
        delay: 0.2 + i * 0.08,
        duration: 0.5,
        ease: "easeOut"
      }
    })
  };

  return (
    <section 
      ref={containerRef}
      id="how-to-scan"
      className="relative w-full py-24 md:py-32 overflow-hidden bg-transparent"
    >
      <div className="max-w-[1600px] mx-auto px-4 md:px-8">
        
        {/* ── 2. Header Block ── */}
        <div className="flex flex-col items-center text-center mb-16 md:mb-20">
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.4 }}
            className="inline-flex items-center gap-2 rounded-full border px-4 py-2 mb-6"
            style={{ backgroundColor: "#0F1714", borderColor: "rgba(45,212,191,0.3)" }}
          >
            <div className="w-1.5 h-1.5 rounded-full" style={{ backgroundColor: "#2DD4BF" }} />
            <span className="text-[12px] font-bold tracking-[0.12em] uppercase" style={{ color: "#2DD4BF" }}>
              How It Works
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={isInView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-4xl md:text-5xl lg:text-[64px] font-black leading-[1.1] tracking-[-0.02em] mb-5 font-sans"
          >
            <span style={{ color: "#FFFFFF" }}>Here's How to </span>
            <span style={{ color: "#2DD4BF" }}>Scan</span>
          </motion.h2>


        </div>

        {/* ── 3. Step Cards Row ── */}
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-6 md:gap-8 relative">
          
          {/* Connecting Arrows (Desktop Only) */}
          <div className="hidden xl:flex absolute top-1/2 left-[25%] -translate-x-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full items-center justify-center" style={{ backgroundColor: "#0A0E0D", border: "1px solid rgba(255,255,255,0.08)" }}>
             <ChevronRight size={16} color="#2DD4BF" />
          </div>
          <div className="hidden xl:flex absolute top-1/2 left-[50%] -translate-x-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full items-center justify-center" style={{ backgroundColor: "#0A0E0D", border: "1px solid rgba(255,255,255,0.08)" }}>
             <ChevronRight size={16} color="#2DD4BF" />
          </div>
          <div className="hidden xl:flex absolute top-1/2 left-[75%] -translate-x-1/2 -translate-y-1/2 z-10 w-8 h-8 rounded-full items-center justify-center" style={{ backgroundColor: "#0A0E0D", border: "1px solid rgba(255,255,255,0.08)" }}>
             <ChevronRight size={16} color="#2DD4BF" />
          </div>

          {/* ── STEP 1 ── */}
          <motion.div
            custom={0}
            variants={cardVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="group relative flex flex-col rounded-[20px] p-7 transition-all duration-300 hover:-translate-y-1"
            style={{ backgroundColor: "#0F1512", border: "1px solid rgba(255,255,255,0.08)" }}
          >
             <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[#2DD4BF]" style={{ backgroundColor: "rgba(45,212,191,0.15)" }}>
                  1
                </div>
                <LayoutGrid size={28} color="#2DD4BF" strokeWidth={1.5} />
             </div>
             <h3 className="text-xl font-bold text-white mb-2 leading-tight">Tap on the pattern card</h3>
             <p className="text-[14px] text-[#9CA3AF] leading-[1.6]">Browse the Pattern Library and select a setup you want to scan.</p>
             
             {/* Mockup Box */}
             <div className="mt-5 flex-1 rounded-xl p-4 flex flex-col relative overflow-hidden" style={{ backgroundColor: "#0B100E", border: "1px solid rgba(45,212,191,0.5)", boxShadow: "inset 0 0 20px rgba(45,212,191,0.05), 0 0 15px rgba(45,212,191,0.1)" }}>
                <div className="text-center font-bold text-[13px] text-white mb-2">VCP (Volatility Contraction Pattern)</div>
                <div className="mx-auto inline-flex items-center gap-1.5 rounded-full border border-[#2DD4BF]/30 bg-[#2DD4BF]/10 px-2 py-0.5 mb-6">
                  <div className="w-1.5 h-1.5 rounded-full bg-[#2DD4BF]" />
                  <span className="text-[9px] font-bold text-[#2DD4BF] uppercase tracking-wider">Bullish Continuation</span>
                </div>
                <div className="mt-auto h-[120px] w-full">
                   <svg width="100%" height="100%" viewBox="0 0 280 160" preserveAspectRatio="none">
                     <defs>
                       <linearGradient id="step1Grad" x1="0" y1="0" x2="0" y2="1">
                         <stop offset="0%" stopColor="rgba(45,212,191,0.25)" />
                         <stop offset="100%" stopColor="rgba(45,212,191,0)" />
                       </linearGradient>
                     </defs>
                     <path d={VCP_AREA} fill="url(#step1Grad)" />
                     <path d={VCP_PATH} fill="none" stroke="#2DD4BF" strokeWidth="2.5" />
                   </svg>
                </div>
             </div>
             
             {/* Carousel Dots */}
             <div className="flex justify-center gap-2 mt-5">
               <div className="w-4 h-1.5 rounded-full bg-[#2DD4BF]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
             </div>
          </motion.div>

          {/* ── STEP 2 ── */}
          <motion.div
            custom={1}
            variants={cardVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="group relative flex flex-col rounded-[20px] p-7 transition-all duration-300 hover:-translate-y-1 hover:border-[#2DD4BF]/50"
            style={{ backgroundColor: "#0F1512", border: "1px solid rgba(255,255,255,0.08)" }}
          >
             <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[#2DD4BF]" style={{ backgroundColor: "rgba(45,212,191,0.15)" }}>
                  2
                </div>
                <Zap size={28} color="#EF4444" strokeWidth={1.5} />
             </div>
             <h3 className="text-xl font-bold text-white mb-2 leading-tight">Tap on Run Scan</h3>
             <p className="text-[14px] text-[#9CA3AF] leading-[1.6]">Click Run Scan to search the market for stocks matching the selected pattern.</p>
             
             {/* Mockup Box */}
             <div className="mt-5 flex-1 rounded-xl p-4 flex flex-col relative overflow-hidden justify-between" style={{ backgroundColor: "#0B100E", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div>
                  <div className="text-center font-bold text-[13px] text-white mb-2">VCP (Volatility Contraction Pattern)</div>
                  <div className="mx-auto flex justify-center mb-4">
                    <div className="inline-flex items-center gap-1.5 rounded-full border border-[#2DD4BF]/30 bg-[#2DD4BF]/10 px-2 py-0.5">
                      <div className="w-1.5 h-1.5 rounded-full bg-[#2DD4BF]" />
                      <span className="text-[9px] font-bold text-[#2DD4BF] uppercase tracking-wider">Bullish Continuation</span>
                    </div>
                  </div>
                  <div className="h-[80px] w-full mb-4 opacity-50">
                     <svg width="100%" height="100%" viewBox="0 0 280 160" preserveAspectRatio="none">
                       <path d={VCP_AREA} fill="url(#step1Grad)" />
                       <path d={VCP_PATH} fill="none" stroke="#2DD4BF" strokeWidth="2.5" />
                     </svg>
                  </div>
                </div>
                
                <button className="w-full flex items-center justify-center gap-2 py-3 rounded-[10px] bg-[#DC2626] text-white font-bold text-[13px] tracking-wide uppercase shadow-[0_4px_14px_rgba(220,38,38,0.4)]">
                   <Zap size={16} fill="white" />
                   Run Scan
                </button>
             </div>
             
             {/* Carousel Dots */}
             <div className="flex justify-center gap-2 mt-5">
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-4 h-1.5 rounded-full bg-[#2DD4BF]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
             </div>
          </motion.div>

          {/* ── STEP 3 ── */}
          <motion.div
            custom={2}
            variants={cardVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="group relative flex flex-col rounded-[20px] p-7 transition-all duration-300 hover:-translate-y-1 hover:border-[#2DD4BF]/50"
            style={{ backgroundColor: "#0F1512", border: "1px solid rgba(255,255,255,0.08)" }}
          >
             <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[#2DD4BF]" style={{ backgroundColor: "rgba(45,212,191,0.15)" }}>
                  3
                </div>
                <BarChart2 size={28} color="#2DD4BF" strokeWidth={1.5} />
             </div>
             <h3 className="text-xl font-bold text-white mb-2 leading-tight">Tap on View Results</h3>
             <p className="text-[14px] text-[#9CA3AF] leading-[1.6]">Once scanning is complete, open the results dashboard to see ranked matches.</p>
             
             {/* Mockup Box */}
             <div className="mt-5 flex-1 rounded-xl p-4 flex flex-col relative overflow-hidden justify-between" style={{ backgroundColor: "#0B100E", border: "1px solid rgba(255,255,255,0.05)" }}>
                <div>
                  <div className="text-[10px] text-[#2DD4BF] font-bold tracking-widest uppercase mb-4">Live Results // VCP</div>
                  
                  <div className="flex justify-between text-[8px] text-[#6B7280] font-bold tracking-wider mb-2 px-1">
                    <span className="w-[15%]">RANK</span>
                    <span className="w-[35%]">TICKER</span>
                    <span className="w-[20%] text-center">SCORE</span>
                    <span className="w-[30%] text-right">RISK:REWARD</span>
                  </div>
                  
                  <div className="flex flex-col gap-3">
                    {[
                      {r: 1, t: 'BHEL', s: 87, rr: '0.6 : 1', gold: true},
                      {r: 2, t: 'BHAGYANGR', s: 86, rr: '0.6 : 1'},
                      {r: 3, t: 'KIRLPNU', s: 93, rr: '0.6 : 1'},
                      {r: 4, t: 'BHARATGEAR', s: 92, rr: '0.6 : 1'},
                    ].map((row, i) => (
                      <div key={i} className="flex items-center justify-between px-1">
                        <div className="w-[15%]">
                          {row.gold ? (
                            <div className="w-4 h-4 rounded-full bg-yellow-500/20 border border-yellow-500/50 flex items-center justify-center text-[9px] text-yellow-500 font-bold">1</div>
                          ) : (
                            <div className="w-4 h-4 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-[9px] text-white/50 font-bold">{row.r}</div>
                          )}
                        </div>
                        <div className="w-[35%] text-[11px] font-mono font-bold text-white">{row.t}</div>
                        <div className="w-[20%] flex justify-center">
                           <div className="px-1.5 py-0.5 rounded-[4px] bg-[#22C55E]/20 text-[#22C55E] text-[10px] font-mono font-bold">{row.s}</div>
                        </div>
                        <div className="w-[30%] text-right text-[10px] font-mono text-[#9CA3AF]">{row.rr}</div>
                      </div>
                    ))}
                  </div>
                </div>
                
                <button className="w-full mt-4 py-3 rounded-[10px] text-black font-bold text-[12px] tracking-wide uppercase shadow-[0_4px_14px_rgba(45,212,191,0.2)]" style={{ background: "linear-gradient(to right, #10B981, #2DD4BF)" }}>
                   View Results
                </button>
             </div>
             
             {/* Carousel Dots */}
             <div className="flex justify-center gap-2 mt-5">
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-4 h-1.5 rounded-full bg-[#2DD4BF]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
             </div>
          </motion.div>

          {/* ── STEP 4 ── */}
          <motion.div
            custom={3}
            variants={cardVariants}
            initial="hidden"
            animate={isInView ? "visible" : "hidden"}
            className="group relative flex flex-col rounded-[20px] p-7 transition-all duration-300 hover:-translate-y-1 hover:border-[#2DD4BF]/50"
            style={{ backgroundColor: "#0F1512", border: "1px solid rgba(255,255,255,0.08)" }}
          >
             <div className="flex items-center justify-between mb-4">
                <div className="w-8 h-8 rounded-full flex items-center justify-center font-bold text-[#2DD4BF]" style={{ backgroundColor: "rgba(45,212,191,0.15)" }}>
                  4
                </div>
                <TrendingUp size={28} color="#2DD4BF" strokeWidth={1.5} />
             </div>
             <h3 className="text-xl font-bold text-white mb-2 leading-tight">Tap on any ticker for further info</h3>
             <p className="text-[14px] text-[#9CA3AF] leading-[1.6]">Click any ticker to open the detailed analysis page.</p>
             
             {/* Mockup Box */}
             <div className="mt-5 flex-1 rounded-xl p-4 flex flex-col relative overflow-hidden" style={{ backgroundColor: "#0B100E", border: "1px solid rgba(255,255,255,0.12)", boxShadow: "0 10px 30px rgba(0,0,0,0.5)" }}>
                
                {/* Header */}
                <div className="flex items-center justify-between mb-1">
                   <div className="flex items-center gap-2">
                     <span className="font-bold text-white text-[13px]">BHEL</span>
                     <span className="text-[#6B7280] text-[9px]">• BHEL</span>
                     <span className="text-[8px] bg-[#2DD4BF]/10 text-[#2DD4BF] px-1.5 py-0.5 rounded uppercase font-bold border border-[#2DD4BF]/20">High Conviction</span>
                   </div>
                   <Star size={12} color="#6B7280" />
                </div>
                
                {/* Price */}
                <div className="flex items-baseline gap-2 mb-1">
                   <span className="text-[20px] font-mono font-bold text-white">243.65</span>
                   <span className="text-[10px] font-mono font-bold text-[#22C55E]">+6.45 (2.72%)</span>
                </div>
                
                {/* Meta */}
                <div className="text-[9px] text-[#6B7280] mb-3">NSE  •  Last updated: 12:29 PM</div>
                
                {/* Tabs */}
                <div className="flex gap-3 text-[9px] font-bold mb-3 border-b border-white/5 pb-2">
                  <span className="text-[#2DD4BF] border-b border-[#2DD4BF] pb-2 -mb-2">1D</span>
                  <span className="text-[#6B7280]">1W</span>
                  <span className="text-[#6B7280]">1M</span>
                  <span className="text-[#6B7280]">3M</span>
                  <span className="text-[#6B7280]">1Y</span>
                  <span className="text-[#6B7280]">5Y</span>
                </div>
                
                {/* Candlestick Chart */}
                <div className="h-[70px] w-full mb-4 relative border-b border-white/5 pb-1">
                   <svg width="100%" height="100%" viewBox="0 0 180 100" preserveAspectRatio="none">
                     <line x1="0" y1="10" x2="140" y2="10" stroke="#FFFFFF" strokeOpacity="0.05" strokeDasharray="2 2" />
                     <text x="145" y="13" fill="#6B7280" fontSize="9" fontFamily="monospace">250.00</text>
                     <line x1="0" y1="50" x2="140" y2="50" stroke="#FFFFFF" strokeOpacity="0.05" strokeDasharray="2 2" />
                     <text x="145" y="53" fill="#6B7280" fontSize="9" fontFamily="monospace">240.00</text>
                     <line x1="0" y1="90" x2="140" y2="90" stroke="#FFFFFF" strokeOpacity="0.05" strokeDasharray="2 2" />
                     <text x="145" y="93" fill="#6B7280" fontSize="9" fontFamily="monospace">230.00</text>

                     {candles.map((c, i) => {
                        const isUp = c.c < c.o;
                        const color = isUp ? "#22C55E" : "#EF4444";
                        return (
                          <g key={i}>
                            <line x1={c.x} y1={c.h} x2={c.x} y2={c.l} stroke={color} strokeWidth="1" />
                            <rect x={c.x - 1.5} y={Math.min(c.o, c.c)} width="3" height={Math.max(0.1, Math.abs(c.o - c.c))} fill={color} />
                          </g>
                        )
                     })}
                   </svg>
                </div>
                
                {/* Stats */}
                <div className="flex flex-col gap-1.5">
                   {[
                     { l: 'Pattern', v: 'VCP (Bullish Continuation)', c: 'text-white text-[9px]' },
                     { l: 'Status', v: 'Breakout Ready', c: 'text-white font-bold text-[9px]' },
                     { l: 'Entry', v: '₹240.50', c: 'text-white font-mono font-bold text-[9px]' },
                     { l: 'Stop Loss', v: '₹226.10', c: 'text-white font-mono font-bold text-[9px]' },
                     { l: 'Target 1', v: '₹258.80', c: 'text-white font-mono font-bold text-[9px]' },
                     { l: 'Target 2', v: '₹276.40', c: 'text-white font-mono font-bold text-[9px]' },
                     { l: 'Risk:Reward', v: '0.8 : 1', c: 'text-white font-mono font-bold text-[9px]' },
                     { l: 'Confidence', v: 'HIGH', c: 'text-[#2DD4BF] font-bold text-[9px]' },
                   ].map((s, i) => (
                     <div key={i} className="flex justify-between items-center">
                        <span className="text-[#6B7280] text-[9px]">{s.l}</span>
                        <span className={s.c}>{s.v}</span>
                     </div>
                   ))}
                </div>
             </div>
             
             {/* Carousel Dots */}
             <div className="flex justify-center gap-2 mt-5">
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-1.5 h-1.5 rounded-full bg-[#4B5563]" />
               <div className="w-4 h-1.5 rounded-full bg-[#2DD4BF]" />
             </div>
          </motion.div>

        </div>


        
      </div>
    </section>
  );
}
