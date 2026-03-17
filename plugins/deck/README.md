# Atlan Deck Builder

Build polished Google Slides decks programmatically via the Slides API using the Atlan brand system.

**v3.0** · Author: Greg Martell · Font: Space Grotesk

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
| Custom | Varies | Anything else |

## Quick Start

```bash
# Strategy deck
/deck strategy for Zoom — audience: RJ Merriman & Data Platform Team

# Problem-solution deck
/deck problem-solution for Medtronic — 5 gaps in their data governance

# Data-driven EBR
/deck:ebr zoom.atlan.com

# Custom deck
/deck custom for Dropbox — competitive positioning against Collibra
```

## Prerequisites

- **Python 3.8+** with pip
- **Google API packages** (auto-installed by pre-flight check):
  - `google-api-python-client`
  - `google-auth`
  - `google-auth-httplib2`
  - `google-auth-oauthlib`
- **Google OAuth** — credentials embedded in build scripts, browser opens on first run
- **Slides template access** — ask Greg for read access to the Atlan master template
- **Snowflake MCP** (EBR only) — configured via `claude mcp add snowflake`

## What's New in v3.0

- **Auto pre-flight check** — detects missing Python/pip/packages and auto-installs
- **Styled terminal output** — ANSI-colored banners, progress bars, step indicators
- **Timeframes & lookback windows** — documented token lifetimes, API quotas, state file expiry
- **EBR as first-class deck type** — surfaced in banner, Quick Start, and deck type selector
- **Expanded Quick Start** — options/flags, 14 slide templates, companion skills reference
- **16 troubleshooting entries** — covers Python setup through stale state recovery

## Brand System

| Element | Value |
|---------|-------|
| Primary | `#2026D2` Atlan Blue |
| Accent | `#62E1FC` Cyan, `#F34D77` Pink |
| Extended | `#FF6B4A` Coral, `#00C48C` Emerald, `#9B7FFF` Purple, `#FFB84D` Gold |
| Font | Space Grotesk (all text) |
| Dark bg | Always `#2026D2`, never black |
| Template | `1SOajzd0opagErD3ATLmj77tlSeOEIvlWaqW6l6MfXQU` |

## 14 Slide Templates

1. Title (dark) — 2. Section Divider — 3. Content + Cards — 4. Two-Column Split — 5. Challenge — 6. Solution — 7. Architecture Diagram — 8. Big Stats Row — 9. Table — 10. Close (dark) — 11. Before/After — 12. Risk & Mitigation — 13. Phased Plan — 14. Quote

## File Structure

```
plugins/deck/
├── .claude-plugin/
│   └── plugin.json           # v3.0.0 metadata
├── README.md                 # This file
└── skills/
    ├── deck/
    │   └── SKILL.md          # Main deck builder (1,400+ lines)
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
