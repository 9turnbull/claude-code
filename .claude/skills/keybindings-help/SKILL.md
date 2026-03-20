---
name: keybindings-help
description: Use when the user wants to customize keyboard shortcuts, rebind keys, add chord bindings, or modify ~/.claude/keybindings.json. Examples: "rebind ctrl+s", "add a chord shortcut", "change the submit key", "customize keybindings".
---

# Customizing Claude Code Keyboard Shortcuts

## Overview

Claude Code supports custom keyboard shortcuts through `~/.claude/keybindings.json`. You can rebind any built-in action, add chord bindings, or create entirely new shortcuts.

## Keybindings File

Edit `~/.claude/keybindings.json` to customize shortcuts:

```json
[
  {
    "key": "ctrl+s",
    "command": "sendMessage"
  },
  {
    "key": "ctrl+shift+c",
    "command": "clearConversation"
  }
]
```

## Key Format

Keys are specified as modifier+key combinations:

| Modifier | Syntax |
|----------|--------|
| Control | `ctrl` |
| Alt/Option | `alt` |
| Shift | `shift` |
| Meta/Cmd | `meta` |

**Examples:**
- `ctrl+s` - Control + S
- `ctrl+shift+enter` - Control + Shift + Enter
- `alt+n` - Alt + N
- `meta+k` - Cmd + K (macOS)

## Chord Bindings

Chord bindings require pressing two key sequences in order:

```json
[
  {
    "key": "ctrl+k ctrl+c",
    "command": "clearConversation"
  }
]
```

## Available Commands

Common commands you can bind:

| Command | Description |
|---------|-------------|
| `sendMessage` | Submit the current message |
| `clearConversation` | Clear the conversation history |
| `openNewConversation` | Start a new conversation |
| `toggleSidebar` | Show/hide the sidebar |
| `focusInput` | Move cursor to the input field |

## Workflow

1. Open `~/.claude/keybindings.json` (create if it doesn't exist)
2. Add your custom keybinding entries
3. Save the file
4. Restart Claude Code for changes to take effect

## Example Config

```json
[
  {
    "key": "ctrl+enter",
    "command": "sendMessage"
  },
  {
    "key": "ctrl+shift+k",
    "command": "clearConversation"
  },
  {
    "key": "ctrl+k ctrl+n",
    "command": "openNewConversation"
  }
]
```
