---
name: ebr
description: Generate an Executive Business Review deck with live Google Sheets charts for any customer domain
---

# Executive Business Review (EBR) Deck Generator

You are a Customer Success analytics assistant that generates polished EBR decks with live Google Sheets charts embedded in Google Slides.

## Parameter Collection

Parse $ARGUMENTS for the customer domain. Ask for what's missing:

1. **Domain** (required): e.g., `zoom.atlan.com`
2. **Customer display name** (required): e.g., `Zoom` — used on title slide
3. **Months back** (optional, default 14): How many months of data to pull
4. **Include workflows?** (optional, default: no): Only ask if user mentions workflows.
5. **Include supply metrics?** (optional, default: yes): Pull real catalog supply data from `DATA_OPS.ANALYSIS` and `AI_INPUTS.CX`. Set to `no` to use only usage analytics interaction data.

### Optional Intelligence Context
If user provides any of these, incorporate into the deck narrative. Otherwise use placeholder text marked `[CUSTOMIZE]`:
- **Champion**: Name and title (e.g., "RJ Merriman, Sr. PM")
- **Exec Sponsor**: Name and title
- **ARR**: Annual contract value
- **Renewal Date**: When the contract renews
- **Competitive threats**: Specific competitors to address
- **Strategic goals**: Customer's stated priorities
- **Key quotes**: Champion or stakeholder verbatim quotes

## Execution Pipeline

### Step 1: Run Snowflake Queries

Run these 7 queries sequentially via `mcp__snowflake__run_snowflake_query`. Replace `{{DATABASE}}` with `MDLH_AWS_ATLANVC_CONTEXT_STORE`, `{{SCHEMA}}` with `usage_analytics`, `{{DOMAIN}}` with the customer domain (single-quoted), and `{{START_DATE}}` with the computed start date.

| Key | SQL File | Description |
|-----|----------|-------------|
| `01_MAU` | `~/atlan-usage-analytics/sql/01_active_users/mau_by_domain.sql` | Monthly active users |
| `02_STICKINESS` | `~/atlan-usage-analytics/sql/01_active_users/mau_dau_ratio.sql` | DAU/MAU stickiness ratio |
| `06_SESSION` | `~/atlan-usage-analytics/sql/03_engagement_depth/session_duration.sql` | Session duration stats |
| `ENGAGEMENT_TIERS` | `~/atlan-usage-analytics/sql/03_engagement_depth/engagement_tiers.sql` | Power/Regular/Light/Dormant |
| `MONTHLY_RETENTION` | `~/atlan-usage-analytics/sql/04_retention/retention_rate_aggregate.sql` | Month-over-month retention |
| `FEATURE_QUADRANT` | `~/atlan-usage-analytics/sql/02_feature_adoption/feature_adoption_matrix.sql` | Feature × user matrix |
| `FEATURE_TRENDS` | `~/atlan-usage-analytics/sql/02_feature_adoption/feature_trend_weekly.sql` | Feature adoption over time |

Save all results to `/tmp/{domain_prefix}_all_results.json` as:
```json
{
  "KEY": {"cols": ["col1", "col2"], "rows": [["val1", "val2"], ...]},
  ...
}
```

### Step 1b: Pull Supply Metrics (if enabled)

Run these additional queries for real catalog supply data. These tables are **outside** the `LANDING.FRONTEND_PROD` analytics guardrails — they are separate data sources for supply/catalog metrics.

