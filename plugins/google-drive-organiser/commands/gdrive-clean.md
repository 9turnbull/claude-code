---
description: Find duplicate files and flag large or old files in Google Drive for cleanup
argument-hint: Optional folder name or ID to scan (defaults to My Drive root)
allowed-tools: ["Task", "TodoWrite", "AskUserQuestion"]
---

> **Write access required.** This command moves files to Trash. The official `@modelcontextprotocol/server-gdrive` package is read-only and cannot perform moves or deletions. You need a write-capable MCP server with `drive` scope. Run `/gdrive-setup` for setup help, or use `/gdrive-audit` for a read-only folder analysis.

# Google Drive Cleaner

Detect duplicates and surface large or old files so you can reclaim storage space.

## Your task

Perform a cleanup scan of the user's Google Drive and present actionable findings.

**Target folder:** $ARGUMENTS (if empty, scan the root of My Drive)

## Steps

1. **Launch the drive-analyser agent** to scan the target folder and return:
   - Full file list with: name, MIME type, size (bytes), MD5 checksum (if available), last modified date, last opened date, owner, parent folder
   - Total storage used

2. **Identify duplicates** from the analysis results:
   - Group files that share the same MD5 checksum (exact duplicates)
   - Group files that share the same name AND file size (likely duplicates, no checksum available)
   - For each duplicate group, identify the oldest copy as the likely original and the rest as candidates for removal

3. **Identify large files** (> 25 MB) sorted descending by size

4. **Identify stale files** not opened or modified in over 12 months

5. **Present findings** to the user:
   - Duplicate groups with file names, sizes, locations, and modification dates
   - Top 20 largest files
   - Top 20 most stale files
   - Estimated storage that could be reclaimed
   - Ask: "Which items would you like to delete or move to Trash?"

6. **Act on the user's selection**:
   - Move confirmed items to Trash (do NOT permanently delete)
   - Report a summary: items trashed, storage freed

Use TodoWrite to track progress through each step. Never permanently delete files — only move to Trash so the user can recover items if needed.
