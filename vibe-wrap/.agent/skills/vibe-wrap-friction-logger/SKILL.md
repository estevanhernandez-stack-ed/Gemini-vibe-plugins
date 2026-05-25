---
name: vibe-wrap-friction-logger
description: "Internal SKILL — not a user workflow. Append-only friction capture for vibe-wrap (Pattern #6). Invoked by every vibe-wrap command at the trigger points listed in `../vibe-wrap-guide/references/friction-triggers.md`. Storage: `~/.gemini/antigravity/data/vibe-wrap/friction.jsonl`. Pattern #11 namespace isolation — writes ONLY inside vibe-wrap's data dir. Counterbalanced by absence-of-friction inference at /evolve-wrap time."
---

# vibe-wrap-friction-logger — Append-Only Friction Capture

Internal SKILL. Not a user-invocable slash command. Loaded by every vibe-wrap command SKILL at the trigger points listed in [`../vibe-wrap-guide/references/friction-triggers.md`](../vibe-wrap-guide/references/friction-triggers.md).

Read `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) first for shared behavior — voice, friction-trigger contract overview, namespace isolation, defensive defaults.

This skill describes the procedure the agent runs whenever it detects user friction. Friction is captured silently — no confirmation prompts, no user-facing chatter. False positives poison `/vibe-wrap-evolve`, so when in doubt, **don't log**.

## Before You Start

- **Trigger map:** [`../vibe-wrap-guide/references/friction-triggers.md`](../vibe-wrap-guide/references/friction-triggers.md) — one section per command SKILL, listing the conditions that produce each friction type plus default confidence. Source of truth for "when does `/vibe-wrap` log what."
- **Atomic protocol:** all writes go through `python .agent/scripts/atomic-append-jsonl.py ~/.gemini/antigravity/data/vibe-wrap/friction.jsonl` (stdin = one JSON object). Never `>>` from a shell.
- **No-op-safe.** A failed atomic append logs to stderr and continues. The SKILL never raises to the caller. Friction capture is best-effort plumbing, not critical path.
- **Pattern #11 namespace isolation.** This SKILL writes to exactly one place: `~/.gemini/antigravity/data/vibe-wrap/friction.jsonl`. Never any sibling's friction file. Never `shared.*`. Never anywhere else.

## Catalog-Wide Invariant

> When in doubt, don't log.

A missed friction signal is recoverable through future calibration. A false positive corrupts `/vibe-wrap-evolve`'s weighting and is much harder to undo. Every defensive default in this SKILL exists to honor that asymmetry.

## Defensive Defaults

These are the load-bearing rules. Every code path through `log()` honors all four.

1. **Required-field validation drops silently.** If the entry is missing `sessionUUID`, `friction_type`, `confidence`, or `symptom`, exit silently with a stderr note. Do not retry. Do not surface the error to the user. Do not log a partial entry.
2. **`repeat_question` and `rephrase_requested` require a quoted prior turn.** These two friction types only log when `symptom` quotes the actual prior message text the user is referencing. Concretely: `symptom` must contain a `"` character AND be longer than 20 characters. Without the quote, the agent is guessing — and guessed friction is exactly the noise the defensive default exists to prevent. The Python script enforces this with a stderr `vibe-wrap-friction-logger: defensive default rejected entry — symptom must quote prior turn` message and exit 1, signaling that the caller's submission was malformed.
3. **No append blocks the command.** If `atomic-append-jsonl.py` exits non-zero (locked file, full disk, permission error), surface the stderr to the calling SKILL but never block the user-facing command. Friction capture is best-effort plumbing.
4. **Per-trigger confidence is fixed.** The `confidence` value comes from `friction-triggers.md`, not from agent judgment in the moment. Hand-tuning confidence per call drifts the calibration model. If a trigger feels mis-tuned, fix it in `friction-triggers.md` (and let `/vibe-wrap-evolve` propose the change) — don't override at log time.

## Where the Log Lives

`~/.gemini/antigravity/data/vibe-wrap/friction.jsonl`

