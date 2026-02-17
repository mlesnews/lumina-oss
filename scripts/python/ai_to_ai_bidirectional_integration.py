#!/usr/bin/env python3
"""
AI <=> AI Bidirectional Integration System

Creates bidirectional integration (<=>) between ALL AI systems:
- Sider.AI (WiseBase features)
- ROAMWISE.AI (Web frontend portal/gateway - .local network only)
- RoamResearch (Lifetime Account - Personal)
- Windows Copilot
- NAS AI Services
- Neo Browser AI
- Local AI (Ollama/ULTRON/KAIJU)
- Cloud AI Services

Tags: #AI #BIDIRECTIONAL #INTEGRATION #SIDER #ROAMWISE #ROAMRESEARCH #AI_TO_AI @JARVIS @LUMINA
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass, field

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

logger = get_logger("AIToAIBidirectional")


@dataclass
class AIService:
    """Represents an AI service"""
    name: str
    service_type: str  # sider, roamwise, roamresearch, copilot, nas_ai, neo_browser, local_ai, cloud_ai
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    available: bool = False
    capabilities: List[str] = field(default_factory=list)
    integration_method: Optional[str] = None  # api, cdp, cli, etc.


class AIToAIBidirectionalIntegration:
    """
    AI <=> AI Bidirectional Integration System

    Creates bidirectional communication and control between ALL AI systems.
    Each AI can communicate with and control other AIs.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize AI-to-AI bidirectional integration"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.config_dir = self.project_root / "config"
        self.config_dir.mkdir(parents=True, exist_ok=True)

        # AI services registry
        self.ai_services: Dict[str, AIService] = {}

        # Integration matrix (bidirectional)
        self.integration_matrix: Dict[str, Dict[str, bool]] = {}

        # Message bus for AI-to-AI communication
        self.message_bus: List[Dict[str, Any]] = []

        logger.info("✅ AI <=> AI Bidirectional Integration initialized")
        logger.info("   🔄 Bidirectional integration between ALL AI systems")

    def discover_all_ai_services(self) -> Dict[str, AIService]:
        """Discover all AI services available"""
        logger.info("=" * 80)
        logger.info("🔍 Discovering All AI Services")
        logger.info("=" * 80)
        logger.info("")

        # 1. Sider.AI
        logger.info("1️⃣  Discovering Sider.AI...")
        sider_ai = self._discover_sider_ai()
        if sider_ai:
            self.ai_services["sider"] = sider_ai
            logger.info(f"   ✅ Sider.AI: {sider_ai.name}")
        logger.info("")

        # 2. ROAMWISE.AI
        logger.info("2️⃣  Discovering ROAMWISE.AI...")
        roamwise_ai = self._discover_roamwise_ai()
        if roamwise_ai:
            self.ai_services["roamwise"] = roamwise_ai
            logger.info(f"   ✅ ROAMWISE.AI: {roamwise_ai.name}")
        logger.info("")

        # 3. RoamResearch
        logger.info("3️⃣  Discovering RoamResearch...")
        roamresearch = self._discover_roamresearch()
        if roamresearch:
            self.ai_services["roamresearch"] = roamresearch
            logger.info(f"   ✅ RoamResearch: {roamresearch.name}")
        logger.info("")

        # 4. Windows Copilot
        logger.info("4️⃣  Discovering Windows Copilot...")
        copilot = self._discover_windows_copilot()
        if copilot:
            self.ai_services["windows_copilot"] = copilot
            logger.info(f"   ✅ Windows Copilot: {copilot.name}")
        logger.info("")

        # 5. NAS AI Services
        logger.info("5️⃣  Discovering NAS AI Services...")
        nas_ai = self._discover_nas_ai()
        if nas_ai:
            self.ai_services["nas_ai"] = nas_ai
            logger.info(f"   ✅ NAS AI: {nas_ai.name}")
        logger.info("")

        # 6. Neo Browser AI
        logger.info("6️⃣  Discovering Neo Browser AI...")
        neo_ai = self._discover_neo_browser_ai()
        if neo_ai:
            self.ai_services["neo_browser"] = neo_ai
            logger.info(f"   ✅ Neo Browser AI: {neo_ai.name}")
        logger.info("")

        # 7. Local AI (Ollama/ULTRON/KAIJU)
        logger.info("7️⃣  Discovering Local AI...")
        local_ai = self._discover_local_ai()
        if local_ai:
            self.ai_services["local_ai"] = local_ai
            logger.info(f"   ✅ Local AI: {local_ai.name}")
        logger.info("")

        # 8. Cloud AI Services
        logger.info("8️⃣  Discovering Cloud AI Services...")
        cloud_ai = self._discover_cloud_ai()
        if cloud_ai:
            self.ai_services["cloud_ai"] = cloud_ai
            logger.info(f"   ✅ Cloud AI: {cloud_ai.name}")
        logger.info("")

        logger.info("=" * 80)
        logger.info(f"📊 Discovered {len(self.ai_services)} AI Service Groups")
        logger.info("=" * 80)

        return self.ai_services

    def _discover_sider_ai(self) -> Optional[AIService]:
        """Discover Sider.AI (WiseBase features) - PRIMARY IMPORTANCE"""
        sider = AIService(
            name="Sider.AI (WiseBase)",
            service_type="sider",
            capabilities=["WiseBase", "AI Assistant", "Content Generation", "Research"]
        )

        logger.info("   ⭐ PRIMARY IMPORTANCE - Sider.AI WiseBase")

        # Check if Sider is installed/running
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name', 'exe']):
                try:
                    proc_name = proc.info['name'].lower()
                    if 'sider' in proc_name:
                        sider.available = True
                        sider.integration_method = "process"
                        sider.endpoint = f"process://{proc.info['pid']}"
                        logger.info(f"   ✅ Sider.AI process found: {proc.info['name']} (PID: {proc.info['pid']})")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check for Sider API/endpoint (WiseBase API)
        sider_endpoints = [
            "http://localhost:3000",
            "http://localhost:8080",
            "http://127.0.0.1:3000",
            "http://localhost:5000/sider",  # Via ROAMWISE
            "http://roamwise.ai/sider"  # Via ROAMWISE gateway
        ]

        for endpoint in sider_endpoints:
            try:
                # Try health check
                response = requests.get(f"{endpoint}/health", timeout=2)
                if response.status_code == 200:
                    sider.endpoint = endpoint
                    sider.available = True
                    sider.integration_method = "api"
                    logger.info(f"   ✅ Sider.AI API found: {endpoint}")
                    break
            except Exception:
                # Try root endpoint
                try:
                    response = requests.get(endpoint, timeout=2)
                    if response.status_code < 500:
                        sider.endpoint = endpoint
                        sider.available = True
                        sider.integration_method = "api"
                        logger.info(f"   ✅ Sider.AI endpoint found: {endpoint}")
                        break
                except Exception:
                    pass

        # Check via ROAMWISE.AI (Sider.AI is half of ROAMWISE)
        try:
            roamwise_response = requests.get("http://roamwise.ai", timeout=5)
            if roamwise_response.status_code < 500:
                # Check if Sider/WiseBase is mentioned in response
                if "sider" in roamwise_response.text.lower() or "wisebase" in roamwise_response.text.lower():
                    sider.available = True
                    sider.endpoint = "http://roamwise.ai/sider"  # Via ROAMWISE gateway
                    sider.integration_method = "roamwise_gateway"
                    logger.info("   ✅ Sider.AI available via ROAMWISE.AI gateway")
        except Exception:
            pass

        # Check config file
        sider_config = self.project_root / "config" / "sider_ai_config.json"
        if sider_config.exists():
            try:
                with open(sider_config, 'r') as f:
                    config = json.load(f)
                    if config.get("wisebase_enabled"):
                        sider.available = True
                        if not sider.endpoint and config.get("endpoints"):
                            sider.endpoint = config.get("endpoints", [""])[0]
                        logger.info("   ✅ Sider.AI configured (WiseBase enabled)")
            except Exception:
                pass

        return sider

    def _discover_roamwise_ai(self) -> Optional[AIService]:
        """Discover ROAMWISE.AI (Web frontend portal/gateway - .local network only)

        ROAMWISE.AI = Sider.AI (WiseBase) + RoamResearch (Lifetime Account)
        Half 1: Sider.AI (WiseBase features)
        Half 2: RoamResearch (Lifetime Account - Personal)
        """
        roamwise = AIService(
            name="ROAMWISE.AI",
            service_type="roamwise",
            capabilities=["Web Portal", "Gateway", "WiseBase Integration", "RoamResearch Integration"]
        )

        logger.info("   🌐 Web Portal/Gateway (.local network only)")
        logger.info("   Half 1: Sider.AI (WiseBase)")
        logger.info("   Half 2: RoamResearch (Lifetime Account)")

        # ROAMWISE is .local network only (but roamwise.ai is reachable)
        roamwise_endpoints = [
            "http://roamwise.ai",  # Discovered as reachable
            "http://roamwise.local",
            "http://<LOCAL_HOSTNAME>",  # From config
            "http://<NAS_PRIMARY_IP>/roamwise",  # NAS
            "http://localhost:5000/roamwise",
            "http://localhost:3000/roamwise"
        ]

        for endpoint in roamwise_endpoints:
            try:
                response = requests.get(endpoint, timeout=5)
                if response.status_code < 500:
                    roamwise.endpoint = endpoint
                    roamwise.available = True
                    roamwise.integration_method = "web_api"
                    logger.info(f"   ✅ ROAMWISE.AI found: {endpoint}")

                    # Check for components in response
                    if "sider" in response.text.lower() or "wisebase" in response.text.lower():
                        logger.info("   ✅ Sider.AI component detected in ROAMWISE")
                    if "roam" in response.text.lower() or "roamresearch" in response.text.lower():
                        logger.info("   ✅ RoamResearch component detected in ROAMWISE")
                    break
            except Exception:
                pass

        return roamwise

    def _discover_roamresearch(self) -> Optional[AIService]:
        """Discover RoamResearch (Lifetime Account - Personal)

        Part of ROAMWISE.AI (other half)
        """
        roamresearch = AIService(
            name="RoamResearch (Lifetime Account - Personal)",
            service_type="roamresearch",
            capabilities=["Knowledge Graph", "Note-taking", "Research", "Personal Knowledge Management"]
        )

        logger.info("   📚 Lifetime Account - Personal")
        logger.info("   Part of ROAMWISE.AI (other half)")

        # Check for RoamResearch process
        try:
            import psutil
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    if 'roam' in proc.info['name'].lower():
                        roamresearch.available = True
                        roamresearch.integration_method = "process"
                        logger.info(f"   ✅ RoamResearch process found")
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except ImportError:
            pass

        # Check config for Lifetime Account
        roamresearch_config = self.config_dir / "roamresearch_config.json"
        if roamresearch_config.exists():
            try:
                with open(roamresearch_config, 'r') as f:
                    config = json.load(f)
                    if config.get("lifetime_account") or config.get("account_type") == "lifetime":
                        roamresearch.available = True
                        roamresearch.api_key = config.get("api_key")
                        roamresearch.endpoint = config.get("base_url", "https://roamresearch.com")
                        roamresearch.integration_method = "api"
                        logger.info("   ✅ RoamResearch configured (Lifetime Account)")
            except Exception:
                pass

        # Also check ROAMWISE config
        roamwise_config = self.config_dir / "roamwise_config.json"
        if roamwise_config.exists():
            try:
                with open(roamwise_config, 'r') as f:
                    config = json.load(f)
                    roamresearch_config = config.get("roamresearch", {})
                    if roamresearch_config.get("account_type") == "lifetime" or roamresearch_config.get("enabled"):
                        roamresearch.available = True
                        roamresearch.api_key = roamresearch_config.get("api_key")
                        roamresearch.endpoint = roamresearch_config.get("base_url", "https://roamresearch.com/api")
                        logger.info("   ✅ RoamResearch configured via ROAMWISE config")
            except Exception:
                pass

        return roamresearch

    def _discover_windows_copilot(self) -> Optional[AIService]:
        """Discover Windows Copilot"""
        copilot = AIService(
            name="Windows Copilot",
            service_type="windows_copilot",
            capabilities=["AI Assistant", "System Control", "Content Generation"]
        )

        try:
            import platform
            if platform.system() == "Windows":
                import psutil
                for proc in psutil.process_iter(['pid', 'name']):
                    try:
                        if 'copilot' in proc.info['name'].lower() or 'msedge' in proc.info['name'].lower():
                            copilot.available = True
                            copilot.integration_method = "windows_api"
                            break
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        pass
        except Exception:
            pass

        return copilot

    def _discover_nas_ai(self) -> Optional[AIService]:
        """Discover NAS AI Services"""
        nas_ai = AIService(
            name="NAS AI Services",
            service_type="nas_ai",
            endpoint="http://<NAS_PRIMARY_IP>",
            capabilities=["Ollama", "AI Gateway"]
        )

        try:
            response = requests.get("http://<NAS_PRIMARY_IP>:11434/api/tags", timeout=5)
            if response.status_code == 200:
                nas_ai.available = True
                nas_ai.integration_method = "api"
                logger.info("   ✅ NAS Ollama available")
        except Exception:
            pass

        return nas_ai

    def _discover_neo_browser_ai(self) -> Optional[AIService]:
        """Discover Neo Browser AI"""
        neo_ai = AIService(
            name="Neo Browser AI",
            service_type="neo_browser",
            capabilities=["Built-in AI Assistant", "AI Search", "Content Generation", "Chat"]
        )

        try:
            from jarvis_neo_full_control import JARVISNeoFullControl
            neo_ai.available = True
            neo_ai.integration_method = "jarvis_api"
            neo_ai.endpoint = "http://localhost:8888"  # JARVIS Neo API
        except ImportError:
            pass

        return neo_ai

    def _discover_local_ai(self) -> Optional[AIService]:
        """Discover Local AI (Ollama/ULTRON/KAIJU)"""
        local_ai = AIService(
            name="Local AI (Ollama/ULTRON)",
            service_type="local_ai",
            endpoint="http://localhost:11434",
            capabilities=["LLM Inference", "Local Models"]
        )

        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            if response.status_code == 200:
                local_ai.available = True
                local_ai.integration_method = "ollama_api"
        except Exception:
            pass

        return local_ai

    def _discover_cloud_ai(self) -> Optional[AIService]:
        """Discover Cloud AI Services"""
        import os

        cloud_ai = AIService(
            name="Cloud AI Services",
            service_type="cloud_ai",
            capabilities=[]
        )

        if os.getenv("AWS_ACCESS_KEY_ID"):
            cloud_ai.capabilities.append("AWS Bedrock")
        if os.getenv("AZURE_OPENAI_API_KEY"):
            cloud_ai.capabilities.append("Azure OpenAI")
        if os.getenv("ANTHROPIC_API_KEY"):
            cloud_ai.capabilities.append("Anthropic")
        if os.getenv("OPENAI_API_KEY"):
            cloud_ai.capabilities.append("OpenAI")

        if cloud_ai.capabilities:
            cloud_ai.available = True
            cloud_ai.integration_method = "api_keys"

        return cloud_ai

    def create_bidirectional_integration(self):
        """Create bidirectional integration matrix between all AI services"""
        logger.info("=" * 80)
        logger.info("🔄 Creating Bidirectional Integration Matrix")
        logger.info("=" * 80)
        logger.info("")

        # Initialize integration matrix (all services can communicate with all others)
        service_names = list(self.ai_services.keys())

        for service_a in service_names:
            self.integration_matrix[service_a] = {}
            for service_b in service_names:
                # Bidirectional: both directions enabled
                self.integration_matrix[service_a][service_b] = True

        logger.info(f"   ✅ Integration matrix created: {len(service_names)}x{len(service_names)}")
        logger.info("   🔄 All AI services can communicate bidirectionally (<=>)")
        logger.info("")

        # Log integration pairs
        logger.info("   Integration Pairs (<=>):")
        for i, service_a in enumerate(service_names):
            for service_b in service_names[i+1:]:
                logger.info(f"      {service_a} <=> {service_b}")

        logger.info("")

    def send_ai_to_ai_message(self, from_service: str, to_service: str, message: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send message from one AI service to another (bidirectional)

        Args:
            from_service: Source AI service name
            to_service: Target AI service name
            message: Message payload

        Returns:
            Response from target service
        """
        if from_service not in self.ai_services:
            return {"error": f"Source service {from_service} not found"}

        if to_service not in self.ai_services:
            return {"error": f"Target service {to_service} not found"}

        # Check if integration is enabled
        if not self.integration_matrix.get(from_service, {}).get(to_service, False):
            return {"error": f"Integration {from_service} <=> {to_service} not enabled"}

        # Log message
        message_entry = {
            "timestamp": datetime.now().isoformat(),
            "from": from_service,
            "to": to_service,
            "message": message
        }
        self.message_bus.append(message_entry)

        # Route message to appropriate handler
        target_service = self.ai_services[to_service]

        if target_service.integration_method == "api":
            return self._send_via_api(target_service, message)
        elif target_service.integration_method == "jarvis_api":
            return self._send_via_jarvis_api(target_service, message)
        elif target_service.integration_method == "ollama_api":
            return self._send_via_ollama_api(target_service, message)
        else:
            return {"error": f"Integration method {target_service.integration_method} not implemented"}

    def _send_via_api(self, service: AIService, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via API"""
        try:
            if not service.endpoint:
                return {"error": "No endpoint configured"}

            response = requests.post(
                f"{service.endpoint}/api/ai-message",
                json=message,
                timeout=10
            )

            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def _send_via_jarvis_api(self, service: AIService, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via JARVIS API"""
        try:
            # Use JARVIS desktop/neo API
            if service.service_type == "neo_browser":
                from jarvis_neo_full_control import JARVISNeoFullControl
                control = JARVISNeoFullControl()

                if message.get("action") == "navigate":
                    success = control.navigate(message.get("url", ""))
                    return {"success": success}
                elif message.get("action") == "execute":
                    result = control.execute_script(message.get("script", ""))
                    return {"result": result}

            return {"error": "Action not supported"}
        except Exception as e:
            return {"error": str(e)}

    def _send_via_ollama_api(self, service: AIService, message: Dict[str, Any]) -> Dict[str, Any]:
        """Send message via Ollama API"""
        try:
            query = message.get("query", "")
            model = message.get("model", "llama3.2:3b")

            response = requests.post(
                f"{service.endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": query,
                    "stream": False
                },
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "model": model
                }
            else:
                return {"error": f"Ollama API returned {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    def get_integration_status(self) -> Dict[str, Any]:
        """Get status of all AI-to-AI integrations"""
        return {
            "services": {
                name: {
                    "available": service.available,
                    "type": service.service_type,
                    "endpoint": service.endpoint,
                    "capabilities": service.capabilities
                }
                for name, service in self.ai_services.items()
            },
            "integration_matrix": self.integration_matrix,
            "total_services": len(self.ai_services),
            "total_integrations": sum(
                sum(1 for enabled in row.values() if enabled)
                for row in self.integration_matrix.values()
            )
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="AI <=> AI Bidirectional Integration")
        parser.add_argument("--discover", action="store_true", help="Discover all AI services")
        parser.add_argument("--status", action="store_true", help="Show integration status")
        parser.add_argument("--send-message", nargs=3, metavar=("FROM", "TO", "MESSAGE"),
                           help="Send message from one AI to another")

        args = parser.parse_args()

        integration = AIToAIBidirectionalIntegration()

        if args.discover:
            integration.discover_all_ai_services()
            integration.create_bidirectional_integration()
            status = integration.get_integration_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.status:
            integration.discover_all_ai_services()
            integration.create_bidirectional_integration()
            status = integration.get_integration_status()
            print(json.dumps(status, indent=2, default=str))

        elif args.send_message:
            from_service, to_service, message_text = args.send_message
            message = {"query": message_text}
            result = integration.send_ai_to_ai_message(from_service, to_service, message)
            print(json.dumps(result, indent=2))

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()