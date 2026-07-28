"use client";

import React, { useState } from "react";
import type { ScanSummaryWithTimestamp, FinalPick } from "@/lib/data-fetcher";
import { motion, AnimatePresence } from "motion/react";
import { BarChart3, TrendingUp, Target, Search, XCircle, Copy, Check } from "lucide-react";

export function DashboardHeader({
  summary,
  picks
}: {
  summary: ScanSummaryWithTimestamp | null;
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
    <div className="flex flex-col xl:flex-row gap-8 justify-between items-start xl:items-end w-full">
      <div className="flex-shrink-0">
        <motion.div 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="inline-flex items-center gap-2 rounded-full border border-emerald-500/20 bg-emerald-500/10 px-3 py-1 mb-4 backdrop-blur-sm"
        >
          <span className="relative flex h-2 w-2">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
          </span>
          <span className="text-[10px] font-bold text-emerald-400 tracking-widest uppercase">
            Live Results // {summary?.mode || "ALL"}
          </span>
        </motion.div>
        
        <motion.h1 
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-2"
        >
          Dashboard
        </motion.h1>
        
        <motion.p 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          className="text-white/50 text-sm font-mono flex items-center gap-2" 
          suppressHydrationWarning
        >
          <BarChart3 className="w-4 h-4" />
          Last scan: {summary?.timestamp ? new Date(summary.timestamp).toLocaleString() : "Just now"}
        </motion.p>
      </div>

      <div className="flex flex-wrap gap-4 w-full xl:w-auto xl:flex-nowrap">
        {/* Total Scanned Card */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.3 }}
          className="group bg-white/[0.02] border border-white/10 rounded-2xl p-5 min-w-[160px] flex-1 xl:flex-none relative overflow-hidden hover:bg-white/[0.04] transition-all hover:border-white/20 hover:shadow-lg hover:shadow-black/50"
        >
          <div className="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity">
            <Search className="w-12 h-12" />
          </div>
          <div className="text-white/40 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
            Total Scanned
          </div>
          <div className="text-3xl font-bold text-white font-mono tracking-tight">
            {totalScanned.toLocaleString()}
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-emerald-400/80">
            <TrendingUp className="w-3 h-3" />
            <span>Market wide</span>
          </div>
        </motion.div>

        {/* High Confidence Card */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.4 }}
          className="group bg-emerald-500/[0.03] border border-emerald-500/10 rounded-2xl p-5 min-w-[160px] flex-1 xl:flex-none relative overflow-hidden hover:bg-emerald-500/[0.08] transition-all hover:border-emerald-500/30 hover:shadow-[0_0_20px_rgba(16,185,129,0.15)]"
        >
          <div className="text-emerald-400/60 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
            High Confidence
          </div>
          <div className="text-3xl font-bold text-white font-mono tracking-tight flex items-baseline gap-2">
            {highConfidenceCount}
            <span className="text-xs text-white/40 font-sans">matches</span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-emerald-400">
            <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)]" />
            <span>A+ Setups</span>
          </div>
        </motion.div>

        {/* Avg Risk Reward Card */}
        <motion.div 
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5 }}
          className="group bg-purple-500/[0.03] border border-purple-500/10 rounded-2xl p-5 min-w-[160px] flex-1 xl:flex-none relative overflow-hidden hover:bg-purple-500/[0.08] transition-all hover:border-purple-500/30 hover:shadow-[0_0_20px_rgba(168,85,247,0.15)]"
        >
          <div className="text-purple-400/60 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center gap-2">
            Avg Risk:Reward
          </div>
          <div className="text-3xl font-bold text-white font-mono tracking-tight flex items-baseline gap-2">
            {avgRR}
            <span className="text-lg text-white/40">: 1</span>
          </div>
          <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-purple-400/80">
            <Target className="w-3 h-3" />
            <span>Portfolio avg</span>
          </div>
        </motion.div>

        {/* Matches Card with Dropdown */}
        <div className="relative flex-1 xl:flex-none z-50">
          <motion.button
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
            onClick={() => setDropdownOpen(dropdownOpen === "matches" ? null : "matches")}
            className="w-full h-full text-left bg-gradient-to-br from-emerald-500/10 to-transparent border border-emerald-500/30 rounded-2xl p-5 min-w-[160px] hover:border-emerald-500/60 transition-all hover:shadow-[0_0_25px_rgba(16,185,129,0.2)] focus:outline-none ring-1 ring-emerald-500/0 hover:ring-emerald-500/20"
          >
            <div className="text-emerald-400/80 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center justify-between">
              Matches Found
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform duration-300 ${dropdownOpen === "matches" ? 'rotate-180' : ''}`}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div className="text-3xl font-bold text-emerald-400 font-mono tracking-tight">
              {matchCount}
            </div>
          </motion.button>

          <AnimatePresence>
            {dropdownOpen === "matches" && (
              <motion.div
                initial={{ opacity: 0, y: 15, scale: 0.95, filter: "blur(4px)" }}
                animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: 10, scale: 0.95, filter: "blur(4px)" }}
                transition={{ duration: 0.2 }}
                className="absolute top-[calc(100%+0.5rem)] right-0 w-80 bg-[#0a0a0c]/95 backdrop-blur-2xl border border-emerald-500/30 rounded-2xl p-5 shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-50 ring-1 ring-white/5"
              >
                <div className="flex justify-between items-center mb-4">
                  <span className="text-[10px] text-emerald-400 uppercase tracking-widest font-bold">
                    Ticker List
                  </span>
                  <button 
                    onClick={() => handleCopy(tickerList)} 
                    className="flex items-center gap-1.5 text-xs text-emerald-300 hover:text-white font-semibold bg-emerald-500/20 hover:bg-emerald-500/40 px-3 py-1.5 rounded-md transition-colors"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    {copied ? "COPIED" : "COPY ALL"}
                  </button>
                </div>
                <div className="text-sm font-mono text-white/90 leading-relaxed bg-black/50 p-4 rounded-xl border border-white/5 max-h-56 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                  {tickerList || <span className="text-white/30 italic">No tickers found.</span>}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Rejected Tickers Dropdown */}
        <div className="relative flex-1 xl:flex-none z-40">
          <motion.button
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
            onClick={() => setDropdownOpen(dropdownOpen === "rejected" ? null : "rejected")}
            className="w-full h-full text-left bg-white/[0.01] border border-red-500/20 rounded-2xl p-5 min-w-[160px] hover:bg-red-500/[0.05] transition-all hover:border-red-500/40 focus:outline-none"
          >
            <div className="text-red-400/60 text-[10px] font-bold uppercase tracking-widest mb-2 flex items-center justify-between">
              Rejected (RR)
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform duration-300 ${dropdownOpen === "rejected" ? 'rotate-180' : ''}`}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div className="text-3xl font-bold text-red-400/90 font-mono tracking-tight flex items-center gap-2">
              {summary?.rejected_by_rr?.length || 0}
              <XCircle className="w-5 h-5 text-red-500/40" />
            </div>
          </motion.button>

          <AnimatePresence>
            {dropdownOpen === "rejected" && (
              <motion.div
                initial={{ opacity: 0, y: 15, scale: 0.95, filter: "blur(4px)" }}
                animate={{ opacity: 1, y: 0, scale: 1, filter: "blur(0px)" }}
                exit={{ opacity: 0, y: 10, scale: 0.95, filter: "blur(4px)" }}
                transition={{ duration: 0.2 }}
                className="absolute top-[calc(100%+0.5rem)] right-0 w-80 bg-[#0a0a0c]/95 backdrop-blur-2xl border border-red-500/30 rounded-2xl p-5 shadow-[0_20px_50px_rgba(0,0,0,0.5)] z-50 ring-1 ring-white/5"
              >
                <div className="flex justify-between items-center mb-4">
                  <span className="text-[10px] text-red-400 uppercase tracking-widest font-bold">
                    Failed Hard Filter
                  </span>
                  <button 
                    onClick={() => handleCopy(rejectedList)} 
                    className="flex items-center gap-1.5 text-xs text-red-300 hover:text-white font-semibold bg-red-500/20 hover:bg-red-500/40 px-3 py-1.5 rounded-md transition-colors"
                  >
                    {copied ? <Check className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                    {copied ? "COPIED" : "COPY ALL"}
                  </button>
                </div>
                <div className="text-sm font-mono text-white/90 leading-relaxed bg-black/50 p-4 rounded-xl border border-white/5 max-h-56 overflow-y-auto scrollbar-thin scrollbar-thumb-white/10 scrollbar-track-transparent">
                  {rejectedList || <span className="text-white/30 italic">No rejected tickers.</span>}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}

