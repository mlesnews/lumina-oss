#!/usr/bin/env python3
"""
Save JARVIS Layout - Save notebook/workplace state for JARVIS

Saves the current state of notebooks, workspace layouts, and configurations
as a "JARVIS layout" that can be restored or referenced by JARVIS systems.

Tags: #JARVIS #LAYOUT #NOTEBOOK #WORKSPACE @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_logger import get_logger

logger = get_logger("SaveJarvisLayout")


class JarvisLayoutSaver:
    """Save workspace/notebook state as JARVIS layout"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize layout saver"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.jarvis_dir = self.data_dir / "jarvis"
        self.layouts_dir = self.jarvis_dir / "layouts"
        self.layouts_dir.mkdir(parents=True, exist_ok=True)

        logger.info("💾 JARVIS Layout Saver initialized")

    def save_notebook_layout(self, notebook_path: Path, layout_name: str = "jarvis") -> Path:
        try:
            """Save notebook as JARVIS layout"""
            logger.info(f"📓 Saving notebook layout: {notebook_path.name}")

            if not notebook_path.exists():
                raise FileNotFoundError(f"Notebook not found: {notebook_path}")

            # Read notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)

            # Create layout metadata
            layout_metadata = {
                "layout_id": f"jarvis_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "layout_name": layout_name,
                "source_notebook": str(notebook_path.relative_to(self.project_root)),
                "saved_at": datetime.now().isoformat(),
                "saved_by": "JARVIS",
                "version": "1.0.0",
                "notebook_metadata": {
                    "nbformat": notebook_data.get("nbformat"),
                    "nbformat_minor": notebook_data.get("nbformat_minor"),
                    "cells_count": len(notebook_data.get("cells", [])),
                    "language": self._detect_notebook_language(notebook_data)
                }
            }

            # Create layout structure
            layout_data = {
                "metadata": layout_metadata,
                "notebook": notebook_data,
                "layout_config": {
                    "name": layout_name,
                    "type": "jupyter_notebook",
                    "restore_cells": True,
                    "restore_outputs": True,
                    "restore_execution_state": False  # Don't restore execution state for safety
                }
            }

            # Save layout
            layout_file = self.layouts_dir / f"{layout_name}_layout_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(layout_file, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Layout saved: {layout_file.name}")

            # Also save as latest
            latest_file = self.layouts_dir / f"{layout_name}_layout_latest.json"
            with open(latest_file, 'w', encoding='utf-8') as f:
                json.dump(layout_data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Latest layout saved: {latest_file.name}")

            return layout_file

        except Exception as e:
            self.logger.error(f"Error in save_notebook_layout: {e}", exc_info=True)
            raise
    def _detect_notebook_language(self, notebook_data: Dict[str, Any]) -> str:
        """Detect primary language from notebook cells"""
        languages = {}
        for cell in notebook_data.get("cells", []):
            cell_type = cell.get("cell_type", "")
            if cell_type == "code":
                lang = cell.get("metadata", {}).get("language", "python")
                languages[lang] = languages.get(lang, 0) + 1

        if languages:
            return max(languages.items(), key=lambda x: x[1])[0]
        return "python"

    def list_saved_layouts(self) -> List[Dict[str, Any]]:
        """List all saved JARVIS layouts"""
        layouts = []

        for layout_file in self.layouts_dir.glob("*_layout_*.json"):
            try:
                with open(layout_file, 'r', encoding='utf-8') as f:
                    layout_data = json.load(f)
                    layouts.append({
                        "file": layout_file.name,
                        "layout_name": layout_data.get("metadata", {}).get("layout_name", "unknown"),
                        "saved_at": layout_data.get("metadata", {}).get("saved_at", ""),
                        "source_notebook": layout_data.get("metadata", {}).get("source_notebook", ""),
                        "cells_count": layout_data.get("metadata", {}).get("notebook_metadata", {}).get("cells_count", 0)
                    })
            except Exception as e:
                logger.warning(f"Error reading layout {layout_file.name}: {e}")

        return sorted(layouts, key=lambda x: x.get("saved_at", ""), reverse=True)

    def load_layout(self, layout_name: str = "jarvis", use_latest: bool = True) -> Optional[Dict[str, Any]]:
        try:
            """Load a saved JARVIS layout"""
            if use_latest:
                layout_file = self.layouts_dir / f"{layout_name}_layout_latest.json"
            else:
                # Find most recent
                layouts = [f for f in self.layouts_dir.glob(f"{layout_name}_layout_*.json") 
                          if "latest" not in f.name]
                if not layouts:
                    return None
                layout_file = max(layouts, key=lambda f: f.stat().st_mtime)

            if not layout_file.exists():
                logger.warning(f"Layout not found: {layout_file}")
                return None

            with open(layout_file, 'r', encoding='utf-8') as f:
                return json.load(f)


        except Exception as e:
            self.logger.error(f"Error in load_layout: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Save JARVIS Layout")
        parser.add_argument('--notebook', type=str, help='Path to notebook file')
        parser.add_argument('--name', type=str, default='jarvis', help='Layout name (default: jarvis)')
        parser.add_argument('--list', action='store_true', help='List saved layouts')
        parser.add_argument('--load', type=str, help='Load layout by name')

        args = parser.parse_args()

        saver = JarvisLayoutSaver()

        if args.list:
            print("\n📋 SAVED JARVIS LAYOUTS:")
            print("=" * 80)
            layouts = saver.list_saved_layouts()
            for layout in layouts:
                print(f"   {layout['layout_name']}: {layout['file']}")
                print(f"      Saved: {layout['saved_at']}")
                print(f"      Source: {layout['source_notebook']}")
                print(f"      Cells: {layout['cells_count']}")
                print()

        elif args.load:
            layout = saver.load_layout(args.load)
            if layout:
                print(f"✅ Loaded layout: {args.load}")
                print(f"   Source: {layout['metadata']['source_notebook']}")
                print(f"   Cells: {layout['metadata']['notebook_metadata']['cells_count']}")
            else:
                print(f"❌ Layout not found: {args.load}")

        elif args.notebook:
            notebook_path = Path(args.notebook)
            if not notebook_path.is_absolute():
                notebook_path = Path.cwd() / notebook_path

            layout_file = saver.save_notebook_layout(notebook_path, args.name)
            print(f"\n✅ JARVIS Layout saved!")
            print(f"   Layout: {layout_file.name}")
            print(f"   Location: {layout_file}")
            print(f"   Latest: {args.name}_layout_latest.json")

        else:
            # Default: save current notebook if in Jupyter
            print("💾 JARVIS Layout Saver")
            print("\nUsage:")
            print("  --notebook PATH    Save notebook as JARVIS layout")
            print("  --name NAME        Layout name (default: jarvis)")
            print("  --list             List all saved layouts")
            print("  --load NAME        Load a saved layout")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()