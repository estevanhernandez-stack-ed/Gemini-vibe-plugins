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

## vibe-test@0.2.3 (ported 2026-05-24)

**Shape:** the family's **richest commands+skills plugin** — 8 commands (`audit`, `coverage`, `evolve`, `fix`, `gate`, `generate`, `posture`, `vibe-test`) + 14 skills (`audit`, `coverage`, `decay`, `evolve`, `fix`, `friction-logger`, `gate`, `generate`, `guide`, `posture`, `router`, `session-logger`, `vitals`, `wins-logger`) → **8 workflows + 6 skills** + AGENTS.md + agent.json. `port.py` did the seven clean command+skill merges mechanically (proving the step-2b fix generalizes again), but made **two new classification errors** the finishing pass corrected — both genuinely new edges, neither covered by the prior cookbook entries.

| Source surface | Source kind | Port target | Why |
|---|---|---|---|
| `audit`/`coverage`/`fix`/`gate`/`generate`/`posture` (cmd + skill) | thin wrapper + impl skill | **workflows** `/vibe-test-<cmd>` | step-2b merge — mechanical |
| `evolve` (cmd + skill) | thin wrapper + impl skill | **workflow** `/vibe-test-evolve` | step-2b merge + evolve-collapse — mechanical |
| `vibe-test` command + `router` **skill** | cross-named pair | **workflow** `/vibe-test` (router, **merged**) | **Error 1 — see below** |
| `vitals` | "Internal SKILL — not a slash command in v0.2" | **skill** `.agent/skills/vibe-test-vitals/` | **Error 2 — see below** |
| `decay`, `session-logger`, `friction-logger`, `wins-logger` | internal | **skills** | loaded, never typed |
| `guide` | shared-behavior | **split** → AGENTS.md + skill `vibe-test-guide` | guide split |

### Error 1 — cross-named command+skill pair → merged router (NEW lesson, headline)

`port.py`'s step-2b merge keys on **same-name** (command `scan` + skill `scan`). vibe-test's router is a **cross-named pair**: the `vibe-test` **command** (`commands/vibe-test.md`) and the `router` **skill** (`skills/router/SKILL.md`) are the *same* bare entry point — `router`'s description is literally *"used when the user says `/vibe-test` (bare)… the entry point."* Different names, so the same-name merge missed it: `port.py` emitted **two** workflows — `/vibe-test` (a thin command-only stub that still said "read `skills/router/SKILL.md`") AND `/vibe-test-router` (the full router body). Two slash commands for one front door.

**Fix:** fold the `router` skill's implementation (greet / first-run-detect / list-subcommands / decay-at-start / Pattern #15 version-resolution / Pattern #16 prereq-shaping) into the `/vibe-test` workflow body; the `vibe-test` command supplies the clean slash identity + `description`. **Delete `vibe-test-router.md`.** End state: one `/vibe-test` router workflow whose body is the router skill's, frontmatter is the command's.

**Lesson (new):** the thin-command-wrapper merge must also catch the **cross-named pair** — a command and a skill that are the *same entry point under different names* (here the eponymous command `vibe-test` + the conventionally-named `router` skill). The signal isn't the name match; it's that the skill's description names the **same slash trigger** the command owns. `port.py`'s same-name merge is necessary but not sufficient.

**Recommended `port.py` guard:** before the same-name merge, scan each unmatched skill's description for a slash-trigger phrase (`` `/<plugin>` `` bare, or `` `/<cmd>` ``). If a skill's declared trigger equals a command's slash (especially the bare `/<plugin>`), merge that skill into that command's workflow even when the names differ. The eponymous-router case (`vibe-test` cmd + `router` skill → `/vibe-test`) is the canonical instance; the resolved target is the bare router `<plugin>.md`, never `/<plugin>-router`.

### Error 2 — slash-mention false-positive → vitals demoted to skill (NEW lesson)

`port.py` promoted `vitals` to a `/vibe-test-vitals` **workflow** (flagged it as the bootstrap-style edge: "real slash trigger `/vibe-test:evolve` despite 'internal' self-label — trust the trigger"). **Wrong inversion of the bootstrap lesson.** The bootstrap edge is: a skill self-labels "internal" but its description lists *its own* `/<plugin>:bootstrap` trigger → it IS user-invocable. vitals is the opposite: it self-labels **"Internal SKILL — not a slash command in v0.2 — invoked by /vibe-test:evolve as a read-only pre-flight,"** and the `/vibe-test:evolve` it mentions is the **caller**, not its own trigger. The classifier false-matched the *mention* of a sibling's slash inside vitals' description as if it were vitals' own entry point.

**Fix:** demote to internal skill `.agent/skills/vibe-test-vitals/SKILL.md` (`name: vibe-test-vitals`). `/vibe-test-evolve` invokes it as a read-only pre-flight via skill-load (the source referenced it as `[../vitals/SKILL.md]`, not a slash — confirmed against source). Re-modeled vitals' seven-check Runtime Paths table for the `.agent/` layout (it self-tests the directory shape, like vibe-walk's vitals — the self-test is its own port surface). A user-facing `/vibe-test-vitals` workflow is slated for v0.3; the port keeps the forward-references (`Future /vibe-test-vitals`, the documented-empty friction-trigger row) intact but does NOT ship a v0.2 workflow.

**Lesson (new):** a skill that explicitly self-labels **"Internal — not a slash command"** but *mentions* a slash trigger in its description is the **mirror image** of bootstrap. The self-label should OVERRIDE a mere slash *mention* — distinguish *"used when the user says `/x`"* (its own trigger → workflow) from *"invoked by `/x` as a pre-flight"* (the caller → stays a skill). A slash in a description is only a promotion signal when the sentence frames it as the skill's **own** invocation, not as who calls it.

**Recommended `port.py` guard:** when a skill carries a "not a slash command" / "internal SKILL" self-label AND a slash mention, parse the grammatical role of the slash: promote only if the trigger phrase is *"used/invoked when the user says `/x`"* (first-person trigger); keep as a skill if it's *"invoked by `/x`"* / *"called from `/x`"* / *"pre-flight for `/x`"* (the slash is the agent/caller). When ambiguous, the explicit "not a slash command" self-label wins — flag for finishing-pass review rather than auto-promoting.

### Framework wiring (the richest in the family)

