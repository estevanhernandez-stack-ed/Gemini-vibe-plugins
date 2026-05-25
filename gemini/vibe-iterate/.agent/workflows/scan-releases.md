---
description: "Run when the user says /scan-releases [package] and wants to know what's new in a specific lib (or all libs) since they last bumped. Reads package.json pins, queries release notes via context7 + web search, outputs per-package list of breaking changes, new features, security fixes, codemod availability."
---

# /scan-releases [package] — what's new since you last bumped

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

For each library in `package.json` (or one specific library if `[package]` is given), queries release notes since the pinned version and renders a digest: breaking changes, new features, security fixes, and whether a codemod exists for the bump.

Read-only. Does NOT bump anything — that's `/upgrade`'s job. The output is decision-support: "is this bump safe? does it unblock anything? is there a known migration path?"

## Hard rules

- **Read-only.** No package installs, no version bumps, no commits. The only side effect is a write to the radar cache (under `framework_releases[]`) so subsequent `/radar` calls have fresh data — this is opt-in via the `--cache` flag, default off for the standalone case.
- **Honor the pinned range.** If the pin is `^16.0.0` and latest is `17.0.0`, surface that 17.x is *available but outside the current range*, then continue with the bump-within-range analysis (16.x → latest 16.x). Don't auto-recommend a major bump unless asked.
- **Cite sources.** Every "breaking change" claim and every "codemod available" claim must link to the source (release notes URL, codemod repo URL).

## Inputs

- **`$1`** — optional. The package name (e.g., `next`, `react`, `vitest`). If absent, scans all libraries from `package.json`'s `dependencies` + `devDependencies`. Cap at 20 libraries when scanning all (skip `@types/*`, `eslint*`, `prettier`, `typescript` unless they're load-bearing).
- **Project state** — `package.json` (or stack equivalent: `pyproject.toml`, `Cargo.toml`, `go.mod`). If no manifest file is present, surface: *"No package manifest found. /scan-releases needs a package.json (or pyproject.toml / Cargo.toml / go.mod) to know what's pinned."*

## Procedure

### Step 1 — read the manifest

Identify the package(s) to scan:

- **`package.json`** — read `dependencies` + `devDependencies`. Capture each as `{ name, current_pin (raw range string) }`.
- **`pyproject.toml`** — read `[project.dependencies]` (PEP 621) or `[tool.poetry.dependencies]` (Poetry).
- **`Cargo.toml`** — read `[dependencies]`.
- **`go.mod`** — read top-level `require` block.

If `[package]` arg was provided, filter to just that one. If not in the manifest, surface: *"`<package>` is not in the manifest. Did you mean: <fuzzy matches>?"*

### Step 2 — query release notes (per package)

For each package, in priority order:

1. **context7 MCP** (preferred) — `mcp__context7__resolve-library-id` to get the canonical ID, then `mcp__context7__query-docs` with the question: *"What's new in `<package>` since version `<current_pin>`? List breaking changes, new features, security fixes, and whether a codemod tool exists for the migration."*
2. **Web search fallback** — if context7 doesn't cover the package or returns empty, query: `<package> changelog since <current-pin>` and `<package> codemod migration <latest-version>`.
3. **GitHub releases API** — if the package's repository is on GitHub (read from `package.json.repository` if present), `gh api repos/<owner>/<repo>/releases` and parse release notes for tags between `current_pin` and `latest`.

For each package, capture:

- `current_pin` (verbatim from manifest)
- `latest` (resolved version, e.g., `19.0.1`)
- `latest_in_range` (latest version that satisfies `current_pin`'s range, e.g., for `^16.0.0` and latest `17.0.0`, this is the latest `16.x`)
- `breaking_changes[]` — each `{ description, source_url }`
- `new_features[]` — each `{ description, source_url }`
- `security_fixes[]` — each `{ description, cve_or_advisory, source_url }`
- `codemod` — `{ available: bool, command: <CLI command if known>, source_url }`

### Step 3 — render the digest

For each package, render this block (in alphabetical order by package name):

```
<package>  <current_pin> → <latest_in_range>  [<latest> available outside range]

Breaking changes (since <current_pin>)
- <description>  ← <source_url>
- ...

New features
- <description>  ← <source_url>
- ...

Security fixes
- <description>  (<cve_or_advisory>)  ← <source_url>
- ...

Codemod
- Available: <yes | no>
- Command: <if available>  ← <source_url>

Recommended action: <bump within range | hold (breaking changes need review) | bump now (security fix) | major bump (outside range — needs deliberate decision)>
```

If a section has no items, omit it entirely (don't render "Breaking changes: none").

After all packages, render a summary:

```
Summary
- Bump within range, no risk:  <list of package names>
- Bump within range, has codemod:  <list>
- Hold — breaking changes:  <list>
- Hold — major bump available:  <list>
- Security fix available:  <list>  ← prioritize these

Next steps
- Bump one safely:  /upgrade <package>
- Refresh broader radar with these findings:  /scan-releases --cache  (writes to .vibe-iterate/radar.cache.json)
```

### Step 4 — optional cache write (if `--cache` flag)

If the user passed `--cache`, write the results to `.vibe-iterate/radar.cache.json` under `framework_releases[]`. This updates the cache without doing the full radar refresh (no competitor or Product Hunt scans).

Read existing cache (if any), update only `framework_releases[]` and `refreshed_at`, write back. Validate against `.agent/skills/guide/schemas/radar-cache.schema.json` before writing.

## When invoked internally

By `feature-add` mode: *"is there a fresh framework feature that unblocks the highest-impact item?"* — `feature-add` calls `/scan-releases --silent` and reads the structured result.

By `/upgrade` mode: pre-flight check before bumping a single package. `/upgrade` calls `/scan-releases <package> --silent` to get the version diff and codemod availability before doing the bump.

In both cases, the calling skill passes `--silent` and consumes the structured output instead of the rendered template.

## Anti-patterns

- **Don't bump anything.** This is read-only. If the user wants the bump, they invoke `/upgrade`.
- **Don't recommend major bumps casually.** "1.x → 2.x available" is information, not a directive. Major bumps need deliberate user decisions.
- **Don't gloss over breaking changes.** If you found one, surface it with the source URL — don't bury it.
- **Don't scan dev-only utilities.** `eslint`, `prettier`, `@types/*`, `typescript` (when not the project's primary lang) are noise unless the user names them explicitly.

## Cross-references

- Sibling sidecar: `/upgrade` — does the actual bump
- Sibling sidecar: `/radar` — broader scan including competitors and Product Hunt
- Schema: `.agent/skills/guide/schemas/radar-cache.schema.json`
- Knowledge sources: AGENTS.md § Knowledge sources
