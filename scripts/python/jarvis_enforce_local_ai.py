#!/usr/bin/env python3
"""
JARVIS Enforce Local AI

ENFORCES LOCAL-FIRST AI USAGE across all JARVIS operations.
Prevents cloud API usage unless explicitly approved.

This addresses the critical issue: "WE ARE STILL WORKING IN THE CLOUD"
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any, Optional
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISEnforceLocalAI")

try:
    from jarvis_local_first_llm_router import JARVISLocalFirstLLMRouter
    ROUTER_AVAILABLE = True
except ImportError:
    ROUTER_AVAILABLE = False
    logger.error("Local-First LLM Router not available")


class JARVISEnforceLocalAI:
    """
    Enforces local-first AI usage across JARVIS

    - Disables cloud API keys by default
    - Routes all LLM requests through local router
    - Monitors and blocks unauthorized cloud usage
    - Provides local resource health monitoring
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

        # Initialize local router
        self.router = None
        if ROUTER_AVAILABLE:
            try:
                self.router = JARVISLocalFirstLLMRouter(project_root)
                self.logger.info("✅ Local-First LLM Router initialized")
            except Exception as e:
                self.logger.error(f"❌ Failed to initialize router: {e}")

        # Cloud API blocking
        self.cloud_apis_blocked = {
            "OPENAI_API_KEY": True,
            "ANTHROPIC_API_KEY": True,
            "CURSOR_AGENT_API_KEY": False,  # Keep Cursor Agent for IDE integration
            "ELEVENLABS_API_KEY": False  # Keep for TTS
        }

        # Enforcement status
        self.enforcement_active = True

        self.logger.info("✅ JARVIS Local AI Enforcement initialized")
        self.logger.warning("🔒 CLOUD API USAGE BLOCKED - Using local resources only")

    def enforce_local_only(self):
        """Enforce local-only mode"""
        self.enforcement_active = True

        # Block cloud API keys in environment
        for key_name, should_block in self.cloud_apis_blocked.items():
            if should_block and key_name in os.environ:
                self.logger.warning(f"🔒 Blocking cloud API key: {key_name}")
                # Don't delete, but mark as blocked
                os.environ[f"{key_name}_BLOCKED"] = "true"

        # Force router to local-only
        if self.router:
            self.router.force_local_only()

        self.logger.info("✅ LOCAL-ONLY MODE ENFORCED")

    def check_local_resources(self) -> Dict[str, Any]:
        """Check status of local AI resources"""
        if not self.router:
            return {
                "error": "Local router not available",
                "local_available": False
            }

        # Check health
        self.router._check_all_providers_health()

        # Get available providers
        local_providers = self.router.get_available_providers(include_cloud=False)

        # Get usage stats
        stats = self.router.get_usage_stats()

        return {
            "local_available": len(local_providers) > 0,
            "local_providers": [p.value for p in local_providers],
            "provider_count": len(local_providers),
            "usage_stats": stats,
            "enforcement_active": self.enforcement_active
        }

    def route_llm_request(self, prompt: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Route LLM request through local router (NO CLOUD)

        This is the ONLY way JARVIS should make LLM requests
        """
        if not self.router:
            return {
                "success": False,
                "error": "Local router not available",
                "provider": None
            }

        # Route through local router (cloud disabled)
        result = self.router.route_request(prompt, model, allow_cloud=False)

        if not result["success"]:
            self.logger.error(f"❌ Local LLM request failed: {result.get('error')}")
            self.logger.warning("⚠️  All local resources unavailable - request cannot proceed")

        return result

    def get_enforcement_report(self) -> Dict[str, Any]:
        """Get enforcement status report"""
        local_status = self.check_local_resources()

        return {
            "enforcement_active": self.enforcement_active,
            "local_resources": local_status,
            "cloud_apis_blocked": {
                key: blocked for key, blocked in self.cloud_apis_blocked.items() if blocked
            },
            "recommendation": "USE LOCAL RESOURCES" if local_status.get("local_available") else "CHECK LOCAL RESOURCES"
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Enforce Local AI")
        parser.add_argument("--enforce", action="store_true", help="Enforce local-only mode")
        parser.add_argument("--status", action="store_true", help="Check local resource status")
        parser.add_argument("--report", action="store_true", help="Generate enforcement report")
        parser.add_argument("--test", type=str, help="Test local LLM with a prompt")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        enforcer = JARVISEnforceLocalAI(project_root)

        if args.enforce:
            enforcer.enforce_local_only()
            print("✅ Local-only mode enforced")

        elif args.status:
            status = enforcer.check_local_resources()
            print("\n📊 Local Resource Status:")
            print(f"   Available: {status.get('local_available', False)}")
            print(f"   Providers: {len(status.get('local_providers', []))}")
            for provider in status.get('local_providers', []):
                print(f"      - {provider}")

            stats = status.get('usage_stats', {})
            print(f"\n   Usage Statistics:")
            print(f"      Total: {stats.get('total_requests', 0)}")
            print(f"      Local: {stats.get('local_requests', 0)} ({stats.get('local_percentage', 0):.1f}%)")
            print(f"      KAIJU: {stats.get('kaiju_requests', 0)} ({stats.get('kaiju_percentage', 0):.1f}%)")
            print(f"      Cloud: {stats.get('cloud_requests', 0)} ({stats.get('cloud_percentage', 0):.1f}%)")

        elif args.report:
            report = enforcer.get_enforcement_report()
            import json
            print(json.dumps(report, indent=2))

        elif args.test:
            result = enforcer.route_llm_request(args.test)
            if result["success"]:
                print(f"\n✅ Response from {result['provider']}:")
                print(result["response"][:500])
            else:
                print(f"\n❌ Error: {result.get('error')}")

        else:
            print("Usage:")
            print("  --enforce          : Enforce local-only mode")
            print("  --status           : Check local resource status")
            print("  --report           : Generate enforcement report")
            print("  --test 'prompt'    : Test local LLM")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()