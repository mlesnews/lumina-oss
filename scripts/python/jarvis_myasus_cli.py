#!/usr/bin/env python3
"""
JARVIS MyASUS CLI Tool
======================
Command-line interface for MyASUS integration capabilities.

Provides access to:
- System diagnostics
- Device information
- Update checks
- Support access
- System optimization

@JARVIS @MYASUS @CLI @SYSTEM_HEALTH @DIAGNOSTICS
"""

import sys
import asyncio
import argparse
from pathlib import Path
from typing import Dict, Any, Optional

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from lumina_unified_logger import LuminaUnifiedLogger
    logger = LuminaUnifiedLogger("Application", "JARVISMyASUS")
    _logger = logger.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger("JARVISMyASUS")


async def run_diagnostics(integration) -> Dict[str, Any]:
    """Run MyASUS diagnostics"""
    _logger.info("🔍 Running MyASUS diagnostics...")
    response = await integration.process_request({
        "action": "myasus_diagnostics",
        "source": "myasus"
    })

    if response.success:
        diagnostics = response.data.get("diagnostics", {})
        _logger.info("✅ Diagnostics completed")
        return {"success": True, "data": diagnostics}
    else:
        _logger.error(f"❌ Diagnostics failed: {response.error}")
        return {"success": False, "error": response.error}


async def get_device_info(integration) -> Dict[str, Any]:
    """Get MyASUS device information"""
    _logger.info("📱 Retrieving device information...")
    response = await integration.process_request({
        "action": "myasus_device_info",
        "source": "myasus"
    })

    if response.success:
        device = response.data.get("device", {})
        _logger.info("✅ Device information retrieved")
        return {"success": True, "data": device}
    else:
        _logger.error(f"❌ Device info failed: {response.error}")
        return {"success": False, "error": response.error}


async def check_updates(integration) -> Dict[str, Any]:
    """Check for MyASUS updates"""
    _logger.info("🔄 Checking for MyASUS updates...")
    response = await integration.process_request({
        "action": "myasus_updates",
        "source": "myasus"
    })

    if response.success:
        _logger.info("✅ Update check completed")
        return {"success": True, "data": response.data}
    else:
        _logger.error(f"❌ Update check failed: {response.error}")
        return {"success": False, "error": response.error}


async def run_optimization(integration) -> Dict[str, Any]:
    """Run MyASUS optimization"""
    _logger.info("⚡ Running system optimization...")
    response = await integration.process_request({
        "action": "myasus_optimization",
        "source": "myasus"
    })

    if response.success:
        optimization = response.data.get("optimization", {})
        _logger.info("✅ Optimization completed")
        return {"success": True, "data": optimization}
    else:
        _logger.error(f"❌ Optimization failed: {response.error}")
        return {"success": False, "error": response.error}


async def open_support(integration) -> Dict[str, Any]:
    """Open MyASUS support"""
    _logger.info("🆘 Opening MyASUS support...")
    response = await integration.process_request({
        "action": "myasus_support",
        "source": "myasus"
    })

    if response.success:
        _logger.info("✅ MyASUS support opened")
        return {"success": True, "data": response.data}
    else:
        _logger.error(f"❌ Failed to open support: {response.error}")
        return {"success": False, "error": response.error}


async def get_hybrid_data(integration) -> Dict[str, Any]:
    """Get hybrid AC + MyASUS data"""
    _logger.info("🔗 Retrieving hybrid data (AC + MyASUS)...")
    response = await integration.process_request({
        "action": "hybrid",
        "source": "auto"
    })

    if response.success:
        _logger.info("✅ Hybrid data retrieved")
        return {"success": True, "data": response.data}
    else:
        _logger.error(f"❌ Hybrid data retrieval failed: {response.error}")
        return {"success": False, "error": response.error}


def print_diagnostics(diagnostics: Dict[str, Any]):
    """Print diagnostics in readable format"""
    print("\n" + "=" * 70)
    print("📊 MYASUS DIAGNOSTICS")
    print("=" * 70)

    if "system_info" in diagnostics:
        sys_info = diagnostics["system_info"]
        print(f"\n🖥️  System Information:")
        print(f"   OS: {sys_info.get('os', 'Unknown')}")
        print(f"   Version: {sys_info.get('version', 'Unknown')}")
        print(f"   Build: {sys_info.get('build', 'Unknown')}")

    if "hardware" in diagnostics:
        hw = diagnostics["hardware"]
        print(f"\n💻 Hardware:")
        if "cpu" in hw:
            print(f"   CPU: {hw['cpu']}")
        if "ram" in hw:
            print(f"   RAM: {hw['ram']} GB")
        if "disk" in hw:
            print(f"\n   Disk Drives:")
            disk_data = hw["disk"]
            if isinstance(disk_data, list):
                for disk in disk_data:
                    if isinstance(disk, dict):
                        print(f"      {disk.get('DeviceID', 'Unknown')}: "
                              f"{disk.get('SizeGB', 0):.2f} GB total, "
                              f"{disk.get('FreeGB', 0):.2f} GB free")
                    else:
                        print(f"      {disk}")
            elif isinstance(disk_data, dict):
                print(f"      {disk_data}")

    print("\n" + "=" * 70)


