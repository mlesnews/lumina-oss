#!/usr/bin/env python3
"""
IDE Queue Processors
<COMPANY_NAME> LLC

Processes IDE queue data:
- Problems queue processor
- Source control queue processor
- Extensions queue processor
- Tasks queue processor
- Terminal queue processor

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from universal_logging_wrapper import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IDEQueueProcessors")


@dataclass
class ProcessedQueueData:
    """Processed queue data"""
    queue_type: str
    items: List[Dict[str, Any]]
    summary: Dict[str, Any]
    actionable_items: List[str]
    intelligence: List[Dict[str, Any]]


class ProblemsQueueProcessor:
    """Process problems panel queue"""

    def __init__(self):
        self.logger = logger

    def process(self, problems: List[Dict[str, Any]]) -> ProcessedQueueData:
        """Process problems queue"""
        errors = [p for p in problems if p.get("severity", "").lower() == "error"]
        warnings = [p for p in problems if p.get("severity", "").lower() == "warning"]
        info = [p for p in problems if p.get("severity", "").lower() == "info"]

        actionable_items = [f"Fix {p.get('source', 'unknown')} error: {p.get('message', '')}" for p in errors[:10]]

        intelligence = []
        if len(errors) > 10:
            intelligence.append({
                "text": f"High error count ({len(errors)}) - potential systemic issues", 
                "type": "issue",
                "intent_peek": "Operator is likely attempting a major refactor or facing significant integration hurdles."
            })

        # Consolidation Logic
        if len(errors) > 0:
            systemic_pattern = self._detect_systemic_pattern(errors)
            if systemic_pattern:
                intelligence.append({
                    "text": f"Systemic Pattern Detected: {systemic_pattern}",
                    "type": "prediction",
                    "intent_peek": f"Operator intent: Resolve {systemic_pattern} across multiple files."
                })

        return ProcessedQueueData(
            queue_type="problems",
            items=problems,
            summary={
                "total": len(problems),
                "errors": len(errors),
                "warnings": len(warnings),
                "info": len(info)
            },
            actionable_items=actionable_items,
            intelligence=intelligence
        )

    def _detect_systemic_pattern(self, errors: List[Dict[str, Any]]) -> Optional[str]:
        """Detect if multiple errors share a common root cause"""
        if not errors: return None

        messages = [e.get("message", "") for e in errors]
        # Example: Multiple "ImportError" or "ModuleNotFoundError"
        for keyword in ["ImportError", "ModuleNotFoundError", "SyntaxError", "TypeError"]:
            if len([m for m in messages if keyword in m]) > 2:
                return f"Systemic {keyword}"
        return None


class SourceControlQueueProcessor:
    """Process source control queue"""

    def __init__(self):
        self.logger = logger

    def process(self, scm_data: Dict[str, Any]) -> ProcessedQueueData:
        """Process source control queue"""
        modified = scm_data.get("modified", [])
        added = scm_data.get("added", [])
        deleted = scm_data.get("deleted", [])
        conflicts = scm_data.get("conflicts", [])

        actionable_items = []
        if modified:
            actionable_items.append(f"Review {len(modified)} modified files")
        if conflicts:
            actionable_items.append(f"Resolve {len(conflicts)} merge conflicts")

        intelligence = []
        if conflicts:
            intelligence.append({"text": f"Merge conflicts detected: {len(conflicts)}", "type": "conflict"})

        return ProcessedQueueData(
            queue_type="source_control",
            items=[{"modified": modified, "added": added, "deleted": deleted, "conflicts": conflicts}],
            summary={
                "modified": len(modified),
                "added": len(added),
                "deleted": len(deleted),
                "conflicts": len(conflicts)
            },
            actionable_items=actionable_items,
            intelligence=intelligence
        )


class ExtensionsQueueProcessor:
    """Process extensions queue"""

    def __init__(self):
        self.logger = logger

    def process(self, extensions: List[Dict[str, Any]]) -> ProcessedQueueData:
        """Process extensions queue"""
        enabled = [e for e in extensions if e.get("enabled", False)]
        disabled = [e for e in extensions if not e.get("enabled", False)]
        errors = [e for e in extensions if e.get("error")]
        updates_available = [e for e in extensions if e.get("update_available", False)]

        actionable_items = []
        if errors:
            actionable_items.append(f"Fix {len(errors)} extension errors")
        if updates_available:
            actionable_items.append(f"Update {len(updates_available)} extensions")

        intelligence = []
        if errors:
            intelligence.append({"text": f"Extension errors: {len(errors)}", "type": "error"})

        return ProcessedQueueData(
            queue_type="extensions",
            items=extensions,
            summary={
                "total": len(extensions),
                "enabled": len(enabled),
                "disabled": len(disabled),
                "errors": len(errors),
                "updates_available": len(updates_available)
            },
            actionable_items=actionable_items,
            intelligence=intelligence
        )


class TasksQueueProcessor:
    """Process tasks queue"""

    def __init__(self):
        self.logger = logger

    def process(self, tasks: List[Dict[str, Any]]) -> ProcessedQueueData:
        """Process tasks queue"""
        running = [t for t in tasks if t.get("status") == "running"]
        completed = [t for t in tasks if t.get("status") == "completed"]
        failed = [t for t in tasks if t.get("status") == "failed"]

        actionable_items = []
        if failed:
            actionable_items.append(f"Fix {len(failed)} failed tasks")

        intelligence = []
        if failed:
            intelligence.append({"text": f"Failed tasks: {len(failed)}", "type": "error"})

        return ProcessedQueueData(
            queue_type="tasks",
            items=tasks,
            summary={
                "total": len(tasks),
                "running": len(running),
                "completed": len(completed),
                "failed": len(failed)
            },
            actionable_items=actionable_items,
            intelligence=intelligence
        )


class TerminalQueueProcessor:
    """Process terminal queue"""

    def __init__(self):
        self.logger = logger

    def process(self, terminal_data: List[Dict[str, Any]]) -> ProcessedQueueData:
        """Process terminal queue with Intent Peeking"""
        outputs = [d for d in terminal_data if d.get("type") == "output"]
        errors = [d for d in terminal_data if d.get("type") == "error"]
        commands = [d for d in terminal_data if d.get("type") == "command"]

        actionable_items = []
        if errors:
            actionable_items.append(f"Review {len(errors)} terminal errors")

        intelligence = []
        if errors:
            intelligence.append({"text": f"Terminal errors: {len(errors)}", "type": "error"})

        # Intent Peeking for @ideop
        if commands:
            last_command = commands[-1].get("content", "").lower()
            intent_peek = self._peek_at_terminal_intent(last_command)
            if intent_peek:
                intelligence.append({
                    "text": f"Clairvoyance: Predicted @ideop Intent",
                    "type": "prediction",
                    "intent_peek": intent_peek
                })

        return ProcessedQueueData(
            queue_type="terminal",
            items=terminal_data,
            summary={
                "total": len(terminal_data),
                "outputs": len(outputs),
                "errors": len(errors),
                "commands": len(commands)
            },
            actionable_items=actionable_items,
            intelligence=intelligence
        )

    def _peek_at_terminal_intent(self, command: str) -> Optional[str]:
        """Attempt to gain clairvoyance into what the operator is doing"""
        if "git add" in command or "git commit" in command:
            return "Operator is preparing for a deployment or milestone snapshot."
        if "pip install" in command:
            return "Operator is expanding the system's capabilities or solving a dependency roadblock."
        if "python test" in command or "pytest" in command:
            return "Operator is ensuring system stability and validating recent changes."
        if "docker" in command:
            return "Operator is orchestrating containerized services across the cluster."
        return None
