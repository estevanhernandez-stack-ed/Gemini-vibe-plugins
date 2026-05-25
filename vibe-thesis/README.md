# vibe-thesis (Antigravity port)

Scaffold and co-author thesis-shaped projects — academic dissertations, master's
theses, long-form research articles, position essays — and render them to PDF /
HTML / markdown. A voice pipeline (capture → apply → lint) layers on top so the
prose reads in your voice and stays honest about its own limits.

This is the **Antigravity 2.0** port of the Claude Code `vibe-thesis` plugin
(source v0.2.0). See `tools/PORT-RUNNER.md` + `vibe-iterate/PORTING.md` for the
porting recipe; this plugin's specifics are in the cookbook's port log.

## Workflows

| Slash | What it does |
|---|---|
| `/vibe-thesis` | Orchestrator / router. Scaffold a new thesis project, or iterate inside an existing one. Auto-engages on scaffold/iterate intent. |
| `/vibe-thesis-render [pdf\|html\|md\|all] [--guard]` | Render the project. Pre-runs compile-tokens + check-citations. `--guard` lints for self-review tone first. |
| `/vibe-thesis-status` | Read-only one-screen project state report (planning docs, body, claim coverage, citations, last render). |
| `/vibe-thesis-voice [revise\|extend ...]` | Author voice synthesis. Names 2-4 author voices + 2-4 field experts + a ratio; `extend` adds the exemplar/narrative/rule layers smooth needs. Writes a `## VOICE SYNTHESIS` block to `AGENTS.md`. |
| `/vibe-thesis-smooth <draft.md> [flags]` | Apply the captured voice profile to a draft (multi-pass rewrite). Output to `<draft>.smoothed.md`. |
| `/vibe-thesis-guard [standard\|strict]` | Lint body content for self-review tone. Advisory. |
| `/vibe-thesis-audit <path> [--strict] [--public]` | Run the same lint against any markdown file — no project required. Public-grade discipline filter. |

No internal skills, no session/friction loggers, no self-evolution. Seven
workflows, that's the surface.

## Install (Antigravity)

Hand Antigravity this repo's URL and ask it to set up the plugin in your target
project. It clones the port, copies `.agent/*` into the project (workflows +
bundled scaffold assets under `.agent/templates/` and `.agent/examples/`), and
**merge-appends** this `AGENTS.md` into your project's existing `AGENTS.md`
(non-destructive), then drops the temp clone.

## The rules file is `AGENTS.md`

The Claude Code original wrote project rules and the voice profile to `CLAUDE.md`
and detected projects via a `<!-- VIBE_THESIS_MARKER -->` stanza in `CLAUDE.md`.
**This port writes and reads `AGENTS.md`** — `/vibe-thesis-voice` writes the
voice block there, `/vibe-thesis-smooth` reads it, and all marker/mode detection
targets it. The bundled ThesisStudio scaffold ships its own `CLAUDE.md` verbatim;
on scaffold, the orchestrator copies it to `AGENTS.md` and treats `AGENTS.md` as
the live rules file. A `CLAUDE.md` may be read for cross-tool context, but the
file the workflows write is `AGENTS.md`.

## Bundled scaffold

The full ThesisStudio scaffold ships verbatim under `.agent/`:

- `.agent/templates/full/` — the complete payload (~109 files): numbered scaffold
  dirs, design system, render scripts (Pandoc + xelatex + biber pipeline),
  schemas, dev container, CI workflows, and the project-local `.claude/skills/`
  (bootstrap / merge-authors / lay-translator / research-integrate).
- `.agent/templates/overlay/` — Path B's local-additions diff.
- `.agent/examples/demo-article/` — the round-trip demo content.

These are scaffold-OUTPUT data — carried byte-for-byte, not plugin logic.

## Toolchain

Rendering needs Pandoc + a LaTeX engine (xelatex) + biber + Node. The scaffold
ships a dev container that installs everything (recommended for first run), or
you can install natively. `/vibe-thesis` walks you through it at scaffold time
and surfaces font-substitution fallbacks if a design-system font is missing.

## Requires

- Node ≥ 18 (for the render scripts).
- Pandoc, a LaTeX engine, biber — or the bundled dev container.
- `gh` (optional) — enables Path B (`gh repo create --template ThesisStudio`).
  Without it, the offline Path A scaffold runs from the bundled templates.
