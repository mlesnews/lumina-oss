#!/usr/bin/env python3
"""
Execute MARVIN's roast on "Planning next moves" and human inability to work with AI
"""

import sys
from pathlib import Path

# Add scripts/python to path
sys.path.insert(0, str(Path(__file__).parent))

from marvin_granular_roast import MarvinGranularRoast

def main():
    print("=" * 80)
    print("🔥 MARVIN GRANULAR ROAST")
    print("Piercing the veil of 'Planning next moves'")
    print("Roasting human inability to properly work with AI")
    print("=" * 80)
    print()

    roaster = MarvinGranularRoast()

    roast = roaster.granular_roast(
        "Planning next moves and human inability to properly work with AI",
        context={
            'focus': 'pierce the veil of planning, roast human-AI interaction failures',
            'targets': [
                'Planning next moves pattern',
                'Human treating AI like human',
                'Master-padawan todo system',
                'One Ring blueprint gap',
                'Human infallibility assumption'
            ]
        }
    )

    print("\n" + "=" * 80)
    print("🔥 MARVIN GRANULAR ROAST COMPLETE")
    print("=" * 80)
    print(f"\nTarget: {roast.target}")
    print(f"Total Faults: {roast.total_faults}")
    print(f"Breakdown: {roast.macro_faults} macro, {roast.meso_faults} meso, {roast.micro_faults} micro, {roast.atomic_faults} atomic")
    print(f"\nSummary: {roast.summary}")

    print("\n" + "-" * 80)
    print("TOP FAULTS IDENTIFIED:")
    print("-" * 80)

    for i, fault in enumerate(roast.faults[:25], 1):
        print(f"\n{i}. [{fault.granularity_level.value.upper()}] {fault.category.value}")
        print(f"   Description: {fault.description}")
        print(f"   Specific Fault: {fault.specific_fault}")
        print(f"   Root Cause: {fault.root_cause}")
        print(f"   Impact: {fault.impact}")
        if fault.evidence:
            evidence_str = fault.evidence[0] if isinstance(fault.evidence[0], str) else str(fault.evidence[0])
            if len(evidence_str) > 120:
                evidence_str = evidence_str[:120] + "..."
            print(f"   Evidence: {evidence_str}")
        print()

    print("\n" + "=" * 80)
    print("🔥 ROAST COMPLETE - JARVIS should now follow up on each fault")
    print("=" * 80)

if __name__ == "__main__":



    main()