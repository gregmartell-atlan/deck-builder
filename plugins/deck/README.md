# Atlan Deck Builder

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

     █████╗ ████████╗██╗      █████╗ ███╗   ██╗
    ██╔══██╗╚══██╔══╝██║     ██╔══██╗████╗  ██║
    ███████║   ██║   ██║     ███████║██╔██╗ ██║
    ██╔══██║   ██║   ██║     ██╔══██║██║╚██╗██║
    ██║  ██║   ██║   ███████╗██║  ██║██║ ╚████║
    ╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝  ╚═══╝

              D E C K   B U I L D E R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**v3.0** · Author: Greg Martell · Font: Space Grotesk

Build polished Google Slides decks programmatically via the Slides API using the Atlan brand system. Every deck is built from code — no manual drag-and-drop.

---

## Skills

| Skill | Command | Description |
|-------|---------|-------------|
| Deck Builder | `/deck:deck` | Strategy, problem-solution, onboarding, and custom decks |
| EBR Generator | `/deck:ebr` | Data-driven Executive Business Reviews with live Sheets charts |

## Deck Types

| Type | Slides | Use Case |
|------|--------|----------|
| Strategy | 15-20 | Joint strategy reviews, QBRs, deep dives |
| Problem-Solution | 10-15 | Gap analysis with matched solutions |
| Onboarding | 8-12 | Kickoff decks for new implementations |
| EBR | 12+ | Snowflake queries → Google Sheets → embedded charts in Slides |
| Custom | Varies | Anything else — describe what you want |

## Quick Start

```bash
# Strategy deck
/deck strategy for Zoom — audience: RJ Merriman & Data Platform Team

# Problem-solution deck
/deck problem-solution for Medtronic — 5 gaps in their data governance

# Onboarding kickoff
/deck onboarding for Notion — kickoff deck for their data catalog rollout

# Data-driven EBR (pulls live Snowflake data)
/deck:ebr zoom.atlan.com

# Custom deck
/deck custom for Dropbox — competitive positioning against Collibra
```

### Options & Flags

Pass these inline for richer, less `[CUSTOMIZE]`-heavy decks:

| Flag | Example | Purpose |
|------|---------|---------|
| `audience:` | `"RJ Merriman & Data Platform Team"` | Who the deck is for |
| `champion:` | `"Sarah Chen, VP Data Engineering"` | Internal champion name + title |
| `sponsor:` | `"CTO / CDO"` | Executive sponsor |
| `goals:` | `"Reduce discovery time 50%"` | Customer's strategic goals |
| `threats:` | `"Collibra, Alation eval in Q3"` | Competitive threats to address |
| `quotes:` | Real stakeholder quotes | Embedded in relevant slides |
| `ref:` | Google Slides/Docs URL | Pull content from existing decks |

---

## Prerequisites

### Python 3.8+

```bash
# macOS
brew install python3

# Linux
sudo apt install python3 python3-pip
```

### Google API Packages

Auto-installed by the pre-flight check. Manual install:

