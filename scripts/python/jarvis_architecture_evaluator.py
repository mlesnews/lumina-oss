#!/usr/bin/env python3
"""
JARVIS Architecture Evaluator
Evaluates system architecture and recommends optimal service placement.

Tags: #ARCHITECTURE #EVALUATION #ENGINEERING @AUTO
"""

import sys
import json
import socket
import requests
import subprocess
from pathlib import Path
from typing import Dict, Any, Optional, List
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

logger = get_logger("JARVISArchitecture")


class ArchitectureEvaluator:
    """
    Architecture Evaluator

    Evaluates current system architecture and recommends optimal service placement
    based on hardware capabilities and requirements.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # System definitions
        self.systems = {
            "ULTRON": {
                "type": "local_machine",
                "ip": "localhost",
                "description": "Current development machine",
                "capabilities": ["docker", "ollama", "python"]
            },
            "KAIJU_NO_8": {
                "type": "desktop_pc",
                "hostname": "kaiju_no_8",
                "ip": "<NAS_IP>",  # Resolved from hostname
                "hardware": {
                    "cpu": "AMD Ryzen 9 5950X 16-Core Processor (16C/32T, 4.2GHz)",
                    "gpu": "NVIDIA GeForce RTX 3090 (24GB VRAM)",
                    "ram": "64GB"
                },
                "description": "Desktop PC with GPU - optimal for GPU workloads",
                "capabilities": ["docker", "ollama", "gpu", "python", "windows"]
            },
            "NAS": {
                "type": "nas",
                "ip": "<NAS_PRIMARY_IP>",
                "model": "Synology DS1821plus",
                "description": "Storage server with DPM (Docker Package Manager)",
                "capabilities": ["docker", "storage", "backups", "dpm"],
                "constraints": ["cpu_only", "limited_ram", "balance_required"]
            }
        }

        self.logger.info("✅ Architecture Evaluator initialized")

    def _resolve_hostname(self, hostname: str) -> Optional[str]:
        """Resolve hostname to IP address"""
        try:
            ip = socket.gethostbyname(hostname)
            return ip
        except socket.gaierror:
            return None

    def _check_service(self, ip: str, port: int, service_name: str) -> Dict[str, Any]:
        """Check if a service is running on a specific IP:port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((ip, port))
            sock.close()

            if result == 0:
                return {"running": True, "accessible": True}
            else:
                return {"running": False, "accessible": False}
        except Exception as e:
            return {"running": False, "accessible": False, "error": str(e)}

    def _check_ollama(self, ip: str, port: int = 11434) -> Dict[str, Any]:
        """Check Ollama service - try multiple ports and check if installed"""
        # Try multiple ports (Ollama can run on different ports)
        ports_to_try = [port, 11437, 11434, 3000, 8080]  # Common Ollama ports

        for test_port in ports_to_try:
            try:
                response = requests.get(f"http://{ip}:{test_port}/api/tags", timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    return {
                        "running": True,
                        "accessible": True,
                        "port": test_port,
                        "models": [m.get("name") for m in models],
                        "model_count": len(models)
                    }
            except Exception:
                continue

        # If not accessible via API, check if port is open (might be running but not network-accessible)
        port_check = self._check_service(ip, port, "Ollama")
        if port_check.get("running"):
            # Port is open but API not responding - might be configured differently
            return {
                **port_check,
                "port": port,
                "models": [],
                "model_count": 0,
                "note": "Port open but API not accessible - may be configured locally only"
            }

        return {**port_check, "port": port, "models": [], "model_count": 0}

    def evaluate_current_architecture(self) -> Dict[str, Any]:
        """Evaluate current system architecture"""
        self.logger.info("="*80)
        self.logger.info("ARCHITECTURE EVALUATION")
        self.logger.info("="*80)

        # Resolve KAIJU_NO_8 IP
        kaiju_ip = self._resolve_hostname("kaiju_no_8")
        if kaiju_ip:
            self.systems["KAIJU_NO_8"]["ip"] = kaiju_ip
            self.logger.info(f"✅ Resolved KAIJU_NO_8: {kaiju_ip}")
        else:
            self.logger.warning("⚠️  Could not resolve kaiju_no_8 hostname, using default <NAS_IP>")

        evaluation = {
            "timestamp": datetime.now().isoformat(),
            "systems": {},
            "services": {},
            "recommendations": []
        }

        # Evaluate each system
        for system_name, system_info in self.systems.items():
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"EVALUATING: {system_name}")
            self.logger.info(f"{'='*80}")

            ip = system_info.get("ip", "localhost")
            system_eval = {
                "type": system_info["type"],
                "ip": ip,
                "description": system_info.get("description", ""),
                "capabilities": system_info.get("capabilities", []),
                "services": {}
            }

            if "hardware" in system_info:
                system_eval["hardware"] = system_info["hardware"]

            # Check services
            if system_name == "ULTRON":
                # Check local Ollama
                ollama_status = self._check_ollama("localhost", 11434)
                system_eval["services"]["ollama"] = ollama_status
                self.logger.info(f"   Ollama (localhost:11434): {'✅ RUNNING' if ollama_status.get('running') else '❌ NOT RUNNING'}")
                if ollama_status.get("model_count", 0) > 0:
                    self.logger.info(f"   Models: {ollama_status.get('model_count')} available")

            elif system_name == "KAIJU_NO_8":
                # Check KAIJU_NO_8 services
                ollama_status = self._check_ollama(ip, 11434)
                system_eval["services"]["ollama"] = ollama_status
                self.logger.info(f"   Ollama ({ip}:11434): {'✅ RUNNING' if ollama_status.get('running') else '❌ NOT RUNNING'}")
                if ollama_status.get("model_count", 0) > 0:
                    self.logger.info(f"   Models: {ollama_status.get('model_count')} available")

                # Check MCP Server
                mcp_status = self._check_service(ip, 8000, "MCP Server")
                system_eval["services"]["mcp_server"] = mcp_status
                self.logger.info(f"   MCP Server ({ip}:8000): {'✅ RUNNING' if mcp_status.get('running') else '❌ NOT RUNNING'}")

                # Check ULTRON Router
                router_status = self._check_service(ip, 3008, "ULTRON Router")
                system_eval["services"]["ultron_router"] = router_status
                self.logger.info(f"   ULTRON Router ({ip}:3008): {'✅ RUNNING' if router_status.get('running') else '❌ NOT RUNNING'}")

            elif system_name == "NAS":
                # Check NAS services
                ollama_status = self._check_ollama(ip, 11434)
                system_eval["services"]["ollama"] = ollama_status
                self.logger.info(f"   Ollama ({ip}:11434): {'✅ RUNNING' if ollama_status.get('running') else '❌ NOT RUNNING'}")
                if ollama_status.get("model_count", 0) > 0:
                    self.logger.info(f"   Models: {ollama_status.get('model_count')} available")

                # Check MCP Server
                mcp_status = self._check_service(ip, 8000, "MCP Server")
                system_eval["services"]["mcp_server"] = mcp_status
                self.logger.info(f"   MCP Server ({ip}:8000): {'✅ RUNNING' if mcp_status.get('running') else '❌ NOT RUNNING'}")

            evaluation["systems"][system_name] = system_eval

        # Generate recommendations
        recommendations = self._generate_recommendations(evaluation)
        evaluation["recommendations"] = recommendations

        # Print recommendations
        self.logger.info(f"\n{'='*80}")
        self.logger.info("RECOMMENDATIONS")
        self.logger.info(f"{'='*80}")
        for i, rec in enumerate(recommendations, 1):
            self.logger.info(f"\n{i}. {rec.get('title', 'Recommendation')}")
            self.logger.info(f"   Priority: {rec.get('priority', 'medium')}")
            self.logger.info(f"   Reason: {rec.get('reason', '')}")
            if rec.get("actions"):
                self.logger.info(f"   Actions:")
                for action in rec["actions"]:
                    self.logger.info(f"      - {action}")

        return evaluation

    def _generate_recommendations(self, evaluation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate architecture recommendations"""
        recommendations = []

        kaiju = evaluation["systems"].get("KAIJU_NO_8", {})
        nas = evaluation["systems"].get("NAS", {})

        # Check if services are on wrong systems
        nas_ollama = nas.get("services", {}).get("ollama", {}).get("running", False)
        kaiju_ollama = kaiju.get("services", {}).get("ollama", {}).get("running", False)

        if nas_ollama and not kaiju_ollama:
            recommendations.append({
                "title": "Move Ollama from NAS to KAIJU_NO_8",
                "priority": "high",
                "reason": "Ollama is running on NAS (CPU-only) but should run on KAIJU_NO_8 (GPU-enabled desktop) for optimal performance",
                "actions": [
                    "Stop Ollama on NAS (<NAS_PRIMARY_IP>)",
                    "Deploy Ollama on KAIJU_NO_8 (<NAS_IP>) with GPU support",
                    "Configure Ollama to use RTX 3090 GPU",
                    "Pull hardware-appropriate models (1B-13B range for 24GB VRAM)"
                ]
            })

        if not kaiju_ollama:
            # Note: User confirmed Ollama is already setup on KAIJU_NO_8
            # May not be accessible from this network location
            recommendations.append({
                "title": "Verify Ollama Configuration on KAIJU_NO_8",
                "priority": "medium",
                "reason": "Ollama is setup on KAIJU_NO_8 but not accessible from this location. Verify configuration and GPU utilization.",
                "actions": [
                    "Verify Ollama is running on KAIJU_NO_8 (check Docker containers or services)",
                    "Verify GPU acceleration is enabled (OLLAMA_NUM_GPU=1)",
                    "Check GPU utilization reaches 50% target",
                    "Pull hardware-appropriate models if needed (using IDM CLI)",
                    "Verify firewall/network access if needed"
                ]
            })

        # NAS recommendations
        nas_services = nas.get("services", {})
        if nas_ollama:
            recommendations.append({
                "title": "Consider removing Ollama from NAS",
                "priority": "medium",
                "reason": "NAS is CPU-only and should focus on storage/backups. GPU workloads belong on KAIJU_NO_8. Remember: BALANCE!",
                "actions": [
                    "Evaluate if NAS Ollama is needed for CPU-only fallback",
                    "If not needed, remove to free NAS resources",
                    "Use NAS DPM (Docker Package Manager) only for storage-related containers"
                ]
            })

        # MCP Server recommendations
        nas_mcp = nas.get("services", {}).get("mcp_server", {}).get("running", False)
        kaiju_mcp = kaiju.get("services", {}).get("mcp_server", {}).get("running", False)

        if not kaiju_mcp and not nas_mcp:
            recommendations.append({
                "title": "Deploy MCP Server (R5 API)",
                "priority": "medium",
                "reason": "MCP Server provides triage, AIQ consensus, and JediCouncil escalation. Should run on KAIJU_NO_8 for centralized access.",
                "actions": [
                    "Deploy MCP Server on KAIJU_NO_8 (<NAS_IP>:8000)",
                    "Copy required Python modules (r5_api_server.py, r5_living_context_matrix.py, etc.)",
                    "Install dependencies (flask, flask-cors, requests)",
                    "Start server with nohup and PYTHONPATH"
                ]
            })

        # ULTRON Router recommendations
        kaiju_router = kaiju.get("services", {}).get("ultron_router", {}).get("running", False)
        if not kaiju_router:
            recommendations.append({
                "title": "Deploy ULTRON Router on KAIJU_NO_8",
                "priority": "low",
                "reason": "ULTRON Router provides intelligent routing between LLM endpoints. Can run on KAIJU_NO_8 or remain local.",
                "actions": [
                    "Evaluate if ULTRON Router is needed",
                    "If needed, deploy on KAIJU_NO_8 (<NAS_IP>:3008)",
                    "Configure routing rules for ULTRON and KAIJU endpoints"
                ]
            })

        return recommendations

    def save_evaluation(self, evaluation: Dict[str, Any], filename: Optional[str] = None) -> Path:
        try:
            """Save evaluation to JSON file"""
            if not filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"architecture_evaluation_{timestamp}.json"

            output_path = self.project_root / "data" / "architecture" / filename
            output_path.parent.mkdir(parents=True, exist_ok=True)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(evaluation, f, indent=2, default=str)

            self.logger.info(f"✅ Evaluation saved to: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in save_evaluation: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Architecture Evaluator")
        parser.add_argument("--evaluate", action="store_true", help="Evaluate current architecture")
        parser.add_argument("--save", action="store_true", help="Save evaluation to file")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        evaluator = ArchitectureEvaluator(project_root)

        if args.evaluate or not args.evaluate:  # Default to evaluate
            evaluation = evaluator.evaluate_current_architecture()

            if args.save:
                evaluator.save_evaluation(evaluation)
            else:
                print(json.dumps(evaluation, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()