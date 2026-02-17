#!/usr/bin/env python3
"""
Setup Script for JARVIS Vacuum Integration

Automates the setup and configuration of vacuum cleaner integration.
"""

import sys
import json
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from jarvis_vacuum_control import JARVISVacuumControl
from jarvis_vacuum_integration import JARVISVacuumIntegration
from lumina_logger import get_logger

logger = get_logger("VacuumSetup")


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import paho.mqtt.client as mqtt
        logger.info("✅ paho-mqtt installed")
    except ImportError:
        missing.append("paho-mqtt")
        logger.warning("⚠️  paho-mqtt not installed")

    try:
        from Crypto.Cipher import AES
        logger.info("✅ pycryptodome installed")
    except ImportError:
        try:
            from cryptography.hazmat.primitives.ciphers import Cipher
            logger.info("✅ cryptography installed")
        except ImportError:
            missing.append("pycryptodome or cryptography")
            logger.warning("⚠️  No crypto library installed")

    try:
        import netifaces
        logger.info("✅ netifaces installed (optional)")
    except ImportError:
        logger.info("ℹ️  netifaces not installed (optional, for better network discovery)")

    if missing:
        logger.error(f"❌ Missing dependencies: {', '.join(missing)}")
        logger.info("   Install with: pip install " + " ".join(missing))
        return False

    return True


def run_discovery():
    """Run vacuum discovery"""
    logger.info("=" * 80)
    logger.info("🔍 Running vacuum discovery...")
    logger.info("=" * 80)

    control = JARVISVacuumControl()
    devices = control.discover_and_register()

    if devices:
        logger.info(f"✅ Discovered {len(devices)} device(s)")
        for device in devices:
            logger.info(f"   • {device.brand.value.upper()} - {device.device_id}")
            logger.info(f"     IP: {device.ip_address}, Protocol: {device.protocol.value}")
        return devices
    else:
        logger.warning("⚠️  No devices discovered automatically")
        logger.info("   You may need to configure devices manually")
        return []


def setup_integration():
    """Set up JARVIS vacuum integration"""
    logger.info("=" * 80)
    logger.info("🔗 Setting up JARVIS Vacuum Integration...")
    logger.info("=" * 80)

    try:
        integration = JARVISVacuumIntegration()
        logger.info("✅ Integration initialized successfully")
        return integration
    except Exception as e:
        logger.error(f"❌ Integration setup failed: {e}")
        return None


def create_example_config():
    """Create example configuration for manual device setup"""
    logger.info("=" * 80)
    logger.info("📝 Creating example configuration...")
    logger.info("=" * 80)

    example_file = project_root / "data" / "jarvis_vacuum" / "controllers_example.json"

    example_config = {
        "updated_at": "2025-01-16T00:00:00",
        "controllers": [
            {
                "device_id": "roborock_s7_example",
                "device": {
                    "device_id": "roborock_s7_example",
                    "brand": "roborock",
                    "model": "S7",
                    "protocol": "miio",
                    "ip_address": "192.168.1.50",
                    "port": 54321,
                    "token": "YOUR_32_BYTE_HEX_TOKEN_HERE",
                    "capabilities": ["cleaning", "mopping", "mapping"],
                    "metadata": {
                        "discovery_method": "manual"
                    }
                },
                "is_connected": False
            },
            {
                "device_id": "roomba_980_example",
                "device": {
                    "device_id": "roomba_980_example",
                    "brand": "irobot",
                    "model": "980",
                    "protocol": "mqtt",
                    "ip_address": "192.168.1.100",
                    "port": 8883,
                    "blid": "YOUR_BLID_HERE",
                    "password": "YOUR_PASSWORD_HERE",
                    "capabilities": ["cleaning", "mapping"],
                    "metadata": {
                        "discovery_method": "manual"
                    }
                },
                "is_connected": False
            }
        ]
    }

    try:
        with open(example_file, 'w', encoding='utf-8') as f:
            json.dump(example_config, f, indent=2, ensure_ascii=False)
        logger.info(f"✅ Example configuration created: {example_file}")
        logger.info("   Copy devices from this file to controllers.json and update with your credentials")
    except Exception as e:
        logger.error(f"❌ Failed to create example config: {e}")


def main():
    """Main setup function"""
    logger.info("=" * 80)
    logger.info("🚀 JARVIS VACUUM INTEGRATION SETUP")
    logger.info("=" * 80)

    # Step 1: Check dependencies
    logger.info("\n📦 Step 1: Checking dependencies...")
    if not check_dependencies():
        logger.error("❌ Please install missing dependencies first")
        return 1

    # Step 2: Run discovery
    logger.info("\n🔍 Step 2: Running discovery...")
    devices = run_discovery()

    # Step 3: Set up integration
    logger.info("\n🔗 Step 3: Setting up integration...")
    integration = setup_integration()

    if not integration:
        logger.error("❌ Integration setup failed")
        return 1

    # Step 4: Create example config
    logger.info("\n📝 Step 4: Creating example configuration...")
    create_example_config()

    # Summary
    logger.info("\n" + "=" * 80)
    logger.info("✅ SETUP COMPLETE")
    logger.info("=" * 80)
    logger.info(f"   Devices discovered: {len(devices)}")
    logger.info("   Integration: Ready")
    logger.info("   Configuration: Ready")
    logger.info("\n📚 Next steps:")
    logger.info("   1. If no devices were discovered, configure manually:")
    logger.info("      - Edit data/jarvis_vacuum/controllers.json")
    logger.info("      - See data/jarvis_vacuum/controllers_example.json for format")
    logger.info("   2. Test connection:")
    logger.info("      python scripts/python/jarvis_vacuum_control.py --status DEVICE_ID")
    logger.info("   3. Start cleaning:")
    logger.info("      python scripts/python/jarvis_vacuum_control.py --start DEVICE_ID")
    logger.info("=" * 80)

    return 0


if __name__ == "__main__":


    sys.exit(main())