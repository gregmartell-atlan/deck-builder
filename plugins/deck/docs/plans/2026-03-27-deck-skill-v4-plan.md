# Deck Skill v4.0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the deck skill so every deck is built on customer intel, uses the engine for all code, and produces 0 healing issues.

**Architecture:** SKILL.md becomes a pure strategic playbook (~1100 lines, zero inline Python). core.py is the single source of truth for all execution code (~1850 lines). A mandatory intel brief gate forces intelligence gathering before any build script is generated.

**Tech Stack:** Python 3.8+, Google Slides/Drive/Sheets APIs, Snowflake MCP, Slack/Glean/Gong MCP tools

---

### Task 1: Fix Engine Bugs — benefit_card() and Validator

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/engine/core.py:814-845` (benefit_card)
- Modify: `~/.claude/local-plugins/plugins/deck/engine/core.py:1290-1301` (_check_outline)
- Modify: `~/.claude/local-plugins/plugins/deck/engine/core.py:1377-1392` (_check_numbers)

- [ ] **Step 1: Fix benefit_card() — replace bordered() with shape()**

Replace the `bordered()` call at line 830 with `shape()` using `ROUND_RECTANGLE`:

```python
def benefit_card(oid, pid, l, t, w, h, tag, title, body, footnote,
                 accent, bg=None):
    """4-layer benefit card: tag + title + body + footnote.

    Modeled on the Zoom v4 "What This Means" slide — each card explains
    one customer benefit with context.

    Layout (left accent bar + 4 text zones):
        ┌──────────────────────────┐
        │ TAG            (10pt bold, accent)
        │ Title          (14pt bold, DARK)
        │ Body text      (11pt, GRAY)
        │ Footnote       (10pt, GRAY)
        └──────────────────────────┘
    """
    bg = bg or WHITE
    shape(oid, pid, l, t, w, h, bg, 'ROUND_RECTANGLE')
    shape(oid + '_bar', pid, l, t, emu(0.04), h, accent)
    # Tag
    textbox(oid + '_tag', pid, l + emu(0.18), t + emu(0.10),
            w - emu(0.3), emu(0.20),
            [(tag, 10, True, accent)], 'START')
    # Title
    textbox(oid + '_t', pid, l + emu(0.18), t + emu(0.32),
            w - emu(0.3), emu(0.30),
            [(title, 14, True, DARK)], 'START')
    # Body
    textbox(oid + '_b', pid, l + emu(0.18), t + emu(0.65),
            w - emu(0.3), h - emu(1.05),
            [(body, TYPE_SCALE['body'], False, GRAY)], 'START', 'TOP')
    # Footnote
    if footnote:
        textbox(oid + '_fn', pid, l + emu(0.18), t + h - emu(0.30),
                w - emu(0.3), emu(0.20),
                [(footnote, 10, False, GRAY)], 'START')
```

- [ ] **Step 2: Update Validator _check_outline() to skip intentional borders**

The Validator should not flag shapes created by `bordered()` or `dashed()` — those have intentional outlines. Add detection by checking if the outline has both fill AND weight set (indicating an intentional border, not a default):

```python
    def _check_outline(self, idx, oid, el):
        if _el_shape_type(el) == 'TEXT_BOX':
            return
        # Skip shapes with intentional borders (bordered/dashed helpers)
        # These have outline fill + weight explicitly set
        props = el.get('shape', {}).get('shapeProperties', {})
        outline = props.get('outline', {})
        has_fill = 'outlineFill' in outline
        has_weight = 'weight' in outline
        if has_fill and has_weight:
            return  # Intentional border — not a bug
        if _el_outline_rendered(el):
            self.issues.append(Issue(
                idx, oid, 'outline', 'error',
                'Shape has visible outline (should be NOT_RENDERED)',
                fix={'updateShapeProperties': {
                    'objectId': oid,
                    'fields': 'outline.propertyState',
                    'shapeProperties': {
                        'outline': {'propertyState': 'NOT_RENDERED'}}}}))
