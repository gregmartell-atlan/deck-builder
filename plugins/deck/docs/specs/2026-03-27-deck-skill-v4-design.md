# Deck Skill v4.0 Design Spec

**Date**: 2026-03-27
**Author**: Greg Martell + Claude
**Status**: Draft

## Problem Statement

The deck skill (v3.1) produces technically correct but visually average decks. The v4 Zoom reference deck is significantly better because a human drove strategic thinking, real data, and design iteration. The skill's intelligence phase is optional (Claude skips it), helpers are inlined in SKILL.md (duplicating the engine), and there's no feedback loop between building and evaluating.

The engine (`core.py`) built today provides mechanical foundations (Grid, text measurement, validation, self-healing) but the skill doesn't use it. The engine also has bugs: `bordered()` produces outlines that the Healer then fixes, meaning 33 issues per deck that shouldn't exist.

## Goals

1. Every deck built by the skill should approach the quality of the v4 Zoom reference
2. No deck is built without customer intel and a reviewed narrative strategy
3. The engine is the single source of truth for all code — SKILL.md has zero inline Python
4. A correctly-built deck produces 0 healing issues
5. Numbers are never hardcoded — every value flows from a DEAL dict

## Non-Goals

- Automating the intelligence phase into Python functions (judgment stays with Claude)
- Building a visual feedback loop in this version (future v4.1)
- Replacing the EBR skill (separate skill, separate pipeline)

## Architecture

### Separation of Concerns

```
SKILL.md (~1100 lines)          core.py (~1850 lines)
├── WHAT to think about         ├── HOW to execute
├── WHEN to do each step        ├── Shape/text/table helpers
├── WHY each step matters       ├── Grid, spacing, measurement
├── Template descriptions       ├── Validation & healing
├── Content principles          ├── Auth & build infrastructure
└── Anti-patterns               └── Intel brief formatter
```

SKILL.md is a strategic playbook. core.py is the execution engine. They don't overlap.

### Mandatory Pipeline

Every deck build follows this sequence. No step is optional.

```
1. Intel Brief    → Gather sources, synthesize, print brief, WAIT for approval
2. Storyboard     → Print slide plan with pacing analysis
3. Reconcile      → Validate DEAL dict, assert consistency
4. Build          → Generate slides using engine (import from core)
5. Heal           → Validate + auto-fix (target: 0 fixable issues)
6. Save           → Context snapshot (pickle + manifest)
```

### Intel Brief Gate

Before generating any build script, Claude MUST:

1. **Search available sources** using MCP tools:
   - Slack: `mcp__claude_ai_Slack__slack_search_public_and_private` for customer channel
   - Glean: `mcp__claude_ai_Glean__search` with `app: "gong"` for call transcripts
   - Snowflake: `mcp__snowflake__run_snowflake_query` for usage data
   - Granola (if available): meeting notes

2. **Synthesize findings** into a structured brief:
   - Deal context (ARR, renewal date, stakeholders)
   - Sources checked (with hit/miss indicators)
   - Key findings (numbered, with source attribution)
   - Narrative strategy (frame, audience, hook, risk)
   - DEAL numbers with reconciliation result

3. **Print the brief** to terminal and wait for user confirmation

4. **Gate**: If user says "proceed", build the deck. If user provides corrections or additional context, incorporate and rebuild the brief.

For deck types where customer intel isn't available (generic templates, internal docs), the brief is shorter but still required — at minimum the narrative strategy and DEAL numbers.

### Engine Fixes

#### Bug: `bordered()` Outline Issue

**Current**: `bordered()` sets outline fill and weight but doesn't set `propertyState`. The outline renders visibly. The Validator flags it. The Healer fixes it. This accounts for ~50% of healing fixes.

**Fix**: `benefit_card()` should use `shape()` (not `bordered()`) for the card body. The left accent bar provides the visual border. The `bordered()` function itself is correct for intentional borders (silos, architecture diagrams) — the Validator should skip shapes where outlines are intentional.

**Implementation**: Add an `_intentional_outlines` set to the Validator. Shapes created by `bordered()` and `dashed()` have expected outlines. The Validator checks if the outline matches the intended border color — if so, it's not a bug.

#### Bug: benefit_card() Using bordered()

**Current**: `benefit_card()` calls `bordered(oid, pid, l, t, w, h, bg, LTBG, 0.5, 'ROUND_RECTANGLE')` — creating a visible LTBG border.

**Fix**: Switch to `shape()` with `ROUND_RECTANGLE` type. The accent bar provides the visual left edge. No border needed.

#### Improvement: Validator Year/Date Exclusion

**Current**: Numbers like 2026, 2025, 2024 in text get flagged as "not in DEAL dict."

**Fix**: Add a `KNOWN_NOISE_NUMBERS` set to the Validator: years (2020-2030), small contextual numbers (percentages, multipliers), and numbers that appear in narrative text rather than data cells.

### SKILL.md Structure (v4.0)

