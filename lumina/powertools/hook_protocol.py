"""
Hook Protocol — Common I/O utilities for Claude Code hooks.

Claude Code hooks receive JSON on stdin and communicate via:
- stdout: JSON messages (systemMessage, etc.)
- stderr: Human-readable warnings/info
- exit code 0: allow the operation
- exit code 2: block the operation (PreToolUse only)

Pattern extracted from production hook implementations.

Example:
    from lumina.powertools import HookIO

    io = HookIO.from_stdin()
    if io.tool_name == "Bash" and "rm -rf" in io.command:
        io.block("Destructive command blocked by safety hook")
    io.allow()
"""

import json
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class HookResult:
    """Result of a hook decision."""
    allowed: bool
    reason: str = ""
    system_message: str = ""


@dataclass
class HookIO:
    """Parsed hook input with convenience methods for common operations.

    Attributes:
        raw: The full JSON dict from stdin
        tool_name: Name of the tool (Bash, Read, Edit, Write, etc.)
        tool_input: Tool input parameters
        tool_output: Tool output (PostToolUse only)
        session_id: Current session identifier
        model: Model being used
        transcript_path: Path to session transcript JSONL
    """
    raw: dict = field(default_factory=dict)
    tool_name: str = ""
    tool_input: dict = field(default_factory=dict)
    tool_output: str = ""
    session_id: str = ""
    model: str = ""
    transcript_path: str = ""

    @classmethod
    def from_stdin(cls) -> "HookIO":
        """Read and parse hook data from stdin."""
        try:
            data = json.loads(sys.stdin.read())
        except (json.JSONDecodeError, EOFError):
            data = {}
        return cls(
            raw=data,
            tool_name=data.get("tool_name", ""),
            tool_input=data.get("tool_input", {}),
            tool_output=str(data.get("tool_output", "")),
            session_id=data.get("session_id", ""),
            model=data.get("model", ""),
            transcript_path=data.get("transcript_path", ""),
        )

    @property
    def command(self) -> str:
        """Get the Bash command (empty string if not a Bash tool call)."""
        if self.tool_name == "Bash":
            return self.tool_input.get("command", "")
        return ""

    @property
    def file_path(self) -> str:
        """Get the file path from Read/Edit/Write tool calls."""
        return self.tool_input.get("file_path", "")

    @property
    def user_prompt(self) -> str:
        """Get user prompt (UserPromptSubmit hooks only)."""
        return self.raw.get("user_prompt", self.raw.get("prompt", ""))

    def allow(self, message: str = "") -> None:
        """Allow the operation and exit."""
        if message:
            print(message, file=sys.stderr)
        sys.exit(0)

    def block(self, reason: str) -> None:
        """Block the operation (PreToolUse only) and exit."""
        result = {"result": "block", "reason": reason}
        print(json.dumps(result))
        sys.exit(2)

    def warn(self, message: str) -> None:
        """Print a warning to stderr (visible to Claude Code)."""
        print(f"WARNING: {message}", file=sys.stderr)

    def system_message(self, message: str) -> None:
        """Send a system message to Claude (visible in context)."""
        print(json.dumps({"systemMessage": message}))

    def decide(self, result: HookResult) -> None:
        """Apply a HookResult decision."""
        if result.system_message:
            self.system_message(result.system_message)
        if result.allowed:
            self.allow(result.reason)
        else:
            self.block(result.reason)
