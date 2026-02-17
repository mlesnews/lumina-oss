#!/usr/bin/env python3
"""
Enforce Local-First AI Routing System

Enforces local-first AI routing (ULTRON, KAIJU, R5) over cloud providers.
Integrates with:
- R5 Living Context Matrix
- Jedi Council / Jedi High Council
- AIQ (AI Quorum) decisioning
- Approval Board of Judges
- Decision Trees

Blocks cloud providers unless explicitly approved by Jedi Council/AIQ.

Tags: #LOCAL_FIRST #ULTRON #KAIJU #R5 #JEDI_COUNCIL #AIQ #DECISIONING @JARVIS @LUMINA @R5
"""

import sys
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("EnforceLocalFirstAIRouting")


class AIProviderType(Enum):
    """AI Provider types"""
    LOCAL_ULTRON = "local_ultron"
    LOCAL_KAIJU = "local_kaiju"
    LOCAL_R5 = "local_r5"
    CLOUD_OPENAI = "cloud_openai"
    CLOUD_ANTHROPIC = "cloud_anthropic"
    CLOUD_OTHER = "cloud_other"


class LocalFirstAIRouter:
    """
    Local-First AI Routing System

    Enforces routing to local-first AI systems (ULTRON, KAIJU, R5)
    with Jedi Council/AIQ approval for cloud fallback.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root

        # Local-first AI endpoints
        self.local_endpoints = {
            "ULTRON": "http://localhost:11434",
            "KAIJU": "http://<NAS_IP>:11434",  # KAIJU Number Eight (Desktop PC), NOT NAS
            "R5": "local"  # R5 is knowledge matrix, not an LLM endpoint
        }

        # Cloud provider detection patterns
        self.cloud_patterns = {
            "openai": ["gpt-", "openai", "o1-"],
            "anthropic": ["claude", "anthropic"],
            "other": ["api.openai.com", "api.anthropic.com"]
        }

        # Load integrations
        self.r5_available = False
        self.jedi_council_available = False
        self.aiq_available = False
        self.decision_tree_available = False

        self._load_integrations()

        # Routing statistics
        self.routing_stats = {
            "local_requests": 0,
            "cloud_requests": 0,
            "blocked_cloud": 0,
            "approved_cloud": 0
        }

        logger.info("✅ Local-First AI Router initialized")

    def _load_integrations(self):
        """Load LUMINA integrations"""
        # R5 integration
        try:
            from r5_living_context_matrix import R5LivingContextMatrix
            self.r5 = R5LivingContextMatrix(self.project_root)
            self.r5_available = True
            logger.info("✅ R5 integration loaded")
        except ImportError:
            self.r5 = None
            logger.warning("⚠️  R5 not available")

        # Decision Tree integration
        try:
            from universal_decision_tree import decide, DecisionContext, DecisionOutcome
            self.decision_tree_available = True
            self.decide = decide
            self.DecisionContext = DecisionContext
            self.DecisionOutcome = DecisionOutcome
            logger.info("✅ Decision Tree integration loaded")
        except ImportError:
            self.decide = None
            logger.warning("⚠️  Decision Tree not available")

        # Jedi Council / AIQ (would be custom integration)
        # For now, we'll use decision trees for routing decisions
        self.jedi_council_available = True  # Assume available via decision trees
        self.aiq_available = True  # Assume available via decision trees

    def route_request(self, request_type: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Route AI request to local-first system

        Policy: Use @local @ai @llm @agent resources over cloud AI providers,
        unless @bau #decisioning @r5 @matrix &| @lattice approves cloud usage.

        Args:
            request_type: Type of request (chat, completion, etc.)
            context: Request context

        Returns:
            Routing decision with endpoint and provider
        """
        if context is None:
            context = {}

        # Check if request is trying to use cloud provider
        model_name = context.get("model", "").lower()
        is_cloud = self._is_cloud_provider(model_name)

        if is_cloud:
            # Cloud provider detected - require @bau #decisioning @r5 @matrix/@lattice approval
            approval_result = self._require_jedi_council_approval(request_type, context, model_name)

            if not approval_result["approved"]:
                # Block cloud, route to local instead
                self.routing_stats["blocked_cloud"] += 1
                local_route = self._select_local_route(request_type, context)

                logger.warning(f"🚫 Cloud provider blocked: {model_name}")
                logger.info(f"✅ Routed to local instead: {local_route['provider']}")

                return {
                    "routed": True,
                    "provider": local_route["provider"],
                    "endpoint": local_route["endpoint"],
                    "model": local_route["model"],
                    "blocked_cloud": True,
                    "original_cloud_model": model_name,
                    "approval_required": True,
                    "approval_reason": approval_result.get("reason", "Cloud provider requires Jedi Council approval")
                }
            else:
                # Approved by Jedi Council/AIQ
                self.routing_stats["approved_cloud"] += 1
                self.routing_stats["cloud_requests"] += 1

                logger.info(f"✅ Cloud provider approved by Jedi Council: {model_name}")
                return {
                    "routed": True,
                    "provider": "cloud",
                    "endpoint": context.get("endpoint"),
                    "model": model_name,
                    "approved": True,
                    "approval_id": approval_result.get("approval_id")
                }
        else:
            # Local-first routing
            local_route = self._select_local_route(request_type, context)
            self.routing_stats["local_requests"] += 1

            logger.info(f"✅ Routed to local-first: {local_route['provider']}")
            return {
                "routed": True,
                "provider": local_route["provider"],
                "endpoint": local_route["endpoint"],
                "model": local_route["model"],
                "local_first": True
            }

    def _is_cloud_provider(self, model_name: str) -> bool:
        """Check if model name indicates cloud provider"""
        model_lower = model_name.lower()

        for provider, patterns in self.cloud_patterns.items():
            for pattern in patterns:
                if pattern in model_lower:
                    return True

        return False

    def _select_local_route(self, request_type: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Select best local-first route"""
        # Check ULTRON availability
        ultron_available = self._check_endpoint_available(self.local_endpoints["ULTRON"])

        # Check KAIJU availability
        kaiju_available = self._check_endpoint_available(self.local_endpoints["KAIJU"])

        # Use R5 matrix for context-aware routing
        if self.r5_available:
            # Query R5 for best local model based on context
            r5_recommendation = self._get_r5_recommendation(request_type, context)
            if r5_recommendation:
                return r5_recommendation

        # Default routing logic
        if ultron_available:
            return {
                "provider": "ULTRON",
                "endpoint": self.local_endpoints["ULTRON"],
                "model": "qwen2.5:72b",  # ULTRON's primary model
                "priority": 1
            }
        elif kaiju_available:
            return {
                "provider": "KAIJU",
                "endpoint": self.local_endpoints["KAIJU"],
                "model": "llama3.2:3b",  # KAIJU's primary model
                "priority": 2
            }
        else:
            # Fallback - should not happen if local-first is properly configured
            logger.error("❌ No local AI endpoints available!")
            return {
                "provider": "NONE",
                "endpoint": None,
                "model": None,
                "priority": 999
            }

    def _check_endpoint_available(self, endpoint: str) -> bool:
        """Check if local endpoint is available"""
        try:
            response = requests.get(f"{endpoint}/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def _get_r5_recommendation(self, request_type: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Get R5 matrix recommendation for local routing"""
        if not self.r5_available:
            return None

        try:
            # R5 would analyze context and recommend best local model
            # For now, return None to use default routing
            # In full implementation, R5 would query living context matrix
            return None
        except Exception as e:
            logger.debug(f"R5 recommendation error: {e}")
            return None

    def _require_jedi_council_approval(self, request_type: str, context: Dict[str, Any], model_name: str) -> Dict[str, Any]:
        """
        Require @bau #decisioning @r5 @matrix/@lattice approval for cloud provider usage

        Policy: Use @local @ai @llm @agent resources over cloud AI providers,
        unless @bau #decisioning @r5 @matrix &| @lattice approves cloud usage.

        Uses decision trees (@bau #decisioning) and R5 matrix for approval
        """
        if not self.decision_tree_available:
            # No decision tree - default to blocking cloud
            return {
                "approved": False,
                "reason": "Decision tree system not available - cloud blocked by default"
            }

        try:
            # Use decision tree for routing decision
            # DecisionContext takes project_root as optional parameter
            decision_context = self.DecisionContext(project_root=self.project_root)

            # Set context attributes
            decision_context.local_ai_available = True  # ULTRON/KAIJU should be available
            decision_context.custom_data = {
                "cloud_model_requested": True,
                "model": model_name,
                "request_type": request_type,
                "jedi_approved": False,  # Default to not approved
                **context
            }

            # Check if cloud usage is approved via decision tree
            result = self.decide("ai_routing", decision_context)

            # Decision tree returns USE_LOCAL or USE_CLOUD
            if result.outcome == DecisionOutcome.USE_CLOUD:
                return {
                    "approved": True,
                    "approval_id": f"jedi-{datetime.now().timestamp()}",
                    "reason": "Approved by Jedi Council via decision tree"
                }
            else:
                # USE_LOCAL or any other outcome blocks cloud
                return {
                    "approved": False,
                    "reason": "Rejected by Jedi Council/AIQ - use local-first AI (ULTRON/KAIJU/R5) instead"
                }
        except Exception as e:
            logger.warning(f"Jedi Council approval check failed: {e}")
            # Default to blocking cloud - local-first enforcement
            return {
                "approved": False,
                "reason": f"Approval system error: {e} - cloud blocked by default (local-first enforced)"
            }

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics"""
        total = sum(self.routing_stats.values())
        local_percent = (self.routing_stats["local_requests"] / total * 100) if total > 0 else 0
        cloud_percent = (self.routing_stats["cloud_requests"] / total * 100) if total > 0 else 0

        return {
            **self.routing_stats,
            "total_requests": total,
            "local_percent": f"{local_percent:.1f}%",
            "cloud_percent": f"{cloud_percent:.1f}%",
            "local_first_enforced": True
        }


def enforce_cursor_settings(project_root: Path):
    """Enforce local-first AI in Cursor settings"""
    cursor_settings = project_root / ".cursor" / "settings.json"

    if not cursor_settings.exists():
        logger.warning("Cursor settings.json not found")
        return False

    try:
        with open(cursor_settings, 'r') as f:
            config = json.load(f)

        # Ensure local models are default
        config["cursor.chat.defaultModel"] = "ULTRON"
        config["cursor.composer.defaultModel"] = "ULTRON"
        config["cursor.inlineCompletion.defaultModel"] = "ULTRON"

        # Add local-first enforcement flag
        if "lumina" not in config:
            config["lumina"] = {}
        config["lumina"]["local_first_enforced"] = True
        config["lumina"]["cloud_requires_approval"] = True
        config["lumina"]["jedi_council_approval_required"] = True

        # Save updated config
        with open(cursor_settings, 'w') as f:
            json.dump(config, f, indent=2)

        logger.info("✅ Cursor settings updated to enforce local-first AI")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to update Cursor settings: {e}")
        return False


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Enforce Local-First AI Routing")
        parser.add_argument("--enforce-cursor", action="store_true", help="Enforce in Cursor settings")
        parser.add_argument("--test", action="store_true", help="Test routing")

        args = parser.parse_args()

        router = LocalFirstAIRouter(project_root)

        if args.enforce_cursor:
            enforce_cursor_settings(project_root)

        if args.test:
            # Test routing
            print("Testing local-first routing...")

            # Test local request
            result1 = router.route_request("chat", {"model": "qwen2.5:72b"})
            print(f"Local request: {result1}")

            # Test cloud request (should be blocked)
            result2 = router.route_request("chat", {"model": "gpt-4"})
            print(f"Cloud request: {result2}")

            # Print stats
            stats = router.get_routing_stats()
            print(f"\nRouting Stats: {json.dumps(stats, indent=2)}")

        print("\n✅ Local-First AI Routing System Ready")
        print("   - ULTRON: Primary local endpoint")
        print("   - KAIJU: Secondary local endpoint (NAS)")
        print("   - R5: Context-aware routing")
        print("   - Jedi Council/AIQ: Cloud approval required")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()