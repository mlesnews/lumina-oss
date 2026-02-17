#!/usr/bin/env python3
"""
JARVIS @ASK Live Progressive Monitor

Live monitoring of batch processing with:
- Current batch number
- Processing rate metrics (slow, max, optimal, partial, degraded, stutter)
- ETA for current file and entire batch
- Hawking tracing and tracking
- Template processes, policies, procedures

Tags: #LIVE_MONITORING #BATCH_TRACKING #RATE_ANALYSIS #HAWKING_TRACING #TEMPLATE_SYSTEM @JARVIS @LUMINA
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import deque
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISAskLiveMonitor")


class RateAnalyzer:
    """Analyze processing rates"""

    RATE_THRESHOLDS = {
        "MAX": 100,      # Max rate (asks per minute)
        "OPTIMAL": 50,  # Optimal rate
        "PARTIAL": 25,  # Partial rate
        "DEGRADED": 10, # Degraded rate
        "SLOW": 5,      # Slow rate
        "STUTTER": 1    # Stutter rate (very slow)
    }

    def __init__(self):
        self.processing_times = deque(maxlen=100)  # Last 100 processing times
        self.ask_counts = deque(maxlen=100)  # Last 100 ask counts

    def add_processing_time(self, time_taken: float, asks_processed: int):
        """Add processing time and ask count"""
        self.processing_times.append(time_taken)
        self.ask_counts.append(asks_processed)

    def calculate_rate(self) -> Dict[str, Any]:
        """Calculate current processing rate"""
        if not self.processing_times:
            return {
                "rate": 0,
                "status": "UNKNOWN",
                "asks_per_minute": 0
            }

        # Calculate average time per ask
        total_time = sum(self.processing_times)
        total_asks = sum(self.ask_counts)

        if total_time == 0 or total_asks == 0:
            return {
                "rate": 0,
                "status": "UNKNOWN",
                "asks_per_minute": 0
            }

        avg_time_per_ask = total_time / total_asks
        asks_per_minute = 60 / avg_time_per_ask if avg_time_per_ask > 0 else 0

        # Determine rate status
        status = "STUTTER"
        if asks_per_minute >= self.RATE_THRESHOLDS["MAX"]:
            status = "MAX"
        elif asks_per_minute >= self.RATE_THRESHOLDS["OPTIMAL"]:
            status = "OPTIMAL"
        elif asks_per_minute >= self.RATE_THRESHOLDS["PARTIAL"]:
            status = "PARTIAL"
        elif asks_per_minute >= self.RATE_THRESHOLDS["DEGRADED"]:
            status = "DEGRADED"
        elif asks_per_minute >= self.RATE_THRESHOLDS["SLOW"]:
            status = "SLOW"

        return {
            "rate": asks_per_minute,
            "status": status,
            "asks_per_minute": asks_per_minute,
            "avg_time_per_ask": avg_time_per_ask,
            "thresholds": self.RATE_THRESHOLDS
        }


class ETACalculator:
    """Calculate estimated time to completion"""

    def __init__(self):
        self.start_time = None
        self.total_asks = 0
        self.processed_asks = 0
        self.rate_analyzer = RateAnalyzer()

    def initialize(self, total_asks: int):
        """Initialize ETA calculator"""
        self.start_time = datetime.now()
        self.total_asks = total_asks
        self.processed_asks = 0

    def update(self, processed: int, time_taken: float):
        """Update progress"""
        self.processed_asks = processed
        self.rate_analyzer.add_processing_time(time_taken, processed)

    def calculate_eta(self) -> Dict[str, Any]:
        """Calculate ETA for current file and entire batch"""
        if self.total_asks == 0 or self.processed_asks == 0:
            return {
                "current_file_eta": "UNKNOWN",
                "batch_eta": "UNKNOWN",
                "completion_percentage": 0,
                "elapsed_time": "0:00:00",
                "estimated_remaining": "UNKNOWN"
            }

        rate_info = self.rate_analyzer.calculate_rate()
        asks_per_minute = rate_info["asks_per_minute"]

        if asks_per_minute == 0:
            return {
                "current_file_eta": "UNKNOWN",
                "batch_eta": "UNKNOWN",
                "completion_percentage": (self.processed_asks / self.total_asks) * 100,
                "elapsed_time": str(datetime.now() - self.start_time) if self.start_time else "0:00:00",
                "estimated_remaining": "UNKNOWN"
            }

        # Calculate remaining asks
        remaining_asks = self.total_asks - self.processed_asks

        # Calculate ETA
        minutes_remaining = remaining_asks / asks_per_minute
        eta_datetime = datetime.now() + timedelta(minutes=minutes_remaining)

        # Elapsed time
        elapsed = datetime.now() - self.start_time if self.start_time else timedelta(0)

        return {
            "current_file_eta": f"{minutes_remaining / remaining_asks * 100:.2f} seconds" if remaining_asks > 0 else "COMPLETE",
            "batch_eta": eta_datetime.strftime("%Y-%m-%d %H:%M:%S"),
            "completion_percentage": (self.processed_asks / self.total_asks) * 100,
            "elapsed_time": str(elapsed).split('.')[0],
            "estimated_remaining": f"{int(minutes_remaining)} minutes" if minutes_remaining >= 1 else f"{int(minutes_remaining * 60)} seconds",
            "asks_per_minute": asks_per_minute,
            "rate_status": rate_info["status"]
        }


class HawkingTracer:
    """Hawking-level tracing and tracking"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "hawking_tracing"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.trace_data = {
            "timestamp": datetime.now().isoformat(),
            "traces": [],
            "metrics": {},
            "events": []
        }

    def trace(self, event: str, data: Dict[str, Any]):
        """Trace an event"""
        trace_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event,
            "data": data
        }
        self.trace_data["traces"].append(trace_entry)
        self.trace_data["events"].append(event)

    def save_trace(self):
        try:
            """Save trace data"""
            trace_file = self.data_dir / f"hawking_trace_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(trace_file, 'w', encoding='utf-8') as f:
                json.dump(self.trace_data, f, indent=2, default=str)
            return trace_file


        except Exception as e:
            self.logger.error(f"Error in save_trace: {e}", exc_info=True)
            raise
