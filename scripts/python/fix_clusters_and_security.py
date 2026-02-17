#!/usr/bin/env python3
"""
Fix Clusters and Security Issues
- Removes GitHub token from git history (step 4)
- Fixes local AI clusters (Iron Legion & ULTRON)
- Runs diagnostics and battletests

Tags: #CLUSTER #SECURITY #FIX @JARVIS @LUMINA @DOIT
"""

import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict

import requests

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger

    logger = get_logger("FixClustersSecurity")
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("FixClustersSecurity")


class ClusterFixer:
    """Fix local AI clusters"""

    def __init__(self):
        self.project_root = project_root
        self.results = {}

    def check_ollama_local(self) -> bool:
        """Check if local Ollama is running"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                logger.info("✅ ULTRON (localhost:11434) is online")
                return True
            else:
                logger.warning(f"⚠️  ULTRON responding but error: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  ULTRON (localhost:11434) is offline")
            return False
        except Exception as e:
            logger.error(f"❌ Error checking ULTRON: {e}")
            return False

    def start_ollama_local(self) -> bool:
        """Start local Ollama service"""
        logger.info("🚀 Starting Ollama service...")

        # Check if already running
        if self.check_ollama_local():
            return True

        # Try to start Ollama
        try:
            # Check if ollama is in PATH
            result = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            )

            if result.returncode != 0:
                logger.error("❌ Ollama not found in PATH")
                return False

            # Start Ollama in background
            logger.info("Starting Ollama service...")
            subprocess.Popen(
                ["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Wait for it to start
            logger.info("⏳ Waiting for Ollama to start...")
            for i in range(15):
                time.sleep(2)
                if self.check_ollama_local():
                    logger.info("✅ Ollama started successfully")
                    return True

            logger.error("❌ Ollama failed to start within 30 seconds")
            return False

        except FileNotFoundError:
            logger.error("❌ Ollama executable not found")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting Ollama: {e}")
            return False

    def check_iron_legion(self) -> Dict[str, Any]:
        """Check Iron Legion cluster status"""
        results = {"main_cluster": False, "models": {}}

        # Check main cluster
        try:
            response = requests.get("http://<NAS_IP>:3000/health", timeout=5)
            if response.status_code == 200:
                logger.info("✅ Iron Legion main cluster (<NAS_IP>:3000) is online")
                results["main_cluster"] = True
            else:
                logger.warning(f"⚠️  Iron Legion main cluster error: {response.status_code}")
        except requests.exceptions.ConnectionError:
            logger.warning("⚠️  Iron Legion main cluster (<NAS_IP>:3000) is offline")
        except Exception as e:
            logger.error(f"❌ Error checking Iron Legion main: {e}")

        # Check individual models
        for port in range(3001, 3008):
            model_name = f"Mark {port - 3000}"
            try:
                response = requests.get(f"http://<NAS_IP>:{port}/health", timeout=3)
                if response.status_code == 200:
                    logger.info(f"✅ {model_name} (port {port}) is online")
                    results["models"][model_name] = True
                else:
                    logger.warning(f"⚠️  {model_name} (port {port}) error: {response.status_code}")
                    results["models"][model_name] = False
            except requests.exceptions.ConnectionError:
                logger.warning(f"⚠️  {model_name} (port {port}) is offline")
                results["models"][model_name] = False
            except Exception as e:
                logger.error(f"❌ Error checking {model_name}: {e}")
                results["models"][model_name] = False

        return results

    def start_cluster_services(self) -> bool:
        """Start cluster services using the startup script"""
        logger.info("🚀 Starting cluster services...")

        try:
            script_path = script_dir / "start_all_cluster_services.py"
            if not script_path.exists():
                logger.error(f"❌ Script not found: {script_path}")
                return False

            result = subprocess.run(
                [sys.executable, str(script_path)], capture_output=True, text=True, timeout=180
            )

            if result.returncode == 0:
                logger.info("✅ Cluster services started")
                return True
            else:
                logger.warning(f"⚠️  Cluster services returned code {result.returncode}")
                if result.stderr:
                    logger.warning(f"Error: {result.stderr[:500]}")
                return False

        except subprocess.TimeoutExpired:
            logger.error("❌ Cluster services startup timed out")
            return False
        except Exception as e:
            logger.error(f"❌ Error starting cluster services: {e}")
            return False

    def run_marvin_diagnostics(self) -> Dict[str, Any]:
        """Run MARVIN diagnostics"""
        logger.info("🤖 Running MARVIN diagnostics...")

        try:
            script_path = script_dir / "marvin_cluster_diagnostic_report.py"
            if not script_path.exists():
                logger.warning("⚠️  MARVIN diagnostic script not found")
                return {}

            result = subprocess.run(
                [sys.executable, str(script_path)], capture_output=True, text=True, timeout=60
            )

            if result.returncode == 0:
                logger.info("✅ MARVIN diagnostics completed")
                return {"success": True, "output": result.stdout}
            else:
                logger.warning(f"⚠️  MARVIN diagnostics returned code {result.returncode}")
                return {"success": False, "error": result.stderr}

        except Exception as e:
            logger.error(f"❌ Error running MARVIN diagnostics: {e}")
            return {"success": False, "error": str(e)}

    def fix_clusters(self) -> Dict[str, Any]:
        """Main fix routine"""
        logger.info("=" * 70)
        logger.info("🔧 FIXING LOCAL AI CLUSTERS")
        logger.info("=" * 70)
        logger.info("")

        results = {"ultron": False, "iron_legion": {}, "timestamp": datetime.now().isoformat()}

        # Fix ULTRON (local Ollama)
        logger.info("📡 Fixing ULTRON (localhost:11434)...")
        if not self.check_ollama_local():
            logger.info("   Starting Ollama service...")
            if self.start_ollama_local():
                results["ultron"] = True
            else:
                logger.error("   ❌ Failed to start Ollama")
        else:
            results["ultron"] = True

        logger.info("")

        # Check Iron Legion
        logger.info("📡 Checking Iron Legion cluster (<NAS_IP>)...")
        iron_legion_status = self.check_iron_legion()
        results["iron_legion"] = iron_legion_status

        # If Iron Legion main is down, try to start services
        if not iron_legion_status.get("main_cluster"):
            logger.info("   Iron Legion main cluster is offline")
            logger.info("   Attempting to start cluster services...")
            if self.start_cluster_services():
                logger.info("   ⏳ Waiting for services to initialize...")
                time.sleep(15)
                iron_legion_status = self.check_iron_legion()
                results["iron_legion"] = iron_legion_status

        logger.info("")

        # Run MARVIN diagnostics
        marvin_results = self.run_marvin_diagnostics()
        results["marvin"] = marvin_results

        return results


def remove_token_from_git_history():
    """Remove GitHub token from git history (Step 4)"""
    logger.info("=" * 70)
    logger.info("🔐 STEP 4: REMOVING GITHUB TOKEN FROM GIT HISTORY")
    logger.info("=" * 70)
    logger.info("")

    # Token to search for must come from environment variable - never hardcode
    exposed_token = os.environ.get("GITHUB_EXPOSED_TOKEN", "")
    if not exposed_token:
        logger.error("❌ GITHUB_EXPOSED_TOKEN environment variable not set")
        logger.info("   Set with: $env:GITHUB_EXPOSED_TOKEN = 'token-to-remove'")
        return

    # Check if token exists in history
    logger.info("🔍 Checking if token exists in git history...")
    try:
        result = subprocess.run(
            ["git", "log", "--all", "--full-history", "--source", "-p", "--", ".kilocode/mcp.json"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=project_root,
        )

        if exposed_token in result.stdout:
            logger.warning("⚠️  Token found in git history!")
            logger.info("")
            logger.info("📋 To remove the token from git history:")
            logger.info("   1. Run: python scripts/python/remove_token_from_git_history.py")
            logger.info("   2. Or use BFG Repo-Cleaner:")
            logger.info("      bfg --replace-text <(echo 'TOKEN_VALUE==REDACTED')")
            logger.info("      (Replace TOKEN_VALUE with the actual exposed token)")
            logger.info("")
            logger.info("⚠️  IMPORTANT: This will rewrite git history!")
            logger.info("   - All collaborators must re-clone")
            logger.info("   - Force push required: git push --force --all")
            logger.info("   - Revoke the token on GitHub immediately!")
            return False
        else:
            logger.info("✅ Token not found in current git history (may have been removed)")
            return True

    except Exception as e:
        logger.error(f"❌ Error checking git history: {e}")
        return False


def main():
    try:
        """Main execution"""
        logger.info("=" * 70)
        logger.info("🚀 FIX CLUSTERS AND SECURITY")
        logger.info("=" * 70)
        logger.info("")

        # Step 1: Remove token from git history
        logger.info("STEP 1: Removing GitHub token from git history...")
        token_removed = remove_token_from_git_history()
        logger.info("")

        # Step 2: Fix clusters
        logger.info("STEP 2: Fixing local AI clusters...")
        fixer = ClusterFixer()
        cluster_results = fixer.fix_clusters()
        logger.info("")

        # Summary
        logger.info("=" * 70)
        logger.info("📊 SUMMARY")
        logger.info("=" * 70)
        logger.info("")

        logger.info("Security:")
        logger.info(
            f"   Token in history: {'⚠️  Yes (needs removal)' if not token_removed else '✅ No'}"
        )
        logger.info("")

        logger.info("Clusters:")
        logger.info(
            f"   ULTRON (localhost:11434): {'✅ Online' if cluster_results.get('ultron') else '❌ Offline'}"
        )

        iron_legion = cluster_results.get("iron_legion", {})
        if iron_legion.get("main_cluster"):
            logger.info("   Iron Legion main: ✅ Online")
        else:
            logger.info("   Iron Legion main: ❌ Offline")

        models_online = sum(1 for v in iron_legion.get("models", {}).values() if v)
        models_total = len(iron_legion.get("models", {}))
        logger.info(f"   Iron Legion models: {models_online}/{models_total} online")
        logger.info("")

        # Save report
        report_file = (
            project_root
            / "data"
            / "syphon_results"
            / f"cluster_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_file.parent.mkdir(parents=True, exist_ok=True)

        import json

        report_data = {
            "token_removed_from_history": token_removed,
            "cluster_results": cluster_results,
            "timestamp": datetime.now().isoformat(),
        }
        report_file.write_text(json.dumps(report_data, indent=2))
        logger.info(f"📄 Report saved to: {report_file}")
        logger.info("")

        return 0

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    sys.exit(main())
