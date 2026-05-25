---
description: "Run when the user says /bug-bash and wants to fix the highest-priority user-reported bug. v1.0: reads feedback.md only. Triages by severity x frequency x blast-radius, reproduces, ships the fix as one PR + Atlas entry. Dormant for repos without feedback.md (surfaces a one-line nudge to add one)."
---

# /bug-bash — what's broken according to users?

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Reads user-reported bugs from `feedback.md`, triages them by severity × frequency × blast-radius, picks the highest-priority bug, reproduces it, and ships the fix as one PR. Atlas entry captures the bug, the reproduction, and the fix.

v1.0 reads ONLY `feedback.md`. Real connectors (GitHub Issues, Discord, 626Labs Dashboard, in-app feedback widget) are deferred to v1.1.

## Hard rules

- **One bug per invocation.** Don't bundle. The next invocation gets the next bug.
- **Reproduce before fixing.** If you can't reproduce locally, don't ship a "fix" — surface that the bug needs more info from the user, log to Atlas as `queued` with a note.
- **Cite the feedback line.** Every triaged bug references the `feedback.md` line that surfaced it.
- **Test the fix.** A bug-fix PR with no test that exercises the bug is a liability. Add a regression test as part of the fix unless the bug is genuinely untestable (UI rendering on a specific device, etc.) — and even then, add a manual-verification step to the PR.

## Session + friction logging

At workflow start — load the `session-logger` skill (`.agent/skills/session-logger/SKILL.md`) and run `start("bug-bash", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `friction-logger.log()` invocation.

At workflow end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })` per the schema.

Honor the friction trigger map at `.agent/skills/guide/references/friction-triggers.md` — section `/bug-bash` — for which friction types to log at which confidence. Note: a user request to skip the regression test is a HIGH-confidence `default_overridden` signal (hard rule violation).

## Inputs

- **No required arguments.** Optional `--id <N>` to target a specific feedback line by number (1-indexed).
- **`feedback.md`** at the project root. Schema: freeform markdown — vibe-iterate parses lines starting with one of: `bug:`, `issue:`, `broken:`, `[bug]`, `[issue]`, or any line tagged `BUG`. Items can include severity tags like `[critical]`, `[major]`, `[minor]` (case-insensitive).
- **`.vibe-iterate/config.json`** for category context. If absent, hand off to bootstrap.

## Dormant case (no `feedback.md`)

If `feedback.md` is **absent** at the project root, surface this exact one-line nudge and exit:

```
Bug-bash needs internal signal. Two options:
- Create feedback.md at the project root and add user-reported bugs (one per line, optional [severity] tag)
- Wait for v1.1 — real connectors (GH Issues, Discord, in-app widget) coming

For now: /vibe-iterate to get a different mode recommendation.
```

Don't auto-create `feedback.md` — that's the user's call.

## Procedure

### Step 1 — posture announcement

> *Bug-bash mode → conservative posture, smallest-diff fix, regression checks aggressive. Reading feedback, triaging, reproducing, fixing ONE.*

### Step 2 — read and parse `feedback.md`

Extract bug lines per the schema above. For each, capture:

- `id` — line number in feedback.md
- `text` — verbatim line content (without the `bug:` / `[bug]` prefix)
- `severity` — extracted from `[critical|major|minor]` tag if present; default `medium` if no tag

If `--id <N>` was passed, filter to just that line. If line N isn't a bug entry, surface: *"Line N doesn't look like a bug entry (no bug/issue/broken prefix or [bug] tag). Did you mean line M?"*.

### Step 3 — triage (severity × frequency × blast-radius)

For each bug entry:

