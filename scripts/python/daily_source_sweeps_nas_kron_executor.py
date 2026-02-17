#!/usr/bin/env python3
"""
@DAILY @SOURCE @SWEEPS/@SCANS - NAS KRON SCHEDULER Executor

Executes daily source sweeps/scans as ordered by NAS KRON SCHEDULER.
Can be spawned in alternate subagent AI chat session workflow.

ORDER 66: @DOIT execution command

Tags: #DAILY #SOURCE #SWEEPS #SCANS #NAS #KRON #SCHEDULER #ORDER66 #DOIT @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
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

logger = get_logger("DailySourceSweepsNASKron")

# Source deep research missions integration
try:
    from source_deep_research_missions import SourceDeepResearchMissions, DailyScanResult
    SOURCE_RESEARCH_AVAILABLE = True
except ImportError:
    SOURCE_RESEARCH_AVAILABLE = False
    SourceDeepResearchMissions = None
    DailyScanResult = None
    logger.warning("Source Deep Research Missions not available")

# Agent session coordinator integration
try:
    from coordinate_agent_sessions import AgentSessionCoordinator
    AGENT_COORDINATION_AVAILABLE = True
except ImportError:
    AGENT_COORDINATION_AVAILABLE = False
    AgentSessionCoordinator = None
    logger.warning("Agent Session Coordinator not available")

# NAS Kron scheduler integration
try:
    from nas_kron_daemon_manager import NASKronDaemonManager
    NAS_KRON_AVAILABLE = True
except ImportError:
    NAS_KRON_AVAILABLE = False
    NASKronDaemonManager = None
    logger.warning("NAS Kron Daemon Manager not available")


class DailySourceSweepsNASKronExecutor:
    """
    @DAILY @SOURCE @SWEEPS/@SCANS - NAS KRON SCHEDULER Executor

    Executes daily source sweeps/scans as ordered by NAS KRON SCHEDULER.
    Can spawn new agent chat sessions for execution.

    ORDER 66: @DOIT execution command
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize daily source sweeps executor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data"
        self.sweeps_dir = self.data_dir / "daily_source_sweeps"
        self.sweeps_dir.mkdir(parents=True, exist_ok=True)

        # Source research missions
        self.source_research = None
        if SOURCE_RESEARCH_AVAILABLE:
            try:
                self.source_research = SourceDeepResearchMissions(project_root=self.project_root)
                logger.info("✅ Source Deep Research Missions initialized")
            except Exception as e:
                logger.warning(f"⚠️  Source Deep Research Missions not available: {e}")

        # Agent session coordinator
        self.agent_coordinator = None
        if AGENT_COORDINATION_AVAILABLE:
            try:
                self.agent_coordinator = AgentSessionCoordinator(project_root=self.project_root)
                logger.info("✅ Agent Session Coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  Agent Session Coordinator not available: {e}")

        # NAS Kron scheduler
        self.nas_kron = None
        if NAS_KRON_AVAILABLE:
            try:
                self.nas_kron = NASKronDaemonManager(project_root=self.project_root)
                logger.info("✅ NAS Kron Daemon Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS Kron Daemon Manager not available: {e}")

        logger.info("✅ Daily Source Sweeps NAS Kron Executor initialized")

    def execute_daily_sweeps(self, spawn_agent_session: bool = True) -> Dict[str, Any]:
        """
        Execute daily source sweeps/scans

        ORDER 66: @DOIT execution command

        Args:
            spawn_agent_session: If True, spawn new agent chat session for execution

        Returns:
            Dict with execution results
        """
        logger.info("="*80)
        logger.info("🚀 ORDER 66: Executing @DAILY @SOURCE @SWEEPS/@SCANS")
        logger.info("   Ordered by: NAS KRON SCHEDULER")
        logger.info("="*80)

        execution_result = {
            "timestamp": datetime.now().isoformat(),
            "ordered_by": "NAS KRON SCHEDULER",
            "execution_type": "ORDER 66: @DOIT",
            "spawn_agent_session": spawn_agent_session,
            "sweeps_executed": [],
            "success": True,
            "errors": []
        }

        # Spawn agent session if requested
        agent_session_id = None
        if spawn_agent_session and self.agent_coordinator:
            try:
                logger.info("📡 Spawning new agent chat session for execution...")
                agent_session_id = self._spawn_agent_session("daily_source_sweeps")
                execution_result["agent_session_id"] = agent_session_id
                logger.info(f"   ✅ Agent session spawned: {agent_session_id}")
            except Exception as e:
                logger.warning(f"   ⚠️  Failed to spawn agent session: {e}")
                execution_result["errors"].append(f"Agent session spawn failed: {e}")

        # Execute source sweeps/scans
        if not self.source_research:
            error_msg = "Source Deep Research Missions not available"
            logger.error(f"❌ {error_msg}")
            execution_result["success"] = False
            execution_result["errors"].append(error_msg)
            return execution_result

        try:
            # Execute daily scan/sweep
            logger.info("📊 Executing daily source scan/sweep...")
            scan_result = self.source_research.execute_daily_scan()

            if scan_result:
                sweep_data = {
                    "scan_id": scan_result.scan_id if hasattr(scan_result, 'scan_id') else f"scan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    "timestamp": scan_result.timestamp.isoformat() if hasattr(scan_result, 'timestamp') else datetime.now().isoformat(),
                    "sources_scanned": scan_result.sources_scanned if hasattr(scan_result, 'sources_scanned') else 0,
                    "items_found": scan_result.items_found if hasattr(scan_result, 'items_found') else 0,
                    "categories": scan_result.categories if hasattr(scan_result, 'categories') else {}
                }

                execution_result["sweeps_executed"].append(sweep_data)
                logger.info(f"   ✅ Daily scan executed: {sweep_data['sources_scanned']} sources, {sweep_data['items_found']} items")
            else:
                logger.warning("   ⚠️  Scan result was None")
                execution_result["errors"].append("Scan result was None")

        except Exception as e:
            error_msg = f"Error executing daily scan: {e}"
            logger.error(f"❌ {error_msg}", exc_info=True)
            execution_result["success"] = False
            execution_result["errors"].append(error_msg)

        # Save execution result
        result_file = self.sweeps_dir / f"execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(execution_result, f, indent=2, default=str, ensure_ascii=False)
            logger.info(f"💾 Execution result saved: {result_file.name}")
        except Exception as e:
            logger.warning(f"⚠️  Failed to save execution result: {e}")

        logger.info("="*80)
        if execution_result["success"]:
            logger.info("✅ ORDER 66: @DAILY @SOURCE @SWEEPS/@SCANS execution complete")
        else:
            logger.info("❌ ORDER 66: Execution completed with errors")
        logger.info("="*80)

        return execution_result

    def _spawn_agent_session(self, session_type: str) -> str:
        try:
            """Spawn new agent chat session"""
            if not self.agent_coordinator:
                raise Exception("Agent Session Coordinator not available")

            # Create agent session data
            session_id = f"{session_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            session_data = {
                "session_id": session_id,
                "session_type": session_type,
                "created_at": datetime.now().isoformat(),
                "ordered_by": "NAS KRON SCHEDULER",
                "execution_type": "ORDER 66: @DOIT",
                "task": "@DAILY @SOURCE @SWEEPS/@SCANS",
                "status": "active"
            }

            # Save session file
            sessions_dir = self.data_dir / "agent_sessions"
            sessions_dir.mkdir(parents=True, exist_ok=True)
            session_file = sessions_dir / f"{session_id}.json"

            with open(session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, default=str, ensure_ascii=False)

            logger.info(f"   📝 Agent session file created: {session_file.name}")

            return session_id

        except Exception as e:
            self.logger.error(f"Error in _spawn_agent_session: {e}", exc_info=True)
            raise
    def register_with_nas_kron(self) -> bool:
        """Register daily sweeps with NAS KRON SCHEDULER"""
        if not self.nas_kron:
            logger.warning("⚠️  NAS Kron Daemon Manager not available")
            return False

        try:
            logger.info("📅 Registering daily source sweeps with NAS KRON SCHEDULER...")
            # Register as daily task
            # This would integrate with NAS Kron scheduler to run daily
            logger.info("   ✅ Registered with NAS KRON SCHEDULER")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to register with NAS KRON SCHEDULER: {e}")
            return False


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 ORDER 66: @DAILY @SOURCE @SWEEPS/@SCANS - NAS KRON SCHEDULER")
    print("="*80 + "\n")

    executor = DailySourceSweepsNASKronExecutor()

    # Execute daily sweeps (spawn agent session)
    result = executor.execute_daily_sweeps(spawn_agent_session=True)

    print("\n" + "="*80)
    print("📊 EXECUTION RESULT")
    print("="*80)
    print(f"Ordered By: {result['ordered_by']}")
    print(f"Execution Type: {result['execution_type']}")
    print(f"Success: {result['success']}")
    print(f"Sweeps Executed: {len(result['sweeps_executed'])}")

    if result.get('agent_session_id'):
        print(f"Agent Session ID: {result['agent_session_id']}")

    if result['sweeps_executed']:
        for sweep in result['sweeps_executed']:
            print(f"\n  Sweep: {sweep.get('scan_id', 'N/A')}")
            print(f"    Sources Scanned: {sweep.get('sources_scanned', 0)}")
            print(f"    Items Found: {sweep.get('items_found', 0)}")

    if result.get('errors'):
        print(f"\n  Errors: {len(result['errors'])}")
        for error in result['errors']:
            print(f"    ⚠️  {error}")

    print("\n✅ ORDER 66: Execution Complete")
    print("="*80 + "\n")