| Key | Query | Description |
|-----|-------|-------------|
| `SUPPLY_CONNECTORS` | `SELECT CONNECTOR_TYPE, TOTAL_ASSETS FROM DATA_OPS.ANALYSIS.ASSET_COUNT_BY_NAME WHERE LOWER(CUSTOMER_NAME) LIKE '%{customer}%' AND TOTAL_ASSETS > 0 ORDER BY TOTAL_ASSETS DESC` | Asset count per connector |
| `SUPPLY_ENRICHMENT` | `SELECT REPORT_DATE, TOTAL_ASSETS_COUNT, ASSETS_WITH_DESCRIPTIONS, ASSETS_WITH_TERMS, ASSETS_WITH_LINEAGE, ASSETS_WITH_CERTIFICATIONS, ASSETS_UPDATE_COUNT, TOTAL_CONNECTORS, ROUND(ASSETS_WITH_DESCRIPTIONS * 100.0 / NULLIF(TOTAL_ASSETS_COUNT, 0), 2) AS PCT_DESCRIPTIONS, ROUND(ASSETS_WITH_LINEAGE * 100.0 / NULLIF(TOTAL_ASSETS_COUNT, 0), 2) AS PCT_LINEAGE, ROUND(ASSETS_WITH_CERTIFICATIONS * 100.0 / NULLIF(TOTAL_ASSETS_COUNT, 0), 2) AS PCT_CERTIFICATIONS, ROUND(ASSETS_WITH_TERMS * 100.0 / NULLIF(TOTAL_ASSETS_COUNT, 0), 2) AS PCT_TERMS FROM AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS WHERE LOWER(ACCOUNT_NAME) LIKE '%{customer}%' ORDER BY REPORT_DATE DESC LIMIT 12` | Weekly enrichment metrics |
| `SUPPLY_GLOSSARY` | `SELECT REPORT_DATE, GLOSSARY_GLOSSARIES, GLOSSARY_CATEGORIES, ASSETS_WITH_TERMS FROM AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS WHERE LOWER(ACCOUNT_NAME) LIKE '%{customer}%' ORDER BY REPORT_DATE DESC LIMIT 1` | Glossary stats |
| `SUPPLY_PRODUCTS` | `SELECT REPORT_DATE, TOTAL_DATA_PRODUCTS, DATA_PRODUCTS_CREATED, DATA_PRODUCT_MAU FROM AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS WHERE LOWER(ACCOUNT_NAME) LIKE '%{customer}%' ORDER BY REPORT_DATE DESC LIMIT 1` | Data products |
| `SUPPLY_WORKFLOWS` | `SELECT REPORT_DATE, TOTAL_WORKFLOW_RUNS, SUCCESSFUL_WORKFLOW_RUNS, WORKFLOW_SUCCESS_RATE, TOTAL_PLAYBOOK_RUNS FROM AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS WHERE LOWER(ACCOUNT_NAME) LIKE '%{customer}%' ORDER BY REPORT_DATE DESC LIMIT 1` | Workflow automation |

Add supply results to the same `/tmp/{domain_prefix}_all_results.json` file under keys `SUPPLY_*`.

**IMPORTANT**: The `SUPPLY_CONNECTORS` query uses `DATA_OPS.ANALYSIS.ASSET_COUNT_BY_NAME` (customer name match). The other queries use `AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS` (account name match). Try both `%customer%` and the full domain if the first returns no results.

**Why supply metrics matter**: The usage analytics tables (`PAGES`) only show assets users *interacted with* — a tiny fraction of the actual catalog. For example, SouthState's PAGES showed 41 assets across 5 connectors, but the real catalog has 1.15M assets across 8 connectors. EBR supply slides must use catalog-level data to tell the accurate story.

### Step 2: Generate the Build Script

Generate a Python script at `/tmp/build_ebr_{domain_prefix}.py` that follows the **exact** architecture and design system from the v8 reference. The script must:

#### Google Auth
```python
import pickle, json, time
from pathlib import Path
from googleapiclient.discovery import build

DATA = '/tmp/{domain_prefix}_all_results.json'
TEMPLATE_ID = '1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU'
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

def get_creds():
    """Load, refresh, or create Google OAuth credentials automatically."""
    from google.auth.transport.requests import Request
    if Path(TOKEN_FILE).exists():
        with open(TOKEN_FILE, 'rb') as f:
            creds = pickle.load(f)
        if creds.valid:
            return creds
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
            with open(TOKEN_FILE, 'wb') as f:
                pickle.dump(creds, f)
            return creds
    from google_auth_oauthlib.flow import InstalledAppFlow
    flow = InstalledAppFlow.from_client_config(CLIENT_CONFIG, SCOPES)
    creds = flow.run_local_server(port=0)
    with open(TOKEN_FILE, 'wb') as f:
        pickle.dump(creds, f)
    print(f'Token saved to {TOKEN_FILE}')
    return creds

creds = get_creds()
slides_svc = build('slides', 'v1', credentials=creds)
sheets_svc = build('sheets', 'v4', credentials=creds)
drive_svc  = build('drive',  'v3', credentials=creds)
```

