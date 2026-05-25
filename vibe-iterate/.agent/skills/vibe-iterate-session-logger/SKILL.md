---
name: vibe-iterate-session-logger
description: "Internal skill — not a user workflow. Two-phase append-only session log for vibe-iterate: a sentinel entry at workflow start (outcome=in_progress) and a terminal entry at workflow end, paired by sessionUUID. Loaded by every banner-mode workflow + bootstrap at start and end. Part of Level 2 (session memory) of the Self-Evolving Plugin Framework. Antigravity port — logs to ~/.gemini/antigravity/data/vibe-iterate/."
---

# vibe-iterate-session-logger — sentinel + terminal session log

Internal skill. Not a user-invocable workflow (no `.agent/workflows/` entry). Every vibe-iterate banner-mode workflow (`/vibe-iterate-feature-add`, `/vibe-iterate-competitive`, `/vibe-iterate-ux-polish`, `/vibe-iterate-bug-bash`) and `/vibe-iterate-bootstrap` loads this skill and runs `start()` at invocation and `end()` at completion. The two entries share a `sessionUUID` so `vibe-iterate-friction-logger.detect_orphans()` can pair them.

> Antigravity port note: in the Claude Code original this was a skill invoked by command SKILLs. Here the callers are **workflows** (`.agent/workflows/*.md`); the procedures below are unchanged except the log path, which repoints from `~/.claude/plugins/data/` to `~/.gemini/antigravity/data/`.

## Where the log lives

`~/.gemini/antigravity/data/vibe-iterate/sessions/<YYYY-MM-DD>.jsonl`

- One file per day. Append-only. Never rewrite existing lines.
- Cross-project: a single user's logs from all their iterations land here.
- Every command run produces **two** entries in the same daily file: one sentinel at start, one terminal at end, paired by `sessionUUID`.
- The directory is created on first use (mkdir -p as part of the first append).

## Entry shapes

Two entries per command run. Both live in the same daily file. Both carry the same `sessionUUID`.

### Sentinel entry (written by `start()`)

```json
{
  "schema_version": 1,
  "timestamp": "2026-05-06T14:25:00-05:00",
  "plugin": "vibe-iterate",
  "plugin_version": "1.0.0",
  "command": "feature-add",
  "project_dir": "vibe-cartographer",
  "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
  "outcome": "in_progress"
}
```

### Terminal entry (written by `end()`)

```json
{
  "schema_version": 1,
  "timestamp": "2026-05-06T14:55:00-05:00",
  "plugin": "vibe-iterate",
  "plugin_version": "1.0.0",
  "command": "feature-add",
  "project_dir": "vibe-cartographer",
  "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
  "outcome": "completed",
  "user_pushback": false,
  "friction_notes": ["complement_rejected: vibe-cartographer (declined Cart-delegation upsell)"],
  "key_decisions": ["picked top candidate (#1)", "delegated scope to vibe-cartographer", "shipped one PR"],
  "atlas_outcome": "shipped",
  "atlas_title": "Add saved-search feature",
  "pr_url": "https://github.com/example/repo/pull/42"
}
```

### Field definitions

Shared by both entries unless noted.

- **schema_version** — always `1` for now. Bump when the entry shape changes.
- **timestamp** — ISO 8601 with timezone offset.
- **plugin** — always `"vibe-iterate"`.
- **plugin_version** — read the `version` field from the port manifest `.agent/agent.json`. Fall back to `"unknown"`.
- **command** — which command is running: `bootstrap` | `feature-add` | `competitive` | `ux-polish` | `bug-bash` | `ship` | `upgrade`. Sidecars `radar`, `spy`, `scan-releases`, `rate` do NOT log sessions (they're read-only and short-lived).
- **project_dir** — basename of the current working directory. Not the full path.
- **sessionUUID** — UUID v4 issued by `start()`. The terminal entry and any friction entries written during this command all carry the same value. Required for orphan pairing.
- **outcome** — sentinel: always `"in_progress"`. Terminal: `completed` | `abandoned` | `error` | `partial`.

**Terminal-only fields:**

- **user_pushback** — boolean. `true` if the user rejected, heavily edited, or overrode an agent suggestion. Be conservative — minor tweaks don't count.
- **friction_notes** — array of short strings. Human-facing recap. The structured friction signal goes to `friction.jsonl` via `vibe-iterate-friction-logger.log()`.
- **key_decisions** — array of short strings. High-signal decisions only. Examples: `"picked candidate #1"`, `"delegated to Cart"`, `"declined Cart upsell"`, `"queued (user paused)"`.
- **atlas_outcome** — copy of the Atlas entry's `outcome` field for this run: `shipped` | `rejected` | `queued` | `null` (for `bootstrap`, which doesn't write Atlas).
- **atlas_title** — copy of the Atlas entry's `title` field. Useful for `/vibe-iterate-evolve` analysis.
- **pr_url** — PR URL if the run shipped a PR; `null` otherwise.

