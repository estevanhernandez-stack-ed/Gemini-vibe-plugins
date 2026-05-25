---
description: "Run when the user says /vibe-iterate-bootstrap, 'set up vibe-iterate', or 'init vibe-iterate' — also invoked by the /vibe-iterate bare router on first run. Identifies the app type, confirms with the user, infers framework pins from package.json, asks for competitor URLs, and writes .vibe-iterate/config.json. Idempotent — re-runnable to refresh stale config."
---

# /vibe-iterate-bootstrap — set up the lay of the land

Persona/posture/Cart-detection are always-on via `AGENTS.md`. Schema validation detail is in the `vibe-iterate-guide` skill (`.agent/skills/vibe-iterate-guide/SKILL.md`). Then follow this workflow.

## What this workflow does

The repo doesn't have a `.vibe-iterate/` directory yet (or its `config.json` is stale), so the agent doesn't know what app this is, who you compete with, or which framework pins to track. The agent's job is to:

1. **Auto-classify the app type** by reading the codebase (`package.json`, `README.md`, top-level dirs, presence of `.agent/` or `.claude-plugin/`, etc.) — don't ask if you can infer.
2. **Confirm classification** with the user in ONE short question. Surface the inference; let them correct.
3. **Auto-extract framework pins** from `package.json` (or pyproject.toml / Cargo.toml / etc.).
4. **Ask the user for competitor URLs** — the only thing Ptolemy can't reliably infer. One short question, category-aware.
5. **Write `.vibe-iterate/config.json`** validated against the `config` schema in the vibe-iterate-guide skill.
6. **Hand back** with a one-line acknowledgment. No lecture.

## Hard rules

- **Do work first, ask second.** Never ask the user something you could infer from the codebase. Two questions max — classification confirmation, competitors.
- **Never auto-fire a mode after bootstrap.** Bootstrap writes config; the user kicks off the next step.
- **Validate before writing.** Read `.agent/skills/vibe-iterate-guide/schemas/config.schema.json`; ensure the config matches before writing.
- **No telemetry.** Bootstrap writes one local file and stops.
- **Idempotent.** If `.vibe-iterate/config.json` already exists, ask if this is a refresh (default: yes if `last_inferred_at` >30 days; default: no otherwise). Don't silently overwrite.

## Session + friction logging

At workflow start — load the `vibe-iterate-session-logger` skill (`.agent/skills/vibe-iterate-session-logger/SKILL.md`) and run `start("bootstrap", <project_dir>)` to get a sessionUUID. Hold it for the run; pass it to every `vibe-iterate-friction-logger.log()` call.

At workflow end — run `vibe-iterate-session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome: null, atlas_title: null, pr_url: null })`. Bootstrap doesn't write Atlas, so `atlas_outcome` and `atlas_title` are `null`.

Honor the friction trigger map at `.agent/skills/vibe-iterate-guide/references/friction-triggers.md` — section `/vibe-iterate-bootstrap`. Universal triggers (`repeat_question`, `rephrase_requested`) also apply; without a quoted prior turn in `symptom`, do not log.

## Posture announcement

> *Bootstrap mode → conservative. I'll do as much as I can from the codebase, then check two things with you. Two minutes max.*

## Procedure

### Step 1 — auto-classify the app type

Read these files (in order; stop once classification is unambiguous):

1. **`.agent/` directory or `.claude-plugin/plugin.json`** present → **agent plugin / Claude Code plugin**. Done.
2. **`package.json`** — read `dependencies` + `devDependencies` + `scripts`:
   - Has `next` / `react` / `vue` / `svelte` / `nuxt` / `astro` / `remix` → **web app**
   - Has `react-native` / `expo` → **mobile app**
   - Has `electron` → **desktop app**
   - Has `commander` / `yargs` / `oclif` / `clap` AND no UI framework → **CLI tool**
   - `"main"` set, `"bin"` absent, no UI framework → **library / SDK**
3. **`pyproject.toml`** or `setup.py`:
   - Has `flask` / `django` / `fastapi` / `streamlit` → **web app** (Python)
   - Has `click` / `typer` / `argparse`-only → **CLI tool**
   - Otherwise → **library / SDK**
4. **`Cargo.toml`** — `[[bin]]` present → **CLI tool**; only `[lib]` → **library / SDK**
5. **`go.mod`** — `main` package in `cmd/` or root → **CLI tool / service**; only sub-packages → **library**
6. **Multiple workspaces** (pnpm-workspace.yaml, lerna.json, Cargo workspace, multi-`package.json` under `packages/`/`apps/`) → **monorepo** (primary; sub-classify the most active workspace as the iteration target)
7. **None match cleanly** — read `README.md` first 50 lines and infer; if still ambiguous, classify as **other** and surface the uncertainty in step 2.

Canonical category strings (match exactly when writing config): `web-app`, `mobile-app`, `desktop-app`, `cli-tool`, `library-sdk`, `agent-plugin`, `monorepo` (with sub-type suffix, e.g. `monorepo:web-app`), `data-research`, `other`.

