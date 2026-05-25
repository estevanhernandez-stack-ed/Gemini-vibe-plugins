---
description: "Research-feeder pipeline for vibe-thesis — discover topics, gather sources, optionally adapt to a blog draft"
---

# Thesis Engine — Research Feeder for vibe-thesis (router)

> Always-on posture (research-feeder, the five axes, BibTeX/Pandoc output contract, verify-before-citing, the vibe-thesis/ThesisStudio pairing, hard rules, voice) is in `AGENTS.md`. This is the orchestrator workflow — it owns the full Discover → Gather → Adapt implementation. The stage-scoped entry points (`/thesis-engine-discover`, `/thesis-engine-write`, `/thesis-engine-blog`, `/thesis-engine-run`) delegate to the matching stage(s) below. Curated discovery feeds live at `.agent/references/domain-feeds.md`.

A three-stage engine: **Discover → Gather → (optional) Adapt**.

The engine's job is to do the cold-start work that's painful inside vibe-thesis: scanning the field for live topics, pulling primary sources and opposing positions, and shaping them into vibe-thesis-compatible notes and a BibTeX bibliography. The drafting itself stays inside vibe-thesis where the persona and citation pipeline live.

**Routing:** running `/thesis-engine` (bare) executes the full pipeline (Stages 1 + 2; Stage 3 opt-in via `--blog`) — same as `/thesis-engine-run`. To run a single stage, use the stage entry points: `/thesis-engine-discover` (Stage 1), `/thesis-engine-write` (Stage 2), `/thesis-engine-blog` (Stage 3).

---

## What this engine is NOT

- It is not a thesis writer. The full-paper Stage 2 from v0.1 is gone — vibe-thesis's `03_BODY/` chapter scaffolding plus the LeadWriter persona handle the actual drafting.
- It is not a citation manager. It produces a BibTeX file. Merging into your canonical `05_CITATIONS/references.bib` is a manual or scripted step.
- It does not modify a live ThesisStudio. Output always lands in a dated run folder; the human (or a future ingest skill) copies subdirs across.

---

## Stage 1 — Topic Discovery

**Goal**: Surface 5 high-signal, low-competition thesis topics via web search.

### Step 1.1 — Domain Selection

Default domain is `ai_ml`. Honor explicit `--domain` arguments. Supported domains:

- `ai_ml` — AI / Machine Learning *(default)*. Capability research — model architectures, training, evals.
- `agentic_systems` — Multi-agent coordination, long-term memory, human-AI handoff design. Systems and HCI research, not capability research. Has axis-specific seed queries (see "Per-domain seed query overrides" below). 626 Labs alignment: every plugin coexists with the others, every plugin makes ask-vs-act calls dozens of times per session.
- `theater_ops` — Theater Technology & Operations
- `film_exhibition` — Film Distribution & Exhibition
- `spatial_xr` — Spatial Computing / XR
- `behavioral_econ` — Behavioral Economics
- `org_behavior` — Organizational Behavior
- `data_eng` — Data Engineering
- Any custom domain string

### Step 1.2 — Search for Cutting-Edge Topics

Run 3–5 web searches across these angles:

```
[domain] research breakthroughs 2025 2026
[domain] unsolved problems emerging trends
[domain] preprint arxiv notable 2025
[domain] industry disruption underreported
```

For each result cluster, extract:
- **Topic name** (5–10 words)
- **Novelty score** (1–5): Is this still emerging vs already mainstream?
- **Thesis potential** (1–5): Is there an arguable, researchable angle?
- **Relevance** (1–5): Connects to the user's domain mix?

### Step 1.2a — Per-Domain Seed Query Overrides

Some domains return weak topic candidates against the generic 4-angle template because their primary research surfaces aren't indexed by "research breakthroughs" or "preprint arxiv notable" searches. For these, use the override seeds below *in place of* the generic angles. Seeds are unsorted — run all of them, dedupe results, then score.

#### `agentic_systems`

The `ai_ml` template biases toward capability research (model architectures, training, evals). `agentic_systems` covers the systems and HCI research surfaces that 626 Labs actually depends on but that capability searches miss. Three axes with seed queries each:

```text
# Axis 1: Compositional agent coordination
"multi-agent coordination protocols 2025 production"
"blackboard architecture LLM agents"
"contract net protocol agentic systems"
"agent collision avoidance shared state"
"orchestrator-worker patterns multi-agent 2025"

# Axis 2: Long-term memory + ambient project awareness
"agentic memory architectures 2025"
"context compaction long-running agents"
"retrieval-augmented persistent agent state"
"ambient project awareness developer tooling agents"
"episodic vs semantic memory LLM agents"

# Axis 3: Human-AI handoff design (HCI of agentic systems)
"when agent should ask vs act LLM 2025"
"uncertainty-driven handoff agentic systems"
"interruption cost LLM agents productivity CHI CSCW"
"mixed-initiative interaction LLM agents"
"AI agent transparency disclosure HCI"
```

