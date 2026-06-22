import { createClient } from "@/lib/supabase/server";

export interface ScanSummary {
  mode: string;
  total_scanned: number;
  pattern_match_count: number;
  rejected_by_rr: string[];
  timestamp: string;
}

export interface FinalPick {
  rank: number;
  symbol: string;
  pattern: string;
  scan_mode: string;
  composite_score: number;
  conviction: "HIGH" | "MEDIUM";
  buy_point: number;
  stop_loss: number;
  target: number;
  rr_ratio: number;
  current_price: number;
  distance_from_buy_pct: number;
  signal_strength: number;
  volume_score: number;
  rr_score: number;
  stage2_score: number;
  rs_score: number;
  judge_verdict: string;
  flags: string;
  pledge_pct?: number | null;
  sector?: string;
  target2?: number;
  pattern_age?: number;
  trend?: string;
}

export async function getScanSummary(): Promise<ScanSummary | null> {
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
    return data as ScanSummary;
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
