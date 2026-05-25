---
description: "Fast dependency + supply-chain check (CVE + lockfile + pinning)"
---

# Vibe Sec — deps

Posture and tier→ASVS are always-on via `AGENTS.md`. The tool-of-record registry
(OSV vs npm-audit) and the `Finding` schema are indexed in the `vibe-sec-guide`
skill (`.agent/skills/vibe-sec-guide/SKILL.md`) — load it before you write findings.

`/vibe-sec-deps` is the fast SCA affordance — `npm audit`-style muscle memory,
not the full audit. It runs the dependency-CVE concern plus the
lockfile-integrity + pinning subset of supply-chain hardening, and nothing else
(Decision 1: it's a UX split, not duplicated logic — `/vibe-sec-audit` runs the full
orchestration over the same primitives).

## What it runs

**Dependency CVE (#1):**

1. **Classify app-vs-lib.** Application projects get `--omit=dev` (Decision 11)
   — dev-dep CVEs are ~30% of raw npm-audit noise and a vulnerable test runner
   that never ships isn't a runtime risk. Libraries keep the full prod tree.
2. **OSV first.** Defer to `osv-scanner` on PATH (the 2026 SCA primary — schema-
   mature, cross-ecosystem, no-account). Parse `--format json`.
3. **npm audit confirms.** OSV wins on "does this CVE exist"; npm audit wins on
   "is there a fix and is it breaking." Run both, **dedupe by CVE/GHSA id**
   (Decision 12) — one finding per vulnerability even when both report it.
4. **Fix routing via isSemVerMajor.** Patch/minor in range → Auto (with
   lockfile-churn rollback: a fix churning >50 lines re-stages, Decision 20).
   Minor needing a range bump → Stage. Semver-major → Inline. No fix → inform-only.

**Supply-chain subset (the fast slice of #6):**

5. **Lockfile integrity + pinning.** Lockfile present? Integrity hashes? Floating
   pins (`latest` / `*` / `x.y.x`) flagged — they drift the resolved version
   between installs.

## What it deliberately skips (that's `/vibe-sec-audit`'s job)

- **SBOM detection/generation** — Regulated-tier supply-chain concern.
- **Typosquat round-trips** (Levenshtein vs the popular list) + dependency-
  confusion — full supply-chain pass.
- **GitHub Actions SHA-pinning + permissions** — full supply-chain pass.
- **Postinstall inspection** — full supply-chain pass.
- **Threat-model** — the sink node, `/vibe-sec-audit` / `/vibe-sec-threat-model` only.

Say so if a user asks why a typosquat or SBOM finding didn't surface here:
"`/vibe-sec-deps` is the fast path — run `/vibe-sec-audit` for the full supply-chain pass."

## EPSS / KEV

The findings schema carries `epss_score` + `kev_listed` hooks, but they're
**not wired to scoring in v0.2** (Decision 13). Hook now, score later, no
migration needed.

## Output

- **Terminal banner** — CVE counts by severity, fix-availability summary, which
  scanner produced what (osv-scanner / npm-audit / both).
- **findings.jsonl** — append-only, one finding per deduped vulnerability, with
  `fix_class` set per the isSemVerMajor routing.

## What to tell the user

Lead with the count: N vulnerabilities, M with fixes available, K requiring a
major bump (those need your review). Name whether OSV ran (deferred) or npm
audit carried it alone. If a fix is a breaking change, never auto-apply it —
route to Inline and explain why.