```bash
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

### Google OAuth

Credentials are **embedded directly in every build script** — no `client_secret.json` needed. On first run, your browser opens for Google login. Token is cached at `/tmp/google_slides_token.pickle`.

### Slides Template

All decks copy from template `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`. Ask Greg for read access if needed.

### Snowflake MCP (EBR only)

```bash
claude mcp add snowflake -- uvx snowflake-labs-mcp --connection-name <name> --service-config-file ~/.snowflake/service_config.yaml
```

---

## Pre-flight Check

**Runs automatically before every build.** Checks Python, pip, all 4 Google API packages, OAuth token status, and existing deck state files. Auto-installs missing packages.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ATLAN DECK BUILDER — PRE-FLIGHT CHECK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓  Python 3.12.4
  ✓  pip found
  ✓  google-api-python-client
  ✓  google-auth
  ✓  google-auth-httplib2
  ✓  google-auth-oauthlib
  ✓  OAuth token exists (0.3d old)
  ·  No existing deck states

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓  ALL CHECKS PASSED — READY TO BUILD
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### What it checks

| # | Check | Pass | Fail |
|---|-------|------|------|
| 1 | Python version | 3.8+ installed | Prompts `brew install python3` |
| 2 | pip available | `pip3` or `pip` on PATH | Prompts `python3 -m ensurepip --upgrade` |
| 3 | google-api-python-client | Import succeeds | Auto-installs via pip |
| 4 | google-auth | Import succeeds | Auto-installs via pip |
| 5 | google-auth-httplib2 | Import succeeds | Auto-installs via pip |
| 6 | google-auth-oauthlib | Import succeeds | Auto-installs via pip |
| 7 | OAuth token | Exists + age shown | Warns browser will open on first build |
| 8 | Deck state files | Count shown | Informational only |

If any critical check fails (Python missing, packages won't install), the pre-flight exits with error and blocks the build.

---

## Terminal Styling

Build scripts output styled ANSI terminal output with progress tracking:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ATLAN DECK BUILDER  │  Highmark Health Strategy
  Highmark Health · strategy · 18 slides
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  [█░░░░] Step 1/5 — Authenticating
  ✓  OAuth token loaded (valid)

  [██░░░] Step 2/5 — Copying template
  ✓  Deck created: 1abc...xyz
       https://docs.google.com/presentation/d/1abc...xyz/edit

  [███░░] Step 3/5 — Cleaning template slides
  ✓  Queued 2 template slide(s) for deletion

  [████░] Step 4/5 — Building slides
  ●  Slide 1: Title slide
  ●  Slide 2: Partnership overview
  ●  Slide 3: Where we stand
  ...
  ●  Sending batch 1/2 (350 requests)...
       Rate limit pause (8s)...
  ●  Sending batch 2/2 (187 requests)...
  ✓  Flushed 537 API requests in 2 batch(es)

  [█████] Step 5/5 — Saving context
  ✓  Context saved: 18 slides, 247 elements
       State:    /tmp/highmark_deck_state.pkl
       Manifest: /tmp/highmark_deck_state_manifest.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  ✓  DECK BUILD COMPLETE
──────────────────────────────────────────────────────
  →  URL:      https://docs.google.com/presentation/d/1abc...xyz/edit
  →  Slides:   18
  →  State:    /tmp/highmark_deck_state.pkl
  →  Manifest: /tmp/highmark_deck_state_manifest.json
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Styling functions (available in every build script)

| Function | Purpose | Example |
|----------|---------|---------|
| `banner(title, subtitle)` | Script header with deck metadata | `banner('Strategy Deck', 'Zoom · 18 slides')` |
| `step(n, total, msg)` | Progress bar per phase | `step(1, 5, 'Authenticating')` |
| `done(msg)` | Green checkmark + message | `done('Token refreshed')` |
| `info(msg)` | Blue dot + message | `info('Slide 4: MAU Trend')` |
| `detail(msg)` | Gray indented secondary info | `detail('https://docs.google.com/...')` |
| `warn(msg)` | Yellow warning | `warn('Token expired — refreshing...')` |
| `fail(msg)` | Red error + exits script | `fail('Template access denied')` |

---

## Timeframes & Lookback Windows

| Resource | Lifetime | What Happens When Expired |
|----------|----------|--------------------------|
| OAuth access token | ~60 minutes | Auto-refreshes via refresh token — transparent |
| OAuth refresh token | ~6 months (or until revoked) | Browser re-opens for Google login |
| Token pickle file | Until `/tmp` cleared | First-run flow triggers again |
| Google Slides API quota | 300 read + 300 write/min | `flush()` auto-batches at 350 with 8s sleep |
| Deck state pickle | Indefinite, stale after manual edits | Re-run `save_context()` to refresh |
| `/tmp` files (macOS) | Cleared on reboot or ~3 days idle | Re-authenticate, rebuild state |
| Embedded Sheets charts | Linked — auto-update with Sheet data | Keep Sheet alive; re-link if deleted |

**Practical implications:**
- **Same-day builds**: Token cached, no re-auth needed
- **Next-day builds**: Access token expired but refresh token handles it — seamless
- **After reboot**: `/tmp` cleared — browser opens once for re-auth
- **After months of inactivity**: Refresh token may expire — delete pickle, re-auth

---

## Brand System

| Element | Value |
|---------|-------|
| Primary | `#2026D2` Atlan Blue |
| Accent | `#62E1FC` Cyan, `#F34D77` Pink |
| Extended | `#FF6B4A` Coral, `#00C48C` Emerald, `#9B7FFF` Purple, `#FFB84D` Gold |
| Font | Space Grotesk (all text — headings, body, labels, charts) |
| Dark bg | Always `#2026D2`, never black |
| Template | `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` |

### Approved Color Pairings

- Blue + Cyan (primary pairing)
- Blue + White (dark slides)
- White + Blue (light slides)
- White + Pink (highlight/alert)
- CORAL + EMERALD (before/after, risk/mitigation)
- PURPLE + BLUE (AI/innovation)

### Type Hierarchy

| Role | Size | Weight | Color |
|------|------|--------|-------|
| Slide title | 20pt | Bold | DARK or WHITE |
| Subtitle | 12pt | Normal | GRAY or CYAN |
| Section header | 28-36pt | Bold | WHITE on BLUE |
| Big stat number | 40-42pt | Bold | BLUE or WHITE |
| Body text | 11-12pt | Normal | DARK or GRAY |
| Card label | 9pt | Bold | Accent color |
| Pill text | 9pt | Bold | WHITE on accent |
| Caption | 8pt | Normal | GRAY |