class LiveMonitor:
    """Live progressive monitoring system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_live_monitoring"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.rate_analyzer = RateAnalyzer()
        self.eta_calculator = ETACalculator()
        self.hawking_tracer = HawkingTracer(project_root)

        self.monitoring = False
        self.monitor_thread = None

    def start_monitoring(self, total_asks: int):
        """Start live monitoring"""
        self.eta_calculator.initialize(total_asks)
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("✅ Live monitoring started")

    def stop_monitoring(self):
        """Stop live monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("⏹️  Live monitoring stopped")

    def _monitor_loop(self):
        """Monitor loop"""
        while self.monitoring:
            try:
                # Get latest processing results
                status = self.get_current_status()

                # Display status
                self.display_status(status)

                # Trace
                self.hawking_tracer.trace("monitor_update", status)

                time.sleep(5)  # Update every 5 seconds
            except Exception as e:
                logger.error(f"Error in monitor loop: {str(e)}")
                time.sleep(5)

    def get_current_status(self) -> Dict[str, Any]:
        try:
            """Get current processing status"""
            # Load latest processing results
            processing_dir = self.project_root / "data" / "ask_processing"
            if processing_dir.exists():
                result_files = list(processing_dir.glob("processing_results_*.json"))
                if result_files:
                    latest = max(result_files, key=lambda p: p.stat().st_mtime)
                    with open(latest, 'r', encoding='utf-8') as f:
                        results = json.load(f)

                    # Calculate metrics
                    processed = results.get("processed", 0)
                    total = results.get("total", 0)

                    # Update ETA calculator
                    if processed > 0:
                        # Estimate time taken (use file modification time)
                        file_time = latest.stat().st_mtime
                        current_time = time.time()
                        time_taken = current_time - file_time
                        self.eta_calculator.update(processed, time_taken)

                    # Get rate info
                    rate_info = self.rate_analyzer.calculate_rate()

                    # Get ETA
                    eta_info = self.eta_calculator.calculate_eta()

                    # Calculate batch number
                    batch_number = len(result_files)

                    return {
                        "timestamp": datetime.now().isoformat(),
                        "batch_number": batch_number,
                        "total_asks": total,
                        "processed": processed,
                        "skipped": results.get("skipped", 0),
                        "failed": results.get("failed", 0),
                        "rate": rate_info,
                        "eta": eta_info,
                        "completion_percentage": (processed / total * 100) if total > 0 else 0
                    }

            return {
                "timestamp": datetime.now().isoformat(),
                "batch_number": 0,
                "total_asks": 0,
                "processed": 0,
                "rate": {"status": "UNKNOWN"},
                "eta": {"batch_eta": "UNKNOWN"}
            }

        except Exception as e:
            self.logger.error(f"Error in get_current_status: {e}", exc_info=True)
            raise
    def display_status(self, status: Dict[str, Any]):
        """Display current status"""
        print("\n" + "=" * 80)
        print("⚔️ @JEDI @PATHFINDER - LIVE PROGRESSIVE MONITORING")
        print("=" * 80)
        print(f"📊 Batch Number: {status.get('batch_number', 0)}")
        print(f"📈 Progress: {status.get('processed', 0)} / {status.get('total_asks', 0)} ({status.get('completion_percentage', 0):.1f}%)")
        print(f"⚡ Rate: {status.get('rate', {}).get('asks_per_minute', 0):.2f} asks/min ({status.get('rate', {}).get('status', 'UNKNOWN')})")
        print(f"⏱️  ETA: {status.get('eta', {}).get('batch_eta', 'UNKNOWN')}")
        print(f"⏳ Remaining: {status.get('eta', {}).get('estimated_remaining', 'UNKNOWN')}")
        print(f"🕐 Elapsed: {status.get('eta', {}).get('elapsed_time', '0:00:00')}")
        print("=" * 80 + "\n")

    def save_status(self, status: Dict[str, Any]):
        try:
            """Save status to file"""
            status_file = self.data_dir / f"live_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, indent=2, default=str)
            return status_file


        except Exception as e:
            self.logger.error(f"Error in save_status: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS @ASK Live Monitor")
    parser.add_argument("--monitor", action="store_true", help="Start live monitoring")
    parser.add_argument("--status", action="store_true", help="Get current status")
    parser.add_argument("--total", type=int, default=1190, help="Total asks to process")

    args = parser.parse_args()

    project_root = Path(__file__).parent.parent.parent
    monitor = LiveMonitor(project_root)

    if args.monitor:
        monitor.start_monitoring(args.total)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            monitor.stop_monitoring()
    elif args.status:
        status = monitor.get_current_status()
        monitor.display_status(status)
        print(json.dumps(status, indent=2, default=str))
    else:
        # Default: show status
        status = monitor.get_current_status()
        monitor.display_status(status)


if __name__ == "__main__":


    main()