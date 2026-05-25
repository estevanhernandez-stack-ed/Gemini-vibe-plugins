---
name: vibe-wrap-plant
description: "Internal SKILL — not a user-invocable slash command. Sibling vibe plugins (or non-vibe tools that opt in) invoke `plant(source, command, phase, outcome=null, payload=null)` at command-start (or any point worth marking) to drop one breadcrumb line into the active session's breadcrumb file. No-op-safe — silent failure if vibe-wrap isn't installed or the session UUID can't be resolved (falls back to `_orphan.jsonl`). Writes one JSONL line to `~/.gemini/antigravity/data/vibe-wrap/breadcrumbs/<session-uuid>.jsonl`. Forward-compat — unknown payload fields are written verbatim. See `references/breadcrumb-contract.md` for the full schema and contract for sibling plugin authors."
---

# vibe-wrap-plant — Drop one breadcrumb into the session trail

Internal SKILL. **Not a user-invocable slash command.** Sibling plugins (or non-vibe tools that want to opt in) invoke this at command-start, command-end, or any other moment they want vibe-wrap to surface in the session wrap doc. One call writes one JSONL line.

Read `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) first for shared behavior — voice, namespace isolation, atomic-append discipline, and the no-op-safe contract framing this SKILL implements.

The full public schema and contract live at [`.agent/scripts/references/breadcrumb-contract.md`](../../scripts/references/breadcrumb-contract.md). That doc is what sibling plugin authors read once and code against forever. This SKILL body documents the implementation side.

## Before you start

- **Atomic protocol.** Every breadcrumb write goes through `python .agent/scripts/atomic-append-jsonl.py`. Never `>>` from a shell.
- **Pattern #11 namespace isolation.** This SKILL writes to exactly one place: `~/.gemini/antigravity/data/vibe-wrap/breadcrumbs/<session-uuid>.jsonl` (or `_orphan.jsonl` on UUID-resolution failure). Never any sibling namespace, never `~/.gemini/profiles/builder.json`.
- **No-op-safe is load-bearing.** Sibling plugin authors rely on this. Every failure path — missing required args, malformed payload, atomic-append failure, unhandled exception — logs a one-line stderr warning and exits 0. Never raise to the caller.
- **Session UUID is passed in, not discovered.** Claude Code does not expose the session UUID as an environment variable to scripts directly. The SKILL caller resolves it via the `${CLAUDE_SESSION_ID}` template substitution and passes it as `--session-id`. Empty / unresolvable → orphan fallback.

## How siblings invoke

The script is designed to be called from a sibling SKILL body (or any tool with shell access). The session UUID flows in via the `${CLAUDE_SESSION_ID}` template substitution at SKILL invocation time.

**Canonical sibling invocation** (one line, dropped into the sibling's own SKILL body at workflow start):

```
python ~/.gemini/antigravity/plugins/cache/vibe-plugins/vibe-wrap/<ver>/skills/vibe-wrap-plant/scripts/plant.py \
  --session-id ${CLAUDE_SESSION_ID} \
  --source vibe-cartographer \
  --command scope \
  --phase start \
  --outcome in_progress
```

The `${CLAUDE_SESSION_ID}` substitution resolves at SKILL invocation time inside the user's environment. If the substitution comes through empty (env not set, hook payload absent, shell wonkiness), the script writes to `_orphan.jsonl` and exits 0. The wrap reader merges orphans into the active session by timestamp proximity at render time.

**With a payload:**

```
python ~/.gemini/antigravity/plugins/cache/vibe-plugins/vibe-wrap/<ver>/skills/vibe-wrap-plant/scripts/plant.py \
  --session-id ${CLAUDE_SESSION_ID} \
  --source vibe-doc \
  --command scan \
  --phase end \
  --outcome completed \
  --payload '{"gaps_found": 3, "tier": "L2"}'
