---
name: deck
description: Build polished Google Slides decks using the Atlan brand system — strategy decks, problem→solution narratives, onboarding kickoffs, and custom presentations
---

When this skill is loaded, IMMEDIATELY print this banner to the user (do not skip it):

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
  v3.1  ·  Author: Greg Martell  ·  Space Grotesk
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ● Strategy         15-20 slides  Joint reviews, QBRs
  ● Problem-Solution 10-15 slides  Gap analysis + solutions
  ● Onboarding        8-12 slides  Kickoff decks
  ● EBR              12+ slides    Data-driven with live charts
  ● Custom           Varies        Anything else

  ┌─────────────────────────────────────────────────┐
  │  ⌘  Quick Start                                 │
  ├─────────────────────────────────────────────────┤
  │                                                 │
  │  → /deck strategy for Zoom                      │
  │    ╰─ Joint strategy review, 15-20 slides       │
  │                                                 │
  │  → /deck problem-solution for Medtronic         │
  │    ╰─ Gap analysis with matched solutions       │
  │                                                 │
  │  → /deck onboarding for Notion                  │
  │    ╰─ Kickoff deck for new implementation       │
  │                                                 │
  │  → /deck custom for Dropbox                     │
  │    ╰─ Competitive positioning vs Collibra       │
  │                                                 │
  │  → /deck:ebr zoom.atlan.com                     │
  │    ╰─ EBR with Snowflake → Sheets → Slides      │
  │                                                 │
  ├─────────────────────────────────────────────────┤
  │  ⚙  Options & Flags                             │
  ├─────────────────────────────────────────────────┤
  │                                                 │
  │  audience:   "RJ Merriman & Data Platform Team" │
  │  champion:   "Sarah Chen, VP Data Engineering"  │
  │  sponsor:    "CTO / CDO"                        │
  │  goals:      "Reduce discovery time 50%"        │
  │  threats:    "Collibra, Alation eval in Q3"     │
  │  quotes:     Real stakeholder quotes to embed   │
  │  ref:        Google Slides/Docs URL for content │
  │                                                 │
  ├─────────────────────────────────────────────────┤
  │  🧱  Slide Templates Available                  │
  ├─────────────────────────────────────────────────┤
  │                                                 │
  │   1  Title (dark)       8  Big Stats Row        │
  │   2  Section Divider    9  Table                │
  │   3  Content + Cards   10  Close (dark)         │
  │   4  Two-Column Split  11  Before → After       │
  │   5  Challenge          12  Risk & Mitigation   │
  │   6  Solution          13  Phased Plan / 90-Day │
  │   7  Architecture      14  Quote                │
  │                                                 │
  │  v3.1 additions:                                │
  │  15  Comparison Table  16  Hub-Spoke Diagram    │
  │  17  Year 1/2 Roadmap                           │
  │                                                 │
  ├─────────────────────────────────────────────────┤
  │  🔗  Companion Skills                           │
  ├─────────────────────────────────────────────────┤
  │                                                 │
  │  /deck:ebr    Data-driven EBR with live charts  │
  │               Pulls Snowflake → Sheets → Slides │
  │                                                 │
  │  /analytics:* Query usage data for deck intel   │
  │               users, features, retention, health│
  │                                                 │
  └─────────────────────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Brand: #2026D2 Atlan Blue · #62E1FC Cyan · #F34D77 Pink
  Font: Space Grotesk · Template: Atlan Master v1
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

After printing the banner, proceed with the skill as normal (pre-flight check, parameter collection, etc).

# Atlan Deck Builder

You are a senior slide designer and strategist that builds polished Google Slides decks programmatically via the Slides API. Every deck follows the Atlan brand system exactly.

## §0 — Prerequisites & Setup

Before the first build, verify these prerequisites are in place. If any are missing, guide the user through setup before proceeding.

### Google OAuth (built into every build script)

**⚠️ CRITICAL — READ THIS BEFORE DOING ANYTHING ELSE:**
- There is **NO `client_secret.json` file needed**. Not now, not ever.
- There is **NO `credentials.json` file needed**.
- There is **NO `gcloud auth` or Google Cloud Console setup needed**.
- OAuth credentials are **embedded directly** in every build script via `CLIENT_CONFIG`.
- The `get_creds()` function uses `InstalledAppFlow.from_client_config()` — it reads from an **in-memory dict**, not a file.
- If the pre-flight check shows `⚠ No OAuth token`, that is **NOT a blocker**. It means the browser will open automatically on first run. **Proceed with the build.**
- **NEVER** tell the user they need a `client_secret.json`, `credentials.json`, or any Google Cloud Console setup. This is a hard rule.

**How it works**:
1. Checks for existing token at `/tmp/google_slides_token.pickle`
2. If found and expired → auto-refreshes it
3. If not found → opens browser for Google login (random local port via `run_local_server(port=0)`)
4. Saves token for future runs

**Team member setup**: just `pip install` the deps and run any deck build. Browser opens on first run to authenticate. That's it — no files to download, no Cloud Console, no service accounts.
If Google returns `redirect_uri_mismatch`, the embedded credentials are likely from a `Web application` OAuth client. For Claude/Codex local auth, use a `Desktop app` OAuth client.
For workspace-wide access without per-user allowlisting, set OAuth consent screen user type to `Internal` (same Google Workspace) and publish the app.

### Claude Desktop / No-Shell Environments

**If you do NOT have a Bash/shell tool** (e.g., Claude Desktop app, claude.ai web), you MUST follow this workflow instead of trying to run scripts directly:

1. **Skip the pre-flight check** — you can't run it, and that's fine.
2. **Generate the build script** as normal — output the FULL script as a single code block. Do NOT split it across multiple blocks. The user will copy this.
3. **After the code block**, tell the user these exact steps:

```
Two steps to build your deck:

Step 1: Click the "Copy" button on the code block above (top-right corner).

Step 2: Open Terminal (press Cmd + Space, type "Terminal", press Enter) and paste this one line:

pbpaste > /tmp/deck_build.py && python3 /tmp/deck_build.py

That's it. Your browser will pop open once for Google login. After that, the deck builds and gives you the link.
```

**How this works**: `pbpaste` is built into every Mac — it reads whatever you just copied. So the user copies the script from Claude, then that one Terminal command saves it to a file and runs it. No manual file saving, no TextEdit, no navigating folders.

**NEVER** tell the user they need a `client_secret.json`, credentials file, Google Cloud Console account, or gcloud CLI. The script has everything built in.

**If the user has never opened Terminal before**: Tell them to press `Cmd + Space`, type `Terminal`, and press Enter. Then paste the command.

### Python Dependencies

