"use client";

import React, { useState } from "react";
import type { ScanSummary, FinalPick } from "@/lib/data-fetcher";
import { motion, AnimatePresence } from "motion/react";

export function DashboardHeader({
  summary,
  picks
}: {
  summary: ScanSummary | null;
  picks: FinalPick[];
}) {
  const [dropdownOpen, setDropdownOpen] = useState<"matches" | "rejected" | null>(null);
  const [copied, setCopied] = useState(false);

  const totalScanned = summary?.total_scanned || 0;
  const matchCount = picks.length;
  
  const highConfidenceCount = picks.filter(p => p.conviction === "HIGH").length;
  const avgRR = picks.length > 0 ? (picks.reduce((acc, p) => acc + p.rr_ratio, 0) / picks.length).toFixed(1) : "0.0";
  
  const tickerList = picks.map(p => p.symbol).join(", ");
  const rejectedList = summary?.rejected_by_rr?.join(", ") || "";

  const handleCopy = (text: string) => {
    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col xl:flex-row gap-6 justify-between items-start xl:items-end">
      <div>
        <div className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 mb-4">
          <span className="h-2 w-2 rounded-full bg-emerald-500 animate-pulse" />
          <span className="text-[10px] font-semibold text-emerald-400 tracking-widest uppercase">
            Live Results // {summary?.mode || "ALL"}
          </span>
        </div>
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-white mb-2">
          Dashboard
        </h1>
        <p className="text-white/40 text-sm font-mono" suppressHydrationWarning>
          Last scan: {summary?.timestamp ? new Date(summary.timestamp).toLocaleString() : "Just now"}
        </p>
      </div>

      <div className="flex flex-wrap gap-4 w-full xl:w-auto">
        {/* Total Scanned Card */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-4 min-w-[140px] flex-1 xl:flex-none">
          <div className="text-white/40 text-[10px] font-semibold uppercase tracking-wider mb-1.5">
            Total Scanned
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {totalScanned.toLocaleString()}
          </div>
        </div>

        {/* High Confidence Card */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-4 min-w-[140px] flex-1 xl:flex-none">
          <div className="text-white/40 text-[10px] font-semibold uppercase tracking-wider mb-1.5 flex items-center justify-between">
            High Confidence
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"></path>
            </svg>
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {highConfidenceCount}
          </div>
        </div>

        {/* Avg Risk Reward Card */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-4 min-w-[140px] flex-1 xl:flex-none">
          <div className="text-white/40 text-[10px] font-semibold uppercase tracking-wider mb-1.5 flex items-center justify-between">
            Avg Risk:Reward
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-purple-400">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
            </svg>
          </div>
          <div className="text-2xl font-bold text-white font-mono">
            {avgRR} : 1
          </div>
        </div>

        {/* Matches Card with Dropdown */}
        <div className="relative flex-1 xl:flex-none">
          <button
            onClick={() => setDropdownOpen(dropdownOpen === "matches" ? null : "matches")}
            className="w-full text-left bg-gradient-to-b from-[#121216] to-[#0a0a0c] border border-emerald-500/30 rounded-xl p-4 min-w-[140px] hover:border-emerald-500/60 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.1)] focus:outline-none"
          >
            <div className="text-emerald-500/60 text-[10px] font-semibold uppercase tracking-wider mb-1.5 flex items-center justify-between">
              Matches Found
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform ${dropdownOpen === "matches" ? 'rotate-180' : ''}`}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div className="text-2xl font-bold text-emerald-400 font-mono">
              {matchCount}
            </div>
          </button>

          <AnimatePresence>
            {dropdownOpen === "matches" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-full mt-2 right-0 w-80 bg-[#121216]/95 backdrop-blur-xl border border-emerald-500/20 rounded-xl p-4 shadow-2xl z-50"
              >
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs text-emerald-500/50 uppercase tracking-widest font-semibold">
                    Ticker List
                  </span>
                  <button onClick={() => handleCopy(tickerList)} className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-semibold bg-emerald-500/10 px-2 py-1 rounded transition-colors">
                    {copied ? "COPIED!" : "COPY ALL"}
                  </button>
                </div>
                <div className="text-sm font-mono text-white/80 leading-relaxed bg-black/40 p-3 rounded-lg border border-white/5 max-h-48 overflow-y-auto">
                  {tickerList || "No tickers found."}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Rejected Tickers Dropdown */}
        <div className="relative flex-1 xl:flex-none">
          <button
            onClick={() => setDropdownOpen(dropdownOpen === "rejected" ? null : "rejected")}
            className="w-full text-left bg-[#121216] border border-red-500/20 rounded-xl p-4 min-w-[140px] hover:border-red-500/40 transition-colors focus:outline-none"
          >
            <div className="text-red-400/60 text-[10px] font-semibold uppercase tracking-wider mb-1.5 flex items-center justify-between">
              Rejected (Watchlist)
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform ${dropdownOpen === "rejected" ? 'rotate-180' : ''}`}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div className="text-2xl font-bold text-red-400 font-mono">
              {summary?.rejected_by_rr?.length || 0}
            </div>
          </button>

          <AnimatePresence>
            {dropdownOpen === "rejected" && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-full mt-2 right-0 w-80 bg-[#121216]/95 backdrop-blur-xl border border-red-500/20 rounded-xl p-4 shadow-2xl z-50"
              >
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs text-red-400/50 uppercase tracking-widest font-semibold">
                    Failed Hard Filter
                  </span>
                  <button onClick={() => handleCopy(rejectedList)} className="flex items-center gap-1.5 text-xs text-red-400 hover:text-red-300 font-semibold bg-red-500/10 px-2 py-1 rounded transition-colors">
                    {copied ? "COPIED!" : "COPY ALL"}
                  </button>
                </div>
                <div className="text-sm font-mono text-white/80 leading-relaxed bg-black/40 p-3 rounded-lg border border-white/5 max-h-48 overflow-y-auto">
                  {rejectedList || "No rejected tickers."}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

      </div>
    </div>
  );
}
