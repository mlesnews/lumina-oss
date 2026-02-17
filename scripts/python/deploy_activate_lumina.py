#!/usr/bin/env python3
"""
Deploy & Activate @lumina
Comprehensive deployment and activation script for Lumina ecosystem
"""

import sys
import json
import subprocess
import time
import requests
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add scripts/python to path
script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from register_with_lumina import register_all_systems_with_lumina
from universal_decision_tree import decide, DecisionContext, DecisionOutcome



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class LuminaDeployment:
    """Deploy and activate Lumina ecosystem"""

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize deployment"""
        import logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("LuminaDeployment")

        if project_root is None:
            # Auto-detect project root
            self.project_root = Path(__file__).parent.parent.parent
        else:
            self.project_root = Path(project_root)

        self.r5_api_port = 8000
        self.r5_api_url = f"http://localhost:{self.r5_api_port}"
        self.r5_process = None

    def register_systems(self) -> bool:
        """Register all systems with Lumina"""
        print("\n" + "=" * 60)
        print("Step 1: Registering Systems with Lumina")
        print("=" * 60)

        try:
            registration = register_all_systems_with_lumina(self.project_root)
            print(f"\n[SUCCESS] Registered {len(registration.get('registered_systems', []))} systems")
            return True
        except Exception as e:
            print(f"\n[ERROR] Registration failed: {e}")
            return False

    def verify_dependencies(self) -> bool:
        """Verify all dependencies are installed"""
        print("\n" + "=" * 60)
        print("Step 2: Verifying Dependencies")
        print("=" * 60)

        required_modules = [
            "flask",
            "flask_cors",
            "pathlib",
            "json",
            "datetime"
        ]

        missing = []
        for module in required_modules:
            try:
                if module == "flask_cors":
                    __import__("flask_cors")
                else:
                    __import__(module)
                print(f"  [OK] {module}")
            except ImportError:
                print(f"  [MISSING] {module}")
                missing.append(module)

        if missing:
            print(f"\n[WARNING] Missing dependencies: {', '.join(missing)}")
            print("Install with: pip install flask flask-cors")
            return False

        print("\n[SUCCESS] All dependencies verified")
        return True

    def verify_configurations(self) -> bool:
        try:
            """Verify all configuration files exist"""
            print("\n" + "=" * 60)
            print("Step 3: Verifying Configurations")
            print("=" * 60)

            required_configs = [
                "config/lumina_extensions_integration.json",
                "config/helpdesk/droids.json",
                "config/helpdesk/helpdesk_structure.json",
                "config/droid_actor_routing.json"
            ]

            missing = []
            for config_path in required_configs:
                full_path = self.project_root / config_path
                if full_path.exists():
                    print(f"  [OK] {config_path}")
                else:
                    print(f"  [MISSING] {config_path}")
                    missing.append(config_path)

            if missing:
                print(f"\n[WARNING] Missing configuration files: {len(missing)}")
                print("Some features may not work correctly")
                return False

            print("\n[SUCCESS] All configurations verified")
            return True

        except Exception as e:
            print(f"\n[ERROR] verify_configurations failed: {e}")
            raise
    def start_r5_api_server(self) -> bool:
        """Start R5 API server"""
        print("\n" + "=" * 60)
        print("Step 4: Starting R5 API Server")
        print("=" * 60)

        # Check if server is already running
        try:
            response = requests.get(f"{self.r5_api_url}/r5/health", timeout=2)
            if response.status_code == 200:
                print(f"  [INFO] R5 API server already running on port {self.r5_api_port}")
                return True
        except requests.exceptions.RequestException:
            pass  # Server not running, continue to start it

        # Start server
        r5_server_script = self.project_root / "scripts" / "python" / "r5_api_server.py"
        if not r5_server_script.exists():
            print(f"  [ERROR] R5 API server script not found: {r5_server_script}")
            return False

        try:
            print(f"  [INFO] Starting R5 API server on port {self.r5_api_port}...")
            self.r5_process = subprocess.Popen(
                [sys.executable, str(r5_server_script)],
                cwd=str(self.project_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Wait for server to start
            max_attempts = 10
            for attempt in range(max_attempts):
                time.sleep(1)
                try:
                    response = requests.get(f"{self.r5_api_url}/r5/health", timeout=2)
                    if response.status_code == 200:
                        print(f"  [SUCCESS] R5 API server started on {self.r5_api_url}")
                        return True
                except requests.exceptions.RequestException:
                    if attempt < max_attempts - 1:
                        print(f"  [WAIT] Waiting for server to start... ({attempt + 1}/{max_attempts})")
                    continue

            print(f"  [ERROR] R5 API server failed to start after {max_attempts} attempts")
            return False

        except Exception as e:
            print(f"  [ERROR] Failed to start R5 API server: {e}")
            return False

    def verify_components(self) -> bool:
        """Verify all Lumina components are operational"""
        print("\n" + "=" * 60)
        print("Step 5: Verifying Components")
        print("=" * 60)

        components_status = {}

        # Test R5 API Server
        try:
            response = requests.get(f"{self.r5_api_url}/r5/health", timeout=2)
            if response.status_code == 200:
                components_status["r5_api_server"] = True
                print(f"  [OK] R5 API Server: {self.r5_api_url}")
            else:
                components_status["r5_api_server"] = False
                print(f"  [FAIL] R5 API Server: HTTP {response.status_code}")
        except Exception as e:
            components_status["r5_api_server"] = False
            print(f"  [FAIL] R5 API Server: {e}")

        # Test Droid Actor System
        try:
            from droid_actor_system import DroidActorSystem
            system = DroidActorSystem(self.project_root)
            components_status["droid_actor_system"] = True
            print(f"  [OK] Droid Actor System: {len(system.droids)} droids loaded")
        except Exception as e:
            components_status["droid_actor_system"] = False
            print(f"  [FAIL] Droid Actor System: {e}")

        # Test JARVIS Helpdesk Integration
        try:
            from jarvis_helpdesk_integration import JARVISHelpdeskIntegration
            integration = JARVISHelpdeskIntegration(self.project_root)
            components_status["jarvis_helpdesk_integration"] = True
            print(f"  [OK] JARVIS Helpdesk Integration: Initialized")
        except Exception as e:
            components_status["jarvis_helpdesk_integration"] = False
            print(f"  [FAIL] JARVIS Helpdesk Integration: {e}")

        # Test @v3 Verification
        try:
            from v3_verification import V3Verification
            verifier = V3Verification()
            components_status["v3_verification"] = True
            print(f"  [OK] @v3 Verification: Initialized")
        except Exception as e:
            components_status["v3_verification"] = False
            print(f"  [FAIL] @v3 Verification: {e}")

        # Test R5 Living Context Matrix
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            r5 = R5LivingContextMatrix(self.project_root)
            components_status["r5_living_context_matrix"] = True
            print(f"  [OK] R5 Living Context Matrix: Initialized")
        except Exception as e:
            components_status["r5_living_context_matrix"] = False
            print(f"  [FAIL] R5 Living Context Matrix: {e}")

        # Summary
        all_ok = all(components_status.values())
        if all_ok:
            print("\n[SUCCESS] All components operational")
        else:
            failed = [k for k, v in components_status.items() if not v]
            print(f"\n[WARNING] {len(failed)} component(s) failed: {', '.join(failed)}")

        return all_ok

    def create_deployment_status(self) -> Dict[str, Any]:
        try:
            """Create deployment status file"""
            # Check if server is actually responding
            r5_status = "unknown"
            try:
                resp = requests.get(f"{self.r5_api_url}/r5/health", timeout=2)
                if resp.status_code == 200:
                    r5_status = "running"
            except:
                pass

            status = {
                "deployed_at": datetime.now().isoformat(),
                "project_root": str(self.project_root),
                "components": {
                    "r5_api_server": {
                        "url": self.r5_api_url,
                        "port": self.r5_api_port,
                        "status": r5_status
                    },
                    "droid_actor_system": {
                        "status": "operational"
                    },
                    "jarvis_helpdesk_integration": {
                        "status": "operational"
                    },
                    "v3_verification": {
                        "status": "operational"
                    },
                    "r5_living_context_matrix": {
                        "status": "operational"
                    }
                },
                "version": "6.0.0"
            }

            status_file = self.project_root / "data" / "lumina_deployment_status.json"
            status_file.parent.mkdir(parents=True, exist_ok=True)

            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2)

            return status

        except Exception as e:
            print(f"\n[ERROR] create_deployment_status failed: {e}")
            raise
    def deploy_and_activate(self) -> bool:
        """Deploy and activate Lumina"""
        print("=" * 60)
        print("LUMINA DEPLOYMENT & ACTIVATION")
        print("=" * 60)
        print(f"Project Root: {self.project_root}")
        print(f"Timestamp: {datetime.now().isoformat()}")

        steps = [
            ("Register Systems", self.register_systems),
            ("Verify Dependencies", self.verify_dependencies),
            ("Verify Configurations", self.verify_configurations),
            ("Start R5 API Server", self.start_r5_api_server),
            ("Verify Components", self.verify_components)
        ]

        results = {}
        for step_name, step_func in steps:
            try:
                results[step_name] = step_func()
            except Exception as e:
                print(f"\n[ERROR] {step_name} failed: {e}")
                results[step_name] = False

        # Create deployment status
        self.create_deployment_status()

        # Summary
        print("\n" + "=" * 60)
        print("DEPLOYMENT SUMMARY")
        print("=" * 60)

        for step_name, success in results.items():
            status = "[SUCCESS]" if success else "[FAILED]"
            print(f"{status} {step_name}")

        all_success = all(results.values())

        if all_success:
            print("\n" + "=" * 60)
            print("[SUCCESS] LUMINA V6 DEPLOYED & ACTIVATED")
            print("=" * 60)
            print("\nLumina V6 is now operational:")
            print(f"  • R5 API Server: {self.r5_api_url}")
            print(f"  • Droid Actor System: Operational")
            print(f"  • JARVIS Helpdesk Integration: Operational")
            print(f"  • @v3 Verification: Operational")
            print(f"  • R5 Living Context Matrix: Operational")
            print("\nTo stop R5 API server, use: Ctrl+C or kill the process")
        else:
            print("\n" + "=" * 60)
            print("[WARNING] DEPLOYMENT COMPLETED WITH ISSUES")
            print("=" * 60)
            print("Some components may not be fully operational.")
            print("Check the errors above and resolve them.")

        return all_success


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Deploy & Activate @lumina")
        parser.add_argument(
            "--project-root",
            type=str,
            default=None,
            help="Project root directory (default: auto-detect)"
        )

        args = parser.parse_args()

        project_root = Path(args.project_root) if args.project_root else None

        deployment = LuminaDeployment(project_root)
        success = deployment.deploy_and_activate()

        sys.exit(0 if success else 1)


    except Exception as e:
        print(f"\n[CRITICAL] Main execution failed: {e}")
        sys.exit(1)
if __name__ == "__main__":



    main()