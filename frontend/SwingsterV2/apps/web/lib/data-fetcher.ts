import { createClient } from "@/lib/supabase/server";

import { ScanSummary, FinalPick } from "./generated-types";

// Adding timestamp to ScanSummary locally since it's added by Supabase default
export interface ScanSummaryWithTimestamp extends ScanSummary {
  timestamp: string;
}

export async function getScanSummary(): Promise<ScanSummaryWithTimestamp | null> {
  try {
    const supabase = await createClient();
    const { data, error } = await supabase
      .from("scan_summary")
      .select("*")
      .order("timestamp", { ascending: false })
      .limit(1)
      .single();
      
    if (error || !data) {
      console.error("Failed to read scan_summary from Supabase:", error?.message);
      return null;
    }
    return data as ScanSummaryWithTimestamp;
  } catch (error) {
    console.error("Failed to read scan_summary", error);
    return null;
  }
}

export async function getFinalPicks(): Promise<FinalPick[]> {
  try {
    const supabase = await createClient();
    // First get the latest scan_summary id
    const { data: summary, error: summaryError } = await supabase
      .from("scan_summary")
      .select("id")
      .order("timestamp", { ascending: false })
      .limit(1)
      .single();
      
    if (summaryError || !summary) {
      return [];
    }

    const { data, error } = await supabase
      .from("final_picks")
      .select("*")
      .eq("scan_summary_id", summary.id)
      .order("rank", { ascending: true });

    if (error) {
      console.error("Failed to read final_picks from Supabase:", error.message);
      return [];
    }
    
    return (data || []) as FinalPick[];
  } catch (error) {
    console.error("Failed to read final_picks", error);
    return [];
  }
}
