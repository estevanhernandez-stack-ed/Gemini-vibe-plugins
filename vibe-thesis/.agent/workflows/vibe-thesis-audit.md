---
description: "Discipline-audit any markdown file for AI-writing tells — inflationary language, self-praise framings, defensive over-qualification, conclusions that re-assert importance. No vibe-thesis project required. Reports findings plus a one-line discipline-bar verdict. Advisory — doesn't auto-fix."
---

# /vibe-thesis-audit — Discipline Audit

Run the synthesis-guard lint against any markdown file — with or without a vibe-thesis project around it. Same patterns as `/vibe-thesis-guard`; no marker requirement; positional path argument.

## Why this exists

The synthesis-guard lint catches the dominant failure mode of LLM-generated writing: inflationary adjectives, self-praise framings, defensive over-qualification, and conclusions that re-assert importance. Inside a vibe-thesis project, it runs as a pre-render gate. Outside one, it's a public-grade discipline filter — useful for auditing blog drafts, AI outputs, peer-reviewed pieces, or any prose that should defend itself.

**This workflow drops the project-marker requirement.** Point it at any `.md` file. Get the same lint, plus a one-line verdict you can quote in a public scorecard.

The framing matters: this is a *discipline* filter, not an *AI-detection* filter. It catches writing that defaults to self-review tone. AI output edited to discipline-bar quality will pass — that's a feature. The bar is the product.

## Behavior

1. **Parse argument.** The first positional arg is the path. Accepts:
   - Single `.md` file: `/vibe-thesis-audit drafts/intro.md`
   - Directory: scans all `.md` files recursively (skips `node_modules/`, `.git/`, `bundles/`)
   - Optional `--strict` flag adds defensive-over-qualification + conclusion-re-assertion + hedging-with-importance patterns
   - Optional `--public` flag formats output as a shareable scorecard (see below)

2. **Refuse politely** if no path given or path doesn't exist. Name the missing path.

3. **Scan each file.** Line-by-line, skip code blocks (triple-backtick fences) and blockquote-prefixed citation lines. Apply the pattern tables below.

4. **Report per-finding:**

   ```text
   <file>:<line>  <pattern-category>  "<quoted offending phrase>"  → <one-line suggestion>
   ```

5. **One-line discipline verdict** at the end:
   - **0 findings:** `Pass — clean.`
   - **1–5 findings (standard set):** `Pass with advisories (<N> hits).`
   - **6–10 findings:** `Marginal — <N> hits across <M> files.`
   - **11+ findings:** `Fail — <N> hits across <M> files. Self-review tone dominant.`

6. **`--public` mode** swaps the verdict for a one-line scorecard suitable for quoting:
   - `[vibe-thesis-audit] Passes discipline bar (3 advisories, standard set)`
   - `[vibe-thesis-audit] Fails discipline bar (11 hits, standard set, self-praise dominant)`

7. **Exit cleanly always.** Advisory only — never blocks anything downstream.

## Pattern tables

### Standard (always-scanned)

| Category | Match | Suggestion |
|---|---|---|
| Inflationary | `\b(groundbreaking\|comprehensive\|rigorous\|definitive\|novel\|state-of-the-art\|seminal\|paradigm-shifting\|cutting-edge)\b` | Name what's covered or claimed instead. *"Comprehensive"* → list the dimensions. *"Novel"* → name what's new and what came before. |
| Self-praise framings | `\b(we make \w+ contributions?\|to the best of our knowledge\|no prior work has\|our approach uniquely\|this is the first\|we are the first to\|this work demonstrates that)\b` | Let the work demonstrate; don't announce the demonstration. Cite the comparison point if claiming first-ness. |

### Strict-only (additional patterns, `--strict`)

| Category | Match | Suggestion |
|---|---|---|
| Defensive over-qualification | `\b(despite limitations,?\|while \w+ is bounded\|notwithstanding\|albeit\|while not exhaustive)\b.{0,80}\b(demonstrate\|show\|prove\|establish\|evidence)` | Either the limitation matters (then own it without demonstrating around it) or it doesn't (then drop the qualifier). |
| Conclusion re-assertion | `(in conclusion\|to summarize\|in summary).{0,200}(profound\|important\|significant\|crucial\|critical\|opens new\|paves the way)` | Conclusions should restate findings, not their importance. Let the reader weigh significance. |
| Hedging-with-importance | `\b(arguably\|perhaps\|it could be said).{0,80}(important\|significant\|profound\|notable)` | If you have to argue significance, the work hasn't earned the claim. Strengthen the evidence or drop the importance claim. |

## Output examples

**Clean run, default mode:**

```text
0 findings across 1 file. Strict pattern set: no.
Pass — clean.
```

**Findings, strict mode:**

```text
drafts/intro.md:14   inflationary       "a comprehensive framework"   → "Comprehensive" → list the dimensions covered.
drafts/intro.md:23   self-praise        "to the best of our knowledge, no prior work has"   → Cite the comparison or rephrase positively.
drafts/conclusion.md:42  conclusion-reassertion (strict)   "These results have profound implications"   → Restate the findings. Significance is the reader's call.

3 findings across 2 files. Strict pattern set: yes.
Pass with advisories (3 hits).
```

**Findings, `--public` mode:**

```text
3 findings across 2 files. Strict pattern set: yes.
[vibe-thesis-audit] Pass with advisories (3 hits, strict set, mixed).
```

**Fail, `--public` mode:**

```text
14 findings across 3 files. Strict pattern set: no.
[vibe-thesis-audit] Fails discipline bar (14 hits, standard set, self-praise dominant).
```

## Edge cases

- Path doesn't exist → refuse with a clear message naming the path.
- Single empty file → `0 findings across 1 file (empty body). Pass — clean.`
- Directory with no `.md` files → `0 .md files under <path>. Nothing to audit.`
- File with 50+ findings → print the first 10, then `... <N more findings in this file. Re-run with --strict for full output.`
- Code blocks and citation blockquotes are skipped, same convention as `/vibe-thesis-guard`.

## Pattern source

The lint patterns are duplicated from `/vibe-thesis-guard` (`.agent/workflows/vibe-thesis-guard.md`). If you change the patterns there, mirror them here. There's no shared engine yet — intentional. Lift to a shared reference file only if patterns diverge or grow past ~30 entries.

## What NOT to do

- **Don't gate anything on this workflow.** It's advisory. `/vibe-thesis-render --guard` is what blocks renders, not this.
- **Don't extend with citation or claim-coverage checks here.** Those are separate concerns. If they're needed, add them as sibling workflows (`/vibe-thesis-check-citations`, `/vibe-thesis-claim-coverage`) and let the user compose.
- **Don't auto-fix.** Same reason as `/vibe-thesis-guard` — the writer revises.
- **Don't expand the pattern set without coordinating with `/vibe-thesis-guard`.** Drift between the two breaks the contract that audit is "guard, marker-free."

## Honest limit on the workflow itself

This catches the *modal failure mode* of LLM-generated writing as of 2026. As models improve, the patterns will need to evolve. Treat the lint as a snapshot of current AI tells, not a permanent definition of "human writing." The bar will rise.
