"use client";

import React, { useState, useEffect } from "react";
import { motion } from "motion/react";
import Link from "next/link";

/* ── Mock watchlist data for the landing page showcase ── */
const mockStocks = [
  { symbol: "RELIANCE", sector: "Energy", score: 92, change: +2.34, rr: "3.2:1", conviction: "HIGH" },
  { symbol: "TCS", sector: "IT", score: 87, change: +1.12, rr: "2.8:1", conviction: "HIGH" },
  { symbol: "HDFCBANK", sector: "Banking", score: 81, change: -0.87, rr: "2.5:1", conviction: "MEDIUM" },
  { symbol: "INFY", sector: "IT", score: 79, change: +3.56, rr: "3.1:1", conviction: "HIGH" },
  { symbol: "BHARTIARTL", sector: "Telecom", score: 76, change: +0.95, rr: "2.2:1", conviction: "MEDIUM" },
];

/* ── Seeded sparkline so values are stable across renders ── */
function sparkPath(seed: number): string {
  const pts: { x: number; y: number }[] = [];
  let v = 50;
  let s = seed;
  for (let i = 0; i < 16; i++) {
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const r = (s % 1000) / 1000;
    v += (r - 0.45) * 10;
    v = Math.max(15, Math.min(85, v));
    pts.push({ x: (i / 15) * 100, y: v });
  }
  return pts.map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`).join(" ");
}

/* ── Animated counter ── */
function AnimatedCounter({ target, suffix = "" }: { target: number; suffix?: string }) {
  const [val, setVal] = useState(0);

  useEffect(() => {
    let frame: number;
    const duration = 1200;
    const start = performance.now();

    const tick = (now: number) => {
      const elapsed = now - start;
      const progress = Math.min(elapsed / duration, 1);
      // ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3);
      setVal(Math.round(eased * target));
      if (progress < 1) frame = requestAnimationFrame(tick);
    };

    frame = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(frame);
  }, [target]);

  return (
    <span>
      {val}
      {suffix}
    </span>
  );
}

/* ── Features list ── */
const features = [
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
        <circle cx="12" cy="7" r="4"></circle>
      </svg>
    ),
    title: "Per-User Isolation",
    desc: "Every user gets their own private watchlist, secured by row-level policies.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
      </svg>
    ),
    title: "One-Click Save",
    desc: "Star any stock from the dashboard to instantly add it to your watchlist.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
      </svg>
    ),
    title: "Live Pattern Sync",
    desc: "Active setups sync automatically — see full AI analysis for watchlisted picks.",
  },
  {
    icon: (
      <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="11" width="18" height="11" rx="2" ry="2"></rect>
        <path d="M7 11V7a5 5 0 0 1 10 0v4"></path>
      </svg>
    ),
    title: "End-to-End Encrypted",
    desc: "Data is secured via Supabase RLS — only you can see your saved stocks.",
  },
];

export function WatchlistShowcase({ isAuthenticated = false }: { isAuthenticated?: boolean }) {
  const [hoveredRow, setHoveredRow] = useState<number | null>(null);
  const [starredRows, setStarredRows] = useState<Set<number>>(new Set([0, 3]));

  const toggleStar = (idx: number) => {
    setStarredRows((prev) => {
      const next = new Set(prev);
      if (next.has(idx)) next.delete(idx);
      else next.add(idx);
      return next;
    });
  };

  return (
    <section
      id="watchlist"
      className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden scroll-mt-24"
    >
      {/* Background accents */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-amber-500/5 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />
      <div
        className="absolute inset-0 z-0 pointer-events-none"
        style={{
          backgroundImage:
            "radial-gradient(circle, rgba(255,255,255,0.02) 1px, transparent 1px)",
          backgroundSize: "40px 40px",
        }}
      />

      <div className="relative z-10 max-w-6xl mx-auto px-6">
        {/* ── Section Header ── */}
        <div className="text-center mb-16 md:mb-20">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 rounded-full border border-amber-500/30 bg-amber-500/10 px-4 py-1.5 mb-6"
          >
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="currentColor" stroke="none" className="text-amber-400">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
            </svg>
            <span className="text-xs font-medium text-amber-400 tracking-widest uppercase">
              Your Watchlist
            </span>
          </motion.div>

          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="text-4xl md:text-5xl lg:text-6xl font-bold text-white tracking-tight leading-tight mb-6"
          >
            Track the setups that{" "}
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-amber-400 to-emerald-400">
              matter to you
            </span>
          </motion.h2>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto leading-relaxed"
          >
            Save your favorite breakout candidates in one place.
          </motion.p>
        </div>

        {/* ── Main Content: Two-Column Layout ── */}
        <div className="flex flex-col lg:flex-row gap-10 lg:gap-14 items-start">
          {/* LEFT: Interactive Watchlist Preview */}
          <motion.div
            initial={{ opacity: 0, x: -40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.2 }}
            className="flex-[1.4] w-full"
          >
            <div className="rounded-2xl border border-white/10 bg-[#0c0c10]/80 backdrop-blur-xl overflow-hidden shadow-[0_0_60px_rgba(16,185,129,0.08)]">
              {/* Table Header Bar */}
              <div className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-[#0a0a0c]">
                <div className="flex items-center gap-2.5">
                  <div className="h-2.5 w-2.5 rounded-full bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.6)] animate-pulse" />
                  <span className="text-sm font-bold text-white tracking-wide uppercase">
                    My Watchlist
                  </span>
                </div>
                <span className="text-xs text-white/30 font-mono">
                  {mockStocks.length} saved
                </span>
              </div>

              {/* Column Headers */}
              <div className="grid grid-cols-[40px_1.5fr_0.7fr_0.8fr_0.7fr_1fr_40px] gap-2 px-6 py-3 text-[10px] font-semibold uppercase tracking-wider text-white/30 border-b border-white/5">
                <span></span>
                <span>Symbol</span>
                <span className="text-center">Score</span>
                <span className="text-center">R:R</span>
                <span className="text-right">Change</span>
                <span className="text-center">Trend</span>
                <span></span>
              </div>

              {/* Rows */}
              <div className="divide-y divide-white/[0.03]">
                {mockStocks.map((stock, i) => {
                  const isHovered = hoveredRow === i;
                  const isStarred = starredRows.has(i);
                  const positive = stock.change >= 0;

                  return (
                    <motion.div
                      key={stock.symbol}
                      initial={{ opacity: 0, y: 10 }}
                      whileInView={{ opacity: 1, y: 0 }}
                      viewport={{ once: true }}
                      transition={{ duration: 0.4, delay: 0.3 + i * 0.08 }}
                      onMouseEnter={() => setHoveredRow(i)}
                      onMouseLeave={() => setHoveredRow(null)}
                      className={`grid grid-cols-[40px_1.5fr_0.7fr_0.8fr_0.7fr_1fr_40px] gap-2 px-6 py-3.5 items-center cursor-pointer transition-all duration-200 ${
                        isHovered ? "bg-white/[0.04]" : ""
                      }`}
                    >
                      {/* Rank Badge */}
                      <div className="flex justify-center">
                        <span
                          className={`text-[10px] font-mono font-bold w-6 h-6 rounded-full flex items-center justify-center ${
                            i === 0
                              ? "bg-yellow-500/10 text-yellow-500 border border-yellow-500/20"
                              : i === 1
                                ? "bg-slate-300/10 text-slate-300 border border-slate-300/20"
                                : i === 2
                                  ? "bg-amber-700/10 text-amber-600 border border-amber-700/20"
                                  : "text-white/30"
                          }`}
                        >
                          {i + 1}
                        </span>
                      </div>

                      {/* Symbol & Sector */}
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-sm font-bold text-white tracking-wide">
                            {stock.symbol}
                          </span>
                          {stock.conviction === "HIGH" && (
                            <span className="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-[8px] px-1.5 py-0.5 rounded-sm uppercase tracking-widest">
                              High
                            </span>
                          )}
                        </div>
                        <span className="text-[10px] text-white/30">{stock.sector}</span>
                      </div>

                      {/* Score */}
                      <div className="flex justify-center">
                        <span className="text-sm font-bold font-mono text-emerald-400 bg-emerald-500/10 border border-emerald-500/15 px-2 py-0.5 rounded">
                          {stock.score}
                        </span>
                      </div>

                      {/* R:R */}
                      <div className="text-center text-xs text-white/60 font-mono">
                        {stock.rr}
                      </div>

                      {/* Change */}
                      <div
                        className={`text-right text-xs font-bold font-mono ${
                          positive ? "text-emerald-400" : "text-red-400"
                        }`}
                      >
                        {positive ? "+" : ""}
                        {stock.change.toFixed(2)}%
                      </div>

                      {/* Sparkline */}
                      <div className="flex justify-center">
                        <svg viewBox="0 0 100 100" className="w-16 h-6" preserveAspectRatio="none">
                          <path
                            d={sparkPath(stock.symbol.charCodeAt(0) * 137 + i * 777)}
                            fill="none"
                            stroke={positive ? "#10b981" : "#ef4444"}
                            strokeWidth="3"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            opacity={0.7}
                          />
                        </svg>
                      </div>

                      {/* Star Button */}
                      <div className="flex justify-center">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            toggleStar(i);
                          }}
                          className={`p-1 rounded-full transition-all duration-200 ${
                            isStarred
                              ? "text-amber-400 scale-110"
                              : "text-white/20 hover:text-amber-400"
                          }`}
                        >
                          <svg
                            xmlns="http://www.w3.org/2000/svg"
                            width="14"
                            height="14"
                            viewBox="0 0 24 24"
                            fill={isStarred ? "currentColor" : "none"}
                            stroke="currentColor"
                            strokeWidth="2"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                          >
                            <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
                          </svg>
                        </button>
                      </div>
                    </motion.div>
                  );
                })}
              </div>

              {/* Footer */}
              <div className="px-6 py-4 border-t border-white/5 bg-[#0a0a0c]/50 flex items-center justify-between">
                <span className="text-[10px] text-white/20 font-mono uppercase tracking-wider">
                  Synced in real-time • Row-level security enabled
                </span>
                <div className="flex gap-1">
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500 shadow-[0_0_4px_rgba(16,185,129,0.6)]" />
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/40" />
                  <div className="w-1.5 h-1.5 rounded-full bg-emerald-500/20" />
                </div>
              </div>
            </div>
          </motion.div>

          {/* RIGHT: Features & Stats */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.7, delay: 0.3 }}
            className="flex-1 w-full flex flex-col gap-6"
          >
            {/* Stats Row */}
            <div className="grid grid-cols-2 gap-4">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4 }}
                className="bg-[#0c0c10]/80 border border-white/10 rounded-xl p-5 text-center"
              >
                <div className="text-3xl font-black text-white font-mono mb-1">
                  <AnimatedCounter target={100} suffix="%" />
                </div>
                <div className="text-[10px] text-white/40 uppercase tracking-widest">
                  Private
                </div>
              </motion.div>
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5 }}
                className="bg-[#0c0c10]/80 border border-white/10 rounded-xl p-5 text-center"
              >
                <div className="text-3xl font-black text-emerald-400 font-mono mb-1">
                  <AnimatedCounter target={0} suffix="ms" />
                </div>
                <div className="text-[10px] text-white/40 uppercase tracking-widest">
                  Sync Delay
                </div>
              </motion.div>
            </div>

            {/* Features List */}
            <div className="space-y-4">
              {features.map((f, i) => (
                <motion.div
                  key={f.title}
                  initial={{ opacity: 0, y: 15 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ duration: 0.4, delay: 0.4 + i * 0.1 }}
                  className="flex gap-4 items-start group"
                >
                  <div className="shrink-0 w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500/20 to-emerald-500/10 border border-white/10 flex items-center justify-center text-amber-400 group-hover:text-emerald-400 group-hover:border-emerald-500/20 transition-colors">
                    {f.icon}
                  </div>
                  <div>
                    <h4 className="text-sm font-bold text-white mb-1">{f.title}</h4>
                    <p className="text-xs text-white/40 leading-relaxed">{f.desc}</p>
                  </div>
                </motion.div>
              ))}
            </div>

            {/* CTA */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: 0.8 }}
              className="mt-2"
            >
              {isAuthenticated ? (
                <Link
                  href="/watchlist"
                  className="group flex items-center justify-center gap-2 w-full py-4 bg-gradient-to-r from-amber-500 to-emerald-500 hover:from-amber-400 hover:to-emerald-400 text-black font-bold rounded-xl transition-all duration-300 shadow-[0_0_25px_rgba(251,191,36,0.2),0_0_25px_rgba(16,185,129,0.2)] hover:shadow-[0_0_40px_rgba(251,191,36,0.3),0_0_40px_rgba(16,185,129,0.3)]"
                >
                  Open My Watchlist
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="transition-transform group-hover:translate-x-1"
                  >
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </Link>
              ) : (
                <Link
                  href="/login"
                  className="group flex items-center justify-center gap-2 w-full py-4 bg-gradient-to-r from-amber-500 to-emerald-500 hover:from-amber-400 hover:to-emerald-400 text-black font-bold rounded-xl transition-all duration-300 shadow-[0_0_25px_rgba(251,191,36,0.2),0_0_25px_rgba(16,185,129,0.2)] hover:shadow-[0_0_40px_rgba(251,191,36,0.3),0_0_40px_rgba(16,185,129,0.3)]"
                >
                  Sign In to Start Tracking
                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="18"
                    height="18"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2.5"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    className="transition-transform group-hover:translate-x-1"
                  >
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                    <polyline points="12 5 19 12 12 19"></polyline>
                  </svg>
                </Link>
              )}
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
