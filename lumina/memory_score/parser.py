"""
Memory file parser and format normalizer.

Reads any AI memory file format (CLAUDE.md, .cursorrules, .aider, etc.),
extracts structural metrics, and normalizes to a common representation.

Zero external dependencies.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from .constants import FORMAT_PATTERNS


@dataclass
class MemoryFileMetrics:
    """Structural metrics extracted from a memory file."""

    path: str
    filename: str
    format_type: str  # claude, cursor, copilot, aider, windsurf, unknown

    # Structure
    line_count: int = 0
    has_frontmatter: bool = False
    heading_counts: Dict[int, int] = field(default_factory=dict)  # level -> count
    table_count: int = 0
    code_block_count: int = 0
    list_item_count: int = 0

    # Content
    lines: List[str] = field(default_factory=list, repr=False)
    word_count: int = 0
    unique_words: int = 0
    blank_line_ratio: float = 0.0

    # Tags and references
    hashtags: List[str] = field(default_factory=list)
    agent_refs: List[str] = field(default_factory=list)
    file_refs: List[str] = field(default_factory=list)
    md_links: List[str] = field(default_factory=list)
    crossref_lines: List[str] = field(default_factory=list)

    # Dates
    dates_found: List[str] = field(default_factory=list)
    most_recent_date: Optional[str] = None

    # Rules
    imperative_count: int = 0
    never_always_count: int = 0

    # Satellite files (for directory scoring)
    satellite_files: List[str] = field(default_factory=list)
    has_trigger_table: bool = False
    has_index_section: bool = False


def detect_format(filename: str) -> str:
    """Detect memory file format from filename."""
    basename = os.path.basename(filename)
    for fmt, patterns in FORMAT_PATTERNS.items():
        for pattern in patterns:
            if basename == pattern or basename.endswith(pattern):
                return fmt
    if basename.endswith(".md"):
        return "claude"  # Default markdown = claude format
    return "unknown"


def parse_file(filepath: str) -> MemoryFileMetrics:
    """Parse a memory file and extract all structural metrics."""
    filepath = str(filepath)
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(f"Memory file not found: {filepath}")

    content = path.read_text(encoding="utf-8", errors="replace")
    lines = content.splitlines()

    metrics = MemoryFileMetrics(
        path=filepath,
        filename=path.name,
        format_type=detect_format(path.name),
        line_count=len(lines),
        lines=lines,
    )

    _extract_structure(metrics, lines)
    _extract_content(metrics, lines, content)
    _extract_tags(metrics, content)
    _extract_dates(metrics, content)
    _extract_rules(metrics, content)
    _extract_satellite_info(metrics, lines)

    return metrics


def parse_directory(dirpath: str) -> List[MemoryFileMetrics]:
    """Parse all memory files in a directory."""
    dirpath = Path(dirpath)
    if not dirpath.is_dir():
        raise NotADirectoryError(f"Not a directory: {dirpath}")

    results = []
    for f in sorted(dirpath.glob("*.md")):
        results.append(parse_file(str(f)))

    # Also check for non-.md memory files
    for pattern_list in FORMAT_PATTERNS.values():
        for pattern in pattern_list:
            if not pattern.endswith(".md"):
                for f in dirpath.glob(pattern):
                    results.append(parse_file(str(f)))

    return results


def _extract_structure(metrics: MemoryFileMetrics, lines: List[str]) -> None:
    """Extract structural metrics: headings, tables, code blocks, frontmatter."""
    in_code_block = False
    in_frontmatter = False
    frontmatter_started = False

    for i, line in enumerate(lines):
        stripped = line.strip()

        # Frontmatter detection (YAML)
        if i == 0 and stripped == "---":
            in_frontmatter = True
            frontmatter_started = True
            continue
        if in_frontmatter and stripped == "---":
            in_frontmatter = False
            metrics.has_frontmatter = True
            continue
        if in_frontmatter:
            continue

        # Code block detection
        if stripped.startswith("```"):
            if in_code_block:
                in_code_block = False
            else:
                in_code_block = True
                metrics.code_block_count += 1
            continue

        if in_code_block:
            continue

        # Heading detection
        match = re.match(r"^(#{1,6})\s", line)
        if match:
            level = len(match.group(1))
            metrics.heading_counts[level] = metrics.heading_counts.get(level, 0) + 1

        # Table detection (pipe-delimited rows)
        if stripped.startswith("|") and stripped.endswith("|"):
            metrics.table_count += 1

        # List items
        if re.match(r"^\s*[-*+]\s", line) or re.match(r"^\s*\d+\.\s", line):
            metrics.list_item_count += 1


def _extract_content(
    metrics: MemoryFileMetrics, lines: List[str], content: str
) -> None:
    """Extract content metrics: words, unique words, blank ratio."""
    words = re.findall(r"\b[a-zA-Z_]{2,}\b", content.lower())
    metrics.word_count = len(words)
    metrics.unique_words = len(set(words))

    blank_count = sum(1 for line in lines if not line.strip())
    metrics.blank_line_ratio = blank_count / max(len(lines), 1)


def _extract_tags(metrics: MemoryFileMetrics, content: str) -> None:
    """Extract hashtags, agent refs, file refs, and cross-references."""
    # Hashtags (#COMPUSEC, #LIFE_SUPPORT, etc.)
    metrics.hashtags = list(set(re.findall(r"#[A-Z][A-Z_]{2,}", content)))

    # Agent refs (@MARVIN, @JARVIS, etc.)
    metrics.agent_refs = list(set(re.findall(r"@[A-Z][A-Za-z_]+", content)))

    # File references (`rules.md`, `trading.md`, etc.)
    metrics.file_refs = list(set(re.findall(r"`([a-z_]+\.md)`", content)))

    # Markdown links to .md files
    metrics.md_links = list(
        set(re.findall(r"\[([^\]]+)\]\(([^\)]+\.md)\)", content))
    )

    # Cross-reference lines
    for line in content.splitlines():
        if "Connects to:" in line or "See also:" in line:
            metrics.crossref_lines.append(line.strip())


def _extract_dates(metrics: MemoryFileMetrics, content: str) -> None:
    """Extract dates mentioned in the content."""
    # Match YYYY-MM-DD format
    dates = re.findall(r"20\d{2}-\d{2}-\d{2}", content)
    metrics.dates_found = sorted(set(dates))
    if metrics.dates_found:
        metrics.most_recent_date = metrics.dates_found[-1]


def _extract_rules(metrics: MemoryFileMetrics, content: str) -> None:
    """Extract rule-related metrics: imperative verbs, NEVER/ALWAYS counts."""
    lower = content.lower()

    # Count imperative verbs
    from .constants import IMPERATIVE_VERBS

    for verb in IMPERATIVE_VERBS:
        metrics.imperative_count += len(
            re.findall(r"\b" + re.escape(verb) + r"\b", lower)
        )

    # Count strong directives
    metrics.never_always_count = len(re.findall(r"\b(NEVER|ALWAYS|MUST)\b", content))


def _extract_satellite_info(metrics: MemoryFileMetrics, lines: List[str]) -> None:
    """Check for satellite file references and trigger tables."""
    content_joined = "\n".join(lines)

    # Trigger table detection (pipe-delimited with file references)
    if re.search(
        r"\|\s*When working on[.\s]*\|",
        content_joined,
        re.IGNORECASE,
    ):
        metrics.has_trigger_table = True

    # Index section detection
    if re.search(r"##\s*(File|Feedback|Reference|User|Project)\s*Index", content_joined):
        metrics.has_index_section = True

    # Count satellite file references in trigger table rows
    for line in lines:
        match = re.search(r"\|\s*`([a-z_]+\.md)`\s*\|", line)
        if match:
            metrics.satellite_files.append(match.group(1))
