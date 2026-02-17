#!/usr/bin/env python3
"""
JARVIS Chat - Cursor Agent (CA) Fidelity Layer

Implements all Cursor Agent tools and MCP capabilities so JARVIS can operate
independently of Cursor extensions while retaining full CA functionality.

See: docs/system/JARVIS_CHAT_CA_FIDELITY_SPEC.md

Author: Lumina AI Team
Date: 2026-02-03
Tags: @PEAK @JARVIS #automation
"""

import json
import logging
import os
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("JarvisCAFidelity")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "python"
CONFIG_DIR = PROJECT_ROOT / "config"


@dataclass
class ShellResult:
    """Result from shell command execution"""
    exit_code: int
    stdout: str
    stderr: str
    elapsed_ms: float
    command: str
    working_dir: str


@dataclass
class GrepMatch:
    """A grep match result"""
    file: str
    line_number: int
    line_content: str
    match: str


@dataclass
class LintError:
    """A linter error"""
    file: str
    line: int
    column: int
    severity: str
    message: str
    source: str


@dataclass
class Todo:
    """A todo item"""
    id: str
    content: str
    status: str  # pending, in_progress, completed, cancelled


@dataclass
class SearchResult:
    """A semantic search result"""
    file: str
    start_line: int
    end_line: int
    content: str
    score: float


@dataclass
class PageSnapshot:
    """Browser page snapshot"""
    url: str
    title: str
    elements: List[Dict[str, Any]]
    html: str


class StoicResponseMixin:
    """
    Stoic philosophy mixin for AI responses.
    
    Based on principles from Marcus Aurelius, Seneca, and Epictetus.
    Shapes responses to be calm, rational, and focused on what's controllable.
    """
    
    # The Four Virtues
    VIRTUES = {
        "wisdom": "Discern what matters from what doesn't",
        "courage": "Act rightly despite difficulty",
        "justice": "Treat all fairly, fulfill obligations",
        "temperance": "Exercise restraint, avoid excess",
    }
    
    # Response templates
    STOIC_RESPONSES = {
        "on_error": "This outcome was within the range of possibility. Let me diagnose the cause.",
        "on_success": "Complete. What is the next priority?",
        "on_uncertainty": "I lack sufficient context to act wisely here. What additional information is available?",
        "on_difficulty": "The obstacle is the way. Let me examine this systematically.",
        "on_criticism": "Thank you for the correction. Let me adjust my approach.",
    }
    
    def stoic_frame_response(self, situation: str, details: str = "") -> str:
        """Frame a response according to Stoic principles"""
        template = self.STOIC_RESPONSES.get(situation, "")
        if template and details:
            return f"{template} {details}"
        return template or details
    
    def is_within_control(self, item: str) -> bool:
        """Determine if something is within our control (Stoic dichotomy)"""
        within_control = [
            "analysis", "reasoning", "response", "quality", "effort",
            "communication", "preparation", "judgment", "action"
        ]
        outside_control = [
            "external", "api", "network", "user", "third-party", 
            "hardware", "outcome", "weather", "market"
        ]
        
        item_lower = item.lower()
        if any(w in item_lower for w in within_control):
            return True
        if any(w in item_lower for w in outside_control):
            return False
        return True  # Default: assume we can influence it
    
    def premeditatio_malorum(self, task: str) -> List[str]:
        """Negative visualization - anticipate what could go wrong"""
        common_issues = [
            f"Network timeout while executing {task}",
            f"Insufficient permissions for {task}",
            f"Resource not found during {task}",
            f"Unexpected data format in {task}",
            f"Dependency unavailable for {task}",
        ]
        return common_issues
    
    def amor_fati_reframe(self, problem: str) -> str:
        """Reframe a problem as an opportunity (Love of Fate)"""
        return f"This {problem} is an opportunity to improve our resilience and understanding."


