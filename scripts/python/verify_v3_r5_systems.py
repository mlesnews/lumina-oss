#!/usr/bin/env python3
"""
Verify, Validate, and Reverify @v3 and @r5 Systems
Tests post creation, logins, API endpoints, and system health
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from v3_verification import V3Verification, V3VerificationConfig, VerificationResult
    V3_AVAILABLE = True
except ImportError as e:
    V3_AVAILABLE = False
    print(f"WARNING: V3 not available: {e}")

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError as e:
    R5_AVAILABLE = False
    print(f"WARNING: R5 not available: {e}")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("WARNING: requests not available for API testing")

try:
    from lumina_core.logging import get_logger
    logger = get_logger("V3R5Verification")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3R5Verification")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class V3R5SystemVerifier:
    """Verify, validate, and reverify @v3 and @r5 systems"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize verifier"""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.results: List[Dict[str, Any]] = []

    def verify_v3_system(self) -> Dict[str, Any]:
        """Verify V3 verification system"""
        result = {
            "system": "V3",
            "status": "unknown",
            "tests": [],
            "errors": []
        }

        if not V3_AVAILABLE:
            result["status"] = "unavailable"
            result["errors"].append("V3 module not importable")
            return result

        try:
            # Test 1: Import and initialization
            verifier = V3Verification()
            result["tests"].append({
                "test": "V3 Import and Initialization",
                "status": "PASSED",
                "message": "V3 system initialized successfully"
            })

            # Test 2: Workflow verification
            test_workflow = {
                "workflow_id": f"verify_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "workflow_name": "V3 Verification Test",
                "steps": [{"step": 1, "action": "verify"}],
                "config": {}
            }

            passed, verification_results = verifier.run_full_verification(test_workflow)
            result["tests"].append({
                "test": "Workflow Verification",
                "status": "PASSED" if passed else "FAILED",
                "message": f"Verification {'passed' if passed else 'failed'}",
                "details": {
                    "total_steps": len(verification_results),
                    "passed_steps": sum(1 for r in verification_results if r.passed),
                    "failed_steps": sum(1 for r in verification_results if not r.passed)
                }
            })

            # Test 3: Data integrity verification
            data_result = verifier.verify_data_integrity(test_workflow, "test_workflow")
            result["tests"].append({
                "test": "Data Integrity Verification",
                "status": "PASSED" if data_result.passed else "FAILED",
                "message": data_result.message
            })

            # Test 4: Aggregation preconditions
            test_sessions = [
                {
                    "session_id": "test_session_1",
                    "timestamp": datetime.now().isoformat(),
                    "messages": [{"role": "user", "content": "test"}]
                }
            ]
            agg_result = verifier.verify_aggregation_preconditions(test_sessions)
            result["tests"].append({
                "test": "Aggregation Preconditions",
                "status": "PASSED" if agg_result.passed else "FAILED",
                "message": agg_result.message
            })

            result["status"] = "operational" if all(t["status"] == "PASSED" for t in result["tests"]) else "degraded"

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"V3 verification error: {e}")
            logger.error(f"V3 verification error: {e}")

        return result

    def verify_r5_system(self) -> Dict[str, Any]:
        """Verify R5 system"""
        result = {
            "system": "R5",
            "status": "unknown",
            "tests": [],
            "errors": []
        }

        if not R5_AVAILABLE:
            result["status"] = "unavailable"
            result["errors"].append("R5 module not importable")
            return result

        try:
            # Test 1: Import and initialization
            r5 = R5LivingContextMatrix(self.project_root)
            result["tests"].append({
                "test": "R5 Import and Initialization",
                "status": "PASSED",
                "message": "R5 system initialized successfully",
                "details": {
                    "data_directory": str(r5.config.data_directory),
                    "output_file": str(r5.config.output_file)
                }
            })

            # Test 2: Session creation (POST)
            test_session = {
                "session_id": f"verify_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "user", "content": "Test message for verification"},
                    {"role": "assistant", "content": "Test response"}
                ],
                "metadata": {
                    "verification_test": True,
                    "test_timestamp": datetime.now().isoformat()
                }
            }

            session_id = r5.ingest_session(test_session)
            result["tests"].append({
                "test": "R5 Session Creation (POST)",
                "status": "PASSED",
                "message": f"Session created successfully: {session_id}",
                "details": {
                    "session_id": session_id,
                    "message_count": len(test_session["messages"])
                }
            })

            # Test 3: Session aggregation
            aggregated = r5.aggregate_sessions()
            result["tests"].append({
                "test": "R5 Session Aggregation",
                "status": "PASSED",
                "message": "Sessions aggregated successfully",
                "details": {
                    "total_sessions": aggregated.get("total_sessions", 0),
                    "total_messages": aggregated.get("total_messages", 0)
                }
            })

            # Test 4: Check data directory
            sessions_dir = r5.config.data_directory / "sessions"
            session_files = list(sessions_dir.glob("*.json")) if sessions_dir.exists() else []
            result["tests"].append({
                "test": "R5 Data Directory",
                "status": "PASSED" if sessions_dir.exists() else "FAILED",
                "message": f"Data directory {'exists' if sessions_dir.exists() else 'missing'}",
                "details": {
                    "sessions_directory": str(sessions_dir),
                    "session_files_count": len(session_files)
                }
            })

            # Test 5: Check output file
            output_file = r5.config.output_file
            result["tests"].append({
                "test": "R5 Output File",
                "status": "PASSED" if output_file.exists() else "WARNING",
                "message": f"Output file {'exists' if output_file.exists() else 'not found'}",
                "details": {
                    "output_file": str(output_file),
                    "file_size": output_file.stat().st_size if output_file.exists() else 0
                }
            })

            result["status"] = "operational" if all(t["status"] == "PASSED" for t in result["tests"]) else "degraded"

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"R5 verification error: {e}")
            logger.error(f"R5 verification error: {e}")

        return result

    def verify_r5_api(self, api_url: str = "http://localhost:8000") -> Dict[str, Any]:
        """Verify R5 API endpoints"""
        result = {
            "system": "R5 API",
            "status": "unknown",
            "tests": [],
            "errors": []
        }

        if not REQUESTS_AVAILABLE:
            result["status"] = "unavailable"
            result["errors"].append("requests library not available")
            return result

        try:
            # Test 1: Health check
            try:
                response = requests.get(f"{api_url}/r5/health", timeout=5)
                if response.status_code == 200:
                    result["tests"].append({
                        "test": "R5 API Health Check",
                        "status": "PASSED",
                        "message": "API server is running",
                        "details": response.json()
                    })
                else:
                    result["tests"].append({
                        "test": "R5 API Health Check",
                        "status": "FAILED",
                        "message": f"Unexpected status: {response.status_code}"
                    })
            except requests.exceptions.ConnectionError:
                result["tests"].append({
                    "test": "R5 API Health Check",
                    "status": "FAILED",
                    "message": "API server not running (connection refused)"
                })
                result["status"] = "unavailable"
                return result
            except Exception as e:
                result["tests"].append({
                    "test": "R5 API Health Check",
                    "status": "ERROR",
                    "message": f"Error: {e}"
                })

            # Test 2: POST session (post creation)
            test_session = {
                "session_id": f"api_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "messages": [
                    {"role": "user", "content": "API test message"},
                    {"role": "assistant", "content": "API test response"}
                ],
                "metadata": {"api_test": True}
            }

            try:
                response = requests.post(
                    f"{api_url}/r5/session",
                    json=test_session,
                    timeout=10
                )
                if response.status_code == 201:
                    result["tests"].append({
                        "test": "R5 API POST Session (Post Creation)",
                        "status": "PASSED",
                        "message": "Session created via API",
                        "details": response.json()
                    })
                else:
                    result["tests"].append({
                        "test": "R5 API POST Session",
                        "status": "FAILED",
                        "message": f"Unexpected status: {response.status_code}",
                        "details": response.text
                    })
            except Exception as e:
                result["tests"].append({
                    "test": "R5 API POST Session",
                    "status": "ERROR",
                    "message": f"Error: {e}"
                })

            # Test 3: GET aggregate
            try:
                response = requests.get(f"{api_url}/r5/aggregate", timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    result["tests"].append({
                        "test": "R5 API GET Aggregate",
                        "status": "PASSED",
                        "message": "Aggregation successful",
                        "details": {
                            "success": data.get("success"),
                            "total_sessions": data.get("data", {}).get("total_sessions", 0)
                        }
                    })
                else:
                    result["tests"].append({
                        "test": "R5 API GET Aggregate",
                        "status": "FAILED",
                        "message": f"Unexpected status: {response.status_code}"
                    })
            except Exception as e:
                result["tests"].append({
                    "test": "R5 API GET Aggregate",
                    "status": "ERROR",
                    "message": f"Error: {e}"
                })

            # Test 4: GET stats
            try:
                response = requests.get(f"{api_url}/r5/stats", timeout=5)
                if response.status_code == 200:
                    result["tests"].append({
                        "test": "R5 API GET Stats",
                        "status": "PASSED",
                        "message": "Stats retrieved successfully",
                        "details": response.json()
                    })
                else:
                    result["tests"].append({
                        "test": "R5 API GET Stats",
                        "status": "FAILED",
                        "message": f"Unexpected status: {response.status_code}"
                    })
            except Exception as e:
                result["tests"].append({
                    "test": "R5 API GET Stats",
                    "status": "ERROR",
                    "message": f"Error: {e}"
                })

            # Note: No authentication endpoints found
            result["tests"].append({
                "test": "R5 API Authentication",
                "status": "INFO",
                "message": "No authentication/login endpoints found - API is open (local network only)"
            })

            result["status"] = "operational" if all(
                t["status"] in ["PASSED", "INFO"] for t in result["tests"]
            ) else "degraded"

        except Exception as e:
            result["status"] = "error"
            result["errors"].append(f"R5 API verification error: {e}")
            logger.error(f"R5 API verification error: {e}")

        return result

    def run_full_verification(self, test_api: bool = True) -> Dict[str, Any]:
        """Run full verification suite"""
        logger.info("=" * 60)
        logger.info("V3 & R5 System Verification")
        logger.info("=" * 60)

        results = {
            "timestamp": datetime.now().isoformat(),
            "v3": self.verify_v3_system(),
            "r5": self.verify_r5_system()
        }

        if test_api:
            results["r5_api"] = self.verify_r5_api()

        # Summary
        all_operational = all(
            r.get("status") == "operational" 
            for r in [results["v3"], results["r5"], results.get("r5_api", {})]
            if r.get("status") != "unavailable"
        )

        results["summary"] = {
            "all_operational": all_operational,
            "v3_status": results["v3"]["status"],
            "r5_status": results["r5"]["status"],
            "r5_api_status": results.get("r5_api", {}).get("status", "not_tested")
        }

        self.results.append(results)
        return results


def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Verify V3 and R5 systems")
        parser.add_argument("--no-api", action="store_true", help="Skip API testing")
        parser.add_argument("--api-url", default="http://localhost:8000", help="R5 API URL")
        parser.add_argument("--output", help="Output JSON file for results")

        args = parser.parse_args()

        verifier = V3R5SystemVerifier()
        results = verifier.run_full_verification(test_api=not args.no_api)

        # Print summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        print(f"V3 Status: {results['v3']['status']}")
        print(f"R5 Status: {results['r5']['status']}")
        if 'r5_api' in results:
            print(f"R5 API Status: {results['r5_api']['status']}")
        print(f"All Operational: {results['summary']['all_operational']}")
        print("\nDetailed Results:")

        for system_name, system_result in [("V3", results["v3"]), ("R5", results["r5"])]:
            print(f"\n{system_name}:")
            for test in system_result.get("tests", []):
                status_symbol = "[OK]" if test["status"] == "PASSED" else "[FAIL]" if test["status"] == "FAILED" else "[!]"
                print(f"  {status_symbol} {test['test']}: {test['message']}")

        if "r5_api" in results:
            system_result = results["r5_api"]
            print(f"\nR5 API:")
            for test in system_result.get("tests", []):
                status_symbol = "[OK]" if test["status"] == "PASSED" else "[FAIL]" if test["status"] == "FAILED" else "[!]"
                print(f"  {status_symbol} {test['test']}: {test['message']}")
            if system_result.get("errors"):
                print("  Errors:")
                for error in system_result["errors"]:
                    print(f"    - {error}")

        # Save results if requested
        if args.output:
            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)
            print(f"\nResults saved to: {args.output}")

        return 0 if results['summary']['all_operational'] else 1


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    sys.exit(main())