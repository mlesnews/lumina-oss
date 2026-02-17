#!/usr/bin/env python3
"""
JARVIS KAIJU Ollama Verifier
Verifies Ollama setup on KAIJU_NO_8 and provides status/startup guidance.

Tags: #VERIFICATION #KAIJU #OLLAMA @AUTO
"""

import sys
import requests
import socket
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

logger = get_logger("JARVISKAIJUOllama")


class KAIJUOllamaVerifier:
    """
    Verify Ollama setup on KAIJU_NO_8

    Checks if Ollama is:
    - Installed
    - Running
    - Accessible
    - Configured with GPU
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.kaiju_ip = "<NAS_IP>"
        self.ollama_ports = [11434, 11437, 3000, 8080]  # Common Ollama ports

    def check_ollama_status(self) -> Dict[str, Any]:
        """Check Ollama status on KAIJU_NO_8"""
        self.logger.info("="*80)
        self.logger.info("KAIJU_NO_8 OLLAMA VERIFICATION")
        self.logger.info("="*80)

        status = {
            "kaiju_ip": self.kaiju_ip,
            "timestamp": datetime.now().isoformat(),
            "ports_checked": [],
            "ollama_found": False,
            "ollama_running": False,
            "ollama_accessible": False,
            "port": None,
            "models": [],
            "recommendations": []
        }

        # Check each port
        self.logger.info(f"\nChecking Ollama on KAIJU_NO_8 ({self.kaiju_ip})...")

        for port in self.ollama_ports:
            self.logger.info(f"   Checking port {port}...")
            port_status = {
                "port": port,
                "port_open": False,
                "ollama_accessible": False,
                "models": []
            }

            # Check if port is open
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(2)
                result = sock.connect_ex((self.kaiju_ip, port))
                sock.close()
                port_status["port_open"] = (result == 0)
            except Exception as e:
                port_status["error"] = str(e)

            # If port is open, try Ollama API
            if port_status["port_open"]:
                try:
                    response = requests.get(f"http://{self.kaiju_ip}:{port}/api/tags", timeout=5)
                    if response.status_code == 200:
                        port_status["ollama_accessible"] = True
                        models_data = response.json().get("models", [])
                        port_status["models"] = [m.get("name") for m in models_data]

                        if not status["ollama_found"]:
                            status["ollama_found"] = True
                            status["ollama_running"] = True
                            status["ollama_accessible"] = True
                            status["port"] = port
                            status["models"] = port_status["models"]

                            self.logger.info(f"   ✅ Ollama found on port {port}!")
                            self.logger.info(f"      Models: {len(port_status['models'])} available")
                            if port_status["models"]:
                                self.logger.info(f"      {', '.join(port_status['models'][:3])}")
                except Exception as e:
                    port_status["api_error"] = str(e)

            status["ports_checked"].append(port_status)

        # Generate recommendations
        if not status["ollama_found"]:
            status["recommendations"].append({
                "action": "check_docker_container",
                "description": "Ollama may be installed but not running. Check Docker Desktop on KAIJU_NO_8: docker ps -a | findstr ollama",
                "command": "docker ps -a | findstr ollama"
            })
            status["recommendations"].append({
                "action": "start_container",
                "description": "If container exists but stopped: docker start ollama",
                "command": "docker start ollama"
            })
            status["recommendations"].append({
                "action": "check_firewall",
                "description": "Verify Windows Firewall allows port 11434 on KAIJU_NO_8",
                "command": "Check Windows Firewall settings"
            })
        else:
            status["recommendations"].append({
                "action": "verify_gpu",
                "description": "Verify GPU acceleration is enabled: Check OLLAMA_NUM_GPU=1 in container",
                "command": "docker inspect ollama | findstr OLLAMA_NUM_GPU"
            })
            if not status["models"]:
                status["recommendations"].append({
                    "action": "pull_models",
                    "description": "Pull models using IDM CLI: python scripts/python/jarvis_ollama_idm_pull.py",
                    "command": "python scripts/python/jarvis_ollama_idm_pull.py"
                })

        # Summary
        self.logger.info("\n" + "="*80)
        self.logger.info("VERIFICATION SUMMARY")
        self.logger.info("="*80)

        if status["ollama_found"]:
            self.logger.info(f"✅ Ollama Status: RUNNING on port {status['port']}")
            self.logger.info(f"   Models: {len(status['models'])} available")
        else:
            self.logger.info("❌ Ollama Status: NOT ACCESSIBLE")
            self.logger.info("   Possible reasons:")
            self.logger.info("   - Ollama installed but container not started")
            self.logger.info("   - Running on non-standard port")
            self.logger.info("   - Firewall blocking access")
            self.logger.info("   - Not installed yet")

        if status["recommendations"]:
            self.logger.info("\n📋 Recommendations:")
            for i, rec in enumerate(status["recommendations"], 1):
                self.logger.info(f"   {i}. {rec['description']}")
                self.logger.info(f"      Command: {rec['command']}")

        return status


def main():
    try:
        """CLI interface"""
        project_root = Path(__file__).parent.parent.parent
        verifier = KAIJUOllamaVerifier(project_root)
        result = verifier.check_ollama_status()

        import json
        print("\n" + json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()