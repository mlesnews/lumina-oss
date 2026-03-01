# /snapshot — Git Checkpoint Bracketing

Create save/restore points before risky operations. Think of it as quicksave in a video game.

## Instructions

Parse `$ARGUMENTS` for the subcommand:

### `/snapshot before [label]` — Create checkpoint
1. Run `git stash create` to capture current state without modifying working tree
2. Get current HEAD commit hash
3. Save both to `~/.claude/snapshots/[timestamp]-[label].json`:
   ```json
   {
     "label": "before-refactor",
     "timestamp": "ISO-8601",
     "head": "abc1234",
     "stash_ref": "def5678",
     "branch": "current-branch-name",
     "files_changed": ["list", "of", "modified", "files"]
   }
   ```
4. Confirm: `SNAPSHOT: Saved "[label]" at [short-hash] ([N] files tracked)`

### `/snapshot after [label]` — Mark completion
1. Find the matching "before" snapshot by label
2. Run `git diff --stat [before-hash]..HEAD` to show what changed
3. Append completion data to the snapshot file
4. Confirm: `SNAPSHOT: "[label]" complete — [N] files changed, [N] insertions, [N] deletions`

### `/snapshot list` — Show all checkpoints
1. Read all files in `~/.claude/snapshots/`
2. Display as table: label, timestamp, status (open/closed), files changed

### `/snapshot restore [label]` — Rollback to checkpoint
1. Find the snapshot by label
2. Confirm with user before proceeding (destructive operation)
3. Run `git checkout [head-hash]` to restore
4. If stash_ref exists, apply it
5. Confirm: `SNAPSHOT: Restored to "[label]" at [short-hash]`

### `/snapshot` (no args) — Show status
Same as `/snapshot list`

## Behavioral Rules
- Always create snapshots BEFORE risky operations (multi-file refactors, dependency changes, config rewrites)
- Never delete snapshot files automatically — let the user manage cleanup
- The `restore` subcommand is destructive — always confirm before executing
- Snapshots are stored in `~/.claude/snapshots/` (create directory if missing)
