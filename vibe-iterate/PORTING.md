# PORTING.md — Claude Code → Antigravity 2.0 cookbook

> The pilot port: vibe-iterate@1.1.0 → Antigravity 2.0. This is the reusable recipe for porting the rest of the vibe-* family. Read it before porting plugin #2.

## TL;DR — the recipe in seven moves

1. **Inventory the source.** List every skill. Classify each as user-invocable (description says "use when the user says `/x`") or internal ("Internal SKILL — not a slash command").
2. **Split the `guide`.** Always-on layer (persona, posture, knowledge sources, cross-plugin detection, hard rules) → `AGENTS.md`. Deep reference detail (schemas, write conventions, trigger maps) → keep as a `guide` skill.
3. **User-invocable skills → workflows** (`.agent/workflows/<name>.md`, slash-invoked). One file per entry point.
4. **Internal/shared skills → skills** (`.agent/skills/<name>/SKILL.md`, semantic-loaded). These stay skills; workflows load them.
5. **Repoint paths.** `~/.claude/plugins/data/<plugin>/` → `~/.gemini/antigravity/data/<plugin>/`. `CLAUDE.md` → `AGENTS.md`. `plugin.json` → `.agent/agent.json` (port-bookkeeping). `${CLAUDE_PLUGIN_ROOT}` → relative `.agent/...` paths.
6. **Rewire cross-references.** `[../guide/SKILL.md]` → a one-liner pointing at AGENTS.md + the guide skill. `[../sidecar/SKILL.md]` → `/sidecar` slash form. `:sidecar` internal-call notation → `/sidecar`. `/plugin:cmd` → `/cmd`.
7. **Carry the data files verbatim.** Schemas and fixtures are format-agnostic — copy them into the guide skill unchanged.

## The mapping that defines the port

Claude Code conflates two things into one "skill" primitive: skills can be both semantically auto-loaded AND slash-invoked. Antigravity splits these:

- **Workflows** = slash-invoked, user-facing entry points.
- **Skills** = semantically loaded reference/behavior, not slash-invoked.
- **Rules** (`AGENTS.md`) = always-on ambient context (the CLAUDE.md equivalent).

So the port's core decision per source skill is: **is this an entry point the user types, or is it loaded by something else?**

### vibe-iterate's 16 source skills → port targets

| Source skill | Source kind | Port target | Why |
|---|---|---|---|
| `vibe-iterate` (bare router) | user-invocable | **workflow** `/vibe-iterate` | User types `/vibe-iterate` |
| `bootstrap` | "internal, but invoked directly when user says /bootstrap" | **workflow** `/bootstrap` | It IS user-invocable (the description lists the slash trigger). The "internal" framing was about the router calling it — workflows can call workflows, so it ports as a workflow. |
| `feature-add` | user-invocable | **workflow** `/feature-add` | Banner mode |
| `competitive` | user-invocable | **workflow** `/competitive` | Banner mode |
| `ux-polish` | user-invocable | **workflow** `/ux-polish` | Banner mode |
| `bug-bash` | user-invocable | **workflow** `/bug-bash` | Banner mode |
| `radar` | user-invocable sidecar | **workflow** `/radar` | Sidecar |
| `spy` | user-invocable sidecar | **workflow** `/spy` | Sidecar |
| `scan-releases` | user-invocable sidecar | **workflow** `/scan-releases` | Sidecar |
| `rate` | user-invocable sidecar | **workflow** `/rate` | Sidecar |
| `ship` | user-invocable sidecar | **workflow** `/ship` | Sidecar |
| `upgrade` | user-invocable sidecar | **workflow** `/upgrade` | Sidecar |
| `evolve-iterate` | user-invocable | **workflow** `/evolve-iterate` | User types it (L3 self-evolution) |
| `session-logger` | "Internal SKILL — not a slash command" | **skill** `.agent/skills/session-logger/` | Loaded by workflows, never typed |
| `friction-logger` | "Internal SKILL — not a slash command" | **skill** `.agent/skills/friction-logger/` | Loaded by workflows, never typed |
| `guide` | "referenced by every command SKILL, never invoked directly" | **split** → `AGENTS.md` + **skill** `.agent/skills/guide/` | See below |

