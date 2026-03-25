---
description: Guided setup for the Google Drive MCP server — configure OAuth credentials and verify connection
allowed-tools: ["AskUserQuestion", "Bash", "TodoWrite"]
---

# Google Drive MCP Setup Wizard

Walk through configuring the `@modelcontextprotocol/server-gdrive` MCP server so Claude Code can connect to your Google Drive.

## Instructions

Use TodoWrite to track progress through the steps below.

---

### Step 1: Check existing configuration

Run the following to check whether the required environment variables are already set:

```bash
echo "GDRIVE_OAUTH_PATH=${GDRIVE_OAUTH_PATH}"
echo "GDRIVE_CREDENTIALS_PATH=${GDRIVE_CREDENTIALS_PATH}"
```

- If `GDRIVE_OAUTH_PATH` is set and the file exists at that path, skip to **Step 6 (Verify connection)**.
- If `GDRIVE_OAUTH_PATH` is empty or the file is missing, continue from Step 2.

---

### Step 2: Create a Google Cloud project and enable the Drive API

Use AskUserQuestion to ask:

> "Have you already enabled the Google Drive API in a Google Cloud project? (If you're not sure, answer No and I'll guide you through it.)"

If **No**, give the user these instructions:

1. Go to https://console.cloud.google.com/ and sign in with the Google account that owns the Drive you want to access.
2. Create a new project (or select an existing one) using the project picker at the top.
3. Go to https://console.cloud.google.com/apis/library/drive.googleapis.com
4. Click **Enable** to enable the Google Drive API for this project.

Then use AskUserQuestion to confirm: "Have you enabled the Google Drive API? Click Yes when ready to continue."

---

### Step 3: Configure the OAuth consent screen

Give the user these instructions:

1. In the Google Cloud Console, go to **APIs & Services → OAuth consent screen**:
   https://console.cloud.google.com/apis/credentials/consent
2. Choose **External** user type (unless you're in a Google Workspace org, in which case choose **Internal**).
3. Fill in the required fields:
   - **App name**: `Google Drive MCP` (or any name you like)
   - **User support email**: your email address
   - **Developer contact email**: your email address
4. On the **Scopes** page you can skip adding scopes manually — the MCP server requests them during auth.
5. On the **Test users** page, add your own Gmail address as a test user.
6. Save and continue through to the end.

Use AskUserQuestion to confirm: "Have you completed the OAuth consent screen setup? Click Yes when ready."

---

### Step 4: Create OAuth 2.0 credentials and download the JSON

Give the user these instructions:

1. Go to **APIs & Services → Credentials**:
   https://console.cloud.google.com/apis/credentials
2. Click **+ Create Credentials** → **OAuth client ID**.
3. For **Application type**, select **Desktop app**.
4. Give it a name (e.g. `MCP Desktop Client`) and click **Create**.
5. In the dialog that appears, click **Download JSON**.
6. Save the file somewhere secure, e.g.:
   - macOS/Linux: `~/.config/gdrive-mcp/gcp-oauth.keys.json`
   - Windows: `%USERPROFILE%\.config\gdrive-mcp\gcp-oauth.keys.json`

Use AskUserQuestion to ask: "What is the full path where you saved the credentials JSON file?"

Store the answer as `$OAUTH_PATH`.

---

### Step 5: Set the environment variable and run first-time auth

Give the user these instructions based on their OS:

**macOS / Linux (zsh):**
```bash
mkdir -p ~/.config/gdrive-mcp
# Add to ~/.zshrc or ~/.bashrc:
echo 'export GDRIVE_OAUTH_PATH="$OAUTH_PATH"' >> ~/.zshrc
source ~/.zshrc
```

**Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable("GDRIVE_OAUTH_PATH", "$OAUTH_PATH", "User")
```

Then run the one-time authentication flow in a terminal:
```bash
npx @modelcontextprotocol/server-gdrive auth
```

This opens a browser window. Sign in with the Google account you added as a test user, and grant the requested permissions. A credentials file will be saved automatically (default: `.gdrive-server-credentials.json` in the current directory, or the path in `GDRIVE_CREDENTIALS_PATH` if set).

Use AskUserQuestion to confirm: "Have you run `npx @modelcontextprotocol/server-gdrive auth` and completed the browser sign-in? Click Yes when done."

**Important:** After setting the env var, you must **restart Claude Code** so it picks up the new environment variable and starts the MCP server.

---

### Step 6: Verify the connection

After restarting Claude Code, verify the `gdrive` MCP server is available by attempting a simple Drive list call using the `gdrive` MCP tools (list files at the Drive root).

- If the call succeeds and returns files or an empty list: report **"Setup complete! The Google Drive MCP server is connected. Run /gdrive-audit to get started."**
- If the MCP tools are unavailable: report **"The gdrive MCP server is not yet available. Make sure you have restarted Claude Code after setting GDRIVE_OAUTH_PATH, then run /gdrive-setup again."**
- If you get an auth error: instruct the user to re-run `npx @modelcontextprotocol/server-gdrive auth` and repeat Step 5.

---

### Read-only scope note

The official `@modelcontextprotocol/server-gdrive` server only requests **`drive.readonly`** access. This means:

- `/gdrive-audit` — fully supported (read-only analysis)
- `/gdrive-organise` and `/gdrive-clean` — require a write-capable MCP server

To use the write commands, you need a community fork or alternative MCP server configured with the full `https://www.googleapis.com/auth/drive` scope. The setup steps above still apply — only the MCP server package changes.
