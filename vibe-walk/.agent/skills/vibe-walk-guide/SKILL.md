---
name: vibe-walk-guide
description: "Shared reference detail for vibe-walk — the D1–D6 output conventions (the data-tour anchor contract, Driver.js default, the 5-step cap, the 6-event analytics schema, the REVIEW_NEEDED halt) and the friction-trigger map. Load this when a vibe-walk workflow is about to build a tour or log friction. The always-on Sherpa persona, posture, and hard rules live in AGENTS.md, not here."
---

# vibe-walk guide — shared reference detail (Sherpa)

The always-on layer (Sherpa persona, the four posture principles, hard rules) lives in **`AGENTS.md`** at the port root — every workflow already has it as ambient context. This skill carries the **deep reference detail** that's too heavy for always-on rules and only matters when a command is mid-flight: the resolved build conventions and the friction-trigger map.

## When to load this

- A command (`/vibe-walk-discover`, `/vibe-walk-walk`, `/vibe-walk-bootstrap`) is about to **make a build decision** — substrate, anchor contract, step cap, analytics schema — and needs the D1–D6 conventions.
- A command is about to **log friction** and needs the trigger map (which friction type fires at which confidence, per command).

## Reference docs

- [`references/conventions.md`](references/conventions.md) — the resolved output decisions D1–D6: the 5-step cap (D1), the drop-in module default (D2), Driver.js as the default substrate with override conditions (D3), the `data-tour="<kebab-semantic-name>"` anchor contract (D4), the 6-event analytics schema (D5), and the anchor-injection boundary + REVIEW_NEEDED halt (D6). Non-negotiable build constraints; source is this cycle's research seed.
- [`references/friction-triggers.md`](references/friction-triggers.md) — where each command invokes `vibe-walk-friction-logger.log()`, with the friction type and confidence (per Pattern #6, consumed by the vibe-walk-friction-logger skill).

## Self-evolving framework — the two internal skills

Every command (`/vibe-walk-bootstrap`, `/vibe-walk-discover`, `/vibe-walk-walk`, `/vibe-walk-vitals`) invokes:
- [`../vibe-walk-session-logger/SKILL.md`](../vibe-walk-session-logger/SKILL.md) — sentinel + terminal session entries, paired by sessionUUID, written to `~/.gemini/antigravity/data/vibe-walk/sessions/<date>.jsonl`.
- [`../vibe-walk-friction-logger/SKILL.md`](../vibe-walk-friction-logger/SKILL.md) — append-only friction entries written to `~/.gemini/antigravity/data/vibe-walk/friction.jsonl`.

The `/vibe-walk-evolve` workflow reads both logs and proposes plugin improvements. It never auto-applies.

## Scripts

The discovery + build phases call helper scripts carried verbatim from the Claude Code source, now under `.agent/scripts/`:
- `scripts/discovery/` — `inventory_surfaces.py`, `anchor_readiness.py`, `build_verdict.py` (Phase 1).
- `scripts/build/` — `substrate_tree.py`, `emit_tour_module.py`, `emit_analytics.py`, `emit_trigger_wiring.py` (Phase 2).
- `scripts/anchors/` — `inject_anchors.js`, a jscodeshift codemod (Phase 2, anchor injection).
