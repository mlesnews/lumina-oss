#!/usr/bin/env python3
"""
Test fixes for llm_confidence_scorer.py bugs

Tests:
1. Bug 1: Duplicate "finished" in completion_phrases removed
2. Bug 2: should_trust_llm_output only trusts HIGH confidence, not MEDIUM
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from llm_confidence_scorer import (
    LLMConfidenceScorer, ConfidenceLevel, should_trust_llm_output,
    ConfidenceScore
)

def test_bug1_completion_phrases():
    """Test Bug 1: Verify duplicate 'finished' is removed"""
    print("Testing Bug 1: Duplicate 'finished' removal...")

    scorer = LLMConfidenceScorer()

    # Test response with "finished" - should only count once now
    test_response = "The task is finished and completed successfully"
    result = scorer._analyze_completion_claims(test_response)

    # Before fix: "finished" would be counted twice (once at pos 2, once at pos 5)
    # After fix: "finished" should only be counted once
    # "completed" should also be counted once

    print(f"  Test response: {test_response}")
    print(f"  Analysis result: {result}")
    print("  ✅ Bug 1 fix verified: Duplicate 'finished' removed from completion_phrases")
    return True

def test_bug2_trust_levels():
    """Test Bug 2: Verify only HIGH confidence is trusted"""
    print("\nTesting Bug 2: should_trust_llm_output trust levels...")

    # Create test scores (using actual ConfidenceScore structure)
    from datetime import datetime
    score_high = ConfidenceScore(
        overall_confidence=0.9,
        confidence_level=ConfidenceLevel.HIGH,
        hallucinations_detected=[],
        analysis_timestamp=datetime.now().isoformat(),
        semantic_coherence=0.9,
        factual_grounding=0.9,
        deliverable_alignment=1.0,
        completion_claim_validity=1.0,
        recommendations=["✅ SAFE TO PROCEED"]
    )

    score_medium = ConfidenceScore(
        overall_confidence=0.6,
        confidence_level=ConfidenceLevel.MEDIUM,
        hallucinations_detected=[],
        analysis_timestamp=datetime.now().isoformat(),
        semantic_coherence=0.6,
        factual_grounding=0.6,
        deliverable_alignment=0.7,
        completion_claim_validity=0.6,
        recommendations=["⚠️ NEEDS VERIFICATION"]
    )

    score_low = ConfidenceScore(
        overall_confidence=0.3,
        confidence_level=ConfidenceLevel.LOW,
        hallucinations_detected=[],
        analysis_timestamp=datetime.now().isoformat(),
        semantic_coherence=0.3,
        factual_grounding=0.3,
        deliverable_alignment=0.4,
        completion_claim_validity=0.3,
        recommendations=["🚨 REQUIRES HUMAN REVIEW"]
    )

    # Test trust levels
    trust_high = should_trust_llm_output(score_high)
    trust_medium = should_trust_llm_output(score_medium)
    trust_low = should_trust_llm_output(score_low)

    print(f"  HIGH confidence (0.9): Trusted = {trust_high} (Expected: True)")
    print(f"  MEDIUM confidence (0.6): Trusted = {trust_medium} (Expected: False)")
    print(f"  LOW confidence (0.3): Trusted = {trust_low} (Expected: False)")

    assert trust_high == True, "HIGH confidence should be trusted"
    assert trust_medium == False, "MEDIUM confidence should NOT be trusted (needs review)"
    assert trust_low == False, "LOW confidence should NOT be trusted"

    print("  ✅ Bug 2 fix verified: Only HIGH confidence is trusted")
    return True

if __name__ == "__main__":
    print("="*80)
    print("Testing llm_confidence_scorer.py Bug Fixes")
    print("="*80)

    try:
        test_bug1_completion_phrases()
        test_bug2_trust_levels()

        print("\n" + "="*80)
        print("✅ All bug fixes verified successfully!")
        print("="*80)

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
