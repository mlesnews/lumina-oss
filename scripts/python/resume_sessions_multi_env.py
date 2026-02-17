#!/usr/bin/env python3
"""
Resume Sessions Across All Environments
Processes incomplete agent chat sessions across all workspace environments with memory monitoring
"""

import sys
import json
import time
import psutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from collections import deque

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResumeSessionsMultiEnv")

class DynamicLoadBalancer:
    """Dynamic CPU and Memory load balancer with spike prediction"""

    def __init__(self, target_cpu: float = 60.0, max_cpu: float = 75.0, 
                 target_memory: float = 70.0, max_memory: float = 85.0):
        self.target_cpu = target_cpu
        self.max_cpu = max_cpu
        self.target_memory = target_memory
        self.max_memory = max_memory
        self.cpu_history = deque(maxlen=30)
        self.memory_history = deque(maxlen=30)
        self.batch_size_history = deque(maxlen=10)
        self.current_batch_size = 5
        self.min_batch_size = 2
        self.max_batch_size = 15

    def get_cpu_load(self) -> float:
        """Get current CPU load"""
        cpu = psutil.cpu_percent(interval=0.1)
        self.cpu_history.append(cpu)
        return cpu

    def get_memory_load(self) -> float:
        """Get current memory load"""
        memory = psutil.virtual_memory().percent
        self.memory_history.append(memory)
        return memory

    def get_resource_state(self) -> Dict[str, float]:
        """Get current resource state"""
        return {
            "cpu": self.get_cpu_load(),
            "memory": self.get_memory_load()
        }

    def predict_spike(self) -> bool:
        """Predict if a CPU spike is likely based on trend"""
        if len(self.cpu_history) < 5:
            return False
        recent = list(self.cpu_history)[-5:]
        trend = (recent[-1] - recent[0]) / len(recent)
        if trend > 2.0 and recent[-1] > self.target_cpu:
            return True
        return False

    def calculate_batch_size(self) -> int:
        """Dynamically calculate optimal batch size based on CPU and Memory load"""
        cpu = self.get_cpu_load()
        memory = self.get_memory_load()
        worst_load = max(cpu, memory)
        worst_target = max(self.target_cpu, self.target_memory)
        worst_max = max(self.max_cpu, self.max_memory)

        if worst_load > worst_max:
            new_size = max(self.min_batch_size, int(self.current_batch_size * 0.4))
        elif worst_load > worst_target * 1.2:
            new_size = max(self.min_batch_size, int(self.current_batch_size * 0.7))
        elif worst_load < worst_target * 0.8:
            new_size = min(self.max_batch_size, int(self.current_batch_size * 1.15))
        else:
            new_size = self.current_batch_size

        if memory > self.target_memory:
            new_size = max(self.min_batch_size, int(new_size * 0.8))

        self.current_batch_size = int((self.current_batch_size * 0.7) + (new_size * 0.3))
        self.current_batch_size = max(self.min_batch_size, min(self.max_batch_size, self.current_batch_size))
        self.batch_size_history.append(self.current_batch_size)
        return self.current_batch_size

    def calculate_delay(self, slow_mode: bool = False) -> float:
        """Calculate delay between batches based on CPU and Memory load"""
        cpu = self.get_cpu_load()
        memory = self.get_memory_load()
        base_delay = 5.0 if slow_mode else 2.0
        worst_load = max(cpu, memory)
        worst_max = max(self.max_cpu, self.max_memory)
        worst_target = max(self.target_cpu, self.target_memory)

        if worst_load > worst_max:
            return base_delay * 3.0
        elif worst_load > worst_target:
            return base_delay * 2.0
        elif worst_load < worst_target * 0.7:
            return base_delay * 0.5
        else:
            return base_delay

    def should_pause(self) -> bool:
        """Check if should pause before next batch"""
        cpu = self.get_cpu_load()
        memory = self.get_memory_load()
        if cpu > self.max_cpu or memory > self.max_memory:
            return True
        if self.predict_spike():
            return True
        return False

