---
description: "Run when the user says /ship <brief> and wants to skip ingestion and ship from a hand-written brief. Takes a markdown brief (file path or inline prompt), runs the build with regression-aware/small-diff posture, ships one PR + Atlas entry. Bypasses the signal-ingestion phase for users who already know what they want."
---

# /ship <brief> — skip ingestion, ship from a brief

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Takes a brief (a markdown file path OR an inline string) and runs Ptolemy's build phase directly — no candidate clustering, no scoring, no Atlas-history check. The user already knows what they want; `/ship` is the express lane.

Posture is unchanged from a banner mode: regression-aware, user-trust-aware, small-diff-preferred. Cart-detection still triggers if the brief describes a heavy iteration. Atlas entry still gets written when the PR opens.

## Hard rules

- **One PR per invocation.** Same as the banner modes. If the brief implies multiple PRs, surface that *before* starting work and ask the user to split the brief.
- **Run the existing test suite.** Before opening the PR. Per the regression-aware default in AGENTS.md § Posture. If a regression surfaces, name it explicitly in the PR description and ask the user to acknowledge before merging.
- **Atlas write is mandatory.** Every `/ship` invocation that opens a PR (or that the user explicitly declines mid-build) writes an Atlas entry with `mode: "ship"`.
- **Cart-detection still applies.** If the brief describes a heavy iteration, surface the Cart-delegation upsell (or auto-delegate if Cart's installed) per AGENTS.md § Cart-detection.

## Session + friction logging

At workflow start — load the `session-logger` skill (`.agent/skills/session-logger/SKILL.md`) and run `start("ship", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `friction-logger.log()` invocation.

At workflow end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })` per the schema.

Honor the friction trigger map at `.agent/skills/guide/references/friction-triggers.md` — section `/ship` — for which friction types to log at which confidence. Note: a user request to skip the test run is a HIGH-confidence `default_overridden` signal.

## Inputs

- **`$1`** — required. Either:
  - A file path (e.g., `briefs/saved-search.md`) — read the file as the brief.
  - An inline string (e.g., `"add a saved-search button to the header that lets users save the current filter state"`) — use as the brief verbatim.

If `$1` is absent, prompt: *"Brief? (paste the brief inline, or pass a file path to a markdown brief)"* and wait.

- **Project state** — `.vibe-iterate/config.json` (for `category` context — used by Ptolemy's posture-switch announcement and to inform code conventions). If absent, surface: *"No vibe-iterate config — running with codebase-only context. Run /vibe-iterate first to set up project context for stronger results."* Continue (don't block).

## Procedure

### Step 1 — posture announcement

> *Ship mode → conservative posture. I'm reading your brief, then building with regression checks aggressive and the smallest diff that delivers the value.*

If the brief looks heavy (judgment call — see Cart-detection threshold), add:

> *This brief touches [specific reasons]. I'd recommend running scope/prd/spec before building. [If Cart installed:] Want me to delegate to vibe-cartographer first? [If Cart missing:] Install vibe-cartographer for a stronger flow, or proceed with the lighter ship-direct flow?*

Wait for user response if you surface the Cart prompt.

### Step 2 — read and parse the brief

Read the brief (file or inline). Extract:

- **Goal** — what the iteration delivers (one line)
- **Scope** — files / surfaces / subsystems involved
- **Acceptance** — how we know it's done (tests, manual checks, visible behavior)
- **Out of scope** — anything explicitly excluded (often missing — that's fine)

If the brief is too vague to identify these, ask ONE clarifying question to fill the gap. Don't ask three. If you can't extract any of them, ask: *"This brief needs a one-line goal — what's the win condition?"* and wait.

### Step 3 — heavy-iteration check

Apply the Cart-detection heuristic:

- Touches 3+ subsystems? OR
- Introduces a new domain concept (new table, new model, new shape)? OR
- Estimated >1 day of focused senior-engineer work?

If yes AND user hasn't already responded to the heavy-iteration prompt in step 1, surface it now and wait. If yes AND user said proceed, proceed. If no, continue.

### Step 4 — pre-flight test run

Run the existing test suite as it stands today. Capture pass/fail. If any tests fail BEFORE you've made changes, surface:

```
Pre-existing test failures detected:
- <test name>
- <test name>

These predate this iteration. Proceed anyway (changes may not be the cause), or pause to investigate?
```

Wait for user response. If "proceed anyway," continue but flag in PR description: *"Pre-existing failures: [list] — not introduced by this PR."*

### Step 5 — implement

Implement per the brief. Apply the three posture defaults:

- **Regression-aware** — keep the diff small enough to reason about; don't refactor unless refactor IS the value.
- **User-trust-aware** — if the change alters a user-facing surface, the PR description must name the change and propose a deprecation path (when applicable).
- **Small-diff-preferred** — minimum viable change. Avoid drive-by cleanups.

Use the project's existing conventions, not 626Labs defaults. Read 2-3 existing files in the same neighborhood to learn local style before adding new files.

### Step 6 — post-flight test run

Run the test suite again. Diff results vs. step 4:

- **Net new failures** = regressions caused by this iteration. Surface them, fix or document.
- **Previously failing tests now passing** = unexpected wins. Note them.
- **All previously passing tests still passing** = green light.

If new failures exist and you can't fix them in this PR's scope, the PR description must name them and propose a follow-up.

### Step 7 — open the PR

Use `gh pr create` with this body shape:

```markdown
## Summary
<one-paragraph description of what shipped and why, derived from the brief>

## Changes
- <bulleted list of file-level changes>

## Brief
<the original brief, verbatim — file path link OR inline quote>

## Test plan
- [x] Existing test suite passes (pre-flight: <N pass / N fail>; post-flight: <N pass / N fail>)
- [ ] <manual verification step from brief acceptance criteria>

## Breaking changes
<if any — name them; otherwise: "None.">

## Migration path
<if breaking changes — describe the deprecation path; otherwise omit>

## Cart-detection
<if delegated to Cart: link to scope.md / prd.md / spec.md; otherwise: "Light flow (own muscle)">

🤖 Generated with [vibe-iterate](https://github.com/estevanhernandez-stack-ed/vibe-iterate)
```

### Step 8 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "ship",
  "outcome": "shipped",
  "title": "<one-line iteration title from brief goal>",
  "rationale": "Hand-written brief; bypassed signal ingestion. <one-line note on Cart-detection outcome and any regression notes>.",
  "rejected_runners_up": [],
  "pr": "<PR URL from step 7>"
}
```

Validate against `.agent/skills/guide/schemas/atlas-entry.schema.json` before writing.

If user declines mid-build (says "stop, not this"), still write an Atlas entry with `outcome: "rejected"` and `pr: null`, with the rationale capturing why. Don't leave the iteration unlogged — the Atlas's purpose is to remember even the things that didn't ship.

### Step 9 — close out

```
Shipped:
- PR: <url>
- Atlas: <.vibe-iterate/atlas.jsonl> (entry appended)
- Pre-flight tests: <N pass / N fail>
- Post-flight tests: <N pass / N fail>
- Cart-detection: <light flow | delegated to vibe-cartographer | user declined upsell>
```

If a regression is unfixed in this PR, repeat the regression line at the bottom in **bold** so the user can't miss it.

## Anti-patterns

- **Don't ingest signals.** That's the banner modes' job. `/ship` is the express lane — if the user wanted ingestion, they'd have invoked `feature-add`.
- **Don't skip the test run.** Even on a tiny change. The regression-aware default is non-negotiable.
- **Don't expand scope.** If you discover the brief understates the work, surface that to the user — don't quietly grow the diff.
- **Don't merge.** PR opens; merge is the user's call (per Ptolemy's user-trust-aware posture).

## Cross-references

- Posture: AGENTS.md § Posture
- Cart-detection: AGENTS.md § Cart-detection
- Atlas conventions: `.agent/skills/guide/references/atlas-conventions.md`
- Schema: `.agent/skills/guide/schemas/atlas-entry.schema.json`
- Sibling: `/upgrade` — express lane for library bumps specifically
