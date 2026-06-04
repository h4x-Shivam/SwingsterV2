export interface PatternData {
  id: string;
  title: string;
  description: string;
  signal: string;
  /** SVG path data for the pattern illustration */
  svgPath: string;
  /** SVG viewBox for the pattern illustration */
  svgViewBox: string;
}

export const patterns: PatternData[] = [
  {
    id: "vcp",
    title: "VCP (Volatility Contraction Pattern)",
    description:
      "A series of progressively tighter price contractions after a base. Each pullback is shallower than the last — showing sellers are exhausted. A volume dry-up at the pivot signals the breakout entry.",
    signal: "Bullish Continuation",
    // VCP: descending wave pattern with tighter swings, then breakout arrow up
    svgPath:
      "M 20 130 Q 50 40, 80 90 Q 100 130, 120 100 Q 135 80, 150 95 Q 160 105, 170 92 Q 175 87, 180 90 L 200 50",
    svgViewBox: "0 0 220 160",
  },
  {
    id: "pole-flag",
    title: "Pole & Flag",
    description:
      "A strong vertical price surge (the pole) followed by a brief, tight consolidation (the flag). The flag forms at a slight downward angle. Breakout from the flag targets the length of the pole added to the breakout point.",
    signal: "Bullish Continuation",
    // Pole (sharp rise) + flag (slight descending channel) + breakout
    svgPath:
      "M 20 140 L 60 40 L 80 55 L 100 48 L 120 60 L 140 52 L 145 50 L 180 20",
    svgViewBox: "0 0 200 160",
  },
  {
    id: "cup-handle",
    title: "Cup & Handle",
    description:
      "Price forms a smooth U-shaped recovery (the cup) followed by a small downward drift (the handle). The handle is a final shakeout before a powerful breakout above the cup's rim — one of the highest probability setups in trading.",
    signal: "Bullish Continuation",
    // Cup (U-shape) + small handle dip + breakout up
    svgPath:
      "M 20 50 Q 30 55, 40 70 Q 60 130, 100 140 Q 140 130, 160 70 Q 165 55, 170 50 Q 175 60, 180 65 Q 185 55, 190 50 L 200 25",
    svgViewBox: "0 0 220 160",
  },
  {
    id: "breakout",
    title: "Breakout",
    description:
      "Price consolidates in a tight range building energy, then bursts above a key resistance level on high volume. The breakout candle is decisive — wide range, strong close, volume spike confirming real demand.",
    signal: "Bullish Continuation",
    // Flat consolidation range then sharp breakout candle upward
    svgPath:
      "M 20 90 L 40 85 L 55 95 L 70 88 L 85 92 L 100 86 L 115 93 L 130 87 L 145 90 L 155 85 L 160 80 L 170 40 L 185 25",
    svgViewBox: "0 0 210 130",
  },
];
