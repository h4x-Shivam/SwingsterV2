"use client";

import React, { useState } from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { ExpandedRow } from "./expanded-row";
import { AnimatePresence, motion } from "motion/react";

export function DataTable({ picks }: { picks: FinalPick[] }) {
  const [expandedRowIndex, setExpandedRowIndex] = useState<number | null>(null);

  if (picks.length === 0) {
    return (
      <div className="w-full h-64 border border-dashed border-white/10 rounded-xl flex items-center justify-center text-white/40 font-mono text-sm">
        No candidates found for the selected criteria.
      </div>
    );
  }

  return (
    <div className="w-full bg-[#121216]/80 backdrop-blur-md border border-white/10 rounded-xl shadow-2xl overflow-visible">
      {/* Table Header */}
      <div className="grid grid-cols-[60px_2fr_1.5fr_1.5fr_2fr_80px] gap-4 px-6 py-4 border-b border-white/10 text-[11px] font-semibold uppercase tracking-wider text-white/40 bg-[#0a0a0c] rounded-t-xl">
        <div className="text-center">Rank</div>
        <div>Ticker</div>
        <div className="text-center">Final Score</div>
        <div className="text-left pl-4">Risk : Reward</div>
        <div className="text-center">Chart Preview</div>
        <div className="text-center">Action</div>
      </div>

      {/* Table Body */}
      <div className="flex flex-col rounded-b-xl overflow-hidden">
        {picks.map((pick, index) => {
          const isExpanded = expandedRowIndex === index;

          return (
            <React.Fragment key={`${pick.symbol}-${index}`}>
              <div 
                onClick={() => setExpandedRowIndex(isExpanded ? null : index)}
                className={`grid grid-cols-[60px_2fr_1.5fr_1.5fr_2fr_80px] gap-4 px-6 py-4 items-center border-b border-white/5 cursor-pointer transition-all duration-300 ${
                  isExpanded ? "bg-[#ffffff08]" : "hover:bg-[#ffffff03]"
                }`}
              >
                {/* Rank */}
                <div className="text-center flex justify-center">
                  <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                    index === 0 ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20" :
                    index === 1 ? "bg-slate-300/10 text-slate-300 border border-slate-300/20" :
                    index === 2 ? "bg-amber-700/10 text-amber-600 border border-amber-700/20" :
                    "text-white/40 font-mono text-xs"
                  }`}>
                    {index < 3 ? (
                      <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M6 9H4.5a2.5 2.5 0 0 1 0-5H6"></path><path d="M18 9h1.5a2.5 2.5 0 0 0 0-5H18"></path><path d="M4 22h16"></path><path d="M10 14.66V17c0 .55-.47.98-.97 1.21C7.85 18.75 7 20.24 7 22"></path><path d="M14 14.66V17c0 .55.47.98.97 1.21C16.15 18.75 17 20.24 17 22"></path><path d="M18 2H6v7a6 6 0 0 0 12 0V2Z"></path></svg>
                    ) : (
                      pick.rank
                    )}
                  </div>
                </div>

                {/* Ticker & Sector */}
                <div>
                  <div className="text-base font-bold text-white tracking-wide flex items-center gap-2">
                    {pick.symbol}
                    {pick.conviction === "HIGH" && (
                      <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[9px] px-1.5 py-0.5 rounded-sm uppercase tracking-widest">
                        High Conviction
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-white/40 mt-1">
                    {pick.sector} <span className="mx-1">•</span> NSE
                  </div>
                </div>

                {/* Final Score */}
                <div className="flex justify-center items-center">
                  <div className="px-3 py-1.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 font-bold font-mono text-lg shadow-[0_0_10px_rgba(16,185,129,0.1)]">
                    {pick.composite_score.toFixed(0)}
                  </div>
                </div>

                {/* Risk:Reward */}
                <div className="pl-4 flex flex-col justify-center">
                  <div className="text-sm font-bold text-white mb-0.5">
                    {pick.rr_ratio.toFixed(1)} : 1
                  </div>
                  <div className="text-[10px] text-white/40 font-mono">
                    Risk: ₹{(pick.buy_point - pick.stop_loss).toFixed(1)} <span className="mx-1">|</span> Target: ₹{pick.target.toFixed(0)}
                  </div>
                </div>

                {/* Chart Preview (Sparkline visualization) */}
                <div className="flex justify-center items-center h-10 w-full px-4">
                  {/* Fake sparkline using SVG */}
                  <svg viewBox="0 0 100 30" className="w-full h-full preserve-3d" preserveAspectRatio="none">
                    <path d="M0,15 Q10,25 20,20 T40,15 T60,25 T80,10 T100,5" fill="none" stroke="#10b981" strokeWidth="1.5" className="opacity-80 drop-shadow-[0_0_3px_rgba(16,185,129,0.8)]" />
                    {/* Add some fake volume bars at bottom */}
                    <rect x="18" y="25" width="2" height="5" fill="#10b981" opacity="0.4" />
                    <rect x="38" y="22" width="2" height="8" fill="#10b981" opacity="0.4" />
                    <rect x="58" y="27" width="2" height="3" fill="#ef4444" opacity="0.4" />
                    <rect x="78" y="20" width="2" height="10" fill="#10b981" opacity="0.8" />
                    <rect x="98" y="18" width="2" height="12" fill="#10b981" opacity="0.9" />
                  </svg>
                </div>

                {/* Action */}
                <div className="flex justify-center items-center">
                  <button 
                    onClick={(e) => e.stopPropagation()}
                    className="p-2 text-white/30 hover:text-emerald-400 transition-colors rounded-full hover:bg-emerald-500/10"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
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
                    className="overflow-hidden bg-[#060608] border-b border-white/5"
                  >
                    <ExpandedRow pick={pick} />
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
