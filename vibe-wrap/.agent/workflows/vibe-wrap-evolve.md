---
description: "Run when the user says `/vibe-wrap-evolve` and wants vibe-wrap to reflect on its own past sessions and propose plugin improvements to itself. Pattern #1 self-evolution loop. Reads vibe-wrap's session log + friction log + last 30 days of wrap docs, weights findings, and writes proposed SKILL / config / template edits to `proposed-changes.md` in the plugin source. **Never auto-applies.** Named `evolve-wrap` from day one (NOT `evolve`) — first marketplace plugin under the new `evolve-<short>` convention. L3 self-evolution; this command improves vibe-wrap itself, not the user's app."
---

Read `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) for shared behavior (voice rules, persona adaptation, friction-trigger contract, namespace isolation).

# evolve-wrap — vibe-wrap reflects on itself

Pattern #1 self-evolution. Read vibe-wrap's own session log, friction log, and recent wrap docs; surface the patterns that actually show up in the data; and write a `proposed-changes.md` naming concrete improvements. **Never auto-applies.** This command improves vibe-wrap itself — not the user's app.

Named `evolve-wrap` from day one, not `evolve` — the first marketplace plugin under the `evolve-<short>` convention. The three sibling plugins with bare `evolve` rename in their next earned cycle (tracked in `drafts/_pending-renames.md`). Do not rename this one to match them; they move toward this name, not the reverse.

## Before you start

- **Session logging.** Call `vibe-wrap-session-logger.start("evolve-wrap", <cwd>)` at workflow start and `vibe-wrap-session-logger.end(<entry>)` at workflow end per the `vibe-wrap-session-logger` skill (`.agent/skills/vibe-wrap-session-logger/SKILL.md`).
- **Empty-state guard.** `evolve-wrap` needs at least one prior wrap session to read. If there's no session-log data and no friction data, surface the empty-state message — `No vibe-wrap sessions to reflect on yet. Run /vibe-wrap a few times first.` — and exit cleanly.
- **Read-only against everything except the proposal file.** This command reads state and writes exactly one artifact: `proposed-changes.md`. It edits no SKILL bodies, no scripts, no config.

## What it reads

All under vibe-wrap's own namespace (Pattern #11 — never a sibling's):

| Source | Path | Used for |
|---|---|---|
| Session log | `~/.gemini/antigravity/data/vibe-wrap/sessions/<YYYY-MM-DD>.jsonl` | Outcome streaks, complements invoked, gate-acceptance rates. |
| Friction log | `~/.gemini/antigravity/data/vibe-wrap/friction.jsonl` | Recurring `friction_type` clusters, quoted symptoms. |
| Wrap docs | `<repo>/docs/session-wraps/*.md` (and `.vibe-wrap/wraps/*.md`) from the last 30 days | Recurring shapes — sections that are always empty, gates always declined, secret-pattern near-misses. |

Window: last 30 days by default. v0.1.0 reads and clusters; the deeper L3 pattern-weighting that Cart's `evolve` does (confidence decay, calibration-aware scoring) lands in v0.2.

## What it writes

One file: `proposed-changes.md` in the plugin source repo (the solo vibe-wrap repo / the marketplace tree — NOT inside the installed `.agent/` skeleton). Shape locked in [`.agent/scripts/references/proposed-changes-template.md`](../scripts/references/proposed-changes-template.md). Four sections:

1. **Observed patterns** — evidence-first. Counts, paths, quoted friction symptoms. A pattern seen once is noise; hold it.
2. **Proposed workflow / skill edits** — concrete file + change + the pattern it answers + confidence. High-confidence = seen 3+ times.
3. **Proposed config changes** — thresholds, defaults, schema. Name the downstream ripple before proposing.
4. **Deferred — what didn't make the cut** — patterns held back, with reasons. Keeps the next cycle from re-litigating.

### Self-edit target map (the port retarget — NOT a blind path)

Source proposals named `plugins/vibe-wrap/skills/<cmd>/SKILL.md`. In the Antigravity port those targets flip, because the eponymous `wrap` skill became the router workflow and the loggers/plant became namespaced skills. Name the **real port file**:

| What the proposal touches | Port target |
|---|---|
| The main wrap command's behavior | `.agent/workflows/vibe-wrap.md` (the router — was the `wrap` skill) |
| `/vibe-wrap-status` behavior | `.agent/workflows/vibe-wrap-status.md` |
| `/vibe-wrap-evolve` behavior | `.agent/workflows/vibe-wrap-evolve.md` |
| Shared persona / posture / voice / hard rules | `AGENTS.md` |
| The per-persona table, voice register frame, friction-trigger map | `.agent/skills/vibe-wrap-guide/references/*.md` |
| A logger / plant skill body | `.agent/skills/vibe-wrap-{session-logger,friction-logger,plant}/SKILL.md` |
| The render core, readers, decision-log dispatcher, gate/secret/backend/breadcrumb contracts | `.agent/scripts/...` (helpers) and `.agent/scripts/references/...` (contracts) |
| The SessionEnd nudge hook | `.agent/hooks/session-end-nudge.py` + `.agent/hooks/settings.json` |

Never propose editing a `plugins/vibe-wrap/skills/...` source path — that path does not exist in the port.

## The contract

- **Never auto-applies.** Output is a proposal. The user reviews and applies edits one at a time with a `[y/n]` per item.
- **Evidence over speculation.** Every proposed edit cites the pattern it answers. If the data is thin, say so — don't invent patterns to fill the template.
- **No sibling writes.** Reads vibe-wrap's own state only. The proposal can suggest edits to vibe-wrap's files; it never touches another plugin.

## Handoff

Close with: `Review proposed changes at <path>. Apply individually with [y/n] per item.`

## Reference

- [`.agent/scripts/references/proposed-changes-template.md`](../scripts/references/proposed-changes-template.md) — the output shape.
- the `vibe-wrap-session-logger` skill (`.agent/skills/vibe-wrap-session-logger/SKILL.md`) — the session log this reads.
- the `vibe-wrap-friction-logger` skill (`.agent/skills/vibe-wrap-friction-logger/SKILL.md`) — the friction log this reads.
- `AGENTS.md` + the `vibe-wrap-guide` skill (`.agent/skills/vibe-wrap-guide/SKILL.md`) — shared behavior, voice, persona adaptation.
- Self-Evolving Plugin Framework Pattern #1 — [`vibe-cartographer/docs/self-evolving-plugins-framework.md`](https://github.com/estevanhernandez-stack-ed/vibe-cartographer/blob/main/docs/self-evolving-plugins-framework.md).
