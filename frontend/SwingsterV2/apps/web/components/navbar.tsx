"use client";

import React, { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { motion } from "motion/react";

export function Navbar({ isAuthenticated = false }: { isAuthenticated?: boolean }) {
  const navLinks = [
    // Features section does not exist yet, commented out for now.
    // { name: "Features", href: "#features" },
    { name: "Home", href: "/" },
    { name: "How It Works", href: "/#how-it-works" },
    ...(isAuthenticated ? [{ name: "My Watchlist", href: "/watchlist" }] : [{ name: "Watchlist", href: "/#watchlist" }]),
    { name: "About", href: "/#about" },
  ];
  const [isScrolled, setIsScrolled] = useState(false);
  const [isVisible, setIsVisible] = useState(true);
  const lastScrollY = useRef(0);
  const [activeSection, setActiveSection] = useState("");
  const [indicatorStyle, setIndicatorStyle] = useState({ left: 0, width: 0, opacity: 0 });
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const navRefs = useRef<(HTMLAnchorElement | null)[]>([]);

  // Handle scroll effects for the navbar background and visibility
  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      
      setIsScrolled(currentScrollY > 80);
      
      // Hide if scrolling down and past the top area
      if (currentScrollY > lastScrollY.current && currentScrollY > 100) {
        setIsVisible(false);
        setIsMobileMenuOpen(false); // Close mobile menu when hiding
      } else {
        setIsVisible(true);
      }
      
      lastScrollY.current = currentScrollY;
    };
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  // Intersection Observer for tracking active sections
  useEffect(() => {
    const observerOptions = {
      root: null,
      rootMargin: "-20% 0px -80% 0px", // Adjust these values to trigger earlier/later
      threshold: 0,
    };

    const observerCallback: IntersectionObserverCallback = (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          setActiveSection(`#${entry.target.id}`);
        }
      });
    };

    const observer = new IntersectionObserver(observerCallback, observerOptions);

    navLinks.forEach((link) => {
      const id = link.href.substring(1);
      const element = document.getElementById(id);
      if (element) {
        observer.observe(element);
      }
    });

    return () => observer.disconnect();
  }, []);

  // Update liquid indicator position when active section changes
  useEffect(() => {
    const activeIndex = navLinks.findIndex((link) => link.href === activeSection);
    
    if (activeIndex !== -1 && navRefs.current[activeIndex]) {
      const activeElement = navRefs.current[activeIndex];
      if (activeElement) {
        setIndicatorStyle({
          left: activeElement.offsetLeft,
          width: activeElement.offsetWidth,
          opacity: 1,
        });
      }
    } else if (window.scrollY < 100) {
      // If at the very top, hide indicator or point to the first item
      setIndicatorStyle((prev) => ({ ...prev, opacity: 0 }));
      setActiveSection("");
    }
  }, [activeSection]);

  const handleLinkClick = (e: React.MouseEvent<HTMLAnchorElement>, href: string) => {
    setIsMobileMenuOpen(false);
    
    if (href === "#top") {
      e.preventDefault();
      window.scrollTo({ top: 0, behavior: "smooth" });
      return;
    }

    // For full-path links (not hash-only), let the browser navigate normally
    // unless it's a same-page hash link like "/#section"
    if (href.startsWith("/") && !href.includes("#")) {
      // Full route navigation — don't prevent default
      return;
    }

    // Handle hash links (e.g., "#how-it-works" or "/#watchlist")
    const hashIndex = href.indexOf("#");
    if (hashIndex !== -1) {
      const id = href.substring(hashIndex + 1);
      const element = document.getElementById(id);
      if (element) {
        e.preventDefault();
        element.scrollIntoView({ behavior: "smooth", block: "start" });
        return;
      }
    }
  };

  return (
    <header 
      className={`fixed top-4 left-0 right-0 z-50 flex justify-center px-4 md:px-0 pointer-events-none transition-all duration-300 ease-in-out ${
        isVisible ? "translate-y-0 opacity-100" : "-translate-y-[150%] opacity-0"
      }`}
    >
      <div 
        className={`pointer-events-auto w-full max-w-[1100px] transition-all duration-300 ease-out border border-white/5 shadow-[0_0_24px_rgba(26,147,111,0.15)]
          ${isScrolled ? "bg-[#0f0f0f]/95" : "bg-[#0f0f0f]/80"}
          ${isMobileMenuOpen ? "rounded-2xl" : "rounded-full"}
        `}
      >
        <div className="flex items-center justify-between px-6 py-3">
          {/* Logo */}
          <a 
            href="#top" 
            onClick={(e) => handleLinkClick(e, "#top")}
            className="flex items-center gap-2 group"
          >
            <div className="w-8 h-8 rounded bg-emerald-500/20 border border-emerald-500/50 flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" className="text-emerald-400"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            </div>
            <span className="font-bold text-lg tracking-tight text-white group-hover:text-emerald-400 transition-colors">
              Swingster
            </span>
          </a>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex relative items-center justify-center gap-1">
            {/* Liquid Background Indicator */}
            <div 
              className="absolute h-8 bg-emerald-500/20 rounded-full transition-all duration-300 ease-out pointer-events-none"
              style={{
                left: indicatorStyle.left,
                width: indicatorStyle.width,
                opacity: indicatorStyle.opacity,
                transform: "translateY(0)" // Ensure hardware acceleration
              }}
            />
            
            {navLinks.map((link, i) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                ref={(el) => {
                  navRefs.current[i] = el;
                }}
                className={`relative px-4 py-1.5 text-sm font-medium rounded-full transition-colors z-10
                  ${activeSection === link.href ? "text-emerald-400" : "text-white/70 hover:text-white"}
                `}
              >
                {link.name}
              </a>
            ))}
          </nav>

          {/* Desktop CTA */}
          <div className="hidden md:block">
            {isAuthenticated ? (
              <form action="/auth/signout" method="post">
                <button 
                  type="submit"
                  className="px-5 py-2 text-sm font-bold bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-full transition-colors inline-block"
                >
                  Sign Out
                </button>
              </form>
            ) : (
              <Link 
                href="/login" 
                className="px-5 py-2 text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-black rounded-full transition-colors inline-block shadow-[0_0_15px_rgba(16,185,129,0.3)]"
              >
                Log In
              </Link>
            )}
          </div>

          {/* Mobile Menu Toggle */}
          <button 
            className="md:hidden text-white/70 hover:text-white p-1"
            onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          >
            {isMobileMenuOpen ? (
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
            )}
          </button>
        </div>

        {/* Mobile Dropdown */}
        {isMobileMenuOpen && (
          <div className="md:hidden border-t border-white/10 px-6 py-4 flex flex-col gap-4">
            {navLinks.map((link) => (
              <a
                key={link.name}
                href={link.href}
                onClick={(e) => handleLinkClick(e, link.href)}
                className={`text-base font-medium py-2 transition-colors
                  ${activeSection === link.href ? "text-emerald-400" : "text-white/70"}
                `}
              >
                {link.name}
              </a>
            ))}
            <div className="pt-2">
              {isAuthenticated ? (
                <form action="/auth/signout" method="post" className="w-full">
                  <button 
                    type="submit"
                    className="block w-full text-center px-5 py-3 text-sm font-bold bg-white/5 hover:bg-white/10 text-white border border-white/10 rounded-full transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    Sign Out
                  </button>
                </form>
              ) : (
                <Link 
                  href="/login" 
                  className="block w-full text-center px-5 py-3 text-sm font-bold bg-emerald-500 hover:bg-emerald-400 text-black rounded-full transition-colors shadow-[0_0_15px_rgba(16,185,129,0.3)]"
                  onClick={() => setIsMobileMenuOpen(false)}
                >
                  Log In
                </Link>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
}
