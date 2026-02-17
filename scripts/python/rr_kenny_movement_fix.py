#!/usr/bin/env python3
"""
RR Session: Kenny Movement Fix
Using Roast and Repair system to fix Kenny's movement stopping issue

Tags: #RR #KENNY #MOVEMENT #BEHAVIORAL @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from kenny_roast_and_repair import KennyRoastAndRepair, RoastCategory, RoastIssue

def main():
    """Run RR session for Kenny movement fix"""
    rr = KennyRoastAndRepair()

    # REST: Observe current state
    session = rr.rest("Analyzing Kenny's movement behavior - why does he stop?")

    # ROAST: Identify movement issues
    issues = [
        RoastIssue(
            category=RoastCategory.BEHAVIORAL,
            description="Kenny stops moving after initial movement - comes to rest in corner",
            severity="high",
            evidence=[
                "User reports: 'came to rest in bottom right corner'",
                "User reports: 'sitting there ever since'",
                "Previous RR session: Movement issue NOT repaired",
                "State may be stuck in IDLE instead of WALKING",
                "animate() may not be calling movement functions consistently"
            ]
        ),
        RoastIssue(
            category=RoastCategory.BEHAVIORAL,
            description="Movement may stop if target position equals current position",
            severity="medium",
            evidence=[
                "smooth_interpolate_position() may not update if target == current",
                "walk_border_smooth() may not update target if already at border end",
                "Need to ensure continuous movement even when 'at target'"
            ]
        ),
        RoastIssue(
            category=RoastCategory.QUALITY,
            description="No movement state verification - can't tell if Kenny is actually moving",
            severity="medium",
            evidence=[
                "No logging of movement state changes",
                "No metrics tracking movement activity",
                "Can't programmatically verify if movement is active"
            ]
        ),
    ]

    for issue in issues:
        rr.roast(issue.category, issue.description, issue.severity, issue.evidence)

    # REPAIR: Fix movement issues
    for i, issue in enumerate(issues):
        if i == 0:
            repair_action = "Ensure state is always WALKING when not frozen - prevent IDLE state from stopping movement"
        elif i == 1:
            repair_action = "Add movement continuation logic - always pick new target even when 'at target'"
        elif i == 2:
            repair_action = "Add movement state logging and metrics - verify movement is actually happening"
        else:
            repair_action = f"Fix: {issue.description}"

        rr.repair(issue, repair_action)

    # Save session
    rr.save_session()

    print("\n✅ RR Session Complete - Kenny Movement Issues Identified")
    print(f"   Issues: {len(issues)}")
    print(f"   Repairs: {len(issues)}")

if __name__ == "__main__":


    main()