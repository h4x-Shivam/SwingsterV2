## 1. Background API Server Setup in app.py

- [x] 1.1 Implement a background REST API server using Python's `http.server` running on a separate daemon thread inside `app.py`.
- [x] 1.2 Implement dynamic port selection (trying 8502, 8503, etc.) to prevent socket binding conflicts.
- [x] 1.3 Implement `/api/status` endpoint to return the current scanning state, progress percentages, and matches found so far.
- [x] 1.4 Implement `/api/scan` endpoint to trigger a non-blocking background scanner (`scan_all` with the specified mode and universe limits) and qualitative evaluation (`run_judge`).
- [x] 1.5 Implement `/api/results` endpoint to serve cached results (`results.json` and `top10.json`).

## 2. Frontend HTML & CSS Styling System

- [x] 2.1 Create `frontend/index.html` structure with semantic elements and clear zone subdivisions (Zones A, B, and C).
- [x] 2.2 Define CSS Custom Properties for base colors (White, Gray 50, Gray 100, Gray 400, Gray 900, Near Black) and pattern-specific accents (VCP, FLAG, CUP).
- [x] 2.3 Write core typography-first styles using Google Fonts (Inter, IBM Plex Mono) with maximum contrast on key numbers and borders restricted to 0.5px or 1px.
- [x] 2.4 Implement standard animations, hover elevations, and responsive grid layouts. Support `prefers-reduced-motion` to instantly disable all transitions.

## 3. Interactive JavaScript Application Logic

- [x] 3.1 Implement multi-state transition system in Vanilla JS (Idle/Ready, Scanning, Judging, and Complete states).
- [x] 3.2 Add click handlers to pattern selectors and universe count selectors, updating active chips visually with 150ms ease transitions.
- [x] 3.3 Implement async AJAX/Fetch scanning loop that triggers backend scans, polls progress status from the background API, and streams candidates into the UI.
- [x] 3.4 Implement score bar rendering using `IntersectionObserver` to trigger a 600ms width transition once cards enter the viewport.
- [x] 3.5 Build zero-dependency SVG micro-charts: horizontal pattern bars, a 5-sector donut chart with highlighted dominant sector, and a score sparkline-style histogram.
- [x] 3.6 Add a custom slide-up bottom toast on scan completion that auto-dismisses after 3s.

## 4. Integration & Overhaul

- [x] 4.1 Update `app.py` to hide all default Streamlit banners, sidebars, and footers via CSS injections.
- [x] 4.2 Render the full-screen interactive frontend page in `app.py` using Streamlit's `st.components.v1.html()`, passing the dynamic API port.
- [x] 4.3 Verify end-to-end functionality including pattern scanning, real-time progression, Groq judge verdict integration, and UI visual layout correctness.
