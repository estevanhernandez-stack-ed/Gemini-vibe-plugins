# PORT-RUNNER.md — the finishing pass after `port.py`

> `port.py` does the mechanical ~80% of a Claude Code → Antigravity 2.0 port:
> classification, file placement, and every string repoint. This document is
> the **judgment ~20%** — the steps an agent/human runs after the script to turn
> the skeleton into a shippable port. The authority on *what* each step means is
> [`vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md) ("Needed thought"
> section). This is the *runbook* for executing it.

The split is honest: the script can move files and swap strings deterministically,
but it cannot decide what's always-on vs situational, write persona prose, or
re-target a self-edit pointer whose meaning flipped when a skill became a
workflow. Those are below.

---

## 0. Run the script

```
python tools/port.py <claude-plugin-dir> <output-dir>
```

Read the stdout summary and `<output-dir>/port-report.json`. The report's
`finishing_pass_todos` array is your checklist — this doc explains each item.

Sanity-check the report first:
- `summary.workflows` + `summary.skills` should equal the source **surface** count
  — i.e. (skills + command-only commands), since each command+skill pair MERGES into
  one workflow (it doesn't double-count). If the source has a `commands/` dir, read
  `report.commands_merged` to see the merge math (see step 2b).
- `edge_classifications` — every entry needs a human eye (see step 3).
- `leftover_grep_hits` — most are expected (see step 6); confirm none are misses.

---

## 1. Synthesize `AGENTS.md` (the always-on layer)

The script writes an `AGENTS.md` **skeleton** with `<!-- TODO: finishing pass -->`
markers and hints naming the source guide reference docs. Your job: turn it into
prose.

**Source:** the Claude Code `guide` skill's `references/*.md` (persona, posture,
knowledge-sources, cart/cross-plugin detection) + the guide's "Hard rules"
section.

**Do:**
- Collapse each always-on reference doc into prose under the matching skeleton
  header. Persona → `## Persona`, posture → `## Posture`, etc.
- Repoint the detection mechanism: "available-skills list (system reminder)" →
  "`<sibling>` workflows/skills available in this Antigravity workspace".
  Preserve the read-only / never-probe / never-hard-fail / never-auto-install
  rules.
- Add a `## Voice` paragraph if the plugin has an established voice.
- Keep it **append-safe**. Live validation (PORTING.md "Validated live") proved
  Antigravity *merge-appends* the port's AGENTS.md into the project's existing
  one. No assumptions about being the only ruleset.

**Don't:**
- Don't copy the reference docs in as files. AGENTS.md is the single source of
  truth for the always-on layer.
- Don't fold schemas or trigger maps into AGENTS.md. Those stay skill-side
  (step 2).

---

## 2b. The command merge (thin-command-wrapper → merged workflow)

> **Applies only to plugins with a `commands/` dir** (vibe-doc was the first;
> sec/test are likely the same shape). `port.py` now handles this automatically —
> this step is the human verification.

Claude Code conflates two surfaces a plugin can expose: **commands** (`commands/*.md`,
the user-typed slash entry) and **skills** (`skills/*/SKILL.md`, semantic-loaded
behavior). A common pattern is the **thin command wrapper**: `commands/scan.md` is
four lines — `description: Scan your project…` + "read `skills/scan/SKILL.md` and
follow it." The command is the slash identity + clean one-line summary; the skill
holds the real implementation (and its own "use when the user mentions 'scan'…"
semantic trigger).

`port.py` reconciles `commands/` against `skills/` into the unified workflow/skill list:

| Source shape | Port target | Rule |
|---|---|---|
| command + same-named skill | **one workflow** `/<plugin>-<cmd>` | MERGE: command → slash + `description`; skill body → workflow body. The standalone skill is **dropped** (its body lives in the workflow now). |
| command-only (no parallel skill) | **workflow** `/<plugin>-<cmd>` | Body IS the command body. |
| skill-only (no parallel command) | classify as usual | Workflow if it carries a real trigger; else skill (loggers, guide). |

**Why this was the big lesson:** before the fix, `port.py` read only `skills/`. It saw
the skill descriptions ("This skill should be used when…" = semantic-load phrasing),
emitted scan/generate/check as **skills** (wrong — they're user-typed entries), and
**dropped the commands entirely** — so `status` (command-only, no parallel skill)
vanished. The merge restores the slash identity AND recovers the command-only case.

**Verify in the finishing pass:**
- The report's `commands_merged` block lists `merged_with_skill` + `command_only_workflows`.
  Confirm each merged workflow's `description` (from the command) reads clean and its
  **body carries the full implementation** (from the skill) — not just the command's
  "read the SKILL" delegation line.
- Confirm **no standalone skill dir survives** for a merged command (port.py emits none;
  if you re-ran an older skeleton, `rm` the `vibe-doc-scan`/`-generate`/`-check` skill dirs).
- For a **command-only** workflow, flesh out any "read `skills/X/SKILL.md`" delegation
  that no longer has a skill to point at — the workflow IS the implementation now.
- Edge note: the merged skill's own `description` (the semantic trigger) is discarded in
  favor of the command's clean one — don't paste the verbose "this skill should be used
  when…" blurb back into the workflow `description`.
- Defensive: if a *merged* source skill ALSO carried `references/`/`schemas/`, port.py
  carries them into a companion `.agent/skills/<name>/` dir and flags it. Decide: fold
  into the guide skill, keep the companion (add a SKILL.md), or inline. (No plugin has hit
  this yet — scan/generate/check have no sub-dirs.)

## 2. The guide split (the subtle one)

The script copies the **whole** guide skill into `.agent/skills/guide/`, including
all `references/*.md`. That's deliberately conservative — it preserves everything
so you decide what to prune. Now do the split.

**Judgment rule (PORTING.md):** if a reference doc is *"how the agent should
behave always,"* it belongs in AGENTS.md (step 1) — **delete it from the guide
skill** after folding. If it's *"the exact shape/rules for a thing the agent
occasionally touches"* (schemas, fixtures, trigger maps, write conventions), it
**stays** in the guide skill.

- **Always-on → fold into AGENTS.md, then `rm` from guide:** persona, posture,
  knowledge-sources, cart/cross-plugin detection.
- **Situational → keep as files:** `schemas/*.json`, `fixtures/*`,
  `references/*-conventions.md`, `references/*-triggers.md`.
- **Rewrite `guide/SKILL.md` to a thin index** pointing at the kept files +
  AGENTS.md. (The vibe-iterate golden guide SKILL.md went from ~55 lines to ~47,
  and the references dir from 6 docs to 2.)

Verify after pruning: the script flagged `guide_split: true` on the guide skill
in the report so you don't miss it.

---

## 3. Fix edge classifications

`port.py` flags any skill where the self-label and the trigger evidence disagree,
or where there was no strong signal. The canonical edge is **bootstrap**: it
self-labels "Internal SKILL" but lists a real `/<plugin>:bootstrap` trigger, so
it ports as a **workflow** (trust the trigger). Confirm each flagged entry:

- A skill the script defaulted to `skill` "no real slash trigger" — does it
  actually have a hidden user entry point? If yes, move it to
  `.agent/workflows/` and swap its frontmatter.
- A skill the script promoted to `workflow` despite an "internal" label — is it
  genuinely user-typed? bootstrap is; a pure logger isn't.

When you move a file between `workflows/` and `skills/`, redo its frontmatter
(workflows: `description` only, filename = slash name; skills: keep `name`).

---

## 4. Per-file guide-intro lines

The script auto-rewrites the source's `Read [`../guide/SKILL.md`](...)` intro
line to a **generic** pointer. The golden port hand-wrote a **per-file** intro
that names which always-on layer the file leans on, e.g.:

> *Ptolemy persona, posture, knowledge sources, and Cart-detection are always-on
> via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is
> in the `guide` skill — load it when you need to validate a write. Then follow
> this workflow.*

Rewrite each (the report's `guide_intro_lines_to_synthesize` count tells you how
many). A short workflow that never writes state can have a one-line intro; a
state-writing workflow should name the schema-validation hook.

---

## 5. Folded-reference back-pointers

Any body that referenced a doc you *folded into AGENTS.md* in step 1/2 (e.g.
"per `../guide/references/cart-detection.md`") must now point at
**`AGENTS.md § <Section>`** — the file no longer exists. Grep the port for
`../guide/references/` and check each: if the target survived the split, keep the
pointer (repointed); if it was folded, redirect to the AGENTS.md section.

---

## 6. `evolve-*` self-edit targets (NOT a blind replace)

If the plugin has an `evolve-*` workflow, its proposal shapes name files to edit:
`plugins/<plugin>/skills/<cmd>/SKILL.md`. These must repoint to the **real port
target** — which is now also the **namespaced** target (step 6.5):

- A source skill that ported to a **workflow** → `.agent/workflows/<plugin>-<cmd>.md`
  (router → `.agent/workflows/<plugin>.md`; an `evolve-*` →
  `.agent/workflows/<plugin>-evolve.md`).
- A source skill that stayed a **skill** → `.agent/skills/<plugin>-<name>/SKILL.md`.
- Trigger maps / schemas → their kept path under `.agent/skills/<plugin>-guide/`.

This is why it can't be a string replace: `feature-add` flips to a workflow but
`friction-triggers.md` stays skill-side. Use the report's `workflows` / `skills`
lists (each carries `name` = the namespaced target and `source_name` = the
original) as the lookup table.

---

## 6.5. Plugin-prefix namespacing (REQUIRED — applied by `port.py`)

Antigravity slash names are **flat** — there is no `/plugin:cmd` namespace like
Claude Code's. Two installed ports that each expose a bare `/bootstrap` collide,
and the live observation that forced this step: **bare workflow names
(`/bootstrap`, `/walk`, `/radar`) were unidentifiable in Antigravity's flat
slash list once more than one port was installed.** You could not tell whose
`/bootstrap` you were about to run.

The convention — **self-labeling + collision-free**:

| Source | Namespaced name | Slash |
|---|---|---|
| Router workflow (file named `<plugin>.md`) | unchanged | `/<plugin>` |
| Any other workflow `<cmd>.md` | `<plugin>-<cmd>.md` | `/<plugin>-<cmd>` |
| `evolve-<anything>.md` (collapse the redundancy) | `<plugin>-evolve.md` | `/<plugin>-evolve` |
| Skill dir `<skill>/` + its frontmatter `name:` | `<plugin>-<skill>/`, `name: <plugin>-<skill>` | — |

`port.py` does this automatically: it renames the files/dirs, sets the skill
frontmatter `name`, and rewrites **every** reference — bare slash-refs
(`/discover` → `/<plugin>-discover`), H1 titles (`# /discover — …`), `description:`
frontmatter, skill-identity refs (`` `guide` ``, "the X skill",
`session-logger.start()`, `friction-logger.log()`), and the relative file paths
(`.agent/skills/<skill>/`, `../<skill>/SKILL.md`, `workflows/<cmd>.md`,
the double-slash `/<plugin>/<cmd>` form). The rewrite is **word-boundary-aware
and longest-first** so `/scan-releases` is handled before `/scan`,
`/evolve-walk` before `/walk`, and the router `/<plugin>` is never corrupted.

**What the script deliberately does NOT touch** — verify by eye:

- **Common-noun prose.** A skill called `guide` is a single token; its plain-word
  uses ("Sherpa is the guide who leads") are left alone. Only the skill IDENTITY
  (backtick-wrapped, "guide skill", path/method-call forms) is namespaced.
- **Sibling-plugin refs.** `vibe-cartographer:scope`, and Cart's own
  `/scope` / `/prd` / `/spec` / `/build`, are NOT this port's commands — they stay
  bare. The slash-rewrite only touches names in this port's rename map.
- **Log/enum data values.** A `command: "discover"` field passed to the session
  logger is a data value, not a slash-ref — unchanged.

**Idempotent.** A name already carrying the `<plugin>-` prefix is left as-is, so
re-running never doubles the prefix (`vibe-walk-vibe-walk-…`).

**Verify (drive to zero):**

```
# every bare command slash-ref should now be prefixed — only /<plugin> is bare
grep -rPaon '(?<![\w-])/(bootstrap|discover|walk|vitals|feature-add|competitive|ux-polish|bug-bash|radar|spy|scan-releases|rate|ship|upgrade|evolve-[a-z]+)\b' \
  .agent AGENTS.md README.md | grep -vE '/<plugin>-'    # expect: nothing
grep -rn '<plugin>-<plugin>-' .                          # expect: nothing (no doubles)
```

Also confirm: every `.agent/skills/<X>/` path and `../<X>/SKILL.md` link resolves
to an on-disk dir, and each skill's frontmatter `name:` equals its dir name. If a
workflow self-tests (e.g. vibe-walk's `/vibe-walk-vitals`), its **expected-file
list** and any `## /<cmd>` section-header checks must be updated to the
namespaced names too — those bare code-fence basenames are intentionally not
auto-rewritten (to protect prose), so they're a hand-finish.

---

## 7. H1 titles & inline-trigger cleanup

The script repoints frontmatter triggers and body slash names (including the
namespacing rewrite in step 6.5), but check:
- **H1 headings** — a source `# /vibe-iterate:rate &lt;idea&gt;` becomes
  `# /vibe-iterate-rate <idea>` (namespaced slash, de-entity the `&lt;`/`&gt;`).
- Any HTML-entity-escaped angle brackets in argument hints.

---

## 8. Re-check the five open questions (PORTING.md) for THIS plugin

Do NOT invent Antigravity primitives. For each, answer against the plugin's
actual feature set and document the answer in the port's PORTING.md/README:

1. **Scheduled refresh / cron** — does this plugin rely on the `schedule` plugin
   or any cron? If yes, wire Antigravity's scheduled-task mechanism *if it
   exists*, else document the feature as manual-only.
2. **`--silent` sub-workflow calls** — does it call sidecars expecting structured
   data back? Keep the `--silent` instruction as agent guidance; flag that
   Antigravity's compose semantics are unverified, or inline the sidecar.
3. **Workflow name collisions** — RESOLVED. Antigravity slash names are flat
   (no plugin namespace), so bare `/bootstrap`, `/discover`, `/radar` collide
   across installed ports and are unidentifiable in the flat slash list. The
   plugin-prefix namespacing convention (step 6.5) is the standing answer:
   `port.py` now applies it automatically. Confirm the rename map in
   `report.namespacing` looks right for this plugin; no per-port decision left.
4. **`plugin_version` discovery** — `.agent/agent.json` holds the mirrored
   version for the loggers' audit field. Confirm whether Antigravity reads it.
5. **Claude-only hooks** — does the source have a `hooks/` dir
   (PreToolUse/PostToolUse/SessionStart/SessionEnd)? `port.py` does NOT port
   hooks. Antigravity's event/automation model needs verification before any
   hook-bearing plugin ships. (vibe-iterate had no hooks, so this didn't bite.)

Also confirm the **builder-profile repoint**: if the plugin reads
`~/.claude/profiles/builder.json` (vibe-cartographer does; vibe-iterate didn't),
the script repoints it to `~/.gemini/profiles/builder.json` — verify the path is
right for the plugin.

---

## 9. Verify

- **Leftover grep.** Re-run the grep over the finished port:
  `~/.claude` (only the intentional repoint-note mention should remain),
  `CLAUDE_PLUGIN_ROOT`, `CLAUDE.md`, `.claude-plugin/plugin.json`,
  `../guide` (only legitimate guide-skill links), `:sidecar` colon forms,
  `/<plugin>:cmd` namespaced slashes. The report's `leftover_grep_hits` is your
  starting list; finishing-pass edits should drive it to zero real misses.
- **Install/run check (the real bar).** Hand Antigravity the port repo URL and
  ask it to set up the plugin in a real target project. Confirm:
  - it clones, copies `.agent/*`, and *merge-appends* AGENTS.md (non-destructive).
  - all workflows + skills load; a representative workflow runs end to end.
  - project-local state (e.g. `.vibe-iterate/config.json`) carries over untouched;
    only the home-dir self-evolution logs repoint to `~/.gemini/antigravity/...`.
- **Diff against the cookbook checklist** in PORTING.md "Reusable checklist for
  the next port" — every box ticked.

---

## 10. Document

- Write the port's `README.md` (install + use).
- Append this plugin's specifics to the cookbook (its open-question answers, any
  new edge it surfaced).
- Log the port as a decision on the 626Labs Dashboard if it crosses a meaningful
  fork (new namespacing convention, a hook-model finding, etc.).

---

## What the script will never do (by design)

- Decide the always-on / situational split.
- Write persona/posture/voice prose.
- Re-target a self-edit pointer whose meaning flipped (skill→workflow).
- Answer the open questions about Antigravity primitives — those need a real
  Antigravity instance, not a regex.
- Port `hooks/` — the event model is unverified.

The script's contract: get the skeleton right and tell you exactly what's left.
The rest is judgment, and judgment is the 20%.
