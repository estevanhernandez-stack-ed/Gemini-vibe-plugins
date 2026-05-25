---
description: "Read-only tier-aware summary from cached state — no re-scan"
---

# Vibe Sec — posture

The read-never-writes rule and tier→ASVS are always-on via `AGENTS.md`. The
`audit.json` / `findings.jsonl` read shapes and the four-band display format are
indexed in the `vibe-sec-guide` skill (`.agent/skills/vibe-sec-guide/SKILL.md`).

`/vibe-sec-posture` is the cheap "where do I stand" read. It is **read-only — it
never re-scans.** It reads cached state and renders the current posture. If the
cache is stale or missing, it says so and points at `/vibe-sec-audit`; it does
not silently kick off a scan.

## What it reads (no scanning)

- `.vibe-sec/state/audit.json` — the cached classification, score, gate verdict,
  counts, tools used, and the scan timestamp.
- `.vibe-sec/state/findings.jsonl` — deduped by id (last write wins).
- `.vibe-sec/state/suppressions.json` — active per-project suppressions.

## What it renders

- **Tier + confidence** + the ASVS floor for that tier.
- **Weighted score vs the tier threshold**, and the gate PASS/FAIL the cached
  audit recorded.
- **Outstanding findings grouped by severity**, deduped by id, with suppressed
  findings noted separately (not counted in the live total).
- **Freshness.** If the cached audit is >24h old, lead with that: "Cached audit
  is N hours old — run `/vibe-sec-audit` for a fresh read." Use `isAuditFresh()`.

## Running it

Built TypeScript readers: `readAuditState()`, `readFindingsDeduped()`,
`isAuditFresh()` in `src/state/`, plus `listSuppressions()` in `src/fix/`. The
four-band structure for display reuses `buildBandedReport()` over the cached
findings — same render, no detection. The invariant: **reading must not write.**
Opening posture leaves findings.jsonl and audit.json byte-identical.

## What to tell the user

Lead with the standing: "<tier>, N% (M% bar), gate PASS/FAIL, K open findings."
If nothing's cached, say "no audit yet — run `/vibe-sec-audit`." If stale, name
the age and recommend a re-run. Don't re-scan to fill a gap; posture is the
fast read, `/vibe-sec-audit` is the work.