---

## 14 Slide Templates

| # | Template | Use Case |
|---|----------|----------|
| 1 | Title (dark) | Opening slide — BLUE bg, decorative ellipses, 42-52pt title |
| 2 | Section Divider | Chapter breaks — large number + section title on BLUE |
| 3 | Content + Cards | KPI cards, insight cards — light bg with pill label |
| 4 | Two-Column Split | BLUE left panel + cards/charts right |
| 5 | Challenge | PINK accent — problem statement + impact metrics |
| 6 | Solution | BLUE accent — solution + feature cards |
| 7 | Architecture Diagram | Component layouts with bands, borders, connectors |
| 8 | Big Stats Row | 3-4 large stat cards in a row (40pt numbers) |
| 9 | Table | Header + alternating rows built from shapes (no native tables) |
| 10 | Close (dark) | Bold statement + 3 asks + next steps on BLUE |
| 11 | Before/After | CORAL pain → EMERALD outcome side-by-side |
| 12 | Risk & Mitigation | Color-coded risk register with owners |
| 13 | Phased Plan | 3-4 phase columns with arrows, timelines, owners |
| 14 | Quote | Accent bar + quote text + attribution |

---

## Layout Compositions Catalog

Proven production layouts you can reference:

| Layout | Slides | Key Pattern |
|--------|--------|-------------|
| Silos / Comparison | 1 | 3+ bordered columns with blind zones + solve bar |
| Architecture Diagram | 1 | Horizontal bands with bordered component boxes |
| Architecture Mapping | 1 | Stacked-card depth effect + agent pills + context layer |
| Problem-Solution | 5-10 | PINK pill + gap → BLUE pill + solution, matched 1:1 |
| Capability Matrix | 1 | Header row + alternating data rows (all shapes) |
| Numbered Challenge List | 1 | CORAL numbered circles + BLUE left panel |
| Before/After | 1 | CORAL "Before" cards → EMERALD "After" cards |
| Risk & Mitigation Table | 1 | Color-coded dots + owner column |
| Phased Plan | 1 | Horizontal phase cards connected by CYAN arrows |

---

## EBR Pipeline (Executive Business Review)

The `/deck:ebr` skill runs a 4-step pipeline:

### Step 1: Snowflake Queries (7 queries)

| Query | Source SQL | Output |
|-------|-----------|--------|
| MAU by domain | `01_active_users/mau_by_domain.sql` | Monthly active users |
| DAU/MAU stickiness | `01_active_users/mau_dau_ratio.sql` | Stickiness ratio |
| Session duration | `03_engagement_depth/session_duration.sql` | Avg + median duration |
| Engagement tiers | `03_engagement_depth/engagement_tiers.sql` | Power/Regular/Light/Dormant |
| Retention rate | `04_retention/retention_rate_aggregate.sql` | Month-over-month retention |
| Feature adoption | `02_feature_adoption/feature_adoption_matrix.sql` | Feature × user matrix |
| Feature trends | `02_feature_adoption/feature_trend_weekly.sql` | Weekly feature adoption |

### Step 2: Google Sheet (7 tabs, 6 charts)

Creates a linked Google Sheet with data tabs and embedded charts:
- MAU line chart, Stickiness bar, Session duration grouped, Engagement tiers stacked, Retention bar, Feature trends multi-line

### Step 3: Google Slides (12+ slides)

Title → Partnership → Value/Gaps → MAU Chart → Engagement Charts → Tiers → Features → Retention → 90-Day Plan → Investment → Exec Summary → Close

### Step 4: Auto-Derived Insights

| Signal | Threshold | Action |
|--------|-----------|--------|
| MAU declining >10% | Flag in "Gaps to Address" |
| Stickiness >15% | Highlight as "above benchmark (5-15%)" |
| Stickiness <10% | Flag as episodic usage concern |
| Retention <60% | Highlight as onboarding opportunity |
| Highest unique users feature | Label as "Core Strength" |
| Fastest growing feature | Label as "Momentum" |
| Declining feature | Flag as "Discussion" topic |

---

## Helper Functions (13 total)

Every build script includes these functions, organized in 3 categories:

### Shape Creators
| Function | Purpose |
|----------|---------|
| `shape()` | Rectangle/ellipse with fill, outline removed |
| `bordered()` | Shape with solid border + fill |
| `dashed()` | Shape with dashed border (risk/ungoverned zones) |

### Text-in-Shape (CRITICAL: never overlay text boxes on shapes)
| Function | Purpose |
|----------|---------|
| `text_in()` | Single-run text directly into a shape |
| `rich_in()` | Multi-styled text directly into a shape |

### Standalone Text (no background shape)
| Function | Purpose |
|----------|---------|
| `textbox()` | Multi-run standalone text box |
| `label()` | Single-run standalone text box |
| `new_slide()` | Create blank slide |

