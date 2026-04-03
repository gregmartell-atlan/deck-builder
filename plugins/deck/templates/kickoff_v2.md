# Kickoff v2 — Partnership Kick-Off Template

**Source deck**: `1fSuVLCPDMCDG9piDcyn4YLG7BymcMTMmDVqSLUWXJuo`
**Title**: Atlan // Eaton / Partnership Kick-Off ~ 4.3.26
**Slides**: 21
**Raw JSON**: `kickoff_v2_raw.json` (same directory)
**Supersedes**: Kickoff v1 (`1jk9zawbJIfwiWlEVYmXrsSf4WVS0IeBEClXs7UXzjFA`, 19 slides)

---

## Color Palette

| Name      | RGB Dict                                            | Hex     | Usage                        |
|-----------|-----------------------------------------------------|---------|------------------------------|
| BLUE      | `{red:0.125, green:0.149, blue:0.824}`              | #2026D2 | Primary brand, dark bgs      |
| DKBLUE    | `{red:0.102, green:0.122, blue:0.71}`               | #1A1FB5 | Decorative ellipses          |
| CYAN      | `{red:0.384, green:0.882, blue:0.988}`              | #62E1FC | Accent, pills, numbers       |
| TEAL      | `{green:0.769, blue:0.549}`                         | #00C48C | Phase dots, milestone diamonds|
| PURPLE    | `{red:0.608, green:0.498, blue:1.0}`                | #9B7FFF | Team accent, phase color     |
| PINK      | `{red:0.953, green:0.302, blue:0.467}`              | #F34D77 | Alerts, scale phase          |
| CORAL     | `{red:1.0, green:0.42, blue:0.29}`                  | #FF6B4A | Phase 1 accent               |
| DARK      | `{red:0.169, green:0.169, blue:0.224}`              | #2B2B39 | Body text                    |
| GRAY      | `{red:0.451, green:0.451, blue:0.588}`              | #737396 | Secondary text               |
| LTBG      | `{red:0.957, green:0.961, blue:0.973}`              | #F4F5F8 | Grid lines, separators       |
| WHITE     | `{red:1.0, green:1.0, blue:1.0}`                    | #FFFFFF | Light slide backgrounds      |

**Font**: Space Grotesk (all text)

---

## Slide Inventory

### Slide 0: Title (Dark) — `sl_title`
**Layout**: Dark blue full-bleed + 3 decorative ellipses
**Elements**: 9
- `s1_bg` — RECTANGLE fill=BLUE (full slide)
- `s1_e1`, `s1_e2`, `s1_e3` — ELLIPSE fill=DKBLUE (decorative)
- `s1_sep` — RECTANGLE fill=CYAN (thin separator at y=2.0)
- `s1_hdr` — TEXT_BOX "PARTNERSHIP KICK-OFF" 10pt CYAN
- `s1_title` — TEXT_BOX "{Customer}" 48pt WHITE
- `s1_sub` — TEXT_BOX subtitle 16pt WHITE
- `s1_date` — TEXT_BOX date 10pt WHITE

**Data inputs**: `customer_name`, `subtitle`, `date_str`
**Maps to**: Template 1 (Title Slide Dark)

---

### Slide 1: Agenda (Dark) — `sl_agenda`
**Layout**: Dark blue bg + 6 numbered agenda items in 2x3 grid
**Elements**: 22
- `s2_bg` — RECTANGLE fill=BLUE
- `s2_e1` — ELLIPSE fill=DKBLUE (decorative)
- `s2_hdr` — "TODAY'S AGENDA" 10pt CYAN
- `s2_title` — "60 Minutes to Align, Plan, and Launch" 28pt WHITE
- Per item (x6): `s2_agN` (RECTANGLE fill=DKBLUE) + `s2_agN_n` (ELLIPSE fill=CYAN, number 14pt) + `s2_agN_t` (TEXT_BOX title bold 11pt + desc 11pt, WHITE)
- Grid: 2 columns (x=0.5, x=5.1), 3 rows (y=1.65, y=2.8, y=3.95)
- Card size: ~4.3" wide x 0.95" tall

