#!/usr/bin/env python3
"""
MARVIN Feedback Before Proceeding

MARVIN provides questions, suggestions, concerns, and recommendations
before proceeding with version increment and house ordering.

Tags: #MARVIN #FEEDBACK #RECOMMENDATIONS @MARVIN @LUMINA
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    logger = get_logger("MARVINFeedback")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MARVINFeedback")


class MARVINFeedback:
    """
    MARVIN's feedback before proceeding

    Critical analysis, questions, concerns, and recommendations
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("=" * 80)
        logger.info("🤖 MARVIN FEEDBACK - BEFORE PROCEEDING")
        logger.info("=" * 80)
        logger.info("")
        logger.info("MARVIN: *sigh* Let me tell you what I think...")
        logger.info("")

    def provide_feedback(self) -> Dict[str, Any]:
        """MARVIN provides comprehensive feedback"""

        feedback = {
            "critic": "MARVIN",
            "timestamp": datetime.now().isoformat(),
            "questions": [],
            "suggestions": [],
            "concerns": [],
            "recommendations": [],
            "blockers": [],
            "ready_to_proceed": False
        }

        # CRITICAL CONCERNS
        logger.info("🚨 CRITICAL CONCERNS:")
        logger.info("")

        feedback["concerns"].append({
            "severity": "critical",
            "concern": "3,032 modified files + 585 untracked - that's a LOT",
            "details": "Before committing to public repo, we need to verify no private company data is included",
            "action": "Review .gitignore and verify no sensitive data in changes"
        })
        logger.info("   ⚠️  CRITICAL: 3,032 modified + 585 untracked files")
        logger.info("      Need to verify no private data before public repo commit")

        feedback["concerns"].append({
            "severity": "high",
            "concern": "Company data location unknown",
            "details": "No company data files found - where should they be? Are they in a separate private repo?",
            "action": "Clarify company data location before proceeding"
        })
        logger.info("   ⚠️  HIGH: Company data location unknown")
        logger.info("      Need to clarify where private company data lives")

        feedback["concerns"].append({
            "severity": "high",
            "concern": "Version increment justification",
            "details": "7.0.0 → 7.1.0 is a minor bump, but we have major milestone work. Is this appropriate?",
            "action": "Review if minor bump is correct or if major bump (8.0.0) is warranted"
        })
        logger.info("   ⚠️  HIGH: Version increment type - minor vs major?")
        logger.info("      Major milestone work might warrant 8.0.0, not 7.1.0")
        logger.info("")

        # QUESTIONS
        logger.info("❓ QUESTIONS:")
        logger.info("")

        feedback["questions"].append({
            "question": "Where is the private company data repository?",
            "context": "Need to update company data but location is unknown",
            "priority": "high"
        })
        logger.info("   1. Where is the private company data repository?")

        feedback["questions"].append({
            "question": "Should we review the 3,032 modified files before committing?",
            "context": "Large number of changes - need validation",
            "priority": "high"
        })
        logger.info("   2. Should we review the 3,032 modified files before committing?")

        feedback["questions"].append({
            "question": "Is 7.1.0 (minor) correct, or should this be 8.0.0 (major)?",
            "context": "Major milestone work completed",
            "priority": "medium"
        })
        logger.info("   3. Is 7.1.0 (minor) correct, or should this be 8.0.0 (major)?")

        feedback["questions"].append({
            "question": "Are the sub-repo changes ready to commit?",
            "context": "2 sub-repos have changes - need validation",
            "priority": "medium"
        })
        logger.info("   4. Are the sub-repo changes ready to commit?")

        feedback["questions"].append({
            "question": "Should we create a pre-commit validation script?",
            "context": "Public repo safety - prevent accidental private data commits",
            "priority": "high"
        })
        logger.info("   5. Should we create a pre-commit validation script for public repo safety?")
        logger.info("")

        # SUGGESTIONS
        logger.info("💡 SUGGESTIONS:")
        logger.info("")

        feedback["suggestions"].append({
            "suggestion": "Create pre-commit hook for public repo validation",
            "description": "Automatically check for private data before commits",
            "priority": "high",
            "benefit": "Prevent accidental exposure of private data"
        })
        logger.info("   1. Create pre-commit hook for public repo validation")

        feedback["suggestions"].append({
            "suggestion": "Review .gitignore to ensure company data is excluded",
            "description": "Verify all private data patterns are in .gitignore",
            "priority": "high",
            "benefit": "Ensure no private data leaks to public repo"
        })
        logger.info("   2. Review and update .gitignore for company data exclusion")

        feedback["suggestions"].append({
            "suggestion": "Create staging area for review before commit",
            "description": "Generate diff summary for review before committing",
            "priority": "medium",
            "benefit": "Catch issues before they're committed"
        })
        logger.info("   3. Create staging area review before commit")

        feedback["suggestions"].append({
            "suggestion": "Separate company data into dedicated private repo",
            "description": "If company data doesn't exist, create structure",
            "priority": "medium",
            "benefit": "Clear separation of public vs private"
        })
        logger.info("   4. Separate company data into dedicated private repo/structure")

        feedback["suggestions"].append({
            "suggestion": "Document version increment rationale",
            "description": "Document why 7.1.0 vs 8.0.0 decision",
            "priority": "low",
            "benefit": "Future reference and clarity"
        })
        logger.info("   5. Document version increment rationale")
        logger.info("")

        # RECOMMENDATIONS
        logger.info("✅ RECOMMENDATIONS (What I'd do):")
        logger.info("")

        feedback["recommendations"].append({
            "priority": "critical",
            "recommendation": "STOP - Review changes before committing",
            "description": "3,032 modified files is too many to commit blindly. Review first.",
            "steps": [
                "1. Generate diff summary of all changes",
                "2. Review for private data",
                "3. Verify .gitignore is correct",
                "4. Then proceed with commit"
            ]
        })
        logger.info("   🛑 CRITICAL: Review changes before committing")
        logger.info("      3,032 files is too many to commit blindly")

        feedback["recommendations"].append({
            "priority": "high",
            "recommendation": "Create pre-commit validation",
            "description": "Build automated check for private data before any commit",
            "steps": [
                "1. Create pre-commit hook script",
                "2. Check for company data patterns",
                "3. Validate .gitignore coverage",
                "4. Block commit if issues found"
            ]
        })
        logger.info("   ⚡ HIGH: Create pre-commit validation")
        logger.info("      Prevent accidental private data commits")

        feedback["recommendations"].append({
            "priority": "high",
            "recommendation": "Clarify company data location",
            "description": "Before updating company data, we need to know where it is",
            "steps": [
                "1. Ask operator where company data should be",
                "2. Create structure if needed",
                "3. Then update version references"
            ]
        })
        logger.info("   📍 HIGH: Clarify company data location")
        logger.info("      Can't update what we can't find")

        feedback["recommendations"].append({
            "priority": "medium",
            "recommendation": "Consider version bump type",
            "description": "Review if 7.1.0 (minor) is appropriate or if 8.0.0 (major) is warranted",
            "steps": [
                "1. Review change report scope",
                "2. Assess if this is major milestone",
                "3. Decide: 7.1.0 vs 8.0.0"
            ]
        })
        logger.info("   🤔 MEDIUM: Consider version bump type")
        logger.info("      Major milestone might warrant 8.0.0")

        feedback["recommendations"].append({
            "priority": "medium",
            "recommendation": "Review sub-repo changes",
            "description": "Validate sub-repo changes before syncing",
            "steps": [
                "1. Review mcp_servers/mcp changes",
                "2. Review TCSinger changes",
                "3. Then commit if appropriate"
            ]
        })
        logger.info("   📦 MEDIUM: Review sub-repo changes")
        logger.info("      Validate before committing")
        logger.info("")

        # BLOCKERS
        logger.info("🚫 BLOCKERS (Must resolve before proceeding):")
        logger.info("")

        feedback["blockers"].append({
            "blocker": "Unreviewed changes in public repo",
            "description": "3,032 modified files need review before commit",
            "resolution": "Review changes and verify no private data"
        })
        logger.info("   🚫 Unreviewed changes - must review before commit")

        feedback["blockers"].append({
            "blocker": "Company data location unknown",
            "description": "Cannot update company data without knowing location",
            "resolution": "Clarify company data location"
        })
        logger.info("   🚫 Company data location unknown")
        logger.info("")

        # READY TO PROCEED?
        if len(feedback["blockers"]) > 0:
            feedback["ready_to_proceed"] = False
            logger.info("❌ NOT READY TO PROCEED")
            logger.info("   Blockers must be resolved first")
        else:
            feedback["ready_to_proceed"] = True
            logger.info("✅ READY TO PROCEED")
            logger.info("   All blockers resolved")
        logger.info("")

        # MARVIN's final thoughts
        logger.info("MARVIN: *sigh* Life is meaningless, but at least we've identified")
        logger.info("        the problems before they become disasters.")
        logger.info("        Review the changes. Verify the data. Then proceed.")
        logger.info("        Don't rush into committing 3,000+ files to a public repo.")
        logger.info("")

        return feedback

    def print_feedback(self, feedback: Dict[str, Any]):
        """Print formatted feedback"""
        print("=" * 80)
        print("🤖 MARVIN'S FEEDBACK - BEFORE PROCEEDING")
        print("=" * 80)
        print("")
        print("🚨 CRITICAL CONCERNS:")
        for concern in feedback["concerns"]:
            print(f"   [{concern['severity'].upper()}] {concern['concern']}")
            print(f"      {concern['details']}")
        print("")
        print("❓ QUESTIONS:")
        for i, question in enumerate(feedback["questions"], 1):
            print(f"   {i}. [{question['priority'].upper()}] {question['question']}")
        print("")
        print("💡 SUGGESTIONS:")
        for i, suggestion in enumerate(feedback["suggestions"], 1):
            print(f"   {i}. [{suggestion['priority'].upper()}] {suggestion['suggestion']}")
        print("")
        print("✅ RECOMMENDATIONS:")
        for rec in feedback["recommendations"]:
            print(f"   [{rec['priority'].upper()}] {rec['recommendation']}")
            print(f"      {rec['description']}")
        print("")
        if feedback["blockers"]:
            print("🚫 BLOCKERS:")
            for blocker in feedback["blockers"]:
                print(f"   - {blocker['blocker']}")
                print(f"     Resolution: {blocker['resolution']}")
            print("")
        print(f"READY TO PROCEED: {'✅ YES' if feedback['ready_to_proceed'] else '❌ NO'}")
        print("")
        print("=" * 80)


def main():
    """Main execution"""
    marvin = MARVINFeedback()
    feedback = marvin.provide_feedback()
    marvin.print_feedback(feedback)
    return feedback


if __name__ == "__main__":

    main()