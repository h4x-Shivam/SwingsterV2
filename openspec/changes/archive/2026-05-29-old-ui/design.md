## Context

The SwingsterV2 scanning suite currently runs on a Streamlit application (`app.py`). While Streamlit is an excellent prototyping tool, its default dark-mode aesthetics, heavy padding, and rigid layout controls make it difficult to achieve the highly precise, information-dense, light-mode Bloomberg-meets-Linear terminal design requested by the user.

To deliver a premium, typographic-first, data-rich user experience, we will replace the Streamlit UI with a custom Single Page Application (SPA) designed with Vanilla HTML, Vanilla CSS, and Modern JavaScript. The SPA will be hosted seamlessly inside Streamlit via full-screen container embedding, and will communicate with a lightweight Python API server running in a background thread to handle live scans, progress streaming, and Groq judging execution.

## Goals / Non-Goals

**Goals:**
- Implement a professional, light-mode single page interface based on the exact specifications (Zone A fixed navbar, Zone B config cards, Zone C live results list).
- Support dynamic scan states: Idle/Ready, Scanning, Judging, and Complete.
- Stream matched stocks into the UI *live* during the scanning process, without waiting for the scan to finish.
- Show a pulsing "Evaluating..." placeholder for each card during the judging stage until resolved by the Groq Judge agent.
- Render high-fidelity, zero-dependency micro-charts (Pattern bar chart, Sector donut chart, Score sparkline-style histogram) that fade in progressively.
- Animate score bars (Signal, Volume, R/R) on scroll using `IntersectionObserver` over a 600ms cubic-bezier transition.
- Slide up an auto-dismissing toast (3s) on scan completion.
- Support `prefers-reduced-motion` to disable all transitions and animations instantly.

**Non-Goals:**
- Rewriting the core quantitative scanning logic (`scanner/engine.py`) or qualitative judge agent (`judge/judge_agent.py`). The existing backend logic and models will remain intact and be wrapped by our API layer.
- Introducing heavy external JavaScript frameworks (such as React, Vue, or Angular) or heavy CSS frameworks (such as Tailwind CSS). The frontend will be a zero-dependency, highly optimized single-page file structure using vanilla HTML/CSS/JS.

## Decisions

### 1. Embedded Single-Page Architecture with Background Python API
- **Decision:** Embed a full-width, full-height HTML/CSS/JS SPA inside Streamlit via `st.components.v1.html(..., height=..., scrolling=True)`. Run a lightweight REST API server using Python's built-in `http.server` or `aiohttp` in a daemon background thread from `app.py`.
- **Rationale:** Exposing a simple backend API allows the frontend JavaScript to make asynchronous `fetch` calls. This makes it possible to start scans, poll real-time progress, stream candidate matches, and fetch LLM judge verdicts dynamically without full-page reloads.
- **Alternatives Considered:** 
  - *Standard Streamlit code modifications*: Rejected because Streamlit's structural limits prevent exact 52px fixed navbars, precise light-mode monochrome palettes, and custom hover states without complex, fragile CSS overrides that break easily.
  - *Standalone Node/React service*: Rejected because it adds deployment/setup complexity for python users. The background-thread API is completely self-contained within `streamlit run app.py`.

### 2. Styling System and Light-Mode Color Palette
- **Decision:** Use Vanilla CSS with CSS Custom Properties for design system variables. Establish:
  - Base palette: White, Gray 50 (Surface), Gray 100 (Page bg), Gray 400 (Dividers), Gray 900 (Labels/Headers), Near Black (Body text).
  - Pattern accents: VCP (Blue 50 bg, Blue 800 text, Blue 600 dot/borders), Flag (Green palette), Cup (Purple palette).
  - Semantic statuses: Positive price change (Green 600 bg/text), Negative price change (Red 600 bg/text).
  - Typography: Google Fonts (Inter for wordmarks/labels, IBM Plex Mono for stock symbols, prices, and stats).
- **Rationale:** This ensures rapid styling, zero compile steps, and perfect alignment with the strict design specs (no gradients, rounded corners <= 8px except on modals, colors used only for semantic accents).

### 3. Interactive Micro-Charts using Clean SVGs & HTML Canvas
- **Decision:** Build the three analytics charts directly in JavaScript:
  - Chart 1 (Pattern Distribution): Simple, clean CSS/HTML flex layout horizontal bars.
  - Chart 2 (Sector Distribution): An SVG-based clean donut chart with max 5 sectors (gray palette with one accent highlight).
  - Chart 3 (Score Distribution): A HTML `<canvas>` or inline SVG-based sparkline histogram.
- **Rationale:** Keeps the client-side bundle size virtually zero and loads instantly, avoiding bulky charting libraries like Chart.js or D3.js.

### 4. IntersectionObserver-Driven Animations
- **Decision:** Use the native browser `IntersectionObserver` API to track when individual stock result cards enter the viewport. Once a card is visible, trigger the width transition of its score bars (Signal, Volume, R/R) from `0%` to their target width.
- **Rationale:** Ensures animations only execute when the user is actively viewing the content, conserving CPU cycles and creating a elegant, progressive scroll-reveal effect.

## Risks / Trade-offs

- **[Risk] Port Conflict for Background API Server:** If port 8502 is already in use on the developer's system, starting the background server will fail.
  - *Mitigation*: The background thread will dynamically attempt to bind to ports sequentially (e.g. 8502, 8503, 8504) until an available port is found. The active port is passed directly to the embedded iframe frontend as a URL query parameter (`?api_port=XXXX`).
  
- **[Risk] Heavy Process Pool Scanning Blocking API Event Loop:** Running CPU-intensive process pools (`scan_all`) on the same thread as the web server can block API responses.
  - *Mitigation*: Run the scanning engine (`scan_all`) on a separate Python executor thread, allowing the REST API to remain responsive and return real-time progress updates.