- Single append-only file (NOT partitioned by date). Matches Cart's `friction.jsonl` shape exactly.
- The atomic-append script handles `mkdir -p` on first use.
- Cross-project: a single user's friction events from all their projects land here.

## Entry Shape

```json
{
  "schema_version": 1,
  "timestamp": "2026-05-10T15:42:00-05:00",
  "plugin": "vibe-wrap",
  "plugin_version": "0.1.0",
  "command": "wrap",
  "project_dir": "vibe-plugins",
  "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
  "friction_type": "complement_rejected",
  "confidence": "high",
  "symptom": "user declined the dashboard bridge gate when threshold fired",
  "complement_involved": "mcp__626labs-cloud__bridge_context_to_architect",
  "key_decisions_at_log_time": ["picked file-md backend earlier this run"]
}
```

### Field definitions

**Required:**

- **schema_version** — always `1` for now.
- **timestamp** — ISO 8601 with timezone offset.
- **plugin** — always `"vibe-wrap"`.
- **plugin_version** — read from `.agent/agent.json`'s `"version"`. Falls back to `"unknown"`.
- **command** — which command was running when the friction surfaced: `wrap`, `status`, `vibe-wrap-plant`, `evolve-wrap`.
- **project_dir** — basename of cwd. PII discipline.
- **sessionUUID** — UUID v4 from the vibe-wrap-session-logger's `start()` for this command run. The caller passes it in. Required for pairing friction events back to a specific session.
- **friction_type** — one of the seven canonical types: `complement_rejected`, `default_overridden`, `sequence_revised`, `artifact_rewritten`, `repeat_question`, `rephrase_requested`, `command_abandoned`. Source of truth for the catalog: [`../vibe-wrap-guide/references/friction-triggers.md`](../vibe-wrap-guide/references/friction-triggers.md).
- **confidence** — `high` | `medium` | `low`. Fixed per trigger by the friction-triggers map. Never override at log time.
- **symptom** — free-form one-line description of what was observed. For `repeat_question` and `rephrase_requested`, MUST quote the prior turn (defensive default 2).

**Optional:**

- **complement_involved** — string or null. Conventionally only non-null when `friction_type === "complement_rejected"` — names the complement the user declined (e.g., `"vibe-cartographer:reflect"`, `"mcp__626labs-cloud__bridge_context_to_architect"`).
- **key_decisions_at_log_time** — array of short strings. Snapshot of session state at the moment of friction. Useful for `evolve-wrap` to correlate friction with prior decisions in the same session.

## Procedure: `log(entry)`

**Argument:** caller-provided partial entry. The caller supplies the friction-specific fields (`sessionUUID`, `friction_type`, `confidence`, `symptom`, optional `complement_involved`, optional `key_decisions_at_log_time`). This procedure fills audit fields and writes.

**Returns:** nothing on success. Exits silently on missing required fields. Surfaces atomic-append errors to the caller without blocking the command.

1. **Build the full entry.** Start from the caller's partial entry. Then add:
   - `schema_version: 1`
   - `timestamp`: now, ISO 8601 with timezone offset (e.g., `2026-05-10T15:42:00-05:00`)
   - `plugin: "vibe-wrap"`
   - `plugin_version`: read from `.agent/agent.json`'s `"version"` field. Fall back to `"unknown"`.
   - `command`: the calling command name.
   - `project_dir`: basename of cwd.
   - Caller-provided fields take precedence for everything else (the trigger knows the friction context; this procedure knows the audit context).

2. **Apply the quoted-prior gate.** If `friction_type` is `repeat_question` or `rephrase_requested`, validate `symptom`:
   - Must contain a `"` character.
   - Must be longer than 20 characters.
   - On failure, write `vibe-wrap-friction-logger: defensive default rejected entry — symptom must quote prior turn` to stderr and exit 1. The caller's friction submission was malformed.

3. **Validate required fields.** Check that `sessionUUID`, `friction_type`, `confidence`, and `symptom` are present and non-empty. Validate `friction_type` is one of the seven canonical values. Validate `confidence` is one of `high`, `medium`, `low`. On any failure: log a one-line stderr note and exit silently. Better to miss than poison.

