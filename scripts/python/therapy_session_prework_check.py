#!/usr/bin/env python3
"""
Therapy Session Pre-Work Check

Checks if we're ready for a therapy session:
- Git status (uncommitted changes)
- Broken systems
- Pending work
- System health

Tags: #THERAPY #PREWORK #PREPARATION #CHECK @JARVIS @TEAM
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("TherapyPreworkCheck")


class TherapyPreworkCheck:
    """
    Check if we're ready for therapy session

    Pre-work includes:
    - Git status check
    - System health
    - Pending work
    - Broken systems
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize pre-work check"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ Therapy Pre-Work Check initialized")

    def check_git_status(self) -> Dict[str, Any]:
        """Check git status for uncommitted changes"""
        logger.info("="*80)
        logger.info("🔍 Checking Git Status")
        logger.info("="*80)

        result = {
            "has_changes": False,
            "modified_files": [],
            "untracked_files": [],
            "ready": True,
            "recommendations": []
        }

        try:
            # Check git status
            git_status = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=10
            )

            if git_status.returncode == 0:
                lines = git_status.stdout.strip().split('\n')
                if lines and lines[0]:  # Has changes
                    result["has_changes"] = True

                    for line in lines:
                        if line.startswith('??'):
                            result["untracked_files"].append(line[3:].strip())
                        else:
                            result["modified_files"].append(line.strip())

                    logger.info(f"   Found {len(result['modified_files'])} modified files")
                    logger.info(f"   Found {len(result['untracked_files'])} untracked files")

                    if len(result['modified_files']) > 20:
                        result["recommendations"].append("Many modified files - consider committing before session")
                        result["ready"] = False
                    elif len(result['modified_files']) > 0:
                        result["recommendations"].append("Some modified files - may want to commit before session")
                else:
                    logger.info("   ✅ No uncommitted changes")
            else:
                logger.warning("   ⚠️  Could not check git status")

        except Exception as e:
            logger.warning(f"   ⚠️  Error checking git status: {e}")
            result["recommendations"].append("Could not check git status - proceed with caution")

        return result

    def check_system_health(self) -> Dict[str, Any]:
        """Check system health"""
        logger.info("="*80)
        logger.info("🔍 Checking System Health")
        logger.info("="*80)

        result = {
            "health": "good",
            "issues": [],
            "ready": True,
            "recommendations": []
        }

        # Check for broken systems
        try:
            from diagnose_manus_interference import ManusInterferenceDiagnostic
            diagnostic = ManusInterferenceDiagnostic(project_root=self.project_root)
            diagnostic_result = diagnostic.run_full_diagnostic()

            if diagnostic_result.get("recommendations"):
                result["issues"].extend(diagnostic_result["recommendations"])
                result["health"] = "needs_attention"
                result["recommendations"].append("System issues detected - may want to address before session")

        except Exception as e:
            logger.debug(f"   Could not run diagnostic: {e}")

        # Check for critical errors
        error_logs = list(self.project_root.glob("data/error_logs/*.json"))
        if error_logs:
            recent_errors = [f for f in error_logs if f.stat().st_mtime > (Path(__file__).stat().st_mtime - 3600)]
            if recent_errors:
                result["issues"].append(f"{len(recent_errors)} recent error logs found")
                result["health"] = "needs_attention"

        if result["health"] == "good":
            logger.info("   ✅ System health: Good")
        else:
            logger.warning(f"   ⚠️  System health: {result['health']}")

        return result

    def check_pending_work(self) -> Dict[str, Any]:
        """Check for pending work"""
        logger.info("="*80)
        logger.info("🔍 Checking Pending Work")
        logger.info("="*80)

        result = {
            "has_pending": False,
            "pending_items": [],
            "ready": True,
            "recommendations": []
        }

        # Check for TODO files
        todo_files = list(self.project_root.glob("**/TODO*.md"))
        if todo_files:
            result["has_pending"] = True
            result["pending_items"].extend([f.name for f in todo_files[:5]])
            logger.info(f"   Found {len(todo_files)} TODO files")

        # Check for incomplete work
        incomplete_markers = ["FIXME", "XXX", "HACK", "TEMP"]
        # This would require code scanning - simplified for now

        if not result["has_pending"]:
            logger.info("   ✅ No obvious pending work")
        else:
            result["recommendations"].append("Some pending work found - may want to note in session")

        return result

    def run_prework_check(self) -> Dict[str, Any]:
        """Run complete pre-work check"""
        logger.info("="*80)
        logger.info("🔍 THERAPY SESSION PRE-WORK CHECK")
        logger.info("="*80)
        logger.info("")

        result = {
            "ready": True,
            "git_status": self.check_git_status(),
            "system_health": self.check_system_health(),
            "pending_work": self.check_pending_work(),
            "overall_recommendations": []
        }

        # Overall assessment
        if not result["git_status"]["ready"]:
            result["ready"] = False
            result["overall_recommendations"].append("Git changes should be committed before session")

        if result["system_health"]["health"] != "good":
            result["overall_recommendations"].append("System health issues should be addressed")

        # Combine recommendations
        all_recommendations = []
        all_recommendations.extend(result["git_status"]["recommendations"])
        all_recommendations.extend(result["system_health"]["recommendations"])
        all_recommendations.extend(result["pending_work"]["recommendations"])
        all_recommendations.extend(result["overall_recommendations"])

        result["all_recommendations"] = list(set(all_recommendations))

        logger.info("")
        logger.info("="*80)
        logger.info("📊 PRE-WORK CHECK SUMMARY")
        logger.info("="*80)
        logger.info(f"   Ready for session: {'✅ YES' if result['ready'] else '⚠️  NEEDS ATTENTION'}")
        logger.info(f"   Git changes: {len(result['git_status']['modified_files'])} modified, {len(result['git_status']['untracked_files'])} untracked")
        logger.info(f"   System health: {result['system_health']['health']}")
        logger.info(f"   Pending work: {'Yes' if result['pending_work']['has_pending'] else 'No'}")
        logger.info(f"   Recommendations: {len(result['all_recommendations'])}")
        logger.info("")

        if result["all_recommendations"]:
            logger.warning("⚠️  RECOMMENDATIONS:")
            for rec in result["all_recommendations"]:
                logger.warning(f"   - {rec}")

        logger.info("="*80)

        return result


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🔍 Therapy Session Pre-Work Check")
    print("   Checking if we're ready for our first session")
    print("="*80 + "\n")

    check = TherapyPreworkCheck()
    result = check.run_prework_check()

    print("\n" + "="*80)
    print("📊 PRE-WORK CHECK RESULTS")
    print("="*80)
    print(f"Ready for session: {'✅ YES' if result['ready'] else '⚠️  NEEDS ATTENTION'}")
    print()

    if result['all_recommendations']:
        print("⚠️  RECOMMENDATIONS:")
        for rec in result['all_recommendations']:
            print(f"   - {rec}")
        print()

    if result['ready']:
        print("✅ Ready to proceed with therapy session!")
        print("   Run: python scripts/python/ai_human_collab_therapy_podcast.py --record")
    else:
        print("⚠️  Consider addressing recommendations before session")
        print("   Or proceed anyway - therapy can help work through issues")

    print("="*80 + "\n")