```

The payload is a JSON-encoded object. Unknown fields are written verbatim — see [`.agent/scripts/references/breadcrumb-contract.md`](../../scripts/references/breadcrumb-contract.md) § Forward compatibility.

## Call signature

```
plant(
  source:      string,         # required — calling plugin's name
  command:     string,         # required — slash command without leading "/"
  phase:       string,         # required — "start" | "end" | "fire"
  outcome:     string | null,  # optional — "in_progress" | "completed" | "failed" | null
  payload:     object | null,  # optional — source-defined extras (any JSON object)
)
```

Implemented as `scripts/plant.py` with the CLI flags:

| Flag | Required | Purpose |
|---|---|---|
| `--session-id` | yes (may be empty) | Claude Code session UUID. Empty → orphan fallback. Caller substitutes `${CLAUDE_SESSION_ID}`. |
| `--source` | yes | Calling plugin's name. |
| `--command` | yes | Slash-command without leading `/`. |
| `--phase` | yes | One of `start`, `end`, `fire`. |
| `--skill` | no | Invoked SKILL name. Omitted from the entry when not supplied. |
| `--outcome` | no | One of `in_progress`, `completed`, `failed`. Empty → null. |
| `--payload` | no | JSON-encoded object. Bad JSON → no line written, exit 0, stderr warning. |

## Where the file lives

Per-session file:

```
~/.gemini/antigravity/data/vibe-wrap/breadcrumbs/<session-uuid>.jsonl
```

Orphan fallback (when `--session-id` is empty or whitespace):

```
~/.gemini/antigravity/data/vibe-wrap/breadcrumbs/_orphan.jsonl
```

One file per Claude Code session. Append-only. JSONL — one JSON object per line. The atomic-append script handles `mkdir -p` on first use.

## Per-line schema (v1)

The script emits exactly this shape per call. The public contract lives at [`.agent/scripts/references/breadcrumb-contract.md`](../../scripts/references/breadcrumb-contract.md) § Data model.

```json
{
  "schema_version": 1,
  "ts": "2026-05-10T15:42:00-05:00",
  "sessionUUID": "550e8400-e29b-41d4-a716-446655440000",
  "source": "vibe-cartographer",
  "command": "scope",
  "skill": "scope",
  "phase": "start",
  "outcome": "in_progress",
  "payload": null
}
```

Field rules:

- `schema_version` — always `1` for v0.1.0.
- `ts` — ISO 8601 with timezone offset, set at write time.
- `sessionUUID` — the value passed via `--session-id`, or `null` when the orphan fallback fires.
- `source`, `command`, `phase` — pass-through from CLI args. Required.
- `skill` — only present when `--skill` is supplied. Omitted from the entry otherwise (saves bytes, matches the contract's "optional" framing).
- `outcome` — pass-through from `--outcome`, or `null` when omitted / empty.
- `payload` — parsed from `--payload` JSON, or `null` when omitted.

## The no-op-safe contract

Every failure path exits 0. Without exception. The contract:

| Failure | What happens |
|---|---|
| `argparse` rejects an unrecognized flag | Stderr warning + exit 0. |
| Required flag missing (`--source`, `--command`, `--phase`) | Stderr warning + exit 0. No line written. |
| `--phase` value not in `{start, end, fire}` | Stderr warning + write the line anyway (forward-compat). |
| `--outcome` value not in `{in_progress, completed, failed}` | Stderr warning + write the line anyway (forward-compat). |
| `--payload` is malformed JSON | Stderr warning + exit 0. No line written. |
| Atomic-append script not found / unreadable | Stderr warning + exit 0. No line written. |
| Atomic-append exits non-zero (disk full, permissions, etc.) | Stderr warning + exit 0. |
| Unhandled Python exception anywhere in main() | Stderr warning + exit 0 (last-resort guard). |

This is load-bearing for sibling plugin authors. The contract is fire-and-forget. If a sibling has to wrap their `vibe-wrap-plant` call in `try/except` to protect against vibe-wrap's failure modes, the contract is broken — file an issue.

## Forward compatibility

Per [`.agent/scripts/references/breadcrumb-contract.md`](../../scripts/references/breadcrumb-contract.md) § Forward compatibility:

- **Unknown `--payload` fields are written verbatim.** No schema validation that would reject the write. A future plugin can add `payload.{anything}` and v0.1.0's reader will pass them through (and skip what it doesn't understand at render time).
- **Unknown `phase` / `outcome` enum values are tolerated on write.** The script warns to stderr but writes the line anyway. v1 readers treat unknown enum values as `"fire"` / null.
- **The `schema_version` field is always `1` for v0.1.0.** When v2 lands, it bumps and the reader routes on the version field.

## Pattern #11 namespace isolation

This SKILL writes to exactly one place:

`~/.gemini/antigravity/data/vibe-wrap/breadcrumbs/<session-uuid>.jsonl` (or `_orphan.jsonl`)

It does NOT write to:

- `~/.gemini/profiles/builder.json` — the unified builder profile is owned by the user / Cart, not vibe-wrap.
- Any sibling plugin's data namespace.
- vibe-wrap's session log (`~/.gemini/antigravity/data/vibe-wrap/sessions/<date>.jsonl`) — that's `vibe-wrap-session-logger`'s territory. Breadcrumbs and session-logs are deliberately separate files with different shapes and purposes.

## Distinct from `vibe-wrap-session-logger`

`vibe-wrap-session-logger` writes vibe-wrap's OWN session-log entries (Pattern #2 — sentinel + terminal pairs for vibe-wrap's self-evolution). `vibe-wrap-plant` writes the cross-plugin breadcrumb trail that vibe-wrap reads at wrap time. Different files, different shapes, different purposes:

| | `vibe-wrap-session-logger` | `vibe-wrap-plant` |
|---|---|---|
| What | vibe-wrap's own self-evolution instrumentation | Cross-plugin breadcrumb trail |
| Who writes | Every vibe-wrap command at start + end | Sibling plugins (or vibe-wrap itself for its own commands) |
| File | `data/vibe-wrap/sessions/<YYYY-MM-DD>.jsonl` | `data/vibe-wrap/breadcrumbs/<session-uuid>.jsonl` |
| Schema | Sentinel + terminal entry pair | One entry per call |
| Read by | `evolve-wrap` | `wrap`, `status` |

## Example sibling invocation (Cart at command-start)

What a Cart SKILL author drops at the top of `/scope`'s SKILL body:

```
python ~/.gemini/antigravity/plugins/cache/vibe-plugins/vibe-wrap/<ver>/skills/vibe-wrap-plant/scripts/plant.py \
  --session-id ${CLAUDE_SESSION_ID} \
  --source vibe-cartographer \
  --command scope \
  --phase start \
  --outcome in_progress
