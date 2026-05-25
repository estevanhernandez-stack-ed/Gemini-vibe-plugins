---
description: "Render the project to PDF, HTML, markdown, or all formats. Default: PDF. Pass --guard to lint for self-review tone before rendering."
---

# /vibe-thesis-render

Renders the current Vibe Thesis project. Wraps `npm run render:<format>` with
sensible pre-steps and clean failure surfacing.

## Prerequisites

- Current directory must be a Vibe Thesis project (contains the
  `<!-- VIBE_THESIS_MARKER: vN.M -->` stanza in `AGENTS.md`).
- `npm install` must have already run (`node_modules/` present). If not,
  surface that as the first hint and offer to run it.

## Behavior

1. **Verify marker.** `grep -q "VIBE_THESIS_MARKER:" AGENTS.md`. If not present,
   refuse with: *"This doesn't look like a Vibe Thesis project (no
   VIBE_THESIS_MARKER stanza in AGENTS.md). Run `vibe-thesis` to scaffold
   first, or invoke `npm run render:pdf` directly if you know what you're
   doing."*

2. **Parse argument.** First positional arg = format, one of `pdf` (default) |
   `html` | `md` | `all`. Second positional arg = `--guard` (optional).

3. **Optional guard pre-step.** If `--guard` was passed, dispatch
   `/vibe-thesis-guard standard` first.
   - If guard reports `0 findings`: print `✓ Synthesis guard clean — proceeding to render.` and continue to step 4.
   - If guard reports `>0 findings`: surface the full findings list. Ask:
     *"Synthesis guard found N issues. Three options: (a) **render anyway** — produce the PDF with the current text, (b) **fix-and-re-run** — pause render so you can edit, then re-invoke `/vibe-thesis-render <format> --guard`, (c) **drop the --guard** — render without the gate this time."*
   - On `(a)`: proceed to step 4. Note in the manifest that render proceeded with N unresolved guard findings.
   - On `(b)`: stop here. Surface a one-line list of `<file>:<line>` references for fast navigation. Do not run render.
   - On `(c)`: proceed to step 4 with no manifest annotation.
   - **Never auto-fix the findings.** Synthesis guard is advisory; the user revises.

4. **Run pre-steps.**
   - `npm run compile-tokens` — recompiles design tokens from `tokens.yaml`.
     If it fails, the user has a malformed `tokens.yaml`; surface the
     validator output verbatim.
   - `npm run check-citations` — lints `[@key]` refs against `references.bib`.
     If missing keys are found, surface them as a clean list. Ask the builder
     to fix or proceed (proceeding produces a PDF with `[Citation Not Found]`
     markers).

5. **Run main render.**
   - `pdf` → `npm run render:pdf`
   - `html` → `npm run render:html`
   - `md` → `npm run render:markdown`
   - `all` → `npm run render:all`

6. **On success.** Read the manifest sibling file (e.g.,
   `08_OUTPUT/pdf/<name>.manifest.json`). Report:
   - Output path(s).
   - Source commit hash from manifest.
   - Design-token fingerprint.
   - Render timestamp.

7. **On failure.** Surface the failing command's stderr. Consult this small
   lookup table for diagnostic hints:

   | Symptom in stderr | Most likely cause |
   |---|---|
   | `! LaTeX Error: File 'XXX.sty' not found` | Missing TeX package; install via `tlmgr install XXX` or use the dev container |
   | `xelatex: not found` / `pandoc: not found` | Toolchain not installed; switch to dev container or `apt install texlive-xetex pandoc` |
   | `Font 'XXX' not found` | Run `.devcontainer/install-fonts.sh` (or its native equivalent) |
   | `! Missing $ inserted` (LaTeX) | Unescaped `%`, `&`, `$`, `\` in body markdown — usually in a chapter title |
   | `[Citation Not Found]` markers in PDF | Forgot to address `check-citations` warnings; missing `references.bib` entries |
   | `validate-schemas` errors | Bad `tokens.yaml` or `frontmatter` block; surface to user verbatim |

   **Do NOT silently mark the render as successful** when stderr indicates
   failure — the round-trip acceptance criterion depends on the user knowing
   when something didn't work.

## Edge cases

- `03_BODY/` is empty (just-scaffolded, no content): render produces a
  placeholder PDF with cover page + empty body. This IS the round-trip
  confirmation behavior the orchestrator's scaffold-mode relies on.
- `08_OUTPUT/` doesn't exist: create it (and the format subdir) before render.
- Both pre-steps fail: surface both errors; let user decide which to fix first.
