#!/usr/bin/env python3
"""
Quantum Anime Live Production Monitor

Real-time monitoring with:
- Current step (e.g., "1 of 49")
- Progressive count
- Working percentage
- Live updates

Tags: #PEAK #F4 #MONITOR #LIVE @LUMINA @JARVIS
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("QuantumAnimeLiveMonitor")


class QuantumAnimeLiveMonitor:
    """
    Live Production Monitor

    Real-time progress tracking with step numbers and percentages
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize live monitor"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnimeLiveMonitor")

        # Production directories
        self.production_dir = self.project_root / "data" / "quantum_anime" / "production"
        self.status_file = self.production_dir / "production_status.json"
        self.tasks_file = self.production_dir / "production_tasks.json"

        # Load production engine
        try:
            from quantum_anime_production_engine import QuantumAnimeProductionEngine
            self.engine = QuantumAnimeProductionEngine(self.project_root)
        except ImportError:
            self.logger.error("Production engine not available")
            self.engine = None

    def get_live_status(self) -> Dict[str, Any]:
        """Get live production status with step numbers"""
        if not self.engine:
            return {"error": "Production engine not available"}

        # Get all tasks
        all_tasks = self.engine.tasks
        total_tasks = len(all_tasks)

        # Calculate progress
        complete_tasks = [t for t in all_tasks if t.status == "complete"]
        in_progress_tasks = [t for t in all_tasks if t.status == "in_progress"]
        pending_tasks = [t for t in all_tasks if t.status == "pending"]

        complete_count = len(complete_tasks)
        in_progress_count = len(in_progress_tasks)
        pending_count = len(pending_tasks)

        # Calculate percentage
        percentage = (complete_count / total_tasks * 100) if total_tasks > 0 else 0.0

        # Get current step (next step to work on)
        # Step number is 1-indexed: show as completed + 1 (progressive count)
        # This shows "working on step X of 49" where X is the next step
        current_step = complete_count + 1  # Next step after completed (progressive count)

        # Note: If there's an in-progress task, it's being worked on, but we show the step number
        # as the next step in sequence (complete_count + 1) for steady progressive count

        # Get current task info
        current_task = None
        if in_progress_tasks:
            current_task = in_progress_tasks[0]
        elif pending_tasks:
            current_task = pending_tasks[0]

        # Group by type for detailed breakdown
        by_type = defaultdict(lambda: {"total": 0, "complete": 0, "in_progress": 0, "pending": 0})
        for task in all_tasks:
            by_type[task.task_type]["total"] += 1
            by_type[task.task_type][task.status] += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_tasks": total_tasks,
            "current_step": current_step,
            "current_step_display": f"{current_step} of {total_tasks}",
            "complete_count": complete_count,
            "in_progress_count": in_progress_count,
            "pending_count": pending_count,
            "percentage": round(percentage, 2),
            "percentage_display": f"{percentage:.2f}%",
            "current_task": {
                "task_id": current_task.task_id if current_task else None,
                "task_type": current_task.task_type if current_task else None,
                "asset_id": current_task.asset_id if current_task else None,
                "status": current_task.status if current_task else None
            } if current_task else None,
            "breakdown_by_type": {
                task_type: {
                    "total": counts["total"],
                    "complete": counts["complete"],
                    "in_progress": counts["in_progress"],
                    "pending": counts["pending"],
                    "percentage": round((counts["complete"] / counts["total"] * 100) if counts["total"] > 0 else 0, 2)
                }
                for task_type, counts in by_type.items()
            },
            "recent_completed": [
                {
                    "task_id": t.task_id,
                    "task_type": t.task_type,
                    "asset_id": t.asset_id
                }
                for t in complete_tasks[-5:]  # Last 5 completed
            ]
        }

    def display_live_status(self, clear_screen: bool = True):
        """Display live status with step counter"""
        status = self.get_live_status()

        if clear_screen:
            # Clear screen (works on most terminals)
            print("\033[2J\033[H", end="")

        print("="*80)
        print("QUANTUM ANIME PRODUCTION - LIVE MONITOR")
        print("="*80)
        print(f"Last Updated: {status['timestamp']}")
        print()

        # Main progress bar
        print("📊 PRODUCTION PROGRESS")
        print(f"   Step: {status['current_step_display']}")
        print(f"   Percentage: {status['percentage_display']}")
        print()

        # Progress bar visualization
        bar_width = 50
        filled = int(status['percentage'] / 100 * bar_width)
        bar = "█" * filled + "░" * (bar_width - filled)
        print(f"   [{bar}] {status['percentage_display']}")
        print()

        # Task counts
        print("📋 TASK STATUS")
        print(f"   ✅ Complete: {status['complete_count']}")
        print(f"   🔄 In Progress: {status['in_progress_count']}")
        print(f"   ⏳ Pending: {status['pending_count']}")
        print(f"   📊 Total: {status['total_tasks']}")
        print()

        # Current task
        if status['current_task']:
            print("🎯 CURRENT TASK")
            task = status['current_task']
            print(f"   Task ID: {task['task_id']}")
            print(f"   Type: {task['task_type'].upper()}")
            print(f"   Asset: {task['asset_id']}")
            print(f"   Status: {task['status'].upper()}")
            print()

        # Breakdown by type
        print("📦 BREAKDOWN BY TYPE")
        for task_type, counts in sorted(status['breakdown_by_type'].items()):
            status_icon = "✅" if counts['percentage'] == 100 else "🔄" if counts['in_progress'] > 0 else "⏳"
            print(f"   {status_icon} {task_type.upper()}: {counts['complete']}/{counts['total']} ({counts['percentage']:.1f}%)")
        print()

        # Recent completed
        if status['recent_completed']:
            print("✅ RECENTLY COMPLETED")
            for task in status['recent_completed']:
                print(f"   • {task['task_type'].upper()}: {task['asset_id']}")
            print()

        print("="*80)

    def monitor_live(self, interval: float = 2.0, max_updates: Optional[int] = None):
        """Monitor production with live updates"""
        print("🚀 Starting Live Monitor...")
        print("Press Ctrl+C to stop")
        print()

        update_count = 0
        try:
            while True:
                if max_updates and update_count >= max_updates:
                    break

                self.display_live_status()

                # Wait before next update
                time.sleep(interval)
                update_count += 1

        except KeyboardInterrupt:
            print("\n\n⏹️  Monitor stopped by user")
        except Exception as e:
            print(f"\n\n❌ Error: {e}")

    def get_status_json(self) -> str:
        try:
            """Get status as JSON string"""
            status = self.get_live_status()
            return json.dumps(status, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in get_status_json: {e}", exc_info=True)
            raise
    def export_status(self, output_path: Optional[Path] = None) -> Path:
        try:
            """Export current status to file"""
            if not output_path:
                output_path = self.production_dir / "live_status.json"

            status = self.get_live_status()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Status exported: {output_path}")
            return output_path


        except Exception as e:
            self.logger.error(f"Error in export_status: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Quantum Anime Live Monitor")
        parser.add_argument("--live", action="store_true", help="Live monitoring mode")
        parser.add_argument("--interval", type=float, default=2.0, help="Update interval in seconds")
        parser.add_argument("--once", action="store_true", help="Display once and exit")
        parser.add_argument("--json", action="store_true", help="Output as JSON")
        parser.add_argument("--export", type=str, help="Export status to file")

        args = parser.parse_args()

        monitor = QuantumAnimeLiveMonitor()

        if args.json:
            print(monitor.get_status_json())
        elif args.export:
            output_path = Path(args.export)
            monitor.export_status(output_path)
            print(f"✅ Status exported to: {output_path}")
        elif args.live:
            monitor.monitor_live(interval=args.interval)
        elif args.once:
            monitor.display_live_status(clear_screen=False)
        else:
            # Default: display once
            monitor.display_live_status(clear_screen=False)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()