# vibe-walk — Antigravity port

The Google Antigravity 2.0 port of [vibe-walk](https://github.com/estevanhernandez-stack-ed/Vibe-Walk), a 626Labs user-onboarding plugin. Same brain — Sherpa, the guide who earns the tour before building one — repackaged for Antigravity's workflow + skill + rules model.

## What it does

Most onboarding tools assume a tour is always the answer. vibe-walk earns it first. It reads your app's user-facing surfaces, gives an honest build/don't-build verdict, names the aha moment, and — only when a tour is warranted — generates a short, instrumented, replayable Driver.js spotlight tour with a human-gated anchor pass.

- **An honest verdict, first-class.** `/discover` runs entirely on your codebase and returns `build` / `don't-build` / `cheaper-first` with equal weight. A tour layered on an already-intuitive UI trains a dismiss reflex; a tour on a blank-canvas first-run has lower ROI than fixing the empty state. The plugin says so.
- **Names the aha moment.** The single action that makes a new user say "this is worth it." Step 1 of any built tour routes here.
- **Generates onboarding only when it earns one.** When the verdict is `build`, `/walk` runs five interview gates then emits a drop-in, instrumented, replayable Driver.js tour — you own the emitted code, same model as shadcn.
- **A human-gated anchor pass.** Stable `data-tour` selectors are auto-injected only where it's provably safe; everything ambiguous halts in `REVIEW_NEEDED.md` for your review.
- **A 6-event analytics adapter** measuring downstream activation, not tour completion (a trap metric).
- **Reuses your existing first-run state.** The tour queues behind whatever already fires on first login — it doesn't stack.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-walk`, `/discover`, `/walk`, etc.).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the internal `session-logger`, `friction-logger`, and the `guide` reference detail).
   - **Rules** from `AGENTS.md` — always-on Sherpa persona, posture, hard rules.
3. The discovery + build phases call helper scripts under `.agent/scripts/` (Python 3.11 for discovery/build, jscodeshift for the anchor codemod). The anchor pass needs `jscodeshift` available in the host app (`node_modules/.bin/jscodeshift`).
4. First run: type `/vibe-walk`. On a fresh repo it hands off to `/bootstrap`, which classifies the app, infers the likely substrate, detects existing onboarding, and writes `.vibe-walk/config.json`.
5. After setup, re-run `/vibe-walk` for the next-step recommendation, or run `/discover` directly.

## The flow

vibe-walk is a linear two-phase flow, not a multi-mode picker:

```
/bootstrap (first run) → /discover (Phase 1) → /walk (Phase 1.5 + Phase 2)
```

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-walk` | Bare router — reads project state, recommends the next step, asks before launching. First run hands off to `/bootstrap`. |
| `/bootstrap` | First-run setup — classifies the app, resolves the likely substrate, detects existing onboarding, writes `.vibe-walk/config.json`. |
| `/discover` | Phase 1 autonomous discovery + the build / don't-build / cheaper-first verdict. Writes `.vibe-walk/discovery.json`. |
| `/walk` | Phase 1.5 interview gates + Phase 2 build (anchors → module → analytics → trigger wiring). Requires a `build` verdict. |
| `/vitals` | Read-only structural self-test — checks `agent.json`, all six workflows + three skills, scripts, guide references, friction-trigger wiring. |
| `/evolve-walk` | L3 self-evolution — reads session + friction logs and proposes improvements to the plugin. Never auto-applies. |

## State files (per host project)

- `.vibe-walk/config.json` — app category, framework, likely substrate, existing-onboarding inventory (written by `/bootstrap`).
- `.vibe-walk/discovery.json` — surface inventory, ranked shortlist, named aha moment, and the **verdict** (written by `/discover`; authoritative).
- `.vibe-walk/build-plan.json` — the resolved five-gate answers + substrate decision (written by `/walk`).

These are project-local and portable as-is. The tour output (`spotlightSteps.ts`, `spotlightTour.ts`, `tourAnalytics.ts`, `TOUR_ANALYTICS.md`, `WIRING.md`) lands in the app's tour directory (default `src/components/tour/`).

## Composes with

vibe-walk works standalone — it requires no sibling plugin. If `vibe-cartographer` or `vibe-iterate` are present in the workspace, discovery can lean on the richer architecture docs a Cart-built app already has, but composition is an enhancement, never a requirement.

## Privacy

No telemetry. The self-evolving session/friction logs (`~/.gemini/antigravity/data/vibe-walk/`) stay local. Delete them anytime; the plugin keeps working, just loses its memory.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-walk@0.1.0`, dogfooded on Celestia3 (Cart cycle #16). See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, every Claude → Antigravity adaptation, the open questions, and the vibe-walk-specific port notes appended at the end.