**Data inputs**: `agenda_items` — list of `(title, description)` tuples (6 items)
**Maps to**: New — "Agenda 2x3 Grid (Dark)"

---

### Slide 2: Team — `sl_team`
**Layout**: Light bg with pill header + team member cards in horizontal row
**Elements**: 31 (variable by team size)
- `s3_pill` — ROUND_RECTANGLE fill=BLUE "YOUR ATLAN TEAM" 10pt
- `s3_title` — 20pt DARK
- `s3_sub` — 11pt GRAY
- Per team member: `_bar` (RECTANGLE, accent color) + avatar image or initials circle + `_n` (name 12pt) + `_r` (role 9pt, accent color) + `_d` (description 9pt GRAY)
- Team members spaced ~1.74" apart starting x=0.508
- `s3_ext` — extended team text 9pt GRAY at bottom

**Data inputs**: `team_members` — list of `(name, role, description, accent_color, avatar_url_or_initials)`, `extended_team_text`
**Accent rotation**: BLUE, CYAN, TEAL, PURPLE, themeColor ACCENT5
**Maps to**: New — "Team Cards (Horizontal)"

---

### Slide 3: Section Divider (Dark) — `sl_sec_journey`
**Layout**: Dark blue full-bleed + 2 decorative ellipses + large number + title + desc
**Elements**: 6
- `sj_bg` — RECTANGLE fill=BLUE
- `sj_e1`, `sj_e2` — ELLIPSE fill=DKBLUE
- `sj_num` — 72pt CYAN (e.g. "01")
- `sj_tt` — 28pt WHITE
- `sj_dd` — 12pt CYAN

**Data inputs**: `section_number`, `section_title`, `section_description`
**Maps to**: Template 2 (Section Divider Dark)

---

### Slide 4: Journey S-Curve — `g3dcf11e6b19_1_0`
**Layout**: Complex infographic with S-curve path, phase dots, QBR markers, phase legend
**Elements**: 59 (images, lines, shapes, text)
- Title: "The Journey to Sustainable Business Value" 20pt DARK
- S-curve rendered as connected ELLIPSE dots with text callouts along the path
- QBR markers: "QBR 1/2/3" with metric descriptions
- Phase legend at bottom: 4 colored rectangles + labels
  - CORAL: "Kickoff & Planning [WEEK 1]"
  - BLUE: "Integration & Migration [WEEKS 2-4]"
  - TEAL: "Build & Enrich [MONTHS 2-3]"
  - PURPLE: "Rollout & Scale [MONTHS 3-6]"

**Data inputs**: `phases` (name, timeframe, color), `curve_callouts`, `qbr_metrics`
**Note**: This slide has matplotlib-generated curve images. When building from scratch, use `matplotlib` to render the S-curve path as PNG, then overlay with native Slides text.
**Maps to**: Variant of Journey Curve (existing kickoff template)

---

### Slide 5: Rollout Overview — `sl_rollout_intel`
**Layout**: Phase-based swim lane timeline with milestones, groups, and description cards
**Elements**: 51
- `ri_title` — 20pt DARK
- `ri_year` — pill BLUE "FY 2026"
- `ri_mbar` — RECTANGLE fill=BLUE (month header bar)
- `ri_mh0-4` — 5 month/phase headers in bar (7pt WHITE bold)
- `ri_vg1-4` — vertical grid lines (LTBG)
- `ri_ml0-4_dia` + `ri_ml0-4_lb` — DIAMOND milestones (TEAL) with labels
- `ri_dgrp0-3`, `ri_bgrp0-3` — grouped bar elements (solid + ghost phases)
- `ri_cm_bar` — "Change Management" bar (BLUE, rounded)
- `ri_sc_bar` — "Scale to Other Domains" bar (PINK, rounded)
- `ri_cd0-3` — description cards: dot + title (8pt bold, accent) + desc (7pt GRAY)
- `ri_foot` — footnote 7pt GRAY
- `ri_may1_line` + `ri_may1_lbl` — date marker

