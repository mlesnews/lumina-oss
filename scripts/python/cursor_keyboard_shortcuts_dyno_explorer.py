#!/usr/bin/env python3
"""
Cursor IDE Keyboard Shortcuts DYNO Explorer

Explores and maps all Cursor IDE keyboard shortcuts and capabilities using @dyno methodology.
Restores and enhances keyboard shortcut mappings with comprehensive exploration.

@JARVIS @DYNO @CURSOR @IDE @KEYBOARD @SHORTCUTS @MAPPING
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import @dyno
try:
    from jarvis_dyno_performance_tuner import JARVISDynoPerformanceTuner
    DYNO_AVAILABLE = True
except ImportError:
    DYNO_AVAILABLE = False
    JARVISDynoPerformanceTuner = None

logger = get_logger("CursorShortcutsDYNO")


class CursorKeyboardShortcutsDYNOExplorer:
    """
    Explore and map Cursor IDE keyboard shortcuts using @dyno methodology.

    Features:
    - Discovers all available keyboard shortcuts
    - Maps function keys and combinations
    - Explores IDE capabilities
    - Restores lost mappings
    - Generates comprehensive documentation
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.data_dir = project_root / "data" / "cursor_shortcuts_dyno"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing mappings
        self.shortcuts_file = project_root / "config" / "cursor_ide_keyboard_shortcuts.json"
        self.keybindings_file = Path.home() / ".cursor" / "User" / "keybindings.json"

        # Initialize @dyno
        self.dyno = None
        if DYNO_AVAILABLE:
            try:
                self.dyno = JARVISDynoPerformanceTuner(project_root)
                self.logger.info("✅ @DYNO initialized for shortcut exploration")
            except Exception as e:
                self.logger.warning(f"⚠️  @DYNO initialization failed: {e}")

        # Shortcut mappings
        self.discovered_shortcuts: Dict[str, Any] = {}
        self.custom_shortcuts: Dict[str, Any] = {}
        self.lost_shortcuts: List[Dict[str, Any]] = []

    def explore_all_shortcuts(self) -> Dict[str, Any]:
        """
        Explore all Cursor IDE keyboard shortcuts and capabilities.

        Returns:
            Complete mapping of all discovered shortcuts
        """
        self.logger.info("="*80)
        self.logger.info("🔍 CURSOR IDE KEYBOARD SHORTCUTS DYNO EXPLORATION")
        self.logger.info("="*80)

        # Start @dyno session
        dyno_session = None
        if self.dyno:
            try:
                dyno_session = self.dyno.start_session("cursor_shortcuts_exploration")
                self.logger.info("✅ @DYNO session started")
            except Exception as e:
                self.logger.warning(f"⚠️  @DYNO session start failed: {e}")

        exploration_results = {
            "timestamp": datetime.now().isoformat(),
            "exploration_method": "@dyno",
            "shortcuts": {}
        }

        # Step 1: Load existing mappings
        self.logger.info("\n📋 Step 1: Loading existing mappings...")
        existing_mappings = self._load_existing_mappings()
        exploration_results["existing_mappings"] = existing_mappings

        # Step 2: Discover default shortcuts
        self.logger.info("\n📋 Step 2: Discovering default shortcuts...")
        default_shortcuts = self._discover_default_shortcuts()
        exploration_results["shortcuts"]["default"] = default_shortcuts

        # Step 3: Discover custom keybindings
        self.logger.info("\n📋 Step 3: Discovering custom keybindings...")
        custom_keybindings = self._discover_custom_keybindings()
        exploration_results["shortcuts"]["custom"] = custom_keybindings

        # Step 4: Discover command palette commands
        self.logger.info("\n📋 Step 4: Discovering command palette commands...")
        command_palette = self._discover_command_palette()
        exploration_results["shortcuts"]["command_palette"] = command_palette

        # Step 5: Discover function keys
        self.logger.info("\n📋 Step 5: Discovering function keys (@FF)...")
        function_keys = self._discover_function_keys()
        exploration_results["shortcuts"]["function_keys"] = function_keys

        # Step 6: Discover IDE capabilities
        self.logger.info("\n📋 Step 6: Discovering IDE capabilities...")
        capabilities = self._discover_ide_capabilities()
        exploration_results["capabilities"] = capabilities

        # Step 7: Identify lost shortcuts
        self.logger.info("\n📋 Step 7: Identifying lost shortcuts...")
        lost = self._identify_lost_shortcuts(existing_mappings, default_shortcuts)
        exploration_results["lost_shortcuts"] = lost

        # Step 8: Generate restoration recommendations
        self.logger.info("\n📋 Step 8: Generating restoration recommendations...")
        recommendations = self._generate_restoration_recommendations(lost, existing_mappings)
        exploration_results["recommendations"] = recommendations

        # Save exploration results
        report_file = self.data_dir / f"exploration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(report_file, 'w') as f:
                json.dump(exploration_results, f, indent=2)
            self.logger.info(f"\n✅ Exploration report saved: {report_file}")
        except Exception as e:
            self.logger.error(f"Failed to save exploration report: {e}")

        # Update shortcuts file
        self._update_shortcuts_file(exploration_results)

        # @dyno: Record exploration
        if self.dyno and dyno_session:
            try:
                self.dyno.record_operator_input(
                    dyno_session,
                    f"Explored {len(default_shortcuts)} default shortcuts, {len(custom_keybindings)} custom keybindings",
                    "exploration"
                )
            except Exception as e:
                self.logger.warning(f"⚠️  @DYNO recording failed: {e}")

        # Print summary
        self._print_summary(exploration_results)

        return exploration_results

    def _load_existing_mappings(self) -> Dict[str, Any]:
        """Load existing keyboard shortcut mappings"""
        mappings = {
            "config_file": {},
            "keybindings_file": {}
        }

        # Load config file
        if self.shortcuts_file.exists():
            try:
                with open(self.shortcuts_file, 'r') as f:
                    mappings["config_file"] = json.load(f)
                self.logger.info(f"   ✅ Loaded config: {len(mappings['config_file'].get('function_keys', {}))} function keys")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed to load config: {e}")

        # Load keybindings file
        if self.keybindings_file.exists():
            try:
                with open(self.keybindings_file, 'r') as f:
                    mappings["keybindings_file"] = json.load(f)
                self.logger.info(f"   ✅ Loaded keybindings: {len(mappings['keybindings_file'])} custom bindings")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed to load keybindings: {e}")
        else:
            self.logger.warning(f"   ⚠️  Keybindings file not found: {self.keybindings_file}")

        return mappings

    def _discover_default_shortcuts(self) -> Dict[str, Any]:
        """Discover default Cursor IDE shortcuts"""
        shortcuts = {
            "navigation": {},
            "editing": {},
            "search": {},
            "debug": {},
            "git": {},
            "terminal": {},
            "command_palette": {}
        }

        # Navigation shortcuts
        shortcuts["navigation"] = {
            "Ctrl+P": "Quick Open",
            "Ctrl+Shift+P": "Command Palette",
            "Ctrl+Tab": "Switch Editor",
            "Ctrl+Shift+Tab": "Previous Editor",
            "Ctrl+K Ctrl+S": "Keyboard Shortcuts",
            "Ctrl+,": "Settings",
            "Ctrl+K Ctrl+W": "Close All Editors",
            "Ctrl+K U": "Close Unmodified Editors",
            "Ctrl+W": "Close Editor",
            "Ctrl+K F": "Close Folder",
            "Alt+Left": "Go Back",
            "Alt+Right": "Go Forward",
            "Ctrl+Shift+E": "Explorer",
            "Ctrl+Shift+F": "Search",
            "Ctrl+Shift+G": "Source Control",
            "Ctrl+Shift+D": "Debug",
            "Ctrl+Shift+X": "Extensions",
        }

        # Editing shortcuts
        shortcuts["editing"] = {
            "Ctrl+C": "Copy",
            "Ctrl+V": "Paste",
            "Ctrl+X": "Cut",
            "Ctrl+Z": "Undo",
            "Ctrl+Shift+Z": "Redo",
            "Ctrl+F": "Find",
            "Ctrl+H": "Replace",
            "Ctrl+D": "Add Selection to Next Find Match",
            "Ctrl+K Ctrl+D": "Move Last Selection to Next Find Match",
            "Alt+Click": "Add Cursor",
            "Ctrl+Alt+Up": "Add Cursor Above",
            "Ctrl+Alt+Down": "Add Cursor Below",
            "Ctrl+Shift+L": "Select All Occurrences",
            "Ctrl+K Ctrl+X": "Trim Trailing Whitespace",
            "Ctrl+K M": "Change Language Mode",
        }

        # Search shortcuts
        shortcuts["search"] = {
            "Ctrl+F": "Find",
            "F3": "Find Next",
            "Shift+F3": "Find Previous",
            "Ctrl+H": "Replace",
            "Ctrl+Shift+F": "Search in Files",
            "Ctrl+Shift+H": "Replace in Files",
            "Ctrl+G": "Go to Line",
            "Ctrl+P": "Quick Open",
        }

        # Debug shortcuts
        shortcuts["debug"] = {
            "F5": "Start Debugging",
            "F9": "Toggle Breakpoint",
            "F10": "Step Over",
            "F11": "Step Into",
            "Shift+F11": "Step Out",
            "Shift+F5": "Stop",
            "Ctrl+Shift+F5": "Restart",
        }

        # Git shortcuts
        shortcuts["git"] = {
            "Ctrl+Shift+G": "Source Control",
            "Ctrl+Enter": "Commit",
            "Ctrl+Shift+P Git": "Git Commands",
        }

        # Terminal shortcuts
        shortcuts["terminal"] = {
            "Ctrl+`": "Toggle Terminal",
            "Ctrl+Shift+`": "New Terminal",
            "Ctrl+Shift+5": "Split Terminal",
        }

        # Command Palette shortcuts
        shortcuts["command_palette"] = {
            "Ctrl+Shift+P": "Command Palette",
            "Ctrl+P": "Quick Open",
            "Ctrl+K Ctrl+S": "Keyboard Shortcuts",
        }

        self.logger.info(f"   ✅ Discovered {sum(len(v) for v in shortcuts.values())} default shortcuts")

        return shortcuts

    def _discover_custom_keybindings(self) -> List[Dict[str, Any]]:
        """Discover custom keybindings from keybindings.json"""
        keybindings = []

        if self.keybindings_file.exists():
            try:
                with open(self.keybindings_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        keybindings = data
                    elif isinstance(data, dict):
                        keybindings = [data]

                self.logger.info(f"   ✅ Discovered {len(keybindings)} custom keybindings")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Failed to read keybindings: {e}")
        else:
            self.logger.info("   ℹ️  No custom keybindings file found")

        return keybindings

    def _discover_command_palette(self) -> List[str]:
        """Discover available command palette commands"""
        # Common Cursor IDE commands
        commands = [
            "workbench.action.files.newFile",
            "workbench.action.files.newUntitledFile",
            "workbench.action.files.openFile",
            "workbench.action.files.openFolder",
            "workbench.action.files.save",
            "workbench.action.files.saveAll",
            "workbench.action.closeActiveEditor",
            "workbench.action.closeAllEditors",
            "workbench.action.splitEditor",
            "workbench.action.toggleSidebarVisibility",
            "workbench.action.quickOpen",
            "workbench.action.showCommands",
            "workbench.action.openSettings",
            "workbench.action.openGlobalKeybindings",
            "editor.action.formatDocument",
            "editor.action.formatSelection",
            "editor.action.rename",
            "editor.action.goToDeclaration",
            "editor.action.goToDefinition",
            "editor.action.goToReferences",
            "editor.action.quickFix",
            "editor.action.showHover",
            "workbench.action.debug.start",
            "workbench.action.debug.stop",
            "workbench.action.debug.restart",
            "workbench.action.debug.continue",
            "workbench.action.debug.stepOver",
            "workbench.action.debug.stepInto",
            "workbench.action.debug.stepOut",
            "workbench.action.terminal.new",
            "workbench.action.terminal.toggleTerminal",
            "workbench.action.togglePanel",
            "workbench.action.maximizeEditor",
            "workbench.action.minimizeOtherEditors",
            "workbench.action.focusActiveEditorGroup",
            "workbench.action.focusNextGroup",
            "workbench.action.focusPreviousGroup",
        ]

        self.logger.info(f"   ✅ Discovered {len(commands)} command palette commands")

        return commands

    def _discover_function_keys(self) -> Dict[str, Any]:
        """Discover function keys (@FF) mappings"""
        function_keys = {
            "F1": {"default": "Show Command Palette", "alternate": "Toggle Help"},
            "F2": {"default": "Rename Symbol", "alternate": "Quick Rename"},
            "F3": {"default": "Find Next", "alternate": "Go to Next Search Result"},
            "F4": {"default": "Go to Definition", "alternate": "Peek Definition"},
            "F5": {"default": "Start Debugging", "alternate": "Continue"},
            "F6": {"default": "Step Over", "alternate": "Next Line"},
            "F7": {"default": "Step Into", "alternate": "Step In"},
            "F8": {"default": "Step Over", "alternate": "Continue"},
            "F9": {"default": "Toggle Breakpoint", "alternate": "Add Breakpoint"},
            "F10": {"default": "Step Over", "alternate": "Next Line"},
            "F11": {"default": "Step Into", "alternate": "Step In"},
            "F12": {"default": "Go to Definition", "alternate": "Peek Definition"},
        }

        self.logger.info(f"   ✅ Discovered {len(function_keys)} function keys")

        return function_keys

    def _discover_ide_capabilities(self) -> Dict[str, Any]:
        """Discover IDE capabilities and features"""
        capabilities = {
            "code_intelligence": [
                "Auto-completion",
                "IntelliSense",
                "Code navigation",
                "Symbol search",
                "Go to definition",
                "Find references",
                "Rename symbol",
                "Code actions",
                "Quick fixes",
            ],
            "editing": [
                "Multi-cursor editing",
                "Column selection",
                "Find and replace",
                "Format document",
                "Format selection",
                "Code folding",
                "Bracket matching",
                "Indentation",
            ],
            "debugging": [
                "Breakpoints",
                "Step debugging",
                "Watch variables",
                "Call stack",
                "Debug console",
                "Conditional breakpoints",
            ],
            "git": [
                "Source control",
                "Diff viewer",
                "Commit",
                "Branch management",
                "Merge conflicts",
            ],
            "terminal": [
                "Integrated terminal",
                "Multiple terminals",
                "Terminal splitting",
                "Terminal profiles",
            ],
            "extensions": [
                "Extension marketplace",
                "Extension management",
                "Extension development",
            ],
        }

        self.logger.info(f"   ✅ Discovered {sum(len(v) for v in capabilities.values())} IDE capabilities")

        return capabilities

    def _identify_lost_shortcuts(self, existing: Dict[str, Any], default: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify lost shortcuts by comparing existing and default"""
        lost = []

        # Check if config file has shortcuts
        config_shortcuts = existing.get("config_file", {}).get("function_keys", {})

        # Compare with default
        default_function_keys = default.get("function_keys", {})

        for key, default_info in default_function_keys.items():
            if key not in config_shortcuts:
                lost.append({
                    "key": key,
                    "default_action": default_info.get("default"),
                    "alternate_action": default_info.get("alternate"),
                    "category": "function_key",
                    "status": "lost"
                })

        self.logger.info(f"   ⚠️  Identified {len(lost)} lost shortcuts")

        return lost

    def _generate_restoration_recommendations(self, lost: List[Dict[str, Any]], existing: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations for restoring lost shortcuts"""
        recommendations = []

        if lost:
            recommendations.append({
                "priority": "high",
                "action": "Restore lost function key mappings",
                "details": f"Found {len(lost)} lost function key mappings. Restore them to config file.",
                "shortcuts": lost
            })

        if not existing.get("keybindings_file"):
            recommendations.append({
                "priority": "medium",
                "action": "Create keybindings.json",
                "details": "Custom keybindings file not found. Create one to store custom mappings.",
                "path": str(self.keybindings_file)
            })

        return recommendations

    def _update_shortcuts_file(self, exploration_results: Dict[str, Any]):
        """Update shortcuts config file with discovered mappings"""
        try:
            # Load existing or create new
            if self.shortcuts_file.exists():
                with open(self.shortcuts_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {
                    "cursor_ide_keyboard_shortcuts": {
                        "version": "1.0.0",
                        "last_updated": datetime.now().isoformat(),
                        "description": "Complete mapping of all Cursor IDE keyboard shortcuts"
                    }
                }

            # Update with discovered shortcuts
            shortcuts_section = data.get("cursor_ide_keyboard_shortcuts", {})
            shortcuts_section["function_keys"] = exploration_results["shortcuts"]["function_keys"]
            shortcuts_section["default_shortcuts"] = exploration_results["shortcuts"]["default"]
            shortcuts_section["custom_keybindings"] = exploration_results["shortcuts"]["custom"]
            shortcuts_section["command_palette"] = exploration_results["shortcuts"]["command_palette"]
            shortcuts_section["capabilities"] = exploration_results["capabilities"]
            shortcuts_section["last_updated"] = datetime.now().isoformat()

            # Save
            with open(self.shortcuts_file, 'w') as f:
                json.dump(data, f, indent=2)

            self.logger.info(f"✅ Updated shortcuts file: {self.shortcuts_file}")
        except Exception as e:
            self.logger.error(f"Failed to update shortcuts file: {e}")

    def _print_summary(self, exploration_results: Dict[str, Any]):
        """Print exploration summary"""
        self.logger.info("\n" + "="*80)
        self.logger.info("EXPLORATION SUMMARY")
        self.logger.info("="*80)

        shortcuts = exploration_results["shortcuts"]
        self.logger.info(f"✅ Default shortcuts: {sum(len(v) for v in shortcuts['default'].values())}")
        self.logger.info(f"✅ Custom keybindings: {len(shortcuts['custom'])}")
        self.logger.info(f"✅ Command palette commands: {len(shortcuts['command_palette'])}")
        self.logger.info(f"✅ Function keys: {len(shortcuts['function_keys'])}")
        self.logger.info(f"✅ IDE capabilities: {sum(len(v) for v in exploration_results['capabilities'].values())}")

        lost = exploration_results.get("lost_shortcuts", [])
        if lost:
            self.logger.warning(f"⚠️  Lost shortcuts: {len(lost)}")
            for shortcut in lost[:5]:  # Show first 5
                self.logger.warning(f"   - {shortcut['key']}: {shortcut['default_action']}")

        recommendations = exploration_results.get("recommendations", [])
        if recommendations:
            self.logger.info(f"\n📋 Recommendations ({len(recommendations)}):")
            for rec in recommendations:
                self.logger.info(f"   [{rec['priority'].upper()}] {rec['action']}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Cursor IDE Keyboard Shortcuts DYNO Explorer")
        parser.add_argument("--explore", action="store_true", help="Explore all shortcuts")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        explorer = CursorKeyboardShortcutsDYNOExplorer(project_root)

        if args.explore:
            result = explorer.explore_all_shortcuts()
            print("\n✅ Exploration complete!")
        else:
            print("Usage: python cursor_keyboard_shortcuts_dyno_explorer.py --explore")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()