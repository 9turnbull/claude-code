---
description: Audit Google Drive folder structure and get improvement suggestions
argument-hint: Optional folder name or ID to audit (defaults to My Drive root)
allowed-tools: ["Task", "TodoWrite"]
---

# Google Drive Folder Audit

Analyse your Drive's folder structure and receive concrete recommendations to improve organisation, discoverability, and consistency.

## Your task

Audit the folder structure of the user's Google Drive and produce a written report with actionable suggestions.

**Target folder:** $ARGUMENTS (if empty, audit the root of My Drive)

## Steps

1. **Launch the drive-analyser agent** to map the complete folder tree and return:
   - Folder hierarchy (name, depth level, number of direct children, total file count, total size)
   - Any loose files sitting directly in the target folder root
   - Folders that are empty
   - Folders with an unusually high number of files (> 100)
   - Maximum folder nesting depth

2. **Analyse the structure** and assess against these criteria:
   - **Flat vs. deep**: Is the hierarchy too shallow (everything dumped in root) or too deep (more than 4 levels of nesting)?
   - **Naming consistency**: Are folder names following a consistent convention (Title Case, lowercase, date prefixes, etc.)?
   - **Empty folders**: List any folders with zero files/sub-folders
   - **Overloaded folders**: List folders with > 100 direct files that would benefit from sub-categorisation
   - **Loose files at root**: Files sitting directly in the root that should be in a folder
   - **Redundant or near-duplicate folder names**: e.g. "Photos" and "Pictures" both existing

3. **Write a structured audit report** with the following sections:
   ### Summary
   - Total folders, total files, total storage, max nesting depth

   ### Strengths
   - What is already well-organised

   ### Issues Found
   - Bullet-pointed list of specific problems with folder paths cited

   ### Recommendations
   - Numbered, prioritised list of concrete actions (e.g. "Merge /Photos and /Pictures into /Photos", "Add sub-folders to /Downloads: 2023, 2024, 2025")

   ### Suggested Folder Structure
   - A proposed top-level folder layout as a tree diagram

4. **Present the report** to the user. Offer to run `/gdrive-organise` or `/gdrive-clean` as follow-up actions.

Use TodoWrite to track progress through each step.