**Data inputs**: `phases` (name, months), `milestones`, `swim_lanes` (bars), `description_cards`, `cross_cutting_bars`
**Maps to**: New — "Rollout Swim Lane Timeline"

---

### Slide 6: Section Divider — `sl_sec1`
**Layout**: Same as Slide 3 pattern
**Data inputs**: `section_number="01"`, `title="Where We Stand"`, `desc`

---

### Slide 7: OKR Cards — `sl_okrs`
**Layout**: Pill header + 3 large metric cards + footer bar
**Elements**: 24
- `s6_pill` — "CDO VISION" pill
- `s6_title` — 20pt DARK
- `s6_sub` — 11pt GRAY
- Per OKR (x3): `_okr` (bg RECTANGLE) + `_top` (accent bar) + `_tag` (pill "OKR N") + `_val` (large value 36pt) + `_t` (title 14pt) + `_d` (desc 11pt)
- Cards distributed evenly across width
- `s6_ftbar` + `s6_ftacc` + `s6_ft` — bottom insight bar

**Data inputs**: `okrs` — list of `(tag, value, title, description, accent_color)`
**Maps to**: Variant of Template 8 (Big Stats Row) with card wrapper

---

### Slide 8: Driving Factors 4-Quadrant — `sl_factors_v2`
**Layout**: Pill header + 4 quadrant cards in 2x2 grid
**Elements**: 18
- `sfact_pill` — "DRIVING FACTORS"
- `sfact_title` — 20pt DARK
- Per quadrant (x4): `_q` (bg RECTANGLE) + `_bar` (top accent, 4 different colors) + `_tt` (title 11pt bold) + `_it` (bullet list 9pt)
- Grid: 2 columns x 2 rows

**Data inputs**: `quadrants` — list of `(title, bullet_items, accent_color)`
**Maps to**: Template 5 (Challenge Slide) adapted to 4-quadrant

---

### Slide 9: Driving Factors Matrix — `sl_factors_matrix`
**Layout**: 3-column x 4-row matrix with colored column headers and row labels
**Elements**: 46
- `fm_pill` — "DRIVING FACTORS"
- `fm_title` — 20pt DARK
- `fm_ch0-2` — column headers (bold, colored bg)
- Per row (x4): `_rl` (bg) + `_bar` (accent) + `_txt` (row label) + per cell: `_c` (bg) + `_txt` (content 9pt)
- `fm_strip0-3` — row separator strips
- `fm_foot` — source footnote

**Data inputs**: `columns` (headers), `rows` (label + cells), `source_text`
**Maps to**: New — "Matrix Grid (Colored Headers)"

---

### Slide 10: Domain Prioritization Bubble Chart — `g3dd093511a3_7_0`
**Layout**: 2-axis scatter plot with domain bubbles + ranking sidebar
**Elements**: 37
- Title pill "DOMAIN PRIORITIZATION"
- Axes: "Viability" (x) and "Value" (y) with gridlines at 0.2 intervals
- "HIGH VALUE HIGH VIABILITY" quadrant label
- Domain bubbles: colored circles positioned on grid
- Ranking cards on right: numbered items with descriptions

**Data inputs**: `domains` (name, viability_score, value_score, color, description)
**Maps to**: New — "Bubble Scatter Plot with Rankings"

---

### Slide 11: Supply & Demand — `sl_supply_v2`
**Layout**: Pill header + matplotlib chart image + insight bar at bottom
**Elements**: 6
- `supdem_pill` — pill
- `supdem_title` — 20pt
- `supdem_img` — matplotlib-generated supply/demand chart (inserted image)
- `supdem_bar` + `supdem_acc` + `supdem_txt` — bottom insight bar

