"use client";

import React from "react";
import { motion } from "motion/react";
import { BorderGlow } from "@/components/ui/border-glow";
import PixelCard from "./PixelCard";

export function AboutSection() {
  return (
    <section id="about" className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden scroll-mt-24">
      <div className="relative z-10 max-w-5xl mx-auto px-6">
        
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-10%" }}
          transition={{ duration: 0.6, ease: "easeOut" }}
        >
          <BorderGlow
            className="w-full"
            innerClassName="p-6 md:p-10 bg-[#0c0c10]/80 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-colors w-full rounded-2xl flex !flex-col md:!flex-row gap-8 md:gap-12"
            edgeSensitivity={30}
            glowColor="16 185 129"
            backgroundColor="#0c0c10"
            borderRadius={16}
            glowRadius={40}
            glowIntensity={0.5}
            coneSpread={20}
            animated={true}
            fillOpacity={0.03}
          >
            {/* Left: Pixel Card Image */}
            <div className="w-full md:w-[280px] shrink-0 h-[350px] md:h-[420px] rounded-xl overflow-hidden relative border border-white/5 group">
              <PixelCard 
                colors="#10b981,#059669,#047857" 
                gap={6} 
                speed={40} 
                className="w-full h-full"
              >
                <div className="absolute inset-0 z-[-1]">
                  {/* eslint-disable-next-line @next/next/no-img-element */}
                  <img 
                    src="/shivam-profile.jpg" 
                    alt="Shivam" 
                    className="w-full h-full object-cover grayscale brightness-75 contrast-125 group-hover:grayscale-0 group-hover:brightness-100 transition-all duration-700 ease-out" 
                  />
                </div>
              </PixelCard>
            </div>

            {/* Right: Content */}
            <div className="flex-1 flex flex-col md:flex-row gap-8">
              {/* Bio Column */}
              <div className="flex-1 flex flex-col justify-center">
                <div className="text-[10px] md:text-xs font-bold tracking-[0.2em] text-emerald-500 uppercase mb-2">
                  Founder
                </div>
                <h3 className="text-3xl md:text-5xl font-bold text-white mb-2">
                  Shivam
                </h3>
                <div className="text-sm font-medium text-emerald-500 mb-6">
                  Creator & Developer of Swingster
                </div>
                
                <p className="text-[#a1a1aa] leading-relaxed text-sm md:text-base mb-8">
                  I'm a BTech Computer Science student and a quantitative finance enthusiast. Swingster is the result of thousands of hours spent researching institutional patterns, market behavior, and building technology that works in the real world.
                </p>

                <div className="flex flex-col gap-3 text-sm text-white/80">
                  <div className="flex items-center gap-3">
                    <svg className="w-4 h-4 text-white/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 10v6M2 10l10-5 10 5-10 5z"/><path d="M6 12v5c3 3 9 3 12 0v-5"/></svg>
                    <span>BTech Computer Science</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <svg className="w-4 h-4 text-white/50" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="m19 9-5 5-4-4-3 3"/></svg>
                    <span>Quantitative Finance Enthusiast</span>
                  </div>
                </div>
              </div>

              {/* Links Column */}
              <div className="w-full md:w-[140px] flex flex-col md:border-l border-white/5 md:pl-8 justify-center gap-6 mt-6 md:mt-0 pt-6 md:pt-0 border-t md:border-t-0">
                <div className="text-[10px] font-bold tracking-[0.2em] text-emerald-500 uppercase mb-2">
                  Connect
                </div>
                
                <div className="flex flex-col gap-4">
                  <a href="https://github.com/h4x-Shivam" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-sm text-white/60 hover:text-white transition-colors">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"/><path d="M9 18c-4.51 2-5-2-7-2"/></svg>
                    <span>GitHub</span>
                  </a>
                  <a href="https://www.linkedin.com/in/shivam-jaiswal-2a5b3b3a5/" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-sm text-white/60 hover:text-[#0a66c2] transition-colors">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"/><rect x="2" y="9" width="4" height="12"/><circle cx="4" cy="4" r="2"/></svg>
                    <span>LinkedIn</span>
                  </a>
                  <a href="https://instagram.com/sh1vxxm" target="_blank" rel="noopener noreferrer" className="flex items-center gap-3 text-sm text-white/60 hover:text-[#E1306C] transition-colors">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                    <span>Instagram</span>
                  </a>
                  <a href="mailto:svxm.h4x@gmail.com" className="flex items-center gap-3 text-sm text-white/60 hover:text-emerald-400 transition-colors">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/></svg>
                    <span>Email</span>
                  </a>
                </div>
              </div>
            </div>
          </BorderGlow>
        </motion.div>
      </div>
    </section>
  );
}
