#!/usr/bin/env python3
"""
Test AIOS Complete Integration

Quick test to verify all components are integrated.
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
    from lumina.aios import AIOS

    print("=" * 80)
    print("✅ AIOS COMPLETE INTEGRATION TEST")
    print("=" * 80)
    print()

    aios = AIOS()
    status = aios.get_status()

    print("COMPONENT STATUS:")
    print("-" * 80)

    components = [
        ('Entry Layer (Peak)', 'peak'),
        ('Knowledge Layer (Library)', 'library'),
        ('Inference Layer (Reality)', 'reality'),
        ('Transformation (PEGL)', 'pegl'),
        ('AOS Core (Spatial)', 'spatial_graph'),
        ('AI Connection', 'ai_connection'),
        ('Homelab', 'homelab'),
        ('Simulators', 'simulators'),
        ('Quantum Entanglement', 'quantum_entanglement')
    ]

    for name, key in components:
        available = False
        if key in status:
            comp_status = status[key]
            if isinstance(comp_status, dict):
                available = comp_status.get('available', False)
            else:
                available = comp_status is not None

        icon = "✅" if available else "❌"
        print(f"{icon} {name}: {'Available' if available else 'Not available'}")

    print()
    print("=" * 80)
    print("✅ AIOS Integration Test Complete")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
