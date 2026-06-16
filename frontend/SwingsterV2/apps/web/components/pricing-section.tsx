"use client";

import React from "react";
import { motion } from "motion/react";
import { Check } from "lucide-react";

// Quarterly (₹799/3mo) currently costs more per month than Monthly (₹299/mo). 
// Confirm this is intentional before launch — typically longer billing cycles are discounted.
const MONTHLY_PRICE = 299;
const QUARTERLY_PRICE = 799;

const sharedFeatures = [
  "All Pattern Scans Unlocked — VCP, Cup & Handle, Flag & Pole, Breakout",
  "Fundamental Data — Market cap, P/E, ROE, Delivery %, Promoter/FII, Pledge %",
  "Live Chart Preview — Embedded real-time charts per stock",
  "AI Technical Analysis — Full AI Judge verdict with conviction scoring"
];

export function PricingSection() {
  return (
    <section id="pricing" className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden scroll-mt-24">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-5xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-16 flex flex-col items-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6"
          >
            <div className="w-2 h-2 rounded-full bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.8)] animate-pulse" />
            <span className="text-xs font-bold tracking-[0.2em] text-white/80 uppercase">Pricing</span>
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
            Simple Pricing, No Hidden Catches
          </h2>
          
          <p className="text-lg text-white/50 max-w-xl mx-auto leading-relaxed">
            Get full access to every scan, pattern, and AI verdict. Cancel anytime.
          </p>
        </div>

        {/* Pricing Cards */}
        <div className="flex flex-col md:flex-row gap-6 max-w-4xl mx-auto justify-center items-center md:items-stretch">
          
          {/* Monthly Plan */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, ease: "easeOut" }}
            className="w-full md:w-1/2 max-w-md flex flex-col"
          >
            <div className="relative w-full h-full bg-[#121216]/60 backdrop-blur-[16px] rounded-2xl p-8 border border-white/5 flex flex-col transition-colors hover:border-white/10">
              <div className="mb-8">
                <h3 className="text-xl font-medium text-white/80 mb-2">Monthly</h3>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-white/60">₹</span>
                  <span className="text-5xl font-bold text-white">{MONTHLY_PRICE}</span>
                  <span className="text-white/40">/mo</span>
                </div>
                <p className="text-sm text-white/40">Billed monthly · Cancel anytime</p>
              </div>

              <div className="flex-1">
                <ul className="flex flex-col gap-4">
                  {sharedFeatures.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-white/70">
                      <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button className="w-full mt-8 py-3 px-4 rounded-full border border-white/10 text-white font-medium hover:bg-white/5 transition-colors">
                Get Started
              </button>
            </div>
          </motion.div>

          {/* Quarterly Plan (Highlighted) */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 0.1, ease: "easeOut" }}
            className="w-full md:w-1/2 max-w-md flex flex-col md:-translate-y-4"
          >
            <div className="relative w-full h-full bg-[#121216]/90 backdrop-blur-[16px] rounded-2xl p-8 border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.15)] flex flex-col transform md:scale-105 transition-all">
              
              {/* Highlight Badge */}
              <div className="absolute top-0 right-8 -translate-y-1/2">
                <span className="bg-emerald-500 text-black text-xs font-bold px-3 py-1 rounded-full shadow-[0_0_10px_rgba(16,185,129,0.5)]">
                  ⭐ BEST VALUE
                </span>
              </div>

              <div className="mb-8">
                <h3 className="text-xl font-medium text-emerald-400 mb-2">Quarterly</h3>
                <div className="flex items-baseline gap-2 mb-2">
                  <span className="text-3xl font-bold text-emerald-500/70">₹</span>
                  <span className="text-5xl font-bold text-white">{QUARTERLY_PRICE}</span>
                  <span className="text-white/40">/3mo</span>
                </div>
                <p className="text-sm text-white/40">Billed every 3 months</p>
              </div>

              <div className="flex-1">
                <ul className="flex flex-col gap-4">
                  {sharedFeatures.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3 text-sm text-white/70">
                      <Check className="w-5 h-5 text-emerald-500 shrink-0" />
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <button className="w-full mt-8 py-3 px-4 rounded-full bg-emerald-500 text-black font-bold hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.4)] transition-all">
                Get Started
              </button>
            </div>
          </motion.div>

        </div>

        <div className="mt-12 text-center">
          <p className="text-sm text-white/40">
            All plans include the same features. Choose what billing cycle works for you.
          </p>
        </div>
      </div>
    </section>
  );
}
