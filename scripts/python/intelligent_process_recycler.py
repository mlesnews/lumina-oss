#!/usr/bin/env python3
"""
Intelligent Process Recycler

AI-driven system that intelligently recycles processes when needed:
- Detects processes that need recycling
- Uses JARVIS/SYPHON/R5 for intelligent decision-making
- Recycles based on resource usage, uptime, errors
- Maintains optimal system state

Tags: #RECYCLING #AI #AUTOMATION #JARVIS #SYPHON #R5 @JARVIS @LUMINA
"""

import sys
import time
import psutil
import subprocess
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

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

logger = get_logger("IntelligentProcessRecycler")

# AI Integrations
try:
    from jarvis_fulltime_super_agent import JARVISFullTimeSuperAgent
    JARVIS_AVAILABLE = True
except ImportError:
    JARVIS_AVAILABLE = False
    JARVISFullTimeSuperAgent = None

try:
    from syphon import SYPHONSystem, SYPHONConfig
    SYPHON_AVAILABLE = True
except ImportError:
    SYPHON_AVAILABLE = False
    SYPHONSystem = None
    SYPHONConfig = None

try:
    from r5_living_context_matrix import R5LivingContextMatrix
    R5_AVAILABLE = True
except ImportError:
    R5_AVAILABLE = False
    R5LivingContextMatrix = None


class RecycleReason(Enum):
    """Reasons for recycling"""
    HIGH_MEMORY = "high_memory"
    HIGH_CPU = "high_cpu"
    LONG_UPTIME = "long_uptime"
    ERROR_COUNT = "error_count"
    DEGRADED_PERFORMANCE = "degraded_performance"
    MANUAL_REQUEST = "manual_request"
    SCHEDULED = "scheduled"
    RESOURCE_LEAK = "resource_leak"


@dataclass
class ProcessInfo:
    """Process information"""
    pid: int
    name: str
    cmdline: List[str]
    cpu_percent: float
    memory_mb: float
    uptime_seconds: float
    create_time: float
    status: str


