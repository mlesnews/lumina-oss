#!/usr/bin/env python3
"""
Cloud Usage Alert System

Detects and alerts when cloud AI providers are being used instead of
local-first AI (ULTRON, KAIJU, R5). Integrates with LUMINA notification system.

Tags: #ALERTS #CLOUD_DETECTION #LOCAL_FIRST @JARVIS @LUMINA
"""

import sys
import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

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

logger = get_logger("CloudUsageAlertSystem")


class CloudUsageAlertSystem:
    """Alert system for cloud AI usage"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.alerts_file = project_root / "data" / "cloud_usage_alerts.json"
        self.alerts_file.parent.mkdir(parents=True, exist_ok=True)

        # Cloud detection patterns
        self.cloud_patterns = {
            "openai": ["gpt-", "openai", "o1-", "api.openai.com"],
            "anthropic": ["claude", "anthropic", "api.anthropic.com"],
            "other": ["api.", "cloud", ".com/api"]
        }

        # Load existing alerts
        self.alerts = self._load_alerts()

        logger.info("✅ Cloud Usage Alert System initialized")

    def _load_alerts(self) -> List[Dict[str, Any]]:
        """Load existing alerts"""
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return []

    def _save_alerts(self):
        """Save alerts to file"""
        try:
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving alerts: {e}")

    def detect_cloud_usage(self, model_name: str, source: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Detect if cloud provider is being used

        Args:
            model_name: Name of AI model being used
            source: Source of the request (cursor, vscode, etc.)

        Returns:
            Alert dict if cloud detected, None otherwise
        """
        model_lower = model_name.lower()

        for provider, patterns in self.cloud_patterns.items():
            for pattern in patterns:
                if pattern in model_lower:
                    # Cloud provider detected!
                    alert = {
                        "timestamp": datetime.now().isoformat(),
                        "provider": provider,
                        "model": model_name,
                        "source": source,
                        "severity": "high",
                        "message": f"⚠️  Cloud provider detected: {provider} ({model_name})",
                        "recommendation": f"Use local-first AI instead: ULTRON (qwen2.5:72b) or KAIJU (llama3.2:3b)",
                        "local_alternatives": [
                            {"provider": "ULTRON", "model": "qwen2.5:72b", "endpoint": "http://localhost:11434"},
                            {"provider": "KAIJU", "model": "llama3.2:3b", "endpoint": "http://<NAS_IP>:11434"}  # KAIJU Number Eight (Desktop PC)
                        ],
                        "acknowledged": False
                    }

                    # Add to alerts
                    self.alerts.append(alert)

                    # Keep only last 100 alerts
                    if len(self.alerts) > 100:
                        self.alerts = self.alerts[-100:]

                    self._save_alerts()

                    logger.warning(f"🚨 {alert['message']}")
                    logger.info(f"   Recommendation: {alert['recommendation']}")

                    return alert

        return None

    def check_cursor_settings(self) -> List[Dict[str, Any]]:
        """Check Cursor settings for cloud usage"""
        alerts = []
        cursor_settings = self.project_root / ".cursor" / "settings.json"

        if not cursor_settings.exists():
            return alerts

        try:
            with open(cursor_settings, 'r') as f:
                config = json.load(f)

            # Check default models
            default_models = [
                config.get("cursor.chat.defaultModel", ""),
                config.get("cursor.composer.defaultModel", ""),
                config.get("cursor.inlineCompletion.defaultModel", "")
            ]

            for model in default_models:
                if model:
                    alert = self.detect_cloud_usage(model, "cursor_settings")
                    if alert:
                        alerts.append(alert)

            # Check custom models
            custom_models = config.get("cursor.chat.customModels", [])
            for model_config in custom_models:
                model_name = model_config.get("model", "")
                if model_name:
                    alert = self.detect_cloud_usage(model_name, "cursor_custom_models")
                    if alert:
                        alerts.append(alert)

        except Exception as e:
            logger.error(f"Error checking Cursor settings: {e}")

        return alerts

    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get recent alerts"""
        cutoff = datetime.now() - timedelta(hours=hours)

        recent = []
        for alert in self.alerts:
            alert_time = datetime.fromisoformat(alert["timestamp"])
            if alert_time >= cutoff:
                recent.append(alert)

        return recent

    def get_summary(self) -> Dict[str, Any]:
        """Get alert summary"""
        recent_24h = self.get_recent_alerts(24)
        recent_7d = self.get_recent_alerts(168)

        by_provider = {}
        for alert in recent_24h:
            provider = alert["provider"]
            by_provider[provider] = by_provider.get(provider, 0) + 1

        return {
            "total_alerts": len(self.alerts),
            "recent_24h": len(recent_24h),
            "recent_7d": len(recent_7d),
            "by_provider": by_provider,
            "local_first_enforced": True,
            "recommendation": "Use ULTRON/KAIJU/R5 instead of cloud providers"
        }


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Cloud Usage Alert System")
    parser.add_argument("--check-cursor", action="store_true", help="Check Cursor settings")
    parser.add_argument("--summary", action="store_true", help="Show alert summary")
    parser.add_argument("--recent", type=int, default=24, help="Show recent alerts (hours)")

    args = parser.parse_args()

    system = CloudUsageAlertSystem(project_root)

    if args.check_cursor:
        print("Checking Cursor settings for cloud usage...")
        alerts = system.check_cursor_settings()
        if alerts:
            print(f"⚠️  Found {len(alerts)} cloud usage alerts:")
            for alert in alerts:
                print(f"   - {alert['message']}")
                print(f"     Recommendation: {alert['recommendation']}")
        else:
            print("✅ No cloud usage detected in Cursor settings")

    if args.summary:
        summary = system.get_summary()
        print("=" * 80)
        print("📊 CLOUD USAGE ALERT SUMMARY")
        print("=" * 80)
        print(f"Total Alerts: {summary['total_alerts']}")
        print(f"Recent (24h): {summary['recent_24h']}")
        print(f"Recent (7d): {summary['recent_7d']}")
        if summary['by_provider']:
            print("\nBy Provider:")
            for provider, count in summary['by_provider'].items():
                print(f"   - {provider}: {count}")
        print(f"\nRecommendation: {summary['recommendation']}")
        print()

    if args.recent:
        recent = system.get_recent_alerts(args.recent)
        if recent:
            print(f"Recent Alerts (last {args.recent}h):")
            for alert in recent[-10:]:  # Show last 10
                print(f"   [{alert['timestamp']}] {alert['message']}")
                print(f"      Source: {alert['source']}")
                print(f"      Recommendation: {alert['recommendation']}")
        else:
            print(f"✅ No alerts in last {args.recent} hours")


if __name__ == "__main__":


    main()