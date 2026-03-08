# Claude Code Slash Command Templates

Portable slash commands for [Claude Code](https://docs.anthropic.com/en/docs/claude-code). These are `.md` files that become system prompts when invoked with `/command-name` in your Claude Code session.

## Installation

```bash
# Copy all commands to your Claude Code commands directory
cp *.md ~/.claude/commands/   # ← don't copy this README

# Or cherry-pick individual commands
cp brainstorm.md ~/.claude/commands/
cp braintrust.md ~/.claude/commands/
cp convergence.md ~/.claude/commands/
cp redact.md ~/.claude/commands/
cp snapshot.md ~/.claude/commands/
cp save.md ~/.claude/commands/
```

After copying, restart Claude Code. Commands appear as `/brainstorm`, `/redact`, etc.

## Commands

| Command | What it does |
|---------|-------------|
| `/brainstorm` | Multi-perspective ideation — 3 viewpoints (Optimist, Critic, Analyst) + synthesis + recommendation |
| `/braintrust` | Polymath lifeline panel — 5 historical thinkers (Einstein, Sun Tzu, Buffett, Feynman, Da Vinci) stress-test high-stakes decisions |
| `/convergence` | AI capability measurement — track boons/banes, calculate hit rate, identify OEM ceiling. See [framework](../docs/AI_CONVERGENCE_MEASUREMENT.md) |
| `/redact` | Toggle sensitive data masking — masks dollar amounts, IPs, account IDs in output |
| `/snapshot` | Git checkpoint bracketing — save/restore points before risky operations |
| `/save` | Auto-commit and push — stage, commit with conventional message, push |

## How Slash Commands Work

Claude Code slash commands are just markdown files. When you type `/brainstorm`, Claude Code reads `~/.claude/commands/brainstorm.md` and injects it as a system prompt for that turn. No plugins, no installs, no third-party dependencies.

### Anatomy of a command

```markdown
# /command-name — Short Description

Instructions for Claude on what to do when this command is invoked.

## Instructions
1. Step one...
2. Step two...

## Behavioral Rules
- Rule one...
- Rule two...
```

The `$ARGUMENTS` placeholder captures everything after the command name:
- `/brainstorm dark mode` → `$ARGUMENTS` = "dark mode"
- `/redact status` → `$ARGUMENTS` = "status"

### Creating your own

1. Create a `.md` file in `~/.claude/commands/`
2. Name it what you want the command to be (e.g., `deploy.md` → `/deploy`)
3. Write instructions in markdown
4. Use `$ARGUMENTS` to capture user input

## Customization

These templates are starting points. Customize them:

- **Rename perspectives** in `/brainstorm` to match your team (e.g., "PM / Engineer / Designer")
- **Add masking patterns** to `/redact` for your domain (e.g., patient IDs for healthcare)
- **Change git workflow** in `/save` to match your branch strategy
- **Add pre/post hooks** to `/snapshot` for your backup strategy

## Requirements

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) CLI
- That's it. No dependencies.
