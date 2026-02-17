#!/usr/bin/env python3
"""
JARVIS Migration Live Monitor - Iron Man Style
Live monitoring of cloud storage migration with JARVIS voice and visual alerts.

Features:
- Real-time migration progress tracking
- JARVIS voice alerts (speaks progress updates)
- JARVIS HUD visual alerts (Iron Man style)
- C: drive space monitoring
- Live status updates

Tags: #JARVIS #MIGRATION #MONITORING #VOICE #HUD #IRON_MAN #LIVE
"""

import sys
import time
import subprocess
import psutil
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import json
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from jarvis_hud_system import JARVISHUDSystem, AlertPriority, HUDDisplayType
    from jarvis_voice_interface import JARVISVoiceInterface
    from jarvis_azure_voice_interface import JARVISAzureVoiceInterface
    from jarvis_elevenlabs_voice import JARVISElevenLabsVoice
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    print(f"⚠️  Import error: {e}")
    JARVISElevenLabsVoice = None

logger = get_logger("JARVISMigrationMonitor")


class JARVISMigrationLiveMonitor:
    """
    JARVIS Migration Live Monitor

    Provides:
    - Real-time migration progress
    - JARVIS voice alerts (speaks updates)
    - JARVIS HUD visual alerts (Iron Man style)
    - C: drive space monitoring
    - Live status display
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.monitoring_active = False

        # Initialize JARVIS systems
        logger.info("🤖 Initializing JARVIS systems...")

        # HUD System (visual alerts)
        try:
            self.hud = JARVISHUDSystem(project_root=project_root)
            logger.info("   ✅ JARVIS HUD System ready")
        except Exception as e:
            logger.warning(f"   ⚠️  HUD not available: {e}")
            self.hud = None

        # ElevenLabs Voice (PRIMARY - best quality, natural JARVIS voice)
        try:
            if JARVISElevenLabsVoice:
                self.elevenlabs_voice = JARVISElevenLabsVoice(project_root=project_root)
                logger.info("   ✅ JARVIS ElevenLabs Voice ready (PRIMARY)")
            else:
                self.elevenlabs_voice = None
        except Exception as e:
            logger.warning(f"   ⚠️  ElevenLabs Voice not available: {e}")
            self.elevenlabs_voice = None

        # Azure Voice (fallback - good quality)
        try:
            self.azure_voice = JARVISAzureVoiceInterface(project_root=project_root)
            logger.info("   ✅ JARVIS Azure Voice ready (FALLBACK)")
        except Exception as e:
            logger.debug(f"   Azure Voice not available: {e}")
            self.azure_voice = None

        # Basic Voice Interface (last resort - pyttsx3, robotic)
        try:
            self.voice = JARVISVoiceInterface(project_root=project_root)
            logger.info("   ✅ JARVIS Voice Interface ready (LAST RESORT)")
        except Exception as e:
            logger.warning(f"   ⚠️  Voice not available: {e}")
            self.voice = None

        # Migration tracking
        self.migration_status = {
            "onedrive": {"status": "unknown", "progress": 0.0, "files_copied": 0, "size_copied_gb": 0.0},
            "dropbox": {"status": "unknown", "progress": 0.0, "files_copied": 0, "size_copied_gb": 0.0}
        }

        # C: drive tracking with trend analysis
        self.last_c_drive_space = 0.0
        self.last_update_time = datetime.now()
        self.space_history = []  # Track space over time to determine trend
        self.space_trend = "unknown"  # "increasing", "decreasing", "stable", "unknown"
        self.last_trend_check = datetime.now()

        logger.info("✅ JARVIS Migration Live Monitor initialized")
        logger.info("   🎤 Voice alerts: Enabled")
        logger.info("   👁️  Visual alerts: Enabled")
        logger.info("   📊 Live monitoring: Ready")

    def speak(self, text: str, priority: str = "info"):
        """Speak text using JARVIS voice - ElevenLabs first for natural voice"""
        # Priority 1: ElevenLabs (best quality, natural JARVIS voice)
        if self.elevenlabs_voice:
            try:
                self.elevenlabs_voice.speak(text)
                logger.debug("   🎤 Spoke via ElevenLabs (natural JARVIS voice)")
                return
            except Exception as e:
                logger.debug(f"   ElevenLabs speak error: {e}")

        # Priority 2: Azure Voice (good quality)
        if self.azure_voice:
            try:
                self.azure_voice.speak(text)
                logger.debug("   🎤 Spoke via Azure Voice")
                return
            except Exception:
                pass

        # Priority 3: Basic Voice (pyttsx3 - robotic, last resort)
        if self.voice:
            try:
                self.voice.speak(text)
                logger.debug("   🎤 Spoke via basic voice (robotic)")
                return
            except Exception:
                pass

        # Fallback: print
        logger.info(f"🔊 JARVIS: {text}")

    def create_visual_alert(self, title: str, message: str, priority: AlertPriority):
        """Create visual HUD alert"""
        if self.hud:
            try:
                alert = self.hud.create_alert(
                    title=title,
                    message=message,
                    priority=priority,
                    display_type=HUDDisplayType.STATUS,
                    action_required=priority in [AlertPriority.CRITICAL, AlertPriority.EMERGENCY]
                )
                return alert
            except Exception as e:
                logger.debug(f"Error creating HUD alert: {e}")
        return None

    def get_c_drive_space(self) -> Dict[str, Any]:
        """Get current C: drive space"""
        try:
            c_drive = psutil.disk_usage("C:")
            used_gb = c_drive.used / (1024**3)
            free_gb = c_drive.free / (1024**3)
            total_gb = c_drive.total / (1024**3)
            used_percent = (c_drive.used / c_drive.total) * 100

            return {
                "used_gb": round(used_gb, 2),
                "free_gb": round(free_gb, 2),
                "total_gb": round(total_gb, 2),
                "used_percent": round(used_percent, 1),
                "free_percent": round(100 - used_percent, 1)
            }
        except Exception as e:
            logger.error(f"Error getting C: drive space: {e}")
            return {}

    def check_migration_progress(self) -> Dict[str, Any]:
        """Check migration progress from robocopy processes"""
        progress = {
            "onedrive": {"running": False, "progress": 0.0},
            "dropbox": {"running": False, "progress": 0.0}
        }

        try:
            # Check for robocopy processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'robocopy' in proc.info['name'].lower():
                        cmdline = ' '.join(proc.info.get('cmdline', []))

                        # Check if it's OneDrive migration
                        if 'OneDrive' in cmdline and 'cloud_storage' in cmdline:
                            progress["onedrive"]["running"] = True

                        # Check if it's Dropbox migration
                        if 'Dropbox' in cmdline and 'cloud_storage' in cmdline:
                            progress["dropbox"]["running"] = True
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
        except Exception as e:
            logger.debug(f"Error checking processes: {e}")

        return progress

    def check_nas_target_size(self, provider: str) -> float:
        """Check size of migrated data on NAS"""
        nas_target = f"\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\cloud_storage\\{provider}"
        target_path = Path(nas_target)

        if not target_path.exists():
            return 0.0

        try:
            total_size = sum(
                f.stat().st_size for f in target_path.rglob('*') if f.is_file()
            )
            return round(total_size / (1024**3), 2)
        except Exception as e:
            logger.debug(f"Error checking NAS size: {e}")
            return 0.0

    def update_hud_display(self, status_data: Dict[str, Any]):
        """Update HUD display with migration status"""
        if not self.hud:
            return

        # Update status panel
        status_content = {
            "title": "Migration Status",
            "data": {
                "OneDrive": f"{status_data.get('onedrive_status', 'Unknown')}",
                "Dropbox": f"{status_data.get('dropbox_status', 'Unknown')}",
                "C: Drive": f"{status_data.get('c_drive_free_gb', 0):.1f} GB free ({status_data.get('c_drive_free_percent', 0):.1f}%)"
            }
        }
        self.hud.update_hud_display("status_panel", status_content)

        # Update metrics panel
        metrics_content = {
            "title": "Migration Metrics",
            "data": {
                "OneDrive Progress": f"{status_data.get('onedrive_progress', 0):.1f}%",
                "Dropbox Progress": f"{status_data.get('dropbox_progress', 0):.1f}%",
                "Space Freed": f"{status_data.get('space_freed_gb', 0):.1f} GB"
            }
        }
        self.hud.update_hud_display("metrics_panel", metrics_content)

    def monitor_migration(self, update_interval: float = 10.0):
        """
        Monitor migration with live JARVIS alerts

        Provides:
        - Voice updates every update_interval
        - Visual HUD updates
        - C: drive space monitoring
        - Migration progress tracking
        """
        logger.info("=" * 80)
        logger.info("🤖 JARVIS MIGRATION LIVE MONITOR - IRON MAN STYLE")
        logger.info("=" * 80)
        logger.info("   🎤 Voice alerts: Enabled")
        logger.info("   👁️  Visual alerts: Enabled")
        logger.info("   📊 Monitoring interval: {:.1f} seconds".format(update_interval))
        logger.info("   📈 Positive trend (space increasing): Reports every 5 minutes")
        logger.info("   📉 Negative trend (space decreasing): Reports every 1 minute")
        logger.info("")

        # Initial announcement
        self.speak("JARVIS migration monitor activated. Beginning live monitoring. I will report every five to ten minutes if space is increasing, and every minute if space is decreasing.")
        self.create_visual_alert(
            "Migration Monitor Active",
            "JARVIS is now monitoring cloud storage migration with trend-based alerts",
            AlertPriority.INFO
        )

        self.monitoring_active = True
        iteration = 0
        last_voice_update = datetime.now()

        # Initialize space tracking
        initial_c_drive = self.get_c_drive_space()
        if initial_c_drive:
            self.last_c_drive_space = initial_c_drive.get("free_gb", 0)
            self.space_history.append({
                "timestamp": datetime.now(),
                "free_gb": self.last_c_drive_space
            })

        try:
            while self.monitoring_active:
                iteration += 1
                current_time = datetime.now()

                # Get current status
                c_drive = self.get_c_drive_space()
                migration_progress = self.check_migration_progress()

                # Check NAS target sizes
                onedrive_size = self.check_nas_target_size("OneDrive")
                dropbox_size = self.check_nas_target_size("Dropbox")

                # Calculate space freed
                space_freed_gb = onedrive_size + dropbox_size

                # Track space history for trend analysis
                current_free_gb = c_drive.get("free_gb", 0)
                if current_free_gb > 0:
                    self.space_history.append({
                        "timestamp": current_time,
                        "free_gb": current_free_gb
                    })
                    # Keep only last 10 measurements (for trend analysis)
                    if len(self.space_history) > 10:
                        self.space_history.pop(0)

                # Determine space trend (increasing = positive, decreasing = negative)
                if len(self.space_history) >= 2:
                    oldest = self.space_history[0]["free_gb"]
                    newest = self.space_history[-1]["free_gb"]
                    change = newest - oldest

                    if change > 1.0:  # More than 1 GB increase
                        self.space_trend = "increasing"
                    elif change < -1.0:  # More than 1 GB decrease
                        self.space_trend = "decreasing"
                    else:
                        self.space_trend = "stable"
                else:
                    self.space_trend = "unknown"

                # Determine status
                onedrive_status = "Running" if migration_progress["onedrive"]["running"] else "Complete" if onedrive_size > 0 else "Pending"
                dropbox_status = "Running" if migration_progress["dropbox"]["running"] else "Complete" if dropbox_size > 0 else "Pending"

                # Calculate progress (rough estimate)
                onedrive_progress = min(100, (onedrive_size / 67.96) * 100) if onedrive_size > 0 else 0
                dropbox_progress = 0  # Unknown size, can't calculate

                # Status data
                status_data = {
                    "timestamp": current_time.isoformat(),
                    "onedrive_status": onedrive_status,
                    "onedrive_progress": onedrive_progress,
                    "onedrive_size_gb": onedrive_size,
                    "dropbox_status": dropbox_status,
                    "dropbox_progress": dropbox_progress,
                    "dropbox_size_gb": dropbox_size,
                    "c_drive_free_gb": c_drive.get("free_gb", 0),
                    "c_drive_free_percent": c_drive.get("free_percent", 0),
                    "c_drive_used_percent": c_drive.get("used_percent", 0),
                    "space_freed_gb": space_freed_gb,
                    "space_trend": self.space_trend
                }

                # Update HUD
                self.update_hud_display(status_data)

                # Dynamic voice update interval based on trend
                time_since_voice = (current_time - last_voice_update).total_seconds()

                # If space is decreasing (negative trend): alert every 60 seconds
                # If space is increasing (positive trend): alert every 5-10 minutes (300-600 seconds)
                if self.space_trend == "decreasing":
                    voice_interval = 60.0  # 1 minute for negative trend
                elif self.space_trend == "increasing":
                    voice_interval = 300.0  # 5 minutes for positive trend (can be 5-10 min)
                else:
                    voice_interval = 180.0  # 3 minutes for stable/unknown

                # Also check for significant changes (5+ GB)
                c_drive_change = current_free_gb - self.last_c_drive_space
                significant_change = abs(c_drive_change) >= 5.0

                # Determine if we should speak
                should_speak = False
                if time_since_voice >= voice_interval:
                    should_speak = True
                elif significant_change:
                    should_speak = True

                if should_speak:
                    free_gb = c_drive.get("free_gb", 0)
                    free_percent = c_drive.get("free_percent", 0)

                    # Build voice message with trend information
                    trend_msg = ""
                    if self.space_trend == "increasing":
                        change_gb = current_free_gb - self.last_c_drive_space
                        if change_gb > 0:
                            trend_msg = f" Positive direction. Space increased by {change_gb:.1f} gigabytes. "
                    elif self.space_trend == "decreasing":
                        change_gb = self.last_c_drive_space - current_free_gb
                        if change_gb > 0:
                            trend_msg = f" WARNING: Space decreased by {change_gb:.1f} gigabytes. "

                    # Build status message
                    if onedrive_status == "Running":
                        voice_msg = f"OneDrive migration in progress. {onedrive_progress:.0f} percent complete.{trend_msg}C drive has {free_gb:.1f} gigabytes free, {free_percent:.1f} percent available."
                    elif onedrive_status == "Complete":
                        voice_msg = f"OneDrive migration complete. {onedrive_size:.1f} gigabytes migrated.{trend_msg}C drive now has {free_gb:.1f} gigabytes free."
                    elif dropbox_status == "Running":
                        voice_msg = f"Dropbox migration in progress.{trend_msg}C drive has {free_gb:.1f} gigabytes free, {free_percent:.1f} percent available."
                    elif dropbox_status == "Complete":
                        voice_msg = f"Dropbox migration complete.{trend_msg}C drive now has {free_gb:.1f} gigabytes free, {free_percent:.1f} percent available."
                    else:
                        voice_msg = f"Migration monitoring active.{trend_msg}C drive has {free_gb:.1f} gigabytes free, {free_percent:.1f} percent available."

                    self.speak(voice_msg)
                    last_voice_update = current_time
                    self.last_c_drive_space = free_gb

                # Visual alerts for critical changes
                if c_drive.get("free_percent", 0) < 10:
                    self.create_visual_alert(
                        "CRITICAL: C Drive Space Low",
                        f"Only {c_drive.get('free_percent', 0):.1f}% free space remaining",
                        AlertPriority.CRITICAL
                    )
                elif c_drive.get("free_percent", 0) < 15:
                    self.create_visual_alert(
                        "WARNING: C Drive Space Low",
                        f"Only {c_drive.get('free_percent', 0):.1f}% free space remaining",
                        AlertPriority.WARNING
                    )

                # Progress alerts
                if onedrive_progress >= 100 and onedrive_status != "Complete":
                    self.create_visual_alert(
                        "OneDrive Migration Complete",
                        f"{onedrive_size:.1f} GB migrated successfully",
                        AlertPriority.INFO
                    )
                    self.speak(f"OneDrive migration complete. {onedrive_size:.1f} gigabytes migrated to NAS.")

                # Log status with trend
                trend_icon = "📈" if self.space_trend == "increasing" else "📉" if self.space_trend == "decreasing" else "➡️"
                logger.info(f"[{iteration}] {trend_icon} OneDrive: {onedrive_status} ({onedrive_progress:.1f}%) | "
                          f"Dropbox: {dropbox_status} | "
                          f"C: Drive: {c_drive.get('free_gb', 0):.1f} GB free ({c_drive.get('free_percent', 0):.1f}%) | "
                          f"Trend: {self.space_trend.upper()} | "
                          f"Space Freed: {space_freed_gb:.1f} GB")

                # Save status
                status_file = self.project_root / "data" / "system" / f"migration_live_status_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                status_file.parent.mkdir(parents=True, exist_ok=True)
                with open(status_file, 'w', encoding='utf-8') as f:
                    json.dump(status_data, f, indent=2, ensure_ascii=False)

                # Wait for next update
                time.sleep(update_interval)

        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Monitoring stopped by user")
            self.speak("Migration monitoring stopped.")
            self.monitoring_active = False
        except Exception as e:
            logger.error(f"❌ Monitoring error: {e}", exc_info=True)
            self.create_visual_alert(
                "Monitoring Error",
                f"Error in migration monitoring: {str(e)}",
                AlertPriority.CRITICAL
            )
            self.monitoring_active = False

    def start_monitoring(self, update_interval: float = 10.0):
        """Start monitoring in background thread"""
        monitor_thread = threading.Thread(
            target=self.monitor_migration,
            args=(update_interval,),
            daemon=True
        )
        monitor_thread.start()
        logger.info("✅ Monitoring started in background thread")
        return monitor_thread


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="JARVIS Migration Live Monitor")
    parser.add_argument("--interval", "-i", type=float, default=10.0,
                       help="Update interval in seconds (default: 10)")
    parser.add_argument("--once", action="store_true",
                       help="Show status once and exit")

    args = parser.parse_args()

    monitor = JARVISMigrationLiveMonitor(project_root)

    if args.once:
        # Single status check
        c_drive = monitor.get_c_drive_space()
        migration_progress = monitor.check_migration_progress()

        print("\n" + "=" * 80)
        print("📊 MIGRATION STATUS (Single Check)")
        print("=" * 80)
        print(f"C: Drive Free: {c_drive.get('free_gb', 0):.1f} GB ({c_drive.get('free_percent', 0):.1f}%)")
        print(f"OneDrive: {migration_progress['onedrive']['running']}")
        print(f"Dropbox: {migration_progress['dropbox']['running']}")
        print("=" * 80)
    else:
        # Continuous monitoring
        print("\n🤖 JARVIS Migration Live Monitor")
        print("   Press Ctrl+C to stop")
        print("")
        monitor.monitor_migration(update_interval=args.interval)


if __name__ == "__main__":


    main()