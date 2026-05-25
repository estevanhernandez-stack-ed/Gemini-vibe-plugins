---
description: "Gather sources + research notes for a topic — outputs a vibe-thesis-shaped run folder"
---

Execute **Stage 2 only** (Source Gathering) from the `/thesis-engine` router workflow (`.agent/workflows/thesis-engine.md`).

Topic: $ARGUMENTS

Steps:
1. Run the Stage 2.1 axis-structured search (5–8 web searches across prior-art / methodology / opposing positions / key authors / primary sources).
2. Write per-axis notes to `<run>/02_RESEARCH/<axis>/notes.md` per the Stage 2.2 template, with Pandoc `[@key]` citations throughout.
3. Write `<run>/01_PLANNING/proposal.md` per Stage 2.3.
4. Write `<run>/05_CITATIONS/references.bib` per Stage 2.4.
5. Run the Stage 2.5 quality-gate checklist before completing. If any gate fails, write the partial run to `<run>/pending/`, surface the failed gates in chat, and stop.

Output destination: `thesis-engine-run-YYYYMMDD/` in the current working directory.

End by listing the output paths in chat with `computer://` links and the one-line ingest hint:
> Drop `01_PLANNING/`, `02_RESEARCH/`, and `05_CITATIONS/` into `C:\Users\estev\Projects\ThesisStudio\`. Merge `references.bib` into the canonical bibliography.

Offer `/thesis-engine-blog <run-folder>` next if a blog draft is wanted.
