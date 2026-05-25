---
name: vibe-iterate-friction-logger
description: "Internal skill — not a user workflow. Append-only friction capture for vibe-iterate. Loaded by every banner-mode workflow + bootstrap at the trigger points listed in .agent/skills/vibe-iterate-guide/references/friction-triggers.md. Implements Pattern #6 (Friction Log) from the Self-Evolving Plugin Framework. Antigravity port — logs to ~/.gemini/antigravity/data/vibe-iterate/."
---

# vibe-iterate-friction-logger — append-only friction capture

Internal skill. Not a user-invocable workflow (no `.agent/workflows/` entry). Loaded by every banner-mode workflow (`/vibe-iterate-feature-add`, `/vibe-iterate-competitive`, `/vibe-iterate-ux-polish`, `/vibe-iterate-bug-bash`) and `/vibe-iterate-bootstrap` at the trigger points listed in [`../vibe-iterate-guide/references/friction-triggers.md`](../vibe-iterate-guide/references/friction-triggers.md), and by `/vibe-iterate-evolve` at the start of analysis for orphan detection.

> Antigravity port note: callers are **workflows** (`.agent/workflows/*.md`); procedures are unchanged except the log path, which repoints from `~/.claude/plugins/data/` to `~/.gemini/antigravity/data/`.

Friction is captured silently — no confirmation prompts, no user-facing chatter. False positives poison `/vibe-iterate-evolve`, so when in doubt, **don't log**.

## Where the log lives

`~/.gemini/antigravity/data/vibe-iterate/friction.jsonl`

- Single file. Append-only. Never rewrite existing lines.
- Cross-project: friction signals from all the user's vibe-iterate runs land here.
- The directory is created on first use.

## Catalog-wide invariant

> When in doubt, don't log.

A missed friction signal is recoverable through future runs producing the same friction. A false positive corrupts `/vibe-iterate-evolve`'s pattern weighting and is much harder to undo. Every defensive default in this SKILL exists to honor that asymmetry.

## Friction types

The seven enum values for `friction_type`:

