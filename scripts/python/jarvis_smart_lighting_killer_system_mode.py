#!/usr/bin/env python3
"""
JARVIS Smart Lighting Killer - System Mode Only
USS Lumina - @scotty (Windows Systems Architect)

#zerodarkthirty: After midnight + lid closed (AC or battery) → display brightness 0%%, keyboard 5%%, external off.
During daytime (6 AM–8 PM EST): full lighting everywhere (never apply zerodarkthirty).

Rules:
- Zerodarkthirty: after midnight (not daytime) AND lid closed → apply profile: display 0%%, keyboard 5%%, external 0 (no service kill).
- Enable (full lighting): daytime OR lid open → start services + set registry 100%% + display 80%%.

@JARVIS @SMART @LIGHTING @ZERODARKTHIRTY @LUMINA
"""

import subprocess
import sys
import time
from datetime import datetime
from datetime import time as dt_time
from pathlib import Path
from typing import Any, Dict, Optional

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SmartLightingKiller")


def _run_powershell(script: str) -> Dict[str, Any]:
    """Run PowerShell script and return result"""
    try:
        result = subprocess.run(
            ["powershell", "-Command", script], capture_output=True, text=True, timeout=10
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def is_system_mode() -> bool:
    """Check if system is in 'system' mode (vs manual/user mode)"""
    # For now, assume system mode is always active
    # In future, could check a config file or registry setting
    return True


def is_dark_mode() -> bool:
    """Check if Windows is in dark mode (after midnight)"""
    try:
        # Check Windows theme registry
        script = """
$appsTheme = (Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name 'AppsUseLightTheme' -ErrorAction SilentlyContinue).AppsUseLightTheme
$systemTheme = (Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize' -Name 'SystemUsesLightTheme' -ErrorAction SilentlyContinue).SystemUsesLightTheme

# 0 = Dark mode, 1 = Light mode
if ($appsTheme -eq 0 -or $systemTheme -eq 0) {
    Write-Output "dark"
} else {
    Write-Output "light"
}
"""
        result = _run_powershell(script)
        if result["success"]:
            theme = result["stdout"].lower().strip()
            is_dark = theme == "dark"

            # Also check time - only after midnight (00:00) is considered dark mode time for killing
            current_time = datetime.now().time()
            midnight = dt_time(0, 0)

            # If it's exactly midnight, consider it dark mode time
            if current_time == midnight:
                is_dark = True

            return is_dark

        return False
    except Exception as e:
        logger.warning(f"Could not check dark mode: {e}")
        return False


def is_lid_closed() -> bool:
    """Check if laptop lid is closed"""
    try:
        # Check lid state via WMI
        script = """
$lidState = (Get-WmiObject -Class Win32_SystemEnclosure -ErrorAction SilentlyContinue | Select-Object -First 1).ChassisTypes
# ChassisTypes: 10 = Notebook, 31 = Convertible, etc.
# For lid state, we check if the system thinks it's in tablet mode or if display is off

# Alternative: Check if primary display is off (indicates lid closed)
$display = Get-WmiObject -Namespace root\\WMI -Class WmiMonitorBasicDisplayParams -ErrorAction SilentlyContinue | Select-Object -First 1
if ($display) {
    # If we can't get display info, lid might be closed
    Write-Output "open"
} else {
    Write-Output "closed"
}

# More reliable: Check if system is in tablet mode (often indicates lid closed/rotated)
$tabletMode = (Get-ItemProperty -Path 'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\ImmersiveShell' -Name 'TabletMode' -ErrorAction SilentlyContinue).TabletMode
if ($tabletMode -eq 1) {
    Write-Output "closed"
} else {
    Write-Output "open"
}
"""
        result = _run_powershell(script)
        if result["success"]:
            lid_state = result["stdout"].lower().strip()
            return lid_state == "closed"

        # Fallback: Check if display is off
        script2 = """
$monitor = Get-WmiObject -Namespace root\\WMI -Class WmiMonitorBrightness -ErrorAction SilentlyContinue | Select-Object -First 1
if ($monitor) {
    Write-Output "open"
} else {
    Write-Output "closed"
}
"""
        result2 = _run_powershell(script2)
        if result2["success"]:
            return result2["stdout"].lower().strip() == "closed"

        return False
    except Exception as e:
        logger.warning(f"Could not check lid state: {e}")
        return False


def is_daytime_est() -> bool:
    """Daytime = 6 AM–8 PM EST. During daytime we never kill lighting (full lighting everywhere)."""
    from datetime import timedelta, timezone

    est = timezone(timedelta(hours=-5))
    now_est = datetime.now(est)
    return 6 <= now_est.hour < 20


# Zerodarkthirty profile: display 0%%, keyboard 5%%, external off (AC or battery)
ZERODARKTHIRTY_DISPLAY_BRIGHTNESS = 0
ZERODARKTHIRTY_KEYBOARD_BRIGHTNESS = 5


def should_apply_zerodarkthirty() -> bool:
    """#zerodarkthirty: After midnight + lid closed (AC or battery). Daytime = never."""
    if is_daytime_est():
        logger.info("   ℹ️  Daytime (6 AM–8 PM EST) — full lighting everywhere")
        return False

    if not is_system_mode():
        return False

    lid_closed = is_lid_closed()
    # AC or battery: after midnight + lid closed = zerodarkthirty
    should_apply = lid_closed

    logger.info(
        "   📊 Zerodarkthirty: after midnight, lid closed %s → apply (display 0%%, kb 5%%)",
        "✅" if lid_closed else "❌",
    )
    return should_apply


def should_enable_lighting() -> bool:
    """Enable full lighting when daytime OR lid open (not zerodarkthirty)."""
    if not is_system_mode():
        return False

    daytime = is_daytime_est()
    lid_closed = is_lid_closed()
    should_enable = daytime or not lid_closed

    logger.info(
        "   📊 Enable full lighting: daytime %s, lid closed %s → %s",
        "✅" if daytime else "❌",
        "✅" if lid_closed else "❌",
        "YES" if should_enable else "NO",
    )
    return should_enable


class SmartLightingKiller:
    """
    #zerodarkthirty: After midnight + lid closed + on power → totally black.
    Daytime (6 AM–8 PM EST): full lighting everywhere (never kill).
    Enable: daytime OR lid open OR on battery.
    """

    def __init__(self, project_root: Path, check_interval: int = 5):
        self.project_root = project_root
        self.check_interval = check_interval
        self.logger = get_logger("SmartLightingKiller")
        self.running = False
        self.kill_count = 0
        self.enable_count = 0

        self.logger.info("=" * 70)
        self.logger.info("🔧 SMART LIGHTING KILLER (#zerodarkthirty)")
        self.logger.info("   USS Lumina - @scotty (Windows Systems Architect)")
        self.logger.info("=" * 70)
        self.logger.info("")
        self.logger.info("   Rules:")
        self.logger.info(
            "   • Zerodarkthirty: after midnight + lid closed (AC or battery) → display 0%%, keyboard 5%%, external off"
        )
        self.logger.info("   • Daytime (6 AM–8 PM EST): full lighting everywhere")
        self.logger.info("   • Enable: daytime OR lid open")
        self.logger.info("=" * 70)
        self.logger.info("")

    def apply_zerodarkthirty(self) -> bool:
        """Apply zerodarkthirty profile: display brightness 0%%, keyboard 5%%, external off (no service kill)."""
        try:
            display_script = """
(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods -ErrorAction SilentlyContinue).WmiSetBrightness(1, 0)
Write-Output "OK"
"""
            _run_powershell(display_script)
            kb = ZERODARKTHIRTY_KEYBOARD_BRIGHTNESS
            script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)
foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{ New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null }}
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'Brightness' -Value {kb} -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value {kb} -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value {kb} -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingBrightness' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
        }}
    }} catch {{}}
}}
Write-Output "OK"
"""
            result = _run_powershell(script)
            return result["success"]
        except Exception as e:  # pylint: disable=broad-except
            self.logger.error("Error applying zerodarkthirty: %s", e)
            return False

    def kill_process(self) -> bool:
        """Kill AacAmbientLighting process (legacy; zerodarkthirty now uses apply_zerodarkthirty instead)."""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue | Stop-Process -Force",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )

            # Also try to stop parent services
            services = [
                "ArmouryCrateService",
                "LightingService",
                "AuraWallpaperService",
                "AuraService",
            ]
            for service in services:
                try:
                    subprocess.run(
                        [
                            "powershell",
                            "-Command",
                            f"Stop-Service -Name '{service}' -Force -ErrorAction SilentlyContinue",
                        ],
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )
                except Exception:
                    pass

            return True
        except Exception as e:
            self.logger.error(f"Error killing process: {str(e)}")
            return False

    def enable_lighting(self) -> bool:
        """Enable full lighting: display 80%%, start services, registry 100%% keyboard + external."""
        try:
            # 1) Display brightness back up (day level)
            _run_powershell("""
(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods -ErrorAction SilentlyContinue).WmiSetBrightness(1, 80)
Write-Output "OK"
""")
            # 2) Start services so keyboard/lighting hardware is driven
            start_script = """
$services = @('ArmouryCrateService', 'LightingService', 'AuraWallpaperService', 'AuraService')
foreach ($svc in $services) {
    try {
        $s = Get-Service -Name $svc -ErrorAction SilentlyContinue
        if ($s -and $s.Status -ne 'Running') {
            Start-Service -Name $svc -ErrorAction SilentlyContinue
        }
    } catch {}
}
Write-Output "Started"
"""
            _run_powershell(start_script)

            # 3) Set brightness to 100% via registry (services will pick this up)
            script = """
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKCU:\\Software\\ASUS\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\Aura'
)

foreach ($path in $paths) {
    try {
        if (-not (Test-Path $path)) {
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }
        if (Test-Path $path) {
            Set-ItemProperty -Path $path -Name 'Brightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'BacklightBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value 100 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enable' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'Enabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'LightingEnabled' -Value 1 -Type DWord -ErrorAction SilentlyContinue
        }
    } catch {
        # Continue
    }
}

