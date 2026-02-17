#!/usr/bin/env python3
"""
RoamWise Setup Script

Sets up local domain and tests connections
"""

import sys
import subprocess
from pathlib import Path
import platform
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("roamwise_setup")


script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def setup_hosts_file():
    try:
        """Add <LOCAL_HOSTNAME> to hosts file"""
        domain = "<LOCAL_HOSTNAME>"
        ip = "127.0.0.1"

        if platform.system() == "Windows":
            hosts_path = Path("C:/Windows/System32/drivers/etc/hosts")
        else:
            hosts_path = Path("/etc/hosts")

        # Check if already exists
        if hosts_path.exists():
            with open(hosts_path, 'r') as f:
                content = f.read()
                if domain in content:
                    print(f"✅ {domain} already in hosts file")
                    return True

        # Add to hosts file (requires admin)
        entry = f"\n{ip} {domain}\n"
        print(f"📝 Add to hosts file ({hosts_path}):")
        print(f"   {entry.strip()}")
        print("\n⚠️  Run as administrator to modify hosts file automatically")
        print("   Or manually add the entry above")

        return False

    except Exception as e:
        logger.error(f"Error in setup_hosts_file: {e}", exc_info=True)
        raise
def test_connections():
    """Test API connections"""
    print("\n🔗 Testing connections...")

    # Test SiderAI Wisebase
    try:
        from roamwise_hybrid_datafeed import SiderAIWisebaseConnector
        wisebase = SiderAIWisebaseConnector()
        print("  ✅ SiderAI Wisebase connector ready")
    except Exception as e:
        print(f"  ⚠️  SiderAI Wisebase: {e}")

    # Test RoamResearch
    try:
        from roamwise_hybrid_datafeed import RoamResearchConnector
        roam = RoamResearchConnector()
        print("  ✅ RoamResearch connector ready")
    except Exception as e:
        print(f"  ⚠️  RoamResearch: {e}")

    # Test Pathfinder
    try:
        from roamwise_hybrid_datafeed import WoWAtlasPathfinder
        pathfinder = WoWAtlasPathfinder()
        print("  ✅ WoW Atlas Pathfinder ready")
    except Exception as e:
        print(f"  ❌ Pathfinder error: {e}")

def main():
    """Main setup"""
    print("\n" + "="*70)
    print("🌐 RoamWise Setup")
    print("="*70 + "\n")

    # Setup hosts file
    setup_hosts_file()

    # Test connections
    test_connections()

    print("\n" + "="*70)
    print("✅ Setup Complete")
    print("="*70)
    print("\nNext steps:")
    print("  1. Add API keys to environment or config file")
    print("  2. Run: python scripts/python/roamwise_hybrid_datafeed.py")
    print("  3. Run: python scripts/python/roamwise_server.py")
    print("  4. Open: http://<LOCAL_HOSTNAME>:5000")
    print("\n")

if __name__ == "__main__":



    main()