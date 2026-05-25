---
description: "Run when the user says /competitive and wants to ship a feature based on what competitors have shipped. Scans competitor changelogs/releases, diffs against your shipped features, ranks gaps by strategic relevance (not parity), picks one, ships one PR + Atlas entry naming what we did and didn't copy."
---

# /competitive — what do they have that we don't?

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Scans every URL in `config.competitors[]` via `/spy --silent`, diffs the union of competitor features against what the user's product ships today, identifies gaps, **ranks gaps by strategic relevance — not parity**, picks one, and ships it.

The strategic-relevance call is the value. "Competitor X shipped Y" is data; "Y matters for OUR users because Z" is the iteration. Ptolemy refuses to ship parity for parity's sake.

## Hard rules

- **One PR per invocation.** Same as feature-add.
- **Strategic relevance > parity.** Every gap gets one of three labels: **match** | **differentiate** | **decline**. The label is the call.
- **Cite the competitor URL** for every gap surfaced. The user should be able to click through to verify.
- **Atlas write is mandatory.** Includes the full diff (matched gaps, differentiated gaps, declined gaps) — not just the chosen one.

## Session + friction logging

At workflow start — load the `session-logger` skill (`.agent/skills/session-logger/SKILL.md`) and run `start("competitive", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `friction-logger.log()` invocation.

At workflow end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })` per the schema.

Honor the friction trigger map at `.agent/skills/guide/references/friction-triggers.md` — section `/competitive` — for which friction types to log at which confidence.

## Inputs

- **No required arguments.** Optional `--url <url>` to add a one-off competitor URL not in `config.competitors[]` (useful for scratch-pad competitive reads).
- **Project state required:** `.vibe-iterate/config.json` (for `category` and `competitors[]`). If absent, hand off to bootstrap. If `competitors[]` is empty, surface: *"No competitors configured. Add some via `/bootstrap` (or hand-edit `.vibe-iterate/config.json`), or pass `--url <url>` for a one-off scan."*

## Procedure

### Step 1 — posture announcement

> *Competitive mode → conservative on copy, aggressive on differentiation. Reading their pages, diffing against what we ship, calling each gap match/differentiate/decline.*

### Step 2 — Cart-detection (early read)

Per AGENTS.md § Cart-detection, check whether `vibe-cartographer` workflows/skills are available in this Antigravity workspace (read-only; never invoke one as a probe). Note: present | absent. Decision deferred to step 8.

### Step 3 — scan competitors (parallel)

For each URL in `config.competitors[]` (plus `--url` if passed), call `/spy <url> --silent`. Capture each spy output as a structured object with `shipped_features[]`, `positioning`, `audience`, `gaps_left_open`, etc.

If `/spy` fails for a URL (404, paywall, network), surface it once at the bottom of the diff — don't fail the whole mode.

### Step 4 — build the union of competitor features

Aggregate all `shipped_features[]` across all spy outputs. Deduplicate near-duplicates (e.g., "saved searches" from Notion + "saved filters" from Obsidian → one entry: `saved searches/filters`).

For each unique feature, capture: `feature`, `competitors_with_it[]` (list of URLs), `frequency` (how many competitors shipped it).

### Step 5 — diff against the user's product

For each unique competitor feature, mark:

- **We have it** — verify by reading the codebase. Check for plausible code paths (route names, function names, README mentions). If found, log as "have it; here's where" with file references.
- **We have something different addressing the same need** — note our version.
- **We don't have it** — this is a gap.

Don't claim "we have it" without evidence — false claims here corrupt the diff.

Build the gaps list (everything tagged "we don't have it").

### Step 6 — strategic relevance scoring (per gap)

For each gap, apply the three-tier rubric:

**Match** — gap closes a feature parity our users actually expect.
- Anchor: the user's `category` description names this capability OR multiple competitors ship it (frequency ≥ 2) AND it's table-stakes for the category.
- Example: a note-taking app missing search. Match.

