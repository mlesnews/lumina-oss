#!/usr/bin/env python3
"""
Jedi Librarian System (@JOCOSTA-NU)
Manages the organization of the Holocron Archive using the Dewey Decimal System.
Synchronizes local @holocrons with the NAS Jupyter server.

Tags: #LIBRARIAN #HOLOCRON #DEWEY #NAS #JUPYTER @JOCOSTA-NU
"""

import sys
import json
import os
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_storage_engineering_team import StorageEngineeringTeam
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    StorageEngineeringTeam = None

logger = get_logger("JediLibrarian")

class JediLibrarian:
    """
    Head Jedi Librarian @JOCOSTA-NU
    Organizes everything from Markdown/JSON to Jupyter Notebooks.
    """

    DEWEY_MAP = {
        "computer_science": "000",
        "philosophy": "100",
        "social_sciences": "300",
        "technology": "600",
        "history_docuseries": "900"
    }

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.holocron_dir = self.project_root / "data" / "holocron"
        self.notebooks_dir = self.holocron_dir / "notebooks"
        self.chapters_dir = self.holocron_dir / "chapters"
        self.index_file = self.holocron_dir / "HOLOCRON_INDEX.json"

        # Ensure directories exist
        self.notebooks_dir.mkdir(parents=True, exist_ok=True)
        self.chapters_dir.mkdir(parents=True, exist_ok=True)

        # Initialize storage team for NAS sync
        if StorageEngineeringTeam:
            self.storage_team = StorageEngineeringTeam(self.project_root)
        else:
            self.storage_team = None

        self.logger.info("🏛️  Jedi Librarian @JOCOSTA-NU initialized")

    def classify_artifact(self, category: str, sub_category: str) -> str:
        """Generate a Dewey Decimal classification code"""
        base = self.DEWEY_MAP.get(category, "000")
        return f"Δ-{base}.{sub_category}"

    def catalog_notebook(self, nb_path: Path, metadata: Dict[str, Any]):
        try:
            """Catalog a Jupyter notebook into the librarian system"""
            # Example classification: Δ-600.1 (Technology/Infrastructure)
            classification = metadata.get("classification", "Δ-000.0")

            # Update HOLOCRON_INDEX.json
            if self.index_file.exists():
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"entries": {}}

            entry_id = f"NB-{nb_path.stem}"
            index["entries"][entry_id] = {
                "title": metadata.get("title", nb_path.name),
                "location": str(nb_path.relative_to(self.project_root)),
                "classification": classification,
                "tags": metadata.get("tags", []),
                "last_updated": datetime.now().isoformat(),
                "chapter_id": metadata.get("chapter_id")
            }

            with open(self.index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)

            self.logger.info(f"📚 Cataloged: {nb_path.name} as {classification}")

        except Exception as e:
            self.logger.error(f"Error in catalog_notebook: {e}", exc_info=True)
            raise
    def sync_to_nas_jupyter(self):
        """Sync all local notebooks to the NAS Jupyter server directory"""
        if not self.storage_team:
            self.logger.error("❌ Storage Engineering Team not available for NAS sync")
            return

        self.logger.info("🔄 Syncing @holocrons to NAS Jupyter server...")

        # NAS target directory for Jupyter
        nas_jupyter_path = "/volume1/homes/mlesn/jupyter_notebooks/holocron"

        # Use storage team to transfer
        for nb in self.notebooks_dir.glob("*.ipynb"):
            result = self.storage_team.transfer_file_to_nas(nb, f"jupyter_notebooks/holocron/{nb.name}")
            if result.get("success"):
                self.logger.info(f"   ✅ Synced: {nb.name}")
            else:
                self.logger.warning(f"   ⚠️  Failed to sync: {nb.name} - {result.get('error')}")

    def create_chapter_from_holocron(self, holocron_id: str):
        """Group a set of holocrons into a numbered #chapter for the docuseries"""
        # Logic to map holocron(s) to a chapter number
        # Chapter 1: Inception
        # Chapter 2: Infrastructure...
        pass

    def generate_docuseries_manifest(self) -> Dict[str, Any]:
        """Generate a manifest for the YouTube Docuseries playlist"""
        # This links #chapters to @holocrons to potential YouTube video IDs
        manifest = {
            "series_title": "LUMINA: The AI Evolution Docuseries",
            "chapters": []
        }
        # Populate from index
        return manifest

if __name__ == "__main__":
    librarian = JediLibrarian()
    # librarian.sync_to_nas_jupyter() # Run this to sync