vibe-test carries the **full** self-evolving stack — Levels 2 + 3 plus decay (Pattern #4), wins (Pattern #14), and vitals (Pattern #8). Verified the workflows reference the internal skills by their namespaced names:

- **Router (`/vibe-test`)** invokes `vibe-test-decay` `check_decay()` at first-run-of-the-day (Pattern #4) and `vibe-test-friction-logger` `detect_orphans()` for abandoned-router detection.
- **`/vibe-test-evolve`** runs `vibe-test-vitals` as a pre-flight (skill-load, internal — NOT a workflow call), then reads `wins.jsonl` (Pattern #14 absence-of-friction inference) + `friction.jsonl` + `sessions/*.jsonl`, weights, and proposes. Self-edit targets are mapped per the port layout (workflows → `.agent/workflows/vibe-test-<cmd>.md`; the router → `.agent/workflows/vibe-test.md`; skills → `.agent/skills/vibe-test-<x>/`; classifier/scoring/generator **code** → the unported CLI `src/`).
- decay, wins-logger, vitals, friction-logger, session-logger all stay **internal skills**; the AGENTS.md "Self-evolving framework" section documents the wiring as the always-on contract.

**Note (richer-framework):** unlike vibe-walk/iterate (session + friction only), vibe-test adds **decay + wins + vitals**. decay is a router-time read; wins is a Pattern #14 counter-weight read only at evolve-aggregation; vitals is an evolve-pre-flight internal skill. None is a workflow — they are all skill-loaded, which is why the namespacing must rewrite their identities (`vibe-test-decay`, `vibe-test-wins-logger`, `vibe-test-vitals`) without ever minting a slash for them. The wins-logger especially is a *read-mostly* skill (evolve reads `wins.jsonl`; the loggers only append) — its value shows up only at L3 aggregation, so a port that drops it silently loses the absence-of-friction signal evolve depends on. Keep all five.

### The guide split

vibe-test's always-on content lives in the guide **SKILL.md body** (like vibe-sec — no `references/*.md` for persona/posture, so the skeleton came up all-TODO). Folded into AGENTS.md prose: persona (6 registers), posture (the 4 catalog-wide invariants + the **F2 honest-coverage stance**), mode + experience-level adaptation, the **tier-classification stance**, the Pattern #13 composition posture, handoff/version/prereq rules, hard rules, voice. Kept skill-side (situational): the **full classification matrix** (6 app types × 5 tiers × modifiers tables), data contracts, JSON schemas, the carried `templates/` dir, the anchored `plays-well-with.md` registry, the friction-trigger map, and the session-memory interface index. Rewrote `vibe-test-guide/SKILL.md` to a thin index pointing at AGENTS.md (a "where the always-on rules live" table) + the kept files.

### builder.json — confirmed load-bearing (12 repoints)

vibe-test **reads** `~/.gemini/profiles/builder.json` across every workflow (`shared.preferences.persona`, `shared.technical_experience.level`, `plugins.vibe-test.testing_experience`) + vitals (check #3 schema-validates it) + evolve. It writes only `_meta` decay stamps to its own `plugins.vibe-test` namespace. port.py did 12 builder-profile repoints; the finishing pass caught one miss inside `schemas/builder-profile.schema.json`'s description (still `~/.claude`) and fixed it.

### CLI-vs-slash (the vibe-doc watch-item)

**Clean — no collision.** vibe-test's body refs are TypeScript import surfaces (`src/composition/anchored-registry.ts`, `dist/handoff/index.js`), not `npx vibe-test <subcmd>` CLI calls — so there was no two-token `npx <plugin> <cmd>` form for the namespacer to hyphen-mangle. Confirmed zero `npx vibe-test-<sub>`. The only `vibe-test:` two-token hits are the literal HTML-comment **markers** the TESTING.md writer injects (`<!-- vibe-test:start/end:X -->`) — data tokens, correctly left alone. Added an AGENTS.md hard rule pinning the distinction (CLI binary `vibe-test <sub>` with a space vs slash workflow `/vibe-test-<cmd>` with a hyphen) so a future pass doesn't conflate them.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** No `schedule`-plugin dependency, no cron.
2. **`--silent` sidecar calls:** **None.** Composition is **state-file-mediated** (like sec) — `/vibe-test-evolve` reads the jsonl logs; vitals is an internal pre-flight skill **invocation** (skill-load within evolve's turn), not a silent sub-*workflow* call returning structured data. Portable as-is; the open-question #2 (a)/(b) distinction lands on (b).
3. **Workflow name collisions:** **RESOLVED — namespacing.** Router `/vibe-test` (bare) + 7 `/vibe-test-<cmd>`. The cross-named pair collapsed to the bare router correctly (no `/vibe-test-router`, no `/vibe-test-vibe-test`).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.2.3` (mirrors `plugin.json`; `package.json` is 0.2.4 — the npm CLI version, intentionally ahead). Read by the session/friction loggers for the audit field.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key. **builder-profile: YES, load-bearing** (see above).

### Mechanical (port.py got it right)

- The **7 clean command+skill merges** (`description` from command, body from skill, standalone skills dropped) — step-2b, zero hand-fix. The merged descriptions are the commands' clean one-liners (not the verbose skill blurbs); the bodies are the skill implementations (H1s match source skill H1s).
- Namespacing: 144 `plugin-namespaced-slash` repoints (`/vibe-test:audit` → `/vibe-test-audit` etc., 10 in posture alone); 19 `data-path`; 12 `builder-profile`; 4 `claude-home-generic`; 3 `plugin-json`; 2 `sidecar-bare`; 5 `command-start-end`. `agent.json` minted from `plugin.json`.

### Needed thought (the 20%)

- **The two classification errors** (above) — the headline calls, both new edges (cross-named-pair merge, slash-mention false-positive).
- **The guide split from a SKILL body** (above), and re-modeling **vitals' self-test** for the `.agent/` layout (8 workflows + 6 skills, not the source's `skills/**`).
- **Per-file guide-intro rewrites** for all 6 merged workflows — the generic auto-rewritten intro listed "persona, experience, Pattern #13, version resolution" (all now in AGENTS.md); rewrote each to the per-file form naming the schema-validation hook each workflow actually leans on (audit → classification matrix + audit-state schema; generate → generate-state schema; gate → locked weighted-score contract; posture → which state files to read).
- **Folded-reference back-pointers:** 7 `[guide > "Persona Adaptation"]` + 4 `[guide > "Handoff Language Rules"]` links redirected to `AGENTS.md §`; the single `[guide > "Classification Matrix"]` link kept guide-side (it stayed). All `../vibe-test-guide/` workflow→skill paths rewritten to root-absolute `.agent/skills/vibe-test-guide/` (workflows can't use `../` — it resolves to `.agent/workflows/guide/`).
- **evolve self-edit target map** retargeted for the layout flip (vitals went skill, router merged into `/vibe-test`) + the CLI-code carve-out (classifier/scoring → unported `src/`).
- **Reference-doc prose cleanup:** the carried `data-contracts.md` / `plays-well-with.md` / `friction-triggers.md` had source-layout `skills/<x>/SKILL.md` consumer paths (port.py namespaced the loggers but left the workflow targets in source form) and "command SKILL" prose — repointed each to its port target and converted to "workflow."

### PORT-RUNNER.md gaps hit this port

1. **Step 2b doesn't cover the cross-named command+skill pair.** PORT-RUNNER step 2b describes the merge as "command + **same-named** skill." The eponymous-command-plus-`router`-skill case is the same entry point under two names — the merge rule must key on the skill's declared slash trigger, not the name. **Recommend:** extend step 2b's table with a row — "command + a differently-named skill whose description declares the **same** slash trigger (e.g. command `vibe-test` + skill `router`, both = `/vibe-test`) → merge into one workflow; target is the bare router `<plugin>.md` if the trigger is `/<plugin>`. port.py's same-name merge misses this; verify by scanning unmatched skills for a slash-trigger that equals a command's slash."
2. **Step 3 needs the bootstrap-mirror case.** PORT-RUNNER step 3 names the bootstrap edge (internal self-label + own slash trigger → promote to workflow) but not its mirror (internal self-label + a slash *mention that is the caller* → stays a skill). vitals is the mirror. **Recommend:** add to step 3 — "Mirror of bootstrap: a skill self-labeled 'Internal — not a slash command' that *mentions* a slash which is its **caller** (`invoked by /x` / `pre-flight for /x`), not its own trigger (`used when the user says /x`), STAYS a skill. The 'not a slash command' self-label OVERRIDES a mere slash mention. Parse the grammatical role of the slash before promoting."
3. **Step 7 (self-test re-model) and the templates carry recur.** vibe-walk already flagged the vitals self-test re-model and the scripts-carry gap; vibe-test hit the **templates** variant — port.py carried `schemas/` + `references/` verbatim but **missed the guide's `templates/` dir** (6 `.template` files the audit/handoff workflows produce output from and vitals check #2 validates). **Recommend:** generalize the vibe-walk script-carry note to "carry ALL sibling data dirs under the guide skill (`schemas/`, `references/`, `templates/`, `fixtures/`) — port.py's verbatim-carry may miss dirs beyond schemas/references; diff the source guide skill's subdirs against the skeleton's."

Otherwise PORT-RUNNER.md carried the rest cleanly — the 7 mechanical merges (step 2b), the guide split, the per-file intros, the namespacing verification, the leftover-grep, and the open-questions re-check all mapped to existing steps. The seven-of-nine merges being mechanical (only the two cross/mirror edges needed hands) is more proof the step-2b fix generalizes — the residue is exactly the two cases the name-keyed merge and the trigger-keyed classifier structurally can't see.

## vibe-insights@0.1.0 (ported 2026-05-24)

**Shape:** a **new shape for the family — one orchestrator workflow over an external engine.** Source = a github-source plugin with **1 skill** (`skills/vibe-insights/SKILL.md`, the orchestrator) + a **separate, pip-installable Python engine** (`src/vibe_insights/`, the deterministic CLI) → **1 workflow + 0 skills** + AGENTS.md + agent.json. No `commands/` dir, no `guide` skill, no loggers, no `evolve-*`, no `hooks/`, no `scripts/`. `port.py` ran it clean: 1 workflow, 0 skills, 2 string repoints (1 claude-home, 1 claude-md), zero edge classifications.

| Source surface | Source kind | Port target | Why |
|---|---|---|---|
| `vibe-insights` (eponymous orchestrator skill) | user-invocable | **workflow** `/vibe-insights` (the **router**) | User types it; eponymous → bare router (not `/vibe-insights-vibe-insights`). port.py classified it correctly as a workflow this time (the description opens with the trigger phrasing). |
| `src/vibe_insights/` (the Python engine) | **external pip-installable CLI** | **NOT ported** — documented prerequisite | The skill runs the *installed* `vibe-insights` binary; same in Claude Code. The port carries the agent layer, the engine ships via pip. |

### The headline new lesson: orchestrator-workflow + external-engine — the port is the skill, NOT a bundle

Every prior port carried the plugin's whole behavior into `.agent/` (workflow/skill bodies, schemas, scripts). vibe-insights is the first where **the heavy lifting lives in a separate program the port does not carry.** The Claude Code skill is an *orchestrator*: it ensures config (`vibe-insights --init`), optionally overlays decisions, runs the deterministic engine (`vibe-insights` / `python -m vibe_insights.cli`), reads `digest.json`, synthesizes a grounded narrative, and re-renders (`--render-only`). The engine (`src/vibe_insights/`) is a standalone pip package (Python 3.11, `[project.scripts] vibe-insights = "vibe_insights.cli:main"`), deterministic + offline (no LLM, no MCP).

**The port = the orchestrator workflow + a documented pip prerequisite.** `src/` is deliberately NOT copied into `.agent/` — mirroring Claude Code, where the skill invokes the installed binary, not a bundled copy. This is distinct from vibe-doc/sec/test, where the deterministic CLI also wasn't bundled BUT those plugins still had a rich agent surface (workflows + guide skill) carrying the orchestration; here the *entire* agent surface is one orchestrator workflow, and its whole job is to drive an external tool.

**The key adaptation — make the prerequisite explicit in two places:** (1) the **workflow body** got a prerequisite blockquote at the intro (the `pip install "git+https://github.com/.../vibe-insights"` line, the "if the binary isn't on PATH, surface the install line and stop, don't reimplement inline" rule) and a reinforcing note at the first engine invocation (step 1's `--init`); (2) the **README** got a dedicated "Prerequisite — install the engine (it is NOT bundled)" section + a "shape that defined this port" section. **Lesson (new):** when a plugin's skill orchestrates an external binary rather than implementing the logic, the port is the skill→workflow + a documented install prerequisite. Don't bundle the engine; do make the dependency explicit in BOTH the workflow (where it invokes the binary) and the README (install). The faithful port preserves the Claude Code contract: the skill ran the installed tool, so the workflow does too.

### Path handling — the plugin has its OWN data dir; only repoint genuine Claude paths

vibe-insights has its own engine data dir `~/.vibe-insights/` (config, digest, decisions cache, reports). Source: `config.py` → `Path.home() / ".vibe-insights"`. **This is the engine's own platform-agnostic path — NOT a Claude path — and was left exactly as-is.** It must NOT be repointed to `~/.gemini`. The only genuine Claude refs that DID repoint (port.py's 2 hits, both correct):

- The coder-voice synthesis reference `~/.claude/CLAUDE.md` → `~/.gemini/antigravity/AGENTS.md` (the Voice section's `coder` option points at where the CODER VOICE SYNTHESIS block lives).
- The self-evolution log path `~/.claude/plugins/data/vibe-insights/` → `~/.gemini/antigravity/data/vibe-insights/` (kept for family consistency; **nothing in this port writes it** — no loggers).

**Lesson (new):** a plugin can have its own tool-namespaced home dir (`~/.vibe-insights/`) that is NOT the agent-tool's config home. Distinguish the plugin's own data dir (platform-agnostic, leave it) from genuine `~/.claude/...` agent-home refs (repoint to `~/.gemini/...`). Verify each `~/.claude`/`CLAUDE.md` hit is a real agent-home ref before repointing — and verify each `~/.vibe-insights`-style hit is the plugin's own dir before leaving it. A blind "repoint every home-dir path to ~/.gemini" would have corrupted the engine's data dir; a blind "leave all dotted-home paths" would have missed the voice + log repoints.

### The minimal-AGENTS.md decision (no guide skill, single orchestrator)

Like keystone/sec, there's no `guide` skill — port.py wrote an all-TODO AGENTS.md skeleton ("no guide skill detected — supply persona/posture by hand"). The source's CLAUDE.md/AGENTS.md are **GitNexus host-app index files** (code-intelligence MCP tooling), not the plugin's persona — correctly ignored as host artifacts, not port material. So the always-on layer was synthesized from the **skill body** (the work-wall rule, the MCP boundary, the output-ceiling discipline, the voice options). **No persona invented.** The genuinely always-on facts that earn the file: (1) the **engine-prerequisite** (load-bearing — the workflow can't run without the external binary); (2) the **work-walling hard rule** (employer sessions stay in the local-only `index.work.local.json` shard, never synced/published — load-bearing for correctness, not a preference); (3) the **decisions-MCP boundary** (only the workflow touches MCP; the engine reads a cache); (4) **output-ceiling discipline**; (5) **path handling** (the `~/.vibe-insights` leave-alone rule); (6) the **voice** options (coder/smart-brevity/oscar, default neutral). Result: a ~100-line AGENTS.md, append-safe, no manufactured persona.

### Decisions MCP — kept, boundary preserved

The MCP-agnostic decisions overlay (`config.decisions.source` = none/file/mcp) stays — Antigravity supports MCP. The boundary is preserved verbatim: **only the workflow touches MCP**; on `source == mcp` it fetches, maps to the canonical `{timestamp, title, body, project_tag, link}` shape, and writes `~/.vibe-insights/decisions.cache.json` BEFORE running the engine — **the engine reads the cache, never MCP itself.** Works with 626Labs `manage_decisions getUnified` or any user MCP. This is the portable-because-state-file-mediated pattern (sec/test's lesson, applied to MCP I/O): the workflow does the MCP read, hands the engine a file. No Antigravity-compose dependency.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** No `schedule`-plugin dependency, no cron. The report is run on demand.
2. **`--silent` sidecar calls:** **None.** Zero `--silent` anywhere in the source skill. The composition is **file-mediated** — the workflow writes `decisions.cache.json` + the narrative HTML fragment, the engine reads them. No sub-workflow invocation; portable as-is (open-question #2 lands on (b), the state-file-handoff architecture).
3. **Workflow name collisions:** **RESOLVED — namespacing.** One bare router `/vibe-insights` (eponymous → router form, not `/vibe-insights-vibe-insights`). Nothing else to namespace.
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.1.0` for family consistency — but vibe-insights has **no loggers** that read it. Pure bookkeeping; nothing consumes it. (`pyproject.toml` and `plugin.json` agree on 0.1.0.)
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key in plugin.json. No `~/.claude/profiles/builder.json` read either — the plugin reads its own `~/.vibe-insights/config.json`, not the shared builder profile.

**The distinctive open item this port — the external-engine dependency.** Unlike every prior port (self-contained in `.agent/`), this port relies on a **pip-installed `vibe-insights` binary being present on PATH** in the Antigravity environment. Whether an Antigravity workspace has Python tooling + the engine installed is unverified. **Mitigation:** the workflow checks for the binary, surfaces the `pip install` line, and fails soft (stops) if absent — it never reimplements the analytics. Documented as the prerequisite in both the workflow body and the README. **To resolve:** confirm Antigravity environments can run pip-installed Python CLIs and that the agent can detect a missing binary cleanly. This is the novel risk class the family hadn't hit — every prior port shipped everything it needed inside `.agent/`.

### Mechanical (port.py got it right)

- Classified the eponymous orchestrator skill → the bare router workflow `/vibe-insights` (description-trigger phrasing read correctly; no reclassification needed). 2 string repoints (`~/.claude/CLAUDE.md` → `~/.gemini/antigravity/AGENTS.md`; the data-path log line). `agent.json` minted from `plugin.json` (0.1.0). Left `~/.vibe-insights/` (the engine's own dir) untouched — correct. Zero edge classifications, zero `CLAUDE_PLUGIN_ROOT`, zero `.claude-plugin` left.

### Needed thought (the 20%)

- **The engine-prerequisite framing** (above) — the headline call. Made the external pip dependency explicit in the workflow body (intro blockquote + first-invocation note) and the README (dedicated section + path-handling provenance table). Decided NOT to bundle `src/`.
- **The path-handling discrimination** (above) — leave `~/.vibe-insights/` (engine's own dir), repoint only the 2 genuine Claude refs. Verified each hit's role before acting.
- **The minimal-AGENTS.md synthesis** (above) — folded the always-on facts (prerequisite, work-wall, MCP boundary, output-ceiling, path rule, voice) from the skill body; ignored the GitNexus host-app CLAUDE.md/AGENTS.md; invented no persona.
- **Confirming the source CLAUDE.md/AGENTS.md were host-app artifacts, not plugin persona** — they're GitNexus code-intelligence index files (`<!-- gitnexus:start -->`), not the plugin's own rules. A naive "fold the source AGENTS.md into the port AGENTS.md" would have imported a code-graph MCP's instructions into the port. Read before folding.

### PORT-RUNNER.md gaps hit this port

1. **No guidance for the orchestrator-over-external-engine shape.** PORT-RUNNER assumes the port carries the plugin's behavior into `.agent/` (workflows/skills/schemas/scripts). It has no step for "the skill orchestrates an external binary that is NOT carried — document it as a pip prerequisite." **Recommend:** add a PORT-RUNNER step (or extend step 8's open-questions) — "If a workflow invokes an external binary (a pip/npm CLI the source skill ran but didn't bundle), do NOT carry the engine source into `.agent/`. Document the install as a prerequisite in BOTH the workflow body (at the first invocation: how to install, fail-soft if absent) and the README (a dedicated prerequisite section). Add 'external-engine dependency' to the open-questions re-check — the port relies on the binary being present in the Antigravity environment, which is unverified."
2. **No guidance for distinguishing the plugin's own data dir from agent-home paths.** PORT-RUNNER step 9's leftover-grep targets `~/.claude` as a thing to repoint, but a plugin with its own tool-namespaced home dir (`~/.vibe-insights/`) has dotted-home paths that are NOT agent-config paths and must be left alone. **Recommend:** a note under step 9 — "Distinguish the plugin's OWN data dir (e.g. `~/.vibe-insights/`, platform-agnostic — leave it) from genuine `~/.claude/...` agent-home refs (repoint to `~/.gemini/...`). Verify each home-dir hit's role before acting; a blind repoint-all corrupts the plugin's own dir, a blind leave-all misses real agent-home refs."
3. **Source rules files may be host-app artifacts, not plugin persona.** vibe-insights' source CLAUDE.md/AGENTS.md were GitNexus code-intelligence index files (the dev's working-repo tooling), not the plugin's always-on layer. PORT-RUNNER step 1 says synthesize AGENTS.md "from the guide references" but doesn't warn that a source-repo CLAUDE.md/AGENTS.md may be unrelated host tooling. **Recommend:** a note under step 1 — "the source repo's own CLAUDE.md/AGENTS.md may be host-app tooling (GitNexus index, another plugin's rules), NOT this plugin's persona. Synthesize from the SKILL body + workflow bodies; read any source rules file before folding it — don't import an unrelated tool's instructions."

Otherwise PORT-RUNNER.md carried the rest cleanly — the eponymous → router resolution (already baked into port.py post-keystone), the minimal-AGENTS.md decision (keystone's lesson), the leftover-grep, the MCP-boundary preservation (sec/test's file-mediated lesson), and the open-questions re-check all mapped to existing steps. The guide-split steps (1, 2, 4, 5), the commands-merge (2b), and the script/template-carry gaps simply didn't apply (no guide, no commands, no scripts) — the residue this port was the genuinely new external-engine shape.

## vibe-wrap@0.2.1 (ported 2026-05-25)

**Shape:** the family's **first hook-bearing port** — and the one that resolves open-question #5 (Claude-only hooks) with a real answer instead of a deferral. Source = 7 skills (`wrap`, `status`, `plant`, `guide`, `evolve-wrap`, `session-logger`, `friction-logger`) + a `hooks/` dir (`hooks.json` + `session-end-nudge.py`), no `commands/` dir → **3 workflows + 4 skills** + AGENTS.md + agent.json + carried scripts + a wired SessionEnd hook. Two headline calls: the **HOOKS handling** (new frontier) and the **eponymous-main-with-differently-named-skill** case.

| Source skill | Source self-label | Port target | Why |
|---|---|---|---|
| `wrap` | description = "use when the user says `/vibe-wrap` (or `/vibe-wrap:wrap`)…" — the main command | **workflow** `/vibe-wrap` (the **router**) | **Eponymous-main edge — see below.** The `wrap` skill IS the plugin's main command; ported to the bare router, not `/vibe-wrap-wrap`. |
| `status` | user-invocable (`/vibe-wrap:status`) | **workflow** `/vibe-wrap-status` | Read-only mid-session check. port.py classified correctly. |
| `evolve-wrap` | user-invocable (`/vibe-wrap:evolve-wrap`) | **workflow** `/vibe-wrap-evolve` | L3 self-evolution, evolve-collapse. Correct. |
| `plant` | "Internal SKILL — not user-invocable" | **skill** `vibe-wrap-plant` | Siblings call it to drop a breadcrumb. Correct (stays a skill). |
| `guide` | shared-behavior, never invoked | **split** → AGENTS.md + skill `vibe-wrap-guide` | guide split. |
| `session-logger`, `friction-logger` | internal | **skills** | loaded, never typed. |

### The HOOKS handling (the headline — first hook-bearing port, open-question #5 resolved)

vibe-wrap ships a Claude Code **SessionEnd** hook (`hooks/hooks.json` + `session-end-nudge.py`) that emits one nudge line when the closing session left a trail. `port.py` does NOT touch `hooks/` (by design — see PORT-RUNNER step 8 #5), so the whole hook was a hand-finish, and the brief's mandate was **research the Antigravity event model, don't speculate.**

**The research finding (web search, not assumption):** **Antigravity 2.0 supports lifecycle hooks, including `SessionEnd`.** The evidence chain:

- Antigravity 2.0's feature set includes a **JSON hook system** ("hooks intercept and customize agent behavior at lifecycle stages") plus scheduled background tasks, announced at I/O 2026. Multiple write-ups confirm hooks are stored/managed in the `.agent`/workspace config and are "the same JSON hook format introduced in Antigravity 2.0," carried over from the **Gemini CLI** lineage.
- The **Gemini CLI configuration reference** (which the sources consistently say shares Antigravity's hook format) documents the full event set — `BeforeTool`, `AfterTool`, `BeforeAgent`, `AfterAgent`, `Notification`, **`SessionStart`**, **`SessionEnd`** ("hooks that execute when a session ends; can perform cleanup or persist session data"), `PreCompress`, `BeforeModel`, `AfterModel`, `BeforeToolSelection`. Hooks live in `settings.json` under a `hooks` object keyed by event name.
- The **Gemini CLI hooks reference** gives the per-entry schema: `{ matcher, sequential, hooks: [{ type: "command", command, name?, timeout?, description? }] }`, and the SessionEnd **stdin payload**: base `{ session_id, transcript_path, cwd, hook_event_name, timestamp }` + SessionEnd-specific `{ reason: "exit|clear|logout|prompt_input_exit|other" }`.

**This matches the Claude Code SessionEnd contract field-for-field.** Claude's payload is `{ session_id, transcript_path, cwd, hook_event_name, why }`; Gemini's is the same with `why → reason` (same enum values). The nudge script reads **neither** `why` nor `reason` — only `session_id` + `cwd` — so the rename is **non-breaking.** This is the cleanest possible hook port: the event exists, the contract is identical, the script is portable as-is.

**How I wired it (NOT a fake wiring — a real one, with a documented fail-soft):**

- Carried `session-end-nudge.py` → `.agent/hooks/` (repointed the breadcrumb data path `~/.claude/...` → `~/.gemini/antigravity/...`; updated the payload docstring `why` → `reason` for fidelity; the logic is untouched).
- Wrote `.agent/hooks/settings.json` — the **Antigravity-native** config: a `hooks.SessionEnd` block with a `command`-type entry running `python3 .agent/hooks/session-end-nudge.py`. The user merges this block into their workspace `.gemini/settings.json` (or user settings) to arm the nudge.
- Kept the Claude Code original `.agent/hooks/hooks.json` for **provenance** (repointed `${CLAUDE_PLUGIN_ROOT}/hooks/...` → `.agent/hooks/...`, added a `_provenance` note explaining the two config homes: Claude's discovered `hooks/hooks.json` vs Antigravity's `settings.json` hooks block — same event, same stdin contract).
- **Documented the fail-soft explicitly** in AGENTS.md (§ Event model — the SessionEnd nudge hook) and the README: the nudge is non-critical; if the settings block isn't merged (or the build discovers hooks differently than expected), the nudge simply doesn't fire and `/vibe-wrap` works fully without it. Nothing depends on the hook.

**Lesson (new, headline):** open-question #5 has a real answer — **Antigravity inherits the Gemini-CLI hook system, and `SessionEnd` is a first-class event.** A SessionEnd hook ports by (a) carrying the script to `.agent/hooks/` with data-path repoints, (b) writing a `settings.json` `hooks.SessionEnd` block (the Antigravity-native home, vs Claude's discovered `hooks/hooks.json`), and (c) documenting the merge step + a fail-soft (the hook is convenience, not dependency). The Claude→Gemini payload delta is `why → reason`; verify whether the script reads that field (this one didn't, so it was non-breaking). The remaining unverified edge: whether a given Antigravity build discovers `settings.json` hooks at the **workspace** vs **user** level — documented as a "place the block accordingly" caveat rather than guessed.

### The eponymous-main-with-differently-named-skill case (the second headline)

`port.py` defaulted `wrap` → workflow `/vibe-wrap-wrap` (its slash-trigger phrasing read correctly as user-invocable). But the resolved slash is wrong: the `wrap` skill IS the plugin's main `/vibe-wrap` command (source description: "use when the user says `/vibe-wrap` (or `/vibe-wrap:wrap`)…"; H1 "The user-facing session wrap"; README "the main end-of-session wrap"). This is the **eponymous-main case** — like keystone — but with a twist the prior eponymous resolutions didn't cover: **the skill is named `wrap`, not `vibe-wrap`,** so port.py's name-equals-plugin check (which caught keystone's `keystone`→`/vibe-keystone` and sec/test's `vibe-sec`/`vibe-test` routers) **didn't fire.** The skill name ≠ plugin name, so the namespacer produced `/vibe-wrap-wrap` (the generic non-router form) instead of recognizing it as the router.

This is the **mirror of vibe-test's Error 1** (cross-named command+skill pair). There it was a `vibe-test` *command* + a `router` *skill* = same front door under two names. Here there's no `commands/` dir — it's a lone skill whose **declared trigger is the bare `/<plugin>`** even though its filename isn't `<plugin>`. The signal is the same: **the skill's declared slash trigger equals `/<plugin>`**, so its target is the bare router `<plugin>.md` → `/<plugin>`, never `/<plugin>-<skillname>`.

**Fix:** renamed `.agent/workflows/vibe-wrap-wrap.md` → `vibe-wrap.md`; rewrote the body's `/vibe-wrap-wrap` self-refs → `/vibe-wrap`; updated every sibling's `/vibe-wrap-wrap`-territory reference (status, friction-triggers, the H1, the "that's wrap's job" prose) to `/vibe-wrap`. End state: one `/vibe-wrap` router workflow, no `/vibe-wrap-wrap` anywhere.

**Lesson (new):** the eponymous-router edge has a **third form** beyond keystone (skill name == plugin name) and vibe-test (command + cross-named `router` skill): a **lone skill whose declared trigger is `/<plugin>` but whose filename isn't `<plugin>`** (here `wrap` → `/vibe-wrap`). port.py's name-equals-plugin router check misses it because it keys on the skill *name*, not the skill's *declared trigger*. Catch it in the finishing pass by reading each non-router workflow's frontmatter `description`/H1 for a bare `/<plugin>` trigger; if found, that workflow IS the router — rename to `<plugin>.md`, never ship the `/<plugin>-<skillname>` doubled-verb form.

### Scripts carry (the vibe-walk/vibe-doc gap, hit hardest yet)

vibe-wrap is the **most script-heavy port so far** — the entire deterministic wrap core lives in `skills/wrap/scripts/` (render-wrap, multi-repo/git-state, two readers, atomic-append, a 7-module `decision-log/` dispatcher package) plus `skills/status/scripts/status.py`, and each logger/plant skill carries its own helper. `port.py` carried **only** the logger + plant skill scripts (the ones nested under skills it copied verbatim); it **did NOT carry** the `wrap`/`status` skill scripts, because the eponymous `wrap` skill collapsed into a single-file workflow (the single-file workflow branch drops sub-dirs) and `status` likewise. So the wrap workflow's whole engine was missing from `.agent/`.

**Hand-fix (the vibe-walk lesson — workflows can't keep scripts under `.agent/skills/`):**

- Carried `skills/wrap/scripts/*` (+ the `decision-log/` package + `assets/wrap-template.md` + `references/*.md`) and `skills/status/scripts/status.py` → **`.agent/scripts/`** (flat — collapsed the source's two scripts dirs, since `render-wrap.py` already referenced its siblings as flat). Dropped all `__pycache__`.
- **Re-modeled the scripts' own internal path constants** — this was the load-bearing part the prior script-carry ports under-flagged. The carried scripts compute paths off `__file__`:
  - `status.py`'s `WRAP_SCRIPTS_DIR = SCRIPT_DIR.parent.parent / "wrap" / "scripts"` → `SCRIPT_DIR` (siblings are now flat).
  - `render-wrap.py`'s `ASSETS_DIR = SCRIPT_DIR.parent / "assets"` → `SCRIPT_DIR / "assets"` (assets travel with the scripts).
  - the loggers'/plant's `PLUGIN_ROOT = SCRIPT_DIR.parent.parent.parent` resolves to `.agent/` correctly post-rename, but `PLUGIN_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"` → `PLUGIN_ROOT / "agent.json"`, and `ATOMIC_APPEND = PLUGIN_ROOT / "skills" / "wrap" / "scripts" / "atomic-append-jsonl.py"` → `PLUGIN_ROOT / "scripts" / "atomic-append-jsonl.py"`.
  - every `~/.claude/plugins/data/...` → `~/.gemini/antigravity/data/...` and `~/.claude/profiles/builder.json` → `~/.gemini/profiles/builder.json` inside the scripts (config.py, read-breadcrumbs.py, read-sibling-state.py, first_run_prompt.py, the 3 logger scripts, plant.py, the hook script) — these are the **deterministic core's own constants**, load-bearing, not prose.
- Repointed every workflow/skill **body** ref: `python skills/wrap/scripts/X.py` → `python .agent/scripts/X.py`; `../vibe-wrap-wrap/scripts/...` and `../vibe-wrap-wrap/references/...` (the namespacer's over-reach when `wrap`→router moved the dir) → `.agent/scripts/...` (root-absolute from workflows; `../../scripts/...` from skills, since workflows can't use `../` and skills are one level deeper).
- **Byte-compiled the whole `.agent/` tree** (`python -m compileall`, exit 0) to catch any path-constant typo — the script-carry ports should ALL do this; it's the cheapest proof the deterministic core still imports.

**Recommend (reinforces vibe-walk gap #1 + vibe-doc gap #4, now THREE ports deep):** promote scripts-carry from "improvise" to a real PORT-RUNNER step. AND add the under-flagged half: **after carrying, re-model the scripts' own `__file__`-relative path constants** (`SCRIPT_DIR.parent...` chains, `PLUGIN_ROOT`, manifest path `.claude-plugin/plugin.json`→`agent.json`, the atomic-append/sibling-script locations) for the collapsed `.agent/scripts/` layout — the body-ref repoint alone leaves the scripts pointing at the source tree. AND byte-compile the tree as the verify gate.

### The guide split

vibe-wrap's always-on layer lives in the guide SKILL **body** + 3 reference docs (`persona-adaptation.md`, `voice.md`, `friction-triggers.md`). Folded into AGENTS.md prose: persona (5 + default), the **bumper-lanes invariant** (every gate defaults to no-action — the load-bearing safety contract), the **read-wide/mutate-narrow** multi-repo rule, mode (Learner/Builder pacing), voice + banned-word list, Pattern #11 namespace isolation, Pattern #13 state-file-mediated composition, the **decision-log-pluggable-backends** posture, the self-evolving-framework wiring, the SessionEnd hook model, and a numbered hard-rules block. Kept skill-side (situational): the full **per-persona × 4-surface table** (persona-adaptation.md), the **voice register frame** (voice.md), the **friction-trigger map** (friction-triggers.md). The script-side contracts (gate-design, secret-patterns, decision-log-backends, breadcrumb-contract) stay next to the deterministic core under `.agent/scripts/references/`. Rewrote `vibe-wrap-guide/SKILL.md` from the full ~190-line shared-behavior doc to a ~45-line situational index pointing at AGENTS.md + the kept files. The carried reference docs had already been data-path + builder-profile repointed by port.py; hand-fixed the residual `## /vibe-wrap (a.k.a. /vibe-wrap-wrap)` and `## /plant` headings to the namespaced forms.

### builder.json — read-only, repointed (10 hits)

vibe-wrap **reads** `~/.gemini/profiles/builder.json` (`shared.preferences.persona` + `shared.preferences.mode`) in the session-logger scripts (start.py/end.py) and per persona-adaptation; it **never writes** the profile (Pattern #11 — `shared.*` is read-only territory, and even vibe-wrap's own `plugins.vibe-wrap._meta` snapshot is deferred to a future version). port.py did 10 builder-profile repoints in the SKILL/reference bodies; the finishing pass caught the 2 misses inside the **carried logger scripts** (start.py + end.py `PROFILE_PATH`) — same "stale strings inside carried scripts" straggler vibe-doc flagged for schemas, here for the loggers' own constants.

### Other repoints

data-path (32, all `~/.claude/plugins/data/vibe-wrap/` → `~/.gemini/antigravity/data/vibe-wrap/`, incl. the breadcrumb/session/friction dirs + the decision-log's own `~/.claude/decisions.{md,jsonl}` user-scoped fallback → `~/.gemini/antigravity/decisions.*`); claude-home (the AGENTS.md log-location provenance note — left as an intentional repoint-note mention per PORT-RUNNER step 9); the 1 `~/.claude/CLAUDE.md` project-binding ref in decision-log-backends.md → `~/.gemini/antigravity/AGENTS.md` (cross-tool context — the rules file the MCP backend reads for project binding); plugin.json → agent.json (the loggers' `plugin_version` audit source); the `spec.md`/`docs/spec.md` source-tree refs (which don't exist in the port) rewritten to the script-side contract docs. The `${CLAUDE_SESSION_ID}` token (17 hits) was **kept** with a documented port note: it's the session-id passthrough placeholder, and Antigravity's exact substitution token is unverified — the contract is token-agnostic (the caller resolves whatever the host exposes as the active session id and passes it as `--session-id`; empty → `_orphan.jsonl`, graceful). Do NOT invent a `${GEMINI_SESSION_ID}` — there's no evidence for one.

### evolve-wrap self-edit targets

Added an explicit **target-map block** to `/vibe-wrap-evolve`: source proposals named `plugins/vibe-wrap/skills/<cmd>/SKILL.md`; those flip because `wrap`→router workflow and the loggers/plant→namespaced skills. The map routes main-command edits → `.agent/workflows/vibe-wrap.md`, shared rules → `AGENTS.md`, the persona/voice/friction refs → `.agent/skills/vibe-wrap-guide/references/`, logger/plant bodies → `.agent/skills/vibe-wrap-<skill>/SKILL.md`, the render core + contracts → `.agent/scripts/...`, and the **hook** → `.agent/hooks/...` (a new target class no prior port's evolve map had). Carried the `proposed-changes-template.md` (port.py missed it — evolve's reference doc, same gap as the wrap scripts) → `.agent/scripts/references/` and fixed its one example self-edit target (`skills/wrap/SKILL.md` → `.agent/workflows/vibe-wrap.md`).

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** vibe-wrap has no `schedule`-plugin dependency. (Antigravity 2.0 does ship scheduled background tasks, but vibe-wrap doesn't use one — the wrap is run on demand / nudged at session end.)
2. **`--silent` sidecar calls:** **None.** Composition is **state-file-mediated** (sec/test's architecture): the wrap reads the breadcrumb trail + sibling session/friction/wins files that siblings already wrote; the `vibe-wrap-plant` skill is a fire-and-forget breadcrumb writer, not a silent sub-workflow returning structured data. Open-question #2 lands on (b) — portable as-is, no compose dependency.
3. **Workflow name collisions:** **RESOLVED — namespacing.** Router `/vibe-wrap` (bare, eponymous) + `/vibe-wrap-status` + `/vibe-wrap-evolve`. The eponymous-with-differently-named-skill case collapsed to the bare router (no `/vibe-wrap-wrap`).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.2.1`, read by the session + friction loggers for the audit field. Same bookkeeping status as the logger-bearing siblings.
5. **Claude-only hooks:** **YES — and RESOLVED with a real wiring.** This is the open-question-#5 port. `hooks/` present (SessionEnd nudge). Antigravity supports SessionEnd via the Gemini-CLI hook system; wired via `.agent/hooks/settings.json` + the carried script, fail-soft documented. See the HOOKS section above. **builder.json: YES, read-only** (10 repoints + 2 caught in carried scripts).

### Mechanical (port.py got it right)

- Classified `status`/`evolve-wrap` as workflows correctly; `plant`/`session-logger`/`friction-logger` as skills correctly; `guide` flagged for the split. Namespacing: 20 plugin-namespaced-slash, 21 sidecar-backtick (all landed `/vibe-wrap-<x>`), 16 command-start-end → workflow-start-end, 32 data-path, 10 builder-profile, 8 claude-home, 2 plugin-root-generic, 4 plugin-json, 3 claude-md. agent.json minted from plugin.json (0.2.1). Carried the logger + plant skill scripts verbatim.

### Needed thought (the 20%)

- **The HOOKS research + wiring** (above) — the headline. Researched the Antigravity/Gemini event model (web search, not speculation), confirmed SessionEnd is first-class, wired it via settings.json with a documented fail-soft, kept hooks.json for provenance.
- **The eponymous-main-with-differently-named-skill reclassification** (above) — `wrap` skill → `/vibe-wrap` router (the third form of the eponymous edge).
- **The scripts carry + the under-flagged `__file__`-path-constant re-model** (above) — the deterministic core's own internal path constants, not just body refs. Byte-compiled to verify.
- **The guide split from a SKILL body + 3 refs**, the **evolve self-edit target map** (with the new hook target class), and the **builder.json straggler fix inside carried logger scripts.**
- **The `${CLAUDE_SESSION_ID}` judgment** — keep the token, document it's a host-agnostic passthrough placeholder with graceful orphan-fallback degradation; don't invent a Gemini token.

### PORT-RUNNER.md gaps hit this port

1. **No step for porting `hooks/`** — the big one, by design (PORT-RUNNER step 8 #5 + the "what the script will never do" list both say port.py doesn't port hooks and the event model is unverified). Now it's verified. **Recommend:** add a real PORT-RUNNER step (and a port.py flag) — "If the source has a `hooks/` dir: Antigravity supports the Gemini-CLI hook system (events incl. SessionStart/SessionEnd/Before-After-Tool/Agent/Model, Notification, PreCompress). Carry the hook script to `.agent/hooks/` (repoint data paths + `${CLAUDE_PLUGIN_ROOT}`); write a `.agent/hooks/settings.json` `hooks.<Event>` block (command-type entry) as the Antigravity-native wiring; keep the source `hooks.json` for provenance; document the merge-into-`.gemini/settings.json` step + a fail-soft. Watch the payload field delta (Claude `why` → Gemini `reason`) — repoint only if the script reads it. Flag the workspace-vs-user settings discovery as the remaining unverified caveat." And port.py should at minimum **carry `hooks/` + flag it** instead of ignoring it.
2. **Eponymous-router has a third form** the name-equals-plugin check misses: a lone skill whose **declared trigger is `/<plugin>`** but whose filename isn't `<plugin>` (`wrap`→`/vibe-wrap`). **Recommend:** extend PORT-RUNNER step 3 / step 6.5 — "the eponymous-router resolution must key on the skill's **declared slash trigger** (`/<plugin>` in the description/H1), not just the skill name. A skill named `wrap` whose trigger is `/vibe-wrap` IS the router → `<plugin>.md`. port.py's name-equals-plugin check catches keystone/sec/test (name == plugin) but not this filename ≠ plugin case."
3. **Scripts-carry now needs the `__file__`-path-constant re-model called out explicitly + a byte-compile verify gate.** vibe-walk and vibe-doc flagged "carry scripts + repoint body refs" but under-stated that the **scripts' own internal path constants** (`SCRIPT_DIR.parent` chains, `PLUGIN_ROOT`, the manifest path, atomic-append/sibling locations) must be re-modeled for the collapsed `.agent/scripts/` layout — the body-ref repoint alone leaves them pointing at the source tree, and they fail silently (no-op-safe loggers just stop logging). **Recommend:** the scripts-carry step must say "re-model the carried scripts' `__file__`-relative path constants for `.agent/scripts/`; then `python -m compileall .agent` (expect exit 0) as the verify gate."
4. **builder.json stragglers live inside carried scripts too** (not just schema `description` strings — vibe-doc's note). The session-logger scripts' `PROFILE_PATH` constant needed the `~/.claude/profiles → ~/.gemini/profiles` repoint by hand. **Recommend:** generalize vibe-doc's "stale strings inside carried files" note to "carried *scripts* (not just schemas/refs) carry stale `~/.claude` / `.claude-plugin` / `builder.json` constants — grep the carried `.py` files specifically after carrying."

Otherwise PORT-RUNNER.md carried the rest cleanly — the guide split, the per-file guide-intro rewrites, the namespacing verification, the evolve self-edit retargeting (extended with the hook target class), the leftover-grep, and the open-questions re-check all mapped to existing steps. The residue this port was the genuinely new hooks frontier (now resolved with a real wiring + research) and the third eponymous-router form.

## vibe-thesis@0.2.0 (ported 2026-05-25)

**Shape:** the most nuanced commands+skills port in the family — cross-named pairs *at scale*, a frontmatter signal port.py doesn't read, a rules-file write target, and a bundled scaffold template. Source = 5 commands (`guard`, `smooth`, `vibe-render`, `vibe-status`, `voice`) + 7 skills (`audit`, `synthesis-guard`, `synthesis-smooth`, `vibe-render`, `vibe-status`, `vibe-thesis` router, `voice-synthesis`) → **7 workflows + 0 skills** + AGENTS.md + agent.json + a 127-file bundled scaffold carried verbatim. No hooks, no loggers, no guide skill, no evolve, no builder.json. port.py emitted 8 workflows + 2 skills with **three classes of reconciliation error** — the finishing pass was almost entirely the merge, the collapse, and the promote.

| Source surface | Source kind | Port target | Why |
|---|---|---|---|
| `vibe-thesis` **skill** (router, `user-invocable: false`) | router | **workflow** `/vibe-thesis` | The orchestrator. Routes scaffold/iterate intent. port.py got this (bare router). |
| `vibe-render` cmd + `vibe-render` skill | **same-named** pair | **workflow** `/vibe-thesis-render` | step-2b merge — port.py merged it, but namespaced to the **doubled** `/vibe-thesis-vibe-render`; collapsed the redundant `vibe-`. |
| `vibe-status` cmd + `vibe-status` skill | **same-named** pair | **workflow** `/vibe-thesis-status` | same: doubled `/vibe-thesis-vibe-status` → `/vibe-thesis-status`. |
| `guard` cmd + `synthesis-guard` skill | **cross-named** pair | **workflow** `/vibe-thesis-guard` | **Error class 1** — see below. |
| `smooth` cmd + `synthesis-smooth` skill | **cross-named** pair | **workflow** `/vibe-thesis-smooth` | **Error class 1.** |
| `voice` cmd + `voice-synthesis` skill | **cross-named** pair | **workflow** `/vibe-thesis-voice` | **Error class 1.** Also the rules-file writer — see below. |
| `audit` skill (`user-invocable: true`, standalone) | user-facing, no parallel cmd | **workflow** `/vibe-thesis-audit` | **Error class 2** — see below. |

**Count: 7 workflows + 0 skills.** Deleted: 3 mis-emitted duplicate workflows (`vibe-thesis-synthesis-smooth.md`, `vibe-thesis-voice-synthesis.md`, and the thin `guard`/`smooth`/`voice` command stubs the merge absorbed), 2 mis-emitted skill dirs (`vibe-thesis-synthesis-guard`, `vibe-thesis-audit`), and the now-empty `.agent/skills/` dir.

### Error class 1 — cross-named pairs AT SCALE + duplicate-collapse (NEW lesson, headline)

vibe-test surfaced the single cross-named pair (the `vibe-test` command + `router` skill → one router). vibe-thesis is that lesson **three times in one plugin, in non-router commands**. The commands here ARE thin wrappers, but they delegate to **differently-named** skills:

- `commands/guard.md` → "Use the **synthesis-guard** skill" (cmd `guard` ↔ skill `synthesis-guard`)
- `commands/smooth.md` → "Use the **synthesis-smooth** skill" (cmd `smooth` ↔ skill `synthesis-smooth`)
- `commands/voice.md` → "Use the **voice-synthesis** skill" (cmd `voice` ↔ skill `voice-synthesis`)

port.py's step-2b merge keys on **same-name**, so it missed all three: it emitted each command as a **command-only workflow** (a thin stub still saying "Use the X skill") AND emitted the skill as a **separate workflow** (`synthesis-smooth`/`voice-synthesis`) or **skill** (`synthesis-guard`). Result: two surfaces per feature — e.g. `/vibe-thesis-voice` (stub) AND `/vibe-thesis-voice-synthesis` (full body). Same front door, two slashes.

**The reconciliation isn't pattern-matchable — you must READ each command + each candidate skill** and confirm the command's delegation line names that skill AND the skill's H1/description owns the command's slash trigger (`synthesis-guard`'s H1 is literally `# /vibe-thesis:guard`; `synthesis-smooth`'s is `# /vibe-thesis:smooth`; `voice-synthesis`'s is `# /vibe-thesis:voice`). For each confirmed pair → **one workflow**: command supplies slash + clean `description`, skill supplies the body. **Collapse the duplicate** port.py minted (delete the standalone skill/workflow). The merge target slash is the **command's** name (`/vibe-thesis-guard`, not `/vibe-thesis-synthesis-guard`).

**Lesson (new, headline):** the thin-wrapper merge must handle cross-named pairs *at scale*, not just the one eponymous-router case. The match signal is **the command's delegation target + the skill's declared slash trigger**, never the name. When port.py emits BOTH a `/<plugin>-<cmd>` stub and a `/<plugin>-<skillname>` full-body workflow for the same feature, that's the tell — collapse to one, keyed on the command's slash. (Sub-rule already known but re-hit: same-named pairs whose name starts with the plugin's own verb prefix produce a **doubled** namespaced slash — `vibe-render`+`vibe-render` → `/vibe-thesis-vibe-render`. Collapse the redundant prefix to `/vibe-thesis-render`. Same call keystone's eponymous router made, applied to a non-router same-named pair.)

**Recommended port.py guard:** when a command body is a thin "Use the **X** skill" delegation, resolve **X** (the named skill) and merge that command with skill X even when names differ — keyed on the delegation target, not the filename. Combine with the existing same-name merge + the vibe-test "skill's declared trigger == a command's slash" guard. And: when a same-named pair's name begins with the plugin's verb prefix (`vibe-render` under `vibe-thesis`), strip the redundant prefix from the namespaced slash.

### Error class 2 — `user-invocable: true` frontmatter as a classification signal (NEW lesson)

`audit` is a standalone user-facing command (a marker-free discipline lint over any .md file) with **no parallel command file**. Its description opens "Use this skill when the user wants to discipline-audit…" — description-phrasing the classifier reads as semantic-load, so port.py **defaulted it to a skill** (`vibe-thesis-audit/SKILL.md`, edge-flagged "no real slash trigger or user-says phrasing"). Wrong: its frontmatter carries **`user-invocable: true`** AND its H1 is `# /vibe-thesis:audit` AND it takes a positional path argument. It's a user-typed entry point → **workflow** `/vibe-thesis-audit`.

**The frontmatter field is the load-bearing signal port.py never read.** vibe-thesis skills carry `user-invocable` / `disable-model-invocation` / `allowed-tools`. `user-invocable: true` is an *explicit* author declaration that this skill is a slash entry point — it should **override** description-phrasing classification. (Every skill in this plugin had `user-invocable: true`; the merged pairs got promoted by the merge, but `audit` — having no command to merge with — fell through to the default because the classifier judged on phrasing, not the field.)

**Lesson (new):** `user-invocable: true` in a skill's frontmatter is a first-class classification signal — read it FIRST, before description phrasing. `true` → workflow (the author marked it user-facing); absent/`false` → fall back to phrasing + trigger evidence. This is cleaner than the bootstrap/vitals grammatical-role heuristics: the author already answered the question in a structured field. Converting skill→workflow, **keep `description`, DROP the skill-only fields** (`user-invocable`, `disable-model-invocation`, `allowed-tools`) — workflows are description-only.

**Recommended port.py guard:** parse skill frontmatter for `user-invocable`. If `true` → classify as workflow regardless of description phrasing (it's an explicit user-facing declaration). If `false` → it's internal *unless* it's the merge target of a command (the router case: `vibe-thesis` skill is `user-invocable: false` but IS the router because a command/intent routes to it). If absent → current phrasing+trigger heuristic. This would have auto-corrected `audit` AND confirmed all the merged pairs.

### The rules-file write target — voice-synthesis writes `AGENTS.md` (keystone's lesson, at the pair level)

`/vibe-thesis-voice` (the merged `voice` cmd + `voice-synthesis` skill) **writes** a `## VOICE SYNTHESIS` block to the project rules file, and `/vibe-thesis-smooth` **reads** it back. On Claude Code that file is `CLAUDE.md`; in the port the file it WRITES must be `AGENTS.md` (keystone's whole-job lesson, here applied to one workflow inside a larger plugin). port.py's 25 `claude-md` repoints flipped the bodies correctly (the voice workflow writes AGENTS.md, smooth reads AGENTS.md, marker/mode detection reads AGENTS.md). The finishing-pass judgment: verify the write/read **pair** stays consistent (voice writes where smooth reads) and that the `description` frontmatter flipped too — port.py left the voice description saying "Writes a VOICE SYNTHESIS block to **CLAUDE.md**" (the leftover the report flagged); fixed to AGENTS.md. Also caught **one over-namespaced prose straggler** (the common-noun trap): the namespacer rewrote a plain-word "run synthesis-guard first" in the router's pre-render offer into "run **vibe-thesis-synthesis-guard** first" — restored to natural prose ("run the synthesis guard first").

**Kept `CLAUDE.md` deliberately** in the output-vs-context spots (keystone's rule): the bundled template ships ThesisStudio's `CLAUDE.md` verbatim, and the router documents "copy the template's `CLAUDE.md` to `AGENTS.md`; the verbatim `CLAUDE.md` stays for cross-tool compatibility, `AGENTS.md` is the live rules file." The OUTPUT contract (voice block, marker, mode) is unambiguously `AGENTS.md`; the bundled `CLAUDE.md` is carried data the port may read.

### The bundled scaffold-template carry (NEW lesson)

vibe-thesis ships a **127-file scaffold the plugin produces** at `templates/full/` (109 files: numbered dirs, design system, render scripts under `templates/full/scripts/`, schemas, dev container, CI, the project-local `.claude/skills/` bootstrap/merge-authors/lay-translator/research-integrate, ThesisStudio's `CLAUDE.md`) + `templates/overlay/` (9: `.gitattributes` + `inject-marker.sh`) + `examples/demo-article/` (9). **This is scaffold-OUTPUT data, not plugin logic** — the orchestrator `cp -R`s it into the user's project at scaffold time. port.py **missed it entirely** (`files_copied_verbatim: []`) because it's a nested `templates/` dir at the plugin root, not a skill's `references/`/`schemas/` — outside everything the script scans.

**Carried verbatim** into `.agent/templates/full/`, `.agent/templates/overlay/`, `.agent/examples/demo-article/`. Crucially: **repointed nothing inside it.** The template's own `CLAUDE.md` and `.claude/skills/` are *the scaffold's files* (ThesisStudio targets Claude Code users who get a CLAUDE.md) — they're cross-tool context inside carried data, not port surfaces. The render scripts (`templates/full/scripts/*.js` + `lib/*.js`) have **zero plugin-path constants** (no `CLAUDE_PLUGIN_ROOT`, no `~/.claude`) — they operate on the scaffolded project's own dirs at runtime — so nothing to re-model. Byte-compile-verified all 11 template JS files with `node --check` (exit 0). The only adaptation was in the **orchestrator workflow** (plugin logic, not template data): re-modeled `PLUGIN_DIR` resolution from "walk up two levels from `skills/vibe-thesis/SKILL.md`" to "resolve `.agent/` relative to workspace root" (the template paths are now `.agent/templates/full/` etc.), and added a template-carry note documenting the verbatim-`CLAUDE.md` + copy-to-`AGENTS.md` step.

**Lesson (new):** a plugin can bundle a whole scaffold tree (its OUTPUT product) at the plugin root, separate from any skill's sub-dirs. port.py only scans skill `references/`/`schemas/`, so a root-level `templates/` / `examples/` payload is invisible to it. **Carry it verbatim** — it's data the plugin emits, not behavior the agent runs. Repoint ONLY genuine plugin paths in the orchestrator that *reach into* it (`PLUGIN_DIR` / `${plugin}/templates/...` refs); leave the scaffold's own files (including a `CLAUDE.md` and `.claude/skills/` the scaffold produces) untouched — those are the scaffold's cross-tool context, not your port surface. Byte-compile any carried scripts as the verify gate.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** No `schedule`-plugin dependency. (The architecture's "future `/vibe-thesis-refresh-templates`" is a manual backlog item, not a cron.)
2. **`--silent` sidecar calls:** **None.** The voice pipeline (`voice` → `smooth` → `guard`) is **explicitly non-composing** — "each skill stands alone; smooth doesn't invoke voice or guard." The orchestrator *dispatches* sub-skills (bootstrap, voice) sequentially in scaffold mode, but as ordinary dispatch with the user in the loop, not silent structured-return sub-workflow calls. Open-question #2 is a non-issue.
3. **Workflow name collisions:** **RESOLVED — namespacing.** Router `/vibe-thesis` (bare, eponymous) + 6 `/vibe-thesis-<cmd>`. The same-named-pair doubled-slash (`/vibe-thesis-vibe-render`) was the local hazard — collapsed to `/vibe-thesis-render`.
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.2.0`. **Nothing reads it** — vibe-thesis has no loggers. Pure bookkeeping; agent.json `port.notes` updated to say so.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key. (The `.husky/pre-commit`/`pre-push` inside `templates/full/` are **git hooks in the scaffold** — carried verbatim as scaffold data, not plugin hooks.) **builder.json: None** — the plugin reads no `~/.claude/profiles/builder.json`; voice is captured via the interview + AGENTS.md block, not a global profile. No profile repoint required.

### Mechanical (port.py got it right)

- The **2 same-named pair merges** (`vibe-render`, `vibe-status`) into full-body workflows (description from command, body from skill) — only the doubled-prefix slash needed collapsing. The router classified correctly as the bare `/vibe-thesis`. The 25 `CLAUDE.md` → `AGENTS.md` repoints across all bodies (marker detection, mode reads, voice write/read target). 55 `plugin-namespaced-slash` repoints (`/vibe-thesis:guard` → `/vibe-thesis-guard`, etc. — including inside the cross-named-pair skill bodies, so when collapsed they were already de-namespaced). 2 `claude-home-generic`. agent.json minted from plugin.json (0.2.0).

### Needed thought (the 20%)

- **The three cross-named-pair merges + duplicate-collapse** (Error class 1) — the headline. Read all 5 commands + 7 skills to confirm each pairing by delegation-target + declared-trigger, merged each to one workflow, deleted the duplicate surfaces.
- **The `audit` skill→workflow promotion on the `user-invocable: true` signal** (Error class 2) — promoted the mis-defaulted skill, dropped the skill-only frontmatter fields, fixed the H1 + refs.
- **The doubled-prefix collapse** (`/vibe-thesis-vibe-render` → `/vibe-thesis-render`, same for status) — H1s, descriptions, and all cross-refs across 4 files.
- **The rules-file write/read pair verification** (voice writes AGENTS.md, smooth reads it) + the description straggler + the over-namespaced prose straggler.
- **The bundled scaffold-template carry** (127 files verbatim) + the `PLUGIN_DIR` re-model in the orchestrator + the verbatim-`CLAUDE.md`/copy-to-`AGENTS.md` framing + byte-compiling the template scripts.
- **The no-guide AGENTS.md synthesis** — no `guide` skill, no persona reference docs. Synthesized a lean AGENTS.md from the orchestrator's load-bearing rules + the shared posture across the voice pipeline: the ThesisStudio three-pillar stance, the Honest-Limits/self-review-tone failure mode, voice posture, the AGENTS.md output contract, the bundled-assets map, and the hard rules (round-trip honesty, sibling-repo guard, don't-fork-ThesisStudio, advisory-guard, no-telemetry). No invented persona (keystone's "no guide ≠ no AGENTS.md" lesson).

### PORT-RUNNER.md gaps hit this port

1. **Step 2b's merge is same-name-only; cross-named thin-wrapper pairs aren't covered.** PORT-RUNNER step 2b describes "command + same-named skill → one workflow." vibe-thesis's `guard`/`smooth`/`voice` commands delegate to differently-named skills (`synthesis-guard`/`synthesis-smooth`/`voice-synthesis`) — the merge missed all three, emitting doubled surfaces. vibe-test flagged the cross-named case for the *router* only; this port proves it happens for **ordinary commands at scale**. **Recommend:** extend step 2b — "the merge must also catch **cross-named** pairs: a thin command whose body delegates to a *differently-named* skill (`Use the **X** skill`). Resolve the delegation target X and merge command+X even when names differ; the workflow slash is the **command's** name. The tell that port.py missed one: it emits BOTH a `/<plugin>-<cmd>` stub AND a `/<plugin>-<skillname>` full-body workflow for the same feature — collapse to one."
2. **No step reads `user-invocable` frontmatter.** PORT-RUNNER step 3 (edge classifications) leans on description phrasing + trigger evidence + grammatical role (bootstrap/vitals). It never mentions the **explicit `user-invocable: true` field** that some plugins' skills carry. `audit` defaulted to skill purely because the classifier judged phrasing, ignoring the structured field that already answered the question. **Recommend:** add to step 3 (and as a port.py pre-check) — "Read each skill's frontmatter for `user-invocable`. `true` → workflow (explicit author declaration, overrides description phrasing). `false` → internal *unless* it's a command/intent merge target (the router case). Absent → fall back to phrasing+trigger. This is the cleanest classification signal when present — read it first."
3. **No step for a root-level bundled scaffold/template payload.** PORT-RUNNER step 2b's defensive note covers a *merged skill's* `references/`/`schemas/`. It has nothing for a plugin that bundles a whole **scaffold tree at the plugin root** (`templates/`, `examples/`) — its OUTPUT product. port.py doesn't scan there, so it's invisible (`files_copied_verbatim: []`). This is distinct from the vibe-walk/vibe-doc *helper-scripts* carry (those are plugin behavior; this is plugin output-data). **Recommend:** add a step — "If the plugin has a root-level `templates/` / `examples/` payload (a scaffold it produces), carry it **verbatim** into `.agent/templates/` / `.agent/examples/`. Repoint ONLY the orchestrator's reach-into refs (`PLUGIN_DIR`, `${plugin}/templates/...`); leave the scaffold's own files untouched — including any `CLAUDE.md`/`.claude/` it ships (those are the scaffold's cross-tool context, carried data, not port surfaces). Byte-compile any carried scripts as the verify gate. port.py should detect + carry + flag a root `templates/` dir."
4. **port.py's report mis-described the commands as non-thin.** The report's `commands_merged.command_only_workflows` listed `guard`/`smooth`/`voice` as command-only — but they DO have parallel (cross-named) skills, so they're not command-only at all. The report's framing ("Each command + same-named skill merged") is silent on the cross-named case, so a finishing pass trusting the report would ship the duplicates. **Recommend (reinforces #1):** the report should flag *unmatched commands whose body delegates to a skill by name* as **likely cross-named pairs needing manual merge**, not silently bucket them as command-only.

Otherwise PORT-RUNNER.md carried the rest cleanly — the namespacing verification, the H1/inline-trigger cleanup, the CLAUDE.md→AGENTS.md output-vs-context discipline (keystone), the no-guide AGENTS.md synthesis (keystone), the leftover-grep, and the open-questions re-check all mapped to existing steps. No guide split (no guide), no scripts-carry-as-plugin-logic (the only scripts are scaffold data), no loggers, no hooks, no evolve, no builder.json — the judgment 20% this port was entirely the commands+skills reconciliation (cross-named at scale + the `user-invocable` signal + duplicate-collapse) and the bundled-scaffold carry.

## thesis-engine@0.2.1 (ported 2026-05-25)

**Shape:** the **eponymous-main-defaulted-to-skill** case — the cleanest instance yet of port.py doubling the main entry. Source = 4 commands (`blog`, `discover`, `run`, `write`) + **1 skill** (`thesis-engine`, the eponymous orchestrator with `scripts/` + `references/` + an `assets/` dir) → **5 workflows + 0 skills** + AGENTS.md + agent.json + carried scripts + carried references. No hooks, no loggers, no builder.json, no evolve, no guide skill, no sidecars. port.py emitted **4 workflows + 1 skill** with one headline error the finishing pass corrected.

| Source surface | Source kind | Port target | Why |
|---|---|---|---|
| `thesis-engine` **skill** (name == plugin, orchestrator, no `/x` phrasing) | eponymous main | **workflow** `/thesis-engine` (the **router**) | **Headline error — see below.** The skill IS the Discover→Gather→Adapt orchestrator; it ports to the bare router, not the doubled `/thesis-engine-thesis-engine`. |
| `run` command (delegates to the skill, Stages 1+2) | thin stage wrapper | **workflow** `/thesis-engine-run` | command-only by port.py's reckoning (no `run` skill); body delegates to the `/thesis-engine` router. |
| `discover` command (Stage 1) | thin stage wrapper | **workflow** `/thesis-engine-discover` | same. |
| `write` command (Stage 2) | thin stage wrapper | **workflow** `/thesis-engine-write` | same. |
| `blog` command (Stage 3) | thin stage wrapper | **workflow** `/thesis-engine-blog` | same. |

**Count: 5 workflows + 0 skills.** Dropped the mis-emitted `thesis-engine-thesis-engine` skill dir after promoting its body to the router; carried its `scripts/` → `.agent/scripts/` and `references/` → `.agent/references/`.

### The headline error — eponymous-main defaulted to a doubled skill (NEW lesson, the brief's flagged case)

port.py classified the `thesis-engine` skill as a **skill** named `thesis-engine-thesis-engine` ("no real slash trigger or user-says phrasing — defaulted to skill"). It's wrong twice over, and it's a *distinct fourth form* of the eponymous-router edge:

1. **It's the eponymous main entry.** Its `name` == the plugin name, its description is the orchestrator blurb ("a research-feeder pipeline… Discover → Gather → Adapt"), and **all four commands delegate into it** ("Invoke the `thesis-engine` skill and execute Stage X from `${CLAUDE_PLUGIN_ROOT}/skills/thesis-engine/SKILL.md`"). It's not loaded-by-something — it IS the thing the commands call.
2. **The classifier defaulted it to skill because it has no `/x` slash phrasing** (its description is pure capability blurb + semantic triggers — "use this skill whenever the user mentions…"). And **the router-rename only fires on workflows** — but the classifier never made it a workflow, so the eponymous-→-router collapse never got a chance to run. port.py's name-equals-plugin router check is downstream of the workflow/skill split; a skill that the split sends to the skill branch is invisible to it. Result: the doubled `thesis-engine-thesis-engine` skill, the absurd `/thesis-engine-thesis-engine` slash it implies.

**Fix:** reclassified the skill to the **bare router workflow** `.agent/workflows/thesis-engine.md` → `/thesis-engine`. Confirmed against the SKILL.md it's the main orchestrator (the three-stage engine; Stage gates; the Repeatable Run Protocol; the cadence table all live in it). Swapped frontmatter (dropped `name` + `version`, description-only). Dropped the `thesis-engine-thesis-engine` skill dir entirely (0 skills end state). Fixed agent.json's `name` (`thesis-engine-thesis-engine` → `thesis-engine`) and the AGENTS.md title.

**Lesson (new, the fourth eponymous form):** the eponymous-router edge now has **four forms** — (1) keystone: skill name == plugin name, user-invoked, port.py made it a `<plugin>-<plugin>` *skill* (caught by name-equals-plugin); (2) vibe-test: a `<plugin>` command + a cross-named `router` skill; (3) vibe-wrap: a lone skill whose *declared trigger* is `/<plugin>` but whose filename isn't `<plugin>`; (4) **thesis-engine: the eponymous skill (name == plugin) that the classifier sends to the SKILL branch because it has no slash-trigger phrasing — so the name-equals-plugin router check (which port.py only runs on the workflow branch) never sees it, and it doubles to `<plugin>-<plugin>` skill.** The first three were promoted-to-workflow-then-mis-namespaced; the fourth never even reached the workflow branch. **port.py gap:** the `name == plugin` router check must fire on the eponymous skill **regardless of which classification branch it lands in** — a skill whose `name` equals the plugin name is the router, full stop, even when its description carries zero slash phrasing. Catch it in the finishing pass: any `<plugin>-<plugin>` skill dir port.py minted is the eponymous main → promote to `.agent/workflows/<plugin>.md`, drop the doubled dir.

### The thin-stage-command reconciliation (the four sub-commands)

The 4 commands (`run`/`discover`/`write`/`blog`) are **thin stage wrappers** — each delegates into the *same* eponymous skill for a *stage subset*: `run` → Stages 1+2 (full), `discover` → Stage 1, `write` → Stage 2, `blog` → Stage 3. They have **no parallel skills** (the only skill is the eponymous orchestrator), so port.py correctly bucketed them as command-only → workflows. The finishing-pass judgment: they're command-only in *count*, but **not standalone** — their real body is "invoke the orchestrator for stage X." Since the orchestrator collapsed to the `/thesis-engine` router, every delegation line was repointed from "Invoke the `thesis-engine-thesis-engine` skill / read `.agent/skills/thesis-engine-thesis-engine/SKILL.md`" → "execute Stage X from the `/thesis-engine` router workflow (`.agent/workflows/thesis-engine.md`)." Verified each carried its real body (the Stage gates, the argument defaults, the ingest hints, the `computer://`-link close) — they did; only the delegation target needed repointing. This is the inverse of vibe-doc's command-only `status` (which had to be *rebuilt* from the command body): here the commands are real but **delegate to the router**, so the implementation lives in one place and the stage workflows are thin, faithful to the source's command-delegates-to-skill design.

**Lesson (new):** when *every* command delegates into a single eponymous orchestrator skill (stage-subset delegation), the orchestrator → router and the commands → thin stage workflows that **delegate to `/<plugin>`**. Don't inline the orchestrator body into each stage workflow — keep one implementation in the router, repoint each command's delegation target from the (now-dropped) doubled skill to the router. The `--blog` flag on `/thesis-engine-run` and the standalone `/thesis-engine-blog` both reach Stage 3 — preserve both paths.

### The blog-output-path namespacer over-reach (a real miss caught)

port.py's namespacer rewrote a **directory path** as if it were a slash-ref: the blog workflow's output destination `<run>/blog/02_DRAFTS/...` became `<run>/thesis-engine-blog/02_DRAFTS/...` (it matched `blog` against the `/blog`→`/thesis-engine-blog` rename and hyphen-joined it onto the preceding `<run>/`). This is the **mirror of vibe-doc's `npx vibe-doc check` → `npx vibe-doc-check` CLI mis-repoint** — the namespacer caught a bare word that *happened to equal a command name* inside a non-slash context (here a filesystem path segment). Fixed by hand back to `<run>/blog/02_DRAFTS/`. The BlogStudio ingest path is `blog/02_DRAFTS/<dated-slug>/`; the directory is literally named `blog`, not the slash command. **Recommend (reinforces vibe-doc gap #2):** the namespacer should exclude path-segment contexts (`<run>/blog/`, `.../blog/02_DRAFTS`) from the slash-rename — a bare command word inside a `/`-delimited filesystem path is not a slash-ref. Verify any output/ingest path whose final segment equals a command name survived un-hyphenated.

### Scripts + references carry out of the collapsed eponymous skill (the wrap lesson, applied)

The eponymous skill carried `scripts/package_skill.py` + `references/domain-feeds.md` + `assets/CLAUDE_PROJECT_INSTRUCTIONS.md`. When the eponymous skill collapses to a single-file router workflow, **its scripts/references location is lost** (the wrap lesson — single-file workflows have no sub-dirs). port.py carried only `scripts/` (into the doomed `thesis-engine-thesis-engine` skill dir); with 0 skills end state, both `scripts/` and `references/` needed a home **outside** any skill dir:

- `scripts/package_skill.py` → `.agent/scripts/`. **Re-modeled its `__file__`-relative constant** (the wrap lesson's under-flagged half): source `SKILL_DIR = Path(__file__).parent.parent` resolved `skills/thesis-engine/scripts/` → the skill root (2 up); in the flat `.agent/scripts/` layout the bundle root is `.agent/` (1 up), so `.parent.parent` → `.parent` (now `BUNDLE_DIR = Path(__file__).parent` = `.agent/`). Without the re-model the packager would zip the entire ports repo root. **Byte-compiled `.agent` (`python -m compileall`, exit 0)** as the verify gate. (Note: `package_skill.py` is a *packaging/dev* helper, not a workflow-runtime script — no workflow invokes it — but the brief mandated carrying `scripts/`, so it's carried faithfully and re-modeled.)
- `references/domain-feeds.md` → `.agent/references/` (a port-level references dir, mirroring `.agent/scripts/`). It's the situational discovery-feed data Stage 1 occasionally consults — the "stays as a file" category. With 0 skills, there's no skill dir to keep it in, so it lives flat under `.agent/references/`. The router's two refs to it were repointed (`.agent/skills/thesis-engine/references/...` → `.agent/references/...`).
- `assets/CLAUDE_PROJECT_INSTRUCTIONS.md` → **deliberately NOT carried.** It's a Claude-Desktop **project-instructions paste block** describing the *removed v0.1 behavior* ("writes full academic thesis papers 2,500–4,000 words", "Section 1.3", "THESIS.md template" — all of which the v0.2.1 SKILL explicitly says is gone). It's stale, Claude-Desktop-specific, cross-tool-only, and references nothing the port runs. Same call as wrap's npm-install artifacts (`copy-templates.js`/`postinstall.js`) — dropped as a non-runtime, tool-specific dev artifact.

**Lesson (new):** the eponymous-skill-collapses-to-router case loses **both** `scripts/` AND `references/` (and any `assets/`) — and with a **0-skill** end state there's no skill dir to relocate references into. Put situational reference data at a port-level `.agent/references/` (parallel to `.agent/scripts/`), repoint the router's refs to it, and judge each non-`scripts`/`references` sub-dir (`assets/`) on whether it's runtime-load-bearing — a stale cross-tool paste block is a drop, not a carry.

### The no-guide AGENTS.md synthesis (keystone/sec/insights lesson, applied)

No `guide` skill — port.py wrote an all-TODO AGENTS.md skeleton ("no guide skill detected — supply persona/posture by hand"), and it had pre-scaffolded a `## Self-evolving framework — session + friction logging` section with a `~/.gemini/antigravity/data/thesis-engine-thesis-engine/` log-path repoint. **Dropped that section entirely** — thesis-engine has no loggers, so there's no log path and no framework wiring to document (the skeleton scaffolds it unconditionally; it's a TODO to *delete* when the plugin has no loggers, not fill in). Synthesized the always-on layer from the SKILL body + the command bodies: **what the plugin is** (research feeder, not drafter), **research-feeder posture** (feed don't write, human owns topic selection, dated-run-folder-not-live-studio, mandatory quality gates), **the five research axes**, the **BibTeX/Pandoc output contract + verify-before-citing** (the load-bearing safety rule — every entry carries the verify note), **the Smart Brevity blog adapter** (inline links NOT Pandoc — a blog is not a paper), **the vibe-thesis/ThesisStudio pairing** (engine feeds, vibe-thesis drafts; hand off, don't reimplement drafting), **scheduling** (manual-only), **MCP logging** (best-effort), **hard rules**, and **voice** (builder-to-builder, specifics over adjectives, say "verify this one" plainly). **No invented persona** — there's no persona in the source, so none manufactured (keystone's "no guide ≠ no AGENTS.md" rule).

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** the SKILL's cadence table lists a weekly scheduled task (`weekly-thesis-engine`, Mondays 8 AM). **Manual-only in the port** — no `schedule`-plugin dependency in the source (the table is documentation of an external scheduler, not a wired cron), and no Antigravity cron primitive invented. Documented in AGENTS.md § Scheduling + the README: run `/thesis-engine-run --domain ai_ml --auto` on demand. (Antigravity 2.0 reportedly ships scheduled background tasks per the vibe-wrap research, but thesis-engine doesn't wire one — left as a documented manual-only with a "wire it then" note if confirmed.)
2. **`--silent` sidecar calls:** **None.** Zero `--silent` in the source. The 4 commands *dispatch* into the one orchestrator for a stage subset — ordinary delegation with the user in the loop (topic table → approve → gather), not silent structured-return sub-workflow calls. Open-question #2 is a non-issue.
3. **Workflow name collisions:** **RESOLVED — namespacing.** Router `/thesis-engine` (bare, eponymous) + 4 `/thesis-engine-<cmd>`. The eponymous main collapsed to the bare router (no `/thesis-engine-thesis-engine`).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `0.2.1`. **Nothing reads it** — thesis-engine has no loggers. Pure bookkeeping; agent.json `port.notes` says so.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key. **builder.json: None** — the plugin reads no `~/.claude/profiles/builder.json` (no global profile use anywhere in source). No profile repoint required.

### Repoints

The only `${CLAUDE_PLUGIN_ROOT}` hits were the 4 command delegation lines (`${CLAUDE_PLUGIN_ROOT}/skills/thesis-engine/SKILL.md`) — port.py repointed them to `.agent/skills/thesis-engine-thesis-engine/SKILL.md`, then the finishing pass repointed them again to the `/thesis-engine` router (the doubled skill is gone). 9 `plugin-namespaced-slash` + 4 `plugin-root-generic` per the report. The 1 `claude-home` leftover the report flagged (the skeleton AGENTS.md's log-path repoint note) **disappeared** when the all-TODO AGENTS.md was rewritten clean (the no-loggers plugin has no log path to note). Zero `~/.claude`, zero `.claude-plugin`, zero `CLAUDE_PLUGIN_ROOT`, zero `CLAUDE.md`, zero doubled prefixes in the finished port. The `C:\Users\estev\Projects\ThesisStudio\` / `BlogStudio\` absolute paths in the bodies are the user's **own studio locations** (ingest targets), not Claude paths — left exactly as-is (the source had them; they're where the run folder gets dropped).

### Mechanical (port.py got it right)

- Classified the 4 commands as command-only workflows correctly (no parallel skills); namespaced them `/thesis-engine-<cmd>` (the report's `workflow_renames`); the `${CLAUDE_PLUGIN_ROOT}` → relative `.agent/...` repoint on the delegation lines; agent.json minted from plugin.json (0.2.1); carried the skill's `scripts/` verbatim.

### Needed thought (the 20%)

- **The eponymous-main-defaulted-to-skill reclassification** (above) — the headline. Promoted the doubled `thesis-engine-thesis-engine` skill → the `/thesis-engine` router; dropped the skill dir; fixed agent.json name + AGENTS.md title.
- **The thin-stage-command reconciliation** (above) — repointed all 4 delegation lines from the doomed skill to the router; verified each carried its real stage body, not just a "read the SKILL" stub.
- **The blog-output-path namespacer over-reach fix** (above) — `<run>/thesis-engine-blog/02_DRAFTS/` → `<run>/blog/02_DRAFTS/`.
- **The scripts + references carry out of the collapsed eponymous skill** (above) — `.agent/scripts/` + `.agent/references/`, the `__file__`-constant re-model + byte-compile, the `assets/` drop.
- **The no-guide AGENTS.md synthesis** (above) — folded the always-on facts from the SKILL + command bodies; deleted the skeleton's unconditional self-evolving-framework section (no loggers); invented no persona.

### PORT-RUNNER.md gaps hit this port

1. **The eponymous router check doesn't fire when the eponymous skill lands in the SKILL branch.** PORT-RUNNER step 3 + step 6.5 cover the eponymous cases where the skill was *promoted to a workflow* then mis-namespaced (keystone/wrap). thesis-engine's eponymous skill **never reached the workflow branch** — the classifier sent it to SKILL (no slash phrasing), so the name-equals-plugin router check (which port.py runs on workflows) never saw it, and it doubled to a `<plugin>-<plugin>` *skill*. **Recommend:** extend step 3 / step 6.5 — "The `name == plugin` router check must fire **regardless of classification branch**: a skill whose `name` equals the plugin name is the router even with zero slash-trigger phrasing. In the finishing pass, treat ANY `<plugin>-<plugin>` skill dir port.py minted as the eponymous main → promote to `.agent/workflows/<plugin>.md`, drop the doubled dir. This is the fourth eponymous form (the prior three were promote-then-mis-namespace; this one is mis-classify-then-double)." And the port.py guard: run the name-equals-plugin check **before** the workflow/skill split commits, not after.
2. **Namespacer mangles output/ingest paths whose final segment equals a command name.** `<run>/blog/02_DRAFTS/` → `<run>/thesis-engine-blog/02_DRAFTS/` — a filesystem path segment caught by the `/blog` slash-rename. This is the vibe-doc `npx vibe-doc check` CLI mis-repoint in a different costume (a bare command word in a non-slash `/`-delimited context). **Recommend (reinforces vibe-doc gap #2):** the namespacer must exclude `/`-delimited filesystem-path contexts; the finishing pass must verify any output/ingest path whose final segment equals a command name survived un-hyphenated.
3. **The skeleton scaffolds a self-evolving-framework section unconditionally — delete it for no-logger plugins.** port.py wrote a `## Self-evolving framework — session + friction logging` section with a log-path repoint into the all-TODO AGENTS.md even though thesis-engine has no loggers. A finishing pass that fills TODOs rather than deleting them would document a non-existent log path. **Recommend:** a note under step 1 — "the skeleton scaffolds a session/friction-logging section + log-path repoint unconditionally. If the plugin has no loggers (no `session-logger`/`friction-logger` skills), **delete** the section — don't fill it. The log path is real only if something writes it."
4. **References have no home in a 0-skill port.** PORT-RUNNER step 2 says situational reference docs "stay in the guide skill." A no-guide, 0-skill plugin whose eponymous skill carried a `references/` dir has nowhere skill-side to put it. **Recommend (extends the scripts-carry step):** "if the eponymous skill collapses to the router and the port has 0 skills, put its `references/` at a port-level `.agent/references/` (parallel to `.agent/scripts/`) and repoint the router's refs there. Judge non-`scripts`/`references` sub-dirs (`assets/`) on runtime load-bearingness — a stale cross-tool paste block is a drop."

Otherwise PORT-RUNNER.md carried the rest cleanly — the command-only → workflow mapping (step 2b), the namespacing verification, the no-guide AGENTS.md synthesis (keystone), the leftover-grep, the scripts-carry + `__file__`-re-model + byte-compile gate (wrap), and the open-questions re-check all mapped to existing steps. The residue this port was the genuinely new fourth eponymous form (mis-classify-then-double, invisible to the workflow-branch router check) + the path-segment namespacer over-reach.


## vibe-cartographer@1.9.1 (ported 2026-05-25) — THE FINALE (port 12/12)

**Shape:** the family's **heaviest plugin and the finale** — 13 commands + 17 skills + a root-level `architecture/` doc set → **13 workflows + 4 skills** + AGENTS.md + agent.json + carried scripts + carried architecture + carried cutters. This is the plugin that *builds the others* and the **Cart-detection target** the prior 11 ports' composition refs all point at. Almost every accumulated lesson in this cookbook applied — and they applied **cleanly**, which is the headline: the residue was one cross-named-pair collapse and the always-known carry/re-model gaps, not new edges. The pipeline matured exactly as intended.

| Source surface | Source kind | Port target | Why |
|---|---|---|---|
| 12 same-named cmd+skill pairs (build, checklist, coder-voice, evolve-cart, iterate, onboard, prd, reflect, scope, spec, tend, vitals) | thin wrapper + impl skill | **workflows** `/vibe-cartographer-<cmd>` (evolve-cart → `/vibe-cartographer-evolve`) | step-2b merge — **all 12 mechanical, zero hand-reclassification** |
| `friction` cmd + `friction-log` skill | **cross-named** pair | **workflow** `/vibe-cartographer-friction` | **Error 1 — the collapse, see below** |
| `decay`, `session-logger`, `friction-logger` | internal | **skills** `vibe-cartographer-<x>` | loaded, never typed |
| `guide` | shared-behavior | **split** → AGENTS.md + skill `vibe-cartographer-guide` | the largest guide split in the family |

**Count: 13 workflows + 4 skills.** No bare router (the commands ARE the surface, like taker — no eponymous `vibe-cartographer` command). port.py emitted 14 workflows + 4 skills; the finishing pass collapsed friction/friction-log to land 13 + 4.

### Error 1 — the friction / friction-log cross-named collapse (the one real reconciliation)

This is vibe-test's Error 1 / vibe-thesis's Error class 1 again, in its now-familiar form: the **`friction` command** (the read-only log VIEWER, `commands/friction.md`, a thin "Use the **friction-log** skill" wrapper) crossed with the **`friction-log` skill** (`skills/friction-log/SKILL.md`, the full viewer implementation). Different names, so port.py's same-name step-2b merge missed it: it emitted `/vibe-cartographer-friction` as a **command-only** thin stub (still pointing at `skills/friction-log/SKILL.md`) AND `/vibe-cartographer-friction-log` as the full-body workflow. Two slashes, one front door.

**The critical disambiguation the brief flagged:** `friction-log` (the VIEWER skill, the impl of the `friction` command) is **NOT** `friction-logger` (the internal Pattern #6 capture skill). Verified by reading both — `friction-log` renders a banner report and writes nothing; `friction-logger` appends entries via the atomic helper. The collapse merges `friction` + `friction-log` into one `/vibe-cartographer-friction` workflow (the `friction-log` body under the `friction` command's clean description); `friction-logger` stays an internal skill. Got the right two. **Lesson reinforced (not new):** the cross-named-pair merge keys on the command's delegation target + the skill's declared trigger; the `-log`/`-logger` near-collision is exactly where a name-keyed merge would pick the wrong sibling — read both bodies, match on "is this the impl of that command's slash" vs "is this the internal append helper."

### The guide split — the largest in the family (the big one)

Cart's `guide` SKILL is ~430 lines and carries the **entire** process knowledge: the 6 personas (Professor/Cohort/Superdev/Architect/Coach/System-default) with a full behavior table, Learner/Builder mode tables, deepening-round mechanics, the Pattern #13 anchored-complements table + live-discovery heuristics, hard rules, interaction rules, the unified-profile ownership contract, AND the Cart-detection contract the other plugins rely on. Like sec/test, the always-on content lives in the **SKILL body**, not in `references/*.md` (the skeleton came up all-TODO with "no matching reference doc detected" — the 6 reference docs are all per-command agent references, situational).

**The split:**
- **Always-on → AGENTS.md prose:** coach persona + tone, the persona MODEL (6 personas named, "read persona at workflow start, persona=voice/mode=pacing"), the mode MODEL (Learner/Builder intro), posture (guard rails, process notes, embedded feedback, client-aware handoff, active engagement), interaction rules (one-question-at-a-time, free-form, speech-to-text, collision check, deepening intro), the composition POSTURE (defer/announce/log/never-defer/privacy + the Antigravity detection-mechanism repoint + the "Cart IS the detection target" note), the unified-profile ownership contract + atomic-write rule, the self-evolving-framework wiring (session/friction/decay), the coder-voice output contract, the hard rules (the 4 Tier-1 hygiene rules folded in), and voice.
- **Situational → kept skill-side as TABLES + mechanics:** the per-persona behavior TABLE, the Learner/Builder dimension TABLES, the deepening-round mechanics, the anchored-complements TABLE + live-discovery heuristics, the build-mode behavior, plus all 6 `references/*.md`, the 4 schemas, 6 templates, and the carried cutters. Rewrote `vibe-cartographer-guide/SKILL.md` from ~430 lines to a ~190-line thin index: a "where the always-on rules live" map table pointing at AGENTS.md sections, a "situational reference docs" map table pointing at the kept files, then the tables themselves.

This is the always-on/situational split at its most demanding — the model (always-on) vs the lookup table that implements it (situational) had to be cleanly separated for personas, modes, AND composition, each of which had both halves. The judgment rule held: the *rule* ("read persona, adopt its voice") is always-on; the *table* ("Professor = patient, leads with why") is situational.

### Architecture docs — the root-level carry (the thesis-template lesson, hit again)

Cart ships a plugin-root `architecture/` dir (default-patterns.md, example-architecture.md, README.md) that `/vibe-cartographer-spec` reads for stack defaults when the builder has none. **port.py missed it entirely** — same class as the vibe-thesis bundled-template + vibe-test `templates/` + vibe-walk scripts gaps (port.py's verbatim-carry only walks the guide skill's sub-dirs, not plugin-root dirs). Carried `architecture/` to `.agent/architecture/`, repointed every `architecture/default-patterns.md` body ref to `.agent/architecture/default-patterns.md` (in spec.md, onboard.md, the guide SKILL, and the guide's spec-patterns.md reference), and **namespaced the slash refs inside `architecture/README.md`** — port.py never processed the dir, so its `/onboard`, `/spec`, `/checklist`, `/build` mentions were still bare (51 of the leftover bare-slash hits were all in this one un-processed file). **Lesson reinforced:** any plugin-root dir beyond `commands/`/`skills/` (here `architecture/`; thesis had a bundled scaffold; walk had `scripts/`) is invisible to port.py — diff the source plugin root against the skeleton, carry what the workflows read, and remember the carried files still need the full namespacing + path-repoint pass (port.py touched none of their strings).

### The cutters sub-dir carry (the vibe-test templates lesson)

The `coder-voice` skill carried a `cutters/` sub-dir (carmack, dhh, bret-victor, julia-evans preset voices). Because `coder-voice` merged into a single-file workflow, the single-file-workflow branch dropped the sub-dir (same mechanism that dropped wrap's `wrap/scripts/`). Carried `coder-voice/cutters/*` to `.agent/skills/vibe-cartographer-guide/cutters/` (co-located with the other situational reference data the guide skill owns) and repointed the workflow's `skills/coder-voice/cutters/<preset>.md` refs to `.agent/skills/vibe-cartographer-guide/cutters/`. **Lesson reinforced (vibe-test gap #3):** a merged skill's sub-dirs (`cutters/`, `templates/`, `scripts/`, `references/`) are dropped by the single-file-workflow branch — carry them to a surviving skill or a port-level dir and repoint.

### builder.json — the heaviest user in the family (55 repoints), confirmed load-bearing

Cart **owns** the builder profile. `/vibe-cartographer-onboard` creates/migrates it, `/vibe-cartographer-reflect` updates it, `/vibe-cartographer-decay` re-validates stale fields, `/vibe-cartographer-vitals` check #3 schema-validates it, and every workflow reads `shared.preferences.persona` from it. port.py did **55 builder-profile repoints** (`~/.claude/profiles/builder.json` to `~/.gemini/profiles/builder.json`) — the most of any port. The finishing pass caught the stragglers port.py's body-pass missed (the vibe-doc "stale strings inside carried files" lesson): the `builder-profile.schema.json` `description` field, the `decay` SKILL's frontmatter description, and confirmed the carried `atomic-*.js` scripts hold **no** internal profile constants (they take the target path as `argv[2]` — fully path-driven, unlike wrap's `__file__`-relative loggers, so no script-internal repoint was needed here). The atomic helpers byte-check clean (`node --check`, the JS equivalent of wrap's `compileall` gate).

### coder-voice writes the rules file — AGENTS.md, not CLAUDE.md (the keystone/thesis-voice lesson)

`/vibe-cartographer-coder-voice` **writes** the `## CODER VOICE SYNTHESIS` block to the project rules file — keystone's whole-job lesson and vibe-thesis's voice-workflow lesson, applied here to one workflow inside the larger plugin. On Claude Code the target was `~/.claude/CLAUDE.md`; in the port the file it WRITES is `~/.gemini/antigravity/AGENTS.md`. port.py flipped the body refs (part of the 24 claude-md repoints) but left the **`description` frontmatter** saying `~/.claude/CLAUDE.md` (the leftover the report flagged) and two prose lines saying "loads on every Claude Code session" — fixed all three to AGENTS.md / Antigravity. Verified the output contract reads semantically right: it WRITES AGENTS.md, may READ a CLAUDE.md for cross-tool context. The cutters it installs are the preset bodies for that same AGENTS.md block.

### CLAUDE.md handling (24 repoints) — output-vs-context, mostly output

Unlike keystone (whose whole job is the rules file) or vibe-doc (which documents host CLAUDE.md as a classification signal), Cart's CLAUDE.md references are mostly the **project rules file it operates on** — repointed to AGENTS.md throughout (the coder-voice output target, the session-logger/decay profile-context reads). The 3 leftover `~/.claude` hits the report flagged were: the decay SKILL description, the coder-voice description, and AGENTS.md — the first two were misses (fixed), the AGENTS.md hits are the **intentional provenance notes** (the Pattern #11 repoint note, the log-location note, the coder-voice-output note — each names the old `~/.claude` path on purpose to document the repoint, per PORT-RUNNER step 9). Final `~/.claude` count: 3, all intentional AGENTS.md provenance.

### The vitals self-test re-model (the vibe-walk/vibe-test lesson, biggest instance)

`/vibe-cartographer-vitals` is a 710-line structural self-test that hardcodes the SOURCE layout in its Runtime Paths table and 8 checks: it enumerated `plugins/vibe-cartographer/skills/**/SKILL.md`, `commands/*.md`, read `plugin.json`, and scanned each command SKILL's "Friction Logging" section. Re-modeled the whole self-test for the `.agent/` layout (the self-test IS its own port surface, per vibe-walk): Runtime Paths table to `.agent/workflows/*.md` (13) + `.agent/skills/*/SKILL.md` (4) + `.agent/scripts/` + `.agent/architecture/` + `.agent/agent.json`; check #1 SKILL-enumeration to workflow+skill enumeration (no `commands/*.md` — they merged); check #6 friction-consistency now reads the "Friction Logging" sections from the **workflows** (not skills), command name derived from the workflow filename stem; checks #2/#3/#4/#8 schema+template+guide paths to `.agent/skills/vibe-cartographer-guide/...`; the version-read to `.agent/agent.json`; and the "command SKILLs"/"nine checks" prose to "command workflows"/"eight checks" for internal consistency (the source had a stray "nine").

### The `../guide` to root-absolute repoint (the vibe-walk relative-path lesson, at scale)

port.py left **33 `../vibe-cartographer-guide/...` refs across 11 workflows**. Workflows live in `.agent/workflows/`, so `../vibe-cartographer-guide/` resolves to `.agent/workflows/vibe-cartographer-guide/` — which doesn't exist. Rewrote all 33 to the root-absolute `.agent/skills/vibe-cartographer-guide/...` form (workflows only). The sibling **skills** (`session-logger`, `friction-logger`) keep `../vibe-cartographer-guide/...` — correct, since `.agent/skills/<skill>/../vibe-cartographer-guide/` resolves right. Also repointed the bare `guide/SKILL.md` prose pointers (the persona-table "See guide/SKILL.md", the "deepening pattern in guide/SKILL.md", the vitals "anchored in guide/SKILL.md") to "the `vibe-cartographer-guide` skill" — port.py's namespacer used the path form and left these. **Lesson reinforced (vibe-walk):** after a guide split, every workflow-to-guide ref must be root-absolute; only skill-to-guide refs keep `../`.

### evolve-cart self-edit targets — the layout-flip map

Added an explicit self-edit target-map block to `/vibe-cartographer-evolve`: source proposals named `plugins/vibe-cartographer/skills/<cmd>/SKILL.md`. The map routes command behavior to `.agent/workflows/vibe-cartographer-<cmd>.md` (the 12 merges flipped these from skills to workflows), always-on rules to `AGENTS.md`, situational reference to `.agent/skills/vibe-cartographer-guide/`, internal skills to `.agent/skills/vibe-cartographer-<skill>/`, scripts to `.agent/scripts/`, architecture to `.agent/architecture/`. Fixed the example proposal targets (`skills/prd/SKILL.md` to `.agent/workflows/vibe-cartographer-prd.md`, `skills/onboard/SKILL.md` to `.agent/workflows/vibe-cartographer-onboard.md`, the `applied_files` data example, the two `guide/SKILL.md` Pattern-#13-table refs). Classic skill-to-workflow target flip — not a blind replace.

### The `/vibe-test:gate` sibling-ref fix (the namespacer-leaves-siblings-bare check)

build.md referenced `/vibe-test:gate` — a **sibling-plugin** ref (Cart defers to vibe-test's gate at the build verification step). Per the namespacing rule, sibling refs stay bare (NOT Cart-prefixed) but the Claude `:` namespace form becomes the Antigravity flat-slash form. Repointed `/vibe-test:gate` to `/vibe-test-gate` (matching vibe-test's actual ported workflow name). The report flagged this as a `namespaced-slash` leftover; it was the one cross-plugin ref needing the colon-to-hyphen flip without the Cart prefix.

### Open-question findings (do NOT invent primitives)

1. **Scheduled refresh / cron:** **None.** No `schedule`-plugin dependency, no cron. The onboard version-check is a best-effort one-shot curl, not a scheduled job.
2. **`--silent` sidecar calls:** **None.** Composition is the **linear build chain** (each workflow consumes the prior's `docs/` artifact) + the Pattern #13 defer-to-complement model — not silent sub-workflow calls returning structured data. Zero `--silent` anywhere. Open-question #2 lands on (b), the state-file/artifact handoff architecture — portable as-is.
3. **Workflow name collisions:** **RESOLVED — namespacing.** No router (the commands are the surface, taker-style); all 13 workflows are `/vibe-cartographer-<cmd>`. No eponymous case. The cross-named friction pair collapsed to one `/vibe-cartographer-friction` (no `/vibe-cartographer-friction-log` dup).
4. **`plugin_version` discovery:** `.agent/agent.json` holds `1.9.1` (mirrors plugin.json), read by the session + friction loggers for the audit field. Same bookkeeping status as the siblings.
5. **Claude-only hooks:** **None.** No `hooks/` dir, no `hooks` key. **builder.json: YES — the heaviest user in the family** (55 repoints; Cart owns the profile — onboard creates/migrates, reflect updates, decay re-validates, vitals validates, every workflow reads persona).

### Mechanical (port.py got it right)

- The **12 same-named command+skill merges** into 12 workflows — fully mechanical, zero hand-reclassification (the step-2b fix at its strongest: 12 clean pairs, the descriptions are the commands' one-liners, the bodies are the skill impls, standalone skill dirs dropped). Repoints: 47 data-path, **55 builder-profile** (family record), 33 claude-home-generic, 24 claude-md, 19 script-invocation, 22 plugin-namespaced-slash, 30 command-start-end, 7 plugin-json. agent.json minted from plugin.json (1.9.1). The 4 internal skills classified + namespaced correctly; guide flagged for the split.

### Needed thought (the 20%)

- **The friction/friction-log cross-named collapse** (above) — the one real reconciliation, with the `-log`/`-logger` disambiguation.
- **The largest guide split in the family** (above) — model-vs-table separation for personas, modes, AND composition, each with both halves.
- **The architecture/ root-level carry + its un-processed slash namespacing** (above) — port.py missed the dir entirely (51 bare-slash hits lived there).
- **The cutters sub-dir carry**, the **vitals self-test re-model** (8 checks + Runtime Paths), the **33 `../guide` to root-absolute repoints**, the **evolve self-edit target map**, the **coder-voice AGENTS.md output-target fix**, the **builder.json + schema + decay stragglers**, and the **`/vibe-test:gate` sibling-ref colon-to-hyphen flip**.

### PORT-RUNNER.md gaps hit this port

1. **Plugin-root dirs beyond commands/skills are invisible to port.py — AND their strings go un-processed.** `architecture/` was missed entirely (thesis's bundled scaffold + walk's scripts were the prior instances). The new half this port surfaced: the carried dir's contents (here `architecture/README.md`) **still carry bare source slashes** port.py never namespaced — 51 of the leftover bare-slash hits were all in that one un-processed file. **Recommend:** the scripts/data-carry step should say "carry ANY plugin-root dir the workflows read (`architecture/`, bundled scaffolds, `scripts/`), THEN run the full namespacing + path-repoint pass over the carried files — port.py touched none of their strings, so bare slashes, `~/.claude` paths, and `:`-namespaced refs inside them are all live."
2. **The `-log`/`-logger` near-collision in the cross-named merge.** When a viewer skill (`friction-log`) and a capture skill (`friction-logger`) coexist, the cross-named merge must pick the viewer (impl of the `friction` command), not the logger. A fuzzy name-match would grab the wrong one. **Recommend:** a note under step 2b — "when collapsing a cross-named pair, if two candidate skills share a stem (`X-log` vs `X-logger`), read both bodies: the merge target is the one whose body IS the command's implementation (renders/returns the command's output), not the internal append helper. The `-log`/`-logger` pair is the canonical trap."
3. **Otherwise: every accumulated lesson applied cleanly.** The guide split (steps 1-2-4-5), the 12 mechanical merges (2b), the namespacing verification (6.5), the evolve self-edit retargeting (6), the scripts-carry + byte-compile (wrap), the schema/script straggler grep (vibe-doc/wrap), the vitals self-test re-model (walk/test), the `../guide` root-absolute rule (walk), the builder.json repoint (doc), the coder-voice/keystone rules-file-write target, and the open-questions re-check ALL mapped to existing steps. The finale's residue (one cross-named collapse + the architecture-dir carry) was the smallest needed-thought share of any heavy port — the cookbook had already absorbed Cart's hard parts from the 11 ports that pointed at it.

### 12/12 — the family is cross-agent

vibe-cartographer is port 12 of 12. The whole vibe-* family — cartographer, doc, sec, test, thesis, iterate, walk, keystone, wrap, insights, thesis-engine — now runs on Antigravity 2.0 as well as Claude Code. The pipeline that started as the vibe-iterate pilot (a hand-cut `.agent/` skeleton + a hand-written cookbook) ends with `port.py` doing the mechanical ~80% and a finishing pass that, by the finale, was applying a known playbook rather than discovering new edges. The flagship — the plugin that builds the others, and the Cart-detection target the rest defer to — kept its identity and workflow names stable, so every sibling port's composition reference still resolves. The family is whole on both agents. Sharp.
