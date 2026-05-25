---
description: "List bundles on the cross-repo shelf with one-line summaries. Supports search and sort."
---

# /vibe-taker-list

> List bundles on the cross-repo shelf with one-line summaries. (Implements the source plugin's List Flow Architecture / Epic: Library management.)

Read-only. **No writes.** Reads `~/.vibe-taker/library/index.json`, formats stdout. Lowest-risk command in the trio; the discovery surface for `/vibe-taker-plant`.

## Loading order — do this every time the workflow fires

Persona, voice, hygiene rules, and the error-class contract are **always-on via
[`AGENTS.md`](/AGENTS.md)** — already in context. List is read-only and never
writes, so it needs only the index shape:

1. **Read** [`.agent/skills/vibe-taker-guide/references/bundle-schema.md`](/.agent/skills/vibe-taker-guide/references/bundle-schema.md) — what `index.json` looks like.
2. **Read** [`.agent/skills/vibe-taker-guide/references/error-contract.md`](/.agent/skills/vibe-taker-guide/references/error-contract.md) — class-0/2 outcome shapes (no class-1 from `/vibe-taker-list`).

Then execute the phases below in order.

## Argument parsing

Form: `/vibe-taker-list [--search <query>] [--sort name|lang]`.

- `--search <query>` — case-insensitive substring across name, summary, tags, source-repo, language. `<query>` is one token (or quote-delimited).
- `--sort name` — alphabetical by `name`.
- `--sort lang` — group by `language`, then alphabetical within group.
- (Default sort) — `captured_at` of `latest_version` descending (most-recently-captured first).

Reject any other flags in v1:

```
[exit 1] Unknown flag `<flag>`. v1 supports: [--search <query>] [--sort name|lang]
```

## Phase 1 — index load

1. **Read** `~/.vibe-taker/library/index.json`.
2. **If absent** → exit class-0 (empty library is success, not failure):

   ```
   Library is empty. Run `/vibe-taker-capture <path>` to add your first bundle.
   ```

3. **If unparseable JSON** → exit class-2:

   ```
   [exit 2] Library index missing or corrupt at ~/.vibe-taker/library/index.json. Re-capture a feature to rebuild, or restore from backup.
   ```

4. **Validate** against `.agent/skills/vibe-taker-guide/schemas/index.schema.json`. On schema failure, exit class-2 with the schema error.

If `bundles` is an empty array (valid index but no entries), print the same empty-library message as the absent-file case and exit class-0.

## Phase 2 — search filter (optional)

When `--search <query>` is passed, filter `bundles[]` to those matching the query (case-insensitive substring) in **any** of:

- `name`
- `summary`
- `tags` (any tag matches)
- The `source_repo` of the bundle's **latest version** (`versions[-1].source_repo`)
- `language`

If the filtered set is empty, exit class-0 with:

```
no matches
```

When `--search` is absent, the working set is the full `bundles[]`.

## Phase 3 — sort

Apply the sort flag (or default).

- **Default** (`captured_at desc`) — for each bundle, compute `latest_captured_at` from the entry whose `version` matches `latest_version`. Sort descending by that timestamp.
- **`--sort=name`** — alphabetical by `bundles[i].name`. Tiebreaker: `latest_captured_at` descending.
- **`--sort=lang`** — primary key `language` ascending; secondary key `name` ascending.

Sort is stable: same comparison key → same ordering as input.

## Phase 4 — dedup hint (Jaccard, 70% default)

> Resolves OQ-2 default. KTD: 70% threshold; tunable post-ship without schema change.

For every pair of bundles in the working set (after filter, before sort — pair set is the same regardless of sort order), compute Jaccard token similarity over `summary` strings:

1. **Tokenize each summary:**
   - Lowercase.
   - Split on non-alphanumeric (`[^a-z0-9]+`).
   - Drop tokens with length < 2.
   - Drop English stop-words: `the, a, an, and, or, but, with, for, of, in, on, at, to, from, by, is, are, was, were, be, been, being, has, have, had, this, that, these, those, it, its`.
   - Result is a set (deduplicated).

2. **Compute Jaccard similarity** between every pair:
   ```
   J(A, B) = |A ∩ B| / |A ∪ B|
   ```
   (When the union is empty — both summaries were stop-word-only — the pair is skipped, similarity treated as 0.)

3. **If `J(A, B) ≥ 0.70`**, mark **both** bundles in the pair: append `[similar to: <other-name>]` to each one's listing block. A bundle similar to multiple others gets multiple `[similar to: …]` markers.

4. **Best-effort, runs at `/vibe-taker-list` time only** — never at `/vibe-taker-capture` time. PRD Library-management story 3 is explicit on this.

## Phase 5 — render

For each bundle in the (filtered + sorted) set, print one block:

```
<name> (<latest_version>)        <language> · <framework or "no framework">        <captured_at as YYYY-MM-DD>
  <summary>
  tags: <comma-separated tags>  [similar to: <other-name>]
```

Spacing rules:

- Name + version: left-aligned, padded to 24 chars (truncate longer names with `…`).
- Language + framework: padded to 28 chars.
- Date: `YYYY-MM-DD` form (strip the time component from the ISO timestamp).
- Each subsequent line indented with 2 spaces.
- The `[similar to: ...]` marker(s) appear inline at the end of the `tags:` line, one space-separated per pair.
- If `tags` is empty, omit the `tags:` line.
- If multiple bundles have versions other than `v1`, that's already shown in `(<latest_version>)` — no extra annotation needed.
- One blank line between blocks.

### Header

When `--sort=lang`, prefix each language group with a one-line section header:

```
=== python (3) ===
```

Where `(3)` is the count in that language group. No header for default sort or `--sort=name`.

### Footer

After all blocks, print one summary line:

```
<count> bundle(s)<sort-clause><filter-clause>
```

Where:

- `<sort-clause>` is `, sorted by <name|lang|captured_at desc>`.
- `<filter-clause>` is `, filtered by --search '<query>'` when search was applied; otherwise empty.

Example: `5 bundles, sorted by captured_at desc, filtered by --search 'image'`.

## Phase 6 — exit

Class-0 in all success branches:

- Bundles printed → class-0.
- Empty library → class-0 with the empty-library message.
- `--search` no matches → class-0 with `no matches`.

Class-2 only on:

- Index file present but unparseable JSON.
- Index file present but fails schema validation.

There is no class-1 outcome for `/vibe-taker-list` in v1 — the library being empty isn't a "decline," it's a clean state.

## Worked examples

### Empty library

```
Library is empty. Run `/vibe-taker-capture <path>` to add your first bundle.
```

### Single bundle, default sort

```
bg-remover (v2)        python · cli-argparse        2026-05-07
  AI-powered CLI background remover. Takes an image path, returns transparent-bg version.
  tags: cli, image, ai

1 bundle, sorted by captured_at desc
```

### Two near-duplicates flagged

```
bg-remover (v1)        python · cli-argparse        2026-05-07
  AI-powered CLI background remover. Takes an image path, returns transparent-bg version.
  tags: cli, image, ai  [similar to: bg-remove-tool]

bg-remove-tool (v1)    python · cli-typer           2026-05-08
  AI-driven CLI tool to remove image backgrounds. Returns a transparent PNG.
  tags: cli, image, ai  [similar to: bg-remover]

2 bundles, sorted by captured_at desc
```

### Search miss

```
no matches
```

### `--sort=lang`

```
=== python (2) ===
bg-remover (v1)        python · cli-argparse        2026-05-07
  AI-powered CLI background remover.
  tags: cli, image

config-loader (v1)     python · none                 2026-04-22
  Loads YAML config with environment overlays.
  tags: config, yaml

=== typescript (1) ===
slack-relay (v1)       typescript · express         2026-04-15
  Relay incoming Slack events to a webhook with HMAC validation.
  tags: slack, webhook

3 bundles, sorted by lang
```

## Failure modes recap

- **Index file present but corrupt** → class-2 with the recovery line.
- **Schema validation fails** → class-2 with the path + schema error.
- **All other branches** (empty, no-match search, normal print) → class-0.

The dedup-hint computation is best-effort. If a malformed bundle entry breaks tokenization mid-flight, skip that pair and continue; never bring down the listing for a hint feature.
