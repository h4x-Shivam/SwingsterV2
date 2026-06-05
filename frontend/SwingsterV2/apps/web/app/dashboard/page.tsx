import React from "react";
import { getScanSummary, getFinalPicks } from "@/lib/data-fetcher";
import { DashboardHeader } from "@/components/dashboard/dashboard-header";
import { DataTable } from "@/components/dashboard/data-table";

export const dynamic = "force-dynamic";

export default async function DashboardPage() {
  const summary = await getScanSummary();
  const picks = await getFinalPicks();

  return (
    <main className="bg-[#060608] min-h-screen text-white/90 p-6 md:p-12 relative overflow-hidden">
      {/* Glow background accent */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-[800px] h-[400px] bg-emerald-500/10 blur-[120px] pointer-events-none" />

      <div className="max-w-7xl mx-auto relative z-10">
        <DashboardHeader summary={summary} picks={picks} />
        
        <div className="mt-12">
          <DataTable picks={picks} />
        </div>
      </div>
    </main>
  );
}
