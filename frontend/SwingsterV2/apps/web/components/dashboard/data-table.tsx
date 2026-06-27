"use client";

import React, { useState } from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { ExpandedRow } from "./expanded-row";
import { AnimatePresence, motion } from "motion/react";
import { LineChart, Search, Sparkles } from "lucide-react";

// Helper for premium animated sparkline
const generateSparkline = (seedStr: string, isHovered: boolean) => {
  let hash = 0;
  for (let i = 0; i < seedStr.length; i++) {
    hash = seedStr.charCodeAt(i) + ((hash << 5) - hash);
  }
  const rng = (min: number, max: number, offset: number) => {
    const r = Math.sin(hash + offset) * 10000;
    return min + (r - Math.floor(r)) * (max - min);
  };
  
  const y1 = rng(10, 25, 1);
  const cy1 = rng(5, 25, 2);
  const y2 = rng(10, 25, 3);
  const cy2 = rng(5, 25, 4);
  const y3 = rng(5, 20, 5);
  const y4 = rng(2, 10, 7);

  const path = `M0,${y1} Q15,${cy1} 30,${y2} T60,${y3} T100,${y4}`;

  const volumeBars = Array.from({ length: 7 }).map((_, i) => {
    const h = rng(2, 14, i * 10);
    const isUp = rng(0, 1, i * 11) > 0.3;
    const color = isUp ? "#10b981" : "#ef4444";
    return (
      <motion.rect 
        key={i} 
        x={10 + i * 13} 
        y={30 - h} 
        width="3" 
        height={h} 
        fill={color} 
        rx="1.5"
        animate={{ 
          height: isHovered ? h * rng(0.8, 1.2, i*5) : h,
          y: isHovered ? 30 - (h * rng(0.8, 1.2, i*5)) : 30 - h
        }}
        transition={{ duration: 0.3, ease: "easeOut" }}
        opacity={isHovered ? 0.8 : (0.2 + rng(0, 0.3, i))} 
      />
    );
  });

  return { path, volumeBars, endY: y4 };
};

