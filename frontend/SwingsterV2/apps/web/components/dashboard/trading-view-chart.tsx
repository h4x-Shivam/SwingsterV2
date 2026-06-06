"use client";

import { AdvancedRealTimeChart } from "react-ts-tradingview-widgets";

interface TradingViewChartProps {
  symbol: string;
}

export function TradingViewChart({ symbol }: TradingViewChartProps) {
  // We use BSE: prefix since it tends to be more universally available 
  const tvSymbol = `BSE:${symbol}`;

  return (
    <div className="absolute inset-0 w-full h-full">
      <AdvancedRealTimeChart
        symbol={tvSymbol}
        interval="D"
        timezone="Asia/Kolkata"
        theme="dark"
        style="1"
        locale="en"
        enable_publishing={false}
        hide_top_toolbar={false}
        hide_legend={false}
        save_image={false}
        autosize={true}
      />
    </div>
  );
}
