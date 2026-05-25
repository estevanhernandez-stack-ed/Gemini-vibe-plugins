---
description: Show current Vibe Doc status
---

# /vibe-doc-status — Show Current Vibe Doc Status

Run `npx vibe-doc status` in the user's project directory via bash. Present the output in a clean format showing last scan time, classification, and documentation coverage.

```bash
cd <project-path> && npx vibe-doc status
```

If no state exists, tell the user to run `/vibe-doc-scan` first.

---

## What to present

Read the CLI output and surface, in a scannable format:

- **Last scan** — when the project was last scanned (timestamp).
- **Classification** — the primary category, secondary categories, and deployment contexts on record.
- **Documentation coverage** — the Required / Recommended / Optional tier breakdown and overall percentage.

If `npx vibe-doc status` reports no `.vibe-doc/state.json`:

```
No Vibe Doc state found for this project.

Run /vibe-doc-scan first to analyze your artifacts, classify the project,
and build the gap report. Then /vibe-doc-status will show your coverage.
```

---

## Notes

- This workflow is **read-only** — it never writes files or changes state. It only reflects the current `.vibe-doc/state.json` back to the user.
- It is a thin reporting surface over the CLI; the substance lives in `npx vibe-doc status`. There is no parallel implementation skill in the source plugin, so there is no SKILL body to merge — this workflow IS the implementation.

---

**Version:** 1.0 (Antigravity port)
