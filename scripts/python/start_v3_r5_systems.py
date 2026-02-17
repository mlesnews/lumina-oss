#!/usr/bin/env python3
"""
Start V3 and R5 Systems with Dependency Checking
Ensures all dependencies are installed before starting services
"""

import sys
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

# Add scripts/python to path
from lumina_core.paths import get_script_dir
script_dir = get_script_dir()
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_core.logging import get_logger
    logger = get_logger("V3R5Startup")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("V3R5Startup")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class V3R5SystemStarter:
    """Start V3 and R5 systems with dependency checking"""

    # Required dependencies
    REQUIRED_DEPENDENCIES = {
        "flask": "Flask web framework for R5 API server",
        "flask-cors": "CORS support for R5 API",
        "requests": "HTTP library for API calls",
    }

    # Optional dependencies (warnings only)
    OPTIONAL_DEPENDENCIES = {
        "azure-keyvault-secrets": "Azure Key Vault integration",
        "azure-identity": "Azure authentication",
        "paramiko": "SSH client support",
    }

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize starter"""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.r5_api_port = 8000
        self.r5_api_url = f"http://localhost:{self.r5_api_port}"
        self.r5_process: Optional[subprocess.Popen] = None

    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version"""
        version = sys.version_info
        if version.major < 3 or (version.major == 3 and version.minor < 8):
            return False, f"Python 3.8+ required, found {version.major}.{version.minor}"
        return True, f"Python {version.major}.{version.minor}.{version.micro}"

    def check_dependency(self, package_name: str) -> bool:
        """Check if a package is installed"""
        try:
            __import__(package_name.replace("-", "_"))
            return True
        except ImportError:
            return False

    def install_dependency(self, package_name: str) -> Tuple[bool, str]:
        """Install a Python package"""
        try:
            logger.info(f"Installing {package_name}...")
            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", package_name],
                capture_output=True,
                text=True,
                timeout=60
            )
            if result.returncode == 0:
                return True, f"{package_name} installed successfully"
            else:
                return False, f"Failed to install {package_name}: {result.stderr}"
        except subprocess.TimeoutExpired:
            return False, f"Timeout installing {package_name}"
        except Exception as e:
            return False, f"Error installing {package_name}: {e}"

    def check_all_dependencies(self) -> Dict[str, Any]:
        """Check all dependencies and install missing ones"""
        results = {
            "python_version": {},
            "required": {},
            "optional": {},
            "all_required_installed": False
        }

        # Check Python version
        py_ok, py_msg = self.check_python_version()
        results["python_version"] = {
            "ok": py_ok,
            "message": py_msg
        }
        if not py_ok:
            logger.error(f"Python version check failed: {py_msg}")
            return results

        logger.info(f"Python version: {py_msg}")

        # Check required dependencies
        missing_required = []
        for package in self.REQUIRED_DEPENDENCIES:
            if self.check_dependency(package):
                results["required"][package] = {"installed": True, "message": "Installed"}
                logger.info(f"  [OK] {package}: Installed")
            else:
                results["required"][package] = {"installed": False, "message": "Not installed"}
                missing_required.append(package)
                logger.warning(f"  [MISSING] {package}: Not installed")

        # Install missing required dependencies
        if missing_required:
            logger.info(f"Installing {len(missing_required)} missing required dependencies...")
            for package in missing_required:
                success, message = self.install_dependency(package)
                if success:
                    results["required"][package] = {"installed": True, "message": message}
                    logger.info(f"  [OK] {package}: {message}")
                else:
                    results["required"][package] = {"installed": False, "message": message}
                    logger.error(f"  [FAIL] {package}: {message}")

        # Check optional dependencies
        for package in self.OPTIONAL_DEPENDENCIES:
            if self.check_dependency(package):
                results["optional"][package] = {"installed": True, "message": "Installed"}
                logger.info(f"  [OK] {package}: Installed (optional)")
            else:
                results["optional"][package] = {"installed": False, "message": "Not installed (optional)"}
                logger.debug(f"  [OPTIONAL] {package}: Not installed")

        # Check if all required are installed
        results["all_required_installed"] = all(
            r.get("installed", False) for r in results["required"].values()
        )

        return results

    def verify_v3_system(self) -> Tuple[bool, str]:
        """Verify V3 system can be imported"""
        try:
            from v3_verification import V3Verification
            verifier = V3Verification()
            return True, "V3 system verified"
        except Exception as e:
            return False, f"V3 system verification failed: {e}"

    def verify_r5_system(self) -> Tuple[bool, str]:
        """Verify R5 system can be imported"""
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            r5 = R5LivingContextMatrix(self.project_root)
            return True, "R5 system verified"
        except Exception as e:
            return False, f"R5 system verification failed: {e}"

    def check_r5_api_running(self) -> bool:
        """Check if R5 API server is already running"""
        try:
            import requests
            response = requests.get(f"{self.r5_api_url}/r5/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def start_r5_api_server(self, background: bool = True) -> Tuple[bool, str]:
        """Start R5 API server"""
        # Check if already running
        if self.check_r5_api_running():
            return True, "R5 API server already running"

        # Check if script exists
        r5_server_script = self.project_root / "scripts" / "python" / "r5_api_server.py"
        if not r5_server_script.exists():
            return False, f"R5 API server script not found: {r5_server_script}"

        try:
            logger.info(f"Starting R5 API server on port {self.r5_api_port}...")

            if background:
                # Start in background
                self.r5_process = subprocess.Popen(
                    [sys.executable, str(r5_server_script)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
                )

                # Wait for server to start
                max_attempts = 15
                for attempt in range(max_attempts):
                    time.sleep(1)
                    if self.check_r5_api_running():
                        logger.info(f"R5 API server started successfully on {self.r5_api_url}")
                        return True, f"R5 API server started on {self.r5_api_url}"
                    if attempt < max_attempts - 1:
                        logger.debug(f"Waiting for server to start... ({attempt + 1}/{max_attempts})")

                return False, "R5 API server failed to start (timeout)"
            else:
                # Run in foreground (blocking)
                logger.info("Starting R5 API server in foreground mode...")
                subprocess.run([sys.executable, str(r5_server_script)], cwd=str(self.project_root))
                return True, "R5 API server started (foreground)"

        except Exception as e:
            return False, f"Failed to start R5 API server: {e}"

    def stop_r5_api_server(self) -> bool:
        """Stop R5 API server"""
        if self.r5_process:
            try:
                self.r5_process.terminate()
                self.r5_process.wait(timeout=5)
                logger.info("R5 API server stopped")
                return True
            except:
                try:
                    self.r5_process.kill()
                    return True
                except:
                    return False
        return False

    def run_startup(self, start_api: bool = True, background: bool = True) -> Dict[str, Any]:
        """Run full startup sequence"""
        logger.info("=" * 60)
        logger.info("V3 & R5 Systems Startup")
        logger.info("=" * 60)

        results = {
            "python_version": {},
            "dependencies": {},
            "v3_verification": {},
            "r5_verification": {},
            "r5_api": {},
            "success": False
        }

        # Step 1: Check Python version
        logger.info("\n[Step 1] Checking Python version...")
        py_ok, py_msg = self.check_python_version()
        results["python_version"] = {"ok": py_ok, "message": py_msg}
        if not py_ok:
            logger.error(f"Python version check failed: {py_msg}")
            return results

        # Step 2: Check and install dependencies
        logger.info("\n[Step 2] Checking dependencies...")
        dep_results = self.check_all_dependencies()
        results["dependencies"] = dep_results

        if not dep_results["all_required_installed"]:
            logger.error("Not all required dependencies are installed")
            return results

        # Step 3: Verify V3 system
        logger.info("\n[Step 3] Verifying V3 system...")
        v3_ok, v3_msg = self.verify_v3_system()
        results["v3_verification"] = {"ok": v3_ok, "message": v3_msg}
        if v3_ok:
            logger.info(f"  [OK] {v3_msg}")
        else:
            logger.error(f"  [FAIL] {v3_msg}")

        # Step 4: Verify R5 system
        logger.info("\n[Step 4] Verifying R5 system...")
        r5_ok, r5_msg = self.verify_r5_system()
        results["r5_verification"] = {"ok": r5_ok, "message": r5_msg}
        if r5_ok:
            logger.info(f"  [OK] {r5_msg}")
        else:
            logger.error(f"  [FAIL] {r5_msg}")

        # Step 5: Start R5 API server (if requested)
        if start_api:
            logger.info("\n[Step 5] Starting R5 API server...")
            api_ok, api_msg = self.start_r5_api_server(background=background)
            results["r5_api"] = {"ok": api_ok, "message": api_msg, "url": self.r5_api_url if api_ok else None}
            if api_ok:
                logger.info(f"  [OK] {api_msg}")
            else:
                logger.error(f"  [FAIL] {api_msg}")

        # Overall success
        results["success"] = (
            py_ok and
            dep_results["all_required_installed"] and
            v3_ok and
            r5_ok and
            (not start_api or results["r5_api"].get("ok", False))
        )

        logger.info("\n" + "=" * 60)
        if results["success"]:
            logger.info("STARTUP COMPLETE - All systems operational")
        else:
            logger.info("STARTUP INCOMPLETE - Some systems failed")
        logger.info("=" * 60)

        return results


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Start V3 and R5 systems with dependency checking")
    parser.add_argument("--no-api", action="store_true", help="Don't start R5 API server")
    parser.add_argument("--foreground", action="store_true", help="Run R5 API server in foreground")
    parser.add_argument("--check-only", action="store_true", help="Only check dependencies, don't start services")

    args = parser.parse_args()

    starter = V3R5SystemStarter()

    if args.check_only:
        # Only check dependencies
        print("Checking dependencies...")
        dep_results = starter.check_all_dependencies()

        print(f"\nPython: {dep_results['python_version']['message']}")
        print("\nRequired Dependencies:")
        for pkg, info in dep_results["required"].items():
            status = "[OK]" if info["installed"] else "[MISSING]"
            print(f"  {status} {pkg}")

        print("\nOptional Dependencies:")
        for pkg, info in dep_results["optional"].items():
            status = "[OK]" if info["installed"] else "[OPTIONAL]"
            print(f"  {status} {pkg}")

        return 0 if dep_results["all_required_installed"] else 1
    else:
        # Full startup
        results = starter.run_startup(start_api=not args.no_api, background=not args.foreground)
        return 0 if results["success"] else 1


if __name__ == "__main__":



    sys.exit(main())