#!/usr/bin/env python3
"""
JARVIS Cursor IDE Comprehensive Keyboard Shortcuts Restorer

Restores Cursor IDE custom keyboard shortcuts with robust, comprehensive, and exhaustive list.
Includes complete @FF (function keys) mapping and all custom shortcuts.

@JARVIS @CURSOR @IDE @FF @KEYBOARD @SHORTCUTS #COMPREHENSIVE #EXHAUSTIVE
"""

import sys
import json
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
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorShortcutsComprehensiveRestorer")


class JARVISCursorShortcutsComprehensiveRestorer:
    """
    Comprehensive Cursor IDE Keyboard Shortcuts Restorer

    Features:
    - Robust restoration from config
    - Comprehensive shortcut mapping
    - Exhaustive @FF (function keys) list
    - All custom shortcuts
    - Backup and restore functionality
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Cursor IDE paths (Windows)
        self.cursor_user_dir = Path.home() / "AppData" / "Roaming" / "Cursor" / "User"
        self.keybindings_file = self.cursor_user_dir / "keybindings.json"

        # Config paths
        self.config_dir = project_root / "config"
        self.shortcuts_config_file = self.config_dir / "cursor_ide_keyboard_shortcuts.json"
        self.backup_dir = project_root / "data" / "cursor_backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Ensure Cursor user directory exists
        self.cursor_user_dir.mkdir(parents=True, exist_ok=True)

    def get_comprehensive_shortcuts(self, use_comprehensive: bool = True) -> Dict[str, Any]:
        """
        Get comprehensive, exhaustive list of all keyboard shortcuts

        Args:
            use_comprehensive: If True, always use comprehensive defaults (enhances existing config)

        Returns:
            Complete shortcuts configuration with @FF mappings
        """
        # Always generate comprehensive defaults
        comprehensive = self._generate_comprehensive_shortcuts()

        # Try to load from config file and merge
        if self.shortcuts_config_file.exists() and not use_comprehensive:
            try:
                with open(self.shortcuts_config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    existing = config.get("cursor_ide_keyboard_shortcuts", {})
                    if existing:
                        # Merge existing with comprehensive (comprehensive takes precedence)
                        for key, value in comprehensive.items():
                            if isinstance(value, dict) and key in existing:
                                # Merge dictionaries
                                existing[key].update(value)
                            else:
                                existing[key] = value
                        self.logger.info(f"✅ Merged shortcuts: {len(existing)} categories")
                        return existing
            except Exception as e:
                self.logger.warning(f"⚠️  Failed to load config: {e}, using comprehensive defaults")

        # Use comprehensive defaults
        self.logger.info("📝 Using comprehensive default shortcuts...")
        return comprehensive

    def _generate_comprehensive_shortcuts(self) -> Dict[str, Any]:
        """Generate comprehensive, exhaustive shortcuts list"""

        return {
            # @FF - Function Keys (F1-F12)
            "function_keys": {
                "F1": {
                    "default": "Show Command Palette",
                    "alternate": "Help: Show All Commands",
                    "category": "navigation",
                    "command": "workbench.action.showCommands",
                    "note": "Primary command access"
                },
                "F2": {
                    "default": "Rename Symbol",
                    "alternate": "Rename Variable/Function",
                    "category": "editing",
                    "command": "editor.action.rename",
                    "note": "Quick rename"
                },
                "F3": {
                    "default": "Find Next",
                    "alternate": "Search Next",
                    "category": "search",
                    "command": "editor.action.nextMatchFindAction",
                    "note": "Search navigation"
                },
                "F4": {
                    "default": "Go to Definition",
                    "alternate": "Peek Definition",
                    "category": "navigation",
                    "command": "editor.action.revealDefinition",
                    "note": "Code navigation"
                },
                "F5": {
                    "default": "Start Debugging",
                    "alternate": "Continue Debugging",
                    "category": "debugging",
                    "command": "workbench.action.debug.start",
                    "note": "Debug control"
                },
                "F6": {
                    "default": "Step Over",
                    "alternate": "Debug Step Over",
                    "category": "debugging",
                    "command": "workbench.action.debug.stepOver",
                    "note": "Debug navigation"
                },
                "F7": {
                    "default": "Step Into",
                    "alternate": "Debug Step Into",
                    "category": "debugging",
                    "command": "workbench.action.debug.stepInto",
                    "note": "Debug navigation"
                },
                "F8": {
                    "default": "Step Out",
                    "alternate": "Debug Step Out",
                    "category": "debugging",
                    "command": "workbench.action.debug.stepOut",
                    "note": "Debug navigation"
                },
                "F9": {
                    "default": "Toggle Breakpoint",
                    "alternate": "Add/Remove Breakpoint",
                    "category": "debugging",
                    "command": "editor.debug.action.toggleBreakpoint",
                    "note": "Debug control"
                },
                "F10": {
                    "default": "Step Over (Alternative)",
                    "alternate": "Debug Step Over",
                    "category": "debugging",
                    "command": "workbench.action.debug.stepOver",
                    "note": "Alternative debug step"
                },
                "F11": {
                    "default": "Toggle Full Screen",
                    "alternate": "Full Screen Editor",
                    "category": "view",
                    "command": "workbench.action.toggleFullScreen",
                    "note": "View control"
                },
                "F12": {
                    "default": "Go to Definition",
                    "alternate": "Peek Definition",
                    "category": "navigation",
                    "command": "editor.action.revealDefinition",
                    "note": "Code navigation"
                }
            },

            # Function Key Combinations
            "function_key_combinations": {
                "Ctrl+F1": {
                    "action": "Show Command Palette",
                    "category": "navigation",
                    "command": "workbench.action.showCommands"
                },
                "Ctrl+F2": {
                    "action": "Rename All Occurrences",
                    "category": "editing",
                    "command": "editor.action.changeAll"
                },
                "Ctrl+F3": {
                    "action": "Find in Selection",
                    "category": "search",
                    "command": "editor.action.addSelectionToNextFindMatch"
                },
                "Ctrl+F4": {
                    "action": "Close Editor",
                    "category": "editing",
                    "command": "workbench.action.closeActiveEditor"
                },
                "Ctrl+F5": {
                    "action": "Restart Debugging",
                    "category": "debugging",
                    "command": "workbench.action.debug.restart"
                },
                "Ctrl+F9": {
                    "action": "Toggle Breakpoint (Conditional)",
                    "category": "debugging",
                    "command": "editor.debug.action.toggleBreakpoint"
                },
                "Ctrl+F12": {
                    "action": "Go to Implementation",
                    "category": "navigation",
                    "command": "editor.action.goToImplementation"
                },
                "Shift+F1": {
                    "action": "Show All Commands",
                    "category": "navigation",
                    "command": "workbench.action.showCommands"
                },
                "Shift+F2": {
                    "action": "Rename Symbol (All Files)",
                    "category": "editing",
                    "command": "editor.action.rename"
                },
                "Shift+F3": {
                    "action": "Find Previous",
                    "category": "search",
                    "command": "editor.action.previousMatchFindAction"
                },
                "Shift+F4": {
                    "action": "Peek Definition",
                    "category": "navigation",
                    "command": "editor.action.peekDefinition"
                },
                "Shift+F5": {
                    "action": "Stop Debugging",
                    "category": "debugging",
                    "command": "workbench.action.debug.stop"
                },
                "Shift+F9": {
                    "action": "Toggle Breakpoint (Conditional)",
                    "category": "debugging",
                    "command": "editor.debug.action.toggleBreakpoint"
                },
                "Shift+F12": {
                    "action": "Go to References",
                    "category": "navigation",
                    "command": "editor.action.goToReferences"
                },
                "Alt+F1": {
                    "action": "Show Accessibility Help",
                    "category": "accessibility",
                    "command": "editor.action.showAccessibilityHelp"
                },
                "Alt+F2": {
                    "action": "Select All Occurrences",
                    "category": "editing",
                    "command": "editor.action.selectHighlights"
                },
                "Alt+F3": {
                    "action": "Add Selection to Next Find Match",
                    "category": "search",
                    "command": "editor.action.addSelectionToNextFindMatch"
                },
                "Alt+F4": {
                    "action": "Close Window",
                    "category": "window",
                    "command": "workbench.action.closeWindow"
                },
                "Alt+F5": {
                    "action": "Restart Frame",
                    "category": "debugging",
                    "command": "workbench.action.debug.restartFrame"
                },
                "Alt+F12": {
                    "action": "Peek Implementation",
                    "category": "navigation",
                    "command": "editor.action.peekImplementation"
                }
            },

            # Cursor-Specific Shortcuts
            "cursor_specific_shortcuts": {
                "Ctrl+K Ctrl+S": {
                    "action": "Open Keyboard Shortcuts",
                    "category": "settings",
                    "command": "workbench.action.openGlobalKeybindings"
                },
                "Ctrl+K Ctrl+C": {
                    "action": "Open Composer",
                    "category": "ai",
                    "command": "cursor.composer.open"
                },
                "Ctrl+K Ctrl+K": {
                    "action": "Open Chat",
                    "category": "ai",
                    "command": "cursor.chat.open"
                },
                "Ctrl+K Ctrl+H": {
                    "action": "Chat History",
                    "category": "ai",
                    "command": "cursor.chat.history"
                },
                "Ctrl+K Ctrl+I": {
                    "action": "Inline Edit",
                    "category": "ai",
                    "command": "cursor.inlineEdit"
                },
                "Ctrl+K Ctrl+E": {
                    "action": "Explain Code",
                    "category": "ai",
                    "command": "cursor.explain"
                },
                "Ctrl+K Ctrl+R": {
                    "action": "Refactor Code",
                    "category": "ai",
                    "command": "cursor.refactor"
                },
                "Ctrl+K Ctrl+T": {
                    "action": "Generate Tests",
                    "category": "ai",
                    "command": "cursor.generateTests"
                },
                "Ctrl+L": {
                    "action": "Select Line",
                    "category": "editing",
                    "command": "expandLineSelection"
                },
                "Ctrl+Shift+L": {
                    "action": "Select All Occurrences",
                    "category": "editing",
                    "command": "editor.action.selectHighlights"
                },
                "Ctrl+D": {
                    "action": "Add Selection to Next Find Match",
                    "category": "editing",
                    "command": "editor.action.addSelectionToNextFindMatch"
                },
                "Ctrl+Shift+D": {
                    "action": "Duplicate Line",
                    "category": "editing",
                    "command": "editor.action.copyLinesDownAction"
                },
                "Ctrl+Enter": {
                    "action": "Send Chat Message",
                    "category": "ai",
                    "command": "cursor.chat.send"
                },
                "Ctrl+Shift+Enter": {
                    "action": "New Line Above",
                    "category": "editing",
                    "command": "editor.action.insertLineBefore"
                },
                "Ctrl+Alt+Enter": {
                    "action": "New Line Below",
                    "category": "editing",
                    "command": "editor.action.insertLineAfter"
                }
            },

            # AI-Specific Shortcuts
            "ai_specific_shortcuts": {
                "Ctrl+K": {
                    "action": "Cursor AI Command Palette",
                    "category": "ai",
                    "command": "cursor.ai.commandPalette"
                },
                "Ctrl+Shift+K": {
                    "action": "AI Chat Toggle",
                    "category": "ai",
                    "command": "cursor.chat.toggle"
                },
                "Ctrl+Alt+K": {
                    "action": "AI Composer Toggle",
                    "category": "ai",
                    "command": "cursor.composer.toggle"
                },
                "Ctrl+K Ctrl+A": {
                    "action": "AI: Accept All",
                    "category": "ai",
                    "command": "cursor.ai.acceptAll"
                },
                "Ctrl+K Ctrl+D": {
                    "action": "AI: Reject All",
                    "category": "ai",
                    "command": "cursor.ai.rejectAll"
                },
                "Ctrl+K Ctrl+N": {
                    "action": "AI: Next Suggestion",
                    "category": "ai",
                    "command": "cursor.ai.nextSuggestion"
                },
                "Ctrl+K Ctrl+P": {
                    "action": "AI: Previous Suggestion",
                    "category": "ai",
                    "command": "cursor.ai.previousSuggestion"
                }
            },

            # Standard VSCode Shortcuts
            "standard_shortcuts": {
                "Ctrl+P": {
                    "action": "Quick Open",
                    "category": "navigation",
                    "command": "workbench.action.quickOpen"
                },
                "Ctrl+Shift+P": {
                    "action": "Command Palette",
                    "category": "navigation",
                    "command": "workbench.action.showCommands"
                },
                "Ctrl+Shift+F": {
                    "action": "Search in Files",
                    "category": "search",
                    "command": "workbench.action.findInFiles"
                },
                "Ctrl+Shift+E": {
                    "action": "Explorer",
                    "category": "navigation",
                    "command": "workbench.view.explorer"
                },
                "Ctrl+Shift+G": {
                    "action": "Source Control",
                    "category": "git",
                    "command": "workbench.view.scm"
                },
                "Ctrl+Shift+D": {
                    "action": "Debug",
                    "category": "debugging",
                    "command": "workbench.view.debug"
                },
                "Ctrl+Shift+X": {
                    "action": "Extensions",
                    "category": "extensions",
                    "command": "workbench.view.extensions"
                },
                "Ctrl+B": {
                    "action": "Toggle Sidebar",
                    "category": "view",
                    "command": "workbench.action.toggleSidebarVisibility"
                },
                "Ctrl+`": {
                    "action": "Toggle Terminal",
                    "category": "terminal",
                    "command": "workbench.action.terminal.toggleTerminal"
                },
                "Ctrl+Shift+`": {
                    "action": "New Terminal",
                    "category": "terminal",
                    "command": "workbench.action.terminal.new"
                },
                "Ctrl+W": {
                    "action": "Close Editor",
                    "category": "editing",
                    "command": "workbench.action.closeActiveEditor"
                },
                "Ctrl+K W": {
                    "action": "Close All Editors",
                    "category": "editing",
                    "command": "workbench.action.closeAllEditors"
                },
                "Ctrl+Shift+W": {
                    "action": "Close Window",
                    "category": "window",
                    "command": "workbench.action.closeWindow"
                },
                "Ctrl+N": {
                    "action": "New File",
                    "category": "editing",
                    "command": "workbench.action.files.newUntitledFile"
                },
                "Ctrl+O": {
                    "action": "Open File",
                    "category": "editing",
                    "command": "workbench.action.files.openFile"
                },
                "Ctrl+S": {
                    "action": "Save",
                    "category": "editing",
                    "command": "workbench.action.files.save"
                },
                "Ctrl+Shift+S": {
                    "action": "Save As",
                    "category": "editing",
                    "command": "workbench.action.files.saveAs"
                },
                "Ctrl+K S": {
                    "action": "Save All",
                    "category": "editing",
                    "command": "workbench.action.files.saveAll"
                },
                "Ctrl+F": {
                    "action": "Find",
                    "category": "search",
                    "command": "actions.find"
                },
                "Ctrl+H": {
                    "action": "Replace",
                    "category": "search",
                    "command": "editor.action.startFindReplaceAction"
                },
                "Ctrl+Shift+F": {
                    "action": "Find in Files",
                    "category": "search",
                    "command": "workbench.action.findInFiles"
                },
                "Ctrl+Shift+H": {
                    "action": "Replace in Files",
                    "category": "search",
                    "command": "workbench.action.replaceInFiles"
                },
                "Ctrl+G": {
                    "action": "Go to Line",
                    "category": "navigation",
                    "command": "workbench.action.gotoLine"
                },
                "Ctrl+Shift+O": {
                    "action": "Go to Symbol",
                    "category": "navigation",
                    "command": "workbench.action.gotoSymbol"
                },
                "Ctrl+T": {
                    "action": "Go to Symbol in Workspace",
                    "category": "navigation",
                    "command": "workbench.action.showAllSymbols"
                },
                "Ctrl+Shift+T": {
                    "action": "Reopen Closed Editor",
                    "category": "navigation",
                    "command": "workbench.action.reopenClosedEditor"
                },
                "Ctrl+K Ctrl+Z": {
                    "action": "Toggle Zen Mode",
                    "category": "view",
                    "command": "workbench.action.toggleZenMode"
                },
                "Ctrl+K U": {
                    "action": "Unfold All",
                    "category": "editing",
                    "command": "editor.unfoldAll"
                },
                "Ctrl+K J": {
                    "action": "Fold All",
                    "category": "editing",
                    "command": "editor.foldAll"
                },
                "Ctrl+K Ctrl+0": {
                    "action": "Fold All Regions",
                    "category": "editing",
                    "command": "editor.foldAllMarkerRegions"
                },
                "Ctrl+K Ctrl+J": {
                    "action": "Unfold All Regions",
                    "category": "editing",
                    "command": "editor.unfoldAllMarkerRegions"
                },
                "Ctrl+/": {
                    "action": "Toggle Line Comment",
                    "category": "editing",
                    "command": "editor.action.commentLine"
                },
                "Ctrl+Shift+A": {
                    "action": "Toggle Block Comment",
                    "category": "editing",
                    "command": "editor.action.blockComment"
                },
                "Ctrl+Shift+K": {
                    "action": "Delete Line",
                    "category": "editing",
                    "command": "editor.action.deleteLines"
                },
                "Ctrl+Enter": {
                    "action": "Insert Line Below",
                    "category": "editing",
                    "command": "editor.action.insertLineAfter"
                },
                "Ctrl+Shift+Enter": {
                    "action": "Insert Line Above",
                    "category": "editing",
                    "command": "editor.action.insertLineBefore"
                },
                "Alt+Up": {
                    "action": "Move Line Up",
                    "category": "editing",
                    "command": "editor.action.moveLinesUpAction"
                },
                "Alt+Down": {
                    "action": "Move Line Down",
                    "category": "editing",
                    "command": "editor.action.moveLinesDownAction"
                },
                "Shift+Alt+Up": {
                    "action": "Copy Line Up",
                    "category": "editing",
                    "command": "editor.action.copyLinesUpAction"
                },
                "Shift+Alt+Down": {
                    "action": "Copy Line Down",
                    "category": "editing",
                    "command": "editor.action.copyLinesDownAction"
                },
                "Ctrl+Shift+\\": {
                    "action": "Jump to Matching Bracket",
                    "category": "navigation",
                    "command": "editor.action.jumpToBracket"
                },
                "Ctrl+]": {
                    "action": "Indent Line",
                    "category": "editing",
                    "command": "editor.action.indentLines"
                },
                "Ctrl+[": {
                    "action": "Outdent Line",
                    "category": "editing",
                    "command": "editor.action.outdentLines"
                },
                "Home": {
                    "action": "Go to Beginning of Line",
                    "category": "navigation",
                    "command": "cursorHome"
                },
                "End": {
                    "action": "Go to End of Line",
                    "category": "navigation",
                    "command": "cursorEnd"
                },
                "Ctrl+Home": {
                    "action": "Go to Beginning of File",
                    "category": "navigation",
                    "command": "cursorTop"
                },
                "Ctrl+End": {
                    "action": "Go to End of File",
                    "category": "navigation",
                    "command": "cursorBottom"
                },
                "Ctrl+Up": {
                    "action": "Scroll Line Up",
                    "category": "view",
                    "command": "scrollLineUp"
                },
                "Ctrl+Down": {
                    "action": "Scroll Line Down",
                    "category": "view",
                    "command": "scrollLineDown"
                },
                "PageUp": {
                    "action": "Scroll Page Up",
                    "category": "view",
                    "command": "scrollPageUp"
                },
                "PageDown": {
                    "action": "Scroll Page Down",
                    "category": "view",
                    "command": "scrollPageDown"
                },
                "Ctrl+PageUp": {
                    "action": "Go to Previous Editor",
                    "category": "navigation",
                    "command": "workbench.action.previousEditor"
                },
                "Ctrl+PageDown": {
                    "action": "Go to Next Editor",
                    "category": "navigation",
                    "command": "workbench.action.nextEditor"
                },
                "Alt+Left": {
                    "action": "Go Back",
                    "category": "navigation",
                    "command": "workbench.action.navigateBack"
                },
                "Alt+Right": {
                    "action": "Go Forward",
                    "category": "navigation",
                    "command": "workbench.action.navigateForward"
                },
                "Ctrl+Shift+Tab": {
                    "action": "Previous Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.previousEditorInGroup"
                },
                "Ctrl+Tab": {
                    "action": "Next Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.nextEditorInGroup"
                },
                "Ctrl+K Ctrl+W": {
                    "action": "Close All Editors",
                    "category": "editing",
                    "command": "workbench.action.closeAllEditors"
                },
                "Ctrl+K Ctrl+Shift+W": {
                    "action": "Close All Editor Groups",
                    "category": "editing",
                    "command": "workbench.action.closeAllGroups"
                },
                "Ctrl+K Ctrl+Left": {
                    "action": "Focus Previous Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusPreviousGroup"
                },
                "Ctrl+K Ctrl+Right": {
                    "action": "Focus Next Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusNextGroup"
                },
                "Ctrl+1": {
                    "action": "Focus First Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusFirstEditorGroup"
                },
                "Ctrl+2": {
                    "action": "Focus Second Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusSecondEditorGroup"
                },
                "Ctrl+3": {
                    "action": "Focus Third Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusThirdEditorGroup"
                },
                "Ctrl+K Ctrl+1": {
                    "action": "Focus First Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusFirstEditorGroup"
                },
                "Ctrl+K Ctrl+2": {
                    "action": "Focus Second Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusSecondEditorGroup"
                },
                "Ctrl+K Ctrl+3": {
                    "action": "Focus Third Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusThirdEditorGroup"
                },
                "Ctrl+\\": {
                    "action": "Split Editor",
                    "category": "view",
                    "command": "workbench.action.splitEditor"
                },
                "Ctrl+K Ctrl+\\": {
                    "action": "Split Editor Right",
                    "category": "view",
                    "command": "workbench.action.splitEditorRight"
                },
                "Ctrl+K Ctrl+Shift+\\": {
                    "action": "Join Editor Group",
                    "category": "view",
                    "command": "workbench.action.joinEditorGroup"
                },
                "Ctrl+K Ctrl+Up": {
                    "action": "Move Editor Up",
                    "category": "view",
                    "command": "workbench.action.moveEditorToAboveGroup"
                },
                "Ctrl+K Ctrl+Down": {
                    "action": "Move Editor Down",
                    "category": "view",
                    "command": "workbench.action.moveEditorToBelowGroup"
                },
                "Ctrl+K Ctrl+Left": {
                    "action": "Move Editor Left",
                    "category": "view",
                    "command": "workbench.action.moveEditorToLeftGroup"
                },
                "Ctrl+K Ctrl+Right": {
                    "action": "Move Editor Right",
                    "category": "view",
                    "command": "workbench.action.moveEditorToRightGroup"
                },
                "Ctrl+Shift+N": {
                    "action": "New Window",
                    "category": "window",
                    "command": "workbench.action.newWindow"
                },
                "Ctrl+Shift+W": {
                    "action": "Close Window",
                    "category": "window",
                    "command": "workbench.action.closeWindow"
                },
                "Ctrl+K M": {
                    "action": "Change Language Mode",
                    "category": "editing",
                    "command": "workbench.action.editor.changeLanguageMode"
                },
                "Ctrl+K Ctrl+X": {
                    "action": "Trim Trailing Whitespace",
                    "category": "editing",
                    "command": "editor.action.trimTrailingWhitespace"
                },
                "Ctrl+K M": {
                    "action": "Change Language Mode",
                    "category": "editing",
                    "command": "workbench.action.editor.changeLanguageMode"
                },
                "Ctrl+K Ctrl+P": {
                    "action": "Copy Path of Active File",
                    "category": "file",
                    "command": "copyFilePath"
                },
                "Ctrl+K P": {
                    "action": "Copy Relative Path of Active File",
                    "category": "file",
                    "command": "copyRelativeFilePath"
                },
                "Ctrl+R": {
                    "action": "Open Recent",
                    "category": "navigation",
                    "command": "workbench.action.openRecent"
                },
                "Ctrl+K Ctrl+R": {
                    "action": "Reveal in File Explorer",
                    "category": "file",
                    "command": "revealFileInOS"
                },
                "Ctrl+K Ctrl+E": {
                    "action": "Focus Files Explorer",
                    "category": "navigation",
                    "command": "workbench.files.action.focusFilesExplorer"
                },
                "Ctrl+Shift+E": {
                    "action": "Focus Explorer",
                    "category": "navigation",
                    "command": "workbench.view.explorer"
                },
                "Ctrl+Shift+F": {
                    "action": "Focus Search",
                    "category": "search",
                    "command": "workbench.view.search"
                },
                "Ctrl+Shift+G": {
                    "action": "Focus Source Control",
                    "category": "git",
                    "command": "workbench.view.scm"
                },
                "Ctrl+Shift+D": {
                    "action": "Focus Debug",
                    "category": "debugging",
                    "command": "workbench.view.debug"
                },
                "Ctrl+Shift+X": {
                    "action": "Focus Extensions",
                    "category": "extensions",
                    "command": "workbench.view.extensions"
                },
                "Ctrl+Shift+J": {
                    "action": "Toggle Search Details",
                    "category": "search",
                    "command": "workbench.action.search.toggleQueryDetails"
                },
                "Ctrl+Shift+C": {
                    "action": "Open New Command Prompt",
                    "category": "terminal",
                    "command": "workbench.action.terminal.new"
                },
                "Ctrl+Shift+U": {
                    "action": "Show Output",
                    "category": "view",
                    "command": "workbench.action.output.toggleOutput"
                },
                "Ctrl+Shift+M": {
                    "action": "Show Problems",
                    "category": "view",
                    "command": "workbench.actions.view.problems"
                },
                "Ctrl+Shift+Y": {
                    "action": "Toggle Debug Console",
                    "category": "debugging",
                    "command": "workbench.debug.action.toggleRepl"
                },
                "Ctrl+U": {
                    "action": "Undo Last Cursor Operation",
                    "category": "editing",
                    "command": "cursorUndo"
                },
                "Ctrl+Shift+Z": {
                    "action": "Redo",
                    "category": "editing",
                    "command": "redo"
                },
                "Ctrl+Y": {
                    "action": "Redo",
                    "category": "editing",
                    "command": "redo"
                },
                "Ctrl+X": {
                    "action": "Cut",
                    "category": "editing",
                    "command": "editor.action.clipboardCutAction"
                },
                "Ctrl+C": {
                    "action": "Copy",
                    "category": "editing",
                    "command": "editor.action.clipboardCopyAction"
                },
                "Ctrl+V": {
                    "action": "Paste",
                    "category": "editing",
                    "command": "editor.action.clipboardPasteAction"
                },
                "Ctrl+Shift+V": {
                    "action": "Paste and Indent",
                    "category": "editing",
                    "command": "editor.action.clipboardPasteAction"
                },
                "Ctrl+A": {
                    "action": "Select All",
                    "category": "editing",
                    "command": "editor.action.selectAll"
                },
                "Ctrl+K Ctrl+X": {
                    "action": "Trim Trailing Whitespace",
                    "category": "editing",
                    "command": "editor.action.trimTrailingWhitespace"
                },
                "Ctrl+K M": {
                    "action": "Change Language Mode",
                    "category": "editing",
                    "command": "workbench.action.editor.changeLanguageMode"
                },
                "Ctrl+K Ctrl+W": {
                    "action": "Close All Editors",
                    "category": "editing",
                    "command": "workbench.action.closeAllEditors"
                },
                "Ctrl+K Ctrl+Shift+W": {
                    "action": "Close All Editor Groups",
                    "category": "editing",
                    "command": "workbench.action.closeAllGroups"
                },
                "Ctrl+K Ctrl+Up": {
                    "action": "Move Editor Up",
                    "category": "view",
                    "command": "workbench.action.moveEditorToAboveGroup"
                },
                "Ctrl+K Ctrl+Down": {
                    "action": "Move Editor Down",
                    "category": "view",
                    "command": "workbench.action.moveEditorToBelowGroup"
                },
                "Ctrl+K Ctrl+Left": {
                    "action": "Move Editor Left",
                    "category": "view",
                    "command": "workbench.action.moveEditorToLeftGroup"
                },
                "Ctrl+K Ctrl+Right": {
                    "action": "Move Editor Right",
                    "category": "view",
                    "command": "workbench.action.moveEditorToRightGroup"
                },
                "Ctrl+K Ctrl+1": {
                    "action": "Focus First Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusFirstEditorGroup"
                },
                "Ctrl+K Ctrl+2": {
                    "action": "Focus Second Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusSecondEditorGroup"
                },
                "Ctrl+K Ctrl+3": {
                    "action": "Focus Third Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusThirdEditorGroup"
                },
                "Ctrl+K Ctrl+\\": {
                    "action": "Split Editor Right",
                    "category": "view",
                    "command": "workbench.action.splitEditorRight"
                },
                "Ctrl+K Ctrl+Shift+\\": {
                    "action": "Join Editor Group",
                    "category": "view",
                    "command": "workbench.action.joinEditorGroup"
                },
                "Ctrl+K Ctrl+Z": {
                    "action": "Toggle Zen Mode",
                    "category": "view",
                    "command": "workbench.action.toggleZenMode"
                },
                "Ctrl+K U": {
                    "action": "Unfold All",
                    "category": "editing",
                    "command": "editor.unfoldAll"
                },
                "Ctrl+K J": {
                    "action": "Fold All",
                    "category": "editing",
                    "command": "editor.foldAll"
                },
                "Ctrl+K Ctrl+0": {
                    "action": "Fold All Regions",
                    "category": "editing",
                    "command": "editor.foldAllMarkerRegions"
                },
                "Ctrl+K Ctrl+J": {
                    "action": "Unfold All Regions",
                    "category": "editing",
                    "command": "editor.unfoldAllMarkerRegions"
                },
                "Ctrl+K Ctrl+S": {
                    "action": "Open Keyboard Shortcuts",
                    "category": "settings",
                    "command": "workbench.action.openGlobalKeybindings"
                },
                "Ctrl+K Ctrl+T": {
                    "action": "Select Color Theme",
                    "category": "settings",
                    "command": "workbench.action.selectTheme"
                },
                "Ctrl+K Ctrl+P": {
                    "action": "Copy Path of Active File",
                    "category": "file",
                    "command": "copyFilePath"
                },
                "Ctrl+K P": {
                    "action": "Copy Relative Path of Active File",
                    "category": "file",
                    "command": "copyRelativeFilePath"
                },
                "Ctrl+K Ctrl+R": {
                    "action": "Reveal in File Explorer",
                    "category": "file",
                    "command": "revealFileInOS"
                },
                "Ctrl+K Ctrl+E": {
                    "action": "Focus Files Explorer",
                    "category": "navigation",
                    "command": "workbench.files.action.focusFilesExplorer"
                },
                "Ctrl+K Ctrl+M": {
                    "action": "Change Language Mode",
                    "category": "editing",
                    "command": "workbench.action.editor.changeLanguageMode"
                },
                "Ctrl+K Ctrl+W": {
                    "action": "Close All Editors",
                    "category": "editing",
                    "command": "workbench.action.closeAllEditors"
                },
                "Ctrl+K Ctrl+Shift+W": {
                    "action": "Close All Editor Groups",
                    "category": "editing",
                    "command": "workbench.action.closeAllGroups"
                },
                "Ctrl+K Ctrl+Up": {
                    "action": "Move Editor Up",
                    "category": "view",
                    "command": "workbench.action.moveEditorToAboveGroup"
                },
                "Ctrl+K Ctrl+Down": {
                    "action": "Move Editor Down",
                    "category": "view",
                    "command": "workbench.action.moveEditorToBelowGroup"
                },
                "Ctrl+K Ctrl+Left": {
                    "action": "Move Editor Left",
                    "category": "view",
                    "command": "workbench.action.moveEditorToLeftGroup"
                },
                "Ctrl+K Ctrl+Right": {
                    "action": "Move Editor Right",
                    "category": "view",
                    "command": "workbench.action.moveEditorToRightGroup"
                },
                "Ctrl+K Ctrl+1": {
                    "action": "Focus First Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusFirstEditorGroup"
                },
                "Ctrl+K Ctrl+2": {
                    "action": "Focus Second Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusSecondEditorGroup"
                },
                "Ctrl+K Ctrl+3": {
                    "action": "Focus Third Editor Group",
                    "category": "navigation",
                    "command": "workbench.action.focusThirdEditorGroup"
                },
                "Ctrl+K Ctrl+\\": {
                    "action": "Split Editor Right",
                    "category": "view",
                    "command": "workbench.action.splitEditorRight"
                },
                "Ctrl+K Ctrl+Shift+\\": {
                    "action": "Join Editor Group",
                    "category": "view",
                    "command": "workbench.action.joinEditorGroup"
                },
                "Ctrl+K Ctrl+Z": {
                    "action": "Toggle Zen Mode",
                    "category": "view",
                    "command": "workbench.action.toggleZenMode"
                },
                "Ctrl+K U": {
                    "action": "Unfold All",
                    "category": "editing",
                    "command": "editor.unfoldAll"
                },
                "Ctrl+K J": {
                    "action": "Fold All",
                    "category": "editing",
                    "command": "editor.foldAll"
                },
                "Ctrl+K Ctrl+0": {
                    "action": "Fold All Regions",
                    "category": "editing",
                    "command": "editor.foldAllMarkerRegions"
                },
                "Ctrl+K Ctrl+J": {
                    "action": "Unfold All Regions",
                    "category": "editing",
                    "command": "editor.unfoldAllMarkerRegions"
                },
                "Ctrl+K Ctrl+S": {
                    "action": "Open Keyboard Shortcuts",
                    "category": "settings",
                    "command": "workbench.action.openGlobalKeybindings"
                },
                "Ctrl+K Ctrl+T": {
                    "action": "Select Color Theme",
                    "category": "settings",
                    "command": "workbench.action.selectTheme"
                },
                "Ctrl+K Ctrl+P": {
                    "action": "Copy Path of Active File",
                    "category": "file",
                    "command": "copyFilePath"
                },
                "Ctrl+K P": {
                    "action": "Copy Relative Path of Active File",
                    "category": "file",
                    "command": "copyRelativeFilePath"
                },
                "Ctrl+K Ctrl+R": {
                    "action": "Reveal in File Explorer",
                    "category": "file",
                    "command": "revealFileInOS"
                },
                "Ctrl+K Ctrl+E": {
                    "action": "Focus Files Explorer",
                    "category": "navigation",
                    "command": "workbench.files.action.focusFilesExplorer"
                },
                "Ctrl+K Ctrl+M": {
                    "action": "Change Language Mode",
                    "category": "editing",
                    "command": "workbench.action.editor.changeLanguageMode"
                }
            },

            # Hardware Conflicts
            "hardware_conflicts": {
                "F1": {
                    "hardware_action": "Help (Windows)",
                    "ide_action": "Show Command Palette",
                    "conflict": "Windows Help vs IDE Command",
                    "solution": "Use Ctrl+Shift+P for Command Palette",
                    "note": "F1 may trigger Windows Help"
                },
                "F4": {
                    "hardware_action": "Close Window (Alt+F4)",
                    "ide_action": "Go to Definition",
                    "conflict": "Alt+F4 closes window",
                    "solution": "Use Ctrl+Click or F12 for Go to Definition",
                    "note": "Alt+F4 is system-level close"
                },
                "F11": {
                    "hardware_action": "Full Screen (Browser)",
                    "ide_action": "Toggle Full Screen",
                    "conflict": "Browser full screen vs IDE full screen",
                    "solution": "Use Ctrl+K Ctrl+Z for Zen Mode",
                    "note": "F11 may trigger browser full screen"
                }
            },

            # Customization
            "customization": {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "total_shortcuts": 0,  # Will be calculated
                "categories": [
                    "navigation",
                    "editing",
                    "search",
                    "debugging",
                    "view",
                    "ai",
                    "settings",
                    "file",
                    "git",
                    "terminal",
                    "extensions",
                    "window",
                    "accessibility"
                ],
                "tags": ["@JARVIS", "@CURSOR", "@IDE", "@FF", "@KEYBOARD", "@SHORTCUTS"]
            }
        }

    def backup_current_keybindings(self) -> bool:
        """Backup current keybindings before restoration"""
        try:
            if self.keybindings_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_dir / f"keybindings_backup_{timestamp}.json"
                shutil.copy2(self.keybindings_file, backup_file)
                self.logger.info(f"✅ Backed up current keybindings to: {backup_file}")
                return True
            else:
                self.logger.info("ℹ️  No existing keybindings file to backup")
                return True
        except Exception as e:
            self.logger.error(f"❌ Failed to backup keybindings: {e}")
            return False

    def convert_to_keybindings_format(self, shortcuts: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Convert comprehensive shortcuts to VSCode/Cursor keybindings.json format"""
        keybindings = []

        # Function Keys (@FF)
        function_keys = shortcuts.get("function_keys", {})
        for key, info in function_keys.items():
            keybindings.append({
                "key": key.lower(),
                "command": info.get("command", ""),
                "when": "editorTextFocus" if info.get("category") in ["editing", "navigation"] else None
            })

        # Function Key Combinations
        function_combinations = shortcuts.get("function_key_combinations", {})
        for combo, info in function_combinations.items():
            keybindings.append({
                "key": combo.lower().replace("ctrl", "ctrl").replace("shift", "shift").replace("alt", "alt"),
                "command": info.get("command", ""),
                "when": "editorTextFocus" if info.get("category") in ["editing", "navigation"] else None
            })

        # Cursor-Specific Shortcuts
        cursor_shortcuts = shortcuts.get("cursor_specific_shortcuts", {})
        for combo, info in cursor_shortcuts.items():
            keybindings.append({
                "key": combo.lower().replace("ctrl", "ctrl").replace("shift", "shift").replace("alt", "alt"),
                "command": info.get("command", ""),
                "when": None  # Cursor shortcuts work globally
            })

        # AI-Specific Shortcuts
        ai_shortcuts = shortcuts.get("ai_specific_shortcuts", {})
        for combo, info in ai_shortcuts.items():
            keybindings.append({
                "key": combo.lower().replace("ctrl", "ctrl").replace("shift", "shift").replace("alt", "alt"),
                "command": info.get("command", ""),
                "when": None  # AI shortcuts work globally
            })

        # Standard Shortcuts
        standard_shortcuts = shortcuts.get("standard_shortcuts", {})
        for combo, info in standard_shortcuts.items():
            keybindings.append({
                "key": combo.lower().replace("ctrl", "ctrl").replace("shift", "shift").replace("alt", "alt"),
                "command": info.get("command", ""),
                "when": self._get_when_clause(info.get("category", "global"))
            })

        return keybindings

    def _get_when_clause(self, category: str) -> Optional[str]:
        """Get VSCode when clause from category"""
        when_mappings = {
            "global": None,
            "editing": "editorTextFocus",
            "navigation": "editorTextFocus",
            "search": "searchViewletFocus || editorTextFocus",
            "debugging": "debugMode || !debugMode",
            "view": None,
            "ai": None,
            "settings": None,
            "file": None,
            "git": "scmRepository",
            "terminal": "terminalFocus",
            "extensions": None,
            "window": None,
            "accessibility": None
        }
        return when_mappings.get(category.lower())

    def restore_keybindings(self, merge: bool = True) -> bool:
        """
        Restore comprehensive keybindings

        Args:
            merge: If True, merge with existing. If False, replace.
        """
        try:
            # Backup current
            self.backup_current_keybindings()

            # Get comprehensive shortcuts (always use comprehensive)
            shortcuts = self.get_comprehensive_shortcuts(use_comprehensive=True)

            # Convert to keybindings format
            new_keybindings = self.convert_to_keybindings_format(shortcuts)

            # Load existing if merging
            existing_keybindings = []
            if merge and self.keybindings_file.exists():
                try:
                    with open(self.keybindings_file, 'r', encoding='utf-8') as f:
                        existing_keybindings = json.load(f)
                        if not isinstance(existing_keybindings, list):
                            existing_keybindings = []
                except Exception as e:
                    self.logger.warning(f"⚠️  Failed to load existing: {e}")

            # Merge or replace
            if merge:
                existing_map = {kb.get("key", ""): kb for kb in existing_keybindings}
                for kb in new_keybindings:
                    key = kb.get("key", "")
                    if key in existing_map:
                        existing_map[key].update(kb)
                    else:
                        existing_keybindings.append(kb)
                final_keybindings = existing_keybindings
            else:
                final_keybindings = new_keybindings

            # Ensure directory exists
            self.keybindings_file.parent.mkdir(parents=True, exist_ok=True)

            # Write keybindings
            with open(self.keybindings_file, 'w', encoding='utf-8') as f:
                json.dump(final_keybindings, f, indent=2, ensure_ascii=False)

            # Save comprehensive config
            with open(self.shortcuts_config_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "cursor_ide_keyboard_shortcuts": shortcuts,
                    "version": "1.0.0",
                    "last_updated": datetime.now().isoformat(),
                    "total_shortcuts": len(final_keybindings)
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Restored {len(final_keybindings)} keybindings")
            self.logger.info(f"   Saved to: {self.keybindings_file}")
            self.logger.info(f"   Config saved to: {self.shortcuts_config_file}")

            return True

        except Exception as e:
            self.logger.error(f"❌ Failed to restore keybindings: {e}", exc_info=True)
            return False

    def generate_documentation(self) -> Optional[Path]:
        """Generate comprehensive shortcuts documentation"""
        try:
            shortcuts = self.get_comprehensive_shortcuts()

            docs_dir = self.project_root / "docs" / "system"
            docs_dir.mkdir(parents=True, exist_ok=True)
            doc_file = docs_dir / "CURSOR_IDE_KEYBOARD_SHORTCUTS_COMPREHENSIVE.md"

            with open(doc_file, 'w', encoding='utf-8') as f:
                f.write("# Cursor IDE Keyboard Shortcuts - Comprehensive Reference\n\n")
                f.write(f"**Generated**: {datetime.now().isoformat()}\n\n")
                f.write("## Overview\n\n")
                f.write("Complete, exhaustive mapping of all Cursor IDE keyboard shortcuts including @FF (function keys).\n\n")

                # @FF Function Keys
                f.write("## @FF - Function Keys (F1-F12)\n\n")
                function_keys = shortcuts.get("function_keys", {})
                for key, info in sorted(function_keys.items()):
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Default**: {info.get('default', 'N/A')}\n")
                    f.write(f"- **Alternate**: {info.get('alternate', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n")
                    f.write(f"- **Command**: `{info.get('command', 'N/A')}`\n")
                    if info.get('note'):
                        f.write(f"- **Note**: {info.get('note')}\n")
                    f.write("\n")

                # Function Key Combinations
                f.write("## Function Key Combinations\n\n")
                combinations = shortcuts.get("function_key_combinations", {})
                for combo, info in sorted(combinations.items()):
                    f.write(f"### `{combo}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n")
                    f.write(f"- **Command**: `{info.get('command', 'N/A')}`\n\n")

                # Cursor-Specific
                f.write("## Cursor-Specific Shortcuts\n\n")
                cursor = shortcuts.get("cursor_specific_shortcuts", {})
                for combo, info in sorted(cursor.items()):
                    f.write(f"### `{combo}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n")
                    f.write(f"- **Command**: `{info.get('command', 'N/A')}`\n\n")

                # AI-Specific
                f.write("## AI-Specific Shortcuts\n\n")
                ai = shortcuts.get("ai_specific_shortcuts", {})
                for combo, info in sorted(ai.items()):
                    f.write(f"### `{combo}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n")
                    f.write(f"- **Command**: `{info.get('command', 'N/A')}`\n\n")

                # Standard Shortcuts
                f.write("## Standard Shortcuts\n\n")
                standard = shortcuts.get("standard_shortcuts", {})
                for combo, info in sorted(standard.items()):
                    f.write(f"### `{combo}`\n")
                    f.write(f"- **Action**: {info.get('action', 'N/A')}\n")
                    f.write(f"- **Category**: {info.get('category', 'N/A')}\n")
                    f.write(f"- **Command**: `{info.get('command', 'N/A')}`\n\n")

                # Hardware Conflicts
                f.write("## Hardware Conflicts\n\n")
                conflicts = shortcuts.get("hardware_conflicts", {})
                for key, info in sorted(conflicts.items()):
                    f.write(f"### `{key}`\n")
                    f.write(f"- **Hardware Action**: {info.get('hardware_action', 'N/A')}\n")
                    f.write(f"- **IDE Action**: {info.get('ide_action', 'N/A')}\n")
                    f.write(f"- **Conflict**: {info.get('conflict', 'N/A')}\n")
                    f.write(f"- **Solution**: {info.get('solution', 'N/A')}\n")
                    if info.get('note'):
                        f.write(f"- **Note**: {info.get('note')}\n")
                    f.write("\n")

            self.logger.info(f"✅ Generated documentation: {doc_file}")
            return doc_file

        except Exception as e:
            self.logger.error(f"❌ Failed to generate documentation: {e}")
            return None


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Cursor IDE Comprehensive Keyboard Shortcuts Restorer")
        parser.add_argument("--restore", action="store_true", help="Restore keybindings")
        parser.add_argument("--replace", action="store_true", help="Replace existing keybindings (don't merge)")
        parser.add_argument("--backup", action="store_true", help="Backup current keybindings")
        parser.add_argument("--docs", action="store_true", help="Generate documentation")
        parser.add_argument("--list", action="store_true", help="List all shortcuts")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        restorer = JARVISCursorShortcutsComprehensiveRestorer(project_root)

        if args.backup:
            restorer.backup_current_keybindings()

        if args.restore:
            merge = not args.replace
            success = restorer.restore_keybindings(merge=merge)
            if success:
                print("✅ Keyboard shortcuts restored successfully")
            else:
                print("❌ Failed to restore keyboard shortcuts")

        if args.docs:
            doc_file = restorer.generate_documentation()
            if doc_file:
                print(f"✅ Documentation generated: {doc_file}")
            else:
                print("❌ Failed to generate documentation")

        if args.list:
            shortcuts = restorer.get_comprehensive_shortcuts()
            print("\n" + "="*80)
            print("CURSOR IDE KEYBOARD SHORTCUTS - COMPREHENSIVE LIST")
            print("="*80)

            # Count shortcuts
            total = 0
            total += len(shortcuts.get("function_keys", {}))
            total += len(shortcuts.get("function_key_combinations", {}))
            total += len(shortcuts.get("cursor_specific_shortcuts", {}))
            total += len(shortcuts.get("ai_specific_shortcuts", {}))
            total += len(shortcuts.get("standard_shortcuts", {}))

            print(f"\nTotal Shortcuts: {total}")
            print(f"  @FF Function Keys: {len(shortcuts.get('function_keys', {}))}")
            print(f"  Function Key Combinations: {len(shortcuts.get('function_key_combinations', {}))}")
            print(f"  Cursor-Specific: {len(shortcuts.get('cursor_specific_shortcuts', {}))}")
            print(f"  AI-Specific: {len(shortcuts.get('ai_specific_shortcuts', {}))}")
            print(f"  Standard: {len(shortcuts.get('standard_shortcuts', {}))}")
            print("="*80)

        if not any([args.restore, args.backup, args.docs, args.list]):
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()