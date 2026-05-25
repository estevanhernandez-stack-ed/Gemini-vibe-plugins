---
name: vibe-test-vitals
description: "Internal SKILL — not a user workflow in v0.2. Invoked by the /vibe-test-evolve workflow as a read-only pre-flight. Pattern #8 (Plugin Self-Test) — checks that referenced files exist, workflows resolve, data files parse against schemas, plays-well-with.md entries still resolve in the ecosystem. Emits a report with 'N issues found, want me to fix?' prompt."
---

<!-- Derived from vibe-cartographer 1.5.0 vitals SKILL (own-impl per Spec Decision 5 / Option a; migrate to @626labs/plugin-core in Phase 3). In v0.2 vitals is NOT a user-invoked workflow — it runs as a pre-flight check from the /vibe-test-evolve workflow. A user-facing /vibe-test-vitals workflow lands in v0.3. -->

# vibe-test-vitals — Structural Integrity Check (Pattern #8)

Internal skill. In v0.2 vitals is invoked only by the `/vibe-test-evolve` workflow (`.agent/workflows/vibe-test-evolve.md`) at its start — never by the user directly. v0.3 adds a `/vibe-test-vitals` workflow; until then the checks are part of evolve's pre-flight.

This SKILL runs seven **read-only** checks against the installed plugin files, the unified profile, the session/friction/wins logs, and the anchored composition registry. It prints a banner-style report with per-check status (✓ pass, ⚠ warn, ✗ fail) and a summary line. **No fix ever runs without an explicit `[y/n]`** — vitals surfaces findings; the user chooses whether to apply remediation. In v0.2 the remediation half is deferred to the caller (`/vibe-test-evolve`); vitals itself never writes.

## Before You Start

- **Data contracts:** [`../vibe-test-guide/references/data-contracts.md`](../vibe-test-guide/references/data-contracts.md) — file locations, schemas, atomic-write/append protocols. Vitals reads every file named there. Does not write any of them.
- **Plays well with:** [`../vibe-test-guide/references/plays-well-with.md`](../vibe-test-guide/references/plays-well-with.md) — check #4 parses this for anchored complements.
- **Friction triggers:** [`../vibe-test-guide/references/friction-triggers.md`](../vibe-test-guide/references/friction-triggers.md) — check #6 audits bidirectional consistency between this file and the workflows.
- **Schemas:**
  - [`../vibe-test-guide/schemas/builder-profile.schema.json`](../vibe-test-guide/schemas/builder-profile.schema.json) — check #3.
  - [`../vibe-test-guide/schemas/audit-state.schema.json`](../vibe-test-guide/schemas/audit-state.schema.json), etc. — check #7.
- **Framework reference:** `docs/self-evolving-plugins-framework.md` Pattern #8 — Plugin Self-Test.

## Session Logging

At workflow start, call `vibe-test-session-logger.start("vitals", <project_dir>)`. Hold the UUID. At exit, `vibe-test-session-logger.end({ sessionUUID, command: "vitals", outcome })`.

- `outcome: "completed"` — clean run.
- `outcome: "partial"` — a check aborted due to unreadable file; report still rendered.
- `outcome: "errored"` — the command crashed before the summary line.

## Friction Logging

Vitals does **not** call `vibe-test-friction-logger.log()` in v0.2. User declines on fix prompts (when the caller surfaces them) are the **expected** mode of interaction, not friction. Only the universal `repeat_question` / `rephrase_requested` triggers apply, and only under the quoted-prior gate (enforced by the state layer).

## Runtime Paths

All paths vitals reads (never writes):

| What | Where |
|------|-------|
| Plugin root | `.agent/` — determined from this SKILL file's own location (`.agent/skills/vibe-test-vitals/SKILL.md`). |
| Workflow files | `.agent/workflows/*.md` (8: the router `vibe-test.md` + `vibe-test-{audit,coverage,evolve,fix,gate,generate,posture}.md`) |
| Skill files | `.agent/skills/**/SKILL.md` (6: `vibe-test-{decay,friction-logger,guide,session-logger,vitals,wins-logger}`) |
| Templates | `.agent/skills/vibe-test-guide/templates/` |
| Schemas | `.agent/skills/vibe-test-guide/schemas/` |
| Plays-well-with | `.agent/skills/vibe-test-guide/references/plays-well-with.md` |
| Friction triggers | `.agent/skills/vibe-test-guide/references/friction-triggers.md` |
| Unified profile | `~/.gemini/profiles/builder.json` |
| Sessions | `~/.gemini/antigravity/data/vibe-test/sessions/*.jsonl` |
| Friction log | `~/.gemini/antigravity/data/vibe-test/friction.jsonl` |
| Wins log | `~/.gemini/antigravity/data/vibe-test/wins.jsonl` |
| Plugin manifest | `.agent/agent.json` (for banner version) |

