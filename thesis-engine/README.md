# thesis-engine — Antigravity port

The Google Antigravity 2.0 port of [thesis-engine](https://github.com/estevanhernandez-stack-ed/Thesis-Engine), the 626Labs research-feeder for vibe-thesis projects. Same brain — Discover → Gather → (optional) Adapt — repackaged for Antigravity's workflow + rules model. It does the cold-start research work that's painful inside vibe-thesis: scanning a field for live topics, pulling primary sources and opposing positions, and shaping them into vibe-thesis-shaped notes plus a BibTeX bibliography.

## What it does

A three-stage engine that feeds vibe-thesis. It is **not** a thesis writer and **not** a citation manager — it produces *inputs* (topic candidates, research notes, a proposal stub, a starter bibliography); the argument, the prose, and the canonical bibliography stay inside vibe-thesis / ThesisStudio.

1. **Discover (Stage 1)** — runs web searches across a chosen domain (default `ai_ml`; `agentic_systems` has its own three-axis seed overrides), scores candidates on novelty / thesis-potential / relevance, and presents a ranked top-5 table. You pick the topic (or pass `--auto` to take the top scorer).
2. **Gather (Stage 2)** — for the chosen topic, runs axis-structured searches across the **five research axes** (prior art, methodology, opposing positions, key authors, primary sources), writes per-axis notes with Pandoc `[@key]` citations, a proposal stub, and a Pandoc-ready `references.bib`. Runs a mandatory quality-gate checklist before completing.
3. **Adapt (Stage 3, optional)** — distills a run folder (or a `THESIS.md`) into a Smart Brevity blog draft for BlogStudio.

Output always lands in a dated `thesis-engine-run-YYYYMMDD/` folder whose subdirectory names mirror the vibe-thesis Template exactly, so it drops cleanly into ThesisStudio.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/thesis-engine`, `/thesis-engine-run`, `/thesis-engine-discover`, `/thesis-engine-write`, `/thesis-engine-blog`).
   - **Rules** from `AGENTS.md` — the always-on layer (research-feeder posture, the five axes, the BibTeX/Pandoc + verify-before-citing output contract, the vibe-thesis pairing, hard rules, voice).
3. There are **no skills** in this port — thesis-engine has no shared-behavior `guide` skill and no loggers. The whole implementation lives in the `/thesis-engine` router workflow body; the stage entry points delegate to it. Situational data (the curated discovery feeds) lives at `.agent/references/domain-feeds.md`; a packaging helper lives at `.agent/scripts/package_skill.py`.
4. To run the full pipeline: type `/thesis-engine` (bare) or `/thesis-engine-run`. To run a single stage, use the stage entry points below.

## Workflows

| Workflow | What it does |
|---|---|
| `/thesis-engine` | Router / orchestrator — the eponymous, user-invoked entry point (the router form). Bare run = the full pipeline (Stages 1 + 2; Stage 3 opt-in via `--blog`). Owns the full Discover → Gather → Adapt implementation. |
| `/thesis-engine-run` | Full pipeline (Stages 1 + 2; `--blog` adds Stage 3). Same as bare `/thesis-engine`. |
| `/thesis-engine-discover` | Stage 1 only — surface 5 ranked topic candidates in a domain. |
| `/thesis-engine-write` | Stage 2 only — gather sources + research notes for a given topic. |
| `/thesis-engine-blog` | Stage 3 only — adapt a run folder (or `THESIS.md`) into a Smart Brevity blog draft. |

The 4 stage workflows are thin entry points that delegate into the matching stage(s) of the `/thesis-engine` router — the implementation lives in one place.

## The output contract

- **Notes use Pandoc `[@authorYear]` citation keys**; the bibliography is **BibTeX** (`05_CITATIONS/references.bib`), Pandoc-ready. This matches vibe-thesis's render pipeline.
- **Every engine-gathered entry carries `note = {Engine-gathered. Verify before citing.}`** — the verify-before-citing safety contract. The engine gathers via web search and can surface a plausible-but-wrong source; strip the note only after a human verifies. This is a hard rule, not boilerplate.
- **The run folder mirrors the vibe-thesis Template exactly** (`01_PLANNING/`, `02_RESEARCH/<axis>/`, `05_CITATIONS/`), so a run drops cleanly into ThesisStudio. Blog drafts (`blog/02_DRAFTS/<dated-slug>/`) drop into BlogStudio.

## Composes with

thesis-engine is the front of a two-tool flow: **engine feeds, vibe-thesis drafts.** It works standalone, but its whole purpose is to seed a vibe-thesis project — drop a run folder's `01_PLANNING/` / `02_RESEARCH/` / `05_CITATIONS/` into ThesisStudio and merge `references.bib` into the canonical bibliography. It never replaces the drafting work inside vibe-thesis (the LeadWriter persona, the citation pipeline, the `03_BODY/` chapter scaffolding).

## Open questions (Antigravity primitives — not invented)

- **Scheduling:** the Claude Code original listed a weekly scheduled task. **Manual-only in this port** — run `/thesis-engine-run --domain ai_ml --auto` on demand. No cron primitive is wired (none confirmed for Antigravity).
- **626Labs MCP logging:** best-effort. A successful full run logs a completion task to the 626Labs Thesis Engine project; if the MCP is unavailable, it notes one line in chat and continues. The run is never gated on MCP.
- **No hooks, no loggers, no builder.json, no sidecars.** thesis-engine has no `hooks/` dir, no session/friction loggers, doesn't read `~/.claude/profiles/builder.json`, and has no silent sub-workflow composition. The full open-question re-check is in the cookbook entry.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `thesis-engine@0.2.1`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow mapping, every Claude → Antigravity adaptation, the open questions, and the thesis-engine-specific port notes (the eponymous-main-defaulted-to-skill case — where port.py doubled the eponymous skill `thesis-engine-thesis-engine` instead of recognizing it as the router; the thin-stage-command reconciliation; the scripts/references carry out of the collapsed skill) appended at the end.
