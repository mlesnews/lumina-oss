#!/usr/bin/env python3
"""
LUMINA Data Consolidation @DOIT Chain
Connects @ask @chains for data consolidation and executes @doit

Tags: #CONSOLIDATION #DOIT #ASKS #CHAINING @JARVIS @SYPHON
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

logger = get_logger("LuminaConsolidationDOITChain")

# Import @ask chain system
try:
    from jarvis_execute_ask_chains import JARVISAskChainExecutor
    ASK_CHAIN_AVAILABLE = True
except ImportError:
    ASK_CHAIN_AVAILABLE = False
    JARVISAskChainExecutor = None
    logger.warning("⚠️  @ask chain system not available")

# Import @doit executor
try:
    from jarvis_doit_executor import JARVISDOITExecutor
    DOIT_AVAILABLE = True
except ImportError:
    DOIT_AVAILABLE = False
    JARVISDOITExecutor = None
    logger.error("❌ @DOIT executor not available")

# Import data consolidator
try:
    from lumina_data_consolidator import LuminaDataConsolidator, ConsolidationType
    CONSOLIDATOR_AVAILABLE = True
except ImportError:
    CONSOLIDATOR_AVAILABLE = False
    LuminaDataConsolidator = None
    logger.error("❌ Data consolidator not available")


class LuminaConsolidationDOITChain:
    """
    LUMINA Data Consolidation @DOIT Chain

    Connects @ask @chains for data consolidation workflow and executes @doit
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize consolidation @doit chain"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger

        # Initialize @ask chain executor
        self.ask_chain_executor = None
        if ASK_CHAIN_AVAILABLE:
            try:
                self.ask_chain_executor = JARVISAskChainExecutor(project_root)
                logger.info("✅ @ask chain executor initialized")
            except Exception as e:
                logger.warning(f"⚠️  @ask chain executor initialization failed: {e}")

        # Initialize @doit executor
        self.doit_executor = None
        if DOIT_AVAILABLE:
            try:
                self.doit_executor = JARVISDOITExecutor(project_root)
                logger.info("✅ @DOIT executor initialized")
            except Exception as e:
                logger.error(f"❌ @DOIT executor initialization failed: {e}")

        # Initialize data consolidator
        self.consolidator = None
        if CONSOLIDATOR_AVAILABLE:
            try:
                self.consolidator = LuminaDataConsolidator(project_root, max_workers=5)
                logger.info("✅ Data consolidator initialized")
            except Exception as e:
                logger.error(f"❌ Data consolidator initialization failed: {e}")

        logger.info("📚 LUMINA Consolidation @DOIT Chain initialized")

    def create_consolidation_asks(self) -> List[Dict[str, Any]]:
        """Create @ask tasks for data consolidation workflow"""
        self.logger.info("📋 Creating @ask tasks for data consolidation...")

        asks = [
            {
                "text": "@ASK: Consolidate all documents from docs/ directory",
                "priority": "high",
                "category": "consolidation",
                "metadata": {
                    "type": "documents",
                    "workflow": "lumina_data_consolidation"
                }
            },
            {
                "text": "@ASK: Consolidate all holocrons from data/holocron/ directory",
                "priority": "high",
                "category": "consolidation",
                "metadata": {
                    "type": "holocrons",
                    "workflow": "lumina_data_consolidation"
                }
            },
            {
                "text": "@ASK: Consolidate YouTube videos for docuseries generation",
                "priority": "high",
                "category": "consolidation",
                "metadata": {
                    "type": "youtube_videos",
                    "workflow": "lumina_data_consolidation"
                }
            },
            {
                "text": "@ASK: Generate @Sparks insights from consolidation metrics",
                "priority": "medium",
                "category": "insights",
                "metadata": {
                    "workflow": "lumina_data_consolidation",
                    "depends_on": ["documents", "holocrons", "youtube_videos"]
                }
            },
            {
                "text": "@ASK: Generate docuseries script from consolidated data",
                "priority": "high",
                "category": "docuseries",
                "metadata": {
                    "workflow": "lumina_data_consolidation",
                    "depends_on": ["documents", "holocrons", "youtube_videos"]
                }
            },
            {
                "text": "@ASK: Feed consolidation telemetry to SYPHON workflow system",
                "priority": "medium",
                "category": "telemetry",
                "metadata": {
                    "workflow": "lumina_data_consolidation",
                    "depends_on": ["documents", "holocrons", "youtube_videos"]
                }
            }
        ]

        self.logger.info(f"✅ Created {len(asks)} @ask tasks")
        return asks

    def create_consolidation_chain(self) -> Optional[str]:
        """Create @ask chain for data consolidation"""
        self.logger.info("🔗 Creating @ask chain for data consolidation...")

        if not self.ask_chain_executor:
            self.logger.error("❌ @ask chain executor not available")
            return None

        # Create @ask tasks
        asks = self.create_consolidation_asks()

        # Check if chain manager is available
        if not hasattr(self.ask_chain_executor, 'chain_manager'):
            self.logger.error("❌ Chain manager not available")
            return None

        chain_manager = self.ask_chain_executor.chain_manager

        # Create chain from asks
        try:
            chain_id = chain_manager.create_chain(asks)
            self.logger.info(f"✅ Created consolidation chain: {chain_id}")
            return chain_id
        except Exception as e:
            self.logger.error(f"❌ Failed to create chain: {e}")
            return None

    def execute_consolidation_workflow(self) -> Dict[str, Any]:
        """Execute data consolidation workflow directly"""
        self.logger.info("🚀 Executing data consolidation workflow...")

        if not self.consolidator:
            return {
                "success": False,
                "error": "Data consolidator not available"
            }

        try:
            # Execute consolidation
            result = self.consolidator.consolidate_all(consolidation_type=ConsolidationType.ALL)

            self.logger.info("✅ Data consolidation workflow complete")
            return result

        except Exception as e:
            self.logger.error(f"❌ Consolidation workflow failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def execute_doit(self, use_triage: bool = True) -> Dict[str, Any]:
        """Execute @doit with consolidation workflow"""
        self.logger.info("="*80)
        self.logger.info("🚀 EXECUTING @DOIT WITH CONSOLIDATION WORKFLOW")
        self.logger.info("="*80)

        if not self.doit_executor:
            self.logger.error("❌ @DOIT executor not available")
            return {
                "success": False,
                "error": "@DOIT executor not available"
            }

        try:
            # Execute @doit
            doit_result = self.doit_executor.doit(use_triage=use_triage)

            # Also execute consolidation workflow
            consolidation_result = self.execute_consolidation_workflow()

            return {
                "success": True,
                "doit_result": doit_result,
                "consolidation_result": consolidation_result,
                "executed_at": datetime.now().isoformat()
            }

        except Exception as e:
            self.logger.error(f"❌ @DOIT execution failed: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    def connect_chains_and_execute_doit(self, use_triage: bool = True) -> Dict[str, Any]:
        """
        Connect @ask @chains for all next steps and execute @doit

        This is the main entry point that:
        1. Creates @ask chains for consolidation workflow
        2. Connects chains to @doit
        3. Executes @doit with full autonomy
        """
        self.logger.info("="*80)
        self.logger.info("🔗 CONNECTING @ASK @CHAINS FOR ALL NEXT STEPS")
        self.logger.info("🚀 EXECUTING @DOIT")
        self.logger.info("="*80)

        results = {
            "chain_created": False,
            "chain_id": None,
            "doit_executed": False,
            "consolidation_executed": False,
            "results": {}
        }

        # Step 1: Create @ask chain
        if self.ask_chain_executor:
            self.logger.info("\n📋 Step 1: Creating @ask chain...")
            chain_id = self.create_consolidation_chain()

            if chain_id:
                results["chain_created"] = True
                results["chain_id"] = chain_id
                self.logger.info(f"✅ Chain created: {chain_id}")

                # Optionally execute chain
                try:
                    chain_result = self.ask_chain_executor.execute_chain(chain_id, max_parallel=3)
                    self.logger.info(f"✅ Chain execution result: {chain_result.get('tasks_completed', 0)} tasks completed")
                except Exception as e:
                    self.logger.warning(f"⚠️  Chain execution failed: {e}")
            else:
                self.logger.warning("⚠️  Could not create chain, proceeding with direct execution")
        else:
            self.logger.warning("⚠️  @ask chain executor not available, proceeding with direct execution")

        # Step 2: Execute consolidation workflow
        self.logger.info("\n📚 Step 2: Executing data consolidation workflow...")
        consolidation_result = self.execute_consolidation_workflow()
        results["consolidation_executed"] = True
        results["results"]["consolidation"] = consolidation_result

        # Step 3: Execute @doit
        self.logger.info("\n🚀 Step 3: Executing @DOIT...")
        doit_result = self.execute_doit(use_triage=use_triage)
        results["doit_executed"] = True
        results["results"]["doit"] = doit_result

        self.logger.info("="*80)
        self.logger.info("✅ ALL STEPS COMPLETE")
        self.logger.info("="*80)

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Consolidation @DOIT Chain")
        parser.add_argument("--no-triage", action="store_true", 
                           help="Disable triage system")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        chain_executor = LuminaConsolidationDOITChain()
        results = chain_executor.connect_chains_and_execute_doit(use_triage=not args.no_triage)

        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(f"\n✅ Execution complete!")
            print(f"   Chain created: {results.get('chain_created', False)}")
            print(f"   @DOIT executed: {results.get('doit_executed', False)}")
            print(f"   Consolidation executed: {results.get('consolidation_executed', False)}")
            if results.get('chain_id'):
                print(f"   Chain ID: {results['chain_id']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()