## The Seven Checks

### Check #1 — Cross-references resolve

Every workflow/skill file referenced by another must exist. Enumerate `.agent/workflows/*.md` + `.agent/skills/**/SKILL.md`, extract markdown links + backticked paths + path-like strings to `.agent/workflows/*.md` and `.agent/skills/*/SKILL.md`. For each, resolve to an absolute path and verify.

- ✓ pass: all references resolve.
- ✗ fail: list each broken reference as `<source>:<line> → <target>`.

### Check #2 — Template references resolve

Every template referenced by a workflow/skill must exist in `.agent/skills/vibe-test-guide/templates/`. Additionally, templates on disk that nothing references surface as ⚠ warn.

- ✓ pass: all references resolve.
- ⚠ warn: orphan templates on disk.
- ✗ fail: broken reference to a missing template.

### Check #3 — Builder profile schema

Parse `~/.gemini/profiles/builder.json`, validate `plugins.vibe-test` block against `builder-profile.schema.json`. Check `_meta` entries for `last_confirmed` + `ttl_days` fields.

- ✓ pass: profile parses + validates.
- ⚠ warn: no profile yet (first-time user) OR non-fatal shape drift.
- ✗ fail: parse error OR required-field violation OR schema-forbidden keys.

### Check #4 — Anchored complement availability

Parse `.agent/skills/vibe-test-guide/references/plays-well-with.md` YAML. For each anchored complement, cross-reference against the `vibe-*` workflows/skills available in this Antigravity workspace.

- ✓ pass: every anchored complement present.
- ⚠ warn: one or more absent (in complete-context branch) OR runtime context incomplete (fail-soft — don't flag missing complements when the surface itself is unreliable).
- No ✗ fail state — anchored drift is warn, not structural failure.

### Check #5 — Log volume sanity

Compute `friction_per_session` and `wins_per_session` over the last 30 days.

- ✓ pass: `0.05 ≤ friction_per_session ≤ 5.0`. Healthy.
- ⚠ warn (under-firing): `friction_per_session < 0.05` with ≥10 sessions in window.
- ⚠ warn (over-firing): `friction_per_session > 5.0`.
- ⚠ warn (first-3-sessions): terminal_entries_in_window < 3 → skip volume eval.
- ⚠ warn (silent): 10+ sessions with zero friction entries.

### Check #6 — Friction-trigger consistency

For each workflow, extract friction-type invocations declared in its Friction Logging section. Compare against `friction-triggers.md` rows.

- ✓ pass: orphan-invocation and orphan-trigger sets both empty.
- ⚠ warn: orphan triggers (declared in map but not invoked in a workflow).
- ✗ fail: orphan invocations (a workflow logs a type not in the map).

Exclude `command_abandoned` (detect_orphans owns it) and any row under `/vibe-test-vitals` / future `/vibe-test-friction` (documented empty).

### Check #7 — State file schema integrity

For every per-project state file at `<project>/.vibe-test/state/*.json`, parse and validate against its schema. For each JSONL log, spot-check the last 100 entries parse.

- ✓ pass: all files parse + validate.
- ⚠ warn: non-critical shape drift (unknown optional fields, trailing junk).
- ✗ fail: parse error OR required-field violation OR schema_version mismatch unreconcilable by migration.

Vitals never writes; it reports. The caller (`/vibe-test-evolve` in v0.2) decides whether to offer remediation.

## Output Format

Banner:

```
  📖  Vibe Test — Vitals
  <version> · <ISO-local-timestamp>
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Per-check box (Unicode box-drawing):

```
  ┌──────────────────────────────────────────────────────────────────┐
  │ ✓  Check 1 — SKILL cross-references                              │
  └──────────────────────────────────────────────────────────────────┘
     All references resolved. Scanned N SKILL files, M command files.
```

Summary:

```
  <N> ✓  ·  <N> ⚠  ·  <N> ✗
```

The seven counts sum to 7.

## Why This SKILL Exists

Pattern #8 is the *"you touch it, you break it"* hedge — every plugin with multiple SKILLs, schemas, and append-only logs eventually develops cross-file drift. Without an on-demand diagnostic, drift surfaces as a command failing mid-flow at the worst possible moment.

In v0.2, vitals runs as an `/vibe-test-evolve` pre-flight so proposed changes see a clean house before they're generated. In v0.3 it will also be a user-invoked slash command with interactive auto-fix prompts modeled on Cart's six-fix pattern.

The read-only contract is load-bearing in v0.2: vitals surfaces findings, `/vibe-test-evolve` proposes fixes, the user approves. Three separate surfaces with clear ownership.
