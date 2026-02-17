#!/usr/bin/env python3
"""
@DOIT Universal SYPHON Integration - Wildcard-Inclusive System

Improves @doit based on communication optimization principles, with universal
piping to @🟢 PUBLIC: GitHub Open-Source (v2.0)/@syphon for all-inclusive "*.*" wildcard-like behavior.

Key Improvements:
- Direct action commands (communication optimization)
- Context-rich requests
- Universal syphon integration (wildcard-like)
- All-inclusive data capture
- Improved context and courage

Tags: #DOIT #SYPHON #UNIVERSAL #WILDCARD #COMMUNICATION_OPTIMIZATION @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field

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

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, SyphonData, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None

# Import DOIT executor
try:
    from jarvis_doit_executor import JARVISDOITExecutor
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    JARVISDOITExecutor = None

logger = get_logger("DOITUniversalSyphon")


@dataclass
class UniversalSyphonTarget:
    """Universal syphon target - wildcard-like inclusion"""
    target_path: str  # "@🟢 PUBLIC: GitHub Open-Source (v2.0)/@syphon"
    include_patterns: List[str] = field(default_factory=lambda: ["*.*"])  # Wildcard patterns
    exclude_patterns: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class DOITAction:
    """DOIT action with communication optimization"""
    action_id: str
    command: str  # Direct action command
    context: str  # Context for the action
    intent: Optional[str] = None  # User intent/goal
    priority: int = 5  # 1-10, higher = more important
    syphon_target: Optional[UniversalSyphonTarget] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "action_id": self.action_id,
            "command": self.command,
            "context": self.context,
            "intent": self.intent,
            "priority": self.priority,
            "syphon_target": self.syphon_target.target_path if self.syphon_target else None,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat()
        }


class DOITUniversalSyphonIntegration:
    """
    Universal DOIT-SYPHON Integration

    Improves @doit with:
    1. Communication optimization (direct commands, context-rich)
    2. Universal syphon integration (wildcard-like "*.*")
    3. All-inclusive data capture
    4. Improved context and courage
    """

    def __init__(self, project_root: Path):
        """Initialize universal DOIT-SYPHON integration"""
        self.project_root = project_root
        self.syphon_target_path = "@🟢 PUBLIC: GitHub Open-Source (v2.0)/@syphon"

        # Initialize SYPHON if available
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None
            logger.warning("⚠️  SYPHON system not available")

        # Initialize DOIT if available
        if DOIT_AVAILABLE:
            try:
                self.doit = JARVISDOITExecutor(project_root)
                logger.info("✅ DOIT executor initialized")
            except Exception as e:
                logger.warning(f"⚠️  DOIT initialization failed: {e}")
                self.doit = None
        else:
            self.doit = None
            logger.warning("⚠️  DOIT executor not available")

        # Action queue
        self.action_queue: List[DOITAction] = []

        # Universal syphon target (wildcard-like)
        self.universal_syphon_target = UniversalSyphonTarget(
            target_path=self.syphon_target_path,
            include_patterns=["*.*"],  # All-inclusive
            metadata={
                "wildcard_mode": True,
                "all_inclusive": True,
                "capture_everything": True
            }
        )

        logger.info("=" * 80)
        logger.info("🚀 DOIT UNIVERSAL SYPHON INTEGRATION")
        logger.info("=" * 80)
        logger.info(f"   SYPHON Target: {self.syphon_target_path}")
        logger.info("   Wildcard Mode: *.* (all-inclusive)")
        logger.info("   Communication Optimization: Enabled")
        logger.info("=" * 80)

    def parse_command(self, command_text: str) -> DOITAction:
        """
        Parse command with communication optimization

        Extracts:
        - Direct action words
        - Context
        - Intent
        - Priority
        """
        # Extract action words
        action_words = ["start", "fix", "create", "update", "proceed", "implement", 
                       "configure", "build", "add", "remove", "change", "run"]

        command_lower = command_text.lower()
        action_word = None
        for word in action_words:
            if command_lower.startswith(word):
                action_word = word
                break

        # Extract context words
        context_words = ["since", "because", "so that", "after", "when", "if"]
        context = None
        for word in context_words:
            if word in command_lower:
                # Extract context clause
                parts = re.split(f"\\b{word}\\b", command_text, maxsplit=1)
                if len(parts) > 1:
                    context = parts[1].strip()
                break

        # Extract intent (if present)
        intent = None
        if "i want" in command_lower or "i need" in command_lower:
            intent_match = re.search(r"i (want|need) (.*?)(?:\.|$)", command_lower)
            if intent_match:
                intent = intent_match.group(2).strip()

        # Determine priority based on action word and urgency indicators
        priority = 5  # Default
        if action_word in ["start", "fix", "create"]:
            priority = 7
        if "urgent" in command_lower or "critical" in command_lower:
            priority = 9
        if "later" in command_lower or "when" in command_lower:
            priority = 3

        action_id = f"doit_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        return DOITAction(
            action_id=action_id,
            command=command_text,
            context=context or command_text,
            intent=intent,
            priority=priority,
            syphon_target=self.universal_syphon_target,
            metadata={
                "action_word": action_word,
                "parsed_at": datetime.now().isoformat(),
                "communication_score": self._score_communication(command_text)
            }
        )

    def _score_communication(self, text: str) -> int:
        """Score communication quality (0-10)"""
        score = 0
        text_lower = text.lower()

        # Action words
        action_words = ["start", "fix", "create", "update", "proceed"]
        if any(word in text_lower for word in action_words):
            score += 3

        # Context words
        context_words = ["since", "because", "so that"]
        if any(word in text_lower for word in context_words):
            score += 2

        # Direct command pattern
        if re.match(r"^(start|fix|create|update|proceed)", text_lower):
            score += 3

        # Intent statement
        if "i want" in text_lower or "i need" in text_lower:
            score += 2

        return min(score, 10)

    def execute_action(self, action: DOITAction) -> Dict[str, Any]:
        """
        Execute DOIT action with universal SYPHON integration

        All actions are automatically syphoned to the universal target.
        """
        logger.info(f"🚀 Executing action: {action.action_id}")
        logger.info(f"   Command: {action.command}")
        if action.context:
            logger.info(f"   Context: {action.context}")
        if action.intent:
            logger.info(f"   Intent: {action.intent}")

        result = {
            "action_id": action.action_id,
            "status": "executing",
            "started_at": datetime.now().isoformat(),
            "syphon_data": None
        }

        # Execute via DOIT if available
        if self.doit:
            try:
                # Execute the command
                doit_result = self.doit.execute_command(action.command)
                result["doit_result"] = doit_result
                result["status"] = "completed"
            except Exception as e:
                logger.error(f"❌ DOIT execution failed: {e}")
                result["status"] = "failed"
                result["error"] = str(e)
        else:
            logger.warning("⚠️  DOIT not available, action queued")
            result["status"] = "queued"

        # Universal SYPHON integration - capture everything
        if self.syphon:
            try:
                syphon_data = SyphonData(
                    data_id=f"doit_{action.action_id}",
                    source_type=DataSourceType.OTHER,
                    source_id=action.action_id,
                    content=action.command,
                    metadata={
                        "context": action.context,
                        "intent": action.intent,
                        "priority": action.priority,
                        "command": action.command,
                        "doit_result": result.get("doit_result"),
                        "status": result["status"]
                    },
                    actionable_items=[action.command],
                    tasks=[{
                        "task_id": action.action_id,
                        "command": action.command,
                        "context": action.context,
                        "priority": action.priority
                    }],
                    intelligence=[{
                        "type": "doit_action",
                        "action": action.to_dict(),
                        "result": result
                    }]
                )

                # Syphon to universal target (wildcard-like)
                syphon_result = self.syphon.extract_intelligence(syphon_data)
                result["syphon_data"] = syphon_data.to_dict()
                result["syphon_result"] = syphon_result

                # Save to syphon target path
                self._save_to_syphon_target(syphon_data, action.syphon_target)

                logger.info(f"✅ Action syphoned to: {action.syphon_target.target_path}")

            except Exception as e:
                logger.error(f"❌ SYPHON integration failed: {e}")
                result["syphon_error"] = str(e)

        result["completed_at"] = datetime.now().isoformat()
        return result

    def _save_to_syphon_target(self, syphon_data: SyphonData, target: UniversalSyphonTarget):
        """Save syphon data to target path (wildcard-like inclusion)"""
        try:
            # Parse target path
            # "@🟢 PUBLIC: GitHub Open-Source (v2.0)/@syphon"
            target_parts = target.target_path.split("/")

            # Create syphon data directory
            syphon_dir = self.project_root / "data" / "syphon" / "universal"
            syphon_dir.mkdir(parents=True, exist_ok=True)

            # Save with wildcard-like naming (all-inclusive)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"doit_syphon_{timestamp}_{syphon_data.data_id}.json"
            filepath = syphon_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(syphon_data.to_dict(), f, indent=2)

            logger.debug(f"💾 Saved to syphon target: {filepath}")

            # Also save to GitHub Open-Source structure if path exists
            github_path = self.project_root / ".cursor" / "skills" / "--syphon"
            if github_path.exists():
                github_path.mkdir(parents=True, exist_ok=True)
                github_file = github_path / filename
                with open(github_file, 'w', encoding='utf-8') as f:
                    json.dump(syphon_data.to_dict(), f, indent=2)
                logger.debug(f"💾 Also saved to GitHub structure: {github_file}")

        except Exception as e:
            logger.error(f"❌ Failed to save to syphon target: {e}")

    def process_command(self, command: str) -> Dict[str, Any]:
        """
        Process command with universal syphon integration

        This is the main entry point - all commands are:
        1. Parsed with communication optimization
        2. Executed via DOIT
        3. Automatically syphoned (wildcard-like "*.*")
        """
        # Parse command
        action = self.parse_command(command)

        # Add to queue
        self.action_queue.append(action)

        # Execute
        result = self.execute_action(action)

        return result

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about DOIT-SYPHON integration"""
        return {
            "total_actions": len(self.action_queue),
            "syphon_available": self.syphon is not None,
            "doit_available": self.doit is not None,
            "universal_target": self.universal_syphon_target.target_path,
            "wildcard_mode": True,
            "all_inclusive": True
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="DOIT Universal SYPHON Integration")
        parser.add_argument("command", nargs="?", help="Command to execute")
        parser.add_argument("--stats", action="store_true", help="Show statistics")
        args = parser.parse_args()

        integration = DOITUniversalSyphonIntegration(project_root)

        if args.stats:
            stats = integration.get_statistics()
            print("=" * 80)
            print("📊 DOIT UNIVERSAL SYPHON STATISTICS")
            print("=" * 80)
            for key, value in stats.items():
                print(f"  {key}: {value}")
            print()
        elif args.command:
            result = integration.process_command(args.command)
            print("=" * 80)
            print("✅ ACTION EXECUTED")
            print("=" * 80)
            print(json.dumps(result, indent=2))
        else:
            print("Usage: doit_universal_syphon_integration.py <command>")
            print("   or: doit_universal_syphon_integration.py --stats")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())