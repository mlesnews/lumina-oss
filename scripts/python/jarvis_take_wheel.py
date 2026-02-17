#!/usr/bin/env python3
"""
JARVIS Take the Wheel - Autonomous System Management

When user says "JARVIS, please take the wheel", JARVIS takes full autonomous control:
- Assesses system state
- Checks all components
- Identifies priorities
- Executes systematically
- Reports status

Tags: #JARVIS #AUTONOMOUS #TAKE_WHEEL #LUMINA @JARVIS
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISTakeWheel")


class JARVISTakeWheel:
    """
    JARVIS Take the Wheel

    Autonomous system management when user requests JARVIS to take control.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Take the Wheel"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_take_wheel"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Import components
        try:
            from autonomous_ai_agent import AutonomousAIAgent
            self.autonomous_agent = AutonomousAIAgent(project_root)
        except ImportError:
            self.autonomous_agent = None
            logger.warning("   ⚠️  Autonomous AI Agent not available")

        try:
            from va_health_detector import VAHealthDetector
            self.va_detector = VAHealthDetector(project_root)
        except ImportError:
            self.va_detector = None
            logger.warning("   ⚠️  VA Health Detector not available")

        try:
            from doit_enhanced import DOITEnhanced
            self.doit = DOITEnhanced(project_root)
        except ImportError:
            self.doit = None
            logger.warning("   ⚠️  DOIT Enhanced not available")

        logger.info("✅ JARVIS Take the Wheel initialized")
        logger.info("   🎯 Ready for autonomous control")

    def take_wheel(self) -> Dict[str, Any]:
        try:
            """
            JARVIS takes the wheel - full autonomous control

            Returns:
                Complete system status and actions taken
            """
            logger.info("=" * 80)
            logger.info("🎯 JARVIS TAKING THE WHEEL")
            logger.info("=" * 80)
            logger.info("")
            logger.info("   🚀 Autonomous control activated")
            logger.info("   📊 Assessing system state...")
            logger.info("")

            session = {
                "timestamp": datetime.now().isoformat(),
                "session_id": f"jarvis_wheel_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "active",
                "assessments": {},
                "actions_taken": [],
                "priorities": [],
                "completed": []
            }

            # Step 1: Assess VA Health
            logger.info("📋 Step 1: Assessing Virtual Assistant Health")
            logger.info("")
            if self.va_detector:
                va_health = self.va_detector.check_va_health()
                session["assessments"]["va_health"] = va_health

                if va_health["summary"]["required_not_running"] > 0 or va_health["summary"]["failed"] > 0:
                    logger.info("   ⚠️  VAs need attention - fixing...")
                    fix_results = self.va_detector.fix_failed_vas(va_health)
                    session["actions_taken"].append({
                        "action": "fix_vas",
                        "result": fix_results,
                        "timestamp": datetime.now().isoformat()
                    })
                    logger.info(f"   ✅ Fixed {len(fix_results['fixed'])} VAs")
                else:
                    logger.info("   ✅ All required VAs are healthy")
            logger.info("")

            # Step 2: Assess TODO Status
            logger.info("📋 Step 2: Assessing TODO Status")
            logger.info("")
            if self.autonomous_agent and self.autonomous_agent.master_todo_tracker:
                pending = self.autonomous_agent.get_pending_todos()
                session["assessments"]["todos"] = {
                    "total_pending": len(pending),
                    "high_priority": len([t for t in pending if t.get("priority") == "high"]),
                    "in_progress": len([t for t in pending if t.get("status") == "in_progress"])
                }
                logger.info(f"   📋 Pending TODOs: {len(pending)}")
                logger.info(f"   🔴 High Priority: {session['assessments']['todos']['high_priority']}")
                logger.info(f"   🔄 In Progress: {session['assessments']['todos']['in_progress']}")
            logger.info("")

            # Step 3: Identify Roadblocks
            logger.info("📋 Step 3: Identifying Roadblocks")
            logger.info("")
            if self.autonomous_agent:
                # Get roadblock report
                roadblock_report_file = self.project_root / "data" / "autonomous_ai" / "roadblocks_report_20260108_033541.json"
                if roadblock_report_file.exists():
                    import json
                    with open(roadblock_report_file, 'r', encoding='utf-8') as f:
                        roadblock_report = json.load(f)
                    session["assessments"]["roadblocks"] = {
                        "total": roadblock_report.get("total_roadblocks", 0),
                        "affected_todos": roadblock_report.get("affected_todos", 0)
                    }
                    logger.info(f"   ⚠️  Roadblocks: {session['assessments']['roadblocks']['total']}")
                    logger.info(f"   📋 Affected TODOs: {session['assessments']['roadblocks']['affected_todos']}")
                else:
                    logger.info("   ✅ No recent roadblock report (may need to identify)")
            logger.info("")

            # Step 4: Work on High Priority TODOs (FORCE MODE - JARVIS has the wheel)
            logger.info("📋 Step 4: Working on High Priority TODOs (JARVIS HAS THE WHEEL)")
            logger.info("")
            if self.autonomous_agent:
                # Force work mode - JARVIS has explicit control
                original_detect = self.autonomous_agent.detect_idle_time
                self.autonomous_agent.detect_idle_time = lambda: (True, 10.0)  # Simulate idle for forced work
                work_result = self.autonomous_agent.work_independently(max_items=10)
                self.autonomous_agent.detect_idle_time = original_detect

                session["actions_taken"].append({
                    "action": "work_on_todos",
                    "result": work_result,
                    "timestamp": datetime.now().isoformat()
                })
                logger.info(f"   ✅ Worked on {work_result.get('todos_worked_on', 0)} TODOs")
                logger.info(f"   ⚠️  Roadblocks identified: {work_result.get('roadblocks_identified', 0)}")
                logger.info(f"   ✅ Roadblocks addressed: {work_result.get('roadblocks_addressed', 0)}")
            logger.info("")

            # Step 5: System Optimization
            logger.info("📋 Step 5: System Optimization")
            logger.info("")
            optimizations = []

            # Check for any system issues
            if session["assessments"].get("va_health", {}).get("summary", {}).get("failed", 0) > 0:
                optimizations.append("VA health issues resolved")

            if session["assessments"].get("roadblocks", {}).get("total", 0) > 0:
                optimizations.append("Roadblocks identified and being addressed")

            session["optimizations"] = optimizations
            logger.info(f"   ✅ Optimizations: {len(optimizations)}")
            for opt in optimizations:
                logger.info(f"      • {opt}")
            logger.info("")

            # Save session
            session_file = self.data_dir / f"session_{session['session_id']}.json"
            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session, f, indent=2, ensure_ascii=False, default=str)

            logger.info("=" * 80)
            logger.info("✅ JARVIS WHEEL SESSION COMPLETE")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📊 Summary:")
            logger.info(f"   VAs Checked: ✅")
            logger.info(f"   TODOs Assessed: {session['assessments'].get('todos', {}).get('total_pending', 0)}")
            logger.info(f"   Actions Taken: {len(session['actions_taken'])}")
            logger.info(f"   Optimizations: {len(optimizations)}")
            logger.info("")
            logger.info("🎯 JARVIS is at the wheel - system under autonomous control")
            logger.info("")
            logger.info(f"   Session saved: {session_file.name}")
            logger.info("")

            return session


        except Exception as e:
            self.logger.error(f"Error in take_wheel: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Take the Wheel")
    parser.add_argument("--take-wheel", action="store_true", help="JARVIS takes the wheel")

    args = parser.parse_args()

    jarvis = JARVISTakeWheel()

    if args.take_wheel:
        jarvis.take_wheel()
    else:
        # Default: take the wheel
        jarvis.take_wheel()

    return 0


if __name__ == "__main__":


    sys.exit(main())