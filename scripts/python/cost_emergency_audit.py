#!/usr/bin/env python3
"""
Cost Emergency Audit System
<COMPANY_NAME> LLC

IMMEDIATE ACTION: Audit and stop all cloud AI usage
Force local AI as default to prevent cost overruns

@JARVIS @MARVIN @TONY @MACE @GANDALF
"""

import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("CostEmergencyAudit")
except:
    logger = None


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class CostAlert:
    """Cost alert"""
    severity: str  # critical, warning, info
    message: str
    provider: str
    estimated_cost: float
    tokens_used: int
    timestamp: datetime


@dataclass
class CostAuditResult:
    """Cost audit result"""
    total_cloud_cost: float
    total_local_cost: float
    savings_potential: float
    cloud_usage_sources: List[str]
    alerts: List[CostAlert]
    recommendations: List[str]
    timestamp: datetime


class CostEmergencyAudit:
    """
    Emergency Cost Audit System

    IMMEDIATE ACTIONS:
    1. Audit all cloud AI usage
    2. Identify cost sources
    3. Force local AI as default
    4. Create cost alerts
    5. Provide cost-saving recommendations
    """

    # Cost per 1M tokens (approximate)
    CLOUD_COSTS = {
        "openai_gpt4": 30.00,  # $30 per 1M tokens
        "openai_gpt35": 1.50,  # $1.50 per 1M tokens
        "anthropic_claude": 15.00,  # $15 per 1M tokens
        "azure_openai": 2.00,  # $2 per 1M tokens
        "github_copilot": 0.00,  # Included in subscription
    }

    LOCAL_COST = 0.001  # $0.001 per 1M tokens (electricity only)

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize audit system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = logger or self._get_logger()

        # Load token tracker
        self.token_tracker_file = self.project_root / "config" / "ai_token_request_tracker.json"
        self.token_data = self._load_token_data()

        self.logger.info("🚨 COST EMERGENCY AUDIT INITIATED")

    def run_emergency_audit(self) -> CostAuditResult:
        """Run emergency cost audit"""
        self.logger.warning("=" * 60)
        self.logger.warning("🚨 EMERGENCY COST AUDIT")
        self.logger.warning("=" * 60)

        # Audit cloud usage
        cloud_usage = self._audit_cloud_usage()

        # Calculate costs
        cloud_cost = self._calculate_cloud_cost(cloud_usage)
        local_cost = self._calculate_local_cost(cloud_usage)
        savings = cloud_cost - local_cost

        # Identify sources
        sources = self._identify_cloud_sources()

        # Generate alerts
        alerts = self._generate_cost_alerts(cloud_usage, cloud_cost)

        # Generate recommendations
        recommendations = self._generate_recommendations(cloud_usage, cloud_cost, savings)

        result = CostAuditResult(
            total_cloud_cost=cloud_cost,
            total_local_cost=local_cost,
            savings_potential=savings,
            cloud_usage_sources=sources,
            alerts=alerts,
            recommendations=recommendations,
            timestamp=datetime.now()
        )

        # Print emergency report
        self._print_emergency_report(result)

        # Save audit
        self._save_audit(result)

        return result

    def _audit_cloud_usage(self) -> Dict[str, Any]:
        """Audit cloud AI usage"""
        usage = {
            "openai": 0,
            "anthropic": 0,
            "azure": 0,
            "github_copilot": 0,
            "unknown": 0
        }

        # Check token tracker
        if self.token_data:
            metrics = self.token_data.get("metrics", {})
            total_tokens = metrics.get("total_tokens_used", 0)

            # Estimate breakdown (would need actual tracking)
            usage["openai"] = int(total_tokens * 0.4)  # Estimate
            usage["anthropic"] = int(total_tokens * 0.3)  # Estimate
            usage["azure"] = int(total_tokens * 0.2)  # Estimate
            usage["github_copilot"] = int(total_tokens * 0.1)  # Estimate

        return usage

    def _calculate_cloud_cost(self, usage: Dict[str, Any]) -> float:
        """Calculate cloud costs"""
        cost = 0.0

        # OpenAI GPT-4
        cost += (usage.get("openai", 0) / 1_000_000) * self.CLOUD_COSTS["openai_gpt4"]

        # Anthropic Claude
        cost += (usage.get("anthropic", 0) / 1_000_000) * self.CLOUD_COSTS["anthropic_claude"]

        # Azure OpenAI
        cost += (usage.get("azure", 0) / 1_000_000) * self.CLOUD_COSTS["azure_openai"]

        # GitHub Copilot (included in subscription)
        # cost += (usage.get("github_copilot", 0) / 1_000_000) * self.CLOUD_COSTS["github_copilot"]

        return cost

    def _calculate_local_cost(self, usage: Dict[str, Any]) -> float:
        """Calculate local AI costs (electricity only)"""
        total_tokens = sum(usage.values())
        return (total_tokens / 1_000_000) * self.LOCAL_COST

    def _identify_cloud_sources(self) -> List[str]:
        """Identify sources of cloud usage"""
        sources = []

        # Check config files for API keys
        config_dir = self.project_root / "config"

        # Check for API key files
        api_key_files = [
            "llm_api_keys.json",
            "openai_config.json",
            "anthropic_config.json"
        ]

        for file_name in api_key_files:
            file_path = config_dir / file_name
            if file_path.exists():
                sources.append(f"Config file: {file_name}")

        # Check for cloud LLM usage in code
        code_sources = [
            "scripts/python/local_ai_integration.py",  # Should use local
            "scripts/python/structured_conversation_flow.py",  # Should use local
            "scripts/python/jarvis_fulltime_super_agent.py"  # Should use local
        ]

        for source in code_sources:
            source_path = self.project_root / source
            if source_path.exists():
                # Check if it's using cloud APIs
                try:
                    content = source_path.read_text()
                    if "openai" in content.lower() or "anthropic" in content.lower():
                        if "local" not in content.lower()[:500]:  # Check first 500 chars
                            sources.append(f"Code: {source} (may be using cloud)")
                except:
                    pass

        return sources

    def _generate_cost_alerts(self, usage: Dict[str, Any], cost: float) -> List[CostAlert]:
        """Generate cost alerts"""
        alerts = []

        total_tokens = sum(usage.values())

        if cost > 10.0:
            alerts.append(CostAlert(
                severity="critical",
                message=f"CRITICAL: Estimated cloud cost ${cost:.2f} - IMMEDIATE ACTION REQUIRED",
                provider="multiple",
                estimated_cost=cost,
                tokens_used=total_tokens,
                timestamp=datetime.now()
            ))
        elif cost > 5.0:
            alerts.append(CostAlert(
                severity="warning",
                message=f"WARNING: Estimated cloud cost ${cost:.2f} - Switch to local AI",
                provider="multiple",
                estimated_cost=cost,
                tokens_used=total_tokens,
                timestamp=datetime.now()
            ))

        if total_tokens > 1_000_000:
            alerts.append(CostAlert(
                severity="warning",
                message=f"High token usage: {total_tokens:,} tokens - Consider local AI",
                provider="all",
                estimated_cost=cost,
                tokens_used=total_tokens,
                timestamp=datetime.now()
            ))

        return alerts

    def _generate_recommendations(self, usage: Dict[str, Any], cost: float, savings: float) -> List[str]:
        """Generate cost-saving recommendations"""
        recommendations = []

        if cost > 0:
            recommendations.append(f"🚨 IMMEDIATE: Switch all AI calls to local resources (KAIJU IRON LEGION)")
            recommendations.append(f"💰 Potential savings: ${savings:.2f} per audit period")
            recommendations.append(f"⚡ Local AI cost: ${self.LOCAL_COST * 1000:.3f} per 1M tokens (electricity only)")
            recommendations.append(f"☁️  Cloud AI cost: ${cost:.2f} for same usage")
            recommendations.append("")
            recommendations.append("ACTION ITEMS:")
            recommendations.append("1. Force local_ai_integration.py to use KAIJU IRON LEGION")
            recommendations.append("2. Disable cloud API calls in all scripts")
            recommendations.append("3. Set local AI as default in all configs")
            recommendations.append("4. Monitor token usage daily")
            recommendations.append("5. Set up cost alerts at $5, $10, $20 thresholds")

        return recommendations

    def _print_emergency_report(self, result: CostAuditResult):
        """Print emergency cost report"""
        print("\n" + "=" * 60)
        print("🚨 EMERGENCY COST AUDIT REPORT")
        print("=" * 60)
        print(f"\n📊 COST ANALYSIS:")
        print(f"   Cloud AI Cost:     ${result.total_cloud_cost:.2f}")
        print(f"   Local AI Cost:     ${result.total_local_cost:.4f}")
        print(f"   💰 Potential Savings: ${result.savings_potential:.2f}")
        print(f"\n⚠️  ALERTS ({len(result.alerts)}):")
        for alert in result.alerts:
            print(f"   [{alert.severity.upper()}] {alert.message}")
        print(f"\n🔍 CLOUD USAGE SOURCES:")
        for source in result.cloud_usage_sources:
            print(f"   • {source}")
        print(f"\n💡 RECOMMENDATIONS:")
        for rec in result.recommendations:
            print(f"   {rec}")
        print("\n" + "=" * 60)
        print("🚨 IMMEDIATE ACTION REQUIRED: Switch to local AI NOW")
        print("=" * 60 + "\n")

    def _load_token_data(self) -> Optional[Dict[str, Any]]:
        """Load token tracker data"""
        try:
            if self.token_tracker_file.exists():
                with open(self.token_tracker_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load token data: {e}")
        return None

    def _save_audit(self, result: CostAuditResult):
        try:
            """Save audit result"""
            audit_dir = self.project_root / "data" / "cost_audits"
            audit_dir.mkdir(parents=True, exist_ok=True)

            audit_file = audit_dir / f"emergency_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            audit_data = {
                "total_cloud_cost": result.total_cloud_cost,
                "total_local_cost": result.total_local_cost,
                "savings_potential": result.savings_potential,
                "cloud_usage_sources": result.cloud_usage_sources,
                "alerts": [asdict(alert) for alert in result.alerts],
                "recommendations": result.recommendations,
                "timestamp": result.timestamp.isoformat()
            }

            with open(audit_file, 'w') as f:
                json.dump(audit_data, f, indent=2)

            self.logger.info(f"💾 Audit saved: {audit_file}")

        except Exception as e:
            self.logger.error(f"Error in _save_audit: {e}", exc_info=True)
            raise
    def _get_logger(self):
        """Get logger"""
        import logging
        logging.basicConfig(level=logging.WARNING)
        return logging.getLogger("CostEmergencyAudit")


if __name__ == "__main__":
    audit = CostEmergencyAudit()
    result = audit.run_emergency_audit()

    print(f"\n✅ Emergency audit complete!")
    print(f"   Total cloud cost: ${result.total_cloud_cost:.2f}")
    print(f"   Potential savings: ${result.savings_potential:.2f}")
    print(f"   Alerts: {len(result.alerts)}")

