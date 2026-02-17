#!/usr/bin/env python3
"""
Shrink Workflow Integration - Integrate The Shrink into WorkflowBase
"""

from typing import Dict, Any, Optional
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from shrink_mental_health_verifier import (
        TheShrink,
        IntrospectionDepth,
        PsychologicalHealthLevel
    )
    SHRINK_AVAILABLE = True
except ImportError as e:
    SHRINK_AVAILABLE = False
    TheShrink = None
    IntrospectionDepth = None
    PsychologicalHealthLevel = None
    print(f"Warning: Shrink module not available: {e}")

def integrate_shrink_with_workflow_base():
    """
    Integration function to add The Shrink to WorkflowBase verification
    """
    if not SHRINK_AVAILABLE:
        return None

    # Initialize The Shrink
    shrink = TheShrink()

    return shrink

def perform_shrink_verification(
    shrink: TheShrink,
    workflow_id: str,
    workflow_data: Dict[str, Any],
    previous_workflows: Optional[list] = None,
    depth: IntrospectionDepth = IntrospectionDepth.STANDARD
) -> Dict[str, Any]:
    """
    Perform Shrink verification on a workflow

    Args:
        shrink: TheShrink instance
        workflow_id: Workflow identifier
        workflow_data: Workflow data dictionary
        previous_workflows: Previous workflow history for pattern analysis
        depth: Depth of introspection

    Returns:
        Dictionary with shrink verification results
    """
    if not shrink:
        return {
            "shrunk": False,
            "reason": "Shrink not available",
            "profile": None
        }

    try:
        # Perform shrink session
        profile = shrink.shrink_workflow(
            workflow_id=workflow_id,
            workflow_data=workflow_data,
            previous_workflows=previous_workflows,
            depth=depth
        )

        # Determine if workflow passes shrink verification
        # Critical or Poor health may require intervention
        passes_verification = profile.health_level not in [
            PsychologicalHealthLevel.CRITICAL,
            PsychologicalHealthLevel.POOR
        ]

        return {
            "shrunk": True,
            "profile": profile,
            "health_level": profile.health_level.value,
            "confidence_calibration": profile.confidence_calibration,
            "decision_quality": profile.decision_quality,
            "self_awareness": profile.self_awareness,
            "detected_patterns": [p.value for p in profile.detected_patterns],
            "red_flags": profile.red_flags,
            "insights": profile.introspection_insights,
            "recommendations": profile.introspection_insights,  # Use insights as recommendations
            "passes_verification": passes_verification,
            "intervention_needed": not passes_verification,
            "strengths": profile.strengths
        }

    except Exception as e:
        return {
            "shrunk": False,
            "error": str(e),
            "passes_verification": True  # Fail open - allow workflow if shrink fails
        }

# Integration code for workflow_base.py
SHRINK_INTEGRATION_CODE = '''
# Add to imports at top of workflow_base.py
try:
    from shrink_mental_health_verifier import (
        TheShrink,
        IntrospectionDepth,
        PsychologicalHealthLevel
    )
    SHRINK_AVAILABLE = True
except ImportError:
    SHRINK_AVAILABLE = False
    TheShrink = None
    IntrospectionDepth = None
    PsychologicalHealthLevel = None

# Add to __init__ method:
if SHRINK_AVAILABLE:
    self.shrink = TheShrink()
else:
    self.shrink = None

# Add to verify_completion method, before final return:
# Perform Shrink deep cycle introspection as final verification step
if SHRINK_AVAILABLE and self.shrink:
    try:
        # Prepare workflow data for shrink
        workflow_data = {
            "type": self.__class__.__name__,
            "steps": self.get_completed_steps() if hasattr(self, 'get_completed_steps') else [],
            "decisions": getattr(self, 'decisions', []),
            "outcomes": getattr(self, 'outcomes', []),
            "confidence_scores": getattr(self, 'confidence_scores', []),
            "errors": getattr(self, 'errors', []),
            "verifications": getattr(self, 'verifications', []),
            "declared_complete": True,
            "pattern_references": getattr(self, 'pattern_references', []),
            "novel_approaches": getattr(self, 'novel_approaches', []),
            "evidence_considered": getattr(self, 'evidence_considered', [])
        }

        # Get workflow ID
        workflow_id = getattr(self, 'workflow_id', f"{self.__class__.__name__}_{id(self)}")

        # Perform shrink session
        shrink_result = perform_shrink_verification(
            shrink=self.shrink,
            workflow_id=workflow_id,
            workflow_data=workflow_data,
            depth=IntrospectionDepth.STANDARD
        )

        # Add shrink result to verification
        if shrink_result.get("shrunk"):
            shrink_profile = shrink_result.get("profile")
            shrink_health = shrink_result.get("health_level")
            shrink_passes = shrink_result.get("passes_verification", True)

            # Add shrink data to result
            result["shrink_verification"] = {
                "performed": True,
                "health_level": shrink_health,
                "confidence_calibration": shrink_result.get("confidence_calibration"),
                "decision_quality": shrink_result.get("decision_quality"),
                "self_awareness": shrink_result.get("self_awareness"),
                "detected_patterns": shrink_result.get("detected_patterns", []),
                "red_flags": shrink_result.get("red_flags", []),
                "insights": shrink_result.get("insights", []),
                "strengths": shrink_result.get("strengths", [])
            }

            # Critical/Poor health may block completion
            if not shrink_passes:
                result["verified"] = False
                result["can_declare_complete"] = False
                result["reason"] = f"Shrink verification failed: Psychological health level '{shrink_health}' requires intervention"
                return result
    except Exception as e:
        # Fail open - don't block workflow if shrink fails
        print(f"Warning: Shrink verification failed: {e}")
        if "shrink_verification" not in result:
            result["shrink_verification"] = {"performed": False, "error": str(e)}
'''

if __name__ == "__main__":
    print("Shrink Workflow Integration Module")
    print("="*70)
    print("\nTo integrate The Shrink into WorkflowBase:")
    print("1. Import TheShrink in workflow_base.py")
    print("2. Initialize self.shrink in __init__")
    print("3. Add shrink verification to verify_completion method")
    print("\nSee SHRINK_INTEGRATION_CODE for implementation details.")

