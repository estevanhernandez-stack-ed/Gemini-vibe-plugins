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

**Easiest — hand Antigravity the repo.** Point the Antigravity agent at this repo and ask it to set up the plugin. It clones, copies the port's `.agent/` into your project, and **merges** the port's `AGENTS.md` into your project's rules (append, non-destructive — it reads your existing rules first). Then type a workflow like `/vibe-iterate`.

**Manual alternative:** copy the port's `.agent/` folder + `AGENTS.md` into your project root.

Either way Antigravity auto-discovers: `.agent/workflows/*.md` → slash commands, `.agent/skills/*/SKILL.md` → semantic, `AGENTS.md` → always-on rules.

> **Convention confirmed:** `.agent/` (singular). Validated live on Celestia3 (2026-05-24) — Antigravity's agent set the port up from this repo and ran it normally, project-local `.vibe-iterate/` state carried over intact.

## Built by [626 Labs](https://626labs.dev)

MIT — *Imagine Something Else.*
