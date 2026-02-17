#!/usr/bin/env python3
"""
RR Session: Pause Detection and Send Detection
Using Roast and Repair system to identify and fix issues

Tags: #RR #PAUSE_DETECTION #SEND_DETECTION #TRANSCRIPTION @JARVIS @LUMINA
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
    """Run RR session for pause/send detection"""
    rr = KennyRoastAndRepair()

    # REST: Observe current state
    session = rr.rest("Analyzing pause detection and send detection workflow")

    # ROAST: Identify issues
    issues = [
        RoastIssue(
            category=RoastCategory.FUNCTIONAL,
            description="Pause detection may not trigger reliably - dynamic timeout (2.5-5.0s) may be too short or too long",
            severity="high",
            evidence=[
                "User reported: '10 seconds of silence and no auto-send'",
                "Dynamic pause timeout: 2.5-5.0s (grading on a curve)",
                "WaitTimeoutError handler triggers transcribe_current_session()",
                "May need better detection of actual speech end vs. brief pause"
            ]
        ),
        RoastIssue(
            category=RoastCategory.FUNCTIONAL,
            description="Send detection may not verify transcription was actually sent to Cursor",
            severity="high",
            evidence=[
                "transcribe_current_session() calls send_to_cursor()",
                "No verification that message actually reached Cursor IDE",
                "Connection errors may fail silently",
                "Retry manager exists but may not be logging failures clearly"
            ]
        ),
        RoastIssue(
            category=RoastCategory.QUALITY,
            description="Pause detection logic may reset too aggressively - consecutive_audio_count resets on every pause",
            severity="medium",
            evidence=[
                "consecutive_audio_count resets to 0 on pause",
                "May cause timeout to jump back to 2.5s too quickly",
                "Should decay gradually, not reset immediately"
            ]
        ),
        RoastIssue(
            category=RoastCategory.FUNCTIONAL,
            description="No confirmation that transcription was successfully sent - user has to manually verify",
            severity="medium",
            evidence=[
                "send_to_cursor() returns boolean but no visual/logging confirmation",
                "User reported: 'Connection error - no retry'",
                "Need better feedback when send succeeds or fails"
            ]
        ),
    ]

    for issue in issues:
        rr.roast(issue.category, issue.description, issue.severity, issue.evidence)

    # REPAIR: Fix issues systematically
    for i, issue in enumerate(issues):
        if i == 0:
            repair_action = "Enhance pause detection: Add speech end detection (energy-based) + improve timeout decay"
        elif i == 1:
            repair_action = "Add send verification: Verify transcription actually reached Cursor with confirmation"
        elif i == 2:
            repair_action = "Improve timeout decay: Gradual decay instead of immediate reset (exponential decay)"
        elif i == 3:
            repair_action = "Add send confirmation logging: Clear success/failure messages with retry status"
        else:
            repair_action = f"Fix: {issue.description}"

        rr.repair(issue, repair_action)

    # Save session
    rr.save_session()

    print("\n✅ RR Session Complete - Pause/Send Detection Issues Identified")
    print(f"   Issues: {len(issues)}")
    print(f"   Repairs Applied: {len(issues)}")

if __name__ == "__main__":


    main()