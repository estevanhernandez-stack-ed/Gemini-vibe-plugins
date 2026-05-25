# tools/ — the port pipeline

Turns a Claude Code plugin into a Google Antigravity 2.0 port. Built to scale
the validated `vibe-iterate` pilot across the rest of the vibe-* family.

A pipeline is **a deterministic transform (the mechanical ~80%) + a documented
finishing pass (the judgment ~20%)**. The cookbook is honest that the whole thing
isn't scriptable — see [`../vibe-iterate/PORTING.md`](../vibe-iterate/PORTING.md)
"Needed thought".

| File | What it is |
|---|---|
| `port.py` | The mechanical transform. stdlib-only Python 3.11+. Classifies skills, places files, applies every string repoint, scaffolds `.agent/agent.json` + an `AGENTS.md` skeleton, and emits `port-report.json`. |
| `PORT-RUNNER.md` | The finishing-pass playbook — the judgment steps after `port.py` (guide split, AGENTS.md prose, edge classifications, evolve self-edit targets, open-question re-check, verify). |

## Usage

```
python tools/port.py <claude-plugin-dir> <output-dir> [--plugin-name NAME] [--quiet] [--no-clean]
```

Example (the golden case):

```
python tools/port.py \
  ../vibe-iterate/plugins/vibe-iterate \
  /tmp/vibe-iterate-port
```

Then follow `PORT-RUNNER.md` to finish the port.

## What `port.py` does (mechanical)

- **Classifies** each source skill from its frontmatter: a real slash trigger
  (`` `/x` ``, `/plugin:cmd`, or "user says /x") → **workflow**; an internal
  self-label with no real trigger → **skill**. Slashes inside file paths and
  qualifier lists do *not* count (that's what would flip the guide to a workflow).
  Disagreements (bootstrap: "internal" label + real trigger) are flagged as edge
  cases for the finishing pass.
- **Places files:** user-invocable → `.agent/workflows/<name>.md` (frontmatter
  swapped to Antigravity form); internal → `.agent/skills/<name>/` with
  `schemas/` + `fixtures/` carried byte-for-byte and `references/*.md` prose
  repointed.
- **Repoints** (string transforms): `~/.claude/plugins/data/<plugin>/` →
  `~/.gemini/antigravity/data/<plugin>/`; `~/.claude/profiles/builder.json` →
  `~/.gemini/profiles/builder.json`; `CLAUDE.md` → `AGENTS.md`;
  `${CLAUDE_PLUGIN_ROOT}` → `.agent`; `.claude-plugin/plugin.json` →
  `.agent/agent.json`; `/plugin:cmd` → `/cmd`; `:sidecar` (backtick + bare) →
  `/sidecar`; sibling `[../X/SKILL.md]` links (full + bare-backtick) → `/X` or a
  skill-load pointer; "command start/end" → "workflow start/end".
- **Scaffolds** `.agent/agent.json` (name + version mirrored from plugin.json)
  and an `AGENTS.md` skeleton with `<!-- TODO: finishing pass -->` markers.
- **Reports** (`port-report.json`): classifications, files transformed, repoint
  tally, leftover-grep hits, and the finishing-pass TODO list.

## Validated against the golden case

Run on `vibe-iterate`'s Claude source, `port.py` reproduces the validated golden
port's structure exactly — **13 workflows, 3 skills (guide + 2 loggers)**, bootstrap
flagged as the single edge — and matches **~92%** of the golden's transformed-file
lines across the 13 workflows + 2 loggers. The remaining delta is the documented
finishing-pass gap: the guide split (always-on → AGENTS.md, situational → kept),
the AGENTS.md prose synthesis, the per-file guide-intro lines, and the
`agent-plugin` category content edit in bootstrap. The 80/20 split is honest.
