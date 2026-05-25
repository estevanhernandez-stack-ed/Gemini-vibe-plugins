---
name: vibe-taker-friction-logger
description: "Reserved placeholder for v2 friction logging. Documents the log(entry) contract and reserved data path. Command skills do NOT invoke this in v1."
---

# vibe-taker — vibe-taker-friction-logger (v2 placeholder)

> **v1 status: not invoked.** This skill ships as documentation-only. Command skills (`capture`, `plant`, `list`) **do not** call into this skill in v1. Reserved for v2 lighting-up of Self-Evolving Plugin Framework Level 3 (friction signals → `/evolve`). Folder + data path exist on disk in v1 so v2 can light up without a directory restructure. KTD-8.

## Contract (reserved for v2)

Append-only friction capture. One JSON line per friction event.

### `log(entry)`

Appends `entry` (one JSON object) to the data file as a single line.

```jsonc
{
  "schema_version": "1.0",
  "logged_at": "<ISO 8601>",
  "command": "capture | plant | list",
  "session_uuid": "<paired with vibe-taker-session-logger entry, when both are firing>",
  "friction_type": "<see triggers reference>",
  "confidence": "low | medium | high",
  "context": {
    "project_dir": "/abs/path",
    "<command-specific keys>": "..."
  },
  "summary": "<one-line description of the friction>",
  "decision": "<what the user/agent did about it, if anything>"
}
```

### Triggers reference

The triggers table — when the v2-active version of this logger fires per-command — lives at:

[`skills/vibe-taker-guide/references/friction-triggers.md`](../vibe-taker-guide/references/friction-triggers.md) **(v1: not present; reserved for v2.)**

In v1 the triggers reference is intentionally absent. v2 lights it up alongside the logger.

## Reserved data path

```
~/.gemini/antigravity/data/vibe-taker/friction.jsonl
```

- Single append-only file across all sessions and commands.
- One JSON object per line (JSONL).
- Reader for v2 `/evolve`-shaped commands aggregates by `friction_type` and `command`, weighted by `confidence`.

## Why placeholder, not full omission

Same reasoning as [vibe-taker-session-logger](../vibe-taker-session-logger/SKILL.md#why-placeholder-not-full-omission): reserving the folder + data path in v1 means v2 doesn't need a per-user disk migration when it lights up.

## v1 verification

> **No v1 command skill calls into this skill.** `grep -r "vibe-taker-friction-logger" plugins/vibe-taker/skills/{capture,plant,list}/` returns empty. The placeholder is documentation only.
