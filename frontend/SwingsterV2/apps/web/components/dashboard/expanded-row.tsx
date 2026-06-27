"use client";
import React from "react";
import type { FinalPick } from "@/lib/data-fetcher";
import { TradingViewChart } from "./trading-view-chart";
import { AlertTriangle, BookOpen, ExternalLink, Target, LineChart, ShieldAlert } from "lucide-react";

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
    { label: "Confidence", value: pick.conviction, color: pick.conviction === "HIGH" ? "text-emerald-400 font-bold" : "text-teal-400" },
    { label: "Pattern Age", value: `${pick.pattern_age} Days` },
    { label: "Trend", value: pick.trend },
  ];

  return (
    <div className="p-8 flex flex-col xl:flex-row gap-8 items-stretch w-full bg-[#020203] shadow-[inset_0_10px_20px_rgba(0,0,0,0.5)]">
      
      {/* ── Left Column: Details & Fundamentals ── */}
      <div className="flex-1 flex flex-col gap-6 w-full xl:max-w-md shrink-0">
        
        {/* Pattern Details Panel */}
        <div className="bg-[#0a0a0c]/80 border border-white/[0.08] rounded-2xl p-6 flex flex-col flex-1 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/5 rounded-full blur-[40px] -mr-16 -mt-16 transition-all duration-700 group-hover:bg-emerald-500/10 group-hover:blur-[50px]" />
          
          <div className="flex items-center gap-2 mb-6">
            <LineChart className="w-4 h-4 text-emerald-500" />
            <h4 className="text-xs font-bold text-white/50 uppercase tracking-widest">
              Trading Plan
            </h4>
          </div>

          <div className="space-y-4 text-sm flex-1 relative z-10">
            {details.map((d, i) => (
              <div key={i} className="flex justify-between items-center group/item hover:bg-white/[0.02] -mx-2 px-2 py-1 rounded transition-colors">
                <span className="text-white/40 text-xs uppercase tracking-wider">{d.label}</span>
                <span className={`font-mono text-right ${d.color || "text-white/90"}`}>{d.value}</span>
              </div>
            ))}
          </div>

          {pick.flags && (
            <div className="mt-6 inline-flex items-start gap-3 bg-red-500/10 border border-red-500/20 rounded-xl p-4 w-full shrink-0 relative z-10">
              <ShieldAlert className="w-5 h-5 text-red-400 mt-0.5 shrink-0" />
              <div>
                <span className="block text-xs font-bold text-red-400 uppercase tracking-wider mb-1">Risk Warning</span>
                <span className="text-sm text-red-300/80 leading-relaxed block">{pick.flags}</span>
              </div>
            </div>
          )}
        </div>

        {/* Fundamentals Redirect */}
        <div className="bg-gradient-to-br from-[#121216] to-[#0a0a0c] border border-white/[0.08] rounded-2xl p-6 flex flex-col justify-center items-center text-center shrink-0 relative overflow-hidden hover:border-white/[0.15] transition-colors">
          <div className="absolute inset-0 bg-[url('/noise.png')] opacity-20 mix-blend-overlay pointer-events-none" />
          <div className="w-14 h-14 bg-emerald-500/10 rounded-full flex items-center justify-center mb-4 border border-emerald-500/20 shadow-[0_0_20px_rgba(16,185,129,0.15)] relative z-10">
            <BookOpen className="w-6 h-6 text-emerald-500" />
          </div>
          <h4 className="text-base font-bold text-white mb-2 relative z-10">Deep Dive into Fundamentals</h4>
          <p className="text-xs text-white/50 mb-6 max-w-[260px] relative z-10 leading-relaxed">
            View detailed financial statements, ratios, and shareholding patterns for {pick.symbol} on Screener.in
          </p>
          <a
            href={`https://www.screener.in/company/${getScreenerSymbol(pick.symbol)}/`}
            target="_blank"
            rel="noopener noreferrer"
            className="px-6 py-3 bg-white hover:bg-emerald-400 text-black font-bold text-xs uppercase tracking-widest rounded-xl transition-all shadow-lg flex items-center justify-center gap-2 w-full relative z-10"
          >
            Open Screener.in
            <ExternalLink className="w-4 h-4" />
          </a>
        </div>
      </div>

      {/* ── Right Column: TradingView Chart ── */}
      <div className="flex-[1.5] flex flex-col w-full h-full min-h-[500px]">
        <div className="bg-[#0a0a0c]/80 border border-white/[0.08] rounded-2xl p-5 flex-1 flex flex-col relative overflow-hidden group">
          {/* Header over chart */}
          <div className="flex justify-between items-center mb-5 px-1">
            <div className="flex items-center gap-3">
              <span className="font-extrabold text-white tracking-wide text-2xl">{pick.symbol}</span>
              <div className="flex bg-yellow-500/10 text-yellow-500 border border-yellow-500/20 rounded-full px-2 py-0.5 items-center gap-1 shadow-[0_0_10px_rgba(234,179,8,0.2)]">
                <Target className="w-3 h-3" />
                <span className="text-[10px] font-bold uppercase tracking-widest">#{pick.rank}</span>
              </div>
            </div>
            
            {/* Chart action buttons inline */}
            <div className="flex items-center gap-2">
              <a 
                href={`https://in.tradingview.com/chart/?symbol=NSE:${pick.symbol}`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-1.5 px-3 py-1.5 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 border border-emerald-500/30 font-bold text-[10px] uppercase tracking-widest rounded-lg transition-colors"
                title="Open full chart in TradingView"
              >
                Full Chart
                <ExternalLink className="w-3 h-3" />
              </a>
              <button 
                onClick={(e) => {
                  e.stopPropagation();
                  if (onToggleWatchlist) onToggleWatchlist();
                }}
                className={`flex items-center gap-1.5 px-3 py-1.5 border font-bold text-[10px] uppercase tracking-widest rounded-lg transition-all ${
                  isWatched 
                    ? "bg-emerald-500 text-black border-emerald-500 shadow-[0_0_15px_rgba(16,185,129,0.4)]" 
                    : "bg-white/5 border-white/10 hover:bg-white/10 text-white/70 hover:text-white"
                }`}
              >
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill={isWatched ? "currentColor" : "none"} stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                </svg>
                {isWatched ? "Saved" : "Watch"}
              </button>
            </div>
          </div>

          {/* TradingView Chart Container */}
          <div className="flex-1 w-full bg-[#020203] rounded-xl border border-white/5 overflow-hidden relative min-h-[400px] ring-1 ring-white/5 ring-inset">
            <TradingViewChart symbol={pick.symbol} />
          </div>

        </div>
      </div>

    </div>
  );
}
