# vibe-test — Antigravity port

The Google Antigravity 2.0 port of [vibe-test](https://github.com/estevanhernandez-stack-ed/vibe-test), a 626Labs test auditor and generator for vibe-coded apps. Same brain — classify the app, audit coverage honestly, generate the tests that actually matter proportional to deployment risk, gate CI on the tier threshold — repackaged for Antigravity's workflow + skill + rules model.

## What it does

Vibe coding ships features fast; the tests lag. vibe-test reads your code, classifies it by app type (6) and maturity tier (5) with context modifiers, measures coverage against an **honest denominator** (no cherry-picked scope), and generates the tests proportional to how the app actually ships — explained like a teacher, never a gatekeeper. Eight workflows over a deterministic CLI surface and a state-file-mediated self-evolving framework.

- **The bare router.** `/vibe-test` greets you, detects first-run vs returning state, lists the six subcommands in plain language, and asks where you want to start — no scan, under 10 seconds, `git status` energy.
- **Audit.** `/vibe-test-audit` scans, classifies (app type + tier + modifiers), measures honest coverage, and ranks gaps with rationales tied back to the classification. The entry diagnostic. Writes `covered-surfaces.json` for vibe-sec.
- **Generate.** `/vibe-test-generate` turns audit findings into test files — confidence-tiered: auto-write / stage for review / show inline.
- **Fix.** `/vibe-test-fix` diagnoses and repairs broken tests and harnesses (F2: a broken harness is reported before any score).
- **Coverage.** `/vibe-test-coverage` is honest-denominator measurement with tier interpretation.
- **Gate.** `/vibe-test-gate` is a single CI pass/fail against the app's tier threshold, sharing the locked weighted-score function with the audit classifier.
- **Posture.** `/vibe-test-posture` is a read-only ambient summary — no scans, no writes, suggests the next move as a question.
- **Self-evolution.** `/vibe-test-evolve` reads its own session + friction + wins logs, weights them with absence-of-friction inference (Pattern #14), and proposes plugin improvements (L3). Runs a `vitals` structural pre-flight first. Never auto-applies.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root. The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-test`, `/vibe-test-audit`, `/vibe-test-coverage`, `/vibe-test-fix`, `/vibe-test-gate`, `/vibe-test-generate`, `/vibe-test-posture`, `/vibe-test-evolve`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the internal loggers, decay, vitals, and the `vibe-test-guide` reference detail).
   - **Rules** from `AGENTS.md` — always-on persona, posture, the F2 honest-coverage stance, tier-classification stance, composition posture, hard rules.
3. The workflows lean on the `@esthernandez/vibe-test` CLI/library surface (scanner, coverage adapters, generator, reporter, handoff writers). Install it where the workspace can reach it (`npm install -g @esthernandez/vibe-test`, or rely on `npx`). The CLI binary is `vibe-test` with **space-separated subcommands** (`vibe-test audit`) — distinct from the hyphenated Antigravity slash names (`/vibe-test-audit`).
4. First run: type `/vibe-test` for the intro, then `/vibe-test-audit` to classify + find gaps, `/vibe-test-generate` to close them, `/vibe-test-gate` before you ship.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-test` | The bare router — identity, first-run/returning detection, subcommand list, next-step prompt. No scan, no writes beyond the session log. |
| `/vibe-test-audit` | Scan + classify (app type + tier + modifiers) + honest coverage + ranked gaps. Writes audit state + `covered-surfaces.json`. |
| `/vibe-test-generate` | Confidence-tiered test generation for the audit's gaps. |
| `/vibe-test-fix` | Diagnose + repair broken tests and harnesses. |
| `/vibe-test-coverage` | Honest-denominator coverage with tier interpretation. |
| `/vibe-test-gate` | CI pass/fail against the tier threshold. |
| `/vibe-test-posture` | Read-only ambient summary — suggests the next move as a question, never executes. |
| `/vibe-test-evolve` | L3 self-evolution — vitals pre-flight + friction/wins/session aggregation → proposals. Never auto-applies. |

## The two classification calls that defined this port

vibe-test is the family's richest commands+skills plugin (8 commands, 14 skills). `port.py` did the seven clean command+skill merges mechanically, but missed two cases the finishing pass corrected:

- **Cross-named command+skill pair → merged router.** The `vibe-test` command and the `router` skill are the **same** entry point — `router`'s description is *"used when the user says `/vibe-test` (bare)… the entry point."* They don't share a name, so `port.py`'s same-name merge missed it and emitted **two** workflows (`/vibe-test` and `/vibe-test-router`). The fix folds the `router` skill's implementation (greet / first-run-detect / list-subcommands / decay-at-start) into the `/vibe-test` workflow body — the command supplies the slash identity, the skill supplies the body — and deletes the duplicate. One `/vibe-test` router.
- **Slash-mention false-positive → vitals demoted to skill.** `port.py` promoted `vitals` to a `/vibe-test-vitals` workflow because its source description *mentions* a slash. But the source self-label reads (Claude-Code form) *"Internal SKILL — not a slash command in v0.2 — invoked by `/vibe-test:evolve` as a read-only pre-flight."* The mentioned slash is the **caller** (`evolve`), not vitals' own trigger — vitals is not user-typed. The fix demotes it to an internal skill (`.agent/skills/vibe-test-vitals/`) that the `/vibe-test-evolve` workflow invokes as a pre-flight. A user-facing `/vibe-test-vitals` workflow is slated for v0.3.

See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for both lessons and the recommended `port.py` guards.

## Skills (internal — loaded, not slash-invoked)

| Skill | Role |
|---|---|
| `vibe-test-guide` | Situational reference detail: the full classification matrix (6 app types × 5 tiers × modifiers), data contracts, JSON schemas, templates, the anchored complement registry, the friction-trigger map, and the session-memory interface index. The always-on layer lives in `AGENTS.md`. |
| `vibe-test-vitals` | Pattern #8 structural self-test — seven read-only checks. Internal in v0.2: invoked only by `/vibe-test-evolve` as a pre-flight. Never writes. |
| `vibe-test-decay` | Pattern #4 profile-decay — re-validates stale builder-profile fields; the router runs `check_decay()` at first-run-of-the-day. |
| `vibe-test-session-logger` | Two-phase session entries (sentinel at start, terminal at end), paired by `sessionUUID`. |
| `vibe-test-friction-logger` | Append-only friction capture at the guide's trigger points; `detect_orphans()` for abandoned sentinels. Conservative — when in doubt, don't log. |
| `vibe-test-wins-logger` | Pattern #14 wins capture — counter-balance to friction in `/vibe-test-evolve` weighting. |

## State files (per host project)

- `.vibe-test/state/audit.json` (or `audit-<hash>.json` scoped) — classification + gaps.
- `.vibe-test/state/*.json` — per-command sidecars (coverage, gate, generate, evolve).
- `.vibe-test/pending/` — staged tests awaiting review.
- `covered-surfaces.json` — written by audit for vibe-sec consumption (two-way handshake).
- `docs/vibe-test/audit-<date>.md`, `docs/TESTING.md` — human-readable reports.

Project-local state is portable as-is; only the home-dir self-evolution logs repoint.

## Cross-plugin / composition

vibe-test works standalone. It **reads** a unified builder profile at `~/.gemini/profiles/builder.json` (created by an onboarding sibling like vibe-cartographer) for persona / experience-level / testing-experience calibration, and writes only `_meta` decay stamps to its own `plugins.vibe-test` namespace. Composition is **state-file-mediated** — `/vibe-test-evolve` reads the jsonl logs; vitals is an internal pre-flight skill invocation, not a silent sub-workflow call. Pattern #13 complements (vibe-doc for prose, vibe-sec for security-aware prioritization, playwright for UI, superpowers TDD/debugging/verification) are deferred to when available in the workspace — read-only detection, announce once, never probe, never auto-install.

## Privacy

No telemetry. The self-evolving session/friction/wins logs (`~/.gemini/antigravity/data/vibe-test/`) stay local. Delete them anytime; the plugin keeps working, just loses its memory.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-test@0.2.3`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, the cross-named-pair merge and the slash-mention-false-positive lessons this port introduced, every Claude → Antigravity adaptation, the open-question answers, and the vibe-test-specific port notes appended at the end.