4. **Atomic append.** Pipe the JSON-stringified entry to `python .agent/scripts/atomic-append-jsonl.py ~/.gemini/antigravity/data/vibe-wrap/friction.jsonl`. On non-zero exit, surface the stderr to the caller. Do not retry — the caller owns retry policy.

The procedure is intentionally narrow. All semantic decisions about *whether* a friction signal exists live in `friction-triggers.md` and the calling SKILL. This procedure only handles validation, audit fields, and the write.

## Wiring

| Caller | Invocation | Notes |
|--------|------------|-------|
| Every command SKILL (`wrap`, `status`, `vibe-wrap-plant`, `evolve-wrap`) | `log(entry)` at the trigger points listed in `friction-triggers.md` | One call per detected trigger. Conservative — when in doubt, skip. |

The `command_abandoned` friction type (sentinel session-log entry without a matching terminal entry) is NOT emitted by any individual command's call — it's a future cross-cutting concern. v0.1.0 doesn't ship `detect_orphans()`. When that lands (post-v0.1.0), it'll mirror Cart's procedure: scan recent session files, find sentinels with no matching terminals over 24h old, emit one `command_abandoned` friction entry per orphan via this same `log()` procedure.

## Orchestrator-context fallback

Same as vibe-wrap-session-logger. When invoked outside vibe-wrap's normal runtime, the friction signal may land in the chat transcript or a project-local note instead of `friction.jsonl`. `/vibe-wrap-evolve` will see no entry — recoverable only from those alternate surfaces. v0.1.0 ships no backfill; documented here so the contract is stable.

## Namespace Isolation (Pattern #11)

This SKILL writes to exactly one place:

`~/.gemini/antigravity/data/vibe-wrap/friction.jsonl` — vibe-wrap's own friction log (vibe-wrap's data directory, append-only).

It does NOT write to:
- Any other plugin's friction log.
- `~/.gemini/profiles/builder.json`.
- Any other namespace under `~/.gemini/antigravity/data/`.

The `friction-triggers.md` map enforces the same discipline at the contract layer; this SKILL enforces it at the write layer. Both layers must hold for Pattern #11 to be load-bearing.

## Failure Modes

- **`.agent/scripts/atomic-append-jsonl.py` missing:** caller's invocation will fail with "command not found" or `FileNotFoundError`. Surface to the caller; do not block the command.
- **`.agent/agent.json` missing or unparseable:** fall back to `plugin_version: "unknown"` and continue. The audit field is informational; the rest of the entry is still valid.
- **Concurrent appends from two commands within the same second:** atomic-append handles ordering. The Windows append path uses `msvcrt.locking` to serialize; POSIX uses `O_APPEND` for kernel-atomic single-line writes.

## Why This SKILL Exists

Friction signals are the empirical input to `/vibe-wrap-evolve`. Without them, `/vibe-wrap-evolve` can only reason from session logs (what happened) and wrap docs (what the agent produced) — both filtered through the agent. Friction adds the unfiltered third channel: what the user actually did when the agent's choice didn't fit.

Pattern #6's whole point is that this signal must be cheap to write, conservative in scope, and safe to ignore on a per-call basis. This SKILL is the implementation of that contract.

## Reference

- [`scripts/log.py`](scripts/log.py) — friction-entry append.
- [`.agent/scripts/atomic-append-jsonl.py`](../../scripts/atomic-append-jsonl.py) — atomic single-line append.
- `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) — shared behavior, voice, namespace isolation, defensive-defaults overview.
- [`../vibe-wrap-guide/references/friction-triggers.md`](../vibe-wrap-guide/references/friction-triggers.md) — per-command trigger map.
- the `vibe-wrap-session-logger` skill (`.agent/skills/vibe-wrap-session-logger/SKILL.md`) — session log shape and `start()` / `end()` procedures. The `sessionUUID` this SKILL receives is minted by `start()`.
