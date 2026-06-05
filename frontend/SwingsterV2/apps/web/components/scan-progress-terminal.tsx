"use client";

import React, { useEffect, useState } from "react";
import { motion, AnimatePresence } from "motion/react";
import { BorderGlow } from "./ui/border-glow";

const terminalLogs = [
  "Initializing SwingsterV2 scan engine...",
  "[OK] Connected to ohlcv.db (Historical Data)",
  "Fetching live tick data...",
  "[OK] Live quotes synchronized.",
  "Scanning universe: 2,185 symbols...",
  "Applying Minervini Stage 2 filters...",
  "> 412 symbols passed trend requirements.",
  "Executing VCP pattern recognition algorithms...",
  "> Analyzing volatility contraction layers...",
  "> Calculating volume dry-up signatures...",
  "Filtering by Risk-Reward minimums...",
  "Sending 65 candidates to Groq Judge Agent...",
  "Awaiting qualitative verdict...",
  "[SUCCESS] 57 setups confirmed with HIGH/MEDIUM conviction."
];

export function ScanProgressTerminal({
  patternName,
  onComplete
}: {
  patternName: string;
  onComplete?: () => void;
}) {
  const [logs, setLogs] = useState<string[]>([]);
  const [progress, setProgress] = useState(0);
  const [isFinished, setIsFinished] = useState(false);

  useEffect(() => {
    let currentLog = 0;
    
    const interval = setInterval(() => {
      if (currentLog < terminalLogs.length) {
        setLogs(prev => [...prev, terminalLogs[currentLog]]);
        setProgress(Math.floor(((currentLog + 1) / terminalLogs.length) * 100));
        currentLog++;
      } else {
        clearInterval(interval);
        setIsFinished(true);
      }
    }, 400); // 400ms per log line

    return () => clearInterval(interval);
  }, []);

  return (
    <BorderGlow
      className="w-full h-full"
      innerClassName="w-full h-full flex flex-col p-6 font-mono text-sm overflow-hidden"
      backgroundColor="#060608"
      edgeSensitivity={30}
      glowColor="16 185 129" // emerald glow
      borderRadius={8}
      glowRadius={30}
      glowIntensity={0.5}
      animated={true}
    >
      {/* Header bar */}
      <div className="flex items-center justify-between mb-6 pb-4 border-b border-white/5 shrink-0">
        <div className="flex items-center gap-3">
          <div className="flex gap-1.5">
            <div className="w-3 h-3 rounded-full bg-red-500/80" />
            <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
            <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
          </div>
          <span className="text-emerald-500 font-semibold tracking-wider text-xs">
            SCAN_ENGINE // {patternName.toUpperCase()}
          </span>
        </div>
        <div className="text-xs text-white/30">sys.v2.4</div>
      </div>

      {/* Terminal Output */}
      <div className="flex-1 overflow-y-auto pr-2 space-y-2 relative no-scrollbar">
        <AnimatePresence initial={false}>
          {logs.map((log, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              className={`leading-relaxed ${
                log.includes("[OK]") || log.includes("[SUCCESS]")
                  ? "text-emerald-400 font-medium"
                  : log.startsWith(">")
                  ? "text-white/40 pl-4"
                  : "text-white/70"
              }`}
            >
              <span className="text-emerald-500/50 mr-2">›</span>
              {log}
            </motion.div>
          ))}
        </AnimatePresence>
        
        {!isFinished && (
          <motion.div
            animate={{ opacity: [1, 0, 1] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="inline-block w-2 h-4 bg-emerald-500 ml-1 translate-y-1"
          />
        )}
      </div>

      {/* Progress Bar & Actions */}
      <div className="mt-6 pt-4 border-t border-white/5 shrink-0">
        <div className="flex justify-between items-end mb-2">
          <span className="text-xs text-white/40 uppercase tracking-widest">
            {isFinished ? "Scan Complete" : "Processing"}
          </span>
          <span className="text-xs text-emerald-500 font-bold">{progress}%</span>
        </div>
        <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden mb-4">
          <motion.div
            className="h-full bg-gradient-to-r from-emerald-600 to-emerald-400"
            initial={{ width: "0%" }}
            animate={{ width: `${progress}%` }}
            transition={{ ease: "linear", duration: 0.4 }}
          />
        </div>
        
        <AnimatePresence>
          {isFinished && (
            <motion.button
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={onComplete}
              className="w-full py-3 rounded-md bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-sm tracking-wide hover:bg-emerald-500/20 transition-colors shadow-[0_0_20px_rgba(16,185,129,0.15)]"
            >
              VIEW RESULTS
            </motion.button>
          )}
        </AnimatePresence>
      </div>
    </BorderGlow>
  );
}