**Count: 13 workflows, 3 skills (guide + 2 loggers), 1 AGENTS.md.**

### The guide split (the subtle one)

`guide` was a Claude Code skill that every command read for shared behavior. It bundled two very different kinds of content:

1. **Always-on behavior** — persona (Ptolemy), the three posture defaults, knowledge-source priority, Cart-detection logic, hard rules. This is context every workflow needs ambiently, every turn.
2. **Deep reference detail** — JSON schemas, Atlas write conventions, the friction-trigger map. This is only needed when a workflow is mid-flight and about to write a state file or log friction.

In Claude Code both lived in one skill body + its `references/`. In Antigravity:

- **(1) → `AGENTS.md`.** Always-on rules are exactly what AGENTS.md is for. Folded in: `ptolemy-persona.md`, `posture.md`, `knowledge-sources.md`, `cart-detection.md`, and the guide's "Hard rules" section. These reference docs were **collapsed into AGENTS.md prose** and NOT copied as separate files (so there's one source of truth for the always-on layer).
- **(2) → `.agent/skills/guide/`.** Kept as a skill because it's heavy and situational, not always-on. Carried over verbatim: `schemas/*.json`, `fixtures/*`, `references/atlas-conventions.md`, `references/friction-triggers.md`. The guide `SKILL.md` was rewritten to a thin index pointing at those files + AGENTS.md.

**Judgment rule for the next plugin:** if a reference doc is "how the agent should behave always," it belongs in AGENTS.md. If it's "the exact shape/rules for a thing the agent occasionally touches," it stays a skill. Schemas and trigger maps are always skill-side; personas and postures are always AGENTS-side.

## Every Claude → Antigravity adaptation (apply each, note each)

### Path repoints

| Claude Code | Antigravity | Where it appears |
|---|---|---|
| `~/.claude/plugins/data/vibe-iterate/` | `~/.gemini/antigravity/data/vibe-iterate/` | session-logger, friction-logger, evolve-iterate (read paths) |
| `~/.claude/profiles/builder.json` | `~/.gemini/...` equivalent | **Not present in vibe-iterate** — it has its own `.vibe-iterate/config.json` per-project, no global builder profile. (Flagged here because sibling plugins — vibe-cartographer — DO use `~/.claude/profiles/builder.json`; those ports must repoint it to `~/.gemini/profiles/builder.json` or the Antigravity user-config equivalent.) |
| `CLAUDE.md` (project rules) | `AGENTS.md` | The whole always-on layer |
| `.claude-plugin/plugin.json` | `.agent/agent.json` | Manifest; read by loggers for `plugin_version` |
| `${CLAUDE_PLUGIN_ROOT}/...` | relative `.agent/...` paths | Logger version-read; no env-var equivalent assumed |

**Chosen data path:** `~/.gemini/antigravity/data/<plugin>/`. Rationale: mirrors the Claude Code `~/.claude/plugins/data/<plugin>/` shape one-for-one (sessions subdir + friction.jsonl at the plugin root), keeps per-plugin isolation, and namespaces under `antigravity/` so it doesn't collide with other Gemini tooling. **Use this exact path for every sibling port** so the self-evolving framework's cross-plugin assumptions stay consistent.

### Naming / invocation repoints

| Claude Code | Antigravity | Notes |
|---|---|---|
| `/vibe-iterate:feature-add` | `/feature-add` | Antigravity workflows are flat slash names, no plugin namespace. **Watch for collisions** across installed ports (see open questions). |
| `:radar` / `:rate` (internal-call shorthand) | `/radar` / `/rate` | The colon-shorthand for "call this sibling skill" becomes the slash form. Note: in Antigravity a workflow calling another workflow is a real invocation — the original `--silent` internal-call convention (return structured data instead of rendering) is preserved in the workflow bodies as instructions, but Antigravity has no built-in "silent sub-workflow" primitive (open question). |
| `[../guide/SKILL.md](...)` markdown links | prose pointing at `AGENTS.md` + `.agent/skills/guide/SKILL.md` | Relative skill-to-skill links don't carry the same meaning |
| `[../session-logger/SKILL.md]` | "load the `session-logger` skill (`.agent/skills/session-logger/SKILL.md`)" | Skills are loaded, not linked |
| "available-skills list (system reminder)" — Cart-detection probe | "`vibe-cartographer` workflows/skills available in this Antigravity workspace" | The detection mechanism is environment-specific; the read-only/no-probe rule is preserved |

