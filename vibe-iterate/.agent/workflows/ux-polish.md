---
description: "Run when the user says /ux-polish and wants to fix shipped-but-rough UI surfaces. Walks routes/components/key flows, identifies rough patches (inconsistent spacing, weak hierarchy, missing empty/loading/error states, dead-end paths), scores by user-trust impact, ships one polish PR + Atlas entry."
---

# /ux-polish — what's shipped but rough?

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `guide` skill (`.agent/skills/guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

The introspective banner mode. No external signal — the agent walks the user's shipped UI surfaces (routes, components, key flows), identifies rough patches, scores them on user-trust impact, picks the highest-impact item, and ships one polish PR. Atlas entry captures the full rough-spot catalog (so future invocations don't re-find the same rough spots).

For UI-bearing apps. Library / CLI / pure-backend repos can still invoke this — the agent will scope to docs / CLI affordances / API error messages / etc., but should surface that the typical "UI surfaces" walk doesn't apply and confirm scope.

## Hard rules

- **One polish PR per invocation.** Same as the other banner modes.
- **Anchor every rough patch to a specific file + line range.** "Inconsistent spacing across the app" is too vague. "`apps/web/components/UserCard.tsx:23-45` uses `mb-2` while siblings use `mb-3`" is actionable.
- **Score on user-trust impact, not aesthetic preference.** The question is "does this make the user pause / lose confidence / see something visibly broken?" — not "do I think it's pretty?"
- **Atlas write captures the full catalog.** Even rough patches not picked this round are logged so future invocations can re-prioritize without re-scanning everything.

## Session + friction logging

At workflow start — load the `session-logger` skill (`.agent/skills/session-logger/SKILL.md`) and run `start("ux-polish", <project_dir>)` to get a sessionUUID. Hold it in memory; pass it to every `friction-logger.log()` invocation.

At workflow end — call `session-logger.end({ sessionUUID, outcome, user_pushback, friction_notes, key_decisions, atlas_outcome, atlas_title, pr_url })` per the schema.

Honor the friction trigger map at `.agent/skills/guide/references/friction-triggers.md` — section `/ux-polish` — for which friction types to log at which confidence.

## Inputs

- **No required arguments.** Optional `--scope <path>` to restrict the walk to a subdirectory (e.g., `--scope app/admin/` to polish just the admin surface).
- **Project state required:** `.vibe-iterate/config.json` (for `category` — used to detect if this is a UI-bearing app). If absent, hand off to bootstrap.

## Procedure

### Step 1 — posture announcement

> *UX-polish mode → conservative posture, smallest-diff fix per surface, regression checks aggressive (visual + behavioral). Walking the surfaces, scoring rough patches, picking ONE to fix.*

### Step 2 — UI-surface check

Read `config.category`. If category is one of:

- `library-sdk`, `cli-tool` → surface: *"This is a [category] — typical UX-polish targets UI surfaces. For this project, I'll scope to: docs, CLI error messages, README clarity, API error shapes. Continue with this scope, or pause? (continue / pause)"*
- `agent-plugin` → surface: *"Agent plugin scope — I'll target workflow/skill descriptions, error messages, and user-facing prompts. Continue? (continue / pause)"*
- `web-app`, `mobile-app`, `desktop-app`, `monorepo` → proceed with normal UI walk

### Step 3 — Cart-detection (early read)

Per AGENTS.md § Cart-detection. Note: present | absent. UX-polish iterations are usually small (single component), but a multi-flow polish could trigger heavy.

### Step 4 — walk the surfaces

For UI-bearing apps:

**A. Routes / pages** — find route definitions:
- Next.js: `app/**/page.tsx`, `pages/**/*.tsx`
- React Router: grep for `<Route path=...>`
- Vue Router: grep for `routes:` array entries
- Mobile (React Native / Expo): `app/**/*.tsx` (Expo Router) or screen registrations

**B. Components** — find shared components:
- `components/`, `src/components/`, `apps/*/components/`

**C. Key flows** — identify multi-step flows by reading code paths that span multiple components/routes (e.g., onboarding, checkout, settings save, search).

For non-UI apps, scope per step 2.

For each surface (route, component, flow), inspect for the **standard rough-patch checklist**:

1. **Empty states** — what does the user see when the list is empty / no results / no data?
2. **Loading states** — is there a visible loading affordance for slow operations?
3. **Error states** — when an API call fails, is the error visible AND actionable?
4. **Dead-end paths** — can the user always get back to a known-safe state? (Back button works? "Home" link visible?)
5. **Visual hierarchy** — primary action visually distinct from secondary?
6. **Spacing consistency** — are similar surfaces using consistent spacing tokens / patterns?
7. **Loading-skeleton vs blank** — do slow renders show a skeleton or just a blank space?
8. **Disabled states** — are disabled buttons visually distinct from enabled?
9. **Form validation messaging** — are errors near the input that triggered them?
10. **Mobile responsiveness** — if the project supports mobile, do flows work at narrow viewports?

For each rough patch found, capture: `file_path`, `line_range`, `surface` (route/component/flow name), `category` (which checklist item), `description` (one line), `evidence` (the actual code snippet or visual artifact reference).

Cap at 30 distinct rough patches. If more, prioritize by surface visibility (routes > shared components > internal components).

### Step 5 — score each rough patch on user-trust impact

Use the **user-trust-impact rubric** (also used by `/rate`):

**(a) Breaks trust** — score 5 (highest priority)
- Empty state with no message ("nothing here, no idea why")
- Error swallowed silently (action does nothing, no feedback)
- Dead-end path with no exit (user has to refresh to escape)
- Broken-looking layout (overlapping elements, cut-off text, broken images)

**(b) Erodes trust** — score 3 (medium priority)
- Inconsistent spacing across the same flow
- Missing loading state on a slow action (>500ms)
- Weak visual hierarchy on a primary screen (CTA not distinguishable)
- Form validation messages far from the input

**(c) Cosmetic** — score 1 (low priority, often skipped)
- 4px alignment drift
- Font-weight inconsistency in a secondary surface
- Minor color drift in a peripheral surface

For each rough patch, also estimate effort (1-5, inverse — same as `/rate`): how big is the diff to fix this one rough patch?

### Step 6 — pick the top rough patch

Sort by `(user_trust_score * 2) + effort_score` descending — weights trust 2x effort. Top entry is the recommendation.

Surface to user:

```
UX-polish scan — <N> surfaces walked, <N> rough patches found

Breaks trust (high priority)
- <surface>: <description>  ← <file>:<line-range>  | Trust: 5  | Effort: <N>/5
- ...

Erodes trust (medium priority)
- <surface>: <description>  ← <file>:<line-range>  | Trust: 3  | Effort: <N>/5
- ...

Cosmetic (low priority — often skipped)
- <surface>: <description>  ← <file>:<line-range>  | Trust: 1  | Effort: <N>/5
- ...

Recommendation: fix #1 (<title>)  — Trust 5, Effort <N>/5

Fix #1, pick another (give number), or pause? (1 / pick / pause)
```

Wait for user response.

### Step 7 — Cart-detection (heavy iteration check)

Most UX-polish iterations are small. If the chosen patch turns out to be heavier than scored (e.g., "fix the empty state" expands to "redesign the data-loading layer"), surface and trigger Cart-detection per AGENTS.md § Cart-detection.

### Step 8 — implement (build phase)

Same as `/ship` build phase: pre-flight tests → implement the fix → post-flight tests → open PR.

For UI work, "tests" includes:
- Existing automated test suite (jest, vitest, playwright)
- A manual visual check: render the affected surface in dev, take a before/after screenshot if possible. Note in PR description if a manual visual check was done.

### Step 9 — open the PR

PR description shape:

```markdown
## Summary
Polish: <surface> — <one-line on the rough patch and the fix>

## Rough patch
- File: <file>:<line-range>
- Surface: <route/component/flow name>
- Category: <user-trust-impact tier>: <description>
- Evidence: <screenshot link OR code-snippet quote>

## Fix
<bulleted list of changes>

## Test plan
- [x] Pre-flight tests: <N pass / N fail>
- [x] Post-flight tests: <N pass / N fail>
- [ ] Manual visual check in dev: <surface URL>

## Other rough patches found this scan (not fixed in this PR)
<bulleted list — 5-10 max — captured in Atlas for future invocations>

🤖 Generated with [vibe-iterate](https://github.com/estevanhernandez-stack-ed/vibe-iterate) /ux-polish
```

### Step 10 — Atlas write

Append to `.vibe-iterate/atlas.jsonl`:

```json
{
  "ts": "<ISO-8601 UTC, now>",
  "mode": "ux-polish",
  "outcome": "shipped",
  "title": "<surface>: <one-line fix description>",
  "rationale": "User-trust tier: <breaks-trust | erodes-trust | cosmetic>. Surface: <name>. Other rough patches found: <count> (top trust=5: <count>; top trust=3: <count>; top trust=1: <count>). Cart-detection: <light | delegated>.",
  "rejected_runners_up": ["<other top-3 rough patches not picked, as titles>", "..."],
  "pr": "<PR URL>"
}
```

The `rejected_runners_up` array logs the catalog — future `ux-polish` invocations should consult this and skip already-noted patches that haven't materially changed.

If user paused: `outcome: "queued"`, `pr: null`. If declined mid-build: `outcome: "rejected"`, `pr: null`.

### Step 11 — close out

```
Polished:
- Surface: <name>
- Fix: <one-line>
- PR: <url>
- Atlas: <.vibe-iterate/atlas.jsonl> (catalog logged)
- Other rough patches found: <N>  (trust=5: <N>, trust=3: <N>, trust=1: <N>)
- Tests: <pre N/N → post N/N>

Next:
- Re-run /ux-polish to fix the next rough patch
- Or /vibe-iterate to get a fresh mode recommendation
```

## Anti-patterns

- **Don't surface aesthetic preferences as rough patches.** "I'd use a different font" is not user-trust impact. Stick to the rubric.
- **Don't bundle multiple polish fixes into one PR.** One rough patch per PR; the next invocation gets the next one.
- **Don't skip the manual visual check.** Tests catch behavior; visual regressions need eyes.
- **Don't expand into a full UI redesign.** If the chosen patch reveals broader issues, surface that and trigger Cart-detection — don't quietly grow.

## Cross-references

- Rubric source-of-truth: this SKILL (cited by `/rate`)
- Sidecar called: `/rate` (for effort scoring per patch), `/ship` (for build phase)
- Cart-detection: AGENTS.md § Cart-detection
- Atlas conventions: `.agent/skills/guide/references/atlas-conventions.md`
