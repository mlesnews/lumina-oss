#!/usr/bin/env python3
"""
🏠 VERIFY HOUSE IN ORDER
Checks all critical systems and reports @TRIAGE status

Run this after fixing Dropbox/OneDrive to verify house is in order.

Usage:
    python scripts/python/verify_house_in_order.py
"""

import sys
import os
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Tuple

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("HouseInOrderVerification")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HouseInOrderVerification")


class HouseInOrderVerification:
    """Verify all systems are in order per @TRIAGE + @BAU"""

    def __init__(self):
        self.checks: List[Tuple[str, str, bool, str]] = []  # (name, status_color, passed, details)
        self.nas_path = r"\\<NAS_PRIMARY_IP>\backups"

    def check_disk_health(self) -> Tuple[str, bool, str]:
        """Check C: drive health"""
        try:
            import ctypes
            free_bytes = ctypes.c_ulonglong(0)
            total_bytes = ctypes.c_ulonglong(0)
            ctypes.windll.kernel32.GetDiskFreeSpaceExW(
                ctypes.c_wchar_p("C:\\"),
                None,
                ctypes.pointer(total_bytes),
                ctypes.pointer(free_bytes)
            )

            total_gb = total_bytes.value / (1024**3)
            free_gb = free_bytes.value / (1024**3)
            used_pct = ((total_gb - free_gb) / total_gb) * 100

            if used_pct >= 95:
                return "🔴 RED", False, f"CRITICAL: {used_pct:.1f}% used ({free_gb:.0f} GB free)"
            elif used_pct >= 85:
                return "🟠 ORANGE", False, f"WARNING: {used_pct:.1f}% used ({free_gb:.0f} GB free)"
            else:
                return "🟢 GREEN", True, f"HEALTHY: {used_pct:.1f}% used ({free_gb:.0f} GB free)"
        except Exception as e:
            return "🔴 RED", False, f"Error checking disk: {e}"

    def check_dropbox_location(self) -> Tuple[str, bool, str]:
        """Check if Dropbox is on C: drive"""
        dropbox_path = Path(os.path.expanduser("~")) / "Dropbox"

        if dropbox_path.exists():
            # Check if it's actually syncing content
            try:
                size_gb = sum(f.stat().st_size for f in dropbox_path.rglob('*') if f.is_file()) / (1024**3)
                if size_gb > 1:  # More than 1GB locally
                    return "🔴 RED", False, f"Dropbox ON C: drive ({size_gb:.1f} GB) - NEEDS FIX"
                else:
                    return "🟠 ORANGE", False, f"Dropbox exists but small ({size_gb:.2f} GB) - verify Smart Sync"
            except:
                return "🟠 ORANGE", False, "Dropbox folder exists - verify settings"
        else:
            return "🟢 GREEN", True, "Dropbox NOT syncing to C: drive"

    def check_onedrive_location(self) -> Tuple[str, bool, str]:
        """Check if OneDrive is on C: drive"""
        onedrive_path = Path(os.path.expanduser("~")) / "OneDrive"

        if onedrive_path.exists():
            try:
                size_gb = sum(f.stat().st_size for f in onedrive_path.rglob('*') if f.is_file()) / (1024**3)
                if size_gb > 1:
                    return "🔴 RED", False, f"OneDrive ON C: drive ({size_gb:.1f} GB) - NEEDS FIX"
                else:
                    return "🟠 ORANGE", False, f"OneDrive exists but small ({size_gb:.2f} GB) - verify Files On-Demand"
            except:
                return "🟠 ORANGE", False, "OneDrive folder exists - verify settings"
        else:
            return "🟢 GREEN", True, "OneDrive NOT syncing to C: drive"

    def check_nas_connectivity(self) -> Tuple[str, bool, str]:
        """Check NAS is accessible"""
        nas_path = Path(self.nas_path)
        try:
            if nas_path.exists():
                return "🟢 GREEN", True, f"NAS accessible at {self.nas_path}"
            else:
                return "🔴 RED", False, f"NAS NOT accessible at {self.nas_path}"
        except Exception as e:
            return "🔴 RED", False, f"NAS error: {e}"

    def check_ollama(self) -> Tuple[str, bool, str]:
        """Check Ollama service"""
        try:
            result = subprocess.run(
                ["ollama", "list"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0 and "NAME" in result.stdout:
                lines = result.stdout.strip().split('\n')
                model_count = len(lines) - 1  # Subtract header
                return "🟢 GREEN", True, f"Ollama running ({model_count} models)"
            else:
                return "🟠 ORANGE", False, "Ollama not responding"
        except subprocess.TimeoutExpired:
            return "🟠 ORANGE", False, "Ollama timeout"
        except FileNotFoundError:
            return "🟠 ORANGE", False, "Ollama not installed"
        except Exception as e:
            return "🟠 ORANGE", False, f"Ollama error: {e}"

    def check_phoenix_memory(self) -> Tuple[str, bool, str]:
        try:
            """Check PHOENIX memory system"""
            phoenix_db = project_root / "data" / "phoenix_memory" / "phoenix.db"
            if phoenix_db.exists():
                size_kb = phoenix_db.stat().st_size / 1024
                return "🟢 GREEN", True, f"PHOENIX active ({size_kb:.1f} KB)"
            else:
                return "🟠 ORANGE", False, "PHOENIX database not found"

        except Exception as e:
            self.logger.error(f"Error in check_phoenix_memory: {e}", exc_info=True)
            raise
    def check_git_status(self) -> Tuple[str, bool, str]:
        """Check for uncommitted changes"""
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True,
                text=True,
                cwd=str(project_root),
                timeout=10
            )
            if result.returncode == 0:
                changes = len([l for l in result.stdout.strip().split('\n') if l])
                if changes > 0:
                    return "🔘 CYAN", False, f"{changes} uncommitted changes"
                else:
                    return "🟢 GREEN", True, "All changes committed"
            else:
                return "🟠 ORANGE", False, "Git status check failed"
        except Exception as e:
            return "🟠 ORANGE", False, f"Git error: {e}"

    def run_all_checks(self) -> Dict[str, Any]:
        """Run all verification checks"""
        print("=" * 80)
        print("🏠 HOUSE IN ORDER VERIFICATION")
        print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("   Protocol: @TRIAGE + @BAU")
        print("=" * 80)
        print()

        checks = [
            ("C: Drive Health", self.check_disk_health),
            ("Dropbox Location", self.check_dropbox_location),
            ("OneDrive Location", self.check_onedrive_location),
            ("NAS Connectivity", self.check_nas_connectivity),
            ("Ollama Service", self.check_ollama),
            ("PHOENIX Memory", self.check_phoenix_memory),
            ("Git Status", self.check_git_status),
        ]

        results = []
        red_count = 0
        orange_count = 0
        green_count = 0

        for name, check_func in checks:
            status, passed, details = check_func()
            results.append((name, status, passed, details))

            if "RED" in status:
                red_count += 1
            elif "ORANGE" in status:
                orange_count += 1
            elif "GREEN" in status:
                green_count += 1

            print(f"   {status} {name}")
            print(f"      {details}")
            print()

        # Summary
        print("=" * 80)
        print("📊 SUMMARY")
        print("=" * 80)
        print(f"   🔴 RED (Blockers):     {red_count}")
        print(f"   🟠 ORANGE (Warnings):  {orange_count}")
        print(f"   🟢 GREEN (Satisfied):  {green_count}")
        print()

        if red_count > 0:
            print("   ❌ HOUSE NOT IN ORDER - Fix RED items first")
            print()
            print("   🔧 REQUIRED ACTIONS:")
            for name, status, passed, details in results:
                if "RED" in status:
                    print(f"      • {name}: {details}")
        elif orange_count > 0:
            print("   ⚠️  HOUSE MOSTLY IN ORDER - Review ORANGE items")
        else:
            print("   ✅ HOUSE IS IN ORDER - All systems GREEN")
            print("   ✅ Ready for next phase (backups, then trading)")

        print()
        print("=" * 80)

        return {
            "timestamp": datetime.now().isoformat(),
            "red_count": red_count,
            "orange_count": orange_count,
            "green_count": green_count,
            "house_in_order": red_count == 0 and orange_count == 0,
            "results": [
                {"name": name, "status": status, "passed": passed, "details": details}
                for name, status, passed, details in results
            ]
        }


def main():
    """Main entry point"""
    verifier = HouseInOrderVerification()
    result = verifier.run_all_checks()
    return 0 if result["house_in_order"] else 1


if __name__ == "__main__":


    sys.exit(main())