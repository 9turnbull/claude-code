---
name: simplify
description: Review changed code for reuse, quality, and efficiency, then fix any issues found.
---

Review the code changes and simplify wherever possible.

1. Use Bash to run `git diff HEAD` to see all changed code
2. For each changed file, review it for:
   - **Reuse**: Extract repeated logic into shared helpers or utilities
   - **Quality**: Fix naming, remove dead code, improve readability
   - **Efficiency**: Eliminate unnecessary operations, redundant lookups, or wasteful patterns
3. Apply fixes directly using Edit tool - don't just report issues, fix them
4. After fixing, re-read changed sections to verify improvements are correct
5. Summarize the simplifications made

Focus on meaningful improvements only. Don't over-engineer or add abstraction layers that don't reduce complexity. Three similar lines are often better than a premature abstraction.