**Differentiate** — they shipped X; we should ship Y instead because it's more aligned with our positioning.
- Anchor: their feature solves a need that exists in our user base, but their solution doesn't fit our positioning. Propose a different solution that does.
- Example: competitor shipped "AI-tagging" with manual review. Our positioning is "no AI in the loop." We could differentiate with "saved smart-folders that anyone-can-edit" — addresses the same need (organization) without violating our positioning.

**Decline** — gap is real but not relevant to us.
- Anchor: their feature targets an audience we don't serve, OR addresses a need our positioning explicitly rejects, OR is so niche our users wouldn't notice.
- Example: competitor shipped enterprise SSO. We're a single-user tool. Decline.

For each gap, also call `/rate "<gap-as-iteration>" --silent` to get effort + regression-risk + user-trust-impact scores. Strategic-relevance label is the headline; the `/rate` scores inform feasibility.

### Step 7 — pick the top match-or-differentiate gap

Among `match` and `differentiate` gaps (skip `decline` for picking purposes), sort by `/rate` total score descending. Top entry is the recommendation.

Surface to the user:

```
Competitive scan results — <N> URLs scanned, <N> gaps identified

Match (close the parity)
- <gap title>  ← Competitors: <urls>  |  Score: <N>/25
- ...

Differentiate (their feature, our angle)
- <gap title> → propose: <our-version description>  ← Competitors: <urls>  |  Score: <N>/25
- ...

Decline (not for us)
- <gap title> ← <one-line rationale why>
- ...

Recommendation: ship #1 (<title>) — <match | differentiate>

Ship #1, pick another (give label + number), or pause? (1 / pick / pause)
```

Wait for user response.

### Step 8 — Cart-detection (heavy iteration check)

Same as feature-add step 8. If chosen gap is heavy (effort score = 1), surface Cart-delegation prompt (if Cart present) or discovery upsell (if Cart absent).

### Step 9 — build (or delegate, then build)

Same as feature-add step 9 — invoke `/ship`-style build, OR delegate to Cart's `/scope → /prd → /spec → return → build`.

If the chosen gap was a `differentiate`, the brief explicitly names: (a) what the competitors did, (b) what we're doing instead, (c) why our version aligns with our positioning.

### Step 10 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "competitive",
  "outcome": "shipped",
  "title": "<chosen gap title>",
  "rationale": "Strategic relevance: <match | differentiate>. Competitors with this feature: <urls>. <if differentiate: our version: ...>. Cart-detection: <light | delegated | declined>. Total /rate score: <N>/25.",
  "rejected_runners_up": ["<other match/differentiate gaps not picked>", "<decline gap titles for the historical record>"],
  "pr": "<PR URL>"
}
```

The `rejected_runners_up` array captures BOTH the unpicked match/differentiate gaps AND the declined gaps. Future invocations of `competitive` (or `feature-add`) read this to avoid re-proposing.

If user paused at step 7: `outcome: "queued"`, `pr: null`. If user declined mid-build at step 9: `outcome: "rejected"`, `pr: null`.

### Step 11 — close out

```
Shipped (competitive):
- Gap closed: <title>  (<match | differentiate>)
- PR: <url>
- Atlas: <.vibe-iterate/atlas.jsonl> (full diff logged)
- Competitors scanned: <N>
- Gaps identified: <N total: M match / D differentiate / X decline>
- Cart-detection: <light | delegated | declined>
- Tests: <pre N/N → post N/N>

Next:
- Re-run /competitive to close another gap
- Or /spy <url> for a one-shot read on a new competitor
```

## Anti-patterns

- **Don't ship parity for parity's sake.** "They shipped it, so we should" is the failure mode. Every gap gets a strategic-relevance label, including `decline`.
- **Don't claim "we have it" without code evidence.** False parity claims poison the diff.
- **Don't surface declined gaps as missed opportunities.** They're declined for a reason; surface them in Atlas (for the record) but not as recommendations.
- **Don't auto-fire build.** User confirms the chosen gap before the build phase starts.

## Cross-references

- Sidecars called: `/spy`, `/rate`, `/ship` (for build phase)
- Cart-detection: AGENTS.md § Cart-detection
- Atlas conventions: `.agent/skills/guide/references/atlas-conventions.md`
- Sibling: `/feature-add` — multi-source candidate-driven; this mode is competitor-driven only
