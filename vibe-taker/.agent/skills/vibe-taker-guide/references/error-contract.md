# Error & exit-code contract

> Consumed by the [`/vibe-taker-capture`](/.agent/workflows/vibe-taker-capture.md), [`/vibe-taker-plant`](/.agent/workflows/vibe-taker-plant.md), and [`/vibe-taker-list`](/.agent/workflows/vibe-taker-list.md) workflows.

vibe-taker runs as markdown SKILLs, not as a process — so "exit codes" are the **conceptual outcome the agent prints**, not a literal `process.exit(N)`. The agent communicates the class via the structure of its stdout summary; downstream tools (and the user) read it as a status.

## Three classes

| Class | Conceptual code | Examples | Recovery message required? |
|---|---|---|---|
| **Success** | `0` | Bundle written, plant applied, list printed, decline accepted by user. | No — the success print is enough. |
| **User-facing decline / soft failure** | `1` | Target not found, glob no-match, in-file selector, name conflict declined, bundle not on shelf, hard language mismatch on plant. | **Yes** — the print includes the exact recovery action (run X, edit Y, capture Z). |
| **Internal / schema failure** | `2` | Index corrupt, contract.json schema invalid, write to shelf failed, mid-flight stack-detect crash. | **Yes** — print path, expected schema/state, recovery (re-capture, hand-edit, restore from backup). |

## Discipline rule — recovery line is mandatory on 1 and 2

**Every class-1 and class-2 outcome MUST include a one-line recovery action** in the printed output. Bare error messages without actionable recovery are a bug — file as friction at `/reflect`.

Bad:

```
Error: bundle not found.
```

Good:

```
[exit 1] No bundle named 'bg-remover' on the shelf. Run `/vibe-taker-list` to see what's available.
```

The format isn't load-bearing (no parser depends on the `[exit N]` prefix), but **the recovery line is**.

## Per-command outcome catalog

### `/vibe-taker-capture`

| Class | Trigger | Recovery line |
|---|---|---|
| 0 | Bundle written. | (Print bundle path + 3-line summary.) |
| 0 | Versioning declined (`n`). | (Print existing-bundle path; "no changes.") |
| 1 | Target path doesn't exist (and isn't a glob). | "Target `<path>` not found. Pass an existing path or a glob." |
| 1 | Glob matches no files. | "No files matched glob `<pattern>`. Check the pattern or `cd` to the right directory." |
| 1 | In-file selector (`file.py:120-180`). | "vibe-taker captures whole files, folders, or globs in v1. Selection-within-a-file isn't supported — extract to its own file first or capture the parent file." |
| 1 | Name conflict declined (`n`). | "No changes. Existing bundle at `<path>`." |
| 2 | Failed to write to shelf. | "Write failed at `<path>`. Check disk space and permissions on `~/.vibe-taker/`." |
| 2 | Index corrupt mid-capture. | "Library index missing or corrupt at `<path>`. Re-capture to rebuild, or restore from backup." |

### `/vibe-taker-plant`

| Class | Trigger | Recovery line |
|---|---|---|
| 0 | Diff applied. | (Print files written + dashboard log status.) |
| 0 | Diff declined by user. | "No files written." |
| 1 | Bundle not on shelf. | "No bundle named `<name>` on the shelf. Run `/vibe-taker-list` to see what's available." |
| 1 | `--version=vX` not found. | "Bundle `<name>` exists but version `<vX>` not found. Available: `<v1, v2, ...>`." |
| 1 | Hard language mismatch. | (Print the [hard-mismatch decline message](./stack-match.md#hard-mismatch-decline-message) verbatim.) |
| 2 | Bundle's `contract.json` fails schema validation. | "Bundle `<path>/contract.json` failed schema validation: `<error>`. Hand-edit the file or re-capture the source." |
| 2 | Stack-detect crash mid-flight. | "Stack-detect failed reading `<manifest-path>`: `<error>`. Hand-fix the manifest or pass the bundle through spec-driven mode by removing the manifest temporarily." |

### `/vibe-taker-list`

| Class | Trigger | Recovery line |
|---|---|---|
| 0 | Bundles printed. | (Print blocks per spec format.) |
| 0 | Library empty. | "Library is empty. Run `/vibe-taker-capture <path>` to add your first bundle." |
| 0 | `--search` had no matches. | "no matches" |
| 2 | Index corrupt. | "Library index missing or corrupt at `<path>`. Re-capture a feature to rebuild, or restore from backup." |

## Output format

Every command's printed outcome opens with the verdict (the class-tag and one-line punch). For class-1 and class-2 outcomes, the recovery line is the next line. For class-0, the success block follows.

Working examples:

```
✓ Bundle written: ~/.vibe-taker/library/bg-remover/v1/

  6 artifacts populated. Index updated.
  language: python  ·  framework: cli-argparse  ·  interface: cli

  Next: `/vibe-taker-list` to see the shelf.
```

```
[exit 1] No bundle named 'bg-remover' on the shelf.
Run `/vibe-taker-list` to see what's available.
```

```
[exit 2] Library index missing or corrupt at /Users/este/.vibe-taker/library/index.json.
Re-capture a feature to rebuild, or restore from backup.
```

The check-mark / `[exit N]` prefix is a readability hint, not a contract. **The contract is: success blocks are unambiguous, declines name the recovery, schema failures name the path.**

## What to avoid

- **Stack traces in user-facing output** — class-2 outcomes summarize the failure (one line) and name the recovery; the full traceback goes to a log file or stderr if the harness captures it. The user shouldn't have to read a Python traceback to learn that the index is corrupt.
- **Multi-step recoveries** — every recovery line is **one action**. If a real recovery needs three steps, write it as one action that opens a doc reference: "see `docs/troubleshooting.md > index-corruption` for the recovery sequence." (v1 doesn't have this doc; if a class needs it, that's a v1.1 friction signal.)
- **Silent class-1** — even when the user is the one who declined (`n` to a versioning bump), print a short "no changes" line so the user knows the command exited cleanly.
