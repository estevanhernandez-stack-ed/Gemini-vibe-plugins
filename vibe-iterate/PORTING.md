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

## vibe-keystone@0.2.1 (ported 2026-05-24)

**Shape:** 2 source skills → **2 workflows + 0 skills** + AGENTS.md + agent.json. The minimal plugin shape in the family — no `guide` skill, no loggers, no scripts. Keystone is a once-per-repo generator, so it carries only opt-in capture (Tier 0) + reflective proposal (Tier 1), not the full session/friction/decay stack.

| Source skill | Source self-label | Port target | Why |
|---|---|---|---|
| `keystone` | description = "Bootstrap a CLAUDE.md…" + lists `/keystone` trigger, no "use when the user says" phrasing for the classifier to latch onto | **workflow** `/vibe-keystone` (the **router**) | **Reclassified — see the eponymous-command edge below.** It IS the plugin's primary user-invoked command. |
| `evolve-keystone` | user-invocable (`/vibe-keystone:evolve-keystone`) | **workflow** `/vibe-keystone-evolve` | L1 self-evolution, user-typed. port.py classified this correctly. |

### The eponymous-command edge (the headline call this port)

`port.py` defaulted **keystone** to a *skill* named `vibe-keystone-keystone` ("no real slash trigger or user-says phrasing — defaulted to skill"). That's wrong twice over:

1. **It's user-invoked.** The source description lists `/keystone` and trigger phrases ("set up CLAUDE.md", "bootstrap claude md"); the H1 is `# Keystone — bootstrap…`; the README opens "You type `/keystone`…". It's an entry point, not loaded-by-something-else. → workflow, not skill.
2. **It's the eponymous main command** — its name equals the plugin name. The namespacing convention (step 6.5) collapses this to the **bare router form** `/<plugin>` (file `vibe-keystone.md` → `/vibe-keystone`), **not** `/<plugin>-<cmd>` which would yield the absurd doubled `/vibe-keystone-keystone`. So the resolution is: promote the skill `.agent/skills/vibe-keystone-keystone/` → workflow `.agent/workflows/vibe-keystone.md`, swap frontmatter (drop `name`, `description`-only), and delete the now-empty `skills/` dir.

**Lesson (new):** when the source plugin has a skill whose name == the plugin name AND it's user-invoked, it ports to the **router** `/<plugin>` — never `/<plugin>-<plugin>`. `port.py`'s `<plugin>-<skill>` skill-namespacing rule produces the doubled form for the eponymous case; catch it in the finishing pass. (Distinct from vibe-iterate/vibe-walk, where the bare router was already its own separate source skill the classifier saw as user-invocable.)

### The CLAUDE.md → AGENTS.md meta-adaptation (keystone's whole job)

Every other port repoints `CLAUDE.md → AGENTS.md` as plumbing (a path in a logger, a rules-file reference). **For keystone, that repoint IS the product.** Keystone *bootstraps the project rules file* — on Claude Code that's `CLAUDE.md`; in the Antigravity port the file it writes must be `AGENTS.md`. port.py did 23 string repoints (`CLAUDE.md` → `AGENTS.md` across the skeleton, the interview, the self-check, the quick-reference) and left 3 leftover `CLAUDE.md` hits in the skill description's trigger phrases.

The finishing-pass judgment: verify the framing reads **semantically** right end-to-end, not just that the strings flipped. The workflow now produces an `AGENTS.md` ("the load-bearing structural file every agent decision rests on" = AGENTS.md); the repo-type adaptation, the tenant interview, and the skeleton all target AGENTS.md. **Kept CLAUDE.md mentions deliberately** in three places where they're *cross-tool context*, not output targets: (a) a tooling note in the workflow ("the Claude Code original wrote CLAUDE.md; you may *read* a CLAUDE.md for context, but write AGENTS.md"); (b) the agent.json provenance line; (c) the README adaptation table. The OUTPUT contract is unambiguously AGENTS.md. Half-CLAUDE/half-AGENTS phrasing (e.g. "produce a CLAUDE.md following the project-CLAUDE pattern") was the trap — rewrote those to "produce an AGENTS.md following the project-rules pattern."

**Lesson (new):** a plugin whose *purpose* is generating the rules file makes the rules-file repoint a content rewrite, not a string swap. Read the whole body for output-vs-context: the file it WRITES must be the target tool's rules file; the file it may READ can stay the source tool's. Don't let the title/skeleton keep saying "CLAUDE.md" while the output flips.

### The no-guide / no-loggers minimal shape