## Procedure: `start(command, project_dir)`

Called by a command SKILL at invocation. Returns the `sessionUUID` the command must hold in memory until it calls `end()`.

**Steps:**

1. **Generate sessionUUID.** Use any UUID v4 generator. Bash: `uuidgen` (macOS/Linux) or `[guid]::NewGuid()` (PowerShell). Node: `crypto.randomUUID()`.
2. **Determine audit fields:**
   - `schema_version: 1`
   - `timestamp: <now ISO datetime with timezone offset>`
   - `plugin: "vibe-iterate"`
   - `plugin_version`: read from the port manifest `.agent/agent.json`. Fall back to `"unknown"`.
   - `command`: the calling command name.
   - `project_dir`: basename of cwd.
3. **Build the sentinel entry** with `outcome: "in_progress"` and the audit fields.
4. **Append to today's session file.** Path: `~/.gemini/antigravity/data/vibe-iterate/sessions/<today>.jsonl` (where `<today>` is `YYYY-MM-DD` in local time). Create the directory if missing. Append one JSON line.
5. **On any failure** (file system error, permission denied), log a one-line warning to stderr and continue. Session logging is instrumentation, not critical path.
6. **Return the `sessionUUID`** to the caller. The command holds it in memory for the duration of the run.

## Procedure: `end(entry)`

Called by a command SKILL at completion, before exiting. Takes a partial entry with the terminal fields.

**Steps:**

1. **Build the full terminal entry.**
   - Start with the caller's partial entry (`sessionUUID`, `outcome`, `user_pushback`, `friction_notes`, `key_decisions`, `atlas_outcome`, `atlas_title`, `pr_url`).
   - Overlay audit fields exactly as in `start()`.
2. **Match the sessionUUID.** The entry's `sessionUUID` MUST equal the value returned by `start()`. Never mint a new UUID here — that breaks orphan pairing.
3. **Append to today's session file.** Same path as `start()`. Create directory if missing.
4. **On any failure**, warn to stderr and continue. Same posture as `start()`.

## Failure modes

- **No write permission on `~/.gemini/antigravity/data/`** → log fails silently. The workflow continues. The user never sees a vibe-iterate-session-logger error.
- **Sessions directory missing** → first `start()` creates it.
- **Port manifest / version missing** → `plugin_version: "unknown"`, continue.

## What NOT to log

- **No PII beyond the `project_dir` basename.** Never the full path. Never user identifiers.
- **No secrets.** Ever.
- **No full command arguments or feedback.md content.** The log is structured signal, not a transcript.
- **No code or PR diffs.** Just `pr_url` and outcome metadata.

## Privacy posture

- Local-first. The log lives in `~/.gemini/antigravity/data/vibe-iterate/` and never leaves the machine unless the user explicitly shares it.
- User-inspectable: `cat ~/.gemini/antigravity/data/vibe-iterate/sessions/<date>.jsonl` shows everything captured.
- User-deletable. The user can `rm -rf ~/.gemini/antigravity/data/vibe-iterate/` at any time; the plugin continues working — just loses the memory.
- Per Este's standing rule: **NO telemetry.** Nothing leaves the local machine. Ever.

## Why this exists

The session log is raw material for **Level 3** of the Self-Evolving Plugin Framework. `/vibe-iterate-evolve` reads these entries (alongside `friction.jsonl`) to propose plugin improvements based on observed patterns.

The sentinel pattern lets `vibe-iterate-friction-logger.detect_orphans()` distinguish "user abandoned the command" from "command never ran" — abandonment is friction signal worth surfacing; non-execution isn't.

## Cross-references

- Sibling SKILL: [`../vibe-iterate-friction-logger/SKILL.md`](../vibe-iterate-friction-logger/SKILL.md) — append-only friction capture
- User-facing SKILL: [`../../workflows/vibe-iterate-evolve.md`](../../workflows/vibe-iterate-evolve.md) — reads sessions + friction, proposes improvements
- Framework reference (in vibe-cartographer): `docs/self-evolving-plugins-framework.md`
