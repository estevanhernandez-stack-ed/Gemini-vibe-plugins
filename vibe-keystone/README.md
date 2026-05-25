# vibe-keystone — Antigravity port

The Google Antigravity 2.0 port of [vibe-keystone](https://github.com/estevanhernandez-stack-ed/vibe-Keystone), the 626Labs bootstrap plugin that writes the load-bearing project-rules file for any repo. Same brain — inventory first, interview for tenant context, adapt to the repo type — repackaged for Antigravity's workflow + rules model. The one meaningful adaptation: on Claude Code keystone produced a `CLAUDE.md`; **here it produces an `AGENTS.md`** — Antigravity's always-on rules file.

## What it does

The keystone is the load-bearing structural file in any repo: every agent decision, every dispatched subagent, every commit message rests on it. If the rules surface is weak, the architecture standing on it crumbles. You type `/vibe-keystone`, it asks a few questions, then writes an `AGENTS.md` that future agents in that repo will stand on.

1. **Inventories the repo** — `git status`, `git log`, top-level layout, stack files, existing `.agent/` / `.claude/`, workflows. Refuses to write blind.
2. **Interviews you for tenant context** — whose repo is this (626Labs / another org / individual)? Tenant docs (handbook, voice guide, principles, persona) to read before drafting? Where do decisions log? Persona inheritance vs. override? Repo type? The defaults are 626Labs-flavored, but tenant answers swap them through — no org's conventions get baked in by accident.
3. **Produces an `AGENTS.md`** following a structured skeleton (title + persona note, Tech Stack + Voice, design system, "What's where", domain section, common tasks, conventions, decisions log, "What NOT to do", references).
4. **Self-checks** — every required section present, no rotting snapshot lists, voice rules match repo type, references concrete.
5. **Proposes follow-ups** — agent config that fits the repo. Does not auto-create.
6. **Optionally captures** (opt-in, off by default) a small anonymous structural note so `/vibe-keystone-evolve` can improve the skeleton over time.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-keystone`, `/vibe-keystone-evolve`).
   - **Rules** from `AGENTS.md` — the lean always-on layer (what the plugin produces, the no-telemetry hard rules, the capture-log location).
3. There are **no skills** in this port — keystone has no shared-behavior `guide` skill and no loggers. The whole of its behavior lives in the `/vibe-keystone` workflow body. (This is the minimal plugin shape in the family.)
4. To bootstrap a repo's rules: type `/vibe-keystone`. It inventories, interviews, and writes `AGENTS.md`.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-keystone` | The main command — bootstraps the repo's `AGENTS.md`. Inventories the repo, interviews for tenant context, writes the rules file adapted to the repo type. The eponymous, user-invoked entry point (the router form). |
| `/vibe-keystone-evolve` | L1 self-evolution — reads the opt-in capture log and proposes skeleton/classifier improvements to `/vibe-keystone`. Writes `proposed-changes.md`. Never auto-applies. |

## The CLAUDE.md → AGENTS.md adaptation

Keystone's whole job is bootstrapping the project's always-on rules file. That file is tool-specific:

| | Claude Code (source) | Antigravity (this port) |
|---|---|---|
| Rules file produced | `CLAUDE.md` | **`AGENTS.md`** |
| Global persona reference | `~/.claude/CLAUDE.md` | global rules file (e.g. `~/.gemini/antigravity/AGENTS.md`) |
| Capture log | `~/.claude/plugins/data/vibe-keystone/` | `~/.gemini/antigravity/data/vibe-keystone/` |

This is not a cosmetic repoint — it's the plugin's *output contract*. The interview, the repo-type adaptation, and the skeleton all target `AGENTS.md`. Keystone may still *read* a `CLAUDE.md` when one is present (dual-tool repos, stale context worth folding), but the file it writes is `AGENTS.md`.

## State files

Keystone is a one-shot generator. It writes one file into the host repo:

- **`AGENTS.md`** at the repo root — the produced rules file. Local only.

The only write outside the repo is the opt-in capture log (below). No other project-local state.

## Privacy

No telemetry. The opt-in capture log (`~/.gemini/antigravity/data/vibe-keystone/captures.jsonl`) is off by default, written only when you say yes at the end of a run, and records structure only — never your code, file paths, repo name, or org name. Local only; never transmitted. See `PRIVACY.md` in the source repo for the full disclosure.

## Composes with

vibe-keystone works standalone — it requires no sibling plugin. It's a Foundation: it sets the rules surface every other plugin's agents stand on. Run it first in a new repo, then layer the process plugins (vibe-cartographer, vibe-iterate, vibe-walk, etc.) on top.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-keystone@0.2.1`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, every Claude → Antigravity adaptation, the open questions, and the vibe-keystone-specific port notes (the eponymous-command → router move, the CLAUDE.md → AGENTS.md meta-adaptation, and the no-guide / no-loggers minimal shape) appended at the end.