| Type | When to use |
|---|---|
| `default_overridden` | User explicitly picks a non-default option (e.g., picks alternative #2 instead of recommended #1, opts for `--no-codemod` when one was available). |
| `complement_rejected` | User declines a Pattern #13 complement offer (e.g., declines Cart-delegation upsell, declines context7 lookup). |
| `artifact_rewritten` | User rewrites or heavily edits an agent-produced artifact (PR description, brief, classification). Conservative — minor copy edits don't count. |
| `sequence_revised` | User pivots mid-flow (e.g., starts feature-add, switches to bug-bash mid-scoring; or pauses then re-runs with different scope). |
| `repeat_question` | User repeats a question the agent already answered. **REQUIRES** a quoted prior-turn snippet in `symptom`. |
| `rephrase_requested` | User asks the agent to rephrase or restate ("explain it differently", "shorter version"). |
| `command_abandoned` | Sentinel session entry has no terminal entry within 24h. Only emitted by `detect_orphans()`. |

## Entry shape

```json
{
  "schema_version": 1,
  "timestamp": "2026-05-06T14:42:00-05:00",
  "plugin": "vibe-iterate",
  "plugin_version": "1.0.0",
  "command": "feature-add",
  "project_dir": "vibe-cartographer",
  "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
  "friction_type": "complement_rejected",
  "confidence": "high",
  "complement_involved": "vibe-cartographer",
  "symptom": "User declined Cart-delegation upsell at heavy-iteration check (effort score 1)."
}
```

### Field definitions

- **schema_version** — always `1` for now.
- **timestamp** — ISO 8601 with timezone offset.
- **plugin** — always `"vibe-iterate"`.
- **plugin_version** — read the `version` field from the port manifest `.agent/agent.json`. Fall back to `"unknown"`.
- **command** — the calling command name. Same enum as `vibe-iterate-session-logger`.
- **project_dir** — basename of cwd.
- **sessionUUID** — the UUID returned by `vibe-iterate-session-logger.start()` for this command run. REQUIRED for orphan pairing.
- **friction_type** — one of the seven enum values above.
- **confidence** — `high` | `medium` | `low`. Comes from the trigger map in [`../vibe-iterate-guide/references/friction-triggers.md`](../vibe-iterate-guide/references/friction-triggers.md), NOT from agent judgment in the moment.
- **complement_involved** — string or null. Conventionally only non-null when `friction_type === "complement_rejected"`. Names the complement (e.g., `"vibe-cartographer"`, `"context7"`).
- **symptom** — short string describing the trigger context. For `repeat_question`, MUST contain a quoted prior-turn snippet.

## Defensive defaults

These are load-bearing. Every code path through `log()` honors all four.

1. **Schema validation silent-drop.** If the entry is missing required fields, has unknown enum values, or fails any structural check, exit silently. Do not retry. Do not surface the error to the user.
2. **`repeat_question` requires a quoted prior in `symptom`.** Without that, the agent is guessing. Drop guessed friction.
3. **No append blocks the command.** If the file write fails (locked file, full disk, permission), log a one-line warning to stderr and continue. The user-facing command never blocks on friction logging.
4. **Per-trigger confidence is fixed.** Comes from `friction-triggers.md`, not from per-call judgment. Hand-tuning drifts the calibration.

## Procedure: `log(entry)`

**Argument:** caller-provided partial entry. The caller supplies the friction-specific fields (`friction_type`, `command`, `project_dir`, `sessionUUID`, `confidence`, `symptom`, optional `complement_involved`); this procedure fills in the audit fields (`schema_version`, `timestamp`, `plugin`, `plugin_version`) and writes.

**Steps:**

1. **Build the full entry.** Start with caller's partial. Add audit fields (`schema_version: 1`, `timestamp`, `plugin: "vibe-iterate"`, `plugin_version`).
2. **Apply the `repeat_question` gate.** If `friction_type === "repeat_question"` and `symptom` is missing, empty, or contains no quoted prior-turn snippet, exit silently.
3. **Validate.** Required fields present? `friction_type` in enum? `confidence` in enum? `sessionUUID` non-empty? On failure, exit silently.
4. **Append to `~/.gemini/antigravity/data/vibe-iterate/friction.jsonl`.** One JSON line. Create directory if missing. On write failure, warn to stderr and continue.

## Procedure: `detect_orphans()`

Scans the session log for sentinels without matching terminals (>24h old) and emits one `command_abandoned` friction entry per orphan.

**Steps:**

1. **Read the session log window.** Enumerate `~/.gemini/antigravity/data/vibe-iterate/sessions/*.jsonl`. Filter to files within the last 7 days. Parse each line; skip malformed lines silently.
2. **Index sentinels.** For each entry with `outcome === "in_progress"`, key by `(command, project_dir, sessionUUID)`. Hold the timestamp.
3. **Index terminals.** For each entry with `outcome` in `{"completed", "abandoned", "error", "partial"}`, mark the matching triple as terminated.
4. **Find orphans.** For each sentinel triple with no terminal, compute `age = now - timestamp`. If `age >= 24 hours`, treat as orphan.
5. **Emit one friction entry per orphan.** Call `log(...)` with `friction_type: "command_abandoned"`, the orphan's `command` / `project_dir` / `sessionUUID`, `confidence: "high"`, and `symptom` describing the abandonment ("command <X> in <project_dir> never reached terminal — sentinel timestamp <T>, age <hours>h").
6. **Suppress duplicates.** Read the last 7 days of `friction.jsonl` first; skip any orphan whose triple already appears as a `command_abandoned` entry.

## Wiring

| Caller | Invocation | Notes |
|--------|------------|-------|
| `/vibe-iterate-evolve` | `detect_orphans()` once at start of analysis | Catches orphan backlog before reading the session log |
| Every banner mode + `bootstrap` | `log(entry)` at trigger points listed in `friction-triggers.md` | One call per detected trigger. Conservative — when in doubt, skip |

## Failure modes

- **No write permission** → silent fail. Friction capture is best-effort.
- **Sessions directory missing** → `detect_orphans()` returns without writing.
- **Port manifest `.agent/agent.json` missing** → `plugin_version: "unknown"`, continue.

## What NOT to log

- **No PII** beyond `project_dir` basename.
- **No secrets.**
- **No conversational content** beyond the `symptom` field's short context string.
- **No agent reasoning.** Only structured signal.

## Why this SKILL exists

Friction signals are the empirical input to `/vibe-iterate-evolve`. Without them, `/vibe-iterate-evolve` can only reason from session logs (what happened) and absence-of-friction inference. Friction adds the unfiltered third channel: what the user actually did when the agent's choice didn't fit. Pattern #6's whole point: the signal must be cheap to write, conservative in scope, and safe to ignore on a per-call basis.

## Cross-references

- Sibling SKILL: [`../vibe-iterate-session-logger/SKILL.md`](../vibe-iterate-session-logger/SKILL.md) — sentinel + terminal session entries
- Trigger map: [`../vibe-iterate-guide/references/friction-triggers.md`](../vibe-iterate-guide/references/friction-triggers.md) — when each command logs which friction type at which confidence
- User-facing SKILL: [`../../workflows/vibe-iterate-evolve.md`](../../workflows/vibe-iterate-evolve.md) — reads friction + sessions, proposes improvements
- Framework reference (in vibe-cartographer): `docs/self-evolving-plugins-framework.md` Pattern #6
