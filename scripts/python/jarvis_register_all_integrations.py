#!/usr/bin/env python3
"""
JARVIS: Register All Integrations
Register all discovered integrations with Integration Hub

@JARVIS @INTEGRATION @HUB @FIRE_SALE
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging
try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVIS_RegisterIntegrations")


def main():
    """Register all integrations"""
    print("=" * 70)
    print("🔗 JARVIS: REGISTERING ALL INTEGRATIONS")
    print("=" * 70)
    print()

    try:
        from scripts.python.jarvis_integration_hub import JARVISIntegrationHub, ServiceType

        hub = JARVISIntegrationHub(project_root=project_root)

        # Register all available integrations
        integrations = [
            # Hardware
            ("asus_unified", "ASUS Unified Integration (@ASUS_UI)", ServiceType.EXTERNAL_API, None, ["hardware_control", "lighting", "diagnostics"]),

            # HomeLab (if available)
            ("docker", "Docker", ServiceType.EXTERNAL_API, None, ["container_management", "orchestration"]),
            ("home_assistant", "Home Assistant", ServiceType.EXTERNAL_API, None, ["home_automation", "device_control"]),
            ("grafana", "Grafana", ServiceType.EXTERNAL_API, None, ["monitoring", "visualization"]),
            ("pihole", "Pi-hole", ServiceType.EXTERNAL_API, None, ["dns_filtering", "network_management"]),

            # Cloud
            ("azure_key_vault", "Azure Key Vault", ServiceType.CLOUD, None, ["secrets_management", "encryption"]),

            # AI/ML
            ("openai", "OpenAI API", ServiceType.EXTERNAL_API, None, ["llm", "embeddings", "vision"]),
            ("claude", "Anthropic Claude", ServiceType.EXTERNAL_API, None, ["llm", "reasoning"]),
            ("elevenlabs", "ElevenLabs", ServiceType.EXTERNAL_API, None, ["tts", "voice_cloning"]),
        ]

        registered = 0
        for service_id, service_name, service_type, endpoint, capabilities in integrations:
            try:
                hub.register_service(
                    service_id=service_id,
                    service_name=service_name,
                    service_type=service_type,
                    endpoint=endpoint,
                    capabilities=capabilities
                )
                registered += 1
                print(f"  ✅ Registered: {service_name}")
            except Exception as e:
                print(f"  ⚠️  Failed to register {service_name}: {e}")

        print()
        print(f"✅ Registered {registered} integrations")

        # Get status
        status = hub.get_status_report()
        print()
        print("INTEGRATION HUB STATUS:")
        print(f"  Total Services: {status['total_services']}")
        print(f"  Connected: {status['status_counts']['connected']}")
        print(f"  Degraded: {status['status_counts']['degraded']}")
        print(f"  Disconnected: {status['status_counts']['disconnected']}")
        print()
        print("=" * 70)

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":


    main()