Keystone has no `guide` skill, no session-logger, no friction-logger, no scripts, no persona/posture reference docs. PORT-RUNNER steps 1–2 (synthesize AGENTS.md from guide references; do the guide split) and the logger-related verifications **have no source material**. The skeleton AGENTS.md port.py wrote was all-TODO with "(no guide skill detected — supply persona/posture by hand)" markers.

**AGENTS.md decision: minimal, not omitted.** There's no persona to invent and no shared posture layer — so I did NOT manufacture one. But two genuinely always-on facts justify a lean AGENTS.md over omission: (1) the rules-file meta-fact (this plugin's OUTPUT is `AGENTS.md`, never `CLAUDE.md` — load-bearing for correctness), and (2) the no-telemetry / no-scripts / capture-log-location hard rules that both workflows share. The result is a ~60-line AGENTS.md: "what this plugin does", workflows list, hard rules, the opt-in-capture framing + log repoint, and a voice paragraph. Append-safe, no invented persona.

**Lesson (new):** "no guide skill" ≠ "no AGENTS.md." Even a guide-less plugin can have always-on facts (output contract, hard rules, log path) worth a minimal AGENTS.md. The bar is *is anything true for every run of this plugin?* — if yes, fold it; if there's genuinely nothing always-on, omit. For keystone, the output-is-AGENTS.md fact alone earns the file.

### Mechanical (port.py got it right)

- The 23 `CLAUDE.md` → `AGENTS.md` skeleton repoints; the `~/.claude/...` → `~/.gemini/antigravity/...` data-path + global-config repoints (5 claude-home, 2 data-path); `/vibe-keystone:evolve-keystone` → `/vibe-keystone-evolve`; agent.json minted from plugin.json; evolve-keystone correctly classified as a workflow.

### Needed thought (the 20%)

