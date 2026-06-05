import fs from "fs";
import path from "path";

// Define the root of the data folder.
// Assuming this Next.js app is at: d:\SwingsterV2\frontend\SwingsterV2\apps\web
// The data folder is at: d:\SwingsterV2\data
const DATA_DIR = path.resolve(process.cwd(), "../../../../data");

export interface ScanSummary {
  mode: string;
  total_scanned: number;
  vcp_found_count: number;
  rejected_by_rr: string[];
  timestamp: string;
}

export interface FinalPick {
  rank: number;
  symbol: string;
  sector: string;
  pattern: string;
  composite_score: number;
  conviction: "HIGH" | "MEDIUM";
  buy_point: number;
  stop_loss: number;
  target: number;
  target2: number;
  rr_ratio: number;
  current_price: number;
  distance_from_buy_pct: number;
  pattern_age: number;
  trend: string;
  judge_verdict: string;
  flags: string;
  signal_strength: number;
  volume_score: number;
  rr_score: number;
  stage2_score: number;
  rs_score: number;
  fundamentals: {
    market_cap: string;
    pe_ratio: string;
    roe: string;
    debt_to_equity: string;
  };
}

export async function getScanSummary(): Promise<ScanSummary | null> {
  try {
    const filePath = path.join(DATA_DIR, "scan_summary.json");
    if (!fs.existsSync(filePath)) return null;
    const fileContents = fs.readFileSync(filePath, "utf8");
    return JSON.parse(fileContents);
  } catch (error) {
    console.error("Failed to read scan_summary.json", error);
    return null;
  }
}

export async function getFinalPicks(): Promise<FinalPick[]> {
  try {
    const filePath = path.join(DATA_DIR, "final_picks.json");
    if (!fs.existsSync(filePath)) return [];
    const fileContents = fs.readFileSync(filePath, "utf8");
    const data = JSON.parse(fileContents);
    return data.results || [];
  } catch (error) {
    console.error("Failed to read final_picks.json", error);
    return [];
  }
}
