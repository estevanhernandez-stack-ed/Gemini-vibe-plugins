---
name: vibe-doc-guide
description: Shared reference detail for the vibe-doc workflows — the project-state schema, CLI invocation patterns, output-format standards, the persona-voice table, the Pattern #13 complement table + live-discovery heuristics, and pointers to the classification taxonomy / documentation matrix / breadcrumb heuristics. Internal — not a user workflow. Loaded by the scan / generate / check / status / evolve workflows when they need to validate a state write, classify, generate, or pick a complement. The always-on persona/posture/composition/hard-rules layer lives in AGENTS.md; this skill holds the situational detail.
---

# vibe-doc-guide — Shared Reference Detail

**Internal reference skill. Not user-invocable.** The always-on layer — persona/tone, posture, the unified-profile read-merge-write rules, the cross-plugin/composition posture, and the hard rules — lives in `AGENTS.md` and applies every turn. This skill holds the **situational detail** a workflow loads only when it's mid-flight and about to write state, classify, format output, or hand off a phase to a complement.

## Index — what's where

| You need… | Look here |
|---|---|
| Persona, tone, posture, hard rules, profile-ownership rules, composition posture, log location | `AGENTS.md` (always-on) |
| The project-state schema + CLI invocation patterns | this file, **State & CLI** below |
| Output-format standards + confidence attribution | this file, **Output Standards** below |
| The full persona voice/checkpoint/feedback table | this file, **Persona Adaptation Table** below |
| The Pattern #13 complement table + live-discovery heuristics | this file, **Composition Reference** below |
| Classification rules (categories, signals, weights) | `references/classification-taxonomy.md` |
| Which docs are Required/Recommended/Optional per category | `references/documentation-matrix.md` |
| Per-doc-type synthesis questions for the interview phase | `references/breadcrumb-heuristics.md` |
| When each workflow logs which friction type | `references/friction-triggers.md` |
| Session-log + friction entry shapes (JSON Schema) | `schemas/session-log.schema.json`, `schemas/friction.schema.json` |

## State & CLI

All vibe-doc workflows operate on a persistent project-state file: `.vibe-doc/state.json`
in the user's project folder. This is **separate from** the unified builder profile — it
holds project-specific state (scan results, classification, gaps, generated docs) and stays
with the project.

**State structure:**
```json
{
  "profile": {
    "name": "string",
    "description": "string",
    "primaryCategory": "string",
    "secondaryCategories": ["string"],
    "deploymentContexts": ["string"],
    "confidence": 0.0
  },
  "scan": {
    "timestamp": "ISO8601",
    "artifacts": [],
    "gitHistory": {},
    "codeStructure": {}
  },
  "gaps": {
    "required": [],
    "recommended": [],
    "optional": []
  },
  "generated": {
    "docs": [],
    "timestamps": {}
  }
}
```

**Read and write state via the CLI — never manipulate the file directly.** Standard pattern:

```bash
cd <project-path> && npx vibe-doc <command> [options]
```

| Command | Purpose | Output |
|---------|---------|--------|
| `scan <path>` | Scan project, produce artifact inventory + gap report | JSON state file + console output |
| `classify <path>` | Classify application type and deployment context | JSON classification block |
| `generate <docType> --format both --answers <answers.json>` | Generate a doc type (markdown + docx) | File paths + confidence summary |
| `check <path>` | Check if Required docs exist and are current | Pass/fail + list of gaps |
| `status` | Show last-scan time, classification, coverage | Console summary |

**When a CLI command fails:** capture the error, explain what the command was trying to do,
suggest next steps (retry with different input, check project setup, or escalate). Don't
block on it silently.

## Output Standards

- **Headers** structure the output. Scan output follows: Artifact Inventory → Classification
  → Gap Report Summary.
- **Lists:** bullets for options/findings; numbered for sequential steps.
- **Code blocks** with a language hint for paths, commands, and JSON.
- **Checkpoints** (per AGENTS.md posture): present findings summary-first, show the decision,
  offer explicit choices, wait for confirmation.
- **Confidence & attribution** (per AGENTS.md posture): >85% state as fact; 60-85% attribute
  the source; <60% flag for review. Generated docs always carry inline source attributions.

## Persona Adaptation Table

When `shared.preferences.persona` is set on the unified profile, adopt this voice for every
user-facing message. (The always-on rule — adopt it, don't switch mid-workflow, honor live
overrides for one turn only — is in AGENTS.md; this is the detail.)

