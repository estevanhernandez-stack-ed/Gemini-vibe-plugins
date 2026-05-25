---
name: vibe-taker-guide
description: "Situational reference for the vibe-taker workflows — the bundle schema, secret-file skip patterns, the stack-match decision tree, the interview gate, the error contract, JSON schemas, and artifact templates. Load when a workflow needs to validate a write or look up a rule. Always-on persona/voice/posture/hygiene live in AGENTS.md."
---

# vibe-taker — guide skill (situational reference index)

The always-on layer — persona, voice, posture (read-source-autonomously,
mandatory-diff-confirmation, stack-match modes, local-library-is-truth), the
four hygiene rules, the error-class discipline, Pattern #13 composition, and the
log-path repoint — lives in [`AGENTS.md`](/AGENTS.md) and is inherited by every
workflow. **This skill is the situational half:** the exact shapes and rules a
workflow consults mid-flight when it's about to read, decide, or write.

Load the file you need for the job — capture doesn't read `stack-match.md`, plant
doesn't read `secret-patterns.md`. Keep the working set small.

## Reference files

| Reference | What it carries | Consumed by |
|---|---|---|
| [`references/bundle-schema.md`](./references/bundle-schema.md) | Bundle directory layout, `contract.json` fields, `index.json` shape, versioning rules. | capture, plant, list |
| [`references/secret-patterns.md`](./references/secret-patterns.md) | Glob patterns matched at capture-time and skipped from `reference/`; load-bearing detection rules. | capture |
| [`references/stack-match.md`](./references/stack-match.md) | Framework-family taxonomy + the high/low/hard match table; code-lift vs spec-driven vs decline decision tree. | plant |
| [`references/interview-gate.md`](./references/interview-gate.md) | When the interview fires, what it asks, the substantive-item heuristic. | capture |
| [`references/error-contract.md`](./references/error-contract.md) | The three exit classes (0/1/2) with the per-command outcome catalog + recovery-line discipline. | capture, plant, list |

## Schemas (validate before any write)

- [`schemas/contract.schema.json`](./schemas/contract.schema.json) — per-bundle contract; capture validates before writing, plant validates before applying.
- [`schemas/index.schema.json`](./schemas/index.schema.json) — shelf manifest at `~/.vibe-taker/library/index.json`; all three workflows validate it on read, capture validates on write.

## Templates (rendered by capture, Phase 7.2)

Three artifact templates in [`templates/`](./templates/) — `README.md.template`,
`architecture.md.template`, `notes.md.template`. Capture renders them with
`{{name}}`, `{{version}}`, `{{summary}}`, `{{captured_at}}`, etc. substituted, and
fills the `None known.` sentinel for empty sections.

## Loading order (per workflow)

```
1. Inherit the always-on layer from AGENTS.md (persona, voice, posture, hygiene).
2. Read the references/*.md files this workflow's job needs.
3. Do the workflow's work; validate writes against the schemas.
4. Print the outcome per references/error-contract.md.
```
