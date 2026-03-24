# CLAUDE.md — AI Assistant Guide for claude-code Repository

This file provides context for AI assistants working in this repository.

## Repository Overview

This is the **official public repository for Claude Code** — Anthropic's agentic coding tool that runs in the terminal, IDE, and GitHub. The repository serves two main purposes:

1. **Issue tracker** for Claude Code bugs, feature requests, and model behavior reports
2. **Plugin library** containing official Claude Code plugins that extend functionality

> The Claude Code binary itself is closed source and not in this repo. This repository contains automation scripts, plugins, examples, and GitHub workflows.

## Repository Structure

```
claude-code/
├── .claude/                    # Claude Code slash command definitions
│   └── commands/               # /commit-push-pr, /dedupe, /triage-issue
├── .claude-plugin/
│   └── marketplace.json        # Marketplace manifest listing all bundled plugins
├── .devcontainer/              # Dev container configuration (Dockerfile + devcontainer.json)
├── .github/
│   ├── ISSUE_TEMPLATE/         # Bug report, feature request, model behavior, docs templates
│   └── workflows/              # GitHub Actions automating issue triage and Claude interactions
├── examples/
│   ├── hooks/                  # Example hook scripts (e.g., bash_command_validator_example.py)
│   └── settings/               # Example settings.json files for enterprise deployments
├── plugins/                    # Official Claude Code plugins (see Plugins section)
│   └── README.md               # Plugin directory index
├── Script/                     # PowerShell scripts (e.g., run_devcontainer_claude_code.ps1)
├── scripts/                    # TypeScript/Bun scripts for issue lifecycle automation
├── CHANGELOG.md                # Version-by-version release notes
├── SECURITY.md                 # Security disclosure policy
└── README.md                   # Public-facing project documentation
```

## GitHub Automation Workflows

These workflows automate repository maintenance and integrate Claude Code directly into GitHub:

| Workflow | Trigger | Purpose |
|---|---|---|
| `claude.yml` | `@claude` mentions in issues/PRs | Runs Claude Code Action on tagged comments |
| `claude-issue-triage.yml` | Issue opened / comment created | Runs `/triage-issue` to label and categorize issues |
| `claude-dedupe-issues.yml` | Issue opened | Runs `/dedupe` to detect and flag duplicate issues |
| `sweep.yml` | Scheduled | Marks stale issues and closes expired lifecycle-labeled ones |
| `issue-lifecycle-comment.yml` | Issue labeled | Posts lifecycle nudge comments for stale/needs-info/etc. |
| `auto-close-duplicates.yml` | Issue labeled `duplicate` | Auto-closes confirmed duplicates |
| `lock-closed-issues.yml` | Issue closed | Locks resolved issues after a grace period |
| `non-write-users-check.yml` | PR/issue events | Validates permissions for non-write users |
| `log-issue-events.yml` | Issue events | Logs events to Statsig for analytics |

### Claude Code Action Integration

The `claude.yml` workflow uses `anthropics/claude-code-action@v1` with `claude-sonnet-4-5-20250929`. Issue triage uses `claude-opus-4-6`. Any `@claude` mention in an issue or PR comment triggers Claude Code to respond.

## Issue Lifecycle System

Issues follow an automated lifecycle defined in `scripts/issue-lifecycle.ts`:

| Label | Auto-close after | Reason |
|---|---|---|
| `invalid` | 3 days | Not about Claude Code |
| `needs-repro` | 7 days | Awaiting reproduction steps |
| `needs-info` | 7 days | Awaiting additional information |
| `stale` | 14 days | Inactive |
| `autoclose` | 14 days | Inactive, marked for closure |

Issues with **10+ 👍 reactions** are exempt from auto-closure. Issues assigned to a team member are exempt from stale marking. Human comments after a lifecycle label is applied prevent auto-closure.

### Scripts (TypeScript/Bun)

All automation scripts use Bun and are in `scripts/`:

- `issue-lifecycle.ts` — Single source of truth for lifecycle labels, timeouts, and messages
- `sweep.ts` — Marks issues stale and closes expired lifecycle-labeled ones; supports `--dry-run`
- `lifecycle-comment.ts` — Posts nudge comments when lifecycle labels are applied
- `auto-close-duplicates.ts` — Closes issues labeled as duplicates
- `backfill-duplicate-comments.ts` — Backfills duplicate detection comments

## Plugins

The `plugins/` directory contains **13 official plugins** organized by category:

### Development
- **`agent-sdk-dev`** — Setup and validate Claude Agent SDK projects (`/new-sdk-app`)
- **`claude-opus-4-5-migration`** — Migrate code from Sonnet 4.x/Opus 4.1 to Opus 4.5
- **`feature-dev`** — 7-phase feature development workflow with explorer/architect/reviewer agents
- **`frontend-design`** — Production-grade frontend design guidance (auto-invoked skill)
- **`plugin-dev`** — Comprehensive toolkit for creating new Claude Code plugins

### Productivity
- **`code-review`** — Automated PR review via 5 parallel specialized agents (`/code-review`)
- **`commit-commands`** — Git workflow automation: `/commit`, `/commit-push-pr`, `/clean_gone`
- **`hookify`** — Create custom hooks from conversation patterns (`/hookify`)
- **`pr-review-toolkit`** — Deep PR review across comments, tests, types, and code quality

