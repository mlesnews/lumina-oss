#!/usr/bin/env python3
"""
Master Padawan Tracker
@AGENT@MASTER.TODOLIST & @SUBAGENT@PADAWAN.LIST

Tracks and quantifies master agent todos and SubAgent padawan status.
Provides @PEAK quantification for Cursor IDE UI/UX.

Tags: #MASTER #PADAWAN #TRACKER #PEAK #QUANTIFY
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MasterPadawanTracker")


class MasterPadawanTracker:
    """
    Master Padawan Tracker

    Tracks:
    - @AGENT@MASTER.TODOLIST - Master agent todo list
    - @SUBAGENT@PADAWAN.LIST - SubAgent padawan list
    - @PEAK quantification - Metrics and visualization
    """

    def __init__(self, project_root: Path):
        """Initialize tracker"""
        self.project_root = project_root
        self.logger = logger

        # Data paths
        self.data_path = project_root / "data"
        self.master_todo_file = self.data_path / "master_todo_list.json"
        self.padawan_list_file = self.data_path / "subagent_padawan_list.json"
        self.peak_metrics_file = self.data_path / "peak_metrics.json"

        # Ensure data directory exists
        self.data_path.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.master_todos = self._load_master_todos()
        self.padawan_list = self._load_padawan_list()
        self.peak_metrics = self._load_peak_metrics()

        self.logger.info("📊 Master Padawan Tracker initialized")

    def _load_master_todos(self) -> Dict[str, Any]:
        """Load master todo list"""
        if self.master_todo_file.exists():
            try:
                with open(self.master_todo_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading master todos: {e}")

        return {
            "todos": [],
            "last_updated": datetime.now().isoformat(),
            "total": 0,
            "pending": 0,
            "in_progress": 0,
            "completed": 0
        }

    def _load_padawan_list(self) -> Dict[str, Any]:
        """Load SubAgent padawan list"""
        if self.padawan_list_file.exists():
            try:
                with open(self.padawan_list_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading padawan list: {e}")

        return {
            "padawans": [],
            "last_updated": datetime.now().isoformat(),
            "total": 0,
            "active": 0,
            "training": 0,
            "ready": 0,
            "deployed": 0
        }

    def _load_peak_metrics(self) -> Dict[str, Any]:
        """Load @PEAK metrics"""
        if self.peak_metrics_file.exists():
            try:
                with open(self.peak_metrics_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"⚠️  Error loading peak metrics: {e}")

        return {
            "metrics": {},
            "last_updated": datetime.now().isoformat(),
            "quantification": {}
        }

    def _save_master_todos(self):
        """Save master todo list"""
        try:
            with open(self.master_todo_file, 'w', encoding='utf-8') as f:
                json.dump(self.master_todos, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving master todos: {e}")

    def _save_padawan_list(self):
        """Save SubAgent padawan list"""
        try:
            with open(self.padawan_list_file, 'w', encoding='utf-8') as f:
                json.dump(self.padawan_list, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving padawan list: {e}")

    def _save_peak_metrics(self):
        """Save @PEAK metrics"""
        try:
            with open(self.peak_metrics_file, 'w', encoding='utf-8') as f:
                json.dump(self.peak_metrics, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"❌ Error saving peak metrics: {e}")

    def update_master_todos(self, todos: List[Dict[str, Any]]):
        """Update master todo list"""
        self.master_todos["todos"] = todos
        self.master_todos["last_updated"] = datetime.now().isoformat()

        # Calculate stats
        self.master_todos["total"] = len(todos)
        self.master_todos["pending"] = sum(1 for t in todos if t.get("status") == "pending")
        self.master_todos["in_progress"] = sum(1 for t in todos if t.get("status") == "in_progress")
        self.master_todos["completed"] = sum(1 for t in todos if t.get("status") == "completed")

        self._save_master_todos()
        self.logger.info(f"✅ Master todos updated: {self.master_todos['total']} total")

    def update_padawan_list(self, padawans: List[Dict[str, Any]]):
        """Update SubAgent padawan list"""
        self.padawan_list["padawans"] = padawans
        self.padawan_list["last_updated"] = datetime.now().isoformat()

        # Calculate stats
        self.padawan_list["total"] = len(padawans)
        self.padawan_list["active"] = sum(1 for p in padawans if p.get("status") == "active")
        self.padawan_list["training"] = sum(1 for p in padawans if p.get("status") == "training")
        self.padawan_list["ready"] = sum(1 for p in padawans if p.get("status") == "ready")
        self.padawan_list["deployed"] = sum(1 for p in padawans if p.get("status") == "deployed")

        self._save_padawan_list()
        self.logger.info(f"✅ Padawan list updated: {self.padawan_list['total']} total")

    def calculate_peak_metrics(self) -> Dict[str, Any]:
        """Calculate @PEAK quantification metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "master_todos": {
                "total": self.master_todos.get("total", 0),
                "pending": self.master_todos.get("pending", 0),
                "in_progress": self.master_todos.get("in_progress", 0),
                "completed": self.master_todos.get("completed", 0),
                "completion_rate": 0.0
            },
            "padawan_list": {
                "total": self.padawan_list.get("total", 0),
                "active": self.padawan_list.get("active", 0),
                "training": self.padawan_list.get("training", 0),
                "ready": self.padawan_list.get("ready", 0),
                "deployed": self.padawan_list.get("deployed", 0),
                "deployment_rate": 0.0
            },
            "quantification": {
                "master_productivity": 0.0,
                "padawan_readiness": 0.0,
                "overall_status": "unknown"
            }
        }

        # Calculate completion rate
        total_todos = metrics["master_todos"]["total"]
        if total_todos > 0:
            metrics["master_todos"]["completion_rate"] = (
                metrics["master_todos"]["completed"] / total_todos
            ) * 100

        # Calculate deployment rate
        total_padawans = metrics["padawan_list"]["total"]
        if total_padawans > 0:
            metrics["padawan_list"]["deployment_rate"] = (
                metrics["padawan_list"]["deployed"] / total_padawans
            ) * 100

        # Calculate overall metrics
        metrics["quantification"]["master_productivity"] = metrics["master_todos"]["completion_rate"]
        metrics["quantification"]["padawan_readiness"] = metrics["padawan_list"]["deployment_rate"]

        # Overall status
        if metrics["quantification"]["master_productivity"] >= 80 and metrics["quantification"]["padawan_readiness"] >= 80:
            metrics["quantification"]["overall_status"] = "excellent"
        elif metrics["quantification"]["master_productivity"] >= 60 and metrics["quantification"]["padawan_readiness"] >= 60:
            metrics["quantification"]["overall_status"] = "good"
        elif metrics["quantification"]["master_productivity"] >= 40 or metrics["quantification"]["padawan_readiness"] >= 40:
            metrics["quantification"]["overall_status"] = "fair"
        else:
            metrics["quantification"]["overall_status"] = "needs_improvement"

        # Save metrics
        self.peak_metrics = metrics
        self.peak_metrics["last_updated"] = datetime.now().isoformat()
        self._save_peak_metrics()

        return metrics

    def get_cursor_ide_dashboard(self) -> Dict[str, Any]:
        """Get dashboard data for Cursor IDE UI/UX"""
        metrics = self.calculate_peak_metrics()

        dashboard = {
            "timestamp": datetime.now().isoformat(),
            "master_todos": {
                "summary": f"{metrics['master_todos']['completed']}/{metrics['master_todos']['total']} completed",
                "progress": metrics["master_todos"]["completion_rate"],
                "status": "✅" if metrics["master_todos"]["completion_rate"] >= 80 else "⚠️" if metrics["master_todos"]["completion_rate"] >= 60 else "❌",
                "breakdown": {
                    "pending": metrics["master_todos"]["pending"],
                    "in_progress": metrics["master_todos"]["in_progress"],
                    "completed": metrics["master_todos"]["completed"]
                }
            },
            "padawan_list": {
                "summary": f"{metrics['padawan_list']['deployed']}/{metrics['padawan_list']['total']} deployed",
                "progress": metrics["padawan_list"]["deployment_rate"],
                "status": "✅" if metrics["padawan_list"]["deployment_rate"] >= 80 else "⚠️" if metrics["padawan_list"]["deployment_rate"] >= 60 else "❌",
                "breakdown": {
                    "active": metrics["padawan_list"]["active"],
                    "training": metrics["padawan_list"]["training"],
                    "ready": metrics["padawan_list"]["ready"],
                    "deployed": metrics["padawan_list"]["deployed"]
                }
            },
            "peak_quantification": {
                "master_productivity": f"{metrics['quantification']['master_productivity']:.1f}%",
                "padawan_readiness": f"{metrics['quantification']['padawan_readiness']:.1f}%",
                "overall_status": metrics["quantification"]["overall_status"]
            }
        }

        return dashboard

    def print_dashboard(self):
        """Print formatted dashboard"""
        dashboard = self.get_cursor_ide_dashboard()

        print("\n" + "=" * 80)
        print("📊 MASTER PADAWAN TRACKER - CURSOR IDE DASHBOARD")
        print("=" * 80)
        print(f"Generated: {dashboard['timestamp']}")
        print()

        # Master Todos
        print("-" * 80)
        print("🎯 @AGENT@MASTER.TODOLIST")
        print("-" * 80)
        master = dashboard["master_todos"]
        print(f"   Status: {master['status']} {master['summary']}")
        print(f"   Progress: {master['progress']:.1f}%")
        print(f"   Breakdown:")
        print(f"     - Pending: {master['breakdown']['pending']}")
        print(f"     - In Progress: {master['breakdown']['in_progress']}")
        print(f"     - Completed: {master['breakdown']['completed']}")
        print()

        # Padawan List
        print("-" * 80)
        print("🧙 @SUBAGENT@PADAWAN.LIST")
        print("-" * 80)
        padawan = dashboard["padawan_list"]
        print(f"   Status: {padawan['status']} {padawan['summary']}")
        print(f"   Progress: {padawan['progress']:.1f}%")
        print(f"   Breakdown:")
        print(f"     - Active: {padawan['breakdown']['active']}")
        print(f"     - Training: {padawan['breakdown']['training']}")
        print(f"     - Ready: {padawan['breakdown']['ready']}")
        print(f"     - Deployed: {padawan['breakdown']['deployed']}")
        print()

        # @PEAK Quantification
        print("-" * 80)
        print("📈 @PEAK QUANTIFICATION")
        print("-" * 80)
        peak = dashboard["peak_quantification"]
        print(f"   Master Productivity: {peak['master_productivity']}")
        print(f"   Padawan Readiness: {peak['padawan_readiness']}")
        print(f"   Overall Status: {peak['overall_status'].upper()}")
        print()

        print("=" * 80)
        print()


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Master Padawan Tracker")
        parser.add_argument("--dashboard", action="store_true", help="Show dashboard")
        parser.add_argument("--metrics", action="store_true", help="Show @PEAK metrics")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tracker = MasterPadawanTracker(project_root)

        if args.dashboard:
            if args.json:
                dashboard = tracker.get_cursor_ide_dashboard()
                print(json.dumps(dashboard, indent=2, default=str))
            else:
                tracker.print_dashboard()

        elif args.metrics:
            metrics = tracker.calculate_peak_metrics()
            print(json.dumps(metrics, indent=2, default=str))

        else:
            tracker.print_dashboard()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()