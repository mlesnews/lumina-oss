"""
Context matrix — multi-source knowledge aggregation (R5 pattern).

Ingests context from multiple sources (sessions, documents, events),
extracts patterns, and provides a queryable knowledge store.

Pattern extracted from production: r5_living_context_matrix.py

Example:
    matrix = ContextMatrix()
    matrix.ingest("session_1", {"role": "user", "content": "Deploy failed"})
    matrix.ingest("session_1", {"role": "system", "content": "OOM in worker"})
    matrix.ingest("session_2", {"role": "user", "content": "Deploy failed again"})

    patterns = matrix.extract_patterns()
    print(f"Found {len(patterns)} patterns")

    results = matrix.query("deploy failure")
    for r in results:
        print(f"  [{r['score']:.2f}] {r['content'][:80]}")
"""

import logging
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set

logger = logging.getLogger(__name__)


@dataclass
class ContextEntry:
    """A single piece of context from a source."""
    source_id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: float = field(default_factory=time.time)
    tags: Set[str] = field(default_factory=set)


@dataclass
class Pattern:
    """A recurring pattern extracted from context entries."""
    pattern_id: str
    description: str
    frequency: int
    sources: List[str]
    first_seen: float
    last_seen: float
    metadata: Dict[str, Any] = field(default_factory=dict)


class ContextMatrix:
    """
    Multi-source knowledge aggregation engine.

    Ingests context entries, detects recurring patterns via keyword
    co-occurrence, and provides keyword-based querying.

    Args:
        max_entries: Maximum entries to retain (FIFO eviction).
    """

    def __init__(self, max_entries: int = 10000):
        self._entries: List[ContextEntry] = []
        self._max_entries = max_entries
        self._patterns: Dict[str, Pattern] = {}
        self._sources: Dict[str, List[int]] = defaultdict(list)

    def ingest(
        self,
        source_id: str,
        message: Dict[str, str],
        tags: Optional[Set[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Ingest a context entry from a source.

        Args:
            source_id: Identifier for the source (session, document, etc.).
            message: Dict with at least 'content' key.
            tags: Optional tags for categorization.
            metadata: Optional metadata dict.

        Returns:
            Index of the stored entry.
        """
        content = message.get("content", "")
        if not content:
            return -1

        entry = ContextEntry(
            source_id=source_id,
            content=content,
            metadata=metadata or {},
            tags=tags or set(),
        )

        idx = len(self._entries)
        self._entries.append(entry)
        self._sources[source_id].append(idx)

        # Evict oldest if over capacity
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries:]
            # Rebuild source index
            self._sources.clear()
            for i, e in enumerate(self._entries):
                self._sources[e.source_id].append(i)

        return idx

    def query(
        self,
        keywords: str,
        limit: int = 10,
        source_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Search entries by keyword overlap.

        Args:
            keywords: Space-separated search terms.
            limit: Max results to return.
            source_id: Optional filter by source.

        Returns:
            List of result dicts sorted by relevance score.
        """
        search_words = set(keywords.lower().split())
        if not search_words:
            return []

        results = []
        entries = self._entries
        if source_id:
            indices = self._sources.get(source_id, [])
            entries = [self._entries[i] for i in indices if i < len(self._entries)]

        for entry in entries:
            content_words = set(entry.content.lower().split())
            overlap = search_words & content_words
            if overlap:
                score = len(overlap) / len(search_words)
                results.append({
                    "source_id": entry.source_id,
                    "content": entry.content,
                    "score": score,
                    "timestamp": entry.timestamp,
                    "tags": list(entry.tags),
                })

        results.sort(key=lambda r: r["score"], reverse=True)
        return results[:limit]

    def extract_patterns(self, min_frequency: int = 2) -> List[Pattern]:
        """
        Extract recurring patterns from ingested context.

        Uses keyword co-occurrence across sources to identify patterns.

        Args:
            min_frequency: Minimum occurrences to qualify as a pattern.

        Returns:
            List of Pattern objects.
        """
        # Build keyword-to-sources mapping
        keyword_sources: Dict[str, Set[str]] = defaultdict(set)
        keyword_timestamps: Dict[str, List[float]] = defaultdict(list)

        for entry in self._entries:
            words = set(entry.content.lower().split())
            # Filter to meaningful words (3+ chars)
            words = {w for w in words if len(w) >= 3}
            for word in words:
                keyword_sources[word].add(entry.source_id)
                keyword_timestamps[word].append(entry.timestamp)

        patterns = []
        for keyword, sources in keyword_sources.items():
            freq = len(sources)
            if freq >= min_frequency:
                timestamps = keyword_timestamps[keyword]
                pattern = Pattern(
                    pattern_id=f"p_{keyword}",
                    description=f"Keyword '{keyword}' appears across {freq} sources",
                    frequency=freq,
                    sources=list(sources),
                    first_seen=min(timestamps),
                    last_seen=max(timestamps),
                )
                patterns.append(pattern)

        patterns.sort(key=lambda p: p.frequency, reverse=True)
        self._patterns = {p.pattern_id: p for p in patterns}
        return patterns

    @property
    def stats(self) -> Dict[str, Any]:
        """Return matrix statistics."""
        return {
            "total_entries": len(self._entries),
            "unique_sources": len(self._sources),
            "patterns_extracted": len(self._patterns),
            "capacity": f"{len(self._entries)}/{self._max_entries}",
        }