def print_device_info(device: Dict[str, Any]):
    """Print device information in readable format"""
    print("\n" + "=" * 70)
    print("📱 MYASUS DEVICE INFORMATION")
    print("=" * 70)
    print(f"\n   Model: {device.get('model', 'Unknown')}")
    print(f"   Manufacturer: {device.get('manufacturer', 'Unknown')}")
    print(f"   Serial Number: {device.get('serial', 'Unknown')}")
    print(f"   System SKU: {device.get('sku', 'Unknown')}")
    print(f"   BIOS Version: {device.get('bios_version', 'Unknown')}")
    print(f"   OS: {device.get('os', 'Unknown')}")
    print("\n" + "=" * 70)


async def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="JARVIS MyASUS CLI - System Health & Diagnostics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s diagnostics          Run system diagnostics
  %(prog)s device-info          Get device information
  %(prog)s check-updates        Check for MyASUS updates
  %(prog)s optimize             Run system optimization
  %(prog)s support              Open MyASUS support
  %(prog)s hybrid               Get hybrid AC + MyASUS data
        """
    )

    parser.add_argument(
        "action",
        choices=["diagnostics", "device-info", "check-updates", "optimize", "support", "hybrid", "capabilities"],
        help="Action to perform"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Import integration
    try:
        from src.cfservices.services.jarvis_core.integrations.armoury_crate_myasus_hybrid import create_hybrid_integration
    except ImportError as e:
        _logger.error(f"❌ Failed to import MyASUS integration: {e}")
        print("❌ MyASUS integration not available")
        return 1

    # Initialize integration
    try:
        integration = create_hybrid_integration(project_root=PROJECT_ROOT)
    except Exception as e:
        _logger.error(f"❌ Failed to initialize integration: {e}")
        print(f"❌ Failed to initialize MyASUS integration: {e}")
        return 1

    # Check availability
    if not integration.myasus_available:
        print("❌ MyASUS is not available on this system")
        print("   Run diagnostics to check installation:")
        integration._diagnose_myasus_installation()
        return 1

    # Execute action
    result = None

    try:
        if args.action == "diagnostics":
            result = await run_diagnostics(integration)
            if result["success"] and not args.json:
                print_diagnostics(result["data"])

        elif args.action == "device-info":
            result = await get_device_info(integration)
            if result["success"] and not args.json:
                print_device_info(result["data"])

        elif args.action == "check-updates":
            result = await check_updates(integration)
            if result["success"] and not args.json:
                print("✅ Update check completed")
                print(f"   {result['data'].get('message', 'Check MyASUS for available updates')}")

        elif args.action == "optimize":
            result = await run_optimization(integration)
            if result["success"] and not args.json:
                opt = result["data"].get("optimization", {})
                print("\n⚡ Optimization Results:")
                if "battery" in opt:
                    bat = opt["battery"]
                    print(f"   Battery Status: {bat.get('status', 'Unknown')}")
                    print(f"   Charge: {bat.get('charge', 'Unknown')}%")
                if "performance" in opt:
                    perf = opt["performance"]
                    print(f"   CPU Usage: {perf.get('cpu_usage', 'Unknown')}%")
                    print(f"   Memory Available: {perf.get('memory_usage', 'Unknown')} GB")

        elif args.action == "support":
            result = await open_support(integration)
            if result["success"] and not args.json:
                print("✅ MyASUS support opened")

        elif args.action == "hybrid":
            result = await get_hybrid_data(integration)
            if result["success"] and not args.json:
                data = result["data"]
                print("\n🔗 Hybrid Data (AC + MyASUS):")
                if "armoury_crate" in data:
                    ac = data["armoury_crate"]
                    print(f"   Armoury Crate: {'✅ Available' if ac.get('available') else '❌ Not available'}")
                if "myasus" in data:
                    my = data["myasus"]
                    print(f"   MyASUS: {'✅ Available' if my.get('available') else '❌ Not available'}")

        elif args.action == "capabilities":
            capabilities = integration.get_capabilities()
            if args.json:
                import json
                print(json.dumps(capabilities, indent=2))
            else:
                print("\n📋 MyASUS Capabilities:")
                myasus_caps = capabilities.get("myasus", {})
                print(f"   Available: {'✅' if myasus_caps.get('available') else '❌'}")
                if myasus_caps.get("available"):
                    print("   Capabilities:")
                    for cap in myasus_caps.get("capabilities", []):
                        print(f"      - {cap}")

    except Exception as e:
        _logger.error(f"❌ Action failed: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1

    # Output JSON if requested
    if args.json and result:
        import json
        print(json.dumps(result, indent=2, default=str))

    # Return exit code
    if result and result.get("success"):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(exit_code)

    exit_code = asyncio.run(main())