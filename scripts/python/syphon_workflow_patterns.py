#!/usr/bin/env python3
"""
SYPHON Workflow Pattern Extraction
Extract workflow patterns using SYPHON intelligence extraction
Integrates with @PEAK Pattern System

@SYPHON @PEAK #PATTERNS #WORKFLOWS @JARVIS
"""

import sys
import re
import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError as e:
    SYPHON_AVAILABLE = False
    logging.warning(f"SYPHON not available: {e}")

try:
    from scripts.python.peak_pattern_system import PeakPatternSystem, PeakPattern, PatternType, PatternQuality
    PEAK_AVAILABLE = True
except ImportError as e:
    PEAK_AVAILABLE = False
    logging.warning(f"Peak Pattern System not available: {e}")

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@dataclass
class WorkflowPattern:
    """Extracted workflow pattern"""
    pattern_id: str
    name: str
    description: str
    workflow_type: str  # e.g., "automation", "data_processing", "api_integration"
    steps: List[Dict[str, Any]]
    triggers: List[str]
    conditions: List[str]
    actions: List[str]
    metadata: Dict[str, Any]
    source_workflow: str
    extracted_at: str


class SYPHONWorkflowPatternExtractor:
    """
    Extract workflow patterns using SYPHON intelligence extraction
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize SYPHON workflow pattern extractor"""
        self.project_root = project_root or Path(__file__).parent.parent.parent

        # Initialize SYPHON
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(self.project_root)
                logger.info("✅ SYPHON system initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize SYPHON: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Initialize Peak Pattern System
        if PEAK_AVAILABLE:
            try:
                self.peak_system = PeakPatternSystem(project_root=self.project_root)
                logger.info("✅ @PEAK Pattern System initialized")
            except Exception as e:
                logger.error(f"❌ Failed to initialize Peak Pattern System: {e}")
                self.peak_system = None
        else:
            self.peak_system = None

        # Storage for extracted patterns
        self.patterns_storage = self.project_root / "data" / "workflow_patterns"
        self.patterns_storage.mkdir(parents=True, exist_ok=True)

        logger.info(f"SYPHON Workflow Pattern Extractor initialized")

    def extract_patterns_from_workflow(
        self,
        workflow_content: str,
        workflow_name: str,
        workflow_source: str = "unknown"
    ) -> List[WorkflowPattern]:
        """
        Extract patterns from workflow content using SYPHON

        Args:
            workflow_content: Workflow content (code, JSON, YAML, etc.)
            workflow_name: Name of the workflow
            workflow_source: Source of the workflow (file path, URL, etc.)

        Returns:
            List of extracted workflow patterns
        """
        logger.info(f"🔍 Extracting patterns from workflow: {workflow_name}")

        patterns = []

        # Use SYPHON to extract intelligence
        if self.syphon:
            try:
                # Use SYPHON's internal extraction methods directly
                actionable_items = self.syphon._extract_actionable_items(workflow_content)
                tasks = self.syphon._extract_tasks(workflow_content, workflow_name)
                decisions = self.syphon._extract_decisions(workflow_content)
                intelligence = self.syphon._extract_intelligence(workflow_content, workflow_name)

                logger.info(f"  📊 SYPHON extracted: {len(actionable_items)} actionable items, {len(tasks)} tasks, {len(decisions)} decisions")

                # Create workflow pattern from extracted data
                pattern = self._create_pattern_from_syphon_data(
                    workflow_name=workflow_name,
                    workflow_source=workflow_source,
                    actionable_items=actionable_items,
                    tasks=tasks,
                    decisions=decisions,
                    intelligence=intelligence,
                    workflow_content=workflow_content
                )

                if pattern:
                    patterns.append(pattern)

            except Exception as e:
                logger.error(f"❌ SYPHON extraction error: {e}", exc_info=True)

        # Also extract patterns directly from workflow structure
        direct_patterns = self._extract_direct_patterns(
            workflow_content=workflow_content,
            workflow_name=workflow_name,
            workflow_source=workflow_source
        )

        patterns.extend(direct_patterns)

        logger.info(f"✅ Extracted {len(patterns)} pattern(s) from workflow: {workflow_name}")

        return patterns

    def _create_pattern_from_syphon_data(
        self,
        workflow_name: str,
        workflow_source: str,
        actionable_items: List[str],
        tasks: List[Dict[str, Any]],
        decisions: List[Dict[str, Any]],
        intelligence: Dict[str, Any],
        workflow_content: str
    ) -> Optional[WorkflowPattern]:
        """Create workflow pattern from SYPHON extracted data"""

        # Classify workflow type
        workflow_type = self._classify_workflow_type(workflow_content, actionable_items)

        # Extract steps from actionable items
        steps = []
        for i, item in enumerate(actionable_items[:20]):  # Limit to top 20
            steps.append({
                "step_number": i + 1,
                "description": item,
                "type": self._classify_step_type(item)
            })

        # Extract triggers
        triggers = self._extract_triggers(workflow_content, actionable_items)

        # Extract conditions from decisions
        conditions = []
        for decision in decisions:
            if isinstance(decision, dict):
                condition_text = decision.get("text", decision.get("decision", ""))
                if condition_text:
                    conditions.append(condition_text)
            elif isinstance(decision, str):
                conditions.append(decision)

        # Extract actions from tasks
        actions = []
        for task in tasks:
            if isinstance(task, dict):
                action_text = task.get("text", task.get("task", ""))
                if action_text:
                    actions.append(action_text)
            elif isinstance(task, str):
                actions.append(task)

        # Create pattern ID
        pattern_id = f"workflow_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(workflow_name) % 10000}"

        pattern = WorkflowPattern(
            pattern_id=pattern_id,
            name=f"{workflow_name} Pattern",
            description=f"Extracted workflow pattern from {workflow_name}",
            workflow_type=workflow_type,
            steps=steps,
            triggers=triggers,
            conditions=conditions,
            actions=actions,
            metadata={
                "intelligence": intelligence if isinstance(intelligence, dict) else {"raw": intelligence},
                "source_workflow": workflow_name,
                "extraction_method": "SYPHON"
            },
            source_workflow=workflow_name,
            extracted_at=datetime.now().isoformat()
        )

        return pattern

    def _extract_direct_patterns(
        self,
        workflow_content: str,
        workflow_name: str,
        workflow_source: str
    ) -> List[WorkflowPattern]:
        """Extract patterns directly from workflow structure"""
        patterns = []

        # Look for common workflow patterns
        # 1. Step-by-step patterns
        step_patterns = re.finditer(r'(?:step|phase|stage)\s*[:\d]+\s*(.+?)(?:\n|$)', workflow_content, re.IGNORECASE)
        steps = []
        for match in step_patterns:
            steps.append({
                "step_number": len(steps) + 1,
                "description": match.group(1).strip(),
                "type": "manual"
            })

        if steps:
            pattern = WorkflowPattern(
                pattern_id=f"direct_pattern_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                name=f"{workflow_name} Direct Pattern",
                description=f"Directly extracted pattern from {workflow_name}",
                workflow_type=self._classify_workflow_type(workflow_content, []),
                steps=steps,
                triggers=self._extract_triggers(workflow_content, []),
                conditions=[],
                actions=[],
                metadata={"extraction_method": "direct"},
                source_workflow=workflow_name,
                extracted_at=datetime.now().isoformat()
            )
            patterns.append(pattern)

        return patterns

    def _classify_workflow_type(self, content: str, actionable_items: List[str]) -> str:
        """Classify workflow type"""
        content_lower = content.lower()
        items_text = " ".join(actionable_items).lower()
        combined = f"{content_lower} {items_text}"

        if any(word in combined for word in ["api", "endpoint", "request", "response"]):
            return "api_integration"
        elif any(word in combined for word in ["data", "process", "transform", "extract"]):
            return "data_processing"
        elif any(word in combined for word in ["automate", "trigger", "schedule", "cron"]):
            return "automation"
        elif any(word in combined for word in ["test", "validate", "verify", "check"]):
            return "testing"
        elif any(word in combined for word in ["deploy", "build", "compile", "release"]):
            return "deployment"
        else:
            return "general"

    def _classify_step_type(self, step_text: str) -> str:
        """Classify step type"""
        step_lower = step_text.lower()

        if any(word in step_lower for word in ["check", "verify", "validate"]):
            return "validation"
        elif any(word in step_lower for word in ["extract", "get", "fetch", "retrieve"]):
            return "extraction"
        elif any(word in step_lower for word in ["process", "transform", "convert"]):
            return "processing"
        elif any(word in step_lower for word in ["save", "store", "write", "persist"]):
            return "storage"
        elif any(word in step_lower for word in ["send", "post", "submit", "notify"]):
            return "notification"
        else:
            return "action"

    def _extract_triggers(self, content: str, actionable_items: List[str]) -> List[str]:
        """Extract workflow triggers"""
        triggers = []

        # Look for trigger patterns
        trigger_patterns = [
            r'trigger[:\s]+(.+?)(?:\n|$)',
            r'when[:\s]+(.+?)(?:\n|$)',
            r'on[:\s]+(.+?)(?:\n|$)',
            r'schedule[:\s]+(.+?)(?:\n|$)',
            r'cron[:\s]+(.+?)(?:\n|$)',
        ]

        for pattern in trigger_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                trigger = match.group(1).strip()
                if trigger and trigger not in triggers:
                    triggers.append(trigger)

        return triggers

    def register_pattern_to_peak(
        self,
        workflow_pattern: WorkflowPattern
    ) -> bool:
        """
        Register workflow pattern to @PEAK Pattern System

        Args:
            workflow_pattern: Workflow pattern to register

        Returns:
            True if successfully registered
        """
        if not self.peak_system:
            logger.warning("⚠️  Peak Pattern System not available")
            return False

        try:
            # Convert workflow pattern to Peak pattern
            peak_pattern = PeakPattern(
                pattern_id=workflow_pattern.pattern_id,
                name=workflow_pattern.name,
                pattern_type=PatternType.PATTERN,  # Default type
                description=workflow_pattern.description,
                code_example=json.dumps(asdict(workflow_pattern), indent=2),
                usage_context=[workflow_pattern.source_workflow],
                quality=PatternQuality.GOOD,
                tags=["workflow", workflow_pattern.workflow_type, "syphon_extracted"],
                metadata={
                    "workflow_type": workflow_pattern.workflow_type,
                    "steps_count": len(workflow_pattern.steps),
                    "triggers": workflow_pattern.triggers,
                    "conditions": workflow_pattern.conditions,
                    "actions": workflow_pattern.actions,
                    "source_workflow": workflow_pattern.source_workflow,
                    "extracted_at": workflow_pattern.extracted_at
                }
            )

            # Register pattern
            success = self.peak_system.register_pattern(peak_pattern, merge_existing=True)

            if success:
                logger.info(f"✅ Registered workflow pattern to @PEAK: {workflow_pattern.name}")
            else:
                logger.warning(f"⚠️  Failed to register pattern: {workflow_pattern.name}")

            return success

        except Exception as e:
            logger.error(f"❌ Error registering pattern to @PEAK: {e}", exc_info=True)
            return False

    def save_pattern(self, pattern: WorkflowPattern) -> bool:
        """Save extracted pattern to disk"""
        try:
            pattern_file = self.patterns_storage / f"{pattern.pattern_id}.json"

            pattern_dict = asdict(pattern)

            with open(pattern_file, "w", encoding="utf-8") as f:
                json.dump(pattern_dict, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Saved pattern: {pattern_file}")
            return True

        except Exception as e:
            logger.error(f"❌ Error saving pattern: {e}", exc_info=True)
            return False

    def extract_from_file(self, file_path: Path) -> List[WorkflowPattern]:
        """Extract patterns from a workflow file"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            return self.extract_patterns_from_workflow(
                workflow_content=content,
                workflow_name=file_path.stem,
                workflow_source=str(file_path)
            )

        except Exception as e:
            logger.error(f"❌ Error reading file {file_path}: {e}")
            return []


def main():
    """Example usage"""
    print("=" * 70)
    print("🔍 SYPHON Workflow Pattern Extraction")
    print("=" * 70)
    print()

    extractor = SYPHONWorkflowPatternExtractor()

    # Example workflow content
    example_workflow = """
    Workflow: Disable All Lighting

    STEP 1: Repair keyboard control (fn+F4)
    STEP 2: Disable lighting via UI automation
    STEP 3: Set registry values
    STEP 4: Verify keyboard shortcut still works

    Trigger: Manual or scheduled
    Conditions: Armoury Crate must be running
    Actions: Disable lighting, preserve keyboard shortcut
    """

    print("📋 Extracting patterns from example workflow...")
    patterns = extractor.extract_patterns_from_workflow(
        workflow_content=example_workflow,
        workflow_name="Disable All Lighting",
        workflow_source="example"
    )

    print(f"✅ Extracted {len(patterns)} pattern(s)")
    print()

    for pattern in patterns:
        print(f"📊 Pattern: {pattern.name}")
        print(f"   Type: {pattern.workflow_type}")
        print(f"   Steps: {len(pattern.steps)}")
        print(f"   Triggers: {len(pattern.triggers)}")
        print(f"   Conditions: {len(pattern.conditions)}")
        print(f"   Actions: {len(pattern.actions)}")
        print()

        # Save pattern
        extractor.save_pattern(pattern)

        # Register to @PEAK
        if extractor.register_pattern_to_peak(pattern):
            print(f"   ✅ Registered to @PEAK Pattern System")
        print()

    print("=" * 70)
    print("✅ SYPHON Workflow Pattern Extraction Complete!")
    print("=" * 70)


if __name__ == "__main__":


    main()