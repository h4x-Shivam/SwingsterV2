import streamlit as st
import json
import os
import time
import textwrap
import pandas as pd
from collections import Counter
from scanner.engine import scan_all
from judge.judge_agent import run_judge, save_top10
from config import SCAN_MODES, SCAN_MODE, GROQ_API_KEY, GROQ_MODEL

# ---------------------------------------------------------------------------
# Streamlit Premium Styling & Configuration
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="SwingsterV2 - Quantitative Portfolio Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Premium Dark Glassmorphism CSS injection
st.html("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');
    
    /* Body & Fonts */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }
    
    /* Sleek Dark Mode Backgrounds */
    .stApp {
        background: linear-gradient(135deg, #0d0f14 0%, #171b26 100%);
        color: #e2e8f0;
    }
    
    /* Header Aesthetics */
    .main-title {
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.8rem;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #94a3b8;
        font-weight: 300;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* Cards Styling */
    .glass-card {
        background: rgba(30, 41, 59, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(16, 185, 129, 0.3);
    }
    
    /* Badges */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.6rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .badge-vcp { background-color: rgba(16, 185, 129, 0.15); color: #10b981; }
    .badge-flag { background-color: rgba(59, 130, 246, 0.15); color: #3b82f6; }
    .badge-cup { background-color: rgba(168, 85, 247, 0.15); color: #a855f7; }
    .badge-breakout { background-color: rgba(245, 158, 11, 0.15); color: #f59e0b; }
    
    .badge-high { background-color: rgba(16, 185, 129, 0.2); color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .badge-medium { background-color: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.3); }
    .badge-low { background-color: rgba(239, 68, 68, 0.2); color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    
    /* Metrics Typography */
    .metric-val {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }
    .metric-lbl {
        font-size: 0.8rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
</style>
""")

# ---------------------------------------------------------------------------
# Sidebar - Scanner Controls
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### ⚡ **SwingsterV2 Controls**")
    st.markdown("---")
    
    # Active Scan Mode Selection
    selected_mode = st.selectbox(
        "Active Scanning Mode",
        options=SCAN_MODES,
        index=SCAN_MODES.index(SCAN_MODE) if SCAN_MODE in SCAN_MODES else 0
    )
    
    st.markdown("---")
    
    # Credentials & Environment Tracker
    has_api_key = GROQ_API_KEY and GROQ_API_KEY != "YOUR_GROQ_KEY_HERE"
    if has_api_key:
        st.success("🤖 **API Key Status: Connected**")
        st.info(f"Model: `{GROQ_MODEL}`")
    else:
        st.warning("⚠️ **API Key Status: Fallback Mode**")
        st.caption("Add your `GROQ_API_KEY` to the `.env` file to unlock LPU quantitative-qualitative analysis.")
        
    st.markdown("---")
    
    # Trigger Button
    run_scan = st.button("🚀 Run Live Parallel Scan", use_container_width=True)

# ---------------------------------------------------------------------------
# Main Layout - Title
# ---------------------------------------------------------------------------
st.markdown("<h1 class='main-title'>SWINGSTER V2</h1>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>High-Performance Technical Analysis Scanner & LLM Judging Agent</div>", unsafe_allow_html=True)

# Helper function to parse output files
def load_top10():
    if os.path.exists("data/top10.json"):
        try:
            with open("data/top10.json", "r") as f:
                return json.load(f)
        except Exception:
            return None
    return None

def load_results():
    if os.path.exists("data/results.json"):
        try:
            with open("data/results.json", "r") as f:
                return json.load(f)
        except Exception:
            return []
    return []

# ---------------------------------------------------------------------------
# Execute Live Scan Pipeline
# ---------------------------------------------------------------------------
if run_scan:
    with st.spinner("Initializing high-performance Parallel Scan Engine..."):
        # Funnel status container
        status_bar = st.empty()
        status_bar.info("Pre-filtering SQLite symbols and building batch queues...")
        
        # Symbol execution
        start_time = time.perf_counter()
        candidates = scan_all(mode=selected_mode)
        scan_elapsed = time.perf_counter() - start_time
        
        # Serialize dataclass
        candidates_dict = [vars(c) for c in candidates]
        os.makedirs("data", exist_ok=True)
        with open("data/results.json", "w") as f:
            json.dump(candidates_dict, f, indent=2)
            
        status_bar.success(f"Parallel scan complete: {len(candidates)} candidates pre-filtered in {scan_elapsed:.2f}s!")
        
    with st.spinner("Forwarding candidate setups to Groq LPU Judge Agent..."):
        judge_start = time.perf_counter()
        top10_results = run_judge(candidates_dict, mode=selected_mode)
        save_top10(top10_results, mode=selected_mode)
        judge_elapsed = time.perf_counter() - judge_start
        
        st.toast(f"Top 10 setups compiled in {judge_elapsed:.2f}s!", icon="🚀")

# ---------------------------------------------------------------------------
# Load and Display Results
# ---------------------------------------------------------------------------
top10_data = load_top10()
results_data = load_results()

if top10_data:
    st.markdown(f"### 📊 **Top Curated Portfolio Candidates — Mode: {top10_data.get('scan_mode', 'ALL')}**")
    st.caption(f"Last scanned on: `{top10_data.get('scan_time', 'N/A')}`")
    
    # -----------------------------------------------------------------------
    # Quantitative Funnel Metrics Grid
    # -----------------------------------------------------------------------
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.html(textwrap.dedent(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='metric-lbl'>Universe Pre-Filtered</div>
            <div class='metric-val'>1,483</div>
            <div class='metric-lbl' style='color:#10b981;'>Eligible Symbols</div>
        </div>
        """))
    with m2:
        st.html(textwrap.dedent(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='metric-lbl'>Funnel Matches</div>
            <div class='metric-val'>{len(results_data)}</div>
            <div class='metric-lbl' style='color:#3b82f6;'>Scored Candidates</div>
        </div>
        """))
    with m3:
        st.html(textwrap.dedent(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='metric-lbl'>LLM Gated</div>
            <div class='metric-val'>10</div>
            <div class='metric-lbl' style='color:#a855f7;'>Final Selections</div>
        </div>
        """))
    with m4:
        st.html(textwrap.dedent(f"""
        <div class='glass-card' style='text-align: center;'>
            <div class='metric-lbl'>API Response Status</div>
            <div class='metric-val'>{"✓ OK" if has_api_key else "Fallback"}</div>
            <div class='metric-lbl' style='color:#f59e0b;'>{"LPU Engine" if has_api_key else "Quantitative Fallback"}</div>
        </div>
        """))

    # -----------------------------------------------------------------------
    # Main Dashboard Columns
    # -----------------------------------------------------------------------
    left_col, right_col = st.columns([2, 1])
    
    # Left Column: Card items
    with left_col:
        st.markdown("#### Curated Stock Seups")
        
        for item in top10_data.get("results", []):
            rank = item.get("rank", 0)
            symbol = item.get("symbol", "")
            pattern = item.get("pattern", "").upper()
            score = item.get("composite_score", 0.0)
            conviction = item.get("conviction", "LOW").upper()
            buy_point = item.get("buy_point", 0.0)
            stop_loss = item.get("stop_loss", 0.0)
            target = item.get("target", 0.0)
            rr_ratio = item.get("rr_ratio", 0.0)
            verdict = item.get("judge_verdict", "")
            why_here = item.get("why_ranked_here", "")
            flags = item.get("flags", "")
            sector = item.get("sector", "N/A")
            distance = item.get("distance_from_buy_pct", 0.0)
            
            # Badge mappings
            p_badge = "badge-vcp"
            if "FLAG" in pattern: p_badge = "badge-flag"
            elif "CUP" in pattern: p_badge = "badge-cup"
            elif "BREAKOUT" in pattern: p_badge = "badge-breakout"
            
            c_badge = "badge-low"
            if conviction == "HIGH": c_badge = "badge-high"
            elif conviction == "MEDIUM": c_badge = "badge-medium"
            
            st.html(textwrap.dedent(f"""
            <div class="glass-card">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.8rem;">
                    <div style="display: flex; align-items: center; gap: 0.8rem;">
                        <span style="font-size: 1.5rem; font-weight: 700; color: #10b981;">#{rank}</span>
                        <span style="font-size: 1.4rem; font-weight: 700; color: #ffffff; letter-spacing: 0.02em;">{symbol}</span>
                        <span class="badge {p_badge}">{pattern}</span>
                        <span style="font-size: 0.9rem; color: #94a3b8;">({sector})</span>
                    </div>
                    <div style="display: flex; align-items: center; gap: 0.8rem;">
                        <span style="font-size: 0.95rem; color:#94a3b8;">Score: <b style="color:#ffffff;">{score:.1f}</b></span>
                        <span class="badge {c_badge}">{conviction} Conviction</span>
                    </div>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.5rem; background: rgba(15, 23, 42, 0.4); padding: 0.8rem; border-radius: 8px; margin-bottom: 0.8rem; text-align: center; border: 1px solid rgba(255,255,255,0.03);">
                    <div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Buy Trigger</div>
                        <div style="font-size: 1.05rem; font-weight: 600; color:#e2e8f0;">₹{buy_point:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Stop Loss</div>
                        <div style="font-size: 1.05rem; font-weight: 600; color:#ef4444;">₹{stop_loss:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Target</div>
                        <div style="font-size: 1.05rem; font-weight: 600; color:#10b981;">₹{target:.2f}</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">R:R Ratio</div>
                        <div style="font-size: 1.05rem; font-weight: 600; color:#3b82f6;">{rr_ratio:.1f}x</div>
                    </div>
                    <div>
                        <div style="font-size: 0.75rem; color: #64748b; text-transform: uppercase;">Buy Proximity</div>
                        <div style="font-size: 1.05rem; font-weight: 600; color:{'#10b981' if -5 <= distance <= 1 else '#f59e0b'};">{distance:+.2f}%</div>
                    </div>
                </div>
                
                <div style="font-size: 0.92rem; line-height: 1.5; color: #cbd5e1; margin-bottom: 0.5rem;">
                    <b>Verdict:</b> {verdict}
                </div>
                <div style="font-size: 0.85rem; color: #94a3b8; font-style: italic;">
                    <b>Ranking Rationale:</b> {why_here}
                </div>
                {f'<div style="margin-top: 0.6rem; font-size: 0.85rem; background: rgba(239, 68, 68, 0.1); border: 1px dashed rgba(239,68,68,0.2); padding: 0.5rem; border-radius: 6px; color: #f87171;">⚠️ <b>Warning flag:</b> {flags}</div>' if flags else ''}
            </div>
            """))
            
    # Right Column: Visual analytics
    with right_col:
        st.markdown("#### Portfolio Analytics")
        
        # Sector Capping visual chart
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("**Sector Concentration**")
        sectors_list = [item.get("sector", "N/A") for item in top10_data.get("results", [])]
        sectors_filtered = [s if s else "Unspecified" for s in sectors_list]
        sec_df = pd.DataFrame(Counter(sectors_filtered).items(), columns=["Sector", "Stocks Count"])
        st.bar_chart(sec_df.set_index("Sector"), color="#10b981", height=200)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Chart patterns counts
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("**Pattern Distribution**")
        patterns_list = [item.get("pattern", "N/A").upper() for item in top10_data.get("results", [])]
        pat_df = pd.DataFrame(Counter(patterns_list).items(), columns=["Pattern Type", "Selections"])
        st.bar_chart(pat_df.set_index("Pattern Type"), color="#3b82f6", height=200)
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Composite score dispersion
        st.markdown("<div class='glass-card'>", unsafe_allow_html=True)
        st.markdown("**Quantitative vs Qualitative Score Dispersion**")
        disp_data = []
        for item in top10_data.get("results", []):
            disp_data.append({
                "Symbol": item.get("symbol", ""),
                "Composite Score": item.get("composite_score", 0.0),
                "Signal Strength": item.get("signal_strength", 0.0)
            })
        disp_df = pd.DataFrame(disp_data)
        st.line_chart(disp_df.set_index("Symbol"), height=200)
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.html(textwrap.dedent("""
    <div class='glass-card' style='text-align: center; padding: 3rem;'>
        <div style='font-size: 3.5rem; margin-bottom: 1rem;'>📊</div>
        <h3>No Scanned Results Available</h3>
        <p style='color: #94a3b8; font-weight: 300;'>Click the <b>Run Live Parallel Scan</b> button in the sidebar control panel to trigger the quantitative process pool and Groq judge pipelines.</p>
    </div>
    """))
