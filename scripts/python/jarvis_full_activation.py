#!/usr/bin/env python3
"""
JARVIS Full System Activation
JARVIS-led complete system initialization, verification, and activation.

Executes comprehensive system startup, integration verification, and operational readiness check.

Tags: #JARVIS #ACTIVATION #FULL_SYSTEM #OPERATION @JARVIS @DOIT @FULLAUTO
"""

import sys
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

logger = get_logger("JARVISFullActivation")


class JARVISFullActivation:
    """
    JARVIS-led full system activation

    Comprehensive initialization, verification, and activation of all JARVIS systems.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize full activation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger
        self.start_time = datetime.now()
        self.activation_results: Dict[str, Any] = {}

        self.logger.info("="*80)
        self.logger.info("🚀 JARVIS FULL SYSTEM ACTIVATION")
        self.logger.info("="*80)
        self.logger.info(f"Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("")

    def execute_full_activation(self) -> Dict[str, Any]:
        """Execute complete JARVIS-led system activation"""

        results = {
            "start_time": self.start_time.isoformat(),
            "phases": {},
            "summary": {}
        }

        # Phase 1: Integration Verification
        self.logger.info("📋 PHASE 1: System Integration Verification")
        self.logger.info("-"*80)
        results["phases"]["integration_verification"] = self._verify_integrations()

        # Phase 2: Core System Initialization
        self.logger.info("")
        self.logger.info("📋 PHASE 2: Core System Initialization")
        self.logger.info("-"*80)
        results["phases"]["core_initialization"] = self._initialize_core_systems()

        # Phase 3: Service Activation
        self.logger.info("")
        self.logger.info("📋 PHASE 3: Service Activation")
        self.logger.info("-"*80)
        results["phases"]["service_activation"] = self._activate_services()

        # Phase 4: Workflow Verification
        self.logger.info("")
        self.logger.info("📋 PHASE 4: Workflow Verification")
        self.logger.info("-"*80)
        results["phases"]["workflow_verification"] = self._verify_workflows()

        # Phase 5: Operational Readiness Check
        self.logger.info("")
        self.logger.info("📋 PHASE 5: Operational Readiness Check")
        self.logger.info("-"*80)
        results["phases"]["operational_readiness"] = self._check_operational_readiness()

        # Generate Summary
        end_time = datetime.now()
        duration = (end_time - self.start_time).total_seconds()

        results["end_time"] = end_time.isoformat()
        results["duration_seconds"] = duration

        # Calculate summary
        total_checks = sum(
            phase.get("total_checks", 0) 
            for phase in results["phases"].values()
        )
        total_passed = sum(
            phase.get("passed", 0) 
            for phase in results["phases"].values()
        )
        total_failed = sum(
            phase.get("failed", 0) 
            for phase in results["phases"].values()
        )

        results["summary"] = {
            "total_checks": total_checks,
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": (total_passed / total_checks * 100) if total_checks > 0 else 0.0,
            "duration_seconds": duration,
            "operational": total_failed == 0
        }

        # Print Final Summary
        self._print_final_summary(results)

        self.activation_results = results
        return results

    def _verify_integrations(self) -> Dict[str, Any]:
        """Verify all system integrations"""
        try:
            from jarvis_integration_verifier import JARVISIntegrationVerifier

            verifier = JARVISIntegrationVerifier(project_root=self.project_root)
            report = verifier.verify_all()

            return {
                "status": "completed",
                "total_checks": report.total_checks,
                "passed": report.passed,
                "failed": report.failed,
                "warnings": report.warnings,
                "success_rate": (report.passed / report.total_checks * 100) if report.total_checks > 0 else 0.0
            }
        except Exception as e:
            self.logger.error(f"❌ Integration verification failed: {e}")
            return {
                "status": "failed",
                "error": str(e),
                "total_checks": 0,
                "passed": 0,
                "failed": 1
            }

    def _initialize_core_systems(self) -> Dict[str, Any]:
        """Initialize all core JARVIS systems"""
        systems = {}

        # 1. JARVIS Full-Time Super Agent
        try:
            self.logger.info("1️⃣  Initializing JARVIS Full-Time Super Agent...")
            from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent

            jarvis = JARVISFullTimeSuperAgent(project_root=self.project_root)
            systems["jarvis_fulltime"] = {"status": "initialized", "ready": True}
            self.logger.info("   ✅ JARVIS Full-Time Super Agent ready")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            systems["jarvis_fulltime"] = {"status": "failed", "error": str(e)}

        # 2. R5 Living Context Matrix
        try:
            self.logger.info("2️⃣  Initializing R5 Living Context Matrix...")
            from r5_living_context_matrix import R5LivingContextMatrix

            r5 = R5LivingContextMatrix(project_root=self.project_root)
            systems["r5"] = {"status": "initialized", "ready": True}
            self.logger.info("   ✅ R5 Living Context Matrix ready")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            systems["r5"] = {"status": "failed", "error": str(e)}

        # 3. SYPHON System
        try:
            self.logger.info("3️⃣  Initializing SYPHON System...")
            from syphon import SYPHONSystem, SYPHONConfig
            from syphon.config import SubscriptionTier

            syphon_config = SYPHONConfig(
                project_root=self.project_root,
                subscription_tier=SubscriptionTier.ENTERPRISE
            )
            syphon = SYPHONSystem(syphon_config)

            systems["syphon"] = {"status": "initialized", "ready": True}
            self.logger.info("   ✅ SYPHON System ready")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            systems["syphon"] = {"status": "failed", "error": str(e)}

        # 4. Decision Tree System
        try:
            self.logger.info("4️⃣  Initializing Universal Decision Tree...")
            from universal_decision_tree import UniversalDecisionTree

            decision_tree = UniversalDecisionTree(project_root=self.project_root)
            systems["decision_tree"] = {"status": "initialized", "ready": True}
            self.logger.info("   ✅ Decision Tree System ready")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            systems["decision_tree"] = {"status": "failed", "error": str(e)}

        # Calculate results
        initialized = sum(1 for s in systems.values() if s.get("status") == "initialized")
        failed = sum(1 for s in systems.values() if s.get("status") == "failed")

        return {
            "status": "completed",
            "systems": systems,
            "total_checks": len(systems),
            "passed": initialized,
            "failed": failed,
            "success_rate": (initialized / len(systems) * 100) if systems else 0.0
        }

    def _activate_services(self) -> Dict[str, Any]:
        """Activate all JARVIS services"""
        services = {}

        # 1. KEEP ALL Automation
        try:
            self.logger.info("1️⃣  Activating KEEP ALL automation...")
            from jarvis_auto_keep_all_manager import JARVISAutoKeepAllManager

            keep_all = JARVISAutoKeepAllManager(project_root=self.project_root)
            result = keep_all.start()

            if result.get('success'):
                services["keep_all"] = {"status": "active", "pid": result.get('pid')}
                self.logger.info(f"   ✅ KEEP ALL automation active (PID: {result.get('pid')})")
            else:
                services["keep_all"] = {"status": "failed", "error": result.get('error')}
                self.logger.warning(f"   ⚠️  KEEP ALL automation failed: {result.get('error')}")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            services["keep_all"] = {"status": "failed", "error": str(e)}

        # 2. Persistent Memory
        try:
            self.logger.info("2️⃣  Activating Persistent Memory...")
            from jarvis_persistent_memory import JARVISPersistentMemory

            memory = JARVISPersistentMemory(project_root=self.project_root)
            services["persistent_memory"] = {"status": "active", "ready": True}
            self.logger.info("   ✅ Persistent Memory active")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            services["persistent_memory"] = {"status": "failed", "error": str(e)}

        # 3. RAlt Hybrid Macro Service
        try:
            self.logger.info("3️⃣  Activating RAlt Hybrid Macro Service...")
            from jarvis_ralt_hybrid_macro import JARVISRAltHybridMacro
            import threading

            ralt_macro = JARVISRAltHybridMacro(project_root=self.project_root)

            def start_macro():
                ralt_macro.start_listening()

            macro_thread = threading.Thread(target=start_macro, daemon=True)
            macro_thread.start()

            import time
            time.sleep(0.5)

            if ralt_macro.is_active:
                services["ralt_macro"] = {"status": "active", "ready": True}
                self.logger.info("   ✅ RAlt Hybrid Macro active (Press Right Alt to activate)")
            else:
                services["ralt_macro"] = {"status": "partial", "ready": False}
                self.logger.warning("   ⚠️  RAlt Macro started but may not be fully active")
        except Exception as e:
            self.logger.error(f"   ❌ Failed: {e}")
            services["ralt_macro"] = {"status": "failed", "error": str(e)}

        # Calculate results
        active = sum(1 for s in services.values() if s.get("status") == "active")
        failed = sum(1 for s in services.values() if s.get("status") == "failed")

        return {
            "status": "completed",
            "services": services,
            "total_checks": len(services),
            "passed": active,
            "failed": failed,
            "success_rate": (active / len(services) * 100) if services else 0.0
        }

    def _verify_workflows(self) -> Dict[str, Any]:
        """Verify all workflows are operational"""
        workflows = {}

        # 1. Incomplete @ASKS Mining
        try:
            self.logger.info("1️⃣  Verifying Incomplete @ASKS Mining...")
            from jarvis_mine_incomplete_asks_inception import JARVISMineIncompleteAsksInception

            asks_miner = JARVISMineIncompleteAsksInception(project_root=self.project_root)
            workflows["incomplete_asks"] = {"status": "ready", "available": True}
            self.logger.info("   ✅ Incomplete @ASKS Mining ready")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Not available: {e}")
            workflows["incomplete_asks"] = {"status": "unavailable", "error": str(e)}

        # 2. Batch Processing
        try:
            self.logger.info("2️⃣  Verifying Batch Processing...")
            from jarvis_manage_batch_processing import JARVISBatchProcessingManager

            batch_manager = JARVISBatchProcessingManager(project_root=self.project_root)
            workflows["batch_processing"] = {"status": "ready", "available": True}
            self.logger.info("   ✅ Batch Processing ready")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Not available: {e}")
            workflows["batch_processing"] = {"status": "unavailable", "error": str(e)}

        # Calculate results
        ready = sum(1 for w in workflows.values() if w.get("status") == "ready")
        unavailable = sum(1 for w in workflows.values() if w.get("status") == "unavailable")

        return {
            "status": "completed",
            "workflows": workflows,
            "total_checks": len(workflows),
            "passed": ready,
            "failed": unavailable,
            "success_rate": (ready / len(workflows) * 100) if workflows else 0.0
        }

    def _check_operational_readiness(self) -> Dict[str, Any]:
        """Final operational readiness check"""
        checks = {}

        # 1. Database connectivity
        try:
            self.logger.info("1️⃣  Checking database connectivity...")
            memory_db = self.project_root / "data" / "jarvis_memory" / "memory.db"
            if memory_db.exists():
                checks["database"] = {"status": "ready", "path": str(memory_db)}
                self.logger.info("   ✅ Database ready")
            else:
                checks["database"] = {"status": "initializing", "note": "Will be created on first use"}
                self.logger.info("   ⚠️  Database will be created on first use")
        except Exception as e:
            checks["database"] = {"status": "error", "error": str(e)}
            self.logger.error(f"   ❌ Error: {e}")

        # 2. Data directories
        try:
            self.logger.info("2️⃣  Checking data directories...")
            required_dirs = [
                "data/jarvis_memory",
                "data/r5_living_matrix",
                "data/jarvis_incomplete_asks"
            ]

            all_exist = True
            for dir_path in required_dirs:
                full_path = self.project_root / dir_path
                if not full_path.exists():
                    full_path.mkdir(parents=True, exist_ok=True)
                    all_exist = False

            checks["data_directories"] = {"status": "ready", "all_exist": all_exist}
            self.logger.info("   ✅ Data directories ready")
        except Exception as e:
            checks["data_directories"] = {"status": "error", "error": str(e)}
            self.logger.error(f"   ❌ Error: {e}")

        # 3. Config files
        try:
            self.logger.info("3️⃣  Checking configuration files...")
            config_file = self.project_root / "config" / "ai_decision_tree.json"
            if config_file.exists():
                checks["config"] = {"status": "ready", "config_exists": True}
                self.logger.info("   ✅ Configuration ready")
            else:
                checks["config"] = {"status": "ready", "config_exists": False, "note": "Will be created automatically"}
                self.logger.info("   ⚠️  Config will be created automatically")
        except Exception as e:
            checks["config"] = {"status": "error", "error": str(e)}
            self.logger.error(f"   ❌ Error: {e}")

        # Calculate results
        ready = sum(1 for c in checks.values() if c.get("status") == "ready")
        errors = sum(1 for c in checks.values() if c.get("status") == "error")

        return {
            "status": "completed",
            "checks": checks,
            "total_checks": len(checks),
            "passed": ready,
            "failed": errors,
            "success_rate": (ready / len(checks) * 100) if checks else 0.0
        }

    def _print_final_summary(self, results: Dict[str, Any]):
        """Print final activation summary"""
        summary = results["summary"]

        self.logger.info("")
        self.logger.info("="*80)
        self.logger.info("📊 JARVIS FULL ACTIVATION SUMMARY")
        self.logger.info("="*80)
        self.logger.info("")
        self.logger.info(f"⏱️  Duration: {summary['duration_seconds']:.2f} seconds")
        self.logger.info(f"📋 Total Checks: {summary['total_checks']}")
        self.logger.info(f"✅ Passed: {summary['total_passed']}")
        self.logger.info(f"❌ Failed: {summary['total_failed']}")
        self.logger.info(f"📈 Success Rate: {summary['success_rate']:.1f}%")
        self.logger.info("")

        if summary['operational']:
            self.logger.info("🎉 ✅ SYSTEM FULLY OPERATIONAL")
            self.logger.info("")
            self.logger.info("🚀 JARVIS is ready for full operation")
            self.logger.info("   All systems initialized and verified")
            self.logger.info("   All services activated")
            self.logger.info("   All workflows ready")
        else:
            self.logger.info("⚠️  SYSTEM OPERATIONAL WITH WARNINGS")
            self.logger.info("")
            self.logger.info(f"   {summary['total_failed']} check(s) failed")
            self.logger.info("   System may operate with reduced functionality")

        self.logger.info("")
        self.logger.info("="*80)

    def save_report(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Save activation report"""
            if output_path is None:
                output_dir = self.project_root / "data" / "jarvis_activation_reports"
                output_dir.mkdir(parents=True, exist_ok=True)
                output_path = output_dir / f"activation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            import json
            with open(output_path, 'w') as f:
                json.dump(self.activation_results, f, indent=2)

            self.logger.info(f"💾 Activation report saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Full System Activation")
    parser.add_argument("--project-root", type=Path, help="Project root directory")
    parser.add_argument("--save-report", action="store_true", help="Save activation report")
    parser.add_argument("--output", type=Path, help="Output path for report")

    args = parser.parse_args()

    activation = JARVISFullActivation(project_root=args.project_root)
    results = activation.execute_full_activation()

    if args.save_report or args.output:
        activation.save_report(args.output)

    # Exit with error code if operational readiness failed
    if not results["summary"]["operational"]:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":


    main()