```

- [ ] **Step 3: Add NOISE_NUMBERS to Validator _check_numbers()**

Years, small contextual numbers, and common formatting numbers should not trigger warnings:

```python
    # Class-level constant on Validator
    NOISE_NUMBERS = (
        set(range(2020, 2031))  # years
        | set(range(0, 100))     # small numbers (percentages, counts)
        | {500, 840}             # common narrative numbers
    )

    def _check_numbers(self, idx, oid, el):
        text = _el_text(el)
        if not text:
            return
        deal_values = set(_flatten_deal(self.deal).values())
        for num in _extract_numbers_from_text(text):
            if num in self.NOISE_NUMBERS:
                continue
            matched = any(
                abs(num - dv) <= abs(dv) * 0.01
                for dv in deal_values if dv != 0)
            if not matched and num > 100:
                self.issues.append(Issue(
                    idx, oid, 'number', 'warning',
                    f'Number {num:,.0f} not found in DEAL dict'
                    ' -- verify correctness'))
```

- [ ] **Step 4: Test engine fixes**

Run the existing test to verify benefit_card no longer uses bordered():

```bash
cd ~/.claude/local-plugins/plugins/deck && python3 -c "
import sys; sys.path.insert(0, 'engine')
from core import *

# Test benefit_card doesn't produce bordered shapes
reqs.clear()
benefit_card('test_bc', 'test_pg', emu(0.5), emu(1.0), emu(4.25), emu(1.6),
             'CONNECTORS', 'Unlimited Connectors',
             'Your 5 connectors are no longer a ceiling.',
             'Currently: 5 connectors on contract', EMERALD)
# Check no bordered() requests exist (no outlineFill in any request)
outline_reqs = [r for r in reqs if 'outlineFill' in str(r)]
assert len(outline_reqs) == 0, f'benefit_card still produces outlines: {len(outline_reqs)} found'
print('OK: benefit_card produces 0 outline requests')

# Test Validator skips intentional borders
reqs.clear()
bordered('test_brd', 'test_pg', emu(0.5), emu(1.0), emu(2.0), emu(1.0), WHITE, BLUE, 1.0)
# Mock a presentation with this bordered shape
mock_el = {
    'objectId': 'test_brd',
    'shape': {
        'shapeType': 'RECTANGLE',
        'shapeProperties': {
            'outline': {
                'outlineFill': {'solidFill': {'color': {'rgbColor': BLUE}}},
                'weight': {'magnitude': 1.0, 'unit': 'PT'},
            }
        },
        'text': {'textElements': []},
    },
    'size': {'width': {'magnitude': emu(2.0)}, 'height': {'magnitude': emu(1.0)}},
}
mock_pres = {'slides': [{'objectId': 's1', 'pageElements': [mock_el]}]}
v = Validator(mock_pres)
issues = v.run_all()
outline_issues = [i for i in issues if i.category == 'outline']
assert len(outline_issues) == 0, f'Validator flagged intentional border: {outline_issues}'
print('OK: Validator skips intentional borders')

# Test noise numbers
mock_el2 = {
    'objectId': 'test_year',
    'shape': {
        'shapeType': 'TEXT_BOX',
        'shapeProperties': {},
        'text': {'textElements': [
            {'textRun': {'content': 'March 2026', 'style': {'fontFamily': 'Space Grotesk'}}}
        ]},
    },
    'size': {'width': {'magnitude': emu(3.0)}, 'height': {'magnitude': emu(0.5)}},
}
mock_pres2 = {'slides': [{'objectId': 's1', 'pageElements': [mock_el2]}]}
v2 = Validator(mock_pres2, deal={'price': 329_898})
issues2 = v2.run_all()
number_issues = [i for i in issues2 if i.category == 'number']
assert len(number_issues) == 0, f'Validator flagged year number: {number_issues}'
print('OK: Validator skips noise numbers (years)')

print()
print('ALL ENGINE FIX TESTS PASSED')
"
```

Expected: All 3 assertions pass.

- [ ] **Step 5: Commit engine fixes**

```bash
cd ~/.claude/local-plugins/plugins/deck
git add engine/core.py
git commit -m "fix(engine): benefit_card uses shape() not bordered(), validator skips intentional outlines and noise numbers"
```

---

### Task 2: Archive Old SKILL.md

**Files:**
- Move: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` → `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.v3.1.md`