### Learning
- **`explanatory-output-style`** — Educational insights hook (SessionStart)
- **`learning-output-style`** — Interactive learning mode requesting code contributions

### Security
- **`security-guidance`** — PreToolUse hook warning on 9 security patterns (XSS, injection, etc.)

### Other
- **`ralph-wiggum`** — Self-referential AI iteration loops (`/ralph-loop`, `/cancel-ralph`)

### Plugin Structure Convention

Every plugin follows this layout:

```
plugin-name/
├── .claude-plugin/
│   └── plugin.json          # Required: name, version, description, author
├── commands/                # Slash commands (.md files with YAML frontmatter)
├── agents/                  # Subagent definitions (.md files)
├── skills/                  # Auto-activating skills
│   └── skill-name/
│       └── SKILL.md         # Required; frontmatter: name, description, version
├── hooks/
│   └── hooks.json           # PreToolUse, PostToolUse, Stop, SessionStart, etc.
├── .mcp.json                # MCP server definitions (optional)
└── README.md
```

**Key rules:**
- All component directories must be at plugin root, NOT inside `.claude-plugin/`
- Use kebab-case for all file and directory names
- Use `${CLAUDE_PLUGIN_ROOT}` for all intra-plugin path references — never hardcode paths
- Skills auto-activate based on task context matching their `description` frontmatter
- Hooks execute at: `PreToolUse`, `PostToolUse`, `Stop`, `SubagentStop`, `SessionStart`, `SessionEnd`, `UserPromptSubmit`, `PreCompact`, `Notification`, `StopFailure`

Hook exit codes:
- `0` — success, continue
- `1` — show stderr to user, do not block
- `2` — block tool call, show stderr to Claude

## Examples

### `examples/hooks/`
Contains `bash_command_validator_example.py` — a PreToolUse hook that intercepts Bash tool calls and enforces conventions (e.g., prefer `rg` over `grep`). Demonstrates the hook stdin/stdout JSON protocol.

### `examples/settings/`
Three reference `settings.json` files for enterprise deployments:
- `settings-lax.json` — Disables `--dangerously-skip-permissions`, blocks plugin marketplaces
- `settings-strict.json` — Adds bash approval required, blocks user hooks and web fetch
- `settings-bash-sandbox.json` — Requires Bash to run in a sandbox

## Development Environment

A `.devcontainer/` setup is provided for consistent development:

- **Base**: Node.js container with zsh, git-delta, Claude Code pre-installed
- **VS Code extensions**: Claude Code, ESLint, Prettier, GitLens
- **Firewall**: `init-firewall.sh` runs on container start (`NET_ADMIN`/`NET_RAW` capabilities)
- **Volumes**: Bash history and `~/.claude` config persist across rebuilds
- **Node options**: `NODE_OPTIONS=--max-old-space-size=4096`

A PowerShell script at `Script/run_devcontainer_claude_code.ps1` helps Windows users launch the dev container.

## Git and Branching Conventions

- **Default branch**: `main` (production) / `master` (legacy alias)
- **Feature branches**: Use descriptive names; Claude automation uses `claude/<description>-<id>` format
- **Commit messages**: Prefix with type (`feat:`, `fix:`, `chore:`, `docs:`) and scope in parens
- **CHANGELOG.md**: Updated per release; version headers are `## X.Y.Z`

## Working in This Repository

### When triaging or responding to issues

- Check `scripts/issue-lifecycle.ts` to understand current label thresholds
- Use labels: `bug`, `feature-request`, `needs-info`, `needs-repro`, `invalid`, `duplicate`, `stale`, `autoclose`
- Do not close issues with 10+ upvotes via automation
- Triage workflow uses the `/triage-issue` slash command defined in `.claude/commands/triage-issue.md`

### When adding or modifying plugins

1. Follow the plugin structure convention above
2. Add metadata in `.claude-plugin/plugin.json` (name required; version/description/author recommended)
3. Update `plugins/README.md` table and `.claude-plugin/marketplace.json`
4. Use `${CLAUDE_PLUGIN_ROOT}` for all path references in hooks and MCP configs
5. Test that all components auto-discover correctly

### When modifying automation scripts

- Scripts use Bun (not Node directly) — `#!/usr/bin/env bun` shebang
- The `GITHUB_TOKEN` env var is required for all GitHub API calls
- Support `--dry-run` flag for scripts that mutate data
- `issue-lifecycle.ts` is the single source of truth — update it, not individual scripts

### When updating workflows

- Pin action versions with full SHA for security (see `claude.yml` for example)
- Use `allowed_non_write_users: "*"` when the workflow should run for all users
- Claude Code Action uses `anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}`
- Model selection via `claude_args: "--model <model-id>"`

## Key Files Reference

| File | Purpose |
|---|---|
| `scripts/issue-lifecycle.ts` | Label names, timeouts, and messages — single source of truth |
| `.claude-plugin/marketplace.json` | Lists all bundled plugins for the marketplace |
| `plugins/README.md` | Human-readable plugin directory with descriptions |
| `.github/workflows/claude.yml` | `@claude` mention integration |
| `.github/workflows/claude-issue-triage.yml` | Automatic issue triage |
| `examples/settings/README.md` | Enterprise settings configuration guide |
| `CHANGELOG.md` | Version history and release notes |
| `SECURITY.md` | Vulnerability disclosure process |
