"""
Dimension analyzers for memory file quality scoring.

Each function takes a MemoryFileMetrics and returns a (score, detail) tuple
where score is 0.0-1.0 and detail is a human-readable explanation.

Zero external dependencies.
"""

import re
from typing import List, Tuple

from .constants import (
    CANONICAL_DOMAINS,
    DOMAIN_KEYWORDS,
    MEMORY_MD_LINE_LIMIT,
    META_KEYWORDS,
    SECRET_PATTERNS,
    TOPIC_FILE_LINE_LIMIT,
)
from .parser import MemoryFileMetrics


def score_structure(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score structural organization: frontmatter, headings, tables, code blocks."""
    points = 0.0
    max_points = 5.0
    details = []

    # Frontmatter (1 point)
    if m.has_frontmatter:
        points += 1.0
        details.append("frontmatter present")
    else:
        details.append("no frontmatter")

    # Heading hierarchy (1 point: at least 2 levels)
    levels = len(m.heading_counts)
    if levels >= 3:
        points += 1.0
        details.append(f"{levels}-level headings")
    elif levels >= 2:
        points += 0.7
        details.append(f"{levels}-level headings")
    elif levels >= 1:
        points += 0.3
        details.append(f"{levels}-level headings")
    else:
        details.append("no headings")

    # Tables (1 point: at least 1 table with 3+ rows)
    if m.table_count >= 10:
        points += 1.0
        details.append(f"{m.table_count} table rows")
    elif m.table_count >= 3:
        points += 0.6
        details.append(f"{m.table_count} table rows")
    else:
        details.append("few/no tables")

    # Code blocks (1 point: at least 1)
    if m.code_block_count >= 3:
        points += 1.0
    elif m.code_block_count >= 1:
        points += 0.6
    details.append(f"{m.code_block_count} code blocks")

    # List items (1 point: structured content)
    if m.list_item_count >= 10:
        points += 1.0
    elif m.list_item_count >= 3:
        points += 0.5
    details.append(f"{m.list_item_count} list items")

    return points / max_points, "; ".join(details)


def score_completeness(
    m: MemoryFileMetrics, all_files: List[MemoryFileMetrics] = None
) -> Tuple[float, str]:
    """Score domain coverage against 15 canonical domains."""
    if all_files is None:
        all_files = [m]

    # Combine content from all files for domain detection
    combined = "\n".join(
        "\n".join(f.lines) for f in all_files
    ).lower()

    covered = []
    missing = []

    for domain in CANONICAL_DOMAINS:
        keywords = DOMAIN_KEYWORDS.get(domain, [])
        hits = sum(1 for kw in keywords if kw in combined)
        if hits >= 2:
            covered.append(domain)
        else:
            missing.append(domain)

    ratio = len(covered) / len(CANONICAL_DOMAINS)
    detail = f"{len(covered)}/{len(CANONICAL_DOMAINS)} domains"
    if missing:
        detail += f" (missing: {', '.join(missing[:3])})"

    return ratio, detail


def score_conciseness(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score signal-to-noise ratio: information density per line."""
    if m.line_count == 0:
        return 0.0, "empty file"

    # Unique word ratio (higher = more diverse vocabulary = more information)
    vocab_ratio = m.unique_words / max(m.word_count, 1)

    # Blank line penalty (>30% blank = verbose)
    blank_penalty = max(0, m.blank_line_ratio - 0.15) * 2

    # Words per line (target: 8-15 words/line is concise)
    words_per_line = m.word_count / max(m.line_count, 1)
    if 5 <= words_per_line <= 20:
        density_score = 1.0
    elif words_per_line < 5:
        density_score = words_per_line / 5
    else:
        density_score = max(0, 1.0 - (words_per_line - 20) / 30)

    score = min(1.0, (vocab_ratio * 0.3 + density_score * 0.5 + (1 - blank_penalty) * 0.2))
    detail = (
        f"{words_per_line:.1f} words/line, "
        f"{m.unique_words} unique/{m.word_count} total, "
        f"{m.blank_line_ratio:.0%} blank"
    )

    return max(0.0, score), detail


def score_freshness(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score content recency based on dates found in the file."""
    if not m.dates_found:
        return 0.3, "no dates found"

    # Parse most recent date
    try:
        parts = m.most_recent_date.split("-")
        year, month, day = int(parts[0]), int(parts[1]), int(parts[2])

        # Simple age calculation (days since 2026-03-14)
        # This is approximate but good enough without datetime
        ref_days = 2026 * 365 + 3 * 30 + 14
        file_days = year * 365 + month * 30 + day
        age_days = ref_days - file_days

        if age_days <= 1:
            score = 1.0
        elif age_days <= 7:
            score = 0.9
        elif age_days <= 14:
            score = 0.75
        elif age_days <= 30:
            score = 0.6
        elif age_days <= 90:
            score = 0.4
        else:
            score = 0.2

        detail = f"most recent: {m.most_recent_date} (~{age_days}d ago), {len(m.dates_found)} dates total"
    except (ValueError, IndexError):
        score = 0.3
        detail = "date parse error"

    return score, detail


def score_modularity(
    m: MemoryFileMetrics, all_files: List[MemoryFileMetrics] = None
) -> Tuple[float, str]:
    """Score separation of concerns: topic files, trigger table, index structure."""
    points = 0.0
    max_points = 5.0
    details = []

    file_count = len(all_files) if all_files else 1

    # Satellite file count (2 points)
    if file_count >= 20:
        points += 2.0
    elif file_count >= 10:
        points += 1.5
    elif file_count >= 5:
        points += 1.0
    elif file_count >= 2:
        points += 0.5
    details.append(f"{file_count} files")

    # Trigger table (1 point)
    if m.has_trigger_table:
        points += 1.0
        details.append("trigger table present")
    else:
        details.append("no trigger table")

    # Index sections (1 point)
    if m.has_index_section:
        points += 1.0
        details.append("index sections present")

    # Satellite refs in trigger table (1 point)
    sat_count = len(m.satellite_files)
    if sat_count >= 15:
        points += 1.0
    elif sat_count >= 5:
        points += 0.6
    elif sat_count >= 1:
        points += 0.3
    details.append(f"{sat_count} satellite refs")

    return points / max_points, "; ".join(details)


def score_cross_referencing(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score internal linking: tags, agent refs, file refs, explicit cross-refs."""
    points = 0.0
    max_points = 4.0
    details = []

    # Hashtags (1 point)
    tag_count = len(m.hashtags)
    if tag_count >= 20:
        points += 1.0
    elif tag_count >= 10:
        points += 0.7
    elif tag_count >= 3:
        points += 0.4
    details.append(f"{tag_count} tags")

    # Agent refs (1 point)
    agent_count = len(m.agent_refs)
    if agent_count >= 10:
        points += 1.0
    elif agent_count >= 5:
        points += 0.6
    elif agent_count >= 1:
        points += 0.3
    details.append(f"{agent_count} agent refs")

    # File refs (1 point)
    file_count = len(m.file_refs) + len(m.md_links)
    if file_count >= 15:
        points += 1.0
    elif file_count >= 5:
        points += 0.6
    elif file_count >= 1:
        points += 0.3
    details.append(f"{file_count} file refs")

    # Explicit cross-refs (1 point)
    xref_count = len(m.crossref_lines)
    if xref_count >= 3:
        points += 1.0
    elif xref_count >= 1:
        points += 0.5
    details.append(f"{xref_count} cross-refs")

    return points / max_points, "; ".join(details)


def score_actionability(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score rule specificity: imperative verbs, NEVER/ALWAYS, concrete examples."""
    if m.line_count == 0:
        return 0.0, "empty file"

    points = 0.0
    max_points = 3.0
    details = []

    # Imperative verb density (1 point)
    imp_density = m.imperative_count / max(m.line_count, 1)
    if imp_density >= 0.3:
        points += 1.0
    elif imp_density >= 0.15:
        points += 0.7
    elif imp_density >= 0.05:
        points += 0.4
    details.append(f"{m.imperative_count} imperatives")

    # Strong directives: NEVER/ALWAYS/MUST (1 point)
    if m.never_always_count >= 10:
        points += 1.0
    elif m.never_always_count >= 5:
        points += 0.7
    elif m.never_always_count >= 1:
        points += 0.3
    details.append(f"{m.never_always_count} NEVER/ALWAYS/MUST")

    # Code examples alongside rules (1 point)
    if m.code_block_count >= 3:
        points += 1.0
    elif m.code_block_count >= 1:
        points += 0.5
    details.append(f"{m.code_block_count} code examples")

    return points / max_points, "; ".join(details)


def score_coverage(
    m: MemoryFileMetrics, all_files: List[MemoryFileMetrics] = None
) -> Tuple[float, str]:
    """Score what percentage of the file system's topics have memory coverage."""
    if all_files is None:
        all_files = [m]

    # Count unique topics covered across all files
    all_topics = set()
    for f in all_files:
        # Each file with frontmatter or meaningful content = a topic
        if f.line_count >= 5:
            all_topics.add(f.filename)

    # Compare against satellite refs in index
    indexed = set(m.satellite_files)
    orphans = all_topics - indexed - {m.filename, "MEMORY.md"}

    if not all_topics:
        return 0.0, "no topic files"

    coverage = len(indexed) / max(len(all_topics), 1)
    detail = f"{len(indexed)} indexed, {len(orphans)} orphans, {len(all_topics)} total"

    return min(1.0, coverage), detail


def score_platform_compliance(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score adherence to platform specs: line limits, no secrets, encoding."""
    points = 0.0
    max_points = 3.0
    details = []
    content = "\n".join(m.lines)

    # Line limit compliance (1 point)
    if m.filename == "MEMORY.md":
        limit = MEMORY_MD_LINE_LIMIT
    elif m.filename == "CLAUDE.md":
        from .constants import CLAUDE_MD_LINE_LIMIT
        limit = CLAUDE_MD_LINE_LIMIT
    else:
        limit = TOPIC_FILE_LINE_LIMIT

    if m.line_count <= limit:
        points += 1.0
        details.append(f"{m.line_count}/{limit} lines")
    else:
        over = m.line_count - limit
        penalty = min(1.0, over / limit)
        points += max(0, 1.0 - penalty)
        details.append(f"{m.line_count}/{limit} lines (OVER by {over})")

    # Secret scan (1 point: no secrets found)
    secret_hits = 0
    for pattern in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        # Filter out common false positives
        for match in matches:
            if len(match) > 20 and not match.startswith("http"):
                secret_hits += 1

    if secret_hits == 0:
        points += 1.0
        details.append("no secrets detected")
    else:
        details.append(f"WARNING: {secret_hits} potential secrets")

    # UTF-8 + no binary (1 point)
    try:
        content.encode("utf-8")
        points += 1.0
        details.append("clean UTF-8")
    except UnicodeEncodeError:
        details.append("encoding issues")

    return points / max_points, "; ".join(details)


def score_meta_awareness(m: MemoryFileMetrics) -> Tuple[float, str]:
    """Score self-awareness: versioning, audit references, hook enforcement."""
    content = "\n".join(m.lines).lower()
    points = 0.0
    max_points = 4.0
    details = []

    # Count meta keywords present
    meta_hits = sum(1 for kw in META_KEYWORDS if kw in content)

    if meta_hits >= 8:
        points += 2.0
    elif meta_hits >= 4:
        points += 1.0
    elif meta_hits >= 2:
        points += 0.5
    details.append(f"{meta_hits} meta keywords")

    # Self-referential rules (1 point: file knows its own limits)
    if "200" in content or "line limit" in content or "truncat" in content:
        points += 1.0
        details.append("knows line limit")

    # Hook/automation references (1 point)
    if "hook" in content or "timer" in content or "cron" in content:
        points += 1.0
        details.append("automation aware")

    return points / max_points, "; ".join(details)
