#!/usr/bin/env python3
"""
Iron Legion Expert Router - Mixture of Experts (MoE) Decisioning System

Intelligently routes requests to the best expert model based on task type,
keywords, and expert specialization.

Tags: #IRON_LEGION #MOE #EXPERT_ROUTING #KAIJU @JARVIS @LUMINA @DOIT
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import requests

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
config_path = project_root / "config" / "iron_legion_experts_config.json"


@dataclass
class ExpertSelection:
    """Result of expert selection"""
    expert_id: str
    expert_name: str
    endpoint: str
    model: str
    confidence: float
    reason: str
    fallback: Optional[str] = None


class IronLegionExpertRouter:
    """Intelligent router for Iron Legion Mixture of Experts"""

    def __init__(self, config_path: Path = config_path):
        """Initialize router with expert configuration"""
        self.config_path = config_path
        self.config = self._load_config()
        self.experts = self.config.get("experts", {})
        self.routing_strategy = self.config.get("routing_strategy", {})
        self.fallback_chain = self.routing_strategy.get("fallback_chain", [])

    def _load_config(self) -> Dict:
        """Load expert configuration"""
        try:
            with open(self.config_path, encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"⚠️  Error loading config: {e}")
            return {}

    def _check_expert_health(self, expert_id: str) -> bool:
        """Check if expert is healthy and available"""
        expert = self.experts.get(expert_id, {})
        endpoint = expert.get("endpoint", "")
        status = expert.get("status", "unknown")

        if status != "working":
            return False

        try:
            # Quick health check
            response = requests.get(f"{endpoint}/health", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text for expert matching"""
        text_lower = text.lower()
        keywords = []

        # Check each expert's keywords
        for expert_id, expert in self.experts.items():
            expert_keywords = expert.get("keywords", [])
            for keyword in expert_keywords:
                if keyword.lower() in text_lower:
                    keywords.append(keyword)

        return keywords

    def _match_expert_by_keywords(self, text: str) -> Optional[ExpertSelection]:
        """Match expert based on keywords in text"""
        text_lower = text.lower()
        best_match = None
        best_score = 0

        for expert_id, expert in self.experts.items():
            # Skip if not working
            if not self._check_expert_health(expert_id):
                continue

            # Count keyword matches
            expert_keywords = expert.get("keywords", [])
            matches = sum(1 for kw in expert_keywords if kw.lower() in text_lower)

            if matches > best_score:
                best_score = matches
                best_match = ExpertSelection(
                    expert_id=expert_id,
                    expert_name=expert.get("name", expert_id),
                    endpoint=expert.get("endpoint", ""),
                    model=expert.get("model", ""),
                    confidence=min(matches / max(len(expert_keywords), 1), 1.0),
                    reason=f"Matched {matches} keywords: {', '.join([kw for kw in expert_keywords if kw.lower() in text_lower][:3])}"
                )

        return best_match

    def _match_expert_by_rules(self, text: str) -> Optional[ExpertSelection]:
        """Match expert based on routing rules"""
        text_lower = text.lower()
        rules = self.routing_strategy.get("rules", [])

        for rule in rules:
            condition = rule.get("condition", "").lower()
            expert_id = rule.get("expert", "")
            confidence = rule.get("confidence", "low")
            fallback = rule.get("fallback")

            # Check condition
            if "code" in condition and any(kw in text_lower for kw in ["code", "function", "class", "import", "def", "bug", "error"]):
                if self._check_expert_health(expert_id):
                    return ExpertSelection(
                        expert_id=expert_id,
                        expert_name=self.experts[expert_id].get("name", expert_id),
                        endpoint=self.experts[expert_id].get("endpoint", ""),
                        model=self.experts[expert_id].get("model", ""),
                        confidence=0.9 if confidence == "high" else 0.7,
                        reason="Code-related task detected",
                        fallback=fallback
                    )

            elif "complex" in condition and any(kw in text_lower for kw in ["complex", "advanced", "sophisticated", "multi-step"]):
                if self._check_expert_health(expert_id):
                    return ExpertSelection(
                        expert_id=expert_id,
                        expert_name=self.experts[expert_id].get("name", expert_id),
                        endpoint=self.experts[expert_id].get("endpoint", ""),
                        model=self.experts[expert_id].get("model", ""),
                        confidence=0.9 if confidence == "high" else 0.7,
                        reason="Complex task detected",
                        fallback=fallback
                    )

            elif "reasoning" in condition and any(kw in text_lower for kw in ["solve", "reason", "analyze", "decide", "think", "logic"]):
                if self._check_expert_health(expert_id):
                    return ExpertSelection(
                        expert_id=expert_id,
                        expert_name=self.experts[expert_id].get("name", expert_id),
                        endpoint=self.experts[expert_id].get("endpoint", ""),
                        model=self.experts[expert_id].get("model", ""),
                        confidence=0.8,
                        reason="Reasoning task detected"
                    )

            elif "quick" in condition and any(kw in text_lower for kw in ["quick", "fast", "simple", "easy"]):
                if self._check_expert_health(expert_id):
                    return ExpertSelection(
                        expert_id=expert_id,
                        expert_name=self.experts[expert_id].get("name", expert_id),
                        endpoint=self.experts[expert_id].get("endpoint", ""),
                        model=self.experts[expert_id].get("model", ""),
                        confidence=0.7,
                        reason="Quick task detected"
                    )

            elif "default" in condition:
                if self._check_expert_health(expert_id):
                    return ExpertSelection(
                        expert_id=expert_id,
                        expert_name=self.experts[expert_id].get("name", expert_id),
                        endpoint=self.experts[expert_id].get("endpoint", ""),
                        model=self.experts[expert_id].get("model", ""),
                        confidence=0.5,
                        reason="Default expert"
                    )

        return None

    def select_expert(self, prompt: str, task_type: Optional[str] = None) -> ExpertSelection:
        """
        Select the best expert for a given prompt

        Args:
            prompt: The user prompt/request
            task_type: Optional explicit task type (code, reasoning, etc.)

        Returns:
            ExpertSelection with selected expert
        """
        # Try rule-based matching first
        selection = self._match_expert_by_rules(prompt)

        # Fallback to keyword matching
        if not selection or selection.confidence < 0.6:
            keyword_selection = self._match_expert_by_keywords(prompt)
            if keyword_selection and keyword_selection.confidence > (selection.confidence if selection else 0):
                selection = keyword_selection

        # Final fallback to chain
        if not selection:
            for expert_id in self.fallback_chain:
                if self._check_expert_health(expert_id):
                    expert = self.experts[expert_id]
                    selection = ExpertSelection(
                        expert_id=expert_id,
                        expert_name=expert.get("name", expert_id),
                        endpoint=expert.get("endpoint", ""),
                        model=expert.get("model", ""),
                        confidence=0.3,
                        reason="Fallback chain selection"
                    )
                    break

        if not selection:
            # Last resort - use first available
            for expert_id, expert in self.experts.items():
                if self._check_expert_health(expert_id):
                    selection = ExpertSelection(
                        expert_id=expert_id,
                        expert_name=expert.get("name", expert_id),
                        endpoint=expert.get("endpoint", ""),
                        model=expert.get("model", ""),
                        confidence=0.1,
                        reason="Last resort - first available"
                    )
                    break

        return selection

    def route_request(self, prompt: str, task_type: Optional[str] = None) -> Dict:
        """
        Route a request to the appropriate expert and return response

        Args:
            prompt: User prompt
            task_type: Optional task type

        Returns:
            Dict with expert info and response
        """
        selection = self.select_expert(prompt, task_type)

        if not selection:
            return {
                "success": False,
                "error": "No available experts",
                "selection": None
            }

        # Make request to selected expert
        try:
            url = f"{selection.endpoint}/v1/chat/completions"
            payload = {
                "model": selection.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 500,
                "stream": False
            }

            response = requests.post(
                url,
                json=payload,
                timeout=60,
                headers={"Content-Type": "application/json"}
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "success": True,
                    "expert": selection.expert_id,
                    "expert_name": selection.expert_name,
                    "model": selection.model,
                    "confidence": selection.confidence,
                    "reason": selection.reason,
                    "response": data.get("choices", [{}])[0].get("message", {}).get("content", ""),
                    "full_response": data
                }
            else:
                # Try fallback if available
                if selection.fallback and self._check_expert_health(selection.fallback):
                    return self.route_request(prompt, task_type)  # Retry with fallback

                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text[:200]}",
                    "expert": selection.expert_id,
                    "selection": selection
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "expert": selection.expert_id,
                "selection": selection
            }

    def get_expert_status(self) -> Dict:
        """Get status of all experts"""
        status = {}
        for expert_id, expert in self.experts.items():
            is_healthy = self._check_expert_health(expert_id)
            status[expert_id] = {
                "name": expert.get("name", expert_id),
                "status": expert.get("status", "unknown"),
                "healthy": is_healthy,
                "endpoint": expert.get("endpoint", ""),
                "model": expert.get("model", "")
            }
        return status


