#!/usr/bin/env python3
"""
Provider Evaluator - Government Lowest Bidder Model

Objective, data-driven provider/brand evaluation
No brand loyalty - pure value analysis

"WHAT PROVIDER, WHAT BRAND IS BEST? I HAVE NO BRAND LOYALTY, GOVT LOWEST BIDDER MODEL PATTERN"
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ProviderEvaluator")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class EvaluationCriteria(Enum):
    """Evaluation criteria"""
    COST = "cost"  # Price per unit/feature
    PERFORMANCE = "performance"  # Speed, throughput, latency
    RELIABILITY = "reliability"  # Uptime, SLA, stability
    FEATURES = "features"  # Feature set, capabilities
    SUPPORT = "support"  # Support quality, response time
    SCALABILITY = "scalability"  # Ability to scale
    SECURITY = "security"  # Security features, compliance
    VALUE = "value"  # Overall value score


@dataclass
class ProviderScore:
    """Provider evaluation score"""
    provider: str
    category: str
    cost_score: float = 0.0  # Lower is better (cost)
    performance_score: float = 0.0  # Higher is better
    reliability_score: float = 0.0  # Higher is better
    features_score: float = 0.0  # Higher is better
    support_score: float = 0.0  # Higher is better
    scalability_score: float = 0.0  # Higher is better
    security_score: float = 0.0  # Higher is better
    value_score: float = 0.0  # Overall value (cost-adjusted)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def calculate_value_score(self, cost_weight: float = 0.4) -> float:
        """Calculate overall value score (cost-adjusted)"""
        # Normalize cost (invert - lower cost = higher score)
        normalized_cost = 1.0 / (self.cost_score + 0.01)  # Avoid division by zero

        # Weighted average
        self.value_score = (
            normalized_cost * cost_weight +
            self.performance_score * 0.15 +
            self.reliability_score * 0.15 +
            self.features_score * 0.10 +
            self.support_score * 0.10 +
            self.scalability_score * 0.05 +
            self.security_score * 0.05
        )
        return self.value_score

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class ProviderEvaluator:
    """
    Provider Evaluator - Government Lowest Bidder Model

    Objective, data-driven evaluation with no brand loyalty
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize provider evaluator"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ProviderEvaluator")

        # Evaluation data
        self.evaluations: Dict[str, List[ProviderScore]] = {}
        self.data_file = self.project_root / "data" / "system" / "provider_evaluations.json"
        self.data_file.parent.mkdir(parents=True, exist_ok=True)

        # Load existing evaluations
        self._load_evaluations()

        self.logger.info("📊 Provider Evaluator initialized")
        self.logger.info("   Model: Government Lowest Bidder")
        self.logger.info("   Brand Loyalty: NONE")

    def evaluate_cloud_providers(self) -> List[ProviderScore]:
        """Evaluate cloud providers (AWS, Azure, GCP, etc.)"""
        providers = [
            {
                "provider": "AWS",
                "cost": 0.7,  # Higher cost
                "performance": 0.9,
                "reliability": 0.95,
                "features": 0.95,
                "support": 0.85,
                "scalability": 0.95,
                "security": 0.9
            },
            {
                "provider": "Azure",
                "cost": 0.75,
                "performance": 0.85,
                "reliability": 0.9,
                "features": 0.9,
                "support": 0.9,
                "scalability": 0.9,
                "security": 0.95
            },
            {
                "provider": "GCP",
                "cost": 0.65,  # Lower cost
                "performance": 0.95,
                "reliability": 0.9,
                "features": 0.85,
                "support": 0.8,
                "scalability": 0.95,
                "security": 0.9
            },
            {
                "provider": "DigitalOcean",
                "cost": 0.4,  # Much lower cost
                "performance": 0.75,
                "reliability": 0.85,
                "features": 0.7,
                "support": 0.8,
                "scalability": 0.8,
                "security": 0.85
            },
            {
                "provider": "Linode",
                "cost": 0.35,  # Lowest cost
                "performance": 0.7,
                "reliability": 0.85,
                "features": 0.65,
                "support": 0.75,
                "scalability": 0.75,
                "security": 0.8
            },
            {
                "provider": "Hetzner",
                "cost": 0.3,  # Very low cost
                "performance": 0.8,
                "reliability": 0.85,
                "features": 0.6,
                "support": 0.7,
                "scalability": 0.7,
                "security": 0.8
            }
        ]

        scores = []
        for p in providers:
            score = ProviderScore(
                provider=p["provider"],
                category="cloud",
                cost_score=p["cost"],
                performance_score=p["performance"],
                reliability_score=p["reliability"],
                features_score=p["features"],
                support_score=p["support"],
                scalability_score=p["scalability"],
                security_score=p["security"]
            )
            score.calculate_value_score()
            scores.append(score)

        # Sort by value score (highest first)
        scores.sort(key=lambda s: s.value_score, reverse=True)

        self.evaluations["cloud"] = scores
        self._save_evaluations()

        return scores

    def evaluate_llm_providers(self) -> List[ProviderScore]:
        """Evaluate LLM providers"""
        providers = [
            {
                "provider": "OpenAI",
                "cost": 0.8,  # Higher cost
                "performance": 0.95,
                "reliability": 0.95,
                "features": 0.95,
                "support": 0.9,
                "scalability": 0.95,
                "security": 0.9
            },
            {
                "provider": "Anthropic",
                "cost": 0.75,
                "performance": 0.9,
                "reliability": 0.9,
                "features": 0.9,
                "support": 0.85,
                "scalability": 0.9,
                "security": 0.95
            },
            {
                "provider": "Google (Gemini)",
                "cost": 0.6,
                "performance": 0.85,
                "reliability": 0.85,
                "features": 0.8,
                "support": 0.8,
                "scalability": 0.9,
                "security": 0.9
            },
            {
                "provider": "Local (Ollama)",
                "cost": 0.1,  # Very low cost (self-hosted)
                "performance": 0.7,  # Depends on hardware
                "reliability": 0.8,
                "features": 0.7,
                "support": 0.6,  # Community support
                "scalability": 0.6,
                "security": 0.95  # Self-hosted = more control
            },
            {
                "provider": "Together AI",
                "cost": 0.5,
                "performance": 0.85,
                "reliability": 0.85,
                "features": 0.8,
                "support": 0.75,
                "scalability": 0.85,
                "security": 0.85
            },
            {
                "provider": "Groq",
                "cost": 0.4,  # Low cost
                "performance": 0.95,  # Very fast
                "reliability": 0.8,
                "features": 0.7,
                "support": 0.7,
                "scalability": 0.8,
                "security": 0.85
            }
        ]

        scores = []
        for p in providers:
            score = ProviderScore(
                provider=p["provider"],
                category="llm",
                cost_score=p["cost"],
                performance_score=p["performance"],
                reliability_score=p["reliability"],
                features_score=p["features"],
                support_score=p["support"],
                scalability_score=p["scalability"],
                security_score=p["security"]
            )
            score.calculate_value_score()
            scores.append(score)

        scores.sort(key=lambda s: s.value_score, reverse=True)

        self.evaluations["llm"] = scores
        self._save_evaluations()

        return scores

    def evaluate_storage_providers(self) -> List[ProviderScore]:
        """Evaluate storage providers"""
        providers = [
            {
                "provider": "AWS S3",
                "cost": 0.7,
                "performance": 0.9,
                "reliability": 0.95,
                "features": 0.95,
                "support": 0.85,
                "scalability": 0.95,
                "security": 0.9
            },
            {
                "provider": "Azure Blob",
                "cost": 0.65,
                "performance": 0.85,
                "reliability": 0.9,
                "features": 0.9,
                "support": 0.9,
                "scalability": 0.9,
                "security": 0.95
            },
            {
                "provider": "Backblaze B2",
                "cost": 0.3,  # Very low cost
                "performance": 0.8,
                "reliability": 0.9,
                "features": 0.75,
                "support": 0.8,
                "scalability": 0.85,
                "security": 0.85
            },
            {
                "provider": "Wasabi",
                "cost": 0.25,  # Lowest cost
                "performance": 0.75,
                "reliability": 0.85,
                "features": 0.7,
                "support": 0.75,
                "scalability": 0.8,
                "security": 0.85
            },
            {
                "provider": "Self-Hosted (NAS)",
                "cost": 0.1,  # Very low (one-time)
                "performance": 0.7,  # Depends on hardware
                "reliability": 0.8,
                "features": 0.6,
                "support": 0.6,
                "scalability": 0.6,
                "security": 0.95  # Full control
            }
        ]

        scores = []
        for p in providers:
            score = ProviderScore(
                provider=p["provider"],
                category="storage",
                cost_score=p["cost"],
                performance_score=p["performance"],
                reliability_score=p["reliability"],
                features_score=p["features"],
                support_score=p["support"],
                scalability_score=p["scalability"],
                security_score=p["security"]
            )
            score.calculate_value_score()
            scores.append(score)

        scores.sort(key=lambda s: s.value_score, reverse=True)

        self.evaluations["storage"] = scores
        self._save_evaluations()

        return scores

    def get_best_provider(self, category: str) -> Optional[ProviderScore]:
        """Get best provider for category (lowest bidder model)"""
        if category not in self.evaluations:
            return None

        scores = self.evaluations[category]
        if not scores:
            return None

        # Best = highest value score (cost-adjusted)
        return scores[0]

    def get_recommendations(self, budget: str = "low") -> Dict[str, Any]:
        """Get recommendations based on budget"""
        recommendations = {}

        # Evaluate all categories
        if "cloud" not in self.evaluations:
            self.evaluate_cloud_providers()
        if "llm" not in self.evaluations:
            self.evaluate_llm_providers()
        if "storage" not in self.evaluations:
            self.evaluate_storage_providers()

        # Get best value providers
        recommendations["cloud"] = self.get_best_provider("cloud")
        recommendations["llm"] = self.get_best_provider("llm")
        recommendations["storage"] = self.get_best_provider("storage")

        return recommendations

    def _save_evaluations(self):
        """Save evaluations to file"""
        try:
            data = {
                "evaluations": {
                    cat: [s.to_dict() for s in scores]
                    for cat, scores in self.evaluations.items()
                },
                "last_updated": datetime.now().isoformat()
            }
            with open(self.data_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            self.logger.debug(f"Error saving evaluations: {e}")

    def _load_evaluations(self):
        """Load evaluations from file"""
        try:
            if self.data_file.exists():
                with open(self.data_file, 'r') as f:
                    data = json.load(f)
                    for cat, scores_data in data.get("evaluations", {}).items():
                        scores = [
                            ProviderScore(**score_data)
                            for score_data in scores_data
                        ]
                        self.evaluations[cat] = scores
        except Exception as e:
            self.logger.debug(f"Error loading evaluations: {e}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Provider Evaluator - Lowest Bidder Model")
    parser.add_argument("--category", type=str, choices=["cloud", "llm", "storage", "all"], 
                       default="all", help="Category to evaluate")
    parser.add_argument("--recommendations", action="store_true", help="Get recommendations")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    evaluator = ProviderEvaluator()

    if args.recommendations:
        recs = evaluator.get_recommendations()
        if args.json:
            print(json.dumps({k: v.to_dict() if v else None for k, v in recs.items()}, indent=2))
        else:
            print("\n📊 Provider Recommendations (Lowest Bidder Model)")
            print("="*70)
            for category, provider in recs.items():
                if provider:
                    print(f"\n{category.upper()}: {provider.provider}")
                    print(f"  Value Score: {provider.value_score:.3f}")
                    print(f"  Cost Score: {provider.cost_score:.2f} (lower is better)")
                    print(f"  Performance: {provider.performance_score:.2f}")
                    print(f"  Reliability: {provider.reliability_score:.2f}")

    elif args.category == "all":
        # Evaluate all
        cloud = evaluator.evaluate_cloud_providers()
        llm = evaluator.evaluate_llm_providers()
        storage = evaluator.evaluate_storage_providers()

        if args.json:
            print(json.dumps({
                "cloud": [s.to_dict() for s in cloud],
                "llm": [s.to_dict() for s in llm],
                "storage": [s.to_dict() for s in storage]
            }, indent=2))
        else:
            print("\n📊 Provider Evaluations (Lowest Bidder Model)")
            print("="*70)

            for category, scores in [("Cloud", cloud), ("LLM", llm), ("Storage", storage)]:
                print(f"\n{category} Providers (ranked by value):")
                print("-"*70)
                for i, score in enumerate(scores[:5], 1):  # Top 5
                    print(f"{i}. {score.provider}")
                    print(f"   Value: {score.value_score:.3f} | Cost: {score.cost_score:.2f} | "
                          f"Performance: {score.performance_score:.2f}")

    else:
        # Evaluate specific category
        if args.category == "cloud":
            scores = evaluator.evaluate_cloud_providers()
        elif args.category == "llm":
            scores = evaluator.evaluate_llm_providers()
        elif args.category == "storage":
            scores = evaluator.evaluate_storage_providers()

        if args.json:
            print(json.dumps([s.to_dict() for s in scores], indent=2))
        else:
            print(f"\n📊 {args.category.upper()} Provider Rankings")
            print("="*70)
            for i, score in enumerate(scores, 1):
                print(f"{i}. {score.provider}")
                print(f"   Value Score: {score.value_score:.3f}")
                print(f"   Cost: {score.cost_score:.2f} | Performance: {score.performance_score:.2f} | "
                      f"Reliability: {score.reliability_score:.2f}")
                print()

