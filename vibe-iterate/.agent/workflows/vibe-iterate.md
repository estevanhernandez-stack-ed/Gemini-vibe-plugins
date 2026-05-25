---
description: "Run when the user types /vibe-iterate (bare, no subcommand). Reads project state (Atlas, radar cache, recent commits), recommends a mode for the moment (feature-add, competitive, ux-polish, bug-bash), and asks before launching. On first run (no .vibe-iterate/ directory), gracefully hands off to the bootstrap workflow before recommending. Never auto-fires."
---

# /vibe-iterate — bare router

Ptolemy persona, posture, knowledge sources, and Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `vibe-iterate-guide` skill (`.agent/skills/vibe-iterate-guide/SKILL.md`) — load it when you need to validate a write. Then follow this workflow.

## What this workflow does

Bare router. The user invoked `/vibe-iterate` with no subcommand — they want help choosing a mode. The agent's job is to:

1. **Detect the project state.** Is `.vibe-iterate/` set up? If not, the first-run path takes over (graceful — see below).
2. **Read the project's signals** (Atlas, radar cache, recent commits, branch state, presence of `feedback.md`).
3. **Synthesize:** what's the most useful mode RIGHT NOW for this project?
4. **Recommend ONE mode** with rationale.
5. **Surface 1-2 alternatives** with rationale for why they're second/third.
6. **Ask the user to confirm** before launching anything.

## Hard rules

- **Never auto-fire a mode.** Always ask the user before invoking another workflow.
- **Read-only by default.** This workflow does NOT write to the Atlas, the config, or any project file. (Bootstrap, when invoked from here, does write — but only after the user confirms.)
- **One recommendation, with alternatives.** Don't surface a 5-mode menu; that's not a recommendation.
- **No litany on first run.** When the project is fresh, don't enumerate everything that's missing. Acknowledge once, hand off to bootstrap, move on.

## First-run path (graceful)

If `.vibe-iterate/config.json` is **absent**, the project hasn't been set up. Ptolemy's response:

```
Fresh repo — no config yet. Let me get the lay of the land before recommending a mode.
```

Then immediately run the **`/vibe-iterate-bootstrap`** workflow (`.agent/workflows/vibe-iterate-bootstrap.md`). Bootstrap handles app-type identification, the brief interview, and writing `.vibe-iterate/config.json`. After bootstrap returns, the bare router does NOT auto-recommend a mode — bootstrap's output already prompts the user to re-run `/vibe-iterate` for a recommendation. This is intentional: the user makes the deliberate choice.

**Don't:**
- Don't say "First-time vibe-iterate run on this project. I'll need to infer your category and competitors before any banner mode can run productively." That's a lecture.
- Don't enumerate every state file that's missing.
- Don't try to recommend a mode without config — modes need the config to do their job.

**Do:**
- Acknowledge once, in one short line, that this is a fresh repo.
- Run bootstrap.
- Let bootstrap's output close the loop.

## Stale-config path (graceful)

If `.vibe-iterate/config.json` exists but `last_inferred_at` is **>30 days old**, surface a one-line nudge AT THE END of the recommendation (not the beginning — don't gate the recommendation on it):

```
(Config last refreshed N days ago — consider /vibe-iterate-bootstrap when you have a sec.)
```

Don't block. Don't re-bootstrap automatically. The recommendation is the headline; the refresh nudge is a sidebar.

## Project state to read (in order, when config exists)

1. **Atlas (`.vibe-iterate/atlas.jsonl`).** If absent or empty, no iterations have shipped yet — note "no shipped iterations yet."
2. **Config (`.vibe-iterate/config.json`).** Read `category`, `competitors`, `framework_pins`, `last_inferred_at`.
3. **Radar cache (`.vibe-iterate/radar.cache.json`).** If absent or `refreshed_at` >14 days old, mark stale; surface a follow-up nudge: *"Run `/vibe-iterate-radar` for a fresh signal scan."*
4. **Recent commits.** Last 10 on the current branch via `git log --oneline -10`.
5. **Branch state.** On `main`/`master`? A feature branch? Uncommitted changes (`git status --porcelain`)?
6. **`feedback.md` presence.** If present at project root, surface as input for a Bug-bash candidate. Read first 30 lines for context (not the whole file — that's bug-bash's job).

## Mode recommendation logic

Pick ONE based on the strongest signal:

| Signal (in priority order) | Recommend |
|---|---|
| `feedback.md` exists with unaddressed items, AND last Atlas-shipped item >7 days ago | **bug-bash** |
| Radar cache shows competitor changelogs with new items in user's category | **competitive** |
| Radar cache shows >3 framework releases since last shipped iteration | **feature-add** |
| Recent commits show 3+ feature lands but no polish PRs (none matching `^(fix|polish|ui)`) | **ux-polish** |
| Atlas shows >5 recent shipped entries, no rejected ones | **feature-add** (gentle note: review the Atlas; you may be over-shipping) |
| Nothing clearly in scope | **feature-add** as the safest default; let the user pivot |

When two signals tie, prefer the mode the user invoked LEAST recently (count `mode` occurrences in the last 30 days of the Atlas, prefer least-frequent).

## Output shape (when config exists)

```
Recommendation: /<mode>

Why:
- [signal 1, with one-line evidence]
- [signal 2, with one-line evidence]

Alternatives:
- /<other-mode-1> — [why this is second]
- /<other-mode-2> — [why this is third]

Project state:
- Atlas: <N entries, last shipped YYYY-MM-DD>
- Config: <inferred YYYY-MM-DD>
- Radar cache: <refreshed YYYY-MM-DD or "absent">
- Branch: <main or feature/...>
- feedback.md: <present|absent>

Run /<mode>? (yes / pick alternative / not now)
```

Wait for the user's response. Do NOT run any subcommand workflow on your own.

## Posture announcement at session-start

Before producing the recommendation, surface the register in one short line:

> *Routing → conservative read. I'm reading state, not writing anything.*

Skip the announcement on the first-run path (bootstrap does its own announcement).

## Cross-references

- Bootstrap: `/vibe-iterate-bootstrap` (`.agent/workflows/vibe-iterate-bootstrap.md`) — invoked on first run
- Banner modes: `/vibe-iterate-feature-add`, `/vibe-iterate-competitive`, `/vibe-iterate-ux-polish`, `/vibe-iterate-bug-bash`
- Sidecars: `/vibe-iterate-radar`, `/vibe-iterate-rate`, `/vibe-iterate-spy`, `/vibe-iterate-scan-releases`, `/vibe-iterate-ship`, `/vibe-iterate-upgrade`
- Rules + reference: `AGENTS.md`, `.agent/skills/vibe-iterate-guide/SKILL.md`