- [ ] **Step 1: Copy old skill to archive**

```bash
cp ~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md \
   ~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.v3.1.md
```

- [ ] **Step 2: Verify archive**

```bash
wc -l ~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.v3.1.md
```

Expected: 2053 lines.

- [ ] **Step 3: Commit archive**

```bash
cd ~/.claude/local-plugins/plugins/deck
git add skills/deck/SKILL.v3.1.md
git commit -m "chore: archive SKILL.md v3.1 before rewrite"
```

---

### Task 3: Write SKILL.md v4.0 — §0 Setup and Banner

**Files:**
- Create: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (overwrite)

This task writes the banner, setup, and prerequisites section. The banner is the existing Atlan ASCII art + menu. Setup is trimmed to reference the engine instead of inline code.

- [ ] **Step 1: Write §0 — Banner + Setup + Prerequisites**

Write the new SKILL.md with the banner (reuse existing ASCII art from v3.1), then the trimmed setup section. Key changes from v3.1:
- No inline `get_creds()` code — reference engine
- No inline dependency install code — engine auto-installs
- Pre-flight check simplified (engine handles dep checks)
- Add engine location and import pattern
- Keep the OAuth explanation (important for new users)
- Keep the Claude Desktop / No-Shell workflow
- Keep the timeframes table

The banner section should be identical to v3.1 lines 1-93. Copy it verbatim from `SKILL.v3.1.md`.

Setup should include:

```markdown
## §0 — Prerequisites & Setup

### Engine Module

All build code lives in the engine at `~/.claude/local-plugins/plugins/deck/engine/core.py`. Build scripts import from it:

\```python
import sys, os
sys.path.insert(0, os.path.expanduser(
    '~/.claude/local-plugins/plugins/deck/engine'))
from core import *
\```

This gives access to all helpers (shape, text_in, build_table, etc.), the Grid system, text measurement, validation, self-healing, and build infrastructure (auth, flush, save_context).

**NEVER define helper functions inline in build scripts.** If a function doesn't exist in the engine, add it to core.py — don't duplicate code.
```

Then include the existing OAuth explanation, Claude Desktop workflow, template access, and pre-flight check from v3.1 — but remove all inline Python code blocks for `get_creds()`, `CLIENT_CONFIG`, etc. Replace with: "The engine's `get_creds()` handles all OAuth automatically. See core.py §11 for details."

- [ ] **Step 2: Verify line count so far**

Target: ~150-200 lines for banner + setup.

---

### Task 4: Write SKILL.md v4.0 — §1 Intel Brief Gate

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (append)

- [ ] **Step 1: Write §1 — Intel Brief Gate**

This is the biggest new section. It defines the mandatory intelligence gathering phase.

