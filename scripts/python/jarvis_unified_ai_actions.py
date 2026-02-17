#!/usr/bin/env python3
"""
JARVIS Unified AI Actions
Unified interface for JARVIS to interact with ALL AI systems on the laptop
Similar to Synology AI integration, but for all local AI systems
#JARVIS #AI #UNIFIED #LOCAL #LLM #OLLAMA #COORDINATION
"""

import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISUnifiedAIActions")

# Import AI systems
try:
    from jarvis_local_first_llm_router import JARVISLocalFirstLLMRouter, LLMProvider
    LLM_ROUTER_AVAILABLE = True
except ImportError:
    LLM_ROUTER_AVAILABLE = False
    logger.warning("JARVISLocalFirstLLMRouter not available")

try:
    from jarvis_ai_coordination import JARVISAICoordination, AIType
    AI_COORDINATION_AVAILABLE = True
except ImportError:
    AI_COORDINATION_AVAILABLE = False
    logger.warning("JARVISAICoordination not available")

try:
    from intelligent_llm_router import IntelligentLLMRouter, RoutingStrategy
    INTELLIGENT_ROUTER_AVAILABLE = True
except ImportError:
    INTELLIGENT_ROUTER_AVAILABLE = False
    logger.warning("IntelligentLLMRouter not available")


