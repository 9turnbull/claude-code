---
name: session-start-hook
description: Creating and developing startup hooks for Claude Code on the web. Use when the user wants to set up a repository for Claude Code on the web, create a SessionStart hook to ensure their project can run tests and linters during web sessions.
---

Set up a `SessionStart` hook so Claude Code on the web can run tests and linters at the start of every session.

## What this does

A `SessionStart` hook runs a shell script automatically when a Claude Code web session begins. This ensures the environment is ready: dependencies installed, services running, linters available.

## Steps

### 1. Identify project needs

Check the repository to understand:
- Package manager (`npm`, `yarn`, `pnpm`, `pip`, `cargo`, etc.)
- Test runner (`jest`, `pytest`, `cargo test`, etc.)
- Linter (`eslint`, `ruff`, `clippy`, etc.)
- Any services needed (database, dev server, etc.)

Use `ls`, `cat package.json`, `cat pyproject.toml`, etc. to discover these.

### 2. Create the hook script

Create `.claude/hooks/session-start.sh`:

```bash
#!/bin/bash
set -e

echo "=== Session Start Hook ==="

# Install dependencies
npm install        # or: pip install -e ".[dev]" / cargo build

# Verify tooling works
echo "Environment ready."
```

Make it executable: `chmod +x .claude/hooks/session-start.sh`

### 3. Register the hook in settings

Add to `.claude/settings.json`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": ".claude/hooks/session-start.sh"
          }
        ]
      }
    ]
  }
}
```

If `.claude/settings.json` already exists, merge the `hooks.SessionStart` key—don't overwrite existing settings.

### 4. Verify

- Read back the hook script and settings to confirm correctness
- If possible, run the script once to verify it works: `bash .claude/hooks/session-start.sh`

## Common patterns by stack

**Node.js / TypeScript**
```bash
npm ci
npx tsc --noEmit
```

**Python**
```bash
pip install -e ".[dev]"
ruff check . || true
```

**Rust**
```bash
cargo build
cargo clippy -- -D warnings || true
```

**Monorepo**
```bash
npm install
npm run build --workspaces
```

## Notes

- Use `|| true` for linters if you don't want hook failures to block the session
- Keep the script fast — it runs at session start before the user's first message
- Commit both `.claude/hooks/session-start.sh` and `.claude/settings.json`
