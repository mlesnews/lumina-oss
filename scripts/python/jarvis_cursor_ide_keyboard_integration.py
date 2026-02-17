#!/usr/bin/env python3
"""
JARVIS-Cursor IDE Keyboard Integration
MANUS Framework - Complete IDE Control via Keyboard Shortcuts

Full integration between JARVIS Full-Time Super Agent and Cursor IDE,
enabling complete keyboard-based control with no mouse clicking required.

Features:
- JARVIS voice/text command processing
- Complete keyboard shortcut mapping for ALL Cursor IDE commands
- Natural language command parsing
- Intelligent command routing (shortcut → command palette → fallback)
- MANUS keyboard execution
- Intuitive human-friendly aliases

@JARVIS @MANUS @SYPHON
"""

import sys
import json
import time
import threading
import queue
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISCursorIDEKeyboardIntegration")

# Import components
try:
    from cursor_ide_keyboard_controller import CursorIDEKeyboardController, ShortcutResult
    KEYBOARD_CONTROLLER_AVAILABLE = True
except ImportError:
    KEYBOARD_CONTROLLER_AVAILABLE = False
    logger.warning("Cursor IDE Keyboard Controller not available")

try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    logger.warning("JARVIS Full-Time Super Agent not available")

try:
    from jarvis_ide_interaction_learner import get_ide_learner, IDEInteraction
    LEARNER_AVAILABLE = True
except ImportError:
    LEARNER_AVAILABLE = False
    logger.warning("IDE Interaction Learner not available")

try:
    from manus_cursor_controller import ManusCursorController
    MANUS_AVAILABLE = True
except ImportError:
    MANUS_AVAILABLE = False
    logger.warning("MANUS Cursor Controller not available")


@dataclass
class CommandExecutionResult:
    """Result of command execution"""
    success: bool
    method: str  # "keyboard_shortcut", "command_palette", "manus", "fallback"
    command: str
    execution_time: float
    error: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ParsedCommand:
    """Parsed natural language command"""
    intent: str
    action: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 1.0
    original_command: str = ""


