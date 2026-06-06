"use client";
import React, { useRef } from "react";
import { useMotionValueEvent, useScroll, motion, AnimatePresence } from "motion/react";
import { BorderGlow } from "./border-glow";

export const StickyScroll = ({
  content,
  contentClassName,
  isScanning = false,
  progressUI = null,
  activeCardOverride,
}: {
  content: {
    title: string;
    description: string;
    content?: React.ReactNode;
  }[];
  contentClassName?: string;
  isScanning?: boolean;
  progressUI?: React.ReactNode;
  activeCardOverride?: number;
}) => {
  const [activeCard, setActiveCard] = React.useState(0);
  const displayCard = activeCardOverride !== undefined && isScanning ? activeCardOverride : activeCard;
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({
    container: ref,
    offset: ["start start", "end start"],
  });
  const cardLength = content.length;

  useMotionValueEvent(scrollYProgress, "change", (latest) => {
    const cardsBreakpoints = content.map((_, index) => index / cardLength);
    const closestBreakpointIndex = cardsBreakpoints.reduce(
      (acc, breakpoint, index) => {
        const distance = Math.abs(latest - breakpoint);
        if (distance < Math.abs(latest - cardsBreakpoints[acc]!)) {
          return index;
        }
        return acc;
      },
      0,
    );
    setActiveCard(closestBreakpointIndex);
  });

  return (
    <BorderGlow
      className="w-full h-[40rem]"
      innerClassName="overflow-hidden h-full w-full"
      edgeSensitivity={30}
      glowColor="142 70 50" // Sleek green/teal accent glow
      backgroundColor="#0a0a0a"
      borderRadius={8}
      glowRadius={40}
      glowIntensity={1.0}
      coneSpread={25}
      animated={true}
      colors={['#10b981', '#059669', '#ef4444']} // Green/red themed gradient border
      fillOpacity={0.05}
    >
      <motion.div
        ref={ref}
        layout
        className="sticky-scroll-container relative flex h-full justify-center space-x-10 overflow-y-auto p-10 w-full"
      >
        <AnimatePresence mode="popLayout">
          {!isScanning && (
            <motion.div 
              key="text-content"
              layout 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -50, filter: "blur(4px)" }}
              transition={{ duration: 0.5, ease: "easeInOut" }}
              className="div relative flex items-start px-4 origin-left"
            >
              <div className="max-w-2xl min-w-[24rem]">
                {content.map((item, index) => (
                  <div key={item.title + index} className="my-20">
                    <motion.h2
                      initial={{ opacity: 0 }}
                      animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                      className="text-2xl font-bold text-slate-100"
                    >
                      {item.title}
                    </motion.h2>
                    <motion.p
                      initial={{ opacity: 0 }}
                      animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                      className="text-kg mt-10 max-w-sm text-slate-300"
                    >
                      {item.description}
                    </motion.p>
                  </div>
                ))}
                <div className="h-40" />
              </div>
            </motion.div>
          )}

          <motion.div
            layout
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className={[
              "sticky top-10 hidden h-[32rem] w-[28rem] overflow-hidden rounded-md lg:block shrink-0 z-10",
              contentClassName ?? "",
            ]
              .filter(Boolean)
              .join(" ")}
          >
            {content[displayCard]?.content ?? null}
          </motion.div>

          {isScanning && (
            <motion.div
              key="progress-ui"
              layout
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50, filter: "blur(4px)" }}
              transition={{ duration: 0.5, ease: "easeInOut", delay: 0.1 }}
              className="relative flex items-start px-4 overflow-hidden w-full max-w-[28rem] min-w-[28rem]"
            >
              <div className="sticky top-10 w-full h-[32rem]">
                {progressUI}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </BorderGlow>
  );
};
