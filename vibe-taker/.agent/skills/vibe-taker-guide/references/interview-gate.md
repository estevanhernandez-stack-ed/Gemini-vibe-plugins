# Interview gate

> Consumed by the [`/vibe-taker-capture`](/.agent/workflows/vibe-taker-capture.md) workflow. Resolves OQ-5's threshold heuristic.

The autonomous read pass does as much as it can without interruption. The interview gate fires only when the autonomous pass can't get to "shippable bundle" without a human signal — and even then, asks **at most 4 questions**, one at a time.

## Trigger conditions

The interview fires when **any** of these is true:

1. **Sparse notes** — `notes.md > Gotchas` count is < 3 substantive items (see [Substantive-item heuristic](#substantive-item-heuristic) below).
2. **No derivable intent** — `architecture.md > Summary` could not be derived because no source `README.md`-like prose exists and no top-of-file docstring on any entry point exists.
3. **Missing prompts despite LLM SDK** — `prompts/` is empty AND the captured dependencies include an LLM SDK (`openai`, `anthropic`, `cohere`, `bedrock`, `boto3` calling Bedrock, `ollama`, `langchain*`, `litellm`, etc.). Likely missed extraction.
4. **Slug collision** — autonomous-proposed slug already exists in `index.json`. The versioning prompt (`Bump to vN+1? [y/N]`) implies an interactive interview anyway; fold the questions in here.

If **none** of the above fires, the agent prints:

> intent derived autonomously — bundle ready at `<path>`; edit `notes.md` if anything's missing.

…and skips the interview entirely (PRD Capture story 6 final criterion).

## Substantive-item heuristic

A `notes.md > Gotchas` line counts as **substantive** when:

- **Length:** the line is **≥ 30 characters** after stripping leading bullet markers (`- `, `* `, `1. `).
- **Distinctiveness:** the line is **not** a near-duplicate of any line already in `architecture.md`. Concretely: Levenshtein distance to every line in `architecture.md` must be **≥ 8** (i.e., not just a re-statement of architecture content).

Stored as `contract.json.notes_completeness.substantive_count` (integer) for diagnostic carry to `/reflect`. Also stored: `interview_fired: bool`.

## The four questions

When the gate fires, ask these **one at a time**, in this order. Stop early if the user provides material for later questions in their answer to an earlier one.

### Q1 — What is this for?

> What is this *for*? Not what the code does — why it exists. One or two sentences.

Used to fill `notes.md > Why this exists` when the autonomous pass couldn't derive it. Also informs `summary` if `summary` is missing.

### Q2 — Shelf name

> Proposed shelf name: `<autonomous-slug>`. Keep it, or override?

The autonomous pass proposes a slug (`[a-z0-9][a-z0-9-]*`) from the source folder name or entry-point filename. User confirms or overrides. If override, validate against the slug pattern; re-ask if invalid.

This question also handles the slug-collision case: if the proposed slug already exists in `index.json`, frame it as:

> `<name>` already on the shelf at `<existing-path>` (latest version: `<vX>`). Bump to `<v(X+1)>`, or override the slug?

`bump` answer (or `y` / empty) → version bump. Override answer → new slug, re-validate.

### Q3 — Tradeoffs to preserve

> Any non-obvious tradeoffs to preserve? Things future-you would forget if it weren't written down.

Used to fill `notes.md > Tradeoffs preserved`. `n` / empty / `none` → write `None known.` and move on.

### Q4 — Tags for search

> Tags for search? Comma-separated. Suggested from autonomous read: `<tag1>, <tag2>, <tag3>`.

Suggested tags come from: `language`, `framework`, `interface_kind`, and any obvious nouns from the autonomous-derived summary. User accepts (`y` / empty) or types a comma-separated override. Tags are stored in both `contract.json.tags` and `index.json.bundles[].tags`.

## Skip rules

- **The interview is one-pass, no backtracking.** If the user wants to revise an earlier answer, they edit `notes.md` / `contract.json` directly after the bundle lands. Backtracking inside the interview would deepen the surface and slow capture for negligible benefit.
- **The interview can be aborted** at any prompt with empty input on a non-required question (Q3, Q4). Q1 and Q2 are required when fired — empty input re-asks the question.
- **Non-blocking questions:** Q3 and Q4 default to `None known.` / `[]` if the user types `n` / empty.

## Tuning

The thresholds (≥30 char substantive, Levenshtein ≥ 8 distinctiveness, < 3 substantive gotchas to fire) are v1 defaults from KTD-5 reasoning. Tune post-ship via friction signals at `/reflect` — first signal worth tracking.

The 30-char threshold catches typical sentence-shaped notes while filtering out one-word stubs. Levenshtein < 8 lets variations slip through (e.g., "Uses sharp" in architecture vs "Uses sharp; native binding issues on M1" in notes).
