#!/usr/bin/env python3
"""
LUMINA Docuseries Manager
Orchestrates the creation of #chapters from @holocrons and links them to YouTube docuseries playlist.
Maintains the Jedi Archives Librarian system / Dewey Decimal organization.

Tags: #DOCUSERIES #CHAPTERS #YOUTUBE #LIBRARIAN @JOCOSTA-NU
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

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

logger = get_logger("LuminaDocuseries")

class LuminaDocuseriesManager:
    """
    Manages the transition from Holocrons to Docuseries Chapters.
    Organized by @JOCOSTA-NU protocols.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.holocron_dir = self.project_root / "data" / "holocron"
        self.docuseries_dir = self.holocron_dir / "docuseries"
        self.docuseries_dir.mkdir(parents=True, exist_ok=True)
        self.manifest_file = self.docuseries_dir / "docuseries_manifest.json"

        self.librarian = JediLibrarian(self.project_root) if JediLibrarian else None

        self.logger.info("🎬 LUMINA Docuseries Manager initialized")

    def generate_chapters_from_asks(self, asks_file: Path):
        try:
            """
            Groups the entire history of @asks into logical #chapters.
            Each chapter becomes a potential @holocron/video.
            """
            if not asks_file.exists():
                self.logger.error(f"❌ Asks file not found: {asks_file}")
                return

            with open(asks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            asks = data.get("asks", [])
            self.logger.info(f"📚 Analyzing {len(asks)} asks for chapter division...")

            # Logic: Group by 100 asks per chapter
            chapters = {}
            chapter_size = 100

            for i, ask in enumerate(asks):
                chapter_num = (i // chapter_size) + 1
                if chapter_num not in chapters:
                    chapters[chapter_num] = {
                        "chapter_id": f"CH-{chapter_num:03d}",
                        "title": f"Chapter {chapter_num}: AI Evolution Phase {chapter_num}",
                        "timestamp_start": ask.get('timestamp', 'Inception'),
                        "asks_count": 0,
                        "holocron_ids": [],
                        "youtube_metadata": {
                            "video_title": f"LUMINA Docuseries | Chapter {chapter_num}: Evolution",
                            "description": f"Detailed walkthrough of the AI development journey for Chapter {chapter_num}.",
                            "tags": ["Lumina", "AI", "Docuseries", f"Chapter_{chapter_num}"]
                        },
                        "dewey_classification": self.librarian.classify_artifact("history_docuseries", str(chapter_num)) if self.librarian else None
                    }
                chapters[chapter_num]["asks_count"] += 1

            # Save manifest
            manifest = {
                "series_name": "LUMINA: The AI Evolution",
                "total_chapters": len(chapters),
                "last_updated": datetime.now().isoformat(),
                "chapters": chapters
            }

            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2)

            self.logger.info(f"✅ Generated {len(chapters)} chapters in manifest.")

        except Exception as e:
            self.logger.error(f"Error in generate_chapters_from_asks: {e}", exc_info=True)
            raise
    def sync_docuseries_to_nas(self):
        """Sync the manifest and related metadata to the NAS"""
        if self.librarian:
            self.logger.info("🔄 Syncing docuseries manifest to NAS...")
            # Use librarian's storage team if available
            if self.librarian.storage_team:
                self.librarian.storage_team.transfer_file_to_nas(self.manifest_file, f"holocron/docuseries/{self.manifest_file.name}")

if __name__ == "__main__":
    manager = LuminaDocuseriesManager()
    project_root = Path(__file__).parent.parent.parent
    asks_file = project_root / "data" / "intelligence" / "LUMINA_ALL_ASKS_ORDERED.json"
    manager.generate_chapters_from_asks(asks_file)
    manager.sync_docuseries_to_nas()