- **The eponymous-command → router reclassification** (above) — the headline call.
- **The CLAUDE.md → AGENTS.md semantic verification** (above) — output-vs-context judgment, not a string swap.
- **The minimal-AGENTS.md decision** (above) — fold the always-on facts, invent no persona.
- **evolve-keystone self-edit targets.** Source proposals named `plugins/vibe-keystone/skills/keystone/SKILL.md` as the file to edit. Because `keystone` flipped to the **router workflow**, every self-edit target repointed to `.agent/workflows/vibe-keystone.md` (Before-You-Start read target, the proposal-location reference, and the "never edit" hard constraint). Classic skill→workflow target flip — not a blind replace.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** Keystone is a one-shot generator. No `schedule` dependency.
2. **`--silent` sidecar calls:** **None.** Two independent workflows; no sidecar returning structured data.
3. **Workflow name collisions:** **RESOLVED — namespacing.** `/vibe-keystone` (router, bare) + `/vibe-keystone-evolve`. The eponymous case is exactly why the router stays `/<plugin>` and doesn't become `/<plugin>-<plugin>`.
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.2.1` for the (absent) loggers' audit field — bookkeeping only; keystone has no loggers that read it, but kept for family consistency.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key in plugin.json. **Builder-profile note:** PRIVACY.md says keystone reads `~/.claude/profiles/builder.json`, but the **skill bodies do not** — the interview asks the user to *name* tenant-doc paths rather than auto-reading the global profile. So there's no active `builder.json` read to repoint; the global-config references in the workflow (a global rules file the user may name) were generalized, not hard-pinned to a `~/.gemini/profiles/builder.json` path. No functional profile repoint required.

### PORT-RUNNER.md gaps hit this port

1. **No guidance for the eponymous-command → router case.** PORT-RUNNER step 3 (edge classifications) covers "skill defaulted to `skill` but has a hidden entry point → move to workflows" — but doesn't name the sub-case where that skill's name == the plugin name, which forces the **router** target `/<plugin>` (not `/<plugin>-<cmd>`, and definitely not the doubled `/<plugin>-<plugin>` that `port.py`'s skill-namespacing produces). **Recommend:** add to step 3 / step 6.5 — "If the reclassified skill's name equals the plugin name, its workflow target is the bare router `<plugin>.md` → `/<plugin>`. Delete the `<plugin>-<plugin>` skill dir port.py minted; do not ship the doubled slash."
2. **No guidance for the rules-file-generator plugin (output-vs-context CLAUDE.md).** PORT-RUNNER step 9's leftover-grep lists `CLAUDE.md` as a thing to drive toward zero — but for a plugin whose *output* is the rules file, some `CLAUDE.md` mentions are **intentional cross-tool context** (the file it may READ) while the OUTPUT must be `AGENTS.md`. A blind "kill all CLAUDE.md" would break the meta-explanation. **Recommend:** a note under step 9 — "For a rules-file generator (keystone), distinguish output target (must be `AGENTS.md`) from cross-tool context (a `CLAUDE.md` it may read / mention for provenance). Verify the *output contract* semantically; not every `CLAUDE.md` hit is a miss."
3. **PORT-RUNNER step 1 assumes a guide skill exists** ("The script writes an AGENTS.md skeleton with TODO markers and hints naming the source guide reference docs"). For a no-guide plugin the skeleton is all-TODO with "no guide skill detected" markers, and steps 1–2 have no source material. The playbook doesn't say what to do when there's no guide: omit AGENTS.md, or write a minimal one? **Recommend:** a note under step 1 — "No guide skill ≠ no AGENTS.md. Fold any always-on facts the plugin has (output contract, hard rules, log path); invent no persona. Omit AGENTS.md only if genuinely nothing is always-on."
4. **Path note (not a content gap):** the task brief and step 10 say append to `tools/PORTING.md`, but the canonical cookbook is `vibe-iterate/PORTING.md` (where vibe-walk's entry lives, and what PORT-RUNNER.md's header points to as the authority). There is no `tools/PORTING.md`. Appended here to keep one cookbook. **Recommend:** PORT-RUNNER step 10 should name the cookbook path explicitly (`vibe-iterate/PORTING.md`) to avoid the ambiguity.

Otherwise PORT-RUNNER.md carried the rest cleanly — the edge-confirmation discipline, the evolve self-edit-target retargeting, the namespacing verification, and the open-questions re-check all mapped to existing steps. The guide-split steps (1, 2, 4, 5) and the script-carry / self-test gaps from vibe-walk simply didn't apply (no guide, no scripts, no vitals).

## vibe-doc@0.8.0 (ported 2026-05-24)

**Shape:** the **first port with a `commands/` dir.** Source = 5 commands (`scan`, `generate`, `check`, `evolve-doc`, `status`) + 7 skills (`scan`, `generate`, `check`, `evolve-doc`, `friction-logger`, `guide`, `session-logger`) → **5 workflows + 3 skills** + AGENTS.md + agent.json. This port surfaced a new mapping pattern AND a `port.py` gap, and it's the **first port to actually USE the `builder.json` repoint**.

### The headline new lesson: thin-command-wrapper → merged workflow

vibe-doc's `commands/*.md` are **thin slash-entry wrappers** that delegate to a parallel skill. `commands/scan.md` is four lines — `description: Scan your project for documentation gaps` + "read `${CLAUDE_PLUGIN_ROOT}/skills/scan/SKILL.md` and follow it." The COMMAND is the slash identity + clean one-line summary; the SKILL holds the real implementation (and its own "use when the user mentions 'scan'…" semantic trigger).

**`port.py` processed only `skills/` and IGNORED `commands/`** — so it (a) emitted scan/generate/check as **skills** (wrong — they're user-typed slash entries; their skill descriptions read as semantic-load phrasing, which the classifier mapped to `skill`), and (b) **dropped the commands entirely**, so `status` (command-only, no parallel skill) **vanished**.

**The correct mapping — merge each command with its parallel skill into ONE workflow:**

| Source | Source kind | Port target | Why |
|---|---|---|---|
| `scan` (cmd + skill) | thin wrapper + impl skill | **workflow** `/vibe-doc-scan` | command → slash + `description`; skill body → workflow body. Standalone skill dropped. |
| `generate` (cmd + skill) | thin wrapper + impl skill | **workflow** `/vibe-doc-generate` | same merge. |
| `check` (cmd + skill) | thin wrapper + impl skill | **workflow** `/vibe-doc-check` | same merge. The command's extra framing ("suggest running `/generate` if stale") folded into the workflow body. |
| `evolve-doc` (cmd + skill) | thin wrapper + impl skill | **workflow** `/vibe-doc-evolve` | already a workflow in the skeleton; reconciled the command's clean `description`, verified the implementation carried, retargeted self-edit targets. |
| `status` (command-ONLY) | thin command, no skill | **workflow** `/vibe-doc-status` | body = the command's `npx vibe-doc status` logic. **Rebuilt from `commands/status.md`** — port.py had dropped it. |
| `guide` | shared-behavior skill | **split** → `AGENTS.md` + **skill** `vibe-doc-guide` | see guide split. |
| `session-logger`, `friction-logger` | internal skills | **skills** `vibe-doc-{session,friction}-logger` | loaded, never typed. |

**Count: 5 workflows + 3 skills + AGENTS.md.** Deleted the mis-emitted standalone `vibe-doc-scan`/`-generate`/`-check` skill dirs after merging their bodies into the workflows.

**Lesson (new, headline):** when a plugin has BOTH `commands/` and `skills/`, the command is the user-facing surface — the merged result is **always a workflow**, regardless of how the skill's own `description` reads. The merge uses the command's clean one-line `description` as the workflow summary and the skill's body as the implementation. Discard the skill's verbose "this skill should be used when…" blurb. A command-only command (no parallel skill) is still a workflow — its body IS the implementation.

### The `port.py` `commands/` enhancement (the big fix)

Taught `port.py` the pattern so sec/test (likely the same shape) port mechanically:

- **`collect_commands(src)`** reads `commands/*.md` when the dir exists.
- **`merge_commands_and_skills(skills, commands, plugin)`** reconciles: command + same-named skill → mark the skill a **workflow** (`merged_from_command`), command's `description` wins, skill body stays as the workflow body, standalone skill dropped; command-only → synthesize a **workflow** from the command body (`command_only`); skill-only → classify as usual. Runs **before** the namespacing map is computed, so the merged/command-only workflows get `/<plugin>-<cmd>` names automatically.
- Report gained a **`commands_merged`** block (`commands_found`, `merged_with_skill`, `command_only_workflows`) + a finishing-pass TODO.
- **Defensive carry:** a *merged* skill that ALSO had `references/`/`schemas/` would lose them in the single-file workflow branch — so the script carries them into a companion `.agent/skills/<name>/` dir and flags it. No plugin hit this (scan/generate/check have no sub-dirs), but sec/test might.
- Re-running the enhanced script on vibe-doc now emits **5 workflows + 3 skills** mechanically (verified). Documented as **PORT-RUNNER.md step 2b**.

### builder.json — first port to USE it

vibe-doc is the **first port where the `~/.claude/profiles/builder.json` → `~/.gemini/profiles/builder.json` repoint is load-bearing** (vibe-iterate/walk had no global profile; keystone names tenant paths but doesn't auto-read it). `/vibe-doc-scan` and `/vibe-doc-generate` **write** `plugins.vibe-doc.*` (read-merge-write, only if the file exists); the guide + `/vibe-doc-evolve` **read** it. port.py did 16 repoints. The finishing pass folded the read-merge-write ownership rules (shared = read-only, plugin-scoped = vibe-doc-owned, never-create, always-merge) into AGENTS.md as an always-on rule, and left the detailed plugin-scoped field list there too — it's a hard contract every workflow that touches the profile must honor.

### CLAUDE.md-as-content (keystone's lesson, applied again)

vibe-doc *reads and generates documentation* — and `CLAUDE.md`/`AGENTS.md` are themselves doc artifacts it handles. Same output-vs-context split as keystone: where `CLAUDE.md` meant **this project's rules file** (a source it reads for context in the generate hint table / ADR+readme source lists, or the confidence-attribution example), repointed to **`AGENTS.md`** (port.py did 8 claude-md repoints). Where it's a **classification signal for a HOST app** — the `skill-command-reference` generator scanning `commands/*.md` + `skills/*/SKILL.md`, the classification-taxonomy listing `.claude-plugin/marketplace.json` as a multi-plugin-repo signal — **kept as content** (vibe-doc documents whatever shape the target app has). Added an explicit AGENTS.md section spelling out the distinction so a future "kill all CLAUDE.md" pass doesn't break the meta-explanation.

### Mechanical (port.py got it right — after the enhancement)

- The command/skill merge into 5 workflows + 3 skills (post-fix). Frontmatter swap on evolve; path repoints (13 data-path, 16 builder-profile, 8 claude-md, 5 plugin-json); `/vibe-doc:evolve-doc` → `/vibe-doc-evolve` (4 namespaced-slash); "command start/end" → "workflow start/end" (9); agent.json minted from plugin.json (version 0.8.0).

### Needed thought (the 20%)

- **The command merge** (above) — the headline judgment call AND the port.py fix.
- **status, the command-only case** — rebuilt the workflow body from `commands/status.md` (port.py had dropped it pre-fix). It's a thin reporting surface over `npx vibe-doc status`; documented in the workflow that there is no parallel skill to merge — the workflow IS the implementation.
- **The guide split.** vibe-doc's always-on layer is tone/persona-adaptability/posture + the **unified-profile read-merge-write rules** + the **Pattern #13 composition posture** + hard rules → folded into AGENTS.md prose. The situational detail kept skill-side: the project-state schema, CLI patterns, output-format standards, the persona **table**, the complement **table** + live-discovery heuristics, and the classification-taxonomy / documentation-matrix / breadcrumb-heuristics / friction-triggers references + JSON schemas. Rewrote `vibe-doc-guide/SKILL.md` from a ~320-line full guide to a thin index pointing at AGENTS.md + the kept files. (port.py's verbatim copy left stale `~/.claude` and `CLAUDE.md` strings inside the schema/reference files — hand-fixed: 2 schema-description data-paths, 1 schema `/evolve-doc` ref, the friction-triggers section headings `/scan` → `/vibe-doc-scan`, and a fistful of "command SKILL" prose → "workflow".)
- **evolve-doc self-edit targets.** Added a target-mapping block: command-behavior edits → `.agent/workflows/vibe-doc-{scan,generate,check,status}.md` (the merge flipped scan/generate/check from skills to workflows); shared behavior → the guide skill / AGENTS.md; **classifier/scoring/state-schema/matrix code → the CLI source repo** (`src/classifier/*.ts`, `src/state/schema.ts`), which is NOT ported into `.agent/` (deterministic CLI code) — so those proposals ship on the next CLI publish, not as `.agent/` edits. Classic skill→workflow target flip plus a port-doesn't-carry-CLI-source nuance.
- **CLI-binary mis-repoint caught.** port.py's namespacing rewrote the **CLI binary name** `npx vibe-doc check` → `npx vibe-doc-check` in one spot (the check skill's exit-code table). The CLI binary is `vibe-doc`, not `vibe-doc-check` — fixed by hand. (The slash command is `/vibe-doc-check`; the CLI subcommand stays `vibe-doc check`. A word-boundary edge the namespacer should ideally exclude `npx vibe-doc <sub>` from — noted as a PORT-RUNNER watch-item.)

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** The only `schedule`/`cron` hits are classification-taxonomy content (how to detect data-pipeline host apps) and a "scheduled check (weekly reminder)" doc *example*. No `schedule`-plugin dependency.
2. **`--silent` sidecar calls:** **None.** The "silent" hits are all the loggers' defensive-default "exit silently" semantics — not sub-workflow calls returning structured data. No sidecar pattern.
3. **Workflow name collisions:** **RESOLVED — namespacing.** 5 distinct `/vibe-doc-*` names; no eponymous router case here (the plugin's main verb is `scan`, not `vibe-doc`, so there's no bare `/vibe-doc` router — every workflow is `/vibe-doc-<cmd>`).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.8.0`, read by both loggers for the audit field. Same bookkeeping status as the siblings.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key in plugin.json. **builder-profile: YES, load-bearing** (first port to use it — see above).

### PORT-RUNNER.md gaps hit this port

1. **No guidance for the `commands/` dir at all** — the big one. PORT-RUNNER had no step for "a plugin with both commands/ and skills/." **Fixed:** added **step 2b (the command merge)** with the merge table, the why-this-was-wrong note, and the verify checklist; updated step 0's sanity-check math (`workflows + skills` = skills + command-only-commands, since pairs merge); taught `port.py` to do it automatically.
2. **CLI-binary vs slash-command namespacing collision.** The namespacer rewrote `npx vibe-doc check` → `npx vibe-doc-check`. **Recommend:** a PORT-RUNNER watch-item under step 6.5 / step 7 — "the namespacer rewrites slash names AND can catch a CLI subcommand that shares the command word (`npx <plugin> <cmd>`); verify CLI invocations kept the `<plugin> <subcommand>` two-token form." (Low frequency; one hit this port.)
3. **port.py's verbatim copy leaves stale strings inside schemas/reference files.** The guide's `schemas/*.json` and `references/*.md` carried `~/.claude/...` and `CLAUDE.md` / `.claude-plugin/plugin.json` in description strings and prose. port.py transforms `references/*.md` prose but **`schemas/*.json` are copied byte-for-byte** (correct for data, but the human-readable `description` fields inside them still need repointing). **Recommend:** step 9's leftover-grep already catches these — just call out that schema `description` strings are a known straggler source for any logger-bearing plugin.

4. **Helper scripts ARE load-bearing here (the vibe-walk gap, hit again).** The loggers call `node scripts/atomic-append-jsonl.js` (atomic session/friction appends) and the evolve profile-write calls `node scripts/atomic-write-json.js` — both ship in the source plugin's `scripts/` dir. **port.py did NOT carry them** (its `files_copied_verbatim` listed only the guide schemas — same gap vibe-walk flagged). Without them the loggers can't do atomic writes. **Hand-fix:** carried `atomic-append-jsonl.js` + `atomic-write-json.js` → `.agent/scripts/` (dropped `copy-templates.js`/`postinstall.js` — those are npm-install/CLI artifacts, not workflow helpers), repointed every body ref `scripts/atomic-*.js` → `.agent/scripts/atomic-*.js` (root-absolute, as node invocations run from the workspace root, not relative to the skill dir), and documented the script location in AGENTS.md. **Recommend (reinforces vibe-walk's gap #1):** `port.py` should detect a top-level `scripts/` dir, carry the workflow-referenced helpers into `.agent/scripts/`, and repoint `scripts/...` body refs. This is now the second port to need it — promote it from "improvise" to a real step.

Otherwise PORT-RUNNER.md carried the rest cleanly — the guide split, edge-confirmation, evolve self-edit retargeting, the namespacing verification, and the open-questions re-check all mapped to existing steps. No vitals self-test to re-model.

## vibe-sec@0.6.0 (ported 2026-05-24)

**Shape:** the **second port with a `commands/` dir** — and the one that proves the vibe-doc lesson generalized. Source = 9 commands (`audit`, `deps`, `fix`, `gate`, `posture`, `research`, `scan`, `threat-model`, `vibe-sec`) + 10 skills (the 9 command-parallel implementations + `guide`) → **9 workflows + 1 skill** (`vibe-sec-guide`) + AGENTS.md + agent.json. No loggers, no evolve, no hooks, no scripts.

### The headline: the commands+skills merge is now MECHANICAL

This is the first port where the thin-command-wrapper → merged-workflow pattern ran **fully mechanically** — `port.py` (taught by the vibe-doc port) merged all 9 command+skill pairs into 9 workflows with **zero hand-reclassification.** The report's `commands_merged` block shows all 9 in `merged_with_skill`, `command_only_workflows: []`, and the `vibe-sec` eponymous pair correctly collapsed to the bare router `/vibe-sec` (not the doubled `/vibe-sec-vibe-sec` — the namespacing rule that bit keystone's eponymous case was already baked in). Spot-checked `audit`, `scan`, `posture`, the router: each workflow's `description` is the **command's** clean one-liner (not the skill's verbose "use when the user says…" blurb), each body is the **skill's** full implementation (not the command's "read the SKILL" delegation line), and the standalone skill dirs for the 9 merged ones were dropped (only `vibe-sec-guide` survives). **Lesson confirmed:** the vibe-doc `commands/` fix is the standing answer for this shape — sec validated it on a 9-pair plugin with no manual merge work. The judgment 20% this port was the guide split + the AGENTS.md synthesis, not the merge.

### The minimal-internal shape (no loggers, no evolve)

vibe-sec is **not self-evolving** — no `session-logger`, no `friction-logger`, no `evolve-sec` skill, no `hooks/` dir, no `scripts/` dir. The only non-workflow surface is the lone `guide` skill. So the logger-related PORT-RUNNER verifications (step 8 #4 `plugin_version` audit-field consumers, the friction-trigger-map keep-as-file, the script-carry gap that bit vibe-walk + vibe-doc) **had no source material** — cleaner than vibe-doc's logger-bearing shape. `agent.json` still mirrors version `0.6.0` for family consistency, but nothing reads it here. This is the second minimal-ish shape in the family (keystone was the first, at 2 workflows + 0 skills); sec is "rich command surface, thin internal layer."

### The guide split — source guide is lean, the heavy detail is in TypeScript

vibe-sec's `guide` skill was already lean (~88 lines, no `references/` dir, no `schemas/*.json` files). port.py wrote an **all-TODO AGENTS.md skeleton** with "(no matching reference doc detected)" markers — because the always-on content lives in the single guide SKILL **body**, not in separate reference docs the skeleton-builder scans for. Hand-synthesis: folded the always-on layer into AGENTS.md prose — the Sec positioning, the defer-when-present posture, the tier→ASVS table, the severity amplifier (the hard rule), the four-band report stance, the OWASP-Top-10 honest-coverage breakdown, the hard rules (the non-negotiable safety line, the `--auto` closed allowlist, mask-always, read-never-writes, the byte-reproducible gate), and the voice. **The situational detail that "stays skill-side" is unusual for this plugin: it's not markdown files, it's the deterministic TypeScript source** (`src/orchestration/tool-registry.ts`, `src/types.ts`, `src/report/bands.ts`, `src/scoring/*`, `src/fix/*`, `src/gate/run-gate.ts`). So the rewritten `vibe-sec-guide/SKILL.md` is a thin **index that names where each shape lives in the source repo** — there are no schemas/fixtures to keep as files, because the schemas are TS types the workflows orchestrate over, not ported markdown. Guide SKILL.md went from the full ~88-line shared-behavior doc to a ~45-line situational index.

**Lesson (new):** when a plugin's "deep reference detail" is its deterministic source code (not `schemas/*.json` + `references/*.md`), the guide skill becomes a **pointer index to the source repo**, not a carrier of kept files. The always-on/situational split still holds; the situational half just isn't ported into `.agent/` — it ships with the npm CLI. (vibe-doc had this for its classifier/state-schema TS too, but sec is the first port where the guide skill is *entirely* index, with zero kept data files.)

### Sidecar composition (open question #2) — the live answer for sec: state-file mediated, NOT `--silent`

The brief flagged open-question #2 (workflow-to-workflow `--silent` composition) as the live one for sec, on the theory that `/vibe-sec-audit` calls `:scan`/`:deps`/etc. as silent sub-workflows. **It does not.** Verified by reading every source skill body: there is **no `--silent` anywhere** in vibe-sec, and the composition is **shared-state-file mediated**, not sub-workflow invocation:

- `/vibe-sec-audit` orchestrates over the **TypeScript detectors directly** (`buildBandedReport`, `appendFindings`, `writeAuditState`) — it does NOT invoke `/vibe-sec-scan` or `/vibe-sec-deps` as sub-runs. It writes `findings.jsonl` + `audit.json`.
- `/vibe-sec-gate`, `/vibe-sec-posture`, and `/vibe-sec-threat-model` **consume** the cached `findings.jsonl` + `audit.json` that audit wrote — they explicitly never re-scan.
- The `:audit` / `:deps` / `:scan` cross-references in the bodies (the 11 sidecar-backtick repoints port.py landed, e.g. ``run `/vibe-sec-audit` for the full pass``, ``` `/vibe-sec-deps` is the fast path ```) are **user-facing recommendations**, not internal silent calls. All 11 landed as `/vibe-sec-<x>` correctly.

So Antigravity's unverified workflow-compose semantics **do not bite this port** — there's nothing silent to verify. The composition is portable precisely because the state files are portable (the live Celestia3 validation already proved `.vibe-*/state/` carries over untouched). Documented in AGENTS.md § Composition and the README. **Lesson (new):** "does it call sidecars silently?" has two distinct architectures — vibe-iterate's in-turn silent skill calls (the genuinely-unverified case) vs vibe-sec's state-file handoff (portable, no compose-semantics dependency). Read the bodies for `--silent` + "consume the structured output, don't render"; if instead the pattern is "writer writes a state file, readers read it," open-question #2 is a non-issue.

### builder.json + CLI-vs-slash watch-items

- **builder.json:** the **workflow/skill bodies do not read `~/.claude/profiles/builder.json`** — same as keystone. The Pattern #11 (Shared User Profile Bus) participation is asserted in `framework.md` (the thesis, not ported) and `docs/gap-analysis` (not ported), and the thesis names `~/.claude/plugins/data/vibe-sec/profile.json` for a Level-2 profile — but no shipped skill body actually reads either. So **no active profile read to repoint.** port.py's `repoints_applied` shows zero builder-profile hits, consistent with this. (If a future version wires the Pattern #11 read into a workflow, repoint to `~/.gemini/profiles/builder.json` then.)
- **CLI-vs-slash (the vibe-doc watch-item):** **clean — no collision.** vibe-sec's source CLI invocation is `node ${CLAUDE_PLUGIN_ROOT}/dist/cli.js` (repointed to `node .agent/dist/cli.js`), not `npx vibe-sec <subcmd>` — so there was no `npx <plugin> <cmd>` two-token form for the namespacer to mangle into `vibe-sec-<cmd>`. The only `vibe-sec <word>` two-token hits in the port are the gate's banner **verdict strings** (`vibe-sec gate FAIL`, `vibe-sec gate PASS`) — prose, correctly left alone. The vibe-doc CLI-binary mis-repoint did **not** recur here.
- **dist/ not carried:** like vibe-doc, the deterministic CLI (`src/`, `dist/cli.js`) is NOT carried into `.agent/` — it publishes from the source repo with the npm package. Body refs to `node .agent/dist/cli.js` and `src/...` entry points name the build contract; the README + guide index say so explicitly.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** `/vibe-sec-research` cadence is friction-log-driven (Pattern #14 signal), explicitly "no hard schedule" (Conflict 8 = A). No `schedule`-plugin dependency.
2. **`--silent` sidecar calls:** **None** (see above). State-file-mediated composition; the live answer is "non-issue for sec."
3. **Workflow name collisions:** **RESOLVED — namespacing.** Router `/vibe-sec` (bare, eponymous) + 8 `/vibe-sec-<cmd>`. The eponymous pair collapsed to the router correctly (no `/vibe-sec-vibe-sec`).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.6.0` for family consistency — but vibe-sec has **no loggers** that read it. Pure bookkeeping; nothing consumes it.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key. Confirmed. No builder-profile read either (see above).

