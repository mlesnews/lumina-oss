#!/usr/bin/env python3
"""
ElevenLabs Quota Monitor

Monitors ElevenLabs API quota usage and provides recommendations.

Tags: #ELEVENLABS #QUOTA #MONITORING #COST_MANAGEMENT
"""

import sys
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ElevenLabsQuota")

# Try to import ElevenLabs TTS for API key
try:
    from elevenlabs_tts_integration import ElevenLabsTTS
    ELEVENLABS_TTS_AVAILABLE = True
except ImportError:
    ELEVENLABS_TTS_AVAILABLE = False
    ElevenLabsTTS = None


class ElevenLabsQuotaMonitor:
    """
    Monitor ElevenLabs API quota usage

    Provides quota status, recommendations, and usage tracking.
    """

    def __init__(self, api_key: Optional[str] = None):
        """Initialize quota monitor"""
        self.logger = logger

        # Get API key
        if api_key:
            self.api_key = api_key
        elif ELEVENLABS_TTS_AVAILABLE and ElevenLabsTTS:
            try:
                tts = ElevenLabsTTS()
                self.api_key = tts.api_key
            except:
                self.api_key = None
        else:
            self.api_key = None

        if not self.api_key:
            self.logger.warning("⚠️  ElevenLabs API key not available")

        self.api_url = "https://api.elevenlabs.io/v1"

        self.logger.info("📊 ElevenLabs Quota Monitor initialized")

    def check_quota(self) -> Dict[str, Any]:
        """
        Check current quota status from ElevenLabs API

        Returns:
            Dict with quota information
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "API key not available",
                "remaining": 0,
                "used": 0,
                "limit": 0
            }

        try:
            # Query user info (includes subscription/usage info)
            response = requests.get(
                f"{self.api_url}/user",
                headers={"xi-api-key": self.api_key},
                timeout=10
            )

            if response.status_code == 200:
                user_data = response.json()

                # Extract subscription info
                subscription = user_data.get("subscription", {})
                subscription_tier = subscription.get("tier", "unknown")
                character_limit = subscription.get("character_limit", 0)
                character_count = subscription.get("character_count", 0)

                # Calculate remaining
                remaining = max(0, character_limit - character_count)
                used = character_count
                limit = character_limit

                # Calculate percentage
                usage_percent = (used / limit * 100) if limit > 0 else 0

                # Determine status
                if remaining < limit * 0.1:  # Less than 10% remaining
                    status = "critical"
                elif remaining < limit * 0.25:  # Less than 25% remaining
                    status = "low"
                elif remaining < limit * 0.5:  # Less than 50% remaining
                    status = "moderate"
                else:
                    status = "healthy"

                quota_info = {
                    "success": True,
                    "remaining": remaining,
                    "used": used,
                    "limit": limit,
                    "usage_percent": round(usage_percent, 2),
                    "status": status,
                    "tier": subscription_tier,
                    "reset_date": self._estimate_reset_date(),
                    "days_until_reset": self._days_until_reset()
                }

                self.logger.info(f"📊 Quota Status: {status.upper()}")
                self.logger.info(f"   Remaining: {remaining:,} / {limit:,} ({100-usage_percent:.1f}%)")
                self.logger.info(f"   Used: {used:,} / {limit:,} ({usage_percent:.1f}%)")
                self.logger.info(f"   Tier: {subscription_tier}")

                return quota_info
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
                error = error_data.get("detail", {}).get("message", response.text) if error_data else response.text

                return {
                    "success": False,
                    "error": error,
                    "status_code": response.status_code,
                    "remaining": 0,
                    "used": 0,
                    "limit": 0
                }

        except Exception as e:
            self.logger.error(f"❌ Error checking quota: {e}")
            return {
                "success": False,
                "error": str(e),
                "remaining": 0,
                "used": 0,
                "limit": 0
            }

    def _estimate_reset_date(self) -> str:
        """Estimate quota reset date (typically monthly)"""
        # ElevenLabs resets monthly, typically on subscription anniversary
        # For now, estimate end of current month
        now = datetime.now()
        if now.month == 12:
            reset = datetime(now.year + 1, 1, 1)
        else:
            reset = datetime(now.year, now.month + 1, 1)

        return reset.isoformat()

    def _days_until_reset(self) -> int:
        """Days until quota resets"""
        reset_date = datetime.fromisoformat(self._estimate_reset_date())
        now = datetime.now()
        delta = reset_date - now
        return max(0, delta.days)

    def estimate_credits(self, text: str) -> int:
        """
        Estimate credits needed for text

        Rough estimate: ~1 credit per 2-3 characters
        """
        # Conservative estimate: 1 credit per 2 characters
        return max(1, len(text) // 2)

    def can_generate(self, estimated_credits: int) -> bool:
        """
        Check if we have enough credits for generation

        Args:
            estimated_credits: Estimated credits needed

        Returns:
            True if enough credits available
        """
        quota = self.check_quota()

        if not quota.get("success"):
            self.logger.warning("⚠️  Could not check quota, assuming insufficient")
            return False

        remaining = quota.get("remaining", 0)
        can_generate = remaining >= estimated_credits

        if not can_generate:
            self.logger.warning(f"⚠️  Insufficient quota: {remaining} remaining, {estimated_credits} required")

        return can_generate

    def get_recommendations(self) -> Dict[str, Any]:
        """
        Get recommendations based on current quota status

        Returns:
            Dict with recommendations
        """
        quota = self.check_quota()

        if not quota.get("success"):
            return {
                "recommendations": [
                    "Unable to check quota - verify API key",
                    "Consider implementing quota monitoring"
                ],
                "priority": "unknown"
            }

        remaining = quota.get("remaining", 0)
        limit = quota.get("limit", 0)
        status = quota.get("status", "unknown")
        usage_percent = quota.get("usage_percent", 0)

        recommendations = []
        priority = "low"

        if status == "critical":
            priority = "critical"
            recommendations.extend([
                "🚨 CRITICAL: Quota nearly exhausted",
                "⏸️  Pause audio generation until quota resets",
                "📝 Use text transcripts instead of audio",
                "💾 Implement usage caching to reduce API calls",
                f"📅 Quota resets in {quota.get('days_until_reset', 0)} days"
            ])
        elif status == "low":
            priority = "high"
            recommendations.extend([
                "⚠️  Quota is low (< 25% remaining)",
                "💾 Implement usage caching immediately",
                "🎯 Use selective audio generation (key segments only)",
                "📊 Monitor usage closely",
                f"📅 Quota resets in {quota.get('days_until_reset', 0)} days"
            ])
        elif status == "moderate":
            priority = "medium"
            recommendations.extend([
                "📊 Quota is moderate (25-50% remaining)",
                "💾 Consider implementing usage caching",
                "🎯 Optimize text length before generation",
                "📈 Plan usage for remainder of month"
            ])
        else:
            priority = "low"
            recommendations.extend([
                "✅ Quota is healthy (> 50% remaining)",
                "💾 Consider implementing caching for efficiency",
                "📊 Monitor usage patterns",
                "🎯 Continue normal operations"
            ])

        # Add general recommendations
        recommendations.extend([
            "",
            "💡 General Recommendations:",
            "  1. Implement usage caching (50-80% reduction)",
            "  2. Use selective generation (key segments only)",
            "  3. Optimize text length before TTS",
            "  4. Consider hybrid TTS (ElevenLabs + local)",
            "  5. Monitor quota regularly"
        ])

        return {
            "recommendations": recommendations,
            "priority": priority,
            "quota_status": status,
            "remaining": remaining,
            "limit": limit,
            "usage_percent": usage_percent
        }

    def format_quota_report(self) -> str:
        """Format quota status as report"""
        quota = self.check_quota()
        recommendations = self.get_recommendations()

        report = []
        report.append("=" * 60)
        report.append("📊 ElevenLabs Quota Status Report")
        report.append("=" * 60)
        report.append("")

        if quota.get("success"):
            report.append(f"Status: {quota.get('status', 'unknown').upper()}")
            report.append(f"Tier: {quota.get('tier', 'unknown')}")
            report.append("")
            report.append(f"Remaining: {quota.get('remaining', 0):,} / {quota.get('limit', 0):,}")
            report.append(f"Used: {quota.get('used', 0):,} / {quota.get('limit', 0):,}")
            report.append(f"Usage: {quota.get('usage_percent', 0):.1f}%")
            report.append("")
            report.append(f"Reset Date: {quota.get('reset_date', 'unknown')}")
            report.append(f"Days Until Reset: {quota.get('days_until_reset', 0)}")
        else:
            report.append(f"❌ Error: {quota.get('error', 'Unknown error')}")

        report.append("")
        report.append("=" * 60)
        report.append("💡 Recommendations")
        report.append("=" * 60)
        report.append("")

        for rec in recommendations.get("recommendations", []):
            report.append(rec)

        report.append("")
        report.append("=" * 60)

        return "\n".join(report)


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="ElevenLabs Quota Monitor")
        parser.add_argument("--check", action="store_true", help="Check quota status")
        parser.add_argument("--report", action="store_true", help="Generate quota report")
        parser.add_argument("--recommendations", action="store_true", help="Show recommendations")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        monitor = ElevenLabsQuotaMonitor()

        if args.recommendations:
            recs = monitor.get_recommendations()
            if args.json:
                print(json.dumps(recs, indent=2, default=str))
            else:
                for rec in recs.get("recommendations", []):
                    print(rec)

        elif args.report:
            report = monitor.format_quota_report()
            print(report)

        elif args.check:
            quota = monitor.check_quota()
            if args.json:
                print(json.dumps(quota, indent=2, default=str))
            else:
                if quota.get("success"):
                    print(f"✅ Quota Status: {quota.get('status', 'unknown').upper()}")
                    print(f"   Remaining: {quota.get('remaining', 0):,} / {quota.get('limit', 0):,}")
                    print(f"   Used: {quota.get('used', 0):,} ({quota.get('usage_percent', 0):.1f}%)")
                    print(f"   Tier: {quota.get('tier', 'unknown')}")
                    print(f"   Reset: {quota.get('days_until_reset', 0)} days")
                else:
                    print(f"❌ Error: {quota.get('error', 'Unknown error')}")

        else:
            # Default: show report
            report = monitor.format_quota_report()
            print(report)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()