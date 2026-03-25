# Google Drive Organiser Plugin

Organise and clean up your Google Drive directly from Claude Code. This plugin connects to Google Drive via the official MCP server and provides three commands for sorting files, removing clutter, and auditing your folder structure.

## Commands

| Command | Description |
|---|---|
| `/gdrive-organise [folder]` | Move loose files into type-based sub-folders (Documents, Images, PDFs, etc.) |
| `/gdrive-clean [folder]` | Find duplicate files and flag large/old files for cleanup |
| `/gdrive-audit [folder]` | Analyse folder structure and get improvement suggestions |

All commands default to your **My Drive root** when no folder argument is provided.

## Prerequisites

### 1. Install the Google Drive MCP server

```bash
npx -y @modelcontextprotocol/server-gdrive
```

### 2. Set up Google OAuth credentials

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Enable the **Google Drive API**
4. Create **OAuth 2.0 credentials** (Desktop app type)
5. Download the credentials JSON file

### 3. Set the credentials path

Set the `GDRIVE_CREDENTIALS_FILE` environment variable to the path of your credentials file:

```bash
# In your shell profile (.zshrc, .bashrc, etc.)
export GDRIVE_CREDENTIALS_FILE="/path/to/your/credentials.json"
```

Or add it to your Claude Code project settings:

```json
// .claude/settings.json
{
  "env": {
    "GDRIVE_CREDENTIALS_FILE": "/path/to/your/credentials.json"
  }
}
```

On first use, the MCP server will open a browser window for you to authorise access to your Google Drive.

## Usage Examples

```
# Organise everything in My Drive root
/gdrive-organise

# Organise a specific folder
/gdrive-organise Work Projects

# Find duplicates and large files in My Drive
/gdrive-clean

# Scan a specific folder for cleanup
/gdrive-clean Downloads

# Audit the full folder structure
/gdrive-audit

# Audit a specific folder
/gdrive-audit My Business
```

## How It Works

Each command launches specialist agents that interact with Google Drive through the MCP server:

- **`drive-analyser`** — Reads and maps your Drive contents, computes statistics, detects duplicates and stale files
- **`drive-organiser`** — Executes an approved plan: creates folders, moves files, and moves unwanted files to Trash

Files are **never permanently deleted** — the cleanup command only moves items to Trash, giving you the chance to review and restore them.

## Plugin Structure

```
google-drive-organiser/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                    # Google Drive MCP server config
├── commands/
│   ├── gdrive-organise.md       # /gdrive-organise command
│   ├── gdrive-clean.md          # /gdrive-clean command
│   └── gdrive-audit.md          # /gdrive-audit command
├── agents/
│   ├── drive-analyser.md        # Scans Drive and returns inventory
│   └── drive-organiser.md       # Executes approved organisation plans
└── README.md
```