When scoring `agentic_systems` topics, weight Relevance against 626 Labs use cases: multi-plugin coexistence (Axis 1), persistent project context across the dashboard / vibe-cartographer / Architect AI (Axis 2), and the ask-vs-act decision every plugin makes (Axis 3). A topic that hits two axes scores higher than one that hits one strongly.

Venues to favor when scoring sources for this domain: CHI, CSCW, AAMAS, MIT Media Lab notes, Anthropic / Google DeepMind / Microsoft Research multi-agent papers, MIT Sloan / HBR on AI-augmented work. Venues to discount: pure capability benchmarks, standalone model papers without interaction studies.

### Step 1.3 — Present Top 5

Show a ranked table:

| # | Topic | Novelty | Thesis Potential | Relevance | Total |
|---|-------|---------|-----------------|-----------|-------|
| 1 | ...   | 4       | 5               | 4         | 13    |

Ask the user to pick one, or auto-select the top scorer if `--auto` is passed.

Write the table to `<run>/topics.md` so it survives the session.

---

## Stage 2 — Source Gathering

**Goal**: For the chosen topic, produce vibe-thesis-shaped research notes and a starter BibTeX bibliography.

### Output structure

```
thesis-engine-run-YYYYMMDD/
├── README.md                       (run summary + ingest instructions)
├── topics.md                       (Stage 1 ranking)
├── 01_PLANNING/
│   └── proposal.md                 (thesis proposal stub: what, why, scope)
├── 02_RESEARCH/
│   ├── prior-art/notes.md
│   ├── methodology-survey/notes.md
│   ├── opposing-positions/notes.md
│   ├── key-authors/notes.md
│   └── primary-sources/notes.md
└── 05_CITATIONS/
    └── references.bib              (BibTeX, Pandoc-ready)
```

The subdirectory names mirror the vibe-thesis Template exactly — drop them into `C:\Users\estev\Projects\ThesisStudio\` and they merge cleanly. `references.bib` should be appended to the canonical `05_CITATIONS/references.bib` (or replace it on a fresh project).

### Step 2.1 — Source Search

Run 5–8 targeted web searches structured by axis:

| Axis | Searches | Target output |
|------|----------|--------------|
| Prior art | "[topic] literature review", "[topic] survey 2024 2025" | 3–5 sources |
| Methodology | "[topic] methodology", "how researchers measure [topic]" | 2–3 sources |
| Opposing | "[topic] critique", "[topic] limitations", "against [topic]" | 2–3 sources |
| Key authors | "[topic] researchers", "leading [topic] scholars" | 2–4 named authors |
| Primary | preprints, datasets, original papers | 2–3 sources |

For each source, capture:
- Title
- Author(s)
- Year
- Venue (journal, conference, blog, preprint server)
- URL
- 2–3 sentence summary
- Pandoc citation key (`authoryear` style — e.g., `smith2024`)

### Step 2.2 — Write Research Notes

Each axis gets its own notes file with this template:

```markdown
# [Axis Name] — [Topic]

## Summary
[2–3 sentence framing of what this axis tells us about the topic]

## Sources

### [@citation-key] — [Title]
- **Author(s)**: ...
- **Year**: ...
- **Venue**: ...
- **URL**: ...
- **Why it matters**: 2–3 sentences specific to the thesis.
- **Quote / data point**: optional pull-quote.

### [@next-key] — ...
```

Use Pandoc citation keys throughout. Body claims should reference sources as `[@key]` so a future drafting step can lift them straight into `03_BODY/`.

### Step 2.3 — Write the Proposal Stub

`01_PLANNING/proposal.md`:

```markdown
# [Topic Title] — Thesis Proposal (Engine-Generated Stub)

> Generated by Thesis Engine on YYYY-MM-DD.
> Edit freely in vibe-thesis. The engine fills in scaffold; the human owns the argument.

## What this thesis argues
[1–2 sentence claim derived from Stage 1 scoring rationale]

