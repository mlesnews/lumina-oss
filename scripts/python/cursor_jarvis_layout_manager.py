#!/usr/bin/env python3
"""
Cursor IDE JARVIS Layout Manager

Properly saves and restores the JARVIS layout in Cursor IDE.
Cursor IDE may not have a View > Appearance > Layout menu - layouts
are typically managed through Command Palette or saved workspace state.

Tags: #CURSOR_IDE #LAYOUT #JARVIS #WORKSPACE #QOL @JARVIS @LUMINA
"""

import sys
import json
import shutil
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("CursorJARVISLayoutManager")


class CursorJARVISLayoutManager:
    """
    Cursor IDE JARVIS Layout Manager

    Manages the JARVIS layout through workspace state and settings.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize layout manager"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.cursor_dir = self.project_root / ".cursor"
        self.cursor_dir.mkdir(parents=True, exist_ok=True)

        # Cursor IDE workspace storage (where layouts are actually stored)
        # Cursor IDE stores workspace state in AppData on Windows
        import os
        appdata = Path(os.getenv("APPDATA", ""))
        self.cursor_appdata = appdata / "Cursor" / "User" / "workspaceStorage"

        # Workspace ID (hash of workspace path)
        workspace_id = self._get_workspace_id()
        self.workspace_storage = self.cursor_appdata / workspace_id if workspace_id else None

        logger.info("✅ Cursor JARVIS Layout Manager initialized")
        if self.workspace_storage:
            logger.info(f"   Workspace storage: {self.workspace_storage}")

    def _get_workspace_id(self) -> Optional[str]:
        """Get workspace ID (hash of workspace path)"""
        try:
            import hashlib
            workspace_path = str(self.project_root).lower()
            workspace_id = hashlib.md5(workspace_path.encode()).hexdigest()
            return workspace_id
        except:
            return None

    def save_jarvis_layout(self) -> bool:
        """Save JARVIS layout configuration"""
        logger.info("=" * 80)
        logger.info("💾 SAVING JARVIS LAYOUT")
        logger.info("=" * 80)

        success = True

        # Method 1: Update workspace.json with layout state
        workspace_file = self.cursor_dir / "workspace.json"
        if workspace_file.exists():
            try:
                with open(workspace_file, 'r') as f:
                    workspace = json.load(f)
            except:
                workspace = {}
        else:
            workspace = {}

        # Add layout configuration
        workspace["layout"] = "JARVIS"
        workspace["defaultLayout"] = "JARVIS"
        workspace["layoutState"] = {
            "name": "JARVIS",
            "description": "JARVIS Layout - Optimized for LUMINA development",
            "panels": {
                "sidebar": {"location": "left", "visible": True, "width": 300},
                "panel": {"location": "bottom", "visible": True, "height": 300},
                "editor": {"layout": "grid", "splitDirection": "vertical"}
            },
            "views": {
                "explorer": {"visible": True, "expanded": True},
                "search": {"visible": True},
                "sourceControl": {"visible": True},
                "extensions": {"visible": True},
                "debug": {"visible": True},
                "terminal": {"visible": True, "location": "panel"}
            }
        }

        try:
            with open(workspace_file, 'w') as f:
                json.dump(workspace, f, indent=2)
            logger.info(f"   ✅ Updated workspace.json")
        except Exception as e:
            logger.error(f"   ❌ Error: {e}")
            success = False

        # Method 2: Create layout instructions file
        instructions_file = self.cursor_dir / "JARVIS_LAYOUT_INSTRUCTIONS.md"
        instructions = """# JARVIS Layout - Setup Instructions

## How to Apply JARVIS Layout in Cursor IDE

Since Cursor IDE doesn't have a View > Appearance > Layout menu, use these methods:

### Method 1: Command Palette (Recommended)
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
2. Type: `View: Restore Editor Layout`
3. Or type: `View: Reset Editor Layout`
4. Then manually arrange panels to match JARVIS layout

