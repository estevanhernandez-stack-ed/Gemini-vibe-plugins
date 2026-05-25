---
name: vibe-wrap-guide
description: "Internal skill — not a user workflow. Situational reference index for vibe-wrap. The always-on layer (persona, the bumper-lanes invariant, voice rules, namespace isolation, composition, mode, hard rules, the event/hook model) lives in AGENTS.md. This skill holds the deep, situational detail every workflow occasionally needs: the per-persona voice table, the full voice register frame, and the friction-trigger map. Loaded by the workflows when they need to validate a write or shape user-facing prose; never invoked directly."
---

# vibe-wrap-guide — situational reference index

The always-on layer for vibe-wrap is in **`AGENTS.md`** (persona, the
bumper-lanes invariant + read-wide/mutate-narrow rule, mode, voice, Pattern #11
namespace isolation, Pattern #13 composition, the decision-log backend posture,
the self-evolving-framework wiring, the SessionEnd hook model, and the hard
rules). Don't duplicate it here.

This skill carries the **situational** detail — the exact shape/rules a workflow
reaches for occasionally, not every turn:

| Need | Load |
|---|---|
| Adapt wrap-doc / `/vibe-wrap-status` / gate-prompt / `/vibe-wrap-evolve` prose to the active persona | [`references/persona-adaptation.md`](references/persona-adaptation.md) — the full five-persona × four-surface table |
| The full voice register frame (working vs essay × technical vs visual), the banned-word list, the bones-vs-texture note, empty-state phrasing | [`references/voice.md`](references/voice.md) |
| When does each workflow log which friction type (Pattern #6 contract) | [`references/friction-triggers.md`](references/friction-triggers.md) — one section per workflow, with `friction_type` + fixed confidence per row |

Script-side situational contracts (the per-gate bumper contract, secret
patterns, the decision-log backend contract, the breadcrumb contract for sibling
authors) live next to the deterministic core under
[`.agent/scripts/references/`](../../scripts/references/):

- `gate-design.md` — bumper-lanes invariant per gate, the read-wide/mutate-narrow boundary.
- `secret-patterns.md` — the patterns that trigger the commit double-confirm.
- `decision-log-backends.md` — the four-backend contract, config precedence, first-run UX.
- `breadcrumb-contract.md` — schema + plant contract for sibling plugin authors.

## How the references are consumed

- **Every workflow that produces user-facing prose** reads
  `references/persona-adaptation.md` once at start (after reading
  `shared.preferences.persona` from `~/.gemini/profiles/builder.json` per
  `AGENTS.md § Persona`). Persona is voice; mode is pacing; the bumper-lanes
  invariant is fixed under both.
- **`vibe-wrap-friction-logger`** honors `references/friction-triggers.md` at
  every `log()` call site. The bidirectional consistency between that map and
  the actual call sites is audited at `/vibe-wrap-evolve` time. Confidence is
  fixed per trigger; `repeat_question` / `rephrase_requested` log nothing
  without a quoted prior.
- **`/vibe-wrap`** loads the script-side `references/*.md` when a gate needs
  validating (secret match → `secret-patterns.md`; gate behavior →
  `gate-design.md`; first-run picker → `decision-log-backends.md`).

## Reference

- [`references/voice.md`](references/voice.md) — full voice rules and register frame.
- [`references/persona-adaptation.md`](references/persona-adaptation.md) — per-persona table for vibe-wrap surfaces.
- [`references/friction-triggers.md`](references/friction-triggers.md) — friction-trigger contract per workflow.
- `AGENTS.md` — the always-on layer (persona, posture, voice, namespace isolation, composition, hard rules, the SessionEnd hook model).
- Self-Evolving Plugin Framework — [`vibe-cartographer/docs/self-evolving-plugins-framework.md`](https://github.com/estevanhernandez-stack-ed/vibe-cartographer/blob/main/docs/self-evolving-plugins-framework.md). Patterns #1, #2, #6, #11, #13, #14.
