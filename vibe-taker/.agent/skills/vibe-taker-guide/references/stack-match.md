# Stack-match decision tree

> Consumed by the [`/vibe-taker-plant`](/.agent/workflows/vibe-taker-plant.md) workflow. KTD-4. Resolves OQ-3.

`/vibe-taker-plant` reads the bundle's `contract.json` and the target repo's manifests, then chooses one of three modes. This file is the canonical lookup table.

## Match levels

| Level | Definition | Plant mode |
|---|---|---|
| **High** | Same primary language **and** same framework family. | code-lift |
| **Low** | Same primary language, **different** framework family. | spec-driven |
| **Hard** | Different primary language. | decline (no file written) |
| **Fallback** | No manifest detected in target. | spec-driven (with notice) |

The chosen mode is named in the diff header: *"Mode: code-lift (high stack match — Node→Node, Express family)"* or *"Mode: spec-driven (low stack match — Python web feature → Python CLI target)"*.

## Detection priority — primary language

Walk cwd (one level up if needed) for manifests. **First match wins** for the primary-language detection; multiple manifests can co-exist for monorepos but the primary is whatever `/vibe-taker-plant` is targeting.

| Manifest | Implies |
|---|---|
| `package.json` (with `"type": "module"` or any `.ts` files) | Node — TypeScript or JavaScript |
| `pyproject.toml` / `requirements.txt` / `setup.py` | Python |
| `Cargo.toml` | Rust |
| `go.mod` | Go |
| `*.csproj` / `*.sln` | C# |
| `Gemfile` | Ruby |
| `composer.json` | PHP |
| (none in cwd or one level up) | Stack unknown — fallback to spec-driven |

## Match table — verbatim

| Source language | Target language | Source framework family | Target framework family | Match level | Plant mode |
|---|---|---|---|---|---|
| Python | Python | Web (FastAPI/Flask/Django) | Web (any of those) | High | code-lift |
| Python | Python | CLI (argparse/Typer/Click) | CLI (any of those) | High | code-lift with arg-parser adapter |
| Python | Python | Data (pandas/jupyter) | Data (any) | High | code-lift |
| Python | Python | Web | CLI | Low | spec-driven |
| Python | Python | (no framework) | (no framework) | High | code-lift |
| Node | Node | Web (Express/Hapi/Koa/Fastify) | Web (any of those) | High | code-lift |
| Node | Node | CLI (yargs/Commander) | CLI (any of those) | High | code-lift |
| Node | Node | React | Vue / Svelte | Low | spec-driven |
| Node | Node | Next.js | Vite + React | Low | spec-driven |
| Rust | Rust | (any) | (any) | High | code-lift |
| Go | Go | (any) | (any) | High | code-lift |
| Python | Node | * | * | Hard | decline |
| Node | Python | * | * | Hard | decline |
| * | * | * | * (different language) | Hard | decline |
| * | (no manifest detected) | * | n/a | Low (fallback) | spec-driven, with notice |

## Framework-family taxonomy

Use these family buckets when comparing source vs target. Same family = high match. Different family same language = low match.

- **Web / server** — Express, Fastify, Hapi, Koa, FastAPI, Flask, Django, Sinatra, Rails, Gin, Actix, Rocket.
- **Web / client** — React, Vue, Svelte, Solid, Angular.
- **Web / fullstack** — Next.js, Nuxt, SvelteKit, Remix.
- **CLI** — argparse, Typer, Click (Python); yargs, Commander, Oclif (Node); Cobra (Go); Clap (Rust).
- **Data / ML** — pandas, NumPy, Jupyter, scikit-learn, PyTorch, TensorFlow.
- **Build tooling** — Vite, esbuild, Webpack, Parcel, Rollup, Turbopack.
- **Game / 3D** — Three.js, R3F, Babylon, Unity (C#), Roblox/Luau.
- **Mobile** — React Native, Expo, Flutter.

## Hard-mismatch decline message

When the match level is `hard`, print **verbatim** (substituting `<source-lang>`, `<target-lang>`, `<bundle-path>`):

```
vibe-taker bundles capture <source-lang>; your target repo is <target-lang>. v1 doesn't auto-port across languages — too lossy. Here's the architecture sketch (<bundle-path>/architecture.md) and reference code (<bundle-path>/reference/); port manually, or capture a <target-lang>-native version of this feature into a new bundle.
```

**No file is written.** Exit class-1.

## No-manifest fallback message

When the target has no detectable manifest:

```
No manifest detected in target — falling back to spec-driven re-implementation. Reference code in <bundle-path>/reference/ for guidance.
```

Then proceed with spec-driven mode.

## Code-lift mechanics (high match)

1. Copy `<bundle>/reference/` files into the target, preserving relative tree under a target-conventional location:
   - Python with `pyproject.toml` and a top-level `src/<package>/` → place files under `src/<package>/<feature>/`.
   - Node with `src/` → `src/<feature>/`.
   - No conventional location → root of target with a `<feature>/` directory.
2. Rewrite imports:
   - Python: `from .` and `from <pkg>.` paths adjusted to target package name from `pyproject.toml`'s `[project].name` or `[tool.poetry].name`.
   - Node: `import './<rel>'` paths adjusted to target's `tsconfig.json#paths` if present, else relative.
3. Adapt within-family framework call sites only when an adapter exists (e.g., `argparse` → `Typer` migration of one flag declaration). When no adapter is wired, fall back to spec-driven for that file. **v1 ships zero adapters.** Same-family code-lift in v1 keeps the source's framework choice.
4. Generate the diff. Stage. Confirm. Write.

## Spec-driven mechanics (low match + fallback)

1. Read `<bundle>/architecture.md` + `<bundle>/contract.json` + `<bundle>/notes.md`.
2. Read `<bundle>/reference/` for shape and intent — but as a guide, not a copy source.
3. Generate fresh code in the target's stack matching the bundle's contract (same inputs, same outputs, same env vars).
4. Generate the diff. Stage. Confirm. Write.

## Why these thresholds

KTD-4: same-language-different-framework auto-translation (Express → FastAPI) is plausible but lossy in v1. Declining gracefully and giving the user the spec to port manually is more honest. Cross-language is not on the table for v1 at all.

Some genuinely-translatable cases (e.g., Click → Typer in Python) get downgraded to spec-driven instead of code-lift because v1 ships zero per-pair adapters. Acceptable tradeoff; v1.x can introduce adapters incrementally without changing the schema.
