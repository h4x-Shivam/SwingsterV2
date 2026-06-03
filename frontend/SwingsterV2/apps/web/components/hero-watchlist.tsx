"use client";

import React from "react";

interface WatchlistRow {
  ticker: string;
  name: string;
  price: string;
  change: number;
  sparkline: number[];
}

// Seeded pseudo-random sparkline generator so values are stable across renders
function generateSparkline(seed: number, trend: number): number[] {
  const points: number[] = [];
  let value = 50;
  let s = seed;
  for (let i = 0; i < 20; i++) {
    // Simple LCG pseudo-random
    s = (s * 1103515245 + 12345) & 0x7fffffff;
    const random = (s % 1000) / 1000;
    const drift = trend > 0 ? 0.6 : -0.6;
    value += (random - 0.5 + drift * 0.15) * 8;
    value = Math.max(10, Math.min(90, value));
    points.push(value);
  }
  return points;
}

const watchlistData: WatchlistRow[] = [
  { ticker: "RELIANCE", name: "Reliance Industries", price: "₹2,943.50", change: 2.34, sparkline: generateSparkline(101, 1) },
  { ticker: "TCS", name: "Tata Consultancy Svcs", price: "₹4,187.25", change: 1.12, sparkline: generateSparkline(202, 1) },
  { ticker: "HDFCBANK", name: "HDFC Bank Ltd", price: "₹1,892.10", change: -0.87, sparkline: generateSparkline(303, -1) },
  { ticker: "INFY", name: "Infosys Ltd", price: "₹1,654.80", change: 3.56, sparkline: generateSparkline(404, 1) },
  { ticker: "ICICIBANK", name: "ICICI Bank Ltd", price: "₹1,298.45", change: -1.23, sparkline: generateSparkline(505, -1) },
  { ticker: "BHARTIARTL", name: "Bharti Airtel Ltd", price: "₹1,756.30", change: 0.95, sparkline: generateSparkline(606, 1) },
  { ticker: "SBIN", name: "State Bank of India", price: "₹842.65", change: -0.42, sparkline: generateSparkline(707, -1) },
  { ticker: "ITC", name: "ITC Ltd", price: "₹482.15", change: 1.87, sparkline: generateSparkline(808, 1) },
  { ticker: "KOTAKBANK", name: "Kotak Mahindra Bank", price: "₹1,934.70", change: -2.15, sparkline: generateSparkline(909, -1) },
  { ticker: "LT", name: "Larsen & Toubro Ltd", price: "₹3,421.90", change: 0.68, sparkline: generateSparkline(1010, 1) },
  { ticker: "AXISBANK", name: "Axis Bank Ltd", price: "₹1,165.30", change: 1.45, sparkline: generateSparkline(1111, 1) },
  { ticker: "WIPRO", name: "Wipro Ltd", price: "₹542.80", change: -0.31, sparkline: generateSparkline(1212, -1) },
];

function Sparkline({ data, positive }: { data: number[]; positive: boolean }) {
  const width = 96;
  const height = 28;
  const padding = 2;

  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min || 1;

  const points = data.map((v, i) => {
    const x = padding + (i / (data.length - 1)) * (width - padding * 2);
    const y = padding + (1 - (v - min) / range) * (height - padding * 2);
    return { x, y };
  });

  const linePath = points
    .map((p, i) => `${i === 0 ? "M" : "L"} ${p.x.toFixed(1)} ${p.y.toFixed(1)}`)
    .join(" ");

  // Closed area path for gradient fill
  const areaPath = `${linePath} L ${points[points.length - 1].x.toFixed(1)} ${height} L ${points[0].x.toFixed(1)} ${height} Z`;

  const color = positive ? "#00c896" : "#ef4444";
  const gradientId = `sparkGrad-${positive ? "g" : "r"}-${data[0].toFixed(0)}`;

  return (
    <svg
      width={width}
      height={height}
      viewBox={`0 0 ${width} ${height}`}
      className="shrink-0"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id={gradientId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor={color} stopOpacity={0.25} />
          <stop offset="100%" stopColor={color} stopOpacity={0} />
        </linearGradient>
      </defs>
      <path d={areaPath} fill={`url(#${gradientId})`} />
      <path
        d={linePath}
        fill="none"
        stroke={color}
        strokeWidth={1.5}
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  );
}

export function HeroWatchlist() {
  return (
    <div className="h-full w-full flex flex-col overflow-hidden">
      {/* ── Table header bar ── */}
      <div className="flex items-center justify-between px-4 md:px-6 py-3 border-b border-border-subtle shrink-0">
        <div className="flex items-center gap-2">
          <div className="h-2 w-2 rounded-full bg-accent animate-pulse-dot" />
          <span className="text-xs font-medium text-text-secondary tracking-wide uppercase">
            Watchlist
          </span>
        </div>
        <span className="text-[10px] text-text-muted font-mono">
          12 instruments
        </span>
      </div>

      {/* ── Column headers ── */}
      <div className="grid grid-cols-[0.9fr_1.2fr_100px_0.9fr_0.7fr] gap-2 px-4 md:px-6 py-2.5 text-[10px] md:text-[11px] font-medium text-text-muted uppercase tracking-wider border-b border-border-subtle shrink-0">
        <span>Ticker</span>
        <span>Name</span>
        <span className="text-center">Chart</span>
        <span className="text-right">Price</span>
        <span className="text-right">Change</span>
      </div>

      {/* ── Rows ── */}
      <div className="flex-1 overflow-hidden">
        {watchlistData.map((row, i) => (
          <div
            key={row.ticker}
            className={`watchlist-row grid grid-cols-[0.9fr_1.2fr_100px_0.9fr_0.7fr] gap-2 px-4 md:px-6 py-1.5 md:py-2 border-b border-border-subtle/50 items-center opacity-0 animate-fade-in-up`}
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <span className="text-xs md:text-sm font-semibold text-text-primary tracking-wide">
              {row.ticker}
            </span>
            <span className="text-[10px] md:text-xs text-text-muted truncate">
              {row.name}
            </span>
            <div className="flex justify-center">
              <Sparkline data={row.sparkline} positive={row.change >= 0} />
            </div>
            <span className="text-xs md:text-sm text-text-secondary font-mono text-right">
              {row.price}
            </span>
            <span
              className={`text-xs md:text-sm font-semibold font-mono text-right ${
                row.change >= 0 ? "text-gain" : "text-loss"
              }`}
            >
              {row.change >= 0 ? "+" : ""}
              {row.change.toFixed(2)}%
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
