# /save — Auto-Commit and Push

Stage all changes, generate a descriptive commit message, commit, and push. One command, no questions.

## Instructions

1. Run `git status` to see all changes (staged, unstaged, untracked)
2. If no changes exist, report: `SAVE: Nothing to commit — working tree clean`
3. Run `git diff --stat` and `git diff --cached --stat` to understand what changed
4. Stage relevant files:
   - Add modified and new files that are part of the current work
   - Do NOT stage files that look like secrets (`.env`, `credentials.*`, `*.key`, `*.pem`)
   - If suspicious files are found, warn the user and skip them
5. Generate a commit message:
   - Use conventional commit format: `feat:`, `fix:`, `refactor:`, `chore:`, `docs:`, `test:`
   - Focus on the "why" not the "what"
   - Keep first line under 72 characters
6. Commit with the generated message
7. Push to the remote tracking branch
8. Report: `SAVE: [short-hash] → [remote]/[branch] ([N] files, [summary])`

### Arguments

- `/save` — full auto (stage + commit + push)
- `/save dry` — show what WOULD be committed without doing it
- `/save msg [message]` — use the provided message instead of auto-generating

## Behavioral Rules
- Never commit files that may contain secrets — scan before staging
- Never force-push — if push fails due to divergence, report and stop
- Always use conventional commit prefixes
- Keep it fast — one command, immediate result
- If on a protected branch (main/master), warn before pushing
