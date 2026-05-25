# vibe-iterate — Antigravity port

The Google Antigravity 2.0 port of [vibe-iterate](https://github.com/estevanhernandez-stack-ed/vibe-iterate), a 626Labs post-ship product-iteration plugin. Same brain — Ptolemy, the shipped-product-conservative cartographer — repackaged for Antigravity's workflow + skill + rules model.

## What it does

Your app is shipped. Now what? vibe-iterate picks the next move and ships it as one PR — regression-aware, small-diff-preferred, no surprise breaking changes.

- **Pick a mode:** `/vibe-iterate-feature-add` (multi-source candidate scan), `/vibe-iterate-competitive` (gap-close vs competitors), `/vibe-iterate-ux-polish` (fix shipped-but-rough surfaces), `/vibe-iterate-bug-bash` (fix the top user-reported bug).
- **Reach for a sidecar:** `/vibe-iterate-radar` (what's new digest), `/vibe-iterate-spy <url>` (one-shot competitor read), `/vibe-iterate-scan-releases [pkg]` (release diff), `/vibe-iterate-rate <idea>` (score an idea), `/vibe-iterate-ship <brief>` (express-lane build), `/vibe-iterate-upgrade <pkg>` (surgical library bump).
- **Route or set up:** `/vibe-iterate` (bare — recommends a mode), `/vibe-iterate-bootstrap` (first-run setup).
- **Self-evolve:** `/vibe-iterate-evolve` reflects on your past sessions and proposes improvements to itself. No auto-apply.

Every iteration writes an Atlas entry (`.vibe-iterate/atlas.jsonl`) naming what was considered, what won, what didn't. The Atlas is the per-project memory that keeps the agent from re-proposing the same thing twice.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-iterate-feature-add`, `/vibe-iterate-radar`, etc.).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the internal `vibe-iterate-session-logger`, `vibe-iterate-friction-logger`, and the `vibe-iterate-guide` reference detail).
   - **Rules** from `AGENTS.md` — always-on persona, posture, knowledge sources, Cart-detection, hard rules.
3. First run: type `/vibe-iterate`. On a fresh repo it hands off to `/vibe-iterate-bootstrap`, which identifies the app type, infers framework pins, and asks for competitor URLs — then writes `.vibe-iterate/config.json`.
4. After setup, re-run `/vibe-iterate` for a mode recommendation, or invoke a mode directly.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-iterate` | Bare router — reads project state, recommends one mode, asks before launching |
| `/vibe-iterate-bootstrap` | First-run setup — classifies the app, infers pins, asks for competitors, writes config |
| `/vibe-iterate-feature-add` | Ship the next feature from a multi-source candidate scan |
| `/vibe-iterate-competitive` | Close a competitor gap, ranked by strategic relevance (not parity) |
| `/vibe-iterate-ux-polish` | Fix a shipped-but-rough UI surface, scored on user-trust impact |
| `/vibe-iterate-bug-bash` | Fix the top user-reported bug from `feedback.md` |
| `/vibe-iterate-radar` | Read-only digest of what's new across stack + competitors |
| `/vibe-iterate-spy <url>` | One-shot competitive read on a single URL |
| `/vibe-iterate-scan-releases [pkg]` | Per-package release diff (breaking changes, codemods, security) |
| `/vibe-iterate-rate <idea>` | Score a feature idea against your shipped product |
| `/vibe-iterate-ship <brief>` | Express-lane build from a hand-written brief |
| `/vibe-iterate-upgrade <pkg>` | Surgical single-library bump with codemod + tests |
| `/vibe-iterate-evolve` | Reflect on past sessions, propose improvements to itself (L3) |

## Composes with

- **vibe-cartographer** (optional) — when present and an iteration is heavy (3+ subsystems / new domain concept / >1 day), vibe-iterate delegates scope → prd → spec to Cart and runs its own build against Cart's spec. Works standalone when Cart isn't installed.
- **context7** (optional MCP) — live framework-docs lookups at decision-time.

## Privacy

No telemetry. The Atlas and the self-evolving session/friction logs (`~/.gemini/antigravity/data/vibe-iterate/`) stay local. Delete them anytime; the plugin keeps working, just loses its memory.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-iterate@1.1.0`. See [`PORTING.md`](PORTING.md) for the exact mapping (skill → workflow vs skill → skill), every Claude → Antigravity adaptation, and open questions. PORTING.md is the cookbook seed for porting the rest of the vibe-* family.