```markdown
## §1 — Intel Brief Gate

**MANDATORY.** No deck is built without an intel brief. No exceptions.

Before generating any build script, gather intelligence from available sources, synthesize it into a structured brief, and print it for user review. Only proceed after explicit approval.

### Step 1: Search Available Sources

Launch these searches in parallel:

| Source | MCP Tool | What to Find |
|--------|----------|-------------|
| **Slack** | `mcp__claude_ai_Slack__slack_search_public_and_private` | Customer channel threads, pricing feedback, stakeholder reactions, internal deal discussions |
| **Gong/Glean** | `mcp__claude_ai_Glean__search` with `app: "gong"` | Call transcripts with champion/EB, objections raised, competitive mentions |
| **Snowflake** | `mcp__snowflake__run_snowflake_query` | Usage data — assets, MAU, feature adoption, connector count. Use queries from `~/atlan-usage-analytics/sql/` |
| **Granola** | If available | Meeting notes, action items, relationship context |

**If a source returns nothing**, flag it in the brief as `✗ No data found`. This is information — it means we're building on incomplete intel and should flag [CUSTOMIZE] markers for what's missing.

### Step 2: Synthesize Into Brief

Print the brief to terminal using this structure:

\```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  INTEL BRIEF — {Customer Name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  DEAL CONTEXT
  Current ARR: {amount} | Renewal: {date}
  Champion: {name} ({title})
  Exec Sponsor: {name} ({title})
  Competitive Threat: {threat or "None identified"}

  SOURCES CHECKED
  ✓ Slack: {channel} ({N} threads)
  ✓ Glean/Gong: {N} call transcripts
  ✓ Snowflake: {metrics pulled}
  ✗ Granola: {reason for miss}

  KEY FINDINGS
  1. {finding} (source: {Slack/Gong/Snowflake})
  2. {finding} (source: {source})
  3. {finding} (source: {source})

  NARRATIVE STRATEGY
  Frame: "{one-sentence framing}"
  Audience: {who} → {who}
  Hook: {what opens the deck}
  Risk: {what could derail the conversation}

  DEAL NUMBERS
  Opt 1: {price}/yr × {term}yr = {TCV}
  Opt 2: {price}/yr × {term}yr = {TCV}
  Reconciliation: ✓ PASS / ✗ FAIL ({details})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\```

### Step 3: Wait for Approval

After printing the brief, ask:

> "Intel brief ready. Review above and tell me to proceed, or provide corrections/additional context."

**Do NOT generate any build script until the user confirms.**

### Step 4: Save Brief

Save the brief to `/tmp/{customer_slug}_intel_brief.md` for reference during multi-part builds.

### Thin Brief (for non-customer decks)

For generic templates, internal docs, or decks where customer intel isn't available, the brief is shorter:

\```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  BRIEF — {Deck Title}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  PURPOSE: {what this deck is for}
  AUDIENCE: {who will see it}
  NARRATIVE: {key message}
  DEAL NUMBERS: {if applicable}
  Reconciliation: ✓ PASS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
\```
```

---

### Task 5: Write SKILL.md v4.0 — §2 Strategic Debate + §3 Brand Reference

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (append)

- [ ] **Step 1: Write §2 — Strategic Debate**

Copy the existing §2 and §2a from `SKILL.v3.1.md` (lines 840-985) with these changes:
- Remove the "Don't skip this" pleading — the intel brief gate makes it mandatory
- Add: "The debate uses findings from the Intel Brief (§1). If the brief shows thin intel, the debate surfaces what's missing."
- Keep all agent personas (VP CS, CEO/Deal Desk, Objection Anticipator)
- Keep audience mapping, multi-spin architecture, number reconciliation
- Keep the collaborator system (§2a)
- Tighten: remove redundant text, aim for ~120 lines (down from ~150)

- [ ] **Step 2: Write §3 — Brand Reference**

This is a reference-only section. No code. Just the values Claude needs to know:

```markdown
## §3 — Brand Reference

These values are defined as code in `core.py`. This section is a quick reference.

### Colors

| Name | Hex | Usage |
|------|-----|-------|
| BLUE | #2026D2 | Primary, dark slide bg, header fills |
| CYAN | #62E1FC | Accent, separators, highlights |
| PINK | #F34D77 | Accent, alerts |
| DARK | #2B2B39 | Primary text on light bg |
| GRAY | #737396 | Secondary text |
| WHITE | #FFFFFF | Text on dark bg, card bg |
| DKBLUE | — | Decorative ellipses on blue bg |
| LTBG | #F4F5F8 | Light card backgrounds |
| LTCYAN | — | Diagram fills |
| LTPINK | — | Gap/risk card bg |
| LTGREEN | — | Success card bg |
| GREEN | — | Positive status |
| ORANGE | — | Warning/retention |
| CORAL | #FF6B4A | Risk, urgent, Option 1 pill |
| EMERALD | #00C48C | Success, Option 2 pill |
| PURPLE | #9B7FFF | AI/innovation highlights |
| GOLD | #FFB84D | Attention boxes |

**Rules**: Never use black (#000000) backgrounds. Never use arbitrary hex values. Only use extended palette (CORAL, PURPLE, GOLD) sparingly.

### Typography

Font: **Space Grotesk** for ALL text. No exceptions.

| Role | Size | Weight | Color |
|------|------|--------|-------|
| Slide title | 20pt | Bold | DARK or WHITE |
| Section header | 28-36pt | Bold | WHITE on BLUE |
| Stat number | 40-42pt | Bold | BLUE or WHITE |
| Subtitle | 12pt | Normal | GRAY or CYAN |
| Body text | 11-12pt | Normal | DARK or GRAY |
| Card label | 9pt | Bold | accent color |
| Caption / footer | 8pt | Normal | GRAY |
| Pill text | 9pt | Bold | WHITE on accent |
| Table header | 9pt | Bold | WHITE on BLUE |
| Table body | 8pt | Normal | DARK |

### Spacing Scale

| Name | Inches | Use |
|------|--------|-----|
| xs | 0.08" | Tight internal padding |
| sm | 0.15" | Card internal padding |
| md | 0.225" | Gap between cards |
| lg | 0.35" | Gap between groups |
| xl | 0.5" | Margin |
| 2xl | 0.75" | Section separation |
| 3xl | 1.0" | Major vertical breaks |

### Grid System

12-column, 8-row grid. Access via `Grid.x(col, span)`, `Grid.y(row, span)`, `Grid.pos(col, row, col_span, row_span)`, `Grid.equal_cards(n)`.
```

