---
description: "Run when the user says `/vibe-walk-vitals` or wants a structural integrity check on the vibe-walk install. Runs read-only structural checks and reports findings in a banner-style report. Implements Pattern #8 (Plugin Self-Test) from the Self-Evolving Plugin Framework. Read-only — no auto-fix in this release."
---

# /vibe-walk-vitals — structural self-test

Slash command `/vibe-walk-vitals`. Runs **read-only** structural checks against the installed plugin files, reports findings in a banner-style report with per-check status (✓ pass, ⚠ warn, ✗ fail), and prints a summary line. No writes, no auto-fix in this release.

This is Pattern #8 (Plugin Self-Test) from the Self-Evolving Plugin Framework. Vitals surfaces drift between files before that drift silently breaks a command mid-flow.

## Before You Start

Sherpa persona and posture are always-on via `AGENTS.md`. Vitals applies the Sherpa voice to the opening line only — the report body is neutral. (This workflow reads the `vibe-walk-guide` skill's references only to confirm they exist; it doesn't load their content.)

## Session Logging

Call `vibe-walk-session-logger.start("vitals", project_dir_basename)` at workflow start. Hold the returned `sessionUUID`. At workflow end, call `vibe-walk-session-logger.end()` with:

- `outcome: "completed"` on a clean run.
- `outcome: "partial"` if a check could not run due to an unreadable file.
- `outcome: "error"` only if the command crashed before the summary line rendered.
- `verdict: null` — vitals produces no tour verdict.
- `tour_built: false`
- `anchor_review_needed: null`
- `key_decisions`: short strings for notable findings (e.g., `"friction-triggers.md missing walk triggers"`, `"discover.md workflow absent"`, `"agent.json version field missing"`).
- `friction_notes: []` — vitals does not emit friction entries; see "Friction Logging" below.

## Friction Logging

Vitals does **not** call `vibe-walk-friction-logger.log()`. Running a structural self-test is not friction. This section is intentionally empty — per the friction-triggers contract, the absence here is auditable.

## Persona Adaptation

One-sentence opening before the report renders:

```
Running structural sweep — checking agent.json, all six workflows + three skills, scripts, guide references, and friction-trigger wiring.
```

Then render the report. No narration between checks.

## Runtime Paths

All paths vitals reads (never writes):

| What | Where |
|------|-------|
| Plugin root | `<repo>/.agent/` — walk up from this workflow file's location. |
| Plugin manifest | `.agent/agent.json` |
| Workflow files | `.agent/workflows/*.md` |
| Skill files | `.agent/skills/*/SKILL.md` |
| Guide references | `.agent/skills/vibe-walk-guide/references/*.md` |
| Discovery scripts | `.agent/scripts/discovery/inventory_surfaces.py`, `anchor_readiness.py`, `build_verdict.py` |
| Build scripts | `.agent/scripts/build/emit_tour_module.py`, `emit_analytics.py`, `substrate_tree.py` |
| Anchor codemod | `.agent/scripts/anchors/inject_anchors.js` |
| Friction triggers doc | `.agent/skills/vibe-walk-guide/references/friction-triggers.md` |

If any path is unreadable for reasons other than "does not exist" (permission denied, I/O error), the affected check reports `✗ fail` with the error surfaced verbatim.

## Flow

1. Write the persona-adapted opening line.
2. Read `.agent/agent.json` version field. Fall back to `"unknown"` on parse failure. Capture local ISO datetime for the banner.
3. Run checks #1 through #7 in order. A failure in one check never aborts the next — the report always includes all seven sections.
4. Render the report (banner + per-check boxes + summary line).
5. Print the closing advisory.
6. Call `vibe-walk-session-logger.end()`.

## Check Specifications

### Check #1 — agent.json valid + version present

**Purpose:** the port manifest is parseable JSON with the required fields.

**(a) Read.** Open `.agent/agent.json`.

**(b) Evaluate.**
1. File missing → ✗ fail.
2. Not parseable JSON → ✗ fail with parse error.
3. Parseable → verify `"name"`, `"version"`, `"description"`, `"author"` all present and non-empty. Collect missing fields.