Write-Output "Enabled"
"""
            result = _run_powershell(script)
            return result["success"]
        except Exception as e:
            self.logger.error(f"Error enabling lighting: {str(e)}")
            return False

    def is_running(self) -> bool:
        """Check if AacAmbientLighting is running"""
        try:
            result = subprocess.run(
                [
                    "powershell",
                    "-Command",
                    "Get-Process -Name 'AacAmbientLighting' -ErrorAction SilentlyContinue",
                ],
                capture_output=True,
                text=True,
                timeout=10,
            )
            return bool(result.stdout.strip())
        except Exception:
            return False

    def run_once(self) -> Dict[str, Any]:
        """Run one check cycle: zerodarkthirty (display 0%%, kb 5%%) or full lighting."""
        if should_apply_zerodarkthirty():
            self.logger.info(
                "   🔍 Applying #zerodarkthirty (display 0%%, keyboard 5%%, external off)..."
            )
            if self.apply_zerodarkthirty():
                self.kill_count += 1
                self.logger.info("   ✅ Zerodarkthirty applied (display 0%%, kb 5%%)")
                return {"action": "zerodarkthirty", "kill_count": self.kill_count}
            self.logger.warning("   ⚠️  Failed to apply zerodarkthirty")
            return {"action": "zerodarkthirty_failed", "kill_count": self.kill_count}

        if should_enable_lighting():
            self.logger.info("   🔍 Applying full lighting (daytime or lid open)...")
            if self.enable_lighting():
                self.enable_count += 1
                self.logger.info(
                    "   ✅ Full lighting applied (display 80%%, kb 100%%, external on)"
                )
                return {"action": "enabled", "enable_count": self.enable_count}
            self.logger.warning("   ⚠️  Failed to enable")
            return {"action": "enable_failed", "enable_count": self.enable_count}

        else:
            # No action needed
            return {
                "action": "no_action",
                "kill_count": self.kill_count,
                "enable_count": self.enable_count,
            }

    def run_continuous(self, duration: Optional[int] = None):
        """Run continuously"""
        self.running = True
        start_time = datetime.now()

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("🔄 STARTING CONTINUOUS MONITORING")
        self.logger.info(f"   Check interval: {self.check_interval} seconds")
        if duration:
            self.logger.info(f"   Duration: {duration} seconds")
        else:
            self.logger.info("   Duration: Infinite (Ctrl+C to stop)")
        self.logger.info("=" * 70)
        self.logger.info("")

        try:
            while self.running:
                result = self.run_once()
                time.sleep(self.check_interval)

                # Check duration
                if duration:
                    elapsed = (datetime.now() - start_time).total_seconds()
                    if elapsed >= duration:
                        self.logger.info("")
                        self.logger.info(f"   ⏰ Duration reached ({duration} seconds)")
                        break
        except KeyboardInterrupt:
            self.logger.info("")
            self.logger.info("   ⏹️  Stopped by user (Ctrl+C)")

        self.running = False

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("📊 MONITORING SUMMARY")
        self.logger.info("=" * 70)
        self.logger.info(f"   🔧 Total Kills: {self.kill_count}")
        self.logger.info(f"   ✅ Total Enables: {self.enable_count}")
        elapsed = (datetime.now() - start_time).total_seconds()
        self.logger.info(f"   ⏱️  Total Time: {elapsed:.0f} seconds")
        if elapsed > 0:
            actions_per_minute = ((self.kill_count + self.enable_count) / elapsed) * 60
            self.logger.info(f"   📊 Actions per Minute: {actions_per_minute:.1f}")
        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("✅ SMART LIGHTING KILLER STOPPED")
        self.logger.info("=" * 70)
        self.logger.info("")


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="Smart Lighting Killer - System Mode Only")
        parser.add_argument(
            "--interval", type=int, default=5, help="Check interval in seconds (default: 5)"
        )
        parser.add_argument(
            "--duration", type=int, default=None, help="Duration in seconds (default: infinite)"
        )
        parser.add_argument("--once", action="store_true", help="Run once and exit")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        killer = SmartLightingKiller(project_root, check_interval=args.interval)

        if args.once:
            result = killer.run_once()
            print()
            print("=" * 70)
            print("🔧 SMART LIGHTING KILLER (ONE-TIME)")
            print("=" * 70)
            action = result.get("action", "no_action")
            if action == "zerodarkthirty":
                print("   ✅ #zerodarkthirty applied (display 0%%, keyboard 5%%, external off)")
            elif action == "zerodarkthirty_failed":
                print("   ⚠️  Failed to apply zerodarkthirty")
            elif action == "enabled":
                print("   ✅ Full lighting applied (display 80%%, keyboard 100%%, external on)")
            elif action == "enable_failed":
                print("   ⚠️  Failed to apply full lighting")
            elif action == "no_action":
                print("   ℹ️  No action needed (conditions not met)")
            else:
                print("   ⚠️  Action: %s" % action)
            print("=" * 70)
        else:
            killer.run_continuous(duration=args.duration)

    except Exception as e:
        logger.error("Error in main: %s", e, exc_info=True)
        raise


if __name__ == "__main__":
    main()
