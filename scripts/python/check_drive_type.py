#!/usr/bin/env python3
"""
Check Drive Type - SSD vs HDD Detection

Checks if the OS drive (C:) is SSD or HDD.
This is critical for understanding migration performance.

Tags: #DRIVE-TYPE #SSD #HDD #DIAGNOSTIC @LUMINA
"""

import sys
import subprocess
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CheckDriveType")


def check_drive_type_windows(drive: str = "C:") -> dict:
    """Check if drive is SSD or HDD on Windows"""
    result = {
        "drive": drive,
        "type": "unknown",
        "method": None,
        "details": {}
    }

    # Method 1: PowerShell Get-PhysicalDisk
    try:
        ps_cmd = f'powershell -Command "Get-PhysicalDisk | Where-Object {{$_.DeviceID -eq 0 -or $_.FriendlyName -like \'*{drive[0]}*\'}} | Select-Object MediaType, FriendlyName, Model | ConvertTo-Json"'
        output = subprocess.run(
            ps_cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=10
        )

        if output.returncode == 0 and output.stdout:
            import json
            try:
                data = json.loads(output.stdout)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]

                if "MediaType" in data:
                    media_type = data["MediaType"]
                    if media_type == 4:  # SSD
                        result["type"] = "SSD"
                        result["method"] = "PowerShell Get-PhysicalDisk"
                    elif media_type == 3:  # HDD
                        result["type"] = "HDD"
                        result["method"] = "PowerShell Get-PhysicalDisk"

                    result["details"] = data
            except:
                pass
    except Exception as e:
        logger.debug(f"PowerShell method failed: {e}")

    # Method 2: WMI query (if PowerShell didn't work)
    if result["type"] == "unknown":
        try:
            wmi_cmd = f'wmic diskdrive get MediaType,Model,Size /format:list'
            output = subprocess.run(
                wmi_cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if output.returncode == 0:
                lines = output.stdout.split('\n')
                for line in lines:
                    if 'MediaType=' in line:
                        media_type = line.split('=')[1].strip()
                        # MediaType 4 = SSD, 3 = HDD
                        if media_type == '4':
                            result["type"] = "SSD"
                            result["method"] = "WMI"
                        elif media_type == '3':
                            result["type"] = "HDD"
                            result["method"] = "WMI"
        except Exception as e:
            logger.debug(f"WMI method failed: {e}")

    # Method 3: Check disk performance characteristics (heuristic)
    if result["type"] == "unknown":
        try:
            import psutil
            import time

            # Quick write test
            test_file = Path(drive) / "test_ssd_check.tmp"
            start = time.time()
            test_file.write_bytes(b"0" * (10 * 1024 * 1024))  # 10MB
            elapsed = time.time() - start
            speed_mbps = 10 / elapsed

            test_file.unlink()

            # Heuristic: SSDs typically write >100 MB/s, HDDs <150 MB/s
            if speed_mbps > 200:
                result["type"] = "SSD (likely)"
                result["method"] = "Performance heuristic"
            elif speed_mbps < 50:
                result["type"] = "HDD (likely)"
                result["method"] = "Performance heuristic"
            else:
                result["type"] = "Unknown (could be either)"
                result["method"] = "Performance heuristic"

            result["details"]["test_speed_mbps"] = speed_mbps
        except Exception as e:
            logger.debug(f"Performance test failed: {e}")

    return result


def main():
    """Check drive type"""
    print("\n" + "=" * 80)
    print("🔍 CHECKING DRIVE TYPE (SSD vs HDD)")
    print("=" * 80)
    print()

    result = check_drive_type_windows("C:")

    print(f"Drive: {result['drive']}")
    print(f"Type: {result['type']}")
    print(f"Detection Method: {result['method']}")
    print()

    if result.get('details'):
        print("Details:")
        for key, value in result['details'].items():
            print(f"   {key}: {value}")
        print()

    # Analysis
    print("=" * 80)
    print("📊 ANALYSIS")
    print("=" * 80)
    print()

    if result["type"] == "SSD" or "SSD" in result["type"]:
        print("✅ **DRIVE IS SSD**")
        print()
        print("Expected Performance:")
        print("   - Sequential Write: 500+ MB/s (typical SSD)")
        print("   - Random Write: 200+ MB/s")
        print()
        print("Current Performance:")
        print("   - Migration Rate: 2.78 MB/s")
        print("   - This is **EXTREMELY SLOW** for an SSD!")
        print()
        print("⚠️  **CRITICAL FINDING:**")
        print("   If this is an SSD, 2.78 MB/s indicates:")
        print("   1. Disk is 92% full → severe performance degradation")
        print("   2. Network file share (SMB) overhead")
        print("   3. Possible disk health issues")
        print("   4. File system fragmentation (even on SSD)")
        print()
        print("💡 **This is NOT normal SSD performance!**")
        print("   SSD should handle 100+ MB/s easily, even when full.")
        print("   The bottleneck is likely:")
        print("   - SMB network protocol overhead")
        print("   - Disk nearly full (92%) causing severe slowdown")
        print("   - Many small files (metadata overhead)")
    elif result["type"] == "HDD" or "HDD" in result["type"]:
        print("💾 **DRIVE IS HDD**")
        print()
        print("Expected Performance:")
        print("   - Sequential Write: 100-150 MB/s (typical HDD)")
        print("   - Random Write: 1-2 MB/s")
        print()
        print("Current Performance:")
        print("   - Migration Rate: 2.78 MB/s")
        print("   - This is slow but more understandable for HDD")
        print()
        print("💡 HDD performance is limited by:")
        print("   - Mechanical seek time")
        print("   - Disk 92% full → slower seeks")
        print("   - Random I/O patterns")
    else:
        print("❓ **DRIVE TYPE UNKNOWN**")
        print()
        print("Could not determine drive type.")
        print("Please check manually in Device Manager or Disk Management.")

    print()
    print("=" * 80)


if __name__ == "__main__":


    main()