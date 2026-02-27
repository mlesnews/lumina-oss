"""
Status Line Builder — Template engine for Claude Code statusLine.

Build dynamic status line displays that show in the Claude Code footer.
Supports color coding, sections, and data source polling.

Configure in settings.json:
    "statusLine": {
        "type": "command",
        "command": "python3 my_statusline.py",
        "padding": 3
    }

Pattern extracted from production JARVIS HUD statusline.

Example:
    from lumina.powertools import StatusLineBuilder

    builder = StatusLineBuilder(lines=2)
    builder.section(0, "GIT", git_branch(), color="cyan")
    builder.section(0, "COST", f"${today_cost:.2f}", color="green" if ok else "red")
    builder.section(1, "MODEL", model_name, color="blue")
    print(builder.render())
"""

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ANSI color codes
COLORS = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "blink": "\033[5m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
}


@dataclass
class Section:
    """A labeled section in the statusline."""
    label: str
    value: str
    color: str = ""
    bold: bool = False


@dataclass
class StatusLineBuilder:
    """Build multi-line status displays for Claude Code.

    Args:
        lines: Number of output lines (1-3 recommended).
        separator: Character between sections on the same line.
        label_style: How to format labels ("bracket", "colon", "none").
    """
    lines: int = 1
    separator: str = " | "
    label_style: str = "bracket"
    _sections: dict[int, list[Section]] = field(default_factory=dict)

    def section(
        self,
        line: int,
        label: str,
        value: str,
        color: str = "",
        bold: bool = False,
    ) -> "StatusLineBuilder":
        """Add a section to a specific line.

        Args:
            line: Line number (0-indexed).
            label: Section label (e.g., "GIT", "COST").
            value: Section value (e.g., "main", "$1.23").
            color: Color name from COLORS dict.
            bold: Whether to bold the value.

        Returns:
            Self for chaining.
        """
        if line not in self._sections:
            self._sections[line] = []
        self._sections[line].append(Section(
            label=label,
            value=value,
            color=color,
            bold=bold,
        ))
        return self

    def _format_section(self, s: Section) -> str:
        """Format a single section with optional color."""
        parts = []

        # Label
        if s.label:
            if self.label_style == "bracket":
                parts.append(f"[{s.label}]")
            elif self.label_style == "colon":
                parts.append(f"{s.label}:")
            else:
                parts.append(s.label)

        # Value with color
        value = s.value
        if s.color and s.color in COLORS:
            prefix = COLORS[s.color]
            if s.bold:
                prefix = COLORS["bold"] + prefix
            value = f"{prefix}{value}{COLORS['reset']}"
        elif s.bold:
            value = f"{COLORS['bold']}{value}{COLORS['reset']}"

        parts.append(value)
        return " ".join(parts)

    def render(self) -> str:
        """Render all lines as a single string."""
        output_lines = []
        for line_num in range(self.lines):
            sections = self._sections.get(line_num, [])
            if sections:
                formatted = [self._format_section(s) for s in sections]
                output_lines.append(self.separator.join(formatted))
            else:
                output_lines.append("")
        return "\n".join(output_lines)

    def clear(self) -> "StatusLineBuilder":
        """Clear all sections."""
        self._sections.clear()
        return self
