# vibe-insights — agent rules (Antigravity port)

> Always-on context for the `/vibe-insights` workflow. This is the Antigravity-rules
> equivalent of the voice + work-wall + output-discipline layer the Claude Code
> plugin carried in its skill body and in `~/.claude/CLAUDE.md`. There is no `guide`
> skill in this port — vibe-insights is a single orchestrator workflow over an
> external engine, so the whole always-on layer is below. Append-safe; assume the
> project already has its own `AGENTS.md` rules this merges into.

## What this plugin is

`/vibe-insights` is an **orchestrator**, not the analytics. It drives a separate,
deterministic Python engine (`vibe-insights` on PATH, or `python -m vibe_insights.cli`)
that reads local Claude Code session transcripts across every config home and machine
and emits a digest + a branded report. The workflow is where the LLM lives: it ensures
config, optionally overlays decisions, runs the engine, synthesizes a grounded narrative
read from `digest.json`, re-renders, and surfaces the result.

## The engine is a separate install (the load-bearing prerequisite)

The engine is **NOT bundled into this port** — same as Claude Code, where the skill
ran the installed `vibe-insights` binary. It's a standalone pip package (Python 3.11+):

```
python -m pip install "git+https://github.com/estevanhernandez-stack-ed/vibe-insights"
```

That puts `vibe-insights` on PATH; `python -m vibe_insights.cli` works either way. The
workflow invokes the binary at config-ensure (`--init`), the main run, `--render-only`,
and the Build Story (`--story-input`). **If the binary isn't present, surface the install
line and stop** — never reimplement the analytics inline. The engine is deterministic and
offline (no LLM, no MCP). Whether an Antigravity workspace has the engine installed is the
distinctive open item for this port (see § Open questions).

## Work-walling (hard rule — load-bearing for correctness)

The wall is by repo, not by home. The engine labels sessions in `work_repos` (employer
repos) as `work` and writes them to the **local-only shard** `index.work.local.json`.

- Work sessions ARE included and labeled in *your own* local report — all your work is
  viewable to you.
- The work shard **never syncs cross-machine** (only the `synced/` folder replicates) and
  **never gets pushed to git or any external/public surface**. Do not publish work content.
- This is not advisory. Honoring the wall is correctness: a leak of an employer's session
  content out of the local boundary is a failure, not a cosmetic miss.

## Decisions overlay — MCP-agnostic, skill-only boundary

Decisions are an optional overlay driven by `config.decisions.source`
(`none` | `file` | `mcp`). **Only this workflow ever touches MCP; the engine reads a
cache.** When `source == mcp`, the workflow fetches from the user's configured decisions
MCP, maps each entry to the canonical shape `{timestamp, title, body, project_tag, link}`,
and writes the list to `~/.vibe-insights/decisions.cache.json` **before** running the engine.
The engine reads that cache; it never calls MCP itself. This boundary is portable as-is —
Antigravity supports MCP. (626Labs `manage_decisions getUnified` or any user MCP both map
to the same canonical shape; the engine is identical regardless of source.)

## Output-ceiling discipline (hard rule)

Never dump the full report inline. Long-form output goes to files
(`~/.vibe-insights/reports/insights.{html,md}`, the narrative fragment, the Build Story
under `<repo>/docs/`); chat gets the tight highlights, the file path, and a one-line
coverage stat. This dodges output-token ceilings and keeps the artifacts diffable.

## Path handling

- `~/.vibe-insights/` — the **engine's own data dir** (config, digest, decisions cache,
  reports). Platform-agnostic; **leave it as-is**. It is NOT a Claude path and must NOT be
  repointed to `~/.gemini`.
- Genuine Claude refs that DID repoint: the coder-voice synthesis reference
  (`~/.claude/CLAUDE.md` → `~/.gemini/antigravity/AGENTS.md`) and the self-evolution log
  path (below).

## Self-evolving framework — session + friction logging

This plugin ships no loggers and no `evolve-*` workflow (single-orchestrator shape). The
log location is kept for family consistency only — nothing in this port writes it:
**`~/.gemini/antigravity/data/vibe-insights/`** (Claude Code original used
`~/.claude/plugins/data/vibe-insights/`).

## Voice

Default is neutral analytic prose. If `config.voice` is set, write the narrative read, the
Next-moves copy, and the Build Story in that voice:

- `coder` — the CODER VOICE SYNTHESIS in `~/.gemini/antigravity/AGENTS.md` (punchline-first,
  specific numbers, em-dashes, the dichotomy moves).
- `smart-brevity` — axiom-led, tight, published-article feel.
- `oscar` — the `oscar` skill / explainer mode (patient, faintly-exasperated).

Builder-to-builder, no corporate speak, no emoji in working output. Ground every narrative
claim in `digest.json` numbers — read what the tables *mean*, don't restate them, and don't
re-derive what the engine already scored (`unfinished_score`, `prune_candidates`).

## Open questions (do NOT invent Antigravity primitives)

- **External-engine dependency (this port's distinctive risk).** The port relies on a
  pip-installed `vibe-insights` binary being present on PATH in the Antigravity environment.
  Whether that holds is unverified — document the prereq, surface the install line, fail
  soft if it's missing.
- No cron/scheduled refresh, no `--silent` sub-workflow calls, no `hooks/`, no
  `~/.claude/profiles/builder.json` read, no workflow name collisions (one bare router
  `/vibe-insights`). All clean for this plugin.
