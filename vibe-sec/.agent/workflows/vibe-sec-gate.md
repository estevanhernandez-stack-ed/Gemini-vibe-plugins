---
description: "CI pass/fail vs tier — exit codes 0/1/2 + GitHub Actions annotations"
---

# Vibe Sec — gate

The amplifier rule and the byte-for-byte-reproducible-gate rule are always-on via
`AGENTS.md`. The gate decision table, exit codes, and the `audit.json` read shape
are indexed in the `vibe-sec-guide` skill (`.agent/skills/vibe-sec-guide/SKILL.md`).

`/vibe-sec-gate` is the CI-safe gate. Deterministic, headless, no agent
reasoning in the decision path — it reads cached state and returns an exit code.
It does **not** re-scan; it consumes what `/vibe-sec-audit` already wrote, so CI
runs are fast and reproducible. Run `/vibe-sec-audit` first, or pin a tier.

## The decision (spec §2.4)

It reads `.vibe-sec/state/findings.jsonl` (deduped by id) + `audit.json` for the
tier, folds findings into per-concern results, and applies:

| Tier | Pass condition |
|---|---|
| Prototype | weighted ≥30%. Critical in concerns 1/2/7(LLM-burn) fails regardless |
| Internal | weighted ≥55%. No concern individually mandatory |
| Public-facing | weighted ≥70% **and** no High/Critical in concerns 3, 5, 7, 8 |
| Customer-facing SaaS | weighted ≥80% **and** no High/Critical in 1, 3, 4, 5, 6, 7, 8 |
| Regulated | weighted ≥90% **and** no High anywhere except #9 (threat-model is advisory) |

The severity amplifier (Critical → 0.5, High → 0.8 cap per concern) is applied
inside the weighted score, so "97% clean but one committed key" still fails.

## Exit codes

- `0` — pass (meets the tier bar, no blocking findings)
- `1` — fail (below threshold, or a High/Critical in a mandatory concern)
- `2` — scanner error (no cached audit + no pinned tier, bad tier, unreadable state)

## GitHub Actions annotations

When `GITHUB_ACTIONS=true`, emit workflow-command annotations:

- `::error file=…,line=…::[severity] title (concern)` for each blocking finding,
  placed on its source line so it lands in the PR diff.
- `::error::vibe-sec gate FAIL — <reasons>` for the verdict.
- `::notice::vibe-sec gate PASS — N% meets the <tier> bar` when clean.

## Running it

The gate is built TypeScript: `runGate(projectRoot, { tier?, githubActions? })`
in `src/gate/run-gate.ts`. It returns `{ exit, pass, score, threshold,
blockingConcerns, reasons, tier, annotations }`. The CLI surface drives it
headless — print the annotations, exit with the code. No fabricated findings,
no agent in the loop; the gate must be reproducible byte-for-byte across runs.

## What to tell the user

In an interactive invocation, lead with the verdict and the exit code: "Gate
FAIL (exit 1) — High in auth-model blocks the Public-facing bar." Name the
blocking concern + finding. In CI, the annotations + exit code are the output;
the chat transcript doesn't reach the runner.
