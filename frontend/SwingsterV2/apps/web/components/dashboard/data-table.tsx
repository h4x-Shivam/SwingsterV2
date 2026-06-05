"use client";

import React, { useState } from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { ExpandedRow } from "./expanded-row";
import { AnimatePresence } from "motion/react";

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
    <div className="w-full bg-[#121216]/50 backdrop-blur-md border border-white/10 rounded-xl overflow-hidden shadow-2xl">
      {/* Table Header */}
      <div className="grid grid-cols-[80px_1.5fr_1fr_1.5fr_1fr_1fr] gap-4 p-4 border-b border-white/10 text-xs font-semibold uppercase tracking-wider text-white/50 bg-[#0a0a0c]">
        <div className="text-center">Rank</div>
        <div>Symbol</div>
        <div className="text-center">Conviction</div>
        <div className="text-right">Price / Distance</div>
        <div className="text-right">R:R Ratio</div>
        <div className="text-right pr-4">Score</div>
      </div>

      {/* Table Body */}
      <div className="flex flex-col">
        {picks.map((pick, index) => {
          const isExpanded = expandedRowIndex === index;
          
          // Color coding for distance
          const distanceColor = 
            pick.distance_from_buy_pct <= 0 && pick.distance_from_buy_pct >= -3 
              ? "text-emerald-400" 
              : pick.distance_from_buy_pct > 0 
                ? "text-amber-400" 
                : "text-white/60";

          return (
            <React.Fragment key={`${pick.symbol}-${index}`}>
              <div 
                onClick={() => setExpandedRowIndex(isExpanded ? null : index)}
                className={`grid grid-cols-[80px_1.5fr_1fr_1.5fr_1fr_1fr] gap-4 p-4 items-center border-b border-white/5 cursor-pointer transition-colors ${
                  isExpanded ? "bg-[#ffffff08]" : "hover:bg-[#ffffff04]"
                }`}
              >
                {/* Rank */}
                <div className="text-center font-mono text-lg font-bold text-white/30">
                  #{pick.rank}
                </div>

                {/* Symbol */}
                <div>
                  <div className="text-lg font-bold text-white tracking-wide">
                    {pick.symbol}
                  </div>
                  <div className="text-[10px] text-white/40 uppercase tracking-widest mt-0.5">
                    {pick.pattern}
                  </div>
                </div>

                {/* Conviction Badge */}
                <div className="flex justify-center">
                  <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-[10px] font-bold tracking-widest uppercase border ${
                    pick.conviction === 'HIGH' 
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 shadow-[0_0_10px_rgba(16,185,129,0.2)]" 
                      : "bg-teal-500/10 border-teal-500/30 text-teal-400"
                  }`}>
                    {pick.conviction}
                  </span>
                </div>

                {/* Price & Distance */}
                <div className="text-right flex flex-col items-end">
                  <div className="font-mono text-sm text-white/90">
                    ₹{pick.current_price.toFixed(2)}
                  </div>
                  <div className={`font-mono text-xs mt-1 ${distanceColor}`}>
                    {pick.distance_from_buy_pct > 0 ? "+" : ""}
                    {pick.distance_from_buy_pct.toFixed(2)}%
                  </div>
                </div>

                {/* Risk/Reward */}
                <div className="text-right font-mono text-sm text-white/80">
                  {pick.rr_ratio.toFixed(1)}x
                </div>

                {/* Composite Score */}
                <div className="text-right pr-4 flex flex-col items-end">
                  <div className="font-mono text-lg font-bold text-emerald-400">
                    {pick.composite_score.toFixed(1)}
                  </div>
                  <div className="w-16 h-1 mt-1.5 bg-white/10 rounded-full overflow-hidden">
                    <div 
                      className="h-full bg-emerald-500" 
                      style={{ width: `${Math.min(100, Math.max(0, pick.composite_score))}%` }} 
                    />
                  </div>
                </div>
              </div>

              {/* Expanded Area */}
              <AnimatePresence>
                {isExpanded && <ExpandedRow pick={pick} />}
              </AnimatePresence>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
