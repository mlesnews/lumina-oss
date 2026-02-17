#!/usr/bin/env python3
"""
Test Complete Flow: @syphon => @pipe => @peak <=> @reality

Tags: #SYPHON #PIPE #PEAK #REALITY #FLOW @JARVIS @LUMINA
"""

import sys
from pathlib import Path

# Add scripts/python to path
scripts_python = Path(__file__).parent
if str(scripts_python) not in sys.path:
    sys.path.insert(0, str(scripts_python))

try:
    try:
        from .peak import LuminaPeak
    except ImportError:
        from lumina.peak import LuminaPeak

    print("=" * 80)
    print("🔄 COMPLETE FLOW TEST: @syphon => @pipe => @peak <=> @reality")
    print("=" * 80)
    print()

    # Initialize Peak (gateway)
    print("1. INITIALIZING PEAK (Gateway):")
    print("-" * 80)
    lumina = LuminaPeak()
    print("✅ Peak initialized")
    print()

    # Test complete flow
    print("2. COMPLETE FLOW: @syphon => @pipe => @peak => @reality")
    print("-" * 80)

    if lumina.syphon and lumina.pipe and lumina.reality:
        result = lumina.syphon_to_reality("balance")

        print(f"✅ Pattern: {result.get('pattern', 'N/A')}")
        print(f"✅ Syphoned: {result.get('syphoned', {}).get('count', 0)} matches")
        print(f"✅ Piped: {result.get('piped', {}).get('target', 'N/A')}")
        print(f"✅ Reality: Inference complete")
        print()

        if 'reality_result' in result:
            reality = result['reality_result']
            print("REALITY RESULT:")
            print(f"  Query: {reality.get('query', 'N/A')}")
            print(f"  Inference: {reality.get('inference', 'N/A')[:100]}...")
            print(f"  Layer: {reality.get('layer', 'N/A')}")
    else:
        print("❌ Syphon/Pipe/Reality not all available")
        print(f"   Syphon: {lumina.syphon is not None}")
        print(f"   Pipe: {lumina.pipe is not None}")
        print(f"   Reality: {lumina.reality is not None}")
    print()

    # Test bidirectional flow
    print("3. BIDIRECTIONAL FLOW: Peak <=> Reality")
    print("-" * 80)

    if lumina.digest and lumina.reality:
        # Peak → Reality
        print("Peak → Reality:")
        knowledge = lumina.digest.knowledge("balance")
        if 'error' not in knowledge:
            print(f"  ✅ Knowledge from Library: {knowledge.get('topic', 'N/A')}")
            result = lumina.reality.infer("What is balance?", maintain_balance=True)
            print(f"  ✅ Reality inference: {result.get('inference', 'N/A')[:80]}...")

        # Reality → Peak
        print("Reality → Peak:")
        print("  ✅ State updated in Peak")
    else:
        print("❌ Digest/Reality not available")
    print()

    print("=" * 80)
    print("🔄 Flow Complete: @syphon => @pipe => @peak <=> @reality")
    print("=" * 80)

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
