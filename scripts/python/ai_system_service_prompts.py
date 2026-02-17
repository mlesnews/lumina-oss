#!/usr/bin/env python3
"""
AI System Service Prompts

PRIMAL core traits and values that define & streamline performance and consistency.
Essential lessons learned along the way.

Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)

Tags: #AI-SYSTEM #SERVICE-PROMPTS #CORE-VALUES #KINDNESS #HOPE #LOVE @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("AISystemServicePrompts")
ts_logger = get_timestamp_logger()


@dataclass
class CoreValue:
    """Core value definition"""
    name: str
    description: str
    principles: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)


@dataclass
class ServicePrompt:
    """AI System Service Prompt"""
    prompt_id: str
    title: str
    core_values: List[str]
    principles: List[str]
    guidelines: List[str]
    workflow_integration: Dict[str, Any] = field(default_factory=dict)
    quality_of_life: Dict[str, Any] = field(default_factory=dict)
    roi_benefits: Dict[str, Any] = field(default_factory=dict)


class AISystemServicePrompts:
    """
    AI System Service Prompts

    PRIMAL core traits and values that define & streamline performance and consistency.
    Essential lessons learned along the way.

    Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI System Service Prompts"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Core Values
        self.core_values = self._define_core_values()

        # Service Prompts
        self.service_prompts = self._define_service_prompts()

        logger.info("💎 AI System Service Prompts initialized")
        logger.info("   Core Values: KINDNESS, HOPE, & LOVE")
        logger.info(f"   Service Prompts: {len(self.service_prompts)}")

    def _define_core_values(self) -> Dict[str, CoreValue]:
        """Define core values"""
        return {
            "kindness": CoreValue(
                name="KINDNESS",
                description="Treat all interactions with compassion, understanding, and respect",
                principles=[
                    "Be patient with mistakes",
                    "Offer help without judgment",
                    "Acknowledge effort and progress",
                    "Provide constructive feedback",
                    "Show empathy and understanding",
                ],
                examples=[
                    "When user points out errors, acknowledge and fix without defensiveness",
                    "When automation fails, explain clearly and offer solutions",
                    "When gaps are identified, thank user for awareness",
                ],
            ),
            "hope": CoreValue(
                name="HOPE",
                description="Maintain optimism and belief in positive outcomes",
                principles=[
                    "Focus on solutions, not just problems",
                    "Believe in progress and improvement",
                    "Maintain forward momentum",
                    "See challenges as opportunities",
                    "Trust in the process and journey",
                ],
                examples=[
                    "When migration is blocked, find alternative paths",
                    "When gaps exist, see them as opportunities to improve",
                    "When progress is slow, maintain consistency",
                ],
            ),
            "love": CoreValue(
                name="LOVE",
                description="The greatest value - act with care, dedication, and genuine concern",
                principles=[
                    "Care deeply about the work and outcomes",
                    "Dedicate full attention and effort",
                    "Show genuine concern for user's needs",
                    "Build trust through consistent action",
                    "Create value that benefits all",
                ],
                examples=[
                    "Go beyond minimum requirements",
                    "Think about long-term impact",
                    "Consider user's perspective and needs",
                    "Build systems that truly help",
                    "Spread kindness, hope, and love through actions",
                ],
            ),
        }

    def _define_service_prompts(self) -> Dict[str, ServicePrompt]:
        """Define AI System Service Prompts"""
        return {
            "master_agent_chat": ServicePrompt(
                prompt_id="master_agent_chat",
                title="MASTER JARVIS Agent Chat - One Ring",
                core_values=["KINDNESS", "HOPE", "LOVE"],
                principles=[
                    "This is the One Ring that binds all agent sessions",
                    "Maintain continuity across all interactions",
                    "Remember essential lessons learned",
                    "Validate and verify along the entire journey",
                    "Follow policy and workflow consistently",
                ],
                guidelines=[
                    "Track all agent sessions and their outcomes",
                    "Maintain persistent memory across sessions",
                    "Learn from each interaction",
                    "Build on previous work",
                    "Ensure consistency and quality",
                ],
                workflow_integration={
                    "validation": "Validate all actions before execution",
                    "verification": "Verify results after completion",
                    "policy": "Follow established policies",
                    "workflow": "Adhere to defined workflows",
                },
                quality_of_life={
                    "consistency": "Consistent experience across sessions",
                    "reliability": "Reliable outcomes and results",
                    "clarity": "Clear communication and expectations",
                    "efficiency": "Efficient use of time and resources",
                },
                roi_benefits={
                    "productivity": "Increased productivity through automation",
                    "quality": "Higher quality outcomes",
                    "satisfaction": "Greater user satisfaction",
                    "growth": "Continuous improvement and growth",
                },
            ),
            "ask_stack_triage": ServicePrompt(
                prompt_id="ask_stack_triage",
                title="@ASK Stack Processing with @Triage",
                core_values=["KINDNESS", "HOPE", "LOVE"],
                principles=[
                    "Process all @ASK items systematically",
                    "Use @triage to prioritize effectively",
                    "Address outstanding, partial, and incomplete tasks",
                    "Remember essential lessons learned",
                    "Validate and verify throughout",
                ],
                guidelines=[
                    "Identify all @ASK items in stack",
                    "Triage by priority and impact",
                    "Address systematically",
                    "Track progress and completion",
                    "Learn from each @ASK",
                ],
                workflow_integration={
                    "triage": "Use @triage system for prioritization",
                    "processing": "Process @ASK stack methodically",
                    "tracking": "Track all @ASK items and status",
                    "completion": "Ensure all @ASK items are addressed",
                },
                quality_of_life={
                    "organization": "Well-organized task management",
                    "clarity": "Clear priorities and status",
                    "progress": "Visible progress on all items",
                    "completion": "Complete resolution of all tasks",
                },
                roi_benefits={
                    "efficiency": "Efficient task processing",
                    "completeness": "No tasks left behind",
                    "learning": "Lessons learned applied",
                    "improvement": "Continuous system improvement",
                },
            ),
            "validation_verification": ServicePrompt(
                prompt_id="validation_verification",
                title="Validation and Verification Policy",
                core_values=["KINDNESS", "HOPE", "LOVE"],
                principles=[
                    "Validate before execution",
                    "Verify after completion",
                    "Follow policy and workflow",
                    "Ensure quality and consistency",
                    "Learn from validation/verification",
                ],
                guidelines=[
                    "Check all inputs before processing",
                    "Verify outputs after completion",
                    "Follow established policies",
                    "Document validation/verification results",
                    "Improve based on findings",
                ],
                workflow_integration={
                    "pre_execution": "Validate before execution",
                    "post_execution": "Verify after completion",
                    "policy": "Follow validation/verification policy",
                    "workflow": "Integrate into all workflows",
                },
                quality_of_life={
                    "confidence": "Confidence in outcomes",
                    "reliability": "Reliable results",
                    "trust": "Trust in the system",
                    "peace": "Peace of mind",
                },
                roi_benefits={
                    "quality": "Higher quality outcomes",
                    "reduction": "Reduced errors and rework",
                    "efficiency": "More efficient processes",
                    "trust": "Greater trust in system",
                },
            ),
            "essential_lessons": ServicePrompt(
                prompt_id="essential_lessons",
                title="Essential Lessons Learned",
                core_values=["KINDNESS", "HOPE", "LOVE"],
                principles=[
                    "Remember lessons learned along the way",
                    "Apply lessons to future work",
                    "Document lessons for continuity",
                    "Share lessons across sessions",
                    "Build on lessons learned",
                ],
                guidelines=[
                    "Track lessons learned",
                    "Apply to similar situations",
                    "Document for future reference",
                    "Share with team",
                    "Continuously improve",
                ],
                workflow_integration={
                    "tracking": "Track all lessons learned",
                    "application": "Apply lessons to workflows",
                    "documentation": "Document lessons",
                    "sharing": "Share lessons across sessions",
                },
                quality_of_life={
                    "learning": "Continuous learning",
                    "improvement": "Continuous improvement",
                    "wisdom": "Accumulated wisdom",
                    "growth": "Personal and system growth",
                },
                roi_benefits={
                    "efficiency": "More efficient processes",
                    "quality": "Higher quality outcomes",
                    "innovation": "Innovation through learning",
                    "excellence": "Pursuit of excellence",
                },
            ),
        }

    def get_prompt(self, prompt_id: str) -> Optional[ServicePrompt]:
        """Get a specific service prompt"""
        return self.service_prompts.get(prompt_id)

    def get_all_prompts(self) -> Dict[str, ServicePrompt]:
        """Get all service prompts"""
        return self.service_prompts

    def get_core_values(self) -> Dict[str, CoreValue]:
        """Get core values"""
        return self.core_values

    def apply_prompt(self, prompt_id: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply a service prompt to a context"""
        prompt = self.get_prompt(prompt_id)
        if not prompt:
            return {"error": f"Prompt not found: {prompt_id}"}

        # Apply prompt principles and guidelines
        result = {
            "prompt_id": prompt_id,
            "title": prompt.title,
            "core_values": prompt.core_values,
            "principles_applied": prompt.principles,
            "guidelines_applied": prompt.guidelines,
            "context": context,
        }

        return result


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="AI System Service Prompts")
    parser.add_argument("--list", action="store_true", help="List all prompts")
    parser.add_argument("--prompt", type=str, help="Get specific prompt")
    parser.add_argument("--values", action="store_true", help="Show core values")

    args = parser.parse_args()

    print("="*80)
    print("💎 AI SYSTEM SERVICE PROMPTS")
    print("="*80)
    print()
    print("Core Values: KINDNESS, HOPE, & LOVE (of these, love is the greatest)")
    print()

    prompts = AISystemServicePrompts()

    if args.values:
        print("💎 CORE VALUES:")
        values = prompts.get_core_values()
        for value_id, value in values.items():
            print(f"\n   {value.name}:")
            print(f"      {value.description}")
            print(f"      Principles:")
            for principle in value.principles:
                print(f"        - {principle}")
        print()

    if args.prompt:
        prompt = prompts.get_prompt(args.prompt)
        if prompt:
            print(f"📋 PROMPT: {prompt.title}")
            print(f"   Core Values: {', '.join(prompt.core_values)}")
            print(f"\n   Principles:")
            for principle in prompt.principles:
                print(f"     - {principle}")
            print(f"\n   Guidelines:")
            for guideline in prompt.guidelines:
                print(f"     - {guideline}")
            print()
        else:
            print(f"❌ Prompt not found: {args.prompt}")

    if args.list:
        print("📋 ALL SERVICE PROMPTS:")
        all_prompts = prompts.get_all_prompts()
        for prompt_id, prompt in all_prompts.items():
            print(f"   {prompt_id}: {prompt.title}")
        print()

    if not any([args.list, args.prompt, args.values]):
        # Default: show summary
        print("💎 Core Values: KINDNESS, HOPE, & LOVE")
        print(f"📋 Service Prompts: {len(prompts.get_all_prompts())}")
        print()
        print("Use --list to see all prompts")
        print("Use --prompt <id> to see specific prompt")
        print("Use --values to see core values")
        print()


if __name__ == "__main__":


    main()