### Frontmatter

- **Workflows:** YAML frontmatter with a `description` (Antigravity uses it as the slash-command summary). vibe-iterate's source skill `description` fields were rewritten from "This skill should be used when the user says `/vibe-iterate:x`" to "Run when the user says `/x`" — same trigger semantics, Antigravity slash form. `name` dropped (the filename is the slash name).
- **Skills:** `name` (optional) + `description` (mandatory — the semantic trigger). Kept the source skills' `name` and rewrote `description` to note the internal-not-a-workflow status and the Antigravity log path.

## Mechanical vs needed-thought

**Mechanical (scriptable, did it with a Python pass):**
- Frontmatter swap (strip old, inject Antigravity form).
- `[../guide/SKILL.md]` guide-intro line → standard AGENTS.md pointer.
- `[../X/SKILL.md]` sibling links → `/X` slash form.
- `:sidecar` → `/sidecar` (with care for backtick-prefixed forms — `` `:rate` `` needed a separate regex pass; the first negative-lookbehind missed backticks).
- `/vibe-iterate:cmd` → `/cmd`.
- `~/.claude/plugins/data/...` → `~/.gemini/antigravity/data/...`.
- "At command start/end" → "At workflow start/end".

**Needed thought (could not be scripted):**
- **The guide split.** Deciding which reference docs are always-on (→ AGENTS.md, collapsed to prose) vs situational (→ guide skill, kept as files). A naive "copy all references" would have duplicated the persona/posture into both AGENTS.md and the skill.
- **bootstrap's classification.** Whether it's a workflow or skill. The source called it "internal" but the description listed a direct slash trigger — it's user-invocable, so it ports as a workflow. (Lesson: trust the slash-trigger phrasing in the description over the "internal" self-label.)
- **The `agent-plugin` category.** Source bootstrap classified Claude Code plugins via `.claude-plugin/plugin.json`. The port adds `.agent/` detection and renames the canonical category `claude-code-plugin` → `agent-plugin` (covers both). Minor content edit, but a real one.
- **Folded-reference back-pointers.** Workflow bodies that said "per `../guide/references/cart-detection.md`" had to point at `AGENTS.md § Cart-detection` instead, since that doc no longer exists as a file. Same for posture/knowledge-sources/persona.
- **evolve-iterate's self-edit targets.** Its proposal shapes name files to edit (`plugins/vibe-iterate/skills/<cmd>/SKILL.md`). Those repoint to `.agent/workflows/<cmd>.md` — because the thing it proposes editing is now a workflow, not a skill.
- **`plugin_version` source.** Loggers read it from `plugin.json`. Repointed to `.agent/agent.json`, which we created specifically to hold the mirrored version (Antigravity doesn't require it for discovery, but the audit field needs a source).

## Content preservation check

No real logic was dropped. Preserved intact:
- Ptolemy persona + the Cart-vs-Ptolemy posture distinction.
- The three posture defaults (regression-aware / user-trust-aware / small-diff-preferred) with their full "how to apply" detail.
- Three-layer knowledge sources (context7 → cache → web), with anti-patterns.
- Cart-detection: Pattern #13 deferral, heavy-iteration threshold, discovery upsell, the "never probe / never hard-fail / never auto-install" rules.
- All per-mode procedures step-for-step (ingest → cluster → Atlas-filter → score → pick → Cart-check → build → Atlas-write → close-out).
- The full `:rate` 5-axis rubric and verdict logic.
- Atlas conventions, schemas, fixtures (verbatim).
- Friction-trigger map (every per-command row), session/friction entry shapes, orphan detection.
- Self-evolving framework wiring (Levels 2 + 3) — only the log path changed.

## Open questions (no clean Antigravity equivalent — do NOT invent)

1. **Scheduled refresh.** The weekly radar cache refresh was powered by the Claude Code `schedule` plugin's cron. Antigravity's scheduled-task/cron mechanism (if any) is unverified. **Mitigation in the port:** `/radar` supports a manual `--refresh`; banner modes degrade gracefully on stale/missing cache. **To resolve:** confirm whether Antigravity has a cron/scheduled-agent primitive and wire the weekly job, or document radar as manual-refresh-only. This is the only place `schedule` was load-bearing.

2. **`--silent` sub-workflow calls.** Banner modes internally call sidecars (`/radar --silent`, `/rate --silent`) expecting structured data back instead of rendered output. Claude Code handled this as a skill-to-skill call within one turn. Antigravity workflow-to-workflow invocation semantics (does it spawn a sub-run? share context? support a "return data, don't render" mode?) are unverified. **Mitigation:** the workflow bodies keep the `--silent` instruction as agent guidance ("consume the structured output, don't render the user template"). **To resolve:** confirm how Antigravity composes workflows and whether the silent/structured-return pattern holds, or inline the sidecar logic into the banner modes.

3. **Workflow name collisions across ports.** Antigravity workflows are flat slash names with no plugin namespace. `/scan-releases`, `/ship`, `/upgrade`, `/rate`, `/radar`, `/spy`, `/bootstrap`, `/evolve-iterate` are generic enough that another installed port (or another vibe-* port) could collide. Claude Code avoided this with the `plugin:cmd` namespace. **To resolve:** decide a namespacing convention for Antigravity — either prefix workflow filenames (`vibe-iterate-radar.md` → `/vibe-iterate-radar`) or confirm Antigravity disambiguates. For this pilot we used the bare names to keep parity; flag before installing multiple ports side-by-side.

4. **`plugin_version` discovery.** We created `.agent/agent.json` to hold the version for the loggers' audit field. Whether Antigravity reads or requires this manifest for discovery is unverified — it's treated as port-bookkeeping. **To resolve:** confirm Antigravity's manifest expectations; if it has its own manifest format, merge `agent.json` into it.

5. **No Claude-only hooks in vibe-iterate.** vibe-iterate has no `hooks/` dir, so the hook-mechanism gap didn't bite this port. **Note for siblings:** any plugin with PreToolUse/PostToolUse/SessionStart hooks will hit this — Antigravity's event/automation model needs verification before porting hook-bearing plugins (e.g., anything using SessionEnd for cleanup or PreToolUse for guardrails).

## Reusable checklist for the next port

- [ ] Inventory source skills; tag each user-invocable vs internal.
- [ ] Identify the `guide` (or equivalent shared-behavior skill); split always-on → AGENTS.md, situational → keep skill.
- [ ] Create `.agent/workflows/`, `.agent/skills/`, `AGENTS.md`, `.agent/agent.json`.
- [ ] Port user-invocable skills → workflows (frontmatter swap + cross-ref rewire).
- [ ] Port internal skills → skills (path repoint + caller-naming note).
- [ ] Copy schemas/fixtures verbatim into the guide skill.
- [ ] Repoint all paths (`~/.claude/...` → `~/.gemini/antigravity/...`, `CLAUDE.md` → `AGENTS.md`, `plugin.json` → `.agent/agent.json`).
- [ ] Repoint `~/.claude/profiles/builder.json` → `~/.gemini/profiles/builder.json` **if the plugin uses it** (vibe-iterate didn't; vibe-cartographer does).
- [ ] Rewire cross-refs: guide-intro lines, sibling links, `:sidecar` → `/sidecar`, `/plugin:cmd` → `/cmd`.
- [ ] Grep for leftovers: `../guide`, `../session-logger`, `/plugin:`, `~/.claude`, `CLAUDE_PLUGIN_ROOT`, `:sidecar`, `available-skills list`.
- [ ] Update self-edit targets in any `evolve-*` workflow.
- [ ] Write README.md (install/use) + append this plugin's specifics to the cookbook.
- [ ] Re-check open questions 1-5 against the plugin's actual feature set (does it schedule? does it call sidecars silently? does it have hooks?).
