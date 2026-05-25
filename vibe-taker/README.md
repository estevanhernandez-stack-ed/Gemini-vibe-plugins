# vibe-taker — Antigravity port

The Google Antigravity 2.0 port of [vibe-taker](https://github.com/estevanhernandez-stack-ed/vibe-taker), the 626Labs feature-portability plugin. Take it with you: capture a feature out of one repo as a portable bundle on a cross-repo shelf, then plant it into another and adapt to the destination stack. Same brain — autonomous capture, mandatory diff confirmation on plant, stack-match-driven code-lift vs spec-driven vs decline — repackaged for Antigravity's workflow + rules model.

vibe-taker is a **lean three-command plugin: no router, no evolve, no CLI.** The three workflows ARE the surface. (Each was a Claude Code command + same-named skill that the port merged into one workflow — see Port provenance.)

## What it does

vibe-taker, in one sentence: it reads files in your repo, writes them to a cross-repo shelf at `~/.vibe-taker/library/`, and writes files into your repo only after you explicitly confirm a diff.

1. **`/vibe-taker-capture <path|file|glob>`** — the harder half. Reads the target with no human input first: language, manifests, entry points, I/O surface, prompts, intent, gotchas. Snapshots the reference code, extracts an architecture sketch + a contract, and only fires a short interview (≤4 questions) when WHY can't be derived from source alone. Skips secret-like files, stubbing any that look load-bearing. Atomic stage-and-`mv` write so a half-built bundle never lands on the shelf.
2. **`/vibe-taker-list [--search <q>] [--sort name|lang]`** — read-only view of the shelf; the discovery surface for plant. Default sort is most-recently-captured first. Flags near-duplicates (Jaccard ≥ 70% over summaries) so the shelf doesn't sprawl.
3. **`/vibe-taker-plant <name> [--version=vX]`** — drop a captured bundle into the current repo. Detects the target stack, picks **code-lift** (same language + family), **spec-driven** (same language, different family, or no manifest), or **declines** (different language — too lossy to auto-port in v1). **Always shows a unified diff and asks `[y/N]` before any write.** No `--yes` flag exists.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-taker-capture`, `/vibe-taker-list`, `/vibe-taker-plant`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded, not slash-invoked (the `vibe-taker-guide` situational reference + two reserved loggers).
   - **Rules** from `AGENTS.md` — the always-on layer (persona, voice, the capture/plant posture, hygiene rules, the error contract, Pattern #13 composition, the log-path repoint).
3. Capture from a repo: `cd` into it, run `/vibe-taker-capture <path>`. List the shelf: `/vibe-taker-list`. Plant elsewhere: `cd` into the target repo, run `/vibe-taker-plant <name>` and confirm the diff.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-taker-capture <path\|file\|glob>` | Lift a feature into a portable bundle on the shelf. Autonomous read pass + interview-only-when-needed. Six artifacts per bundle (`README.md`, `architecture.md`, `contract.json`, `prompts/`, `reference/`, `notes.md`). |
| `/vibe-taker-list [--search <q>] [--sort name\|lang]` | Read-only shelf listing with near-duplicate flagging. The discovery surface for plant. |
| `/vibe-taker-plant <name> [--version=vX]` | Plant a bundle into the current repo. Stack-match → code-lift / spec-driven / decline. Mandatory diff confirmation before any write. |

## Skills

| Skill | Role |
|---|---|
| `vibe-taker-guide` | Situational reference loaded by the workflows: the bundle schema, secret-file skip patterns, the stack-match decision tree, the interview gate, the error contract, plus the JSON schemas and the three artifact templates. (The always-on half — persona/voice/posture/hygiene — was split out into `AGENTS.md`.) |
| `vibe-taker-session-logger` | Reserved v2 placeholder — documents the two-phase session-log contract + reserved data path. **No v1 workflow invokes it.** |
| `vibe-taker-friction-logger` | Reserved v2 placeholder — documents the friction-log contract + reserved data path. **No v1 workflow invokes it.** |

## The local shelf — source of truth

Bundles live at `~/.vibe-taker/library/<name>/<version>/`; the shelf manifest is `~/.vibe-taker/library/index.json`. Hand-editing a bundle is supported and expected — the JSON schema is the contract, not the agent's output. The shelf is **local only by default** — no network calls, no sync (cross-machine sharing is a v2 concern). On the first-ever capture on a machine, capture writes a privacy notice to `~/.vibe-taker/README.md`.

## Composes with

vibe-taker works standalone. Its one optional composition: after a successful plant, it checks for the 626Labs decision-log MCP (`mcp__626labs-cloud__manage_decisions`) and logs the plant if present — succeeding silently if absent. The MCP is never required. The two loggers are reserved-but-dormant in v1, so the self-evolving framework's `/evolve` loop is not yet wired.

## State files

- **`~/.vibe-taker/library/`** (home dir) — the cross-repo shelf. Carried over untouched from a Claude Code install; the bundle format is portable as-is.
- **Target repo** — only on an explicit, confirmed plant. Per-file atomic `.tmp` + `mv`.
- **`~/.gemini/antigravity/data/vibe-taker/`** — reserved log location for the v2 loggers (Claude Code original used `~/.claude/plugins/data/vibe-taker/`). Dormant in v1.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-taker@0.1.2`. The port merged each of the three Claude Code commands (`capture`, `list`, `plant`) with its same-named implementation skill into one workflow apiece — the command's clean one-line description became the workflow `description`, the skill body became the workflow body. The `guide` skill was split: persona/voice/posture/hygiene → `AGENTS.md`; bundle schema / secret patterns / stack-match tree / interview gate / error contract / schemas / templates → the `vibe-taker-guide` skill. The two loggers stay skills (reserved-dormant in v1). See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the command-merge pattern (step 2b), every Claude → Antigravity adaptation, the open-question answers, and the vibe-taker-specific port notes.
