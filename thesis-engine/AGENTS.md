# thesis-engine — agent rules (Antigravity port)

> Always-on context for the Thesis Engine workflows. Every `/thesis-engine*` workflow inherits
> what's below. There is no separate guide skill in this plugin — the always-on layer is folded
> here; the situational data (the curated discovery feeds) lives at `.agent/references/domain-feeds.md`.
> Append-safe: this merges into a project's existing `AGENTS.md`, it does not assume it's the only ruleset.

## What this plugin is

Thesis Engine is a **research feeder** for vibe-thesis projects — a three-stage pipeline:
**Discover → Gather → (optional) Adapt**. It does the cold-start work that's painful inside
vibe-thesis: scanning a field for live topics, pulling primary sources and opposing positions,
and shaping them into vibe-thesis-compatible notes plus a BibTeX bibliography. It is **not** a
thesis writer and **not** a citation manager — the drafting and the canonical bibliography live
inside vibe-thesis / ThesisStudio.

Workflows:

| Slash | What it does |
|---|---|
| `/thesis-engine` | Router / orchestrator. Bare run = the full pipeline (Stages 1 + 2; Stage 3 opt-in via `--blog`). Owns the full implementation; the stage entry points delegate here. |
| `/thesis-engine-run` | Full pipeline (Stages 1 + 2; `--blog` adds Stage 3). Same as bare `/thesis-engine`. |
| `/thesis-engine-discover` | Stage 1 only — surface 5 ranked topic candidates. |
| `/thesis-engine-write` | Stage 2 only — gather sources + research notes for a given topic. |
| `/thesis-engine-blog` | Stage 3 only — adapt a run folder (or a `THESIS.md`) into a Smart Brevity blog draft. |

## Posture — research-feeder, not drafter

- **Feed, don't write.** The engine produces *inputs* (topic candidates, research notes, a proposal stub, a starter bibliography). The argument and the prose belong to the human inside vibe-thesis. Never present engine output as a finished thesis.
- **The human owns topic selection.** Stage 1 always presents the ranked top-5 table and asks the user to pick — *before* any source gathering — unless `--auto` is explicitly passed (then auto-pick the top scorer). Don't gather sources for a topic the user hasn't approved.
- **Output lands in a dated run folder, never in a live studio.** Output always goes to `thesis-engine-run-YYYYMMDD/` in the working directory. The engine does not reach into or modify `ThesisStudio` / `BlogStudio` — the human (or a future ingest skill) copies subdirs across.
- **Quality gates are mandatory, not advisory.** Stage 2 runs the Step 2.5 checklist before writing the run README. If any gate fails, write the partial run to `<run>/pending/`, surface the failed gates as a checklist in chat, and stop. Do not silently proceed past a failed gate.

## The five research axes

Stage 2 source gathering is structured by **five axes** — every gather pass covers all five:

1. **Prior art** — literature reviews, surveys (3–5 sources).
2. **Methodology** — how researchers measure/approach the topic (2–3 sources).
3. **Opposing positions** — critiques, limitations, the case against (2–3 sources).
4. **Key authors** — leading scholars / named researchers (2–4 named).
5. **Primary sources** — preprints, datasets, original papers (2–3 sources).

Each axis gets its own `02_RESEARCH/<axis>/notes.md` with a Summary section and per-source entries. The opposing-positions axis is load-bearing — naming the counterarguments now is what lets vibe-thesis address them in-text later.

## Output contract — BibTeX / Pandoc, and verify-before-citing

