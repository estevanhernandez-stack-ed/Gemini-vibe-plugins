---
description: "Capture a feature out of the current repo as a portable bundle on the cross-repo shelf."
---

# /vibe-taker-capture

> Capture a feature out of the current repo as a portable bundle on the cross-repo shelf. (Implements the source plugin's Capture Flow Architecture / Epic: Capture.)

The harder half of vibe-taker. Read the target with no human input first; only ask the user when WHY can't be derived from source alone.

## Loading order — do this every time the workflow fires

Persona, voice, the capture posture (read source autonomously, interview only
when WHY can't be derived), the hygiene rules, atomic-write discipline, and the
error-class contract are **always-on via [`AGENTS.md`](/AGENTS.md)** — they're
already in context. Then load the situational reference detail capture needs:

1. **Read** [`.agent/skills/vibe-taker-guide/references/bundle-schema.md`](/.agent/skills/vibe-taker-guide/references/bundle-schema.md) — what artifacts you're producing and what shape they take.
2. **Read** [`.agent/skills/vibe-taker-guide/references/secret-patterns.md`](/.agent/skills/vibe-taker-guide/references/secret-patterns.md) — what to skip and how to detect load-bearing secrets.
3. **Read** [`.agent/skills/vibe-taker-guide/references/interview-gate.md`](/.agent/skills/vibe-taker-guide/references/interview-gate.md) — when to interview, what to ask.
4. **Read** [`.agent/skills/vibe-taker-guide/references/error-contract.md`](/.agent/skills/vibe-taker-guide/references/error-contract.md) — class-0/1/2 outcome shapes.

Then execute the phases below in order. Validate `contract.json` / `index.json`
against the schemas in `.agent/skills/vibe-taker-guide/schemas/` before any write.

## Argument parsing

The command form is `/vibe-taker-capture <path|file|glob>`. The argument is a single token (path, filename, or glob pattern). No flags in v1.

**Special case — in-file selector** (e.g., `file.py:120-180`, `module.ts#function`, anything with `:<number>` or `#<symbol>` after a path): **decline immediately**. Print verbatim:

```
[exit 1] vibe-taker captures whole files, folders, or globs in v1. Selection-within-a-file isn't supported — extract to its own file first or capture the parent file.
```

Exit class-1. **No bundle written.** PRD Capture story 4.

## Phase 1 — target resolution

| Input pattern | Resolution | Behavior |
|---|---|---|
| Single file (`scripts/foo.py`) | One file | `reference/foo.py`. `architecture.md` notes "single-file feature." |
| Folder (`apps/bg-remover/`) | Recursive read of folder | Preserve relative tree under `reference/<basename>/`. |
| Glob (`packages/auth/**`) | All matches under glob root | Preserve relative tree under `reference/` from glob root. Empty match → exit 1, "no files matched" error. |
| In-file selector | Decline | (Handled in argument parsing above.) |

**Verify before proceeding:** if the path doesn't exist (and isn't a glob), exit class-1:

```
[exit 1] Target `<path>` not found. Pass an existing path or a glob.
```

If the input looks like a glob (contains `*`, `?`, `[`, `**`) and matches zero files, exit class-1:

```
[exit 1] No files matched glob `<pattern>`. Check the pattern or `cd` to the right directory.
```

Resolve to a list of absolute file paths in scope. Carry the **glob root** (deepest directory that's a literal prefix of the glob) as `reference_root` — preserved tree under `reference/` is relative to this.

## Phase 2 — autonomous read pass

Walk every file in scope. **No interview yet.** This is the autonomous-extraction layer PRD Capture story 5 expects.

### 2.1 Language sniff

For each file:

- **By extension first:** `.py → python`, `.ts/.tsx → typescript`, `.js/.mjs/.cjs/.jsx → javascript`, `.rs → rust`, `.go → go`, `.cs → csharp`, `.rb → ruby`, `.sh/.bash → bash`.
- **Shebang fallback** for extensionless files.
- **Aggregate** to a primary language (most-frequent non-config extension across the captured tree). Carry the count distribution to inform `notes.md` if multi-language.

### 2.2 Manifest detect

Scan the captured tree for:

| Manifest | Implies |
|---|---|
| `package.json` | Node — read `dependencies`, `devDependencies`, `bin`, `[engines]`, `type`. |
| `pyproject.toml` | Python — read `[project].dependencies`, `[project.scripts]`, `[tool.poetry]`. |
| `requirements.txt` | Python — line-per-dep with optional version pins. |
| `Cargo.toml` | Rust — read `[dependencies]`, `[[bin]]`. |
| `*.csproj` | C# — XML `<PackageReference>`. |
| `Gemfile` | Ruby — `gem '<name>', '<version>'`. |
| `go.mod` | Go — `require` block. |

Extract `language`, `framework`, `dependencies` for `contract.json`. Framework is the highest-signal dep present:

- Python: `fastapi` / `flask` / `django` / `pandas` / `click` / `typer` / `argparse` (always available, treat as `cli-argparse` only when the entry-point uses it).
- Node: `express` / `fastify` / `next` / `react` / `vue` / `svelte` / `yargs` / `commander`.
- Rust: any crate name in the family table.
- Go: any in family table.

If multiple matches, prefer the framework most strongly bound to the entry-point file. If still ambiguous, pick the first hit and note the ambiguity in `notes.md`.

### 2.3 Entry-point identification

Heuristic by language:

- **Python:** files containing `if __name__ == "__main__"`, files registered as `[project.scripts]` in `pyproject.toml`, or single-file scripts with shebangs.
- **Node:** files referenced under `"bin"` in `package.json`, files with shebangs, or `index.{js,ts}` at the root, or files with a top-level `commander` / `yargs` invocation.
- **Rust:** `[[bin]]` entries in `Cargo.toml`, `src/main.rs`.
- **Go:** files with `package main` and a `func main()`.
- **Other:** shebanged files; files matching `main.*`, `cli.*`, `__main__.*`.

Record absolute paths within the captured tree. Will be relativized to `reference/` paths in `contract.json.entry_points`.

### 2.4 I/O surface extraction

By language and framework:

**Python:**

- `argparse.ArgumentParser` calls — extract `add_argument` declarations (name, type, required, help).
- `click` decorators (`@click.command`, `@click.option`, `@click.argument`).
- `typer` function signatures and `typer.Option` / `typer.Argument` annotations.
- `sys.argv` direct usage → input shape `[{"name":"argv","type":"other","description":"raw sys.argv passthrough"}]`.

**Node:**

- `yargs` chain (`.option`, `.command`, `.demandCommand`).
- `commander` chain (`.option`, `.argument`, `.command`).
- Direct `process.argv` indexing → similar `argv` passthrough input.

**Outputs:**

- Writes to `sys.stdout` / `console.log` (with shape detection — if it's JSON-shaped, mark as structured stdout).
- File-write calls with explicit paths: `open(path, "w")`, `Path(path).write_text`, `fs.writeFileSync`.
- Return values from named main functions when statically inferrable.

**Env vars:** regex-grep across all captured files (not just entry points) for:

- `os.environ\[["']([A-Z_][A-Z0-9_]*)["']\]`
- `os\.getenv\(["']([A-Z_][A-Z0-9_]*)["']`
- `process\.env\.([A-Z_][A-Z0-9_]*)`
- `Deno\.env\.get\(["']([A-Z_][A-Z0-9_]*)["']`
- `getenv\("([A-Z_][A-Z0-9_]*)"\)` (C-family)

Each unique env-var name → an entry in `contract.json.env_vars`. Default `load_bearing: true` when the env var is read **without** a default fallback in the same call (`os.getenv("X", "default")` → `load_bearing: false`); otherwise `true`.

### 2.5 Prompt extraction

For every file:

- Find string literals **>100 characters** passed as an argument to a known LLM SDK call. Recognized SDK call sites:
  - **OpenAI:** `openai.ChatCompletion.create`, `openai.chat.completions.create`, `client.chat.completions.create`, `client.responses.create`.
  - **Anthropic:** `anthropic.messages.create`, `client.messages.create`.
  - **Cohere:** `cohere.chat`, `co.chat`.
  - **Bedrock:** `bedrock.invoke_model`, `boto3.client("bedrock-runtime")...invoke_model`.
  - **Ollama:** HTTP POST to `/api/generate` or `/api/chat` with a `prompt`/`messages` body.
  - **Generic:** any function call with the literal argument name `prompt=`, `system=`, `messages=`, `instructions=`.
- Each matched string → `prompts/<descriptive-name>.txt`. Name the file from the variable name when the prompt is assigned (`SYSTEM_PROMPT = "..."` → `system_prompt.txt`); from the call site otherwise (`anthropic_system.txt`).

Save the prompts in-memory at this phase. Files write happens in Phase 7 (item 6).

### 2.6 Intent extraction

Read every:

- `README.md`, `README.rst`, `README.txt` in scope.
- `CHANGELOG.md`.
- Top-of-file docstring (Python: triple-quoted at top of file; JS/TS: leading `/** ... */`).
- Top-of-file comment block.

Build:

- `notes.md > Why this exists` — synthesize from intent material. Lead with a 1-2 sentence "what this is for, beyond what the code does" line, then bullets for non-obvious context.
- `architecture.md > Summary` — 1-3 sentences derived from the intersection of source README + entry-point docstrings.
- `summary` (one-liner for `index.json` and `README.md` of the bundle) — distill the architecture summary.

If **no intent material exists** (no README, no docstrings, no top comments), set `architecture.md > Summary = null` for now — the interview gate will fire in Phase 5 (item 6).

### 2.7 Gotcha pattern-match

Walk `dependencies`. For each, check the known list:

| Dep matches | Gotcha bullet to add |
|---|---|
| `sharp` | "Uses `sharp` — native binding; check Apple Silicon support; first-install often pulls platform-specific binaries." |
| `pillow` / `PIL` | "Uses Pillow — may need libjpeg/zlib system libs at install on minimal base images." |
| `playwright` | "Uses Playwright — first-run downloads browser binaries (~300 MB)." |
| `tensorflow` / `torch` / `pytorch` | "Uses ML framework — GPU optional; CPU fallback can be slow on large inputs." |
| Contains `aws` | "Cloud SDK — check default region behavior; `AWS_REGION` env var typically required." |
| Contains `gcp` / `google-cloud-` | "Cloud SDK — service-account credentials typically required (`GOOGLE_APPLICATION_CREDENTIALS`)." |
| Contains `azure` | "Cloud SDK — check default Azure region/subscription resolution." |
| `selenium` | "Uses Selenium — needs a separate WebDriver binary on PATH." |
| `ffmpeg-python` / `imageio-ffmpeg` | "Wraps `ffmpeg` — system binary required (not pulled by pip)." |

Add matched bullets to `notes.md > Gotchas`. Multiple matches → multiple bullets. No matches → `Gotchas` may end up empty (interview gate will fire on `< 3 substantive items` in Phase 5).

## Phase 3 — secret-file skip

Apply the patterns from [`secret-patterns.md`](/.agent/skills/vibe-taker-guide/references/secret-patterns.md). For every file in scope:

1. **Match basename and repo-relative path** against the glob list (case-insensitive on Windows).
2. **Apply carve-outs** — `.env.example`, `.env.sample`, `.env.template`, `.env.local.example`, the secret-patterns reference itself, documented loader files.
3. **If matched and not carved out: skip** the file from `reference/`. Add to a `skipped[]` list in memory.

For each skipped file, **before discarding**:

1. Compute basename minus extension; convert to UPPER_SNAKE.
2. Search the **non-skipped** captured files for:
   - `import` / `require` / `from … import` of the basename.
   - `dotenv.config()`, `load_dotenv()`, `dotenv.load()` calls.
   - `os.environ[…]` / `os.getenv(…)` / `process.env.<X>` references whose key matches a pattern derived from the basename or earlier-extracted env vars.
3. **If a match is found, mark the skipped file as load-bearing.** Add a stub to `contract.json.env_vars`:
   ```json
   { "name": "<INFERRED_NAME>", "load_bearing": true, "description": "Inferred from skipped <repo-relative-path>; provide at plant-time." }
   ```
4. **Print a warning** in the stdout summary (Phase 4) per PRD Capture story 8:

   > Skipped X secret-like files that look load-bearing. Capture continues with these stubbed in `contract.json` under `env_vars`. Provide them at plant-time.

The print itself happens in the summary; this phase only marks state.

## Phase 4 — slug proposal

Propose a slug from the captured target:

1. **Folder capture** → folder basename, lowered, non-`[a-z0-9-]` collapsed to `-`, leading/trailing `-` stripped.
2. **Single-file capture** → filename without extension, same normalization.
3. **Glob capture** → glob root basename if it's a real directory; else the longest-common-prefix of matched files' basenames.

Validate against the slug pattern `^[a-z0-9][a-z0-9-]*$`. If the proposal is empty or fails validation (e.g., starts with a digit-then-non-slug-char), set `slug-proposed = null` — the interview will ask the user.

## Phase 5 — versioning detection

Read `~/.vibe-taker/library/index.json`. (If the file is absent, treat as `{ "schema_version": "1.0", "bundles": [] }`.) Look for an entry whose `name` matches `slug-proposed`.

- **No match** → no version conflict; the new bundle will be `<name>/v1/`. Continue to Phase 6.
- **Match found** → fire the bump prompt. The interview gate (Phase 6) will fold the slug-confirmation question (Q2) around this. Print before asking:

  ```
  `<name>` already on the shelf at `~/.vibe-taker/library/<name>/<latest_version>/`. Bump to `<v(n+1)>`? [y/N]
  ```

  - On `y` (or empty when already-bump-framed) → set `target_version = v(n+1)`, set `version_bump = true`. If the existing on-disk layout is bare `<name>/` (no version subdir), mark `migrate_legacy = true`.
  - On `n` → exit class-1: `[exit 1] No changes. Existing bundle at <path>.`

  - Anything else (a slug override) → re-run Phase 5 with the new slug; if no collision, continue with the new slug as `<name>/v1/`.

`target_version` defaults to `v1` when there's no collision.

## Phase 6 — interview gate

Apply the trigger conditions from [`interview-gate.md`](/.agent/skills/vibe-taker-guide/references/interview-gate.md):

The gate fires when **any** of:

1. `notes.md > Gotchas` count is < **3 substantive items** (line ≥ 30 chars after stripping bullet markers, AND Levenshtein ≥ 8 to every line in `architecture.md`).
2. `architecture.md > Summary` could not be derived (Phase 2.6 left `summary` null).
3. `prompts/` would be empty AND captured `dependencies` include an LLM SDK (`openai`, `anthropic`, `cohere`, `boto3` calling Bedrock, `ollama`, `langchain*`, `litellm`).
4. The slug collided in Phase 5 (versioning prompt is fired — fold the questions in).

If **none** fires, **skip the interview** and print:

```
intent derived autonomously — bundle ready at <path>; edit `notes.md` if anything's missing.
```

Set `notes_completeness.interview_fired = false`. Continue to Phase 7.

When the gate fires, ask the four questions **one at a time**, in order. Stop early if the user provides material for later questions in their answer to an earlier one.

### Q1 — What is this for?

> What is this *for*? Not what the code does — why it exists. One or two sentences.

- Required when fired. Empty input re-asks.
- Used to fill `notes.md > Why this exists` and (if missing) the bundle `summary`.

### Q2 — Shelf name (folds in versioning prompt)

If `version_bump` is true:

> `<name>` already on the shelf (latest: `<vX>`). Bump to `<v(X+1)>`, or override the slug?

If `version_bump` is false:

> Proposed shelf name: `<slug>`. Keep it, or override?

- `y` / empty / `bump` → confirm bump (when applicable).
- New slug string → re-run Phase 5 with the new slug. If no longer a collision, set `target_version = v1`.
- Validate any override against `^[a-z0-9][a-z0-9-]*$`. Re-ask on invalid.

### Q3 — Tradeoffs to preserve

> Any non-obvious tradeoffs to preserve? Things future-you would forget if it weren't written down.

- `n` / empty / `none` → write `None known.` to `notes.md > Tradeoffs preserved`.
- Otherwise → use the user's text verbatim.

### Q4 — Tags for search

> Tags for search? Comma-separated. Suggested from autonomous read: `<tag1>, <tag2>, <tag3>`.

- Suggested defaults come from `language`, `framework`, `interface_kind`, plus any obvious nouns from the autonomous summary.
- `y` / empty → accept suggested tags as-is.
- Comma-separated input → use those tags.

Set `notes_completeness.interview_fired = true` and `notes_completeness.substantive_count = <count of substantive Gotcha bullets after interview>`.

## Phase 7 — bundle generation

Build all six artifacts in memory (or a local-temp staging dir under `~/.vibe-taker/library/.staging/<name>-<target_version>-<unix-timestamp>/`).

### 7.1 Cleanup stale staging

At the start of every capture, **before staging anything new**: remove any `~/.vibe-taker/library/.staging/<*>` whose mtime is older than 1 hour. These are stranded crash residues from prior runs.

### 7.2 Templates

Render the three template files from [`skills/vibe-taker-guide/templates/`](/.agent/skills/vibe-taker-guide/templates/). Substitute `{{name}}`, `{{version}}`, `{{summary}}`, `{{captured_at}}`, `{{source_repo}}`, `{{source_path}}`, etc. Slot fills:

- **`README.md.template`** → `<staging>/README.md`. `{{what_it_is}}` from `architecture.md > Summary`. `{{when_to_reach}}` from interview Q1 if fired, else from `notes.md > Why this exists`.
- **`architecture.md.template`** → `<staging>/architecture.md`. `{{summary_paragraph}}` from Phase 2.6. `{{components_block}}` from entry points + helpers (single-file features get `Single-file feature — no internal components.`). `{{data_flow_block}}` from I/O extraction (inputs → entry-point → outputs as ASCII or one-paragraph prose). `{{key_files_block}}` enumerates entry points + manifest path.
- **`notes.md.template`** → `<staging>/notes.md`. `{{why_block}}` from Q1 / autonomous intent. `{{gotchas_block}}` from Phase 2.7 + Phase 3 load-bearing warnings. `{{tradeoffs_block}}` from Q3.

**Empty sections are explicit** — `None known.` rather than absent. The template carries the heading; the renderer fills the body or writes the sentinel.

### 7.3 `contract.json`

Build directly from analysis (no template). Required fields are populated from Phases 2-3. Optional fields (`tags`, `summary`, `notes_completeness`) come from interview output / Phase 2.6.

```jsonc
{
  "schema_version": "1.0",
  "name": "<slug>",
  "version": "<target_version>",
  "language": "<from Phase 2.1>",
  "framework": "<from Phase 2.2 or null>",
  "interface_kind": "<cli|library|...>",
  "inputs": [ ... ],
  "outputs": [ ... ],
  "dependencies": [ ... ],
  "env_vars": [ ... ],
  "source_repo": "<git remote of cwd, or absolute cwd if no remote>",
  "source_path": "<repo-relative path of the capture target>",
  "captured_at": "<ISO 8601 UTC, second precision>",
  "entry_points": [ "<paths relative to reference/>" ],
  "tags": [ ... ],
  "summary": "<one-line>",
  "notes_completeness": { "substantive_count": <int>, "interview_fired": <bool> }
}
```

Pretty-printed with 2-space indent. Validate against `.agent/skills/vibe-taker-guide/schemas/contract.schema.json` **before** writing. If validation fails, exit class-2:

```
[exit 2] contract.json failed schema validation: <error>. This is a vibe-taker bug — file friction at /reflect.
```

### 7.4 Prompts

Write each extracted prompt (Phase 2.5) to `<staging>/prompts/<descriptive-name>.txt` verbatim. If no prompts were extracted, create `<staging>/prompts/empty.txt` with the single line `(no prompts extracted from this feature)`.

### 7.5 Reference snapshot

Copy every non-skipped file from the captured tree into `<staging>/reference/`, preserving the relative tree under `reference_root`:

- **Folder capture** → `<staging>/reference/<basename>/...`
- **Single-file capture** → `<staging>/reference/<filename>`
- **Glob capture** → `<staging>/reference/<rel-tree-from-glob-root>`

Skipped (secret-like) files do **not** land here. Phase 3 already removed them from the working set.

## Phase 8 — atomic write (KTD-3)

All bundle writes go through stage-and-`mv`:

1. **Final destination resolution:**
   - `version_bump = false`, `target_version = v1` → `~/.vibe-taker/library/<name>/v1/`.
   - `version_bump = true`, `target_version = v(n+1)`:
     - If `migrate_legacy = true` (the existing bundle was at bare `<name>/`): move `~/.vibe-taker/library/<name>/` to `~/.vibe-taker/library/<name>/v1/` first (atomic `mv`), update the matching `index.json` entry's `versions[0].version = "v1"`, then proceed.
     - Place the new bundle at `~/.vibe-taker/library/<name>/v(n+1)/`.
2. **Stage the full bundle directory** at `~/.vibe-taker/library/.staging/<name>-<target_version>-<unix-timestamp>/`.
3. **Verify all six artifact paths exist** in the staging dir before moving:
   - `README.md`, `architecture.md`, `contract.json`, `prompts/` (with at least `empty.txt` or real prompts), `reference/` (non-empty), `notes.md`.
4. **Move staging → final** with one `mv`. If the move fails (e.g., permission denied), exit class-2 with the path and error.
5. **Index update:**
   - Read existing `~/.vibe-taker/library/index.json` (or seed with `{schema_version: "1.0", bundles: []}` if absent).
   - For new bundles: append a new entry. For version bumps: append to the matching entry's `versions[]` and update `latest_version`.
   - Validate the resulting index against `.agent/skills/vibe-taker-guide/schemas/index.schema.json`. Bail (class-2) on validation failure.
   - Write to `~/.vibe-taker/library/index.json.tmp`. `mv index.json.tmp index.json`.

Result: a half-written bundle never lands on the shelf. A crash mid-capture leaves a stranded `.staging/<*>` directory that the next `/vibe-taker-capture` removes (Phase 7.1).

## Phase 9 — first-run privacy notice

If `~/.vibe-taker/README.md` does **not** exist (i.e., this is the first-ever vibe-taker capture on this machine):

1. **Write** the privacy notice to `~/.vibe-taker/README.md`:

   ```markdown
   # ~/.vibe-taker/

   Local vibe-taker shelf. **Local only by default.**

   vibe-taker writes to your local home directory only (`~/.vibe-taker/`). No network calls, no sync.
   Cross-machine sharing is a v2 concern — when it ships, the migration path is moving this whole
   directory wholesale.

   - Bundles live in `library/<feature-name>/<version>/`.
   - The shelf manifest is `library/index.json`.
   - `library/.staging/` is the temp staging area for atomic writes — never user-facing; safe to ignore or delete.

   See the plugin docs at https://github.com/estevanhernandez-stack-ed/vibe-taker for capture/plant
   commands and the bundle schema.
   ```

2. **Print the same notice to stdout** before the success summary, so the user sees it once.

This satisfies PRD Library-management story 4.

## Phase 10 — success summary

Class-0 outcome. Print:

```
✓ Bundle written: ~/.vibe-taker/library/<name>/<target_version>/

  6 artifacts populated. Index updated.
  language: <lang>  ·  framework: <framework or none>  ·  interface: <kind>
  entry-points: <count>   inputs: <count>   outputs: <count>   env_vars: <count>   prompts: <count>

  source: <source_repo> (<source_path>)

  next: `/vibe-taker-list` to see the shelf, or `/vibe-taker-plant <name>` from a target repo.
```

When the interview gate did **not** fire, prepend the autonomous-derived line:

```
intent derived autonomously — bundle ready at <path>; edit notes.md if anything's missing.
```

When secret-like files were skipped and **load-bearing** was inferred, append:

```
⚠ Skipped <N> secret-like files that look load-bearing.
   Capture continues with these stubbed in contract.json under env_vars.
   Provide them at plant-time. Skipped: <comma-separated names>.
```

Exit class-0.

## Failure modes recap

All exits include a one-line recovery action per [`error-contract.md`](/.agent/skills/vibe-taker-guide/references/error-contract.md):

- Target not found / glob no-match / in-file selector / name-conflict declined → class-1 with the exact recovery line.
- Schema-invalid contract / write-failure / index-corruption mid-flight → class-2 with the path and recovery.
- Successful capture (with or without interview) → class-0 with the summary above.
