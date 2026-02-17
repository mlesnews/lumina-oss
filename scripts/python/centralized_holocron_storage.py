#!/usr/bin/env python3
"""
Centralized Holocron Storage - NAS/Network Storage Integration

All holocrons use centralized storage (NAS) to:
- Preserve local disk space on each host
- Enable shared access across all Lumina instances
- Group like information with like
- Avoid creating thousands of local holocrons

Tags: #HOLOCRON #CENTRALIZED_STORAGE #NAS #NETWORK_STORAGE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CentralizedHolocronStorage")


class CentralizedHolocronStorage:
    """
    Centralized Holocron Storage Manager

    Uses NAS/network storage for all holocrons to:
    - Preserve local disk space
    - Enable shared access
    - Group related information
    - Avoid local holocrons
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Load NAS config
        self.nas_config = self._load_nas_config()

        # Determine storage path (NAS if available, otherwise project root)
        self.storage_base = self._get_storage_base()

        # Holocron base path
        self.holocron_base = self.storage_base / "data" / "holocron"
        self.holocron_base.mkdir(parents=True, exist_ok=True)

        logger.info("=" * 80)
        logger.info("📦 CENTRALIZED HOLOCRON STORAGE")
        logger.info("=" * 80)
        logger.info(f"   Storage Base: {self.storage_base}")
        logger.info(f"   Holocron Base: {self.holocron_base}")
        logger.info(f"   NAS Available: {self.nas_config is not None}")
        logger.info("=" * 80)

    def _load_nas_config(self) -> Optional[Dict[str, Any]]:
        """Load NAS configuration"""
        nas_config_file = self.project_root / "config" / "nas_config.json"
        if nas_config_file.exists():
            try:
                with open(nas_config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"⚠️  Could not load NAS config: {e}")
        return None

    def _get_storage_base(self) -> Path:
        """
        Get storage base path

        Priority:
        1. NAS mount point (if configured and available)
        2. Project root (fallback)
        """
        if self.nas_config:
            # Try NAS mount point using NAS storage utility
            try:
                from nas_storage_utility import NASStorageUtility
                nas_utility = NASStorageUtility(project_root=self.project_root)

                if nas_utility.is_nas_available() and nas_utility.nas_base_path:
                    nas_storage_path = nas_utility.nas_base_path / "holocron"
                    logger.info(f"   ✅ NAS storage available: {nas_storage_path}")
                    return nas_storage_path.parent  # Return base, holocron will be subdirectory
                else:
                    logger.info("   ⚠️  NAS configured but not available - using project root")
            except ImportError:
                logger.debug("   NAS storage utility not available - using project root")
            except Exception as e:
                logger.warning(f"   ⚠️  Error checking NAS availability: {e} - using project root")

        # Use project root as storage base (fallback)
        return self.project_root

    def get_holocron_path(self, category: str, entry_name: str) -> Path:
        """
        Get holocron entry path

        Groups like information with like:
        - category: Groups related entries (e.g., "jedi_training", "workflow_analytics")
        - entry_name: Specific entry name
        """
        category_dir = self.holocron_base / category
        category_dir.mkdir(parents=True, exist_ok=True)

        return category_dir / f"{entry_name}.json"

    def save_holocron_entry(
        self,
        category: str,
        entry_name: str,
        data: Dict[str, Any],
        update_index: bool = True
    ) -> Path:
        """
        Save holocron entry to centralized storage

        Args:
            category: Category to group with (e.g., "jedi_training")
            entry_name: Entry name
            data: Entry data
            update_index: Whether to update HOLOCRON_INDEX.json
        """
        entry_path = self.get_holocron_path(category, entry_name)

        # Add metadata
        entry_data = {
            "entry_id": f"{category}_{entry_name}",
            "category": category,
            "entry_name": entry_name,
            "last_updated": datetime.now().isoformat(),
            "storage_location": str(entry_path.relative_to(self.storage_base)),
            "data": data
        }

        # Save entry
        try:
            with open(entry_path, 'w', encoding='utf-8') as f:
                json.dump(entry_data, f, indent=2, ensure_ascii=False)

            logger.info(f"💾 Saved holocron entry: {category}/{entry_name}")

            # Update index if requested
            if update_index:
                self._update_holocron_index(category, entry_name, entry_path)

            return entry_path

        except Exception as e:
            logger.error(f"❌ Error saving holocron entry: {e}")
            raise

    def load_holocron_entry(self, category: str, entry_name: str) -> Optional[Dict[str, Any]]:
        """Load holocron entry from centralized storage"""
        entry_path = self.get_holocron_path(category, entry_name)

        if not entry_path.exists():
            return None

        try:
            with open(entry_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"❌ Error loading holocron entry: {e}")
            return None

    def _update_holocron_index(self, category: str, entry_name: str, entry_path: Path):
        """Update HOLOCRON_INDEX.json"""
        index_path = self.holocron_base / "HOLOCRON_INDEX.json"

        # Load existing index
        index_data = {}
        if index_path.exists():
            try:
                with open(index_path, 'r', encoding='utf-8') as f:
                    index_data = json.load(f)
            except Exception:
                index_data = {}

        # Ensure entries structure
        if "entries" not in index_data:
            index_data["entries"] = {}
        if category not in index_data["entries"]:
            index_data["entries"][category] = {}

        # Update entry
        entry_id = f"{category}_{entry_name}"
        index_data["entries"][category][entry_name] = {
            "entry_id": entry_id,
            "title": entry_name.replace("_", " ").title(),
            "location": str(entry_path.relative_to(self.storage_base)),
            "category": category,
            "last_updated": datetime.now().isoformat()
        }

        # Update metadata
        index_data["last_updated"] = datetime.now().isoformat()

        # Save index
        try:
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Could not update holocron index: {e}")


def main():
    """Main entry point"""
    storage = CentralizedHolocronStorage()
    print(f"✅ Centralized storage initialized")
    print(f"   Base: {storage.storage_base}")
    print(f"   Holocron: {storage.holocron_base}")


if __name__ == "__main__":


    main()