#!/usr/bin/env python3
"""
Proactive Service Discovery and Installation Workflow

When a service is mentioned, immediately:
1. Check if it's installed/running
2. If not, ask operator if they want it installed
3. Provide installation options

Tags: #PROACTIVE #DISCOVERY #INSTALLATION #WORKFLOW @JARVIS @LUMINA
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

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

logger = get_logger("ProactiveServiceDiscovery")


@dataclass
class ServiceDiscoveryResult:
    """Service discovery result"""
    service_name: str
    installed: bool
    running: bool
    endpoint: Optional[str] = None
    installation_method: Optional[str] = None
    installation_instructions: Optional[str] = None


class ProactiveServiceDiscovery:
    """
    Proactive Service Discovery

    When a service is mentioned, immediately check if it's installed
    and offer installation if not.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize proactive service discovery"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        logger.info("✅ Proactive Service Discovery initialized")

    def discover_service(self, service_name: str) -> Tuple[ServiceDiscoveryResult, bool]:
        """
        Discover a service and check installation status

        Args:
            service_name: Name of service to discover

        Returns:
            Tuple of (discovery_result, needs_installation_prompt)
        """
        logger.info("=" * 80)
        logger.info(f"🔍 PROACTIVE DISCOVERY: {service_name.upper()}")
        logger.info("=" * 80)
        logger.info("")

        service_name_lower = service_name.lower()

        # Route to appropriate discoverer
        if "n8n" in service_name_lower:
            return self._discover_n8n()
        elif "nas" in service_name_lower and "n8n" in service_name_lower:
            return self._discover_nas_n8n()
        elif "ollama" in service_name_lower:
            return self._discover_ollama()
        elif "docker" in service_name_lower:
            return self._discover_docker()
        elif "claude" in service_name_lower:
            return self._discover_claude_desktop()
        elif "sider" in service_name_lower:
            return self._discover_sider_ai()
        elif "roamwise" in service_name_lower:
            return self._discover_roamwise()
        else:
            # Generic discovery
            return self._discover_generic(service_name)

    def _discover_nas_n8n(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover NAS N8N"""
        try:
            from discover_nas_n8n import NASN8NDiscoverer

            discoverer = NASN8NDiscoverer(self.project_root)
            n8n_info = discoverer.discover_n8n()

            result = ServiceDiscoveryResult(
                service_name="NAS N8N",
                installed=n8n_info.get("installed", False),
                running=n8n_info.get("running", False),
                endpoint=n8n_info.get("endpoint"),
                installation_method="Docker on NAS",
                installation_instructions=(
                    "N8N can be installed on NAS via:\n"
                    "1. Docker: docker run -it --rm --name n8n -p 5678:5678 n8nio/n8n\n"
                    "2. Synology Package Center: Install N8N package\n"
                    "3. Manual installation on NAS"
                )
            )

            needs_prompt = not result.installed or not result.running

            if result.installed and result.running:
                logger.info(f"   ✅ {result.service_name} is installed and running")
                logger.info(f"   📡 Endpoint: {result.endpoint}")
            elif result.installed:
                logger.warning(f"   ⚠️  {result.service_name} is installed but not running")
                needs_prompt = True
            else:
                logger.warning(f"   ❌ {result.service_name} is NOT installed")
                needs_prompt = True

            return result, needs_prompt

        except Exception as e:
            logger.error(f"   ❌ Error discovering N8N: {e}")
            return ServiceDiscoveryResult(
                service_name="NAS N8N",
                installed=False,
                running=False
            ), True

    def _discover_n8n(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover N8N (generic)"""
        return self._discover_nas_n8n()

    def _discover_ollama(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover Ollama"""
        try:
            from discover_standalone_ai_apps import StandaloneAIDiscoverer

            discoverer = StandaloneAIDiscoverer(self.project_root)
            apps = discoverer.discover_all()

            ollama_app = next((app for app in apps if app.name == "ollama"), None)

            if ollama_app:
                result = ServiceDiscoveryResult(
                    service_name="Ollama",
                    installed=ollama_app.installed,
                    running=ollama_app.running,
                    endpoint="http://localhost:11434",
                    installation_method="Download from ollama.ai",
                    installation_instructions="Download and install from https://ollama.ai"
                )

                needs_prompt = not result.installed or not result.running
                return result, needs_prompt

            return ServiceDiscoveryResult(
                service_name="Ollama",
                installed=False,
                running=False,
                installation_method="Download from ollama.ai"
            ), True

        except Exception as e:
            logger.error(f"   ❌ Error discovering Ollama: {e}")
            return ServiceDiscoveryResult(
                service_name="Ollama",
                installed=False,
                running=False
            ), True

    def _discover_docker(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover Docker"""
        try:
            from discover_standalone_ai_apps import StandaloneAIDiscoverer

            discoverer = StandaloneAIDiscoverer(self.project_root)
            apps = discoverer.discover_all()

            docker_app = next((app for app in apps if app.name == "docker_desktop"), None)

            if docker_app:
                result = ServiceDiscoveryResult(
                    service_name="Docker Desktop",
                    installed=docker_app.installed,
                    running=docker_app.running,
                    endpoint=None,
                    installation_method="Download from docker.com",
                    installation_instructions="Download Docker Desktop from https://www.docker.com/products/docker-desktop"
                )

                needs_prompt = not result.installed
                return result, needs_prompt

            return ServiceDiscoveryResult(
                service_name="Docker Desktop",
                installed=False,
                running=False,
                installation_method="Download from docker.com"
            ), True

        except Exception as e:
            logger.error(f"   ❌ Error discovering Docker: {e}")
            return ServiceDiscoveryResult(
                service_name="Docker Desktop",
                installed=False,
                running=False
            ), True

    def _discover_claude_desktop(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover Claude Desktop"""
        try:
            from discover_standalone_ai_apps import StandaloneAIDiscoverer

            discoverer = StandaloneAIDiscoverer(self.project_root)
            apps = discoverer.discover_all()

            claude_app = next((app for app in apps if app.name == "claude_desktop"), None)

            if claude_app:
                result = ServiceDiscoveryResult(
                    service_name="Claude Desktop",
                    installed=claude_app.installed,
                    running=claude_app.running,
                    installation_method="Download from anthropic.com",
                    installation_instructions="Download Claude Desktop from https://www.anthropic.com/claude"
                )

                needs_prompt = not result.installed
                return result, needs_prompt

            return ServiceDiscoveryResult(
                service_name="Claude Desktop",
                installed=False,
                running=False,
                installation_method="Download from anthropic.com"
            ), True

        except Exception as e:
            logger.error(f"   ❌ Error discovering Claude Desktop: {e}")
            return ServiceDiscoveryResult(
                service_name="Claude Desktop",
                installed=False,
                running=False
            ), True

    def _discover_sider_ai(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover Sider.AI"""
        try:
            from list_all_desktop_ai_services import DesktopAIServiceInventory

            inventory = DesktopAIServiceInventory(self.project_root)
            sider_info = inventory.check_sider_ai()

            result = ServiceDiscoveryResult(
                service_name="Sider.AI",
                installed=sider_info.get("installed", False) or sider_info.get("api_available", False),
                running=sider_info.get("running", False),
                endpoint=sider_info.get("endpoint"),
                installation_method="Install Sider.AI application",
                installation_instructions="Install Sider.AI from https://sider.ai or via ROAMWISE gateway"
            )

            needs_prompt = not result.installed
            return result, needs_prompt

        except Exception as e:
            logger.error(f"   ❌ Error discovering Sider.AI: {e}")
            return ServiceDiscoveryResult(
                service_name="Sider.AI",
                installed=False,
                running=False
            ), True

    def _discover_roamwise(self) -> Tuple[ServiceDiscoveryResult, bool]:
        """Discover ROAMWISE.AI"""
        try:
            from list_all_desktop_ai_services import DesktopAIServiceInventory

            inventory = DesktopAIServiceInventory(self.project_root)
            roamwise_info = inventory.check_roamwise_ai()

            result = ServiceDiscoveryResult(
                service_name="ROAMWISE.AI",
                installed=roamwise_info.get("available", False),
                running=roamwise_info.get("available", False),
                endpoint=roamwise_info.get("endpoint"),
                installation_method="Deploy on NAS or local server",
                installation_instructions="ROAMWISE.AI should be deployed on NAS or local server (.local network)"
            )

            needs_prompt = not result.installed
            return result, needs_prompt

        except Exception as e:
            logger.error(f"   ❌ Error discovering ROAMWISE.AI: {e}")
            return ServiceDiscoveryResult(
                service_name="ROAMWISE.AI",
                installed=False,
                running=False
            ), True

    def _discover_generic(self, service_name: str) -> Tuple[ServiceDiscoveryResult, bool]:
        """Generic discovery"""
        logger.warning(f"   ⚠️  Generic discovery for {service_name} (no specific discoverer)")
        return ServiceDiscoveryResult(
            service_name=service_name,
            installed=False,
            running=False
        ), True

    def prompt_installation(self, result: ServiceDiscoveryResult) -> Dict[str, Any]:
        """
        Prompt operator for installation

        Args:
            result: Service discovery result

        Returns:
            Installation prompt information
        """
        logger.info("")
        logger.info("=" * 80)
        logger.info("❓ INSTALLATION PROMPT")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"   Service: {result.service_name}")
        logger.info(f"   Status: {'✅ Installed' if result.installed else '❌ NOT INSTALLED'}")
        if result.running:
            logger.info(f"   Running: ✅")
        elif result.installed:
            logger.info(f"   Running: ❌ (installed but not running)")
        logger.info("")

        if not result.installed:
            if result.installation_method:
                logger.info(f"   📦 Installation Method: {result.installation_method}")
            logger.info("")
            logger.info("   📋 Installation Instructions:")
            if result.installation_instructions:
                for line in result.installation_instructions.split('\n'):
                    logger.info(f"      {line}")
            logger.info("")
            logger.info(f"   ❓ Would you like to install {result.service_name}?")
            logger.info("      (This is a prompt - operator decision required)")

        return {
            "service": result.service_name,
            "installed": result.installed,
            "running": result.running,
            "needs_installation": not result.installed,
            "installation_method": result.installation_method,
            "installation_instructions": result.installation_instructions,
            "endpoint": result.endpoint
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Proactive Service Discovery")
        parser.add_argument("service", help="Service name to discover")
        parser.add_argument("--prompt", action="store_true", help="Show installation prompt")

        args = parser.parse_args()

        discovery = ProactiveServiceDiscovery()
        result, needs_prompt = discovery.discover_service(args.service)

        if needs_prompt or args.prompt:
            prompt_info = discovery.prompt_installation(result)
            import json
            print(json.dumps(prompt_info, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()