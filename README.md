# Deck Builder Skill (Team Install Guide)

This repository contains the skills used by Claude/Codex to build Google Slides decks:

- `skills/deck/SKILL.md` = main `/deck` skill (strategy, problem-solution, onboarding, custom)
- `skills/ebr/SKILL.md` = `/deck:ebr` skill (data-driven EBRs with supply metrics + live charts)
- `skills/deck/deck_terminal_ui.py` = live feed preview module (ASCII wireframes in terminal)

### What's New (v3.1 — March 19, 2026)

- **Real supply metrics** — EBR skill now pulls catalog data from `DATA_OPS.ANALYSIS.ASSET_COUNT_BY_NAME` (assets per connector) and `AI_INPUTS.CX.CUSTOMER_WEEKLY_METRICS` (enrichment %, glossary, data products, workflows). No more page-view interaction proxies.
- **Supply narrative intelligence** — auto-detects whether to frame as "expand supply" or "deepen catalog quality" based on connector count and enrichment percentages.
- **`styled_element()` helper** — safe multi-style text replacement that computes character indices from segments automatically. Prevents off-by-one font bleed bugs when mixing large stat numbers with small labels.
- **Live feed preview** — `deck_terminal_ui.py` renders high-fidelity ASCII wireframes of each slide before the build fires. Data-driven charts (horizontal bars, vertical bars, S-curves, proportion bars, KPI cards) with Atlan brand colors via 24-bit ANSI. 72-col max for Claude Code compatibility.
- **Supply & demand visual slides** — 4 new matplotlib-powered slide templates: Scale Mismatch (log-scale bars), Catalog Depth Waterfall, Supply-Demand S-Curves with gap area, Connector Portfolio (proportion bar + stat cards).

This guide is written for non-technical teammates. You can copy/paste each command exactly as shown.

## What You Will Need

Before starting, make sure:

1. You are logged into your work computer.
2. You can open Terminal.
3. You have Claude Code installed.
4. You have a managed Google Workspace account (your `@atlan.com` account).

## Quick Version (If You Are Comfortable in Terminal)

```bash
pip install -U google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
rm -f /tmp/google_slides_token.pickle /tmp/build_deck_*.py /tmp/build_ebr_*.py /tmp/*_deck_state.pkl /tmp/*_deck_state.json
```

Then restart Claude Code and run:

```text
/deck strategy for <customer>
```

If you want the fully detailed instructions, follow the sections below.

---

## Full Step-by-Step Setup (Recommended)

## Step 1: Open Terminal

1. Press `Command + Space`.
2. Type `Terminal`.
3. Press Enter.

You should see a window with text and a cursor.

## Step 2: Install Python Packages (Required)

Copy/paste this command into Terminal and press Enter:

```bash
pip install -U google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

What this does:

- Installs Google API libraries required for Slides + OAuth login.
- Updates old versions if they already exist.

If you get `pip: command not found`, try:

```bash
python3 -m pip install -U google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

## Step 3: Clear Old Local Auth/Build Files (Important)

Copy/paste this command and press Enter:

```bash
rm -f /tmp/google_slides_token.pickle /tmp/build_deck_*.py /tmp/build_ebr_*.py /tmp/*_deck_state.pkl /tmp/*_deck_state.json
```

What this does:

- Removes old OAuth token files.
- Removes old generated build scripts.
- Prevents stale settings from causing login errors.

## Step 4: Restart Claude Code

1. Fully quit Claude Code (not just close the window).
2. Re-open Claude Code.

This ensures the latest skill files are loaded.

## Step 5: Run Your First Deck Command

In Claude Code, run:

```text
/deck strategy for <customer>
```

Example:

```text
/deck strategy for Zoom
```

## Step 6: Complete Google Sign-In

On first run:

1. A browser window opens.
2. Choose your `@atlan.com` Google account.
3. Approve access.
4. Return to Claude Code.

After this, token is saved locally and future runs should not ask again unless token expires.

---

## Installing/Updating Skill Files from This Repo

If you are asked to manually refresh skill files:

## A) Clone this repo

```bash
cd ~
git clone https://github.com/gregmartell-atlan/deck-builder.git
```

If folder already exists:

```bash
cd ~/deck-builder
git pull
```

## B) Copy skills into Claude local plugin directory

```bash
mkdir -p ~/.claude/local-plugins/plugins/deck/skills/deck
mkdir -p ~/.claude/local-plugins/plugins/deck/skills/ebr
cp ~/deck-builder/skills/deck/SKILL.md ~/.claude/local-plugins/plugins/deck/skills/deck/SKILL.md
cp ~/deck-builder/skills/ebr/SKILL.md ~/.claude/local-plugins/plugins/deck/skills/ebr/SKILL.md
```

## C) Also refresh plugin cache copy (recommended)

```bash
mkdir -p ~/.claude/plugins/cache/atlan-local/deck/1.0.0/skills/deck
mkdir -p ~/.claude/plugins/cache/atlan-local/deck/1.0.0/skills/ebr
cp ~/deck-builder/skills/deck/SKILL.md ~/.claude/plugins/cache/atlan-local/deck/1.0.0/skills/deck/SKILL.md
cp ~/deck-builder/skills/ebr/SKILL.md ~/.claude/plugins/cache/atlan-local/deck/1.0.0/skills/ebr/SKILL.md
```

Then repeat Step 3 (clear old local files) and Step 4 (restart Claude Code).

---

## Google OAuth Requirements (For Team Leads/Admins)

- OAuth client type must be **Desktop app**.
- OAuth consent screen audience should be **Internal**.
- Team members should sign in with their managed workspace account.

If settings were just changed in Google Cloud, allow some propagation time and retry.

---

## Troubleshooting

## Error: `redirect_uri_mismatch`

This almost always means stale skill files or wrong OAuth client type.

Do this:

1. Update skill files from this repo (see install/update section above).
2. Run cleanup command from Step 3.
3. Restart Claude Code.
4. Retry `/deck ...`.

## Error: “app is restricted to test users”

- Confirm you are signing in with your `@atlan.com` account.
- Ask admin to confirm consent screen audience is `Internal`.
- Wait and retry if settings were recently changed.

## Error: `ModuleNotFoundError`

Run package install again:

```bash
pip install -U google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

## Browser opens but login does not finish

1. Close browser tab.
2. Run cleanup command from Step 3.
3. Restart Claude Code.
4. Try again.

---

## What To Send When Asking for Help

If you still get blocked, send this to your support contact:

1. Screenshot of the full error.
2. Exact command you ran in Claude Code.
3. Output of:

```bash
python3 --version
```
