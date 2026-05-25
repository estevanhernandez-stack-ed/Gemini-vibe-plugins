# Vibe Plugins — cross-agent ports

Ports of the [Vibe Plugins](https://github.com/estevanhernandez-stack-ed/vibe-plugins) family to agent platforms beyond Claude Code. One repo, folder-separated by platform — the Claude Code plugin repos stay pure; the ports live here.

> **Source of truth is upstream.** The canonical plugins are the Claude Code versions (their solo repos + the `vibe-plugins` marketplace). These are *ports* — they track upstream behavior, adapted to each platform's extension model.

## Layout

| Path | Platform | Status |
|---|---|---|
| `gemini/` | **Google Antigravity 2.0** (agent development environment — desktop / CLI `agy` / SDK) | 🟢 pilot: `vibe-iterate` |
| `gpt/` | OpenAI (Codex / GPT) | ⏳ not started |

## How a port maps (Antigravity)

The model is close to Claude Code, which is why the port is mostly mechanical:

| Claude Code | Antigravity 2.0 |
|---|---|
| `SKILL.md` skill (slash-invocable) | **workflow** — `.agent/workflows/<name>.md` (slash-invoked) |
| `SKILL.md` skill (internal/shared) | **skill** — `.agent/skills/<name>/SKILL.md` (semantic-loaded) |
| `CLAUDE.md` | `AGENTS.md` |
| `~/.claude/plugins/data/<plugin>/` | `~/.gemini/antigravity/data/<plugin>/` |

The full recipe — including the user-invocable-vs-internal split and every Claude→Antigravity adaptation — lives in each port's **`PORTING.md`**. Start with [`gemini/vibe-iterate/PORTING.md`](gemini/vibe-iterate/PORTING.md): it's the pilot cookbook for porting the rest of the family.

## Pilot: vibe-iterate → Antigravity

`gemini/vibe-iterate/` — 13 workflows, 3 skills, `AGENTS.md`. Proven path: vibe-iterate originally ran under Antigravity on the fly, which is what kicked off this initiative.

**Open runtime questions** (need a live Antigravity instance to settle — see PORTING.md): scheduled/cron refresh, workflow-to-workflow `--silent` composition, and flat slash-name collisions across multiple installed ports.

## Built by [626 Labs](https://626labs.dev)

MIT — *Imagine Something Else.*
