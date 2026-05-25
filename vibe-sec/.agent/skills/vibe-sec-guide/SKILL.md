---
name: vibe-sec-guide
description: "Situational reference index for the Vibe Sec workflows — where the tool-of-record registry, the Finding/audit JSON schemas, and the four-band report format spec live. The always-on layer (persona, posture, tier→ASVS, severity amplifier, hard rules, voice) is in AGENTS.md. Loaded by a workflow when it needs to validate a write or render the report. Not a slash command — do not invoke directly."
---

# Vibe Sec — guide (thin index)

The always-on behavior — positioning, the defer-when-present posture, the
tier→ASVS map, the severity amplifier, the four-band stance, OWASP coverage
honesty, the hard rules (the safety line, the `--auto` allowlist, mask-always,
read-never-writes), the composition model, and the voice — lives in
**`AGENTS.md`** (merged into the project's ruleset at install). Read it first;
it's ambient context for every workflow.

This skill is the **situational layer**: the exact shapes and rules a workflow
touches only when it's mid-flight and about to write state or render the report.

## Where the situational detail lives

vibe-sec's heavy reference detail is in the **deterministic TypeScript source**
(`src/` in the source repo), not duplicated here as markdown. A workflow
orchestrates over these entry points — it does not hand-fabricate findings or
report rows. When you need the exact shape, read the source:

| Concern | Source of truth | Used by |
|---|---|---|
| **Tool-of-record registry** (which tool wins per concern, PATH probe order) | `src/orchestration/tool-registry.ts`, `src/orchestration/defer.ts` | every detection workflow (`/vibe-sec-scan`, `/vibe-sec-audit`, `/vibe-sec-deps`) |
| **The `Finding` schema** + `primary_concern` / `secondary_concerns[]` dedup rule | `src/types.ts`, the `to-findings` mappers under `src/detectors/*` | `/vibe-sec-audit`, `/vibe-sec-scan`, `/vibe-sec-deps` (any writer of `findings.jsonl`) |
| **The `audit.json` state shape** | `src/state/audit-state.ts` | `/vibe-sec-audit` (writer); `/vibe-sec-gate`, `/vibe-sec-posture` (readers) |
| **Weighted score + severity amplifier math** | `src/scoring/weighted-score.ts`, `src/scoring/severity-amplifier.ts` | `/vibe-sec-audit`, `/vibe-sec-gate` |
| **The four-band report format spec** (band assembly, OWASP-grouped subsection, banner) | `src/report/bands.ts`, `src/report/markdown.ts`, `src/report/banner.ts` | `/vibe-sec-audit`, `/vibe-sec-posture` |
| **Fix routing + destructive-action map + `--auto` allowlist** | `src/fix/route.ts`, `src/fix/apply.ts`, `src/fix/stage.ts`, `src/fix/suppression.ts` | `/vibe-sec-fix` |
| **Gate decision table + exit codes + GH-Actions annotations** | `src/gate/run-gate.ts` | `/vibe-sec-gate` |
| **Threat-model assembly + locked Mermaid convention** | `runThreatModel` (threat-model entry) | `/vibe-sec-threat-model` |
| **The full thesis** (the why behind the layer, the three-layer model, scope) | `framework.md` in the source repo | background / `/vibe-sec-research` |

> Note: the deterministic CLI (`src/`, `dist/cli.js`) is **not carried into
> `.agent/`** — it's published from the source repo. Workflow bodies that
> reference `node .agent/dist/cli.js` or `src/...` entry points name the build
> contract; the actual binary ships with the npm package, not the port skeleton.

## Data directories

- **Global:** `~/.gemini/antigravity/data/vibe-sec/` (Claude Code original:
  `~/.claude/plugins/data/vibe-sec/`).
- **Per-project state:** `<project>/.vibe-sec/state/` — see `AGENTS.md § State
  files` for the full list (carried verbatim across the port).