class JARVISUnifiedAIActions:
    """
    Unified interface for JARVIS to interact with ALL AI systems

    Provides high-level commands for:
    - LLM routing and querying
    - AI coordination and synchronization
    - Model management
    - Health monitoring
    - Usage statistics
    """

    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize JARVIS Unified AI Actions

        Args:
            project_root: Project root directory
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Initialize AI systems
        self.llm_router: Optional[JARVISLocalFirstLLMRouter] = None
        self.ai_coordination: Optional[JARVISAICoordination] = None
        self.intelligent_router: Optional[IntelligentLLMRouter] = None

        if LLM_ROUTER_AVAILABLE:
            try:
                self.llm_router = JARVISLocalFirstLLMRouter(self.project_root)
                logger.info("✅ Local-First LLM Router initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize LLM Router: {e}")

        if AI_COORDINATION_AVAILABLE:
            try:
                self.ai_coordination = JARVISAICoordination(self.project_root)
                logger.info("✅ AI Coordination initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize AI Coordination: {e}")

        if INTELLIGENT_ROUTER_AVAILABLE:
            try:
                self.intelligent_router = IntelligentLLMRouter(RoutingStrategy.ADAPTIVE)
                logger.info("✅ Intelligent LLM Router initialized")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize Intelligent Router: {e}")

        logger.info("🤖 JARVIS Unified AI Actions initialized")
        logger.info(f"   LLM Router: {'✅' if self.llm_router else '❌'}")
        logger.info(f"   AI Coordination: {'✅' if self.ai_coordination else '❌'}")
        logger.info(f"   Intelligent Router: {'✅' if self.intelligent_router else '❌'}")

    def list_available_ais(self) -> Dict[str, Any]:
        """
        List all available AI systems

        Returns:
            Dict with AI systems and their status
        """
        ais = {
            "llm_providers": [],
            "ai_systems": [],
            "coordination_status": {}
        }

        # Get LLM providers
        if self.llm_router:
            try:
                available = self.llm_router.get_available_providers(include_cloud=False)
                for provider in available:
                    provider_config = self.llm_router.providers[provider]
                    ais["llm_providers"].append({
                        "id": provider.value,
                        "name": provider.value.replace("_", " ").title(),
                        "priority": provider_config.get("priority"),
                        "base_url": provider_config.get("base_url"),
                        "models": provider_config.get("models", []),
                        "healthy": self.llm_router.provider_health.get(provider, False)
                    })
            except Exception as e:
                logger.error(f"Error getting LLM providers: {e}")

        # Get AI systems from coordination
        if self.ai_coordination:
            try:
                for ai_id, ai_info in self.ai_coordination.ai_registry.items():
                    ais["ai_systems"].append({
                        "id": ai_id,
                        "name": ai_info.ai_name,
                        "type": ai_info.ai_type.value,
                        "status": ai_info.status,
                        "synced": ai_info.synced,
                        "capabilities": ai_info.capabilities,
                        "coordination_level": ai_info.coordination_level
                    })

                ais["coordination_status"] = {
                    "active": self.ai_coordination.coordination_active,
                    "total_ais": len(self.ai_coordination.ai_registry)
                }
            except Exception as e:
                logger.error(f"Error getting AI systems: {e}")

        return {
            "success": True,
            "ais": ais,
            "timestamp": datetime.now().isoformat()
        }

    def query_llm(self, prompt: str, model: Optional[str] = None, 
                  allow_cloud: bool = False, provider: Optional[str] = None) -> Dict[str, Any]:
        """
        Query an LLM (routed automatically)

        Args:
            prompt: The prompt to send
            model: Specific model to use (optional)
            allow_cloud: Allow cloud fallback (default: False)
            provider: Specific provider to use (optional)

        Returns:
            Dict with response and provider used
        """
        if not self.llm_router:
            return {
                "success": False,
                "error": "LLM Router not available"
            }

        try:
            # Use intelligent router if available and no specific provider
            if self.intelligent_router and not provider:
                # Use intelligent routing
                logger.info("🧠 Using intelligent routing...")
                # This would use the intelligent router's adaptive routing
                # For now, fall back to local-first router
                pass

            # Route request
            result = self.llm_router.route_request(
                prompt=prompt,
                model=model,
                allow_cloud=allow_cloud
            )

            return {
                "success": result.get("success", False),
                "response": result.get("response", ""),
                "provider": result.get("provider"),
                "model": result.get("model"),
                "usage_stats": self.llm_router.usage_stats if result.get("success") else None,
                "error": result.get("error")
            }

        except Exception as e:
            logger.error(f"Error querying LLM: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_llm_health(self) -> Dict[str, Any]:
        """
        Get health status of all LLM providers

        Returns:
            Dict with health status
        """
        if not self.llm_router:
            return {
                "success": False,
                "error": "LLM Router not available"
            }

        health = {}
        for provider in LLMProvider:
            is_healthy = self.llm_router.provider_health.get(provider, False)
            provider_config = self.llm_router.providers.get(provider, {})

            health[provider.value] = {
                "healthy": is_healthy,
                "enabled": provider_config.get("enabled", False),
                "priority": provider_config.get("priority"),
                "base_url": provider_config.get("base_url")
            }

        return {
            "success": True,
            "health": health,
            "last_check": self.llm_router.last_health_check.isoformat() if self.llm_router.last_health_check else None
        }

    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics

        Returns:
            Dict with usage stats
        """
        stats = {}

        if self.llm_router:
            stats["llm_router"] = self.llm_router.usage_stats.copy()

        if self.intelligent_router:
            # Get metrics from intelligent router
            stats["intelligent_router"] = {
                "total_requests": len(self.intelligent_router.routing_history),
                "strategy": self.intelligent_router.routing_strategy.value
            }

        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.now().isoformat()
        }

    def sync_all_ais(self) -> Dict[str, Any]:
        """
        Synchronize with all AI systems

        Returns:
            Dict with sync results
        """
        if not self.ai_coordination:
            return {
                "success": False,
                "error": "AI Coordination not available"
            }

        results = {}

        try:
            for ai_id in self.ai_coordination.ai_registry.keys():
                try:
                    synced = self.ai_coordination.sync_with_ai(ai_id, force=True)
                    results[ai_id] = {
                        "success": synced,
                        "synced_at": datetime.now().isoformat()
                    }
                except Exception as e:
                    results[ai_id] = {
                        "success": False,
                        "error": str(e)
                    }

            return {
                "success": True,
                "results": results,
                "total": len(results),
                "successful": sum(1 for r in results.values() if r.get("success"))
            }

        except Exception as e:
            logger.error(f"Error syncing AIs: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def execute_action(self, action: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a JARVIS AI action

        Args:
            action: Action name
            **kwargs: Action-specific parameters

        Returns:
            Dict with action result
        """
        action_map = {
            "list_ais": self.list_available_ais,
            "query_llm": lambda: self.query_llm(
                kwargs.get("prompt", ""),
                kwargs.get("model"),
                kwargs.get("allow_cloud", False),
                kwargs.get("provider")
            ),
            "llm_health": self.get_llm_health,
            "usage_stats": self.get_usage_statistics,
            "sync_ais": self.sync_all_ais
        }

        if action not in action_map:
            return {
                "success": False,
                "error": f"Unknown action: {action}",
                "available_actions": list(action_map.keys())
            }

        try:
            result = action_map[action]()
            result["action"] = action
            result["timestamp"] = datetime.now().isoformat()
            return result
        except Exception as e:
            logger.error(f"Error executing action {action}: {e}")
            return {
                "success": False,
                "error": str(e),
                "action": action
            }

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - cleanup"""
        pass


def main():
    """CLI interface for JARVIS Unified AI Actions"""
    import argparse
    import json

    parser = argparse.ArgumentParser(description="JARVIS Unified AI Actions")
    parser.add_argument("--action", required=True,
                       choices=["list_ais", "query_llm", "llm_health", "usage_stats", "sync_ais"],
                       help="Action to execute")
    parser.add_argument("--prompt", help="Prompt for query_llm action")
    parser.add_argument("--model", help="Model name (optional)")
    parser.add_argument("--allow-cloud", action="store_true", help="Allow cloud fallback")
    parser.add_argument("--provider", help="Specific provider to use")
    parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    try:
        with JARVISUnifiedAIActions() as jarvis:
            kwargs = {}
            if args.prompt:
                kwargs["prompt"] = args.prompt
            if args.model:
                kwargs["model"] = args.model
            if args.allow_cloud:
                kwargs["allow_cloud"] = True
            if args.provider:
                kwargs["provider"] = args.provider

            result = jarvis.execute_action(args.action, **kwargs)

            if args.json:
                print(json.dumps(result, indent=2))
            else:
                # Pretty print
                if result.get("success"):
                    print("✅ Success!")
                    print(json.dumps(result, indent=2))
                else:
                    print(f"❌ Error: {result.get('error', 'Unknown error')}")
                    return 1

            return 0 if result.get("success") else 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())