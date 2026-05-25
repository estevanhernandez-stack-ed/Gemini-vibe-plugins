---
name: guide
description: "Shared reference detail for vibe-iterate — Atlas write conventions, the friction-trigger map, and the JSON schemas for config / atlas-entry / radar-cache. Load this when a vibe-iterate workflow needs to validate a state-file write or look up which friction type fires at which trigger. The always-on persona, posture, knowledge sources, and Cart-detection live in AGENTS.md, not here."
---

# vibe-iterate guide — shared reference detail (Ptolemy)

The always-on layer (Ptolemy persona, the three posture defaults, knowledge sources, Cart-detection, hard rules) lives in **`AGENTS.md`** at the port root — every workflow already has it as ambient context. This skill carries the **deep reference detail** that's too heavy for always-on rules and only matters when a workflow is mid-flight: schema validation, Atlas write rules, and the friction-trigger map.

## When to load this

- A workflow is about to **write a state file** (`config.json`, `atlas.jsonl`, `radar.cache.json`) and needs to validate against the schema.
- A banner mode or `bootstrap` needs the **friction-trigger map** to know which friction type fires at which confidence.
- You want the Atlas read/write conventions (append-only, recent-rejection check, cross-plugin scope).

## Reference docs

- [`references/atlas-conventions.md`](references/atlas-conventions.md) — Atlas write rules, entry shape, read patterns, privacy posture.
- [`references/friction-triggers.md`](references/friction-triggers.md) — when each workflow logs which friction type at which confidence (per Pattern #6, consumed by the friction-logger skill).

## Schemas (validate before any state-file write)

- [`schemas/atlas-entry.schema.json`](schemas/atlas-entry.schema.json) — one JSONL line in `.vibe-iterate/atlas.jsonl`.
- [`schemas/config.schema.json`](schemas/config.schema.json) — `.vibe-iterate/config.json`.
- [`schemas/radar-cache.schema.json`](schemas/radar-cache.schema.json) — `.vibe-iterate/radar.cache.json`.

Fixtures for spot-checking a write: [`fixtures/atlas-entry.valid.jsonl`](fixtures/atlas-entry.valid.jsonl), [`fixtures/atlas-entry.invalid.jsonl`](fixtures/atlas-entry.invalid.jsonl), [`fixtures/config.valid.json`](fixtures/config.valid.json), [`fixtures/radar-cache.valid.json`](fixtures/radar-cache.valid.json).

**Rule:** if a workflow writes any of these files, validate against the schema first. Malformed writes corrupt the ledger and break downstream consumers.

## Self-evolving framework — the two internal skills

Every banner mode (`/feature-add`, `/competitive`, `/ux-polish`, `/bug-bash`) and `/bootstrap` invokes:
- [`../session-logger/SKILL.md`](../session-logger/SKILL.md) — sentinel + terminal session entries, paired by sessionUUID, written to `~/.gemini/antigravity/data/vibe-iterate/sessions/<date>.jsonl`.
- [`../friction-logger/SKILL.md`](../friction-logger/SKILL.md) — append-only friction entries written to `~/.gemini/antigravity/data/vibe-iterate/friction.jsonl`.

The `/evolve-iterate` workflow reads both logs and proposes plugin improvements. Sidecars (`/radar`, `/spy`, `/scan-releases`, `/rate`) do NOT log — they're read-only and short-lived.

## Cross-plugin requirements

| Plugin | Required? | Role |
|---|---|---|
| Antigravity scheduled-task / cron | Optional | Powers the weekly radar refresh; `/radar` supports manual refresh meanwhile |
| `vibe-cartographer` | Optional (auto-detected) | Heavy-iteration delegation target (see AGENTS.md § Cart-detection) |
| `context7` (MCP) | Optional (auto-detected) | Live framework-docs lookups at decision-time |

For optional plugins: detect at workflow start, branch on availability, never hard-fail when one is absent.
