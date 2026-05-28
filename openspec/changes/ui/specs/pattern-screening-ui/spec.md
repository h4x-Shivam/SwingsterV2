## ADDED Requirements

### Requirement: Professional Light-Mode Visual Theme
The system SHALL render a minimal, professional, light-mode interface for NSE/BSE technical pattern screening. The interface SHALL avoid gradients, glows, neon, blur, and glassmorphism (except where explicitly requested). It SHALL use clean white surfaces, max contrast key numbers, and razor-thin borders without zebra stripes. Every pixel must earn its place, and color SHALL be used only for semantic meaning or specific pattern accents.

#### Scenario: Page Render Theme Check
- **WHEN** the user loads the page
- **THEN** the interface renders in a high-contrast, light-mode palette with Inter/DM Sans for headings, JetBrains Mono/IBM Plex Mono for numeric/stock data, and borders restricted to Gray 100/Gray 400.

### Requirement: Fixed Top Navbar (Zone A)
The system SHALL display a fixed top navbar (Zone A) of exactly 52px height at the top of the viewport. It SHALL contain a left-aligned wordmark "ChartSeeker" in 16px medium with "AI" in blue accent, and a right-aligned current date along with a gray 100 pill exchange badge "NSE · BSE". It SHALL have no navigation links, a white background, no shadow, and a subtle 0.5px gray bottom border.

#### Scenario: Navbar Layout
- **WHEN** the page is rendered or scrolled
- **THEN** the navbar remains fixed at the top of the screen with a subtle 0.5px gray bottom border, white background, and no shadow.

### Requirement: Scan Configuration Panel (Zone B)
The system SHALL render a three-row Scan Configuration Panel (Zone B) inside a white card with a 1px gray border, 16px radius, and 24px internal padding.
- Row 1: Pattern mode selector with three toggle chips (VCP, FLAG, CUP). Active chips SHALL show custom semantic colors (e.g. active VCP chip has blue 50 bg, blue 800 text, 4px blue 600 left indicator dot). Inactive chips SHALL show gray 50 bg and gray 400 text.
- Row 2: Stock universe selector with four count pills (25, 50, 100, 200). Active pills SHALL show gray 900 bg and white text. For universe counts of 100 or more, a muted estimated time suffix SHALL appear (e.g. "~5 min").
- Row 3: Scan action row containing a full-width "Run scan" button (44px tall, 6px radius, white bg, gray 900 text, 1px gray 300 border).
The configuration panel SHALL collapse to a compact "Scan settings" accordion label showing active settings inline once the scan completes.

#### Scenario: Scanning Settings Selection
- **WHEN** the user clicks pattern selector or universe selector chips
- **THEN** the selection states update visually with 150ms ease transitions, and clicking "Run scan" initiates the scanning process while scaling the button to 0.99.

### Requirement: Summary and Analytics Cards (Zone C)
The system SHALL display Zone C with aggregate stats, analytics, and matched results.
- The summary bar SHALL contain three borderless metric cards (Scanned, Matches, Top Score) with gray 50 backgrounds, followed by an inline pattern breakdown (e.g., "4× VCP · 3× Flag · 1× Cup") in muted text.
- The analytics row SHALL display three equal columns separated by 0.5px gray dividers:
  1. Pattern Distribution: Horizontal bar chart with three bars colored by pattern accents, showing counts without axes.
  2. Sector Distribution: Simple donut chart of maximum 5 sectors using a gray palette and a single accent highlight on the dominant sector, with a legend below in 11px text.
  3. Score Distribution: Sparkline-style histogram of combined scores with a blue 50 fill, blue 400 stroke, and X-axis labeled 0-100.

#### Scenario: Visual Charts Presentation
- **WHEN** a scan completes successfully
- **THEN** the summary metrics and the three charts fade in progressively and render the quantitative and qualitative distributions correctly.

### Requirement: Stock Result Cards
The system SHALL list matched stock setups as detailed cards. Each card SHALL have a white background, 1px gray border, 8px radius, and 20px padding. The left edge SHALL have a 3px solid line colored by the pattern's accent color.
- Header row: Ticker symbol (16px mono 500), exchange badge (10px pill), price (18px mono 500), price change badge (green bg for positive, red bg for negative), and pattern accent badge.
- Score row: Three labeled score bars (Signal, Volume, R/R). Each bar SHALL be 4px tall, 100% column width, rounded, and colored by pattern or green/orange, with values in 12px mono below.
- Details row: Detail string in 11px gray mono on the left, and a combined score in 22px mono on the right.
- Judge verdict row (LLM evaluation): Verdict pill (STRONG BUY/WATCHLIST/REJECT) and a one-sentence reasoning in 12px gray, alongside Entry, Stop, and Target in three mini-columns.
- Rank watermark: Absolute-positioned rank watermark at the top-right (80px, mono, 0.04 opacity).

#### Scenario: Result Card Interaction
- **WHEN** a stock card is scrolled into view or hovered
- **THEN** its score bars animate their width over 600ms using IntersectionObserver, and hovering over the card elevates the border to gray 300 with a subtle box-shadow.

### Requirement: Scan States and Transitions
The system SHALL handle four distinct scan states:
- Idle: Shows configuration panel and a single line of muted text: "Configure and run a scan to see results." No hero illustrations.
- Scanning: Replace button area with a 3px progress bar, current ticker label on the left, and scanning percentage on the right. Matching stock cards SHALL stream into the UI dynamically as they are found.
- Judging: Unresolved cards SHALL show a pulsing "Evaluating..." placeholder in the judge row, while resolved cards render the full verdict.
- Complete: Collapse the config panel, fade in the summary bar and charts, and slide up a "Scan complete — N matches" bottom toast that auto-dismisses after 3s.

#### Scenario: Scanning Progress Flow
- **WHEN** the user initiates a scan
- **THEN** the UI updates its progress, streams in matches, displays judging placeholders, collapses the panel on completion, and shows a bottom toast.
