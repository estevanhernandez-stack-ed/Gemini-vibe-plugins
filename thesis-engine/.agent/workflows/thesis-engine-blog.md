---
description: "Adapt a Thesis Engine run folder (or thesis) into a Smart Brevity blog draft"
---

Execute **Stage 3 only** (Blog Adaptation) from the `/thesis-engine` router workflow (`.agent/workflows/thesis-engine.md`).

Source path: $ARGUMENTS (defaults to `./` — current working directory if no path is given).

Steps:
1. Read the source. If it's a Thesis Engine run folder, ingest `01_PLANNING/proposal.md` and the five `02_RESEARCH/<axis>/notes.md` files. If it's a single `THESIS.md`, ingest that.
2. Apply the Stage 3.1 distillation table to map source material to blog sections.
3. Produce `POST.md` per the Stage 3.2 specs (800–1,200 words, Smart Brevity tone, ≤60-char title, 3–5 tags).
4. Produce `frontmatter.yaml` per the Stage 3.3 schema.

Output destination: `<run>/blog/02_DRAFTS/YYYY-MM-DD-[slug]/` if running against a run folder; otherwise the same directory as the source thesis.

End by listing the output paths with `computer://` links and the ingest hint:
> Drop `blog/02_DRAFTS/<dated-slug>/` into `C:\Users\estev\Projects\BlogStudio\02_DRAFTS\`.
