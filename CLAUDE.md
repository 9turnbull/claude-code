# CLAUDE.md — Claude Code Repository Guide

This file provides guidance for AI assistants (and developers) working in this repository.

## What This Repository Is

This is the **official Claude Code plugins, examples, and documentation repository** maintained by Anthropic. It is **not** the Claude Code CLI source code — the CLI is distributed separately via install scripts. This repository serves as:

- The canonical **plugin marketplace** for Claude Code
- A collection of **14 production-ready plugins** with examples
- **Configuration templates** for enterprise deployment
- **GitHub automation workflows** using Claude Code's GitHub Actions integration

## Repository Structure

```
claude-code/
├── .claude/                    # Project-level Claude Code configuration
│   ├── commands/               # Project-scoped custom slash commands
│   └── settings.json           # Project settings (plugin marketplace, enabled plugins)
├── .claude-plugin/
│   └── marketplace.json        # Bundled plugin registry (canonical plugin list)
├── .devcontainer/
│   └── devcontainer.json       # Dev container spec (Node.js, git-delta, zsh)
├── .github/
│   ├── ISSUE_TEMPLATE/         # GitHub issue templates
│   └── workflows/              # 12 CI/CD workflows for repository automation
├── examples/
│   ├── hooks/                  # Example hook scripts
│   └── settings/               # Security configuration templates (lax/strict/sandbox)
├── plugins/                    # 14 official Claude Code plugins (see below)
├── scripts/                    # Repository maintenance scripts (TypeScript/Shell)
├── CHANGELOG.md
├── README.md
└── SECURITY.md
```

## Plugin Architecture

### Plugin Directory Layout

Every plugin follows this standard structure:

```
plugins/<plugin-name>/
├── .claude-plugin/plugin.json  # Plugin metadata (name, version, description, author)
├── commands/                   # Slash commands defined as Markdown files
├── agents/                     # Specialized AI agents (*.md with instructions)
├── skills/                     # Reusable knowledge modules (SKILL.md)
├── hooks/                      # Event handler scripts + hooks.json manifest
├── .mcp.json                   # MCP server config (optional)
└── README.md                   # Plugin documentation
```

### Command Files

Slash commands are Markdown files with optional YAML frontmatter:

```markdown
---
description: Short description shown in command picker
argument-hint: <what to pass>
---

Command instructions in natural language...
```

### Hook System

Hooks are event-driven scripts triggered by Claude Code lifecycle events. A `hooks.json` manifest in the plugin root maps events to scripts:

- **PreToolUse** — runs before a tool is executed (can block or allow)
- **PostToolUse** — runs after a tool completes
- **SessionStart** — runs when a Claude Code session begins
- **SessionStop** — runs when a session ends

Hook scripts are typically Python or shell, reading event JSON from stdin and writing responses to stdout.

### Marketplace Registration

Every plugin must be registered in `.claude-plugin/marketplace.json` to be discoverable:

```json
{
  "name": "plugin-name",
  "description": "...",
  "source": "./plugins/plugin-name",
  "category": "productivity"
}
```

Valid categories: `development`, `productivity`, `learning`, `security`, `git`.

## Available Plugins

| Plugin | Category | Description |
|--------|----------|-------------|
| `agent-sdk-dev` | development | Agent SDK setup wizard and validators |
| `claude-opus-4-5-migration` | development | Automated model string migration tool |
| `code-review` | productivity | 5-agent parallel PR review with confidence scoring |
| `commit-commands` | git | `/commit`, `/commit-push-pr`, `/clean_gone` workflows |
| `explanatory-output-style` | learning | Educational mode with implementation insights |
| `feature-dev` | productivity | 7-phase guided feature development pipeline |
| `frontend-design` | productivity | Production UI design patterns and guidance |
| `hookify` | customization | Create custom hooks from conversation patterns |
| `learning-output-style` | learning | Interactive learning with codebase contributions |
| `plugin-dev` | development | Plugin creation toolkit with 7 skills |
| `pr-review-toolkit` | productivity | 6 specialized PR review agents |
| `ralph-wiggum` | autonomy | Self-referential iterative agent loops |
| `remote-control` | mobility | Browser/mobile session access setup |
| `security-guidance` | security | PreToolUse hook for security pattern detection |

