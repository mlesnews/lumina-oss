#!/usr/bin/env python3
"""
Fix Iron Legion Laptop Virtual Cluster

Diagnoses and fixes issues with the Iron Legion virtual cluster on the laptop.
Checks Ollama endpoints, starts services if needed, and validates cluster health.
"""

import sys
import json
import time
import subprocess
import platform
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("⚠️ Warning: requests library not available. Install with: pip install requests")

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IronLegionFix")


class IronLegionClusterFixer:
    """Fix Iron Legion virtual cluster issues"""

    def __init__(self):
        self.logger = logger
        self.primary_endpoint = "http://localhost:3000"
        self.fallback_endpoint = "http://localhost:11437"
        self.ollama_default_port = 11434  # Standard Ollama port
        self.fix_results = []

    def diagnose_cluster(self) -> Dict[str, Any]:
        """Diagnose cluster health and identify issues"""
        self.logger.info("🔍 Diagnosing Iron Legion cluster...")

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "primary_endpoint": self.primary_endpoint,
            "fallback_endpoint": self.fallback_endpoint,
            "issues": [],
            "health": {}
        }

        # Check primary endpoint
        primary_health = self._check_endpoint(self.primary_endpoint)
        diagnosis["health"]["primary"] = primary_health
        if not primary_health["available"]:
            diagnosis["issues"].append({
                "endpoint": self.primary_endpoint,
                "issue": "Primary endpoint not responding",
                "severity": "critical"
            })

        # Check fallback endpoint
        fallback_health = self._check_endpoint(self.fallback_endpoint)
        diagnosis["health"]["fallback"] = fallback_health
        if not fallback_health["available"]:
            diagnosis["issues"].append({
                "endpoint": self.fallback_endpoint,
                "issue": "Fallback endpoint not responding",
                "severity": "critical"
            })

        # Check standard Ollama port
        ollama_health = self._check_endpoint(f"http://localhost:{self.ollama_default_port}")
        diagnosis["health"]["ollama_standard"] = ollama_health

        # Check if Ollama process is running
        ollama_process = self._check_ollama_process()
        diagnosis["ollama_process"] = ollama_process

        # Overall cluster status
        if primary_health["available"] or fallback_health["available"]:
            diagnosis["cluster_status"] = "degraded" if len(diagnosis["issues"]) > 0 else "healthy"
        else:
            diagnosis["cluster_status"] = "inoperative"

        return diagnosis

    def _check_endpoint(self, endpoint: str) -> Dict[str, Any]:
        """Check if an endpoint is responding"""
        health = {
            "endpoint": endpoint,
            "available": False,
            "response_time": None,
            "error": None,
            "models": []
        }

        if not REQUESTS_AVAILABLE:
            health["error"] = "requests library not available"
            return health

        try:
            # Try Ollama API endpoint
            start_time = time.time()
            response = requests.get(f"{endpoint}/api/tags", timeout=5)
            response_time = (time.time() - start_time) * 1000

            if response.status_code == 200:
                health["available"] = True
                health["response_time"] = response_time
                try:
                    data = response.json()
                    if "models" in data:
                        health["models"] = [m.get("name", "") for m in data["models"]]
                except:
                    pass
            else:
                health["error"] = f"HTTP {response.status_code}"

        except requests.exceptions.ConnectionError:
            health["error"] = "Connection refused - service not running"
        except requests.exceptions.Timeout:
            health["error"] = "Connection timeout"
        except Exception as e:
            health["error"] = str(e)

        return health

    def _check_ollama_process(self) -> Dict[str, Any]:
        """Check if Ollama process is running"""
        result = {
            "running": False,
            "processes": [],
            "paths": []
        }

        try:
            if platform.system() == "Windows":
                # Check Windows processes
                proc = subprocess.run(
                    ["tasklist", "/FI", "IMAGENAME eq ollama.exe"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if "ollama.exe" in proc.stdout:
                    result["running"] = True
                    # Parse process info
                    lines = proc.stdout.strip().split('\n')
                    for line in lines[2:]:  # Skip header
                        if line.strip():
                            parts = line.split()
                            if len(parts) >= 2:
                                result["processes"].append({
                                    "name": parts[0],
                                    "pid": parts[1] if parts[1].isdigit() else None
                                })
            else:
                # Unix-like systems
                proc = subprocess.run(
                    ["pgrep", "-fl", "ollama"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if proc.returncode == 0:
                    result["running"] = True
                    for line in proc.stdout.strip().split('\n'):
                        if line.strip():
                            result["processes"].append({"command": line.strip()})

        except Exception as e:
            result["error"] = str(e)

        return result

    def fix_cluster(self, diagnosis: Dict[str, Any]) -> Dict[str, Any]:
        """Fix identified cluster issues"""
        self.logger.info("🔧 Starting cluster fix process...")

        fix_result = {
            "timestamp": datetime.now().isoformat(),
            "fixes_applied": [],
            "fixes_failed": [],
            "cluster_status_after": "unknown"
        }

        # Fix 1: Start Ollama if not running
        if not diagnosis.get("ollama_process", {}).get("running", False):
            self.logger.info("🔄 Attempting to start Ollama...")
            start_result = self._start_ollama()
            if start_result["success"]:
                fix_result["fixes_applied"].append("Started Ollama service")
                self.logger.info("✅ Ollama started successfully")
            else:
                fix_result["fixes_failed"].append({
                    "fix": "Start Ollama",
                    "reason": start_result.get("error", "Unknown error")
                })
                self.logger.warning(f"⚠️ Failed to start Ollama: {start_result.get('error')}")

        # Wait a bit for Ollama to start
        if fix_result["fixes_applied"]:
            self.logger.info("⏳ Waiting for Ollama to initialize...")
            time.sleep(5)

        # Fix 2: Check if we need to configure port forwarding or proxy
        if not diagnosis["health"].get("primary", {}).get("available") and \
           not diagnosis["health"].get("fallback", {}).get("available"):
            # Check if standard Ollama port is available
            ollama_health = diagnosis["health"].get("ollama_standard", {})
            if ollama_health.get("available"):
                self.logger.info("🔄 Standard Ollama port (11434) is available")
                self.logger.info("💡 Consider updating cluster config to use standard port")
                fix_result["fixes_applied"].append("Identified alternative endpoint (11434)")

        # Verify fixes
        verification = self.verify_cluster()
        fix_result["verification"] = verification
        fix_result["cluster_status_after"] = verification.get("cluster_status", "unknown")

        return fix_result

    def _start_ollama(self) -> Dict[str, Any]:
        """Attempt to start Ollama service"""
        result = {"success": False, "error": None}

        try:
            if platform.system() == "Windows":
                # Try to start Ollama on Windows
                # Check common installation paths
                possible_paths = [
                    r"C:\Program Files\Ollama\ollama.exe",
                    r"C:\Users\{}\AppData\Local\Programs\Ollama\ollama.exe".format(
                        os.environ.get("USERNAME", "")
                    ),
                    "ollama.exe"  # If in PATH
                ]

                for path in possible_paths:
                    if Path(path).exists() if Path(path).is_absolute() else True:
                        try:
                            # Start Ollama as a service or background process
                            proc = subprocess.Popen(
                                [path, "serve"],
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE,
                                creationflags=subprocess.CREATE_NEW_CONSOLE if hasattr(subprocess, 'CREATE_NEW_CONSOLE') else 0
                            )
                            result["success"] = True
                            result["pid"] = proc.pid
                            break
                        except Exception as e:
                            continue

                if not result["success"]:
                    result["error"] = "Ollama executable not found in common paths. Please start Ollama manually."
            else:
                # Unix-like systems
                try:
                    proc = subprocess.Popen(
                        ["ollama", "serve"],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE
                    )
                    result["success"] = True
                    result["pid"] = proc.pid
                except FileNotFoundError:
                    result["error"] = "Ollama not found in PATH. Please install Ollama or add to PATH."

        except Exception as e:
            result["error"] = str(e)

        return result

    def verify_cluster(self) -> Dict[str, Any]:
        """Verify cluster is working after fixes"""
        self.logger.info("✅ Verifying cluster health...")

        verification = {
            "timestamp": datetime.now().isoformat(),
            "endpoints": {},
            "cluster_status": "unknown"
        }

        # Check primary
        primary = self._check_endpoint(self.primary_endpoint)
        verification["endpoints"]["primary"] = primary

        # Check fallback
        fallback = self._check_endpoint(self.fallback_endpoint)
        verification["endpoints"]["fallback"] = fallback

        # Check standard Ollama
        ollama_std = self._check_endpoint(f"http://localhost:{self.ollama_default_port}")
        verification["endpoints"]["ollama_standard"] = ollama_std

        # Determine overall status
        if primary["available"] or fallback["available"]:
            verification["cluster_status"] = "operational"
        elif ollama_std["available"]:
            verification["cluster_status"] = "operational_on_standard_port"
        else:
            verification["cluster_status"] = "inoperative"

        return verification

    def get_recommendations(self, diagnosis: Dict[str, Any], fix_result: Dict[str, Any]) -> List[str]:
        """Get recommendations for fixing the cluster"""
        recommendations = []

        if diagnosis["cluster_status"] == "inoperative":
            recommendations.append(
                "🚨 CRITICAL: Cluster is completely inoperative. All endpoints are down."
            )
            recommendations.append(
                "   1. Ensure Ollama is installed: https://ollama.com/download"
            )
            recommendations.append(
                "   2. Start Ollama service manually: `ollama serve`"
            )
            recommendations.append(
                "   3. Verify Ollama is running: `ollama list`"
            )

        if not diagnosis.get("ollama_process", {}).get("running"):
            recommendations.append(
                "⚠️ Ollama process is not running. Start it with: `ollama serve`"
            )

        # Check if standard port is available but configured ports are not
        ollama_std = diagnosis["health"].get("ollama_standard", {})
        if ollama_std.get("available") and not diagnosis["health"].get("primary", {}).get("available"):
            recommendations.append(
                f"💡 Standard Ollama port (11434) is available. Consider updating cluster config."
            )

        if fix_result["cluster_status_after"] == "operational":
            recommendations.append(
                "✅ Cluster is now operational! All fixes applied successfully."
            )
        elif fix_result["cluster_status_after"] == "operational_on_standard_port":
            recommendations.append(
                f"✅ Ollama is running on standard port (11434). Update cluster config to use this port."
            )
        else:
            recommendations.append(
                "⚠️ Cluster still needs attention. Review the diagnostic output above."
            )

        return recommendations


def main():
    """Main fix routine"""
    print("🔧 IRON LEGION CLUSTER FIX")
    print("=" * 50)

    fixer = IronLegionClusterFixer()

    # Step 1: Diagnose
    print("\n📊 STEP 1: DIAGNOSIS")
    print("-" * 30)
    diagnosis = fixer.diagnose_cluster()
    print(f"Cluster Status: {diagnosis['cluster_status'].upper()}")

    if diagnosis["issues"]:
        print(f"\nIssues Found: {len(diagnosis['issues'])}")
        for issue in diagnosis["issues"]:
            print(f"  • {issue['endpoint']}: {issue['issue']} ({issue['severity']})")

    # Step 2: Fix
    print("\n🔧 STEP 2: APPLYING FIXES")
    print("-" * 30)
    fix_result = fixer.fix_cluster(diagnosis)

    if fix_result["fixes_applied"]:
        print(f"Fixes Applied: {len(fix_result['fixes_applied'])}")
        for fix in fix_result["fixes_applied"]:
            print(f"  ✅ {fix}")

    if fix_result["fixes_failed"]:
        print(f"\nFixes Failed: {len(fix_result['fixes_failed'])}")
        for fix in fix_result["fixes_failed"]:
            print(f"  ❌ {fix['fix']}: {fix['reason']}")

    # Step 3: Verify
    print("\n✅ STEP 3: VERIFICATION")
    print("-" * 30)
    verification = fix_result["verification"]
    print(f"Final Cluster Status: {verification['cluster_status'].upper()}")

    for endpoint_name, endpoint_health in verification["endpoints"].items():
        status = "✅ AVAILABLE" if endpoint_health.get("available") else "❌ UNAVAILABLE"
        print(f"  {endpoint_name}: {status}")
        if endpoint_health.get("models"):
            print(f"    Models: {len(endpoint_health['models'])}")

    # Step 4: Recommendations
    print("\n💡 RECOMMENDATIONS")
    print("-" * 30)
    recommendations = fixer.get_recommendations(diagnosis, fix_result)
    for rec in recommendations:
        print(rec)

    print("\n" + "=" * 50)
    print("Iron Legion Cluster Fix Complete")
    return 0 if verification["cluster_status"] == "operational" else 1


if __name__ == "__main__":
    import os


    sys.exit(main())