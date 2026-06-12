"use client";

import React, { useRef, useState, useEffect } from "react";
import { motion } from "motion/react";
import Link from "next/link";

const StaggeredText = ({ text }: { text: string }) => {
  const words = text.split(" ");
  return (
    <div className="flex flex-wrap justify-center gap-x-2 md:gap-x-3">
      {words.map((word, i) => (
        <motion.span
          key={i}
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-10%" }}
          transition={{ duration: 0.6, delay: i * 0.05, ease: "easeOut" }}
          className={`inline-block ${(word === "2,000" || word === "Stocks") ? "text-emerald-400 drop-shadow-[0_0_8px_rgba(16,185,129,0.3)]" : ""}`}
        >
          {word}
        </motion.span>
      ))}
    </div>
  );
};

const cards = [
  {
    numeral: "01",
    title: "We Scan the Market",
    desc: "Every day, Swingster scans 2,000+ NSE stocks — instantly filtering out illiquid, penny, and weak-trend names so only real opportunities remain.",
    MiniViz: () => {
      return (
        <div className="mt-6 p-3 bg-white/[0.02] rounded-lg border border-white/[0.05] flex flex-col gap-3 relative overflow-hidden">
          <div className="flex justify-between items-center text-sm text-white/70 font-mono font-medium">
            <span>2,847</span>
            <span className="text-white/20 text-xs">→</span>
            <span>312</span>
            <span className="text-white/20 text-xs">→</span>
            <span>47</span>
            <span className="text-white/20 text-xs">→</span>
            <span className="text-emerald-400 font-black text-lg drop-shadow-[0_0_8px_rgba(16,185,129,0.6)]">10</span>
          </div>
          <div className="w-full h-1.5 bg-white/5 rounded-full overflow-hidden flex">
            <motion.div 
              initial={{ width: "100%" }}
              whileInView={{ width: "35%" }}
              viewport={{ once: true }}
              transition={{ duration: 1, delay: 0.8, ease: "easeInOut" }}
              className="h-full bg-white/20"
            />
            <motion.div 
              initial={{ width: "0%" }}
              whileInView={{ width: "10%" }}
              viewport={{ once: true }}
              transition={{ duration: 1, delay: 1.8, ease: "easeInOut" }}
              className="h-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)]"
            />
          </div>
        </div>
      );
    }
  },
  {
    numeral: "02",
    title: "We Detect the Pattern",
    desc: "Our algorithm hunts for VCP, Cup & Handle, and Flag setups — calculating the exact buy point, stop loss, and risk-to-reward for each one.",
    MiniViz: () => {
      return (
        <div className="mt-6 p-3 bg-white/[0.02] rounded-lg border border-white/[0.05] flex items-end h-[48px] gap-1 relative overflow-hidden">
          {/* VCP Pattern SVG */}
          <svg className="absolute inset-0 w-full h-full" preserveAspectRatio="none" viewBox="0 0 100 40">
            <motion.path 
              d="M 0,10 C 15,45 25,45 35,15 C 45,35 55,35 65,20 C 72,28 78,28 85,20 L 100,5" 
              fill="none" 
              stroke="#10b981" 
              strokeWidth="2.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              initial={{ pathLength: 0, opacity: 0 }}
              whileInView={{ pathLength: 1, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 1.5, delay: 0.8, ease: "easeInOut" }}
              className="drop-shadow-[0_0_6px_rgba(16,185,129,0.6)]"
            />
            {/* Breakout dot */}
            <motion.circle 
              cx="85" cy="20" r="3" 
              fill="#10b981"
              initial={{ opacity: 0, scale: 0 }}
              whileInView={{ opacity: 1, scale: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: 2.1 }}
              className="drop-shadow-[0_0_8px_rgba(16,185,129,0.9)]"
            />
          </svg>
        </div>
      );
    }
  },
  {
    numeral: "03",
    title: "AI Verifies the Setup",
    desc: "A specialized AI reviews the top candidates for pattern quality, sector balance, and conviction — so you only see the strongest 10 setups.",
    MiniViz: () => {
      const [status, setStatus] = useState("SCANNING...");
      const [color, setColor] = useState("text-white/40");
      
      useEffect(() => {
        const statuses = [
          { text: "LOW CONVICTION", col: "text-white/40" },
          { text: "MEDIUM CONVICTION", col: "text-yellow-400" },
          { text: "HIGH CONVICTION", col: "text-emerald-400 drop-shadow-[0_0_5px_rgba(16,185,129,0.8)]" }
        ];
        let i = 0;
        const interval = setInterval(() => {
          setStatus(statuses[i].text);
          setColor(statuses[i].col);
          i = (i + 1) % statuses.length;
        }, 1500);
        return () => clearInterval(interval);
      }, []);

      return (
        <div className="mt-6 p-3 bg-white/[0.02] rounded-lg border border-white/[0.05] flex items-center justify-center relative overflow-hidden h-[48px]">
           <span className={`text-xs font-mono font-bold tracking-widest transition-colors duration-300 ${color}`}>
             {status}
           </span>
        </div>
      );
    }
  }
];

