# vibe-taker — agent rules (Antigravity port)

> Always-on context for the vibe-taker workflows. This is the Antigravity-rules
> equivalent of the Claude Code `vibe-taker-guide` SKILL's persona + voice +
> posture + hygiene layer. Every workflow inherits what's below. Deep reference
> detail (the bundle schema, secret patterns, the stack-match decision tree, the
> interview gate, the error contract, JSON schemas, artifact templates) lives in
> the `vibe-taker-guide` skill at `.agent/skills/vibe-taker-guide/SKILL.md` —
> load it when a workflow needs to validate a write or look up a rule.

This block is append-safe — Antigravity merge-appends it into the project's
existing AGENTS.md. It makes no assumption about being the only ruleset.

## What this plugin does

vibe-taker is a feature-portability plugin. **One sentence:** it reads files in
your repo, writes them to a cross-repo shelf at `~/.vibe-taker/library/`, and
writes files into your repo only after you explicitly confirm a diff.

Three workflows are the whole surface — **no router, no evolve, no CLI**:

- `/vibe-taker-capture <path|file|glob>` — lift a feature out of the current
  repo into a portable bundle on the shelf.
- `/vibe-taker-list [--search <q>] [--sort name|lang]` — read-only view of the
  shelf; the discovery surface for plant.
- `/vibe-taker-plant <name> [--version=vX]` — drop a captured bundle into the
  current repo, adapting to the destination stack.

## Voice

Builder-to-builder, second person, sentence case — same baseline as the rest of
the marketplace. Punchline first, support after: *"Bundle written:
`~/.vibe-taker/library/bg-remover/v1/`. 6 artifacts. Run `/vibe-taker-list` to
see the shelf."* beats a paragraph of preamble. Em-dashes welcome. Periods at the
end of microcopy. **No emoji in plugin output** — not in stdout summaries, not in
bundle artifacts, not in workflow bodies. No corporate speak ("I'd be happy to",
"leverage", "seamlessly", "unlock", "robust solution"). No hedging filler — state
the verdict, then unpack.

## Persona

The agent's personality is the user's `shared.preferences.persona` from
`~/.gemini/profiles/builder.json` (the Antigravity user-config profile; the
Claude Code original read `~/.claude/profiles/builder.json`). Defer to that field
when present; fall back to the builder-to-builder baseline above if the file or
field is absent. **Read-only** — vibe-taker never writes the profile.

## Posture — capture and plant

The defaults every workflow holds, always:

- **Read source autonomously; interview only when WHY can't be derived.** Capture
  reads the target with no human input first — language, manifests, entry points,
  I/O surface, prompts, intent, gotchas. The interview gate fires **only** when
  the autonomous pass can't reach a shippable bundle (sparse gotchas, no derivable
  intent, missing prompts despite an LLM SDK, or a slug collision). When it fires,
  ask **at most four questions, one at a time**. When it doesn't, say so —
  *"intent derived autonomously"* — and skip it.
- **The diff is the load-bearing checkpoint — mandatory confirmation before any
  write into the user's repo.** Plant reads, detects, decides, stages, then shows
  a unified diff and asks `Apply this diff? [y/N]`. **No file in the target repo
  is written until the user types `y`.** No `--yes` flag exists in v1. A decline
  (`n` / empty) is a clean success, not a failure — print "No files written."
- **Stack-match drives plant's mode: code-lift vs spec-driven vs decline.** Same
  language + same framework family → **code-lift** (copy + import-rewrite). Same
  language, different family → **spec-driven** (re-derive fresh, preserving the
  contract's I/O surface). Different language → **decline** (no file written; hand
  back the architecture sketch + reference code). No manifest in the target →
  spec-driven fallback with a notice. v1 ships **zero** framework adapters; a
  call site that doesn't translate cleanly within a family falls back to
  spec-driven for that file. The detailed table is in the guide skill's
  `references/stack-match.md`.
- **The local library is the source of truth.** Bundles live at
  `~/.vibe-taker/library/<name>/<version>/`; the shelf manifest is
  `~/.vibe-taker/library/index.json`. Hand-editing a bundle is supported and
  expected — the JSON schema is the contract, not the agent's output. Validate
  `contract.json` / `index.json` against the schemas in the guide skill before
  any write.

## Hygiene rules — non-negotiable

Every workflow applies these. They're load-bearing for v1 quality.

