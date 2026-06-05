import React from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { motion } from "motion/react";

export function ExpandedRow({ pick }: { pick: FinalPick }) {
  const scores = [
    { label: "Signal Strength", value: pick.signal_strength, weight: 45, color: "bg-blue-500" },
    { label: "Volume Score", value: pick.volume_score, weight: 30, color: "bg-purple-500" },
    { label: "Risk-Reward", value: pick.rr_score, weight: 10, color: "bg-emerald-500" },
    { label: "Stage 2 Trend", value: pick.stage2_score, weight: 10, color: "bg-orange-500" },
    { label: "Relative Strength", value: pick.rs_score, weight: 5, color: "bg-pink-500" },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: "auto" }}
      exit={{ opacity: 0, height: 0 }}
      className="overflow-hidden border-b border-white/5 bg-[#0a0a0c]"
    >
      <div className="p-6 md:p-8 flex flex-col lg:flex-row gap-8">
        
        {/* Judge Panel */}
        <div className="flex-1 space-y-4">
          <div className="flex items-center gap-2 mb-2">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
              <path d="M9 12l2 2 4-4"></path>
            </svg>
            <h4 className="text-sm font-semibold text-white/80 uppercase tracking-widest">
              AI Judge Verdict
            </h4>
          </div>
          <p className="text-base text-white/70 leading-relaxed max-w-2xl border-l-2 border-emerald-500/30 pl-4 py-1">
            {pick.judge_verdict || "No verdict provided by the judge."}
          </p>

          {pick.flags && (
            <div className="mt-4 inline-flex items-start gap-2 bg-red-500/10 border border-red-500/20 rounded-lg p-3 max-w-2xl">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-red-400 mt-0.5 shrink-0">
                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                <line x1="12" y1="9" x2="12" y2="13"></line>
                <line x1="12" y1="17" x2="12.01" y2="17"></line>
              </svg>
              <div>
                <span className="block text-xs font-bold text-red-400 uppercase tracking-wider mb-1">Risk Warning</span>
                <span className="text-sm text-red-300/80 leading-snug">{pick.flags}</span>
              </div>
            </div>
          )}
        </div>

        {/* Breakdown Panel */}
        <div className="flex-1 bg-[#121216] rounded-xl border border-white/5 p-5">
          <h4 className="text-xs font-semibold text-white/50 uppercase tracking-widest mb-4">
            Composite Score Breakdown
          </h4>
          <div className="space-y-4">
            {scores.map((s, i) => (
              <div key={i} className="flex items-center gap-4">
                <div className="w-32 text-xs font-medium text-white/60 truncate">
                  {s.label} <span className="text-white/30">({s.weight}%)</span>
                </div>
                <div className="flex-1 h-2 bg-white/5 rounded-full overflow-hidden">
                  <div
                    className={`h-full ${s.color} opacity-80`}
                    style={{ width: `${s.value}%` }}
                  />
                </div>
                <div className="w-8 text-right text-xs font-mono text-white/80">
                  {s.value.toFixed(0)}
                </div>
              </div>
            ))}
          </div>
        </div>

      </div>
    </motion.div>
  );
}
