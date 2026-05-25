---
description: "Run when the user says '/vibe-keystone-evolve' or wants Keystone to reflect on its past runs and propose improvements to itself. Reads the opt-in capture log at ~/.gemini/antigravity/data/vibe-keystone/captures.jsonl, finds patterns (sections always dropped, sections always overridden, repo-types the classifier keeps getting wrong, sections users keep asking for), and proposes concrete skeleton/classifier edits to the keystone workflow. Never auto-applies."
---

# /vibe-keystone-evolve — Reflect on past runs, propose skeleton improvements

Slash command `/vibe-keystone-evolve`. This is Tier 1 of Keystone's evolution loop — the reflective half that reads the opt-in capture signal Tier 0 produces (`Step 6` of the `/vibe-keystone` workflow) and proposes concrete improvements to the skeleton and the repo-type classifier.

**Nothing auto-applies.** This workflow reads capture data and writes proposals to `proposed-changes.md`. It never edits the `/vibe-keystone` workflow itself — that's the user's call, one proposal at a time. (Mirrors the never-auto-apply discipline of `vibe-cartographer:evolve-cart`.)

## Why this exists

Keystone produces the load-bearing context file, then never sees it again — so without a sensor it can't tell which parts of its skeleton are wrong. Tier 0 capture (opt-in) records a small structural note per run. This workflow mines those notes for patterns the maintainer would otherwise only learn anecdotally:

- A skeleton section the user **drops almost every time** → it's probably over-included; make it more conditional, or cut it.
- A default the user **overrides the same way almost every time** → the default is likely wrong; propose flipping it.
- A repo type the **classifier keeps getting wrong** (`repo_type_autodetected ≠ repo_type_final`) → the Step 0 signals need tuning.
- A section users **keep asking for that the skeleton doesn't offer** → propose adding it.

## Before You Start

- **Read the capture log:** `~/.gemini/antigravity/data/vibe-keystone/captures.jsonl`. Each line is one opt-in run capture (schema in the `/vibe-keystone` workflow's Step 6).
- **Read the current skeleton:** `.agent/workflows/vibe-keystone.md` — Step 2 (the section skeleton) and Step 0 (the classifier signals). Proposals must point at real locations in this file. (In the Claude Code source this lived at `skills/keystone/SKILL.md`; in this port it is the `/vibe-keystone` router workflow.)

## Suppression — not enough signal yet

Capture is opt-in, so the log fills slowly. If the log is **missing, empty, or has fewer than 5 entries**, do not propose. Report exactly:

> Not enough capture signal yet (N entries; need 5+). Capture is opt-in — turn it on at the end of `/vibe-keystone` runs, and re-run `/vibe-keystone-evolve` once a handful have accumulated.

Then stop. Proposing from 1-2 runs would be noise dressed as insight.

## Flow

1. **Parse** every line of `captures.jsonl` as JSON. Silently skip malformed lines (note the count in the report). Apply the suppression rule above.

2. **Aggregate** across the valid captures:
   - **Section drop rate:** for each skeleton section, `dropped_count / total_runs`.
   - **Section override rate + direction:** for each section, how often it's overridden and to what.
   - **Classifier miss rate:** fraction of runs where `repo_type_autodetected ≠ repo_type_final`, broken down by `(autodetected → final)` pair.
   - **Requested-but-missing sections:** cluster the free-text `sections_requested_not_in_skeleton` labels; count near-duplicates together.

3. **Rank by confidence** (frequency-weighted — more runs behind a pattern = higher confidence). These thresholds are initial guesses, to be tuned as the corpus grows:
   - **High:** pattern holds in ≥70% of runs AND ≥5 runs.
   - **Medium:** 40–70%, or ≥70% but only 3–4 runs.
   - **Low:** below that — mention only as "watch," don't propose a change.

4. **Write proposals** to `proposed-changes.md` at the repo root (append a dated section if the file already exists — Keystone's harness task force already uses `proposed-changes-harness.md`, so keep this one named `proposed-changes.md`). For each proposal:
   - The pattern and its evidence (rate, run count, confidence).
   - The exact skeleton/classifier location it maps to (`.agent/workflows/vibe-keystone.md` Step 2 §<section>, or Step 0 classification).
   - The concrete edit proposed.
   - A one-line "why it pays."

5. **Report** a short banner to the user: how many captures were read, how many patterns surfaced at each confidence level, and the path to `proposed-changes.md`. End with: "Nothing was changed. Review the proposals and apply the ones you agree with."

## Hard constraints

- **Never edit `.agent/workflows/vibe-keystone.md`.** Propose only. The user applies.
- **Never transmit anything.** This workflow reads a local file and writes a local file. No network — consistent with `PRIVACY.md`.
- **Ground every proposal in capture evidence.** No proposal without a rate and a run count behind it. If the signal is thin, say so and downgrade to "watch."
- **Don't fabricate captures.** If the log is short, the answer is the suppression message, not invented patterns.

## Why this is Tier 1, not the full Cartographer stack

Keystone is a once-per-repo generator, not a multi-session workflow — so it does not get friction logging, session logging, or decay (that would be cargo-culting machinery built for a different shape of tool). The evolution loop it *does* get is the minimal pair: opt-in structural capture (Tier 0) + reflective proposal (Tier 1). A drift-doctor that watches already-shipped AGENTS.md files age is a separate product, deliberately out of scope here.
