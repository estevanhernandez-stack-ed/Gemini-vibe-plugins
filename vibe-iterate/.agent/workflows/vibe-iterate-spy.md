---
description: "Run when the user says /vibe-iterate-spy <url> and wants a one-shot competitive read on a single URL. Fetches and reads the URL (changelog, what's-new, landing page), outputs a structured read of what they shipped, what they emphasize, gaps, and overlap with the user's product."
---

# /vibe-iterate-spy <url> — one-shot competitive read on a single URL

Persona/posture/knowledge-sources/Cart-detection are always-on via `AGENTS.md`. Reference detail (Atlas conventions, schemas, friction map) is in the `vibe-iterate-guide` skill (`.agent/skills/vibe-iterate-guide/SKILL.md`) — load it to validate any state-file write. Then follow this workflow.

## What this workflow does

Takes a single URL — typically a competitor's changelog, what's-new page, release notes, or landing page — and returns a structured read: what they shipped, what they emphasize in their positioning, what gaps they leave open, and where their work overlaps with the user's product.

Used standalone for ad-hoc competitive intel ("just saw this drop, what's their angle?"). Used internally by `competitive` mode for each URL in `competitors[]`.

## Hard rules

- **Read-only.** No mode runs, no PR, no Atlas write. The output is intelligence, not action.
- **Single URL only.** If the user passes multiple URLs, run `/vibe-iterate-spy` once per URL and surface separate reads. Don't batch into one report — each competitor deserves its own structured slot.
- **Don't speculate beyond what's on the page.** If their changelog says "added saved searches," don't extrapolate to "they're pivoting to enterprise search." Stick to evidence.
- **Quote when it matters.** When summarizing positioning or feature claims, quote the source language verbatim — competitor word choice IS the signal.

## Inputs

- **`$1`** — the URL. Required. Must start with `http://` or `https://`. If absent or malformed, prompt: *"What URL? (changelog, release page, what's-new page, or landing page)"* and wait.
- **Project state** — `.vibe-iterate/config.json` (for `category` — used to scope the "overlap with us" analysis). If absent, run with empty overlap analysis and surface the gap once at the top: *"No vibe-iterate config — overlap analysis will be generic. Run /vibe-iterate first to set category context."*

## Procedure

### Step 1 — fetch

Use WebFetch with this prompt:

> *"This is a competitor's [changelog | release notes | what's-new page | landing page — pick the most likely from the URL path]. Extract:*
> *1. Every shipped feature mentioned, with one-line description and date if present*
> *2. The product's positioning — what do they emphasize? what's the headline value claim?*
> *3. The target audience — who is this for? (read between the lines if not stated)*
> *4. The marketing voice — formal? playful? technical? founder-speak?*
> *5. Any pricing or packaging signals*
> *6. Any explicit comparisons to other products*
> *Return as structured markdown with H2 headings per category."*

If WebFetch fails or returns paywalled / login-required content:

```
/vibe-iterate-spy couldn't fetch <url>:
- HTTP <status>: <reason>
- Possible causes: paywalled, login-required, robots.txt-blocked, network unreachable

Try:
- A direct changelog URL instead of the marketing page
- Their GitHub releases page (github.com/<owner>/<repo>/releases)
- Their RSS feed if one exists
```

### Step 2 — overlap analysis

If `.vibe-iterate/config.json` is present, compare the extracted features and positioning to the user's product:

- **Feature overlap** — for each feature the competitor shipped, mark: `we have it`, `we don't have it`, `we have something different that addresses the same need`. The "we have it" call is anchored to the user's `category` description and any inferred capabilities — don't claim the user has a feature without evidence (look for it in the codebase if needed before claiming).
- **Positioning overlap** — does the competitor's headline value claim sound like the user's, or different?
- **Audience overlap** — same target audience, or different?

If `.vibe-iterate/config.json` is absent, skip overlap analysis entirely (don't fake it).

### Step 3 — render the structured read

```
Spy on <url>  (fetched YYYY-MM-DD HH:MM UTC)

What they shipped
- <feature 1>  (date if known) — <one-line>
- <feature 2>  (date if known) — <one-line>
- ...

What they emphasize (positioning)
- Headline claim: "<verbatim quote from their page>"
- Voice: <formal | playful | technical | founder-speak | mixed>
- Pricing / packaging signals: <one-line, or "none surfaced">

Target audience
- <one-line read of who this is for>

Where it overlaps with us  (skip if no .vibe-iterate/config.json)
- We have it: <feature 1>, <feature 2>
- We don't have it: <feature 3>, <feature 4>
- We have something different addressing the same need: <feature 5> ← we ship <our version> instead

Gaps they leave open  (one-paragraph synthesis)
<what they're NOT addressing — could be a positioning angle for the user>

Comparisons they make
- <one-line per explicit comparison to a third-party product, if any>

Recommended follow-up
- /vibe-iterate-competitive — ranks these gaps by strategic relevance and proposes one to ship
- /vibe-iterate-rate "<idea inspired by this>" — sanity-check before committing
- /vibe-iterate-radar — refresh the broader radar to put this in context
```

If a section has no content (e.g., no comparisons made on the page), omit it entirely. Don't pad.

## When invoked internally by `competitive` mode

The calling mode passes `--silent`; `/vibe-iterate-spy` returns the parsed structured read as a JSON-shaped object instead of rendering the user-facing template. The mode aggregates spy outputs across all `competitors[]` URLs before scoring.

## Anti-patterns

- **Don't paraphrase headline claims.** Quote them verbatim — word choice is the intelligence.
- **Don't speculate about strategy.** "They're probably pivoting to..." is noise. Stick to what's on the page.
- **Don't skip the overlap analysis** when config is present (unless user passes `--no-overlap`).
- **Don't bundle multiple URLs** into one read. Each URL gets its own `/vibe-iterate-spy` call.
- **Don't claim feature parity** without checking the codebase. "We have it" is a claim with consequences — verify before asserting.

## Cross-references

- Sibling sidecar: `/vibe-iterate-radar` — broader scheduled scan across all competitors
- Banner mode: `/vibe-iterate-competitive` — invokes `/vibe-iterate-spy` internally per URL
- Knowledge sources: AGENTS.md § Knowledge sources
