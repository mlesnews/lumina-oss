"""
JSON-backed pattern storage with efficacy scores.

A lightweight pattern database that stores named patterns with metadata,
tracks their usage/efficacy, and persists to a JSON file.

Pattern extracted from production: data/wopr/pattern_database.json

Example:
    db = PatternDB(path=Path("patterns.json"))
    db.store("retry_backoff", {
        "description": "Exponential backoff on API failures",
        "category": "resilience",
        "max_retries": 3,
    })
    db.record_usage("retry_backoff", success=True)

    pattern = db.get("retry_backoff")
    print(f"Efficacy: {pattern['efficacy']:.0%}")
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class PatternDB:
    """
    JSON-backed pattern storage with usage tracking.

    Args:
        path: File path for persistence. If None, operates in-memory only.
    """

    def __init__(self, path: Optional[Path] = None):
        self._path = path
        self._patterns: Dict[str, Dict[str, Any]] = {}
        if path and path.exists():
            self._load()

    def store(
        self,
        name: str,
        data: Dict[str, Any],
        overwrite: bool = False,
    ) -> bool:
        """
        Store a named pattern.

        Args:
            name: Pattern identifier.
            data: Pattern data (arbitrary dict).
            overwrite: If True, replace existing pattern.

        Returns:
            True if stored, False if exists and overwrite=False.
        """
        if name in self._patterns and not overwrite:
            return False

        self._patterns[name] = {
            **data,
            "_name": name,
            "_created": time.time(),
            "_updated": time.time(),
            "_usage_count": 0,
            "_success_count": 0,
            "_efficacy": 0.0,
        }
        self._save()
        return True

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a pattern by name. Returns None if not found."""
        pattern = self._patterns.get(name)
        if pattern:
            return {
                k: v for k, v in pattern.items()
                if not k.startswith("_") or k in ("_efficacy", "_usage_count", "_name")
            }
        return None

    def record_usage(self, name: str, success: bool = True) -> None:
        """
        Record a usage of a pattern and update efficacy.

        Args:
            name: Pattern name.
            success: Whether the usage was successful.
        """
        pattern = self._patterns.get(name)
        if not pattern:
            return

        pattern["_usage_count"] += 1
        if success:
            pattern["_success_count"] += 1

        pattern["_efficacy"] = (
            pattern["_success_count"] / pattern["_usage_count"]
        )
        pattern["_updated"] = time.time()
        self._save()

    def search(self, keyword: str) -> List[Dict[str, Any]]:
        """Search patterns by keyword in name or description."""
        keyword = keyword.lower()
        results = []
        for name, data in self._patterns.items():
            desc = str(data.get("description", "")).lower()
            if keyword in name.lower() or keyword in desc:
                results.append(self.get(name))
        return [r for r in results if r is not None]

    def top_patterns(self, n: int = 10) -> List[Dict[str, Any]]:
        """Return top N patterns by efficacy (minimum 1 usage)."""
        candidates = [
            p for p in self._patterns.values()
            if p["_usage_count"] > 0
        ]
        candidates.sort(key=lambda p: p["_efficacy"], reverse=True)
        return [self.get(p["_name"]) for p in candidates[:n]]

    def list_all(self) -> List[str]:
        """Return all pattern names."""
        return list(self._patterns.keys())

    def delete(self, name: str) -> bool:
        """Delete a pattern. Returns True if it existed."""
        if name in self._patterns:
            del self._patterns[name]
            self._save()
            return True
        return False

    def _save(self) -> None:
        if not self._path:
            return
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            self._path.write_text(json.dumps(self._patterns, indent=2, default=str))
        except OSError as exc:
            logger.warning("Failed to save pattern DB: %s", exc)

    def _load(self) -> None:
        if not self._path or not self._path.exists():
            return
        try:
            self._patterns = json.loads(self._path.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            logger.warning("Failed to load pattern DB: %s", exc)
            self._patterns = {}