**(c) Report.**
- ✓ pass: all required fields present. Include: `name: <name>, version: <version>`.
- ✗ fail: file missing or unparseable, or one or more required fields missing. List each issue.

**(d) Fail-soft.** Any I/O error → ✗ fail with the error text.

---

### Check #2 — All expected workflows + skills present with valid frontmatter

**Purpose:** every workflow and skill the port declares exists on disk with parseable YAML frontmatter. The Antigravity port splits the nine Claude Code source skills into six workflows + three skills.

**(a) Read.** Check for these six expected workflow files under `.agent/workflows/`:

```
vibe-walk.md    vibe-walk-bootstrap.md    vibe-walk-discover.md    vibe-walk-walk.md    vibe-walk-vitals.md    vibe-walk-evolve.md
```

For each, parse the YAML frontmatter and verify a non-empty `description` field (workflows carry `description` only — the filename is the slash name; no `name` field).

Then check for these three expected skill directories under `.agent/skills/`:

```
vibe-walk-guide    vibe-walk-session-logger    vibe-walk-friction-logger
```

For each, confirm `SKILL.md` is present. Parse its frontmatter and verify both `name` and `description` are non-empty strings (skills keep `name`).

**(b) Evaluate.** Collect:
- Missing workflow files or skill directories.
- Present skill directories with missing `SKILL.md`.
- Present files with unparseable or incomplete frontmatter (workflow missing `description`; skill missing `name` or `description`).

**(c) Report.**
- ✓ pass: all six workflows + three skills present, all frontmatter valid. Include: `6 workflows + 3 skills, all frontmatter valid`.
- ⚠ warn: a file is present but its frontmatter is incomplete (non-fatal — it may still load but may not surface its slash/semantic trigger).
- ✗ fail: one or more expected workflow files or skill directories are absent. List each as `workflows/<name>.md — missing` or `skills/<dir>/SKILL.md — missing`.

**(d) Fail-soft.** If a file exists but frontmatter cannot be parsed, warn per-file with the parse error rather than failing the whole check (unless files are missing entirely, which is a fail).

---

### Check #3 — Discovery scripts present

**Purpose:** the three Phase 1 discovery scripts exist.

**(a) Read.** Check for:
- `.agent/scripts/discovery/inventory_surfaces.py`
- `.agent/scripts/discovery/anchor_readiness.py`
- `.agent/scripts/discovery/build_verdict.py`

**(b) Evaluate.** Record which are missing.

**(c) Report.**
- ✓ pass: all three present. Include: `3/3 discovery scripts present`.
- ✗ fail: one or more missing. List each as `.agent/scripts/discovery/<name> — missing`.

---

### Check #4 — Build scripts present

**Purpose:** the four Phase 2 build scripts exist.

**(a) Read.** Check for:
- `.agent/scripts/build/substrate_tree.py`
- `.agent/scripts/build/emit_tour_module.py`
- `.agent/scripts/build/emit_analytics.py`
- `.agent/scripts/build/emit_trigger_wiring.py`

**(b) Evaluate.** Record which are missing.

**(c) Report.**
- ✓ pass: all four present. Include: `4/4 build scripts present`.
- ✗ fail: one or more missing. List each as `.agent/scripts/build/<name> — missing`.

---

### Check #5 — Anchor codemod present

**Purpose:** the Phase 2 anchor-injection codemod exists.

**(a) Read.** Check for `.agent/scripts/anchors/inject_anchors.js`.

**(b) Evaluate.** Present or absent.

**(c) Report.**
- ✓ pass: `inject_anchors.js` present.
- ✗ fail: `.agent/scripts/anchors/inject_anchors.js — missing`.

---

### Check #6 — Guide references present

**Purpose:** the two surviving guide reference files exist. (The Antigravity port folded `sherpa-persona.md` and `posture.md` into `AGENTS.md` — only the situational refs stay skill-side.)

**(a) Read.** Check for:
- `.agent/skills/vibe-walk-guide/references/conventions.md`
- `.agent/skills/vibe-walk-guide/references/friction-triggers.md`

**(b) Evaluate.** Record which are missing.

