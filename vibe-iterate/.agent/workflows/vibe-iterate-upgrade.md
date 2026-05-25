---
description: "Run when the user says /vibe-iterate-upgrade <package> and wants to surgically bump one library to its latest version with codemods if available. Reads release notes via /vibe-iterate-scan-releases, runs the codemod if one exists, runs the test suite, ships the bump as one PR with an Atlas entry."
---

# /vibe-iterate-upgrade <package> — surgical library bump

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `vibe-iterate-guide` skill (`.agent/skills/vibe-iterate-guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Surgical version of the cut Modernize banner mode. Single-package focus: bump one library to its latest version (or to a user-specified version), run the codemod if one exists, run the test suite, open one PR. Atlas-write happens regardless of outcome.

Use this when responding to a `/vibe-iterate-scan-releases` finding ("react has a security fix") or a vendor-issued security advisory.

## Hard rules

- **One package per invocation.** If the user wants to bump multiple, they invoke `/vibe-iterate-upgrade` once per package. (`/vibe-iterate-upgrade react` then `/vibe-iterate-upgrade next`.) The narrow blast radius IS the value.
- **Run the test suite.** Pre-flight AND post-flight, per AGENTS.md § Posture. Bumps are the highest-regression-risk operation in vibe-iterate; the test runs are non-negotiable.
- **Codemods auto-run only when the package vendor publishes them.** If the codemod is a third-party tool with no vendor endorsement, surface the option to the user but don't auto-run.
- **Major bumps require explicit user opt-in.** If the bump crosses a semver major boundary, prompt before proceeding. Default: ask.

## Session + friction logging

At workflow start — load the `vibe-iterate-session-logger` skill (`.agent/skills/vibe-iterate-session-logger/SKILL.md`) and run `start("upgrade", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `vibe-iterate-friction-logger.log()` invocation.

At workflow end — call `vibe-iterate-session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })` per the schema.

Honor the friction trigger map at `.agent/skills/vibe-iterate-guide/references/friction-triggers.md` — section `/vibe-iterate-upgrade` — for which friction types to log at which confidence. Note: a user opting for a major bump, requesting test-skip, or rolling back are all HIGH-confidence signals.

## Inputs

- **`$1`** — required. The package name (e.g., `next`, `react`, `tailwindcss`).
- **`--to <version>`** — optional. Specific target version. If absent, defaults to `latest_in_range` (latest version satisfying the current pinned range). To bump to a major version outside the range, pass `--to <major>` explicitly.
- **`--no-codemod`** — optional. Skip the codemod step even if one is available. Use when you want to apply changes manually.

If `$1` is absent, prompt: *"Which package? Pass the package name (e.g., next, react, tailwindcss). For options, see /vibe-iterate-scan-releases first."*

- **Project state** — `package.json` (or stack equivalent). Must have the package in `dependencies` or `devDependencies`. If not present, surface: *"`<package>` is not in the manifest. Did you mean: <fuzzy matches>? Or did you mean to install fresh?"*

## Procedure

### Step 1 — posture announcement

> *Upgrade mode → conservative posture. Bumping `<package>` from `<current_pin>` to `<target>`. Pre-flight tests, then bump, then codemod (if any), then post-flight tests. PR opens at the end.*

### Step 2 — call `/vibe-iterate-scan-releases <package> --silent` internally

Get the structured output: `current_pin`, `latest`, `latest_in_range`, `breaking_changes[]`, `new_features[]`, `security_fixes[]`, `codemod{available, command, source_url}`.

### Step 3 — major-bump gate

If the target version (default: `latest_in_range`, or `--to <version>` if specified) crosses a semver major boundary from `current_pin`, surface:

```
Major bump:  <package>  <current_pin> → <target>

Breaking changes (per release notes):
- <description>  ← <source_url>
- ...

Codemod available: <yes / no>  [if yes:] <command>

This is a major bump. Want to proceed? (yes / no — keep current major / pick a smaller target)
```

Wait for user response. If "no — keep current major," reset target to `latest_in_range` (within the current major) and continue.

If `--to <version>` was explicitly passed AND it's a major bump, skip this gate (user already opted in).

### Step 4 — pre-flight test run

Run the existing test suite. Capture pass/fail. If any tests are failing pre-bump, surface:

```
Pre-existing test failures detected:
- <test name>
- <test name>

These predate this bump. Proceed anyway, or pause to investigate?
```

Wait for user response.

### Step 5 — bump the version

Update `package.json` (or stack equivalent):

- For `package.json`: replace the version range for `<package>` with the target version range. Default: pin to `^<target>` (caret range allowing future patch + minor). If the user passed `--to <exact-version>`, use the exact version (no caret).
- Run the package manager's install: `pnpm install` (preferred — repo uses pnpm) or `npm install` if no `pnpm-lock.yaml` is present. If `yarn.lock` is the only lockfile, use `yarn install`.

Capture install errors. If install fails (peer-dep conflict, version not found), surface the error verbatim and pause for user direction.

### Step 6 — run codemod (if available and not `--no-codemod`)

If the vendor publishes a codemod (e.g., `npx @next/codemod@latest <transform> .`), run it as documented. Capture stdout / stderr.

If the codemod fails, surface the failure but continue — the test run will catch the regression. Don't auto-roll-back.

### Step 7 — post-flight test run

Run the test suite again. Diff vs. step 4:

- **Net new failures** = caused by the bump (or by the codemod). Surface them.
- **All previously passing tests still passing** = green light.

If new failures exist:

```
Bump introduced <N> regression(s):
- <test name>
- <test name>

Options:
1. Roll back the bump (git stash / git checkout package.json + lockfile)
2. Try to fix in this PR (extends scope)
3. Ship anyway with regressions documented in PR description
4. Ship anyway with regressions in a follow-up issue

Which? (1/2/3/4)
```

Wait for user response.

### Step 8 — open the PR

Use `gh pr create` with this body shape:

```markdown
## Summary
Bump `<package>` from `<current_pin>` to `<target>`.
<one-paragraph rationale: security fix? new feature? maintenance?>

## Changes
- `package.json`: `<package>` `<current_pin>` → `<target>`
- `pnpm-lock.yaml` (or equivalent) regenerated
- Codemod: <ran <command> | not run | not available>
<additional file changes if codemod modified source>

## Release notes highlights
- <highlight 1>  ← <source_url>
- <highlight 2>  ← <source_url>

## Breaking changes
<if any from release notes — name them; otherwise: "None.">

## Test plan
- [x] Pre-flight tests: <N pass / N fail>
- [x] Post-flight tests: <N pass / N fail>
- [x] Codemod ran cleanly  (if applicable)
- [ ] Manual smoke test in dev (recommended for any bump)

## Migration path
<if breaking — describe the deprecation path; otherwise omit>

🤖 Generated with [vibe-iterate](https://github.com/estevanhernandez-stack-ed/vibe-iterate) /vibe-iterate-upgrade
```

### Step 9 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "upgrade",
  "outcome": "shipped",
  "title": "Bump <package> <current_pin> → <target>",
  "rationale": "<one-line: security fix CVE-... | new feature unlocks ... | maintenance bump | major bump per user opt-in>. Codemod: <ran | not available | skipped>. Tests: <N regressions | clean>.",
  "rejected_runners_up": [],
  "pr": "<PR URL>"
}
```

If the user rolled back in step 7, write the Atlas entry with `outcome: "rejected"`, `pr: null`, and rationale capturing why the rollback happened.

Validate against `.agent/skills/vibe-iterate-guide/schemas/atlas-entry.schema.json` before writing.

### Step 10 — close out

```
Upgraded:
- Package: <package>  <current_pin> → <target>
- PR: <url>
- Codemod: <ran | not available | skipped>
- Tests: <pre N/N → post N/N>  [<N> regressions if any]
- Atlas: <.vibe-iterate/atlas.jsonl> (entry appended)
```

## Anti-patterns

- **Don't bump multiple packages in one invocation.** Narrow blast radius is the point. Run `/vibe-iterate-upgrade` once per package.
- **Don't auto-merge the PR.** Bumps need a human eye on regression signal even when tests pass.
- **Don't skip the codemod step quietly** when one is available. If you decide to skip, surface the choice in the PR description.
- **Don't bump to `latest` blindly.** `latest_in_range` is the safe default. Going outside the range is a deliberate choice.
- **Don't run a full radar refresh** as part of the upgrade. That's `/vibe-iterate-radar`'s job. The internal `/vibe-iterate-scan-releases --silent` call is enough.

## Cross-references

- Sibling: `/vibe-iterate-scan-releases` — pre-flight version diff (called internally)
- Sibling: `/vibe-iterate-ship` — express lane for non-upgrade iterations
- Posture: AGENTS.md § Posture
- Atlas conventions: `.agent/skills/vibe-iterate-guide/references/atlas-conventions.md`
- Schema: `.agent/skills/vibe-iterate-guide/schemas/atlas-entry.schema.json`
