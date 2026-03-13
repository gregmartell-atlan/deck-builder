# Deck Builder Skill

Claude/Codex deck-building skills for Atlan Google Slides workflows.

## Contents

- `skills/deck/SKILL.md` - main `/deck` skill
- `skills/ebr/SKILL.md` - `/deck:ebr` skill

## Team Setup

1. Install/update plugin files on each machine.
2. Install Python dependencies:

```bash
pip install -U google-api-python-client google-auth google-auth-httplib2 google-auth-oauthlib
```

3. Clear old local auth/build state:

```bash
rm -f /tmp/google_slides_token.pickle /tmp/build_deck_*.py /tmp/build_ebr_*.py /tmp/*_deck_state.pkl /tmp/*_deck_state.json
```

4. Restart Claude Code.
5. Run any deck command, for example:

```text
/deck strategy for <customer>
```

## OAuth Requirements

- OAuth client type: **Desktop app**
- Consent screen audience: **Internal** (same Google Workspace)
- Teammates must sign in with their managed workspace account.

If a user gets `redirect_uri_mismatch`, they are likely using stale skill files with an old client config.
