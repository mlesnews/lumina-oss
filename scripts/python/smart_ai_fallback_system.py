#!/usr/bin/env python3
"""
Smart AI Fallback System
<COMPANY_NAME> LLC

Local AI first, GROK when needed (decision tree controlled, not gate-gated).
Uses universal decision tree for all decisions.

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import sys
from pathlib import Path
from typing import Optional, Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from universal_decision_tree import decide, DecisionContext, DecisionOutcome
from local_ai_integration import get_local_ai, LocalAIIntegration



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class SmartAIFallback:
    """
    Smart AI Fallback System

    Decision Tree Flow:
    1. Try Local AI first (always)
    2. Check quality
    3. If quality < 0.7 → Decision Tree
    4. Decision Tree Determines:
       - Retry local (if retries available)
       - Use GROK (if complexity/urgency high)
       - Use local (if acceptable)

    GROK is NOT gate-gated - decision tree controls access.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize fallback system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.local_ai = get_local_ai()

        # GROK configuration (if needed)
        self.grok_enabled = True
        self.grok_api_key = None  # Would load from secure storage

        import logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger("SmartAIFallback")

    def generate(self,
                 prompt: str,
                 complexity: str = "medium",
                 urgency: str = "medium",
                 cost_sensitive: bool = True,
                 max_retries: int = 3) -> Optional[str]:
        """
        Generate response with smart fallback

        Args:
            prompt: Input prompt
            complexity: low, medium, high
            urgency: low, medium, high
            cost_sensitive: Whether to prioritize cost
            max_retries: Maximum local AI retries

        Returns:
            Generated response or None
        """
        retry_count = 0

        while retry_count <= max_retries:
            # Try local AI first
            if self.local_ai.available:
                response = self.local_ai.generate_response(prompt)

                if response:
                    # Evaluate quality (simplified - would use actual quality metrics)
                    quality = self._evaluate_quality(response, prompt)

                    if quality >= 0.7:
                        self.logger.info(f"✅ Local AI response (quality: {quality:.2f})")
                        return response

                    # Quality too low - use decision tree
                    self.logger.info(f"⚠️  Local AI quality low ({quality:.2f}), consulting decision tree...")

                    # Create decision context
                    context = DecisionContext(
                        complexity=complexity,
                        urgency=urgency,
                        cost_sensitive=cost_sensitive,
                        local_ai_available=True,
                        local_ai_quality=quality,
                        retry_count=retry_count,
                        max_retries=max_retries
                    )

                    # Make decision
                    decision = decide("ai_fallback", context)

                    self.logger.info(f"📊 Decision: {decision.outcome.value} - {decision.reasoning}")

                    if decision.outcome == DecisionOutcome.RETRY_LOCAL:
                        retry_count += 1
                        self.logger.info(f"🔄 Retrying local AI (attempt {retry_count}/{max_retries})")
                        continue

                    elif decision.outcome == DecisionOutcome.USE_GROK:
                        # Use GROK (decision tree approved, not gate-gated)
                        self.logger.info("🚀 Using GROK (decision tree approved)")
                        return self._call_grok(prompt)

                    elif decision.outcome == DecisionOutcome.USE_LOCAL:
                        # Accept local response despite low quality
                        self.logger.info("✅ Using local AI (decision tree approved)")
                        return response

            # Local AI not available or failed
            context = DecisionContext(
                complexity=complexity,
                urgency=urgency,
                cost_sensitive=cost_sensitive,
                local_ai_available=False,
                local_ai_quality=0.0,
                retry_count=retry_count,
                max_retries=max_retries
            )

            decision = decide("ai_fallback", context)

            if decision.outcome == DecisionOutcome.USE_GROK:
                self.logger.info("🚀 Using GROK (local AI unavailable)")
                return self._call_grok(prompt)

            retry_count += 1

        # All options exhausted
        self.logger.error("❌ All AI options exhausted")
        return None

    def _evaluate_quality(self, response: str, prompt: str) -> float:
        """Evaluate response quality (simplified)"""
        # Simplified quality evaluation
        # In production, would use actual quality metrics

        if not response or len(response) < 10:
            return 0.3

        # Check for common error patterns
        error_patterns = ["error", "failed", "unable", "cannot"]
        if any(pattern in response.lower() for pattern in error_patterns):
            return 0.4

        # Basic quality score
        quality = 0.7

        # Boost for longer, more detailed responses
        if len(response) > 100:
            quality += 0.1

        # Boost for relevant keywords
        prompt_words = set(prompt.lower().split())
        response_words = set(response.lower().split())
        overlap = len(prompt_words & response_words) / max(len(prompt_words), 1)
        quality += overlap * 0.2

        return min(quality, 1.0)

    def _call_grok(self, prompt: str) -> Optional[str]:
        """Call GROK API (decision tree controlled, not gate-gated)"""
        if not self.grok_enabled:
            self.logger.error("GROK not enabled")
            return None

        # TODO: Implement GROK API call  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
        # This would use xAI's GROK API
        # Cost: $5 per 1M tokens (cheaper than OpenAI)

        self.logger.warning("⚠️  GROK API not yet implemented - returning None")
        return None


# Singleton instance
_fallback_instance: Optional[SmartAIFallback] = None


def get_smart_fallback() -> SmartAIFallback:
    """Get singleton smart fallback instance"""
    global _fallback_instance
    if _fallback_instance is None:
        _fallback_instance = SmartAIFallback()
    return _fallback_instance


if __name__ == "__main__":
    fallback = get_smart_fallback()

    # Test cases
    print("\n🧪 Testing Smart AI Fallback System")
    print("=" * 60)

    # Test 1: Simple prompt (should use local)
    print("\nTest 1: Simple prompt")
    result1 = fallback.generate("What is Python?", complexity="low", urgency="low")
    print(f"   Result: {result1[:100] if result1 else 'None'}...")

    # Test 2: Complex prompt (may use GROK)
    print("\nTest 2: Complex prompt")
    result2 = fallback.generate(
        "Explain quantum computing and its applications in AI",
        complexity="high",
        urgency="high",
        cost_sensitive=False
    )
    print(f"   Result: {result2[:100] if result2 else 'None'}...")
