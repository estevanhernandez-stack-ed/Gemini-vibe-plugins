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

## Validated live (2026-05-24, Celestia3)

The pilot was installed and run in a real Antigravity 2.0 instance on the Celestia3 project. Confirmed:

- **Directory convention is `.agent/` (singular).** Antigravity's own agent wrote `.agent/workflows/`, `.agent/skills/`, `.agent/agent.json`. The `.agent` vs `.agents` doc ambiguity is settled — use `.agent/`.
- **Install UX is agentic.** Handing Antigravity the repo URL and asking it to set up the plugin is the canonical install: it `git clone`s the port, copies `.agent/*` into the target project, and **appends** the port's `AGENTS.md` rules into the project's existing `AGENTS.md` (non-destructive — it read the project's CLAUDE.md/AGENTS.md first), then deletes the temp clone. No manual file shuffling needed.
- **AGENTS.md is merge-append, not standalone.** The port's AGENTS.md content becomes an addition to the project's ruleset. (Cookbook implication: keep each port's AGENTS.md self-contained and append-safe — no assumptions about being the only rules.)
- **Project-local state carries over.** The existing `.vibe-iterate/config.json` (framework pins) + `atlas.jsonl` from the Claude Code side were preserved and reused by the port untouched. The project-local data layer is portable as-is; only the home-dir self-evolution logs repoint (`~/.claude/...` → `~/.gemini/antigravity/...`).
- **Full plugin loaded, behaving normally.** All 13 workflows + 3 skills installed; modes run.

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

---

# Port log

Per-port notes appended as the pipeline runs the rest of the family. Each entry: what was mechanical vs needed thought THIS port, the edge resolutions, and any PORT-RUNNER.md gap hit.

## vibe-walk@0.1.0 (ported 2026-05-24)

**Shape:** 9 source skills → **6 workflows + 3 skills** + AGENTS.md + agent.json + carried scripts.

| Source skill | Source self-label | Port target | Why |
|---|---|---|---|
| `vibe-walk` (bare router) | user-invocable | **workflow** `/vibe-walk` | User types it |
| `bootstrap` | "Internal SKILL … directly when user says /bootstrap" | **workflow** `/bootstrap` | Real slash trigger — the canonical bootstrap edge (trust the trigger over the "internal" label) |
| `discover` | description = "Phase 1 autonomous discovery…" (no /slash phrasing) | **workflow** `/discover` | **Reclassified — see edge below** |
| `walk` | description = "Phase 1.5 interview gates…" (no /slash phrasing) | **workflow** `/walk` | **Reclassified — see edge below** |
| `vitals` | user-invocable | **workflow** `/vitals` | Structural self-test, user-typed |
| `evolve-walk` | user-invocable | **workflow** `/evolve-walk` | L3 self-evolution, user-typed |
| `guide` | shared-behavior, never invoked | **split** → `AGENTS.md` + **skill** `.agent/skills/guide/` | See guide split |
| `session-logger` | "Internal SKILL — not a slash command" | **skill** | Loaded by commands, never typed |
| `friction-logger` | "Internal SKILL — not a slash command" | **skill** | Loaded by commands, never typed |

### The discover / walk edge (the vibe-doc-style trap, resolved)

`port.py` defaulted **discover** and **walk** to *skills* because their `description` frontmatter opens with "Phase 1 autonomous discovery…" / "Phase 1.5 interview gates…" — no "use when the user says `/x`" phrasing for the classifier to latch onto. **Both are actually user-invoked slash commands.** Evidence:

- The **router** (`vibe-walk` SKILL.md) routing table outputs `Run /vibe-walk:<step>?` and names `/vibe-walk:discover` and `/vibe-walk:walk` as the explicit next steps in a linear two-phase flow.
- Both have **H1 titles** `# /vibe-walk:discover` and `# /vibe-walk:walk` — the slash form.
- Cross-refs everywhere: "Next: `/vibe-walk:walk`", "tell the builder to run `/vibe-walk:discover` first", "re-run `/vibe-walk:walk`".

This is exactly the case the cookbook warns about: a real entry point whose *description* is written as a capability blurb, not a trigger sentence. **Lesson reinforced:** classify on the router's hand-off targets + H1 + cross-refs, not just the description's opening phrasing. Both reclassified to `.agent/workflows/` with frontmatter swapped (`name` dropped, `description` rewritten to "Run when the user says `/discover`…").

### Mechanical (port.py got it right)

- Frontmatter swap on the 4 it correctly called workflows; path repoints (`~/.claude/...` → `~/.gemini/antigravity/...`, 8 data-path hits); `/vibe-walk:cmd` → `/cmd` (27 namespace repoints, including inside discover/walk bodies — so when reclassified they were already de-namespaced); "command start/end" → "workflow start/end"; agent.json minted from plugin.json.

### Needed thought (the 20%)

- **The discover/walk reclassification** (above) — the headline judgment call this port.
- **The guide split.** Folded `sherpa-persona.md` + `posture.md` into AGENTS.md prose (always-on), **deleted them from the guide skill**; kept `conventions.md` (D1–D6 build constraints) + `friction-triggers.md` (trigger map) as situational skill-side files. Guide SKILL.md rewritten to a thin index.
- **Relative-path direction after the move.** Workflows can't use `../guide/...` (resolves to `.agent/workflows/guide/`, which doesn't exist). Every workflow uses the root-absolute `.agent/skills/guide/...` form; only sibling **skills** keep `../guide/...`. Caught a leftover `../guide` in vitals' cross-refs that the move exposed.
- **vitals' structural self-test had to be re-modeled for the port layout.** Source vitals checked "nine SKILL dirs under `plugins/vibe-walk/skills/`" + read `plugin.json`. Rewrote it to check 6 workflows + 3 skills under `.agent/`, read `.agent/agent.json`, the 2 surviving guide refs (not 4), and 4 build scripts (source listed 3 but `emit_trigger_wiring.py` exists). This is the first ported plugin with its own self-test — the self-test itself is a port surface.
- **evolve-walk self-edit targets.** Added an explicit target-mapping block so proposals name the real port file (command behavior → `.agent/workflows/<cmd>.md`; persona/rules → `AGENTS.md`; conventions/triggers → guide-skill refs; helpers → `.agent/scripts/...`). Not a blind replace — discover/walk flipping to workflows changes their target dir.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** `/discover --refresh` is a manual user re-run, not a scheduled job. vibe-walk has zero `schedule`-plugin dependency (cleaner than vibe-iterate, whose weekly radar needed it).
2. **`--silent` sidecar calls:** **None.** Linear flow (router → discover → walk), no sidecars returning structured data silently. Nothing to preserve here.
3. **Workflow name collisions:** **RESOLVED — plugin-prefix namespacing.** Bare `/bootstrap` collided with vibe-iterate's `/bootstrap`; `/discover`, `/walk`, `/vitals`, `/evolve-walk` were generic and unidentifiable in Antigravity's flat slash list once a second port was installed. The standing convention (decided once, applied across the whole family, baked into `port.py`): router stays `/<plugin>`; every other workflow → `/<plugin>-<cmd>`; `evolve-*` collapses to `/<plugin>-evolve`; skills → `<plugin>-<skill>` (dir + frontmatter `name`). So `/discover` → `/vibe-walk-discover`, `/evolve-walk` → `/vibe-walk-evolve`. See `tools/PORT-RUNNER.md` step 6.5 for the full rule + the careful ref-rewrite (word-boundary-aware, longest-first, identity-only for single-token skill names, sibling-plugin refs untouched).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.1.0` for the loggers' audit field. Same unverified-bookkeeping status as vibe-iterate.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key in plugin.json. No builder-profile usage either (no `~/.claude/profiles/builder.json`), so no profile repoint needed.

### PORT-RUNNER.md gaps hit this port

1. **Scripts are not addressed by the playbook.** vibe-walk is the **first script-bearing plugin** in the pipeline — it carries 8 helper scripts (Python discovery/build + a jscodeshift codemod). `port.py` did **not** copy them (the report listed zero `files_copied_verbatim`), and PORT-RUNNER.md has no step for "carry the scripts dir + repoint `${plugin}/scripts/...` body refs → `.agent/scripts/...`." I improvised: copied `scripts/` → `.agent/scripts/` (dropping `__pycache__` + `__tests__` dev artifacts), repointed the cross-ref pointers and the jscodeshift CLI path, and documented the script location in AGENTS.md + the guide skill. **The bare Python imports** (`from discovery.inventory_surfaces import inventory`) were left as-is (faithful to source); they assume `.agent/scripts/` on `sys.path`. **Recommend:** add a PORT-RUNNER step 11 — "Carry `scripts/` → `.agent/scripts/`; repoint `${plugin}/scripts/...` and `../../scripts/...` body refs; note the sys.path assumption for bare imports." And add `scripts` carry to the reusable checklist.
2. **The self-test is its own port surface.** PORT-RUNNER.md doesn't call out that a `vitals`-style structural self-test hardcodes the *source* layout and must be re-modeled for the port. vibe-iterate had no vitals so this never surfaced. **Recommend:** a one-line note under step 7 — "if the plugin has a structural self-test (vitals/doctor), re-model its checks for the `.agent/` layout; it's the one workflow that asserts the directory shape."
3. **Minor:** the inventory-surfaces script reads the host app's orientation docs and scans for `CLAUDE.md` (a host-app file, not a port artifact). Left unchanged — it's reading the *target app*, not the plugin. An Antigravity-aware enhancement would also scan `AGENTS.md`, but that's a behavior change, out of scope for a faithful port. Noted, not done.

Otherwise PORT-RUNNER.md carried the rest cleanly — the guide split, edge-confirmation, guide-intro rewrites, evolve self-edit targets, and the open-questions re-check all mapped to existing steps.
