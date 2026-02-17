#!/usr/bin/env python3
"""
Execute All Systems @DOIT - Connect @ask @chains for All Next Steps

Unified execution system that chains together:
1. SYPHON + Agents/Subagents + VAs + @asks Unified System
2. Content Creation Engine (Books & YouTube Docuseries)
3. Building Blocks + @PEAK + Jedi Archive Organizer
4. Workflow Flow Rate Calculator & IDE Footer Display
5. Bad Request Error Diagnostic & Fix System

@DOIT Workflow Integration:
- Always @DOIT (execute, don't just suggest)
- Answer own questions proactively
- Generate 3 viable actionable solutions
- Apply @5W1H (Who, What, When, Where, Why, How) questioning framework

Tags: #EXECUTE #DOIT #CHAINS #UNIFIED #5W1H @JARVIS @TEAM
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime
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

logger = get_logger("ExecuteAllSystemsDOIT")


class UnifiedSystemExecutor:
    """
    Unified System Executor - Connect @ask @chains for All Next Steps

    Chains together all systems and executes them in proper order

    @DOIT Workflow Integration:
    - Always @DOIT (execute, don't just suggest)
    - Answer own questions proactively
    - Generate 3 viable actionable solutions
    - Apply @5W1H questioning framework
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize unified executor"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.results = {}

        # Initialize @DOIT 5W1H Workflow
        try:
            from doit_5w1h_workflow import DOIT5W1HWorkflow
            self.doit_workflow = DOIT5W1HWorkflow(project_root=self.project_root)
            logger.info("✅ @DOIT 5W1H Workflow integrated")
        except ImportError:
            self.doit_workflow = None
            logger.warning("⚠️  @DOIT 5W1H Workflow not available")

        logger.info("✅ Unified System Executor initialized")

    def execute_all(self) -> Dict[str, Any]:
        """
        Execute all systems in proper chain order

        Execution Chain:
        1. SYPHON + Agents + VAs + @asks Unified System
        2. Building Blocks + @PEAK + Jedi Archive Organizer
        3. Content Creation Engine
        4. Workflow Flow Rate Calculator
        5. IDE Footer Flow Rate Display
        """
        logger.info("🚀 Starting Unified System Execution - @DOIT")

        execution_results = {
            "started_at": datetime.now().isoformat(),
            "systems_executed": [],
            "errors": [],
            "success": True
        }

        try:
            # Step 1: SYPHON + Agents + VAs + @asks Unified System (with @ask @chains)
            logger.info("\n" + "="*80)
            logger.info("STEP 1: SYPHON + Agents + VAs + @asks Unified System")
            logger.info("   🔗 Connecting @ask @chains: Discover → Restack → Timeline → Process")
            logger.info("="*80)
            result1 = self._execute_syphon_agents_asks_system()
            execution_results["systems_executed"].append({
                "system": "SYPHON + Agents + VAs + @asks (@ask @chains connected)",
                "success": result1.get("success", False),
                "result": result1
            })

            # Extract @asks data for next steps
            asks_data = result1.get("result", {})
            if asks_data.get("asks_discovered", 0) > 0:
                logger.info(f"   📊 @asks data available: {asks_data.get('asks_discovered', 0)} asks discovered")
                execution_results["asks_data"] = asks_data

            # Step 2: Building Blocks + @PEAK + Jedi Archive Organizer
            logger.info("\n" + "="*80)
            logger.info("STEP 2: Building Blocks + @PEAK + Jedi Archive Organizer")
            logger.info("="*80)
            result2 = self._execute_building_blocks_peak_jedi()
            execution_results["systems_executed"].append({
                "system": "Building Blocks + @PEAK + Jedi Archive",
                "success": result2.get("success", False),
                "result": result2
            })

            # Step 3: Content Creation Engine
            logger.info("\n" + "="*80)
            logger.info("STEP 3: Content Creation Engine")
            logger.info("="*80)
            result3 = self._execute_content_creation_engine()
            execution_results["systems_executed"].append({
                "system": "Content Creation Engine",
                "success": result3.get("success", False),
                "result": result3
            })

            # Step 4: Workflow Flow Rate Calculator
            logger.info("\n" + "="*80)
            logger.info("STEP 4: Workflow Flow Rate Calculator")
            logger.info("="*80)
            result4 = self._execute_workflow_flow_rate_calculator()
            execution_results["systems_executed"].append({
                "system": "Workflow Flow Rate Calculator",
                "success": result4.get("success", False),
                "result": result4
            })

            # Step 5: IDE Footer Flow Rate Display
            logger.info("\n" + "="*80)
            logger.info("STEP 5: IDE Footer Flow Rate Display")
            logger.info("="*80)
            result5 = self._execute_ide_footer_display()
            execution_results["systems_executed"].append({
                "system": "IDE Footer Flow Rate Display",
                "success": result5.get("success", False),
                "result": result5
            })

            execution_results["completed_at"] = datetime.now().isoformat()
            execution_results["success"] = all(
                s["success"] for s in execution_results["systems_executed"]
            )

            logger.info("\n" + "="*80)
            logger.info("✅ ALL SYSTEMS EXECUTION COMPLETE - @DOIT")
            logger.info("="*80)

        except Exception as e:
            logger.error(f"❌ Error during execution: {e}", exc_info=True)
            execution_results["errors"].append(str(e))
            execution_results["success"] = False

        return execution_results

    def _execute_syphon_agents_asks_system(self) -> Dict[str, Any]:
        """Execute SYPHON + Agents + VAs + @asks Unified System"""
        try:
            from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem
            from jarvis_restack_all_asks import ASKRestacker

            # Initialize unified system
            system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
            status = system.get_system_status()

            logger.info("✅ SYPHON + Agents + VAs + @asks Unified System initialized")
            logger.info(f"   SYPHON Available: {status.get('syphon_available', False)}")
            logger.info(f"   @asks Available: {status.get('asks_available', False)}")
            logger.info(f"   Agents Tracked: {status.get('agents_tracked', 0)}")

            # Connect @ask chains: Discover, Restack, Timeline
            logger.info("\n   🔗 Connecting @ask @chains...")

            # Step 1: Discover all @asks
            if system.ask_restacker:
                logger.info("   📋 Step 1: Discovering all @asks...")
                all_asks = system.ask_restacker.discover_all_asks()
                logger.info(f"      ✅ Discovered {len(all_asks)} @asks")

                if all_asks:
                    # Step 2: Restack @asks
                    logger.info("   📚 Step 2: Restacking @asks...")
                    restacked_asks = system.ask_restacker.restack_asks(all_asks)
                    logger.info(f"      ✅ Restacked {len(restacked_asks)} @asks")

                    # Step 3: Create timeline
                    logger.info("   📖 Step 3: Creating timeline...")
                    timeline = system.ask_restacker.create_timeline(restacked_asks)
                    logger.info(f"      ✅ Created timeline with {len(timeline)} entries")

                    # Step 4: Process @asks through unified system
                    logger.info("   🔄 Step 4: Processing @asks through unified system...")
                    system._process_asks()
                    logger.info("      ✅ @asks processed through unified system")

                    # Step 5: Get timeline from system
                    timeline_from_system = system.get_asks_timeline()
                    logger.info(f"      ✅ Retrieved timeline: {len(timeline_from_system)} entries")

                    return {
                        "success": True,
                        "status": status,
                        "asks_discovered": len(all_asks),
                        "asks_restacked": len(restacked_asks),
                        "timeline_entries": len(timeline),
                        "timeline_from_system": len(timeline_from_system)
                    }
                else:
                    logger.info("      ⚠️  No @asks found to process")
            else:
                logger.info("      ⚠️  @asks restacker not available")

            return {"success": True, "status": status}

        except Exception as e:
            logger.warning(f"⚠️  SYPHON + Agents + VAs + @asks System: {e}")
            return {"success": False, "error": str(e)}

    def _execute_building_blocks_peak_jedi(self) -> Dict[str, Any]:
        """Execute Building Blocks + @PEAK + Jedi Archive Organizer"""
        try:
            from building_blocks_peak_jedi_organizer import BuildingBlocksPeakJediOrganizer, OperationalIntent

            organizer = BuildingBlocksPeakJediOrganizer(project_root=self.project_root)

            # Process example operational intent
            example_intent = """
            def extract_intelligence(self, source: str) -> Dict[str, Any]:
                \"\"\"Extract intelligence from source\"\"\"
                result = self.syphon.extract(source)
                return result
            """

            result = organizer.process_operational_intent(
                example_intent,
                OperationalIntent.INTELLIGENCE
            )

            logger.info("✅ Building Blocks + @PEAK + Jedi Archive Organizer executed")
            logger.info(f"   Building Blocks: {result.get('total_blocks', 0)}")
            logger.info(f"   Catalog Entries: {result.get('total_catalog_entries', 0)}")

            return {"success": True, "result": result}

        except Exception as e:
            logger.warning(f"⚠️  Building Blocks + @PEAK + Jedi Archive: {e}")
            return {"success": False, "error": str(e)}

    def _execute_content_creation_engine(self) -> Dict[str, Any]:
        """Execute Content Creation Engine (uses @asks from Step 1)"""
        try:
            from content_creation_engine import ContentCreationEngine

            engine = ContentCreationEngine(project_root=self.project_root)

            # Get @asks timeline from unified system
            from syphon_agents_asks_unified_system import SYPHONAgentsAsksUnifiedSystem
            system = SYPHONAgentsAsksUnifiedSystem(project_root=self.project_root)
            timeline = system.get_asks_timeline()

            logger.info(f"   📖 Using {len(timeline)} @asks from timeline for content creation")

            # Create a book from @asks
            book = engine.create_book_from_asks(
                title="The Lumina Project: A Journey Through Conversation",
                subtitle="From Ideas to Intelligence",
                author="JARVIS AI"
            )

            logger.info("✅ Content Creation Engine executed")
            if book:
                logger.info(f"   Book Created: {len(book.chapters)} chapters")
                book_file = engine.save_book(book)
                logger.info(f"   Book Saved: {book_file.name}")

            return {"success": True, "book_created": book is not None, "asks_used": len(timeline)}

        except Exception as e:
            logger.warning(f"⚠️  Content Creation Engine: {e}")
            return {"success": False, "error": str(e)}

    def _execute_workflow_flow_rate_calculator(self) -> Dict[str, Any]:
        """Execute Workflow Flow Rate Calculator"""
        try:
            from workflow_flow_rate_calculator import WorkflowFlowRateCalculator

            calculator = WorkflowFlowRateCalculator(project_root=self.project_root)

            # Simulate some workflows
            for i in range(3):
                workflow_id = f"workflow_{i+1}"
                calculator.register_workflow(workflow_id, tasks_total=10)
                calculator.update_workflow(workflow_id, tasks_completed=5 + i)

            stats = calculator.calculate_flow_rate()

            logger.info("✅ Workflow Flow Rate Calculator executed")
            logger.info(f"   Current Flow Rate: {stats.current_flow_rate:.2f} workflows/s")
            logger.info(f"   Peak Flow Rate: {stats.peak_flow_rate:.2f} workflows/s")
            logger.info(f"   Efficiency: {stats.efficiency * 100:.1f}%")

            return {"success": True, "stats": stats.to_dict()}

        except Exception as e:
            logger.warning(f"⚠️  Workflow Flow Rate Calculator: {e}")
            return {"success": False, "error": str(e)}

    def _execute_ide_footer_display(self) -> Dict[str, Any]:
        """Execute IDE Footer Flow Rate Display"""
        try:
            from ide_footer_flow_rate_display import IDEFooterFlowRateDisplay

            display = IDEFooterFlowRateDisplay(project_root=self.project_root)

            # Start display
            display.start()
            time.sleep(1.0)  # Let it update

            # Get display text
            display_text = display.get_display_text()
            stats = display.get_stats()

            logger.info("✅ IDE Footer Flow Rate Display executed")
            logger.info(f"   Display Text: {display_text[:60]}...")
            if stats:
                logger.info(f"   Current Flow Rate: {stats.get('current_flow_rate', 0):.2f} workflows/s")

            # Stop display
            display.stop()

            return {"success": True, "display_text": display_text, "stats": stats}

        except Exception as e:
            logger.warning(f"⚠️  IDE Footer Flow Rate Display: {e}")
            return {"success": False, "error": str(e)}


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 EXECUTE ALL SYSTEMS @DOIT - Connect @ask @chains for All Next Steps")
    print("="*80 + "\n")

    executor = UnifiedSystemExecutor()
    results = executor.execute_all()

    print("\n" + "="*80)
    print("📊 EXECUTION SUMMARY")
    print("="*80)
    print(f"   Started: {results.get('started_at', 'N/A')}")
    print(f"   Completed: {results.get('completed_at', 'N/A')}")
    print(f"   Success: {results.get('success', False)}")
    print(f"\n   Systems Executed: {len(results.get('systems_executed', []))}")

    for system in results.get("systems_executed", []):
        status_icon = "✅" if system.get("success") else "❌"
        print(f"   {status_icon} {system.get('system', 'Unknown')}")

    if results.get("errors"):
        print(f"\n   Errors: {len(results['errors'])}")
        for error in results["errors"]:
            print(f"      ⚠️  {error}")

    print("\n✅ @DOIT EXECUTION COMPLETE")
    print("="*80 + "\n")
