# vibe-sec — Antigravity port

The Google Antigravity 2.0 port of [vibe-sec](https://github.com/estevanhernandez-stack-ed/vibe-sec), the 626Labs tier-aware security audit and orchestration layer for vibe-coded apps. Same brain — classify the tier, defer to the security tools you already have, run an in-house baseline when they're absent, calibrate severity, and ship a four-band report — repackaged for Antigravity's workflow + skill + rules model.

## What it does

Vibe-coded apps ship with a predictable, classifiable set of security gaps: secrets in source, auth as an afterthought, dependency roulette, overpermissive defaults. vibe-sec isn't another scanner — it sits **above** the security-tool stack. When gitleaks, OSV-Scanner, Semgrep CE, Trivy, or trufflehog are on the system it defers to them, parses their output, and re-frames it against your app's risk tier; when they're absent it runs an in-house TypeScript baseline. Either way vibe-sec owns the layer the tools don't: tier classification mapped to OWASP ASVS, severity calibration, the four-band report, confidence-routed fixes, and threat-model synthesis. The product is the layer, not the detector.

- **Router-first.** `/vibe-sec` reads cached audit state and recommends the next move — audit when there's no prior run, a re-run when it's stale, posture when it's fresh and clean.
- **Full tier-calibrated audit.** `/vibe-sec-audit` classifies the tier (inheriting from Vibe Test when present), runs the in-scope concern detectors, collects `findings.jsonl`, and renders the four-band report across markdown + terminal banner + sidecar.
- **Fast affordances.** `/vibe-sec-scan` (secrets, with full git-history walk) and `/vibe-sec-deps` (CVE + lockfile + pinning) are the muscle-memory fast paths.
- **CI gate.** `/vibe-sec-gate` is deterministic, headless, byte-for-byte reproducible — it consumes what audit wrote and returns an exit code (+ GitHub Actions annotations). No agent in the decision path.
- **Read-only posture.** `/vibe-sec-posture` is the cheap "where do I stand" read — never re-scans.
- **Confidence-routed fixes.** `/vibe-sec-fix` routes each finding by confidence, with hard destructive-action overrides (secret rotation, auth edits, JWT regen are always inline-runbook, never auto).
- **Threat-model synthesis.** `/vibe-sec-threat-model` is the sink node — STRIDE/DREAD synthesis emitting Mermaid + Threat-Dragon JSON.
- **Living research.** `/vibe-sec-research --concern <name>` re-runs one concern's domain research to refresh the briefs.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-sec`, `/vibe-sec-scan`, `/vibe-sec-audit`, `/vibe-sec-deps`, `/vibe-sec-fix`, `/vibe-sec-gate`, `/vibe-sec-posture`, `/vibe-sec-threat-model`, `/vibe-sec-research`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the `vibe-sec-guide` situational reference index).
   - **Rules** from `AGENTS.md` — always-on positioning, posture, tier→ASVS, severity amplifier, the four-band stance, OWASP coverage honesty, hard rules (the safety line), and voice.
3. The detection runs over the deterministic `vibe-sec` CLI (built TypeScript). Install it where the workspace can reach it (`npm install -g @esthernandez/vibe-sec`, or rely on `npx`); the `.agent/` skeleton carries the agent layer, not the compiled CLI binary.
4. First run: type `/vibe-sec` on a project. It reads state and routes you — usually to `/vibe-sec-audit`, which classifies the tier and establishes the baseline in `.vibe-sec/state/`.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-sec` | Router — state-aware next-step over cached `audit.json`. The entry point. |
| `/vibe-sec-scan` | Fast secret scan — defers to gitleaks/trufflehog, in-house regex/entropy/AST fallback, full git-history walk on first run. |
| `/vibe-sec-audit` | Full ten-concern tier-calibrated audit. Writes `findings.jsonl` + `audit.json`, renders the four-band report. |
| `/vibe-sec-deps` | Fast SCA — dependency CVE (OSV + npm-audit, deduped) + lockfile integrity + pinning. |
| `/vibe-sec-fix` | Confidence-routed remediation with hard destructive-action overrides and a closed `--auto` allowlist. |
| `/vibe-sec-gate` | CI pass/fail vs tier — exit codes 0/1/2 + GitHub Actions annotations. Consumes cached state, never re-scans. |
| `/vibe-sec-posture` | Read-only tier-aware summary from cached state. Reading never writes. |
| `/vibe-sec-threat-model` | STRIDE/DREAD synthesis sink node — Mermaid + Threat-Dragon-v2.5 JSON. |
| `/vibe-sec-research` | Re-run one concern's domain research to refresh the living briefs. |

## The shape that defined this port: commands+skills merge, run mechanically

vibe-sec has both a `commands/` directory (9 thin slash-entry wrappers) and a `skills/` directory (10 skills — the 9 command-parallel implementations plus `guide`). This is the same thin-command-wrapper shape vibe-doc introduced — and because vibe-doc already taught `port.py` the pattern, **this port ran fully mechanically: 9 command+skill pairs merged into 9 workflows, the lone `guide` skill stayed a skill, zero hand-reclassification.** The command supplies the slash identity + clean one-line `description`; the parallel skill supplies the implementation body; the standalone skill is dropped. `vibe-sec` (command + skill) collapsed to the bare router `/vibe-sec`; the other eight became `/vibe-sec-<cmd>`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the merge pattern.

## Skills (internal — loaded, not slash-invoked)

| Skill | Role |
|---|---|
| `vibe-sec-guide` | Situational reference index: where the tool-of-record registry, the `Finding`/`audit.json` schemas, the weighted-score + amplifier math, and the four-band report format spec live (the deterministic TypeScript source). The always-on layer lives in `AGENTS.md`. |

vibe-sec ships **no session-logger, no friction-logger, and no evolve workflow** — it's the minimal-internal shape (one guide skill, no telemetry hooks). The Level-2 self-evolution it describes lives in the CLI, not the agent surface.

## State files (per host project)

All project-local, carried verbatim across the port:

- `.vibe-sec/state/audit.json` — cached classification, score, gate verdict, counts, tools used, timestamp.
- `.vibe-sec/state/findings.jsonl` — append-only, deduped by id; the cross-plugin handoff sidecar **and** the composition spine.
- `.vibe-sec/state/history-scan.json` — incremental git-history scan boundary.
- `.vibe-sec/state/suppressions.json` — per-project suppressions.
- `.vibe-sec/pending/fixes/*.diff` — staged fixes awaiting `git apply`.
- `docs/vibe-sec/audit-report.md`, `docs/vibe-sec-threat-model.md`, `.vibe-sec/state/threat-model.json` — generated reports + the Threat-Dragon sidecar.

## Cross-plugin / composition

vibe-sec's commands compose through the **shared `findings.jsonl` + `audit.json` state**, not through silent sub-workflow calls. `/vibe-sec-audit` orchestrates over the TypeScript detectors directly and writes the state; `/vibe-sec-gate`, `/vibe-sec-posture`, and `/vibe-sec-threat-model` consume it. Cross-command mentions in the bodies (`run /vibe-sec-audit for the full pass`) are user-facing recommendations, not internal invocations — so Antigravity's unverified workflow-compose semantics don't bite this port. Composition is portable because the state files are portable.

It also inherits tier classification from **Vibe Test** when `.vibe-test/state/covered-surfaces.json` is present and fresh — the two plugins agree on tier unless a security-specific signal promotes it.

## Privacy

No telemetry. Per-project state (`.vibe-sec/state/`) and any home-dir profile (`~/.gemini/antigravity/data/vibe-sec/`) stay local. Delete them anytime; the plugin keeps working.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-sec@0.6.0`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, the thin-command-wrapper → merged-workflow pattern, every Claude → Antigravity adaptation, the open-question answers, and the vibe-sec-specific port notes appended at the end.