### Composite Helpers
| Function | Purpose |
|----------|---------|
| `pill()` | Colored pill label (1.8" x 0.24") |
| `kpi_card()` | Metric card with accent top bar |
| `insight_card()` | Card with accent bar + label + title + body |
| `action_card()` | Numbered action item with blue circle |
| `feature_card()` | Feature status card with accent bar |
| `sheets_chart()` | Embed linked Google Sheets chart |
| `numbered_circle()` | Colored numbered circle |
| `quote_block()` | Quote with left accent bar + attribution |
| `risk_row()` | Risk/mitigation row with colored dots |
| `phase_card()` | Single phase in a timeline layout |

---

## Context Saving

Every build script saves a full deck snapshot after execution:

- **`{name}_deck_state.pkl`** — Pickle for script-to-script state passing
- **`{name}_deck_state_manifest.json`** — Human-readable JSON with slide inventory (objectIds, element counts, text content)

This enables:
- Multi-part builds (Part A builds slides 1-10, Part B loads state and builds 11+)
- Safe modification of existing decks (verify objectIds before deleting/rebuilding)
- Rollback if later changes introduce regressions

---

## Anti-Patterns (Never Do These)

| Rule | Why |
|------|-----|
| No TEXT_BOX overlaid on shapes | Always use `text_in()` / `rich_in()` on the shape's objectId |
| No black backgrounds | Use BLUE `#2026D2` for dark slides |
| No titles > 20pt on content slides | Will wrap and overlap |
| No stat numbers > 42pt | Overflow cards |
| No off-brand colors | Only use the defined palette |
| No outline weight = 0 | Use `propertyState: 'NOT_RENDERED'` |
| No object IDs < 5 chars | API rejects them |
| No single batch > 350 requests | Will fail — `flush()` auto-splits |
| No reusing object IDs across slides | Causes collisions |

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `python3: command not found` | `brew install python3` (macOS) or `sudo apt install python3 python3-pip` (Linux) |
| `ModuleNotFoundError` | Pre-flight auto-installs. Manual: `python3 -m pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib` |
| `pip: command not found` | `python3 -m ensurepip --upgrade` |
| Auth error / expired token | Delete `/tmp/google_slides_token.pickle` and re-run |
| Token gone after reboot | Normal — `/tmp` is cleared on macOS reboot. Browser re-opens for auth. |
| Token expires mid-build | Access tokens last ~60min. Auto-refreshes between batches. |
| `redirect_uri_mismatch` | OAuth client must be `Desktop app` type, not `Web application` |
| "Batch too large" error | Check `flush()` function — should auto-split at 350 |
| `429 Too Many Requests` | Increase sleep from 8s to 12s in `flush()` |
| Charts not appearing | Verify Sheets URL is shared (anyone: reader) |
| Template access denied | Ask Greg for read access to `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` |
| Snowflake query fails (EBR) | Check Snowflake MCP config, verify domain exists |
| Object ID collision | Use 5+ char IDs, never reuse across slides |
| `[CUSTOMIZE]` markers everywhere | Provide more intel context when invoking |
| Stale deck state | Re-run `save_context()` against the existing PRES_ID |

---

## File Structure

```
plugins/deck/
├── .claude-plugin/
│   └── plugin.json           # v3.0.0 metadata
├── README.md                 # This file
└── skills/
    ├── deck/
    │   └── SKILL.md          # Main deck builder (1,420 lines)
    └── ebr/
        └── SKILL.md          # EBR generator (285 lines)
```

## Build Output Locations

| File | Path | Purpose |
|------|------|---------|
| Build script | `/tmp/build_deck_{name}.py` | Generated Python build script |
| EBR script | `/tmp/build_ebr_{domain}.py` | EBR-specific build script |
| OAuth token | `/tmp/google_slides_token.pickle` | Cached Google auth (~60min access, ~6mo refresh) |
| Deck state | `/tmp/{name}_deck_state.pkl` | Pickle for multi-part builds |
| Manifest | `/tmp/{name}_deck_state_manifest.json` | Human-readable slide inventory |
| EBR data | `/tmp/{domain}_all_results.json` | Snowflake query results |

## Reference Decks

| Deck | ID | Notes |
|------|----|-------|
| Zoom v8 | `17nd3Ht5rzU_RsirHEmqUL--XHXqgxQS2gcjK_9dmY34` | 19 slides, all fixes applied |
| Medtronic | `1TQ3gQckXmPfzP0ZPS5XLpCyCt7wUtHlorBXblvCI7YQ` | 16 slides, problem-solution |
| Architecture Deep Dive | `17YADG2rs4Moe9yXE60wKkfll8R4deDsPQDA0Yq0NE9k` | Architecture mapping reference |
| Template | `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` | Base template for copying |
