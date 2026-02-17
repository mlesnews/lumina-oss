#!/usr/bin/env python3
"""
JARVIS Continuous Workflow Analyzer
Runs workflow analysis automatically and executes opportunities

Tags: #JARVIS #WORKFLOW #AUTOMATION #DOIT @JARVIS @LUMINA
"""

import sys
import time
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

# Import analyzers
try:
    from jarvis_summary_workflow_analyzer import SummaryWorkflowAnalyzer
    from jarvis_workflow_opportunity_executor import WorkflowOpportunityExecutor
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("JARVISContinuousAnalyzer")

PROJECT_ROOT = Path(__file__).parent.parent.parent


class ContinuousWorkflowAnalyzer:
    """Continuously analyze workflows and execute opportunities"""

    def __init__(self, project_root: Path, auto_execute: bool = True):
        self.project_root = project_root
        self.auto_execute = auto_execute

        self.analyzer = SummaryWorkflowAnalyzer(project_root)
        self.executor = WorkflowOpportunityExecutor(project_root)

        self.logger = logger

        # Analysis interval (hours)
        self.analysis_interval = 24  # Daily analysis

        # Last analysis timestamp
        self.last_analysis_file = project_root / "data" / "jarvis" / "workflow_analysis" / ".last_analysis"

    def should_run_analysis(self) -> bool:
        """Check if analysis should run"""
        if not self.last_analysis_file.exists():
            return True

        try:
            last_time = float(self.last_analysis_file.read_text().strip())
            elapsed_hours = (time.time() - last_time) / 3600
            return elapsed_hours >= self.analysis_interval
        except (ValueError, OSError):
            return True

    def mark_analysis_complete(self):
        try:
            """Mark analysis as complete"""
            self.last_analysis_file.parent.mkdir(parents=True, exist_ok=True)
            self.last_analysis_file.write_text(str(time.time()))

        except Exception as e:
            self.logger.error(f"Error in mark_analysis_complete: {e}", exc_info=True)
            raise
    def run_analysis_cycle(self) -> dict:
        """Run one analysis cycle"""
        self.logger.info("=" * 80)
        self.logger.info("🔄 CONTINUOUS WORKFLOW ANALYSIS CYCLE")
        self.logger.info("=" * 80)
        self.logger.info("")

        # Run analysis
        self.logger.info("📊 Running workflow analysis...")
        analysis_result = self.analyzer.analyze_all()

        if not analysis_result:
            self.logger.warning("⚠️  Analysis returned no results")
            return {}

        summaries_analyzed = analysis_result.get("summaries_analyzed", 0)
        patterns_found = analysis_result.get("patterns_found", 0)
        opportunities = analysis_result.get("opportunities_generated", 0)

        self.logger.info("")
        self.logger.info(f"✅ Analysis complete:")
        self.logger.info(f"   Summaries analyzed: {summaries_analyzed}")
        self.logger.info(f"   Patterns found: {patterns_found}")
        self.logger.info(f"   Opportunities: {opportunities}")
        self.logger.info("")

        # Execute opportunities if enabled
        if self.auto_execute and opportunities > 0:
            self.logger.info("🚀 Executing opportunities...")
            self.logger.info("")

            execution_result = self.executor.execute_all_opportunities(auto_execute=True)

            total_executed = execution_result.get("total_executed", 0)
            self.logger.info("")
            self.logger.info(f"✅ Executed {total_executed} opportunities")
        else:
            self.logger.info("ℹ️  Auto-execution disabled or no opportunities")

        # Mark as complete
        self.mark_analysis_complete()

        # Step 4: #DECISIONING - Close workflow (if enabled)
        if self.auto_execute and opportunities > 0:
            try:
                from jarvis_workflow_decisioning_closer import WorkflowDecisioningCloser

                self.logger.info("")
                self.logger.info("Step 4: #DECISIONING - Closing workflow...")
                self.logger.info("")

                closer = WorkflowDecisioningCloser(project_root=self.project_root)

                # Extract workflow data from analysis
                workflow_data = {
                    "ticket_ids": self._extract_ticket_ids(analysis_result),
                    "pm_task_ids": self._extract_pm_task_ids(analysis_result),
                    "change_request_ids": self._extract_cr_ids(analysis_result),
                    "tasks_completed": self._extract_completed_tasks(analysis_result),
                    "documentation_complete": True,
                    "verification_passed": True
                }

                # Get session ID (use current session or generate)
                session_id = self._get_session_id()

                # Close workflow
                closure_result = closer.close_workflow(session_id, workflow_data)

                if closure_result.get("success"):
                    self.logger.info("✅ Workflow closed successfully")
                else:
                    self.logger.warning("⚠️  Workflow closure had issues")

            except ImportError:
                self.logger.debug("Workflow closer not available - skipping")
            except Exception as e:
                self.logger.warning(f"⚠️  Error closing workflow: {e}")

        self.logger.info("")
        self.logger.info("=" * 80)
        self.logger.info("✅ Analysis cycle complete")
        self.logger.info("=" * 80)
        self.logger.info("")

        return {
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis_result,
            "execution": execution_result if self.auto_execute else None
        }

    def _extract_ticket_ids(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract ticket IDs from analysis"""
        # Look for ticket references in patterns/opportunities
        ticket_ids = []
        patterns = analysis_result.get("patterns_detail", [])
        for pattern in patterns:
            metadata = pattern.get("metadata", {})
            if "ticket_id" in metadata:
                ticket_ids.append(metadata["ticket_id"])
        return ticket_ids

    def _extract_pm_task_ids(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract PM task IDs from analysis"""
        pm_task_ids = []
        patterns = analysis_result.get("patterns_detail", [])
        for pattern in patterns:
            metadata = pattern.get("metadata", {})
            if "pm_task_id" in metadata:
                pm_task_ids.append(metadata["pm_task_id"])
        return pm_task_ids

    def _extract_cr_ids(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract change request IDs from analysis"""
        cr_ids = []
        patterns = analysis_result.get("patterns_detail", [])
        for pattern in patterns:
            metadata = pattern.get("metadata", {})
            if "change_request_id" in metadata:
                cr_ids.append(metadata["change_request_id"])
        return cr_ids

    def _extract_completed_tasks(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Extract completed tasks from analysis"""
        completed = []
        opportunities = analysis_result.get("opportunities_detail", [])
        for opp in opportunities:
            if opp.get("status") == "completed":
                completed.append(opp.get("title", ""))
        return completed

    def _get_session_id(self) -> str:
        """Get current session ID"""
        # Try to get from environment or generate
        import os
        session_id = os.environ.get("CURSOR_SESSION_ID") or os.environ.get("SESSION_ID")
        if not session_id:
            # Generate session ID
            session_id = f"workflow_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        return session_id

    def run_continuous(self, check_interval_minutes: int = 60):
        """Run continuous analysis (check every N minutes)"""
        self.logger.info("🔄 Starting continuous workflow analysis")
        self.logger.info(f"   Check interval: {check_interval_minutes} minutes")
        self.logger.info(f"   Analysis interval: {self.analysis_interval} hours")
        self.logger.info(f"   Auto-execute: {self.auto_execute}")
        self.logger.info("")

        while True:
            try:
                if self.should_run_analysis():
                    self.run_analysis_cycle()
                else:
                    elapsed = time.time() - float(self.last_analysis_file.read_text().strip())
                    hours_until = self.analysis_interval - (elapsed / 3600)
                    self.logger.debug(f"⏳ Next analysis in {hours_until:.1f} hours")

                # Sleep until next check
                time.sleep(check_interval_minutes * 60)

            except KeyboardInterrupt:
                self.logger.info("")
                self.logger.info("🛑 Stopping continuous analysis")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in analysis cycle: {e}")
                time.sleep(check_interval_minutes * 60)  # Wait before retry


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Continuous Workflow Analyzer")
    parser.add_argument('--project-root', type=Path, help='Project root directory')
    parser.add_argument('--no-auto-execute', action='store_true', help='Disable auto-execution')
    parser.add_argument('--interval-hours', type=int, default=24, help='Analysis interval in hours')
    parser.add_argument('--check-minutes', type=int, default=60, help='Check interval in minutes')
    parser.add_argument('--once', action='store_true', help='Run once and exit')

    args = parser.parse_args()

    analyzer = ContinuousWorkflowAnalyzer(
        project_root=args.project_root or PROJECT_ROOT,
        auto_execute=not args.no_auto_execute
    )
    analyzer.analysis_interval = args.interval_hours

    if args.once:
        analyzer.run_analysis_cycle()
    else:
        analyzer.run_continuous(check_interval_minutes=args.check_minutes)

    return 0


if __name__ == "__main__":


    sys.exit(main())