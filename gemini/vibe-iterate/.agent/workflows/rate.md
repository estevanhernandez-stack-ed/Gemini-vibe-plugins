---
description: "Run when the user says /rate <idea> and wants to score a feature idea against their shipped product. Reads the codebase + Atlas, scores on impact, fit-with-stack, effort, regression-risk, user-trust-impact. Outputs scores + rationale + ship-now/queue/decline verdict. Used internally by every banner mode to rank candidates."
---

# /rate <idea> — score a feature idea against your shipped product

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Takes a one-line idea (`"add saved searches"`, `"add dark mode"`, `"AI-powered tagging"`) and scores it against the shipped product. The user gets back five scores, a one-paragraph rationale, and a one-line verdict — *ship-now / queue / decline*.

Used standalone by anyone who already has an idea and wants a sanity check before committing to it. Used internally by every banner mode to rank candidates against each other.

## Hard rules

- **Read-only.** This workflow does NOT write to the Atlas, the config, or any project file.
- **No mode auto-fire.** A `ship-now` verdict is a recommendation, not an invocation. The user kicks off `/ship` or `/feature-add` if they want to act on it.
- **Score with evidence, not vibes.** Each score is anchored to a specific signal (a file, a commit, a competitor URL, a framework feature, an Atlas entry). No score without a citation.
- **Honor recent rejections.** If the Atlas shows this idea (or a near-duplicate) was rejected in the last 60 days, surface that prominently — verdict skews `decline` unless the rationale has materially changed.

## Inputs

- **`$1`** — the idea, as a one-line string. If the user invoked the command without an argument, prompt: *"What's the idea? (one line)"* and wait.
- **Project state** — same as the bare router reads: `.vibe-iterate/config.json`, `.vibe-iterate/atlas.jsonl`, `package.json` (or stack equivalent), recent commits.

If `.vibe-iterate/config.json` is **absent**, surface: *"No config yet. Run /vibe-iterate first to set up — or pass --no-config to score against codebase only."* Don't silently score with no context.

## Scoring rubric

Five scores, each on a **1-5 scale** (5 = strongest). Anchor every score to specific evidence.

### 1. Impact (1-5)

How much does this iteration move the user-experience needle?

- **5** — addresses a top-3 user complaint in `feedback.md`, OR closes a parity gap with a key competitor's headline feature, OR unblocks a workflow that's currently impossible
- **4** — addresses a recurring friction in feedback or commits (multiple `fix(...)` commits in the same area)
- **3** — clear win but no urgent driver; "this would be nice"
- **2** — minor improvement; affects a small subset of users
- **1** — speculative; no evidence of demand

**Evidence cites:** quote the relevant `feedback.md` line, the commit subject, or the competitor URL.

### 2. Fit-with-stack (1-5)

How well does this idea fit the existing stack and patterns?

- **5** — uses primitives already in the codebase; minor file-level changes
- **4** — needs a new module or component but follows existing patterns
- **3** — needs a new dependency or pattern shift; doable, requires some invention
- **2** — needs a major architectural choice (new database, new auth model, new framework)
- **1** — fights the current stack; would require ripping out and replacing something load-bearing

**Evidence cites:** name the relevant files / patterns / dependencies.

### 3. Effort (1-5, **inverse** — 5 = least effort)

How small is the diff?

- **5** — single-file change, <50 lines
- **4** — multi-file but bounded; <300 lines, no new tests required
- **3** — needs new tests; new module; ~1 day of focused work
- **2** — touches multiple subsystems; new database migration or schema change; ~3 days
- **1** — touches >3 subsystems OR introduces a new domain concept; >1 week (triggers Cart-detection — see AGENTS.md § Cart-detection)

**Evidence cites:** name the subsystems / files / migrations that would be touched.

### 4. Regression-risk (1-5, **inverse** — 5 = lowest risk)

How likely is this to break something already shipped?

- **5** — additive only; no changes to existing surfaces
- **4** — modifies an internal helper; existing tests cover it; no public-API change
- **3** — modifies a frequently-used internal API; tests need updating
- **2** — modifies a public API or user-facing flow; behavior change for existing users
- **1** — changes a load-bearing surface (auth, payment, data layer); breaking change risk

**Evidence cites:** name the surface (function name, route, schema field) that would change.

### 5. User-trust-impact (1-5, **inverse** — 5 = neutral or positive trust)

Does this iteration risk eroding user trust?