def main():
    """Test the expert router"""
    import argparse

    parser = argparse.ArgumentParser(description="Iron Legion Expert Router")
    parser.add_argument("--prompt", help="Test prompt")
    parser.add_argument("--status", action="store_true", help="Show expert status")
    parser.add_argument("--test", action="store_true", help="Run test prompts")

    args = parser.parse_args()

    router = IronLegionExpertRouter()

    if args.status:
        print("\n🔍 Iron Legion Expert Status:\n")
        status = router.get_expert_status()
        for expert_id, info in status.items():
            health = "✅" if info["healthy"] else "❌"
            print(f"{health} {info['name']}: {info['status']} - {info['model']}")
        return

    if args.test:
        test_prompts = [
            "Write a Python function to calculate fibonacci numbers",
            "Explain quantum computing in simple terms",
            "Solve this math problem: 2x + 5 = 15",
            "Quick: what is the capital of France?",
            "Create a complex neural network architecture"
        ]

        for prompt in test_prompts:
            print(f"\n📝 Prompt: {prompt}")
            selection = router.select_expert(prompt)
            print(f"   → Selected: {selection.expert_name}")
            print(f"   → Confidence: {selection.confidence:.2f}")
            print(f"   → Reason: {selection.reason}")
        return

    if args.prompt:
        print(f"\n📝 Routing prompt: {args.prompt}\n")
        result = router.route_request(args.prompt)

        if result["success"]:
            print(f"✅ Expert: {result['expert_name']}")
            print(f"   Model: {result['model']}")
            print(f"   Confidence: {result['confidence']:.2f}")
            print(f"   Reason: {result['reason']}")
            print(f"\n📤 Response:\n{result['response']}")
        else:
            print(f"❌ Error: {result.get('error', 'Unknown error')}")
    else:
        print("Usage: python iron_legion_expert_router.py --prompt 'your prompt'")
        print("       python iron_legion_expert_router.py --status")
        print("       python iron_legion_expert_router.py --test")


if __name__ == "__main__":


    main()