#!/usr/bin/env python3
"""
Kilo Code Peak Workflow Integration

Ensures Kilo Code utilizes peak Kilo Code workflows, automation, and validation.
"""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from peak_pattern_system import PeakPatternSystem

    PEAK_PATTERN_AVAILABLE = True
except ImportError:
    PEAK_PATTERN_AVAILABLE = False
    PeakPatternSystem = None


@dataclass
class KiloCodeWorkflowUsage:
    """Kilo Code workflow usage tracking"""

    workflow_id: str
    workflow_name: str
    peak_patterns_used: List[str] = field(default_factory=list)
    automation_enabled: bool = False
    validation_enabled: bool = False
    last_used: Optional[str] = None
    usage_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class KiloCodePeakIntegration:
    """
    Kilo Code Peak Workflow Integration

    Ensures Kilo Code utilizes:
    - Peak Kilo Code workflows
    - Automation
    - Validation
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("KiloCodePeakIntegration")

        # Directories
        self.data_dir = self.project_root / "data" / "kilo_code_peak"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.usage_file = self.data_dir / "workflow_usage.json"
        self.config_file = self.project_root / "config" / "kilo_code_optimized_config.json"

        # Peak pattern system
        self.peak_patterns = None
        if PEAK_PATTERN_AVAILABLE and PeakPatternSystem:
            try:
                self.peak_patterns = PeakPatternSystem(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Peak pattern system not available: {e}")

        # State
        self.workflow_usage: Dict[str, KiloCodeWorkflowUsage] = {}

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        # Load usage
        if self.usage_file.exists():
            try:
                with open(self.usage_file, encoding="utf-8") as f:
                    data = json.load(f)
                    for workflow_id, usage_data in data.items():
                        self.workflow_usage[workflow_id] = KiloCodeWorkflowUsage(**usage_data)
            except Exception as e:
                self.logger.error(f"Error loading usage: {e}")

    def _save_state(self):
        """Save state"""
        try:
            usage_data = {
                workflow_id: usage.to_dict() for workflow_id, usage in self.workflow_usage.items()
            }
            with open(self.usage_file, "w", encoding="utf-8") as f:
                json.dump(usage_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_state: {e}", exc_info=True)
            raise

    def ensure_peak_workflow_usage(
        self, workflow_id: str, workflow_name: str
    ) -> KiloCodeWorkflowUsage:
        """
        Ensure Kilo Code uses peak workflows, automation, validation

        Tracks usage and ensures peak patterns are utilized.
        """
        if workflow_id not in self.workflow_usage:
            self.workflow_usage[workflow_id] = KiloCodeWorkflowUsage(
                workflow_id=workflow_id, workflow_name=workflow_name
            )

        usage = self.workflow_usage[workflow_id]
        usage.last_used = datetime.now().isoformat()
        usage.usage_count += 1

        # Get peak patterns for workflow
        if self.peak_patterns:
            # Use find_patterns or get_pattern_suggestions to find relevant patterns
            # For now, search by workflow name in pattern tags/usage_context
            all_patterns = list(self.peak_patterns.patterns.values())
            relevant_patterns = [
                p
                for p in all_patterns
                if workflow_name.lower() in p.name.lower()
                or any(workflow_name.lower() in ctx.lower() for ctx in p.usage_context)
                or any(workflow_name.lower() in tag.lower() for tag in p.tags)
            ]
            usage.peak_patterns_used = [p.pattern_id for p in relevant_patterns]

        # Ensure automation is enabled
        usage.automation_enabled = self._check_automation_enabled(workflow_name)

        # Ensure validation is enabled
        usage.validation_enabled = self._check_validation_enabled(workflow_name)

        # If not using peak patterns, log warning
        if not usage.peak_patterns_used:
            self.logger.warning(f"⚠️ Kilo Code workflow {workflow_name} not using peak patterns")

        # If automation not enabled, log warning
        if not usage.automation_enabled:
            self.logger.warning(f"⚠️ Kilo Code workflow {workflow_name} automation not enabled")

        # If validation not enabled, log warning
        if not usage.validation_enabled:
            self.logger.warning(f"⚠️ Kilo Code workflow {workflow_name} validation not enabled")

        self._save_state()

        return usage

    def _check_automation_enabled(self, workflow_name: str) -> bool:
        """Check if automation is enabled for workflow"""
        # Check config
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    # Check automation settings
                    automation = config.get("automation", {})
                    return automation.get("enabled", False)
            except Exception as e:
                self.logger.debug(f"Could not check automation: {e}")
        return False

    def _check_validation_enabled(self, workflow_name: str) -> bool:
        """Check if validation is enabled for workflow"""
        # Check config
        if self.config_file.exists():
            try:
                with open(self.config_file, encoding="utf-8") as f:
                    config = json.load(f)
                    # Check validation settings
                    validation = config.get("validation", {})
                    return validation.get("enabled", False)
            except Exception as e:
                self.logger.debug(f"Could not check validation: {e}")
        return False

    def get_workflows_not_using_peak(self) -> List[str]:
        """Get workflows not using peak patterns"""
        return [
            workflow_name
            for workflow_id, usage in self.workflow_usage.items()
            if not usage.peak_patterns_used
        ]

    def get_workflows_missing_automation(self) -> List[str]:
        """Get workflows missing automation"""
        return [
            workflow_name
            for workflow_id, usage in self.workflow_usage.items()
            if not usage.automation_enabled
        ]

    def get_workflows_missing_validation(self) -> List[str]:
        """Get workflows missing validation"""
        return [
            workflow_name
            for workflow_id, usage in self.workflow_usage.items()
            if not usage.validation_enabled
        ]


def main():
    """Main execution for testing"""
    integration = KiloCodePeakIntegration()

    print("=" * 80)
    print("🔧 KILO CODE PEAK INTEGRATION")
    print("=" * 80)

    # Check workflow usage
    usage = integration.ensure_peak_workflow_usage("workflow_123", "TestWorkflow")

    print("\n📊 Workflow Usage:")
    print(f"   Peak Patterns Used: {len(usage.peak_patterns_used)}")
    print(f"   Automation Enabled: {usage.automation_enabled}")
    print(f"   Validation Enabled: {usage.validation_enabled}")


if __name__ == "__main__":

    main()