---

### Task 6: Write SKILL.md v4.0 — §4 Deck Archetypes

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (append)

- [ ] **Step 1: Write §4 — Deck Archetypes**

Copy existing archetypes from `SKILL.v3.1.md` (Strategy, Problem-Solution, Onboarding, CS Kickoff, EBR redirect, Custom) and add the new Renewal/Proposal archetype. Each archetype should specify:
- Slide count and sequence
- Which engine helpers to use
- Intel requirements
- When to use this archetype

The new Renewal/Proposal archetype:

```markdown
### Renewal / Proposal
- 8-9 slides
- Title → Why Change (3 numbered trend cards) → What This Means (4 benefit cards) → Evidence (Sheets chart from Snowflake) → Option 1 (proposal table, CORAL) → Option 2 (proposal table, EMERALD) → Side-by-Side (comparison table, DKBLUE) → Summary
- **Key helpers**: `benefit_card()`, `proposal_table()`, `option_pill()`, `fmt_compact()`
- **Intel**: Slack for stakeholder sentiment, Snowflake for growth data, contract details for DEAL dict
- **Critical**: "Why Change" must use customer-specific language from intel, not generic trends. Each benefit card needs a footnote grounding it in the customer's current state.
- **Tables**: All option/comparison tables MUST use `proposal_table()` for consistent positioning across slides
```

---

### Task 7: Write SKILL.md v4.0 — §5 Slide Templates + §6 Build Pipeline

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (append)

- [ ] **Step 1: Write §5 — Slide Templates**

Copy all 17 template descriptions from `SKILL.v3.1.md` but **remove all code blocks**. Keep only the text descriptions of what each template looks like and when to use it. Add a decision table at the top:

```markdown
## §5 — Slide Templates

### Which Helper for Which Situation

| Situation | Engine Function |
|-----------|----------------|
| Any tabular data | `build_table()` or `proposal_table()` |
| Text on colored shape | `shape()` then `text_in()` on same oid |
| Multi-styled text on shape | `shape()` then `rich_in()` on same oid |
| Auto-sized text on shape | `shape()` then `smart_text_in()` on same oid |
| Slide title, subtitle | `label()` — standalone, no shape |
| Multi-styled free text | `textbox()` — standalone, no shape |
| Metric card | `kpi_card()` |
| Benefit with footnote | `benefit_card()` |
| Feature status | `feature_card()` |
| Colored pill label | `pill()` (auto-width) or `option_pill()` |
| Proposal/option table | `proposal_table()` — canonical position |
| Numbered circle | `numbered_circle()` |
| Customer quote | `quote_block()` |
| Phased plan column | `phase_card()` |
| Linked Sheets chart | `sheets_chart()` |
```

Then the 17 template descriptions (text only, no code). Each template keeps the same format as v3.1 but without Python code blocks.

- [ ] **Step 2: Write §6 — Build Pipeline**

