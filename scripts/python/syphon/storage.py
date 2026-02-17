#!/usr/bin/env python3
"""
SYPHON Storage

Storage backend for SYPHON extracted data.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, TYPE_CHECKING

from syphon.models import SyphonData
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

if TYPE_CHECKING:
    from syphon.core import SYPHONConfig

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SyphonStorage:
    """Storage backend for SYPHON data with NAS proxy-cache support"""

    def __init__(self, config: "SYPHONConfig", cache: Optional[Any] = None) -> None:
        """
        Initialize storage.

        Args:
            config: SYPHON configuration
            cache: Optional NAS proxy-cache instance
        """
        self.config = config
        self.cache = cache
        self.logger = get_logger("SyphonStorage")
        self.extracted_data_file = config.data_dir / "extracted_data.json"
        self.extracted_data: List[SyphonData] = []

        # Load existing data
        self._load()

    def _load(self) -> None:
        """Load existing extracted data (with cache support)"""
        cache_key = f"syphon_storage_{self.extracted_data_file.stat().st_mtime if self.extracted_data_file.exists() else 0}"

        # Try cache first
        if self.cache:
            try:
                cached_data = self.cache.get(cache_key)
                if cached_data is not None:
                    self.extracted_data = cached_data
                    self.logger.debug("Loaded syphon data from cache")
                    return
            except Exception as e:
                self.logger.debug(f"Cache load failed: {e}")

        # Load from file
        if self.extracted_data_file.exists():
            try:
                with open(self.extracted_data_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.extracted_data = [SyphonData.from_dict(item) for item in data]

                # Cache the loaded data
                if self.cache:
                    try:
                        self.cache.put(
                            cache_key,
                            self.extracted_data,
                            physics_domain="syphon",
                            ttl_seconds=3600,  # 1 hour
                            metadata={"file": str(self.extracted_data_file)}
                        )
                    except Exception:
                        pass

                self.logger.info(f"Loaded {len(self.extracted_data)} syphon items")
            except Exception as e:
                self.logger.error(f"Error loading syphon data: {e}")
                self.extracted_data = []

    def save(self, data: SyphonData) -> None:
        """
        Save extracted data (with cache support).

        Args:
            data: SyphonData to save
        """
        try:
            # Check if already exists
            existing = next((d for d in self.extracted_data if d.data_id == data.data_id), None)
            if existing:
                # Update existing
                index = self.extracted_data.index(existing)
                self.extracted_data[index] = data
            else:
                # Add new
                self.extracted_data.append(data)

            # Cache individual data item
            if self.cache:
                try:
                    cache_key = f"syphon_data_{data.data_id}"
                    self.cache.put(
                        cache_key,
                        data,
                        physics_domain="syphon",
                        ttl_seconds=7200,  # 2 hours
                        metadata={"data_id": data.data_id, "source_type": data.source_type.value if hasattr(data.source_type, 'value') else str(data.source_type)}
                    )
                except Exception as e:
                    self.logger.debug(f"Cache save failed: {e}")

            # Save to file
            self._persist()
            self.logger.debug(f"Saved syphon data: {data.data_id}")

        except Exception as e:
            self.logger.error(f"Error saving syphon data: {e}")

    def _persist(self) -> None:
        """Persist data to storage"""
        try:
            data = [item.to_dict() for item in self.extracted_data]
            with open(self.extracted_data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.logger.error(f"Error persisting syphon data: {e}")

    def get(self, data_id: str) -> Optional[SyphonData]:
        """Get data by ID"""
        return next((d for d in self.extracted_data if d.data_id == data_id), None)

    def get_all(self, source_type: Optional[str] = None) -> List[SyphonData]:
        """Get all data, optionally filtered by source type"""
        if source_type:
            return [d for d in self.extracted_data if d.source_type.value == source_type]
        return self.extracted_data.copy()

    def close(self) -> None:
        """Close storage and persist data"""
        self._persist()
        self.logger.info("Storage closed")

