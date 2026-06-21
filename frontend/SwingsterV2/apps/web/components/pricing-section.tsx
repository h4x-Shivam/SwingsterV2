"use client";

import React, { useState } from "react";
import { motion } from "motion/react";
import { Coffee, Heart } from "lucide-react";

export function PricingSection() {
  const [amount, setAmount] = useState<string>("2");

  const presetAmounts = ["2", "5", "10", "20"];

  return (
    <section id="pricing" className="relative w-full py-24 md:py-32 bg-transparent overflow-hidden scroll-mt-24">
      {/* Background glow */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-emerald-500/5 rounded-full blur-[100px] pointer-events-none" />

      <div className="relative z-10 max-w-3xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-12 flex flex-col items-center">
          <motion.div 
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/5 border border-white/10 backdrop-blur-md mb-6"
          >
            <Coffee className="w-4 h-4 text-emerald-500" />
            <span className="text-xs font-bold tracking-[0.2em] text-white/80 uppercase">Support Us</span>
          </motion.div>
          
          <h2 className="text-4xl md:text-5xl font-bold text-white tracking-tight mb-4">
            Buy Me a Coffee
          </h2>
          
          <p className="text-lg text-white/50 max-w-xl mx-auto leading-relaxed">
            Swingster is free to use. If you find value in our pattern scans and AI verdicts, consider supporting the development!
          </p>
        </div>

        {/* Buy Me A Coffee Card */}
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="w-full max-w-md mx-auto"
        >
          <div className="relative w-full bg-[#121216]/90 backdrop-blur-[16px] rounded-3xl p-8 border border-emerald-500/30 shadow-[0_0_30px_rgba(16,185,129,0.1)] flex flex-col transition-colors hover:border-emerald-500/50">
            
            <div className="mb-8 text-center">
               <h3 className="text-xl font-medium text-white mb-2">Choose an amount</h3>
            </div>

            {/* Presets */}
            <div className="grid grid-cols-4 gap-3 mb-6">
              {presetAmounts.map((preset) => (
                <button
                  key={preset}
                  onClick={() => setAmount(preset)}
                  className={`py-3 rounded-xl border transition-all text-sm font-semibold ${
                    amount === preset 
                      ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400' 
                      : 'border-white/10 text-white/60 hover:border-white/20 hover:bg-white/5'
                  }`}
                >
                  ${preset}
                </button>
              ))}
            </div>

            {/* Custom Amount Input */}
            <div className="relative mb-8">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none">
                <span className="text-white/40 text-lg font-medium">$</span>
              </div>
              <input
                type="number"
                value={amount}
                onChange={(e) => setAmount(e.target.value)}
                placeholder="Custom Amount"
                className="w-full bg-white/5 border border-white/10 rounded-xl py-4 pl-8 pr-4 text-white text-lg focus:outline-none focus:border-emerald-500/50 focus:bg-white/10 transition-colors"
                min="1"
              />
            </div>

            <button className="w-full py-4 px-4 rounded-xl bg-emerald-500 text-black font-bold hover:bg-emerald-400 hover:shadow-[0_0_20px_rgba(16,185,129,0.4)] transition-all flex items-center justify-center gap-2 text-lg">
              <Heart className="w-5 h-5 fill-black" />
              Support Swingster
            </button>
            
            <p className="text-center text-xs text-white/40 mt-4">
              Payments are secure and encrypted.
            </p>
          </div>
        </motion.div>
      </div>
    </section>
  );
}