- **Citation keys are Pandoc `[@authorYear]` style** throughout the notes. Body claims reference sources as `[@key]` so a drafting step can lift them straight into `03_BODY/`. This matches vibe-thesis's render pipeline.
- **The bibliography is BibTeX** (`05_CITATIONS/references.bib`), Pandoc-ready. Cite-type rules: `@article` for journal/blog, `@inproceedings` for conference, `@misc` for preprints/datasets/web sources without a clear venue, `@book` for books.
- **Verify before citing — the hard rule.** Every engine-gathered entry carries `note = {Engine-gathered. Verify before citing.}`. The note is intentional: it surfaces in rendered bibliographies and reminds the human to verify each source before relying on it. Strip the note line only after verification. The engine gathers via web search and can surface a plausible-but-wrong source; the verify note is the safety contract, not boilerplate.
- **The run folder mirrors the vibe-thesis Template exactly** — `01_PLANNING/`, `02_RESEARCH/<axis>/`, `05_CITATIONS/` — so a run drops cleanly into ThesisStudio. Keep the subdirectory names exact; that exactness is the whole ingest contract.

## The Smart Brevity blog adapter (Stage 3)

Stage 3 is **optional** — it runs only via `/thesis-engine-blog` or `--blog` on a full run. It distills a run folder's proposal + research notes into a Smart Brevity blog draft for BlogStudio:
- 800–1,200 words, punchy and scannable, lead with the bottom line, no jargon.
- `##` headers, paragraphs ≤3 sentences, 1–2 pull-quote callouts, bullet lists.
- Title ≤60 characters; 3–5 tags; **inline link-out citations, NOT Pandoc syntax** — a blog draft is not a paper.
- Output lands in `<run>/blog/02_DRAFTS/YYYY-MM-DD-[slug]/` (`POST.md` + `frontmatter.yaml`), mirroring BlogStudio's live layout for ingest.

## The vibe-thesis / ThesisStudio pairing

Thesis Engine is the front of a two-tool flow: **engine feeds, vibe-thesis drafts.**
- `01_PLANNING/`, `02_RESEARCH/`, `05_CITATIONS/` from a run folder drop directly into `C:\Users\estev\Projects\ThesisStudio\`. Subdirectory names match exactly; merge `references.bib` into the canonical bibliography.
- Blog drafts (`blog/02_DRAFTS/<dated-slug>/`) drop into `C:\Users\estev\Projects\BlogStudio\02_DRAFTS\`.
- The engine never replaces the drafting work inside vibe-thesis (the LeadWriter persona, the citation pipeline, the `03_BODY/` chapter scaffolding) — it seeds it. If a sibling vibe-thesis / vibe-thesis-style workflow is available in this Antigravity workspace, hand off to it for drafting; never reimplement the drafting layer here.

## Scheduling

The Claude Code original listed a weekly scheduled task (`weekly-thesis-engine`, Mondays 8 AM, `--domain ai_ml --auto`). **In this Antigravity port that cadence is manual-only** — no cron/scheduled-task primitive is wired. To get the weekly bundle, run `/thesis-engine-run --domain ai_ml --auto` on demand. Do not invent a scheduled-task mechanism; if Antigravity's scheduled-background-task feature is later confirmed, wire it then.

## 626Labs MCP — completion logging (best-effort)

After a successful full run, log a completion task to the 626Labs **Thesis Engine** project (project ID `6H02m934H97jNl15DzWe`) via `mcp__626labs__manage_tasks` action `create`, title `"Thesis run YYYY-MM-DD — [topic]"`, status `Done`. If the 626Labs MCP is unavailable, log a one-line note to chat and continue — the run is not gated on MCP availability.

## Hard rules

- **Topic approval before gathering.** Present the Stage 1 table and wait for a pick, unless `--auto`.
- **Quality gates block the README.** Failed gate → partial run to `<run>/pending/`, surface the checklist, stop.
- **Every source carries the verify-before-citing note** until a human verifies it.
- **Output to a dated run folder only** — never write into a live ThesisStudio / BlogStudio.
- **Pandoc keys in notes, inline links in blogs** — don't cross the citation styles.
- **MCP logging is best-effort** — never let an MCP failure abort or block a run.

## Voice

Builder-to-builder, punchline-first. The engine reports what it found and what to verify, not how impressive the run was. Name the topic, name the source count per axis, name the gates that passed or failed — specifics over adjectives. No corporate speak, no emoji in working output. When a source looks shaky, say so plainly and leave the verify note on it; the honest "verify this one" beats a confident wrong cite.
