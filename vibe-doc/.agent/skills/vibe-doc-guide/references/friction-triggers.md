# Friction Triggers

Source of truth for "when does each workflow log which friction type." Every workflow references this doc in its "Friction Logging" section. The vibe-doc-friction-logger SKILL reads from here at log time only via the calling workflow — this file is for humans and for any future structural audit.

## How to read this file

Each section covers one workflow. Within a section, a markdown table lists every condition under which that workflow should call `vibe-doc-friction-logger.log()`, the friction type it emits, the default confidence, and any required-field notes.

| Column | Meaning |
|--------|---------|
| **Trigger** | The observable user-or-agent behavior that should produce a friction entry. |
| **Friction type** | One of the seven canonical types from [`friction.schema.json`](../schemas/friction.schema.json). |
| **Confidence** | `high` / `medium` / `low`. Fixed per trigger — never overridden at log time (defensive default #4 in `vibe-doc-friction-logger/SKILL.md`). |
| **Notes** | Required additional fields, defensive-default reminders, complement attribution. |

The seven canonical friction types: `command_abandoned`, `default_overridden`, `complement_rejected`, `repeat_question`, `artifact_rewritten`, `sequence_revised`, `rephrase_requested`.

`/vibe-doc-evolve` weighting at high/medium/low: `1.0 / 0.6 / 0.3`.

**Universal trigger (applies to every workflow):** `command_abandoned` is never emitted directly by a workflow — it surfaces only via `vibe-doc-friction-logger.detect_orphans()`, which runs at `/vibe-doc-scan` startup as the de facto entry-point command and on demand by `/vibe-doc-evolve`. Don't list it in per-command tables; it's accounted for once, here.

## Universal triggers (any command)

| Trigger | Friction type | Confidence | Notes |
|---------|---------------|------------|-------|
| Sentinel session-log entry has no terminal pair after 24h (detected by `vibe-doc-friction-logger.detect_orphans()`) | `command_abandoned` | high | Emitted out-of-band by `/vibe-doc-scan` startup or `/vibe-doc-evolve`. Per-command sections do **not** call this. |
| User asks the agent to re-explain or simplify a previous answer, AND the prior turn is captured in `symptom` as a quoted snippet | `repeat_question` | high | **Defensive default:** without a quoted prior in `symptom`, do not log. Better to miss than poison. |
| User asks for a rephrase or restatement (e.g., "say that more plainly", "TLDR") with a quoted prior | `rephrase_requested` | medium | Capture the topic and the quoted prior in `symptom`. Same quoted-prior discipline as `repeat_question`. |

The two question-style triggers (`repeat_question`, `rephrase_requested`) apply to every command. Per-command tables below do not repeat them — they're listed once here.

---

## /vibe-doc-scan

| Trigger | Friction type | Confidence | Notes |
|---------|---------------|------------|-------|
| User declines a Pattern #13 complement offer (e.g., `context7` for tech-stack lookups during classification) | `complement_rejected` | high | Set `complement_involved` to the complement name. |
| User chooses Path B (cold start, no intake) when classification confidence ends up low (`< 0.85`) and would have benefited from intake context | `default_overridden` | medium | Quote the path-decision phrasing in `symptom`. Confidence stays medium because intake-skip is also a legitimate quick-scan signal. |
| User overrides the auto-classification result at the confirmation checkpoint (picks a different primary category than the rule engine returned) | `artifact_rewritten` | high | Capture the agent's pick and the user's pick in `symptom`. Strong signal that classifier signals or weights need adjustment. |
| User runs `/vibe-doc-generate` or `/vibe-doc-check` from the same project before the `/vibe-doc-scan` terminal entry lands (orphan-followed-by-different-command pattern) | `sequence_revised` | medium | Detected by next-command sentinel within 1h, no `/vibe-doc-scan` terminal. |

---

## /vibe-doc-generate

| Trigger | Friction type | Confidence | Notes |
|---------|---------------|------------|-------|
| User declines a Pattern #13 complement offer (typically `context7` for library/API references inside generated docs) | `complement_rejected` | high | Set `complement_involved`. Generate is the highest-density complement command — expect multiple offers per session. |
| User explicitly overrides the recommended doc-tier focus (asks to generate an Optional doc when Required tier still has unmet gaps) | `default_overridden` | medium | Quote the recommendation and the override in `symptom`. |
| User rewrites >50% of a generated doc within the same session (line diff between agent-generated and user-final version) | `artifact_rewritten` | medium | Generate artifacts are more user-shaped than scan output by nature — confidence stays medium. |
| User skips Required-tier gaps and goes straight to Optional | `sequence_revised` | low | Tier-skip is a soft default; users have legitimate reasons to start with what's easy. Confidence low. |

---

## /vibe-doc-check

| Trigger | Friction type | Confidence | Notes |
|---------|---------------|------------|-------|
| (none) | — | — | `/vibe-doc-check` is a CI-style pass/fail with no interactive surface. Exit codes only. By spec scope, `/vibe-doc-check` does not call `vibe-doc-friction-logger.log()`. |

> **Forward-looking note:** If a future version of `/vibe-doc-check` grows interactive behavior (e.g., a `--fix` flag that prompts), revisit this section.

---

## /vibe-doc-evolve

| Trigger | Friction type | Confidence | Notes |
|---------|---------------|------------|-------|
| User rejects a proposal in `proposed-changes.md` (`[reject]` interactively or removes the entry from the queue) | `default_overridden` | medium | Capture proposal title in `symptom`. The fact that `/vibe-doc-evolve` itself proposed the change is implicit — no `complement_involved`. |
| User declines a Pattern #13 complement offer (e.g., `superpowers:writing-plans` to scope a multi-step proposal) | `complement_rejected` | high | Set `complement_involved`. |
| User rewrites >50% of an accepted proposal before applying it | `artifact_rewritten` | high | Strong signal — the proposal was directionally right but executed wrong. |
| User reorders the proposal queue significantly | `sequence_revised` | low | Queue order is a soft default. Confidence low. |

---

## Adding a new trigger

When a workflow grows a new condition that should produce friction:

1. Add a row to that workflow's section above (or `Universal triggers` if it applies broadly).
2. Pick the friction type from the canonical seven. If none fit, that's a signal the type set itself needs revisiting — open an `/vibe-doc-evolve` proposal rather than coining a new type silently.
3. Pick confidence based on signal strength: high = concrete and unambiguous (line-diff, explicit reject); medium = behavioral inference; low = could plausibly be normal exploration.
4. Add the matching `vibe-doc-friction-logger.log()` invocation in the workflow at the trigger point.
