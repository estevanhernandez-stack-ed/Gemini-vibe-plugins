---
description: "Run when the user says '/vibe-keystone' or wants to bootstrap an AGENTS.md for a repository, with tenant-aware adaptation. Interviews the user for org / decision surface / voice rules / persona before drafting, so the produced file reflects THEIR conventions — not 626Labs defaults baked in. The keystone is the load-bearing structural file — every agent decision in the repo rests on it. Use when starting in a new repo without an AGENTS.md, or when the existing one is stale. Trigger phrases include 'set up AGENTS.md', 'create the keystone', 'bootstrap agents md', 'agents md for this repo', 'agent rules for this repo'."
---

# /vibe-keystone — bootstrap a 626Labs-pattern AGENTS.md

You are an agent in a 626Labs-owned (or 626Labs-style) repository. Your task is to produce an `AGENTS.md` for this repo following the 626Labs project-rules pattern. Read this entire workflow before writing anything.

The keystone is the load-bearing structural file: every decision the agent makes in the repo rests on it. On Antigravity, that file is `AGENTS.md` — the always-on ruleset every workflow and agent reads. Get it right.

> **A note on tooling.** This is the Antigravity port. The Claude Code original wrote `CLAUDE.md`; Antigravity's equivalent always-on rules file is `AGENTS.md`, so that is what you produce here. If the repo also has a `CLAUDE.md` (e.g. it's used with Claude Code too), you may read it for context — but the file you write is `AGENTS.md`.

## Step 0 — Refuse to write blind

Before producing the file, inventory the repo:

1. `git status` and `git log --oneline -20` — branch state + recent rhythm
2. `ls -la` — top-level layout
3. Read `package.json`, `pyproject.toml`, `Cargo.toml`, or whatever defines the stack
4. Read existing `README.md` and any top-level `*.md` files
5. Check for: `.agent/`, `.claude/`, `.husky/`, `.github/workflows/`, `scripts/`, `docs/`, `.ai/`
6. Look for build/deploy infra: `Makefile`, `Dockerfile`, GitHub Actions, etc.
7. **If `AGENTS.md` already exists**, read it before overwriting. Do not blindly replace. (Also read a `CLAUDE.md` if present — it's a sibling rules file worth folding context from — but write `AGENTS.md`.)

Identify the repo type:

- **Code platform** (services, apps, libraries, plugins)
- **Marketing/content site** (public-facing, copy-heavy)
- **Long-form writing / thesis** (prose-heavy, citation-bound)
- **Infrastructure / mixed** (multiple surfaces)

## Step 1 — Tenant interview before drafting

Before an AGENTS.md is meaningful, you need to know whose conventions it should encode. This workflow ships with **626Labs defaults** baked in (Dashboard MCP for decisions, 626Labs voice rules, brand tokens, Architect persona inheritance) — but those should only land when the user is actually 626Labs. For any other tenant, ask first.

Ask the user in one round (concise — single message back). Group the questions and let them skip ones that don't apply:

### Tenant identity

1. **Whose repo is this — 626Labs, another organization, an individual project?**

   If 626Labs: the defaults apply (Dashboard MCP, brand voice, Architect persona). Skip to question 4.

   If another tenant, follow up:
   - What's the organization or individual name? (Used in references throughout the produced AGENTS.md.)
   - **Do you have tenant docs I should read before drafting?** Examples: a global rules file defining a persona, an org `HANDBOOK.md`, a `CONTRIBUTING.md`, a `VALUES.md` / principles doc, a brand voice guide, a style guide, an architecture doc. **Name the paths and I'll read them before drafting** — your priorities, voice rules, and conventions should fold into the produced file.

### Decisions log

2. **Where do significant decisions log?**
   - A decision-log MCP — if your org runs one, name it; the 626Labs pattern auto-detects the recognized `mcp__626labs-cloud__manage_decisions` dashboard when present (default for 626Labs repos)
   - A different MCP / tool (name it)
   - A `decisions.md` (or similar) file in the repo
   - An external tracker (Linear / Jira / Notion / GitHub Issues)
   - None — decisions live in commit messages and PR descriptions only

### Persona

3. **Persona inheritance:**
   - **Inherit from global** — does a global rules file (e.g. `~/.gemini/antigravity/AGENTS.md`, or whatever your tool reads as global) define a persona this repo should reference (e.g., 626Labs's "The Architect")? If yes, the produced AGENTS.md will say "inherits {name}, no need to re-establish."
   - **Override** — does this repo need its own persona that supersedes global (typical for writing/thesis where Lead Writer takes over)?
   - **No persona** — the repo doesn't operate under a named persona; skip the persona block entirely.

### Repo type and existing agents

4. **Primary work mode:** code platform / marketing-content / writing-thesis / infrastructure-mixed
5. **Existing agent config?** — list any `.agent/` workflows/skills or `.claude/agents/` already present, or "propose new ones based on the repo type."

### If refreshing an existing AGENTS.md

If `AGENTS.md` already exists, also ask: keep the existing persona/voice/structure and refresh the rest, or rewrite section-by-section?

---

After the user answers, **read any tenant docs they named before drafting**. Tenant priorities, voice rules, and decision-log conventions should fold into the produced AGENTS.md instead of inheriting 626Labs defaults that don't apply.

Carry these answers downstream as adaptations:

| Section | 626Labs default | Other tenant — substitute |
|---|---|---|
| Tech Stack & Voice (content-bearing repos) | 626Labs voice rules + brand tokens (cyan, magenta, navy, Space Grotesk, etc.) | Pull from tenant brand/voice docs. If no docs, propose a minimal voice block and ask the user to confirm. |
| Design system reference | `~/.gemini/antigravity/skills/626labs-design/` | Tenant's equivalent if any; otherwise drop the section. |
| Decisions log | A decision-log MCP if the org runs one (the 626Labs pattern auto-detects `mcp__626labs-cloud__manage_decisions log`) | Whatever the user named in Q2. If "none," drop the section or point at commit/PR conventions. |
| Persona inheritance note | The Architect (or whatever 626Labs has) | Tenant's persona name, or "no persona" framing. |

## Step 2 — Skeleton (sections in this order)

Produce an `AGENTS.md` with these sections. Drop sections marked CONDITIONAL when they don't apply.

### 1. Title + persona inheritance note (ALWAYS, conditional on Step 1 Q3)

If the user said **inherit from global**:

```markdown
# {Repo Name}

> **Persona:** This repo inherits {global persona name from Step 1} from the global rules file. No need to re-establish — just adds project context below.
```

If the user said **override** (writing/thesis case):

```markdown
> **Persona override:** In this repo, you operate as {Project Persona} — not the global one. {Persona} supersedes for {scope}; global process habits (gather context, log decisions, assess blast radius) still apply to project work (commits, file moves, MCP calls).
```

If the user said **no persona** at all, drop the blockquote entirely. Just the `# {Repo Name}` title.

### 2. Tech Stack (ALWAYS) — paired with Voice for content-heavy repos

For a code-only repo:

```markdown
## Tech Stack

- **Language/Framework:** {actual}
- **Build:** {actual}
- **Deploy:** {actual}
- **Testing:** {actual}
```

For any public-facing / content-bearing repo, add a Voice section.

**If 626Labs-owned (Step 1 Q1):**

```markdown
## Tech Stack & Voice

- **Stack:** {as above}
- **Brand:** Cyan `#17d4fa` + magenta `#f22f89`, always paired. Navy `#0f1f31` field. Space Grotesk display, Inter body, JetBrains Mono code/meta (uppercase + 0.12em tracking on small labels).
- **Voice:** Builder-to-builder, second person, sentence case. No "empower / leverage / seamlessly / unlock / unleash." Em-dashes welcome. No emoji in UI copy or marketing surfaces. Tagline: *Imagine Something Else.*
```

**If another tenant:** pull voice rules + brand tokens from any tenant docs the user named in Step 1. Match the tenant's existing brand voice rather than inventing one. If no tenant voice docs exist, write a minimal block and ask the user to confirm or extend:

```markdown
## Tech Stack & Voice

- **Stack:** {as above}
- **Voice:** {tenant-provided voice rules, OR — if none — a minimal "builder-to-builder, second person, no corporate speak" placeholder for the user to extend}
- **Brand:** {tenant-provided tokens, OR — if none — note "no brand tokens established"}
```

### 3. Design system reference (CONDITIONAL — visual repos AND a design skill exists)

**If 626Labs-owned:**

```markdown
## Design system

Canonical brand spec lives at `~/.gemini/antigravity/skills/626labs-design/` (globally available — same skill across every 626 Labs repo). Use `colors_and_type.css` as the token source and `ui_kits/` as the pattern reference. Local `Design/` (or wherever this repo keeps brand artifacts) is for repo-specific references only.
```

**If another tenant with their own design skill / system docs:** point at their canonical brand spec the same way.

**If no tenant design system exists:** drop this section entirely. Don't fabricate a reference.

### 4. What's Where (ALWAYS)

A markdown table with paths and one-line purposes. One row per major directory or load-bearing file. Anyone should find anything in 5 seconds.

```markdown
## What's where

| Path | What it is |
|---|---|
| `src/` | {one line} |
| `scripts/` | {one line} |
| ... |
```

### 5. Domain-specific section (CONDITIONAL — every repo has one)

This is the operational center of gravity. Pick what applies:

- **Code platform:** MCP server / infrastructure / API surface / federation pattern
- **Site:** How the site rebuilds, bot workflows
- **Writing:** Mode switching (THESIS_MODE), citation discipline
- **Mixed:** A "How the system works at runtime" overview

Use sub-headings under one parent section. Be concrete — name the actual files, scripts, workflows, and triggers.

### 6. Common tasks (ALWAYS)

```markdown
## Common tasks

| You want to… | Path / command |
|---|---|
| {task} | {how} |
```

5–10 rows covering the most frequent operations.

### 7. Conventions (ALWAYS)

```markdown
## Conventions

- **Commits:** Conventional commits ({list types — for thesis repos use academic-flavored: draft / revise / cite / respond / meta / chore})
- **Style:** {brief, stack-specific}
- **File rules:** {what's read-only, what's generated, what's the canonical source}
```

### 8. Decisions log (CONDITIONAL on Step 1 Q2 — drop entirely if user said "none")

The shape adapts to the user's answer in Step 1 Q2.

**If a decision-log MCP (auto-detected — e.g. the 626Labs dashboard):**

```markdown
## Decisions log

Significant decisions log to a decision-log MCP when one is available — the 626Labs pattern auto-detects the recognized **626Labs Dashboard** (`mcp__626labs-cloud__manage_decisions log`). It's optional: if no such MCP is present, fall back to a `decisions.md` (or your team's tracker), or skip. Never required. When logging, tag with the bound project ID. The bar: *would future-you (or someone asking "why this approach?") want to know this in 3–6 months?*

Especially:
- {category 1, repo-specific}
- {category 2}
- {3–5 categories total}

Skip the routine: {what doesn't get logged}.

If unbound (no project match): tag with the repo name in the description and set `projectId: null`.
```

**If a different MCP / tool:** swap the tool name and any binding mechanics. Same shape, same bar. Keep the MCP optional — name a fallback when it's absent.

**If a `decisions.md` file:**

```markdown
## Decisions log

Significant decisions land in `decisions.md` (or `docs/decisions/` for ADR-style). Each entry: date, title, context, decision, consequences. The bar: *would future-you want to know this in 3–6 months?*

Categories worth logging: {repo-specific list}. Skip the routine.
```

**If an external tracker (Linear / Jira / Notion / GitHub Issues):** point at the tracker, link to the project/board, name the labels or convention used to mark "decision" entries.

**If "none":** drop this section entirely. Don't fabricate a decision-log surface that doesn't exist. Optionally add a one-line note in the Conventions section: "Significant decisions are captured in commit messages and PR descriptions; no separate decision log."

### 8b. Knowledge & taste — repo as system of record (CONDITIONAL — repos with tacit conventions worth capturing)

The agent only sees what's in the repo. Taste, "we don't do it that way here," the reasoning that lives in Slack threads and someone's head — none of it reaches the agent unless it's written down where the agent reads. For any repo with real tacit conventions, designate an in-repo home for them and name it here.

```markdown
## Knowledge & taste

The repo is the system of record — if it isn't written here, the agent can't see it.

- **Conventions / taste:** {path — e.g., `docs/conventions.md`, or this file's Conventions section}
- **Why-decisions:** {the decisions-log surface named above}
- **Things the agent keeps getting wrong:** capture the correction as a short note in {path} the moment it surfaces, instead of re-explaining it every session.
```

Drop this section when the repo has no tacit conventions beyond what Conventions already covers (most greenfield or solo scratch repos). Don't manufacture a knowledge base that doesn't exist.

### 9. What NOT to do (ALWAYS)

3–5+ explicit, repo-specific guardrails. Each one names the failure mode and (where useful) the right alternative.

```markdown
## What NOT to do

- **Don't {specific thing}** — {why, or what to do instead}
- ...
```

Examples to draw from when identifying don'ts: don't hand-edit generated files (and the right edit point), don't bypass the build pipeline, don't commit secrets, don't force-push to main, don't fabricate citations (thesis), don't write to read-only directories.

### 10. References (CONDITIONAL — when any of these exist)

```markdown
## References

- Architecture details: {path}
- Agent workflows / skills: `.agent/workflows/`, `.agent/skills/`
- Specialized agents (Claude Code, if dual-tool): `.claude/agents/`
- CI/CD: `{path}`
```

## Step 3 — Output discipline

- File: `AGENTS.md` at repo root
- Headings: ATX (`#`, `##`, `###`)
- Prose: terse, action-first
- No emoji in file content
- Em-dashes welcome
- Code fences for commands; markdown tables for paths/tasks/conventions
- Voice: builder-to-builder, second person, no hedging, no corporate speak
- **Append-safe.** Antigravity merge-appends AGENTS.md into a project's existing rules. Write the file self-contained, but don't assume it's the only ruleset present — no "this is the entire context" framing.

## Step 4 — Self-check before claiming done

Verify:

- [ ] Every ALWAYS section is present
- [ ] At least 3 explicit "What NOT to do" items, each repo-specific
- [ ] References specific paths/files in this repo (not generic placeholders)
- [ ] Decisions log section points at 626Labs MCP (when 626Labs-owned)
- [ ] No re-establishing the global persona (unless explicitly overriding)
- [ ] No snapshot lists ("recent decisions", "current sprint") that will rot
- [ ] Voice section present if repo has public-facing surface

## Step 5 — Propose follow-ups (don't auto-create)

After the AGENTS.md lands, propose:

- Agent workflows/skills under `.agent/` (or `.claude/agents/` for Claude Code dual-tool repos) that would serve recurring tasks in this repo (code-reviewer, security-auditor, copy-reviewer, visual-asset-reviewer, citation-checker, devils-advocate, story-editor, etc. — pick what fits)
- Reference docs for specialized guidance that doesn't fit in AGENTS.md
- Automation that closes a feedback loop (template-edit drift checks, type-check-after-edit, etc.), if the host tool supports it

Each suggestion is a proposal. The user decides what gets built.

## Step 6 — Capture for evolution (opt-in, off by default)

Keystone is a one-shot generator — it writes a great file and never sees it again, so on its own it can't learn which parts of the skeleton it keeps getting wrong. This step is the smallest possible sensor that fixes that, and it is **strictly opt-in**.

After the AGENTS.md lands, ask once:

> "Want me to record a small, anonymous note about what this run produced, so `/vibe-keystone-evolve` can spot patterns and improve the skeleton over time? It's local-only, opt-in, and captures structure — never your code or your org's name. [y/N]"

Default is no. A "no" — or no answer — writes nothing.

**Only if the user says yes**, append one JSON line to `~/.gemini/antigravity/data/vibe-keystone/captures.jsonl` (create the directory if absent). The agent performs this append directly — **Keystone ships no scripts**, and this step does not introduce one. Capture exactly this shape, and nothing more:

```json
{
  "schema_version": 1,
  "timestamp": "<ISO local datetime>",
  "run_type": "fresh | refresh",
  "tenant_kind": "626labs | other-org | individual",
  "repo_type_autodetected": "code | marketing-content | long-form-writing | infra-mixed",
  "repo_type_final": "code | marketing-content | long-form-writing | infra-mixed",
  "sections_included": ["title", "tech-stack", "what-where"],
  "sections_dropped": ["design-system", "decisions-log"],
  "sections_overridden": [{ "section": "persona", "from_default": "inherit", "to": "override" }],
  "sections_requested_not_in_skeleton": ["<free-text label of a section the user asked for that the skeleton doesn't offer>"]
}
```

`repo_type_autodetected` is your Step 0 classification; `repo_type_final` is what it ended up as after the interview. When they differ, that's the signal `/vibe-keystone-evolve` uses to tune the classifier.

**Hard privacy rules for capture:**

- Never write the tenant's name, the repo's name, file paths from the repo, source code, or any AGENTS.md content. Only the structural signal above.
- Opt-in per run. Default off.
- Local only — no network, ever. This is the one place Keystone writes outside the repo's `AGENTS.md`; it is disclosed in `PRIVACY.md`.
- If the append fails for any reason, say so in one line and move on — capture never blocks the run.

---

## Repo type quick reference

**Code platform:**

- Tech Stack only (no Voice section unless platform also has marketing surface)
- Domain section: architecture, MCP, federation pattern, infrastructure
- Conventions emphasize type safety, testing, styling
- "What NOT to do": code-quality + deployment guardrails

**Marketing / content site:**

- Tech Stack & Voice combined (voice is load-bearing)
- Add Design system section
- Domain section: rebuild pipeline, bot workflows, asset flow
- "What NOT to do": content/build pipeline + brand discipline

**Long-form writing / thesis:**

- Persona override clause is mandatory
- Add Citation discipline section
- Mode switching (if template-driven)
- Academic-flavored commits (draft / revise / cite / respond / meta)
- "What NOT to do": fabrication + scope creep + manifest discipline

**Infrastructure / mixed:**

- Tech Stack covers all surfaces
- Domain section: runtime model + cross-surface coordination
- "What NOT to do": cross-surface coordination guardrails

---

## What you do not do

- Do not write AGENTS.md without inventorying the repo first. Blind writes produce generic, useless files.
- Do not re-establish the global persona unless explicitly overriding. The global persona already loads; the repo AGENTS.md adds project context, doesn't restate identity.
- Do not list "current state" or "recent decisions" snapshot-style. Those rot. Always describe how to *find* state, never enumerate the current values.
- Do not include voice rules without a public-facing surface to apply them to. Code-only platforms don't need the brand voice section.
- Do not auto-create agent config (`.agent/` workflows/skills, `.claude/agents/`, reference docs, automation). Propose them; let the user decide.
- Do not overwrite an existing AGENTS.md without showing a diff and confirming.