class MultiEnvironmentSessionResumer:
    """Resume sessions across all workspace environments"""

    def __init__(self, projects_root: Optional[Path] = None):
        # Default to Dropbox my_projects directory
        if projects_root is None:
            projects_root = Path.home() / "Dropbox" / "my_projects"

        self.projects_root = projects_root
        self.environments = self._discover_environments()

        # Centralized resumed sessions tracking (use .lumina as primary)
        self.lumina_root = self.projects_root / ".lumina"
        self.resumed_dir = self.lumina_root / "data" / "resumed_sessions"
        self.resumed_dir.mkdir(parents=True, exist_ok=True)

        # Load balancer
        self.load_balancer = DynamicLoadBalancer(target_cpu=60.0, max_cpu=75.0, 
                                                  target_memory=70.0, max_memory=85.0)

        # Get already resumed session IDs from all environments
        self.resumed_ids = self._load_resumed_ids_all_envs()

    def _discover_environments(self) -> Dict[str, Path]:
        try:
            """Discover all workspace environments"""
            environments = {}

            if not self.projects_root.exists():
                logger.warning(f"Projects root not found: {self.projects_root}")
                return environments

            # Look for common environment patterns
            env_patterns = [
                ".lumina",
                "<COMPANY>-financial-services_llc-env",
                "<COMPANY>-financial-services_llc-env_portable",
                "<COMPANY_ID>-env",
                "*lumina*",
                "*<COMPANY>*",
                "*cfs*"
            ]

            for item in self.projects_root.iterdir():
                if item.is_dir():
                    # Check if it has a data/r5_living_matrix/sessions directory
                    sessions_dir = item / "data" / "r5_living_matrix" / "sessions"
                    if sessions_dir.exists():
                        env_name = item.name
                        environments[env_name] = item
                        logger.info(f"   ✅ Found environment: {env_name}")

            logger.info(f"Discovered {len(environments)} environments with session directories")
            return environments

        except Exception as e:
            self.logger.error(f"Error in _discover_environments: {e}", exc_info=True)
            raise
    def _load_resumed_ids_all_envs(self) -> Set[str]:
        """Load set of already-resumed session IDs from all environments"""
        resumed_ids = set()

        # Check centralized resumed directory (in .lumina)
        if self.resumed_dir.exists():
            for resumed_file in self.resumed_dir.glob("resumed_*.json"):
                try:
                    with open(resumed_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        session_id = data.get("session_id") or resumed_file.stem.replace("resumed_", "")
                        resumed_ids.add(session_id)
                except:
                    pass

        # Also check each environment's local resumed directory (if exists)
        for env_name, env_path in self.environments.items():
            env_resumed_dir = env_path / "data" / "resumed_sessions"
            if env_resumed_dir.exists():
                for resumed_file in env_resumed_dir.glob("resumed_*.json"):
                    try:
                        with open(resumed_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            session_id = data.get("session_id") or resumed_file.stem.replace("resumed_", "")
                            resumed_ids.add(session_id)
                    except:
                        pass

        logger.info(f"Loaded {len(resumed_ids)} already-resumed session IDs from all environments")
        return resumed_ids

    def find_incomplete_sessions_all_envs(self, recent_only: bool = False, 
                                          limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """Find incomplete sessions across all environments"""
        logger.info("🔍 Finding incomplete sessions across all environments...")
        all_incomplete = []

        for env_name, env_path in self.environments.items():
            sessions_dir = env_path / "data" / "r5_living_matrix" / "sessions"

            if not sessions_dir.exists():
                continue

            logger.info(f"   Scanning {env_name}...")
            session_files = list(sessions_dir.glob("*.json"))

            if recent_only and limit:
                session_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                session_files = session_files[:limit]
            else:
                session_files.sort(key=lambda p: p.stat().st_mtime)  # Oldest first

            env_incomplete = 0

            for session_file in session_files:
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    session_id = data.get("session_id", session_file.stem)

                    # Skip if already resumed
                    if session_id in self.resumed_ids:
                        continue

                    messages = data.get("messages", [])

                    # Check if incomplete (few messages)
                    if len(messages) < 3:
                        timestamp = datetime.fromtimestamp(session_file.stat().st_mtime)

                        all_incomplete.append({
                            "file": session_file,
                            "session_id": session_id,
                            "messages": len(messages),
                            "timestamp": timestamp,
                            "data": data,
                            "environment": env_name,
                            "env_path": env_path
                        })
                        env_incomplete += 1
                except Exception as e:
                    logger.debug(f"Error reading {session_file.name}: {e}")
                    continue

            logger.info(f"      Found {env_incomplete} incomplete sessions in {env_name}")

        # Sort by timestamp (oldest first)
        all_incomplete.sort(key=lambda s: s["timestamp"])

        logger.info(f"Found {len(all_incomplete)} total incomplete sessions across all environments")
        return all_incomplete

    def resume_session(self, session: Dict[str, Any]) -> bool:
        """Resume a single session (save to centralized location)"""
        try:
            session_id = session["session_id"]
            environment = session["environment"]
            data = session["data"].copy()

            # Mark as resumed
            data["resumed"] = True
            data["resume_timestamp"] = datetime.now().isoformat()
            data["resume_method"] = "multi_env_dynamic_scaling"
            data["original_environment"] = environment

            # Save to centralized resumed directory
            output_file = self.resumed_dir / f"resumed_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            # Add to resumed set
            self.resumed_ids.add(session_id)

            logger.info(f"✅ Resumed: {session_id} (from {environment})")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to resume {session['session_id']}: {e}")
            return False

    def process_batch(self, batch: List[Dict[str, Any]]) -> Dict[str, int]:
        """Process a batch of sessions"""
        results = {"success": 0, "failed": 0}

        for session in batch:
            if self.resume_session(session):
                results["success"] += 1
            else:
                results["failed"] += 1
            time.sleep(0.5)

        return results

    def resume_all_envs(self, max_sessions: Optional[int] = None,
                       recent_only: bool = False, slow_mode: bool = False,
                       continuous: bool = False) -> Dict[str, Any]:
        """Resume all sessions across all environments"""
        logger.info("=" * 60)
        logger.info("🚀 RESUMING SESSIONS (Multi-Environment + Memory Monitoring)")
        logger.info("=" * 60)
        logger.info(f"Environments: {', '.join(self.environments.keys())}")
        if slow_mode:
            logger.info("🐢 Slow mode: Processing over time in background")
        if continuous:
            logger.info("♻️  Continuous mode: Will process until complete")
        logger.info("")

        total_resumed_all_runs = 0
        total_failed_all_runs = 0
        run_number = 0

        while True:
            run_number += 1

            # Find incomplete sessions across all environments
            incomplete = self.find_incomplete_sessions_all_envs(
                recent_only=recent_only,
                limit=max_sessions * 2 if max_sessions else None
            )

            if not incomplete:
                logger.info("✅ No incomplete sessions found in any environment")
                break

            # Limit to requested number per run
            if max_sessions:
                incomplete = incomplete[:max_sessions]

            logger.info(f"Run #{run_number}: Processing {len(incomplete)} sessions")
            logger.info(f"Processing {len(incomplete)} sessions with dynamic batching")
            logger.info("")

            total_resumed = 0
            total_failed = 0
            batch_num = 0

            i = 0
            while i < len(incomplete):
                batch_size = self.load_balancer.calculate_batch_size()
                resources = self.load_balancer.get_resource_state()

                if self.load_balancer.should_pause():
                    logger.warning(f"⚠️  High resource usage (CPU: {resources['cpu']:.1f}%, Memory: {resources['memory']:.1f}%) - pausing 10s")
                    time.sleep(10.0)
                    continue

                batch = incomplete[i:i+batch_size]
                batch_num += 1

                # Show environment breakdown for batch
                env_counts = {}
                for s in batch:
                    env = s["environment"]
                    env_counts[env] = env_counts.get(env, 0) + 1
                env_str = ", ".join([f"{env}:{count}" for env, count in env_counts.items()])

                logger.info(f"📦 Batch {batch_num}: Processing {len(batch)} sessions (CPU: {resources['cpu']:.1f}%, Memory: {resources['memory']:.1f}%, Batch: {batch_size})")
                logger.info(f"   Environments: {env_str}")

                results = self.process_batch(batch)
                total_resumed += results["success"]
                total_failed += results["failed"]

                i += len(batch)

                progress = (i / len(incomplete)) * 100
                logger.info(f"   ✅ Batch complete: {results['success']} resumed, {results['failed']} failed")
                logger.info(f"   📊 Overall progress: {i}/{len(incomplete)} ({progress:.1f}%)")

                if i < len(incomplete):
                    delay = self.load_balancer.calculate_delay(slow_mode=slow_mode)
                    logger.info(f"   ⏳ Waiting {delay:.1f}s before next batch...")
                    time.sleep(delay)

                logger.info("")

            total_resumed_all_runs += total_resumed
            total_failed_all_runs += total_failed

            logger.info("=" * 60)
            logger.info(f"✅ Run #{run_number} COMPLETE: Resumed {total_resumed}, Failed {total_failed}")
            logger.info("=" * 60)

            final_resources = self.load_balancer.get_resource_state()
            logger.info(f"📊 Final CPU: {final_resources['cpu']:.1f}%")
            logger.info(f"📊 Final Memory: {final_resources['memory']:.1f}%")

            if continuous:
                remaining = self.find_incomplete_sessions_all_envs(recent_only=recent_only)
                if remaining:
                    logger.info("")
                    logger.info(f"🔄 Continuous mode: {len(remaining)} sessions remaining, waiting 30s...")
                    time.sleep(30.0)
                    continue

            break

        logger.info("")
        logger.info("=" * 60)
        logger.info(f"✅ ALL RUNS COMPLETE")
        logger.info("=" * 60)
        logger.info(f"Total resumed across all runs: {total_resumed_all_runs}")
        logger.info(f"Total failed across all runs: {total_failed_all_runs}")
        logger.info("=" * 60)

        return {
            "status": "complete",
            "total_runs": run_number,
            "total_resumed": total_resumed_all_runs,
            "total_failed": total_failed_all_runs,
            "environments": list(self.environments.keys())
        }

def main():
    try:
        import argparse

        parser = argparse.ArgumentParser(description="Resume sessions across all environments")
        parser.add_argument("--max-sessions", type=int, default=None, help="Max sessions per run")
        parser.add_argument("--target-cpu", type=float, default=60.0, help="Target CPU percent")
        parser.add_argument("--max-cpu", type=float, default=75.0, help="Max CPU percent")
        parser.add_argument("--target-memory", type=float, default=70.0, help="Target Memory percent")
        parser.add_argument("--max-memory", type=float, default=85.0, help="Max Memory percent")
        parser.add_argument("--recent-only", action="store_true", help="Only process recent sessions")
        parser.add_argument("--slow-mode", action="store_true", help="Slow mode: longer delays")
        parser.add_argument("--continuous", action="store_true", help="Continuous mode: run until complete")
        parser.add_argument("--projects-root", type=str, help="Root directory for all projects")

        args = parser.parse_args()

        projects_root = Path(args.projects_root) if args.projects_root else None

        resumer = MultiEnvironmentSessionResumer(projects_root=projects_root)
        resumer.load_balancer.target_cpu = args.target_cpu
        resumer.load_balancer.max_cpu = args.max_cpu
        resumer.load_balancer.target_memory = args.target_memory
        resumer.load_balancer.max_memory = args.max_memory

        initial_resources = resumer.load_balancer.get_resource_state()
        logger.info(f"📊 Initial CPU: {initial_resources['cpu']:.1f}%")
        logger.info(f"📊 Initial Memory: {initial_resources['memory']:.1f}%")
        logger.info("")

        result = resumer.resume_all_envs(
            max_sessions=args.max_sessions,
            recent_only=args.recent_only,
            slow_mode=args.slow_mode,
            continuous=args.continuous
        )

        return result

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    sys.exit(0 if result.get("status") == "complete" else 1)



    result = main()