## Why it matters
[Why now? What's the gap in the field? Pull from prior-art notes.]

## Scope
- **In scope**: ...
- **Out of scope**: ...

## Methodology sketch
[Pull from methodology-survey notes — what approach do similar studies use?]

## Anticipated counterarguments
[Pull from opposing-positions notes — name them now so vibe-thesis can address them in-text.]

## Next steps inside vibe-thesis
1. Decide `THESIS_MODE` (dissertation / article / masters).
2. Drop `02_RESEARCH/` and `05_CITATIONS/references.bib` into ThesisStudio.
3. Refine claim → run a research swarm via `04_AGENT_SWARMS/` if deeper coverage is needed.
4. Begin drafting in `03_BODY/`.
```

### Step 2.4 — Write the BibTeX File

`05_CITATIONS/references.bib`:

```bibtex
@article{smith2024,
  title   = {Title here},
  author  = {Smith, Jane},
  year    = {2024},
  journal = {Venue Name},
  url     = {https://...},
  note    = {Engine-gathered. Verify before citing.}
}

@inproceedings{jones2025,
  ...
}
```

Cite type rules: `@article` for journal/blog, `@inproceedings` for conference, `@misc` for preprints/datasets/web sources without a clear venue, `@book` for books.

The `note = {Engine-gathered. Verify before citing.}` line is intentional — it surfaces in rendered bibliographies and reminds the human to verify each entry before relying on it. Strip the note line after verification.

### Step 2.5 — Quality Gates

Before completing:

- [ ] At least 12 sources total across all axes (3+ prior art, 2+ opposing, others as found)
- [ ] Each source has a Pandoc citation key
- [ ] Each notes file references its sources with `[@key]` syntax
- [ ] `references.bib` parses (no malformed entries)
- [ ] `proposal.md` has a single explicit thesis claim
- [ ] Each `02_RESEARCH/<axis>/notes.md` has a Summary section

If any gate fails, surface the failed gates as a checklist in chat and write the partial run to `<run>/pending/`. Do not silently proceed.

---

## Stage 3 — Blog Adaptation (Optional)

**Goal**: From the Stage 2 proposal + research notes, produce a Smart Brevity blog draft for BlogStudio. This stage is optional and only runs when invoked via `/thesis-engine-blog` (or `--blog` on a full run).

### Output structure

```
thesis-engine-run-YYYYMMDD/
└── blog/
    └── 02_DRAFTS/
        └── YYYY-MM-DD-[slug]/
            ├── POST.md
            └── frontmatter.yaml
```

Subdirectory names mirror BlogStudio's live layout — drop `02_DRAFTS/<dated-slug>/` into `C:\Users\estev\Projects\BlogStudio\02_DRAFTS\` for ingest.

### Step 3.1 — Distillation Rules

| Source material           | Blog equivalent                          |
|---------------------------|------------------------------------------|
| `proposal.md` claim       | Hook paragraph + bold one-line headline  |
| Prior-art notes           | "What we thought we knew" (2–3 paragraphs) |
| Methodology notes         | Brief — only if methodology is the story |
| Opposing-positions notes  | "The strongest case against this" mini-section |
| Primary sources           | Pull-quote or data callout               |

### Step 3.2 — Blog Post Specs

- **Length**: 800–1,200 words
- **Tone**: Smart Brevity — punchy, scannable, no jargon, lead with the bottom line
- **Format**: `##` headers, paragraphs ≤3 sentences, 1–2 pull-quote callouts, bullet lists
- **Title**: ≤60 characters, curiosity-gap or claim style
- **Tags**: 3–5 keywords from topic + axes
- **Citations**: Inline link out (no Pandoc syntax — this is a blog draft, not a paper)

### Step 3.3 — frontmatter.yaml

```yaml
title: "..."
slug: "kebab-case-title"
excerpt: "1-2 sentence teaser, ≤140 chars"
tags: [tag1, tag2, tag3]
domain: "..."
source_run: "thesis-engine-run-YYYYMMDD"
generated_date: "YYYY-MM-DD"
status: draft
```

---

## Repeatable Run Protocol

When the user invokes `/thesis-engine` or `/thesis-engine-run`, execute Stages 1 + 2 in sequence. Stage 3 is opt-in via `--blog` or via the standalone `/thesis-engine-blog` command.

After a successful run:
1. Write `<run>/README.md` summarizing what was produced and how to ingest it into ThesisStudio.
2. Log a completion task to the 626Labs **Thesis Engine** project (project ID `6H02m934H97jNl15DzWe`) using `mcp__626labs__manage_tasks` action `create` with title `"Thesis run YYYY-MM-DD — [topic]"` and status `Done`. If the 626Labs MCP is unavailable, log a one-line note to chat and continue.
3. List the output paths in chat with `computer://` links.

---

## Recurring Cadence Options

| Frequency | Trigger | Output |
|-----------|---------|--------|
| Weekly    | Scheduled task `weekly-thesis-engine` (Mondays 8 AM, `--domain ai_ml --auto`) — manual-only in Antigravity (see AGENTS.md § Scheduling) | 1 topic + research bundle, no blog |
| On-demand | `/thesis-engine` or `/thesis-engine-run` | Same |
| Batch     | `/thesis-engine-run --count 3` | 3 topics + 3 research bundles |
| Discover-only | `/thesis-engine-discover` | Topic table only |
| Blog-only | `/thesis-engine-blog [run-folder-or-thesis.md]` | Blog draft from existing run or thesis |

---

## Integration Notes

- **vibe-thesis (ThesisStudio)** — `01_PLANNING/`, `02_RESEARCH/`, `05_CITATIONS/` from a run folder drop directly into `C:\Users\estev\Projects\ThesisStudio\`. Subdirectory names match exactly. Merge `references.bib` into the canonical bibliography.
- **BlogStudio** — `blog/02_DRAFTS/<dated-slug>/` drops into `C:\Users\estev\Projects\BlogStudio\02_DRAFTS\`.
- **626Labs MCP** — Each run logs a completion task to project `6H02m934H97jNl15DzWe`.
- **Citation style** — Pandoc `[@authorYear]` keys throughout, BibTeX bibliography. Matches vibe-thesis's render pipeline.

---

## References

See `.agent/references/domain-feeds.md` for a curated list of RSS feeds, preprint servers, and newsletters to seed Stage 1 discovery searches.
