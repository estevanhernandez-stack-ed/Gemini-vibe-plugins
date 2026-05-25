# vibe-wrap — Antigravity port

The Google Antigravity 2.0 port of [vibe-wrap](https://github.com/estevanhernandez-stack-ed/vibe-wrap), a 626Labs session-end wrap-up plugin. Same brain — read the trail your toolkit already left, render a clean handoff doc, gate the rest — repackaged for Antigravity's workflow + skill + rules model. **This is the family's first hook-bearing port** — see § Event model.

## What it does

You just spent two hours across Cart, Doc, and a pile of commits. Now you're closing out, and the last ten minutes go to reconstructing "what got done today" from `git log`, memory, and scattered tool output. vibe-wrap collapses that cost. It reads the breadcrumb trail your sibling vibe plugins already left during the session — their session-logs, friction logs, wins logs — plus git state across repos and your decision log, then renders a markdown handoff doc and gates commit + push interactively. Cart's `/reflect` is project-scoped; this is for the close of a single working session.

- **Reads the trail, doesn't reconstruct it.** Breadcrumbs, sibling session-logs / friction / wins, git state, and your active decision-log backend.
- **Renders a durable wrap doc** — what shipped, decisions logged, friction captured, what's still uncommitted, what's still unpushed, session bounds. Each section names its empty state plainly.
- **Read wide, mutate narrow.** "What shipped" and "Still unpushed" span every sibling repo the session touched; the commit and push gates stay scoped to the current repo only. vibe-wrap never offers to commit or push another repo.
- **Bumpers, not walls.** Commit / push / decision-log-write / dashboard-bridge gates are each interactive and default to no-action. The doc lands regardless of which gates you accept or skip.
- **Pluggable decision log.** Four backends — `file-md` (recommended default), `file-jsonl`, `626labs-mcp` (the dashboard via MCP, auto-selected when reachable), `disabled`. Not a 626Labs-specific surface.

## Install / use in Antigravity

1. Copy this port's `.agent/` directory and `AGENTS.md` into your project root (or wherever Antigravity reads agent config for the workspace). The agentic install — hand Antigravity this repo URL and ask it to set up the plugin — clones, copies `.agent/*`, and merge-appends `AGENTS.md` into your project's existing one (non-destructive).
2. Antigravity auto-discovers:
   - **Workflows** from `.agent/workflows/*.md` — slash-invocable (`/vibe-wrap`, `/vibe-wrap-status`, `/vibe-wrap-evolve`).
   - **Skills** from `.agent/skills/*/SKILL.md` — semantically loaded when relevant (the internal `vibe-wrap-session-logger`, `vibe-wrap-friction-logger`, `vibe-wrap-plant`, and the `vibe-wrap-guide` reference detail).
   - **Rules** from `AGENTS.md` — always-on persona, the bumper-lanes invariant, voice, namespace isolation, the composition posture, and hard rules.
3. The wrap + status workflows call helper scripts under `.agent/scripts/` (Python 3.11; pure stdlib + git CLI). The deterministic core (`render-wrap.py`, the readers, the `decision-log/` dispatcher, the wrap template, the gate/secret/backend contracts) lives there; the logger + plant helpers live under each internal skill's `scripts/` dir.
4. **(Optional) Arm the SessionEnd nudge** — merge the `hooks` block from `.agent/hooks/settings.json` into your workspace `.gemini/settings.json`. See § Event model.
5. Requirements: Python 3.11+ on `PATH`, Git CLI on `PATH`. The 626Labs MCP is optional — one of four decision-log backends.

## Workflows

| Workflow | What it does |
|---|---|
| `/vibe-wrap` | The router / main command. Render the session wrap doc and surface the commit / push / decision-log / bridge gates. Flags: `--inline-only`, `--bridge`, `--session-window <hours>`, `--repos`, `--repo-roots`, `--no-multi-repo`. |
| `/vibe-wrap-status` | Read-only mid-session check — breadcrumb count, source plugins detected, friction count, decisions in window. Under 3 seconds, ≤20 lines. No mutations. |
| `/vibe-wrap-evolve` | L3 self-evolution. vibe-wrap reflects on its own sessions and writes a review-only `proposed-changes.md`. Never auto-applies. |

Plus the internal skill `vibe-wrap-plant` — sibling plugins call it to drop a breadcrumb (no-op-safe; not user-invocable).

## Event model — the SessionEnd nudge hook (the first hook-bearing port)

vibe-wrap is the first plugin in the family to ship a Claude Code hook, so this port is the cookbook's first hooks resolution.

**The finding:** Antigravity 2.0 supports lifecycle hooks. Its JSON hook system is inherited from the Gemini CLI lineage and exposes first-class lifecycle events including **`SessionEnd`** ("hooks that execute when a session ends; can perform cleanup or persist session data"), defined in `settings.json` under a `hooks` object keyed by event name. Each entry is a `command`-type hook that runs a shell command and receives a JSON payload on stdin (`session_id`, `transcript_path`, `cwd`, `hook_event_name`, `reason`). This matches the Claude Code SessionEnd contract field-for-field — Claude's `why` is Gemini's `reason`, and the nudge script reads neither (only `session_id` + `cwd`), so the difference is non-breaking.

**How it's wired:** the active config is [`.agent/hooks/settings.json`](.agent/hooks/settings.json). Merge its `hooks` block into your workspace `.gemini/settings.json` (or user settings, depending on where your Antigravity build discovers `settings.json` hooks). On session close it runs `python3 .agent/hooks/session-end-nudge.py`, which emits **one** line — `session looks done — /vibe-wrap to summarize?` — when the closing session left a trail (≥1 breadcrumb, ≥1 uncommitted file, or ≥1 commit ahead of remote). It is read-only, exits 0 on every path, and **never invokes `/vibe-wrap`.** The Claude Code original `.agent/hooks/hooks.json` is kept for provenance.

**Fail-soft:** the nudge is a non-critical convenience. If you don't merge the settings block — or if your Antigravity build discovers hooks differently than expected — the nudge simply doesn't fire and **`/vibe-wrap` works fully without it.** Nothing in the plugin depends on the hook.

## Decision-log backend

vibe-wrap pulls session decisions from a pluggable decision log — not a 626Labs-specific surface. Four backends: `file-md` (Markdown, recommended), `file-jsonl`, `626labs-mcp` (auto-selected when reachable), `disabled` (skips the gate). On your first `/vibe-wrap` with no config and no MCP, a one-time picker names the four options with `[skip — disabled]` as the fourth choice. Precedence: per-project `<repo>/.vibe-wrap/config.json` → global `~/.gemini/antigravity/data/vibe-wrap/config.json` → MCP auto-detect → first-run prompt. Smart-default file path: `<repo>/docs/decisions.md` when a `docs/` dir exists, else `~/.gemini/antigravity/decisions.md`. Full contract at [`.agent/scripts/references/decision-log-backends.md`](.agent/scripts/references/decision-log-backends.md).

## State files

- **Wrap docs** — `<repo>/docs/session-wraps/<ts>.md` (fallback `<repo>/.vibe-wrap/wraps/<ts>.md`). Project-local; portable as-is.
- **Decision log** — wherever your chosen backend points (in-repo, user-scoped, or the MCP). Owned by the user's log, outside vibe-wrap's namespace.
- **Self-evolution + breadcrumbs** — `~/.gemini/antigravity/data/vibe-wrap/` (breadcrumbs, vibe-wrap's own session + friction logs, global config). Home-dir; repointed from the Claude Code `~/.claude/plugins/data/vibe-wrap/`.

## Composes with

vibe-wrap reads what your plugins already write — zero coupling. If a sibling emits Pattern #2 session-logs at `~/.gemini/antigravity/data/<plugin>/sessions/<date>.jsonl`, vibe-wrap surfaces that work automatically. For richer attribution, a sibling drops a breadcrumb via the `vibe-wrap-plant` skill (fire-and-forget, no-op-safe). Anchored complements: `vibe-cartographer`, `vibe-doc`, `vibe-iterate`, `vibe-test` (sessions + friction + wins), `vibe-sec`, `thesis-engine`, `vibe-thesis`, `vibe-taker`. Composition is state-file-mediated — vibe-wrap reads the files siblings write, never invokes them — so there's no Antigravity workflow-compose dependency. The full sibling-author contract is at [`.agent/scripts/references/breadcrumb-contract.md`](.agent/scripts/references/breadcrumb-contract.md).

## Privacy

No telemetry. The self-evolving session/friction/breadcrumb logs (`~/.gemini/antigravity/data/vibe-wrap/`) stay local. Delete them anytime; the plugin keeps working, just loses its memory. No PII beyond the working-directory basename; no transcript content; no file contents.

## Port provenance

Mechanically and editorially ported from the Claude Code plugin at `vibe-wrap@0.2.1`. The headline port surfaces: the **SessionEnd hook** (first hook-bearing port — Antigravity supports the lifecycle event; wired via `settings.json`, fail-soft) and the **eponymous-main-with-differently-named-skill** case (the source `wrap` skill IS the `/vibe-wrap` command, ported to the bare router, not `/vibe-wrap-wrap`). See [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) for the full cookbook — the skill → workflow vs skill → skill mapping, every Claude → Antigravity adaptation, the open questions, and the vibe-wrap-specific port notes appended at the end.
