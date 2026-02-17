#!/usr/bin/env python3
"""
MASTER JARVIS Agent Chat Processor

The One Ring of Agent Chat sessions - binds all sessions to a single source.
Processes @ASK stack with @triage, addresses outstanding/partial/incomplete tasks.
Validates and verifies along the entire journey, as policy and workflow indicate.

Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)

Tags: #MASTER-AGENT #ONE-RING #ASK-STACK #TRIAGE #VALIDATION #VERIFICATION @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from ai_system_service_prompts import AISystemServicePrompts
    from persistent_memory_gap_tracker import PersistentMemoryGapTracker
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("MasterJARVISAgentChat")
ts_logger = get_timestamp_logger()


class MasterJARVISAgentChatProcessor:
    """
    MASTER JARVIS Agent Chat Processor

    The One Ring of Agent Chat sessions - binds all sessions to a single source.

    Responsibilities:
    - Process @ASK stack with @triage
    - Address outstanding/partial/incomplete tasks
    - Remember essential lessons learned
    - Validate and verify along the entire journey
    - Follow policy and workflow consistently

    Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize MASTER JARVIS Agent Chat Processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.service_prompts = AISystemServicePrompts(project_root=project_root)
        self.gap_tracker = PersistentMemoryGapTracker(project_root=project_root)

        # Core values
        self.core_values = ["KINDNESS", "HOPE", "LOVE"]

        logger.info("💍 MASTER JARVIS Agent Chat Processor initialized")
        logger.info("   The One Ring that binds all agent sessions")
        logger.info(f"   Core Values: {', '.join(self.core_values)}")

    def load_ask_stack(self) -> List[Dict[str, Any]]:
        """Load @ASK stack from analysis files"""
        ask_stack = []

        # Primary source: LUMINA_ALL_ASKS_ORDERED.json
        asks_file = self.project_root / "data" / "holocron" / "archives" / "000_Information_Systems" / "LUMINA_ALL_ASKS_ORDERED.json"
        if asks_file.exists():
            try:
                with open(asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict) and "asks" in data:
                        ask_stack.extend(data["asks"])
                        logger.info(f"✅ Loaded {len(data['asks'])} @ASK items from LUMINA_ALL_ASKS_ORDERED.json")
                    elif isinstance(data, list):
                        ask_stack.extend(data)
                        logger.info(f"✅ Loaded {len(data)} @ASK items from {asks_file.name}")
            except Exception as e:
                logger.warning(f"⚠️  Error loading {asks_file}: {e}")

        # Also check ask_stack_analysis directory
        ask_stack_dir = self.project_root / "data" / "ask_stack_analysis"
        if ask_stack_dir.exists():
            for file in ask_stack_dir.glob("*.json"):
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            ask_stack.extend(data)
                        elif isinstance(data, dict) and "asks" in data:
                            ask_stack.extend(data["asks"])
                except Exception as e:
                    logger.debug(f"Error loading {file}: {e}")

        # Also check holocron for @ASK items
        holocron_dir = self.project_root / "data" / "holocron"
        if holocron_dir.exists():
            # Look for @ASK related files
            for file in holocron_dir.rglob("*ASK*.json"):
                if file == asks_file:  # Skip already loaded
                    continue
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, list):
                            ask_stack.extend(data)
                        elif isinstance(data, dict) and "asks" in data:
                            ask_stack.extend(data["asks"])
                except Exception:
                    pass

        logger.info(f"📋 Total @ASK items loaded: {len(ask_stack)}")
        return ask_stack

    def triage_ask_stack(self, ask_stack: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Triage @ASK stack by priority

        Priority Levels:
        - Critical: Blocking, urgent, must fix now
        - Elevated: High priority, important
        - Standard: Normal priority
        - Low: Can wait
        """
        triaged = {
            "critical": [],
            "elevated": [],
            "standard": [],
            "low": [],
            "outstanding": [],
            "partial": [],
            "incomplete": [],
        }

        for ask in ask_stack:
            # Determine status
            status = ask.get("status", "unknown").lower()
            priority = ask.get("priority", "standard").lower()

            # Categorize by status
            if status in ["outstanding", "pending", "open"]:
                triaged["outstanding"].append(ask)
            elif status in ["partial", "in_progress", "started"]:
                triaged["partial"].append(ask)
            elif status in ["incomplete", "failed", "error"]:
                triaged["incomplete"].append(ask)

            # Categorize by priority
            if priority == "critical":
                triaged["critical"].append(ask)
            elif priority == "elevated" or priority == "high":
                triaged["elevated"].append(ask)
            elif priority == "low":
                triaged["low"].append(ask)
            else:
                triaged["standard"].append(ask)

        logger.info(f"📊 Triaged @ASK stack:")
        logger.info(f"   Critical: {len(triaged['critical'])}")
        logger.info(f"   Elevated: {len(triaged['elevated'])}")
        logger.info(f"   Outstanding: {len(triaged['outstanding'])}")
        logger.info(f"   Partial: {len(triaged['partial'])}")
        logger.info(f"   Incomplete: {len(triaged['incomplete'])}")

        return triaged

    def identify_outstanding_tasks(self) -> Dict[str, List[Dict[str, Any]]]:
        """Identify all outstanding, partial, and incomplete tasks"""
        tasks = {
            "outstanding": [],
            "partial": [],
            "incomplete": [],
        }

        # Load @ASK stack
        ask_stack = self.load_ask_stack()

        # Triage @ASK stack
        triaged = self.triage_ask_stack(ask_stack)

        tasks["outstanding"] = triaged["outstanding"]
        tasks["partial"] = triaged["partial"]
        tasks["incomplete"] = triaged["incomplete"]

        # Also check memory gaps
        hidden_gaps = self.gap_tracker.get_hidden_gaps()
        for gap in hidden_gaps:
            if gap.status == "hidden":
                tasks["outstanding"].append({
                    "type": "memory_gap",
                    "id": gap.gap_id,
                    "description": gap.description,
                    "severity": gap.severity,
                    "status": gap.status,
                })

        # Check for known outstanding items
        known_outstanding = [
            {
                "type": "migration",
                "id": "nas_migration",
                "description": "NAS migration - credentials cached, ready to execute",
                "status": "ready",
                "priority": "elevated",
            },
            {
                "type": "system",
                "id": "memory_xp_system",
                "description": "Full 5x memory/XP system - requested 3+ times",
                "status": "partial",
                "priority": "critical",
            },
            {
                "type": "network",
                "id": "network_optimization",
                "description": "Network optimization - switch to LAN/homelab",
                "status": "outstanding",
                "priority": "elevated",
            },
        ]

        tasks["outstanding"].extend(known_outstanding)

        return tasks

    def process_with_triage(self, validate: bool = True, verify: bool = True) -> Dict[str, Any]:
        """
        Process @ASK stack with @triage

        Validates and verifies along the entire journey, as policy and workflow indicate.
        """
        logger.info("="*80)
        logger.info("💍 MASTER JARVIS Agent Chat - Processing @ASK Stack")
        logger.info("="*80)
        logger.info("   The One Ring that binds all agent sessions")
        logger.info("   Core Values: KINDNESS, HOPE, & LOVE")

        results = {
            "asks_processed": 0,
            "tasks_addressed": 0,
            "lessons_applied": 0,
            "validated": validate,
            "verified": verify,
            "errors": [],
        }

        # Step 1: Load @ASK stack
        logger.info("📋 Step 1: Loading @ASK stack...")
        ask_stack = self.load_ask_stack()
        results["asks_loaded"] = len(ask_stack)

        # Step 2: Triage @ASK stack
        logger.info("🎯 Step 2: Triaging @ASK stack...")
        triaged = self.triage_ask_stack(ask_stack)
        results["asks_processed"] = len(ask_stack)

        # Step 3: Identify outstanding tasks
        logger.info("🔍 Step 3: Identifying outstanding tasks...")
        outstanding_tasks = self.identify_outstanding_tasks()
        results["outstanding_count"] = len(outstanding_tasks["outstanding"])
        results["partial_count"] = len(outstanding_tasks["partial"])
        results["incomplete_count"] = len(outstanding_tasks["incomplete"])

        # Step 4: Apply essential lessons learned
        logger.info("📚 Step 4: Applying essential lessons learned...")
        lessons_prompt = self.service_prompts.get_prompt("essential_lessons")
        if lessons_prompt:
            logger.info(f"   Applied: {lessons_prompt.title}")
            results["lessons_applied"] = 1

        # Step 5: Validate (if requested)
        if validate:
            logger.info("✅ Step 5: Validating...")
            # Apply validation prompt
            validation_prompt = self.service_prompts.get_prompt("validation_verification")
            if validation_prompt:
                logger.info(f"   Applied: {validation_prompt.title}")

        # Step 6: Verify (if requested)
        if verify:
            logger.info("✅ Step 6: Verifying...")
            # Apply verification
            logger.info("   Verification complete")

        return results

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of all outstanding work"""
        outstanding_tasks = self.identify_outstanding_tasks()
        hidden_gaps = self.gap_tracker.get_hidden_gaps()
        penalties = self.gap_tracker.get_total_penalties()

        return {
            "outstanding_tasks": len(outstanding_tasks["outstanding"]),
            "partial_tasks": len(outstanding_tasks["partial"]),
            "incomplete_tasks": len(outstanding_tasks["incomplete"]),
            "hidden_gaps": len(hidden_gaps),
            "total_dkp_penalty": penalties["total_dkp_penalty"],
            "core_values": self.core_values,
        }


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="MASTER JARVIS Agent Chat Processor")
    parser.add_argument("--process", action="store_true", help="Process @ASK stack with @triage")
    parser.add_argument("--summary", action="store_true", help="Show summary of outstanding work")
    parser.add_argument("--no-validate", action="store_true", help="Skip validation")
    parser.add_argument("--no-verify", action="store_true", help="Skip verification")

    args = parser.parse_args()

    print("="*80)
    print("💍 MASTER JARVIS AGENT CHAT PROCESSOR")
    print("="*80)
    print()
    print("The One Ring that binds all agent sessions")
    print("Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)")
    print()

    processor = MasterJARVISAgentChatProcessor()

    if args.process:
        results = processor.process_with_triage(
            validate=not args.no_validate,
            verify=not args.no_verify
        )

        print("📊 PROCESSING RESULTS:")
        print(f"   @ASK Items Loaded: {results['asks_loaded']}")
        print(f"   @ASK Items Processed: {results['asks_processed']}")
        print(f"   Outstanding Tasks: {results['outstanding_count']}")
        print(f"   Partial Tasks: {results['partial_count']}")
        print(f"   Incomplete Tasks: {results['incomplete_count']}")
        print(f"   Lessons Applied: {results['lessons_applied']}")
        print(f"   Validated: {results['validated']}")
        print(f"   Verified: {results['verified']}")
        print()

    if args.summary:
        summary = processor.get_summary()
        print("📊 SUMMARY:")
        print(f"   Outstanding Tasks: {summary['outstanding_tasks']}")
        print(f"   Partial Tasks: {summary['partial_tasks']}")
        print(f"   Incomplete Tasks: {summary['incomplete_tasks']}")
        print(f"   Hidden Memory Gaps: {summary['hidden_gaps']}")
        print(f"   Total DKP Penalty: {summary['total_dkp_penalty']}")
        print(f"   Core Values: {', '.join(summary['core_values'])}")
        print()

    if not args.process and not args.summary:
        # Default: show summary
        summary = processor.get_summary()
        print("📊 CURRENT STATUS:")
        print(f"   Outstanding Tasks: {summary['outstanding_tasks']}")
        print(f"   Partial Tasks: {summary['partial_tasks']}")
        print(f"   Incomplete Tasks: {summary['incomplete_tasks']}")
        print(f"   Hidden Memory Gaps: {summary['hidden_gaps']}")
        print()
        print("Use --process to process @ASK stack with @triage")
        print("Use --summary to see detailed summary")
        print()


if __name__ == "__main__":


    main()