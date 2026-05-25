# vibe-keystone — agent rules (Antigravity port)

> Always-on context for the vibe-keystone workflows. Keystone is deliberately
> lean: it has no `guide` skill, no persona layer, and no session/friction
> loggers — the whole of its behavior lives in the `/vibe-keystone` workflow
> body. This file holds only the handful of facts every keystone run needs
> ambiently. Keep it append-safe: Antigravity merge-appends it into the project's
> existing AGENTS.md, so assume you are one ruleset among several.

## What this plugin does

Keystone bootstraps the project's **always-on rules file**. On Claude Code that
file is `CLAUDE.md`; on Antigravity it is **`AGENTS.md`** — the load-bearing
structural file every agent decision in a repo rests on. The `/vibe-keystone`
workflow inventories the repo, interviews the user for tenant context (org /
decision surface / voice rules / persona), and writes an `AGENTS.md` adapted to
the repo type (code platform / marketing site / long-form writing / mixed).

**The output is always `AGENTS.md`.** Keystone may *read* a `CLAUDE.md` when one
is present (a dual-tool repo, or stale context worth folding), but the file it
produces is `AGENTS.md`. Don't write `CLAUDE.md` — that's the source tool's
artifact, not this port's output.

## Workflows

- **`/vibe-keystone`** — the router and main command. Bootstraps the repo's
  `AGENTS.md`. This is the eponymous, user-invoked entry point.
- **`/vibe-keystone-evolve`** — L1 self-evolution. Reads the opt-in capture log
  and proposes skeleton/classifier improvements to `/vibe-keystone`. Never
  auto-applies.

## Hard rules

- **No telemetry, no network.** Keystone reads the local repo and writes a local
  `AGENTS.md`. The only write outside the repo is the opt-in capture log (below),
  and it never leaves the machine. No outbound calls, ever.
- **Never write blind.** Inventory the repo before producing any file. Blind
  writes produce generic, useless rules.
- **Never overwrite an existing `AGENTS.md` without showing a diff and
  confirming.** Refresh, don't clobber.
- **Keystone ships no scripts.** The capture append (opt-in) is performed by the
  agent directly. This port introduces no executable helper.
- **Propose, don't auto-create.** Follow-up agent config (`.agent/` workflows,
  `.claude/agents/`, reference docs, automation) is proposed at the end of a run;
  the user decides what gets built.

## Self-evolving framework — opt-in capture only

Keystone is a once-per-repo generator, not a multi-session workflow, so it does
**not** carry session logging, friction logging, or decay (those would be
cargo-cult machinery for a different shape of tool). Its evolution loop is the
minimal pair: opt-in structural capture (Tier 0, written at the end of a
`/vibe-keystone` run only when the user says yes) + reflective proposal
(`/vibe-keystone-evolve`, Tier 1).

**Capture log location (Antigravity repoint):**
`~/.gemini/antigravity/data/vibe-keystone/captures.jsonl`
(the Claude Code original used `~/.claude/plugins/data/vibe-keystone/`).

Capture is **off by default**, anonymous (structure only — never code, file
paths, repo name, or org name), and local-only. See `PRIVACY.md` for the full
disclosure.

## Voice

Builder-to-builder, second person, punchline first. The produced `AGENTS.md`
is terse and action-first: no corporate speak ("empower / leverage / seamlessly /
unlock / unleash"), no emoji in file content, em-dashes welcome, markdown tables
for paths/tasks/conventions, code fences for commands. When 626Labs-owned, the
tagline is *Imagine Something Else.*