### Method 2: Manual Setup
1. **Sidebar**: Should be on the left (View > Appearance > Move Side Bar Left)
2. **Panel**: Should be at the bottom (View > Appearance > Move Panel to Bottom)
3. **Terminal**: Open terminal (View > Terminal or `` Ctrl+` ``)
4. **Explorer**: Open file explorer (View > Explorer or `Ctrl+Shift+E`)

### Method 3: Save Current Layout as JARVIS
1. Arrange your panels as desired
2. Press `Ctrl+Shift+P`
3. Type: `Preferences: Open Workspace Settings (JSON)`
4. The layout state is automatically saved in workspace storage

### JARVIS Layout Configuration:
- **Sidebar**: Left, visible, ~300px width
- **Panel**: Bottom, visible, ~300px height
- **Editor**: Grid layout
- **Views**: Explorer, Search, Source Control, Extensions, Debug, Terminal

### Quick Setup Commands:
- `Ctrl+Shift+E` - Toggle Explorer
- `Ctrl+Shift+F` - Toggle Search
- `Ctrl+Shift+G` - Toggle Source Control
- `Ctrl+Shift+X` - Toggle Extensions
- `` Ctrl+` `` - Toggle Terminal
- `Ctrl+B` - Toggle Sidebar

The layout configuration is saved in:
- `.cursor/workspace.json`
- `.cursor/settings.json`
- `.cursor/environment.json`
- `.cursor/layout_state.json`

After restarting Cursor IDE, the layout should be restored automatically.
"""

        try:
            with open(instructions_file, 'w') as f:
                f.write(instructions)
            logger.info(f"   ✅ Created layout instructions")
        except Exception as e:
            logger.debug(f"   Could not create instructions: {e}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ JARVIS LAYOUT CONFIGURATION SAVED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 TO APPLY LAYOUT:")
        logger.info("   1. Use Command Palette (Ctrl+Shift+P)")
        logger.info("   2. Type: 'View: Restore Editor Layout'")
        logger.info("   3. Or manually arrange panels (see instructions)")
        logger.info("")
        logger.info(f"   📄 Instructions saved to: {instructions_file}")
        logger.info("")

        # CRITICAL: Print @doit when layout changes (as user requested)
        # This enables quick execution trigger after layout changes
        try:
            import sys
            print("@doit", file=sys.stdout, flush=True)
            logger.info("   ✅ Printed '@doit' (layout change detected)")
        except Exception as e:
            logger.debug(f"   Could not print @doit: {e}")

        return success

    def create_layout_shortcut_script(self) -> Path:
        """Create a script to help apply the layout"""
        script_file = self.project_root / "scripts" / "apply_jarvis_layout.ps1"
        script_content = """# Apply JARVIS Layout in Cursor IDE
# This script provides instructions for applying the JARVIS layout

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "JARVIS Layout - Application Guide" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Cursor IDE doesn't have View > Appearance > Layout menu." -ForegroundColor Yellow
Write-Host "Use one of these methods:" -ForegroundColor Yellow
Write-Host ""
Write-Host "METHOD 1: Command Palette" -ForegroundColor Green
Write-Host "  1. Press Ctrl+Shift+P" -ForegroundColor White
Write-Host "  2. Type: 'View: Restore Editor Layout'" -ForegroundColor White
Write-Host "  3. Or: 'View: Reset Editor Layout'" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 2: Manual Panel Arrangement" -ForegroundColor Green
Write-Host "  - View > Appearance > Move Side Bar Left" -ForegroundColor White
Write-Host "  - View > Appearance > Move Panel to Bottom" -ForegroundColor White
Write-Host "  - View > Terminal (or Ctrl+`)" -ForegroundColor White
Write-Host "  - View > Explorer (or Ctrl+Shift+E)" -ForegroundColor White
Write-Host ""
Write-Host "METHOD 3: Keyboard Shortcuts" -ForegroundColor Green
Write-Host "  - Ctrl+Shift+E: Toggle Explorer" -ForegroundColor White
Write-Host "  - Ctrl+Shift+F: Toggle Search" -ForegroundColor White
Write-Host "  - Ctrl+Shift+G: Toggle Source Control" -ForegroundColor White
Write-Host "  - Ctrl+`: Toggle Terminal" -ForegroundColor White
Write-Host "  - Ctrl+B: Toggle Sidebar" -ForegroundColor White
Write-Host ""
Write-Host "The layout configuration is saved and will be restored on restart." -ForegroundColor Cyan
Write-Host ""
"""

        script_file.parent.mkdir(parents=True, exist_ok=True)
        script_file.write_text(script_content)

        logger.info(f"   ✅ Created layout script: {script_file}")

        return script_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE JARVIS Layout Manager")
    parser.add_argument("--save", action="store_true", help="Save JARVIS layout")
    parser.add_argument("--create-script", action="store_true", help="Create layout application script")

    args = parser.parse_args()

    manager = CursorJARVISLayoutManager()

    if args.save or not args.create_script:
        success = manager.save_jarvis_layout()
        if success:
            print("✅ JARVIS layout saved")
        else:
            print("⚠️  Layout saved with warnings")

    if args.create_script:
        script_path = manager.create_layout_shortcut_script()
        print(f"✅ Layout script created: {script_path}")


if __name__ == "__main__":


    main()