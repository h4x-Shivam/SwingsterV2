import React from "react";
import type { FinalPick } from "@/lib/data-fetcher";

export function ExpandedRow({ pick }: { pick: FinalPick }) {
  const scores = [
    { label: "Pattern Quality", value: pick.signal_strength, weight: "40%" },
    { label: "Volume Confirmation", value: pick.volume_score, weight: "25%" },
    { label: "Risk Reward", value: pick.rr_score, weight: "20%" },
    { label: "Trend Strength", value: pick.stage2_score, weight: "10%" },
    { label: "Freshness (RS)", value: pick.rs_score, weight: "5%" },
  ];

  const details = [
    { label: "Pattern", value: pick.pattern },
    { label: "Status", value: "Breakout Ready", color: "text-white" },
    { label: "Breakout Level", value: `₹${pick.buy_point.toFixed(2)}` },
    { label: "Stop Loss", value: `₹${pick.stop_loss.toFixed(2)}` },
    { label: "Target 1", value: `₹${pick.target.toFixed(2)}` },
    { label: "Target 2", value: `₹${pick.target2?.toFixed(2) || "N/A"}` },
    { label: "Risk:Reward", value: `${pick.rr_ratio.toFixed(1)} : 1` },
    { label: "Confidence", value: pick.conviction, color: pick.conviction === "HIGH" ? "text-emerald-400" : "text-teal-400" },
    { label: "Pattern Age", value: `${pick.pattern_age} Days` },
    { label: "Trend", value: pick.trend },
  ];

  return (
    <div className="p-8 flex flex-col xl:flex-row gap-8 items-start w-full bg-[#0a0a0c] shadow-inner">
      
      {/* ── Left Column: AI Judge & Fundamentals ── */}
      <div className="flex-1 space-y-8 w-full">
        {/* Judge Verdict */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-6">
          <div className="flex items-center gap-2 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500">
              <path d="M12 22c5.523 0 10-4.477 10-10S17.523 2 12 2 2 6.477 2 12s4.477 10 10 10z"></path>
              <path d="M9 12l2 2 4-4"></path>
            </svg>
            <h4 className="text-sm font-semibold text-white uppercase tracking-widest">
              AI Judge Verdict
            </h4>
          </div>
          <p className="text-[15px] text-white/70 leading-relaxed">
            {pick.judge_verdict || "No verdict provided by the judge."}
          </p>

          {pick.flags && (
            <div className="mt-4 inline-flex items-start gap-2 bg-red-500/10 border border-red-500/20 rounded-lg p-3 w-full">
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

        {/* Fundamentals (New) */}
        {pick.fundamentals && (
          <div className="bg-[#121216] border border-white/5 rounded-xl p-6">
            <h4 className="text-xs font-semibold text-white/50 uppercase tracking-widest mb-4">
              Fundamental Data (NSE)
            </h4>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Market Cap</div>
                <div className="text-sm font-mono text-white">{pick.fundamentals.market_cap}</div>
              </div>
              <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">P/E Ratio</div>
                <div className="text-sm font-mono text-white">{pick.fundamentals.pe_ratio}</div>
              </div>
              <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">ROE</div>
                <div className="text-sm font-mono text-emerald-400">{pick.fundamentals.roe}</div>
              </div>
              <div className="bg-black/30 p-3 rounded-lg border border-white/5">
                <div className="text-[10px] text-white/40 uppercase tracking-wider mb-1">Debt to Equity</div>
                <div className="text-sm font-mono text-white">{pick.fundamentals.debt_to_equity}</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* ── Center Column: Score Breakdown & Details ── */}
      <div className="flex-[1.2] flex flex-col gap-6 w-full">
        {/* Score Breakdown */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-6">
          <div className="flex justify-between items-end mb-6">
            <h4 className="text-xs font-semibold text-white/50 uppercase tracking-widest">
              Score Breakdown
            </h4>
            <div className="flex items-baseline gap-1">
              <span className="text-3xl font-bold font-mono text-emerald-400">{pick.composite_score.toFixed(0)}</span>
              <span className="text-xs text-white/40 font-mono">/100</span>
            </div>
          </div>
          <div className="space-y-4">
            {scores.map((s, i) => (
              <div key={i}>
                <div className="flex justify-between items-center mb-1.5 text-[11px] font-medium">
                  <div className="text-white/60">{s.label} <span className="text-white/30 ml-1">({s.weight})</span></div>
                  <div className="text-white font-mono">{s.value.toFixed(0)} <span className="text-white/30">/100</span></div>
                </div>
                <div className="w-full h-1.5 bg-black/50 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-emerald-500 rounded-full shadow-[0_0_8px_rgba(16,185,129,0.5)]"
                    style={{ width: `${s.value}%` }}
                  />
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Pattern Details */}
        <div className="bg-[#121216] border border-white/5 rounded-xl p-6 flex-1">
          <h4 className="text-xs font-semibold text-white/50 uppercase tracking-widest mb-4">
            Pattern Details
          </h4>
          <div className="space-y-3 text-sm">
            {details.map((d, i) => (
              <div key={i} className="flex justify-between items-center">
                <span className="text-white/40">{d.label}</span>
                <span className={`font-medium ${d.color || "text-white"}`}>{d.value}</span>
              </div>
            ))}
          </div>
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
              #1 Match
            </div>
          </div>

          {/* TradingView iframe */}
          <div className="flex-1 w-full bg-[#0a0a0c] rounded-lg border border-white/5 overflow-hidden relative min-h-[300px]">
            {/* The actual TradingView Advanced Chart Widget iframe */}
            <iframe 
              src={`https://s.tradingview.com/widgetembed/?frameElementId=tradingview_123&symbol=NSE:${pick.symbol}&interval=D&symboledit=0&saveimage=0&toolbarbg=121216&studies=%5B%5D&theme=dark&style=1&timezone=Asia%2FKolkata&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en`}
              className="absolute inset-0 w-full h-full border-none"
              allowFullScreen
            />
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
            <button className="flex items-center justify-center gap-2 w-full py-3 bg-transparent border border-white/10 hover:bg-white/5 text-white/80 font-semibold tracking-wide rounded-lg transition-colors">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
              Add to Watchlist
            </button>
          </div>
        </div>
      </div>

    </div>
  );
}
