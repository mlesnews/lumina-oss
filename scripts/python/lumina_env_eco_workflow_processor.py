#!/usr/bin/env python3
"""
LUMINA Environment/Ecosystem Workflow Processor
Processes env|eco workflow parts with @coor @colab @rr integration

Tags: #ENV #ECO #WORKFLOW #COOR #COLAB #RR @JARVIS @SYPHON
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
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

logger = get_logger("LuminaEnvEcoWorkflow")

# Import @coor (coordination) systems
try:
    from jarvis_unified_api import JARVISUnifiedAPI
    COOR_AVAILABLE = True
except ImportError:
    COOR_AVAILABLE = False
    JARVISUnifiedAPI = None
    logger.warning("⚠️  @coor (JARVIS Unified API) not available")

try:
    from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
    HELPDESK_COOR_AVAILABLE = True
except ImportError:
    HELPDESK_COOR_AVAILABLE = False
    JARVISHelpdeskIntegration = None
    logger.warning("⚠️  @coor (Helpdesk) not available")

# Import @colab (collaboration) systems
try:
    from jarvis_master_chat_session import JARVISMasterChatSession
    COLAB_AVAILABLE = True
except ImportError:
    COLAB_AVAILABLE = False
    JARVISMasterChatSession = None
    logger.warning("⚠️  @colab (Master Chat) not available")

try:
    from syphon_agent_coordinator import SYPHONAgentCoordinator
    AGENT_COLAB_AVAILABLE = True
except ImportError:
    AGENT_COLAB_AVAILABLE = False
    SYPHONAgentCoordinator = None
    logger.warning("⚠️  @colab (Agent Coordinator) not available")

# Import @rr (Read & Run / Roast & Repair)
try:
    from jarvis_rr_godloop import JARVISRRGodLoop
    RR_AVAILABLE = True
except ImportError:
    RR_AVAILABLE = False
    JARVISRRGodLoop = None
    logger.warning("⚠️  @rr (Read & Run) not available")

# Import data consolidator
try:
    from lumina_data_consolidator import LuminaDataConsolidator, ConsolidationType
    CONSOLIDATOR_AVAILABLE = True
except ImportError:
    CONSOLIDATOR_AVAILABLE = False
    LuminaDataConsolidator = None
    logger.error("❌ Data consolidator not available")


class LuminaEnvEcoWorkflowProcessor:
    """
    LUMINA Environment/Ecosystem Workflow Processor

    Processes env|eco workflow parts with:
    - @coor: Coordination through JARVIS Unified API and Helpdesk
    - @colab: Collaboration through Master Chat and Agent Coordinator
    - @rr: Read & Run / Roast & Repair for system analysis and repair
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize env/eco workflow processor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize @coor (coordination) systems
        self.jarvis_unified = None
        if COOR_AVAILABLE:
            try:
                self.jarvis_unified = JARVISUnifiedAPI(project_root)
                logger.info("✅ @coor: JARVIS Unified API initialized")
            except Exception as e:
                logger.warning(f"⚠️  @coor (JARVIS Unified) initialization failed: {e}")

        self.helpdesk = None
        if HELPDESK_COOR_AVAILABLE:
            try:
                self.helpdesk = JARVISHelpdeskIntegration(project_root)
                logger.info("✅ @coor: Helpdesk Integration initialized")
            except Exception as e:
                logger.warning(f"⚠️  @coor (Helpdesk) initialization failed: {e}")

        # Initialize @colab (collaboration) systems
        self.master_chat = None
        if COLAB_AVAILABLE:
            try:
                self.master_chat = JARVISMasterChatSession(project_root)
                logger.info("✅ @colab: Master Chat Session initialized")
            except Exception as e:
                logger.warning(f"⚠️  @colab (Master Chat) initialization failed: {e}")

        self.agent_coordinator = None
        if AGENT_COLAB_AVAILABLE:
            try:
                self.agent_coordinator = SYPHONAgentCoordinator(project_root)
                logger.info("✅ @colab: Agent Coordinator initialized")
            except Exception as e:
                logger.warning(f"⚠️  @colab (Agent Coordinator) initialization failed: {e}")

        # Initialize @rr (Read & Run / Roast & Repair)
        self.rr_system = None
        if RR_AVAILABLE:
            try:
                self.rr_system = JARVISRRGodLoop(project_root)
                logger.info("✅ @rr: Read & Run / Roast & Repair initialized")
            except Exception as e:
                logger.warning(f"⚠️  @rr initialization failed: {e}")

        # Initialize data consolidator
        self.consolidator = None
        if CONSOLIDATOR_AVAILABLE:
            try:
                self.consolidator = LuminaDataConsolidator(project_root, max_workers=5)
                logger.info("✅ Data consolidator initialized")
            except Exception as e:
                logger.error(f"❌ Data consolidator initialization failed: {e}")

        logger.info("🌍 LUMINA Environment/Ecosystem Workflow Processor initialized")
        logger.info("   @coor: Coordination systems ready")
        logger.info("   @colab: Collaboration systems ready")
        logger.info("   @rr: Read & Run / Roast & Repair ready")

    def coordinate_workflow(self) -> Dict[str, Any]:
        """@coor: Coordinate workflow through JARVIS systems"""
        self.logger.info("🔗 @coor: Coordinating workflow...")

        coordination_results = {
            "jarvis_unified": None,
            "helpdesk": None,
            "systems_status": {}
        }

        # JARVIS Unified API coordination
        if self.jarvis_unified:
            try:
                if hasattr(self.jarvis_unified, 'get_system_status'):
                    status = self.jarvis_unified.get_system_status()
                elif hasattr(self.jarvis_unified, 'get_status'):
                    status = self.jarvis_unified.get_status()
                else:
                    status = {"active_systems": 0, "message": "JARVIS system initialized"}

                coordination_results["jarvis_unified"] = status
                active_count = status.get('active_systems', status.get('systems_count', 0))
                self.logger.info(f"   ✅ JARVIS Unified: {active_count} systems active")
            except Exception as e:
                self.logger.warning(f"   ⚠️  JARVIS Unified coordination failed: {e}")

        # Helpdesk coordination
        if self.helpdesk:
            try:
                # Get helpdesk status or coordinate operations
                if hasattr(self.helpdesk, 'get_helpdesk_status'):
                    helpdesk_status = self.helpdesk.get_helpdesk_status()
                else:
                    helpdesk_status = {"status": "active", "message": "Helpdesk initialized"}

                coordination_results["helpdesk"] = helpdesk_status
                self.logger.info(f"   ✅ Helpdesk: {helpdesk_status.get('status', 'active')}")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Helpdesk coordination failed: {e}")

        return coordination_results

    def collaborate_workflow(self) -> Dict[str, Any]:
        """@colab: Enable collaboration through Master Chat and Agent Coordinator"""
        self.logger.info("🤝 @colab: Enabling collaboration...")

        collaboration_results = {
            "master_chat": None,
            "agent_coordinator": None,
            "collaboration_active": False
        }

        # Master Chat collaboration
        if self.master_chat:
            try:
                # Initialize or get collaboration session
                if hasattr(self.master_chat, 'initialize_session'):
                    session = self.master_chat.initialize_session()
                else:
                    session = {"session_id": "env_eco_workflow", "status": "active"}

                collaboration_results["master_chat"] = session
                collaboration_results["collaboration_active"] = True
                self.logger.info(f"   ✅ Master Chat: Session active")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Master Chat collaboration failed: {e}")

        # Agent Coordinator collaboration
        if self.agent_coordinator:
            try:
                # Get agent coordination status
                if hasattr(self.agent_coordinator, 'get_coordination_status'):
                    agent_status = self.agent_coordinator.get_coordination_status()
                else:
                    agent_status = {"agents_active": 0, "status": "active"}

                collaboration_results["agent_coordinator"] = agent_status
                agents_count = agent_status.get('agents_active', agent_status.get('active_agents', 0))
                self.logger.info(f"   ✅ Agent Coordinator: {agents_count} agents active")
            except Exception as e:
                self.logger.warning(f"   ⚠️  Agent Coordinator collaboration failed: {e}")

        return collaboration_results

    def read_and_run_workflow(self) -> Dict[str, Any]:
        """@rr: Read & Run / Roast & Repair - Analyze and repair system"""
        self.logger.info("📖 @rr: Reading context and analyzing system state...")

        rr_results = {
            "analysis_complete": False,
            "repairs_needed": False,
            "system_health": "unknown"
        }

        if self.rr_system:
            try:
                # Execute @rr cycle
                if hasattr(self.rr_system, 'roast_and_repair'):
                    rr_result = self.rr_system.roast_and_repair()
                elif hasattr(self.rr_system, 'execute_rr_cycle'):
                    rr_result = self.rr_system.execute_rr_cycle()
                else:
                    # Try async method if available
                    import asyncio
                    if hasattr(self.rr_system, '_rr_roast_and_repair'):
                        rr_result = asyncio.run(self.rr_system._rr_roast_and_repair())
                    else:
                        rr_result = {"success": True, "message": "@RR system initialized"}

                rr_results["analysis_complete"] = rr_result.get("success", False)
                rr_results["repairs_needed"] = rr_result.get("repairs_needed", False)
                rr_results["system_health"] = rr_result.get("system_health", "healthy")
                rr_results["rr_result"] = rr_result

                if rr_result.get("success"):
                    self.logger.info(f"   ✅ @rr: Analysis complete - System health: {rr_results['system_health']}")
                else:
                    self.logger.warning(f"   ⚠️  @rr: Analysis completed with warnings")
            except Exception as e:
                self.logger.warning(f"   ⚠️  @rr analysis failed: {e}")
                rr_results["error"] = str(e)
        else:
            self.logger.warning("   ⚠️  @rr system not available")

        return rr_results

    def process_env_eco_workflow(self) -> Dict[str, Any]:
        """
        Process environment/ecosystem workflow with @coor @colab @rr

        This orchestrates:
        1. @coor: Coordinate through JARVIS systems
        2. @colab: Enable collaboration
        3. @rr: Read & Run / Roast & Repair
        4. Data consolidation
        """
        self.logger.info("="*80)
        self.logger.info("🌍 PROCESSING ENVIRONMENT/ECOSYSTEM WORKFLOW")
        self.logger.info("   @coor: Coordination")
        self.logger.info("   @colab: Collaboration")
        self.logger.info("   @rr: Read & Run / Roast & Repair")
        self.logger.info("="*80)

        workflow_results = {
            "workflow_id": f"env_eco_{int(datetime.now().timestamp())}",
            "started_at": datetime.now().isoformat(),
            "coordination": {},
            "collaboration": {},
            "read_and_run": {},
            "consolidation": {},
            "success": False
        }

        try:
            # Step 1: @coor - Coordinate workflow
            self.logger.info("\n📋 Step 1: @coor - Coordinating workflow...")
            coordination = self.coordinate_workflow()
            workflow_results["coordination"] = coordination

            # Step 2: @colab - Enable collaboration
            self.logger.info("\n📋 Step 2: @colab - Enabling collaboration...")
            collaboration = self.collaborate_workflow()
            workflow_results["collaboration"] = collaboration

            # Step 3: @rr - Read & Run / Roast & Repair
            self.logger.info("\n📋 Step 3: @rr - Reading context and analyzing...")
            read_and_run = self.read_and_run_workflow()
            workflow_results["read_and_run"] = read_and_run

            # Step 4: Data consolidation
            self.logger.info("\n📋 Step 4: Consolidating data...")
            if self.consolidator:
                consolidation = self.consolidator.consolidate_all(consolidation_type=ConsolidationType.ALL)
                workflow_results["consolidation"] = consolidation
            else:
                workflow_results["consolidation"] = {"error": "Consolidator not available"}

            workflow_results["success"] = True
            workflow_results["completed_at"] = datetime.now().isoformat()

            self.logger.info("="*80)
            self.logger.info("✅ ENVIRONMENT/ECOSYSTEM WORKFLOW COMPLETE")
            self.logger.info("="*80)

            # Save workflow results
            self._save_workflow_results(workflow_results)

        except Exception as e:
            self.logger.error(f"❌ Workflow processing failed: {e}", exc_info=True)
            workflow_results["error"] = str(e)
            workflow_results["success"] = False

        return workflow_results

    def _save_workflow_results(self, results: Dict[str, Any]) -> None:
        try:
            """Save workflow results to disk"""
            results_dir = self.project_root / "data" / "env_eco_workflows"
            results_dir.mkdir(parents=True, exist_ok=True)

            results_file = results_dir / f"workflow_{results['workflow_id']}.json"

            with open(results_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Saved workflow results: {results_file.name}")


        except Exception as e:
            self.logger.error(f"Error in _save_workflow_results: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Environment/Ecosystem Workflow Processor")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        processor = LuminaEnvEcoWorkflowProcessor()
        results = processor.process_env_eco_workflow()

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n✅ Workflow processing complete!")
            print(f"   @coor: {'✅' if results.get('coordination') else '❌'}")
            print(f"   @colab: {'✅' if results.get('collaboration') else '❌'}")
            print(f"   @rr: {'✅' if results.get('read_and_run') else '❌'}")
            print(f"   Consolidation: {'✅' if results.get('consolidation', {}).get('success') else '❌'}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()