### Mechanical (port.py got it right)

- The full **9-pair commands+skills merge** into 9 workflows + 1 skill (the headline — mechanical, zero hand-fix). `description` from command, body from skill, standalone skills dropped, eponymous → router.
- Namespacing: 34 `plugin-namespaced-slash` repoints (`:audit` → `/vibe-sec-audit`, `/vibe-sec:threat-model` → `/vibe-sec-threat-model`, etc.); 11 `sidecar-backtick` repoints (all landed as `/vibe-sec-<x>`); 10 `plugin-root-generic` (`${CLAUDE_PLUGIN_ROOT}` → relative); 1 `data-path` (the guide's data-dir line). `agent.json` minted from `package.json` (0.6.0). Zero `${CLAUDE_PLUGIN_ROOT}`, zero `/vibe-sec:` colons, zero doubled prefixes left in the finished port.

### Needed thought (the 20%)

- **The AGENTS.md synthesis from a guide-SKILL body (not reference docs).** port.py's skeleton was all-TODO with "no matching reference doc detected" because sec's always-on content lives in the guide SKILL **body**, not in `references/*.md` the skeleton-builder scans. Synthesized the full always-on layer (persona/posture/tier-ASVS/amplifier/four-band/OWASP-honesty/hard-rules/voice) into AGENTS.md prose from the guide body + the audit/fix/gate/threat-model workflow bodies.
- **The guide-as-pure-index split** (above) — situational detail is TS source, not kept markdown files; guide SKILL.md became a pointer index to the source repo.
- **The per-file guide-intro rewrites.** All 9 workflows said "Read the guide skill first for [positioning / tier table / amplifier / safety line]" — but those moved to AGENTS.md. Rewrote each intro to the per-file form: always-on layer via AGENTS.md, the situational schema/entry-point detail via the `vibe-sec-guide` index, scaled to what each workflow actually writes (research, which writes no state, gets a one-liner; audit/gate/fix, which write through schemas, name the validation hook).
- **Confirming sidecar composition is state-file-mediated** (above) — the open-question #2 judgment call this port: read for `--silent`, found none, characterized the real composition architecture.

### PORT-RUNNER.md gaps hit this port

1. **Step 1/step 2 assume the always-on content is in `references/*.md`.** PORT-RUNNER step 1 says "Source: the guide skill's `references/*.md`" and the skeleton-builder only scans for matching reference-doc filenames (persona.md, posture.md, …). vibe-sec's always-on content is in the guide **SKILL.md body** with no `references/` dir, so the skeleton came up all-TODO with "no matching reference doc detected" — the synthesis source was actually the SKILL body + the workflow bodies. This is the inverse of vibe-walk/iterate (separate reference docs). **Recommend:** a note under step 1 — "the always-on source may be the guide SKILL.md **body** (single-file guide), not `references/*.md`. If the skeleton reports 'no matching reference doc detected,' synthesize AGENTS.md from the guide body + the workflow bodies, not from absent reference files."
2. **No guidance for "situational detail is source code, not kept files."** PORT-RUNNER step 2 says situational content "STAYS in the guide skill" as `schemas/*.json` / `references/*.md`. For sec the situational detail is the deterministic TypeScript (`src/`), which is NOT ported into `.agent/` — so the guide skill becomes a **pointer index to the source repo**, carrying zero data files. **Recommend:** a note under step 2 — "if the situational detail is the plugin's deterministic source (TS types, detector entry points) rather than `schemas/*.json` + `references/*.md`, the guide skill becomes an index that NAMES where each shape lives in the source repo; there may be zero kept data files. The split still holds — the situational half just ships with the CLI, not the `.agent/` skeleton."
3. **Open-question #2 needs the two-architecture distinction.** PORT-RUNNER step 8 #2 frames `--silent` sub-workflow calls as the thing to check, which presumes the iterate architecture (in-turn silent skill calls). sec's composition is state-file-mediated (writer writes findings.jsonl, readers read it) — a fundamentally different, **already-portable** pattern with no Antigravity-compose dependency. **Recommend:** rewrite step 8 #2 to distinguish: "(a) genuine silent sub-workflow calls (grep `--silent`) — the unverified case; (b) state-file handoff (one workflow writes a cached state file, others read it) — portable as-is, no compose-semantics dependency. Determine which architecture the plugin uses before flagging #2 as live."

Otherwise PORT-RUNNER.md carried the rest cleanly — the commands+skills merge (step 2b, now mechanical), the namespacing verification, the H1/inline-trigger check, the leftover-grep, and the open-questions re-check all mapped to existing steps. The commands+skills merge being mechanical is the proof that the vibe-doc port.py fix generalizes.
