---
description: "Run when the user says /radar and wants a read-only digest of what's new across their stack and competitor set since last visit. Reads the cached scheduled-refresh file (per-project, weekly). When the cache is missing, optionally runs a manual refresh on demand. No mode run, no PR — just the digest."
---

# /radar — what's new since last visit

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Reads `.vibe-iterate/radar.cache.json` and renders a **digest** of what's new across the user's framework pins, competitor set, and Product Hunt category since the last cache refresh. Read-only by default; offers a manual refresh when the cache is missing or stale.

Used internally by every banner mode as the cheap first-pass scan.

## Hard rules

- **Read-only by default.** No mode runs, no PR opens, no Atlas write.
- **Never auto-refresh on a stale cache.** If the cache is stale (>14 days), surface the staleness and ask the user before refreshing.
- **Never run a full refresh during a banner mode.** When called internally by `feature-add`, `competitive`, etc., use whatever's in the cache; if absent, surface the gap to the calling mode and let IT decide whether to ask the user.

## Inputs

- **No required arguments.** Optional `--refresh` flag forces a manual refresh even if the cache is current.
- **Project state** — `.vibe-iterate/config.json` (for `framework_pins[]` and `competitors[]`), `.vibe-iterate/radar.cache.json` (the cached digest).

If `.vibe-iterate/config.json` is **absent**, surface: *"No config yet. Run /vibe-iterate first to set up — the radar needs to know what stack and competitors to track."* Don't proceed.

## Procedure

### Step 1 — read the cache

Try to read `.vibe-iterate/radar.cache.json`. Three states:

1. **Cache present and current** (`refreshed_at` ≤ 14 days ago) → render the digest from cache (skip to step 4).
2. **Cache present but stale** (`refreshed_at` > 14 days ago) → surface staleness, offer manual refresh:
   ```
   Radar cache last refreshed [N days] ago — stale. Refresh now? (yes / no — render stale digest)
   ```
   - If yes → step 2 (manual refresh).
   - If no → step 4 (render stale digest with a `[STALE]` banner).
3. **Cache absent** → surface the absence, offer manual refresh:
   ```
   No radar cache yet. The weekly scheduled refresh hasn't run, OR the schedule plugin isn't wired.

   Refresh manually now? (yes / no)
   ```
   - If yes → step 2.
   - If no → exit cleanly with a one-line acknowledgment ("OK — install the schedule plugin and configure the weekly refresh, or re-run /radar with --refresh anytime.").

### Step 2 — manual refresh (when user opts in or `--refresh` flag is set)

Refresh fetches three signals, in order. Each is independent — if one fails, log the failure and continue.

**A. Framework releases** (one query per pin in `framework_pins[]`):
- Prefer `mcp__context7__resolve-library-id` + `mcp__context7__query-docs` for canonical docs and version info.
- If context7 is unavailable, fall back to web search: query for `<package> <version-range> changelog` and `<package> latest release notes`.
- Per pin, capture: `current_pin`, `latest`, `highlights[]` (3-5 bullets max), `codemod_available` (boolean), `breaking` (boolean).

**B. Competitor changes** (one fetch per URL in `competitors[]`):
- Use WebFetch on each URL with the prompt: *"Summarize what's new since [N days ago] in 3-7 bullets. Identify each shipped feature by name."*
- Capture: `url`, `fetched_at`, `summary` (one paragraph), `items[]` (3-7 strings).
- If WebFetch returns 404 / 403 / unreachable, log a one-line warning and skip that URL.

**C. Product Hunt buzz** (one search):
- WebSearch for `<config.category-keyword> "product hunt" 2026` (or the current year).
- Capture top 5 launches: `name`, `tagline`, `url`, `votes`.
- If no relevant results, set `product_hunt_buzz: []`.

### Step 3 — write the cache

Build the cache object per the schema at `.agent/skills/guide/schemas/radar-cache.schema.json`:

```json
{
  "refreshed_at": "<ISO-8601 UTC timestamp, now>",
  "framework_releases": [...],
  "competitor_changes": [...],
  "product_hunt_buzz": [...]
}
```

**Validate against the schema before writing.** If validation fails, fix and re-validate; do NOT write a malformed cache (downstream consumers depend on shape).

Write to `.vibe-iterate/radar.cache.json`. Atomic (full-file write, not append).

### Step 4 — render the digest

Group by category. Don't pad with "no items" — if a category is empty, omit it entirely.

```
Radar — refreshed YYYY-MM-DD HH:MM UTC [STALE if applicable]

Framework releases (N pins tracked)
- <package> <current_pin> → <latest>  [breaking | codemod available]
  - <highlight 1>
  - <highlight 2>
  - <highlight 3>

Competitor changes (N URLs scanned)
- <competitor URL>  (fetched YYYY-MM-DD)
  - <item 1>
  - <item 2>
  - <item 3>
  Summary: <one-line summary>

Product Hunt — <category-keyword>
- <name> (<votes> votes) — <tagline>  [<url>]

Deltas since last /radar call
- <one-line delta if any: "Notion shipped AI tagging since your last visit", "react 19.0.1 patch released since last visit">
```

If this is the first `/radar` call ever (no prior cache to diff against), omit the "Deltas since last /radar call" section.

## When invoked internally by a banner mode

The calling mode passes a `--silent` flag; `/radar` returns the parsed cache as a structured object instead of rendering the user-facing digest. If the cache is missing or stale, return a sentinel object so the calling mode knows to surface the gap.

## Anti-patterns

- **Don't refresh on every invocation.** The cache exists for a reason. Refresh only on user opt-in or `--refresh`.
- **Don't render every pin / URL even when nothing's new.** Bullets describe deltas; if a pin hasn't moved, omit it.
- **Don't fail loudly on partial fetch failures.** Log the failed URL/pin, continue, surface the failure as a one-line note at the bottom of the digest.
- **Don't write the cache mid-render.** Step 3 (write) happens before step 4 (render). Render reads from disk to confirm the write succeeded.

## Cross-references

- Schema: `.agent/skills/guide/schemas/radar-cache.schema.json`
- Knowledge sources reference: AGENTS.md § Knowledge sources
- Sibling sidecar: `/scan-releases` (per-package version diff with codemod detection)
- Sibling sidecar: `/spy` (one-shot competitor read for a single URL)
