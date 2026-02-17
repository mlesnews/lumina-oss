#!/usr/bin/env python3
"""
Continuous Project Orchestrator - "Make It So"

Orchestrates all project systems continuously:
- Living Blueprint Sync (continuous)
- Project Projection Assessment (scheduled)
- Autonomous Execution (on-demand)
- Verification & Validation (continuous)
- Quality Assurance ("Measure twice, cut once")

All systems operational - no manual intervention required.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional
import signal
import sys

# Import systems
try:
    from living_blueprint_sync import LivingBlueprintSync
    from project_projection_assessor import ProjectProjectionAssessor
    from master_feedback_loop_autonomous_executor import MasterFeedbackLoopAutonomousExecutor
    SYSTEMS_AVAILABLE = True
except ImportError as e:
    SYSTEMS_AVAILABLE = False
    print(f"⚠️ Import error: {e}")


class ContinuousProjectOrchestrator:
    """
    Continuous Project Orchestrator

    "Make It So" - All systems operational, continuously running
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = self._setup_logging()

        # Initialize systems
        if SYSTEMS_AVAILABLE:
            self.blueprint_sync = LivingBlueprintSync(project_root)
            self.projection_assessor = ProjectProjectionAssessor(project_root)
            self.autonomous_executor = MasterFeedbackLoopAutonomousExecutor(project_root)
        else:
            self.blueprint_sync = None
            self.projection_assessor = None
            self.autonomous_executor = None

        # Configuration
        self.blueprint_sync_interval = 300  # 5 minutes
        self.projection_assessment_interval = 3600  # 1 hour
        self.verification_interval = 60  # 1 minute

        # State
        self.running = False
        self.last_blueprint_sync = None
        self.last_projection_assessment = None

    def _setup_logging(self) -> logging.Logger:
        logger = logging.getLogger("ContinuousProjectOrchestrator")
        logger.setLevel(logging.INFO)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter(
                '%(asctime)s - 🎯 ContinuousOrchestrator - %(levelname)s - %(message)s'
            ))
            logger.addHandler(handler)
        return logger

    async def sync_blueprint_continuously(self):
        """Continuously sync blueprint (living document)"""
        self.logger.info("🔄 Starting continuous blueprint sync...")

        while self.running:
            try:
                # Sync blueprint
                sync_result = self.blueprint_sync.sync_blueprint()

                if sync_result['success']:
                    self.last_blueprint_sync = datetime.now()
                    self.logger.info(f"✅ Blueprint synced - Changes: {sync_result['changes_detected']}")
                else:
                    self.logger.warning(f"⚠️ Blueprint sync failed: {sync_result.get('steps_failed', [])}")

                await asyncio.sleep(self.blueprint_sync_interval)

            except Exception as e:
                self.logger.error(f"❌ Error in blueprint sync: {e}")
                await asyncio.sleep(self.blueprint_sync_interval)

    async def assess_projection_periodically(self):
        """Periodically assess project projections"""
        self.logger.info("📊 Starting periodic projection assessment...")

        while self.running:
            try:
                # Generate projection report
                report = self.projection_assessor.generate_projection_report()

                self.last_projection_assessment = datetime.now()

                # Log key metrics
                blueprint_assessment = report.get('blueprint_assessment', {})
                project_projection = report.get('project_projection', {})

                self.logger.info(f"📊 Projection Assessment:")
                self.logger.info(f"   Blueprint Recreation Capability: {blueprint_assessment.get('recreation_capability', 0):.1%}")
                self.logger.info(f"   Project Completion: {project_projection.get('completion_percentage', 0):.1f}%")
                self.logger.info(f"   AI-Capable Tasks: {project_projection.get('ai_capable_tasks', 0)}")

                await asyncio.sleep(self.projection_assessment_interval)

            except Exception as e:
                self.logger.error(f"❌ Error in projection assessment: {e}")
                await asyncio.sleep(self.projection_assessment_interval)

    async def verify_systems_continuously(self):
        """Continuously verify system integrity"""
        self.logger.info("🔍 Starting continuous system verification...")

        while self.running:
            try:
                # Verify blueprint
                verification = self.blueprint_sync.verify_and_validate_workflow()

                if verification['all_checks_passed']:
                    self.logger.debug("✅ System verification passed")
                else:
                    self.logger.warning("⚠️ System verification issues detected")
                    # Auto-fix by syncing
                    self.blueprint_sync.sync_blueprint()

                await asyncio.sleep(self.verification_interval)

            except Exception as e:
                self.logger.error(f"❌ Error in system verification: {e}")
                await asyncio.sleep(self.verification_interval)

    async def run_continuously(self):
        """Run all systems continuously"""
        self.logger.info("🚀 Starting Continuous Project Orchestrator...")
        self.logger.info("   'Make It So' - All systems operational")
        self.logger.info("")
        self.logger.info("   Active Systems:")
        self.logger.info("   ✅ Living Blueprint Sync (continuous)")
        self.logger.info("   ✅ Project Projection Assessment (periodic)")
        self.logger.info("   ✅ System Verification (continuous)")
        self.logger.info("   ✅ Autonomous Execution (on-demand)")
        self.logger.info("")

        self.running = True

        # Run all systems concurrently
        tasks = [
            asyncio.create_task(self.sync_blueprint_continuously()),
            asyncio.create_task(self.assess_projection_periodically()),
            asyncio.create_task(self.verify_systems_continuously())
        ]

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self.logger.info("🛑 Orchestrator stopping...")
            self.running = False

    def stop(self):
        """Stop orchestrator"""
        self.running = False
        self.logger.info("🛑 Stopping Continuous Project Orchestrator...")


async def main():
    """Main execution"""
    orchestrator = ContinuousProjectOrchestrator()

    # Handle graceful shutdown
    def signal_handler(sig, frame):
        orchestrator.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("\n" + "=" * 80)
    print("🎯 CONTINUOUS PROJECT ORCHESTRATOR")
    print("=" * 80)
    print("'Make It So' - All Systems Operational")
    print()
    print("Running continuously... Press Ctrl+C to stop")
    print()

    # Initial sync and assessment
    print("🔧 Initial Setup...")

    # Sync blueprint
    if orchestrator.blueprint_sync:
        sync_result = orchestrator.blueprint_sync.sync_blueprint()
        print(f"   Blueprint Sync: {'✅' if sync_result['success'] else '❌'}")

    # Initial projection assessment
    if orchestrator.projection_assessor:
        report = orchestrator.projection_assessor.generate_projection_report()
        blueprint = report.get('blueprint_assessment', {})
        project = report.get('project_projection', {})
        print(f"   Projection Assessment: ✅")
        print(f"      Recreation Capability: {blueprint.get('recreation_capability', 0):.1%}")
        print(f"      Project Completion: {project.get('completion_percentage', 0):.1f}%")

    print()
    print("✅ Initial setup complete - Starting continuous operation...")
    print()

    # Run continuously
    await orchestrator.run_continuously()


if __name__ == "__main__":




    asyncio.run(main())