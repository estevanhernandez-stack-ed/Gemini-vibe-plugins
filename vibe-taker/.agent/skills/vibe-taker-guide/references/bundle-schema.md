# Bundle schema — single source of truth

A vibe-taker bundle is six artifact paths inside `~/.vibe-taker/library/<feature-name>/<version>/`. The shape is locked at `schema_version: "1.0"` (KTD-2 in [`spec.md`](../../../docs/spec.md#ktd-2--bundle-schema-is-the-contract-surface-locked-in-v1)). Every downstream feature — versioning, sync, marketplace publishing if it ever happens — depends on this being stable.

This reference is the readable companion to the two JSON Schemas:

- [`schemas/contract.schema.json`](../schemas/contract.schema.json) — per-bundle contract.
- [`schemas/index.schema.json`](../schemas/index.schema.json) — shelf manifest at `~/.vibe-taker/library/index.json`.

## Bundle directory layout

```
~/.vibe-taker/library/<feature-name>/<version>/
├── README.md          # human-readable: what, when to reach, intent
├── architecture.md    # components, data flow, key files
├── contract.json      # I/O surface, deps, env, language/framework
├── prompts/           # AI prompts if any; empty dir → empty.txt sentinel
│   └── <name>.txt
├── reference/         # verbatim snapshot of source — read-only truth
│   └── <preserved tree>
└── notes.md           # WHY, gotchas, tradeoffs
```

- `<feature-name>` is a slug `^[a-z0-9][a-z0-9-]*$` — autonomous proposes; user confirms during interview.
- `<version>` is `v1`, `v2`, … — bumped on re-capture (see [Versioning](#versioning)).
- All six artifact paths exist on every bundle. Empty directories use a `.gitkeep`-style sentinel (`empty.txt` with a one-line note) so the absence is unambiguous.

## `contract.json` — required + optional fields

### Required

| Field | Type | Notes |
|---|---|---|
| `schema_version` | string | `"1.0"` for v1. |
| `name` | string | Slug; matches bundle directory name. |
| `version` | string | `"v1"`, `"v2"`, … |
| `language` | string | `python` / `typescript` / `javascript` / `rust` / `go` / `csharp` / `ruby` / `bash` / `other:<name>`. |
| `framework` | string \| null | `fastapi`, `flask`, `express`, `nextjs`, `react`, `cli-argparse`, `cli-typer`, `cli-click`, `cli-yargs`, `cli-commander`, `none`, etc. `null` when undetectable. |
| `interface_kind` | string | `cli` / `library` / `skill` / `script` / `service` / `bot` / `other`. |
| `inputs` | array | See input shape below. |
| `outputs` | array | See output shape below. |
| `dependencies` | array of strings | Package names with version specifiers when discoverable, e.g. `"requests>=2.28"`. From manifest. |
| `env_vars` | array | See env-var shape below. |
| `source_repo` | string | URL or local path of source repo at capture time. |
| `source_path` | string | Relative path within `source_repo`. |
| `captured_at` | string (ISO 8601) | Capture timestamp. |
| `entry_points` | array of strings | File paths within `reference/` that are program entry points. |

### Optional

| Field | Type | Notes |
|---|---|---|
| `tags` | array of strings | User-supplied search tags. Mirrored in `index.json`. |
| `summary` | string | One-line summary. Mirrored in `index.json`. |
| `notes_completeness` | object | `{ "substantive_count": int, "interview_fired": bool }` — diagnostics for the interview-gate heuristic. |

### Input shape

```json
{ "name": "image_path", "type": "path", "required": true, "description": "Path to source image" }
```

`type` is one of: `path` / `string` / `int` / `float` / `bool` / `enum:<v1>|<v2>|...` / `stdin` / `flag` / `other`.

### Output shape

```json
{ "name": "transparent_image", "type": "path", "description": "Output path for transparent-bg image" }
```

### Env-var shape

```json
{ "name": "OPENAI_API_KEY", "load_bearing": true, "description": "API key for the bg-removal model" }
```

`load_bearing: true` means the feature won't function without this env var. Plant-time prompts the user to provide if missing in target.

## `index.json` — shelf manifest

Pretty-printed JSON, 2-space indent, max ~200 bytes per entry.

```json
{
  "schema_version": "1.0",
  "bundles": [
    {
      "name": "bg-remover",
      "latest_version": "v2",
      "versions": [
        { "version": "v1", "captured_at": "2026-04-30T14:22:01Z", "source_repo": "https://github.com/626labs/hub", "source_path": "tools/bg-remove/" },
        { "version": "v2", "captured_at": "2026-05-07T09:11:43Z", "source_repo": "https://github.com/626labs/hub", "source_path": "tools/bg-remove/" }
      ],
      "tags": ["cli", "image", "ai"],
      "summary": "AI-powered CLI background remover. Takes an image path, returns transparent-bg version.",
      "language": "python",
      "framework": "cli-argparse"
    }
  ]
}
```

- `bundles` is an **array, not a map** — preserves user-visible ordering and survives hand-edits cleanly.
- `latest_version` is what `/vibe-taker-plant <name>` (without `--version`) selects.
- `versions[]` is append-only in normal flow; only `/vibe-taker-capture` writes to it, only with `mv`-atomic semantics.

## `architecture.md` — required structure

Every bundle's `architecture.md` opens with:

1. **Summary** (1-3 sentences) — what the feature is and what it does.
2. **Components** (heading) — name each entry point, helper, and external dependency.
3. **Data flow** (heading) — how data moves through the feature. ASCII or prose.

Empty sections are explicit (`None known.` / `Single-file feature — no internal components.`), never absent.

## `notes.md` — required structure

1. **Why this exists** — autonomous-derived from source `README.md`-like prose, or interview-supplied. Never empty.
2. **Gotchas** — non-obvious tradeoffs, library quirks, known issues. `None known.` is acceptable.
3. **Tradeoffs preserved** — optional; populated by interview question 3 when fired.

`notes_completeness.substantive_count` in `contract.json` reflects how many gotcha-bullets cleared the heuristic threshold.

## `README.md` — bundle entry point

Renders cleanly on GitHub if the bundle is ever published. Sections:

1. **What it is** (one paragraph).
2. **When to reach for it** (one paragraph).
3. **Plant** — the literal command (`/vibe-taker-plant <name>`).
4. **Reference** — link to `reference/` for the source-of-truth files.

## `prompts/` — AI prompt extraction

When the captured feature calls an LLM, every system prompt and user-template prompt gets extracted into `prompts/<descriptive-name>.txt` verbatim. Detection heuristic: any string literal **>100 chars** passed to a known LLM SDK call (OpenAI, Anthropic, Cohere, Bedrock client, Ollama HTTP request, etc.). False negatives are acceptable in v1 — the interview gate fires if `prompts/` is empty *and* dependencies include an LLM SDK.

If the feature has no AI prompts, `prompts/` exists but contains a single `empty.txt` with one line: `(no prompts extracted from this feature)`.

## Versioning

> Resolves OQ-1. KTD-5: prompt user, no `--auto-bump` flag in v1.

- On `/vibe-taker-capture`, after autonomous read produces a proposed slug, check `index.json` for an existing entry with that name.
- If found, the agent prints: *"<name> already on the shelf at <path>. Bump to <next-version>? [y/N]"*
- On `y`, the new bundle goes to `<name>/v<n+1>/`. If the existing bundle was at `<name>/` with no version subdirectory (legacy / first-write), the agent first moves it to `<name>/v1/` and updates `index.json` accordingly, then writes the new bundle to `<name>/v2/`.
- On `n` or empty input, the command exits with no changes and prints the path of the existing bundle.

## Validation

Every `contract.json` must validate against `contract.schema.json` before any plant. A schema-invalid bundle exits class-2 (internal failure) on `/vibe-taker-plant` with the path and the schema error.

```bash
python -c "import jsonschema, json; jsonschema.Draft202012Validator(json.load(open('contract.schema.json'))).validate(json.load(open('contract.json')))"
```

Hand-editing a bundle is supported and expected — the schema is the contract, not the agent's output. If the agent gets a field wrong, edit the file directly; the schema validates on plant, not on capture.

## Cross-references

- Spec: [`spec.md > Bundle Schema`](../../../docs/spec.md#bundle-schema), [`spec.md > Library Shelf`](../../../docs/spec.md#library-shelf----vibe-takerlibrary).
- PRD: [`prd.md > Epic: Bundle schema`](../../../docs/prd.md#epic-bundle-schema).
- Capture flow that produces the bundle: [`spec.md > Capture Flow Architecture`](../../../docs/spec.md#capture-flow-architecture).
- Plant flow that consumes the bundle: [`spec.md > Plant Flow Architecture`](../../../docs/spec.md#plant-flow-architecture).
