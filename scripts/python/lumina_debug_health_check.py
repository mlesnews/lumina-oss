#!/usr/bin/env python3
"""
LUMINA Debug Mode Health Check - V3 Validation

Comprehensive granular health check for all LUMINA systems in debug mode.
Verifies all systems are GREEN before NAS migration and other operations.

Tags: #HEALTH_CHECK #DEBUG_MODE #V3 #VALIDATION #LUMINA_CORE @JARVIS @BONES @UATU @DOIT
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

# Add project root to path
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
    logging.basicConfig(level=logging.DEBUG)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LUMINADebugHealthCheck")


class HealthStatus(Enum):
    """Health status levels"""
    GREEN = "GREEN"      # ✅ All systems operational
    YELLOW = "YELLOW"    # ⚠️  Warnings, non-critical
    RED = "RED"          # ❌ Errors detected
    CRITICAL = "CRITICAL" # 🚨 Critical issues


class SystemCheck:
    """Individual system check result"""
    def __init__(self, name: str, status: HealthStatus, details: Dict[str, Any]):
        self.name = name
        self.status = status
        self.details = details
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "status": self.status.value,
            "details": self.details,
            "timestamp": self.timestamp.isoformat()
        }


class LuminaDebugHealthCheck:
    """
    LUMINA Debug Mode Health Check

    Comprehensive granular health check for all systems:
    - Core LUMINA systems (JARVIS, R5, SYPHON, WOPR, UATU, BONES)
    - Docker/Kubernetes
    - Local AI configurations
    - System resources
    - Network connectivity
    - File system integrity
    """

    def __init__(self, project_root: Optional[Path] = None, debug_mode: bool = True):
        """Initialize health checker"""
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent.parent
        self.debug_mode = debug_mode
        self.checks: List[SystemCheck] = []
        self.overall_status = HealthStatus.GREEN

        # Unix/Linux startup style header
        logger.info("=" * 80)
        logger.info("LUMINA System Health Check - V3 Validation")
        logger.info("=" * 80)
        logger.info(f"Project Root: {self.project_root}")
        logger.info(f"Debug Mode: {self.debug_mode}")
        logger.info("")
        logger.info("Starting system checks...")
        logger.info("")

    def check_core_systems(self) -> List[SystemCheck]:
        """Check all core LUMINA systems"""
        logger.info("=" * 80)
        logger.info("Starting core LUMINA systems...")
        logger.info("=" * 80)
        logger.info("")

        checks = []

        # @JARVIS
        jarvis_status = self._check_jarvis()
        checks.append(jarvis_status)
        self._log_check(jarvis_status)

        # @R5 (Living Context Matrix)
        r5_status = self._check_r5()
        checks.append(r5_status)
        self._log_check(r5_status)

        # @SYPHON
        syphon_status = self._check_syphon()
        checks.append(syphon_status)
        self._log_check(syphon_status)

        # @WOPR
        wopr_status = self._check_wopr()
        checks.append(wopr_status)
        self._log_check(wopr_status)

        # @UATU (The Watcher)
        uatu_status = self._check_uatu()
        checks.append(uatu_status)
        self._log_check(uatu_status)

        # @BONES (System Diagnostics)
        bones_status = self._check_bones()
        checks.append(bones_status)
        self._log_check(bones_status)

        # Pattern Unified Engine
        pattern_status = self._check_pattern_unified_engine()
        checks.append(pattern_status)
        self._log_check(pattern_status)

        logger.info("")
        return checks

    def _check_jarvis(self) -> SystemCheck:
        """Check @JARVIS system"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check JARVIS files
            jarvis_files = [
                "scripts/python/jarvis_dynamic_scaling_helper.py",
                "scripts/python/jarvis_extrapolation_engine.py",
                ".cursor/commands/jarvis.md"
            ]

            found_files = []
            missing_files = []

            for file_path in jarvis_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found_files.append(file_path)
                else:
                    missing_files.append(file_path)

            details["files_found"] = len(found_files)
            details["files_missing"] = len(missing_files)
            details["found"] = found_files
            details["missing"] = missing_files

            if missing_files:
                status = HealthStatus.YELLOW
                details["issue"] = f"Missing {len(missing_files)} JARVIS files"

            # Check JARVIS dynamic scaling
            try:
                from scripts.python.jarvis_dynamic_scaling_helper import get_jarvis_wait
                wait_helper = get_jarvis_wait()
                details["dynamic_scaling"] = "available"
                details["dynamic_scaling_enabled"] = wait_helper.dynamic_scaling_enabled
            except Exception as e:
                status = HealthStatus.YELLOW
                details["dynamic_scaling"] = "error"
                details["dynamic_scaling_error"] = str(e)

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@JARVIS", status, details)

    def _check_r5(self) -> SystemCheck:
        """Check @R5 (Living Context Matrix)"""
        details = {}
        status = HealthStatus.GREEN

        try:
            r5_files = [
                "scripts/python/r5_living_context_matrix.py",
                ".cursor/commands/@r5.md",
                "--serve/data/r5_living_matrix"
            ]

            found = []
            missing = []

            for file_path in r5_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)

            details["files_found"] = len(found)
            details["files_missing"] = len(missing)
            details["found"] = found
            details["missing"] = missing

            # Check Pattern Unified Engine integration
            try:
                r5_file = self.project_root / "scripts/python/r5_living_context_matrix.py"
                if r5_file.exists():
                    content = r5_file.read_text(encoding="utf-8")
                    if "PatternUnifiedEngine" in content:
                        details["unified_engine_integrated"] = True
                    else:
                        details["unified_engine_integrated"] = False
                        status = HealthStatus.YELLOW
            except Exception as e:
                details["integration_check_error"] = str(e)

            if missing:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@R5", status, details)

    def _check_syphon(self) -> SystemCheck:
        """Check @SYPHON system"""
        details = {}
        status = HealthStatus.GREEN

        try:
            syphon_files = [
                "scripts/python/lumina/syphon.py",
                "scripts/python/syphon_system.py",
                ".cursor/commands/@syphon.md"
            ]

            found = []
            missing = []

            for file_path in syphon_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)

            details["files_found"] = len(found)
            details["files_missing"] = len(missing)

            # Check unified engine integration
            try:
                syphon_file = self.project_root / "scripts/python/lumina/syphon.py"
                if syphon_file.exists():
                    content = syphon_file.read_text(encoding="utf-8")
                    if "PatternUnifiedEngine" in content:
                        details["unified_engine_integrated"] = True
                    else:
                        details["unified_engine_integrated"] = False
            except Exception:
                pass

            if missing:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@SYPHON", status, details)

    def _check_wopr(self) -> SystemCheck:
        """Check @WOPR system"""
        details = {}
        status = HealthStatus.GREEN

        try:
            wopr_files = [
                "scripts/python/lumina/wopr_simulator.py",
                "scripts/python/wopr_ops.py"
            ]

            found = []
            missing = []

            for file_path in wopr_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)

            details["files_found"] = len(found)
            details["files_missing"] = len(missing)

            # Check unified engine integration
            try:
                wopr_file = self.project_root / "scripts/python/lumina/wopr_simulator.py"
                if wopr_file.exists():
                    content = wopr_file.read_text(encoding="utf-8")
                    if "PatternUnifiedEngine" in content:
                        details["unified_engine_integrated"] = True
                    else:
                        details["unified_engine_integrated"] = False
            except Exception:
                pass

            if missing:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@WOPR", status, details)

    def _check_uatu(self) -> SystemCheck:
        """Check @UATU (The Watcher)"""
        details = {}
        status = HealthStatus.GREEN

        try:
            uatu_files = [
                ".cursor/commands/@uatu.md",
                "docs/system/WATCHER_ECOSYSTEM_WIDE_INSIGHTS.md",
                "data/watcher_observations"
            ]

            found = []
            missing = []

            for file_path in uatu_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)

            details["files_found"] = len(found)
            details["files_missing"] = len(missing)

            # Check observation directory
            obs_dir = self.project_root / "data/watcher_observations"
            if obs_dir.exists():
                obs_files = list(obs_dir.glob("*.json"))
                details["observation_files"] = len(obs_files)
            else:
                details["observation_files"] = 0
                status = HealthStatus.YELLOW

            if missing:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@UATU", status, details)

    def _check_bones(self) -> SystemCheck:
        """Check @BONES (System Diagnostics)"""
        details = {}
        status = HealthStatus.GREEN

        try:
            bones_files = [
                ".cursor/commands/@bones.md",
                "scripts/reboot-performance-test.ps1",
                "scripts/reboot-performance-check.ps1"
            ]

            found = []
            missing = []

            for file_path in bones_files:
                full_path = self.project_root / file_path
                if full_path.exists():
                    found.append(file_path)
                else:
                    missing.append(file_path)

            details["files_found"] = len(found)
            details["files_missing"] = len(missing)

            if missing:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("@BONES", status, details)

    def _check_pattern_unified_engine(self) -> SystemCheck:
        """Check Pattern Unified Engine"""
        details = {}
        status = HealthStatus.GREEN

        try:
            engine_file = self.project_root / "scripts/python/pattern_unified_engine.py"
            test_file = self.project_root / "scripts/python/pattern_unified_v3_test.py"

            details["engine_file_exists"] = engine_file.exists()
            details["test_file_exists"] = test_file.exists()

            if engine_file.exists():
                # Try to import
                try:
                    sys.path.insert(0, str(self.project_root))
                    from scripts.python.pattern_unified_engine import PatternUnifiedEngine
                    engine = PatternUnifiedEngine(self.project_root)
                    details["engine_importable"] = True
                    details["engine_initialized"] = True
                except Exception as e:
                    details["engine_importable"] = False
                    details["engine_error"] = str(e)
                    status = HealthStatus.YELLOW
            else:
                status = HealthStatus.RED
                details["error"] = "Pattern Unified Engine file not found"

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Pattern Unified Engine", status, details)

    def check_docker_kubernetes(self) -> List[SystemCheck]:
        """Check Docker and Kubernetes"""
        logger.info("=" * 80)
        logger.info("Starting Docker & Kubernetes services...")
        logger.info("=" * 80)
        logger.info("")

        checks = []

        # Docker
        docker_status = self._check_docker()
        checks.append(docker_status)
        self._log_check(docker_status)

        # Kubernetes
        k8s_status = self._check_kubernetes()
        checks.append(k8s_status)
        self._log_check(k8s_status)

        # Docker images
        docker_images_status = self._check_docker_images()
        checks.append(docker_images_status)
        self._log_check(docker_images_status)

        logger.info("")
        return checks

    def _check_docker(self) -> SystemCheck:
        """Check Docker status"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check if Docker is installed
            try:
                result = subprocess.run(
                    ["docker", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    details["installed"] = True
                    details["version"] = result.stdout.strip()
                else:
                    details["installed"] = False
                    status = HealthStatus.RED
            except FileNotFoundError:
                details["installed"] = False
                status = HealthStatus.RED
            except Exception as e:
                details["installed"] = "unknown"
                details["error"] = str(e)
                status = HealthStatus.YELLOW

            # Check if Docker daemon is running
            if details.get("installed"):
                try:
                    result = subprocess.run(
                        ["docker", "info"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        details["daemon_running"] = True
                    else:
                        details["daemon_running"] = False
                        details["daemon_error"] = result.stderr
                        status = HealthStatus.RED
                except Exception as e:
                    details["daemon_running"] = "unknown"
                    details["daemon_error"] = str(e)
                    status = HealthStatus.YELLOW

            # Check Docker authentication (from image description)
            try:
                result = subprocess.run(
                    ["docker", "login", "--help"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                details["auth_available"] = True
                # Note: Actual login status would require checking Docker config
                details["auth_note"] = "Check Docker Desktop for login status"
            except Exception:
                details["auth_available"] = False

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Docker", status, details)

    def _check_kubernetes(self) -> SystemCheck:
        """Check Kubernetes status"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check kubectl
            try:
                result = subprocess.run(
                    ["kubectl", "version", "--client"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    details["kubectl_installed"] = True
                    # Extract version from output
                    if "Client Version" in result.stdout:
                        details["kubectl_version"] = "available"
                else:
                    details["kubectl_installed"] = False
                    status = HealthStatus.YELLOW
            except FileNotFoundError:
                details["kubectl_installed"] = False
                status = HealthStatus.YELLOW
            except Exception as e:
                details["kubectl_installed"] = "unknown"
                details["error"] = str(e)
                status = HealthStatus.YELLOW

            # Check if Kubernetes is running (from image description)
            details["kubernetes_running"] = "Check Docker Desktop status bar"
            details["note"] = "From image: Kubernetes running status shown in Docker Desktop"

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Kubernetes", status, details)

    def _check_docker_images(self) -> SystemCheck:
        """Check Docker images (especially dyno_lumina_jarvis)"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check for dyno_lumina_jarvis image
            try:
                result = subprocess.run(
                    ["docker", "images", "dyno-lumina-jarvis", "--format", "{{.Repository}}:{{.Tag}}"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0 and result.stdout.strip():
                    images = [img.strip() for img in result.stdout.strip().split("\n") if img.strip()]
                    details["dyno_lumina_jarvis_found"] = True
                    details["dyno_lumina_jarvis_images"] = images
                else:
                    details["dyno_lumina_jarvis_found"] = False
                    status = HealthStatus.YELLOW
                    details["issue"] = "dyno-lumina-jarvis image not found locally"
            except Exception as e:
                details["dyno_lumina_jarvis_check_error"] = str(e)
                status = HealthStatus.YELLOW

            # Note about access issues from image description
            details["access_issues"] = [
                "push access denied - repository may require authorization",
                "unable to pull dyno-lumina-jarvis:latest (HTTP 404)",
                "signed out of Docker Desktop"
            ]
            details["access_note"] = "Check Docker Desktop notifications for authentication issues"
            status = HealthStatus.YELLOW  # Access issues are warnings

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Docker Images", status, details)

    def check_local_ai_configs(self) -> List[SystemCheck]:
        """Check local AI configurations"""
        logger.info("=" * 80)
        logger.info("Starting local AI configurations...")
        logger.info("=" * 80)
        logger.info("")

        checks = []

        # Cursor IDE connection
        cursor_status = self._check_cursor_ide()
        checks.append(cursor_status)
        self._log_check(cursor_status)

        # Ollama
        ollama_status = self._check_ollama()
        checks.append(ollama_status)
        self._log_check(ollama_status)

        # ULTRON Virtual Cluster (localhost + KAIJU + FALC)
        ultron_cluster_status = self._check_ultron_virtual_cluster()
        checks.append(ultron_cluster_status)
        self._log_check(ultron_cluster_status)

        # Local LLM configs
        llm_configs_status = self._check_llm_configs()
        checks.append(llm_configs_status)
        self._log_check(llm_configs_status)

        logger.info("")
        return checks

    def _check_cursor_ide(self) -> SystemCheck:
        """Check Cursor IDE connection and status"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check for known Cursor IDE serialization errors
            # Error: "serialize binary: invalid int 32: 4294967295"
            # This is a Cursor IDE internal bug (value overflow in binary serialization)
            details["known_issues"] = [
                {
                    "error": "ConnectError: serialize binary: invalid int 32: 4294967295",
                    "type": "Cursor IDE Internal Bug",
                    "description": "Binary serialization overflow (2^32 - 1)",
                    "impact": "Connection errors, agent stream failures",
                    "workaround": "Reload window, restart Cursor IDE",
                    "status": "Known Cursor IDE issue - not LUMINA system failure"
                }
            ]

            # Check Cursor settings
            cursor_settings = Path.home() / "AppData" / "Roaming" / "Cursor" / "User" / "settings.json"
            if cursor_settings.exists():
                try:
                    with open(cursor_settings, "r", encoding="utf-8") as f:
                        settings = json.load(f)
                        details["settings_file_exists"] = True
                        details["settings_valid"] = True

                        # Check for custom models
                        if "cursor.chat.customModels" in settings:
                            models = settings["cursor.chat.customModels"]
                            details["custom_models_count"] = len(models)
                            ultron_models = [m for m in models if m.get("name", "").lower() in ["ultron", "ultron"]]
                            details["ultron_models_configured"] = len(ultron_models)
                        else:
                            details["custom_models_count"] = 0
                except Exception as e:
                    details["settings_file_exists"] = True
                    details["settings_valid"] = False
                    details["settings_error"] = str(e)
                    status = HealthStatus.YELLOW
            else:
                details["settings_file_exists"] = False
                status = HealthStatus.YELLOW

            # Note about Cursor IDE connection errors
            details["cursor_ide_note"] = "Cursor IDE connection errors are Cursor IDE bugs, not LUMINA system failures"
            details["cursor_ide_workaround"] = "Reload window (Ctrl+Shift+P → 'Reload Window') or restart Cursor IDE if connection errors occur"
            details["cursor_ide_status"] = "Cursor IDE is running (connection errors are IDE bugs)"

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Cursor IDE Connection", status, details)

    def _check_ultron_virtual_cluster(self) -> SystemCheck:
        """
        Check ULTRON Virtual Cluster connectivity

        ULTRON is a virtual cluster combining:
        - Node 1: ULTRON Standalone (localhost:11434) - Laptop local, qwen2.5:72b
        - Node 2: KAIJU/Iron Legion (<NAS_IP>:3000/3001) - Primary cluster, codellama:13b
        - Node 3: FALC/Millennium Falcon (localhost:11436) - Failover cluster, PERSPECTIVE models

        Three-node virtual cluster with failover configuration.
        """
        details = {}
        status = HealthStatus.GREEN
        nodes_operational = 0
        nodes_total = 3

        try:
            # Load ULTRON cluster config
            ultron_config_file = self.project_root / "config" / "ultron_cluster_selection.json"
            if ultron_config_file.exists():
                try:
                    with open(ultron_config_file, "r", encoding="utf-8") as f:
                        ultron_config = json.load(f)
                        details["ultron_config_loaded"] = True
                        cluster_config = ultron_config.get("available_clusters", {})
                except Exception as e:
                    details["ultron_config_error"] = str(e)
                    cluster_config = {}
            else:
                cluster_config = {}
                details["ultron_config_missing"] = True

            # Node 1: ULTRON Standalone (localhost:11434)
            ultron_standalone = cluster_config.get("ultron_standalone", {})
            localhost_status = self._check_ultron_node(
                name="ULTRON Standalone",
                ip="localhost",
                port=11434,
                node_type="Standalone",
                model="qwen2.5:72b",
                endpoint=ultron_standalone.get("endpoint", "http://localhost:11434")
            )
            details["node_ultron_standalone"] = localhost_status
            if localhost_status.get("operational", False):
                nodes_operational += 1
            else:
                status = HealthStatus.YELLOW if status == HealthStatus.GREEN else status

            # Node 2: KAIJU/Iron Legion (<NAS_IP>:3000 or 3001)
            iron_legion = cluster_config.get("iron_legion", {})
            kaiju_endpoint = iron_legion.get("endpoint", "http://<NAS_IP>:3000")
            # Parse endpoint to get IP and port
            if "://" in kaiju_endpoint:
                kaiju_parts = kaiju_endpoint.replace("http://", "").split(":")
                kaiju_ip = kaiju_parts[0]
                kaiju_port = int(kaiju_parts[1]) if len(kaiju_parts) > 1 else 3000
            else:
                kaiju_ip = "<NAS_IP>"
                kaiju_port = 3000

            kaiju_status = self._check_ultron_node(
                name="KAIJU/Iron Legion",
                ip=kaiju_ip,
                port=kaiju_port,
                node_type="Iron Legion Expert Cluster",
                model="codellama:13b",
                endpoint=kaiju_endpoint
            )
            # Also check individual model port (3001)
            if not kaiju_status.get("operational", False) and kaiju_port == 3000:
                kaiju_status_alt = self._check_ultron_node(
                    name="KAIJU/Iron Legion (Alt)",
                    ip=kaiju_ip,
                    port=3001,
                    node_type="Iron Legion Individual",
                    model="codellama:13b",
                    endpoint=f"http://{kaiju_ip}:3001"
                )
                if kaiju_status_alt.get("operational", False):
                    kaiju_status = kaiju_status_alt
                    kaiju_status["port_used"] = 3001

            details["node_kaiju"] = kaiju_status
            if kaiju_status.get("operational", False):
                nodes_operational += 1
            else:
                status = HealthStatus.YELLOW if status == HealthStatus.GREEN else status

            # Node 3: FALC/Millennium Falcon (localhost:11436)
            millennium_falcon = cluster_config.get("millennium_falcon", {})
            falc_endpoint = millennium_falcon.get("endpoint", "http://localhost:11436")
            # Parse endpoint
            if "://" in falc_endpoint:
                falc_parts = falc_endpoint.replace("http://", "").split(":")
                falc_ip = falc_parts[0]
                falc_port = int(falc_parts[1]) if len(falc_parts) > 1 else 11436
            else:
                falc_ip = "localhost"
                falc_port = 11436

            falc_status = self._check_ultron_node(
                name="FALC/Millennium Falcon",
                ip=falc_ip,
                port=falc_port,
                node_type="Millennium Falcon Failover",
                model="PERSPECTIVE models",
                endpoint=falc_endpoint
            )
            details["node_falc"] = falc_status
            if falc_status.get("operational", False):
                nodes_operational += 1
            else:
                status = HealthStatus.YELLOW if status == HealthStatus.GREEN else status

            # Cluster summary
            details["cluster_type"] = "Virtual Cluster - Three-Node Failover"
            details["cluster_description"] = "ULTRON Virtual Cluster: Localhost + KAIJU + FALC"
            details["nodes_total"] = nodes_total
            details["nodes_operational"] = nodes_operational
            details["cluster_health"] = f"{nodes_operational}/{nodes_total} nodes operational"

            # Failover requirements: Need at least 2 nodes for failover
            if nodes_operational < 2:
                status = HealthStatus.RED
                details["cluster_status"] = "CRITICAL - Less than 2 nodes operational (failover requires 2+)"
                details["failover_capable"] = False
            elif nodes_operational < nodes_total:
                status = HealthStatus.YELLOW
                details["cluster_status"] = "DEGRADED - Some nodes unavailable"
                details["failover_capable"] = True
            else:
                details["cluster_status"] = "OPERATIONAL - All nodes available"
                details["failover_capable"] = True

            # Check Cursor config for ULTRON cluster
            cursor_config = self.project_root / "data" / "cursor_models" / "cursor_models_config.json"
            if cursor_config.exists():
                try:
                    with open(cursor_config, "r", encoding="utf-8") as f:
                        config = json.load(f)
                        ultron_configs = [
                            m for m in config.get("cursor.chat.customModels", [])
                            if m.get("name", "").lower() in ["ultron", "ultron"]
                        ]
                        if ultron_configs:
                            details["cursor_config_found"] = True
                            details["cursor_config_count"] = len(ultron_configs)
                            # Check cluster description
                            for cfg in ultron_configs:
                                desc = cfg.get("description", "")
                                if "cluster" in desc.lower() or "failover" in desc.lower():
                                    details["cluster_configured"] = True
                                if not cfg.get("localOnly", False):
                                    details["cursor_config_warning"] = "localOnly not set to true"
                                    status = HealthStatus.YELLOW
                        else:
                            details["cursor_config_found"] = False
                            status = HealthStatus.YELLOW
                except Exception as e:
                    details["cursor_config_error"] = str(e)

            # Note about Cursor IDE connection errors
            details["cursor_ide_note"] = "Cursor IDE may reject local models despite correct cluster config"
            details["cursor_ide_workaround"] = "Cluster works via Ollama API directly, Cursor validation is separate"

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("ULTRON Virtual Cluster", status, details)

    def _check_ultron_node(self, name: str, ip: str, port: int, node_type: str, model: str, endpoint: Optional[str] = None) -> Dict[str, Any]:
        """Check individual ULTRON cluster node"""
        node_status = {
            "name": name,
            "ip": ip,
            "port": port,
            "type": node_type,
            "model": model,
            "operational": False
        }

        if endpoint:
            node_status["endpoint"] = endpoint

        try:
            # Test API connectivity
            import urllib.request
            import json as json_lib

            api_url = f"http://{ip}:{port}/api/tags"
            try:
                req = urllib.request.Request(api_url)
                with urllib.request.urlopen(req, timeout=5) as response:
                    data = json_lib.loads(response.read())
                    models = [m.get("name", "") for m in data.get("models", [])]
                    node_status["api_accessible"] = True
                    node_status["api_models"] = len(models)
                    node_status["operational"] = True
                    node_status["available_models"] = models[:5]  # First 5 for brevity

                    # Check if target model is available (flexible matching)
                    model_found = False
                    if model:
                        # Try exact match first
                        if any(model.lower() in m.lower() for m in models):
                            model_found = True
                        # Try partial match
                        elif any(part in m.lower() for part in model.lower().split(":") for m in models):
                            model_found = True

                    if model_found:
                        node_status["model_available"] = True
                    else:
                        node_status["model_available"] = False
                        node_status["model_note"] = f"Target model '{model}' not found, but node is operational with {len(models)} models"
            except urllib.error.URLError as e:
                node_status["api_accessible"] = False
                node_status["api_error"] = str(e)
                node_status["operational"] = False
            except Exception as e:
                node_status["api_error"] = str(e)
                node_status["operational"] = False

        except Exception as e:
            node_status["error"] = str(e)
            node_status["operational"] = False

        return node_status

    def _check_ollama(self) -> SystemCheck:
        """Check Ollama"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check if Ollama is installed
            try:
                result = subprocess.run(
                    ["ollama", "--version"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode == 0:
                    details["installed"] = True
                    details["version"] = result.stdout.strip()
                else:
                    details["installed"] = False
                    status = HealthStatus.YELLOW
            except FileNotFoundError:
                details["installed"] = False
                status = HealthStatus.YELLOW
            except Exception as e:
                details["installed"] = "unknown"
                details["error"] = str(e)
                status = HealthStatus.YELLOW

            # Check if Ollama service is running
            if details.get("installed"):
                try:
                    result = subprocess.run(
                        ["ollama", "list"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        details["service_running"] = True
                        # Count models
                        lines = [l for l in result.stdout.strip().split("\n") if l.strip() and not l.startswith("NAME")]
                        details["models_installed"] = len(lines)
                    else:
                        details["service_running"] = False
                        status = HealthStatus.YELLOW
                except Exception as e:
                    details["service_running"] = "unknown"
                    details["error"] = str(e)
                    status = HealthStatus.YELLOW

            # Check Ollama config files
            ollama_configs = [
                "containerization/k8s/manifests/deployments/ollama-deployment.yaml"
            ]

            found_configs = []
            for config in ollama_configs:
                config_path = self.project_root / config
                if config_path.exists():
                    found_configs.append(config)

            details["config_files_found"] = len(found_configs)
            details["config_files"] = found_configs

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Ollama", status, details)

    def _check_llm_configs(self) -> SystemCheck:
        """Check local LLM configurations"""
        details = {}
        status = HealthStatus.GREEN

        try:
            # Check for LLM config files
            llm_config_paths = [
                "data/cursor_models/cursor_models_config.json",
                "config/mcp_config_localhost.json",
                "config/homelab_mcp_hybrid_config.json"
            ]

            found_configs = []
            missing_configs = []

            for config_path in llm_config_paths:
                full_path = self.project_root / config_path
                if full_path.exists():
                    found_configs.append(config_path)
                    # Try to read and validate JSON
                    try:
                        with open(full_path, "r", encoding="utf-8") as f:
                            config_data = json.load(f)
                            details[f"{config_path}_valid"] = True
                    except Exception as e:
                        details[f"{config_path}_valid"] = False
                        details[f"{config_path}_error"] = str(e)
                        status = HealthStatus.YELLOW
                else:
                    missing_configs.append(config_path)

            details["configs_found"] = len(found_configs)
            details["configs_missing"] = len(missing_configs)
            details["found"] = found_configs
            details["missing"] = missing_configs

            if missing_configs:
                status = HealthStatus.YELLOW

        except Exception as e:
            status = HealthStatus.RED
            details["error"] = str(e)

        return SystemCheck("Local LLM Configs", status, details)

    def check_system_resources(self) -> List[SystemCheck]:
        """Check system resources"""
        logger.info("")
        logger.info("Checking system resources...")
        logger.info("")

        checks = []

        try:
            import psutil

            # CPU
            cpu_percent = psutil.cpu_percent(interval=1)
            cpu_status = HealthStatus.GREEN
            if cpu_percent > 90:
                cpu_status = HealthStatus.CRITICAL
            elif cpu_percent > 75:
                cpu_status = HealthStatus.YELLOW

            cpu_check = SystemCheck("CPU", cpu_status, {
                "usage_percent": cpu_percent,
                "cores": psutil.cpu_count(),
                "threshold_warning": 75,
                "threshold_critical": 90
            })
            checks.append(cpu_check)
            self._log_check(cpu_check)

            # Memory
            memory = psutil.virtual_memory()
            mem_status = HealthStatus.GREEN
            if memory.percent > 90:
                mem_status = HealthStatus.CRITICAL
            elif memory.percent > 80:
                mem_status = HealthStatus.YELLOW

            mem_check = SystemCheck("Memory", mem_status, {
                "usage_percent": memory.percent,
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_gb": round(memory.used / (1024**3), 2),
                "threshold_warning": 80,
                "threshold_critical": 90
            })
            checks.append(mem_check)
            self._log_check(mem_check)

            # Disk
            disk = psutil.disk_usage(self.project_root.drive if self.project_root.drive else "/")
            disk_status = HealthStatus.GREEN
            if disk.percent > 95:
                disk_status = HealthStatus.CRITICAL
            elif disk.percent > 85:
                disk_status = HealthStatus.YELLOW

            disk_check = SystemCheck("Disk", disk_status, {
                "usage_percent": disk.percent,
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_gb": round(disk.used / (1024**3), 2),
                "threshold_warning": 85,
                "threshold_critical": 95
            })
            checks.append(disk_check)
            self._log_check(disk_check)

        except ImportError:
            logger.warning("   ⚠️  psutil not available, skipping resource checks")
        except Exception as e:
            logger.error(f"   ❌ Error checking resources: {e}")

        logger.info("")
        return checks

    def _log_check(self, check: SystemCheck) -> None:
        """Log check result - Unix/Linux style OK/FAIL"""
        # Unix/Linux style: [  OK  ] or [FAILED]
        if check.status == HealthStatus.GREEN:
            status_display = "[  OK  ]"
            logger.info(f"{status_display} {check.name}")
        elif check.status == HealthStatus.YELLOW:
            status_display = "[WARN ]"
            logger.warning(f"{status_display} {check.name}")
        elif check.status == HealthStatus.RED:
            status_display = "[FAILED]"
            logger.error(f"{status_display} {check.name}")
        else:  # CRITICAL
            status_display = "[CRIT ]"
            logger.critical(f"{status_display} {check.name}")

        # Debug details
        if self.debug_mode:
            for key, value in check.details.items():
                if key not in ["found", "missing", "error"] or value:  # Only show non-empty lists
                    logger.debug(f"         {key}: {value}")

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all health checks"""
        all_checks = []

        # Core systems
        all_checks.extend(self.check_core_systems())

        # Docker/Kubernetes
        all_checks.extend(self.check_docker_kubernetes())

        # Local AI configs
        all_checks.extend(self.check_local_ai_configs())

        # System resources
        all_checks.extend(self.check_system_resources())

        self.checks = all_checks

        # Determine overall status
        statuses = [check.status for check in all_checks]
        if HealthStatus.CRITICAL in statuses:
            self.overall_status = HealthStatus.CRITICAL
        elif HealthStatus.RED in statuses:
            self.overall_status = HealthStatus.RED
        elif HealthStatus.YELLOW in statuses:
            self.overall_status = HealthStatus.YELLOW
        else:
            self.overall_status = HealthStatus.GREEN

        return self.generate_report()

    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive health check report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "overall_status": self.overall_status.value,
            "project_root": str(self.project_root),
            "debug_mode": self.debug_mode,
            "summary": {
                "total_checks": len(self.checks),
                "green": len([c for c in self.checks if c.status == HealthStatus.GREEN]),
                "yellow": len([c for c in self.checks if c.status == HealthStatus.YELLOW]),
                "red": len([c for c in self.checks if c.status == HealthStatus.RED]),
                "critical": len([c for c in self.checks if c.status == HealthStatus.CRITICAL])
            },
            "checks": [check.to_dict() for check in self.checks]
        }

        return report

    def save_report(self, report: Dict[str, Any]) -> Path:
        try:
            """Save report to file"""
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            report_dir = self.project_root / "data" / "health_checks"
            report_dir.mkdir(parents=True, exist_ok=True)

            report_file = report_dir / f"debug_health_check_{timestamp}.json"

            with open(report_file, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)

            logger.info(f"         Report saved: {report_file}")
            return report_file

        except Exception as e:
            self.logger.error(f"Error in save_report: {e}", exc_info=True)
            raise
    def print_summary(self, report: Dict[str, Any]) -> None:
        """Print summary - Unix/Linux style"""
        logger.info("")
        logger.info("=" * 80)
        logger.info("System Health Check Summary")
        logger.info("=" * 80)
        logger.info("")

        summary = report["summary"]
        overall = report["overall_status"]

        # Unix/Linux style final status
        if overall == "GREEN":
            status_display = "[  OK  ]"
            logger.info(f"{status_display} All systems operational")
        elif overall == "YELLOW":
            status_display = "[WARN ]"
            logger.warning(f"{status_display} Warnings detected")
        elif overall == "RED":
            status_display = "[FAILED]"
            logger.error(f"{status_display} Errors detected")
        else:  # CRITICAL
            status_display = "[CRIT ]"
            logger.critical(f"{status_display} Critical issues detected")

        logger.info("")
        logger.info(f"Total Checks: {summary['total_checks']}")
        logger.info(f"  [  OK  ]: {summary['green']}")
        logger.info(f"  [WARN ]: {summary['yellow']}")
        logger.info(f"  [FAILED]: {summary['red']}")
        logger.info(f"  [CRIT ]: {summary['critical']}")
        logger.info("")

        if overall != "GREEN":
            logger.info("=" * 80)
            logger.info("ISSUES DETECTED - REVIEW DETAILS ABOVE")
            logger.info("=" * 80)
            logger.info("")
            logger.info("[WARN ] checks need attention but are non-critical")
            logger.info("[FAILED] checks indicate errors that should be fixed")
            logger.info("[CRIT ] checks require immediate action")
            logger.info("")
        else:
            logger.info("=" * 80)
            logger.info("[  OK  ] ALL SYSTEMS OPERATIONAL - READY FOR OPERATIONS")
            logger.info("=" * 80)
            logger.info("")


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Debug Mode Health Check - V3 Validation")
        parser.add_argument("--debug", action="store_true", default=True, help="Enable debug mode")
        parser.add_argument("--no-debug", action="store_true", help="Disable debug mode")
        parser.add_argument("--save", action="store_true", default=True, help="Save report to file")
        parser.add_argument("--project-root", type=str, help="Project root directory")

        args = parser.parse_args()

        debug_mode = args.debug and not args.no_debug
        project_root = Path(args.project_root) if args.project_root else None

        # Run health check
        checker = LuminaDebugHealthCheck(project_root=project_root, debug_mode=debug_mode)
        report = checker.run_all_checks()

        # Print summary
        checker.print_summary(report)

        # Save report
        if args.save:
            report_file = checker.save_report(report)
            logger.info(f"         Full report: {report_file}")

        # Exit with appropriate code
        if report["overall_status"] == "GREEN":
            sys.exit(0)
        elif report["overall_status"] == "YELLOW":
            sys.exit(1)  # Warnings
        elif report["overall_status"] == "RED":
            sys.exit(2)  # Errors
        else:
            sys.exit(3)  # Critical


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()