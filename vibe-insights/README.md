# vibe-insights — Antigravity port

The Google Antigravity 2.0 port of [vibe-insights](https://github.com/estevanhernandez-stack-ed/vibe-insights), the 626Labs cross-machine, work-walled Claude Code session analytics plugin. Same brain — a deterministic Python engine reads your session transcripts across every config home and machine, walls your employer's sessions local, and emits one branded report; the agent layer synthesizes a grounded narrative read on top — repackaged for Antigravity's workflow + rules model.

This port has a **novel shape for the family: one orchestrator workflow over an external engine.** The `/vibe-insights` workflow doesn't implement the analytics — it orchestrates a separate, pip-installable Python CLI. The engine is a documented **prerequisite**, not a bundle (exactly as in Claude Code, where the skill ran the installed `vibe-insights` binary).

## What it does

`/vibe-insights` ensures config, optionally overlays your logged decisions, runs the engine, synthesizes a narrative read grounded in the digest numbers, re-renders the report, and surfaces it — without ever dumping the full report inline. The engine produces:

- **Coverage** — sessions / repos / token burn, split by account (work vs personal) × machine.
- **Where was I** — most-recent sessions with titles, branches, machines (recall).
- **Token & cost** — burn, output share, and the cache reveal (cache-read tokens vs fresh input).
- **Trends** — burn per day, recent-vs-baseline acceleration.
- **How you work** — tool mix (the build-debug loop), delegation habit (subagent + Haiku usage), per-machine workhorse comparison.
- **Pick this back up** — open feature branches ranked by how likely they are to be genuinely unfinished, plus a **prune candidates** list.
- **Decisions** — your logged architectural decisions (MCP-agnostic: file or your dashboard MCP).
- **A narrative read** — a synthesized "how you actually work" interpretation, grounded in the numbers.

## Prerequisite — install the engine (it is NOT bundled)

The `vibe-insights` engine is a standalone, pip-installable Python tool (3.11+). This port carries the **agent layer only** — the `/vibe-insights` workflow that orchestrates it. Install the engine once where the Antigravity workspace can reach it:

```bash
python -m pip install "git+https://github.com/estevanhernandez-stack-ed/vibe-insights"
# Optional: share token/parse definitions with Sanduhr et al. (pulls cc-logs)
python -m pip install "git+https://github.com/estevanhernandez-stack-ed/vibe-insights#egg=vibe-insights[shared]"
```

That puts `vibe-insights` on PATH; `python -m vibe_insights.cli` works either way. The engine is deterministic and **offline** — it never calls an LLM or MCP; it reads local JSONL transcripts and a few local cache files. The LLM work (the narrative, the decisions overlay, per-session tags) happens in the `/vibe-insights` workflow and is handed to the engine as files. That keeps the analytics reproducible and the agent layer portable.

If the binary isn't found, the workflow surfaces the install line and stops — it does not reimplement the analytics inline.

## Install / use in Antigravity

1. Install the engine (above) — the prerequisite.
2. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
3. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-insights`).
   - **Rules** from `AGENTS.md` — the always-on layer: what the plugin is, the engine prerequisite, the work-wall hard rule, the decisions-MCP boundary, output-ceiling discipline, path handling, and voice.
4. There are **no skills** in this port — vibe-insights has no shared-behavior `guide` skill and no loggers. The whole agent layer is the single `/vibe-insights` orchestrator workflow. (This is the minimal-internal, single-orchestrator shape.)
5. To run: type `/vibe-insights`. On first run it ensures config (`vibe-insights --init`), then runs the engine and synthesizes the read.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-insights` | The orchestrator. Ensures the engine + config, optionally overlays decisions (none/file/MCP → cache before running), runs the engine, synthesizes the narrative read grounded in `digest.json`, re-renders (`--render-only`), and surfaces the report under the output-ceiling discipline. Also drives the optional Build Story (`--story-input`). |

## The shape that defined this port: orchestrator workflow + external engine

vibe-insights is the first port that is **a skill→workflow plus a documented pip prerequisite, not a bundle.** The Claude Code source is a github-source plugin = one orchestrator skill (`skills/vibe-insights/`) + a separate, pip-installable Python engine (`src/vibe_insights/`). The port carries the orchestrator (now `/vibe-insights`) and documents the engine as an external install — `src/` is deliberately **not** copied into `.agent/`, mirroring Claude Code, where the skill runs the installed binary. The judgment that defined the port: make the prerequisite explicit (workflow body + this README), and **leave the engine's own data dir (`~/.vibe-insights/`) alone** — only genuine Claude refs repoint. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook + the vibe-insights-specific notes.

## Path handling

| | Claude Code (source) | Antigravity (this port) |
|---|---|---|
| Engine data dir | `~/.vibe-insights/` | **`~/.vibe-insights/` (unchanged — engine's own, platform-agnostic)** |
| Coder-voice reference | `~/.claude/CLAUDE.md` | `~/.gemini/antigravity/AGENTS.md` |
| Self-evolution log (unused here) | `~/.claude/plugins/data/vibe-insights/` | `~/.gemini/antigravity/data/vibe-insights/` |

`~/.vibe-insights/` is the **engine's** data dir (config, digest, decisions cache, reports) — not a Claude/Antigravity tool path. It was correctly left untouched. Only the voice reference and the (unused) log path repointed.

## Decisions overlay (MCP-agnostic)

Decisions are optional, driven by `config.decisions.source` (`none` | `file` | `mcp`). When `mcp`, the **workflow** fetches from the user's configured decisions MCP, maps to the canonical `{timestamp, title, body, project_tag, link}` shape, and writes `~/.vibe-insights/decisions.cache.json` **before** running the engine — the engine reads the cache, never MCP. Only the workflow touches MCP. This boundary is portable as-is; Antigravity supports MCP. Works with 626Labs `manage_decisions getUnified` or any user MCP.

## Work-walling (privacy)

The wall is by repo, not by home. Sessions in your configured `work_repos` are labeled `work` and written to the **local-only** shard `index.work.local.json` — visible in your own report, but never synced cross-machine and never pushed to git or any external surface. Personal sessions sync. This is a correctness rule, not a preference.

## Composes with

vibe-insights works standalone. Its token math can align with **Sanduhr** via the optional [`cc-logs`](https://github.com/estevanhernandez-stack-ed/cc-logs) package when present, so burn numbers stay consistent across tools. Decisions can come from any MCP — including the 626Labs dashboard.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-insights@0.1.0`. See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, every Claude → Antigravity adaptation, the open questions, and the vibe-insights-specific port notes (the orchestrator-workflow + external-engine shape, and the "leave the plugin's own data dir alone, only repoint Claude paths" nuance) appended at the end.