For each, note the **framework anchor** (e.g. `Next.js 16`, `React Native + Expo`, `Click`, `Cargo lib`) — used to make the inference concrete.

### Step 2 — confirm with the user (ONE question)

```
Looks like a [framework anchor] — I'd classify this as a [category].

Right? (yes / pick another / let me describe it)
```

If "another" — show the canonical list, let them pick. If "let me describe it" — take a one-line free-text description, map it to the closest canonical category.

### Step 3 — auto-extract framework pins

From the inferred stack's manifest:
- **`package.json`** — read `dependencies` + `devDependencies`. Extract pins for any framework named in step 1 + the top 5 most-impactful runtime deps (skip dev-only utilities like `eslint`, `prettier`, `typescript`, `@types/*` unless load-bearing). Cap at 8.
- **`pyproject.toml`** — `[project.dependencies]` (PEP 621) or `[tool.poetry.dependencies]`. Same cap.
- **`Cargo.toml`** — `[dependencies]`. Same cap.
- **`go.mod`** — top-level `require` block. Same cap.

Capture each as `{ "name": "<package>", "version": "<version-string>" }`. Keep range strings verbatim (`^16.0.0`). If no manifest exists, `framework_pins` is `[]`.

### Step 4 — ask for competitor URLs (ONE question)

Surface category-aware suggestions:
- **web-app (productivity)** → "e.g. notion.so/blog/category/product, obsidian.md/changelog, github.com/logseq/logseq/releases"
- **web-app (SaaS/B2B)** → "e.g. stripe.com/changelog, vercel.com/changelog, github.com/<competitor>/releases"
- **agent-plugin** → "e.g. other plugins in your category — github.com/<owner>/<plugin>/releases"
- **cli-tool** → "e.g. gh.io changelog, github.com/<competitor>/releases"
- **mobile-app** → "e.g. App Store / Play Store changelogs, competitor blogs"
- **library-sdk** → "e.g. comparable libraries' changelogs or release pages"

```
Who do you compete with? Drop 2-5 URLs (one per line) — changelogs, release pages, or what's-new pages work best.

Examples for [category]: <category-aware suggestions>

Or hit enter to skip — you can add competitors later by editing .vibe-iterate/config.json.
```

0 URLs → `competitors: []` and continue. 1-5 → validate each starts with `http://`/`https://`; skip malformed ones with a one-line warning.

### Step 5 — synthesize the category description

`category` string format: `<framework anchor> — <one-line description of what the app does>`. Example: `Next.js 16 web app — AI-powered note-taking with vector search and shared workspaces`.

Read first 10 lines of `README.md` for purpose; fall back to `package.json` `"description"`; if both missing, `<framework anchor> — purpose unclear (edit .vibe-iterate/config.json to set)`.

### Step 6 — write `.vibe-iterate/config.json`

```json
{
  "category": "<from step 5>",
  "competitors": [<from step 4>],
  "framework_pins": [<from step 3>],
  "last_inferred_at": "<ISO-8601 UTC timestamp, now>"
}
```

**Validate against `.agent/skills/vibe-iterate-guide/schemas/config.schema.json` before writing.** Create `.vibe-iterate/` if missing. Atomic write (fresh write, no read-modify-write).

Do NOT create `atlas.jsonl` here (first banner mode that ships/rejects/queues creates it). Do NOT create `radar.cache.json` here (that's the scheduled refresh's / `/vibe-iterate-radar`'s job).

### Step 7 — hand back

```
Set up:
- Category: [category]
- Competitors: [N URLs] (or "none — add later")
- Framework pins: [N tracked]
- Written: .vibe-iterate/config.json

Want a mode recommendation now? Run /vibe-iterate (no args).
```

Do NOT auto-fire the bare router.

## Refresh case (config already exists)

1. Read `last_inferred_at`.
2. >30 days old → *"Config last refreshed [N days] ago. Refresh now? (yes / no — keep existing)"* — default yes.
3. <30 days old → *"Config is current (refreshed [N days] ago). Refresh anyway? (yes / no)"* — default no.
4. Yes → run steps 1-6; step 6 overwrites; surface what changed (pins added/removed, category drift).
5. No → exit cleanly with a one-line acknowledgment.

## Anti-patterns

- **Don't list every missing file.** Acknowledge once, move on.
- **Don't ask for the framework when you can read package.json.** Same for name, description, language.
- **Don't write an empty atlas.jsonl** "to be ready."
- **Don't kick off any mode after bootstrap.**
- **Don't lecture about what vibe-iterate does.** The user invoked it.

## Cross-references

- Schema: `.agent/skills/vibe-iterate-guide/schemas/config.schema.json`
- Atlas conventions (why we don't pre-create atlas.jsonl): `.agent/skills/vibe-iterate-guide/references/atlas-conventions.md`
- Bare router that invokes this on first run: `/vibe-iterate`
