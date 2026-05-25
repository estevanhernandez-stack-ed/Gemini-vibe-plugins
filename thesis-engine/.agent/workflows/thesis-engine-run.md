---
description: "Run the Thesis Engine pipeline — discover a topic, gather sources for vibe-thesis"
---

Run the full Thesis Engine pipeline — execute Stages 1 + 2 from the `/thesis-engine` router workflow (`.agent/workflows/thesis-engine.md`).

Arguments: $ARGUMENTS

Defaults:
- If `--domain` is not specified, use `ai_ml`.
- If `--auto` is present, skip the topic-confirmation step in Stage 1 and pick the top scorer.
- If `--count N` is present, repeat Stages 1 + 2 N times against the same Stage 1 ranking.
- If `--blog` is present, also run Stage 3 to produce a blog draft.

Output destination: a dated subfolder `thesis-engine-run-YYYYMMDD/` inside the current working directory. The run folder mirrors vibe-thesis subdirectory names (`01_PLANNING/`, `02_RESEARCH/<axis>/`, `05_CITATIONS/`) so it drops cleanly into `C:\Users\estev\Projects\ThesisStudio\`.

Stage gates are mandatory:
- Show the Stage 1 ranking table before gathering sources.
- Run the Stage 2.5 quality-gate checklist before writing the run README. If any gate fails, write the partial run to `<run>/pending/` and stop.
- After a successful run, log a completion task to the 626Labs **Thesis Engine** project (project ID `6H02m934H97jNl15DzWe`) using `mcp__626labs__manage_tasks` action `create` with title `"Thesis run YYYY-MM-DD — [topic]"` and status `Done`.

End the run by listing the output paths in chat with `computer://` links and a one-line ingest hint:
> Drop `01_PLANNING/`, `02_RESEARCH/`, and `05_CITATIONS/` into `C:\Users\estev\Projects\ThesisStudio\`. Merge `references.bib` into the canonical bibliography.