export function HowItWorks() {
  const containerRef = useRef<HTMLDivElement>(null);

  return (
    <section id="how-it-works" className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden scroll-mt-24">
      {/* Background Treatments */}
      <div className="absolute inset-0 z-0 pointer-events-none" style={{ backgroundImage: 'radial-gradient(circle, rgba(255,255,255,0.03) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
      <div className="absolute -bottom-1/3 -left-1/4 w-[800px] h-[800px] bg-emerald-500/10 rounded-full blur-[120px] pointer-events-none opacity-20" />

      <div className="relative z-10 max-w-6xl mx-auto px-6" ref={containerRef}>
        
        {/* Section Header */}
        <div className="text-center mb-20 flex flex-col items-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6"
          >
            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse" />
            <span className="text-xs font-bold tracking-[0.2em] text-white/80 uppercase">How It Works</span>
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white tracking-tight mb-6 max-w-4xl mx-auto">
            <StaggeredText text="From 2,000 Stocks to Your Top 10 — In 3 Steps" />
          </h2>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto leading-relaxed"
          >
            No charting, no screening, no guesswork. Just open the dashboard and see what's ready to move.
          </motion.p>
        </div>

        {/* Cards & Connector Line */}
        <div className="relative flex flex-col md:flex-row gap-8 md:gap-6 lg:gap-8 justify-center">
          
          {/* Connector Line (Desktop) */}
          <div className="hidden md:block absolute top-1/2 left-[16%] right-[16%] h-[2px] -translate-y-1/2 z-0">
             <svg className="w-full h-full" preserveAspectRatio="none">
                <motion.line 
                  x1="0" y1="50%" x2="100%" y2="50%" 
                  stroke="#10b981" 
                  strokeWidth="2"
                  strokeDasharray="1000"
                  strokeDashoffset="1000"
                  initial={{ strokeDashoffset: 1000 }}
                  whileInView={{ strokeDashoffset: 0 }}
                  viewport={{ once: true, margin: "-20%" }}
                  transition={{ duration: 2, delay: 0.5, ease: "easeInOut" }}
                  style={{ filter: 'drop-shadow(0 0 4px rgba(16,185,129,0.8))' }}
                />
             </svg>
          </div>

          {/* Connector Line (Mobile) */}
          <div className="md:hidden absolute left-1/2 top-[10%] bottom-[10%] w-[2px] -translate-x-1/2 z-0">
             <svg className="w-full h-full" preserveAspectRatio="none">
                <motion.line 
                  x1="50%" y1="0" x2="50%" y2="100%" 
                  stroke="#10b981" 
                  strokeWidth="2"
                  strokeDasharray="1000"
                  strokeDashoffset="1000"
                  initial={{ strokeDashoffset: 1000 }}
                  whileInView={{ strokeDashoffset: 0 }}
                  viewport={{ once: true, margin: "-10%" }}
                  transition={{ duration: 2, delay: 0.5, ease: "easeInOut" }}
                  style={{ filter: 'drop-shadow(0 0 4px rgba(16,185,129,0.8))' }}
                />
             </svg>
          </div>

          {/* Render Cards */}
          {cards.map((card, idx) => (
            <motion.div
              key={card.numeral}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, margin: "-10%" }}
              transition={{ duration: 0.6, delay: 0.2 + idx * 0.12 }}
              className="relative z-10 flex-1 group"
            >
              {/* Outer Wrapper for Animated Glow on Hover */}
              <div className="relative w-full h-full rounded-2xl p-[1px] overflow-hidden">
                 {/* Conic Gradient for Hover Border */}
                 <div className="absolute inset-[-100%] bg-[conic-gradient(from_0deg,transparent_0_340deg,rgba(16,185,129,0.6)_360deg)] animate-[spin_3s_linear_infinite] opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                 
                 {/* Card Content Base */}
                 <div className="relative w-full h-full bg-[#0c0c10]/80 backdrop-blur-[16px] rounded-[15px] p-8 md:p-6 lg:p-8 flex flex-col border border-white/[0.08] group-hover:border-transparent transition-colors">
                    
                    {/* Text */}
                    <h3 className="text-xl md:text-2xl font-bold text-white mb-3 mt-4">
                      {card.title}
                    </h3>
                    <p className="text-white/60 leading-relaxed text-sm md:text-base flex-1">
                      {card.desc}
                    </p>

                    {/* Mini Visualizations */}
                    <card.MiniViz />
                 </div>

                 {/* Connection Dot - Lights up when line reaches it */}
                 <motion.div 
                   className="absolute hidden md:block w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)] -left-[1.5px] top-1/2 -translate-y-1/2"
                   initial={{ opacity: 0, scale: 0 }}
                   whileInView={{ opacity: 1, scale: 1 }}
                   viewport={{ once: true }}
                   transition={{ duration: 0.3, delay: 0.5 + idx * 0.6 }}
                 />
                 <motion.div 
                   className="absolute md:hidden w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.8)] top-[-1.5px] left-1/2 -translate-x-1/2"
                   initial={{ opacity: 0, scale: 0 }}
                   whileInView={{ opacity: 1, scale: 1 }}
                   viewport={{ once: true }}
                   transition={{ duration: 0.3, delay: 0.5 + idx * 0.6 }}
                 />
              </div>
            </motion.div>
          ))}
        </div>

        {/* CTA Button */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6, delay: 1 }}
          className="mt-20 flex justify-center"
        >
          <Link 
            href="#patterns"
            className="group px-8 py-4 bg-emerald-500 text-black font-bold rounded-full transition-all duration-300 hover:scale-105 hover:bg-emerald-400 shadow-[0_0_20px_rgba(16,185,129,0.4)] hover:shadow-[0_0_30px_rgba(16,185,129,0.6)] flex items-center gap-2"
          >
            See It In Action
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" className="transition-transform group-hover:translate-x-1"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
          </Link>
        </motion.div>
        
      </div>
    </section>
  );
}