## GitHub Actions Workflows

The repository uses Claude Code's GitHub Actions integration to automate repository management:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `claude.yml` | `@claude` mentions in issues/PRs | Run Claude Code on demand |
| `claude-dedupe-issues.yml` | New issues, manual dispatch | AI-powered duplicate detection |
| `claude-issue-triage.yml` | Issue comments | Auto-apply labels via AI triage |
| `lock-closed-issues.yml` | Daily schedule (2pm UTC) | Lock stale closed issues after 7 days |
| `auto-close-duplicates.yml` | Issue label update | Close confirmed duplicates |
| `sweep.yml` | Issue label trigger | Sweep bot integration |

The main `claude.yml` workflow uses:
```yaml
uses: anthropics/claude-code-action@v1
with:
  anthropic_api_key: ${{ secrets.ANTHROPIC_API_KEY }}
  claude_args: "--model claude-sonnet-4-5-20250929"
```

## Project Settings

The `.claude/settings.json` configures this repository as a local plugin marketplace:

```json
{
  "$schema": "https://json.schemastore.org/claude-code-settings.json",
  "extraKnownMarketplaces": {
    "claude-code-plugins": {
      "source": "directory",
      "path": "/home/user/claude-code"
    }
  },
  "enabledPlugins": {
    "remote-control@claude-code-plugins": true
  }
}
```

## Project-Scoped Commands

Three custom commands are defined in `.claude/commands/` for repository maintenance:

- `dedupe` — Find and deduplicate GitHub issues
- `triage-issue` — Apply labels to a GitHub issue
- `commit-push-pr` — Commit, push, and open a PR

## Development Conventions

### When Adding a New Plugin

1. Create directory at `plugins/<plugin-name>/`
2. Add `.claude-plugin/plugin.json` with required metadata fields: `name`, `version`, `description`, `author`
3. Add plugin documentation in `README.md`
4. Register the plugin in `.claude-plugin/marketplace.json`
5. Validate with `claude plugin validate` before committing

### When Modifying Existing Plugins

- Keep `plugin.json` version field updated when making functional changes
- Ensure hook scripts exit with code `0` for success, non-zero to block
- Test hooks locally before committing

### Commit Style

Use conventional commits:
- `feat(plugin-name): ...` for new plugin features
- `fix(plugin-name): ...` for bug fixes
- `chore: ...` for maintenance tasks (CHANGELOG updates, etc.)
- `docs: ...` for documentation-only changes

### Branch Naming

Branches for Claude-automated work follow the pattern: `claude/<description>-<session-id>`

## Required Secrets (GitHub Actions)

| Secret | Purpose |
|--------|---------|
| `ANTHROPIC_API_KEY` | Claude API access for all workflows |
| `GITHUB_TOKEN` | Standard GitHub token (auto-provided) |
| `STATSIG_API_KEY` | Analytics event logging (optional) |

## Environment Variables (DevContainer)

| Variable | Value | Purpose |
|----------|-------|---------|
| `NODE_OPTIONS` | `--max-old-space-size=4096` | Node.js memory limit |
| `CLAUDE_CONFIG_DIR` | `/home/node/.claude` | Claude config location |

## Settings Templates

The `examples/settings/` directory provides security configuration templates:

- `settings-lax.json` — Permissive settings for trusted environments
- `settings-strict.json` — Restrictive settings for production/enterprise
- `settings-sandbox.json` — Maximum isolation for untrusted code

## Security

Vulnerabilities should be reported via [HackerOne VDP](https://hackerone.com/anthropic-vdp). Do not open public GitHub issues for security vulnerabilities. See `SECURITY.md` for full policy.

## Key Links

- [Official Documentation](https://code.claude.com/docs/en/overview)
- [Setup Guide](https://code.claude.com/docs/en/setup)
- [Data Usage Policy](https://code.claude.com/docs/en/data-usage)
- [Commercial Terms](https://www.anthropic.com/legal/commercial-terms)
- [Discord Community](https://anthropic.com/discord)
- [Bug Reports](https://github.com/anthropics/claude-code/issues)
