#!/usr/bin/env python3
"""
Lumina AI Intelligence Scorer
Uses Iron Legion specialized experts to classify and score intelligence items.

Classifies items into:
- CRITICAL: Needs immediate human attention (valid + urgent)
- ACTIONABLE: Important task (valid + needs action)
- INFORMATIONAL: Useful context (valid + no action)
- NOISE: Spam, duplicates, or low-value data

Tags: #AI_SCORING #INTELLIGENCE #IRON_LEGION #NOISE_REDUCTION @JARVIS @LUMINA
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AIIntelligenceScorer")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AIIntelligenceScorer")

try:
    from scripts.python.iron_legion_expert_router import IronLegionExpertRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    logger.warning("⚠️  IronLegionExpertRouter not available")


class LuminaAIIntelligenceScorer:
    """AI-powered scorer for reducing noise in intelligence gathering"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.router = IronLegionExpertRouter() if ROUTER_AVAILABLE else None

    def score_item(self, content: str, source: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Score an intelligence item using AI

        Returns:
            Dict with 'category', 'score', 'summary', and 'is_valid'
        """
        if not self.router:
            return {
                "category": "informational",
                "score": 0.5,
                "summary": content[:100] + "...",
                "is_valid": True,
                "ai_enhanced": False
            }

        prompt = f"""
Analyze the following intelligence item from source '{source}'.
Categorize it into exactly one of: [CRITICAL, ACTIONABLE, INFORMATIONAL, NOISE].
Rate its validity from 0.0 to 1.0.
Provide a 1-sentence summary.

CONTENT:
{content}

METADATA:
{json.dumps(metadata or {}, default=str)}

Return ONLY a JSON object with:
{{
  "category": "CATEGORY_NAME",
  "validity_score": 0.0,
  "importance_score": 0.0,
  "summary": "1-sentence summary",
  "reasoning": "Brief explanation"
}}
"""

        # Route to reasoning expert (Mistral)
        result = self.router.route_request(prompt, task_type="reasoning")

        if result.get("success"):
            try:
                # Clean response to handle potential markdown code blocks
                raw_response = result["response"]
                if "```json" in raw_response:
                    raw_response = raw_response.split("```json")[1].split("```")[0].strip()
                elif "```" in raw_response:
                    raw_response = raw_response.split("```")[1].split("```")[0].strip()

                ai_data = json.loads(raw_response)

                # Standardize category
                cat = ai_data.get("category", "INFORMATIONAL").upper()

                return {
                    "category": cat,
                    "score": ai_data.get("importance_score", 0.5),
                    "validity": ai_data.get("validity_score", 0.5),
                    "summary": ai_data.get("summary", ""),
                    "reasoning": ai_data.get("reasoning", ""),
                    "is_valid": ai_data.get("validity_score", 0.5) > 0.4,
                    "ai_enhanced": True,
                    "expert": result.get("expert_name")
                }
            except Exception as e:
                logger.warning(f"⚠️  Failed to parse AI response: {e}")

        return {
            "category": "informational",
            "score": 0.5,
            "summary": "AI scoring failed, using default classification",
            "is_valid": True,
            "ai_enhanced": False,
            "error": "AI processing failed"
        }

    def batch_process(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Process a batch of items"""
        processed = []
        for item in items:
            content = item.get("content", item.get("body", item.get("message", "")))
            source = item.get("source", "unknown")
            scored = self.score_item(content, source, item.get("metadata"))
            processed.append({**item, "ai_score": scored})
        return processed


def main():
    try:
        """Test AI Scorer"""
        scorer = LuminaAIIntelligenceScorer(project_root)
        test_content = "URGENT: Your server <NAS_PRIMARY_IP> is running out of disk space. Current usage 98%."
        result = scorer.score_item(test_content, "System Monitor")
        print(json.dumps(result, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()