- **5** — pure win; no surprise to existing users; no change to behavior they rely on
- **4** — adds a new surface; opt-in; existing flows unchanged
- **3** — minor visible change (UI tweak, copy change); users will notice but won't be confused
- **2** — changes a flow users complete repeatedly (form, checkout, login); needs a deprecation path
- **1** — breaks an existing user-trust expectation (e.g., removes a feature they rely on, changes default behavior, surfaces a confusing error state)

**Evidence cites:** name the user-facing surface and the trust expectation being affected.

See the **user-trust-impact rubric** in `the `/ux-polish` workflow` for the full version of this rubric — `/rate` uses the same anchors.

## Atlas check (recent-rejection guard)

Read `.vibe-iterate/atlas.jsonl` for the last 60 days. For each entry where `outcome == "rejected"` or `outcome == "shipped"`, compare the entry's `title` to the rated idea. If the title is a near-duplicate (same noun phrase or same verb-object pair), surface it:

```
Atlas note: this idea (or a near-duplicate) was [rejected on YYYY-MM-DD | shipped on YYYY-MM-DD].
- Prior entry: "<title>"
- Rationale: "<rationale>"

[If rejected:] Verdict skews `decline` unless the new rationale materially changes the calculus.
[If shipped:] This may be a follow-up — describe what's different to avoid duplicating shipped work.
```

If no near-duplicate found, no Atlas note needed (don't pad with "no prior entries").

## Verdict logic

Compute total score (sum of 5 scores, 5-25). Apply the rubric:

| Total | Verdict | Threshold conditions |
|---|---|---|
| **22-25** | `ship-now` | All scores ≥ 4 AND no Atlas-rejection in last 60 days |
| **18-21** | `ship-now` if regression-risk ≥ 4 AND user-trust-impact ≥ 4; else `queue` | "Strong but not unanimous — queue if either trust or risk is iffy" |
| **13-17** | `queue` | "Worth doing eventually; not the move right now" |
| **5-12** | `decline` | "Not a fit. Atlas this so it's logged." |

**Atlas-rejection override:** if the Atlas check surfaced a recent rejection AND the new rationale isn't materially different, force verdict to `decline` regardless of total score.

**Cart-trigger:** if effort score is 1 (touches >3 subsystems, new domain concept, or >1 week), include in the rationale: *"This iteration triggers Cart-detection. If/when shipped, the agent should delegate `/scope → /prd → /spec` to vibe-cartographer (if installed) or surface the discovery upsell (if not)."*

## Output shape

```
Idea: <the idea, verbatim>

Scores:
- Impact:             <N>/5  ← <one-line evidence cite>
- Fit-with-stack:     <N>/5  ← <one-line evidence cite>
- Effort:             <N>/5  ← <one-line evidence cite>  (5 = lowest effort)
- Regression-risk:    <N>/5  ← <one-line evidence cite>  (5 = lowest risk)
- User-trust-impact:  <N>/5  ← <one-line evidence cite>  (5 = lowest impact)

Total: <N>/25

Rationale:
<one-paragraph synthesis — what the scores mean together, what to watch for, any Atlas notes>

Verdict: <ship-now | queue | decline>
<one-line action — e.g., "Run /ship to launch a build session." or "Queued — re-run /rate when [specific condition] changes." or "Decline — log to Atlas via /ship --decline if you want it on the record.">
```

## When invoked internally by a banner mode

When a banner mode (`feature-add`, `competitive`, `ux-polish`, `bug-bash`) calls `/rate` to rank candidates, the calling mode is responsible for:
- Passing each candidate through `/rate`
- Sorting by total score
- Honoring the Atlas-rejection override
- Picking the top candidate (with ties broken by lowest-effort-score = quickest win)

The internal call doesn't render the full output template — it just consumes the scores. The rendered template is for standalone user-invoked calls.

## Anti-patterns

- **Don't score without evidence.** "Impact: 4 (this seems important)" is a non-answer. Cite a feedback line, a commit, a competitor URL.
- **Don't ignore Atlas history.** Re-scoring a recently-rejected idea without acknowledging it wastes the user's time and the Atlas's purpose.
- **Don't gold-plate the rationale.** One paragraph, not three.
- **Don't render a verdict that contradicts the scores.** If total is 8 but you wrote `ship-now`, something's wrong — re-score or check the rubric.

## Cross-references

- Schema: `.agent/skills/guide/schemas/atlas-entry.schema.json`
- Rubric reference: `/ux-polish` — full user-trust-impact tiers
- Cart-detection: AGENTS.md § Cart-detection
- Posture (regression-aware, user-trust-aware): AGENTS.md § Posture
