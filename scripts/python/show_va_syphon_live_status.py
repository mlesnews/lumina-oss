#!/usr/bin/env python3
"""
Show VA SYPHON/R5 Live Status

Shows real-time status of SYPHON/R5/JARVIS integrations in running VAs.

Tags: #VA #STATUS #SYPHON @JARVIS @LUMINA
"""

import sys
import time
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

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

logger = get_logger("ShowVASyphonLiveStatus")


class VALiveStatusMonitor:
    """Monitor live VA status"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.syphon_data_file = project_root / "data" / "syphon" / "extracted_data.json"
        self.r5_matrix_file = project_root / "data" / "r5_living_matrix" / "LIVING_CONTEXT_MATRIX_PROMPT.md"

    def find_running_vas(self) -> List[Dict[str, Any]]:
        """Find running VAs"""
        va_patterns = {
            "ironman": "ironman_virtual_assistant",
            "kenny": "kenny_imva_enhanced",
            "anakin": "anakin_combat_virtual_assistant",
            "jarvis": "jarvis_virtual_assistant"
        }

        running_vas = []

        for va_name, pattern in va_patterns.items():
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'create_time']):
                try:
                    cmdline = proc.info.get('cmdline', [])
                    if cmdline and any(pattern in str(arg) for arg in cmdline):
                        running_vas.append({
                            "name": va_name,
                            "pid": proc.info['pid'],
                            "uptime": time.time() - proc.info['create_time'],
                            "process": proc
                        })
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue

        return running_vas

    def check_syphon_activity(self) -> Dict[str, Any]:
        """Check SYPHON activity"""
        status = {
            "active": False,
            "data_file_exists": False,
            "last_extraction": None,
            "total_extractions": 0
        }

        if self.syphon_data_file.exists():
            status["data_file_exists"] = True
            try:
                with open(self.syphon_data_file, 'r') as f:
                    data = json.load(f)
                    if isinstance(data, list) and len(data) > 0:
                        status["active"] = True
                        status["total_extractions"] = len(data)
                        # Get most recent extraction
                        if data:
                            latest = max(data, key=lambda x: x.get('extracted_at', ''))
                            status["last_extraction"] = latest.get('extracted_at', 'unknown')
            except Exception as e:
                status["error"] = str(e)

        return status

    def check_r5_activity(self) -> Dict[str, Any]:
        """Check R5 activity"""
        status = {
            "active": False,
            "matrix_file_exists": False,
            "last_update": None,
            "size": 0
        }

        if self.r5_matrix_file.exists():
            status["matrix_file_exists"] = True
            try:
                stat = self.r5_matrix_file.stat()
                status["size"] = stat.st_size
                status["last_update"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
                status["active"] = stat.st_size > 0
            except Exception as e:
                status["error"] = str(e)

        return status

    def show_live_status(self):
        """Show live status of all VAs"""
        print("\n" * 2)
        print("=" * 80)
        print("📊 VA SYPHON/R5 LIVE STATUS".center(80))
        print("=" * 80)
        print()

        # Running VAs
        running_vas = self.find_running_vas()
        print(f"🔄 Running Virtual Assistants: {len(running_vas)}")
        print("-" * 80)
        for va in running_vas:
            uptime_hours = va["uptime"] / 3600
            print(f"  ✅ {va['name'].upper()}: PID {va['pid']} (Uptime: {uptime_hours:.1f}h)")
        print()

        # SYPHON Status
        syphon_status = self.check_syphon_activity()
        print("🔍 SYPHON Intelligence Extraction:")
        print("-" * 80)
        if syphon_status["active"]:
            print(f"  ✅ ACTIVE")
            print(f"     Total Extractions: {syphon_status['total_extractions']}")
            print(f"     Last Extraction: {syphon_status['last_extraction']}")
        else:
            print(f"  ⚠️  INACTIVE")
            if syphon_status.get("data_file_exists"):
                print(f"     Data file exists but empty")
            else:
                print(f"     Data file not found: {self.syphon_data_file}")
        print()

        # R5 Status
        r5_status = self.check_r5_activity()
        print("🧠 R5 Living Context Matrix:")
        print("-" * 80)
        if r5_status["active"]:
            print(f"  ✅ ACTIVE")
            print(f"     Matrix Size: {r5_status['size']:,} bytes")
            print(f"     Last Update: {r5_status['last_update']}")
        else:
            print(f"  ⚠️  INACTIVE")
            if r5_status.get("matrix_file_exists"):
                print(f"     Matrix file exists but empty")
            else:
                print(f"     Matrix file not found: {self.r5_matrix_file}")
        print()

        # Integration Status
        print("🔗 Integration Status:")
        print("-" * 80)
        if len(running_vas) > 0 and syphon_status["active"]:
            print("  ✅ VAs are running with SYPHON active")
        elif len(running_vas) > 0:
            print("  ⚠️  VAs are running but SYPHON not producing data")
            print("     → SYPHON may need time to extract intelligence")
            print("     → Check VA logs for SYPHON initialization")
        else:
            print("  ❌ No VAs running")
            print("     → Start VAs to see SYPHON/R5 in action")

        print()
        print("=" * 80)
        print("💡 TIP: SYPHON extracts intelligence every 60 seconds")
        print("   R5 aggregates context continuously")
        print("   Check VA logs for detailed activity")
        print("=" * 80)
        print()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description="Show VA SYPHON/R5 Live Status")
    parser.add_argument("--watch", action="store_true", help="Watch mode (refresh every 5s)")

    args = parser.parse_args()

    monitor = VALiveStatusMonitor(project_root)

    if args.watch:
        try:
            while True:
                monitor.show_live_status()
                time.sleep(5)
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
    else:
        monitor.show_live_status()


if __name__ == "__main__":


    main()