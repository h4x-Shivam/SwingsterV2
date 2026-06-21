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
  const { scrollY } = useScroll({
    container: ref,
  });
  const itemRefs = useRef<(HTMLDivElement | null)[]>([]);

  if (itemRefs.current.length !== content.length) {
    itemRefs.current = Array(content.length).fill(null);
  }

  useMotionValueEvent(scrollY, "change", (latest) => {
    if (!itemRefs.current.length) return;

    let newIndex = 0;
    for (let i = 0; i < content.length; i++) {
      const el = itemRefs.current[i];
      if (!el) continue;

      // The total vertical space this item occupies before the next item
      const patternHeight = el.offsetHeight + 128; // element height + mb-32 (8rem = 128px)
      
      // The exact pixel scroll offset where this item is perfectly aligned with the top of the right card (40px)
      const alignmentOffset = el.offsetTop - 40;
      
      // The user requested to switch "when the user scroll 60% of the pattern"
      const switchPoint = alignmentOffset + (patternHeight * 0.6);

      if (latest >= switchPoint) {
        newIndex = i + 1;
      }
    }

    setActiveCard(Math.max(0, Math.min(content.length - 1, newIndex)));
  });

  return (
    <div
      ref={ref}
      className="sticky-scroll-container relative flex h-[40rem] justify-center space-x-10 overflow-y-auto p-10 w-full"
      style={{
        maskImage: "linear-gradient(to bottom, transparent 0px, transparent 10px, black 40px, black 100%)",
        WebkitMaskImage: "linear-gradient(to bottom, transparent 0px, transparent 10px, black 40px, black 100%)"
      }}
    >
      <AnimatePresence mode="wait">
        {!isScanning && (
          <motion.div 
            key="text-content"
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -50, filter: "blur(4px)" }}
            transition={{ duration: 0.5, ease: "easeInOut" }}
            className="div relative flex items-start px-4 origin-left"
          >
            <div className="max-w-2xl min-w-[24rem] pt-10">
              {content.map((item, index) => (
                <div 
                  key={item.title + index} 
                  ref={(el) => {
                    itemRefs.current[index] = el;
                  }}
                  className="mb-32 min-h-[10rem]"
                >
                  <motion.h2
                    initial={{ opacity: 0 }}
                    animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                    transition={{ duration: 0.4 }}
                    className="text-2xl font-bold text-slate-100"
                  >
                    {item.title}
                  </motion.h2>
                  <motion.p
                    initial={{ opacity: 0 }}
                    animate={{ opacity: activeCard === index ? 1 : 0.3 }}
                    transition={{ duration: 0.4 }}
                    className="text-lg mt-6 max-w-sm text-slate-300 leading-relaxed"
                  >
                    {item.description}
                  </motion.p>
                </div>
              ))}
              <div className="h-[20rem]" />
            </div>
          </motion.div>
        )}

        <div
          className={[
            "sticky top-10 hidden h-[32rem] w-[28rem] overflow-hidden rounded-md lg:block shrink-0 z-10",
            contentClassName ?? "",
          ]
            .filter(Boolean)
            .join(" ")}
        >
          <AnimatePresence mode="popLayout" initial={false}>
            <motion.div
              key={displayCard}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              exit={{ opacity: 0, scale: 1.05 }}
              transition={{ duration: 0.4, ease: "easeInOut" }}
              className="w-full h-full"
            >
              {content[displayCard]?.content ?? null}
            </motion.div>
          </AnimatePresence>
        </div>

        {isScanning && (
          <motion.div
            key="progress-ui"
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
    </div>
  );
};
