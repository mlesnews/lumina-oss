#!/usr/bin/env python3
"""
JARVIS Test-First Policy Enforcer
Ensures all systems follow the policy: ALWAYS TEST - Never assume.

Tags: #POLICY #TESTING #VERIFICATION @AUTO
"""

import sys
from pathlib import Path
from typing import Dict, Any, List, Callable, Optional
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

logger = get_logger("JARVISTestFirst")


class TestFirstPolicy:
    """
    Test-First Policy Enforcer

    POLICY: ALWAYS TEST - Never assume. Verify everything before making recommendations.

    This class provides decorators and utilities to enforce testing before assumptions.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.test_results: List[Dict[str, Any]] = []

        self.logger.info("✅ Test-First Policy Enforcer initialized")
        self.logger.info("   📋 POLICY: Always test, never assume")

    def test_before_assume(self, test_name: str, test_func: Callable, 
                          assumption: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a test before making an assumption.

        Args:
            test_name: Name of the test
            test_func: Function that returns test result (Dict with 'success', 'result', etc.)
            assumption: Optional assumption to log if test fails

        Returns:
            Test result dictionary
        """
        self.logger.info(f"   🧪 TESTING: {test_name}...")

        try:
            result = test_func()

            test_result = {
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "success": result.get("success", False),
                "result": result,
                "assumption": assumption
            }

            if test_result["success"]:
                self.logger.info(f"   ✅ TEST PASSED: {test_name}")
            else:
                self.logger.warning(f"   ❌ TEST FAILED: {test_name}")
                if assumption:
                    self.logger.warning(f"   ⚠️  Cannot assume: {assumption}")

            self.test_results.append(test_result)
            return test_result

        except Exception as e:
            test_result = {
                "test_name": test_name,
                "timestamp": datetime.now().isoformat(),
                "success": False,
                "error": str(e),
                "assumption": assumption
            }
            self.logger.error(f"   ❌ TEST ERROR: {test_name} - {e}")
            self.test_results.append(test_result)
            return test_result

    def verify_service(self, service_name: str, host: str, port: int, 
                      api_endpoint: Optional[str] = None) -> Dict[str, Any]:
        """
        Verify a service is running and accessible.

        Args:
            service_name: Name of the service
            host: Host IP or hostname
            port: Port number
            api_endpoint: Optional API endpoint to test (e.g., "/api/tags")

        Returns:
            Verification result
        """
        def test_func():
            import socket
            import requests

            # Test 1: Port connectivity
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((host, port))
                sock.close()
                port_open = (result == 0)
            except Exception as e:
                return {"success": False, "error": f"Port test failed: {e}"}

            if not port_open:
                return {"success": False, "port_open": False, "message": "Port not accessible"}

            # Test 2: API endpoint (if provided)
            if api_endpoint:
                try:
                    response = requests.get(f"http://{host}:{port}{api_endpoint}", timeout=5)
                    api_accessible = (response.status_code == 200)
                    return {
                        "success": api_accessible,
                        "port_open": True,
                        "api_accessible": api_accessible,
                        "status_code": response.status_code,
                        "data": response.json() if api_accessible else None
                    }
                except Exception as e:
                    return {
                        "success": False,
                        "port_open": True,
                        "api_accessible": False,
                        "error": str(e)
                    }

            return {"success": True, "port_open": True}

        return self.test_before_assume(
            f"{service_name} on {host}:{port}",
            test_func,
            assumption=f"{service_name} is running on {host}:{port}"
        )

    def verify_docker_container(self, container_name: str, host: str, 
                               ssh_credentials: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Verify a Docker container is running (requires SSH).

        Args:
            container_name: Name of the Docker container
            host: Host IP
            ssh_credentials: Optional SSH credentials dict with 'username' and 'password'

        Returns:
            Verification result
        """
        def test_func():
            if not ssh_credentials:
                return {"success": False, "error": "SSH credentials required"}

            try:
                import paramiko
                client = paramiko.SSHClient()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.connect(
                    hostname=host,
                    port=22,
                    username=ssh_credentials.get("username"),
                    password=ssh_credentials.get("password"),
                    timeout=10
                )

                stdin, stdout, stderr = client.exec_command(
                    f"docker ps | grep -i {container_name}",
                    timeout=10
                )
                output = stdout.read().decode().strip()
                error = stderr.read().decode().strip()
                exit_code = stdout.channel.recv_exit_status()

                client.close()

                container_running = (exit_code == 0 and container_name.lower() in output.lower())

                return {
                    "success": container_running,
                    "container_running": container_running,
                    "output": output,
                    "error": error
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

        return self.test_before_assume(
            f"Docker container '{container_name}' on {host}",
            test_func,
            assumption=f"Container '{container_name}' is running on {host}"
        )

    def get_test_summary(self) -> Dict[str, Any]:
        """Get summary of all tests performed"""
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r.get("success")])
        failed = total - passed

        return {
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "tests": self.test_results
        }


def test_first_decorator(test_name: str):
    """
    Decorator to enforce test-first policy on functions.

    Usage:
        @test_first_decorator("Verify Ollama running")
        def check_ollama():
            # Test code here
            return {"success": True, "result": "..."}
    """
    def decorator(func: Callable):
        def wrapper(*args, **kwargs):
            logger.info(f"   🧪 TESTING: {test_name}...")
            try:
                result = func(*args, **kwargs)
                if result.get("success"):
                    logger.info(f"   ✅ TEST PASSED: {test_name}")
                else:
                    logger.warning(f"   ❌ TEST FAILED: {test_name}")
                return result
            except Exception as e:
                logger.error(f"   ❌ TEST ERROR: {test_name} - {e}")
                return {"success": False, "error": str(e)}
        return wrapper
    return decorator


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        policy = TestFirstPolicy(project_root)

        # Example: Test Ollama on KAIJU_NO_8
        result = policy.verify_service(
            "Ollama",
            "<NAS_IP>",
            11434,
            api_endpoint="/api/tags"
        )

        summary = policy.get_test_summary()
        print(f"\nTest Summary: {summary['passed']}/{summary['total_tests']} passed")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()