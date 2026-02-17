#!/usr/bin/env python3
"""
Jedi Archives Organizer (@JOCOSTA-NU)
Re-organizes all Holocron artifacts (Markdown, JSON, Notebooks) into a Dewey Decimal structure.
Maintains the "Card Catalog" in HOLOCRON_INDEX.json.

Tags: #ARCHIVES #ORGANIZATION #DEWEY @JOCOSTA-NU
"""

import sys
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jedi_librarian_system import JediLibrarian
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    JediLibrarian = None

logger = get_logger("JediArchives")

class JediArchivesOrganizer:
    """
    Implements the organizational vision of @JOCOSTA-NU.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.holocron_root = self.project_root / "data" / "holocron"
        self.intel_root = self.project_root / "data" / "intelligence"

        # Librarian for classification
        self.librarian = JediLibrarian(self.project_root)

        # Dewey Folders
        self.archives_dir = self.holocron_root / "archives"
        self.folders = {
            "000": self.archives_dir / "000_Information_Systems",
            "600": self.archives_dir / "600_Technology_and_Architecture",
            "900": self.archives_dir / "900_History_and_Docuseries"
        }

        for folder in self.folders.values():
            folder.mkdir(parents=True, exist_ok=True)

    def organize_system(self):
        """Move files into their designated Dewey folders and update the catalog"""
        self.logger.info("🏛️  Starting Jedi Archives re-organization...")

        catalog_updates = []

        # 1. Organize Information Systems (000)
        info_targets = [
            "LUMINA_ALL_ASKS_ORDERED.json",
            "LUMINA_ALL_ASKS_ORDERED_INDEX.json",
            "LUMINA_ASKS_SUMMARY.md",
            "MANUS_IMPROVEMENTS_ASK_STACK_REPORT.json"
        ]
        for target in info_targets:
            self._move_and_catalog(self.intel_root / target, "computer_science", "1", catalog_updates)

        # 2. Organize Technology (600)
        tech_targets = [
            "master_blueprint_anthropic_comparison_20251229_190126.json",
            "MASTER_BLUEPRINT_ANTHROPIC_RESIPHON_ANALYSIS.md",
            "VIDEO_AUDIO_TRANSCRIPTION_SYSTEM.md"
        ]
        for target in tech_targets:
            self._move_and_catalog(self.intel_root / target, "technology", "5", catalog_updates)

        # 3. Organize History (900)
        history_targets = [
            "LUMINA_SEQUENTIAL_STORYTELLING.md",
            "LUMINA_SEQUENTIAL_STORYTELLING_INDEX.json",
            "LUMINA_FINAL_SEQUENTIAL_STORYTELLING.md",
            "LUMINA_ENHANCED_STORYTELLING.md"
        ]
        for target in history_targets:
            self._move_and_catalog(self.intel_root / target, "history_docuseries", "1", catalog_updates)

        # Finalize Catalog
        self.logger.info(f"✅ Re-organization complete. {len(catalog_updates)} items moved.")

    def _move_and_catalog(self, source_path: Path, category: str, sub: str, updates: List):
        try:
            """Helper to move and catalog an item"""
            if not source_path.exists():
                return

            dewey = self.librarian.classify_artifact(category, sub)
            base_folder = dewey.split("-")[1].split(".")[0]
            dest_folder = self.folders.get(base_folder)

            if dest_folder:
                dest_path = dest_folder / source_path.name
                # Copy instead of move for now to maintain stability
                shutil.copy2(source_path, dest_path)

                # Catalog entry
                metadata = {
                    "title": source_path.stem.replace("_", " ").title(),
                    "classification": dewey,
                    "tags": [category, "archive"]
                }
                self.librarian.catalog_notebook(dest_path, metadata)
                updates.append(dest_path)

        except Exception as e:
            self.logger.error(f"Error in _move_and_catalog: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    organizer = JediArchivesOrganizer()
    organizer.organize_system()