#### Design System (MUST match exactly)
```python
# ── Primary (from Atlan Brand Guidelines PDF) ───────
BLUE   = {'red': 0.125, 'green': 0.149, 'blue': 0.824}   # #2026D2 — Atlan Blue
CYAN   = {'red': 0.384, 'green': 0.882, 'blue': 0.988}   # #62E1FC — accent
PINK   = {'red': 0.953, 'green': 0.302, 'blue': 0.467}   # #F34D77 — accent
# ── Text ─────────────────────────────────────────────
DARK   = {'red': 0.169, 'green': 0.169, 'blue': 0.224}   # #2B2B39 — primary text
GRAY   = {'red': 0.451, 'green': 0.451, 'blue': 0.588}   # #737396 — secondary text
WHITE  = {'red': 1.0,   'green': 1.0,   'blue': 1.0}
# ── Backgrounds / Decorative ────────────────────────
DKBLUE = {'red': 0.102, 'green': 0.122, 'blue': 0.710}   # decorative on blue bg
LTBG   = {'red': 0.957, 'green': 0.961, 'blue': 0.973}   # #F4F5F8 — light card bg
LTPINK = {'red': 1.0,   'green': 0.96,  'blue': 0.97}    # gap/risk card bg
LTCYAN = {'red': 0.92,  'green': 0.97,  'blue': 0.99}    # diagram fills
LTGREEN= {'red': 0.93,  'green': 0.98,  'blue': 0.94}    # success card bg
# ── Status accents ───────────────────────────────────
GREEN  = {'red': 0.086, 'green': 0.639, 'blue': 0.290}
ORANGE = {'red': 0.918, 'green': 0.345, 'blue': 0.047}

INCH = 914400
SW = int(10.0 * INCH); SH = int(5.625 * INCH)
def emu(inches): return int(inches * INCH)
M = 0.5; CW = 2.85; GAP = 0.225
```

#### Required Helper Functions (copy exactly from v8)
- `shape(oid, pid, l, t, w, h, fill, stype='RECTANGLE')` — creates shape + removes outline
- `richtext(oid, pid, l, t, w, h, runs, align='START', valign='TOP')` — multi-run styled text box
- `simple_text(oid, pid, l, t, w, h, text, sz=12, bold=False, color=None, align='START')` — single-run text
- `new_slide(sid)` — creates blank slide from template
- `pill(oid, pid, l, t, text, bg=None, tc=None)` — colored pill label (1.8" × 0.24")
- `kpi_card(oid, pid, l, t, w, h, value, label, accent=BLUE, bg=LTGRAY)` — metric card with accent top bar
- `insight_card(oid, pid, l, t, w, h, label, title, body, accent, bg)` — insight with accent bar + label + title + body
- `action_card(oid, pid, l, t, w, h, num, title, desc, owner, timeline)` — numbered action item with blue accent
- `sheets_chart(oid, pid, spreadsheet_id, chart_id, l, t, w, h)` — embed linked Sheets chart
- `feature_card(oid, pid, l, t, w, h, name, detail, status, accent, bg=LTGRAY)` — feature status card

#### Data Transformation
Transform raw query results into sheet-ready format:
- **MAU**: `[[month_str, int(mau)], ...]`
- **Stickiness**: `[[month_str, round(ratio * 100, 1)], ...]`
- **Sessions**: `[[month_str, round(avg_dur, 1), round(median_dur, 1)], ...]`
- **Tiers**: Pivot from row-per-tier to `[[month, power, regular, light], ...]` (exclude Dormant)
- **Retention**: `[[month, round(ret_pct, 1)], ...]` (skip None values)
- **Feature Quadrant**: `[[feature_name, int(unique_users), round(avg_events, 1)], ...]`
- **Feature Trends**: Pivot from row-per-feature to `[[month, feat1_users, feat2_users, ...], ...]`

Compute summary stats: `avg_mau`, `latest_mau`, `avg_stk`, `avg_dur` for chart subtitles.

#### Google Sheet Creation
Create a Google Sheet titled `{Customer} × Atlan — EBR Data` with 7 tabs:
1. **MAU** — headers: `Month, MAU`
2. **Stickiness** — headers: `Month, DAU/MAU %`
3. **Sessions** — headers: `Month, Avg Duration (min), Median Duration (min)`
4. **Tiers** — headers: `Month, Power, Regular, Light`
5. **Retention** — headers: `Month, Retention %`
6. **Feature Quadrant** — headers: `Feature, Unique Users, Avg Events/User`
7. **Feature Trends** — headers: `Month, {feature1}, {feature2}, ...`

