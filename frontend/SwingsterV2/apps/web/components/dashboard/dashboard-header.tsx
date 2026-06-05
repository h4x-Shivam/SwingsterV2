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
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [copied, setCopied] = useState(false);

  const totalScanned = summary?.total_scanned || 0;
  const matchCount = picks.length;
  const tickerList = picks.map(p => p.symbol).join(", ");

  const handleCopy = () => {
    navigator.clipboard.writeText(tickerList);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="flex flex-col md:flex-row gap-6 justify-between items-start md:items-end">
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
        <p className="text-white/40 text-sm font-mono">
          Last scan: {summary?.timestamp ? new Date(summary.timestamp).toLocaleString() : "Just now"}
        </p>
      </div>

      <div className="flex gap-4">
        {/* Total Scanned Card */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-5 min-w-[160px]">
          <div className="text-white/40 text-xs font-semibold uppercase tracking-wider mb-2">
            Total Scanned
          </div>
          <div className="text-3xl font-bold text-white font-mono">
            {totalScanned.toLocaleString()}
          </div>
        </div>

        {/* Matches Card with Dropdown */}
        <div className="relative">
          <button
            onClick={() => setDropdownOpen(!dropdownOpen)}
            className="text-left bg-gradient-to-b from-[#121216] to-[#0a0a0c] border border-emerald-500/30 rounded-xl p-5 min-w-[160px] hover:border-emerald-500/60 transition-colors shadow-[0_0_15px_rgba(16,185,129,0.1)] focus:outline-none"
          >
            <div className="text-emerald-500/60 text-xs font-semibold uppercase tracking-wider mb-2 flex items-center justify-between">
              Matches Found
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className={`transition-transform ${dropdownOpen ? 'rotate-180' : ''}`}>
                <polyline points="6 9 12 15 18 9"></polyline>
              </svg>
            </div>
            <div className="text-3xl font-bold text-emerald-400 font-mono">
              {matchCount}
            </div>
          </button>

          {/* Dropdown Menu */}
          <AnimatePresence>
            {dropdownOpen && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="absolute top-full mt-3 right-0 w-80 bg-[#121216]/95 backdrop-blur-xl border border-white/10 rounded-xl p-4 shadow-2xl z-50"
              >
                <div className="flex justify-between items-center mb-3">
                  <span className="text-xs text-white/50 uppercase tracking-widest font-semibold">
                    Ticker List
                  </span>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 text-xs text-emerald-400 hover:text-emerald-300 font-semibold bg-emerald-500/10 px-2 py-1 rounded transition-colors"
                  >
                    {copied ? (
                      <>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                        COPIED!
                      </>
                    ) : (
                      <>
                        <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                        COPY ALL
                      </>
                    )}
                  </button>
                </div>
                <div className="text-sm font-mono text-white/80 leading-relaxed bg-black/40 p-3 rounded-lg border border-white/5 max-h-48 overflow-y-auto">
                  {tickerList || "No tickers found."}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
