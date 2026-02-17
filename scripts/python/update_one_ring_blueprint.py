#!/usr/bin/env python3
"""
Update One Ring Blueprint - Living Document Manager
Automatically updates the One Ring Master Blueprint as a living document
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("update_one_ring_blueprint")


# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class OneRingBlueprintManager:
    """Manage One Ring Blueprint as a living document"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize blueprint manager"""
        if project_root is None:
            self.project_root = Path("D:/Dropbox/my_projects")
        else:
            self.project_root = Path(project_root)

        self.blueprint_json = self.project_root / "config" / "one_ring_blueprint.json"
        self.blueprint_md = self.project_root / "config" / "one_ring_blueprint.md"

    def load_blueprint(self) -> Dict[str, Any]:
        try:
            """Load current blueprint"""
            if self.blueprint_json.exists():
                with open(self.blueprint_json, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                return self._create_initial_blueprint()

        except Exception as e:
            self.logger.error(f"Error in load_blueprint: {e}", exc_info=True)
            raise
    def _create_initial_blueprint(self) -> Dict[str, Any]:
        """Create initial blueprint structure"""
        return {
            "blueprint_metadata": {
                "title": "The One Ring - Master Blueprint",
                "status": "LIVING DOCUMENT",
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "living_document": True
            }
        }

    def update_system_status(self, system_name: str, status: Dict[str, Any]) -> bool:
        """Update status for a specific system"""
        blueprint = self.load_blueprint()

        if "core_systems" not in blueprint:
            blueprint["core_systems"] = {}

        if system_name not in blueprint["core_systems"]:
            blueprint["core_systems"][system_name] = {}

        blueprint["core_systems"][system_name].update(status)
        blueprint["core_systems"][system_name]["last_updated"] = datetime.now().isoformat()

        return self._save_blueprint(blueprint)

    def update_deployment_status(self, deployment_data: Dict[str, Any]) -> bool:
        """Update deployment status"""
        blueprint = self.load_blueprint()

        if "deployment_status" not in blueprint:
            blueprint["deployment_status"] = {}

        blueprint["deployment_status"].update(deployment_data)
        blueprint["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()

        return self._save_blueprint(blueprint)

    def add_version_history_entry(self, changes: list, updated_by: str = "System") -> bool:
        """Add entry to version history"""
        blueprint = self.load_blueprint()

        if "version_history" not in blueprint:
            blueprint["version_history"] = []

        entry = {
            "date": datetime.now().isoformat(),
            "version": self._increment_version(blueprint),
            "changes": changes,
            "updated_by": updated_by
        }

        blueprint["version_history"].append(entry)
        blueprint["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()
        blueprint["blueprint_metadata"]["version"] = entry["version"]

        return self._save_blueprint(blueprint)

    def _increment_version(self, blueprint: Dict[str, Any]) -> str:
        """Increment version number"""
        current_version = blueprint.get("blueprint_metadata", {}).get("version", "1.0.0")
        parts = current_version.split(".")
        if len(parts) == 3:
            major, minor, patch = parts
            patch = str(int(patch) + 1)
            return f"{major}.{minor}.{patch}"
        return "1.0.1"

    def _save_blueprint(self, blueprint: Dict[str, Any]) -> bool:
        """Save blueprint to file"""
        try:
            # Update metadata
            blueprint["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()

            # Save JSON
            self.blueprint_json.parent.mkdir(parents=True, exist_ok=True)
            with open(self.blueprint_json, 'w', encoding='utf-8') as f:
                json.dump(blueprint, f, indent=2, ensure_ascii=False)

            print(f"[SUCCESS] Blueprint updated: {self.blueprint_json}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to save blueprint: {e}")
            return False

    def sync_with_lumina_status(self) -> bool:
        """Sync blueprint with Lumina deployment status"""
        try:
            deployment_status_file = self.project_root / "data" / "lumina_deployment_status.json"
            if deployment_status_file.exists():
                with open(deployment_status_file, 'r', encoding='utf-8') as f:
                    lumina_status = json.load(f)

                blueprint = self.load_blueprint()

                if "deployment_status" not in blueprint:
                    blueprint["deployment_status"] = {}

                blueprint["deployment_status"]["lumina_jarvis_extension"] = {
                    "status": "deployed_and_activated" if lumina_status.get("test_status") == "all_passing" else "partial",
                    "deployed_at": lumina_status.get("deployed_at", ""),
                    "components_operational": len([c for c in lumina_status.get("components", {}).values() if c.get("status") == "operational"]),
                    "test_status": lumina_status.get("test_status", "unknown")
                }

                blueprint["deployment_status"]["r5_api_server"] = lumina_status.get("components", {}).get("r5_api_server", {})

                blueprint["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()

                return self._save_blueprint(blueprint)
        except Exception as e:
            print(f"[WARNING] Failed to sync with Lumina status: {e}")
            return False

    def sync_with_holocron(self) -> bool:
        """Sync blueprint with Holocron Archive"""
        try:
            holocron_file = self.project_root / "data" / "holocron" / "HOLOCRON_INDEX.json"
            if holocron_file.exists():
                with open(holocron_file, 'r', encoding='utf-8') as f:
                    holocron = json.load(f)

                blueprint = self.load_blueprint()

                if "core_systems" not in blueprint:
                    blueprint["core_systems"] = {}

                blueprint["core_systems"]["holocron_archive"] = {
                    "name": "Holocron Archive - Master Blueprint",
                    "type": "rogue_ai_defense_intelligence",
                    "status": holocron.get("archive_metadata", {}).get("status", "unknown"),
                    "last_updated": holocron.get("last_updated", ""),
                    "location": "data/holocron/",
                    "purpose": holocron.get("archive_metadata", {}).get("purpose", ""),
                    "classification": holocron.get("archive_metadata", {}).get("classification", ""),
                    "core_principle": holocron.get("archive_philosophy", {}).get("core_principle", ""),
                    "defense_philosophy": holocron.get("archive_philosophy", {}).get("defense_philosophy", ""),
                    "mission": holocron.get("archive_philosophy", {}).get("mission", ""),
                    "index_file": "data/holocron/HOLOCRON_INDEX.json",
                    "integration": "Integrated with Lumina | JARVIS Extension"
                }

                blueprint["blueprint_metadata"]["last_updated"] = datetime.now().isoformat()

                return self._save_blueprint(blueprint)
        except Exception as e:
            print(f"[WARNING] Failed to sync with Holocron: {e}")
            return False

    def update_all(self) -> bool:
        """Update blueprint with all current system states"""
        print("Updating One Ring Blueprint...")
        print("=" * 60)

        results = []

        # Sync with Lumina
        print("\n[1] Syncing with Lumina deployment status...")
        results.append(("Lumina Status", self.sync_with_lumina_status()))

        # Sync with Holocron
        print("\n[2] Syncing with Holocron Archive...")
        results.append(("Holocron Archive", self.sync_with_holocron()))

        # Summary
        print("\n" + "=" * 60)
        print("Update Summary")
        print("=" * 60)

        for name, success in results:
            status = "[SUCCESS]" if success else "[FAILED]"
            print(f"{status} {name}")

        all_success = all(r[1] for r in results)

        if all_success:
            print("\n[SUCCESS] One Ring Blueprint updated successfully!")
        else:
            print("\n[WARNING] Some updates failed. Check errors above.")

        return all_success


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Update One Ring Blueprint")
        parser.add_argument(
            "--project-root",
            type=str,
            default=None,
            help="Project root directory"
        )
        parser.add_argument(
            "--sync-all",
            action="store_true",
            help="Sync with all systems"
        )

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        manager = OneRingBlueprintManager(project_root)

        if args.sync_all:
            success = manager.update_all()
        else:
            # Default: update all
            success = manager.update_all()

        sys.exit(0 if success else 1)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()