**(c) Report.**
- ✓ pass: both present. Include: `2/2 guide references present`.
- ✗ fail: one or more missing. List each as `.agent/skills/vibe-walk-guide/references/<name> — missing`.

---

### Check #7 — Friction-trigger table covers all three commands

**Purpose:** the `friction-triggers.md` table has a section for each of the three commands that fire it (`bootstrap`, `discover`, `walk`). Orphan or missing sections are a warn — the friction-detection surface is incomplete.

**(a) Read.** Open `.agent/skills/vibe-walk-guide/references/friction-triggers.md`. Parse section headings (lines starting with `##`).

**(b) Evaluate.** Confirm these three headings are present (case-insensitive match on the command name):
- `## /vibe-walk-bootstrap`
- `## /vibe-walk-discover`
- `## /vibe-walk-walk`

For each present section, confirm it contains at least one friction trigger row (a bullet line starting with `-` or `*`). A section with an empty body is ⚠ warn — documented intentional emptiness is fine; undocumented emptiness is not.

**(c) Report.**
- ✓ pass: all three sections present and each has at least one trigger row. Include: `3 sections, all populated`.
- ⚠ warn: a section is present but has no trigger rows, and the file does not document the emptiness as intentional (compare: the `/vibe-walk-vitals` section in vibe-cartographer's friction-triggers is documented-empty; an undocumented empty section here is a signal that triggers went missing).
- ✗ fail: one or more of the three expected sections is entirely absent from the file. List each as `/<command> section — missing`.

**(d) Fail-soft.** File unreadable → ✗ fail with the I/O error. File present but empty → ✗ fail: `friction-triggers.md is empty`.

---

## Output Format

### Banner header

```
  Vibe-Walk — Vitals
  <version> · <ISO-local-timestamp>
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Then one blank line before the first check.

### Per-check boxed section

Each check renders as its own box:

```
  ┌──────────────────────────────────────────────────────────────────┐
  │ ✓  Check 1 — agent.json valid + version present                   │
  └──────────────────────────────────────────────────────────────────┘
     name: vibe-walk, version: 0.1.0
```

```
  ┌──────────────────────────────────────────────────────────────────┐
  │ ✗  Check 2 — workflows + skills present                           │
  └──────────────────────────────────────────────────────────────────┘
     workflows/vibe-walk-discover.md — missing
```

**Status glyph rules:** `✓` pass · `⚠` warn · `✗` fail. Two spaces after the glyph before the check title.

**Box width:** 68 columns.

**Empty findings for ✓ pass:** one summary line of the form `<headline metric>`.

### Summary line

After the last check box, one blank line, then:

```
  <N> ✓  ·  <N> ⚠  ·  <N> ✗
```

Indented two spaces. The three counts sum to 7.

### Closing advisory

```
Re-run /vibe-walk-vitals any time to re-check. For structural proposals, see /vibe-walk-evolve.
```

## Expected output on a clean install

A fully-shipped v0.1.0 install should produce `7 ✓  ·  0 ⚠  ·  0 ✗`.

The first run before a dogfood session is the natural time to run this. If anything's missing or drifted, the check output names exactly what to fix before the session starts.

## Why this exists

vibe-walk has six workflows, three skills, eight scripts, and two guide-reference files that cross-reference each other. Without an on-demand diagnostic, a missing script or a deleted reference file surfaces as a cryptic error mid-build at the worst possible moment. `/vibe-walk-vitals` makes the structural state visible in one pass — cheap to run, hard to misread.

## Cross-references

- Guide (Sherpa persona + posture): `AGENTS.md` + the `vibe-walk-guide` skill (`.agent/skills/vibe-walk-guide/SKILL.md`)
- Session logger: the `vibe-walk-session-logger` skill (`.agent/skills/vibe-walk-session-logger/SKILL.md`)
- Friction logger: the `vibe-walk-friction-logger` skill (`.agent/skills/vibe-walk-friction-logger/SKILL.md`)
- Self-evolution: `/vibe-walk-evolve`
- Friction triggers: `.agent/skills/vibe-walk-guide/references/friction-triggers.md`
