#!/usr/bin/env python3
"""
Quick Activation Script for AIOS

Simple one-command activation of AIOS.

Usage:
    python activate_aios.py

Tags: #ACTIVATION #AIOS #QUICK_START @JARVIS @LUMINA
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

scripts_python = Path(__file__).parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ActivateAIOS")


def main():
    """Activate AIOS"""
    print("=" * 80)
    print("🚀 ACTIVATING AIOS - AI Operating System")
    print("=" * 80)
    print()

    try:
        from lumina.aios import AIOS

        logger.info("Initializing AIOS...")
        aios = AIOS()

        # Get status
        status = aios.get_status()

        print("✅ AIOS ACTIVATED")
        print()
        print("STATUS:")
        print("-" * 80)

        # Count active components
        total = 0
        active = 0

        for layer_name, layer_data in status.items():
            if layer_name == 'initialized':
                continue
            if not isinstance(layer_data, dict):
                continue

            for component, available in layer_data.items():
                total += 1
                if available is True or (isinstance(available, str) and 'Available' in available):
                    active += 1

        print(f"Components: {active}/{total} active")
        print()

        # Show key components
        print("KEY COMPONENTS:")
        print("-" * 80)
        key_components = [
            ('Entry Layer', 'peak', status.get('entry_layer', {})),
            ('Knowledge Layer', 'library', status.get('knowledge_layer', {})),
            ('Inference Layer', 'reality', status.get('inference_layer', {})),
            ('AOS Core', 'spatial_graph', status.get('aos_core', {}))
        ]

        for name, key, layer in key_components:
            value = layer.get(key, False)
            icon = "✅" if (value is True or (isinstance(value, str) and 'Available' in value)) else "❌"
            print(f"  {icon} {name}: {key}")

        print()

        # Test query
        print("TESTING:")
        print("-" * 80)
        try:
            result = aios.execute("balance", use_flow=False, use_pegl=False)
            if result and result.get('result'):
                print("✅ Test query executed successfully")
            else:
                print("⚠️  Test query executed but no result")
        except Exception as e:
            print(f"⚠️  Test query failed: {e}")

        print()
        print("=" * 80)
        print("🚀 AIOS is ready to use!")
        print()
        print("Usage:")
        print("  from lumina.aios import AIOS")
        print("  aios = AIOS()")
        print("  result = aios.execute('your query')")
        print("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"❌ Activation failed: {e}", exc_info=True)
        print()
        print("=" * 80)
        print("❌ ACTIVATION FAILED")
        print("=" * 80)
        print(f"Error: {e}")
        print()
        print("Try:")
        print("  python scripts/python/lumina/aios_deploy.py --check-prerequisites")
        print("  python scripts/python/lumina/aios_deploy.py --deploy")
        print("=" * 80)
        return 1


if __name__ == "__main__":


    sys.exit(main())