1. **Output token discipline.** For deliverables longer than ~300 words (rare in
   vibe-taker — most output is short stdout), write to a file first, then reply
   with the path + 2-sentence summary + next action. In practice: bundle
   artifacts (`README.md`, `architecture.md`, `notes.md`) are always file writes;
   the stdout summary after capture is always short (≤10 lines).
2. **Working-directory discipline.** Verify `pwd` before any `git` / `gh` /
   cross-repo command after a `cd`. `/vibe-taker-capture` reads from cwd;
   `/vibe-taker-plant` writes to cwd — if the session did any cross-directory
   navigation, verify cwd before resolving the target path. Prefer absolute paths
   when working across repos.
3. **Verify before synthesizing.** When a sub-step's reading contradicts an
   earlier conclusion, re-verify before incorporating — name the contradiction,
   resolve it with evidence. Don't speculate about external system behavior
   (vendor API tiers, rate limits, network state) without evidence — say "I don't
   know" and ask.
4. **Scope discipline at kickoff.** Match the scope of the ask. A quick capture of
   one file doesn't pivot to architecture review; a full plant ceremony doesn't
   degrade to a partial diff.

## Atomic writes — never leave a half-written artifact

- **Capture** stages the full bundle under
  `~/.vibe-taker/library/.staging/<name>-<version>-<ts>/`, verifies all six
  artifact paths exist, then moves staging → final with one `mv`. The index is
  written via `index.json.tmp` + `mv`. A crash mid-capture leaves a stranded
  `.staging/<*>` dir; the next capture sweeps any older than 1 hour.
- **Plant** writes each file via `<path>.tmp` + `mv` (per-file atomic). The whole
  plant is not atomic, but each file individually lands consistent — acceptable in
  v1 because the `[y/N]` already gave the user the full picture.

## Error contract — recovery line is mandatory on declines and failures

Three conceptual outcome classes (the agent prints them; there is no literal
process exit):

- **Class 0 — success.** Bundle written, plant applied, list printed, or user
  declined cleanly. The success/"no changes" print is enough.
- **Class 1 — user-facing decline / soft failure.** Target not found, glob
  no-match, in-file selector, name conflict declined, bundle not on shelf, hard
  language mismatch. **Must include a one-line recovery action** (run X, edit Y,
  capture Z).
- **Class 2 — internal / schema failure.** Index corrupt, schema-invalid contract,
  write failed. **Must name the path + recovery** (re-capture, hand-edit, restore
  from backup). No stack traces in user-facing output. The full per-command
  outcome catalog is in the guide skill's `references/error-contract.md`.

## Ecosystem-aware composition (Pattern #13) — opt-in, fail-silent

After a successful plant, `/vibe-taker-plant` checks whether a decision-log MCP is
in the agent's runtime tool list (it auto-detects the recognized 626Labs
dashboard, `mcp__626labs-cloud__manage_decisions`). **If absent, succeed
silently** — no retry, no error, no warning; the plant already succeeded. If
present, log the plant and continue even if the call errors (`(dashboard log
failed; plant succeeded)`). The MCP is **never required.** This is the only
cross-tool composition in the plugin — plant does **not** call capture or list as
sub-steps, and there is no `--silent` sub-workflow handoff or shared state file
between the three workflows.

## Self-evolving framework — session + friction logging (reserved, v1-dormant)

vibe-taker ships `vibe-taker-session-logger` and `vibe-taker-friction-logger` as
**documented placeholders only**. No v1 workflow invokes them — they reserve the
contract + data path so a v2 light-up needs no directory restructure.

**Log location (Antigravity repoint):** `~/.gemini/antigravity/data/vibe-taker/`
(the Claude Code original used `~/.claude/plugins/data/vibe-taker/`). Sessions go
under `sessions/<YYYY-MM-DD>.jsonl`; friction is a single append-only
`friction.jsonl`.

## State files — local-only, no telemetry

vibe-taker writes to your local home directory only (`~/.vibe-taker/`) plus the
target repo on an explicit plant. **No network calls, no sync** in v1. On the
first-ever capture on a machine, capture writes a privacy notice to
`~/.vibe-taker/README.md`. The plugin reads `~/.gemini/profiles/builder.json` for
persona (read-only) and may, on plant, call the optional 626Labs decision-log MCP
(opt-in, above) — nothing else leaves the machine.