class JARVISCursorIDEKeyboardIntegration:
    """
    JARVIS-Cursor IDE Keyboard Integration

    Complete integration enabling JARVIS to control Cursor IDE
    via keyboard shortcuts with natural language commands.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize components
        self.keyboard_controller = None
        if KEYBOARD_CONTROLLER_AVAILABLE:
            try:
                self.keyboard_controller = CursorIDEKeyboardController()
                logger.info("✅ Keyboard controller initialized")
            except Exception as e:
                logger.warning(f"Keyboard controller initialization failed: {e}")

        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root=self.project_root)
                logger.info("✅ JARVIS initialized")
            except Exception as e:
                logger.warning(f"JARVIS initialization failed: {e}")

        self.manus_controller = None
        if MANUS_AVAILABLE:
            try:
                self.manus_controller = ManusCursorController()
                logger.info("✅ MANUS controller initialized")
            except Exception as e:
                logger.warning(f"MANUS controller initialization failed: {e}")

        # Interaction learner
        self.learner = None
        if LEARNER_AVAILABLE:
            try:
                self.learner = get_ide_learner(project_root=self.project_root)
                logger.info("✅ Interaction learner initialized")
            except Exception as e:
                logger.warning(f"Interaction learner initialization failed: {e}")

        # Command queue for async execution
        self.command_queue = queue.Queue()
        self.execution_thread = threading.Thread(target=self._command_execution_loop, daemon=True)
        self.execution_thread.start()

        # Enhanced command mappings
        self.command_mappings = self._build_enhanced_command_mappings()

        # Load command palette commands from config
        self.palette_commands = self._load_palette_commands()

        # Natural language patterns
        self.nl_patterns = self._build_natural_language_patterns()

        logger.info("✅ JARVIS-Cursor IDE Keyboard Integration initialized")
        logger.info("   Complete keyboard control - no mouse required")
        logger.info("   Natural language → Keyboard shortcuts")

    def _build_enhanced_command_mappings(self) -> Dict[str, Dict[str, Any]]:
        """Build enhanced command mappings with all Cursor IDE commands"""
        mappings = {
            # File Operations
            "file_operations": {
                "new_file": {"shortcut": "new_file", "aliases": ["create file", "new file", "new", "create"]},
                "open_file": {"shortcut": "open_file", "aliases": ["open file", "open", "file", "browse file"]},
                "save_file": {"shortcut": "save_file", "aliases": ["save", "save file", "save current"]},
                "save_all": {"shortcut": "save_all", "aliases": ["save all", "save everything", "save all files"]},
                "save_as": {"shortcut": "save_as", "aliases": ["save as", "save with name", "save copy"]},
                "close_file": {"shortcut": "close_editor", "aliases": ["close", "close file", "close tab"]},
                "close_all": {"shortcut": "close_all_editors", "aliases": ["close all", "close everything"]},
                "reopen_closed": {"shortcut": "reopen_closed_editor", "aliases": ["reopen", "undo close", "reopen file"]},
            },

            # Editing Operations
            "editing": {
                "undo": {"shortcut": "undo", "aliases": ["undo", "reverse", "go back"]},
                "redo": {"shortcut": "redo", "aliases": ["redo", "repeat", "forward"]},
                "cut": {"shortcut": "cut", "aliases": ["cut", "cut selection"]},
                "copy": {"shortcut": "copy", "aliases": ["copy", "copy selection"]},
                "paste": {"shortcut": "paste", "aliases": ["paste", "insert"]},
                "select_all": {"shortcut": "select_all", "aliases": ["select all", "select everything"]},
                "find": {"shortcut": "find", "aliases": ["find", "search", "find text"]},
                "replace": {"shortcut": "replace", "aliases": ["replace", "find and replace", "search and replace"]},
                "find_in_files": {"shortcut": "find_in_files", "aliases": ["find in files", "global search", "search everywhere"]},
                "goto_line": {"shortcut": "goto_line", "aliases": ["goto line", "go to line", "line number", "jump to line"]},
                "delete_line": {"shortcut": "delete_line", "aliases": ["delete line", "remove line"]},
                "move_line_up": {"shortcut": "move_line_up", "aliases": ["move line up", "line up"]},
                "move_line_down": {"shortcut": "move_line_down", "aliases": ["move line down", "line down"]},
                "duplicate_line": {"shortcut": "copy_line_down", "aliases": ["duplicate line", "copy line"]},
                "comment_line": {"shortcut": "toggle_line_comment", "aliases": ["comment", "uncomment", "toggle comment", "comment line"]},
                "format_code": {"shortcut": "format_document", "aliases": ["format", "format code", "beautify", "auto format"]},
            },

            # Navigation
            "navigation": {
                "goto_definition": {"shortcut": "goto_definition", "aliases": ["definition", "go to definition", "goto definition"]},
                "peek_definition": {"shortcut": "peek_definition", "aliases": ["peek definition", "preview definition"]},
                "show_references": {"shortcut": "show_references", "aliases": ["references", "find references", "where used"]},
                "go_back": {"shortcut": "go_back", "aliases": ["back", "go back", "previous"]},
                "go_forward": {"shortcut": "go_forward", "aliases": ["forward", "go forward", "next"]},
                "next_tab": {"shortcut": "next_editor", "aliases": ["next tab", "next file", "next editor"]},
                "previous_tab": {"shortcut": "previous_editor", "aliases": ["previous tab", "prev file", "previous editor"]},
                "goto_symbol": {"shortcut": "goto_symbol_in_editor", "aliases": ["symbol", "go to symbol", "function", "class"]},
            },

            # AI/Assistant Operations
            "cursor_ai": {
                "open_chat": {"shortcut": "cursor_chat", "aliases": ["chat", "open chat", "cursor chat", "talk to cursor", "ai chat"]},
                "composer": {"shortcut": "cursor_composer", "aliases": ["composer", "cursor composer", "multi-file edit", "codebase edit"]},
                "inline_chat": {"shortcut": "inline_chat", "aliases": ["inline chat", "code chat", "contextual chat"]},
                "accept_suggestion": {"shortcut": "accept_suggestion", "aliases": ["accept", "accept suggestion", "take suggestion"]},
                "dismiss_suggestion": {"shortcut": "dismiss_suggestion", "aliases": ["dismiss", "reject", "cancel suggestion"]},
                "trigger_suggest": {"shortcut": "trigger_suggest", "aliases": ["autocomplete", "suggest", "intellisense"]},
            },

            # View/Panel Operations
            "view": {
                "command_palette": {"shortcut": "command_palette", "aliases": ["command palette", "palette", "commands"]},
                "toggle_sidebar": {"shortcut": "toggle_sidebar", "aliases": ["sidebar", "toggle sidebar", "hide sidebar"]},
                "toggle_explorer": {"shortcut": "toggle_explorer", "aliases": ["explorer", "file explorer", "files"]},
                "toggle_search": {"shortcut": "toggle_search", "aliases": ["search", "search view", "find in files"]},
                "toggle_git": {"shortcut": "toggle_source_control", "aliases": ["git", "source control", "version control"]},
                "toggle_extensions": {"shortcut": "toggle_extensions", "aliases": ["extensions", "plugins"]},
                "toggle_terminal": {"shortcut": "toggle_terminal", "aliases": ["terminal", "toggle terminal", "console"]},
                "toggle_output": {"shortcut": "toggle_output", "aliases": ["output", "console", "log"]},
                "toggle_problems": {"shortcut": "toggle_problems", "aliases": ["problems", "errors", "warnings"]},
                "zoom_in": {"shortcut": "zoom_in", "aliases": ["zoom in", "bigger", "increase zoom"]},
                "zoom_out": {"shortcut": "zoom_out", "aliases": ["zoom out", "smaller", "decrease zoom"]},
                "reset_zoom": {"shortcut": "reset_zoom", "aliases": ["reset zoom", "normal zoom"]},
            },

            # Debug Operations
            "debugging": {
                "start_debug": {"shortcut": "start_debugging", "aliases": ["debug", "start debug", "run debug"]},
                "stop_debug": {"shortcut": "stop_debugging", "aliases": ["stop debug", "kill debug"]},
                "toggle_breakpoint": {"shortcut": "toggle_breakpoint", "aliases": ["breakpoint", "toggle breakpoint"]},
                "step_over": {"shortcut": "step_over", "aliases": ["step over", "next line", "next"]},
                "step_into": {"shortcut": "step_into", "aliases": ["step into", "enter function"]},
                "step_out": {"shortcut": "step_out", "aliases": ["step out", "exit function", "return"]},
            },

            # Git Operations (via command palette)
            "git": {
                "git_stage_all": {"palette": "git_stage_all", "aliases": ["stage all", "git stage", "stage changes", "git stage all"]},
                "git_unstage_all": {"palette": "git_unstage_all", "aliases": ["unstage all", "git unstage", "unstage everything"]},
                "git_commit": {"palette": "git_commit", "aliases": ["commit", "git commit", "commit changes"]},
                "git_push": {"palette": "git_push", "aliases": ["push", "git push", "push to remote"]},
                "git_pull": {"palette": "git_pull", "aliases": ["pull", "git pull", "pull from remote"]},
                "git_sync": {"palette": "git_sync", "aliases": ["sync", "git sync", "sync repository"]},
            },

            # Advanced Operations (command palette)
            "advanced_palette": {
                "organize_imports": {"palette": "organize_imports", "aliases": ["organize imports", "sort imports", "clean imports"]},
                "python_select_interpreter": {"palette": "python_select_interpreter", "aliases": ["python interpreter", "select interpreter", "python env"]},
                "refactor_extract_function": {"palette": "refactor_extract_function", "aliases": ["extract function", "refactor extract"]},
                "refactor_extract_variable": {"palette": "refactor_extract_variable", "aliases": ["extract variable", "extract var"]},
                "split_editor": {"palette": "split_editor", "aliases": ["split editor", "split view", "split window"]},
                "show_settings": {"palette": "show_settings", "aliases": ["settings", "preferences", "configure"]},
                "show_keybindings": {"palette": "show_keybindings", "aliases": ["keybindings", "keyboard shortcuts", "shortcuts"]},
            },

            # Advanced Operations
            "advanced": {
                "rename_symbol": {"shortcut": "rename_symbol", "aliases": ["rename", "refactor rename", "rename variable"]},
                "quick_fix": {"shortcut": "quick_fix", "aliases": ["quick fix", "code actions", "fix"]},
                "organize_imports": {"palette": "organize_imports", "aliases": ["organize imports", "sort imports"]},
                "reveal_in_explorer": {"shortcut": "reveal_in_explorer", "aliases": ["reveal file", "show in explorer"]},
                "toggle_word_wrap": {"shortcut": "toggle_word_wrap", "aliases": ["word wrap", "wrap text"]},
                "toggle_zen_mode": {"shortcut": "toggle_zen_mode", "aliases": ["zen mode", "distraction free"]},
            },
        }

        return mappings

    def _load_palette_commands(self) -> Dict[str, Dict[str, Any]]:
        """Load command palette commands from config file"""
        palette_commands = {}
        config_path = self.project_root / "config" / "cursor_ide_complete_keyboard_shortcuts.json"

        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    palette_config = config.get("command_palette_commands", {})
                    palette_commands = palette_config
                    logger.info(f"✅ Loaded {len(palette_commands)} command palette commands")
        except Exception as e:
            logger.warning(f"Failed to load palette commands: {e}")

        return palette_commands

    def _build_natural_language_patterns(self) -> Dict[str, List[str]]:
        """Build natural language patterns for command recognition"""
        patterns = {
            "file_operations": [
                r"(?:create|new|make)\s+(?:a\s+)?(?:new\s+)?file",
                r"open\s+(?:a\s+)?(?:file\s+)?(?:called|named)?\s*([^\s]+)?",
                r"save\s+(?:the\s+)?(?:current\s+)?(?:file)?",
                r"close\s+(?:the\s+)?(?:current\s+)?(?:file|tab|editor)?",
            ],
            "editing": [
                r"undo",
                r"redo",
                r"cut",
                r"copy",
                r"paste",
                r"find\s+(?:text\s+)?(?:called|named)?\s*([^\s]+)?",
                r"replace\s+(?:text\s+)?(?:with)?",
                r"format\s+(?:code|file|document)?",
                r"comment\s+(?:out\s+)?(?:line|code)?",
            ],
            "navigation": [
                r"(?:go\s+to|goto|jump\s+to)\s+(?:definition|line|symbol)",
                r"(?:show|find)\s+references",
                r"(?:go\s+)?back",
                r"(?:go\s+)?forward",
                r"next\s+(?:tab|file|editor)",
                r"(?:previous|prev)\s+(?:tab|file|editor)",
            ],
            "cursor_ai": [
                r"(?:open|start|show)\s+chat",
                r"(?:open|start|show)\s+composer",
                r"(?:talk\s+to|chat\s+with)\s+cursor",
                r"accept\s+(?:suggestion|suggested\s+code)?",
            ],
            "view": [
                r"(?:toggle|show|hide)\s+(?:sidebar|explorer|terminal|output|problems)",
                r"(?:open|show)\s+command\s+palette",
                r"(?:zoom\s+)?(?:in|out|reset)",
            ],
            "debugging": [
                r"(?:start|run)\s+debug",
                r"stop\s+debug",
                r"(?:add|toggle)\s+breakpoint",
                r"step\s+(?:over|into|out)",
            ],
            "git": [
                r"(?:stage|git\s+stage)\s+(?:all\s+)?(?:changes|files)?",
                r"(?:commit|git\s+commit)",
                r"(?:push|git\s+push)",
                r"(?:pull|git\s+pull)",
            ],
        }
        return patterns

    def parse_natural_language_command(self, command: str) -> ParsedCommand:
        """
        Parse natural language command to determine intent

        Args:
            command: Natural language command (e.g., "open chat", "save file")

        Returns:
            ParsedCommand with intent and action
        """
        command_lower = command.lower().strip()
        original_command = command

        # Remove common prefixes
        prefixes = ["please", "can you", "could you", "let me", "i want to", "i need to", "help me"]
        for prefix in prefixes:
            if command_lower.startswith(prefix):
                command_lower = command_lower[len(prefix):].strip()

        # Remove common suffixes
        suffixes = ["please", "now", "right now"]
        for suffix in suffixes:
            if command_lower.endswith(suffix):
                command_lower = command_lower[:-len(suffix)].strip()

        # Search through command mappings
        for category, commands in self.command_mappings.items():
            for cmd_name, cmd_info in commands.items():
                # Check aliases
                aliases = cmd_info.get("aliases", [])
                for alias in aliases:
                    alias_lower = alias.lower()
                    if alias_lower == command_lower or alias_lower in command_lower or command_lower in alias_lower:
                        return ParsedCommand(
                            intent=category,
                            action=cmd_name,
                            original_command=original_command,
                            confidence=0.9 if alias_lower == command_lower else 0.7
                        )

                # Check shortcut name
                if cmd_name.lower() == command_lower or cmd_name.lower().replace("_", " ") == command_lower:
                    return ParsedCommand(
                        intent=category,
                        action=cmd_name,
                        original_command=original_command,
                        confidence=0.95
                    )

        # Fallback: try fuzzy matching
        best_match = None
        best_score = 0.0

        for category, commands in self.command_mappings.items():
            for cmd_name, cmd_info in commands.items():
                aliases = cmd_info.get("aliases", [])
                for alias in aliases:
                    alias_lower = alias.lower()
                    # Simple word overlap scoring
                    command_words = set(command_lower.split())
                    alias_words = set(alias_lower.split())
                    if command_words and alias_words:
                        overlap = len(command_words & alias_words) / len(command_words | alias_words)
                        if overlap > best_score and overlap > 0.3:
                            best_score = overlap
                            best_match = (category, cmd_name)

        if best_match:
            category, cmd_name = best_match
            return ParsedCommand(
                intent=category,
                action=cmd_name,
                original_command=original_command,
                confidence=best_score
            )

        # Default: unknown command
        return ParsedCommand(
            intent="unknown",
            action="unknown",
            original_command=original_command,
            confidence=0.0
        )

    def execute_command(self, command: str, async_execution: bool = False) -> CommandExecutionResult:
        """
        Execute a command (natural language or shortcut name)

        Args:
            command: Natural language command or shortcut name
            async_execution: If True, queue for async execution

        Returns:
            CommandExecutionResult
        """
        start_time = time.time()

        # Parse command
        parsed = self.parse_natural_language_command(command)

        if parsed.action == "unknown":
            return CommandExecutionResult(
                success=False,
                method="unknown",
                command=command,
                execution_time=time.time() - start_time,
                error=f"Unknown command: {command}"
            )

        # Queue for async execution if requested
        if async_execution:
            self.command_queue.put(("execute", parsed))
            return CommandExecutionResult(
                success=True,
                method="queued",
                command=command,
                execution_time=0.0,
                details={"queued": True, "parsed": parsed.action}
            )

        # Execute synchronously
        return self._execute_parsed_command(parsed, start_time)

    def _execute_parsed_command(self, parsed: ParsedCommand, start_time: float) -> CommandExecutionResult:
        """Execute a parsed command"""
        category = parsed.intent
        action = parsed.action

        # Get command mapping
        cmd_info = None
        if category in self.command_mappings and action in self.command_mappings[category]:
            cmd_info = self.command_mappings[category][action]

        if not cmd_info:
            return CommandExecutionResult(
                success=False,
                method="unknown",
                command=parsed.original_command,
                execution_time=time.time() - start_time,
                error=f"Command mapping not found: {action}"
            )

        # Try keyboard shortcut first
        if "shortcut" in cmd_info:
            shortcut_name = cmd_info["shortcut"]
            if self.keyboard_controller:
                result = self.keyboard_controller.execute_shortcut(shortcut_name)
                if result.success:
                    execution_time = time.time() - start_time
                    execution_result = CommandExecutionResult(
                        success=True,
                        method="keyboard_shortcut",
                        command=parsed.original_command,
                        execution_time=execution_time,
                        details={"shortcut": shortcut_name, "result": result.method}
                    )

            # Record interaction for learning
            self._record_interaction(parsed, execution_result, "keyboard_shortcut")

            return execution_result

        # Try command palette
        if "palette" in cmd_info:
            palette_key = cmd_info["palette"]
            if self.keyboard_controller:
                # Get full command from loaded palette commands
                full_command = palette_key
                if palette_key in self.palette_commands:
                    full_command = self.palette_commands[palette_key].get("command", palette_key)

                # Execute command palette command
                result = self.keyboard_controller.execute_command_palette_command(full_command)

                if result.success:
                    return CommandExecutionResult(
                        success=True,
                        method="command_palette",
                        command=parsed.original_command,
                        execution_time=time.time() - start_time,
                        details={"palette_command": full_command, "palette_key": palette_key}
                    )

        # Try natural language command via keyboard controller
        if self.keyboard_controller:
            result = self.keyboard_controller.execute_natural_language_command(parsed.original_command)
            if result.success:
                return CommandExecutionResult(
                    success=True,
                    method="natural_language",
                    command=parsed.original_command,
                    execution_time=time.time() - start_time,
                    details={"method": result.method}
                )

        # Fallback: command palette with original command
        if self.keyboard_controller:
            result = self.keyboard_controller.execute_command_palette_command(parsed.original_command)
            if result.success:
                return CommandExecutionResult(
                    success=True,
                    method="command_palette_fallback",
                    command=parsed.original_command,
                    execution_time=time.time() - start_time,
                    details={"fallback": True}
                )

        return CommandExecutionResult(
            success=False,
            method="failed",
            command=parsed.original_command,
            execution_time=time.time() - start_time,
            error="All execution methods failed"
        )

    def _command_execution_loop(self):
        """Background thread for async command execution"""
        while True:
            try:
                item = self.command_queue.get(timeout=1.0)
                if item is None:  # Shutdown signal
                    break

                action, parsed = item
                if action == "execute":
                    start_time = time.time()
                    result = self._execute_parsed_command(parsed, start_time)
                    logger.info(f"✅ Async command executed: {parsed.original_command} ({result.method})")

                self.command_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error in command execution loop: {e}")

    def _record_interaction(self, parsed: ParsedCommand, result: CommandExecutionResult, method: str):
        """Record interaction for learning"""
        if not self.learner:
            return

        try:
            interaction = IDEInteraction(
                timestamp=datetime.now(),
                interaction_type=method,
                command=parsed.original_command,
                feature=parsed.action,
                context={
                    "intent": parsed.intent,
                    "confidence": parsed.confidence,
                    "method": result.method
                },
                outcome="success" if result.success else "failure",
                duration=result.execution_time
            )
            self.learner.record_interaction(interaction)
        except Exception as e:
            logger.debug(f"Failed to record interaction: {e}")

    def process_jarvis_command(self, command: str) -> CommandExecutionResult:
        """
        Process command from JARVIS (voice or text)

        Args:
            command: Command from JARVIS

        Returns:
            CommandExecutionResult
        """
        logger.info(f"🎤 Processing JARVIS command: {command[:100]}")
        return self.execute_command(command, async_execution=False)

    def get_available_commands(self, category: Optional[str] = None) -> Dict[str, Any]:
        """
        Get available commands, optionally filtered by category

        Args:
            category: Optional category filter

        Returns:
            Dictionary of available commands
        """
        if category:
            if category in self.command_mappings:
                return self.command_mappings[category]
            return {}
        return self.command_mappings

    def search_commands(self, query: str) -> List[Dict[str, Any]]:
        """
        Search commands by name or alias

        Args:
            query: Search query

        Returns:
            List of matching commands
        """
        query_lower = query.lower()
        results = []

        for category, commands in self.command_mappings.items():
            for cmd_name, cmd_info in commands.items():
                # Check command name
                if query_lower in cmd_name.lower():
                    results.append({
                        "category": category,
                        "name": cmd_name,
                        "info": cmd_info
                    })
                    continue

                # Check aliases
                aliases = cmd_info.get("aliases", [])
                if any(query_lower in alias.lower() for alias in aliases):
                    results.append({
                        "category": category,
                        "name": cmd_name,
                        "info": cmd_info
                    })

        return results


def get_jarvis_cursor_integration(project_root: Optional[Path] = None) -> JARVISCursorIDEKeyboardIntegration:
    """Get or create JARVIS-Cursor IDE integration instance"""
    global _integration_instance
    if '_integration_instance' not in globals():
        _integration_instance = JARVISCursorIDEKeyboardIntegration(project_root=project_root)
    return _integration_instance


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="JARVIS-Cursor IDE Keyboard Integration - Complete keyboard control"
        )
        parser.add_argument("--command", type=str, help="Execute command (natural language or shortcut)")
        parser.add_argument("--search", type=str, help="Search commands")
        parser.add_argument("--list", action="store_true", help="List all commands")
        parser.add_argument("--category", type=str, help="Filter by category")
        parser.add_argument("--jarvis-command", type=str, help="Process command from JARVIS")

        args = parser.parse_args()

        integration = JARVISCursorIDEKeyboardIntegration()

        if args.command:
            result = integration.execute_command(args.command)
            print(f"Success: {result.success}")
            print(f"Method: {result.method}")
            if result.error:
                print(f"Error: {result.error}")
            print(f"Execution time: {result.execution_time:.2f}s")

        elif args.jarvis_command:
            result = integration.process_jarvis_command(args.jarvis_command)
            print(json.dumps({
                "success": result.success,
                "method": result.method,
                "execution_time": result.execution_time,
                "error": result.error,
                "details": result.details
            }, indent=2))

        elif args.search:
            results = integration.search_commands(args.search)
            print(f"Found {len(results)} matches:")
            for result in results:
                print(f"  [{result['category']}] {result['name']}: {result['info'].get('aliases', [])}")

        elif args.list:
            commands = integration.get_available_commands(category=args.category)
            for category, cmd_dict in commands.items():
                if args.category and category != args.category:
                    continue
                print(f"\n{category.upper().replace('_', ' ')}:")
                for cmd_name, cmd_info in cmd_dict.items():
                    aliases = cmd_info.get("aliases", [])
                    print(f"  {cmd_name}: {', '.join(aliases[:3])}")

        else:
            parser.print_help()
            print("\n✅ JARVIS-Cursor IDE Keyboard Integration")
            print("   Complete keyboard control - no mouse required")
            print("   Natural language → Keyboard shortcuts")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()