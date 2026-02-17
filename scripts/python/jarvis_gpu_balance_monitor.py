#!/usr/bin/env python3
"""
JARVIS GPU Balance Monitor
Monitors GPU utilization and ensures 50% balance for optimal performance
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
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

logger = get_logger("JARVISGPUBalance")


class GPUBalanceMonitor:
    """Monitor and balance GPU utilization at 50%"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.target_utilization = 50.0  # 50% target

    def get_gpu_utilization(self) -> Dict[str, Any]:
        """Get current GPU utilization"""
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu', 
                 '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )

            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpus = []
                for i, line in enumerate(lines):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        gpus.append({
                            "gpu_id": i,
                            "utilization": float(parts[0]),
                            "memory_used_mb": float(parts[1]),
                            "memory_total_mb": float(parts[2]),
                            "temperature": float(parts[3]),
                            "memory_percent": (float(parts[1]) / float(parts[2])) * 100
                        })

                return {
                    "success": True,
                    "gpus": gpus,
                    "average_utilization": sum(g["utilization"] for g in gpus) / len(gpus) if gpus else 0
                }
            else:
                return {"success": False, "error": "nvidia-smi failed"}
        except FileNotFoundError:
            return {"success": False, "error": "nvidia-smi not found (no NVIDIA GPU or drivers)"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def check_balance(self) -> Dict[str, Any]:
        """Check if GPU is balanced at target utilization"""
        gpu_info = self.get_gpu_utilization()

        if not gpu_info.get("success"):
            return {
                "success": False,
                "error": gpu_info.get("error"),
                "balanced": False
            }

        avg_util = gpu_info.get("average_utilization", 0)
        target = self.target_utilization
        tolerance = 10.0  # 10% tolerance

        balanced = abs(avg_util - target) <= tolerance

        return {
            "success": True,
            "balanced": balanced,
            "current_utilization": avg_util,
            "target_utilization": target,
            "difference": avg_util - target,
            "gpus": gpu_info.get("gpus", [])
        }

    def report_status(self) -> None:
        """Report GPU balance status"""
        status = self.check_balance()

        if not status.get("success"):
            self.logger.warning(f"⚠️  GPU monitoring unavailable: {status.get('error')}")
            return

        current = status.get("current_utilization", 0)
        target = status.get("target_utilization", 50)
        balanced = status.get("balanced", False)

        self.logger.info("="*80)
        self.logger.info("GPU BALANCE STATUS")
        self.logger.info("="*80)
        self.logger.info(f"Target Utilization: {target}%")
        self.logger.info(f"Current Utilization: {current:.1f}%")
        self.logger.info(f"Difference: {current - target:+.1f}%")
        self.logger.info(f"Status: {'✅ BALANCED' if balanced else '⚠️  NOT BALANCED'}")

        for gpu in status.get("gpus", []):
            self.logger.info(f"  GPU {gpu['gpu_id']}: {gpu['utilization']:.1f}% util, {gpu['memory_percent']:.1f}% memory, {gpu['temperature']:.0f}°C")

        self.logger.info("="*80)

        if not balanced:
            if current < target - 10:
                self.logger.warning(f"⚠️  GPU underutilized ({current:.1f}% < {target}%)")
                self.logger.info("   Recommendation: Increase workload or reduce GPU power limit")
            elif current > target + 10:
                self.logger.warning(f"⚠️  GPU overutilized ({current:.1f}% > {target}%)")
                self.logger.info("   Recommendation: Reduce workload or increase GPU power limit")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="GPU Balance Monitor")
        parser.add_argument("--check", action="store_true", help="Check GPU balance")
        parser.add_argument("--status", action="store_true", help="Show detailed status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        monitor = GPUBalanceMonitor(project_root)

        if args.check or args.status:
            monitor.report_status()
        else:
            status = monitor.check_balance()
            print(json.dumps(status, indent=2))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()