**Data inputs**: Supply/demand chart data, `insight_text`
**Note**: Requires matplotlib to generate chart PNG
**Maps to**: Image + Insight Bar pattern

---

### Slide 12: Implementation Timeline (Staggered) — `g3dd093511a3_2_0`
**Layout**: Staggered bar timeline with milestones and description cards
**Elements**: 51
- Title pill "IMPLEMENTATION ROADMAP"
- Month headers: APR, MAY, JUN, JUL
- Staggered bars with bar names (4 workstreams)
- Diamond milestones with labels and dates
- Description cards below with colored dots

**Data inputs**: `months`, `bars` (name, start, end, color), `milestones`, `description_cards`
**Maps to**: Template 18 (Staggered Bar Timeline) — use `timeline_staggered()`

---

### Slide 13: Connector Integration Timeline — `sl_integ_stag2`
**Layout**: Detailed connector onboarding Gantt with phase grouping
**Elements**: 113
- Pill "CONNECTOR ONBOARDING"
- Month headers with grid lines
- Per connector: ghost bar + solid bar + left/right circle endpoints + diamond milestone + name label
- Phase 1 (7 connectors) + separator + Phase 2 (4 connectors)
- Milestone diamonds at bottom
- "TO BE CONFIRMED" callout box

**Data inputs**: `connectors` (name, phase, start_month, end_month, confirmed), `milestones`
**Maps to**: New — "Connector Gantt Chart"

---

### Slide 14: First 30 Days Sprint — `sl_30day`
**Layout**: Pill header + 4 week cards with arrows between them
**Elements**: 33
- `s13_pill` — "FIRST 30 DAYS"
- `s13_title` — 20pt
- Per week (x4): `_wk` (bg RECTANGLE) + `_top` (accent bar) + `_hdr` (colored header) + `_wk` (week label) + `_ph` (phase name) + `_items` (bullet list) + `_own` (owners)
- `s13_arr0-2` — RIGHT_ARROW shapes between cards

**Data inputs**: `weeks` — list of `(week_label, phase_name, bullet_items, owners, accent_color)`
**Maps to**: Variant of Template 13 (Phased Plan) — use `phase_card()` x4

---

### Slide 15: Section Divider — `sl_sec2`
**Layout**: Same as Slide 3 pattern
**Data inputs**: `section_number="02"`, `title="Making It Real"`, `desc`

---

### Slide 16: Migration Table — `sl_migration2`
**Layout**: Pill header + native table (6x5) + callout bar
**Elements**: 7
- `mig_pill` — "ALATION MIGRATION"
- `mig_title` — 20pt
- `mig_sub` — 11pt GRAY
- `mig_tbl` — native table 6 rows x 5 columns
- `mig_callout` + `mig_cbar` + `mig_ctxt` — colored callout bar at bottom

**Data inputs**: `table_data` (6x5), `callout_text`
**Maps to**: Template 9 (Table Slide) + callout bar — use `build_table()`

---

### Slide 17: Risks & Mitigations Table — `sl_risks2`
**Layout**: Pill header + native table (5x4) + insight bar
**Elements**: 6
- `risk_pill` — "RISK MANAGEMENT"
- `risk_title` — 20pt
- `risk_tbl` — native table 5 rows x 4 columns
- `risk_bar` + `risk_baracc` + `risk_bartxt` — bottom bar with protocol text

**Data inputs**: `risks_table` (5x4), `protocol_text`
**Maps to**: Template 12 (Risk & Mitigation Table) — use `build_table()`

---

### Slide 18: Engagement Model — `sl_engage`
**Layout**: Pill header + 4 engagement cards (vertical stack, 2x2)
**Elements**: 22
- `s15_pill` — "WAYS OF WORKING"
- `s15_title` — 20pt
- Per engagement (x4): `_eng` (bg) + `_bar` (accent) + `_t` (title bold) + `_c` (cadence BLUE) + `_d` (description with attendees)

