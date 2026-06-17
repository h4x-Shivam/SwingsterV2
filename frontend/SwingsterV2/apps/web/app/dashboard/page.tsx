import React from "react";
import { redirect } from "next/navigation";
import { createClient } from "@/lib/supabase/server";
import { getScanSummary, getFinalPicks } from "@/lib/data-fetcher";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DataTable } from "@/components/dashboard/data-table";
import { getWatchlistSymbols } from "@/app/actions/watchlist";
import { Navbar } from "@/components/navbar";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  // Auth guard — redirect unauthenticated users
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) {
    redirect("/login");
  }

  const summary = await getScanSummary();
  const picks = await getFinalPicks();
  const watchlistSet = await getWatchlistSymbols();
  // Pass down as array or Set. Since we pass to a client component, converting to array is safer for serialization.
  const watchlist = Array.from(watchlistSet);

  return (
    <>
      <Navbar isAuthenticated={true} />
      <main className="bg-[#060608] min-h-screen text-white/90 p-6 md:p-12 relative overflow-hidden pt-24 md:pt-32">
        {/* Glow background accent */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/10 blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto relative z-10">
          <DashboardHeader summary={summary} picks={picks} />
          
          <div className="mt-12">
            <DataTable picks={picks} initialWatchlist={watchlist} />
          </div>
        </div>
      </main>
    </>
  );
}

