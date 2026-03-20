---
name: update-config
description: Use this skill to configure the Claude Code harness via settings.json. Automated behaviors ("from now on when X", "each time X", "whenever X", "before/after X") require hooks configured in settings.json - the harness executes these, not Claude, so memory/preferences cannot fulfill them. Also use for: permissions ("allow X", "add permission", "move permission to"), env vars ("set X=Y"), hook troubleshooting, or any changes to settings.json/settings.local.json files. Examples: "allow npm commands", "add bq permission to global settings", "move permission to user settings", "set DEBUG=true", "when claude stops show X". For simple settings like theme/model, use Config tool.
---

# Configuring Claude Code via settings.json

## Overview

Claude Code behavior is controlled via `settings.json` files. Automated behaviors, permissions, environment variables, and hooks are all configured here.

## Settings File Locations

| File | Scope | Use For |
|------|-------|---------|
| `~/.claude/settings.json` | User (global) | Personal preferences, global permissions |
| `.claude/settings.json` | Project | Project-specific settings shared with team |
| `.claude/settings.local.json` | Project local | Personal overrides not committed to git |

## Key Configuration Areas

### Permissions

Allow or deny tool usage:

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run *)",
      "Bash(git *)",
      "Edit(*)"
    ],
    "deny": [
      "Bash(rm -rf *)"
    ]
  }
}
```

### Environment Variables

Set environment variables for Claude Code sessions:

```json
{
  "env": {
    "DEBUG": "true",
    "NODE_ENV": "development"
  }
}
```

### Hooks

Automate behaviors that trigger on events:

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Claude stopped'"
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "echo 'Running bash command'"
          }
        ]
      }
    ]
  }
}
```

### Available Hook Events

- `PreToolUse` - Before a tool is used
- `PostToolUse` - After a tool completes
- `Stop` - When Claude stops/completes a task
- `SessionStart` - When a session begins
- `SessionEnd` - When a session ends

## Workflow

1. Identify what behavior to configure
2. Choose the right settings file (user vs project vs local)
3. Add the appropriate configuration
4. Verify changes take effect in the next Claude Code session

## Common Patterns

**Allow specific bash commands:**
```json
{ "permissions": { "allow": ["Bash(npm *)", "Bash(yarn *)"] } }
```

**Move permission to user settings** (when project settings are too broad):
Edit `~/.claude/settings.json` instead of `.claude/settings.json`

**Hook troubleshooting:**
- Check hook command exits with 0 for success
- Use `echo` commands to debug
- Check `--verbose` mode for hook execution details