**Data inputs**: `engagements` — list of `(title, cadence, description_with_attendees)`
**Maps to**: Variant of insight_card() layout

---

### Slide 19: Success Metrics Table — `sl_metrics2`
**Layout**: Pill header + native table (6x5) + footer bar + quote
**Elements**: 7
- `met_pill` — "SUCCESS METRICS"
- `met_title` — 20pt
- `met_tbl` — native table 6 rows x 5 columns
- `met_ftbar` + `met_ftacc` + `met_fttxt` — footer bar
- `met_quote` — attribution quote at bottom

**Data inputs**: `metrics_table` (6x5), `footer_text`, `quote_text`
**Maps to**: Template 9 (Table Slide) + quote — use `build_table()`

---

### Slide 20: Close (Dark) — `sl_close`
**Layout**: Dark blue bg + 3 numbered next steps + bottom bar
**Elements**: 14
- `s19_bg` — RECTANGLE fill=BLUE
- `s19_e1`, `s19_e2` — ELLIPSE fill=DKBLUE (decorative)
- `s19_title` — 28pt WHITE
- `s19_sep` — thin separator
- Per step (x3): `s19_nN` (number in ELLIPSE fill=CYAN) + `s19_nsN` (step text, bold title + desc)
- `s19_nsbox` + `s19_nsacc` + `s19_nst` — bottom callout bar

**Data inputs**: `closing_title`, `next_steps` — list of `(title, description)`, `next_touchpoint_text`
**Maps to**: Template 10 (Close Slide Dark) + numbered steps

---

## Full Build Sequence

```
sl_title           → Title (Dark) — Template 1
sl_agenda          → Agenda 2x3 Grid (Dark) — NEW
sl_team            → Team Cards (Horizontal) — NEW
sl_sec_journey     → Section Divider (Dark) — Template 2
journey_curve      → Journey S-Curve — matplotlib + shapes
sl_rollout_intel   → Rollout Swim Lane — NEW
sl_sec1            → Section Divider (Dark) — Template 2
sl_okrs            → OKR Cards — variant of Template 8
sl_factors_v2      → 4-Quadrant (2x2) — variant of Template 5
sl_factors_matrix  → Matrix Grid — NEW
domain_bubble      → Bubble Scatter — NEW
sl_supply_v2       → Image + Insight Bar — matplotlib
timeline_impl      → Staggered Timeline — Template 18
sl_integ_stag2     → Connector Gantt — NEW
sl_30day           → Sprint Cards (4-week) — variant of Template 13
sl_sec2            → Section Divider (Dark) — Template 2
sl_migration2      → Table + Callout — Template 9
sl_risks2          → Risk Table — Template 12
sl_engage          → Engagement Cards — NEW
sl_metrics2        → Metrics Table + Quote — Template 9
sl_close           → Close (Dark) — Template 10
```

## New Templates Introduced

These slide patterns are new to the engine and need template functions:

1. **Agenda 2x3 Grid (Dark)** — 6-item numbered agenda on dark bg
2. **Team Cards (Horizontal)** — 4-6 team members with accent bars + avatars
3. **Rollout Swim Lane Timeline** — phased swim lanes with milestones + descriptions
4. **Matrix Grid (Colored Headers)** — N-column x M-row matrix
5. **Bubble Scatter Plot** — 2-axis with positioned circles + ranking sidebar
6. **Connector Gantt Chart** — per-item bars with phase grouping
7. **Engagement Cards** — cadence-based engagement items

## Reused Templates

These map directly to existing engine templates:

- Title Dark → Template 1
- Section Divider → Template 2
- OKR Cards → Template 8 variant (Big Stats)
- Sprint Cards → Template 13 (Phased Plan)
- Table slides → Template 9 (build_table)
- Risk table → Template 12
- Staggered timeline → Template 18 (timeline_staggered)
- Close Dark → Template 10
