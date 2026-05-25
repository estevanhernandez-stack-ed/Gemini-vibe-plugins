#!/usr/bin/env python3
"""
port.py — Claude Code plugin -> Google Antigravity 2.0 mechanical transform.

The deterministic ~80% of the port pipeline. Reads a Claude Code plugin dir
(skills/, optional commands/, .claude-plugin/plugin.json) and emits an
Antigravity port skeleton (.agent/workflows/, .agent/skills/, .agent/agent.json,
a scaffolded AGENTS.md with TODO markers).

The judgment ~20% (guide->AGENTS.md prose synthesis, the always-on/situational
split, edge classifications, evolve-* self-edit retargeting, open-question
re-check) is intentionally NOT done here. It's the finishing pass — see
PORT-RUNNER.md. This script emits a port-report.json that tells the finishing
pass exactly what's left.

Python 3.11+, stdlib only. The golden reference is vibe-iterate@1.1.0
(vibe-plugins-ports/vibe-iterate/) ported from
vibe-iterate/plugins/vibe-iterate/. See PORTING.md for the authoritative recipe.

Usage:
    python port.py <claude-plugin-dir> <output-dir> [--plugin-name NAME] [--quiet]

Example:
    python port.py \\
        C:/Users/estev/Projects/vibe-iterate/plugins/vibe-iterate \\
        C:/temp/vibe-iterate-port
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path


# ---------------------------------------------------------------------------
# Classification
# ---------------------------------------------------------------------------

# A description is user-invocable if it references a real slash trigger OR uses
# the canonical "use when the user says" phrasing. The cookbook's load-bearing
# lesson: trust the slash-trigger phrasing over an "internal" self-label
# (bootstrap calls itself "Internal SKILL" but lists /<plugin>:bootstrap).
#
# A REAL slash trigger is a command invocation, not a slash inside a path
# ("skills/guide/references/x.md") or a slash-delimited qualifier list
# ("regression-aware/user-trust-aware"). We only count a slash that:
#   - starts at a word boundary (preceded by start, space, backtick, or quote),
#   - is NOT followed by another path segment ending in ".md" or "/", and
#   - is either namespaced (/plugin:cmd) OR appears in a trigger context
#     (backtick-wrapped, quoted, or after "user says" / "user types").
# This is intentionally strict: false positives flip a skill into a workflow,
# which is the worst failure mode (it nukes the guide split). When unsure the
# script defaults to skill and flags the edge for the finishing pass.
SLASH_TRIGGER_RE = re.compile(
    r"""(?<![\w/])           # not preceded by word char or slash (path)
        /([A-Za-z][\w-]*(?::[\w-]+)?)  # /cmd or /plugin:cmd
        (?![\w-]*/)          # not followed by more path (…/x/…)
        (?!\.[a-z])          # not a filename (…/x.md)
    """,
    re.VERBOSE,
)
# Trigger context: a slash command that's clearly invoked, not incidental.
TRIGGER_CONTEXT_RE = re.compile(
    r"""(user\s+(?:says|types|invokes|runs)\s*[`'"]?/[\w:-]+   # "user says /x"
        |`/[\w:-]+`                                            # `/x` backtick
        |/[\w-]+:[\w-]+)                                       # /plugin:cmd
    """,
    re.IGNORECASE | re.VERBOSE,
)
USER_SAYS_RE = re.compile(
    r"\b(?:use[ds]?\b.*\bwhen the user says|when the user says|"
    r"when the user (?:types|invokes|runs))\b",
    re.IGNORECASE,
)
# Strict internal label: "Internal SKILL — not a slash command/user". A skill
# that says THIS and has no real trigger is unambiguously a skill.
INTERNAL_LABEL_RE = re.compile(
    r"internal skill\b.*?not a (?:slash command|user)", re.IGNORECASE
)
# Soft internal self-label: any "Internal SKILL" framing. Used only to FLAG an
# edge — a soft-internal skill that ALSO carries a real trigger is bootstrap's
# exact case (ports as a workflow, but the disagreement is worth a human eye).
SOFT_INTERNAL_RE = re.compile(r"\binternal skill\b", re.IGNORECASE)


def parse_frontmatter(text: str) -> tuple[dict, str]:
    """Split a SKILL.md into (frontmatter dict, body). Minimal YAML: flat
    key: value pairs, values may be quoted. Good enough for plugin frontmatter
    (name + description), which is all the cookbook touches."""
    if not text.startswith("---"):
        return {}, text
    end = text.find("\n---", 3)
    if end == -1:
        return {}, text
    raw = text[3:end].strip("\n")
    body = text[end + 4:]
    if body.startswith("\n"):
        body = body[1:]
    fm: dict[str, str] = {}
    cur_key = None
    for line in raw.splitlines():
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m:
            cur_key = m.group(1)
            val = m.group(2).strip()
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            fm[cur_key] = val
        elif cur_key is not None and line.strip():
            # folded continuation line
            fm[cur_key] = (fm[cur_key] + " " + line.strip()).strip()
    return fm, body


@dataclass
class SkillInfo:
    name: str            # dir name (the slash name / skill name)
    src_dir: Path
    skill_md: Path
    frontmatter: dict
    body: str
    classification: str  # "workflow" | "skill"
    reason: str
    edge_flag: bool = False   # classification disagreed with the self-label
    has_extra_files: bool = False  # references/ schemas/ fixtures/ scripts/


def classify(name: str, fm: dict, plugin_name: str) -> tuple[str, str, bool]:
    """Return (classification, reason, edge_flag).

    Rules (from PORTING.md TL;DR move 1 + the bootstrap lesson in move-by-move):
      - description references a slash trigger (/x or /plugin:x) -> workflow
      - description says "use when the user says" -> workflow
      - description self-labels "Internal SKILL — not a slash command" AND has
        no slash trigger -> skill
      - guide-style "referenced by every command, never invoked" -> skill (the
        guide gets a special split flag downstream)
    The edge_flag fires when the self-label and the slash-trigger evidence
    disagree (bootstrap), so the finishing pass eyeballs it.
    """
    desc = fm.get("description", "")
    internal_label = bool(INTERNAL_LABEL_RE.search(desc))

    # A slash trigger only counts as user-invocable evidence when it appears in
    # a real trigger CONTEXT (backtick-wrapped, namespaced /plugin:cmd, or after
    # "user says/types"). A bare slash inside a file path or a slash-delimited
    # qualifier list does NOT count — that's what flipped guide/friction-logger
    # to workflows in the first cut.
    has_trigger_context = bool(TRIGGER_CONTEXT_RE.search(desc))
    says_user = bool(USER_SAYS_RE.search(desc))
    user_invocable = has_trigger_context or says_user
    triggers = SLASH_TRIGGER_RE.findall(desc) if user_invocable else []

    # Guide / shared-behavior special case: stays a skill (and gets the split).
    if re.search(r"referenced by every command|never invoked directly|"
                 r"shared behavior|loaded as a reference|used internally by",
                 desc, re.IGNORECASE) and not user_invocable:
        return "skill", "shared-behavior reference, never user-invoked", False

    if internal_label and not user_invocable:
        return "skill", "self-labeled internal, no real slash trigger", False

    if user_invocable:
        trig = (f"/{triggers[0]}" if triggers else "use-when-user-says")
        # bootstrap's case: any "Internal SKILL" framing PLUS a real trigger.
        # Ports as a workflow (trust the trigger) but flag the disagreement.
        if internal_label or SOFT_INTERNAL_RE.search(desc):
            return (
                "workflow",
                f"real slash trigger ({trig}) despite 'internal' self-label — "
                "trust the trigger (cookbook bootstrap lesson)",
                True,
            )
        return "workflow", f"user-invocable slash trigger ({trig})", False

    # No strong signal: default to skill (semantic-load), flag for review.
    return "skill", "no real slash trigger or user-says phrasing — defaulted to skill", True


# ---------------------------------------------------------------------------
# Repoint rules (the scriptable string transforms from PORTING.md)
# ---------------------------------------------------------------------------

@dataclass
class Repoint:
    label: str
    pattern: re.Pattern
    repl: str  # may use backrefs
    count: int = 0


def build_repoints(plugin_name: str) -> list[Repoint]:
    pn = re.escape(plugin_name)
    rules = [
        # --- path repoints ---
        Repoint(
            "data-path",
            re.compile(r"~/\.claude/plugins/data/"),
            "~/.gemini/antigravity/data/",
        ),
        Repoint(
            "builder-profile",
            re.compile(r"~/\.claude/profiles/builder\.json"),
            "~/.gemini/profiles/builder.json",
        ),
        # any remaining ~/.claude/... (catch-all, after the specific ones)
        Repoint(
            "claude-home-generic",
            re.compile(r"~/\.claude/"),
            "~/.gemini/antigravity/",
        ),
        # --- manifest / env repoints ---
        Repoint(
            "plugin-root-manifest",
            re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/\.claude-plugin/plugin\.json"),
            ".agent/agent.json",
        ),
        Repoint(
            "plugin-root-generic",
            re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}"),
            ".agent",
        ),
        Repoint(
            "plugin-json",
            re.compile(r"\.claude-plugin/plugin\.json"),
            ".agent/agent.json",
        ),
        Repoint(
            "claude-md",
            re.compile(r"\bCLAUDE\.md\b"),
            "AGENTS.md",
        ),
        # --- invocation repoints ---
        # /<plugin>:cmd -> /cmd  (also handles backtick `/plugin:cmd`)
        Repoint(
            "plugin-namespaced-slash",
            re.compile(rf"/{pn}:([\w-]+)"),
            r"/\1",
        ),
        # :sidecar internal-call notation -> /sidecar.
        # Two passes: backtick-wrapped `:rate` and bare " :rate" / "(:rate".
        # The backtick form needs its own pass (negative-lookbehind missed it
        # in the pilot — PORTING.md "Mechanical" note).
        Repoint(
            "sidecar-backtick",
            re.compile(r"`:([\w-]+)`"),
            r"`/\1`",
        ),
        Repoint(
            "sidecar-bare",
            # ':word' not preceded by a word char, slash, or colon, and not
            # part of a "key: value" (require it touches a boundary like space,
            # paren, or start). Avoids eating "outcome: completed".
            re.compile(r"(?<![\w/:])\:([a-z][\w-]+)\b"),
            r"/\1",
        ),
        # --- prose / phrasing repoints ---
        Repoint(
            "command-start-end",
            re.compile(r"\b([Aa]t )command (start|end)\b"),
            r"\1workflow \2",
        ),
        Repoint(
            "command-start-noun",
            re.compile(r"\bcommand start and end\b"),
            "workflow start and end",
        ),
    ]
    return rules


def apply_repoints(text: str, repoints: list[Repoint]) -> str:
    for rp in repoints:
        text, n = rp.pattern.subn(rp.repl, text)
        rp.count += n
    return text


# Cross-reference rewrites: relative skill-to-skill links, two forms.
#   full:        [`../X/SKILL.md`](../X/SKILL.md)
#   bare-backtick: `../X/SKILL.md`   (inline, no markdown link wrapper)
# Order matters — rewrite the full form first so the bare pass doesn't eat the
# inner backtick path of an already-handled link.
SIBLING_LINK_FULL_RE = re.compile(
    r"\[`\.\./([\w-]+)/SKILL\.md`\]\(\.\./[\w-]+/SKILL\.md\)"
)
SIBLING_LINK_BARE_RE = re.compile(r"`\.\./([\w-]+)/SKILL\.md`")


def rewrite_cross_refs(
    text: str,
    workflow_names: set[str],
    skill_names: set[str],
    report: "PortReport",
) -> str:
    """Rewire [`../X/SKILL.md`](...) links. Workflows -> /X slash form.
    Skills -> 'the X skill (.agent/skills/X/SKILL.md)'. The guide-intro
    boilerplate line is left to the finishing pass (varied prose per file)
    but flagged."""

    def repl(m: re.Match) -> str:
        target = m.group(1)
        if target == "guide":
            report.guide_ref_hits += 1
            return ("`AGENTS.md` + the `guide` skill "
                    "(`.agent/skills/guide/SKILL.md`)")
        if target in workflow_names:
            return f"`/{target}`"
        if target in skill_names:
            return (f"the `{target}` skill "
                    f"(`.agent/skills/{target}/SKILL.md`)")
        # unknown target — leave a pointer, flag it
        report.unknown_xref_targets.append(target)
        return f"`{target}` (`.agent/.../{target}`)"

    text = SIBLING_LINK_FULL_RE.sub(repl, text)
    text = SIBLING_LINK_BARE_RE.sub(repl, text)
    return text


# Frontmatter rewrite for workflows: drop name, rewrite description trigger.
DESC_TRIGGER_RE = re.compile(
    r"This skill should be used when the user says\s*", re.IGNORECASE
)


def rewrite_workflow_frontmatter(fm: dict, plugin_name: str) -> str:
    """Emit Antigravity workflow frontmatter: description only (name dropped —
    filename is the slash name). Rewrite 'This skill should be used when the
    user says /plugin:x' -> 'Run when the user says /x'."""
    desc = fm.get("description", "")
    desc = DESC_TRIGGER_RE.sub("Run when the user says ", desc)
    # /plugin:cmd -> /cmd inside the description too
    desc = re.sub(rf"/{re.escape(plugin_name)}:([\w-]+)", r"/\1", desc)
    # :sidecar -> /sidecar inside the description (backtick + bare forms),
    # matching the body repoints. The golden frontmatter uses /scan-releases.
    desc = re.sub(r"`:([\w-]+)`", r"`/\1`", desc)
    desc = re.sub(r"(?<![\w/:])\:([a-z][\w-]+)\b", r"/\1", desc)
    # backtick-wrap the bare slash trigger the source quoted bare:
    # source "/vibe-iterate" frontmatter often left it bare; the golden keeps
    # bare. Leave as-is (golden uses bare /trigger in description).
    # collapse the catch-all path repoints in the description as well
    desc = desc.replace("~/.claude/plugins/data/", "~/.gemini/antigravity/data/")
    desc = desc.replace("claude-code-plugin", "antigravity-workflow")
    desc = desc.replace('"', "'")
    return f'---\ndescription: "{desc}"\n---\n'


def rewrite_skill_frontmatter(fm: dict, plugin_name: str) -> str:
    """Emit Antigravity skill frontmatter: keep name, rewrite description to
    note internal status + the Antigravity log path. Light touch — the finishing
    pass may add the 'Antigravity port' note prose."""
    name = fm.get("name", "")
    desc = fm.get("description", "")
    desc = desc.replace("~/.claude/plugins/data/", "~/.gemini/antigravity/data/")
    desc = desc.replace("not a slash command", "not a user workflow")
    desc = desc.replace('"', "'")
    head = "---\n"
    if name:
        head += f"name: {name}\n"
    head += f'description: "{desc}"\n---\n'
    return head


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

@dataclass
class PortReport:
    plugin_name: str = ""
    source: str = ""
    output: str = ""
    workflows: list[dict] = field(default_factory=list)
    skills: list[dict] = field(default_factory=list)
    edge_classifications: list[dict] = field(default_factory=list)
    repoints_applied: dict = field(default_factory=dict)
    guide_ref_hits: int = 0
    unknown_xref_targets: list[str] = field(default_factory=list)
    leftover_grep_hits: dict = field(default_factory=dict)
    files_transformed: list[str] = field(default_factory=list)
    files_copied_verbatim: list[str] = field(default_factory=list)
    finishing_pass_todos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "plugin_name": self.plugin_name,
            "source": self.source,
            "output": self.output,
            "summary": {
                "workflows": len(self.workflows),
                "skills": len(self.skills),
                "edge_classifications": len(self.edge_classifications),
                "files_transformed": len(self.files_transformed),
                "files_copied_verbatim": len(self.files_copied_verbatim),
                "guide_intro_lines_to_synthesize": self.guide_ref_hits,
            },
            "workflows": self.workflows,
            "skills": self.skills,
            "edge_classifications": self.edge_classifications,
            "repoints_applied": self.repoints_applied,
            "unknown_xref_targets": sorted(set(self.unknown_xref_targets)),
            "leftover_grep_hits": self.leftover_grep_hits,
            "files_transformed": self.files_transformed,
            "files_copied_verbatim": self.files_copied_verbatim,
            "finishing_pass_todos": self.finishing_pass_todos,
        }


# Patterns the finishing pass should grep for to confirm nothing slipped.
LEFTOVER_PATTERNS = {
    "claude-home": re.compile(r"~/\.claude"),
    "plugin-root-env": re.compile(r"CLAUDE_PLUGIN_ROOT"),
    "claude-md": re.compile(r"\bCLAUDE\.md\b"),
    "plugin-json": re.compile(r"\.claude-plugin/plugin\.json"),
    "sibling-skill-link": re.compile(r"\.\./[\w-]+/SKILL\.md"),
    "guide-ref": re.compile(r"\.\./guide"),
    "sidecar-colon": re.compile(r"(?<![\w/:])\:[a-z][\w-]+\b"),
    "namespaced-slash": re.compile(r"/[\w-]+:[\w-]+"),
}


def grep_leftovers(out_dir: Path, plugin_name: str) -> dict:
    hits: dict[str, list[str]] = {}
    for md in sorted(out_dir.rglob("*.md")):
        try:
            text = md.read_text(encoding="utf-8")
        except Exception:
            continue
        rel = str(md.relative_to(out_dir))
        for label, pat in LEFTOVER_PATTERNS.items():
            for m in pat.finditer(text):
                # ignore the namespaced-slash false positives like http://x
                frag = m.group(0)
                if label == "namespaced-slash" and ("//" in text[max(0, m.start()-1):m.end()]):
                    continue
                if label == "sidecar-colon" and frag.lower() in (
                    ":completed", ":shipped", ":rejected", ":queued",
                ):
                    continue
                hits.setdefault(label, []).append(f"{rel}: …{frag}…")
    # de-noise: keep at most 8 examples per label
    return {k: v[:8] for k, v in hits.items()}


# ---------------------------------------------------------------------------
# Main transform
# ---------------------------------------------------------------------------

def load_plugin_manifest(src: Path) -> dict:
    pj = src / ".claude-plugin" / "plugin.json"
    if pj.exists():
        return json.loads(pj.read_text(encoding="utf-8"))
    return {}


def collect_skills(src: Path, plugin_name: str) -> list[SkillInfo]:
    skills_dir = src / "skills"
    out: list[SkillInfo] = []
    if not skills_dir.is_dir():
        return out
    for d in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        skill_md = d / "SKILL.md"
        if not skill_md.exists():
            continue
        text = skill_md.read_text(encoding="utf-8")
        fm, body = parse_frontmatter(text)
        cls, reason, edge = classify(d.name, fm, plugin_name)
        extra = any(
            (d / sub).is_dir()
            for sub in ("references", "schemas", "fixtures", "scripts")
        )
        out.append(SkillInfo(
            name=d.name, src_dir=d, skill_md=skill_md,
            frontmatter=fm, body=body,
            classification=cls, reason=reason, edge_flag=edge,
            has_extra_files=extra,
        ))
    return out


def copytree_verbatim(src: Path, dst: Path, report: PortReport, out_root: Path,
                      repoints: list[Repoint], workflow_names: set[str],
                      skill_names: set[str]):
    """Carry the guide's sub-dirs into the port.

    Split per the cookbook's "carry verbatim" rule, honestly applied:
      - schemas/ + fixtures/ are FORMAT-AGNOSTIC DATA -> copied byte-for-byte.
      - references/*.md are PROSE -> get the same repoints + cross-ref rewrite
        as workflow/skill bodies (the golden port hand-touched these; the
        slash/sidecar/path forms in the prose must repoint too).
      - scripts/ -> copied verbatim (code; repoint by hand if needed, flagged).
    """
    # Truly verbatim: data + code.
    for sub in ("schemas", "fixtures", "scripts"):
        s = src / sub
        if s.is_dir():
            shutil.copytree(s, dst / sub, dirs_exist_ok=True)
            report.files_copied_verbatim.append(
                str((dst / sub).relative_to(out_root)) + "/* (verbatim)"
            )

    # references/: transform .md prose, copy any non-.md verbatim.
    refs = src / "references"
    if refs.is_dir():
        (dst / "references").mkdir(parents=True, exist_ok=True)
        for f in sorted(refs.iterdir()):
            if not f.is_file():
                continue
            target = dst / "references" / f.name
            if f.suffix.lower() == ".md":
                text = f.read_text(encoding="utf-8")
                text = apply_repoints(text, repoints)
                text = rewrite_cross_refs(text, workflow_names, skill_names,
                                          report)
                target.write_text(text, encoding="utf-8")
                report.files_transformed.append(
                    str(target.relative_to(out_root))
                )
            else:
                shutil.copy2(f, target)
                report.files_copied_verbatim.append(
                    str(target.relative_to(out_root)) + " (verbatim)"
                )


AGENTS_SKELETON = """# {plugin} — agent rules (Antigravity port)

> Always-on context for the {plugin} workflows. This is the Antigravity-rules
> equivalent of the Claude Code `guide` SKILL's persona + posture + conventions
> layer. Every workflow inherits what's below. Deep reference detail (schemas,
> conventions, trigger maps) lives in the `guide` skill at
> `.agent/skills/guide/SKILL.md`.

<!-- TODO: finishing pass — SYNTHESIZE the always-on layer below as prose.
     Source: the Claude Code `guide` skill's references/. The judgment call
     (PORTING.md "The guide split"): docs that are "how the agent should behave
     ALWAYS" collapse into AGENTS.md prose here; docs that are "the exact
     shape/rules for a thing the agent occasionally touches" (schemas, trigger
     maps) STAY in the guide skill — do NOT duplicate them here.
     Fold in (collapse to prose, do not copy as files): persona, posture,
     knowledge-sources, cross-plugin/Cart detection, and the guide's Hard rules.
     Below are scaffolded section headers + the source reference docs detected. -->

## Persona

<!-- TODO: collapse the persona reference doc to prose here. -->
{persona_hint}

## Posture

<!-- TODO: collapse the posture reference doc to prose here. -->
{posture_hint}

## Knowledge sources

<!-- TODO: collapse the knowledge-sources reference doc to prose here. -->
{knowledge_hint}

## Cross-plugin detection

<!-- TODO: collapse the cart-detection / cross-plugin reference doc to prose.
     Repoint the detection mechanism: "available-skills list (system reminder)"
     -> "<sibling> workflows/skills available in this Antigravity workspace".
     Preserve the read-only / never-probe / never-hard-fail / never-auto-install
     rules. -->
{detection_hint}

## State files

<!-- TODO: list the per-project state files this plugin writes (kept verbatim;
     project-local state is portable as-is). -->

## Self-evolving framework — session + friction logging

<!-- TODO: confirm the log path repoint below is correct for this plugin. -->
**Log location (Antigravity repoint):** `~/.gemini/antigravity/data/{plugin}/`
(Claude Code original used `~/.claude/plugins/data/{plugin}/`.)

## Hard rules

<!-- TODO: fold the guide's "Hard rules" section here as prose. -->
{hardrules_hint}

## Voice

<!-- TODO: one paragraph — builder-to-builder, punchline-first, no corporate
     speak, no emoji in working output. Match the plugin's established voice. -->
"""


def make_agents_skeleton(plugin_name: str, guide: SkillInfo | None) -> str:
    """Scaffold AGENTS.md with TODO markers + hints pulled from the guide's
    detected reference docs (so the finishing pass knows what to fold)."""
    def hint(*keywords) -> str:
        if not guide:
            return "<!-- (no guide skill detected — supply persona/posture by hand) -->"
        refs = guide.src_dir / "references"
        found = []
        if refs.is_dir():
            for f in sorted(refs.glob("*.md")):
                if any(k in f.name.lower() for k in keywords):
                    found.append(f.name)
        if found:
            return ("<!-- source reference doc(s): "
                    + ", ".join(f"`guide/references/{n}`" for n in found)
                    + " -->")
        return "<!-- (no matching reference doc detected) -->"

    return AGENTS_SKELETON.format(
        plugin=plugin_name,
        persona_hint=hint("persona"),
        posture_hint=hint("posture"),
        knowledge_hint=hint("knowledge", "source"),
        detection_hint=hint("cart", "detect", "cross", "compose"),
        hardrules_hint=hint("rule", "guide"),
    )


def make_agent_json(manifest: dict, plugin_name: str) -> str:
    version = manifest.get("version", "0.0.0")
    desc = manifest.get("description", "")
    author = manifest.get("author", "")
    if isinstance(author, dict):
        author = author.get("name", "")
    obj = {
        "name": plugin_name,
        "version": version,
        "description": desc,
        "author": author,
        "license": manifest.get("license", ""),
        "source_plugin": {
            "marketplace": "vibe-plugins",
            "name": plugin_name,
            "version": version,
            "format": "claude-code",
        },
        "port": {
            "target": "antigravity-2.0",
            "notes": (
                "Manifest mirrors the Claude Code plugin.json version. Read by "
                "session-logger/friction-logger for the plugin_version audit "
                "field. Antigravity discovers workflows from .agent/workflows/ "
                "and skills from .agent/skills/ — this file is a port-bookkeeping "
                "manifest, not a discovery requirement."
            ),
        },
    }
    # ensure_ascii=False keeps em-dashes literal (matches the golden agent.json;
    # no — escaping in working output).
    return json.dumps(obj, indent=2, ensure_ascii=False) + "\n"


def run_port(src: Path, out: Path, plugin_name: str | None,
             quiet: bool) -> PortReport:
    manifest = load_plugin_manifest(src)
    plugin_name = plugin_name or manifest.get("name") or src.name

    report = PortReport(plugin_name=plugin_name, source=str(src), output=str(out))

    skills = collect_skills(src, plugin_name)
    if not skills:
        print(f"ERROR: no skills/ with SKILL.md found under {src}", file=sys.stderr)
        sys.exit(2)

    # First pass: settle classifications + the guide split target.
    guide = next((s for s in skills if s.name == "guide"), None)
    workflow_names = {s.name for s in skills if s.classification == "workflow"}
    skill_names = {s.name for s in skills if s.classification == "skill"}

    # Output skeleton dirs
    wf_dir = out / ".agent" / "workflows"
    sk_dir = out / ".agent" / "skills"
    wf_dir.mkdir(parents=True, exist_ok=True)
    sk_dir.mkdir(parents=True, exist_ok=True)

    repoints = build_repoints(plugin_name)

    for s in skills:
        # transform the body (shared repoints + cross-ref rewrite)
        body = apply_repoints(s.body, repoints)
        body = rewrite_cross_refs(body, workflow_names, skill_names, report)

        if s.classification == "workflow":
            fm_out = rewrite_workflow_frontmatter(s.frontmatter, plugin_name)
            dest = wf_dir / f"{s.name}.md"
            dest.write_text(fm_out + body, encoding="utf-8")
            report.files_transformed.append(
                str(dest.relative_to(out))
            )
            report.workflows.append({
                "name": s.name,
                "slash": f"/{s.name}",
                "reason": s.reason,
                "edge_flag": s.edge_flag,
            })
        else:
            fm_out = rewrite_skill_frontmatter(s.frontmatter, plugin_name)
            dest_dir = sk_dir / s.name
            dest_dir.mkdir(parents=True, exist_ok=True)
            (dest_dir / "SKILL.md").write_text(fm_out + body, encoding="utf-8")
            report.files_transformed.append(
                str((dest_dir / "SKILL.md").relative_to(out))
            )
            copytree_verbatim(s.src_dir, dest_dir, report, out,
                              repoints, workflow_names, skill_names)
            report.skills.append({
                "name": s.name,
                "reason": s.reason,
                "edge_flag": s.edge_flag,
                "carried_verbatim": s.has_extra_files,
                "guide_split": (s.name == "guide"),
            })

        if s.edge_flag:
            report.edge_classifications.append({
                "name": s.name,
                "classified_as": s.classification,
                "reason": s.reason,
                "note": "VERIFY in finishing pass — self-label vs trigger "
                        "disagreed, or no strong signal.",
            })

    # Scaffold agent.json + AGENTS.md
    (out / ".agent" / "agent.json").write_text(
        make_agent_json(manifest, plugin_name), encoding="utf-8"
    )
    report.files_transformed.append(".agent/agent.json")
    (out / "AGENTS.md").write_text(
        make_agents_skeleton(plugin_name, guide), encoding="utf-8"
    )
    report.files_transformed.append("AGENTS.md (skeleton — finishing pass)")

    # Repoint tally + leftover grep
    report.repoints_applied = {rp.label: rp.count for rp in repoints if rp.count}
    report.leftover_grep_hits = grep_leftovers(out, plugin_name)

    # Finishing-pass TODO list (the judgment ~20%)
    todos = [
        "AGENTS.md: synthesize the always-on layer as prose (persona, posture, "
        "knowledge sources, cross-plugin detection, hard rules, voice). The "
        "skeleton has TODO markers + source-doc hints.",
        "Guide split: decide which guide reference docs are always-on (collapse "
        "into AGENTS.md prose, then DELETE from the guide skill so there's one "
        "source of truth) vs situational (keep as files in the guide skill). "
        "Rewrite the guide SKILL.md to a thin index. Schemas + trigger maps "
        "stay skill-side; personas + postures go AGENTS-side.",
    ]
    if report.guide_ref_hits:
        todos.append(
            f"Guide-intro lines: {report.guide_ref_hits} workflow/skill bodies "
            "had a '[../guide/SKILL.md]' intro line auto-rewritten to a generic "
            "pointer. Rewrite each to the per-file prose form (e.g. 'Persona/"
            "posture/Cart-detection are always-on via AGENTS.md…')."
        )
    for ec in report.edge_classifications:
        todos.append(
            f"Edge classification: '{ec['name']}' -> {ec['classified_as']} "
            f"({ec['reason']}). Confirm."
        )
    evolve = [s for s in skills if s.name.startswith("evolve")]
    if evolve:
        todos.append(
            f"Self-edit targets in {', '.join(e.name for e in evolve)}: the "
            "proposal shapes name files to edit "
            "('plugins/<plugin>/skills/<cmd>/SKILL.md'). Repoint each to its "
            "real port target — '.agent/workflows/<cmd>.md' for ported "
            "workflows, '.agent/skills/<name>/...' for ported skills. This is "
            "NOT a blind string replace (a skill that became a workflow flips "
            "the target dir)."
        )
    todos.append(
        "Folded-reference back-pointers: any body that said 'per "
        "../guide/references/<doc>.md' for a doc that got collapsed into "
        "AGENTS.md must point at 'AGENTS.md § <Section>' instead."
    )
    todos.append(
        "H1 titles / inline triggers: the script repoints frontmatter triggers "
        "and body slash names, but H1 headings and HTML-entity forms "
        "(e.g. '/plugin:rate &lt;idea&gt;') may need a hand pass for clean "
        "'/rate <idea>' form."
    )
    todos.append(
        "Open questions 1-5 (PORTING.md): re-check against THIS plugin's feature "
        "set — does it schedule (cron)? call sidecars silently? have hooks/? "
        "use ~/.claude/profiles/builder.json? namespace-collide on workflow "
        "names? Document the answers; do NOT invent Antigravity primitives."
    )
    if report.leftover_grep_hits:
        todos.append(
            "Leftover grep hits remain (see leftover_grep_hits) — review each; "
            "some are legitimate (the AGENTS.md repoint note mentions the old "
            "path on purpose), some are misses to clean up."
        )
    report.finishing_pass_todos = todos

    if not quiet:
        print_report(report)
    return report


def print_report(report: PortReport):
    r = report
    print(f"\n=== port.py — {r.plugin_name} ===")
    print(f"source: {r.source}")
    print(f"output: {r.output}")
    print(f"\nClassified {len(r.workflows)} workflows, {len(r.skills)} skills:")
    for w in r.workflows:
        flag = "  <-- EDGE" if w["edge_flag"] else ""
        print(f"  workflow  /{w['name']}{flag}")
    for s in r.skills:
        tags = []
        if s["guide_split"]:
            tags.append("GUIDE-SPLIT")
        if s["carried_verbatim"]:
            tags.append("verbatim files")
        if s["edge_flag"]:
            tags.append("EDGE")
        suffix = ("  [" + ", ".join(tags) + "]") if tags else ""
        print(f"  skill     {s['name']}{suffix}")
    print(f"\nRepoints applied: {r.repoints_applied}")
    if r.edge_classifications:
        print("\nEdge classifications (verify in finishing pass):")
        for ec in r.edge_classifications:
            print(f"  - {ec['name']} -> {ec['classified_as']}: {ec['reason']}")
    if r.leftover_grep_hits:
        print("\nLeftover grep hits (review):")
        for label, hits in r.leftover_grep_hits.items():
            print(f"  [{label}] {len(hits)} hit(s)")
    print(f"\nFinishing-pass TODOs: {len(r.finishing_pass_todos)} "
          "(see PORT-RUNNER.md + port-report.json)")


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source", help="Claude Code plugin dir (with skills/, .claude-plugin/plugin.json)")
    ap.add_argument("output", help="Output dir for the Antigravity port skeleton")
    ap.add_argument("--plugin-name", help="Override plugin name (defaults to plugin.json name)")
    ap.add_argument("--quiet", action="store_true", help="Suppress stdout summary")
    ap.add_argument("--no-clean", action="store_true",
                    help="Do not wipe the output dir first")
    args = ap.parse_args(argv)

    src = Path(args.source).resolve()
    out = Path(args.output).resolve()
    if not src.is_dir():
        print(f"ERROR: source not a directory: {src}", file=sys.stderr)
        sys.exit(2)

    if out.exists() and not args.no_clean:
        # safety: never clean a dir that isn't ours
        if (out / ".agent").exists() or not any(out.iterdir()):
            shutil.rmtree(out, ignore_errors=True)
        else:
            print(f"ERROR: output dir exists and isn't an empty/port dir: {out}\n"
                  "       pass --no-clean to merge, or pick an empty dir.",
                  file=sys.stderr)
            sys.exit(2)
    out.mkdir(parents=True, exist_ok=True)

    report = run_port(src, out, args.plugin_name, args.quiet)

    report_path = out / "port-report.json"
    report_path.write_text(json.dumps(report.to_dict(), indent=2), encoding="utf-8")
    if not args.quiet:
        print(f"\nReport written: {report_path}")


if __name__ == "__main__":
    main()
