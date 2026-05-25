---
description: "Plant a captured feature from the shelf into the current repo. Adapts to the destination stack."
---

# /vibe-taker-plant

> Plant a captured bundle from the shelf into the current repo. (Implements the source plugin's Plant Flow Architecture / Epic: Plant.)

The mostly-mechanical half — once the bundle schema is locked, plant reads, detects, decides, stages, confirms, writes. The mandatory checkpoint is the diff `[y/N]`. **No file is written without explicit user confirmation.**

## Loading order — do this every time the workflow fires

Persona, voice, the plant posture (mandatory diff confirmation before any write,
the code-lift / spec-driven / decline modes, local-library-is-truth), the hygiene
rules, atomic-write discipline, the error-class contract, and Pattern #13
composition are **always-on via [`AGENTS.md`](/AGENTS.md)** — already in context.
Then load the situational reference detail plant needs:

1. **Read** [`.agent/skills/vibe-taker-guide/references/bundle-schema.md`](/.agent/skills/vibe-taker-guide/references/bundle-schema.md) — what the bundle's contract.json carries.
2. **Read** [`.agent/skills/vibe-taker-guide/references/stack-match.md`](/.agent/skills/vibe-taker-guide/references/stack-match.md) — the decision tree, framework families, decline message.
3. **Read** [`.agent/skills/vibe-taker-guide/references/error-contract.md`](/.agent/skills/vibe-taker-guide/references/error-contract.md) — class-0/1/2 outcome shapes.

Then execute the phases below in order. Validate `index.json` / `contract.json`
against the schemas in `.agent/skills/vibe-taker-guide/schemas/` before acting on them.

## Argument parsing

Form: `/vibe-taker-plant <name> [--version=vX]`.

- `<name>` — required. The bundle slug.
- `--version=vX` — optional. If absent, plant uses `index.json.bundles[i].latest_version`.

Reject any other flags in v1 (no `--yes`, no `--shelf-path` per KTD-6/KTD-7). Print:

```
[exit 1] Unknown flag `<flag>`. v1 supports: `<name>` [--version=vX]
```

## Phase 1 — bundle load

1. **Read** `~/.vibe-taker/library/index.json`. If absent or unparseable JSON, exit class-2:

   ```
   [exit 2] Library index missing or corrupt at ~/.vibe-taker/library/index.json. Re-capture a feature to rebuild, or restore from backup.
   ```

2. **Validate** the index against `.agent/skills/vibe-taker-guide/schemas/index.schema.json`. Same class-2 path on validation failure with the schema error appended.

3. **Find** the entry whose `name == <input-name>` (exact, case-sensitive). On absent:

   ```
   [exit 1] No bundle named '<name>' on the shelf. Run `/vibe-taker-list` to see what's available.
   ```

4. **Resolve version:**
   - If `--version=vX` was passed, look up the matching entry in `versions[]`. On absent:

     ```
     [exit 1] Bundle `<name>` exists but version `<vX>` not found. Available: <comma-separated versions>.
     ```

   - If `--version` was absent, use `latest_version`.

5. **Read** `~/.vibe-taker/library/<name>/<version>/contract.json`. Parse JSON.
6. **Validate** the contract against `.agent/skills/vibe-taker-guide/schemas/contract.schema.json`. On validation failure, exit class-2:

   ```
   [exit 2] Bundle `<bundle-path>/contract.json` failed schema validation: <error>. Hand-edit the file or re-capture the source.
   ```

7. Carry `contract.language`, `contract.framework`, `contract.interface_kind`, `contract.entry_points`, `contract.env_vars` into the working state for downstream phases.

## Phase 2 — target stack detect

Walk the **current working directory** (and one level up if cwd has nothing) for manifests, in priority order:

| Manifest | Implies | Framework derivation |
|---|---|---|
| `package.json` (with `"type": "module"` OR `.ts` files anywhere in cwd tree) | Node — TypeScript or JavaScript | Read `dependencies` for highest-signal dep: `express`/`fastify`/`hapi`/`koa` (web/server), `react`/`vue`/`svelte` (web/client), `next`/`nuxt` (web/fullstack), `yargs`/`commander`/`oclif` (CLI). |
| `pyproject.toml` / `requirements.txt` / `setup.py` | Python | Read deps for `fastapi`/`flask`/`django` (web), `pandas`/`jupyter` (data), `click`/`typer`/explicit `argparse` usage in entry points (CLI). |
| `Cargo.toml` | Rust | `[dependencies]` lookup for `actix-web`/`rocket` (web), `clap` (CLI). |
| `go.mod` | Go | `require` block: `gin`/`echo` (web), `cobra`/`urfave/cli` (CLI). |
| `*.csproj` / `*.sln` | C# | XML `<PackageReference>` lookup. |
| `Gemfile` | Ruby | Gemfile parse for `rails`/`sinatra`. |
| `composer.json` | PHP | `require` lookup. |

If multiple manifests co-exist (monorepo), pick the one closest to cwd (cwd wins over parent). Carry `target.language`, `target.framework`, `target.framework_family`.

If **no manifest detected** in cwd or one level up: set `target.language = null`, `target.framework = null`. The decision tree handles this as the no-manifest fallback.

## Phase 3 — decision tree

Apply the table from [`stack-match.md`](/.agent/skills/vibe-taker-guide/references/stack-match.md):

```
match_level = compute_match(contract.language, contract.framework, target.language, target.framework, target.framework_family)
```

Where:

- **High** — `contract.language == target.language` AND same framework family. Mode: `code-lift`. (v1 ships zero adapters; same-language same-family code-lift keeps the source's framework choice.)
- **Low** — `contract.language == target.language`, different framework family. Mode: `spec-driven`.
- **Hard** — `contract.language != target.language` (and target.language is not null). Mode: `decline`.
- **Fallback** — `target.language is null` (no manifest). Mode: `spec-driven` with notice.

The chosen `mode` and `match_level` are named in the diff header (Phase 7).

## Phase 4 — hard-mismatch decline path

Triggered when `match_level == "hard"`. **No file is written.**

Print verbatim, substituting `<source-lang>` (= `contract.language`), `<target-lang>` (= `target.language`), `<bundle-path>` (= `~/.vibe-taker/library/<name>/<version>/`):

```
vibe-taker bundles capture <source-lang>; your target repo is <target-lang>. v1 doesn't auto-port across languages — too lossy. Here's the architecture sketch (<bundle-path>/architecture.md) and reference code (<bundle-path>/reference/); port manually, or capture a <target-lang>-native version of this feature into a new bundle.
```

Exit class-1.

## Phase 5 — no-manifest fallback notice

Triggered when `match_level == "fallback"`. Print before continuing into spec-driven mode (Phase 6 in item 8):

```
No manifest detected in target — falling back to spec-driven re-implementation. Reference code in <bundle-path>/reference/ for guidance.
```

Then proceed to Phase 6 (item 8) with `mode = spec-driven`, `match_level = fallback`.

## Decision header — render at the top of the diff

When Phases 1-3 leave us in `code-lift` (high) or `spec-driven` (low or fallback), the diff (rendered in Phase 7, item 8) is preceded by:

```
Mode: <code-lift | spec-driven>
Stack match: <high | low | hard-decline | fallback>
Bundle: <name> <version>  ·  source: <contract.language>/<contract.framework or none>
Target: <target.language or "no manifest">/<target.framework or "—">
```

This is what the user reads before answering the `[y/N]` prompt.

## Phase 6 — code-lift mode

Triggered when `mode == "code-lift"` (high match).

### 6.1 Target-conventional placement

Determine where files land in the target. Follow the target's existing convention:

- **Python with `pyproject.toml` + a `src/<package>/` layout** → place files under `src/<package>/<feature>/`. Read `<package>` from `[project].name` (PEP 621) or `[tool.poetry].name` (Poetry).
- **Python with `pyproject.toml` + flat layout** (no `src/`) → place files under `<package>/<feature>/`.
- **Python with only `requirements.txt`** (no `pyproject.toml`) → place files at root with `<feature>/` subdir.
- **Node with `src/`** → `src/<feature>/`.
- **Node without `src/`** → `<feature>/` at root.
- **Rust** → `src/<feature>/` (always `src/` in Cargo crates).
- **Go** → `<feature>/` package at root or under `internal/<feature>/` if `internal/` exists.
- **C#** → `<Feature>/` (PascalCase) folder under the `.csproj` directory.
- **Default fallback** → `<feature>/` at root.

`<feature>` is the bundle's slug (`contract.name`). For single-file bundles where the entire feature is one file, place that file at `<feature>.<ext>` rather than under a folder.

### 6.2 Import rewriting

Walk every `.py` / `.ts` / `.tsx` / `.js` / `.jsx` / `.rs` / `.go` file being placed.

**Python:**

- `from .` and `from <source-package>.<...>` → rewrite to target package.
  - Source package is whatever was the source's top-level package name (read from the bundle's `reference/<src-tree>/pyproject.toml` if captured; else infer from `entry_points`).
  - Target package is from `[project].name` / `[tool.poetry].name` of the target's `pyproject.toml`.
- Relative imports stay relative; absolute-from-package imports get the package name swapped.

**Node:**

- `import './<rel>'` and `import '../<rel>'` — keep relative (path is preserved by the tree placement).
- `import 'src/<...>'` or `import '@<alias>/<...>'` — adjust to target's `tsconfig.json#paths` if present, else rewrite to a target-relative form.
- `require('<source-pkg>/<...>')` for the source's own package name → target package name.

**Rust:**

- `crate::` references stay (crate-relative). `use <source-crate>::<...>` rewrites to target crate.

**Go:**

- Module imports `<source-mod>/<...>` rewrite to `<target-mod>/<...>` from `go.mod`'s `module` line.

**Adapter coverage:** v1 ships **zero** in-language framework adapters (no Click→Typer, no Express→Fastify, etc.). When a framework call site doesn't translate cleanly inside the same family, fall back to **spec-driven mode for that file specifically** — render the file as a fresh re-implementation rather than a literal copy. Per-file fallback keeps the rest of the code-lift intact.

### 6.3 Stage the diff

Build a unified diff against the target's current state:

- Each file to be created → `+++` block with full content.
- Each file to be modified (rare in v1; primarily import-rewrite of an already-named target file) → diff against current.

Stage in memory or in a session-only `.vibe-taker-staging/` directory under cwd. **Do not commit** the staging directory; `.gitignore` covers it.

Continue to Phase 8 (diff render + confirm).

## Phase 7 — spec-driven mode

Triggered when `mode == "spec-driven"` (low match or fallback).

1. **Read** `<bundle>/architecture.md` — components, data flow, key files.
2. **Read** `<bundle>/contract.json` — exact I/O surface to match in the target.
3. **Read** `<bundle>/notes.md` — why and gotchas; preserve tradeoffs in the target.
4. **Read** `<bundle>/reference/` files — for shape and intent, **as a guide, not a copy source**. Don't lift literal code; re-derive in the target's framework conventions.
5. **Generate** fresh code in the target's stack. Preserve:
   - Same input names + types from `contract.inputs`.
   - Same output names + types from `contract.outputs`.
   - Same env-var names from `contract.env_vars` (rename target-side conventions if any apply).
   - Same external-service touchpoints (LLM SDK calls, file I/O, CLI flags).
6. **Place** generated files using the same target-conventional placement rules as Phase 6.1.
7. **Stage** the diff (Phase 6.3 mechanics — fresh files, no rewrites needed).

Continue to Phase 8.

## Phase 8 — diff render + mandatory `[y/N]` checkpoint

The single mandatory user-confirmation point. PRD Plant story 1: *"No file is written without explicit user confirmation."* No `--yes` flag in v1 (KTD-7).

### 8.1 Render

Print the unified diff to stdout. Format:

```
Mode: <code-lift | spec-driven>
Stack match: <high | low | fallback>
Bundle: <name> <version>  ·  source: <contract.language>/<contract.framework or none>
Target: <target.language>/<target.framework or "—"> at <cwd>

--- Files to be written ---
(<N> files; <total-bytes> bytes)

<unified diff per file, in dependency-friendly order: contracts/types first, entry points last>

--- Env vars from bundle (provide before running) ---
<list of contract.env_vars with load_bearing flag>

--- Notes carried from bundle ---
<bundle's notes.md > Gotchas section, verbatim>
```

Make it scannable. Long diffs are fine; the user is making a binary decision but should have the full picture.

### 8.2 Prompt

Print on its own line:

```
Apply this diff? [y/N]
```

### 8.3 Decline path

On `n`, empty input, or any non-`y` answer:

- **No file is written.**
- Print:

  ```
  No files written.
  ```

- Clean up `.vibe-taker-staging/` if it was used.
- Exit class-0 (the user declined cleanly; this is success, not failure).

### 8.4 Apply path

On `y`:

1. **Per-file atomic write.** For each file in the diff:
   - Write to `<target-path>.tmp`.
   - On all writes succeeding, `mv <target-path>.tmp <target-path>`.
   - If any write fails mid-flight, roll back any `.tmp` files already written (delete them) and exit class-2 with the failed path.
2. **Clean up** any `.vibe-taker-staging/` directory under cwd.
3. **Print** the success summary (Phase 10).

### 8.5 Atomic-per-file rationale

Per-file `.tmp` + `mv` makes each individual write atomic on POSIX (and on Windows with NTFS for same-volume moves). The whole-plant operation is **not** atomic — it's a sequence of per-file atomic moves. If something dies between file 3 and file 4, files 1-3 are landed and 4-N aren't. This is acceptable in v1: the `[y/N]` confirmation already gives the user the full picture; mid-flight crashes are vanishingly rare for filesystem ops; and a partial plant is still partial *valid* code (each file individually is consistent).

## Phase 9 — dashboard decision log (opt-in / fail-silent)

PRD Plant story 5. Pattern #13 (ecosystem-aware composition).

After a successful apply (Phase 8.4):

1. **Check** whether a decision-log MCP is in the agent's runtime tool list — auto-detects the recognized 626Labs dashboard (`mcp__626labs-cloud__manage_decisions`). It's optional; never required.
2. **If absent** — succeed silently. No retry, no error, no warning. The plant is already a success.
3. **If present** — call:

   ```
   action: log
   body:
     title: "Planted <name> <version> into <cwd-basename>"
     description: |
       Source: <contract.source_repo> (<contract.source_path>)
       Target: <cwd>
       Mode: <code-lift | spec-driven>
       Stack match: <high | low | fallback>
     tags: ["vibe-taker", "plant", "<contract.language>"]
     projectId: <bound-project-id-if-current-repo-bound-else-null>
   ```

   - To get `bound-project-id`: read `git config --get remote.origin.url` from cwd; if a remote exists and the detected MCP exposes it, optionally call `mcp__626labs-cloud__manage_projects` with action `findByRepo` to get the project ID. If no remote, no match, or no such tool, set `projectId: null` and tag the decision with the cwd basename.
   - **Don't fail the plant on dashboard errors.** If the call returns an error, print one line: `(dashboard log failed; plant succeeded)` and exit class-0 anyway.

## Phase 10 — success summary

Class-0 outcome after a `y` on the diff.

```
✓ Planted <name> <version> into <cwd>

  <N> files written.
  Mode: <code-lift | spec-driven>  ·  Stack match: <high | low | fallback>

  Env vars to set before running:
    <list of load-bearing env vars from contract>

  Source: <contract.source_repo> (<contract.source_path>)

  <(dashboard log succeeded | plant logged to 626Labs Dashboard | dashboard not connected)>
```

Exit class-0.

## Failure modes recap

All exits include a one-line recovery action per [`error-contract.md`](/.agent/skills/vibe-taker-guide/references/error-contract.md):

- Bundle not on shelf / version not found / hard mismatch / user declined → class-1 / class-0 with the recovery line.
- Schema-invalid contract / write failure mid-flight / index-corrupt → class-2 with the path.
- Successful plant (code-lift or spec-driven) with user `y` → class-0 with the summary above.
- Successful decline (user `n`) → class-0; "no files written."

The diff is the load-bearing checkpoint. Until the user types `y`, **no file in cwd is touched.**