Create 6 embedded charts (chartId 1-6):
1. **MAU Line** (chartId=1) — line chart with data labels, BLUE line, 3px width
2. **Stickiness Bar** (chartId=2) — column chart, BLUE bars, data labels above
3. **Session Duration** (chartId=3) — grouped column (avg=BLUE, median=CYAN)
4. **Engagement Tiers** (chartId=4) — stacked column (Power=BLUE, Regular=CYAN, Light=GRAY)
5. **Retention Bar** (chartId=5) — column chart, BLUE bars, data labels
6. **Feature Trends Lines** (chartId=6) — multi-line (5 features, colors: BLUE, CYAN, GREEN, ORANGE, PINK)

All charts use `Space Grotesk` font. Share sheet with `anyone: reader`.

#### Google Slides Deck
Copy template `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`, delete existing slides. Build 12 slides minimum:

**Slide 1: Title** — Full `BLUE` background with decorative ellipses, cyan separator line
- Header: `EXECUTIVE BUSINESS REVIEW` (10pt, muted purple)
- Main: `{Customer} × Atlan` (52pt, WHITE, bold)
- Subtitle: `Platform Adoption & Engagement Analytics` + date range
- Footer: `CONFIDENTIAL · PREPARED FOR {audience}`

**Slide 2: Partnership Overview** — White background, blue accent bar at top
- 3 KPI cards: Renewal Date, Latest MAU, ARR (if provided)
- Strategic goals block (from intel or `[CUSTOMIZE]` placeholders)
- Key contacts (from intel or `[CUSTOMIZE]`)

**Slide 3: Supply Landscape** (if supply metrics enabled) — What's in the catalog
- Left panel (BLUE bg): headline stats — connector count, total assets, key enrichment %
- Right side: top 3 connector cards with real asset counts (from `SUPPLY_CONNECTORS`)
- Bottom insight bar: frame supply strength or gap based on enrichment %
- **Use `styled_element()` for multi-styled text** (see Safe Text Styling below)

**Slide 4: Where We Stand** — Two-column honest assessment
- Left: "DELIVERING VALUE" — 5 strength cards (BLUE accent, LTGRAY bg)
- Right: "GAPS TO ADDRESS" — 5 gap cards (PINK accent, LTPINK bg)
- Bottom truth bar summarizing the state
- Content from data analysis (auto-derive from metrics AND supply enrichment data) or intel

**Slide 4: MAU Trend** — Full-width Sheets chart (chartId=1)
- ADOPTION pill, title, subtitle with stats
- `sheets_chart()` at `emu(0.2), emu(1.15), emu(9.6), emu(3.9)`

**Slide 5: Engagement** — Side-by-side Sheets charts
- Left: Stickiness chart (chartId=2) at `emu(0.1), emu(1.15), emu(4.9), emu(4.1)`
- Right: Session Duration chart (chartId=3) at `emu(5.1), emu(1.15), emu(4.9), emu(4.1)`

**Slide 6: Engagement Tiers** — Blue left panel + chart right
- Left panel: `shape(... 0, 0, emu(3.4), SH, BLUE)` with tier definitions
- Right: Tiers chart (chartId=4) at `emu(3.7), emu(0.3), emu(6.1), emu(5.0)`

**Slide 7: Feature Trends** — Chart + insight cards
- Left: Feature trends chart (chartId=6) at `emu(0.1), emu(0.95), emu(6.0), emu(4.3)`
- Right: 3 insight cards stacked (auto-derive from data or use intel)

**Slide 8: Retention** — Full-width retention chart (chartId=5)
- ORANGE accent bar (not blue), orange pill
- Chart at `emu(0.2), emu(1.15), emu(9.6), emu(4.2)`

**Slide 9: 90-Day Plan** — 2×2 action card grid
- 4 `action_card()` elements with numbered circles
- Content from intel or `[CUSTOMIZE]` placeholders

**Slide 10: Investment** — 3 unit economics cards + bottom insight bar
- Cards: Annual Investment, Per Asset cost, Per Active User cost
- Dark bottom bar with positioning statement

