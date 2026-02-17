#!/usr/bin/env python3
"""
Keyboard Shortcut Mapper

Explores and maps all keyboard shortcuts for:
- Windows 11 Pro operating system
- All installed applications
- Neo web browser
- JARVIS-interactable applications
- API/CLI secure tunnel MANUS-controlled applications

Tags: #KEYBOARD_SHORTCUTS #WINDOWS11 #NEO_BROWSER #JARVIS #MANUS @JARVIS @LUMINA
"""

import sys
import json
import subprocess
import winreg
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict

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

logger = get_logger("KeyboardShortcutMapper")


@dataclass
class KeyboardShortcut:
    """Keyboard shortcut definition"""
    shortcut_id: str
    application: str
    category: str  # "os", "application", "neo_browser", "jarvis", "manus"
    key_combination: str
    description: str
    action: str
    context: str = "global"  # "global", "window", "dialog", "menu"
    source: str = "discovered"  # "discovered", "documented", "custom"
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KeyboardShortcutMapper:
    """
    Keyboard Shortcut Mapper

    Discovers and maps all keyboard shortcuts across the system.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize keyboard shortcut mapper"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "keyboard_shortcuts"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Storage
        self.shortcuts_file = self.data_dir / "shortcuts.json"
        self.shortcuts: Dict[str, KeyboardShortcut] = {}

        # Load existing
        self._load_shortcuts()

        logger.info("✅ Keyboard Shortcut Mapper initialized")
        logger.info("   🎹 Ready to map all shortcuts")

    def _load_shortcuts(self):
        """Load existing shortcuts"""
        if self.shortcuts_file.exists():
            try:
                with open(self.shortcuts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.shortcuts = {
                        sid: KeyboardShortcut(**sdata)
                        for sid, sdata in data.get("shortcuts", {}).items()
                    }
                logger.info(f"   ✅ Loaded {len(self.shortcuts)} existing shortcuts")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load shortcuts: {e}")

    def _save_shortcuts(self):
        """Save shortcuts"""
        try:
            with open(self.shortcuts_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "total_shortcuts": len(self.shortcuts),
                    "shortcuts": {sid: s.to_dict() for sid, s in self.shortcuts.items()}
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving shortcuts: {e}")

    def discover_windows11_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Discover Windows 11 Pro keyboard shortcuts

        Returns:
            List of Windows 11 shortcuts
        """
        logger.info("   🪟 Discovering Windows 11 Pro shortcuts...")

        windows_shortcuts = [
            # System
            KeyboardShortcut("win11_win", "Windows 11", "os", "Win", "Open Start menu", "Open Start menu", "global"),
            KeyboardShortcut("win11_win_d", "Windows 11", "os", "Win+D", "Show desktop", "Minimize all windows", "global"),
            KeyboardShortcut("win11_win_e", "Windows 11", "os", "Win+E", "Open File Explorer", "Open File Explorer", "global"),
            KeyboardShortcut("win11_win_r", "Windows 11", "os", "Win+R", "Open Run dialog", "Open Run dialog", "global"),
            KeyboardShortcut("win11_win_i", "Windows 11", "os", "Win+I", "Open Settings", "Open Settings app", "global"),
            KeyboardShortcut("win11_win_l", "Windows 11", "os", "Win+L", "Lock computer", "Lock the computer", "global"),
            KeyboardShortcut("win11_win_tab", "Windows 11", "os", "Win+Tab", "Task View", "Open Task View", "global"),
            KeyboardShortcut("win11_win_arrow", "Windows 11", "os", "Win+Arrow", "Snap window", "Snap window to side", "global"),
            KeyboardShortcut("win11_win_shift_s", "Windows 11", "os", "Win+Shift+S", "Snipping Tool", "Open Snipping Tool", "global"),
            KeyboardShortcut("win11_win_v", "Windows 11", "os", "Win+V", "Clipboard history", "Open clipboard history", "global"),
            KeyboardShortcut("win11_win_period", "Windows 11", "os", "Win+.", "Emoji panel", "Open emoji panel", "global"),
            KeyboardShortcut("win11_win_x", "Windows 11", "os", "Win+X", "Quick Link menu", "Open Quick Link menu", "global"),
            KeyboardShortcut("win11_win_p", "Windows 11", "os", "Win+P", "Project display", "Project to another screen", "global"),
            KeyboardShortcut("win11_win_a", "Windows 11", "os", "Win+A", "Action Center", "Open Action Center", "global"),
            KeyboardShortcut("win11_win_k", "Windows 11", "os", "Win+K", "Connect devices", "Open Connect panel", "global"),

            # Window Management
            KeyboardShortcut("win11_alt_tab", "Windows 11", "os", "Alt+Tab", "Switch apps", "Switch between open apps", "global"),
            KeyboardShortcut("win11_alt_shift_tab", "Windows 11", "os", "Alt+Shift+Tab", "Switch apps (reverse)", "Switch apps in reverse", "global"),
            KeyboardShortcut("win11_alt_f4", "Windows 11", "os", "Alt+F4", "Close window", "Close active window", "global"),
            KeyboardShortcut("win11_alt_enter", "Windows 11", "os", "Alt+Enter", "Properties", "Open Properties dialog", "global"),
            KeyboardShortcut("win11_alt_space", "Windows 11", "os", "Alt+Space", "Window menu", "Open window menu", "window"),
            KeyboardShortcut("win11_alt_esc", "Windows 11", "os", "Alt+Esc", "Cycle windows", "Cycle through windows", "global"),

            # Text Editing
            KeyboardShortcut("win11_ctrl_c", "Windows 11", "os", "Ctrl+C", "Copy", "Copy selected text", "global"),
            KeyboardShortcut("win11_ctrl_v", "Windows 11", "os", "Ctrl+V", "Paste", "Paste text", "global"),
            KeyboardShortcut("win11_ctrl_x", "Windows 11", "os", "Ctrl+X", "Cut", "Cut selected text", "global"),
            KeyboardShortcut("win11_ctrl_z", "Windows 11", "os", "Ctrl+Z", "Undo", "Undo last action", "global"),
            KeyboardShortcut("win11_ctrl_y", "Windows 11", "os", "Ctrl+Y", "Redo", "Redo last action", "global"),
            KeyboardShortcut("win11_ctrl_a", "Windows 11", "os", "Ctrl+A", "Select all", "Select all items", "global"),
            KeyboardShortcut("win11_ctrl_f", "Windows 11", "os", "Ctrl+F", "Find", "Find in document", "global"),
            KeyboardShortcut("win11_ctrl_h", "Windows 11", "os", "Ctrl+H", "Replace", "Find and replace", "global"),

            # Navigation
            KeyboardShortcut("win11_ctrl_arrow", "Windows 11", "os", "Ctrl+Arrow", "Move cursor", "Move cursor word by word", "text"),
            KeyboardShortcut("win11_ctrl_shift_arrow", "Windows 11", "os", "Ctrl+Shift+Arrow", "Select text", "Select text word by word", "text"),
            KeyboardShortcut("win11_home", "Windows 11", "os", "Home", "Start of line", "Move to start of line", "text"),
            KeyboardShortcut("win11_end", "Windows 11", "os", "End", "End of line", "Move to end of line", "text"),
            KeyboardShortcut("win11_ctrl_home", "Windows 11", "os", "Ctrl+Home", "Start of document", "Move to start of document", "text"),
            KeyboardShortcut("win11_ctrl_end", "Windows 11", "os", "Ctrl+End", "End of document", "Move to end of document", "text"),

            # File Operations
            KeyboardShortcut("win11_ctrl_n", "Windows 11", "os", "Ctrl+N", "New", "Create new item", "global"),
            KeyboardShortcut("win11_ctrl_o", "Windows 11", "os", "Ctrl+O", "Open", "Open file", "global"),
            KeyboardShortcut("win11_ctrl_s", "Windows 11", "os", "Ctrl+S", "Save", "Save file", "global"),
            KeyboardShortcut("win11_ctrl_shift_s", "Windows 11", "os", "Ctrl+Shift+S", "Save as", "Save file as", "global"),
            KeyboardShortcut("win11_ctrl_w", "Windows 11", "os", "Ctrl+W", "Close tab", "Close current tab/window", "global"),
            KeyboardShortcut("win11_ctrl_t", "Windows 11", "os", "Ctrl+T", "New tab", "Open new tab", "browser"),
            KeyboardShortcut("win11_ctrl_shift_t", "Windows 11", "os", "Ctrl+Shift+T", "Reopen tab", "Reopen closed tab", "browser"),

            # System Shortcuts
            KeyboardShortcut("win11_ctrl_shift_esc", "Windows 11", "os", "Ctrl+Shift+Esc", "Task Manager", "Open Task Manager", "global"),
            KeyboardShortcut("win11_ctrl_alt_del", "Windows 11", "os", "Ctrl+Alt+Del", "Security screen", "Open security screen", "global"),
            KeyboardShortcut("win11_f11", "Windows 11", "os", "F11", "Fullscreen", "Toggle fullscreen", "global"),
            KeyboardShortcut("win11_f5", "Windows 11", "os", "F5", "Refresh", "Refresh page/window", "global"),
            KeyboardShortcut("win11_ctrl_f5", "Windows 11", "os", "Ctrl+F5", "Hard refresh", "Hard refresh page", "browser"),
        ]

        # Add to shortcuts
        for shortcut in windows_shortcuts:
            self.shortcuts[shortcut.shortcut_id] = shortcut

        logger.info(f"   ✅ Discovered {len(windows_shortcuts)} Windows 11 shortcuts")
        return windows_shortcuts

    def discover_neo_browser_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Discover Neo web browser keyboard shortcuts

        Returns:
            List of Neo browser shortcuts
        """
        logger.info("   🌐 Discovering Neo browser shortcuts...")

        neo_shortcuts = [
            # Navigation
            KeyboardShortcut("neo_ctrl_t", "Neo Browser", "neo_browser", "Ctrl+T", "New tab", "Open new tab", "browser"),
            KeyboardShortcut("neo_ctrl_w", "Neo Browser", "neo_browser", "Ctrl+W", "Close tab", "Close current tab", "browser"),
            KeyboardShortcut("neo_ctrl_shift_t", "Neo Browser", "neo_browser", "Ctrl+Shift+T", "Reopen tab", "Reopen closed tab", "browser"),
            KeyboardShortcut("neo_ctrl_n", "Neo Browser", "neo_browser", "Ctrl+N", "New window", "Open new window", "browser"),
            KeyboardShortcut("neo_ctrl_shift_n", "Neo Browser", "neo_browser", "Ctrl+Shift+N", "Incognito window", "Open incognito window", "browser"),
            KeyboardShortcut("neo_ctrl_r", "Neo Browser", "neo_browser", "Ctrl+R", "Reload", "Reload current page", "browser"),
            KeyboardShortcut("neo_ctrl_shift_r", "Neo Browser", "neo_browser", "Ctrl+Shift+R", "Hard reload", "Hard reload page", "browser"),
            KeyboardShortcut("neo_ctrl_l", "Neo Browser", "neo_browser", "Ctrl+L", "Focus address bar", "Focus address bar", "browser"),
            KeyboardShortcut("neo_alt_left", "Neo Browser", "neo_browser", "Alt+Left", "Back", "Go back", "browser"),
            KeyboardShortcut("neo_alt_right", "Neo Browser", "neo_browser", "Alt+Right", "Forward", "Go forward", "browser"),
            KeyboardShortcut("neo_ctrl_shift_delete", "Neo Browser", "neo_browser", "Ctrl+Shift+Delete", "Clear data", "Clear browsing data", "browser"),

            # Tab Management
            KeyboardShortcut("neo_ctrl_1", "Neo Browser", "neo_browser", "Ctrl+1-8", "Switch tab", "Switch to tab 1-8", "browser"),
            KeyboardShortcut("neo_ctrl_9", "Neo Browser", "neo_browser", "Ctrl+9", "Last tab", "Switch to last tab", "browser"),
            KeyboardShortcut("neo_ctrl_tab", "Neo Browser", "neo_browser", "Ctrl+Tab", "Next tab", "Switch to next tab", "browser"),
            KeyboardShortcut("neo_ctrl_shift_tab", "Neo Browser", "neo_browser", "Ctrl+Shift+Tab", "Previous tab", "Switch to previous tab", "browser"),
            KeyboardShortcut("neo_ctrl_shift_w", "Neo Browser", "neo_browser", "Ctrl+Shift+W", "Close window", "Close current window", "browser"),

            # Bookmarks
            KeyboardShortcut("neo_ctrl_d", "Neo Browser", "neo_browser", "Ctrl+D", "Bookmark", "Bookmark current page", "browser"),
            KeyboardShortcut("neo_ctrl_shift_d", "Neo Browser", "neo_browser", "Ctrl+Shift+D", "Bookmark all", "Bookmark all tabs", "browser"),
            KeyboardShortcut("neo_ctrl_shift_o", "Neo Browser", "neo_browser", "Ctrl+Shift+O", "Bookmarks manager", "Open bookmarks manager", "browser"),

            # Developer Tools
            KeyboardShortcut("neo_f12", "Neo Browser", "neo_browser", "F12", "Developer tools", "Open developer tools", "browser"),
            KeyboardShortcut("neo_ctrl_shift_i", "Neo Browser", "neo_browser", "Ctrl+Shift+I", "Developer tools", "Open developer tools", "browser"),
            KeyboardShortcut("neo_ctrl_shift_j", "Neo Browser", "neo_browser", "Ctrl+Shift+J", "Console", "Open console", "browser"),
            KeyboardShortcut("neo_ctrl_u", "Neo Browser", "neo_browser", "Ctrl+U", "View source", "View page source", "browser"),

            # Search
            KeyboardShortcut("neo_ctrl_f", "Neo Browser", "neo_browser", "Ctrl+F", "Find in page", "Find in current page", "browser"),
            KeyboardShortcut("neo_ctrl_g", "Neo Browser", "neo_browser", "Ctrl+G", "Find next", "Find next occurrence", "browser"),
            KeyboardShortcut("neo_ctrl_shift_g", "Neo Browser", "neo_browser", "Ctrl+Shift+G", "Find previous", "Find previous occurrence", "browser"),

            # Zoom
            KeyboardShortcut("neo_ctrl_plus", "Neo Browser", "neo_browser", "Ctrl++", "Zoom in", "Zoom in", "browser"),
            KeyboardShortcut("neo_ctrl_minus", "Neo Browser", "neo_browser", "Ctrl+-", "Zoom out", "Zoom out", "browser"),
            KeyboardShortcut("neo_ctrl_0", "Neo Browser", "neo_browser", "Ctrl+0", "Reset zoom", "Reset zoom to 100%", "browser"),

            # History
            KeyboardShortcut("neo_ctrl_h", "Neo Browser", "neo_browser", "Ctrl+H", "History", "Open history", "browser"),
        ]

        # Add to shortcuts
        for shortcut in neo_shortcuts:
            self.shortcuts[shortcut.shortcut_id] = shortcut

        logger.info(f"   ✅ Discovered {len(neo_shortcuts)} Neo browser shortcuts")
        return neo_shortcuts

    def discover_jarvis_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Discover JARVIS-interactable application shortcuts

        Returns:
            List of JARVIS shortcuts
        """
        logger.info("   🤖 Discovering JARVIS shortcuts...")

        jarvis_shortcuts = [
            # Cursor IDE (from keybindings.json)
            KeyboardShortcut("jarvis_cursor_chat", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+J", "Focus chat", "Focus Cursor chat", "ide"),
            KeyboardShortcut("jarvis_cursor_composer", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+C", "Open composer", "Open Cursor composer", "ide"),
            KeyboardShortcut("jarvis_cursor_agent", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+A", "Start agent", "Start Cursor agent", "ide"),
            KeyboardShortcut("jarvis_cursor_new_chat", "Cursor IDE", "jarvis", "Ctrl+Shift+J", "New chat", "New Cursor chat", "ide"),
            KeyboardShortcut("jarvis_cursor_refactor", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+R", "Refactor", "Refactor code", "ide"),
            KeyboardShortcut("jarvis_cursor_test", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+T", "Generate test", "Generate test", "ide"),
            KeyboardShortcut("jarvis_cursor_index", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+I", "Index codebase", "Index codebase", "ide"),
            KeyboardShortcut("jarvis_cursor_summarize", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+S", "Summarize", "Summarize code", "ide"),
            KeyboardShortcut("jarvis_cursor_debug", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+D", "Debug explain", "Explain debug", "ide"),
            KeyboardShortcut("jarvis_cursor_inline", "Cursor IDE", "jarvis", "Ctrl+K Ctrl+E", "Inline edit", "Inline edit", "ide"),
            KeyboardShortcut("jarvis_cursor_accept_all", "Cursor IDE", "jarvis", "Ctrl+Enter", "Accept all", "Accept all changes", "ide"),
            KeyboardShortcut("jarvis_cursor_keep_all", "Cursor IDE", "jarvis", "Ctrl+Shift+Enter", "Keep all", "Keep all changes", "ide"),

            # MANUS Screenshots
            KeyboardShortcut("jarvis_manus_quick", "MANUS", "jarvis", "Ctrl+Shift+S", "Quick screenshot", "MANUS quick screenshot", "global"),
            KeyboardShortcut("jarvis_manus_context", "MANUS", "jarvis", "Ctrl+Shift+C", "Screenshot with context", "MANUS screenshot with context", "global"),
            KeyboardShortcut("jarvis_manus_capture", "MANUS", "jarvis", "Ctrl+Alt+S", "Capture screenshot", "MANUS capture screenshot", "global"),

            # Voice Controls
            KeyboardShortcut("jarvis_voice_queue", "JARVIS Voice", "jarvis", "Ctrl+Shift+V", "Voice queue", "Open voice queue", "global"),
            KeyboardShortcut("jarvis_vcr_play", "JARVIS VCR", "jarvis", "Ctrl+Shift+P", "Play voice", "Play/resume voice request", "global"),
            KeyboardShortcut("jarvis_vcr_pause", "JARVIS VCR", "jarvis", "Ctrl+Shift+;", "Pause voice", "Pause voice request", "global"),
            KeyboardShortcut("jarvis_vcr_stop", "JARVIS VCR", "jarvis", "Ctrl+Shift+.", "Stop voice", "Stop voice request", "global"),
            KeyboardShortcut("jarvis_vcr_record", "JARVIS VCR", "jarvis", "Ctrl+Shift+R", "Record voice", "Start voice recording", "global"),
        ]

        # Add to shortcuts
        for shortcut in jarvis_shortcuts:
            self.shortcuts[shortcut.shortcut_id] = shortcut

        logger.info(f"   ✅ Discovered {len(jarvis_shortcuts)} JARVIS shortcuts")
        return jarvis_shortcuts

    def discover_installed_applications_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Discover shortcuts from installed applications

        Returns:
            List of application shortcuts
        """
        logger.info("   📱 Discovering installed application shortcuts...")

        # Common application shortcuts
        app_shortcuts = [
            # VS Code / Cursor (general)
            KeyboardShortcut("app_vscode_terminal", "VS Code/Cursor", "application", "Ctrl+`", "Toggle terminal", "Toggle integrated terminal", "ide"),
            KeyboardShortcut("app_vscode_explorer", "VS Code/Cursor", "application", "Ctrl+Shift+E", "Explorer", "Focus explorer", "ide"),
            KeyboardShortcut("app_vscode_search", "VS Code/Cursor", "application", "Ctrl+Shift+F", "Search", "Search in files", "ide"),
            KeyboardShortcut("app_vscode_git", "VS Code/Cursor", "application", "Ctrl+Shift+G", "Source control", "Focus source control", "ide"),
            KeyboardShortcut("app_vscode_debug", "VS Code/Cursor", "application", "Ctrl+Shift+D", "Debug", "Focus debug", "ide"),
            KeyboardShortcut("app_vscode_extensions", "VS Code/Cursor", "application", "Ctrl+Shift+X", "Extensions", "Focus extensions", "ide"),
            KeyboardShortcut("app_vscode_command", "VS Code/Cursor", "application", "Ctrl+Shift+P", "Command palette", "Open command palette", "ide"),
            KeyboardShortcut("app_vscode_settings", "VS Code/Cursor", "application", "Ctrl+,", "Settings", "Open settings", "ide"),

            # PowerShell / Terminal
            KeyboardShortcut("app_powershell_clear", "PowerShell", "application", "Ctrl+L", "Clear screen", "Clear terminal screen", "terminal"),
            KeyboardShortcut("app_powershell_history", "PowerShell", "application", "F7", "Command history", "Show command history", "terminal"),

            # File Explorer
            KeyboardShortcut("app_explorer_new_folder", "File Explorer", "application", "Ctrl+Shift+N", "New folder", "Create new folder", "explorer"),
            KeyboardShortcut("app_explorer_delete", "File Explorer", "application", "Delete", "Delete", "Delete selected item", "explorer"),
            KeyboardShortcut("app_explorer_rename", "File Explorer", "application", "F2", "Rename", "Rename selected item", "explorer"),
            KeyboardShortcut("app_explorer_properties", "File Explorer", "application", "Alt+Enter", "Properties", "Show properties", "explorer"),
        ]

        # Add to shortcuts
        for shortcut in app_shortcuts:
            self.shortcuts[shortcut.shortcut_id] = shortcut

        logger.info(f"   ✅ Discovered {len(app_shortcuts)} application shortcuts")
        return app_shortcuts

    def discover_manus_controlled_shortcuts(self) -> List[KeyboardShortcut]:
        """
        Discover MANUS-controlled application shortcuts (API/CLI secure tunnel)

        Returns:
            List of MANUS shortcuts
        """
        logger.info("   🎮 Discovering MANUS-controlled shortcuts...")

        manus_shortcuts = [
            # MANUS API/CLI
            KeyboardShortcut("manus_api_control", "MANUS API", "manus", "Ctrl+Alt+M", "MANUS control", "Open MANUS control panel", "global"),
            KeyboardShortcut("manus_desktop_control", "MANUS Desktop", "manus", "Ctrl+Alt+D", "Desktop control", "Enable desktop control", "global"),
            KeyboardShortcut("manus_ide_control", "MANUS IDE", "manus", "Ctrl+Alt+I", "IDE control", "Enable IDE control", "global"),
            KeyboardShortcut("manus_browser_control", "MANUS Browser", "manus", "Ctrl+Alt+B", "Browser control", "Enable browser control", "global"),

            # Secure Tunnel
            KeyboardShortcut("manus_tunnel_connect", "MANUS Tunnel", "manus", "Ctrl+Alt+T", "Connect tunnel", "Connect secure tunnel", "global"),
            KeyboardShortcut("manus_tunnel_disconnect", "MANUS Tunnel", "manus", "Ctrl+Alt+Shift+T", "Disconnect tunnel", "Disconnect secure tunnel", "global"),

            # Automation
            KeyboardShortcut("manus_automation_start", "MANUS Automation", "manus", "Ctrl+Alt+A", "Start automation", "Start automation", "global"),
            KeyboardShortcut("manus_automation_stop", "MANUS Automation", "manus", "Ctrl+Alt+Shift+A", "Stop automation", "Stop automation", "global"),
        ]

        # Add to shortcuts
        for shortcut in manus_shortcuts:
            self.shortcuts[shortcut.shortcut_id] = shortcut

        logger.info(f"   ✅ Discovered {len(manus_shortcuts)} MANUS shortcuts")
        return manus_shortcuts

    def discover_all(self) -> Dict[str, Any]:
        """
        Discover all keyboard shortcuts

        Returns:
            Summary of discoveries
        """
        logger.info("=" * 80)
        logger.info("🎹 KEYBOARD SHORTCUT DISCOVERY")
        logger.info("=" * 80)

        # Discover all categories
        win11 = self.discover_windows11_shortcuts()
        neo = self.discover_neo_browser_shortcuts()
        jarvis = self.discover_jarvis_shortcuts()
        apps = self.discover_installed_applications_shortcuts()
        manus = self.discover_manus_controlled_shortcuts()

        # Save
        self._save_shortcuts()

        summary = {
            "windows11": len(win11),
            "neo_browser": len(neo),
            "jarvis": len(jarvis),
            "applications": len(apps),
            "manus": len(manus),
            "total": len(self.shortcuts)
        }

        logger.info("=" * 80)
        logger.info("📊 DISCOVERY SUMMARY")
        logger.info("=" * 80)
        logger.info(f"   Windows 11: {summary['windows11']} shortcuts")
        logger.info(f"   Neo Browser: {summary['neo_browser']} shortcuts")
        logger.info(f"   JARVIS: {summary['jarvis']} shortcuts")
        logger.info(f"   Applications: {summary['applications']} shortcuts")
        logger.info(f"   MANUS: {summary['manus']} shortcuts")
        logger.info(f"   Total: {summary['total']} shortcuts")
        logger.info("=" * 80)

        return summary

    def get_shortcuts_by_category(self, category: str) -> List[KeyboardShortcut]:
        """Get shortcuts by category"""
        return [s for s in self.shortcuts.values() if s.category == category]

    def get_shortcuts_by_application(self, application: str) -> List[KeyboardShortcut]:
        """Get shortcuts by application"""
        return [s for s in self.shortcuts.values() if s.application == application]

    def search_shortcuts(self, query: str) -> List[KeyboardShortcut]:
        """Search shortcuts by query"""
        query_lower = query.lower()
        return [
            s for s in self.shortcuts.values()
            if query_lower in s.key_combination.lower() or
               query_lower in s.description.lower() or
               query_lower in s.action.lower() or
               query_lower in s.application.lower()
        ]

    def export_shortcuts(self, format: str = "json") -> str:
        try:
            """
            Export shortcuts to file

            Args:
                format: Export format (json, markdown, csv)

            Returns:
                Path to exported file
            """
            if format == "json":
                export_file = self.data_dir / "shortcuts_export.json"
                with open(export_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        "exported_at": datetime.now().isoformat(),
                        "total_shortcuts": len(self.shortcuts),
                        "shortcuts": [s.to_dict() for s in self.shortcuts.values()]
                    }, f, indent=2, ensure_ascii=False)

            elif format == "markdown":
                export_file = self.data_dir / "shortcuts_export.md"
                with open(export_file, 'w', encoding='utf-8') as f:
                    f.write("# Keyboard Shortcuts Reference\n\n")
                    f.write(f"*Exported: {datetime.now().isoformat()}*\n\n")
                    f.write(f"**Total Shortcuts: {len(self.shortcuts)}**\n\n")

                    # Group by category
                    categories = {}
                    for shortcut in self.shortcuts.values():
                        if shortcut.category not in categories:
                            categories[shortcut.category] = []
                        categories[shortcut.category].append(shortcut)

                    for category, shortcuts in sorted(categories.items()):
                        f.write(f"## {category.replace('_', ' ').title()}\n\n")
                        f.write("| Application | Shortcut | Description | Action |\n")
                        f.write("|------------|----------|-------------|--------|\n")
                        for s in sorted(shortcuts, key=lambda x: x.application):
                            f.write(f"| {s.application} | `{s.key_combination}` | {s.description} | {s.action} |\n")
                        f.write("\n")

            logger.info(f"   ✅ Exported {len(self.shortcuts)} shortcuts to {export_file}")
            return str(export_file)


        except Exception as e:
            self.logger.error(f"Error in export_shortcuts: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Keyboard Shortcut Mapper")
        parser.add_argument("--discover", action="store_true", help="Discover all shortcuts")
        parser.add_argument("--category", type=str, help="Get shortcuts by category")
        parser.add_argument("--application", type=str, help="Get shortcuts by application")
        parser.add_argument("--search", type=str, help="Search shortcuts")
        parser.add_argument("--export", choices=["json", "markdown"], help="Export shortcuts")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        mapper = KeyboardShortcutMapper()

        if args.discover or not any([args.category, args.application, args.search, args.export]):
            summary = mapper.discover_all()
            if args.json:
                print(json.dumps(summary, indent=2))

        elif args.category:
            shortcuts = mapper.get_shortcuts_by_category(args.category)
            if args.json:
                print(json.dumps([s.to_dict() for s in shortcuts], indent=2))
            else:
                print(f"\n📋 Shortcuts for category: {args.category}")
                print("=" * 80)
                for s in shortcuts:
                    print(f"  • {s.key_combination:20} | {s.description:30} | {s.application}")

        elif args.application:
            shortcuts = mapper.get_shortcuts_by_application(args.application)
            if args.json:
                print(json.dumps([s.to_dict() for s in shortcuts], indent=2))
            else:
                print(f"\n📋 Shortcuts for application: {args.application}")
                print("=" * 80)
                for s in shortcuts:
                    print(f"  • {s.key_combination:20} | {s.description:30} | {s.category}")

        elif args.search:
            shortcuts = mapper.search_shortcuts(args.search)
            if args.json:
                print(json.dumps([s.to_dict() for s in shortcuts], indent=2))
            else:
                print(f"\n🔍 Search results for: {args.search}")
                print("=" * 80)
                for s in shortcuts:
                    print(f"  • {s.key_combination:20} | {s.description:30} | {s.application} ({s.category})")

        elif args.export:
            export_file = mapper.export_shortcuts(args.export)
            if args.json:
                print(json.dumps({"export_file": export_file}, indent=2))
            else:
                print(f"✅ Exported to: {export_file}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()