```markdown
## §6 — Build Pipeline

### Import Pattern

Every build script starts with:

\```python
import sys, os
sys.path.insert(0, os.path.expanduser(
    '~/.claude/local-plugins/plugins/deck/engine'))
from core import *
\```

**No other imports needed** for deck building. The engine provides all helpers, auth, and infrastructure.

### Build Script Template

\```python
# ── DEAL dict (from intel brief) ──────────────────
DEAL = { ... }
assert not reconcile(DEAL), "Fix DEAL numbers first"

# ── Storyboard ────────────────────────────────────
storyboard([
    slide_spec('title', 'Customer x Atlan', 'Subtitle'),
    slide_spec('cards', 'Slide Title', items=3),
    # ...
], 'Deck Name')

# ── Auth + template ───────────────────────────────
creds = get_creds()
slides_svc, drive_svc, sheets_svc = init_services(creds)
PRES_ID = copy_template(drive_svc, 'Deck Title')
clean_template(slides_svc, PRES_ID)
STATE_FILE = '/tmp/{name}_deck_state.pkl'

# ── Build slides ──────────────────────────────────
# Use Grid for positioning:
#   x, w = Grid.x(col, span)
#   y, h = Grid.y(row, span)
# Use smart_text_in() for auto-sized text
# Use proposal_table() for option/comparison tables
# Use option_pill() for semantic pill coloring
# Use fmt_compact() for abbreviated numbers
# Use fmt_currency() for dollar amounts from DEAL dict

# ── Flush + Heal + Save ──────────────────────────
flush(slides_svc, PRES_ID)
healer = Healer(PRES_ID, slides_svc, deal=DEAL)
result = healer.heal()  # Target: 0 fixable issues
save_context(PRES_ID, slides_svc, STATE_FILE)
print_summary(PRES_ID, STATE_FILE)
\```

### Multi-Part Builds (15+ slides)

For large decks, split into two scripts with pickle state passing:
- Part A: slides 1-10, calls `save_context()` at end
- Part B: loads state via `load_context()`, builds slides 11+
- Each part runs the full flush → heal → save sequence

### Charts: Sheets-First

Every data visualization MUST have a Google Sheet backing it. Use `sheets_chart()` to embed linked charts. For visuals Sheets can't render (bezier curves, custom fills), use matplotlib → PNG → `createImage`, but ALSO write the data to a Sheet tab.
```

---

### Task 8: Write SKILL.md v4.0 — §7 Content Principles + §8 Anti-Patterns + §9 Quality Checklist + §10 Troubleshooting

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md` (append)

- [ ] **Step 1: Write §7 — Content Principles**

Copy from `SKILL.v3.1.md` §5 (Content Principles), keeping all 12 principles verbatim.

- [ ] **Step 2: Write §8 — Anti-Patterns**

Copy from `SKILL.v3.1.md` §6 (Anti-Patterns) with these additions:

```markdown
### #0 RULE: No Inline Helper Definitions
- **NEVER** define shape/text/table helpers in build scripts
- **ALWAYS** import from the engine: `from core import *`
- If a helper doesn't exist, add it to `core.py` — don't inline it

### NEW: No Building Without Intel Brief
- **NEVER** generate a build script without first producing an intel brief (§1)
- Even if the user says "just build it" — produce at minimum a thin brief

### NEW: No Hardcoded Numbers
- **NEVER** write `"$329,898"` as a string literal in a build script
- **ALWAYS** use `fmt_currency(DEAL['opt_1yr']['unit_price'])`
- All numbers flow from the DEAL dict
```

Keep all existing anti-patterns (no text-box-on-shape, visual, layout, table, technical).

- [ ] **Step 3: Write §9 — Quality Checklist**

```markdown
## §9 — Quality Checklist

Before delivering any deck, verify:

**Intel & Strategy**
- [ ] Intel brief produced and reviewed
- [ ] Storyboard pacing has no warnings
- [ ] DEAL dict reconciliation passes
- [ ] Narrative strategy documented in brief

**Build Quality**
- [ ] Healing round 1: 0 fixable issues
- [ ] All numbers from DEAL dict (no hardcoded strings)
- [ ] Charts backed by Google Sheets
- [ ] Context saved (pickle + manifest)

