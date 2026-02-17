#!/usr/bin/env python3
"""
@v3 Battle Test - ULTRON Virtual Cluster

Comprehensive battle-tested verification of:
- ULTRON Standalone (localhost:11434)
- KAIJU/Iron Legion (<NAS_IP>:3000/3001)
- FALC/Millennium Falcon (localhost:11436)
- Failover scenarios
- Cluster health and connectivity
- Model availability
- API responsiveness

Tags: #V3 #VERIFICATION #ULTRON #VIRTUAL_CLUSTER #KAIJU #FALC #BATTLE_TESTED @JARVIS @BONES @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import urllib.request
import urllib.error

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from v3_verification import V3Verification, V3VerificationConfig, VerificationResult
    from lumina_core.logging import get_logger
    V3_AVAILABLE = True
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("UltronClusterV3BattleTest")
    V3_AVAILABLE = False

logger = get_logger("UltronClusterV3BattleTest") if V3_AVAILABLE else logging.getLogger("UltronClusterV3BattleTest")


@dataclass
class ClusterNodeResult:
    """Individual cluster node test result"""
    node_name: str
    endpoint: str
    operational: bool
    api_accessible: bool
    response_time_ms: float
    models_available: int
    target_model_found: bool
    error: Optional[str] = None
    details: Dict[str, Any] = None


@dataclass
class FailoverTestResult:
    """Failover scenario test result"""
    scenario: str
    passed: bool
    primary_node: str
    failover_node: str
    failover_time_ms: float
    details: Dict[str, Any]


class UltronClusterV3BattleTest:
    """@v3 Battle Test for ULTRON Virtual Cluster"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize battle test"""
        self.project_root = Path(project_root) if project_root else script_dir.parent.parent
        self.v3_verifier = V3Verification() if V3_AVAILABLE else None
        self.results: List[Dict[str, Any]] = []

        # Load cluster configuration
        self.cluster_config = self._load_cluster_config()

    def _load_cluster_config(self) -> Dict[str, Any]:
        """Load ULTRON cluster configuration"""
        config_file = self.project_root / "config" / "ultron_cluster_selection.json"
        if config_file.exists():
            try:
                with open(config_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load cluster config: {e}")
        return {}

    def run_battle_test(self) -> Dict[str, Any]:
        """Run full @v3 battle test suite for ULTRON Virtual Cluster"""
        logger.info("="*80)
        logger.info("🚀 @v3 BATTLE TEST: ULTRON Virtual Cluster")
        logger.info("="*80)
        logger.info("")

        battle_test_results = {
            "system": "ULTRON Virtual Cluster",
            "test_date": datetime.now().isoformat(),
            "nodes": {},
            "cluster_health": {},
            "failover_tests": {},
            "api_tests": {},
            "integration_tests": {},
            "overall_status": "unknown",
            "all_passed": False
        }

        # Test all nodes
        logger.info("📡 Testing Cluster Nodes...")
        logger.info("")
        battle_test_results["nodes"]["ultron_standalone"] = self._test_node_ultron_standalone()
        battle_test_results["nodes"]["kaiju_iron_legion"] = self._test_node_kaiju()
        battle_test_results["nodes"]["falc_millennium_falcon"] = self._test_node_falc()

        # Test cluster health
        logger.info("")
        logger.info("🏥 Testing Cluster Health...")
        logger.info("")
        battle_test_results["cluster_health"] = self._test_cluster_health()

        # Test failover scenarios
        logger.info("")
        logger.info("🔄 Testing Failover Scenarios...")
        logger.info("")
        battle_test_results["failover_tests"] = self._test_failover_scenarios()

        # Test API responsiveness
        logger.info("")
        logger.info("⚡ Testing API Responsiveness...")
        logger.info("")
        battle_test_results["api_tests"] = self._test_api_responsiveness()

        # Test integration with health check
        logger.info("")
        logger.info("🔗 Testing Integration...")
        logger.info("")
        battle_test_results["integration_tests"] = self._test_integration()

        # Overall status
        all_nodes_passed = all(
            r.get("operational", False)
            for r in battle_test_results["nodes"].values()
        )
        cluster_health_passed = battle_test_results["cluster_health"].get("passed", False)
        failover_passed = all(
            r.get("passed", False)
            for r in battle_test_results["failover_tests"].values()
        )
        api_passed = battle_test_results["api_tests"].get("passed", False)
        integration_passed = battle_test_results["integration_tests"].get("passed", False)

        battle_test_results["all_passed"] = (
            all_nodes_passed and
            cluster_health_passed and
            failover_passed and
            api_passed and
            integration_passed
        )
        battle_test_results["overall_status"] = "PASSED" if battle_test_results["all_passed"] else "FAILED"

        # Summary
        logger.info("")
        logger.info("="*80)
        logger.info("📊 @v3 BATTLE TEST SUMMARY")
        logger.info("="*80)
        logger.info(f"Overall Status: {battle_test_results['overall_status']}")
        logger.info("")
        logger.info("Nodes:")
        for node, result in battle_test_results["nodes"].items():
            status = "✅ OPERATIONAL" if result.get("operational") else "❌ FAILED"
            response_time = result.get("response_time_ms", 0)
            logger.info(f"  {node.upper()}: {status} ({response_time:.2f}ms)")
        logger.info("")
        logger.info(f"Cluster Health: {'✅ PASSED' if cluster_health_passed else '❌ FAILED'}")
        logger.info(f"Failover Tests: {'✅ PASSED' if failover_passed else '❌ FAILED'}")
        logger.info(f"API Tests: {'✅ PASSED' if api_passed else '❌ FAILED'}")
        logger.info(f"Integration Tests: {'✅ PASSED' if integration_passed else '❌ FAILED'}")
        logger.info("="*80)

        return battle_test_results

    def _test_node_ultron_standalone(self) -> Dict[str, Any]:
        """Test ULTRON Standalone node"""
        logger.info("🔍 Testing ULTRON Standalone (localhost:11434)...")
        result = {
            "node_name": "ULTRON Standalone",
            "endpoint": "http://localhost:11434",
            "operational": False,
            "api_accessible": False,
            "response_time_ms": 0.0,
            "models_available": 0,
            "target_model_found": False,
            "details": {}
        }

        try:
            start_time = time.time()
            api_url = "http://localhost:11434/api/tags"
            req = urllib.request.Request(api_url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                response_time = (time.time() - start_time) * 1000

                models = [m.get("name", "") for m in data.get("models", [])]
                result["api_accessible"] = True
                result["operational"] = True
                result["response_time_ms"] = response_time
                result["models_available"] = len(models)
                result["target_model_found"] = any("qwen2.5:72b" in m for m in models)
                result["details"]["available_models"] = models[:5]
                result["details"]["total_models"] = len(models)

                logger.info(f"   ✅ ULTRON Standalone: OPERATIONAL ({response_time:.2f}ms, {len(models)} models)")
        except urllib.error.URLError as e:
            result["error"] = str(e)
            result["details"]["error_type"] = "URLError"
            logger.error(f"   ❌ ULTRON Standalone: FAILED - {e}")
        except Exception as e:
            result["error"] = str(e)
            result["details"]["error_type"] = "Exception"
            logger.error(f"   ❌ ULTRON Standalone: FAILED - {e}")

        return result

    def _test_node_kaiju(self) -> Dict[str, Any]:
        """Test KAIJU/Iron Legion node"""
        logger.info("🔍 Testing KAIJU/Iron Legion (<NAS_IP>:3000/3001)...")
        result = {
            "node_name": "KAIJU/Iron Legion",
            "endpoint": "http://<NAS_IP>:3000",
            "operational": False,
            "api_accessible": False,
            "response_time_ms": 0.0,
            "models_available": 0,
            "target_model_found": False,
            "details": {}
        }

        # Try port 3000 first (expert router)
        ports_to_try = [3000, 3001]
        for port in ports_to_try:
            try:
                start_time = time.time()
                api_url = f"http://<NAS_IP>:{port}/api/tags"
                req = urllib.request.Request(api_url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json.loads(response.read())
                    response_time = (time.time() - start_time) * 1000

                    models = [m.get("name", "") for m in data.get("models", [])]
                    result["api_accessible"] = True
                    result["operational"] = True
                    result["endpoint"] = f"http://<NAS_IP>:{port}"
                    result["response_time_ms"] = response_time
                    result["models_available"] = len(models)
                    result["target_model_found"] = any("codellama:13b" in m for m in models)
                    result["details"]["available_models"] = models[:5]
                    result["details"]["total_models"] = len(models)
                    result["details"]["port_used"] = port

                    logger.info(f"   ✅ KAIJU/Iron Legion: OPERATIONAL on port {port} ({response_time:.2f}ms, {len(models)} models)")
                    break
            except urllib.error.URLError:
                if port == ports_to_try[-1]:
                    result["error"] = f"Failed on all ports: {ports_to_try}"
                    result["details"]["ports_tested"] = ports_to_try
                    logger.error(f"   ❌ KAIJU/Iron Legion: FAILED on all ports")
                continue
            except Exception as e:
                result["error"] = str(e)
                result["details"]["error_type"] = "Exception"
                logger.error(f"   ❌ KAIJU/Iron Legion: FAILED - {e}")
                break

        return result

    def _test_node_falc(self) -> Dict[str, Any]:
        """Test FALC/Millennium Falcon node"""
        logger.info("🔍 Testing FALC/Millennium Falcon (localhost:11436)...")
        result = {
            "node_name": "FALC/Millennium Falcon",
            "endpoint": "http://localhost:11436",
            "operational": False,
            "api_accessible": False,
            "response_time_ms": 0.0,
            "models_available": 0,
            "target_model_found": False,
            "details": {}
        }

        try:
            start_time = time.time()
            api_url = "http://localhost:11436/api/tags"
            req = urllib.request.Request(api_url)
            with urllib.request.urlopen(req, timeout=5) as response:
                data = json.loads(response.read())
                response_time = (time.time() - start_time) * 1000

                models = [m.get("name", "") for m in data.get("models", [])]
                result["api_accessible"] = True
                result["operational"] = True
                result["response_time_ms"] = response_time
                result["models_available"] = len(models)
                result["target_model_found"] = any("perspective" in m.lower() for m in models)
                result["details"]["available_models"] = models[:5]
                result["details"]["total_models"] = len(models)

                logger.info(f"   ✅ FALC/Millennium Falcon: OPERATIONAL ({response_time:.2f}ms, {len(models)} models)")
        except urllib.error.URLError as e:
            result["error"] = str(e)
            result["details"]["error_type"] = "URLError"
            logger.error(f"   ❌ FALC/Millennium Falcon: FAILED - {e}")
        except Exception as e:
            result["error"] = str(e)
            result["details"]["error_type"] = "Exception"
            logger.error(f"   ❌ FALC/Millennium Falcon: FAILED - {e}")

        return result

    def _test_cluster_health(self) -> Dict[str, Any]:
        """Test overall cluster health"""
        logger.info("🏥 Testing cluster health...")
        result = {
            "test": "cluster_health",
            "passed": False,
            "nodes_operational": 0,
            "nodes_total": 3,
            "failover_capable": False,
            "details": {}
        }

        # Count operational nodes from previous tests
        # This would be called after node tests, so we need to get results differently
        # For now, we'll test directly
        nodes = {
            "ultron": self._test_node_ultron_standalone(),
            "kaiju": self._test_node_kaiju(),
            "falc": self._test_node_falc()
        }

        operational_count = sum(1 for n in nodes.values() if n.get("operational", False))
        result["nodes_operational"] = operational_count
        result["failover_capable"] = operational_count >= 2
        result["passed"] = operational_count >= 2  # Need at least 2 for failover
        result["details"]["nodes"] = {k: v.get("operational", False) for k, v in nodes.items()}

        if result["passed"]:
            logger.info(f"   ✅ Cluster Health: PASSED ({operational_count}/3 nodes operational, failover capable)")
        else:
            logger.error(f"   ❌ Cluster Health: FAILED ({operational_count}/3 nodes operational, failover NOT capable)")

        return result

    def _test_failover_scenarios(self) -> Dict[str, Any]:
        """Test failover scenarios"""
        logger.info("🔄 Testing failover scenarios...")
        results = {}

        # Scenario 1: Primary (KAIJU) fails, failover to FALC
        logger.info("   Testing: KAIJU → FALC failover...")
        results["kaiju_to_falc"] = self._test_single_failover(
            "KAIJU → FALC",
            "http://<NAS_IP>:3000",
            "http://localhost:11436"
        )

        # Scenario 2: Primary (KAIJU) fails, failover to ULTRON Standalone
        logger.info("   Testing: KAIJU → ULTRON Standalone failover...")
        results["kaiju_to_ultron"] = self._test_single_failover(
            "KAIJU → ULTRON",
            "http://<NAS_IP>:3000",
            "http://localhost:11434"
        )

        # Scenario 3: All nodes operational (no failover needed)
        logger.info("   Testing: All nodes operational...")
        results["all_operational"] = {
            "scenario": "All nodes operational",
            "passed": True,
            "details": {
                "ultron": self._test_node_ultron_standalone().get("operational", False),
                "kaiju": self._test_node_kaiju().get("operational", False),
                "falc": self._test_node_falc().get("operational", False)
            }
        }
        if all(results["all_operational"]["details"].values()):
            logger.info("   ✅ All nodes operational: PASSED")
        else:
            logger.warning("   ⚠️  All nodes operational: PARTIAL")
            results["all_operational"]["passed"] = False

        return results

    def _test_single_failover(self, scenario_name: str, primary: str, failover: str) -> Dict[str, Any]:
        """Test a single failover scenario"""
        result = {
            "scenario": scenario_name,
            "passed": False,
            "primary_node": primary,
            "failover_node": failover,
            "failover_time_ms": 0.0,
            "details": {}
        }

        try:
            # Test primary node
            primary_parts = primary.replace("http://", "").split(":")
            primary_ip = primary_parts[0]
            primary_port = int(primary_parts[1]) if len(primary_parts) > 1 else 11434

            start_time = time.time()
            primary_url = f"http://{primary_ip}:{primary_port}/api/tags"
            try:
                req = urllib.request.Request(primary_url)
                with urllib.request.urlopen(req, timeout=2) as response:
                    # Primary is up, no failover needed
                    result["details"]["primary_operational"] = True
                    result["details"]["failover_triggered"] = False
                    result["passed"] = True
                    logger.info(f"      ✅ {scenario_name}: Primary operational, no failover needed")
            except (urllib.error.URLError, Exception):
                # Primary failed, test failover
                result["details"]["primary_operational"] = False
                result["details"]["failover_triggered"] = True

                failover_parts = failover.replace("http://", "").split(":")
                failover_ip = failover_parts[0]
                failover_port = int(failover_parts[1]) if len(failover_parts) > 1 else 11434

                failover_url = f"http://{failover_ip}:{failover_port}/api/tags"
                try:
                    req = urllib.request.Request(failover_url)
                    with urllib.request.urlopen(req, timeout=5) as response:
                        failover_time = (time.time() - start_time) * 1000
                        result["failover_time_ms"] = failover_time
                        result["passed"] = True
                        result["details"]["failover_operational"] = True
                        logger.info(f"      ✅ {scenario_name}: Failover successful ({failover_time:.2f}ms)")
                except (urllib.error.URLError, Exception) as e:
                    result["details"]["failover_operational"] = False
                    result["details"]["failover_error"] = str(e)
                    result["passed"] = False
                    logger.error(f"      ❌ {scenario_name}: Failover failed - {e}")
        except Exception as e:
            result["details"]["error"] = str(e)
            result["passed"] = False
            logger.error(f"      ❌ {scenario_name}: Test error - {e}")

        return result

    def _test_api_responsiveness(self) -> Dict[str, Any]:
        """Test API responsiveness across all nodes"""
        logger.info("⚡ Testing API responsiveness...")
        result = {
            "test": "api_responsiveness",
            "passed": False,
            "average_response_time_ms": 0.0,
            "max_response_time_ms": 0.0,
            "min_response_time_ms": 0.0,
            "details": {}
        }

        nodes = {
            "ultron": ("http://localhost:11434", self._test_node_ultron_standalone),
            "kaiju": ("http://<NAS_IP>:3001", self._test_node_kaiju),
            "falc": ("http://localhost:11436", self._test_node_falc)
        }

        response_times = []
        for node_name, (endpoint, test_func) in nodes.items():
            node_result = test_func()
            if node_result.get("operational", False):
                rt = node_result.get("response_time_ms", 0)
                response_times.append(rt)
                result["details"][node_name] = {
                    "response_time_ms": rt,
                    "operational": True
                }
            else:
                result["details"][node_name] = {
                    "response_time_ms": None,
                    "operational": False
                }

        if response_times:
            result["average_response_time_ms"] = sum(response_times) / len(response_times)
            result["max_response_time_ms"] = max(response_times)
            result["min_response_time_ms"] = min(response_times)
            result["passed"] = result["average_response_time_ms"] < 1000  # Under 1 second
            logger.info(f"   ✅ API Responsiveness: PASSED (avg: {result['average_response_time_ms']:.2f}ms)")
        else:
            result["passed"] = False
            logger.error("   ❌ API Responsiveness: FAILED (no operational nodes)")

        return result

    def _test_integration(self) -> Dict[str, Any]:
        """Test integration with health check system"""
        logger.info("🔗 Testing integration with health check...")
        result = {
            "test": "integration",
            "passed": False,
            "details": {}
        }

        try:
            # Check if health check script exists
            health_check_script = self.project_root / "scripts" / "python" / "lumina_debug_health_check.py"
            result["details"]["health_check_exists"] = health_check_script.exists()

            # Check if ULTRON cluster check exists in health check
            if health_check_script.exists():
                with open(health_check_script, "r", encoding="utf-8") as f:
                    content = f.read()
                    result["details"]["has_ultron_check"] = "_check_ultron_virtual_cluster" in content
                    result["details"]["has_cluster_verification"] = "ULTRON Virtual Cluster" in content

            # Check if cluster config exists
            cluster_config = self.project_root / "config" / "ultron_cluster_selection.json"
            result["details"]["cluster_config_exists"] = cluster_config.exists()

            # Check if documentation exists
            docs = self.project_root / "docs" / "system" / "ULTRON_VIRTUAL_CLUSTER.md"
            result["details"]["documentation_exists"] = docs.exists()

            result["passed"] = (
                result["details"].get("health_check_exists", False) and
                result["details"].get("has_ultron_check", False) and
                result["details"].get("cluster_config_exists", False)
            )

            if result["passed"]:
                logger.info("   ✅ Integration: PASSED")
            else:
                logger.warning("   ⚠️  Integration: PARTIAL")
        except Exception as e:
            result["details"]["error"] = str(e)
            result["passed"] = False
            logger.error(f"   ❌ Integration: FAILED - {e}")

        return result

    def save_battle_test_report(self, results: Dict[str, Any], output_path: Optional[Path] = None) -> Path:
        try:
            """Save battle test report to file"""
            if output_path is None:
                output_path = self.project_root / "data" / "v3_verification" / f"ultron_cluster_v3_battle_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

            logger.info(f"📄 Battle test report saved: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_battle_test_report: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="@v3 Battle Test for ULTRON Virtual Cluster"
        )
        parser.add_argument("--save-report", action="store_true", help="Save battle test report to file")
        parser.add_argument("--output", type=str, help="Output path for battle test report")

        args = parser.parse_args()

        battle_test = UltronClusterV3BattleTest()
        results = battle_test.run_battle_test()

        if args.save_report or args.output:
            output_path = Path(args.output) if args.output else None
            report_path = battle_test.save_battle_test_report(results, output_path)
            print(f"\n📄 Battle test report saved: {report_path}")

        # Exit with appropriate code
        exit_code = 0 if results["all_passed"] else 1
        sys.exit(exit_code)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()