# Google Drive Organiser Plugin

Organise and clean up your Google Drive directly from Claude Code. This plugin connects to Google Drive via the official MCP server and provides commands for sorting files, removing clutter, and auditing your folder structure.

## Commands

| Command | Description | Requires write access? |
|---|---|---|
| `/gdrive-setup` | Interactive setup wizard — configure OAuth credentials and verify connection | No |
| `/gdrive-audit [folder]` | Analyse folder structure and get improvement suggestions | No (read-only) |
| `/gdrive-organise [folder]` | Move loose files into type-based sub-folders | **Yes** |
| `/gdrive-clean [folder]` | Find duplicate files and flag large/old files for cleanup | **Yes** |

All commands default to your **My Drive root** when no folder argument is provided.

> **Scope note:** The official `@modelcontextprotocol/server-gdrive` package only requests `drive.readonly` access. `/gdrive-audit` works out of the box. `/gdrive-organise` and `/gdrive-clean` require a write-capable MCP server — see [Write access](#write-access) below.

---

## Quick Start

Run `/gdrive-setup` in Claude Code and follow the interactive wizard. It will guide you through every step below.

---

## Manual Setup

### Prerequisites

- Node.js 18+ (for `npx`)
- A Google account with access to the Drive you want to organise

### Step 1 — Enable the Google Drive API

1. Sign in to the [Google Cloud Console](https://console.cloud.google.com/) with the Google account that owns the Drive.
2. Create a new project (or select an existing one) via the project picker at the top.
3. Navigate to the [Google Drive API page](https://console.cloud.google.com/apis/library/drive.googleapis.com) and click **Enable**.

### Step 2 — Configure the OAuth consent screen

1. Go to [APIs & Services → OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
2. Choose **External** user type (or **Internal** if you're in a Google Workspace org).
3. Fill in the required fields: app name, support email, developer contact email.
4. On the **Test users** page, add your own Gmail address.
5. Save and continue.

### Step 3 — Create OAuth 2.0 credentials

1. Go to [APIs & Services → Credentials](https://console.cloud.google.com/apis/credentials).
2. Click **+ Create Credentials** → **OAuth client ID**.
3. Set **Application type** to **Desktop app** (not Web, not Service Account).
4. Click **Create**, then **Download JSON** from the confirmation dialog.
5. Save the file to a secure location, e.g.:
   - macOS/Linux: `~/.config/gdrive-mcp/gcp-oauth.keys.json`
   - Windows: `%USERPROFILE%\.config\gdrive-mcp\gcp-oauth.keys.json`

### Step 4 — Set environment variables

Set `GDRIVE_OAUTH_PATH` to the full absolute path of the credentials file you downloaded.

**macOS / Linux (add to `~/.zshrc` or `~/.bashrc`):**
```bash
export GDRIVE_OAUTH_PATH="$HOME/.config/gdrive-mcp/gcp-oauth.keys.json"
```

**Windows (PowerShell — sets for current user permanently):**
```powershell
[System.Environment]::SetEnvironmentVariable(
  "GDRIVE_OAUTH_PATH",
  "$env:USERPROFILE\.config\gdrive-mcp\gcp-oauth.keys.json",
  "User"
)
```

Optionally, set `GDRIVE_CREDENTIALS_PATH` to control where the OAuth access token is stored after authentication (defaults to `.gdrive-server-credentials.json` in the working directory):
```bash
export GDRIVE_CREDENTIALS_PATH="$HOME/.config/gdrive-mcp/credentials.json"
```

### Step 5 — Authenticate (one-time browser flow)

Run the auth command in your terminal:

```bash
npx @modelcontextprotocol/server-gdrive auth
```

A browser window opens. Sign in with the Google account you added as a test user and grant the requested permissions. The access token is saved to `GDRIVE_CREDENTIALS_PATH` and reused on future runs — you won't need to repeat this unless the token expires.

### Step 6 — Restart Claude Code

Restart Claude Code so it picks up the new environment variable and starts the `gdrive` MCP server. Then run `/gdrive-setup` to verify the connection.

---

## Write Access

The official `@modelcontextprotocol/server-gdrive` package only requests `drive.readonly` scope. To use `/gdrive-organise` and `/gdrive-clean` (which move and trash files), you need a write-capable MCP server.

Replace the entry in `.mcp.json` with a community server that requests the full `https://www.googleapis.com/auth/drive` scope, then re-run `/gdrive-setup` to authenticate with the new server.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| MCP server not starting | `GDRIVE_OAUTH_PATH` not set or empty | Set the env var and restart Claude Code |
| `Error: ENOENT: no such file or directory` | Path in `GDRIVE_OAUTH_PATH` doesn't exist | Check the path is correct and absolute |
| `invalid_client` during auth | Wrong credential type | Re-create OAuth credentials as **Desktop app** type |
| `access_denied` during auth | Google account not added as test user | Add the account on the OAuth consent screen Test users page |
| Token expired / `invalid_grant` | Refresh token revoked | Re-run `npx @modelcontextprotocol/server-gdrive auth` |
| Files not moving / permission error | Read-only scope | Switch to a write-capable MCP server (see [Write access](#write-access)) |
| `gdrive` tools not visible in Claude Code | MCP server not started | Confirm env var is set, then restart Claude Code |

---

## Plugin Structure

```
google-drive-organiser/
├── .claude-plugin/
│   └── plugin.json
├── .mcp.json                    # Google Drive MCP server config
├── commands/
│   ├── gdrive-setup.md          # /gdrive-setup — interactive setup wizard
│   ├── gdrive-audit.md          # /gdrive-audit — folder structure analysis
│   ├── gdrive-organise.md       # /gdrive-organise — sort files by type
│   └── gdrive-clean.md          # /gdrive-clean — find duplicates & stale files
├── agents/
│   ├── drive-analyser.md        # Scans Drive and returns inventory
│   └── drive-organiser.md       # Executes approved organisation plans
└── README.md
```