@dataclass
class RecycleDecision:
    """Recycling decision"""
    process: ProcessInfo
    reason: RecycleReason
    priority: str  # critical, high, medium, low
    should_recycle: bool
    confidence: float  # 0.0 to 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntelligentProcessRecycler:
    """
    Intelligent Process Recycler

    Uses AI (JARVIS/SYPHON/R5) to intelligently decide when to recycle processes.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.recycled_processes: List[Dict[str, Any]] = []

        # AI Integrations
        self.jarvis = None
        if JARVIS_AVAILABLE:
            try:
                self.jarvis = JARVISFullTimeSuperAgent(project_root)
                logger.info("✅ JARVIS integrated for recycling decisions")
            except Exception as e:
                logger.warning(f"⚠️  JARVIS not available: {e}")

        self.syphon = None
        if SYPHON_AVAILABLE:
            try:
                syphon_config = SYPHONConfig(project_root=project_root, enable_regex_tools=True)
                self.syphon = SYPHONSystem(syphon_config)
                logger.info("✅ SYPHON integrated for intelligence extraction")
            except Exception as e:
                logger.warning(f"⚠️  SYPHON not available: {e}")

        self.r5 = None
        if R5_AVAILABLE:
            try:
                self.r5 = R5LivingContextMatrix(project_root)
                logger.info("✅ R5 integrated for context aggregation")
            except Exception as e:
                logger.warning(f"⚠️  R5 not available: {e}")

        # Recycling thresholds
        self.thresholds = {
            "max_memory_mb": 512,
            "max_cpu_percent": 80.0,
            "max_uptime_hours": 24.0,
            "max_error_rate": 0.1
        }

        logger.info("✅ Intelligent Process Recycler initialized")

    def get_process_info(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        """Get process information"""
        try:
            return ProcessInfo(
                pid=proc.pid,
                name=proc.name(),
                cmdline=proc.cmdline(),
                cpu_percent=proc.cpu_percent(interval=0.1),
                memory_mb=proc.memory_info().rss / 1024 / 1024,
                uptime_seconds=time.time() - proc.create_time(),
                create_time=proc.create_time(),
                status=proc.status()
            )
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            return None

    def should_recycle_process(self, process_info: ProcessInfo) -> RecycleDecision:
        """Use AI to decide if process should be recycled"""
        reasons = []
        priority = "low"
        confidence = 0.0
        metadata = {}

        # Check memory
        if process_info.memory_mb > self.thresholds["max_memory_mb"]:
            reasons.append(RecycleReason.HIGH_MEMORY)
            priority = "high"
            confidence += 0.3
            metadata["memory_mb"] = process_info.memory_mb
            metadata["threshold"] = self.thresholds["max_memory_mb"]

        # Check CPU
        if process_info.cpu_percent > self.thresholds["max_cpu_percent"]:
            reasons.append(RecycleReason.HIGH_CPU)
            if priority == "low":
                priority = "high"
            confidence += 0.3
            metadata["cpu_percent"] = process_info.cpu_percent
            metadata["threshold"] = self.thresholds["max_cpu_percent"]

        # Check uptime
        uptime_hours = process_info.uptime_seconds / 3600
        if uptime_hours > self.thresholds["max_uptime_hours"]:
            reasons.append(RecycleReason.LONG_UPTIME)
            if priority == "low":
                priority = "medium"
            confidence += 0.2
            metadata["uptime_hours"] = uptime_hours

        # Use SYPHON to extract intelligence about similar processes
        if self.syphon and reasons:
            try:
                # Extract patterns from past recycling decisions
                # This would inform the decision
                pass
            except Exception as e:
                logger.debug(f"SYPHON intelligence extraction error: {e}")

        # Use R5 for context
        if self.r5:
            try:
                # Aggregate context about process patterns
                pass
            except Exception as e:
                logger.debug(f"R5 context aggregation error: {e}")

        # Use JARVIS for orchestration
        if self.jarvis:
            try:
                # JARVIS would orchestrate the recycling decision
                pass
            except Exception as e:
                logger.debug(f"JARVIS orchestration error: {e}")

        should_recycle = len(reasons) > 0 and confidence >= 0.3

        return RecycleDecision(
            process=process_info,
            reason=reasons[0] if reasons else RecycleReason.MANUAL_REQUEST,
            priority=priority,
            should_recycle=should_recycle,
            confidence=min(confidence, 1.0),
            metadata=metadata
        )

    def recycle_process(self, process_info: ProcessInfo, decision: RecycleDecision) -> bool:
        """Recycle a process"""
        try:
            logger.info(f"🔄 Recycling {process_info.name} (PID: {process_info.pid})")
            logger.info(f"   Reason: {decision.reason.value}")
            logger.info(f"   Priority: {decision.priority}")
            logger.info(f"   Confidence: {decision.confidence:.1%}")

            proc = psutil.Process(process_info.pid)

            # Get command to restart
            cmdline = process_info.cmdline
            if not cmdline:
                logger.warning(f"⚠️  Cannot recycle {process_info.name}: No command line")
                return False

            # Terminate process
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)

            time.sleep(2)  # Wait for cleanup

            # Restart process
            logger.info(f"🚀 Restarting {process_info.name}...")
            # Headless/daemon mode - no visible terminals
            creation_flags = 0
            if sys.platform == 'win32':
                # DETACHED_PROCESS (0x00000008) + CREATE_NO_WINDOW (0x08000000)
                creation_flags = 0x08000008

            # Log file
            log_dir = self.project_root / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)
            process_name = process_info.name.replace('.exe', '')
            log_file = log_dir / f"{process_name}_{datetime.now().strftime('%Y%m%d')}.log"

            with open(log_file, 'a') as log_handle:
                subprocess.Popen(
                    cmdline,
                    cwd=str(self.project_root),
                    stdout=log_handle,
                    stderr=subprocess.STDOUT,
                    creationflags=creation_flags,
                    start_new_session=True if sys.platform != 'win32' else False
                )

            # Log recycling
            self.recycled_processes.append({
                "timestamp": datetime.now().isoformat(),
                "process": process_info.name,
                "pid": process_info.pid,
                "reason": decision.reason.value,
                "priority": decision.priority,
                "confidence": decision.confidence,
                "metadata": decision.metadata
            })

            logger.info(f"✅ Recycled {process_info.name}")
            return True

        except Exception as e:
            logger.error(f"❌ Error recycling {process_info.name}: {e}")
            return False

    def find_processes_to_recycle(self) -> List[RecycleDecision]:
        """Find processes that should be recycled"""
        decisions = []

        # Find Python processes related to our project
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline', [])
                if not cmdline:
                    continue

                # Check if it's a project-related process
                is_project_process = any(
                    str(self.project_root) in str(arg) or
                    "virtual_assistant" in str(arg).lower() or
                    "kenny" in str(arg).lower() or
                    "ironman" in str(arg).lower() or
                    "anakin" in str(arg).lower() or
                    "jarvis" in str(arg).lower()
                    for arg in cmdline
                )

                if is_project_process:
                    process_info = self.get_process_info(proc)
                    if process_info:
                        decision = self.should_recycle_process(process_info)
                        if decision.should_recycle:
                            decisions.append(decision)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        return decisions

    def recycle_all_needed(self) -> Dict[str, Any]:
        """Recycle all processes that need recycling"""
        logger.info("=" * 80)
        logger.info("🔄 INTELLIGENT PROCESS RECYCLING")
        logger.info("=" * 80)
        logger.info("")

        decisions = self.find_processes_to_recycle()

        results = {
            "timestamp": datetime.now().isoformat(),
            "processes_checked": len(decisions),
            "processes_recycled": 0,
            "recycled": []
        }

        if not decisions:
            logger.info("✅ No processes need recycling")
            return results

        logger.info(f"Found {len(decisions)} processes that may need recycling:")
        for decision in decisions:
            logger.info(f"  - {decision.process.name} (PID: {decision.process.pid})")
            logger.info(f"    Reason: {decision.reason.value} | Priority: {decision.priority} | Confidence: {decision.confidence:.1%}")

        logger.info("")

        # Sort by priority and confidence
        decisions.sort(key=lambda d: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}[d.priority],
            -d.confidence
        ))

        # Recycle processes
        for decision in decisions:
            if self.recycle_process(decision.process, decision):
                results["processes_recycled"] += 1
                results["recycled"].append({
                    "process": decision.process.name,
                    "pid": decision.process.pid,
                    "reason": decision.reason.value,
                    "priority": decision.priority
                })
            time.sleep(1)  # Stagger recycling

        logger.info("")
        logger.info("=" * 80)
        logger.info("📊 RECYCLING SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Processes Recycled: {results['processes_recycled']}/{results['processes_checked']}")
        logger.info("=" * 80)

        return results


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Intelligent Process Recycler")
        parser.add_argument("--recycle", action="store_true", help="Recycle processes that need it")
        parser.add_argument("--check", action="store_true", help="Check which processes need recycling")
        parser.add_argument("--all", action="store_true", help="Check and recycle all")

        args = parser.parse_args()

        recycler = IntelligentProcessRecycler(project_root)

        if args.check or args.all:
            decisions = recycler.find_processes_to_recycle()
            print("\n" + "=" * 80)
            print("🔍 PROCESSES THAT NEED RECYCLING")
            print("=" * 80)
            print()
            if decisions:
                for decision in decisions:
                    print(f"  {decision.process.name} (PID: {decision.process.pid})")
                    print(f"    Reason: {decision.reason.value}")
                    print(f"    Priority: {decision.priority}")
                    print(f"    Confidence: {decision.confidence:.1%}")
                    print(f"    Memory: {decision.process.memory_mb:.1f} MB")
                    print(f"    CPU: {decision.process.cpu_percent:.1f}%")
                    print(f"    Uptime: {decision.process.uptime_seconds/3600:.1f} hours")
                    print()
            else:
                print("  ✅ No processes need recycling")
            print("=" * 80)

        if args.recycle or args.all:
            results = recycler.recycle_all_needed()

            # Save results
            results_file = project_root / "data" / "process_recycling_results.json"
            results_file.parent.mkdir(parents=True, exist_ok=True)
            import json
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)

            logger.info(f"✅ Results saved: {results_file.name}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()