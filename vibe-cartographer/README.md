# vibe-cartographer — Antigravity port

The Google Antigravity 2.0 port of [vibe-cartographer](https://github.com/estevanhernandez-stack-ed/vibe-cartographer), the 626Labs vibe-coding course-correction process — the plugin that builds the others. Same brain — plot the course from idea to shipped app across a linear chain of coaching workflows, with persona-adaptive voice, a unified builder profile, and a full self-evolving stack — repackaged for Antigravity's workflow + skill + rules model. This is the flagship of the family and the **Cart-detection target** the other ten ports defer to.

## What it does

Vibe coding ships fast but drifts — the planning, the decisions, the "why this approach" gets lost. Vibe Cartographer is a coach that walks a builder through a deliberate idea → ship process, producing real artifacts at each step (builder profile, scope, PRD, spec, checklist, reflection) that double as proof-of-process and a portfolio. The chain is linear by design — each workflow consumes the prior one's artifact.

```
/vibe-cartographer-onboard → -scope → -prd → -spec → -checklist → -build → -iterate → -reflect
```

Plus four standalone tools: `-vitals` (structural self-test), `-friction` (read-only friction-log viewer), `-coder-voice` (voice synthesis written to AGENTS.md), and `-evolve` (L3 self-evolution).

- **Persona + mode adaptive.** The builder picks a persona (Professor / Cohort / Superdev / Architect / Coach / system-default) and a mode (Learner / Builder) during onboard — persona shapes voice, mode shapes pacing, both apply across every workflow.
- **Owns the unified builder profile.** Vibe Cartographer is the family's profile owner (`~/.gemini/profiles/builder.json`, Pattern #11) — onboard creates/migrates it, reflect updates it, every sibling plugin reads it.
- **Architecture-doc aware.** Bundled default patterns guide the spec/checklist/build technical decisions; the builder can supply their own.
- **Self-evolving.** Session logging (L2), friction logging (Pattern #6), profile decay (Pattern #4), and reflective self-evolution (L3) — all local-first, all append-only, nothing auto-applied.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (13 of them, all `/vibe-cartographer-<cmd>`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the `vibe-cartographer-guide` situational reference + the internal decay / session-logger / friction-logger skills).
   - **Rules** from `AGENTS.md` — always-on persona model, posture, profile-ownership contract, composition posture, hard rules, voice.
3. The self-evolving loggers and profile writes shell out to two zero-dependency Node helpers in `.agent/scripts/` (`atomic-append-jsonl.js`, `atomic-write-json.js`). They need Node on PATH; nothing else.
4. First run: type `/vibe-cartographer-onboard` in your project folder. It welcomes you, builds your profile, sets persona + mode, then hands off down the chain.

## Workflows

| Workflow | Step | What it does |
|---|---|---|
| `/vibe-cartographer-onboard` | 1 | Welcome, builder profile, persona + mode selection, architecture docs, decay pre-flight. Owns the unified profile. |
| `/vibe-cartographer-scope` | 2 | Brainstorm and refine the idea into a focused scope. Writes `scope.md`. |
| `/vibe-cartographer-prd` | 3 | Turn scope into testable requirements. Writes `prd.md`. |
| `/vibe-cartographer-spec` | 4 | Translate the PRD into a technical blueprint using your architecture. Writes `spec.md`. |
| `/vibe-cartographer-checklist` | 5 | Sequence the spec into a dependency-aware build plan; lock the build mode. Writes `checklist.md`. |
| `/vibe-cartographer-build` | 6 | Build the app — step-by-step or autonomous, per the locked mode. Writes source. |
| `/vibe-cartographer-iterate` | 7 | Optional polish pass. Run zero or many times. |
| `/vibe-cartographer-reflect` | 8 | Retro + peer-style review; updates the unified profile. Writes `reflection.md`. |
| `/vibe-cartographer-vitals` | — | Eight read-only structural-integrity checks + six opt-in auto-fixes. |
| `/vibe-cartographer-friction` | — | Read-only friction-log viewer — filter by project/type/confidence/days, grouped banner report. |
| `/vibe-cartographer-coder-voice` | — | Capture/refresh/extend a coder voice profile — writes the `## CODER VOICE SYNTHESIS` block to `AGENTS.md`. |
| `/vibe-cartographer-evolve` | — | L3 self-evolution — reads session + friction logs, proposes workflow/skill edits. Never auto-applies. |

## Reconciliation: the merges + the friction collapse

vibe-cartographer is the family's heaviest plugin — 13 commands + 17 skills + an `architecture/` doc set. The Claude Code source paired most commands with a same-named implementation skill (the thin-command-wrapper pattern). The port **merges each command with its parallel skill into one workflow** — the command supplies the slash identity + clean `description`, the skill supplies the body. Twelve pairs merged this way (build, checklist, coder-voice, iterate, onboard, prd, reflect, scope, spec, tend, vitals, and evolve-cart → `/vibe-cartographer-evolve`).

The one wrinkle: `friction` (the read-only log-viewer command) delegated to a **differently-named** `friction-log` skill — a cross-named pair. `port.py`'s same-name merge missed it and emitted two workflows; the finishing pass collapsed them into one `/vibe-cartographer-friction` (the `friction-log` skill's full viewer body under the `friction` command's clean description). The internal `friction-logger` (Pattern #6 capture) is a **distinct** skill and stays internal. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full pattern.

## Skills (internal — loaded, not slash-invoked)

| Skill | Role |
|---|---|
| `vibe-cartographer-guide` | Situational reference: the per-persona behavior table, the Learner/Builder mode tables, the deepening-round mechanics, the anchored-complements table + live-discovery heuristics, the build-mode behavior, plus pointers to the data contracts, friction-trigger map, schemas, templates, and cutter presets. The always-on layer lives in `AGENTS.md`. |
| `vibe-cartographer-decay` | Pattern #4 profile-decay engine — invoked by onboard at start to re-validate stale profile fields. |
| `vibe-cartographer-session-logger` | Sentinel (start) + terminal (end) session entries, paired by `sessionUUID`. |
| `vibe-cartographer-friction-logger` | Append-only friction capture at the trigger points in the guide's friction-triggers map. Conservative — when in doubt, don't log. |

## Bundled reference (carried into `.agent/`)

- `.agent/architecture/` — default patterns, a worked example, and a README. Read by `/vibe-cartographer-spec` when the builder has no architecture docs of their own. (port.py missed this root-level dir; carried by hand.)
- `.agent/skills/vibe-cartographer-guide/schemas/` — builder-profile, session-log, friction, and friction-calibration JSON schemas.
- `.agent/skills/vibe-cartographer-guide/templates/` — scope / prd / spec / checklist / reflection / builder-profile templates.
- `.agent/skills/vibe-cartographer-guide/cutters/` — preset coder voices (carmack, dhh, bret-victor, julia-evans) for `/vibe-cartographer-coder-voice`.
- `.agent/scripts/` — the atomic JSONL-append + JSON-write helpers the loggers and profile writes use.

## State files (per host project + per user)

- **Per project:** `docs/` artifacts (scope, prd, spec, checklist, reflection, builder-profile) + `process-notes.md` — the build chain's working record. Portable as-is.
- **Per user:** `~/.gemini/profiles/builder.json` — the unified cross-plugin builder profile (Pattern #11). vibe-cartographer owns its own `plugins.vibe-cartographer` block and has shared-read on `shared.*`.
- **Self-evolution (local, append-only):** `~/.gemini/antigravity/data/vibe-cartographer/sessions/*.jsonl` + `~/.gemini/antigravity/data/vibe-cartographer-friction.jsonl` (+ `-friction.calibration.jsonl`).

## Cross-plugin / composition

Vibe Cartographer is the **detection target** for the rest of the family — vibe-doc, vibe-test, vibe-sec, vibe-thesis, vibe-iterate, vibe-walk all check for `vibe-cartographer` workflows/skills in the workspace and defer to it for the planning/onboarding phases they don't own. This port keeps the identity and workflow names stable so those references resolve.

It also composes the other way (Pattern #13): when specialist complements are available in the workspace, Cart defers to them at the right phase (`superpowers:brainstorming` at scope, `superpowers:test-driven-development` at build, the Figma MCP at spec, `gh` at checklist/reflect, and more). Read-only detection — announce once, never probe, never auto-install. The builder is always the final arbiter.

## Privacy

No telemetry. The self-evolving session/friction logs (`~/.gemini/antigravity/data/vibe-cartographer/`) and the unified profile stay local. Delete them anytime; the plugin keeps working, just loses its memory.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-cartographer@1.9.1`. This is port 12 of 12 — the finale, and the family is now cross-agent end to end. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook: the skill → workflow vs skill → skill mapping, the thin-command-wrapper + cross-named-pair merges, the guide split (Cart's was the largest in the family), the builder.json repoint (Cart's heaviest user), the coder-voice rules-file-write target, every Claude → Antigravity adaptation, the open-question answers, and the vibe-cartographer finale notes appended at the end.