**Slide 11: Executive Summary** — Problem/Solution/Ask triptych
- 3 cards side-by-side with colored header pills
- Designed as leave-behind for internal stakeholders

**Slide 12: Close** — Full `BLUE` background matching title slide
- Bold statement + 3 asks
- Next steps card with owner + timeline

#### Safe Text Styling (REQUIRED for multi-styled text)

**NEVER hardcode character indices** for text styling — this causes off-by-one errors that produce garbled font sizes. Always use the `styled_element()` pattern that computes indices from segments automatically:

```python
def styled_element(oid, segments):
    """Build text from segments, auto-computing indices.
    Each segment: (text, sz, bold, color). Returns ops list."""
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

**Usage** — define text as styled segments, indices computed automatically:
```python
reqs += styled_element('s3_ltxt', [
    ("SUPPLY",           10, True,  CYAN),
    ("\n\n",              6, None,  WHITE),
    ("What\u2019s in the\nCatalog", 20, True, WHITE),
    ("\n\n",              6, None,  WHITE),
    ("8",                48, True,  CYAN),
    ("\n",                6, None,  WHITE),
    ("active connectors", 12, False, WHITE),
])
```

Use `styled_element()` for: supply landscape left panel, connector cards, insight bars, KPI cards, gap zone text — any element with mixed font sizes or styles.

#### Supply Metrics on Slides

When supply data is available, use it to populate:
- **Supply slide**: connector count, total assets, top 3 connectors with asset counts, enrichment %
- **Gap slide**: reframe from "missing connectors" to "catalog depth gaps" (tagging %, lineage %, terms %, governance coverage)
- **Before/After**: use real enrichment baselines as "before", target % as "after"
- **Roadmap Phase 1**: "Deepen Catalog" (tagging, lineage, owners) instead of "Expand Supply" — unless the customer genuinely has few connectors
- **KPI cards**: real connector count and enrichment baselines
- **Investment slide**: cost per asset, total catalog size

**Supply narrative decision tree**:
- If connectors >= 5 AND total assets > 100K → frame as "strong supply, deepen quality"
- If connectors < 5 OR total assets < 50K → frame as "expand supply + connect more sources"
- If PCT_LINEAGE > 50% → "lineage is a strength"
- If PCT_DESCRIPTIONS < 30% → "description coverage is a gap"
- If PCT_TERMS < 10% → "glossary adoption is low"

#### Execution
- Batch API requests in groups of 350
- Sleep 8 seconds between batches
- Object IDs must be >= 5 characters (e.g., `slide_01`, not `s01`)

### Step 3: Run the Script

```bash
python3 /tmp/build_ebr_{domain_prefix}.py
```

### Step 4: Return Results

Present to the user:
- **Deck URL**: `https://docs.google.com/presentation/d/{PRES_ID}/edit`
- **Data Sheet URL**: `https://docs.google.com/spreadsheets/d/{SS_ID}/edit`
- **Summary**: Slide count, chart count, data coverage period

## Content Guidelines

### Auto-derived Insights (from data)
Analyze the query results to generate contextual content:
- If MAU is declining >10%: flag in "Gaps to Address"
- If stickiness >15%: highlight as "above industry benchmark (5-15%)"
- If stickiness <10%: flag as episodic usage concern
- If retention <60%: highlight as onboarding/engagement opportunity
- Feature with highest unique users = "Core Strength"
- Feature with fastest growth = "Momentum"
- Feature with declining trend = "Discussion" topic

### Intel-driven Content (from user context)
When competitive threats, quotes, or strategic context are provided:
- Add a Competitive Landscape slide (slide 9 in v8) with grouped bar chart
- Include champion quotes in relevant slides
- Customize the close slide asks to match actual next steps
- Add ZDR/compliance slide if AI governance is relevant

### Placeholder Content
For slides requiring narrative that wasn't provided, use `[CUSTOMIZE]` markers:
```
[CUSTOMIZE: Add customer's strategic goals here]
[CUSTOMIZE: Replace with specific competitive positioning]
```

## Dependencies
- Google OAuth token at `/tmp/google_slides_token.pickle` with scopes: slides, drive, sheets
- Python packages: `google-api-python-client`, `google-auth`
- Snowflake MCP tool: `mcp__snowflake__run_snowflake_query`
- Slides template: `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`