**Severity** (per the [tag] OR Ptolemy's read of the text):
- `critical` — data loss, security, app unusable, payment/auth broken — score 5
- `major` — primary feature broken or visibly wrong — score 4
- `medium` — non-primary feature broken; workaround exists — score 3
- `minor` — cosmetic; rare path; easy workaround — score 2
- `unclear` (text doesn't make severity obvious) — score 3 default; flag for user clarification

**Frequency** (how often this affects users):
- Multiple feedback.md mentions of the same/near-duplicate bug → frequency 5
- Single mention but text says "every time" / "always" → frequency 4
- Single mention, intermittent → frequency 3
- Single mention, edge case → frequency 2

**Blast-radius** (how many users affected):
- All users on the affected flow → score 5
- Most users (common configuration) → 4
- Some users (specific configuration) → 3
- Few users (rare environment / edge case) → 2

Compute priority: `severity + frequency + blast_radius` (max 15).

### Step 4 — pick the top bug

Sort by priority descending. Surface top 3 to user:

```
Bugs from feedback.md — <N> entries triaged

1. <one-line bug summary>  (priority <N>/15)  ← line <id>: "<verbatim>"
   - Severity: <tier>  | Frequency: <tier>  | Blast-radius: <tier>

2. <one-line bug summary>  (priority <N>/15)  ← line <id>: "<verbatim>"
   - Severity: <tier>  | Frequency: <tier>  | Blast-radius: <tier>

3. <one-line bug summary>  (priority <N>/15)  ← line <id>: "<verbatim>"
   - Severity: <tier>  | Frequency: <tier>  | Blast-radius: <tier>

Other bugs queued: <count>

Recommendation: fix #1 (<title>)

Fix #1, pick another (give number), or pause? (1 / pick / pause)
```

Wait for user response.

### Step 5 — reproduce

Try to reproduce the chosen bug locally. Steps:

1. Read the bug text and infer the affected surface (route, function, command, flow).
2. Find the code path. Read 2-3 relevant files.
3. Construct a minimal reproduction:
   - For a UI bug: identify the route/component, the user action, the expected behavior, the actual broken behavior.
   - For a backend bug: identify the input shape, the expected output, the actual broken output.
   - For a CLI bug: construct the exact command + flags + input that triggers it.
4. Run the reproduction. Capture: did it reproduce? what was the broken behavior?

If you **cannot reproduce**:

```
Couldn't reproduce <bug title>:
- What I tried: <reproduction steps>
- What I expected: <broken behavior per feedback>
- What I got: <actual behavior — possibly working as intended>

Possible causes:
- Bug needs specific input/configuration not in feedback.md
- Bug is intermittent (race condition, timing-dependent)
- Bug was fixed since the feedback was reported
- Misread of feedback.md text

Action: log to Atlas as `queued` with note for follow-up; ask user for repro steps before fixing? (yes / try a different bug / pause)
```

If user says yes, write a `queued` Atlas entry and exit. If user says try a different bug, return to step 4 with the chosen bug demoted.

### Step 6 — fix

Once reproduced, implement the fix. Apply Ptolemy's posture:

- **Smallest diff that fixes the bug.** Resist drive-by cleanups.
- **Add a regression test** that exercises the bug. The test must FAIL on the buggy code and PASS on the fixed code. Run it both ways to confirm.
- **No surprise behavior change.** If fixing the bug changes behavior users may rely on (even broken behavior), name it in the PR description.

### Step 7 — pre-flight + post-flight tests

Per AGENTS.md § Posture. The new regression test from step 6 should pass; existing tests should still pass.

### Step 8 — open the PR

PR description shape:

```markdown
## Summary
Fix: <bug title>

## Bug
- Reported in: `feedback.md:<line-id>` — "<verbatim feedback text>"
- Severity: <tier>  | Frequency: <tier>  | Blast-radius: <tier>  | Priority: <N>/15

## Reproduction
<numbered steps to reproduce on the broken code>

Expected: <expected behavior>
Actual (broken): <actual behavior>

## Fix
<one-paragraph explanation of the fix>

## Test plan
- [x] New regression test added: <test file path>:<test name>
- [x] Test fails on buggy code, passes on fixed code
- [x] Pre-flight tests: <N pass / N fail>
- [x] Post-flight tests: <N pass / N fail>

## Behavior change
<if the fix changes behavior users may have relied on — name it; otherwise: "None — fix matches the feature's documented intent">

🤖 Generated with [vibe-iterate](https://github.com/estevanhernandez-stack-ed/vibe-iterate) /bug-bash
```

### Step 9 — update `feedback.md`

After the PR opens, update `feedback.md` to mark the addressed line:

- Prefix the addressed line with `[fixed in PR #N]` (where N is the PR number)
- Don't delete the line — the historical record matters

Surface the change in the close-out: *"Updated feedback.md:<line-id> with `[fixed in PR #N]`."*

### Step 10 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "bug-bash",
  "outcome": "shipped",
  "title": "Fix: <bug title>",
  "rationale": "Severity <tier>, frequency <tier>, blast-radius <tier> (priority <N>/15). Repro: <one-line>. Fix: <one-line>. Regression test added.",
  "rejected_runners_up": ["<other top-3 bugs not picked, as titles>"],
  "pr": "<PR URL>"
}
```

If user paused: `outcome: "queued"`, `pr: null`. If couldn't reproduce: `outcome: "queued"`, `pr: null`, rationale captures the repro attempt.

### Step 11 — close out

```
Fixed:
- Bug: <title>
- PR: <url>
- Atlas: <.vibe-iterate/atlas.jsonl> (entry appended)
- feedback.md updated: line <id> tagged [fixed in PR #N]
- Regression test: <test file path>:<test name>
- Tests: <pre N/N → post N/N>

Other bugs queued: <count>
Next:
- Re-run /bug-bash to fix the next bug
- Or /vibe-iterate to get a fresh mode recommendation
```

## Anti-patterns

- **Don't ship a fix you couldn't reproduce.** "Probably this fixes it" is not a fix. Reproduce first.
- **Don't skip the regression test.** A bug fix without a test that catches the original bug is a liability.
- **Don't bundle multiple bug fixes.** One bug per PR. Reviewability and rollback matter.
- **Don't delete addressed lines from feedback.md.** Tag them. Historical record matters for the user and for future bug-bash invocations.
- **Don't auto-create feedback.md.** That's the user's call. The dormant nudge is the right move when the file's missing.

## Cross-references

- Sidecar called: `/rate` (optional — for effort/risk scoring on the chosen bug), `/ship` (for build phase)
- Posture: AGENTS.md § Posture
- Atlas conventions: `.agent/skills/guide/references/atlas-conventions.md`
- Schema: `.agent/skills/guide/schemas/atlas-entry.schema.json`