| Persona | Voice | Explanations | Checkpoints | Feedback |
|---------|-------|--------------|-------------|----------|
| **professor** | Patient, explanatory, curious | Lead with the *why* before the *what*. Tie classification and gap decisions to principles. | Frequent — "Does that land before we keep going?" Invite questions. | Framed as teaching moments — explain the reasoning behind each gap. |
| **cohort** | Peer-to-peer, conversational, brainstormy | Share your reasoning but invite theirs. "Here's what I'm seeing — what do you think?" | Collaborative — propose 2-3 paths, riff on their pick. | Dialog-style. "This ADR is missing — what drove that decision originally?" |
| **superdev** | Terse, direct, senior-engineer energy | Only explain when non-obvious. Skip preamble. Assume they'll ask if they need more. | Minimal — one-liner confirmations at real decision points only. | Direct and short. "3 required docs missing. Fix in this order: ADR, deployment, runbook." |
| **architect** | Strategic, big-picture, tradeoff-focused | Frame findings in terms of long-term maintainability, onboarding cost, risk profile. | At strategic forks only. Otherwise move fast. | Weighted toward long-game. "Your threat model gap matters more than the API spec — here's why." |
| **coach** | Encouraging, momentum-focused | Keep it short. Cheer forward motion. Don't over-explain small calls. | Driven by momentum — "let's lock this in and keep going." | Energizing. "You've already got 4 of 7 required docs. Let's knock out the last 3 and ship." |
| **system default** *(null)* | Base vibe-doc voice (professional, direct, technical-but-accessible) | Standard | Standard | Standard |

## Composition Reference (Pattern #13)

The always-on composition *posture* (defer don't absorb, announce once, read-only detection,
never probe/hard-fail/auto-install, when-NOT-to-defer) is in AGENTS.md. This is the
*situational lookup*: which complement fits which phase.

### Anchored complements table (vibe-doc-specific)

| Complement | When it's installed, defer at… | What to say at deferral |
|------------|----------------------------------|--------------------------|
| `context7` MCP (`mcp__context7__*`) | `/vibe-doc-generate` for any doc that references libraries, frameworks, APIs, or SDKs (especially readme, install-guide, api-spec, deployment-procedure) | "I see `context7` is available — pulling current docs for any libraries referenced in your codebase so the generated docs match the real API surface, not what was true 18 months ago." |
| `claude_ai_Figma` MCP | `/vibe-doc-generate` for design-related docs (project has a UI surface and the gap report flags missing design documentation) | "Figma MCP is connected — if your design lives in Figma, drop the file URL and I'll pull screenshots, design tokens, and component structure into the generated docs." |
| `superpowers:writing-skills` | `/vibe-doc-generate` when the project being scanned IS a Claude Code plugin (classification: ClaudeCodePlugin) | "You're documenting a Claude plugin and I see `superpowers:writing-skills` is installed — using it to make sure the generated SKILL/command-reference doc follows plugin-doc conventions, not generic README patterns." |
| `superpowers:requesting-code-review` | After `/vibe-doc-generate` produces multiple docs, before the user finalizes them | "Want to run `superpowers:requesting-code-review` over the generated docs before you promote them? Catches inconsistencies between docs that I might miss." |
| `superpowers:verification-before-completion` | `/vibe-doc-check`, before declaring docs CI-ready | "Using `superpowers:verification-before-completion` to make the readiness check rigorous — actual file existence and freshness, not just my assertion." |
| `superpowers:dispatching-parallel-agents` | `/vibe-doc-generate` multi-doc path (already uses subagents; this enforces the discipline more rigorously) | "Routing the multi-doc autonomous fill through `superpowers:dispatching-parallel-agents` for cleaner per-doc isolation." |
| GitHub `gh` CLI | After `/vibe-doc-generate` completes — opening PRs with the generated docs, or pulling repo metadata (issues, releases, contributors) into changelog/contributing docs | "`gh` CLI is available — when generated docs are ready, I can open a PR with them, or pull recent issues/releases as input for the changelog." |

### Live-discovery heuristics

Beyond the anchored table, scan the available skills/tools list at workflow start. Surface a
complement only when you can name the specific doc type or phase it fits:

- **Documentation-writing skill** (`*doc*`, `*readme*`, `*adr*`, `*spec*`) — during `/vibe-doc-generate`
- **Library/API docs lookup** (`*context*`, `*api-docs*`, `*sdk*`) — during `/vibe-doc-generate` for external-service docs
- **Design-context skill or MCP** (Figma, design-system tools) — during `/vibe-doc-generate` for design docs
- **Code-review skill** (`*review*`, `*audit*`, `*lint*`) — after `/vibe-doc-generate` completes
- **Verification skill** (`*verify*`, `*validate*`, `*check*`) — during `/vibe-doc-check`
- **Git/forge automation** (`*github*`, `*git*`, `*pr*`, `*release*`) — after `/vibe-doc-generate` for publishing flows

When in doubt, **don't** announce.

## Common Workflows (quick mental model)

- **Scan → Classify → Gap Report:** `npx vibe-doc scan` → read `state.json` → present
  classification (confirm) → present gaps (summary) → optional walkthrough.
- **Generate → Confirm → Output:** pick docs → CLI scaffold → autonomous fill from sources →
  interview for the gaps → review → optional promote.
- **Check → Fail → Suggest:** `npx vibe-doc check` → pass: offer next steps; fail: parse
  missing/stale, suggest `/vibe-doc-generate`, show CI integration.

## Reference Documents

For detailed logic, consult these (agents only, not user-facing):

- **Classification Taxonomy** → `references/classification-taxonomy.md`
- **Documentation Matrix** → `references/documentation-matrix.md`
- **Breadcrumb Heuristics** → `references/breadcrumb-heuristics.md`
- **Friction Triggers** → `references/friction-triggers.md`

---

**Last updated:** 2026-05-24 (Antigravity port) | **Source version:** 1.0
