#!/usr/bin/env python3
"""
Diagnose Retry Manager Issue - Network Team Analysis

Analyzes retry manager issues and works with network/support teams to isolate root cause.
Request ID: 3d734a5e-9008-439c-9773-5334ef81a4db

Tags: #RETRY_MANAGER #DIAGNOSTIC #NETWORK #TROUBLESHOOTING @JARVIS @LUMINA
"""

import sys
import json
import traceback
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RetryManagerDiagnostic")

REQUEST_ID = "3d734a5e-9008-439c-9773-5334ef81a4db"


class RetryManagerDiagnostic:
    """
    Diagnostic tool for retry manager issues

    Works with network team and support teams to isolate root cause.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize diagnostic tool"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "retry_manager_diagnostics"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        logger.info("✅ Retry Manager Diagnostic initialized")
        logger.info(f"   Request ID: {REQUEST_ID}")

    def check_retry_manager_config(self) -> Dict[str, Any]:
        """Check retry manager configuration"""
        logger.info("🔍 Checking retry manager configuration...")

        try:
            from cursor_chat_retry_manager import CursorChatRetryManager, RetryStrategy

            manager = CursorChatRetryManager()

            config = {
                "max_retries": manager.max_retries,
                "initial_delay": manager.initial_delay,
                "max_delay": manager.max_delay,
                "strategy": manager.strategy.value,
                "status": "configured"
            }

            logger.info(f"   ✅ Max retries: {config['max_retries']}")
            logger.info(f"   ✅ Initial delay: {config['initial_delay']}s")
            logger.info(f"   ✅ Max delay: {config['max_delay']}s")
            logger.info(f"   ✅ Strategy: {config['strategy']}")

            return config

        except Exception as e:
            logger.error(f"   ❌ Error checking config: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def check_network_connectivity(self) -> Dict[str, Any]:
        """Check network connectivity (for network team)"""
        logger.info("🌐 Checking network connectivity...")

        results = {
            "timestamp": datetime.now().isoformat(),
            "checks": []
        }

        # Check localhost (ULTRON)
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('localhost', 11434))
            sock.close()

            ulotron_status = "reachable" if result == 0 else "unreachable"
            results["checks"].append({
                "target": "localhost:11434 (ULTRON)",
                "status": ulotron_status,
                "port": 11434
            })
            logger.info(f"   {'✅' if result == 0 else '❌'} ULTRON (localhost:11434): {ulotron_status}")
        except Exception as e:
            results["checks"].append({
                "target": "localhost:11434 (ULTRON)",
                "status": "error",
                "error": str(e)
            })
            logger.error(f"   ❌ ULTRON check failed: {e}")

        # Check NAS (KAIJU)
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex(('<NAS_PRIMARY_IP>', 11434))
            sock.close()

            kaiju_status = "reachable" if result == 0 else "unreachable"
            results["checks"].append({
                "target": "<NAS_PRIMARY_IP>:11434 (KAIJU)",
                "status": kaiju_status,
                "port": 11434
            })
            logger.info(f"   {'✅' if result == 0 else '❌'} KAIJU (<NAS_PRIMARY_IP>:11434): {kaiju_status}")
        except Exception as e:
            results["checks"].append({
                "target": "<NAS_PRIMARY_IP>:11434 (KAIJU)",
                "status": "error",
                "error": str(e)
            })
            logger.error(f"   ❌ KAIJU check failed: {e}")

        # Check NAS general connectivity
        try:
            import subprocess
            result = subprocess.run(
                ['ping', '-n', '1', '<NAS_PRIMARY_IP>'],
                capture_output=True,
                text=True,
                timeout=5
            )
            nas_ping = "reachable" if result.returncode == 0 else "unreachable"
            results["checks"].append({
                "target": "<NAS_PRIMARY_IP> (NAS)",
                "status": nas_ping,
                "method": "ping"
            })
            logger.info(f"   {'✅' if result.returncode == 0 else '❌'} NAS (<NAS_PRIMARY_IP>): {nas_ping}")
        except Exception as e:
            results["checks"].append({
                "target": "<NAS_PRIMARY_IP> (NAS)",
                "status": "error",
                "error": str(e)
            })
            logger.error(f"   ❌ NAS ping failed: {e}")

        return results

    def check_retry_logic(self) -> Dict[str, Any]:
        """Test retry logic functionality"""
        logger.info("🔄 Testing retry logic...")

        try:
            from cursor_chat_retry_manager import CursorChatRetryManager, RetryStrategy

            manager = CursorChatRetryManager(max_retries=3)

            # Test function that fails then succeeds
            attempt_count = [0]
            def test_function():
                attempt_count[0] += 1
                if attempt_count[0] < 3:
                    raise ConnectionError(f"Simulated connection error (attempt {attempt_count[0]})")
                return {"status": "success", "attempt": attempt_count[0]}

            # Test retry
            try:
                result = manager.retry(test_function)
                logger.info(f"   ✅ Retry logic working - succeeded after {result['attempt']} attempts")
                return {
                    "status": "working",
                    "result": result,
                    "attempts": attempt_count[0]
                }
            except Exception as e:
                logger.error(f"   ❌ Retry logic failed: {e}")
                return {
                    "status": "failed",
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

        except Exception as e:
            logger.error(f"   ❌ Error testing retry logic: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def check_error_handling(self) -> Dict[str, Any]:
        """Check error handling in retry manager"""
        logger.info("⚠️  Checking error handling...")

        try:
            from cursor_chat_retry_manager import CursorChatRetryManager

            manager = CursorChatRetryManager()

            # Test different error types
            error_types = [
                TimeoutError("Test timeout"),
                ConnectionError("Test connection error"),
                OSError("Test OS error"),
                RuntimeError("Test runtime error"),
                Exception("Test generic error")
            ]

            results = {
                "error_types_tested": len(error_types),
                "retryable_errors": []
            }

            for error in error_types:
                is_retryable = manager.is_retryable_error(error)
                results["retryable_errors"].append({
                    "error_type": type(error).__name__,
                    "is_retryable": is_retryable,
                    "message": str(error)
                })
                logger.info(f"   {'✅' if is_retryable else '❌'} {type(error).__name__}: {'Retryable' if is_retryable else 'Not retryable'}")

            return results

        except Exception as e:
            logger.error(f"   ❌ Error checking error handling: {e}")
            return {
                "status": "error",
                "error": str(e),
                "traceback": traceback.format_exc()
            }

    def check_request_id_tracking(self) -> Dict[str, Any]:
        """Check if Request ID is being tracked"""
        logger.info(f"📋 Checking Request ID tracking: {REQUEST_ID}...")

        try:
            from track_request_id import RequestIDTracker

            tracker = RequestIDTracker()

            # Check if request ID exists
            tracking_data = tracker.get_request_data(REQUEST_ID)

            if tracking_data:
                logger.info(f"   ✅ Request ID found in tracking")
                logger.info(f"      Source: {tracking_data.get('source', 'unknown')}")
                logger.info(f"      Severity: {tracking_data.get('severity', 'unknown')}")
                return {
                    "status": "found",
                    "data": tracking_data
                }
            else:
                logger.warning(f"   ⚠️  Request ID not found in tracking")
                return {
                    "status": "not_found",
                    "request_id": REQUEST_ID
                }

        except ImportError:
            logger.warning("   ⚠️  Request ID tracker not available")
            return {
                "status": "tracker_unavailable"
            }
        except Exception as e:
            logger.error(f"   ❌ Error checking Request ID: {e}")
            return {
                "status": "error",
                "error": str(e)
            }

    def run_full_diagnostic(self) -> Dict[str, Any]:
        try:
            """Run full diagnostic analysis"""
            logger.info("=" * 80)
            logger.info("🔍 RETRY MANAGER DIAGNOSTIC - Full Analysis")
            logger.info("=" * 80)
            logger.info(f"Request ID: {REQUEST_ID}")
            logger.info("")

            diagnostic_results = {
                "request_id": REQUEST_ID,
                "timestamp": datetime.now().isoformat(),
                "diagnostics": {}
            }

            # 1. Check configuration
            logger.info("STEP 1: Configuration Check")
            logger.info("-" * 80)
            diagnostic_results["diagnostics"]["configuration"] = self.check_retry_manager_config()
            logger.info("")

            # 2. Check network connectivity (for network team)
            logger.info("STEP 2: Network Connectivity Check (Network Team)")
            logger.info("-" * 80)
            diagnostic_results["diagnostics"]["network"] = self.check_network_connectivity()
            logger.info("")

            # 3. Test retry logic
            logger.info("STEP 3: Retry Logic Test")
            logger.info("-" * 80)
            diagnostic_results["diagnostics"]["retry_logic"] = self.check_retry_logic()
            logger.info("")

            # 4. Check error handling
            logger.info("STEP 4: Error Handling Check")
            logger.info("-" * 80)
            diagnostic_results["diagnostics"]["error_handling"] = self.check_error_handling()
            logger.info("")

            # 5. Check Request ID tracking
            logger.info("STEP 5: Request ID Tracking")
            logger.info("-" * 80)
            diagnostic_results["diagnostics"]["request_tracking"] = self.check_request_id_tracking()
            logger.info("")

            # Generate summary
            logger.info("=" * 80)
            logger.info("📊 DIAGNOSTIC SUMMARY")
            logger.info("=" * 80)

            # Identify issues
            issues = []
            recommendations = []

            # Check configuration
            if diagnostic_results["diagnostics"]["configuration"].get("status") == "error":
                issues.append("Retry manager configuration error")
                recommendations.append("Review retry manager initialization")

            # Check network
            network_checks = diagnostic_results["diagnostics"]["network"].get("checks", [])
            unreachable = [c for c in network_checks if c.get("status") in ["unreachable", "error"]]
            if unreachable:
                issues.append(f"Network connectivity issues: {len(unreachable)} targets unreachable")
                recommendations.append("Network team: Check connectivity to ULTRON/KAIJU/NAS")
                for check in unreachable:
                    logger.warning(f"   ⚠️  {check.get('target')}: {check.get('status')}")

            # Check retry logic
            if diagnostic_results["diagnostics"]["retry_logic"].get("status") != "working":
                issues.append("Retry logic not working as intended")
                recommendations.append("Review retry manager implementation")

            # Check error handling
            error_handling = diagnostic_results["diagnostics"]["error_handling"]
            non_retryable = [e for e in error_handling.get("retryable_errors", []) if not e.get("is_retryable")]
            if non_retryable:
                issues.append(f"Some errors not marked as retryable: {len(non_retryable)}")
                recommendations.append("Review error classification logic")

            # Summary
            diagnostic_results["issues"] = issues
            diagnostic_results["recommendations"] = recommendations
            diagnostic_results["status"] = "issues_found" if issues else "no_issues"

            logger.info("")
            if issues:
                logger.warning("⚠️  ISSUES FOUND:")
                for issue in issues:
                    logger.warning(f"   • {issue}")
            else:
                logger.info("✅ No issues found")

            logger.info("")
            logger.info("💡 RECOMMENDATIONS:")
            for rec in recommendations:
                logger.info(f"   • {rec}")

            logger.info("")
            logger.info("=" * 80)

            # Save diagnostic results
            diagnostic_file = self.data_dir / f"diagnostic_{REQUEST_ID}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(diagnostic_file, 'w', encoding='utf-8') as f:
                json.dump(diagnostic_results, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Diagnostic results saved: {diagnostic_file}")
            logger.info("")

            return diagnostic_results


        except Exception as e:
            self.logger.error(f"Error in run_full_diagnostic: {e}", exc_info=True)
            raise
def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Diagnose Retry Manager Issue")
    parser.add_argument("--request-id", default=REQUEST_ID, help="Request ID to diagnose")

    args = parser.parse_args()

    diagnostic = RetryManagerDiagnostic()
    results = diagnostic.run_full_diagnostic()

    logger.info("")
    logger.info("✅ Diagnostic complete")
    logger.info("   Share results with network team and support teams")


if __name__ == "__main__":


    main()