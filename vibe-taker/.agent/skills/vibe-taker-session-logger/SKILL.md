---
name: vibe-taker-session-logger
description: "Reserved placeholder for v2 session logging. Documents the contract (start/terminal-append) and reserved data path. Command skills do NOT invoke this in v1."
---

# vibe-taker — vibe-taker-session-logger (v2 placeholder)

> **v1 status: not invoked.** This skill ships as documentation-only. Command skills (`capture`, `plant`, `list`) **do not** call into this skill in v1. Reserved for v2 lighting-up of Self-Evolving Plugin Framework Level 2 (session memory). The folder + data path exist on disk in v1 so v2 can light up without a directory restructure. KTD-8.

## Contract (reserved for v2)

Two-phase append-only session log: a sentinel entry at workflow start (outcome = `in_progress`) and a terminal entry at workflow end, paired by `sessionUUID`.

### `start(command, project_dir) → sessionUUID`

Append-only entry written at workflow start.

```jsonc
{
  "schema_version": "1.0",
  "session_uuid": "<uuid v4>",
  "command": "capture | plant | list",
  "project_dir": "/abs/path/to/cwd",
  "started_at": "<ISO 8601>",
  "outcome": "in_progress"
}
```

### Terminal append

Written at workflow end. Same shape, paired by `session_uuid`.

```jsonc
{
  "schema_version": "1.0",
  "session_uuid": "<same as start>",
  "command": "capture | plant | list",
  "project_dir": "/abs/path/to/cwd",
  "started_at": "<ISO 8601 from start entry>",
  "ended_at": "<ISO 8601>",
  "outcome": "success | decline | failure",
  "exit_class": 0 | 1 | 2,
  "decisions": [
    "<one-line decision>",
    "..."
  ],
  "artifact_path": "/abs/path/to/written-bundle-or-planted-target",
  "duration_seconds": <number>
}
```

## Reserved data path

```
~/.gemini/antigravity/data/vibe-taker/sessions/<YYYY-MM-DD>.jsonl
```

- One file per UTC day. Append-only JSONL.
- Both start and terminal entries land in the same file (paired by `session_uuid`).
- Reader for v2 `/evolve`-shaped commands joins start ↔ terminal on `session_uuid`.

## Why placeholder, not full omission

If v1 left the folder + data path entirely undeclared, v2 would need a migration step on user disks (move existing-but-orphan v1 paths if any exist, change skill folder name, etc.). Reserving the path costs zero in v1 (no writes happen) and keeps v2 surgical: light up the contract, not the directory layout.

## v1 verification

> **No v1 command skill calls into this skill.** `grep -r "vibe-taker-session-logger" plugins/vibe-taker/skills/{capture,plant,list}/` returns empty. The placeholder is documentation only.