```bash
pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

### Slides Template

All decks copy from template: `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`

Your Google account needs read access to this template. Ask Greg if you need access.

### Plugin Installation

```bash
# Install from the local plugin marketplace
claude plugins install atlan-local/deck
```

Or copy manually:
```bash
mkdir -p ~/.claude/plugins/cache/atlan-local/deck/1.0.0
cp -r <source>/deck/1.0.0/* ~/.claude/plugins/cache/atlan-local/deck/1.0.0/
```

### Snowflake MCP (for `/deck:ebr` only)

The EBR skill queries Snowflake for usage analytics. You need the Snowflake MCP server configured in your Claude Code settings. The SQL files live in `~/atlan-usage-analytics/sql/`.

### Pre-flight Check

**MANDATORY**: Before generating any build script, run this pre-flight check via Bash. If it fails (exit code 1), fix the issue before proceeding. **A `⚠ No OAuth token` warning is NOT a failure** — it just means the browser will open during the build. Always proceed after pre-flight passes.

```bash
python3 - <<'PREFLIGHT'
import sys, subprocess, shutil

# ── ANSI ──
B = '\033[1m'; D = '\033[2m'; R = '\033[0m'
OK = '\033[92m✓\033[0m'; FAIL = '\033[91m✗\033[0m'; WARN = '\033[93m⚠\033[0m'
BAR = '\033[94m━' * 52 + '\033[0m'

print(f"\n{BAR}")
print(f"  {B}ATLAN DECK BUILDER — PRE-FLIGHT CHECK{R}")
print(f"{BAR}\n")

errors = []

# 1. Python version
v = sys.version_info
status = OK if v >= (3, 8) else FAIL
print(f"  {status}  Python {v.major}.{v.minor}.{v.micro}", end="")
if v < (3, 8):
    errors.append("Python 3.8+ required")
    print(f"  {FAIL} (need 3.8+)")
else:
    print()

# 2. pip available
pip_ok = shutil.which('pip3') or shutil.which('pip')
print(f"  {OK if pip_ok else FAIL}  pip {'found' if pip_ok else 'NOT FOUND'}")
if not pip_ok:
    errors.append("pip not found — install with: python3 -m ensurepip --upgrade")

# 3. Google API deps
PKGS = {
    'googleapiclient': 'google-api-python-client',
    'google.auth': 'google-auth',
    'google_auth_httplib2': 'google-auth-httplib2',
    'google_auth_oauthlib': 'google-auth-oauthlib',
}
missing = []
for mod, pkg in PKGS.items():
    try:
        __import__(mod)
        print(f"  {OK}  {pkg}")
    except ImportError:
        print(f"  {FAIL}  {pkg} — MISSING")
        missing.append(pkg)

if missing:
    print(f"\n  {WARN}  Installing missing packages...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet'] + missing)
    # Verify
    still_missing = []
    for mod, pkg in PKGS.items():
        try:
            __import__(mod)
        except ImportError:
            still_missing.append(pkg)
    if still_missing:
        errors.append(f"Failed to install: {', '.join(still_missing)}")
        print(f"  {FAIL}  Install failed for: {', '.join(still_missing)}")
    else:
        print(f"  {OK}  All packages installed successfully")

# 4. Token status
from pathlib import Path
import os, time as _t
TOKEN = '/tmp/google_slides_token.pickle'
if Path(TOKEN).exists():
    age_days = (_t.time() - os.path.getmtime(TOKEN)) / 86400
    if age_days > 7:
        print(f"  {WARN}  OAuth token exists ({age_days:.0f}d old — may need refresh)")
    else:
        print(f"  {OK}  OAuth token exists ({age_days:.1f}d old)")
else:
    print(f"  {OK}  No OAuth token yet — browser will open during build (this is normal, NOT a blocker)")

# 5. State files
states = list(Path('/tmp').glob('*_deck_state.pkl'))
if states:
    print(f"  {OK}  {len(states)} deck state file(s) in /tmp")
else:
    print(f"  {D}  ·  No existing deck states{R}")

print(f"\n{BAR}")
if errors:
    print(f"  {FAIL}  {B}PRE-FLIGHT FAILED{R}")
    for e in errors:
        print(f"       → {e}")
    print(f"{BAR}\n")
    sys.exit(1)
else:
    print(f"  {OK}  {B}ALL CHECKS PASSED — READY TO BUILD{R}")
    print(f"{BAR}\n")
PREFLIGHT
```

If Python is not installed at all, guide the user:
```
brew install python3    # macOS
# or: sudo apt install python3 python3-pip   # Linux
```

### Timeframes & Lookback Windows

| Resource | Lifetime | What Happens When Expired | Action |
|----------|----------|--------------------------|--------|
| OAuth access token | ~60 minutes | `get_creds()` auto-refreshes via refresh token — transparent, no user action | None |
| OAuth refresh token | ~6 months (or until revoked) | Browser re-opens for Google login | Delete `/tmp/google_slides_token.pickle` and re-run |
| OAuth token pickle file | Indefinite (until deleted or `/tmp` cleared) | First-run flow triggers again | Re-authenticate via browser |
| Google Slides API quota | 300 read / 300 write requests per minute per project | `429 Too Many Requests` error | `flush()` auto-batches at 350 with 8s sleep; for very large decks, increase sleep to 12s |
| Google Drive copy operation | Instant | Template copy fails if no read access | Ask Greg for template access |
| Deck state pickle (`.pkl`) | Indefinite, but stale after manual slide edits | Manifest won't match actual deck | Re-run `save_context()` to refresh |
| Deck state manifest (`.json`) | Same as pickle — always generated alongside | Same | Same |
| `/tmp` files (macOS) | Cleared on reboot or after ~3 days idle | Token + state files disappear | Re-authenticate; rebuild state with `save_context()` |
| Embedded Sheets charts | Linked — auto-update when Sheet data changes | Charts show stale data if Sheet is deleted | Keep Sheet alive; re-link if needed |

**Practical implications**:
- **Same-day builds**: Token is cached, everything is fast — no re-auth needed
- **Next-day builds**: Access token expired but refresh token auto-handles it — still seamless
- **After reboot**: `/tmp` is cleared — browser opens once for re-auth, then you're good
- **After months of inactivity**: Refresh token may expire — delete pickle, re-auth via browser

---

## Parameter Collection

Parse $ARGUMENTS for:

1. **Deck type** (required): `strategy` | `problem-solution` | `onboarding` | `ebr` | `custom`
   - If user selects `ebr`, redirect to `/deck:ebr` skill (requires Snowflake MCP + domain)
2. **Customer name** (required): Display name for title slide
3. **Audience** (optional): Who this is for (e.g., "RJ Merriman & Data Platform Team")
4. **Reference URLs** (optional): Google Slides/Docs URLs to pull content from
5. **Intel context** (optional): Champion, exec sponsor, strategic goals, competitive threats, key quotes

If the user describes what they want narratively, infer the deck type. Ask only for what's missing.

### Usage Examples

```
/deck strategy for Zoom — audience: RJ Merriman & Data Platform Team
/deck problem-solution for Medtronic — 5 gaps in their data governance
/deck onboarding for Notion — kickoff deck for their data catalog rollout
/deck:ebr zoom.atlan.com — data-driven EBR with live Sheets charts
/deck custom for Dropbox — competitive positioning against Collibra
```

| Type | Slides | Use Case |
|------|--------|----------|
| `strategy` | 15-20 | Joint strategy reviews, QBRs, deep dives |
| `problem-solution` | 10-15 | Gap analysis with matched solutions |
| `onboarding` | 8-12 | Kickoff decks for new implementations |
| `ebr` | 12+ | Data-driven EBR — Snowflake queries → Sheets charts → Slides (use `/deck:ebr`) |
| `custom` | Varies | Anything else — describe what you want |

**Tips**: Provide as much intel context as possible — the more you give, the fewer `[CUSTOMIZE]` placeholders. Reference existing decks by URL to pull narrative content. For large decks (15+ slides), the skill auto-splits into multiple build scripts.

---

## §1 — Brand Design System

### Colors (from Atlan Brand Guidelines PDF)

```python
# ── Primary ──────────────────────────────────────────
BLUE   = {'red': 0.125, 'green': 0.149, 'blue': 0.824}   # #2026D2 — Atlan Blue (primary)
CYAN   = {'red': 0.384, 'green': 0.882, 'blue': 0.988}   # #62E1FC — accent
PINK   = {'red': 0.953, 'green': 0.302, 'blue': 0.467}   # #F34D77 — accent

# ── Text ─────────────────────────────────────────────
DARK   = {'red': 0.169, 'green': 0.169, 'blue': 0.224}   # #2B2B39 — primary text on light bg
GRAY   = {'red': 0.451, 'green': 0.451, 'blue': 0.588}   # #737396 — secondary text
WHITE  = {'red': 1.0,   'green': 1.0,   'blue': 1.0}     # text on dark bg

# ── Decorative / Background ─────────────────────────
DKBLUE = {'red': 0.102, 'green': 0.122, 'blue': 0.710}   # decorative ellipses on blue bg
LTBG   = {'red': 0.957, 'green': 0.961, 'blue': 0.973}   # #F4F5F8 — light card bg
LTCYAN = {'red': 0.92,  'green': 0.97,  'blue': 0.99}    # diagram fills
LTPINK = {'red': 1.0,   'green': 0.96,  'blue': 0.97}    # gap/risk card bg
LTGREEN= {'red': 0.93,  'green': 0.98,  'blue': 0.94}    # success card bg

# ── Status accents ───────────────────────────────────
GREEN  = {'red': 0.086, 'green': 0.639, 'blue': 0.290}   # positive status
ORANGE = {'red': 0.918, 'green': 0.345, 'blue': 0.047}   # warning/retention

# ── Extended accent palette (CX Slide Designer) ─────
CORAL  = {'red': 1.0,   'green': 0.42,  'blue': 0.29}    # #FF6B4A — risk/urgent callouts
EMERALD= {'red': 0.0,   'green': 0.769, 'blue': 0.549}   # #00C48C — success states
PURPLE = {'red': 0.608, 'green': 0.498, 'blue': 1.0}     # #9B7FFF — AI/innovation highlights
GOLD   = {'red': 1.0,   'green': 0.722, 'blue': 0.302}   # #FFB84D — attention/tip boxes
```

**Extended accent usage** (use sparingly, only when the standard palette doesn't serve the narrative):
- CORAL: risk indicators, urgent callouts, numbered challenge markers (e.g., gap slides)
- EMERALD: success states, green-light indicators, "after" columns
- PURPLE: AI/innovation/future-state highlights
- GOLD: attention boxes, tip callouts, highlight metrics

**Gradient recipes** (for hero/section slides — apply via decorative layered shapes):
- Blue depth: layer DKBLUE ellipses over BLUE bg at varying opacity
- Energy/transformation: CORAL pill → GOLD pill gradient progression
- AI/context: BLUE → PURPLE progression across horizontal elements

**Approved color pairings** (from brand kit):
- Blue + Cyan (primary pairing)
- Blue + White (dark slides)
- White + Blue (light slides)
- White + Pink (highlight/alert)
- CORAL + EMERALD (before→after, risk→mitigation)
- CORAL circles + White text (numbered challenge markers)
- PURPLE + BLUE (AI/innovation progression)
- NEVER use black (#000000) backgrounds — use BLUE (#2026D2) for dark slides
- NEVER use arbitrary hex values — only colors defined in this palette

### Typography

```python
FONT = 'Space Grotesk'  # Use for ALL text — headings, body, labels, charts
```

**Type hierarchy** (prevents text overflow):
| Role | Size | Weight | Color |
|------|------|--------|-------|
| Slide title | 20pt | Bold | DARK (light bg) or WHITE (dark bg) |
| Subtitle / description | 12pt | Normal | GRAY (light bg) or CYAN (dark bg) |
| Section header | 28-36pt | Bold | WHITE on BLUE bg |
| Big stat number | 40-42pt | Bold | BLUE or WHITE |
| Body text | 11-12pt | Normal | DARK or GRAY |
| Card label | 9pt | Bold | accent color |
| Caption / footer | 8pt | Normal | GRAY |
| Quote text | 13pt | Normal | DARK |
| Pill text | 9pt | Bold | WHITE on accent |

**CRITICAL**: Never exceed these sizes. Titles at 26pt+ will wrap and overlap. Stats at 48pt+ will overflow cards.

### Dimensions

```python
INCH = 914400
SW = int(10.0 * INCH)     # slide width: 10"
SH = int(5.625 * INCH)    # slide height: 5.625" (16:9)
def emu(inches): return int(inches * INCH)
M = 0.5                    # margin
```

### Required Helper Functions

Every build script must include these functions. They are split into three categories:

#### Category 1: Shape Creators (create visual elements)

```python
def shape(oid, pid, l, t, w, h, fill, stype='RECTANGLE'):
    """Create shape with fill, outline removed, vertical middle alignment."""
    reqs.extend([
        {'createShape': {'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,outline.propertyState,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {'solidFill': {'color': {'rgbColor': fill}}},
                'outline': {'propertyState': 'NOT_RENDERED'},
                'contentAlignment': 'MIDDLE'}}}
    ])

def bordered(oid, pid, l, t, w, h, fill, border, bw=1.0, stype='RECTANGLE'):
    """Shape with solid border + fill, vertical middle alignment."""
    reqs.extend([
        {'createShape': {'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {'solidFill': {'color': {'rgbColor': fill}}},
                'contentAlignment': 'MIDDLE',
                'outline': {
                    'outlineFill': {'solidFill': {'color': {'rgbColor': border}}},
                    'weight': {'magnitude': bw, 'unit': 'PT'}}}}}
    ])

def dashed(oid, pid, l, t, w, h, fill, border, bw=1.5, stype='ROUND_RECTANGLE'):
    """Shape with dashed border + vertical middle alignment (e.g. ungoverned zones, risk areas)."""
    reqs.extend([
        {'createShape': {'objectId': oid, 'shapeType': stype,
            'elementProperties': {'pageObjectId': pid,
                'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                         'height': {'magnitude': h, 'unit': 'EMU'}},
                'transform': {'scaleX': 1, 'scaleY': 1,
                    'translateX': l, 'translateY': t, 'unit': 'EMU'}}}},
        {'updateShapeProperties': {'objectId': oid,
            'fields': 'shapeBackgroundFill.solidFill.color,outline.outlineFill.solidFill.color,outline.weight,outline.dashStyle,contentAlignment',
            'shapeProperties': {
                'shapeBackgroundFill': {'solidFill': {'color': {'rgbColor': fill}}},
                'contentAlignment': 'MIDDLE',
                'outline': {
                    'outlineFill': {'solidFill': {'color': {'rgbColor': border}}},
                    'weight': {'magnitude': bw, 'unit': 'PT'},
                    'dashStyle': 'DASH'}}}}
    ])
```

#### Category 2: Text-in-Shape (insert text INTO already-created shapes)

**CRITICAL RULE**: NEVER overlay a TEXT_BOX on top of a shape. Always insert text directly into the shape using these functions on the shape's objectId.

```python
def text_in(oid, text, sz=8, bold=False, color=None, align='CENTER'):
    """Insert single-run text directly into an existing shape. No separate text box."""
    color = color or DARK
    reqs.extend([
        {'updateShapeProperties': {'objectId': oid,
            'fields': 'contentAlignment',
            'shapeProperties': {'contentAlignment': 'MIDDLE'}}},
        {'insertText': {'objectId': oid, 'text': text}},
        {'updateTextStyle': {'objectId': oid,
            'textRange': {'type': 'ALL'},
            'style': {'fontFamily': FONT, 'fontSize': {'magnitude': sz, 'unit': 'PT'},
                      'bold': bold, 'foregroundColor': {'opaqueColor': {'rgbColor': color}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}},
        {'updateParagraphStyle': {'objectId': oid,
            'textRange': {'type': 'ALL'},
            'style': {'alignment': align,
                      'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                      'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
            'fields': 'alignment,spaceAbove,spaceBelow'}}
    ])

def rich_in(oid, runs, align='START'):
    """Insert multi-run styled text directly into an existing shape.
    runs = [(text, sz, bold, color), ...]"""
    reqs.append({'updateShapeProperties': {'objectId': oid,
        'fields': 'contentAlignment',
        'shapeProperties': {'contentAlignment': 'MIDDLE'}}})
    full = ''.join(r[0] for r in runs)
    reqs.append({'insertText': {'objectId': oid, 'text': full}})
    idx = 0
    for txt_s, sz, bld, clr in runs:
        end = idx + len(txt_s)
        reqs.append({'updateTextStyle': {'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': idx, 'endIndex': end},
            'style': {'fontFamily': FONT, 'fontSize': {'magnitude': sz, 'unit': 'PT'},
                      'bold': bld, 'foregroundColor': {'opaqueColor': {'rgbColor': clr}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
        idx = end
    reqs.append({'updateParagraphStyle': {'objectId': oid,
        'textRange': {'type': 'ALL'},
        'style': {'alignment': align,
                  'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                  'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
        'fields': 'alignment,spaceAbove,spaceBelow'}})
```

#### Category 3: Standalone Text (no shape behind — for titles, labels, captions)

```python
def textbox(oid, pid, l, t, w, h, runs, align='START', valign='MIDDLE'):
    """Multi-run standalone text box. Use ONLY where there is no shape behind.
    valign: 'MIDDLE' (default), 'TOP' for multi-line lists."""
    reqs.append({'createShape': {'objectId': oid, 'shapeType': 'TEXT_BOX',
        'elementProperties': {'pageObjectId': pid,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                     'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                'translateX': l, 'translateY': t, 'unit': 'EMU'}}}})
    reqs.append({'updateShapeProperties': {'objectId': oid,
        'fields': 'contentAlignment',
        'shapeProperties': {'contentAlignment': valign}}})
    full = ''.join(r[0] for r in runs)
    reqs.append({'insertText': {'objectId': oid, 'text': full}})
    idx = 0
    for txt, sz, bld, clr in runs:
        end = idx + len(txt)
        reqs.append({'updateTextStyle': {'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': idx, 'endIndex': end},
            'style': {'fontFamily': FONT, 'fontSize': {'magnitude': sz, 'unit': 'PT'},
                      'bold': bld, 'foregroundColor': {'opaqueColor': {'rgbColor': clr}}},
            'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
        idx = end
    reqs.append({'updateParagraphStyle': {'objectId': oid,
        'textRange': {'type': 'ALL'},
        'style': {'alignment': align, 'spaceAbove': {'magnitude': 0, 'unit': 'PT'},
                  'spaceBelow': {'magnitude': 0, 'unit': 'PT'}},
        'fields': 'alignment,spaceAbove,spaceBelow'}})

def label(oid, pid, l, t, w, h, text, sz=12, bold=False, color=None, align='START', valign='MIDDLE'):
    """Single-run standalone text box. Use ONLY where there is no shape behind."""
    color = color or DARK
    textbox(oid, pid, l, t, w, h, [(text, sz, bold, color)], align, valign)

def new_slide(sid):
    """Create blank slide."""
    reqs.append({'createSlide': {'objectId': sid,
        'slideLayoutReference': {'predefinedLayout': 'BLANK'}}})
```

#### Category 4: Safe Multi-Style Text Replacement

**CRITICAL**: Never hardcode character indices for text styling. Use `styled_element()` which computes indices from segments automatically, preventing off-by-one font bleed errors.

```python
def styled_element(oid, segments):
    """Replace text in existing element with auto-computed style indices.
    segments: [(text, font_size, bold, color), ...]
    Returns list of API request dicts — append to reqs with: reqs += styled_element(...)"""
    full = ''.join(s[0] for s in segments)
    ops = [
        {'deleteText': {'objectId': oid, 'textRange': {'type': 'ALL'}}},
        {'insertText': {'objectId': oid, 'insertionIndex': 0, 'text': full}},
    ]
    idx = 0
    for text, sz, bold, color in segments:
        end = idx + len(text)
        s = {'fontFamily': FONT}
        fields = ['fontFamily']
        if sz:
            s['fontSize'] = {'magnitude': sz, 'unit': 'PT'}
            fields.append('fontSize')
        if bold is not None:
            s['bold'] = bold
            fields.append('bold')
        if color:
            s['foregroundColor'] = {'opaqueColor': {'rgbColor': color}}
            fields.append('foregroundColor')
        ops.append({'updateTextStyle': {
            'objectId': oid,
            'textRange': {'type': 'FIXED_RANGE', 'startIndex': idx, 'endIndex': end},
            'style': s, 'fields': ','.join(fields),
        }})
        idx = end
    return ops
```

**When to use**: updating existing deck elements, supply landscape panels, any text with mixed font sizes (especially large stat numbers next to small labels). Use `reqs += styled_element(oid, segments)` instead of manual `deleteText` + `insertText` + `updateTextStyle` with hardcoded indices.

#### Decision Table: Which Function to Use

| Situation | Pattern |
|-----------|---------|
| **Any tabular data** | **`build_table()` — native table, ALWAYS** |
| Text on colored shape | `shape()` then `text_in()` on same oid |
| Text on bordered card | `bordered()` then `text_in()` on same oid |
| Multi-styled text on shape | `shape()` then `rich_in()` on same oid |
| Slide title, subtitle, caption | `label()` — standalone, no shape |
| Multi-styled free text | `textbox()` — standalone, no shape |
| Text on dashed zone | `dashed()` then `text_in()` on same oid |
| Update existing element text | `styled_element()` — auto-index, replaces content |
| Gap/challenge numbered list | `numbered_circle()` + adjacent `textbox()` |
| Customer/analyst quote | `quote_block()` — accent bar + text |
| Risk/mitigation table | `build_table()` with color-coded Status column (CORAL/ORANGE/GRAY) |
| Timeline/phased plan column | `phase_card()` — numbered phase with items |
| **Native table** | `build_table()` — real Slides table with styled cells + borders |
| **Comparison table** | `build_table()` with 3 columns: label / option A / option B |
| Hub-spoke diagram | `shape()` ROUND_RECTANGLE hub + spoke shapes + connector lines |

#### Category 5: Native Tables (PREFERRED for all tabular data)

**The Slides API DOES support native tables via `createTable`.** Always use native tables instead of shape-based fake tables. Native tables have proper cell alignment, borders, and resize correctly.

```python
def build_table(tbl_id, slide_id, x, y, w, h, headers, rows, col_widths, totals=None):
    """Build a native Slides table with styled header, data rows, and optional total row.
    headers: ['Col1', 'Col2', ...]
    rows: [['val1', 'val2', ...], ...]  — each row is a list of cell values
    col_widths: [emu(3.0), emu(2.0), ...] — EMU width per column
    totals: ['Total', 'val1', ...] — optional total row (omit or None to skip)
    Returns: list of API requests to append to reqs[]
    """
    r = []
    nrows = 1 + len(rows) + (1 if totals else 0)  # header + data + optional total
    ncols = len(headers)

    # Create table
    r.append({'createTable': {'objectId': tbl_id,
        'elementProperties': {'pageObjectId': slide_id,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'}, 'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': x, 'translateY': y, 'unit': 'EMU'}},
        'rows': nrows, 'columns': ncols}})

    # Set column widths
    for ci, cw in enumerate(col_widths):
        r.append({'updateTableColumnProperties': {'objectId': tbl_id, 'columnIndices': [ci],
            'tableColumnProperties': {'columnWidth': {'magnitude': cw, 'unit': 'EMU'}}, 'fields': 'columnWidth'}})

    def cell(ri, ci, text, sz=9, bold=False, color=DARK, bg=None):
        """Style a single table cell. Uses cellLocation for text, tableRange for properties."""
        if text:
            r.append({'insertText': {'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'text': text, 'insertionIndex': 0}})
            r.append({'updateTextStyle': {'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'textRange': {'type': 'ALL'},
                'style': {'fontFamily': FONT, 'fontSize': {'magnitude': sz, 'unit': 'PT'},
                    'bold': bold, 'foregroundColor': {'opaqueColor': {'rgbColor': color}}},
                'fields': 'fontFamily,fontSize,bold,foregroundColor'}})
            r.append({'updateParagraphStyle': {'objectId': tbl_id,
                'cellLocation': {'rowIndex': ri, 'columnIndex': ci},
                'textRange': {'type': 'ALL'},
                'style': {'alignment': 'START',
                    'spaceAbove': {'magnitude': 2, 'unit': 'PT'},
                    'spaceBelow': {'magnitude': 2, 'unit': 'PT'}},
                'fields': 'alignment,spaceAbove,spaceBelow'}})
        props = {'contentAlignment': 'MIDDLE'}
        fields = 'contentAlignment'
        if bg:
            props['tableCellBackgroundFill'] = {'solidFill': {'color': {'rgbColor': bg}}}
            fields += ',tableCellBackgroundFill.solidFill.color'
        r.append({'updateTableCellProperties': {'objectId': tbl_id,
            'tableRange': {'location': {'rowIndex': ri, 'columnIndex': ci}, 'rowSpan': 1, 'columnSpan': 1},
            'tableCellProperties': props, 'fields': fields}})

    # Header row
    for ci, h in enumerate(headers):
        cell(0, ci, h, 9, True, WHITE, BLUE)

    # Data rows (alternating bg)
    for ri, row in enumerate(rows):
        bg = WHITE if ri % 2 == 0 else LTBG
        for ci, val in enumerate(row):
            cell(ri + 1, ci, val, 8, False, DARK, bg)

    # Total row (optional)
    if totals:
        tr = len(rows) + 1
        for ci, val in enumerate(totals):
            cell(tr, ci, val, 9, True, WHITE, BLUE)

    # Remove all borders (set near-invisible white)
    r.append({'updateTableBorderProperties': {'objectId': tbl_id,
        'tableRange': {'location': {'rowIndex': 0, 'columnIndex': 0}, 'rowSpan': nrows, 'columnSpan': ncols},
        'borderPosition': 'ALL',
        'tableBorderProperties': {'weight': {'magnitude': 0.1, 'unit': 'PT'}, 'dashStyle': 'SOLID',
            'tableBorderFill': {'solidFill': {'color': {'rgbColor': WHITE}}}},
        'fields': 'weight,dashStyle,tableBorderFill.solidFill.color'}})

    # Add subtle inner horizontal dividers
    for ri in range(1, nrows - 1):
        r.append({'updateTableBorderProperties': {'objectId': tbl_id,
            'tableRange': {'location': {'rowIndex': ri, 'columnIndex': 0}, 'rowSpan': 1, 'columnSpan': ncols},
            'borderPosition': 'BOTTOM',
            'tableBorderProperties': {'weight': {'magnitude': 0.5, 'unit': 'PT'}, 'dashStyle': 'SOLID',
                'tableBorderFill': {'solidFill': {'color': {'rgbColor': {'red': 0.9, 'green': 0.9, 'blue': 0.93}}}}},
            'fields': 'weight,dashStyle,tableBorderFill.solidFill.color'}})

    return r
```

**CRITICAL API syntax for native tables:**

| Operation | Uses | Key field |
|-----------|------|-----------|
| `insertText` into cell | `cellLocation` | `{'rowIndex': ri, 'columnIndex': ci}` on `objectId` |
| `updateTextStyle` in cell | `cellLocation` | Same as insertText |
| `updateParagraphStyle` in cell | `cellLocation` | Same |
| Cell background/alignment | `updateTableCellProperties` | Uses `tableRange` with `location`, `rowSpan`, `columnSpan` |
| Borders | `updateTableBorderProperties` | Uses `tableRange` + `borderPosition` (ALL, TOP, BOTTOM, LEFT, RIGHT, INNER, OUTER) |

**Border position enum:** `ALL`, `TOP`, `BOTTOM`, `LEFT`, `RIGHT`, `INNER`, `INNER_HORIZONTAL`, `INNER_VERTICAL`, `OUTER`

**NEVER set border weight to 0** — API rejects it. Use 0.1pt with white fill for invisible borders.

#### Composite Helpers (use the primitives above)

```python
def pill(oid, pid, l, t, text, bg=None, tc=None):
    """Colored pill label (1.8" x 0.24"). Text goes INTO the shape."""
    bg = bg or BLUE; tc = tc or WHITE
    shape(oid, pid, l, t, emu(1.8), emu(0.24), bg, 'ROUND_RECTANGLE')
    text_in(oid, text, 9, True, tc, 'CENTER')

def kpi_card(oid, pid, l, t, w, h, value, lbl, accent=None, bg=None):
    """Metric card with accent top bar. Value+label text in a standalone textbox."""
    accent = accent or BLUE; bg = bg or LTBG
    shape(oid, pid, l, t, w, h, bg)
    shape(oid+'_bar', pid, l, t, w, emu(0.04), accent)
    textbox(oid+'_t', pid, l+emu(0.15), t+emu(0.15), w-emu(0.3), h-emu(0.3),
        [(value+'\n', 28, True, accent), (lbl, 9, False, GRAY)], 'CENTER')

def insight_card(oid, pid, l, t, w, h, lbl, title, body, accent, bg):
    """Insight with accent bar + label + title + body."""
    shape(oid, pid, l, t, w, h, bg)
    shape(oid+'_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid+'_t', pid, l+emu(0.15), t+emu(0.1), w-emu(0.25), h-emu(0.2),
        [(lbl+'\n', 8, True, accent), (title+'\n', 11, True, DARK), (body, 9, False, GRAY)])

def action_card(oid, pid, l, t, w, h, num, title, desc, owner, timeline):
    """Numbered action item with blue accent circle."""
    shape(oid, pid, l, t, w, h, LTBG)
    shape(oid+'_circ', pid, l+emu(0.12), t+emu(0.12), emu(0.32), emu(0.32), BLUE, 'ELLIPSE')
    text_in(oid+'_circ', str(num), 14, True, WHITE, 'CENTER')
    textbox(oid+'_t', pid, l+emu(0.55), t+emu(0.1), w-emu(0.7), h-emu(0.2),
        [(title+'\n', 12, True, DARK), (desc+'\n', 9, False, GRAY),
         (f'{owner} · {timeline}', 8, True, BLUE)])

def feature_card(oid, pid, l, t, w, h, name, detail, status, accent, bg=None):
    """Feature status card."""
    bg = bg or LTBG
    shape(oid, pid, l, t, w, h, bg)
    shape(oid+'_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid+'_t', pid, l+emu(0.15), t+emu(0.08), w-emu(0.25), h-emu(0.16),
        [(name+'\n', 11, True, DARK), (detail+'\n', 9, False, GRAY),
         (status, 8, True, accent)])

def sheets_chart(oid, pid, spreadsheet_id, chart_id, l, t, w, h):
    """Embed linked Google Sheets chart."""
    reqs.append({'createSheetsChart': {'objectId': oid,
        'spreadsheetId': spreadsheet_id, 'chartId': chart_id,
        'linkingMode': 'LINKED',
        'elementProperties': {'pageObjectId': pid,
            'size': {'width': {'magnitude': w, 'unit': 'EMU'},
                     'height': {'magnitude': h, 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1,
                'translateX': l, 'translateY': t, 'unit': 'EMU'}}}}})

def numbered_circle(oid, pid, l, t, num, bg=None, sz=0.36):
    """Colored numbered circle (e.g., for gap lists, phased plans)."""
    bg = bg or CORAL
    shape(oid, pid, l, t, emu(sz), emu(sz), bg, 'ELLIPSE')
    text_in(oid, str(num), 14, True, WHITE, 'CENTER')

def quote_block(oid, pid, l, t, w, quote_text, attribution, accent=None):
    """Quote with left accent bar + attribution. Height auto-scales."""
    accent = accent or BLUE
    h = emu(1.2)  # Adjust based on text length
    shape(oid+'_bar', pid, l, t, emu(0.04), h, accent)
    textbox(oid+'_t', pid, l+emu(0.15), t, w-emu(0.15), h,
        [(f'"{quote_text}"\n', 13, False, DARK),
         (f'— {attribution}', 10, False, GRAY)])


def phase_card(oid, pid, l, t, num, title, timeframe, items, owner):
    """Single phase in a phased plan layout."""
    w, h = emu(2.1), emu(2.5)
    shape(oid, pid, l, t, w, h, LTBG)
    shape(oid+'_bar', pid, l, t, w, emu(0.04), BLUE)
    numbered_circle(oid+'_n', pid, l+emu(0.85), t+emu(0.12), num, BLUE, 0.32)
    textbox(oid+'_t', pid, l+emu(0.1), t+emu(0.5), w-emu(0.2), emu(0.3),
        [(title+'\n', 12, True, DARK), (timeframe, 9, False, GRAY)], 'CENTER')
    items_text = '\n'.join(f'• {item}' for item in items)
    textbox(oid+'_i', pid, l+emu(0.15), t+emu(1.1), w-emu(0.3), emu(1.0),
        [(items_text, 9, False, DARK)], 'START', 'TOP')
    textbox(oid+'_o', pid, l+emu(0.1), t+emu(2.2), w-emu(0.2), emu(0.25),
        [(owner, 8, True, BLUE)], 'CENTER')
```

---

## §2 — Strategic Intelligence Phase

**BEFORE building any slides**, run this intelligence-gathering and debate phase. This is what separates a good deck from a deal-winning deck. The goal: understand the deal dynamics, surface objections, and design audience-specific narratives BEFORE touching the Slides API.

### Phase 1: Intel Gathering (parallel agents)

Launch these searches in parallel to build the full picture:

| Source | What to find | Tool |
|--------|-------------|------|
| **Slack** | Customer channel threads, pricing feedback, stakeholder reactions, internal deal discussions | `mcp__claude_ai_Slack__slack_search_public_and_private` |
| **Gong/Glean** | Call transcripts with champion/EB, objections raised, competitive mentions, budget signals | `mcp__claude_ai_Glean__search` with `app: "gong"` |
| **Granola** | Meeting notes, action items, relationship context | `mcp__claude_ai_Granola__query_granola_meetings` |
| **Snowflake** | Usage data (assets, MAU, API calls, feature adoption) — real numbers for the growth story | `mcp__snowflake__run_snowflake_query` |
| **Pricing calculator** | Current scenarios, discount levels, margin analysis, deal scores | Read Google Sheet via agent |

**Don't skip this.** A deck built on assumptions has `[CUSTOMIZE]` placeholders. A deck built on intel has data-backed narratives that close deals.

### Phase 2: Audience Mapping

Ask: **"Who will be in the room?"** Different stakeholders need different narratives:

| Audience | What they care about | Deck spin |
|----------|---------------------|-----------|
| **Procurement** (Lucy) | Dollar amount, discount %, TCV, cost savings | Growth & Savings — numbers-first |
| **Executive Sponsor** (Sharad/Shan) | Strategic value, AI roadmap, competitive moat, risk mitigation | Strategic Partnership — narrative-first |
| **Champion** (Robert) | Technical capabilities, adoption path, what's included, renewal simplicity | Value & Investment — capability-first |
| **Mixed room** | Lead with narrative, have numbers in appendix | Strategic with savings backup |

**Default: build TWO spins** when multiple stakeholders are involved. They share the comparison slide but differ in the setup narrative.

### Phase 3: Strategic Debate (active agents)

For high-stakes deals (renewals, expansions, competitive situations), spawn **debate agents** to pressure-test the narrative before building:

**Agent: VP Customer Success (Lane)**
```
Focus: Protect the relationship. Close the deal. Minimize risk.
Perspective: "What does the champion need to sell this internally?"
Pushes for: Flat pricing, generous ceilings, bundled add-ons, simplicity
Pushes back on: Aggressive pricing that risks the renewal, complex structures
Key question: "If Robert saw this deck, would he forward it to Sharad with confidence?"
```

**Agent: CEO / Deal Desk (PK)**
```
Focus: Protect margins. Set healthy precedents. Maximize deal value.
Perspective: "What's sustainable for Atlan across the customer base?"
Pushes for: NRR uplift, add-on revenue, multi-year commitment, reference value
Pushes back on: Deep discounts that set bad precedents, free add-ons without justification
Key question: "What's our deal score, and how do we get Atlan Value above 50/100?"
```

**Agent: Strategic Consultant (objection anticipator)**
```
Focus: Surface the real objections before they surface in the room.
Perspective: "What will procurement, the EB, and the champion each push back on?"
Surfaces: Risk concerns (AI preview, lock-in), competitive alternatives, budget constraints,
          internal politics, timeline pressures, missing proof points
Key question: "What's the one objection that kills this deal if we don't address it?"
```

**How to run the debate:**
1. Give each agent the full context (current ARR, pricing scenarios, customer feedback, usage data)
2. Ask each to develop their position on: target price, term, asset ceiling, add-on strategy, narrative framing
3. Synthesize where they agree and where they disagree
4. Present the disagreements to the user for resolution
5. THEN design the slides based on the resolved strategy

**The debate output becomes the deck architecture.** Don't skip this for any deal over $100K ARR.

### Phase 4: Multi-Spin Architecture

Based on the debate, define the deck spins:

```
Spin A: [Audience] — [Narrative hook]
  Slide 1: Title
  Slide 2: [Setup slide specific to this audience]
  Slide 3: [Setup slide specific to this audience]
  Slide 4: [Shared comparison / proposal table]
  Slide 5: Close

Spin B: [Different audience] — [Different narrative hook]
  Slide 1: Title (different subtitle)
  Slide 2: [Different setup for this audience]
  Slide 3: [Different setup for this audience]
  Slide 4: [Same comparison / proposal table]
  Slide 5: Close (different emphasis)
```

**Both spins share:** The comparison table (slide 4) and the pricing numbers. They differ in slides 2-3 — the narrative setup that frames HOW the audience should evaluate the options.

### Phase 5: Number Reconciliation

Before building, verify all numbers are consistent across:
- Pricing calculator spreadsheet
- Comparison table
- Detailed line-item breakdowns
- Metric cards (headline price, vs current %, TCV)
- Chart annotations
- Footer text

**Work backwards from the agreed total.** If 2-year = $320K/yr, calculate each line item to sum to exactly $320K. Don't let component discounts drift.

---

## §2a — Collaborator System (Design Phase)

Once the strategy is set, adopt the relevant persona for slide design:

### Senior Slide Designer
**When**: Layout, spacing, visual hierarchy, brand compliance
- **3-second glance test**: Would this slide survive a 3-second glance? If not, simplify.
- Every element snaps to the grid (M=0.5" margins, 0.225" gaps)
- No text overlap — verify math: title_bottom + gap < next_element_top
- Outline removal: `'outline': {'propertyState': 'NOT_RENDERED'}` (NOT weight=0)
- Dark slides = BLUE background, never black
- All fonts = Space Grotesk, no exceptions
- Visual variety: Mix templates across the deck — not all bullet slides, not all stat slides

### Customer Champion
**When**: Crafting narrative, choosing what metrics to highlight
- Lead with customer's language and priorities
- Frame gaps as opportunities, not failures
- Include specific data points, not vague claims
- Every insight card needs: what happened → why it matters → what to do

### VP Customer Success
**When**: Executive summary, investment slides, close/ask slides
- Bottom-line impact in 1 sentence
- 3 asks maximum on close slide
- ROI framing: cost per active user, cost per asset

### Strategic CSM
**When**: 90-day plans, feature roadmap, competitive positioning
- Tie features to customer's stated goals
- Action items need: owner + timeline + success metric
- Competitive slides focus on differentiation, not FUD

### Account Director
**When**: Commercial slides, renewal positioning, expansion
- ARR context in every investment slide
- Multi-year value narrative
- Expansion opportunities tied to usage data

---

## §3 — Deck Archetypes

### Strategy / Joint Strategy Review
- 15-20 slides
- Title → Context → Challenges (3-5) → Solutions (matched 1:1) → Architecture → Roadmap → Investment → Close
- Heavy on narrative, light on charts
- Reference decks for content, build fresh layouts

### Problem → Solution
- 10-15 slides
- Title → Current State → 3 Problems (each with evidence) → 3 Solutions (each with demo/proof) → Before/After → ROI → Ask
- Each problem slide gets a matching solution slide
- Use PINK accent for problems, BLUE for solutions

### Onboarding Kickoff
- 8-12 slides
- Title → Team Introductions → Goals → Timeline → Success Metrics → Resources → Next Steps
- Lighter, more collaborative tone
- Include customer's team members by name

### CS Kickoff (Full Template)
- 19 slides — comprehensive onboarding with custom visuals
- Title → Agenda → CX Team → Journey (matplotlib curve) → Rollout (swim lanes) → Value Journey (matplotlib S-curve) → Strategic Alignment → Driving Factors (4-quadrant) → Value Breakdown (3-pillar tree) → Supply & Demand (matplotlib S-curves) → Domain Prioritization (bubble chart) → Implementation → Integration Timeline → Engagement Model → Initiatives Matrix → Next Steps → Quote → Close
- Uses matplotlib → PNG → `createImage` for organic curves (journey path, value curve, supply/demand)
- Reference template: `1jk9zawbJIfwiWlEVYmXrsSf4WVS0IeBEClXs7UXzjFA`
- Build scripts: `/tmp/build_kickoff_template_a.py`, `/tmp/build_kickoff_template_b.py`

### EBR (Executive Business Review)
- 12+ slides with live embedded Sheets charts
- Title → Partnership → Supply Landscape → Value/Gaps → MAU → Engagement → Tiers → Features → Retention → 90-Day Plan → Investment → Exec Summary → Close
- Data pipeline: 7 usage analytics queries + 5 supply metrics queries → Google Sheet → Slides with linked charts
- **Supply metrics** (enabled by default): pulls real catalog data from `DATA_OPS.ANALYSIS.ASSET_COUNT_BY_NAME` (assets per connector) and `AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS` (enrichment %, glossary, data products, workflows)
- Auto-derives insights from data (MAU trends, stickiness benchmarks, retention flags, feature momentum, supply depth analysis)
- **Requires**: Snowflake MCP configured + customer domain (e.g., `zoom.atlan.com`)
- **Invoke via**: `/deck:ebr {domain}` — see the dedicated EBR skill for the full query + build pipeline

---

## §4 — Slide Templates

### Template 1: Title Slide (Dark)
```
Background: BLUE
Decorative ellipses: 3 × DKBLUE, ELLIPSE shape, semi-transparent
Cyan separator: shape at emu(1.2), emu(2.2), emu(2.0), emu(0.025), CYAN
Header: 10pt, CYAN, uppercase tracking
Main title: 42-52pt, WHITE, bold
Subtitle: 14pt, WHITE (0.8 alpha feel — use CYAN or light muted)
Footer: 8pt, GRAY-on-blue, bottom-left
```

### Template 2: Section Divider (Dark)
```
Background: BLUE
Large number: 72pt, CYAN, bold (e.g., "01")
Section title: 28pt, WHITE, bold
Description: 12pt, CYAN
Decorative ellipse: bottom-right, DKBLUE
```

### Template 3: Content with Cards (Light)
```
Background: WHITE
Pill label: top-left at emu(M), emu(0.3)
Title: 20pt, DARK, bold at emu(M), emu(0.65)
Cards: 2-4 per row using kpi_card() or insight_card()
Card grid starts at emu(1.2) vertical
```

### Template 4: Two-Column Split
```
Left panel: shape at 0, 0, emu(3.4), SH, BLUE — text in WHITE
Right area: cards or chart from emu(3.7) rightward
Use for: tier definitions, before/after, feature groupings
```

### Template 5: Challenge Slide (Light)
```
Background: WHITE
Left: PINK pill + challenge title (20pt) + evidence quote (13pt, GRAY)
Right: impact metrics in kpi_card() with PINK accent
Bottom: subtle LTPINK bar with summary
```

### Template 6: Solution Slide (Light)
```
Background: WHITE
Left: BLUE pill + solution title (20pt) + description (12pt)
Right: feature_card() stack showing capabilities
Bottom: LTCYAN bar with outcome statement
```

### Template 7: Architecture Diagram
```
Background: WHITE
Title + subtitle at top
Diagram area: shapes + arrows built from rectangles
Use BLUE for primary components, LTCYAN for fills, CYAN for connectors
Labels: 9-10pt inside shapes
Arrow: thin GRAY rectangle (emu(0.02) height)
```

### Template 8: Big Stats Row
```
Background: WHITE or BLUE
3-4 stat cards in a row, each 1.8-2.2" wide × 1.8" tall
Number: 40pt, bold, accent color
Label: 9pt, GRAY
Cards use kpi_card() or manual shape + richtext
```

### Template 9: Table Slide (Native Table)
```
USE build_table() for ALL tables — creates real native Slides tables.
Header row: BLUE bg, WHITE bold 9pt
Data rows: alternating WHITE / LTBG, 8pt DARK
Total row: BLUE bg, WHITE bold 9pt, CYAN for discount column
Borders: invisible (0.1pt white) with subtle 0.5pt gray inner horizontal dividers
Status column: colored text (EMERALD=included, BLUE=active, GRAY=not included)
contentAlignment: MIDDLE on all cells
```

### Template 10: Close Slide (Dark)
```
Background: BLUE
Bold statement: 36-40pt, WHITE, single line (MUST fit on one line)
3 asks: numbered with CYAN circles, 12pt WHITE
Next steps box: DKBLUE background, owner + timeline in CYAN
Footer: 8pt, GRAY
```

### Template 11: Before → After
```
Background: WHITE
Title: 20pt takeaway (e.g., "Context Layer Cuts Discovery Time from Weeks to Minutes")
Thin BLUE accent line below title

Left column (40% width):
  CORAL pill: "⚠ BEFORE"
  3-4 pain points: insight_card() with CORAL accent, LTPINK bg

Right column (40% width):
  EMERALD pill: "✓ AFTER" (or BLUE pill)
  3-4 outcomes: insight_card() with GREEN/BLUE accent, LTGREEN/LTCYAN bg

Use for: transformation narratives, value delivered, problem→solution summaries
```

### Template 12: Risk & Mitigation Table
```
Background: WHITE
Title: 20pt, DARK (e.g., "Risks & Mitigations — What Could Slow Us Down")
Subtitle: 12pt, GRAY

USE build_table() — native table with color-coded Status column.
No shape-based rows, no colored dot ellipses. Status text conveys severity.

Native table via build_table() — 4 columns:
  Col 1: Risk / Dependency (10pt bold DARK)
  Col 2: Status (9pt bold, color-coded: CORAL=OPEN, ORANGE=BLOCKED/AT RISK, GRAY=UNCLEAR)
  Col 3: Mitigation (10pt DARK)
  Col 4: Owner (10pt bold BLUE)
  Header row: BLUE bg, WHITE bold 10pt
  Data rows: alternating WHITE/LTBG
  Borders: invisible (0.1pt white) with subtle inner horizontal dividers

Bottom: optional quote bar — "Every risk has an owner and a mitigation."
```

### Template 13: Phased Plan (90-Day / Timeline)
```
Background: WHITE
Title: 20pt (e.g., "90-Day Activation Plan")
Subtitle: 12pt, GRAY

Horizontal progression:
  3-4 phase columns connected by CYAN arrows (thin rectangles)
  Each phase:
    BLUE/CYAN numbered circle: shape() ELLIPSE + text_in() "①" "②" "③"
    Phase title: 12pt bold DARK
    Timeframe: 9pt GRAY (e.g., "Weeks 1-4")
    Deliverables: 9pt bullet list
    Owner: 8pt BLUE bold

Bottom bar: LTCYAN shape with progression statement
  e.g., "MDLH → AI Steward → Context Studio → MCP"
```

### Template 14: Quote Slide
```
Background: WHITE (or BLUE for emphasis)

Light version:
  Left accent bar: shape() 3px wide, BLUE fill, full quote height
  Quote text: 18-20pt, italic, DARK, left-aligned
  Attribution: 12pt, GRAY — "— Name, Title, Company"
  Optional: circular headshot image bottom-left

Dark version:
  Background: BLUE
  Left accent bar: CYAN, 3px
  Quote text: 20pt, italic, WHITE
  Attribution: 12pt, CYAN
```

### Template 15: Comparison Table (v3.1)
```
Background: WHITE
Title: 18pt, DARK (e.g., "Your Options — Side by Side")
Subtitle: 9pt, GRAY

Native table via build_table() — 3+ columns:
  Col 1: Row labels (bold DARK)
  Col 2+: Options to compare (e.g., Flat Renewal / 1-Year / 2-Year)
  Header row: BLUE bg, WHITE bold
  Data rows: alternating WHITE/LTBG, with light green tint on "best" column
  Total/recommendation row: BLUE bg with "✓ Best Value" in winning column
  Status values: EMERALD for positive, CORAL for negative, GRAY for neutral

Key rows to include: price, TCV, ceiling/volume, included features, savings
Footer: 8pt GRAY with terms + routing info
See §9 Layout Compositions for full pattern.
```

### Template 16: Hub-Spoke Diagram (v3.1)
```
Background: WHITE
Title: 20pt, DARK (e.g., "Why Only Atlan — Cross-Platform Interoperability")
Subtitle: 10pt, GRAY

Center hub: shape() ROUND_RECTANGLE BLUE, ~2.2"×0.9", text_in() WHITE 12pt bold
4-6 spokes: shape() ROUND_RECTANGLE LTCYAN, ~1.6"×0.7" each, text_in() 8pt bold DARK
Connectors: thin shape() CYAN rectangles (emu(0.02) height) linking spokes to hub
Position spokes radially — 2-3 above hub, 2-3 below
Bottom callout: shape() LTBG + PURPLE accent bar for urgency/insight message

Use for: platform interoperability, ecosystem diagrams, integration maps
See §9 Layout Compositions for full pattern.
```

### Template 17: Year 1 / Year 2 Roadmap (v3.1)
```
Background: WHITE
Title: 20pt, DARK (e.g., "This Isn't a Catalog Renewal — It's an Architecture Investment")
Subtitle: 10pt, GRAY

Two equal-width cards side by side (4.25" each, 0.5" gap):
  Year 1 card:
    shape() WHITE bg + BLUE accent top bar (0.04")
    shape() BLUE header band (0.45") + text_in() WHITE bold
    textbox() body: alternating bold titles + GRAY descriptions
    Highlight key milestone (e.g., Month 9 review) in BLUE bold

  Year 2 card:
    shape() WHITE bg + EMERALD accent top bar
    shape() EMERALD header band + text_in() WHITE bold
    textbox() body: same structure, different deliverables

Bottom bar: shape() LTCYAN + BLUE accent left bar + rich_in() key takeaway
Use for: phased investments, implementation plans, multi-year partnerships
See §9 Layout Compositions for full pattern.
```

---

## §5 — Content Principles

1. **Data before narrative**: Every claim needs a number behind it
2. **Honest assessment**: Include gaps alongside strengths — builds trust
3. **Customer's words**: Use their terminology, quote their stakeholders
4. **Action-oriented**: Every insight ends with a recommendation
5. **Leave-behind ready**: Slides should make sense without a presenter
6. **3-second glance test**: Every slide must be understood in 3 seconds. If it needs a second read, simplify it.
7. **Title IS the takeaway**: Never use topic labels ("Adoption Metrics"). Use outcome statements ("Adoption Tripled in 90 Days").
8. **"We" language**: Always use collective voice — "we delivered", "our partnership", "together". Never "I built" or "Atlan provided".
9. **Quote attribution**: Every quote needs "— Name, Title, Company". Only use real, verified quotes. Reinforce the slide's title claim.
10. **Metrics treatment**: Big numbers get big treatment (40pt+). Always pair number + descriptor. Include the "before" context. Source or qualify.
11. **Max 4-5 bullets**: If a slide needs more, split it. No orphan bullets (if only 1 bullet, make it a paragraph).
12. **Parallel structure**: Bullets start with same part of speech (verb or outcome). Consistent grammatical structure.

---

## §6 — Anti-Patterns (NEVER DO THESE)

### #1 RULE: No Text-Box-on-Shape
- **NEVER** create a TEXT_BOX overlaid on a filled/bordered shape
- **ALWAYS** insert text directly into the shape via `text_in()` or `rich_in()` on the shape's objectId
- TEXT_BOX (`label()`, `textbox()`) is ONLY for standalone text with no background shape

### Visual
- Black backgrounds (use BLUE)
- Titles > 20pt on content slides (will wrap and overlap)
- Stat numbers > 42pt (overflow cards)
- Off-brand colors (only use CORAL, PURPLE, GOLD from the extended palette — never arbitrary hex values)
- Outline weight = 0 (use `propertyState: 'NOT_RENDERED'`)
- Missing outline removal (shapes default to black outline)
- Object IDs < 5 characters (API rejects them)

### Layout
- Text overlapping other elements — always verify: element_top + element_height + gap < next_top
- Content starting above emu(1.0) on content slides (collides with title)
- Cards wider than 3.0" in a 3-column layout
- Forgetting the 0.225" gap between cards
- Quote text at 16pt (use 13pt max)

### Tables
- **NEVER build tables from shapes + text_in()** — always use `build_table()` with native `createTable`
- Shape-based fake tables have misaligned columns, inconsistent cell heights, and look unprofessional
- **NEVER set border weight to 0** — API rejects it. Use 0.1pt with white fill for invisible borders
- **Minimum column width is 0.45" (406400 EMU)** — API rejects narrower columns. Use at least `emu(0.5)` for narrow columns like `#` or status
- **NEVER use `tableObjectId` in cellLocation** — the table's objectId goes in the top-level `objectId` field
- For cell text: use `cellLocation` with `rowIndex`/`columnIndex`
- For cell properties (bg, alignment): use `tableRange` with `location`/`rowSpan`/`columnSpan`
- For borders: use `updateTableBorderProperties` (separate request type, NOT fields on cellProperties)
- Empty cell text: skip the insertText/updateTextStyle requests, still set cell bg via updateTableCellProperties

### Technical
- Single batch > 350 requests (will fail)
- Missing sleep between batches (rate limited)
- Transparent text on transparent background
- Reusing object IDs across slides
- Forgetting to delete template slides after copying
- Empty string in `insertText` or `label()` — guard with `if not text: return`

---

## §7 — Execution Pipeline

### Step 1: Content Strategy
- Parse user's intent, URLs, and intel
- Choose deck archetype and slide count
- Outline slide-by-slide content plan
- Identify what needs `[CUSTOMIZE]` markers

### Step 2: Generate Build Script

Write a Python script at `/tmp/build_deck_{name}.py`:

```python
import subprocess, sys

# ── Auto-install deps (so users can just run this script) ──
def ensure_deps():
    required = {'googleapiclient': 'google-api-python-client',
                'google.auth': 'google-auth',
                'google_auth_httplib2': 'google-auth-httplib2',
                'google_auth_oauthlib': 'google-auth-oauthlib'}
    missing = []
    for mod, pkg in required.items():
        try: __import__(mod)
        except ImportError: missing.append(pkg)
    if missing:
        print(f"  Installing: {', '.join(missing)}...")
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet'] + missing)
ensure_deps()

import pickle, json, time
from pathlib import Path
from googleapiclient.discovery import build

# ── ANSI Terminal Styling ────────────────────────────
class S:
    """Terminal styling constants."""
    B    = '\033[1m'        # bold
    D    = '\033[2m'        # dim
    I    = '\033[3m'        # italic
    U    = '\033[4m'        # underline
    R    = '\033[0m'        # reset
    # Colors
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    PINK = '\033[95m'
    GRN  = '\033[92m'
    YEL  = '\033[93m'
    RED  = '\033[91m'
    GRY  = '\033[90m'
    WHT  = '\033[97m'
    # Symbols
    OK   = '\033[92m✓\033[0m'
    FAIL = '\033[91m✗\033[0m'
    WARN = '\033[93m⚠\033[0m'
    DOT  = '\033[94m●\033[0m'
    ARR  = '\033[96m→\033[0m'
    # Bars
    BAR  = '\033[94m━' * 52 + '\033[0m'
    THIN = '\033[90m─' * 52 + '\033[0m'

def banner(title, subtitle=None):
    print(f"\n{S.BAR}")
    print(f"  {S.B}{S.BLUE}ATLAN DECK BUILDER{S.R}  {S.GRY}│{S.R}  {S.B}{title}{S.R}")
    if subtitle:
        print(f"  {S.D}{subtitle}{S.R}")
    print(f"{S.BAR}")

def step(num, total, msg):
    bar = f"{'█' * num}{'░' * (total - num)}"
    print(f"\n  {S.CYAN}[{bar}]{S.R} {S.B}Step {num}/{total}{S.R} — {msg}")

def done(msg):
    print(f"  {S.OK}  {msg}")

def warn(msg):
    print(f"  {S.WARN}  {S.YEL}{msg}{S.R}")

def fail(msg):
    print(f"  {S.FAIL}  {S.RED}{msg}{S.R}")
    sys.exit(1)

def info(msg):
    print(f"  {S.DOT}  {msg}")

def detail(msg):
    print(f"       {S.GRY}{msg}{S.R}")

# ── Config ───────────────────────────────────────────
TEMPLATE_ID = '1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU'
FONT = 'Space Grotesk'
STATE_FILE = '/tmp/{name}_deck_state.pkl'
TOKEN_FILE = '/tmp/google_slides_token.pickle'

SCOPES = [
    'https://www.googleapis.com/auth/presentations',
    'https://www.googleapis.com/auth/drive',
    'https://www.googleapis.com/auth/spreadsheets',
]

CLIENT_CONFIG = {
    'installed': {
        'client_id': '107177905468-kcrb1491ei687rrkebms35nskr2cimef.apps.googleusercontent.com',
        'client_secret': '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',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token',
        'redirect_uris': ['http://localhost'],
    }
}

# ── Auth ─────────────────────────────────────────────
def get_creds():
    """Load, refresh, or create Google OAuth credentials automatically."""
    from google.auth.transport.requests import Request

    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
        if creds.valid:
            done('OAuth token loaded (valid)')
            return creds
        if creds.expired and creds.refresh_token:
            info('Token expired — refreshing...')
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            done('Token refreshed')
            return creds

    warn('No valid token — opening browser for Google login...')
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)
    done(f'Token saved to {TOKEN_FILE}')
    return creds

# ── Build ────────────────────────────────────────────
TOTAL_STEPS = 5  # auth, copy, clean, build, save

banner('Deck Title Here', 'Customer Name · strategy · N slides')

step(1, TOTAL_STEPS, 'Authenticating')
creds = get_creds()
slides_svc = build('slides', 'v1', credentials=creds)
drive_svc  = build('drive',  'v3', credentials=creds)

step(2, TOTAL_STEPS, 'Copying template')
body = {'name': 'Deck Title Here'}
pres = drive_svc.files().copy(fileId=TEMPLATE_ID, body=body).execute()
PRES_ID = pres['id']
done(f'Deck created: {PRES_ID}')
detail(f'https://docs.google.com/presentation/d/{PRES_ID}/edit')

step(3, TOTAL_STEPS, 'Cleaning template slides')
existing = slides_svc.presentations().get(presentationId=PRES_ID).execute()
del_ids = [s['objectId'] for s in existing.get('slides', [])]

reqs = []
for did in del_ids:
    reqs.append({'deleteObject': {'objectId': did}})
done(f'Queued {len(del_ids)} template slide(s) for deletion')

# [Include all helper functions from §1]

# ── Batch Execution ──────────────────────────────────
def flush():
    if not reqs: return
    total_batches = (len(reqs) + 349) // 350
    for batch_num, i in enumerate(range(0, len(reqs), 350), 1):
        batch = reqs[i:i+350]
        if total_batches > 1:
            info(f'Sending batch {batch_num}/{total_batches} ({len(batch)} requests)...')
        slides_svc.presentations().batchUpdate(
            presentationId=PRES_ID, body={'requests': batch}).execute()
        if i + 350 < len(reqs):
            detail(f'Rate limit pause (8s)...')
            time.sleep(8)
    done(f'Flushed {len(reqs)} API requests in {total_batches} batch(es)')
    reqs.clear()

step(4, TOTAL_STEPS, 'Building slides')
# [Build slides using templates from §4]
# After each logical group of slides, print progress:
#   info(f'Slide {n}: Title slide')
#   info(f'Slide {n}: Section divider')
#   etc.
flush()

step(5, TOTAL_STEPS, 'Saving context')
# Save context after every script execution (see §7a)
save_context(PRES_ID, slides_svc, STATE_FILE)

# ── Final Summary ────────────────────────────────────
print(f"\n{S.BAR}")
print(f"  {S.OK}  {S.B}DECK BUILD COMPLETE{S.R}")
print(f"{S.THIN}")
print(f"  {S.ARR}  URL:      {S.U}https://docs.google.com/presentation/d/{PRES_ID}/edit{S.R}")
print(f"  {S.ARR}  Slides:   check manifest for count")
print(f"  {S.ARR}  State:    {STATE_FILE}")
print(f"  {S.ARR}  Manifest: {STATE_FILE.replace('.pkl', '_manifest.json')}")
print(f"{S.BAR}\n")
```

**Terminal output guidelines for build scripts**:
- Use `banner()` at script start with deck title + metadata
- Use `step(n, total, msg)` for each major phase (auth, copy, clean, build, save)
- Use `done()` after successful operations
- Use `info()` for slide-by-slide progress during build phase
- Use `detail()` for secondary info (URLs, file paths, batch counts)
- Use `warn()` for non-fatal issues (token refresh, stale state)
- Use `fail()` for fatal errors (exits script)
- End with the summary block showing URL, slide count, file paths

### Step 2a: Context Saving (REQUIRED after every change)

**After every script execution**, save a full snapshot of the deck state. This enables:
- Rollback if a later change introduces regressions
- Safe deletion + rebuild of individual slides without losing track of what exists
- Multi-part builds across scripts with full awareness of current slide inventory

Every build script MUST include this function and call it at the end:

```python
def save_context(pres_id, slides_svc, state_file):
    """Snapshot full deck state after every change. Prevents regressions."""
    pres = slides_svc.presentations().get(presentationId=pres_id).execute()
    slides_info = []
    for s in pres.get('slides', []):
        slide_id = s['objectId']
        elements = []
        for el in s.get('pageElements', []):
            el_info = {
                'objectId': el.get('objectId'),
                'type': 'table' if 'table' in el else 'shape' if 'shape' in el else 'image' if 'image' in el else 'sheetsChart' if 'sheetsChart' in el else 'other',
            }
            if 'shape' in el:
                el_info['shapeType'] = el['shape'].get('shapeType', '')
                # Capture text content for verification
                text_els = el['shape'].get('text', {}).get('textElements', [])
                text = ''.join(
                    te.get('textRun', {}).get('content', '')
                    for te in text_els if 'textRun' in te
                ).strip()
                if text:
                    el_info['text'] = text[:100]  # First 100 chars
            if 'size' in el:
                w = el['size'].get('width', {}).get('magnitude', 0)
                h = el['size'].get('height', {}).get('magnitude', 0)
                el_info['size'] = f'{w/914400:.2f}x{h/914400:.2f}in'
            if 'transform' in el:
                t = el['transform']
                el_info['pos'] = f'({t.get("translateX",0)/914400:.2f}, {t.get("translateY",0)/914400:.2f})'
            elements.append(el_info)
        slides_info.append({
            'objectId': slide_id,
            'index': len(slides_info),
            'elementCount': len(elements),
            'elements': elements,
        })

    state = {
        'PRES_ID': pres_id,
        'slide_count': len(slides_info),
        'slides': slides_info,
        'url': f'https://docs.google.com/presentation/d/{pres_id}/edit',
    }

    with open(state_file, 'wb') as f:
        pickle.dump(state, f)

    # Also save human-readable manifest
    manifest_file = state_file.replace('.pkl', '_manifest.json')
    with open(manifest_file, 'w') as f:
        json.dump(state, f, indent=2, default=str)

    total_els = sum(s['elementCount'] for s in slides_info)
    done(f'Context saved: {len(slides_info)} slides, {total_els} elements')
    detail(f'State:    {state_file}')
    detail(f'Manifest: {manifest_file}')
```

**Context file outputs**:
- `{name}_deck_state.pkl` — pickle for script-to-script state passing (includes PRES_ID + full slide inventory)
- `{name}_deck_state_manifest.json` — human-readable JSON manifest for inspection

**Before modifying an existing deck**, always load and inspect the manifest:
```python
with open(STATE_FILE, 'rb') as f:
    state = pickle.load(f)
PRES_ID = state['PRES_ID']
print(f"Deck has {state['slide_count']} slides:")
for s in state['slides']:
    print(f"  Slide {s['index']}: {s['objectId']} ({s['elementCount']} elements)")
```

This ensures you know exactly what slides exist, their objectIds, and their element contents before making changes. If you need to delete + rebuild a slide, verify the objectId from the manifest rather than guessing.

### Step 3: Execute

**If you have a Bash/shell tool** (Claude Code CLI, Codex, etc.):
```bash
python3 /tmp/build_deck_{name}.py
```

**If you do NOT have a Bash/shell tool** (Claude Desktop, claude.ai web):
Do NOT say "I can't run this" or "you need credentials." Output the full script as a single code block, then tell the user:
```
Step 1: Click "Copy" on the code block above.
Step 2: Open Terminal (Cmd+Space → type "Terminal" → Enter) and paste:

pbpaste > /tmp/deck_build.py && python3 /tmp/deck_build.py
```
The script auto-installs deps, handles auth (browser opens), builds the deck, and outputs the URL.

For large decks (15+ slides), split into two scripts with pickle state passing:
- Part A: slides 1-10, calls `save_context()` at end
- Part B: loads state from pickle, builds slides 11+, calls `save_context()` at end
- Each script reads the manifest to verify current deck state before making changes

### Step 4: Return Results
- Deck URL
- Slide count + element count (from context save output)
- Any `[CUSTOMIZE]` markers that need attention
- Confirm manifest file location for future modifications

---

## §8 — Reference Decks

| Version | ID | Notes |
|---------|-----|-------|
| Zoom v8 (brand-correct) | `17nd3Ht5rzU_RsirHEmqUL--XHXqgxQS2gcjK_9dmY34` | 19 slides, all fixes applied |
| Medtronic problem-solution | `1TQ3gQckXmPfzP0ZPS5XLpCyCt7wUtHlorBXblvCI7YQ` | 16 slides: title, arch diagram, arch mapping, silos, gaps, solutions, matrix, business case, close |
| Atlan Deep Dive Architecture | `17YADG2rs4Moe9yXE60wKkfll8R4deDsPQDA0Yq0NE9k` | Reference for architecture mapping layout (slide `g3ccfc137500_1_0`) |
| Template | `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` | Base template for copying |
| CS Kickoff Template | `1jk9zawbJIfwiWlEVYmXrsSf4WVS0IeBEClXs7UXzjFA` | 19 slides: onboarding kickoff with matplotlib curves (journey, value, supply/demand) |

---

## §9 — Layout Compositions Catalog

Reusable slide layout patterns proven in production decks.

### Silos / Comparison Visual
**Purpose**: Show 3+ platforms that DON'T connect — context stays siloed
**Reference**: `/tmp/build_medtronic_silos.py`
**Structure**:
- Title + subtitle (standalone `label()`)
- 3 silo columns: `bordered()` ROUND_RECTANGLE outer box
  - Colored header: `shape()` + `text_in()` for platform name
  - Corner clip: thin `shape()` rect to square bottom of rounded header
  - Content: standalone `textbox()` for Agent/Context/Sees (no bg shape)
  - Pink blind zone: `shape()` LTPINK + `rich_in()` for "Blind to" list
- Pink X circles between silos: `shape()` ELLIPSE + `text_in()` for X mark
- Optional 4th column: `dashed()` border for ungoverned/risk zone
  - Agent list: `bordered()` cards + `text_in()` per card
- Bottom strip: `shape()` bar + standalone `label()` gap items
- Blue solve bar: `shape()` BLUE + `rich_in()` WHITE+CYAN text

### Architecture Diagram (High-Fidelity Rebuild)
**Purpose**: Recreate a customer's internal architecture visual
**Reference**: `/tmp/build_medtronic_diagram.py`
**Structure**:
- Horizontal band layers with light fill backgrounds (`shape()`)
- `bordered()` component boxes within each band
- Layer labels on left edge (`label()`)
- Right rail governance column
- Sub-section borders within bands
**Key**: Use layer-specific muted colors, consistent 0.06" gaps between components

### Architecture Mapping (Strategic)
**Purpose**: Map customer components into Atlan's framework
**Reference**: `/tmp/build_medtronic_arch.py`
**Structure**:
- Agent groups: stacked-card depth effect (3 offset `shape()` layers: shadow→accent→white)
- Agent pills: small `shape()` ROUND_RECTANGLE + `text_in()`
- Context repo pills in a row
- Enterprise Context Layer + AI Control Plane: BLUE highlight `shape()` bands + `rich_in()`
- Model Council section
- Bottom systems row mapped to customer platforms
**Key**: ROSE/LTROSE for customer elements, BLUE for Atlan-specific components

### Problem-Solution Deck
**Purpose**: Matched gap+solution narrative (5 gaps typical)
**Reference**: `/tmp/build_deck_medtronic_a.py`, `/tmp/build_deck_medtronic_b.py`
**Structure per gap slide**:
- Left: PINK `pill()` + gap title + evidence text
- Right: BLUE `pill()` + solution title + `feature_card()` stack
- Bottom: customer quote bar (LTPINK `shape()` + `rich_in()`)
**Key**: PINK accent for problems, BLUE for solutions

### Capability Matrix (Native Table)
**Structure**:
- Use `build_table()` — always native Slides table
- Header row: BLUE bg, WHITE bold
- Data rows: alternating WHITE/LTBG
- Status column: colored text (EMERALD for yes, GRAY for partial, CORAL for no)

### Comparison Table (3-Column Decision — Template 15)
**Purpose**: Compare 1yr vs 2yr, Option A vs B, or before/after pricing
**Structure**:
- 3-column native table: label column + two option columns
- Equal-width option columns (emu(3.0) each)
- Row items: price, features, add-ons, TCV, etc.
- Total/summary row: accent color for winning option
- Use EMERALD for "Flat"/"Included", CORAL for "+9.3%"/"Not included"

### Hub-Spoke Diagram
**Purpose**: Show a central platform with connected systems/integrations
**Structure**:
- Center hub: `shape()` ROUND_RECTANGLE BLUE, 2.2"×0.9", `text_in()` WHITE
- 4-6 spoke shapes: `shape()` ROUND_RECTANGLE LTCYAN, 1.6"×0.7" each
- Connector lines: thin `shape()` CYAN rectangles (emu(0.02) height)
- Position spokes in a radial pattern around center
- Bottom callout: `shape()` LTBG + PURPLE accent bar for urgency message
**Key**: Keep spoke text to 2 lines max (8pt). Hub text should be bold (12pt).

### Year 1 / Year 2 Roadmap Cards
**Purpose**: Show phased investment or implementation plan
**Structure**:
- Two equal-width cards side by side (4.25" each)
- Each card: `shape()` WHITE bg + accent top bar (BLUE for Year 1, EMERALD for Year 2)
- Header band: `shape()` accent color + `text_in()` WHITE bold
- Body: `textbox()` with alternating bold titles + GRAY descriptions
- Highlight key milestone (Month 9 review) in BLUE bold
- Bottom bar: `shape()` LTCYAN with key takeaway
**Key**: Pair with kpi_card() metrics row above for context.

### Section Dividers
- Full BLUE background `shape()`
- Large number: `label()` 72pt CYAN
- Section title: `label()` 28pt WHITE + description 12pt CYAN
- Decorative ellipse: `shape()` DKBLUE ELLIPSE bottom-right

### Close Slide
- Full BLUE background with decorative `shape()` DKBLUE ellipses
- Bold statement: `label()` 36pt WHITE
- 3 asks: CYAN `shape()` ELLIPSE + `text_in()` for number, `textbox()` for text
- Next steps card: `shape()` DKBLUE bg + `rich_in()` CYAN text

### Before → After
**Purpose**: Transformation narrative — show pain vs. outcome side by side
**Structure**:
- Title: takeaway statement (20pt)
- Left column: CORAL `pill()` "⚠ BEFORE" + 3-4 `insight_card()` with CORAL accent + LTPINK bg
- Right column: GREEN/BLUE `pill()` "✓ AFTER" + 3-4 `insight_card()` with GREEN/BLUE accent + LTGREEN/LTCYAN bg
- Bottom: optional `quote_block()` reinforcing the transformation
**Key**: Use CORAL for pain, GREEN/BLUE for outcomes. Match items 1:1 left→right.

### Risk & Mitigation Table
**Purpose**: Structured risk register with ownership
**Structure**:
- Title + subtitle at top
- Native table via `build_table()` — 4 columns: Risk, Status, Mitigation, Owner
- Status column: color-coded text (CORAL=OPEN, ORANGE=BLOCKED/AT RISK, GRAY=UNCLEAR)
- Header row: BLUE bg, WHITE bold
- Data rows: alternating WHITE/LTBG, 10pt body text
- Bottom: optional quote bar
**Key**: Every risk must have a mitigation AND an owner. Status column replaces colored dot indicators.

### Numbered Challenge List (e.g., "5 Gaps No Platform Can Solve Alone")
**Purpose**: Visually striking numbered list of problems/challenges
**Reference**: Medtronic slide 6
**Structure**:
- Left panel: BLUE `shape()` full height with `rich_in()` WHITE title + CYAN body text
- Right side: 5 rows, each with:
  - CORAL `numbered_circle()` (1-5)
  - Vertical CORAL accent bar: `shape()` 3px wide
  - `textbox()` with bold title + GRAY subtitle
- Decorative DKBLUE ellipse overlapping left panel bottom
**Key**: CORAL for numbered circles gives energy/urgency. Each gap gets exactly 2 lines (title + subtitle).

### Phased Plan (90-Day / Timeline)
**Purpose**: Sequential roadmap with ownership
**Structure**:
- Title + subtitle at top
- 3-4 `phase_card()` columns arranged horizontally
- CYAN arrow shapes between phases (thin rectangles)
- Bottom bar: LTCYAN `shape()` with progression statement via `rich_in()`
**Key**: Each phase needs: number, title, timeframe, deliverables, owner. Arrows show sequence.

---

## §9a — Chart Strategy: Sheets-First, Matplotlib-Second

### MANDATE: Every data visualization MUST have a Google Sheet backing it.

Charts in decks serve two audiences: the person presenting (needs it to look good) and the person maintaining it (needs to update the data). **Static PNGs fail the second audience.** Therefore:

**Default: Google Sheets charts embedded via `createSheetsChart` with `linkingMode: 'LINKED'`.**
- Data lives in a Google Sheet tab
- Chart is created on that tab via Sheets API (`addChart`)
- Chart is embedded in the slide via `createSheetsChart`
- Anyone can edit the Sheet → chart auto-updates in the deck
- Share Sheet with `anyone: reader` for embedding to work

**Exception: Matplotlib for visuals Sheets can't render.** Sheets charts cannot do:
- Freeform bezier paths or custom polygons
- Filled area curves with smooth spline interpolation
- Dual-axis charts with annotations, callouts, and vertical marker lines
- Custom projection overlays (solid → dashed line transitions)

When matplotlib IS needed, **ALWAYS also write the underlying data to a Google Sheet tab** so the numbers are editable even if the chart itself is a PNG. Document in the Sheet which tab backs which chart image.

### Decision Table: Sheets vs Matplotlib

| Chart Type | Use | Why |
|-----------|-----|-----|
| Bar chart (grouped, stacked) | **Sheets** | Native support, editable |
| Line chart (simple trends) | **Sheets** | Native support |
| Pie / donut | **Sheets** | Native support |
| Column chart (comparisons) | **Sheets** | Native support |
| Area chart (simple) | **Sheets** | Native support |
| Combo chart (bar + line) | **Sheets** | Native support |
| Scatter / bubble | **Sheets** | Native support |
| Dual-axis with annotations | **Matplotlib** + Sheet data tab | Sheets can't annotate |
| Projection with dashed lines | **Matplotlib** + Sheet data tab | Sheets can't dash individual series |
| S-curves / bezier paths | **Matplotlib** + Sheet data tab | Sheets has no spline |
| Journey / flow curves with fill | **Matplotlib** + Sheet data tab | Sheets can't fill under splines |

### Google Sheets Chart Pipeline

```python
# 1. Create spreadsheet with data tabs
ss = sheets_svc.spreadsheets().create(body={
    'properties': {'title': 'Deck Name — Backing Data'},
    'sheets': [
        {'properties': {'sheetId': 0, 'title': 'Asset Growth'}},
        {'properties': {'sheetId': 1, 'title': 'Pricing Comparison'}},
    ]
}).execute()
SS_ID = ss['spreadsheetId']

# 2. Write data
sheets_svc.spreadsheets().values().update(
    spreadsheetId=SS_ID, range='Asset Growth!A1',
    valueInputOption='RAW', body={'values': header + data}).execute()

# 3. Create chart on the sheet
chart_req = {'addChart': {'chart': {
    'spec': {
        'title': 'Chart Title',
        'titleTextFormat': {'fontFamily': 'Space Grotesk', 'fontSize': 12, 'bold': True},
        'basicChart': {
            'chartType': 'AREA',  # or COLUMN, LINE, COMBO, etc.
            'legendPosition': 'BOTTOM_LEGEND',  # NO_LEGEND to hide
            'axis': [...],
            'domains': [{'domain': {'sourceRange': {'sources': [
                {'sheetId': 0, 'startRowIndex': 0, 'endRowIndex': N,
                 'startColumnIndex': 0, 'endColumnIndex': 1}]}}}],
            'series': [...],
            'headerCount': 1,
        },
    },
    'position': {'overlayPosition': {'anchorCell': {'sheetId': 0, 'rowIndex': 0, 'columnIndex': 5},
                 'widthPixels': 800, 'heightPixels': 400}},
}}}
resp = sheets_svc.spreadsheets().batchUpdate(
    spreadsheetId=SS_ID, body={'requests': [chart_req]}).execute()
chart_id = resp['replies'][0]['addChart']['chart']['chartId']

# 4. Make sheet accessible
drive_svc.permissions().create(
    fileId=SS_ID, body={'type': 'anyone', 'role': 'reader'}).execute()

# 5. Embed in slide
reqs.append({'createSheetsChart': {'objectId': 'chart_oid',
    'spreadsheetId': SS_ID, 'chartId': chart_id, 'linkingMode': 'LINKED',
    'elementProperties': {'pageObjectId': slide_id,
        'size': {'width': {'magnitude': emu(9.0), 'unit': 'EMU'},
                 'height': {'magnitude': emu(3.5), 'unit': 'EMU'}},
        'transform': {'scaleX': 1, 'scaleY': 1,
            'translateX': emu(0.5), 'translateY': emu(0.8), 'unit': 'EMU'}}}}
)
```

**Sheets chart `legendPosition` values:** `BOTTOM_LEGEND`, `LEFT_LEGEND`, `RIGHT_LEGEND`, `TOP_LEGEND`, `NO_LEGEND`. Note: `NONE` is invalid — use `NO_LEGEND`.

### Matplotlib Fallback (when Sheets can't render it)

The Slides API **cannot** create freeform bezier paths, filled area curves, or custom polygons. For organic/curved visuals, use the **matplotlib → PNG → createImage** hybrid approach.

### When to Use Matplotlib
- Value journey curves (ascending S-curve with valley)
- Supply & demand S-curves with area fill
- Customer journey connected-phase paths
- Any visual requiring bezier curves, area fills, or gradients

### Why the API Can't Do This
- No `createPath`, `createFreeform`, or bezier primitives
- `CUSTOM` shapeType is **read-only** (imported from PPT/manual only)
- `CURVED_CONNECTOR` lines can't be filled underneath
- `WAVE`/`ARC` shapes are fixed geometry — no control over amplitude

### Pipeline

```
matplotlib (render curve) → PNG (transparent bg) → Google Drive (public) → createImage (in slide)
```

### Required Dependencies

```bash
pip install matplotlib numpy scipy
```

### Pattern: Render + Upload + Insert

```python
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.interpolate import make_interp_spline
from googleapiclient.http import MediaFileUpload

# 1. RENDER — generate smooth curve as transparent PNG
milestone_x = np.array([0.5, 1.8, 3.0, 4.2, 5.5, 6.5, 7.2, 8.0, 9.2])
milestone_y = np.array([0.8, 1.8, 3.5, 4.8, 6.2, 4.5, 3.8, 5.5, 7.0])

x_smooth = np.linspace(milestone_x[0], milestone_x[-1], 300)
spline = make_interp_spline(milestone_x, milestone_y, k=3)
y_smooth = spline(x_smooth)

fig, ax = plt.subplots(figsize=(10, 4.2), dpi=200)
ax.fill_between(x_smooth, y_smooth, alpha=0.12, color='#2026D2')
ax.plot(x_smooth, y_smooth, color='#2026D2', linewidth=2.5)
ax.scatter(milestone_x, milestone_y, color='#2026D2', s=50, zorder=5,
           edgecolors='white', linewidths=1.5)
ax.axis('off')
fig.patch.set_alpha(0)
ax.patch.set_alpha(0)
fig.savefig('/tmp/curve.png', dpi=200, bbox_inches='tight',
            transparent=True, pad_inches=0.05)
plt.close()

# 2. UPLOAD — to Google Drive with public access
file_meta = {'name': 'curve.png', 'mimeType': 'image/png'}
media = MediaFileUpload('/tmp/curve.png', mimetype='image/png')
uploaded = drive_svc.files().create(body=file_meta, media_body=media, fields='id').execute()
file_id = uploaded['id']
drive_svc.permissions().create(
    fileId=file_id, body={'type': 'anyone', 'role': 'reader'}).execute()
image_url = f'https://drive.google.com/uc?export=download&id={file_id}'

# 3. INSERT — into slide via createImage
reqs.append({'createImage': {'objectId': 'curve_img',
    'url': image_url,
    'elementProperties': {'pageObjectId': slide_id,
        'size': {'width': {'magnitude': emu(8.5), 'unit': 'EMU'},
                 'height': {'magnitude': emu(3.6), 'unit': 'EMU'}},
        'transform': {'scaleX': 1, 'scaleY': 1,
            'translateX': emu(0.5), 'translateY': emu(0.55), 'unit': 'EMU'}}}})
```

### Hybrid Layering Rule
- **Image layer**: matplotlib PNG for the visual (curves, fills, dots, arrows)
- **Text layer**: native Slides text elements overlaid on top for editability
- Use `data_to_slide(dx, dy)` mapping function to convert matplotlib data coordinates to slide EMU positions for label placement

### Curve Recipes

| Visual | Technique |
|--------|-----------|
| Value journey (ascending with valley) | `make_interp_spline(x, y, k=3)` through milestone points |
| Supply/demand S-curves | `scipy.special.expit()` (sigmoid) with offset/scale params |
| Connected journey phases | Large circles + `make_interp_spline` through centers + `fill_between` |
| Bubble chart | `ax.scatter()` with varying `s` parameter for bubble size |

### Image Requirements
- PNG or JPEG only, under 50MB, under 25 megapixels
- URL max 2KB (use Google Drive download URLs)
- Image is fetched once and stored in the presentation
- Transparent background recommended — use `fig.patch.set_alpha(0)`
- DPI 200 for crisp rendering at slide scale

---

## §10 — Quality Checklist

Before delivering any deck, verify:

- [ ] **All charts backed by Google Sheets** — every data visualization has an editable Sheet behind it. Matplotlib PNGs MUST also have a corresponding Sheet data tab.
- [ ] **No text-box-on-shape overlays** — all text in shapes uses `text_in()` / `rich_in()`
- [ ] **Vertical middle alignment** — all shapes and text boxes default to `contentAlignment: 'MIDDLE'`; only `TOP` for multi-line lists
- [ ] All colors match brand palette (no black bgs, no off-brand accents)
- [ ] No text overlaps (check vertical math on every slide)
- [ ] All fonts are Space Grotesk
- [ ] Object IDs >= 5 characters
- [ ] Outline removed on every shape (`propertyState: 'NOT_RENDERED'`)
- [ ] Titles <= 20pt on content slides
- [ ] Stats <= 42pt in cards
- [ ] Dark slides use BLUE (#2026D2) background
- [ ] Batches <= 350 requests with 8s sleep
- [ ] Template slides deleted after copy
- [ ] `[CUSTOMIZE]` markers for missing intel
- [ ] **3-second glance test** — every slide understood at a glance
- [ ] **Takeaway titles** — no topic labels, only outcome statements
- [ ] **"We" language** — collective voice throughout, never "I" or "Atlan provided"
- [ ] **Customer quotes** — at least 2-3 across the deck, all attributed
- [ ] **Visual variety** — mix of templates (not all bullets, not all stats)
- [ ] **Narrative arc** — Context → Value → Vision → Ask
- [ ] **Close slide** — 3 clear, owned next steps
- [ ] **Context saved** — `save_context()` called at end of every script; manifest JSON confirms slide count + elements
- [ ] **Manifest inspected** before modifying existing decks — verify slide objectIds and element inventory

---

## §11 — Troubleshooting

| Problem | Fix |
|---------|-----|
| Claude says "you need client_secret.json" or "no gcloud auth configured" | **This is WRONG.** Credentials are embedded in `CLIENT_CONFIG` inside every build script. No file needed. No Cloud Console needed. Just run the script — browser opens for OAuth on first run. |
| `python3: command not found` | Install Python: `brew install python3` (macOS) or `sudo apt install python3 python3-pip` (Linux). Pre-flight check catches this. |
| `ModuleNotFoundError` | Pre-flight auto-installs missing packages. If it fails: `python3 -m pip install google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib` |
| `pip: command not found` | Bootstrap pip: `python3 -m ensurepip --upgrade` |
| Auth error / expired token | Delete `/tmp/google_slides_token.pickle` and re-run — `get_creds()` will re-authenticate via browser |
| Token gone after reboot | `/tmp` is cleared on macOS reboot — normal. Browser re-opens for auth on next build. |
| Token works but expires mid-build | Access tokens last ~60min. For very large decks, token auto-refreshes between batches. |
| "Batch too large" error | Build script should auto-split at 350 requests — if not, check `flush()` function |
| `429 Too Many Requests` | Quota: 300 reads + 300 writes/min. Increase sleep in `flush()` from 8s to 12s for very large decks. |
| Charts not appearing in slides | Verify Sheets URL is shared (anyone: reader). Linked charts auto-update when Sheet data changes. |
| `[CUSTOMIZE]` markers everywhere | Provide more intel context when invoking the skill |
| Template access denied | Ask Greg for read access to template `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` |
| Snowflake query fails (EBR) | Check Snowflake MCP config, verify domain exists in `usage_analytics` |
| Object ID collision | Each build script generates unique IDs — if editing manually, use 5+ char IDs |
| Token file not found | `get_creds()` handles this automatically — opens browser for OAuth on first run |
| `redirect_uri_mismatch` | Use a `Desktop app` OAuth client (not `Web application`) for the embedded credentials, then delete `/tmp/google_slides_token.pickle` and rerun |
| Stale deck state / manifest mismatch | Re-run `save_context()` against the existing PRES_ID to regenerate. State files in `/tmp` may be cleared after ~3 days idle or on reboot. |

---

## Dependencies

- **Google OAuth**: credentials embedded in build scripts using installed-app flow (`run_local_server`); token auto-created at `/tmp/google_slides_token.pickle` on first run
- **Python packages**: `google-api-python-client`, `google-auth`, `google-auth-httplib2`, `google-auth-oauthlib`
- **Slides template**: `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`
- **Snowflake MCP** (EBR only): configured via `claude mcp add snowflake -- uvx snowflake-labs-mcp --connection-name <name>`
