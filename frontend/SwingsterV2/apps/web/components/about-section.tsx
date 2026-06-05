"use client";

import React from "react";
import { motion } from "motion/react";
import { BorderGlow } from "@/components/ui/border-glow";

export function AboutSection() {
  return (
    <section className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden">
      <div className="relative z-10 max-w-6xl mx-auto px-6">
        
        {/* Section Header */}
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight">
            About <span className="text-[#10b981]">Swingster</span>
          </h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8 md:gap-12 items-stretch">
          
          {/* Card 1: The Philosophy */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-10%" }}
            transition={{ duration: 0.6, ease: "easeOut" }}
            className="h-full"
          >
            <BorderGlow
              className="w-full h-full"
              innerClassName="p-8 md:p-10 bg-[#0c0c10]/80 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-colors w-full h-full text-left rounded-2xl flex flex-col justify-center"
              edgeSensitivity={30}
              glowColor="16 185 129" // Emerald
              backgroundColor="#0c0c10"
              borderRadius={16}
              glowRadius={40}
              glowIntensity={0.5}
              coneSpread={20}
              animated={true}
              fillOpacity={0.03}
            >
              <div className="w-12 h-12 rounded-xl bg-emerald-500/10 border border-emerald-500/30 flex items-center justify-center mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10b981" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 2 22 12 17 22 22 12 2"></polygon></svg>
              </div>
              <h3 className="text-2xl font-bold text-white mb-4">
                The Algorithmic Edge for Retail
              </h3>
              <p className="text-white/60 leading-relaxed text-base md:text-lg">
                The market isn't driven by luck; it's driven by institutional accumulation and supply/demand imbalances. Swingster was built to bridge the gap between retail traders and Wall Street algorithms.
                <br/><br/>
                By combining strict Stage 2 trend criteria with real-time quantitative geometry, Swingster strips away the noise. It doesn't predict the future—it simply identifies the exact moments when volatility contracts and explosive moves are mathematically most likely to happen.
              </p>
            </BorderGlow>
          </motion.div>

          {/* Card 2: The Creator */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, margin: "-10%" }}
            transition={{ duration: 0.6, delay: 0.2, ease: "easeOut" }}
            className="h-full"
          >
            <BorderGlow
              className="w-full h-full"
              innerClassName="p-8 md:p-10 bg-[#0c0c10]/80 backdrop-blur-xl border border-white/5 hover:border-white/10 transition-colors w-full h-full text-left rounded-2xl flex flex-col justify-between"
              edgeSensitivity={30}
              glowColor="168 85 247" // Purple
              backgroundColor="#0c0c10"
              borderRadius={16}
              glowRadius={40}
              glowIntensity={0.5}
              coneSpread={20}
              animated={true}
              fillOpacity={0.03}
            >
              <div>
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 rounded-full bg-gradient-to-tr from-purple-500 to-indigo-500 p-[2px]">
                    <div className="w-full h-full rounded-full bg-[#0c0c10] flex items-center justify-center overflow-hidden">
                      {/* Placeholder for User Profile Picture */}
                      <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" className="text-white/40"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-white">Shivam</h3>
                    <span className="text-sm font-medium text-purple-400 uppercase tracking-widest">Creator / Developer</span>
                  </div>
                </div>
                
                <p className="text-white/60 leading-relaxed text-base md:text-lg mb-8">
                  I’m a BTech Computer Science undergrad by day, and a quantitative finance enthusiast by night. I built Swingster because I was tired of manually scanning thousands of NSE charts looking for perfect setups.
                  <br/><br/>
                  I wanted to write code that could see what the human eye often misses: the subtle dry-ups in volume and the exact pivot points of a VCP. Swingster is the intersection of my two greatest passions—building scalable software and decoding market psychology.
                </p>
              </div>

              {/* Social Links Grid */}
              <div className="flex items-center gap-4 pt-6 border-t border-white/5">
                {/* GitHub */}
                <a href="#" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M15 22v-4a4.8 4.8 0 0 0-1-3.5c3 0 6-2 6-5.5.08-1.25-.27-2.48-1-3.5.28-1.15.28-2.35 0-3.5 0 0-1 0-3 1.5-2.64-.5-5.36-.5-8 0C6 2 5 2 5 2c-.3 1.15-.3 2.35 0 3.5A5.403 5.403 0 0 0 4 9c0 3.5 3 5.5 6 5.5-.39.49-.68 1.05-.85 1.65-.17.6-.22 1.23-.15 1.85v4"></path><path d="M9 18c-4.51 2-5-2-7-2"></path></svg>
                </a>
                {/* LinkedIn */}
                <a href="#" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-[#0a66c2] hover:bg-white/10 hover:border-[#0a66c2]/50 transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M16 8a6 6 0 0 1 6 6v7h-4v-7a2 2 0 0 0-2-2 2 2 0 0 0-2 2v7h-4v-7a6 6 0 0 1 6-6z"></path><rect x="2" y="9" width="4" height="12"></rect><circle cx="4" cy="4" r="2"></circle></svg>
                </a>
                {/* Twitter / X */}
                <a href="#" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-white hover:bg-white/10 hover:border-white/20 transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 4s-.7 2.1-2 3.4c1.6 10-9.4 17.3-18 11.6 2.2.1 4.4-.6 6-2C3 15.5.5 9.6 3 5c2.2 2.6 5.6 4.1 9 4-.9-4.2 4-6.6 7-3.8 1.1 0 3-1.2 3-1.2z"></path></svg>
                </a>
                {/* Instagram */}
                <a href="#" target="_blank" rel="noreferrer" className="w-10 h-10 rounded-full bg-white/5 border border-white/10 flex items-center justify-center text-white/60 hover:text-[#e1306c] hover:bg-white/10 hover:border-[#e1306c]/50 transition-all">
                  <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="2" y="2" width="20" height="20" rx="5" ry="5"></rect><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"></path><line x1="17.5" y1="6.5" x2="17.51" y2="6.5"></line></svg>
                </a>
              </div>
            </BorderGlow>
          </motion.div>
        </div>

        {/* Footer text */}
        <div className="mt-24 pt-8 border-t border-white/10 text-center flex flex-col items-center justify-center">
          <div className="flex items-center gap-2 mb-4">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-500"><polygon points="12 2 2 22 12 17 22 22 12 2"></polygon></svg>
            <span className="text-xl font-bold text-white tracking-widest uppercase">Swingster</span>
          </div>
          <p className="text-sm text-white/40">
            © {new Date().getFullYear()} Swingster. Developed with precision by Shivam.
          </p>
        </div>
      </div>
    </section>
  );
}
