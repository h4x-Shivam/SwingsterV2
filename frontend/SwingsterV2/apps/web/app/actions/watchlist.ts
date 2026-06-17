"use server";

import { createClient } from "@/lib/supabase/server";
import { revalidatePath } from "next/cache";

export async function toggleWatchlist(symbol: string) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) {
    throw new Error("User not authenticated");
  }

  // Check if symbol exists
  const { data: existing } = await supabase
    .from("watchlists")
    .select("id")
    .eq("user_id", user.id)
    .eq("symbol", symbol)
    .single();

  if (existing) {
    // Remove it
    const { error } = await supabase
      .from("watchlists")
      .delete()
      .eq("id", existing.id);
    
    if (error) {
      console.error("Error removing from watchlist:", error);
      throw new Error("Failed to remove from watchlist");
    }
  } else {
    // Add it
    const { error } = await supabase
      .from("watchlists")
      .insert({
        user_id: user.id,
        symbol: symbol,
      });
      
    if (error) {
      console.error("Error adding to watchlist:", error);
      throw new Error("Failed to add to watchlist");
    }
  }

  revalidatePath("/dashboard");
  revalidatePath("/watchlist");
  return true;
}

export async function getWatchlistSymbols(): Promise<Set<string>> {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();

  if (!user) return new Set();

  const { data, error } = await supabase
    .from("watchlists")
    .select("symbol")
    .eq("user_id", user.id);

  if (error) {
    console.error("Error fetching watchlist:", error);
    return new Set();
  }

  return new Set((data || []).map((row) => row.symbol));
}