```

That's the whole integration. No imports, no try/except wrappers, no library. The substitution resolves at SKILL invocation time; the script handles every failure path silently. Cart's SKILL body keeps running whether vibe-wrap is installed or not.

## Why no env var read

The session UUID is not exposed as an environment variable to scripts directly. The two surfaces that carry it:

1. **Workflow / skill bodies** — a session-id template substitution resolves at invocation time. The caller passes the resolved value to `plant.py` as `--session-id`. This is the canonical path.
2. **Hook scripts** — `SessionStart`, `SessionEnd`, etc. receive a JSON payload on stdin with `session_id` as a top-level field. vibe-wrap's `SessionEnd` nudge hook uses this (see `AGENTS.md § Event model — the SessionEnd nudge hook` and `.agent/hooks/`).

Pulling the env var directly from `plant.py` would be unreliable. The CLI-arg + caller-resolved-substitution pattern is the lockstep contract.

> **Port note (session-id token).** Throughout this skill the substitution is written `${CLAUDE_SESSION_ID}` — the Claude Code token. Antigravity's exact session-id substitution token is **unverified**; do NOT assume `${CLAUDE_SESSION_ID}` resolves verbatim in an Antigravity workspace. The contract is token-agnostic: the caller resolves *whatever the host exposes as the active session id* and passes it as `--session-id`. If it resolves empty (token mismatch, env not set), `plant.py` writes to `_orphan.jsonl` and exits 0 — the wrap reader merges orphans by timestamp proximity, so a missing session-id degrades gracefully rather than breaking. Confirm the host's session-id token when wiring sibling plant calls.

## Reference

- [`scripts/plant.py`](scripts/plant.py) — the actual breadcrumb writer.
- [`.agent/scripts/atomic-append-jsonl.py`](../../scripts/atomic-append-jsonl.py) — atomic single-line append protocol.
- [`.agent/scripts/references/breadcrumb-contract.md`](../../scripts/references/breadcrumb-contract.md) — public schema + sibling-author contract.
- `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) — shared behavior, voice, namespace isolation.
- the `vibe-wrap-session-logger` skill (`.agent/skills/vibe-wrap-session-logger/SKILL.md`) — distinct from `vibe-wrap-plant`; instrumentation for vibe-wrap's own commands.
