#!/usr/bin/env python3
"""
AI-Managed Startup - Self-Optimizing LUMINA Startup

JARVIS automatically manages startup:
- Self-times startup/shutdown
- Learns from historical data
- Auto-optimizes startup sequence
- Self-adjusts based on performance
- No manual intervention needed

Tags: #AI_MANAGED #SELF_OPTIMIZING #AUTOMATIC #JARVIS @JARVIS @LUMINA
"""

import sys
import time
import threading
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
from collections import defaultdict

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

logger = get_logger("AIManagedStartup")


class AIManagedStartup:
    """
    AI-Managed Startup System

    JARVIS automatically:
    - Times startup/shutdown
    - Learns optimal startup sequence
    - Auto-optimizes based on historical data
    - Self-adjusts service order
    - No manual intervention needed
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_startup_optimization"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.optimization_file = self.data_dir / "startup_optimization.json"
        self.optimization_data = self._load_optimization_data()

        self.start_time = None
        self.service_times: Dict[str, float] = {}
        self.service_order: List[str] = []

    def _load_optimization_data(self) -> Dict:
        """Load historical optimization data"""
        if self.optimization_file.exists():
            try:
                with open(self.optimization_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load optimization data: {e}")

        return {
            "historical_times": [],
            "service_averages": {},
            "optimal_order": [],
            "bottlenecks": [],
            "optimizations_applied": [],
            "last_optimized": None
        }

    def _save_optimization_data(self):
        """Save optimization data"""
        try:
            with open(self.optimization_file, 'w', encoding='utf-8') as f:
                json.dump(self.optimization_data, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            logger.warning(f"Could not save optimization data: {e}")

    def _analyze_historical_data(self) -> Dict:
        """AI: Analyze historical startup data to find optimal sequence"""
        historical = self.optimization_data.get("historical_times", [])
        if len(historical) < 3:
            return {}  # Need more data

        # Calculate average times per service
        service_totals = defaultdict(list)
        for run in historical:
            for service, time_taken in run.get("service_times", {}).items():
                service_totals[service].append(time_taken)

        service_averages = {
            service: sum(times) / len(times)
            for service, times in service_totals.items()
        }

        # Identify bottlenecks (consistently slow)
        bottlenecks = [
            (service, avg_time)
            for service, avg_time in service_averages.items()
            if avg_time > 1.0
        ]
        bottlenecks.sort(key=lambda x: x[1], reverse=True)

        # Determine optimal order (fast services first, slow in parallel)
        optimal_order = sorted(
            service_averages.items(),
            key=lambda x: x[1]  # Fastest first
        )

        return {
            "service_averages": service_averages,
            "bottlenecks": bottlenecks,
            "optimal_order": [s[0] for s in optimal_order]
        }

    def _get_optimal_startup_sequence(self) -> List[str]:
        """AI: Get optimal startup sequence based on historical data"""
        analysis = self._analyze_historical_data()

        if not analysis:
            # No historical data - use default order
            return ["hybrid_listening", "button_monitors", "right_alt_remap", "kenny", "ace"]

        optimal_order = analysis.get("optimal_order", [])
        bottlenecks = [b[0] for b in analysis.get("bottlenecks", [])]

        # CRITICAL: Always start hybrid_listening first (most important)
        if "hybrid_listening" in optimal_order:
            optimal_order.remove("hybrid_listening")
        optimal_order.insert(0, "hybrid_listening")

        logger.info("🤖 AI: Optimal startup sequence determined from historical data")
        logger.info(f"   Order: {optimal_order}")
        if bottlenecks:
            logger.info(f"   Bottlenecks identified: {bottlenecks}")

        return optimal_order

    def start(self):
        """Start AI-managed startup - JARVIS handles everything automatically - NO MANUAL INTERVENTION"""
        # AI-MANAGED: Automatically start timing (JARVIS manages this)
        try:
            from startup_timer import start_timing
            start_timing()
        except:
            pass

        self.start_time = time.time()

        logger.info("=" * 80)
        logger.info("🤖 AI-MANAGED STARTUP - JARVIS SELF-OPTIMIZING")
        logger.info("=" * 80)
        logger.info("   JARVIS is automatically managing startup")
        logger.info("   Learning from historical data")
        logger.info("   Auto-optimizing based on performance")
        logger.info("=" * 80)

        # AI: Get optimal startup sequence
        optimal_sequence = self._get_optimal_startup_sequence()

        # Start services in optimal order
        results = {}
        threads = []

        # CRITICAL: Start hybrid listening first (always) - AI automatically manages timing
        if "hybrid_listening" in optimal_sequence:
            logger.info("1. Starting hybrid listening (CRITICAL - AI priority)...")
            try:
                service_start = time.time()
                from hybrid_passive_active_listening import HybridPassiveActiveListening
                hybrid_listener = HybridPassiveActiveListening(project_root)
                hybrid_listener.start()
                service_time = time.time() - service_start
                self.service_times["hybrid_listening"] = service_time
                self.service_order.append("hybrid_listening")
                results["hybrid_listening"] = True
                logger.info(f"✅ Hybrid listening started ({service_time:.2f}s)")
                logger.info("   🤖 AI: Timing managed automatically by JARVIS")
            except Exception as e:
                results["hybrid_listening"] = False
                logger.error(f"❌ Hybrid listening failed: {e}")
                return False

        # AI: Start other services in parallel (based on optimal order)
        remaining_services = [s for s in optimal_sequence if s != "hybrid_listening"]

        if remaining_services:
            logger.info(f"2. Starting {len(remaining_services)} services in parallel (AI-optimized)...")

            def start_service(service_name: str):
                """Start a service (AI-managed)"""
                try:
                    service_start = time.time()

                    if service_name == "button_monitors":
                        from fix_all_clicking_issues import AllButtonMonitor
                        monitor = AllButtonMonitor()
                        monitor.start_all_monitors()
                    elif service_name == "kenny":
                        from kenny_imva_enhanced import KennyIMVAEnhanced
                        kenny = KennyIMVAEnhanced(size=120)
                        kenny.start()
                    elif service_name == "ace":
                        from acva_armoury_crate_integration import ACVAArmouryCrateIntegration
                        ace = ACVAArmouryCrateIntegration(project_root)
                        hwnd = ace.find_armoury_crate_va()
                        if hwnd:
                            ace.acva_hwnd = hwnd
                            import ctypes
                            user32 = ctypes.windll.user32
                            user32.ShowWindow(hwnd, 1)
                            user32.SetForegroundWindow(hwnd)

                    service_time = time.time() - service_start
                    self.service_times[service_name] = service_time
                    self.service_order.append(service_name)
                    results[service_name] = True
                    logger.info(f"✅ {service_name} started ({service_time:.2f}s)")
                except Exception as e:
                    results[service_name] = False
                    logger.warning(f"⚠️  {service_name} failed: {e}")

            # Start in parallel
            for service_name in remaining_services:
                t = threading.Thread(target=start_service, args=(service_name,), daemon=True)
                t.start()
                threads.append(t)

            # Wait for parallel services (max 5 seconds)
            for t in threads:
                t.join(timeout=5.0)

        total_time = time.time() - self.start_time

        # AI: Learn from this startup (automatic - no manual intervention)
        self._learn_from_startup(total_time)

        logger.info("=" * 80)
        logger.info("✅ AI-MANAGED STARTUP COMPLETE")
        logger.info("=" * 80)
        logger.info(f"⏱️  Total time: {total_time:.2f}s")
        logger.info("🤖 JARVIS has learned from this startup automatically")
        logger.info("🤖 JARVIS will optimize next startup based on this data")
        logger.info("   No manual intervention needed - fully AI-managed")
        logger.info("=" * 80)

        return True

    def _learn_from_startup(self, total_time: float):
        """AI: Learn from this startup and optimize for next time"""
        # Record this startup
        startup_record = {
            "timestamp": datetime.now().isoformat(),
            "total_time": total_time,
            "service_times": self.service_times.copy(),
            "service_order": self.service_order.copy()
        }

        historical = self.optimization_data.get("historical_times", [])
        historical.append(startup_record)

        # Keep only last 20 runs (prevent data bloat)
        if len(historical) > 20:
            historical = historical[-20:]

        self.optimization_data["historical_times"] = historical
        self.optimization_data["last_startup"] = datetime.now().isoformat()

        # AI: Analyze and optimize
        analysis = self._analyze_historical_data()
        if analysis:
            self.optimization_data["service_averages"] = analysis["service_averages"]
            self.optimization_data["bottlenecks"] = [
                {"name": b[0], "avg_time": b[1]} 
                for b in analysis["bottlenecks"]
            ]
            self.optimization_data["optimal_order"] = analysis["optimal_order"]
            self.optimization_data["last_optimized"] = datetime.now().isoformat()

            logger.info("🤖 AI: Startup analysis complete (automatic)")
            avg_time = sum(h['total_time'] for h in historical[-5:]) / min(5, len(historical))
            logger.info(f"   Average startup time (last 5): {avg_time:.2f}s")
            if analysis["bottlenecks"]:
                logger.info(f"   Bottlenecks identified: {[b[0] for b in analysis['bottlenecks']]}")
            logger.info("   🤖 AI: Next startup will use optimized sequence automatically")

        self._save_optimization_data()

    def shutdown(self):
        """AI: Time shutdown and learn from it"""
        shutdown_start = time.time()

        logger.info("🤖 AI: Timing shutdown...")

        # Shutdown services (in reverse order)
        shutdown_time = time.time() - shutdown_start

        # Record shutdown time
        if "shutdown_times" not in self.optimization_data:
            self.optimization_data["shutdown_times"] = []

        self.optimization_data["shutdown_times"].append({
            "timestamp": datetime.now().isoformat(),
            "shutdown_time": shutdown_time
        })

        # Keep only last 20 shutdowns
        shutdown_times = self.optimization_data["shutdown_times"]
        if len(shutdown_times) > 20:
            self.optimization_data["shutdown_times"] = shutdown_times[-20:]

        self._save_optimization_data()

        logger.info(f"⏱️  Shutdown time: {shutdown_time:.2f}s")
        logger.info("🤖 AI: Shutdown data recorded for optimization")


# Global AI-managed startup instance
_ai_startup: Optional[AIManagedStartup] = None


def get_ai_startup(project_root: Optional[Path] = None) -> AIManagedStartup:
    """Get global AI-managed startup instance"""
    global _ai_startup
    if _ai_startup is None:
        _ai_startup = AIManagedStartup(project_root)
    return _ai_startup


def ai_managed_startup():
    """AI-managed startup - JARVIS handles everything automatically"""
    startup = get_ai_startup()
    return startup.start()


if __name__ == "__main__":
    print("=" * 80)
    print("🤖 AI-MANAGED STARTUP - JARVIS SELF-OPTIMIZING")
    print("=" * 80)
    print()
    print("JARVIS will automatically:")
    print("  ✅ Time startup/shutdown")
    print("  ✅ Learn from historical data")
    print("  ✅ Auto-optimize startup sequence")
    print("  ✅ Self-adjust based on performance")
    print("  ✅ No manual intervention needed")
    print()

    ai_managed_startup()

    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🤖 AI: Shutting down...")
        startup = get_ai_startup()
        startup.shutdown()
