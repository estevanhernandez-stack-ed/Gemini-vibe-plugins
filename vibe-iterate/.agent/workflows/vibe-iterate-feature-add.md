---
description: "Run when the user says /vibe-iterate-feature-add and wants to ship the next feature. Scans competitor URLs, Product Hunt, framework releases, and feedback.md. Clusters candidates, scores on impact/fit/effort/Atlas-history, ships one PR with an Atlas entry naming the candidates considered and the runners-up."
---

# /vibe-iterate-feature-add — what should we build next?

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `vibe-iterate-guide` skill (`.agent/skills/vibe-iterate-guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

The default banner mode for "the app's shipped, what do I build next?" Ingests four signals (competitor URLs, Product Hunt, framework releases, `feedback.md` if present), clusters candidates, scores them via `/vibe-iterate-rate`, picks the top one, and ships one PR. Atlas entry captures what was considered, what won, what didn't.

## Hard rules

- **One PR per invocation.** No multi-PR sprawl. If the iteration is heavy enough to need multiple PRs, surface that and trigger Cart-detection.
- **Honor Atlas history.** Recently rejected candidates (60-day window) are demoted; recently shipped candidates are skipped (don't double-ship the same thing).
- **No auto-fire of `/vibe-iterate-ship`.** The user confirms the chosen candidate before the build starts.
- **Atlas write is mandatory.** Every invocation that opens a PR (or that the user explicitly declines mid-flow) writes an Atlas entry. Read `.agent/skills/vibe-iterate-guide/references/atlas-conventions.md`.

## Session + friction logging

At workflow start — load the `vibe-iterate-session-logger` skill (`.agent/skills/vibe-iterate-session-logger/SKILL.md`) and run `start("feature-add", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `vibe-iterate-friction-logger.log()` invocation.

At workflow end — call `vibe-iterate-session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })`. `atlas_outcome` mirrors the Atlas entry's outcome (`shipped` | `rejected` | `queued`). `pr_url` is the PR URL when shipped, else `null`.

Honor the friction trigger map at `.agent/skills/vibe-iterate-guide/references/friction-triggers.md` — section `/vibe-iterate-feature-add` — for which friction types to log at which confidence. Universal triggers (`repeat_question`, `rephrase_requested`) also apply; honor the defensive default — no quoted prior turn in `symptom` means don't log.

## Inputs

- **No required arguments.** Optional `--from <signal>` to restrict the scan to one source (`competitors` | `product-hunt` | `releases` | `feedback`).
- **Project state required:** `.vibe-iterate/config.json` (for `category`, `competitors[]`, `framework_pins[]`). If absent, hand off to bootstrap: *"No config yet. Run `/vibe-iterate` first to bootstrap, then re-invoke this mode."*

## Procedure

### Step 1 — posture announcement

> *Feature-add mode → cutting-edge posture, current framework idioms, fit-with-stack scoring. Reading signals, clustering, scoring, picking ONE to ship.*

### Step 2 — Cart-detection (early read)

Per AGENTS.md § Cart-detection, check whether `vibe-cartographer` workflows/skills are available in this Antigravity workspace (read-only; never invoke one as a probe). Note: present | absent. The decision to delegate happens AFTER scoring, when the iteration's heaviness is known.

### Step 3 — ingest signals

Run these in parallel where possible:

**A. Competitor URLs** — call `/vibe-iterate-radar --silent` to read the cached competitor changes. If cache is missing/stale, surface the gap and offer to refresh: *"Radar cache is [stale | absent]. Refresh now for fresh competitor signal? (yes / no — proceed with stale data)"*. If user says no, continue with whatever's in the cache (or skip competitors entirely if absent).

**B. Product Hunt** — same `/vibe-iterate-radar --silent` call covers this. Read `product_hunt_buzz[]` from the cache.

**C. Framework releases** — call `/vibe-iterate-scan-releases --silent` to get the structured per-package release diff. This is fresh data (always queries; cheap).

**D. feedback.md** — if `feedback.md` exists at the project root, read it. Extract user-mentioned feature requests (pattern: lines starting with "feature:", "request:", or any line tagged `[feature]`).

If `--from <signal>` was passed, restrict ingestion to just that source.

### Step 4 — cluster candidates

For each ingested signal, extract candidate ideas as one-line strings:

- **Competitor changes** → "Competitor X shipped saved searches" → candidate: "saved searches"
- **Product Hunt buzz** → "AI-tagging app trending" → candidate: "AI-powered tagging"
- **Framework releases** → "Next 16 added Server Actions race-fix" → candidate: "leverage new Server Actions guarantees in <existing flow>"
- **feedback.md** → "user wants dark mode" → candidate: "dark mode"

Cluster near-duplicates into single candidates. If 3 sources mention the same idea, that's a single candidate with 3 supporting signals (and a higher impact score).

Cap at 12 distinct candidates. If more than 12, drop the ones with the weakest single-source signals.

### Step 5 — Atlas-history filter

For each candidate, compare to recent Atlas entries (last 60 days):

- If `outcome == "shipped"` and title is a near-duplicate → **skip** (don't double-ship)
- If `outcome == "rejected"` and title is a near-duplicate → **demote** (will likely fail re-scoring; explicit Atlas-rejection note in the rationale)
- Otherwise → **keep**

### Step 6 — score each candidate via `/vibe-iterate-rate`

For each remaining candidate, call `/vibe-iterate-rate "<candidate>" --silent`. Capture the structured scores (impact, fit-with-stack, effort, regression-risk, user-trust-impact, total, verdict, evidence).

Sort by total score descending. Ties broken by lowest-effort-score (5 = quickest win wins).

### Step 7 — pick the top candidate

Top candidate = highest total score. Surface the top 3 to the user with a recommendation:

```
Candidates (top 3 of <N> scored)

1. <title>  (total: <N>/25)  ← recommended
   - Sources: <competitor changelog | feedback.md line N | framework release | etc.>
   - Verdict: <ship-now | queue>

2. <title>  (total: <N>/25)
   - Sources: ...
   - Verdict: ...

3. <title>  (total: <N>/25)
   - Sources: ...
   - Verdict: ...

Other candidates considered: <list of titles only — no scores>

Ship #1, pick another (give number), or pause? (1 / pick / pause)
```

Wait for user response.

### Step 8 — Cart-detection (heavy iteration check)

For the chosen candidate, check the effort score:

- If effort score is 1 (touches >3 subsystems, new domain concept, or >1 week) → **heavy iteration**
- Apply Cart-detection logic from AGENTS.md § Cart-detection:
  - **Cart present** → ask: *"This iteration is heavy. Delegate scope/prd/spec to vibe-cartographer first? (yes — delegate / no — proceed with light flow)"*. Wait.
  - **Cart absent** → surface the discovery upsell: *"This iteration would benefit from Cart's structured `/scope → /prd → /spec` flow. Install vibe-cartographer (`/plugin install vibe-cartographer`), or proceed with vibe-iterate's lighter flow?"*. Wait.

If user opts to delegate to Cart, the rest of this mode runs through Cart's flow (scope → prd → spec → return) before invoking the build phase.

### Step 9 — build (or delegate, then build)

If light flow: invoke the same build phase as `/vibe-iterate-ship` (with the chosen candidate's title + rationale as the brief). Reuse the `/vibe-iterate-ship` SKILL's procedure for steps 4-7 (pre-flight tests, implement, post-flight tests, open PR).

If delegated to Cart: hand the candidate's title to `vibe-cartographer:scope`. Take its output, hand to `prd`, then `spec`. Take Cart's spec back. Run vibe-iterate's build phase against the spec.

### Step 10 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "feature-add",
  "outcome": "shipped",
  "title": "<chosen candidate title>",
  "rationale": "Top-scored candidate (<N>/25). Sources: <list>. Cart-detection: <light flow | delegated to vibe-cartographer | user declined upsell>. <one-line on regression posture>.",
  "rejected_runners_up": ["<runner-up 1 title>", "<runner-up 2 title>", ...],
  "pr": "<PR URL>"
}
```

If user paused at step 7, write Atlas with `outcome: "queued"`, `pr: null`, and rationale capturing why (so future invocations don't re-propose the same thing).

If user declined mid-build at step 9, write Atlas with `outcome: "rejected"`, `pr: null`.

Validate against `.agent/skills/vibe-iterate-guide/schemas/atlas-entry.schema.json` before writing.

### Step 11 — close out

```
Shipped:
- Feature: <title>
- PR: <url>
- Atlas: <.vibe-iterate/atlas.jsonl> (entry appended; runners-up logged)
- Sources picked from: <list>
- Cart-detection: <light flow | delegated | user declined upsell>
- Tests: <pre N/N → post N/N>  [<N> regressions if any]

Next:
- Re-run /vibe-iterate-feature-add to ship the next one
- Or /vibe-iterate to get a fresh mode recommendation
```

## Anti-patterns

- **Don't ship parity-driven features.** Just because a competitor shipped X doesn't mean we should — that's `competitive` mode's failure case. `feature-add` is candidate-driven, multi-source, fit-scored.
- **Don't skip the Atlas-history filter.** Re-shipping a recently-shipped feature wastes the user's time and corrupts the Atlas's history value.
- **Don't expand to a multi-PR sprawl.** If the chosen candidate turns out to be heavier than scored, surface that and trigger Cart-detection — don't quietly grow.
- **Don't gold-plate the rationale.** Atlas rationale is one paragraph max; PR description is the full prose.

## Cross-references

- Sidecars called: `/vibe-iterate-radar`, `/vibe-iterate-scan-releases`, `/vibe-iterate-rate`, `/vibe-iterate-ship` (for the build phase)
- Cart-detection: AGENTS.md § Cart-detection
- Posture: AGENTS.md § Posture
- Atlas conventions: `.agent/skills/vibe-iterate-guide/references/atlas-conventions.md`
- Schema: `.agent/skills/vibe-iterate-guide/schemas/atlas-entry.schema.json`