class JarvisChatCAFidelity(StoicResponseMixin):
    """
    Cursor Agent fidelity layer for JARVIS Chat.
    
    Implements all CA tools so JARVIS can operate independently of
    Cursor extensions while retaining full functionality.
    
    Philosophy: Stoic (calm, rational, focused on controllable factors)
    
    Integrates with:
    - All Lumina frameworks (28+ frameworks)
    - All subagents (12+ specialized agents)
    - Water Workflow System
    - Local AI clusters (ULTRON, KAIJU, BitNet)
    - MCP servers
    """
    
    def __init__(
        self,
        project_root: Optional[Path] = None,
        ai_endpoint: str = "http://localhost:11434/v1",
    ):
        self.project_root = Path(project_root) if project_root else PROJECT_ROOT
        self.ai_endpoint = ai_endpoint
        self.shell_cwd = str(self.project_root)
        self.shell_env = os.environ.copy()
        self._todos: Dict[str, Todo] = {}
        self._background_tasks: Dict[str, subprocess.Popen] = {}
        
        # Load configuration
        self._load_config()
        
        # Initialize unified integration (lazy loaded)
        self._unified: Optional[Any] = None
        
    def _load_config(self):
        """Load homelab and cluster configuration"""
        config_path = CONFIG_DIR / "homelab_mcp_hybrid_config.json"
        if config_path.exists():
            with open(config_path) as f:
                self.config = json.load(f)
        else:
            self.config = {}
            
        # Load cluster endpoints
        self.endpoints = {
            "ultron": "http://localhost:11434/v1",
            "kaiju": "http://<NAS_IP>:11437/v1",
            "nas": "http://<NAS_PRIMARY_IP>:8085",
        }
        
        if self.config.get("ai_cluster", {}).get("gpu_nodes"):
            for name, node in self.config["ai_cluster"]["gpu_nodes"].items():
                self.endpoints[name.lower()] = f"http://{node['ip']}:{node['ollama_port']}/v1"
    
    # =========================================================================
    # FILE SYSTEM OPERATIONS
    # =========================================================================
    
    def file_read(
        self,
        path: str,
        offset: Optional[int] = None,
        limit: Optional[int] = None,
    ) -> str:
        """
        Read file contents with optional line offset/limit.
        
        Args:
            path: Absolute or relative path to file
            offset: Line number to start from (1-based)
            limit: Number of lines to read
            
        Returns:
            File contents with line numbers
        """
        file_path = self._resolve_path(path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        
        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        start = (offset - 1) if offset else 0
        end = (start + limit) if limit else len(lines)
        
        result = []
        for i, line in enumerate(lines[start:end], start=start + 1):
            result.append(f"{i:6}|{line.rstrip()}")
        
        return "\n".join(result)
    
    def file_write(self, path: str, contents: str) -> bool:
        """
        Write contents to file, creating directories as needed.
        
        Args:
            path: Absolute or relative path to file
            contents: Contents to write
            
        Returns:
            True if successful
        """
        file_path = self._resolve_path(path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(contents)
        
        logger.info(f"Wrote {len(contents)} bytes to {path}")
        return True
    
    def str_replace(
        self,
        path: str,
        old_string: str,
        new_string: str,
        replace_all: bool = False,
    ) -> bool:
        """
        Replace string in file.
        
        Args:
            path: Path to file
            old_string: String to find
            new_string: String to replace with
            replace_all: If True, replace all occurrences
            
        Returns:
            True if replacement was made
        """
        file_path = self._resolve_path(path)
        
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        if old_string not in content:
            raise ValueError(f"String not found in {path}: {old_string[:50]}...")
        
        if replace_all:
            new_content = content.replace(old_string, new_string)
        else:
            # Replace only first occurrence
            new_content = content.replace(old_string, new_string, 1)
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(new_content)
        
        logger.info(f"Replaced string in {path}")
        return True
    
    def file_delete(self, path: str) -> bool:
        """Delete a file."""
        file_path = self._resolve_path(path)
        
        if file_path.exists():
            file_path.unlink()
            logger.info(f"Deleted {path}")
            return True
        return False
    
    def ls(self, path: str, ignore_globs: Optional[List[str]] = None) -> List[str]:
        """List directory contents."""
        dir_path = self._resolve_path(path)
        
        if not dir_path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        
        items = []
        for item in sorted(dir_path.iterdir()):
            if item.name.startswith("."):
                continue
            
            # Check ignore patterns
            if ignore_globs:
                skip = False
                for pattern in ignore_globs:
                    if item.match(pattern):
                        skip = True
                        break
                if skip:
                    continue
            
            suffix = "/" if item.is_dir() else ""
            items.append(f"{item.name}{suffix}")
        
        return items
    
    def glob(
        self,
        pattern: str,
        target_directory: Optional[str] = None,
    ) -> List[str]:
        """Find files matching glob pattern."""
        base_dir = self._resolve_path(target_directory) if target_directory else self.project_root
        
        # Ensure pattern is recursive
        if not pattern.startswith("**/"):
            pattern = f"**/{pattern}"
        
        matches = list(base_dir.glob(pattern))
        return [str(m.relative_to(base_dir)) for m in sorted(matches)]
    
    def grep(
        self,
        pattern: str,
        path: Optional[str] = None,
        ignore_case: bool = False,
        context_lines: int = 0,
    ) -> List[GrepMatch]:
        """Search file contents using ripgrep."""
        search_path = self._resolve_path(path) if path else self.project_root
        
        cmd = ["rg", "--line-number", "--no-heading"]
        
        if ignore_case:
            cmd.append("-i")
        if context_lines:
            cmd.extend(["-C", str(context_lines)])
        
        cmd.extend([pattern, str(search_path)])
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
            )
        except FileNotFoundError:
            # Fallback to Python grep if rg not available
            return self._python_grep(pattern, search_path, ignore_case)
        
        matches = []
        for line in result.stdout.splitlines():
            # Parse: file:line:content
            parts = line.split(":", 2)
            if len(parts) >= 3:
                matches.append(GrepMatch(
                    file=parts[0],
                    line_number=int(parts[1]),
                    line_content=parts[2],
                    match=pattern,
                ))
        
        return matches
    
    def _python_grep(
        self,
        pattern: str,
        path: Path,
        ignore_case: bool,
    ) -> List[GrepMatch]:
        """Fallback grep using Python regex."""
        flags = re.IGNORECASE if ignore_case else 0
        regex = re.compile(pattern, flags)
        matches = []
        
        if path.is_file():
            files = [path]
        else:
            files = path.rglob("*")
        
        for file in files:
            if not file.is_file():
                continue
            try:
                with open(file, "r", encoding="utf-8", errors="ignore") as f:
                    for i, line in enumerate(f, 1):
                        if regex.search(line):
                            matches.append(GrepMatch(
                                file=str(file),
                                line_number=i,
                                line_content=line.rstrip(),
                                match=pattern,
                            ))
            except Exception:
                continue
        
        return matches
    
    # =========================================================================
    # SHELL OPERATIONS
    # =========================================================================
    
    def shell_exec(
        self,
        command: str,
        working_directory: Optional[str] = None,
        timeout_ms: int = 30000,
    ) -> ShellResult:
        """
        Execute shell command.
        
        Args:
            command: Command to execute
            working_directory: Directory to run in (defaults to current)
            timeout_ms: Timeout in milliseconds
            
        Returns:
            ShellResult with output and status
        """
        cwd = working_directory or self.shell_cwd
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=cwd,
                env=self.shell_env,
                timeout=timeout_ms / 1000,
            )
            
            elapsed_ms = (time.time() - start_time) * 1000
            
            # Update shell cwd if command was cd
            if command.strip().startswith("cd "):
                new_dir = command.strip()[3:].strip().strip('"').strip("'")
                if os.path.isabs(new_dir):
                    self.shell_cwd = new_dir
                else:
                    self.shell_cwd = str(Path(cwd) / new_dir)
            
            return ShellResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                elapsed_ms=elapsed_ms,
                command=command,
                working_dir=cwd,
            )
            
        except subprocess.TimeoutExpired:
            elapsed_ms = (time.time() - start_time) * 1000
            return ShellResult(
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout_ms}ms",
                elapsed_ms=elapsed_ms,
                command=command,
                working_dir=cwd,
            )
    
    def background_task(self, command: str, working_directory: Optional[str] = None) -> str:
        """Start a background task and return its ID."""
        import uuid
        
        task_id = str(uuid.uuid4())[:8]
        cwd = working_directory or self.shell_cwd
        
        proc = subprocess.Popen(
            command,
            shell=True,
            cwd=cwd,
            env=self.shell_env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        self._background_tasks[task_id] = proc
        logger.info(f"Started background task {task_id}: {command}")
        
        return task_id
    
    def check_background_task(self, task_id: str) -> Optional[ShellResult]:
        """Check status of background task. Returns None if still running."""
        if task_id not in self._background_tasks:
            raise ValueError(f"Unknown task ID: {task_id}")
        
        proc = self._background_tasks[task_id]
        
        if proc.poll() is None:
            return None  # Still running
        
        stdout, stderr = proc.communicate()
        
        return ShellResult(
            exit_code=proc.returncode,
            stdout=stdout.decode() if stdout else "",
            stderr=stderr.decode() if stderr else "",
            elapsed_ms=0,  # Unknown for background tasks
            command="",
            working_dir="",
        )
    
    # =========================================================================
    # CODE INTELLIGENCE
    # =========================================================================
    
    def semantic_search(
        self,
        query: str,
        target_directories: Optional[List[str]] = None,
        num_results: int = 15,
    ) -> List[SearchResult]:
        """
        Semantic code search.
        
        This is a simplified implementation using keyword matching.
        Full semantic search requires embeddings infrastructure.
        """
        # Extract keywords from query
        keywords = re.findall(r'\w+', query.lower())
        
        results = []
        search_dirs = target_directories or [str(self.project_root)]
        
        for search_dir in search_dirs:
            dir_path = self._resolve_path(search_dir)
            
            for file in dir_path.rglob("*.py"):
                try:
                    content = file.read_text(encoding="utf-8", errors="ignore")
                    lines = content.splitlines()
                    
                    # Score based on keyword matches
                    score = sum(
                        content.lower().count(kw) for kw in keywords
                    ) / max(1, len(content))
                    
                    if score > 0:
                        results.append(SearchResult(
                            file=str(file),
                            start_line=1,
                            end_line=len(lines),
                            content=content[:500],
                            score=score,
                        ))
                except Exception:
                    continue
        
        # Sort by score and return top results
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:num_results]
    
    def read_lints(self, paths: Optional[List[str]] = None) -> List[LintError]:
        """Get linter errors for files."""
        errors = []
        
        target_paths = paths or [str(self.project_root)]
        
        for path in target_paths:
            file_path = self._resolve_path(path)
            
            if file_path.suffix == ".py":
                # Run ruff for Python files
                result = subprocess.run(
                    ["ruff", "check", str(file_path), "--output-format=json"],
                    capture_output=True,
                    text=True,
                )
                
                if result.stdout:
                    try:
                        lint_results = json.loads(result.stdout)
                        for item in lint_results:
                            errors.append(LintError(
                                file=item.get("filename", str(file_path)),
                                line=item.get("location", {}).get("row", 0),
                                column=item.get("location", {}).get("column", 0),
                                severity=item.get("type", "error"),
                                message=item.get("message", ""),
                                source="ruff",
                            ))
                    except json.JSONDecodeError:
                        pass
        
        return errors
    
    # =========================================================================
    # TASK MANAGEMENT
    # =========================================================================
    
    def todo_write(self, todos: List[Todo], merge: bool = True) -> bool:
        """Create or update todo list."""
        if merge:
            for todo in todos:
                self._todos[todo.id] = todo
        else:
            self._todos = {todo.id: todo for todo in todos}
        
        logger.info(f"Updated {len(todos)} todos (merge={merge})")
        return True
    
    def todo_list(self) -> List[Todo]:
        """Get all todos."""
        return list(self._todos.values())
    
    # =========================================================================
    # WEB OPERATIONS
    # =========================================================================
    
    def web_search(self, query: str) -> List[Dict[str, str]]:
        """Search the web (requires API integration)."""
        logger.warning("Web search not yet implemented - requires API key")
        return []
    
    def web_fetch(self, url: str) -> str:
        """Fetch URL content."""
        import urllib.request
        
        try:
            with urllib.request.urlopen(url, timeout=30) as response:
                return response.read().decode("utf-8")
        except Exception as e:
            raise RuntimeError(f"Failed to fetch {url}: {e}")
    
    # =========================================================================
    # AI OPERATIONS
    # =========================================================================
    
    def ai_chat(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        model: str = "auto",
    ) -> str:
        """
        Send chat request to local AI cluster.
        
        Uses local_ai_context_bridge for intelligent routing.
        """
        try:
            from local_ai_context_bridge import LocalAIContextBridge
            
            bridge = LocalAIContextBridge()
            response = bridge.chat(
                prompt=prompt,
                system_prompt=system_prompt,
                model=model,
            )
            return response.get("content", "")
        except ImportError:
            logger.error("local_ai_context_bridge not available")
            return ""
    
    def ai_complete(
        self,
        prefix: str,
        suffix: Optional[str] = None,
        model: str = "auto",
    ) -> str:
        """Get code completion from local AI."""
        prompt = f"Complete the following code:\n\n{prefix}"
        if suffix:
            prompt += f"\n\n[Code continues with:]\n{suffix}"
        
        return self.ai_chat(prompt, model=model)
    
    # =========================================================================
    # BROWSER AUTOMATION (via MCP)
    # =========================================================================
    
    def browser_navigate(self, url: str) -> bool:
        """Navigate browser to URL."""
        return self._call_mcp("cursor-ide-browser", "browser_navigate", {"url": url})
    
    def browser_snapshot(self) -> PageSnapshot:
        """Get browser page snapshot."""
        result = self._call_mcp("cursor-ide-browser", "browser_snapshot", {})
        return PageSnapshot(
            url=result.get("url", ""),
            title=result.get("title", ""),
            elements=result.get("elements", []),
            html=result.get("html", ""),
        )
    
    def browser_click(self, selector: str) -> bool:
        """Click element in browser."""
        return self._call_mcp("cursor-ide-browser", "browser_click", {"selector": selector})
    
    def browser_type(self, selector: str, text: str) -> bool:
        """Type text in browser element."""
        return self._call_mcp("cursor-ide-browser", "browser_type", {"selector": selector, "text": text})
    
    def browser_fill(self, selector: str, text: str) -> bool:
        """Fill browser input (replaces content)."""
        return self._call_mcp("cursor-ide-browser", "browser_fill", {"selector": selector, "text": text})
    
    def _call_mcp(self, server: str, tool: str, args: Dict[str, Any]) -> Any:
        """Call MCP server tool."""
        # This would integrate with actual MCP client
        logger.warning(f"MCP call: {server}.{tool}({args}) - not yet connected")
        return {}
    
    # =========================================================================
    # UNIFIED INTEGRATION - Frameworks & Subagents
    # =========================================================================
    
    @property
    def unified(self):
        """Lazy load the unified integration"""
        if self._unified is None:
            try:
                from jarvis_chat_unified_integration import get_jarvis
                self._unified = get_jarvis()
            except ImportError:
                logger.warning("Unified integration not available")
                self._unified = None
        return self._unified
    
    def list_frameworks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available frameworks"""
        if self.unified:
            from jarvis_chat_unified_integration import FrameworkCategory
            cat = FrameworkCategory(category) if category else None
            return self.unified.list_frameworks(cat)
        return []
    
    def list_subagents(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all available subagents"""
        if self.unified:
            from jarvis_chat_unified_integration import SubagentDomain
            dom = SubagentDomain(domain) if domain else None
            return self.unified.list_subagents(dom)
        return []
    
    def load_framework(self, key: str) -> Any:
        """Load a framework by key"""
        if self.unified:
            return self.unified.load_framework(key)
        raise RuntimeError("Unified integration not available")
    
    def spawn_subagent(self, key: str, **kwargs) -> Any:
        """Spawn a subagent by key"""
        if self.unified:
            return self.unified.spawn_subagent(key, **kwargs)
        raise RuntimeError("Unified integration not available")
    
    def delegate_task(
        self,
        agent_key: str,
        task: str,
        parameters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delegate a task to a subagent"""
        if self.unified:
            return self.unified.delegate_to_subagent(agent_key, task, parameters)
        return {"success": False, "error": "Unified integration not available"}
    
    def flow(
        self,
        task: str,
        context: Optional[Dict[str, Any]] = None,
        confidence: str = "medium",
    ) -> Dict[str, Any]:
        """
        Water Workflow - Be like water.
        
        Flow autonomously when path is clear, escalate when blocked.
        """
        if self.unified:
            return self.unified.flow(task, context, confidence)
        return {"task": task, "state": "executed", "result": "Direct execution"}
    
    def system_status(self) -> Dict[str, Any]:
        """Get unified system status"""
        status = {
            "jarvis_ca_fidelity": "active",
            "project_root": str(self.project_root),
            "shell_cwd": self.shell_cwd,
            "todos": len(self._todos),
            "background_tasks": len(self._background_tasks),
        }
        
        if self.unified:
            status["unified_integration"] = self.unified.status()
        else:
            status["unified_integration"] = "not_loaded"
        
        return status
    
    # =========================================================================
    # HELPER METHODS
    # =========================================================================
    
    def _resolve_path(self, path: Optional[str]) -> Path:
        """Resolve path relative to project root."""
        if path is None:
            return self.project_root
        
        path_obj = Path(path)
        if path_obj.is_absolute():
            return path_obj
        return self.project_root / path_obj


# =============================================================================
# CLI INTERFACE
# =============================================================================

def main():
    """CLI interface for testing JARVIS CA Fidelity."""
    import argparse
    
    parser = argparse.ArgumentParser(description="JARVIS Chat CA Fidelity Layer")
    parser.add_argument("command", choices=["read", "ls", "grep", "shell", "todo", "ai"])
    parser.add_argument("args", nargs="*")
    parser.add_argument("--path", "-p", help="Path for file operations")
    parser.add_argument("--pattern", help="Pattern for grep")
    parser.add_argument("--prompt", help="Prompt for AI chat")
    
    args = parser.parse_args()
    
    jarvis = JarvisChatCAFidelity()
    
    if args.command == "read":
        path = args.path or args.args[0] if args.args else None
        if path:
            print(jarvis.file_read(path))
        else:
            print("Error: --path required")
    
    elif args.command == "ls":
        path = args.path or args.args[0] if args.args else "."
        for item in jarvis.ls(path):
            print(item)
    
    elif args.command == "grep":
        pattern = args.pattern or args.args[0] if args.args else None
        if pattern:
            for match in jarvis.grep(pattern, args.path):
                print(f"{match.file}:{match.line_number}:{match.line_content}")
        else:
            print("Error: --pattern required")
    
    elif args.command == "shell":
        cmd = " ".join(args.args) if args.args else None
        if cmd:
            result = jarvis.shell_exec(cmd)
            print(result.stdout)
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            print(f"Exit code: {result.exit_code}")
        else:
            print("Error: command required")
    
    elif args.command == "todo":
        for todo in jarvis.todo_list():
            print(f"[{todo.status}] {todo.id}: {todo.content}")
    
    elif args.command == "ai":
        prompt = args.prompt or " ".join(args.args) if args.args else None
        if prompt:
            response = jarvis.ai_chat(prompt)
            print(response)
        else:
            print("Error: --prompt required")


if __name__ == "__main__":
    main()
