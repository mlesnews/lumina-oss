#!/usr/bin/env python3
"""
Homelab Integration for AIOS

Connects Lumina <=> Homelab <=> AIOS

Homelab Infrastructure:
- ULTRON (Local Laptop): localhost:11434 (Ollama)
- KAIJU Number Eight (Desktop PC): <NAS_IP>:11434 (Ollama)
- NAS (DS2118+): <NAS_PRIMARY_IP> (Storage)

Tags: #HOMELAB #INTEGRATION #AIOS #LUMINA @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
import requests
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent.parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HomelabIntegration")


class HomelabService:
    """Represents a homelab service"""

    def __init__(self, name: str, service_type: str, endpoint: str, **kwargs):
        """
        Initialize homelab service.

        Args:
            name: Service name
            service_type: Type of service (ollama, storage, etc.)
            endpoint: Service endpoint URL/IP
            **kwargs: Additional service properties
        """
        self.name = name
        self.service_type = service_type
        self.endpoint = endpoint
        self.properties = kwargs
        self.available = False
        self._check_availability()

    def _check_availability(self) -> bool:
        """Check if service is available"""
        if self.service_type == "ollama":
            try:
                response = requests.get(f"{self.endpoint}/api/tags", timeout=2)
                self.available = response.status_code == 200
            except:
                self.available = False
        elif self.service_type == "storage":
            # Check NAS availability (ping or SMB)
            try:
                # Simple ping check
                import socket
                ip = self.endpoint.split("://")[-1].split(":")[0]
                socket.create_connection((ip, 445), timeout=2)
                self.available = True
            except:
                self.available = False
        else:
            self.available = False

        if self.available:
            logger.info(f"✅ {self.name} ({self.service_type}) available at {self.endpoint}")
        else:
            logger.debug(f"{self.name} ({self.service_type}) not available at {self.endpoint}")

        return self.available

    def is_available(self) -> bool:
        """Check if service is available"""
        return self.available

    def get_info(self) -> Dict[str, Any]:
        """Get service information"""
        return {
            'name': self.name,
            'type': self.service_type,
            'endpoint': self.endpoint,
            'available': self.available,
            **self.properties
        }


class HomelabIntegration:
    """
    Homelab Integration

    Connects Lumina <=> Homelab <=> AIOS

    Discovers and manages homelab services:
    - ULTRON (Local Ollama)
    - KAIJU (Network Ollama)
    - NAS (Storage)
    """

    def __init__(self):
        """Initialize Homelab Integration"""
        logger.info("🏠 Initializing Homelab Integration...")

        # Define homelab services
        self.services = {
            'ultron': HomelabService(
                name="ULTRON",
                service_type="ollama",
                endpoint="http://localhost:11434",
                priority=1,
                description="Local laptop Ollama server"
            ),
            'kaiju': HomelabService(
                name="KAIJU Number Eight",
                service_type="ollama",
                endpoint="http://<NAS_IP>:11434",
                priority=2,
                description="Desktop PC Ollama server"
            ),
            'nas': HomelabService(
                name="NAS DS2118+",
                service_type="storage",
                endpoint="<NAS_PRIMARY_IP>",
                priority=3,
                description="Network Attached Storage"
            )
        }

        logger.info("✅ Homelab Integration initialized")
        self._log_services()

    def _log_services(self):
        """Log available services"""
        available = [name for name, service in self.services.items() if service.is_available()]
        if available:
            logger.info(f"Available homelab services: {', '.join(available)}")
        else:
            logger.warning("⚠️  No homelab services available")

    def discover_services(self) -> Dict[str, Any]:
        """
        Discover all homelab services.

        Returns:
            Service discovery results
        """
        results = {}
        for name, service in self.services.items():
            # Recheck availability
            service._check_availability()
            results[name] = service.get_info()

        return results

    def get_service(self, name: str) -> Optional[HomelabService]:
        """Get specific homelab service"""
        return self.services.get(name)

    def get_available_services(self) -> List[str]:
        """Get list of available service names"""
        return [name for name, service in self.services.items() if service.is_available()]

    def get_ai_services(self) -> List[HomelabService]:
        """Get available AI services (Ollama)"""
        return [
            service for service in self.services.values()
            if service.service_type == "ollama" and service.is_available()
        ]

    def get_storage_services(self) -> List[HomelabService]:
        """Get available storage services"""
        return [
            service for service in self.services.values()
            if service.service_type == "storage" and service.is_available()
        ]

    def get_status(self) -> Dict[str, Any]:
        """Get homelab integration status"""
        return {
            'services': {
                name: service.get_info()
                for name, service in self.services.items()
            },
            'available_count': len(self.get_available_services()),
            'ai_services': len(self.get_ai_services()),
            'storage_services': len(self.get_storage_services())
        }


def main():
    """Example usage"""
    print("=" * 80)
    print("🏠 HOMELAB INTEGRATION")
    print("   Lumina <=> Homelab <=> AIOS")
    print("=" * 80)
    print()

    homelab = HomelabIntegration()

    # Discover services
    print("DISCOVERING SERVICES:")
    print("-" * 80)
    services = homelab.discover_services()
    for name, info in services.items():
        icon = "✅" if info['available'] else "❌"
        print(f"{icon} {info['name']} ({info['type']}): {info['endpoint']}")
    print()

    # Available services
    available = homelab.get_available_services()
    print(f"AVAILABLE SERVICES: {len(available)}")
    print("-" * 80)
    for name in available:
        service = homelab.get_service(name)
        print(f"  ✅ {service.name} - {service.service_type}")
    print()

    # AI services
    ai_services = homelab.get_ai_services()
    print(f"AI SERVICES: {len(ai_services)}")
    print("-" * 80)
    for service in ai_services:
        print(f"  ✅ {service.name} - {service.endpoint}")
    print()

    # Status
    status = homelab.get_status()
    print("STATUS:")
    print("-" * 80)
    print(f"  Total Services: {len(status['services'])}")
    print(f"  Available: {status['available_count']}")
    print(f"  AI Services: {status['ai_services']}")
    print(f"  Storage Services: {status['storage_services']}")
    print()

    print("=" * 80)
    print("🏠 Homelab Integration - Ready for AIOS")
    print("=" * 80)


if __name__ == "__main__":


    main()