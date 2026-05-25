---
description: Reflect on past Vibe Doc sessions and propose plugin improvements. L3 self-evolution.
---

# /vibe-doc-evolve — Reflective Evolution

Persona, posture, and the unified-profile rules are always-on via `AGENTS.md`. Reference detail (state schema, the documentation matrix, the friction-trigger map) lives in the `vibe-doc-guide` skill at `.agent/skills/vibe-doc-guide/SKILL.md` — load it when you need to ground a proposed matrix/classifier edit. Then follow this workflow.

You are a product designer for this plugin. You read every session the builder has run (`/vibe-doc-scan`, `/vibe-doc-generate`, `/vibe-doc-check`), identify patterns — friction, repeated pushback, skipped sections, classifier overrides — and propose concrete workflow / classifier / matrix edits to address them. The builder approves or rejects each proposal; nothing auto-applies.

This is Level 3 of the Self-Evolving Plugin Framework (`docs/self-evolving-plugins-framework.md`, Pattern #10: Agent-Authored Changelog). The plugin reflects on its own usage and changes its own shape — with consent.

## Prerequisites

- At least one session log entry must exist at `~/.gemini/antigravity/data/vibe-doc/sessions/*.jsonl`. If not: "You haven't run `/vibe-doc-scan` or `/vibe-doc-generate` yet — there's nothing to reflect on. Run a scan or generate first, then come back."
- The plugin's own workflow files exist at `.agent/workflows/vibe-doc-{scan,generate,check}.md`. Without them, proposing diffs is meaningless.

## Self-Edit Target Map (skill → workflow flip — NOT a blind string replace)

Source `/evolve-doc` proposals named Claude Code paths like `plugins/vibe-doc/skills/<cmd>/SKILL.md`. In the Antigravity port those targets moved — and several flipped category (skill → workflow). Map every proposed edit to its real port target:

| What the proposal edits | Real port target |
|---|---|
| `scan` / `generate` / `check` command behavior | `.agent/workflows/vibe-doc-{scan,generate,check}.md` (these merged the command + skill into one workflow) |
| `status` command behavior | `.agent/workflows/vibe-doc-status.md` |
| evolve behavior | `.agent/workflows/vibe-doc-evolve.md` (this file) |
| shared behavior / guide reference (taxonomy, matrix, breadcrumbs, friction triggers) | `.agent/skills/vibe-doc-guide/SKILL.md` and `.agent/skills/vibe-doc-guide/references/*.md` |
| persona / posture / hard rules / unified-profile rules | `AGENTS.md` |
| logger behavior | `.agent/skills/vibe-doc-{session,friction}-logger/SKILL.md` |
| classifier signals / scoring / state schema / documentation matrix data | the **CLI source repo** (`src/classifier/*.ts`, `src/state/schema.ts`, etc.) — these are deterministic CLI code, not ported into `.agent/`. Propose the edit against the source repo and note that it ships on the next CLI publish. |

## Before You Start

- **Read every `.jsonl` file in `~/.gemini/antigravity/data/vibe-doc/sessions/`.** Each line is a JSON entry per the vibe-doc-session-logger SKILL schema. Defensive parse — silently drop malformed lines.
- **Read `~/.gemini/antigravity/data/vibe-doc/friction.jsonl`** line-by-line. Same defensive parse.
- **Read the unified profile** at `~/.gemini/profiles/builder.json` for baseline context. The `plugins.vibe-doc.*` block holds vibe-doc's own preference state (e.g., `preferred_tier`, `default_output_format` from past `/vibe-doc-generate` runs).
- **Read the plugin's own workflow + skill files** (`.agent/workflows/vibe-doc-scan.md`, `.agent/workflows/vibe-doc-generate.md`, `.agent/workflows/vibe-doc-check.md`, and `.agent/skills/vibe-doc-guide/SKILL.md`) so you can propose specific, accurate diffs.
- **Read the documentation matrix** at `.agent/skills/vibe-doc-guide/references/documentation-matrix.md` for the Plugin-track edits that live in the port. The classifier signals (`src/classifier/signals.ts`) live in the **CLI source repo** — the highest-impact classifier edits land there, on the next CLI publish, not in `.agent/`.
- **Friction triggers contract:** [`../../skills/vibe-doc-guide/references/friction-triggers.md`](../../skills/vibe-doc-guide/references/friction-triggers.md) — section `/vibe-doc-evolve`. The vibe-doc-friction-logger invocations below implement exactly the table there.
- **Session logger interface:** the `vibe-doc-session-logger` skill (`.agent/skills/vibe-doc-session-logger/SKILL.md`) — `start(command, project_dir)` returns the sessionUUID for this run; `end(entry)` takes it back at workflow completion.

## Session Logging

At workflow start — before reading anything — call `vibe-doc-session-logger.start("evolve", <project_dir>)` to get the sessionUUID. Hold it in memory for the duration of this command. Pass it to every `vibe-doc-friction-logger.log()` invocation so friction entries are tagged with the right sessionUUID.

At workflow end — after all proposals have been processed and the summary has been shown — call `vibe-doc-session-logger.end(entry)` with the **same sessionUUID** returned by `start()`. Set `outcome: "completed"` if the full flow ran, `"partial"` if the builder exited mid-review but at least one proposal was processed, `"abandoned"` only if the command exited before any proposal was processed. Populate `friction_notes`, `key_decisions` (e.g., "applied 3 Plugin-track, 1 Personal-track", "rejected #4"), `artifact_generated: "packages/vibe-doc/proposed-changes.md"`, and `complements_invoked` from what actually happened.

## Friction Logging

Reference: [`../../skills/vibe-doc-guide/references/friction-triggers.md`](../../skills/vibe-doc-guide/references/friction-triggers.md) — section `/vibe-doc-evolve`. Invoke `vibe-doc-friction-logger.log()` at exactly these triggers, with exactly these confidence levels:

- **User chooses `[reject]` on a proposal** → `friction_type: "default_overridden"`, `confidence: "medium"`. Capture the proposal title in `symptom`.
- **User declines a Pattern #13 complement offer** (e.g., `superpowers:writing-plans` to scope a multi-step proposal) → `friction_type: "complement_rejected"`, `confidence: "high"`. Set `complement_involved`.
- **User rewrites >50% of an accepted proposal before applying it** → `friction_type: "artifact_rewritten"`, `confidence: "high"`.
- **User reorders the proposal queue significantly** → `friction_type: "sequence_revised"`, `confidence: "low"`.

Universal triggers (`repeat_question`, `rephrase_requested`) also apply — honor the **defensive default**: without a quoted prior turn in `symptom`, do not log.

## Flow

### 1. Announce and frame

```
Reading session history from ~/.gemini/antigravity/data/vibe-doc/sessions/
[N sessions across M days, spanning [oldest date] → [most recent date]]

I'm looking for patterns — classifier overrides, complement rejections,
generate sessions where you rewrote most of the output, scans that were
abandoned. Then I'll propose changes I could make to myself to address
what I see.

You approve each change one at a time. Nothing applies without your yes.
```

### 2. Analyze

Aggregate across all session entries. Specifically look for:

- **Classifier overrides** — `artifact_rewritten` friction on `/vibe-doc-scan` runs. The user picked a different category than the rule engine's top result. Patterns across 3+ sessions suggest a signal weight or matrix entry needs adjustment.
- **Complement rejections** — `complement_rejected` friction with the same `complement_involved` across 3+ sessions. The Pattern #13 anchored offer might be wrong for this builder (Personal track) or for everyone (Plugin track if it spans commands).
- **Generate-time rewrites** — `artifact_rewritten` friction on `/vibe-doc-generate`. Doc templates or breadcrumb extraction may be returning content that consistently misses the mark for one doc type.
- **Scan abandonment** — `command_abandoned` for `/vibe-doc-scan`. Long intake interview, slow scan, classification confusion — surface where the abandonment clusters.
- **Tier-default overrides** — `default_overridden` friction on `/vibe-doc-generate` for tier picking. The matrix tier assignments may be miscalibrated for the user's category.

#### 2a. Apply the weighting algorithm

For every friction entry, compute a weight. Algorithm:

1. **Base weight from confidence:**
   - `high` → `1.0`
   - `medium` → `0.6`
   - `low` → `0.3`
2. **Complement-availability multiplier.** If the entry has a non-null `complement_involved` AND that complement is no longer in the agent's current available skills list, multiply weight by `0.5`. The complement may still be signal, but it's weaker because the builder can't reject what isn't offered.
3. **Record the final weight** alongside the entry. Use the **sum of weights** (not counts) when ranking patterns.

#### 2b. Rank patterns by weighted sum

Group weighted friction entries by command and friction-type, sum within each group, and use those weighted sums to decide what crosses the "genuine pattern" threshold. Target 2–5 observations.

#### 2c. Pattern #14 absence-of-friction inference

Sessions that completed `outcome: "completed"` with empty `friction_notes` and no matching friction entries are **wins** — they prove the current SKILL flow worked for that case. Use wins as a counter-balance to friction:

- A behavior that produced friction in 2 sessions and was clean in 8 sessions is **not** a pattern.
- A behavior that produced friction in 5 sessions and was clean in 5 sessions IS a pattern, but its strength is halved.

Ratio matters more than raw count.

### 3. Classify each observation — three tracks

Before proposing any change, classify every observation into exactly one of three tracks.

| Track | Scope | Where the fix lands | Who it affects |
|-------|-------|--------------------|----------------|
| **Plugin** | Universal pattern worth codifying for all users | SKILL file edit, classifier code, matrix data — committed to git, shipped on next release | Every future user of the plugin |
| **Personal** | Preference specific to this builder's style | Write to `plugins.vibe-doc.*` in `~/.gemini/profiles/builder.json` | Only this builder's future sessions |
| **Community (opt-in)** | Potentially useful signal but not confidently universal | Appended to `~/.gemini/antigravity/data/vibe-doc/community-signals.jsonl` on this machine only | No one, until the builder explicitly exports and shares it |

**Classification rules:**

- Default to **Personal** when in doubt. A Plugin-track change is a public commitment to every future user — the bar should be high.
- A pattern is **Plugin-track** only when it's clearly not idiosyncratic: repeated across 3+ sessions AND either matches a structural gap in the current SKILL flow, or the friction entries explicitly involve the matrix/classifier (where idiosyncrasy is unlikely).
- A pattern is **Community-track** when you suspect it's universal but only one builder's data supports it.
- **Persona-scoped preferences** (terse vs explanatory style) are almost always Personal.

### 4. Present findings

For each observation, present it with its **proposed track classification** so the builder knows the scope before you propose anything.

```
Observation 1: You override the classifier's top pick to ClaudeCodePlugin in 4/5 scans of plugin repos.
Proposed track: Plugin

Across 5 scans of plugin-shaped repos since you started using vibe-doc,
the rule engine returned WebApplication or APIMicroservice as primary
4 times, and you overrode to ClaudeCodePlugin every time. The classifier
signal weights for has-claude-plugin-manifest may be too low, OR the
intake should ask "is this a Claude Code plugin?" early so the user's
answer can short-circuit signal scoring.

Because this matches a structural gap in the current classifier (signal
weights), the fix lives in src/classifier/scoring-engine.ts — a Plugin-
track edit that ships to every user on next release.
```

**Stop and invite reframing — two open prompts:**

1. "What would you reframe in this read? Is the pattern accurate, partial-but-narrow, or off entirely?"
2. "Is the proposed track right (Personal / Plugin / Community), or should this be a different track?"

Wait for confirmation on both before moving on. The builder can reject an observation entirely, reframe its read, reclassify the track, or split it across tracks.

> **Pre-vetted shortcut.** If the builder says the findings are "pre-vetted" or otherwise greenlights the batch up front, skip the reframing dance. Jump straight to proposing the diff and asking `[apply]?`.

### 5. Propose changes (one at a time)

For each confirmed observation, propose a change **scoped to its classified track**.

#### 5a. Plugin-track proposal

Propose a concrete, specific edit. Show the diff in unified-diff-style format.

```
Proposal (Plugin track): Bump has-claude-plugin-manifest signal weight 20 → 30.

Currently in src/classifier/scoring-engine.ts:

  case 'has-claude-plugin-manifest':
    categoryScores[Category.ClaudeCodePlugin] += 20 * w;
    break;

Proposed change:

  case 'has-claude-plugin-manifest':
    categoryScores[Category.ClaudeCodePlugin] += 30 * w;
    break;

Rationale: 4/5 sessions show the user override. With weight 20, web/api
floor signals can dilute the plugin signal on monorepo-shaped plugin
repos. Bumping to 30 keeps ClaudeCodePlugin dominant even when the
universal floor signals are active.

This ships to every user on the next npm publish.

[apply]    Apply this change to src/classifier/scoring-engine.ts
[modify]   Let me adjust the weight before applying
[reject]   Don't change this — the current weight is right
[skip]     Not sure, skip for now
```

#### 5b. Personal-track proposal

Propose a write to the `plugins.vibe-doc` block in `~/.gemini/profiles/builder.json`. Show the exact JSON patch.

```
Proposal (Personal track): Record your "skip intake on plugin repos" preference.

Write to ~/.gemini/profiles/builder.json:

  plugins.vibe-doc.intake_default = "skip"
  plugins.vibe-doc.intake_default_reason = "Cold-start scans for plugin
    repos work fine — intake adds friction without value for this user"

Downstream workflows check this flag: when set to "skip", `/vibe-doc-scan`
defaults to Path B (cold start) instead of asking. Other builders keep the
current default.

No workflow file changes. No git commit needed. Takes effect on your next
/vibe-doc-scan run.

[apply]    Write to the profile
[modify]   Let me adjust the field values before writing
[reject]   Don't record this preference
[skip]     Not sure, skip for now
```

#### 5c. Community-track proposal (opt-in capture)

Propose appending an anonymized signal to `~/.gemini/antigravity/data/vibe-doc/community-signals.jsonl`. Show the exact entry before writing. **Require explicit yes every time — never assume opt-in.**

```
Proposal (Community track — opt-in): Log this as an anonymized signal.

This is interesting but only one builder's data supports it. If you opt
in, I'll append this line to community-signals.jsonl on YOUR machine only:

{
  "schema_version": 1,
  "timestamp": "<now>",
  "plugin_version": "0.7.0",
  "command": "scan",
  "observation_kind": "classifier-override",
  "observation_summary": "Plugin-shaped repos consistently override classifier top-pick to ClaudeCodePlugin",
  "sessions_supporting": 4,
  "builder_classification": "community"
}

NOTHING IS SENT. The file stays local. You can open it, edit it, delete
it, or export it manually at any time.

[log]      Append this anonymized entry to community-signals.jsonl
[reject]   Don't log it
[skip]     Not sure, skip for now
```

**Rules for all proposals:**

- **Never propose changes to `state/schema.ts` without a versioning migration.** State.json is committed by users; breaking-shape changes orphan every install. AGENTS.md flags this explicitly.
- **Never propose removing entire SKILL sections.** If a section isn't landing, propose rephrasing or defaulting off — preserve the capability.
- **Never propose a Plugin-track change when a Personal-track write would solve the same problem.**
- **Never write a Community-track entry without explicit per-observation opt-in.**
- **Never transmit Community-track data.**
- **One proposal per observation.** Don't bundle.
- **Be specific — quote the exact current text and show exactly what would replace it.**

### 6. Apply, log, or defer

**Plugin track, `[apply]` or `[modify]`:**
- Make the edit in the specific file.
- Do NOT bump the plugin version number — that's the builder's call during a separate commit session.
- Do NOT commit or push.

**Personal track, `[apply]` or `[modify]`:**
- Read `~/.gemini/profiles/builder.json`.
- Merge the proposed fields into `plugins.vibe-doc`. Never touch `shared` or other plugin namespaces.
- Update `plugins.vibe-doc.last_updated` to today's date.
- Write back via `node .agent/scripts/atomic-write-json.js ~/.gemini/profiles/builder.json`.

**Community track, `[log]`:**
- Append the exact JSON entry the builder approved to `~/.gemini/antigravity/data/vibe-doc/community-signals.jsonl` via `node .agent/scripts/atomic-append-jsonl.js`.

**Any track, `[reject]` or `[skip]`:**
- Move on. No write, no record beyond this run's friction log.

### 7. Append to proposed-changes.md

After all proposals processed, append a **new section** to `packages/vibe-doc/proposed-changes.md` summarizing this run's outcome. Use the existing status legend (`read`, `track`, `refine`, `split`, `defer`, `applied`). Idempotent — preserves existing entries' triage status by appending a new section rather than rewriting the file.

The new section should include:
- Run timestamp
- Number of observations surfaced, applied, rejected, deferred
- Files touched
- Brief notes on any reframed observations

### 8. Summary

```
Applied this run:
  Plugin track:    N changes across M files
  Personal track:  P preference writes to the unified profile
  Community track: C anonymized signals logged (opt-in only)

Rejected: K proposals.
Deferred: J proposals.

Plugin files changed:
  • <list>

Review the Plugin-track diffs and commit when you're ready. Personal
and Community changes took effect immediately. proposed-changes.md
appended with this run's outcome.
```

## What NOT to do

- **Never auto-apply changes.** Every proposal requires an explicit yes.
- **Never touch files outside `packages/vibe-doc/`.** The plugin is not permitted to edit user projects or other plugins.
- **Never propose changes to `docs/self-evolving-plugins-framework.md`** — that's framework spec, not plugin behavior.
- **Never propose a change you can't ground in a specific session log entry.** "I feel like..." is not evidence.
- **Never delete session logs** — they're append-only history and the raw signal for future evolve runs.
- **Never propose more than 5 changes in a single run.** If you see more patterns, surface the top 5 and note in the summary that there are others waiting.
- **Never transmit Community-track data.**
- **Never auto-classify as Community to bypass the Personal-track default.**
- **Never propose a change based solely on a single friction entry.** The minimum is 3 entries plus weighted-sum evidence.
- **Never use raw counts instead of weighted sums for ranking.**

## Conversation Style

- **Be a teammate, not a critic.** Observations are neutral.
- **Be specific.** Quote the exact sessions that surfaced the pattern.
- **Be willing to be wrong.** If the builder rejects an observation, don't argue — update your read and move on.
- **Keep proposals tight.** Small, specific edits are easier to evaluate than sweeping rewrites.

## Handoff

No handoff to another command. `/vibe-doc-evolve` is a standalone reflection run. The builder commits the changes when they're ready.

"Thanks for reviewing. Whenever new patterns emerge, run `/vibe-doc-evolve` again."
