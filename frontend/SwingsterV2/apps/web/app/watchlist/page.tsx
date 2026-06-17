import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getWatchlistSymbols } from "@/app/actions/watchlist";
import { getFinalPicks } from "@/lib/data-fetcher";
import { DataTable } from "@/components/dashboard/data-table";
import { Navbar } from "@/components/navbar";

export const dynamic = "force-dynamic";

function getScreenerSymbol(rawSymbol: string): string {
  return rawSymbol
    .replace(/\.(NS|NSE|BO|BSE)$/i, '')
    .replace(/-EQ$/i, '')
    .trim()
    .toUpperCase();
}

export default async function WatchlistPage() {
  // Auth guard — redirect unauthenticated users
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    redirect("/login");
  }

  const watchlistSet = await getWatchlistSymbols();
  const watchlist = Array.from(watchlistSet);
  const picks = await getFinalPicks();

  // Find which watched symbols are in active picks
  const activePicks = picks.filter((pick) => watchlistSet.has(pick.symbol));
  
  // Find which watched symbols are stale (not in current picks)
  const staleSymbols = watchlist.filter((symbol) => !picks.some((p) => p.symbol === symbol));

  return (
    <>
      <Navbar isAuthenticated={true} />
      <main className="bg-[#060608] min-h-screen text-white/90 p-6 md:p-12 relative overflow-hidden pt-24 md:pt-32">
        {/* Glow background accent */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/10 blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto relative z-10">
          <div className="mb-12">
            <h1 className="text-4xl md:text-5xl font-black text-white tracking-tight uppercase">
              My <span className="text-emerald-500">Watchlist</span>
            </h1>
            <p className="text-white/50 mt-4 text-lg max-w-2xl">
              Keep track of your favorite setups. Active patterns show full AI Judge analysis, while older picks remain saved for your convenience.
            </p>
          </div>

          {watchlist.length === 0 ? (
            <div className="w-full h-64 border border-dashed border-white/10 rounded-xl flex flex-col items-center justify-center text-white/40 font-mono text-sm gap-4">
              <svg xmlns="http://www.w3.org/2000/svg" width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white/20">
                <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon>
              </svg>
              Your watchlist is empty. Star stocks from the dashboard to add them.
            </div>
          ) : (
            <div className="space-y-12">
              {activePicks.length > 0 && (
                <div>
                  <h2 className="text-xl font-bold text-white mb-6 uppercase tracking-widest flex items-center gap-2">
                    <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
                    Active Setups ({activePicks.length})
                  </h2>
                  <DataTable picks={activePicks} initialWatchlist={watchlist} />
                </div>
              )}

              {staleSymbols.length > 0 && (
                <div>
                  <h2 className="text-xl font-bold text-white/60 mb-6 uppercase tracking-widest">
                    Saved Symbols ({staleSymbols.length})
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {staleSymbols.map((symbol) => (
                      <div key={symbol} className="bg-[#121216] border border-white/5 rounded-xl p-6 flex flex-col justify-between">
                        <div className="flex justify-between items-start mb-4">
                          <div className="text-xl font-bold text-white tracking-wide">
                            {symbol}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <a
                            href={`https://in.tradingview.com/chart/?symbol=NSE:${symbol}`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 py-2 bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-400 text-xs font-bold uppercase tracking-wider rounded text-center transition-colors border border-emerald-500/20"
                          >
                            TradingView
                          </a>
                          <a
                            href={`https://www.screener.in/company/${getScreenerSymbol(symbol)}/`}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="flex-1 py-2 bg-white/5 hover:bg-white/10 text-white/80 text-xs font-bold uppercase tracking-wider rounded text-center transition-colors border border-white/10"
                          >
                            Screener
                          </a>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </main>
    </>
  );
}

