# Secret-file skip patterns

> Consumed by the [`/vibe-taker-capture`](/.agent/workflows/vibe-taker-capture.md) workflow. PRD Capture story 8 is the contract.

`/vibe-taker-capture` walks every file in scope. Files whose path or basename matches any pattern below are **skipped silently from `reference/`** and listed in stdout under "Skipped secret-like files: ...". They never land on the shelf.

## Glob patterns matched

Match against the file's basename **and** its repo-relative path. Case-insensitive on Windows, case-sensitive on macOS/Linux (mirror the host filesystem's behavior).

```
.env
.env.*
*.pem
*.key
id_rsa
id_rsa.*
id_dsa
id_dsa.*
id_ecdsa
id_ecdsa.*
id_ed25519
id_ed25519.*
*credentials*
*credential*
*secret*
*secrets*
*.pgpass
.netrc
.npmrc
.pypirc
auth.json
service-account*.json
gcp-key*.json
firebase-adminsdk-*.json
```

## What's NOT skipped

Files that *reference* secrets (read env vars, call dotenv, document expected env-var names) are kept — they're the load-bearing capture material. The pattern is "skip the secret value, keep the code that reads it."

Examples of files **kept**:

- `.env.example` — explicitly documents shape; matches `.env.*` glob but the `.example` suffix flags it as a template. **Carve-out: any `.env.example` / `.env.template` / `.env.sample` is kept.**
- `config.py` that calls `os.getenv("OPENAI_API_KEY")` — the *call* is the load-bearing surface; the actual key never appears here.
- `package.json` — even if it's named after `package` it never matches `*credential*`, etc.

## Carve-outs (kept despite matching)

```
.env.example
.env.sample
.env.template
.env.local.example
secret-patterns.md       # this file itself
secrets-loader.{ts,js,py,rs,go}     # documented loader, not the secret
```

When in doubt, keep. False negatives (a secret that slips through) are worse than false positives (a documented loader file getting skipped). The carve-out list is conservative.

## Load-bearing detection

When a file is skipped, before discarding it:

1. **Take the basename minus extension.** `OPENAI_KEY.env` → `OPENAI_KEY`. `secrets/api.json` → `api`. Convert to UPPER_SNAKE.
2. **Search the rest of the captured tree** (not the skipped file itself) for any of:
   - `import` / `require` / `from … import` of the basename (`from .secrets_loader import api_keys`)
   - `dotenv.config()` / `load_dotenv()` / `dotenv.load()` calls (which implicitly load `.env*` from cwd)
   - `os.environ[...]` / `os.getenv(...)` / `process.env.<X>` references whose key matches a pattern derived from the basename or the file's content (when content was readable before the skip).
3. **If a match is found, the skipped file is load-bearing.** Add a stub to `contract.json.env_vars`:
   ```json
   { "name": "<INFERRED_NAME>", "load_bearing": true, "description": "Inferred from skipped <path>; provide at plant-time." }
   ```
4. **Print a warning** in the capture-summary stdout block:

   > Skipped X secret-like files that look load-bearing. Capture continues with these stubbed in `contract.json` under `env_vars`. Provide them at plant-time.

PRD Capture story 8 is the contract.

## What this file does NOT cover

- **In-source secrets** (a literal API key hardcoded in `bg-remove.py`). The agent does not scan source files for secret-shaped strings in v1. False positives on real string literals would create noise. Out of scope; revisit if a friction signal at `/reflect` flags a slip.
- **Binary blobs** (compiled credentials, encrypted keys). Same v1 punt. The glob list catches the common file shapes; binary detection is its own job.

## When to update this list

Treat this file as a living list. Add patterns when:

- A real-world capture scoops up a file class we missed (friction at `/reflect`).
- A new tool ecosystem becomes common in 626labs work (e.g., Vault, Doppler, 1Password CLI dotfiles).

Removing patterns is rare — false positives on a documented carve-out are cheaper than false negatives on a real secret.
