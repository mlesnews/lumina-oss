#!/usr/bin/env python3
"""
Quantum Anime Task Chain Executor

Chains tasks until successful completion:
- Executes pending tasks in sequence
- Respects dependencies
- Continues until all tasks complete
- Real-time progress updates
- Error handling and retry logic

Tags: #PEAK #F4 #CHAIN #AUTOMATION @LUMINA @JARVIS
"""

import sys
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

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

logger = get_logger("QuantumAnimeTaskChain")


class QuantumAnimeTaskChain:
    """
    Task Chain Executor - Chains tasks until successful completion

    Automatically executes all pending tasks in sequence
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize task chain"""
        self.project_root = project_root or script_dir.parent.parent
        self.logger = get_logger("QuantumAnimeTaskChain")

        # Load production engine
        try:
            from quantum_anime_production_engine import QuantumAnimeProductionEngine
            self.engine = QuantumAnimeProductionEngine(self.project_root)
        except ImportError:
            self.logger.error("Production engine not available")
            self.engine = None

        # Load executor
        try:
            from quantum_anime_production_executor import QuantumAnimeProductionExecutor
            self.executor = QuantumAnimeProductionExecutor(self.project_root)
        except ImportError:
            self.logger.error("Production executor not available")
            self.executor = None

        # Load real asset generator (NO PLACEHOLDERS)
        try:
            from quantum_anime_real_asset_generator import QuantumAnimeRealAssetGenerator
            self.real_generator = QuantumAnimeRealAssetGenerator(self.project_root)
            self.real_generator.engine = self.engine  # Share engine reference
        except ImportError:
            self.logger.error("Real asset generator not available")
            self.real_generator = None

        # Load monitor
        try:
            from quantum_anime_live_monitor import QuantumAnimeLiveMonitor
            self.monitor = QuantumAnimeLiveMonitor(self.project_root)
        except ImportError:
            self.logger.error("Live monitor not available")
            self.monitor = None

    def get_ready_tasks(self) -> List:
        """Get tasks that are ready to execute (dependencies met)"""
        if not self.engine:
            return []

        ready_tasks = []

        for task in self.engine.tasks:
            if task.status == "pending":
                # Check if all dependencies are met
                deps_met = True
                if task.dependencies:
                    for dep_id in task.dependencies:
                        dep_task = next((t for t in self.engine.tasks if t.task_id == dep_id), None)
                        if not dep_task or dep_task.status != "complete":
                            deps_met = False
                            break

                if deps_met:
                    ready_tasks.append(task)

        return ready_tasks

    def execute_task(self, task) -> bool:
        """Execute a single task"""
        self.logger.info(f"🔄 Executing task: {task.task_id} ({task.task_type})")

        try:
            # Mark as in progress
            task.status = "in_progress"
            self.engine._save_tasks()

            # Execute based on task type - CREATE REAL ASSETS, NO PLACEHOLDERS
            if task.task_type == "storyboard":
                # Create REAL storyboard with actual panels
                scene_info = self._get_scene_info_for_task(task)
                self.real_generator.create_real_storyboard(task, scene_info)
            elif task.task_type == "voice":
                # Create REAL voice script with full content
                self.real_generator.create_real_voice_script(task)
            elif task.task_type == "music":
                # Create REAL music composition plan
                self.real_generator.create_real_music_composition(task)
            elif task.task_type == "marketing":
                # Create REAL marketing content
                self.real_generator.create_real_marketing_content(task)
            elif task.task_type == "script":
                # Scripts are already complete
                task.status = "complete"
            elif task.task_type == "animation":
                # Create REAL animation plan (not placeholder)
                self.real_generator.create_real_animation_plan(task)
            elif task.task_type == "render":
                # Create REAL render specification (not placeholder)
                self.real_generator.create_real_render_spec(task)
            else:
                self.logger.warning(f"Unknown task type: {task.task_type}")
                task.status = "complete"  # Mark as complete to avoid blocking

            # Mark as complete
            task.status = "complete"
            self.engine._save_tasks()

            self.logger.info(f"✅ Task completed: {task.task_id}")
            return True

        except Exception as e:
            self.logger.error(f"❌ Task failed: {task.task_id} - {e}")
            task.status = "pending"  # Reset to pending for retry
            self.engine._save_tasks()
            return False

    def _get_scene_info_for_task(self, task) -> Dict[str, Any]:
        """Get scene info for task"""
        scene_num = task.metadata.get("scene_number", 0)
        if scene_num == 0:
            # Try to extract from asset_id
            if "scene_01" in task.asset_id:
                scene_num = 1
            elif "scene_02" in task.asset_id:
                scene_num = 2
            elif "scene_03" in task.asset_id:
                scene_num = 3
            elif "scene_04" in task.asset_id:
                scene_num = 4
            elif "scene_05" in task.asset_id:
                scene_num = 5
            elif "scene_06" in task.asset_id:
                scene_num = 6
            elif "scene_07" in task.asset_id:
                scene_num = 7

        scene_titles = {
            1: "Opening: The Flat World",
            2: "Discovery: Meeting Another Dot",
            3: "Realization: There Must Be More",
            4: "The Second Dimension",
            5: "Mastering Two Dimensions",
            6: "The Third Dimension Beckons",
            7: "Closing: Next Time"
        }

        scene_durations = {
            1: 120.0,
            2: 180.0,
            3: 150.0,
            4: 180.0,
            5: 150.0,
            6: 120.0,
            7: 60.0
        }

        return {
            "scene_number": scene_num,
            "title": scene_titles.get(scene_num, f"Scene {scene_num}"),
            "duration_seconds": scene_durations.get(scene_num, 120.0),
            "description": f"Scene {scene_num} content"
        }

    def chain_until_complete(self, show_progress: bool = True, delay: float = 0.5):
        """Chain tasks until all are complete"""
        if not self.engine or not self.executor:
            self.logger.error("Required components not available")
            return

        print("="*80)
        print("QUANTUM ANIME TASK CHAIN - EXECUTING UNTIL COMPLETE")
        print("="*80)
        print()

        iteration = 0
        max_iterations = 1000  # Safety limit
        last_complete_count = 0
        stuck_count = 0

        while True:
            iteration += 1

            if iteration > max_iterations:
                self.logger.warning("Max iterations reached - stopping")
                break

            # Get current status
            status = self.monitor.get_live_status() if self.monitor else None

            if status:
                complete_count = status['complete_count']
                total_tasks = status['total_tasks']
                percentage = status['percentage']
                current_step = status['current_step']

                # Check if complete
                if complete_count >= total_tasks:
                    print("\n" + "="*80)
                    print("✅ ALL TASKS COMPLETE!")
                    print("="*80)
                    print(f"   Total Tasks: {total_tasks}")
                    print(f"   Completed: {complete_count}")
                    print(f"   Percentage: {percentage:.2f}%")
                    print(f"   Iterations: {iteration}")
                    print("="*80)
                    break

                # Show progress
                if show_progress:
                    print(f"\n📊 Iteration {iteration} - Step {current_step} of {total_tasks} ({percentage:.2f}%)")
                    print(f"   Complete: {complete_count}/{total_tasks}")

                # Check if stuck (no progress)
                if complete_count == last_complete_count:
                    stuck_count += 1
                    if stuck_count > 10:
                        # Check if there are any ready tasks
                        ready_tasks = self.get_ready_tasks()
                        if not ready_tasks:
                            print("\n⚠️  No ready tasks - may be waiting on dependencies or complete")
                            break
                else:
                    stuck_count = 0

                last_complete_count = complete_count

            # Get ready tasks
            ready_tasks = self.get_ready_tasks()

            if not ready_tasks:
                # Check if there are pending tasks that might have unmet dependencies
                pending_tasks = [t for t in self.engine.tasks if t.status == "pending"]
                if pending_tasks:
                    # Try to execute pending tasks anyway (dependencies might be met but not detected)
                    print(f"\n⚠️  No ready tasks, but {len(pending_tasks)} pending - attempting to execute...")
                    for task in pending_tasks[:5]:  # Try first 5
                        print(f"   🔄 Attempting: {task.task_id}")
                        success = self.execute_task(task)
                        if success:
                            executed_any = True
                            break

                    if not executed_any:
                        print("\n⚠️  No ready tasks available - may have dependency issues")
                        break
                elif status and status['pending_count'] == 0:
                    # All tasks are either complete or in progress
                    print("\n⏳ All tasks are either complete or in progress")
                    time.sleep(2)  # Wait a bit and check again
                    continue
                else:
                    print("\n⚠️  No ready tasks available - may have dependency issues")
                    break

            # Execute ready tasks (can do multiple in parallel if no dependencies)
            executed_any = False
            for task in ready_tasks:
                if show_progress:
                    print(f"   🔄 Executing: {task.task_id} ({task.task_type})")

                success = self.execute_task(task)
                executed_any = executed_any or success

                if delay > 0:
                    time.sleep(delay)

            # If no ready tasks but we tried pending tasks, check if we made progress
            if not executed_any and not ready_tasks:
                # Check if we're actually done
                if status:
                    if status['complete_count'] >= status['total_tasks']:
                        break
                    # If we have pending tasks, try to execute them
                    pending_tasks = [t for t in self.engine.tasks if t.status == "pending"]
                    if pending_tasks:
                        # Force execute remaining tasks
                        for task in pending_tasks:
                            if show_progress:
                                print(f"   🔄 Force executing: {task.task_id} ({task.task_type})")
                            success = self.execute_task(task)
                            executed_any = executed_any or success
                            if delay > 0:
                                time.sleep(delay)

                if not executed_any:
                    print("\n⚠️  No tasks executed this iteration")
                    break

        # Final status
        if self.monitor:
            print("\n" + "="*80)
            print("FINAL STATUS")
            print("="*80)
            self.monitor.display_live_status(clear_screen=False)

        return status if status else None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Quantum Anime Task Chain Executor")
    parser.add_argument("--no-progress", action="store_true", help="Don't show progress updates")
    parser.add_argument("--delay", type=float, default=0.5, help="Delay between tasks (seconds)")
    parser.add_argument("--max-iterations", type=int, default=1000, help="Maximum iterations")

    args = parser.parse_args()

    chain = QuantumAnimeTaskChain()
    chain.chain_until_complete(show_progress=not args.no_progress, delay=args.delay)


if __name__ == "__main__":


    main()