```
§0  Setup & Prerequisites
    - Engine location and import pattern
    - Python deps (auto-installed by engine)
    - OAuth (embedded, no files needed)
    - Template access
    - Pre-flight check (trimmed — engine handles most)

§1  Intel Brief Gate (NEW)
    - Which MCP tools to call for each source
    - Brief structure and required sections
    - Approval gate — no brief, no deck
    - Handling thin sources (flag gaps, ask user)

§2  Strategic Debate
    - Agent personas (VP CS, CEO/Deal Desk, Objection Anticipator)
    - Multi-spin architecture for mixed audiences
    - Number reconciliation as part of debate output
    - When to skip debate (simple decks, templates)

§3  Brand Reference
    - Color palette (names + hex, for Claude's reference)
    - Typography scale (role → size → weight → color)
    - Spacing scale names (xs through 3xl)
    - NO CODE — just reference values

§4  Deck Archetypes
    - Strategy (15-20 slides)
    - Problem-Solution (10-15 slides)
    - Onboarding (8-12 slides)
    - Renewal/Proposal (8-9 slides, NEW)
    - EBR (redirect to /deck:ebr)
    - Custom (varies)
    - CS Kickoff (19 slides, existing)

§5  Slide Templates (17 templates)
    - Text descriptions only (what it looks like, when to use)
    - Decision table: which helper for which situation
    - NO CODE — helpers live in engine

§6  Build Pipeline
    - Import pattern: sys.path + from core import *
    - Build script template (skeleton, no inline helpers)
    - Storyboard before building
    - DEAL dict pattern with reconciliation
    - flush() → heal() → save_context() sequence
    - Multi-part builds for 15+ slide decks

§7  Content Principles
    - Data before narrative
    - Title IS the takeaway
    - "We" language
    - 3-second glance test
    - Max 4-5 bullets per slide

§8  Anti-Patterns
    - No text-box-on-shape (existing)
    - No inline helper definitions (NEW — always import)
    - No hardcoded numbers (NEW — always DEAL dict)
    - No building without intel brief (NEW)
    - No arbitrary colors (existing)
    - Table rules (existing)

§9  Quality Checklist
    - Intel brief reviewed ✓ (NEW)
    - Storyboard pacing clean ✓ (NEW)
    - DEAL reconciliation pass ✓ (NEW)
    - Healing round 1: 0 fixable issues ✓ (NEW)
    - All existing checks (fonts, colors, alignment, etc.)

§10 Troubleshooting
    - Trimmed to essential issues
    - Engine-specific troubleshooting
```

### Renewal/Proposal Archetype (NEW)

**Purpose**: Renewal decks, pricing proposals, commercial negotiations.

**Slide sequence** (8-9 slides):
1. Title (dark) — Customer x Atlan, proposal framing
2. Why Change — 3 numbered trend cards explaining pricing evolution
3. What This Means — 4 benefit cards (2x2) translating trends to customer value
4. Evidence — Linked Sheets chart proving growth/adoption (real Snowflake data)
5. Option 1 — Proposal table with CORAL pill (basic/current path)
6. Option 2 — Proposal table with EMERALD pill (recommended/expanded)
7. Side-by-Side — Comparison table with DKBLUE pill (3-4 columns)
8. Summary — Text leave-behind with both options summarized

**Key primitives**: `benefit_card()`, `proposal_table()`, `option_pill()`, `fmt_compact()`

**Intel requirements**: Slack threads for stakeholder sentiment, Snowflake for asset/MAU growth, current contract details for DEAL dict.

**Content principles specific to this archetype**:
- "Why Change" must use customer-specific language, not generic trends
- Each benefit card needs a footnote grounding it in current state
- Option tables share identical positioning via `proposal_table()`
- Summary must be readable as a standalone leave-behind

### What Gets Removed from SKILL.md

~800 lines of inline Python cut:
- All Category 1-5 helper function definitions
- `build_table()` implementation
- `save_context()` implementation
- `get_creds()` and OAuth code
- ANSI terminal styling class
- `styled_element()` implementation
- All composite helper implementations

These all live in `core.py` now. SKILL.md references them by name with usage notes, not code.

## Testing Plan

1. **Engine fix verification**: Run existing test suite after fixing `bordered()`/`benefit_card()`. Healing round 1 should find 0 fixable issues on a test deck.

2. **Zoom deck rebuild**: Build the Zoom renewal deck from scratch using the new skill. Compare against v4 reference for:
   - Narrative quality (is the "Why Change" slide customer-specific?)
   - Visual quality (do tables/cards/pills look right?)
   - Number consistency (does DEAL dict flow everywhere?)
   - Healing count (target: 0 fixable issues)

3. **Different customer test**: Build a deck for a non-Zoom customer to verify the skill generalizes beyond one reference deck.

## Migration

- `core.py` is updated in place (bug fixes, intel brief formatter)
- `SKILL.md` is rewritten from scratch (clean break, not incremental patch)
- Old SKILL.md archived at `SKILL.v3.1.md` in case we need to reference it
- No changes to the EBR skill (separate file)

## Resolved Questions

1. **Intel brief persistence**: Yes, save to `/tmp/{customer}_intel_brief.md`. Multi-part builds and rebuild-after-feedback both need the brief context.
2. **Visual review loop**: Defer to v4.1. The current scope is already significant. The intel brief gate is the higher-leverage improvement.
3. **High-level build functions**: No. Keep slide construction in the build script. A `build_renewal_deck()` function would hide too much — Claude needs to make per-slide content decisions that depend on the intel brief. The engine provides primitives, the skill provides the thinking.
