#!/usr/bin/env python3
"""
@SCOTTY's Dynamic Taskbar System
Tracks application usage and dynamically adjusts taskbar based on popularity

Tags: #SCOTTY #TASKBAR #DYNAMIC #USAGE_TRACKING @SCOTTY @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from collections import defaultdict
from typing import Dict, List, Tuple

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SCOTTYDynamicTaskbar")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SCOTTYDynamicTaskbar")


class DynamicTaskbarManager:
    """Manages dynamic taskbar based on application usage"""

    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.usage_file = self.project_root / "data" / "scotty_taskbar_usage.json"
        self.config_file = self.project_root / "data" / "scotty_taskbar_config.json"
        self.usage_file.parent.mkdir(parents=True, exist_ok=True)

        # Load usage data
        self.usage_data = self._load_usage_data()
        self.config = self._load_config()

    def _load_usage_data(self) -> Dict:
        """Load application usage tracking data"""
        if self.usage_file.exists():
            try:
                with open(self.usage_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load usage data: {e}")

        return {
            "applications": {},
            "last_updated": datetime.now().isoformat()
        }

    def _load_config(self) -> Dict:
        """Load taskbar configuration"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load config: {e}")

        return {
            "max_taskbar_items": 10,
            "min_usage_days": 7,
            "update_frequency_hours": 24,
            "pinned_apps": []
        }

    def _save_usage_data(self):
        """Save usage tracking data"""
        self.usage_data["last_updated"] = datetime.now().isoformat()
        try:
            with open(self.usage_file, 'w', encoding='utf-8') as f:
                json.dump(self.usage_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save usage data: {e}")

    def track_application_launch(self, app_name: str, app_path: str):
        """Track when an application is launched"""
        now = datetime.now()
        today = now.date().isoformat()

        if "applications" not in self.usage_data:
            self.usage_data["applications"] = {}

        if app_name not in self.usage_data["applications"]:
            self.usage_data["applications"][app_name] = {
                "path": app_path,
                "launches": {},
                "total_launches": 0,
                "first_seen": today,
                "last_seen": today
            }

        app_data = self.usage_data["applications"][app_name]
        app_data["last_seen"] = today
        app_data["total_launches"] = app_data.get("total_launches", 0) + 1

        if today not in app_data["launches"]:
            app_data["launches"][today] = 0
        app_data["launches"][today] += 1

        self._save_usage_data()
        logger.debug(f"Tracked launch: {app_name}")

    def get_top_applications(self, limit: int = 10, days: int = 7) -> List[Tuple[str, Dict]]:
        """Get top applications by usage in the last N days"""
        cutoff_date = (datetime.now() - timedelta(days=days)).date()

        app_scores = []

        for app_name, app_data in self.usage_data.get("applications", {}).items():
            # Calculate recent usage
            recent_launches = 0
            for date_str, count in app_data.get("launches", {}).items():
                try:
                    date = datetime.fromisoformat(date_str).date()
                    if date >= cutoff_date:
                        recent_launches += count
                except:
                    pass

            # Score = recent launches + (total launches / 100) for historical weight
            score = recent_launches + (app_data.get("total_launches", 0) / 100)

            app_scores.append((app_name, {
                "score": score,
                "recent_launches": recent_launches,
                "total_launches": app_data.get("total_launches", 0),
                "path": app_data.get("path", ""),
                "last_seen": app_data.get("last_seen", "")
            }))

        # Sort by score (descending)
        app_scores.sort(key=lambda x: x[1]["score"], reverse=True)

        return app_scores[:limit]

    def update_taskbar_recommendations(self) -> List[str]:
        """Get recommended applications for taskbar"""
        top_apps = self.get_top_applications(
            limit=self.config.get("max_taskbar_items", 10),
            days=self.config.get("min_usage_days", 7)
        )

        recommendations = [app_name for app_name, _ in top_apps]

        logger.info(f"Top {len(recommendations)} applications for taskbar:")
        for i, (app_name, data) in enumerate(top_apps, 1):
            logger.info(f"  {i}. {app_name} (score: {data['score']:.2f}, launches: {data['recent_launches']})")

        return recommendations

    def save_config(self):
        """Save configuration"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="@SCOTTY's Dynamic Taskbar Manager")
    parser.add_argument("--track", type=str, help="Track application launch (app_name:app_path)")
    parser.add_argument("--top", type=int, default=10, help="Show top N applications")
    parser.add_argument("--days", type=int, default=7, help="Look back N days")
    parser.add_argument("--recommend", action="store_true", help="Get taskbar recommendations")

    args = parser.parse_args()

    manager = DynamicTaskbarManager()

    if args.track:
        app_name, app_path = args.track.split(":", 1)
        manager.track_application_launch(app_name, app_path)
        print(f"✅ Tracked: {app_name}")
    elif args.recommend:
        recommendations = manager.update_taskbar_recommendations()
        print(f"\n📋 Recommended taskbar applications:")
        for i, app in enumerate(recommendations, 1):
            print(f"  {i}. {app}")
    else:
        top_apps = manager.get_top_applications(limit=args.top, days=args.days)
        print(f"\n🏆 Top {len(top_apps)} applications (last {args.days} days):")
        for i, (app_name, data) in enumerate(top_apps, 1):
            print(f"  {i}. {app_name}")
            print(f"     Score: {data['score']:.2f}, Recent: {data['recent_launches']}, Total: {data['total_launches']}")


if __name__ == "__main__":


    main()