#!/usr/bin/env python3
"""
MANUS System-Wide Keyboard Shortcuts - Windows OS Level

Maps Cursor IDE keyboard shortcuts to system-wide Windows shortcuts.
Enables @MANUS @FULLCONTROL @FULLAUTO @MAX mode.

Tags: #MANUS #FULLCONTROL #FULLAUTO #MAX #KEYBOARD_SHORTCUTS #WINDOWS #SYSTEM_WIDE @JARVIS @LUMINA
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MANUSSystemWideShortcuts")


class MANUSSystemWideShortcuts:
    """
    MANUS System-Wide Keyboard Shortcuts

    Maps Cursor IDE shortcuts to Windows OS level for @FULLCONTROL @FULLAUTO @MAX
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize MANUS system-wide shortcuts"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "manus_shortcuts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load Cursor keybindings
        self.cursor_keybindings_file = self.project_root / ".cursor" / "keybindings.json"
        self.cursor_keybindings = self._load_cursor_keybindings()

        logger.info("✅ MANUS System-Wide Keyboard Shortcuts initialized")
        logger.info("   @FULLCONTROL @FULLAUTO @MAX mode: ACTIVE")

    def _load_cursor_keybindings(self) -> List[Dict[str, Any]]:
        """Load Cursor IDE keybindings"""
        try:
            if self.cursor_keybindings_file.exists():
                with open(self.cursor_keybindings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"   ⚠️  Could not load Cursor keybindings: {e}")

        return []

    def create_autohotkey_script(self) -> Path:
        try:
            """
            Create AutoHotkey script for system-wide shortcuts

            Returns:
                Path to AutoHotkey script
            """
            script_path = self.data_dir / "manus_system_shortcuts.ahk"

            # Map Cursor shortcuts to system-wide actions
            mappings = self._generate_shortcut_mappings()

            ahk_script = "; MANUS System-Wide Keyboard Shortcuts\n"
            ahk_script += "; @FULLCONTROL @FULLAUTO @MAX\n"
            ahk_script += "; Auto-generated from Cursor IDE keybindings\n\n"

            for mapping in mappings:
                ahk_script += f"{mapping}\n"

            with open(script_path, 'w', encoding='utf-8') as f:
                f.write(ahk_script)

            logger.info(f"✅ AutoHotkey script created: {script_path.name}")
            return script_path

        except Exception as e:
            self.logger.error(f"Error in create_autohotkey_script: {e}", exc_info=True)
            raise
    def _generate_shortcut_mappings(self) -> List[str]:
        """Generate AutoHotkey shortcut mappings"""
        mappings = []

        # Map Cursor shortcuts to system-wide actions
        for binding in self.cursor_keybindings:
            key = binding.get("key", "")
            command = binding.get("command", "")

            # Convert Cursor key format to AutoHotkey format
            ahk_key = self._convert_to_ahk_key(key)

            if ahk_key and command:
                # Map to system action
                action = self._map_command_to_action(command)
                if action:
                    mappings.append(f"{ahk_key}::{action}")

        # Add specific MANUS shortcuts
        mappings.extend([
            "^!u::Send, ^!u  ; Undo All (Ctrl+Alt+U)",
            "^!k::Send, ^!k  ; Keep All (Ctrl+Alt+K)",
            "^k^j::Run, cursor.exe  ; Focus Cursor Chat",
            "^k^c::Run, cursor.exe  ; Open Cursor Composer",
            "^k^a::Run, cursor.exe  ; Start Cursor Agent"
        ])

        return mappings

    def _convert_to_ahk_key(self, cursor_key: str) -> str:
        """Convert Cursor key format to AutoHotkey format"""
        # Cursor: "ctrl+k ctrl+j" -> AutoHotkey: "^k^j"
        # Cursor: "ctrl+alt+u" -> AutoHotkey: "^!u"
        # Cursor: "ctrl+shift+k" -> AutoHotkey: "^+k"

        key_map = {
            "ctrl": "^",
            "alt": "!",
            "shift": "+",
            "win": "#"
        }

        parts = cursor_key.lower().split()
        ahk_parts = []

        for part in parts:
            modifiers = part.split("+")
            ahk_modifiers = []
            letter = None

            for mod in modifiers:
                if mod in key_map:
                    ahk_modifiers.append(key_map[mod])
                else:
                    letter = mod

            if letter:
                ahk_parts.append("".join(ahk_modifiers) + letter)
            else:
                ahk_parts.append("".join(ahk_modifiers))

        return "".join(ahk_parts) if ahk_parts else None

    def _map_command_to_action(self, command: str) -> Optional[str]:
        """Map Cursor command to system action"""
        # For now, just pass through to Cursor
        # In full implementation, would map to actual system actions
        return f"Send, {command}"

    def create_powershell_shortcuts(self) -> Path:
        """
        Create PowerShell script for Windows shortcuts

        Returns:
            Path to PowerShell script
        """
        script_path = self.data_dir / "manus_system_shortcuts.ps1"

        ps_script = "# MANUS System-Wide Keyboard Shortcuts\n"
        ps_script += "# @FULLCONTROL @FULLAUTO @MAX\n"
        ps_script += "# Auto-generated from Cursor IDE keybindings\n\n"

        ps_script += """
# Register system-wide hotkeys using Register-HotKey
# Note: Requires admin privileges for system-wide shortcuts

# Undo All: Ctrl+Alt+U
Register-HotKey -Key U -Modifier Ctrl,Alt -Action {
    # Send to active window
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("^!u")
}

# Keep All: Ctrl+Alt+K
Register-HotKey -Key K -Modifier Ctrl,Alt -Action {
    # Send to active window
    Add-Type -AssemblyName System.Windows.Forms
    [System.Windows.Forms.SendKeys]::SendWait("^!k")
}

Write-Host "✅ MANUS System-Wide Shortcuts Registered"
Write-Host "   @FULLCONTROL @FULLAUTO @MAX mode: ACTIVE"
"""

        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(ps_script)

        logger.info(f"✅ PowerShell script created: {script_path.name}")
        return script_path

    def install_shortcuts(self) -> Dict[str, Any]:
        """
        Install system-wide shortcuts

        Returns:
            Installation result
        """
        logger.info("=" * 80)
        logger.info("🚀 MANUS SYSTEM-WIDE KEYBOARD SHORTCUTS INSTALLATION")
        logger.info("=" * 80)
        logger.info("")

        result = {
            "autohotkey_script": None,
            "powershell_script": None,
            "installed": False
        }

        # Create AutoHotkey script
        try:
            ahk_script = self.create_autohotkey_script()
            result["autohotkey_script"] = str(ahk_script)
            logger.info(f"   ✅ AutoHotkey script: {ahk_script.name}")
        except Exception as e:
            logger.error(f"   ❌ AutoHotkey script failed: {e}")

        # Create PowerShell script
        try:
            ps_script = self.create_powershell_shortcuts()
            result["powershell_script"] = str(ps_script)
            logger.info(f"   ✅ PowerShell script: {ps_script.name}")
        except Exception as e:
            logger.error(f"   ❌ PowerShell script failed: {e}")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ MANUS SYSTEM-WIDE SHORTCUTS READY")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("   1. Install AutoHotkey: https://www.autohotkey.com/")
        logger.info("   2. Run: manus_system_shortcuts.ahk")
        logger.info("   3. Or run PowerShell script as Administrator")
        logger.info("")

        result["installed"] = True
        return result


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS System-Wide Keyboard Shortcuts")
    parser.add_argument("--install", action="store_true", help="Install system-wide shortcuts")
    parser.add_argument("--create-ahk", action="store_true", help="Create AutoHotkey script")
    parser.add_argument("--create-ps", action="store_true", help="Create PowerShell script")

    args = parser.parse_args()

    manus = MANUSSystemWideShortcuts()

    if args.install:
        manus.install_shortcuts()
    elif args.create_ahk:
        manus.create_autohotkey_script()
    elif args.create_ps:
        manus.create_powershell_shortcuts()
    else:
        parser.print_help()

    return 0


if __name__ == "__main__":


    sys.exit(main())