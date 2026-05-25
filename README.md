# Gemini-vibe-plugins

The **Google Antigravity 2.0** ports of the [Vibe Plugins](https://github.com/estevanhernandez-stack-ed/vibe-plugins) family. One repo per agent platform — this is the Gemini/Antigravity one; the Claude Code plugin repos stay pure upstream.

> **Source of truth is upstream.** The canonical plugins are the Claude Code versions (their solo repos + the `vibe-plugins` marketplace). These are *ports* — they track upstream behavior, adapted to Antigravity's extension model.

## Layout

One folder per ported plugin, at the repo root:

| Plugin | Status |
|---|---|
| [`vibe-iterate/`](vibe-iterate/) | 🟢 pilot — 13 workflows, 3 skills, AGENTS.md |
| _the other 11_ | ⏳ port via the cookbook |

## How a port maps (Claude Code → Antigravity)

The model is close, which is why porting is mostly mechanical:

| Claude Code | Antigravity 2.0 |
|---|---|
| `SKILL.md` skill (slash-invocable) | **workflow** — `<root>/.agent/workflows/<name>.md` (slash-invoked) |
| `SKILL.md` skill (internal/shared) | **skill** — `<root>/.agent/skills/<name>/SKILL.md` (semantic-loaded) |
| `CLAUDE.md` | `AGENTS.md` |
| `~/.claude/plugins/data/<plugin>/` | `~/.gemini/antigravity/data/<plugin>/` |

The full recipe — the user-invocable-vs-internal split and every Claude→Antigravity adaptation — is in [`vibe-iterate/PORTING.md`](vibe-iterate/PORTING.md). Read it before porting plugin #2.

## Installing a port in Antigravity

Drop the port's `.agent/` folder + `AGENTS.md` into your project root; Antigravity auto-discovers (workflows → slash commands, skills → semantic, `AGENTS.md` → rules). Type a workflow like `/vibe-iterate` to confirm it loaded.

> **Directory-name caveat:** Google's own codelabs disagree on `.agent/` (singular) vs `.agents/` (plural) for the workspace config dir, and on the global path. The ports use `.agent/`. Confirm against your Antigravity build — if a workflow doesn't appear after dropping the folder in, rename `.agent/` → `.agents/`. Once confirmed, the cookbook gets pinned to the right convention.

## Built by [626 Labs](https://626labs.dev)

MIT — *Imagine Something Else.*
