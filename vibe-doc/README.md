# vibe-doc — Antigravity port

The Google Antigravity 2.0 port of [vibe-doc](https://github.com/estevanhernandez-stack-ed/Vibe-Doc), a 626Labs documentation gap analyzer. Same brain — scan, classify, find the doc gaps, generate professional docs from what you actually built — repackaged for Antigravity's workflow + skill + rules model.

## What it does

Vibe coding produces real artifacts fast: working code, architecture decisions, test suites, deploy configs. The docs lag behind — ADRs, runbooks, threat models, API specs. vibe-doc reads what you've built, finds the holes, and generates the docs from your existing code, configs, and history. It runs five workflows over a deterministic CLI (`npx vibe-doc`), so you get conversational intelligence on top of reproducible output.

- **Scan, classify, gap report.** `/vibe-doc-scan` walks your artifacts, classifies the app type and deployment context (hybrid rules + LLM), and cross-references against the 7-doc v1 standard to produce a prioritized Required / Recommended / Optional gap report.
- **Autonomous-first generation.** `/vibe-doc-generate` reads the codebase and fills what it can confidently synthesize, then interviews you only for the sections code can't answer (security judgment, business intent, undocumented ops). Never fabricates — honest `NEEDS INPUT` over confident hallucination, with inline source citations on everything it fills.
- **CI-safe readiness check.** `/vibe-doc-check` is a pass/fail on Required-doc existence + freshness, exit codes for your pipeline. Writes nothing.
- **Status at a glance.** `/vibe-doc-status` reflects the current scan, classification, and coverage.
- **Self-evolution.** `/vibe-doc-evolve` reads its own session + friction logs and proposes plugin improvements (L3). Never auto-applies.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-doc-scan`, `/vibe-doc-generate`, `/vibe-doc-check`, `/vibe-doc-status`, `/vibe-doc-evolve`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the internal `vibe-doc-session-logger`, `vibe-doc-friction-logger`, and the `vibe-doc-guide` reference detail).
   - **Rules** from `AGENTS.md` — always-on persona, posture, profile rules, composition posture, hard rules.
3. The workflows shell out to the `vibe-doc` CLI (`npx vibe-doc scan|generate|check|status`). Install it where the workspace can reach it (`npm install -g @esthernandez/vibe-doc`, or rely on `npx`).
4. First run: type `/vibe-doc-scan` on a project. It classifies the app, builds the gap report, and writes `.vibe-doc/state.json`. Then `/vibe-doc-generate` to fill gaps, `/vibe-doc-check` before you ship.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-doc-scan` | Scan artifacts, classify the app, produce the gap report. Writes `.vibe-doc/state.json`. The entry point. |
| `/vibe-doc-generate` | Autonomous-first doc generation: fill from the codebase, interview for the gaps, write to `docs/generated/`. |
| `/vibe-doc-check` | CI-safe pass/fail on Required-doc existence + freshness. Exit codes only — writes nothing. |
| `/vibe-doc-status` | Read-only reflection of the current scan, classification, and coverage. |
| `/vibe-doc-evolve` | L3 self-evolution — reads session + friction logs and proposes plugin improvements. Never auto-applies. |

## The shape that defined this port: thin-command-wrapper → merged workflow

vibe-doc is the first port in the family with a `commands/` directory. Its `commands/*.md` were **thin slash-entry wrappers** that delegated to a parallel skill — e.g. `commands/scan.md` (four lines, "Scan your project for documentation gaps") just said "read `skills/scan/SKILL.md` and follow it." The SKILL held the real implementation.

The port **merges each command with its parallel skill into one workflow**: the command supplies the slash identity + the clean `description`, the skill supplies the implementation body. `scan`, `generate`, and `check` each collapsed from a (command + skill) pair into a single `/vibe-doc-<cmd>` workflow. `status` was **command-only** (no parallel skill) — it became a workflow whose body is the command's own `npx vibe-doc status` logic. `evolve-doc` was already a command + skill; it merged the same way and collapsed to `/vibe-doc-evolve`. `guide`, `session-logger`, and `friction-logger` stay internal skills. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full pattern and the `port.py` `commands/` enhancement.

## Skills (internal — loaded, not slash-invoked)

| Skill | Role |
|---|---|
| `vibe-doc-guide` | Situational reference detail: state schema, CLI patterns, output standards, the persona table, the Pattern #13 complement table, and pointers to the classification taxonomy / documentation matrix / breadcrumb-heuristic question sets. The always-on layer lives in `AGENTS.md`. |
| `vibe-doc-session-logger` | Sentinel (start) + terminal (end) session entries, paired by `sessionUUID`. |
| `vibe-doc-friction-logger` | Append-only friction capture at the trigger points in the guide's friction-triggers map. Conservative — when in doubt, don't log. |

## State files (per host project)

- `.vibe-doc/state.json` — the data contract: classification, scan results, gap lists, generation history. Written/read via the CLI, never hand-edited.
- `.vibe-doc/intake-profile.json` — optional Path-A intake answers, passed to the CLI via `--profile`.

Generated docs land in `docs/generated/<docType>.md` (and `.docx`) — a staging area. Promotion to the repo root is always an explicit user action. These are project-local and portable as-is.

## Cross-plugin / composition

vibe-doc works standalone. If a unified builder profile exists at `~/.gemini/profiles/builder.json` (created by an onboarding sibling like vibe-cartographer), vibe-doc reads it to calibrate tone/depth/persona and writes only to its own `plugins.vibe-doc` namespace. It also defers to specialist complements when they're available in the workspace (context7 for library-referencing docs, Figma for design docs, superpowers review/verification skills, `gh` for PRs/changelog input) — read-only detection, announce once, never probe, never auto-install.

## Privacy

No telemetry. The self-evolving session/friction logs (`~/.gemini/antigravity/data/vibe-doc/`) stay local. Delete them anytime; the plugin keeps working, just loses its memory.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-doc@0.8.0`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, the thin-command-wrapper → merged-workflow pattern this port introduced, every Claude → Antigravity adaptation, the open-question answers, and the vibe-doc-specific port notes appended at the end.
