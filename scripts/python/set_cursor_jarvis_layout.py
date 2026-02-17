#!/usr/bin/env python3
"""
Set Cursor IDE Default Layout to "JARVIS"

Sets the default Cursor IDE layout to the custom "JARVIS" layout.

Tags: #CURSOR_IDE #LAYOUT #JARVIS #QOL #WORKSPACE @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

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

logger = get_logger("CursorJARVISLayout")


class CursorJARVISLayoutSetter:
    """
    Set Cursor IDE Default Layout to JARVIS

    Configures Cursor IDE to use the "JARVIS" layout by default.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize layout setter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_dir = self.project_root / ".cursor"
        self.cursor_dir.mkdir(parents=True, exist_ok=True)

        # Cursor IDE settings files
        self.settings_file = self.cursor_dir / "settings.json"
        self.workspace_file = self.cursor_dir / "workspace.json"
        self.environment_file = self.cursor_dir / "environment.json"

        logger.info("✅ Cursor JARVIS Layout Setter initialized")

    def set_jarvis_layout(self) -> bool:
        """Set JARVIS as the default layout"""
        logger.info("=" * 80)
        logger.info("🎯 SETTING CURSOR IDE LAYOUT TO 'JARVIS'")
        logger.info("=" * 80)

        success = True

        # Method 1: Update workspace.json
        if self.workspace_file.exists():
            try:
                with open(self.workspace_file, 'r') as f:
                    workspace = json.load(f)
            except:
                workspace = {}
        else:
            workspace = {}

        # Set layout in workspace
        if "settings" not in workspace:
            workspace["settings"] = {}

        workspace["settings"]["workbench.view.alwaysShowHeaderActions"] = True
        workspace["settings"]["workbench.panel.defaultLocation"] = "bottom"
        workspace["settings"]["workbench.sideBar.location"] = "left"

        # Set layout name
        workspace["layout"] = "JARVIS"
        workspace["defaultLayout"] = "JARVIS"

        try:
            with open(self.workspace_file, 'w') as f:
                json.dump(workspace, f, indent=2)
            logger.info(f"   ✅ Updated {self.workspace_file}")
        except Exception as e:
            logger.error(f"   ❌ Error updating workspace: {e}")
            success = False

        # Method 2: Update settings.json
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
            except:
                settings = {}
        else:
            settings = {}

        # Set layout-related settings
        settings["workbench.view.alwaysShowHeaderActions"] = True
        settings["workbench.panel.defaultLocation"] = "bottom"
        settings["workbench.sideBar.location"] = "left"
        settings["workbench.layout"] = "JARVIS"
        settings["workbench.defaultLayout"] = "JARVIS"

        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=2)
            logger.info(f"   ✅ Updated {self.settings_file}")
        except Exception as e:
            logger.error(f"   ❌ Error updating settings: {e}")
            success = False

        # Method 3: Update environment.json
        if self.environment_file.exists():
            try:
                with open(self.environment_file, 'r') as f:
                    environment = json.load(f)
            except:
                environment = {}
        else:
            environment = {}

        # Add layout to environment
        if "workspace" not in environment:
            environment["workspace"] = {}

        environment["workspace"]["layout"] = "JARVIS"
        environment["workspace"]["defaultLayout"] = "JARVIS"

        try:
            with open(self.environment_file, 'w') as f:
                json.dump(environment, f, indent=2)
            logger.info(f"   ✅ Updated {self.environment_file}")
        except Exception as e:
            logger.error(f"   ❌ Error updating environment: {e}")
            success = False

        # Method 4: Create layout state file (if Cursor uses it)
        layout_state_file = self.cursor_dir / "layout_state.json"
        layout_state = {
            "currentLayout": "JARVIS",
            "defaultLayout": "JARVIS",
            "layouts": {
                "JARVIS": {
                    "name": "JARVIS",
                    "description": "JARVIS Layout - Optimized for LUMINA development",
                    "panels": {
                        "sidebar": {"location": "left", "visible": True},
                        "panel": {"location": "bottom", "visible": True},
                        "editor": {"layout": "grid"}
                    }
                }
            }
        }

        try:
            with open(layout_state_file, 'w') as f:
                json.dump(layout_state, f, indent=2)
            logger.info(f"   ✅ Created {layout_state_file}")
        except Exception as e:
            logger.debug(f"   Could not create layout state: {e}")

        logger.info("")
        logger.info("=" * 80)
        if success:
            logger.info("✅ JARVIS LAYOUT SET AS DEFAULT")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📋 Next Steps:")
            logger.info("   1. Restart Cursor IDE to apply layout")
            logger.info("   2. If layout doesn't apply automatically:")
            logger.info("      - Go to View > Appearance > Layout")
            logger.info("      - Select 'JARVIS' layout")
            logger.info("      - Or use Command Palette: 'View: Restore Layout'")
            logger.info("")
        else:
            logger.info("⚠️  LAYOUT SET WITH WARNINGS")
            logger.info("=" * 80)
            logger.info("   Some files may not have been updated")
            logger.info("   Please check manually")
            logger.info("")

        return success

    def verify_jarvis_layout(self) -> bool:
        """Verify JARVIS layout is set"""
        logger.info("   🔍 Verifying JARVIS layout configuration...")

        verified = True

        # Check workspace.json
        if self.workspace_file.exists():
            try:
                with open(self.workspace_file, 'r') as f:
                    workspace = json.load(f)
                    if workspace.get("layout") == "JARVIS" or workspace.get("defaultLayout") == "JARVIS":
                        logger.info("   ✅ workspace.json: JARVIS layout set")
                    else:
                        logger.warning("   ⚠️  workspace.json: JARVIS layout not found")
                        verified = False
            except:
                logger.warning("   ⚠️  Could not read workspace.json")
                verified = False

        # Check settings.json
        if self.settings_file.exists():
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    if settings.get("workbench.layout") == "JARVIS" or settings.get("workbench.defaultLayout") == "JARVIS":
                        logger.info("   ✅ settings.json: JARVIS layout set")
                    else:
                        logger.warning("   ⚠️  settings.json: JARVIS layout not found")
                        verified = False
            except:
                logger.warning("   ⚠️  Could not read settings.json")
                verified = False

        # Check environment.json
        if self.environment_file.exists():
            try:
                with open(self.environment_file, 'r') as f:
                    environment = json.load(f)
                    workspace = environment.get("workspace", {})
                    if workspace.get("layout") == "JARVIS" or workspace.get("defaultLayout") == "JARVIS":
                        logger.info("   ✅ environment.json: JARVIS layout set")
                    else:
                        logger.warning("   ⚠️  environment.json: JARVIS layout not found")
                        verified = False
            except:
                logger.warning("   ⚠️  Could not read environment.json")
                verified = False

        return verified


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Set Cursor IDE Layout to JARVIS")
    parser.add_argument("--set", action="store_true", help="Set JARVIS layout")
    parser.add_argument("--verify", action="store_true", help="Verify JARVIS layout")

    args = parser.parse_args()

    setter = CursorJARVISLayoutSetter()

    if args.set or not any([args.set, args.verify]):
        success = setter.set_jarvis_layout()
        if success:
            print("✅ JARVIS layout set as default")
        else:
            print("⚠️  Layout set with warnings - check logs")

    elif args.verify:
        verified = setter.verify_jarvis_layout()
        if verified:
            print("✅ JARVIS layout verified")
        else:
            print("⚠️  JARVIS layout not fully configured")


if __name__ == "__main__":


    main()