**Brand & Design**
- [ ] All colors from brand palette
- [ ] All fonts Space Grotesk
- [ ] Titles <= 20pt on content slides
- [ ] Stats <= 42pt in cards
- [ ] Dark slides use BLUE background
- [ ] Outlines removed on all non-bordered shapes
- [ ] Vertical middle alignment on all shapes

**Content**
- [ ] 3-second glance test passes on every slide
- [ ] Titles are takeaways, not topic labels
- [ ] "We" language throughout
- [ ] At least 2-3 customer quotes (if available from intel)
- [ ] Visual variety — mix of templates
- [ ] Close slide has 3 clear, owned next steps
```

- [ ] **Step 4: Write §10 — Troubleshooting**

Trim from `SKILL.v3.1.md` §11. Keep only essential issues. Add engine-specific items:

```markdown
| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: core` | Verify engine path: `~/.claude/local-plugins/plugins/deck/engine/core.py` |
| Healing finds 30+ issues | Likely using old inline helpers instead of engine. Check `from core import *` |
| Intel brief empty | Check MCP tool access — Slack, Glean, Snowflake may need re-auth |
| Numbers inconsistent | Run `reconcile(DEAL)` and fix the DEAL dict before building |
```

Plus the existing OAuth, template access, batch size, and rate limit troubleshooting from v3.1.

- [ ] **Step 5: Add Dependencies section at end**

```markdown
## Dependencies

- **Engine**: `~/.claude/local-plugins/plugins/deck/engine/core.py` — all build code
- **Python packages**: auto-installed by engine (google-api-python-client, google-auth, etc.)
- **Google OAuth**: embedded in engine, token at `/tmp/google_slides_token.pickle`
- **Slides template**: `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU`
- **Snowflake MCP** (for charts/EBR): configured via `claude mcp add snowflake`
- **Slack/Glean MCP** (for intel brief): configured in Claude Code settings
```

- [ ] **Step 6: Commit SKILL.md v4.0**

```bash
cd ~/.claude/local-plugins/plugins/deck
git add skills/deck/SKILL.md
git commit -m "feat: rewrite SKILL.md v4.0 — intel brief gate, engine-only code, renewal archetype"
```

---

### Task 9: Verify — Rebuild Zoom Deck With New Skill

**Files:**
- Create: `/tmp/build_zoom_v7.py` (test build)

- [ ] **Step 1: Build the Zoom renewal deck from scratch**

Using the v4.0 skill, invoke `/deck renewal for Zoom`. The skill should:
1. Run the intel brief gate (search Slack, Snowflake)
2. Print the brief and wait for approval
3. Generate a build script that imports from the engine
4. Run storyboard, reconcile, build, heal, save
5. Healing round 1 should find 0 fixable issues

- [ ] **Step 2: Verify healing result**

```bash
python3 -c "
import json
with open('/tmp/zoom_v7_deck_state_manifest.json') as f:
    state = json.load(f)
print(f'Slides: {state[\"slide_count\"]}')
print(f'Elements: {sum(s[\"elementCount\"] for s in state[\"slides\"])}')
"
```

- [ ] **Step 3: Compare against v4 reference**

Open both decks side-by-side:
- v4 reference: `1aWzjrZQQssvvRReGNFwt9xkIelKFetSRWvicHukuJ00`
- v7 engine build: the new PRES_ID

Check: narrative quality, visual consistency, number accuracy, table alignment.

---

### Task 10: Final Commit and Cleanup

**Files:**
- Modify: `~/.claude/local-plugins/plugins/deck/docs/specs/2026-03-27-deck-skill-v4-design.md`

- [ ] **Step 1: Update spec status to Complete**

Change `**Status**: Draft` to `**Status**: Complete`.

- [ ] **Step 2: Clean up old task state files**

```bash
rm -f /tmp/zoom_engine_test_deck_state.pkl /tmp/zoom_engine_test_deck_state_manifest.json
rm -f /tmp/zoom_v5_deck_state.pkl /tmp/zoom_v5_deck_state_manifest.json
```

- [ ] **Step 3: Final commit**

```bash
cd ~/.claude/local-plugins/plugins/deck
git add -A
git commit -m "feat: deck skill v4.0 complete — engine fixes, intel brief gate, renewal archetype"
```