export function DataTable({ picks, initialWatchlist = [] }: { picks: FinalPick[], initialWatchlist?: string[] }) {
  const [expandedRowIndex, setExpandedRowIndex] = useState<number | null>(null);
  const [watchlistSet, setWatchlistSet] = useState<Set<string>>(new Set(initialWatchlist));
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);

  const toggleWatchlistSymbol = (symbol: string) => {
    const next = new Set(watchlistSet);
    if (next.has(symbol)) {
      next.delete(symbol);
    } else {
      next.add(symbol);
    }
    setWatchlistSet(next);
  };

  if (picks.length === 0) {
    return (
      <motion.div 
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="w-full min-h-[400px] border border-white/5 bg-[#121216]/50 rounded-3xl flex flex-col items-center justify-center relative overflow-hidden backdrop-blur-sm"
      >
        <div className="absolute inset-0 bg-gradient-to-b from-transparent to-[#0a0a0c]/80" />
        <div className="relative z-10 flex flex-col items-center text-center max-w-sm">
          <div className="w-20 h-20 mb-6 rounded-full bg-white/[0.02] border border-white/5 flex items-center justify-center shadow-2xl relative">
            <div className="absolute inset-0 rounded-full border border-emerald-500/20 animate-[spin_4s_linear_infinite]" />
            <Search className="w-8 h-8 text-white/20" />
          </div>
          <h3 className="text-xl font-bold text-white mb-2">No candidates found</h3>
          <p className="text-white/40 text-sm mb-6">
            Our scanners couldn&apos;t find any highly rated setups right now. Try adjusting your scan parameters or check back later.
          </p>
          <button className="px-6 py-2.5 rounded-full bg-white/5 border border-white/10 text-white/70 text-sm font-semibold hover:bg-white/10 hover:text-white transition-colors">
            Refresh Scan
          </button>
        </div>
      </motion.div>
    );
  }

  return (
    <div className="w-full bg-[#0a0a0c]/90 backdrop-blur-2xl border border-white/[0.08] rounded-3xl shadow-[0_30px_60px_-15px_rgba(0,0,0,0.8)] overflow-hidden relative">
      
      {/* Table Header */}
      <div className="grid grid-cols-[60px_2.5fr_1.5fr_2fr_2fr_80px] gap-6 px-8 py-5 border-b border-white/[0.08] text-[10px] font-bold uppercase tracking-[0.2em] text-white/30 bg-[#060608]/50">
        <div className="text-center">Rank</div>
        <div>Asset</div>
        <div className="text-center">Conviction</div>
        <div>Risk Profile</div>
        <div className="text-center pl-4">Momentum</div>
        <div className="text-center">Track</div>
      </div>

      {/* Table Body */}
      <div className="flex flex-col relative z-10">
        {picks.map((pick, index) => {
          const isExpanded = expandedRowIndex === index;
          const isHovered = hoveredRow === index;
          const isWatched = watchlistSet.has(pick.symbol);

          // Calculate score percentage for progress bar
          const maxPossibleScore = 100; // Assuming 100 is max composite score
          const scorePercent = Math.min(100, Math.max(0, (pick.composite_score / maxPossibleScore) * 100));
          
          // Calculate risk reward for split bar
          const rrTotal = pick.rr_ratio + 1;
          const riskPercent = (1 / rrTotal) * 100;
          const rewardPercent = (pick.rr_ratio / rrTotal) * 100;

          return (
            <React.Fragment key={`${pick.symbol}-${index}`}>
              <div 
                onClick={() => setExpandedRowIndex(isExpanded ? null : index)}
                onMouseEnter={() => setHoveredRow(index)}
                onMouseLeave={() => setHoveredRow(null)}
                className={`grid grid-cols-[60px_2.5fr_1.5fr_2fr_2fr_80px] gap-6 px-8 py-6 items-center border-b border-white/[0.04] cursor-pointer transition-all duration-300 relative group
                  ${isExpanded ? "bg-white/[0.03]" : "hover:bg-white/[0.02]"}
                `}
              >
                {/* Active indicator line */}
                <div className={`absolute left-0 top-0 bottom-0 w-[3px] bg-emerald-500 transition-opacity duration-300 ${isExpanded ? "opacity-100" : "opacity-0 group-hover:opacity-50"}`} />

                {/* Rank */}
                <div className="text-center flex justify-center">
                  <div className={`w-9 h-9 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-300 ${
                    index === 0 ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 shadow-[0_0_15px_rgba(234,179,8,0.2)]" :
                    index === 1 ? "bg-slate-300/10 text-slate-300 border border-slate-300/20 shadow-[0_0_15px_rgba(203,213,225,0.1)]" :
                    index === 2 ? "bg-amber-700/10 text-amber-500 border border-amber-700/20 shadow-[0_0_15px_rgba(180,83,9,0.2)]" :
                    "bg-white/[0.02] text-white/30 border border-white/[0.05] group-hover:bg-white/[0.05] group-hover:text-white/70 font-mono text-xs"
                  }`}>
                    {index < 3 ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="currentColor" className="opacity-90"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg>
                    ) : (
                      pick.rank
                    )}
                  </div>
                </div>

                {/* Ticker & Sector */}
                <div>
                  <div className="flex items-center gap-3">
                    <span className="text-lg font-extrabold text-white tracking-tight group-hover:text-emerald-400 transition-colors">
                      {pick.symbol}
                    </span>
                    {pick.conviction === "HIGH" && (
                      <span className="flex items-center gap-1 bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px] px-2 py-0.5 rounded-full uppercase tracking-widest font-bold">
                        <Sparkles className="w-3 h-3" />
                        Top Pick
                      </span>
                    )}
                  </div>
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs font-medium text-white/40">{pick.sector}</span>
                    <span className="w-1 h-1 rounded-full bg-white/10" />
                    <span className="text-[10px] uppercase tracking-widest font-bold text-white/20">NSE</span>
                  </div>
                </div>

                {/* Final Score (Progress Bar) */}
                <div className="flex flex-col justify-center items-center gap-2">
                  <div className="text-xl font-bold font-mono text-white group-hover:text-emerald-400 transition-colors drop-shadow-[0_0_8px_rgba(16,185,129,0.1)]">
                    {pick.composite_score.toFixed(0)}
                  </div>
                  <div className="w-full max-w-[80px] h-1.5 bg-white/5 rounded-full overflow-hidden">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${scorePercent}%` }}
                      transition={{ duration: 1, ease: "easeOut" }}
                      className="h-full bg-gradient-to-r from-emerald-500/50 to-emerald-400 rounded-full"
                    />
                  </div>
                </div>

                {/* Risk:Reward (Split Bar) */}
                <div className="flex flex-col justify-center gap-1.5">
                  <div className="flex justify-between items-end text-xs font-mono font-medium">
                    <span className="text-red-400/80 group-hover:text-red-400 transition-colors">R1</span>
                    <span className="text-lg font-bold text-white group-hover:text-emerald-400 transition-colors">{pick.rr_ratio.toFixed(1)}</span>
                    <span className="text-emerald-400/80 group-hover:text-emerald-400 transition-colors">R{pick.rr_ratio.toFixed(0)}</span>
                  </div>
                  <div className="w-full h-1.5 flex gap-0.5 rounded-full overflow-hidden opacity-80 group-hover:opacity-100 transition-opacity">
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${riskPercent}%` }}
                      className="h-full bg-red-500/70"
                    />
                    <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: `${rewardPercent}%` }}
                      className="h-full bg-emerald-500/70"
                    />
                  </div>
                  <div className="flex justify-between text-[9px] uppercase tracking-widest text-white/30">
                    <span>-₹{(pick.buy_point - pick.stop_loss).toFixed(1)}</span>
                    <span>+₹{(pick.target - pick.buy_point).toFixed(0)}</span>
                  </div>
                </div>

                {/* Chart Preview (Premium Animated Sparkline) */}
                <div className="flex justify-center items-center h-12 w-full px-4 relative group/chart">
                  <div className="absolute inset-0 bg-gradient-to-r from-transparent via-emerald-500/5 to-transparent opacity-0 group-hover/chart:opacity-100 transition-opacity rounded-lg" />
                  <svg viewBox="0 0 100 30" className="w-full h-full preserve-3d overflow-visible" preserveAspectRatio="none">
                    {(() => {
                      const { path, volumeBars, endY } = generateSparkline(pick.symbol, isHovered);
                      return (
                        <>
                          <motion.path 
                            d={path} 
                            fill="none" 
                            stroke="currentColor" 
                            strokeWidth="2" 
                            className="text-emerald-500/80 drop-shadow-[0_2px_4px_rgba(16,185,129,0.3)]"
                            initial={{ pathLength: 0 }}
                            animate={{ pathLength: 1 }}
                            transition={{ duration: 1.5, ease: "easeInOut" }}
                          />
                          {/* Glowing dot at the end */}
                          <motion.circle 
                            cx="100" 
                            cy={endY} 
                            r="2" 
                            className="fill-emerald-400"
                            initial={{ opacity: 0, scale: 0 }}
                            animate={{ opacity: 1, scale: 1 }}
                            transition={{ delay: 1.5, duration: 0.3 }}
                          />
                          {/* Glow effect on hover */}
                          <motion.circle 
                            cx="100" 
                            cy={endY} 
                            r="6" 
                            className="fill-emerald-500/20"
                            animate={{ 
                              scale: isHovered ? [1, 1.5, 1] : 1,
                              opacity: isHovered ? [0.5, 0.8, 0.5] : 0
                            }}
                            transition={{ repeat: Infinity, duration: 1.5 }}
                          />
                          {volumeBars}
                        </>
                      );
                    })()}
                  </svg>
                </div>

                {/* Action */}
                <div className="flex justify-center items-center">
                  <button 
                    onClick={async (e) => {
                      e.stopPropagation();
                      toggleWatchlistSymbol(pick.symbol);
                      const { toggleWatchlist } = await import("@/app/actions/watchlist");
                      try {
                        await toggleWatchlist(pick.symbol);
                      } catch (err) {
                        toggleWatchlistSymbol(pick.symbol);
                      }
                    }}
                    className={`p-2.5 rounded-full border transition-all duration-300 hover:scale-110 active:scale-95 ${
                      isWatched 
                        ? "text-emerald-400 bg-emerald-500/10 border-emerald-500/30 shadow-[0_0_15px_rgba(16,185,129,0.2)]" 
                        : "text-white/30 bg-white/[0.02] border-white/5 hover:text-white hover:bg-white/10 hover:border-white/20"
                    }`}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={isWatched ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                    </svg>
                  </button>
                </div>
              </div>

              {/* Expanded Row */}
              <AnimatePresence>
                {isExpanded && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="overflow-hidden bg-[#040405] border-b border-white/[0.08]"
                  >
                    <ExpandedRow 
                      pick={pick} 
                      isWatched={isWatched}
                      onToggleWatchlist={async () => {
                        toggleWatchlistSymbol(pick.symbol);
                        const { toggleWatchlist } = await import("@/app/actions/watchlist");
                        try {
                          await toggleWatchlist(pick.symbol);
                        } catch (err) {
                          toggleWatchlistSymbol(pick.symbol);
                        }
                      }}
                    />
                  </motion.div>
                )}
              </AnimatePresence>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
