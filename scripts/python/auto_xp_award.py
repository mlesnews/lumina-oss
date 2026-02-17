#!/usr/bin/env python3
"""
Auto XP Award Helper
Call this after successful task completion to automatically award XP
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.ai_experience_system import auto_award_task_completion, TaskComplexity, TaskIntensity


def award_task_xp(task_description: str, complexity=None, intensity=None):
    """
    Helper function to award XP after task completion
    Call this after successfully completing a task

    Args:
        task_description: Description of completed task
        complexity: Optional TaskComplexity enum
        intensity: Optional TaskIntensity enum
    """
    try:
        reward, level_info = auto_award_task_completion(
            task_description=task_description,
            complexity=complexity,
            intensity=intensity,
            success=True
        )

        # Silent success - just award, don't print (can be called from other scripts)
        return reward, level_info
    except Exception as e:
        # Fail silently if there's an error
        return None, None


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Auto XP Award for Task Completion")
    parser.add_argument("--task", required=True, help="Task description")
    parser.add_argument("--complexity", choices=[c.value for c in TaskComplexity],
                       help="Task complexity level")
    parser.add_argument("--intensity", choices=[i.value for i in TaskIntensity],
                       help="Task intensity level")

    args = parser.parse_args()

    complexity = TaskComplexity[args.complexity.upper()] if args.complexity else None
    intensity = TaskIntensity[args.intensity.upper()] if args.intensity else None

    reward, level_info = auto_award_task_completion(
        task_description=args.task,
        complexity=complexity,
        intensity=intensity,
        success=True
    )

    print(f"✅ Auto-awarded +{reward.total_xp} XP for: {args.task}")
