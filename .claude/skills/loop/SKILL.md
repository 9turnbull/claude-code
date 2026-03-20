---
name: loop
description: Run a prompt or slash command on a recurring interval (e.g. /loop 5m /foo, defaults to 10m) - When the user wants to set up a recurring task, poll for status, or run something repeatedly on an interval (e.g. "check the deploy every 5 minutes", "keep running /babysit-prs"). Do NOT invoke for one-off tasks.
---

Run a prompt or slash command repeatedly on a fixed interval.

## Usage

`/loop [interval] <prompt or /skill>`

- **interval**: Optional. Duration like `30s`, `5m`, `2h`. Defaults to `10m`.
- **prompt or /skill**: What to run each iteration.

## Examples

- `/loop 5m /babysit-prs` — run `/babysit-prs` every 5 minutes
- `/loop check deploy status and report` — check deploy status every 10 minutes
- `/loop 30s run tests and summarize failures` — run tests every 30 seconds

## How to execute

1. Parse the interval from the first argument (default: `10m`)
2. Parse the task from remaining arguments
3. Execute the task immediately (iteration 1)
4. Use `sleep <seconds>` via Bash between iterations
5. Repeat until the user stops the session

## Interval parsing

| Input | Seconds |
|-------|---------|
| `30s` | 30 |
| `5m`  | 300 |
| `2h`  | 7200 |

Convert to seconds: strip suffix, multiply by unit factor.

## Loop behavior

- Print a header before each iteration: `--- Loop iteration N (interval: Xm) ---`
- After each iteration, sleep for the specified interval
- Continue indefinitely until interrupted
- If the task is a slash command (starts with `/`), invoke it as a skill

## Notes

- Only use for recurring tasks. For one-off tasks, just run the task directly.
- Keep iteration output concise so the conversation doesn't flood.
