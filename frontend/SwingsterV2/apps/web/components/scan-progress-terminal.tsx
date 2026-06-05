"use client";

import React, { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "motion/react";
import { BorderGlow } from "./ui/border-glow";

export function ScanProgressTerminal({
  patternName,
  onComplete
}: {
  patternName: string;
  onComplete?: () => void;
}) {
  const [logs, setLogs] = useState<string[]>(["Initializing SwingsterV2 scan engine..."]);
  const [progress, setProgress] = useState(0);
  const [isFinished, setIsFinished] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Auto-scroll to bottom
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [logs]);

  useEffect(() => {
    let isCancelled = false;

    const runLiveScan = async () => {
      try {
        const response = await fetch(`/api/scan?mode=${patternName}`);
        if (!response.body) return;

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        while (!isCancelled) {
          const { value, done } = await reader.read();
          if (done) {
            setIsFinished(true);
            break;
          }

          const chunk = decoder.decode(value, { stream: true });
          const lines = chunk.split("\n");

          for (const line of lines) {
            if (line.startsWith("data: ")) {
              let msg = line.substring(6);
              try {
                msg = JSON.parse(msg); // Decode the string
              } catch (e) {
                // Ignore parse errors, use raw msg
              }

              if (msg.trim()) {
                setLogs((prev) => {
                  const newLogs = [...prev, msg];
                  return newLogs.slice(-50); // Keep terminal history manageable
                });

                // Extract progress like "Progress: 150/2153"
                const progressMatch = msg.match(/Progress:\s*(\d+)\s*\/\s*(\d+)/);
                if (progressMatch) {
                  const current = parseInt(progressMatch[1], 10);
                  const total = parseInt(progressMatch[2], 10);
                  if (total > 0) {
                    setProgress(Math.floor((current / total) * 100));
                  }
                }

                if (msg.includes("[SYSTEM] Process exited")) {
                  setProgress(100);
                  setIsFinished(true);
                }
              }
            }
          }
        }
      } catch (err) {
        console.error(err);
        if (!isCancelled) {
          setLogs((prev) => [...prev, "[SYSTEM_ERROR] Connection failed"]);
          setIsFinished(true);
        }
      }
    };

    runLiveScan();

    return () => {
      isCancelled = true;
    };
  }, [patternName]);

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
      <div ref={scrollRef} className="flex-1 overflow-y-auto pr-2 space-y-2 relative no-scrollbar pb-4 scroll-smooth">
        <AnimatePresence initial={false}>
          {logs.map((log, i) => {
            const isSuccess = log?.includes("[OK]") || log?.includes("[SUCCESS]");
            const isError = log?.includes("[ERROR]") || log?.includes("[WARN]");
            const isSystem = log?.includes("[SYSTEM]");
            const isSubItem = log?.startsWith(">");
            
            return (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                className={`leading-relaxed text-xs md:text-sm ${
                  isSuccess
                    ? "text-emerald-400 font-medium"
                    : isError
                    ? "text-red-400"
                    : isSystem
                    ? "text-emerald-500/50"
                    : isSubItem
                    ? "text-white/40 pl-4"
                    : "text-white/70"
                }`}
              >
                <span className="text-emerald-500/50 mr-2">›</span>
                {log}
              </motion.div>
            );
          })}
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
