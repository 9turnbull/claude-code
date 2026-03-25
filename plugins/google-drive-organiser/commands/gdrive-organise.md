---
description: Organise Google Drive files into folders by file type
argument-hint: Optional folder name or ID to organise (defaults to My Drive root)
allowed-tools: ["Task", "TodoWrite", "AskUserQuestion"]
---

> **Write access required.** This command moves files between folders. The official `@modelcontextprotocol/server-gdrive` package is read-only and cannot perform moves. You need a write-capable MCP server with `drive` scope. Run `/gdrive-setup` for setup help, or use `/gdrive-audit` for a read-only folder analysis.

# Google Drive Organiser

Organise files in Google Drive by grouping them into type-based folders.

## Your task

You are organising a user's Google Drive. Your goal is to move loose files into labelled folders by type, keeping the user in control of every decision.

**Target folder:** $ARGUMENTS (if empty, organise the root of My Drive)

## Steps

1. **Launch the drive-analyser agent** to scan the target folder and return:
   - A list of all files (name, MIME type, size, last modified, parent folder)
   - Any existing sub-folders already present
   - A summary count by file category

2. **Review the analysis** and build a proposed organisation plan:
   - Map each loose file to a destination folder using this scheme:
     | Category | Folder name | MIME types |
     |---|---|---|
     | Documents | `Documents` | Docs, Word, ODT, TXT, RTF, Pages |
     | Spreadsheets | `Spreadsheets` | Sheets, Excel, ODS, Numbers, CSV |
     | Presentations | `Presentations` | Slides, PowerPoint, ODP, Keynote |
     | PDFs | `PDFs` | application/pdf |
     | Images | `Images` | image/* |
     | Videos | `Videos` | video/* |
     | Audio | `Audio` | audio/* |
     | Archives | `Archives` | zip, tar, gz, rar, 7z |
     | Code | `Code` | text/x-*, application/json, application/xml, etc. |
     | Other | `Other` | anything unclassified |
   - Skip files already inside a named sub-folder (only move loose files at the target level)

3. **Present the plan to the user** using AskUserQuestion:
   - Show a table: File → Destination folder
   - Ask: "Shall I proceed with this organisation? You can also customise folder names."
   - If the user wants changes, update the plan before continuing

4. **Launch the drive-organiser agent** with the approved plan to:
   - Create any destination folders that do not already exist
   - Move each file to its destination folder
   - Report a summary of files moved and folders created

5. **Report completion** — list folders created, files moved, and any files skipped or that had errors.

Use TodoWrite to track progress through each step.
