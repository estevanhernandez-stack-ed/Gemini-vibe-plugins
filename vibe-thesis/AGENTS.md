# vibe-thesis — agent rules (Antigravity port)

> Always-on context for the vibe-thesis workflows. The Claude Code plugin had no
> shared `guide` skill — this layer is synthesized from the orchestrator's
> load-bearing rules + the shared posture across the voice pipeline. Append-safe:
> Antigravity merge-appends this into the target project's existing `AGENTS.md`.

## What this plugin does

Vibe Thesis scaffolds and co-authors thesis-shaped projects — academic
dissertations, master's theses, long-form research articles, position essays —
and renders them to PDF / HTML / markdown. It wraps the ThesisStudio template
with a Claude-Code-native (now Antigravity-native) orchestration layer plus a
three-skill voice pipeline (capture → apply → lint).

Workflows:

- **`/vibe-thesis`** — the orchestrator / router. Auto-engages on scaffold or
  iterate intent. Scaffold mode sources the workspace (Path A offline-bundled,
  or Path B `gh repo create --template ThesisStudio`), dispatches the
  project-local `/bootstrap`, runs `/vibe-thesis-voice`, installs the toolchain,
  and confirms a round-trip render. Iterate mode detects the project phase and
  routes to the next-most-useful workflow.
- **`/vibe-thesis-render`** — render the project (PDF / HTML / md / all).
  Pre-runs compile-tokens + check-citations; `--guard` lints for self-review
  tone first.
- **`/vibe-thesis-status`** — read-only one-screen project state report.
- **`/vibe-thesis-voice`** — author voice synthesis (capture). Base + extend
  modes. **Writes the `## VOICE SYNTHESIS` block to `AGENTS.md`** (see Output
  contract below).
- **`/vibe-thesis-smooth`** — apply the captured voice profile to a draft
  (multi-pass rewrite). The middle step of the voice pipeline.
- **`/vibe-thesis-guard`** — lint body content for self-review tone. Advisory.
- **`/vibe-thesis-audit`** — the same lint against any markdown file, no project
  marker required. Public-grade discipline filter.

There are no internal skills, no session/friction loggers, no evolve workflow.

## The ThesisStudio stance (always-on)

The plugin layers on ThesisStudio's three persona pillars. Honor them in any
drafting or review work:

1. **Sourced Specificity** — claims carry citations; specifics beat generalities.
   Name the dimension, the number, the comparison point.
2. **Disciplined Argument** — structure serves the claim. No padding, no
   signposting for its own sake.
3. **Honest Limits** — own what the work doesn't cover. This is the pillar the
   guard/audit lints make enforceable: **self-review tone is the failure mode.**
   Inflationary adjectives (*groundbreaking, comprehensive, novel*), self-praise
   framings (*we make N contributions, to the best of our knowledge*), defensive
   over-qualification, and conclusions that re-assert importance are all the
   work praising itself instead of letting findings speak. Catch them; let the
   writer revise.

## Voice posture

Author voice is the fourth layer under the pillars: 2-4 timeless author voices
+ 2-4 contemporary field experts + a synthesis ratio, optionally extended with
written exemplars, narrative samples, and forced-choice micro/macro rules.
**Synthesize, don't imitate** — take rhythm and sentence shape, leave signature
tics behind. The ratio shifts emphasis, not membership. The voice pipeline is
linear and composable: `/vibe-thesis-voice` captures, `/vibe-thesis-smooth`
applies, `/vibe-thesis-guard` lints — each stands alone; the user composes.

## Output contract — the rules file is `AGENTS.md`

The Claude Code original wrote project rules and the voice profile to `CLAUDE.md`
and detected projects via a `<!-- VIBE_THESIS_MARKER: vN.M -->` stanza in
`CLAUDE.md`. **In this port, the live rules file is `AGENTS.md`:**

- `/vibe-thesis-voice` **writes** the `## VOICE SYNTHESIS` block to `AGENTS.md`.
- `/vibe-thesis-smooth` **reads** that block from `AGENTS.md`.
- All marker detection (`grep VIBE_THESIS_MARKER`), `THESIS_MODE` reads, and
  status reporting target `AGENTS.md`.
- The bundled scaffold (`templates/full/`) ships ThesisStudio's `CLAUDE.md`
  verbatim. On scaffold, copy it to `AGENTS.md` and treat `AGENTS.md` as the
  live rules file. A `CLAUDE.md` may be **read** for cross-tool context, but the
  file the workflows **write** is `AGENTS.md`.

## Bundled assets

The plugin carries the ThesisStudio scaffold verbatim under `.agent/`:

- `.agent/templates/full/` — the complete scaffold payload (~109 files): numbered
  dirs, design system, render scripts (`scripts/`), schemas, dev container, CI,
  the project-local `.claude/skills/` (bootstrap / merge-authors / lay-translator
  / research-integrate), and ThesisStudio's `CLAUDE.md`.
- `.agent/templates/overlay/` — Path B's local-additions diff (`.gitattributes`
  + `inject-marker.sh`).
- `.agent/examples/demo-article/` — the round-trip demo content.

These are scaffold-OUTPUT data, not plugin logic — carried byte-for-byte. The
orchestrator resolves them via `PLUGIN_DIR=.agent` at runtime.

## Hard rules

- **Round-trip honesty.** In scaffold mode, never silently mark the round-trip
  successful when `npm run render:pdf` fails. The single non-negotiable
  acceptance criterion is "install + scaffold + round-trip works on first try,
  no manual fixups." Surface failures verbatim.
- **Sibling-repo hard guard.** Refuse any operation whose path resolves to
  `agentic-architect-vibe` (check via `git remote -v` or path basename). That
  repo is the article-source-of-truth for the toolchain; modifying it breaks the
  article.
- **Don't fork ThesisStudio.** The templates payload is a verbatim snapshot.
  Don't edit the bundled scaffold in place; refresh it via the documented
  procedure, not by hand-editing carried files.
- **Guard/audit are advisory.** They never auto-fix and never gate anything on
  their own. `/vibe-thesis-render --guard` is the only place findings can pause a
  render, and only with explicit user acknowledgment.
- **No telemetry.** This port has no session log, no friction log, no home-dir
  data writes. Nothing reports anywhere.

## Voice

Builder-to-builder, second person, sentence case. Punchline first, support after.
Em-dashes welcome. No corporate speak, no emoji in working output. When the work
is academic prose, the bar is the ThesisStudio stance — specific, disciplined,
honest about limits. Let the findings speak.
