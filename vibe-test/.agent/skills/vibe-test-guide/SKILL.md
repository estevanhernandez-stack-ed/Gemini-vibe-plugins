---
name: vibe-test-guide
description: "Internal SKILL — not a user workflow. Situational reference detail for the Vibe Test workflows: the full classification matrix (6 app types × 5 tiers × modifiers), data contracts, JSON schemas, the anchored complement registry, the friction-trigger map, and the session-memory interface index. Always-on behavior (persona, posture, composition posture, handoff/version/prereq rules) lives in AGENTS.md."
---

# vibe-test-guide — Situational Reference

Internal skill. Not a user-invocable workflow. The **always-on layer** — persona,
posture, the F2 honest-coverage stance, mode/experience adaptation, the Pattern #13
composition posture, handoff rules, version resolution, and prereq shaping — lives
in `AGENTS.md` and is loaded ambiently on every turn. This skill holds only the
**situational reference detail** a workflow loads when it's about to validate a
write, pull a classification rule, or check a complement.

If a workflow says *"load the `vibe-test-guide` skill to validate a state write or
pull a classification rule,"* this is that file.

## Where the always-on rules live

| Topic | Where |
|---|---|
| Persona registers + one-line rule | `AGENTS.md § Persona` |
| Posture / catalog-wide invariants / F2 honest-coverage | `AGENTS.md § Posture` |
| Mode + experience-level adaptation | `AGENTS.md § Posture` |
| Tier-classification stance | `AGENTS.md § Tier-classification stance` |
| Composition posture (anchored + dynamic) | `AGENTS.md § Composition (Pattern #13)` |
| Handoff language rules | `AGENTS.md § Handoff language rules` |
| Version resolution (Pattern #15) | `AGENTS.md § Version resolution (Pattern #15)` |
| Prereq shaping (Pattern #16) | `AGENTS.md § Prereq shaping (Pattern #16)` |
| Hard rules + voice | `AGENTS.md § Hard rules`, `§ Voice` |

## Where the situational reference lives

- **Data contracts:** [`references/data-contracts.md`](./references/data-contracts.md) — every state file, who writes, who reads, when, schema version.
- **Plays well with (Pattern #13 anchored):** [`references/plays-well-with.md`](./references/plays-well-with.md) — the 7 complement entries with deferral contracts.
- **Friction triggers:** [`references/friction-triggers.md`](./references/friction-triggers.md) — per-command trigger contracts. Every workflow's "Friction Logging" section mirrors a row here.
- **Schemas:** [`schemas/`](./schemas/) — JSON Schema Draft-07 for every state file.
- **Framework reference:** `docs/self-evolving-plugins-framework.md` Patterns #4, #6, #8, #10, #12, #13, #14, #15, #16.

## Classification matrix (the reference detail)

`framework.md` (monorepo root) holds the full matrix; this condensed reference
lets a workflow classify without re-loading the framework doc.

**6 app types × 5 tiers × context modifiers.**

### App types (deterministic rule match)

| app_type | Detection heuristic |
|----------|---------------------|
| `static` | No server code, no SPA framework. Flat HTML/CSS/JS. |
| `spa` | React/Vue/Svelte/etc., no detected API routes. |
| `spa-api` | SPA + one API surface (Express/Fastify/Next API routes/Hono). |
| `full-stack-db` | `spa-api` + database layer (Prisma/Drizzle/raw pg/mysql). |
| `api-service` | Server code with routes, no UI layer. |
| `multi-tenant-saas` | `full-stack-db` + auth + tenant boundary (RLS hints, org scope, user_id plumbing in routes). |

### Tiers (fuzzy — the workflow may prompt)

| Tier | Score target | Signals |
|------|--------------|---------|
| `prototype` | ≥40 | Personal scratch, no deploy target, no secrets, README says "WIP" / "experiment". |
| `internal` | ≥55 | Internal tool, team <10, no external users, deployed but auth-gated. |
| `public-facing` | ≥70 | Public URL, organic users, no PII beyond basic. |
| `customer-facing-saas` | ≥85 | Paid users, billing, uptime commitments. |
| `regulated` | ≥95 | HIPAA / SOC2 / financial / healthcare / government. |

### Context modifiers

`customer-facing`, `b2b`, `internal-only`, `auth-required`, `pii-present`, `payment-flow`, `file-uploads`, `realtime`, `offline-capable`.

The classifier applies deterministic rules where it can and prompts the builder when the signal is genuinely ambiguous (A1). When it prompts, the format is *"Looks like public-facing based on [signals] — still match?"* — never *"What tier is this?"*. Confidence starts at 0.9 for clean matches, degrades to 0.6 for mixed-stack splits (A8).

### Weighted score formula

See `src/coverage/weighted-score.ts` for the locked formula. The classifier and gate share the same pure function — identical input, identical output. No inference drift between the two call sites.

## Session-memory interface index

Every workflow wraps its run with these calls. The interfaces are skill-level; the
state-layer TypeScript under `src/state/` is invoked via the file-tool / `node -e`
patterns the workflows describe. The behavioral contract for each lives in
`AGENTS.md § Self-evolving framework`; the implementing skills are:

- **`vibe-test-session-logger`** (`.agent/skills/vibe-test-session-logger/SKILL.md`) — `start(command, project_dir) → sessionUUID`; `end(entry)`.
- **`vibe-test-friction-logger`** (`.agent/skills/vibe-test-friction-logger/SKILL.md`) — `log(entry)` → `~/.gemini/antigravity/data/vibe-test/friction.jsonl`; `detect_orphans()`.
- **`vibe-test-wins-logger`** (`.agent/skills/vibe-test-wins-logger/SKILL.md`) — `log(entry)` → `~/.gemini/antigravity/data/vibe-test/wins.jsonl` (Pattern #14).
- **`vibe-test-decay`** (`.agent/skills/vibe-test-decay/SKILL.md`) — `check_decay()`; `stamp(field_path)` (Pattern #4).
- **`vibe-test-vitals`** (`.agent/skills/vibe-test-vitals/SKILL.md`) — Pattern #8 structural pre-flight, invoked only by `/vibe-test-evolve`.

## Why this skill exists

The always-on rules every workflow needs at entry are in `AGENTS.md`. What's left
here is the heavy, occasionally-touched detail: the classification matrix, the
data/schema contracts, the anchored registry, the trigger map. Keeping it skill-side
(loaded on demand) keeps the always-on layer lean while preserving the single source
of truth for the shapes a workflow validates against.
