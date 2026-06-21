"use client";
import React from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { TradingViewChart } from "./trading-view-chart";

function getScreenerSymbol(rawSymbol: string): string {
  return rawSymbol
    .replace(/\.(NS|NSE|BO|BSE)$/i, '')
    .replace(/-EQ$/i, '')
    .trim()
    .toUpperCase();
}

export function ExpandedRow({ 
  pick, 
  isWatched = false, 
  onToggleWatchlist 
}: { 
  pick: FinalPick;
  isWatched?: boolean;
  onToggleWatchlist?: () => void;
}) {

  const details = [
    { label: "Pattern", value: pick.pattern },
    { label: "Status", value: "Breakout Ready", color: "text-white" },
    { label: "Breakout Level", value: `₹${pick.buy_point.toFixed(2)}` },
    { label: "Stop Loss", value: `₹${pick.stop_loss.toFixed(2)}` },
    { label: "Target 1", value: `₹${pick.target.toFixed(2)}` },
    { label: "Target 2", value: `₹${pick.target2?.toFixed(2) || "—"}` },
    { label: "Risk:Reward", value: `${pick.rr_ratio.toFixed(1)} : 1` },
    { label: "Confidence", value: pick.conviction, color: pick.conviction === "HIGH" ? "text-emerald-400" : "text-teal-400" },
    { label: "Pattern Age", value: `${pick.pattern_age} Days` },
    { label: "Trend", value: pick.trend },
  ];

  return (
    <div className="p-8 flex flex-col xl:flex-row gap-8 items-stretch w-full bg-[#0a0a0c] shadow-inner">
      
      {/* ── Left Column: Details & Fundamentals ── */}
      <div className="flex-1 flex flex-col gap-6 w-full xl:max-w-md shrink-0">
        
        {/* Pattern Details */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-6 flex flex-col flex-1">
          <h4 className="text-xs font-semibold text-white/50 uppercase tracking-widest mb-4">
            Pattern Details
          </h4>
          <div className="space-y-3 text-sm flex-1">
            {details.map((d, i) => (
              <div key={i} className="flex justify-between items-center">
                <span className="text-white/40">{d.label}</span>
                <span className={`font-medium ${d.color || "text-white"}`}>{d.value}</span>
              </div>
            ))}
          </div>

          {pick.flags && (
            <div className="mt-6 inline-flex items-start gap-2 bg-red-500/10 border border-red-500/20 rounded-lg p-3 w-full shrink-0">
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

        {/* Fundamentals Redirect */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-6 flex flex-col justify-center items-center text-center shrink-0">
          <div className="w-12 h-12 bg-white/5 rounded-full flex items-center justify-center mb-4 border border-white/10">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500"><path d="M21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h6"></path><polyline points="21 3 14 3 14 10"></polyline><line x1="21" y1="3" x2="10" y2="14"></line></svg>
          </div>
          <h4 className="text-sm font-semibold text-white mb-2">Deep Dive into Fundamentals</h4>
          <p className="text-xs text-white/50 mb-6 max-w-xs">
            View detailed financial statements, ratios, and shareholding patterns for {pick.symbol} on Screener.in
          </p>
          <a
            href={`https://www.screener.in/company/${getScreenerSymbol(pick.symbol)}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-2.5 bg-emerald-500 hover:bg-emerald-400 text-[#060608] font-bold text-sm tracking-wide rounded-lg transition-colors shadow-[0_0_15px_rgba(16,185,129,0.2)] flex items-center justify-center gap-2 w-full"
          >
            Open Screener.in
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
          </a>
        </div>
      </div>

      {/* ── Right Column: TradingView Chart ── */}
      <div className="flex-[1.5] flex flex-col w-full h-full min-h-[500px]">
        <div className="bg-[#121216] border border-white/5 rounded-xl p-4 flex-1 flex flex-col relative overflow-hidden group">
          {/* Header over chart */}
          <div className="flex justify-between items-center mb-4">
            <div className="flex items-center gap-2">
              <span className="font-bold text-white tracking-wider text-lg">{pick.symbol}</span>
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none" className="text-yellow-500"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            </div>
            <div className="bg-emerald-500/10 text-emerald-400 text-[10px] px-2 py-1 rounded border border-emerald-500/20 uppercase tracking-widest">
              #{pick.rank} Match
            </div>
          </div>

          {/* TradingView Chart */}
          <div className="flex-1 w-full bg-[#0a0a0c] rounded-lg border border-white/5 overflow-hidden relative min-h-[300px]">
            <TradingViewChart symbol={pick.symbol} />
          </div>

          {/* Action Buttons */}
          <div className="mt-4 flex flex-col gap-3">
            <a 
              href={`https://in.tradingview.com/chart/?symbol=NSE:${pick.symbol}`}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-center gap-2 w-full py-3 bg-emerald-500 hover:bg-emerald-400 text-[#060608] font-bold tracking-wide rounded-lg transition-colors shadow-[0_0_20px_rgba(16,185,129,0.3)]"
            >
              Open in TradingView
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            </a>
            <button 
              onClick={(e) => {
                e.stopPropagation();
                if (onToggleWatchlist) onToggleWatchlist();
              }}
              className={`flex items-center justify-center gap-2 w-full py-3 border font-semibold tracking-wide rounded-lg transition-colors ${
                isWatched 
                  ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 hover:bg-emerald-500/20" 
                  : "bg-transparent border-white/10 hover:bg-white/5 text-white/80"
              }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill={isWatched ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              {isWatched ? "Remove from Watchlist" : "Add to Watchlist"}
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
