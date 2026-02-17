#!/usr/bin/env python3
"""
Iron Legion Download Monitor - R2D2 Astromech Engineering
Monitors model file downloads on KAIJU with real-time progress tracking
"""

import subprocess
import time
import json
from datetime import datetime
from pathlib import Path

class IronLegionDownloadMonitor:
    """R2D2-style monitoring for Iron Legion model downloads"""

    def __init__(self):
        self.kaiju_ip = "<NAS_IP>"
        self.models = {
            "Llama-3.2-11B-Vision-Instruct.Q4_K_M.gguf": {
                "expected_gb": 5.55,
                "volume_path": "/var/lib/docker/volumes/iron-legion-llamacpp_iron-legion-models/_data",
                "host_path": "D:\\Ollama\\models"
            }
        }
        self.monitor_interval = 10  # seconds

    def get_file_size_remote(self, file_path, is_volume=False):
        """Get file size from KAIJU via SSH"""
        try:
            if is_volume:
                # Docker volume path (Linux)
                cmd = f'ssh {self.kaiju_ip} "docker exec iron-legion-mark-ii-llama32-llamacpp sh -c \\"stat -c %s {file_path} 2>/dev/null || echo 0\\""'
            else:
                # Windows host path
                cmd = f'ssh {self.kaiju_ip} "$f = Get-Item \'{file_path}\' -ErrorAction SilentlyContinue; if ($f) {{ Write-Output $f.Length }} else {{ Write-Output 0 }}"'

            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                size_bytes = int(result.stdout.strip() or "0")
                return size_bytes
            return 0
        except Exception as e:
            print(f"Error checking file size: {e}")
            return 0

    def format_size(self, bytes_size):
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} PB"

    def check_download_progress(self, model_name):
        """Check download progress for a model"""
        model_info = self.models[model_name]
        expected_bytes = model_info["expected_gb"] * 1024 * 1024 * 1024

        # Check both volume and host paths
        volume_file = f"{model_info['volume_path']}/{model_name}"
        host_file = f"{model_info['host_path']}/{model_name}"

        volume_size = self.get_file_size_remote(volume_file, is_volume=True)
        host_size = self.get_file_size_remote(host_file, is_volume=False)

        current_size = max(volume_size, host_size)
        progress_pct = (current_size / expected_bytes * 100) if expected_bytes > 0 else 0

        return {
            "model": model_name,
            "current_size_bytes": current_size,
            "current_size_gb": current_size / (1024**3),
            "expected_size_gb": model_info["expected_gb"],
            "progress_percent": progress_pct,
            "volume_size": volume_size,
            "host_size": host_size,
            "status": "complete" if current_size >= expected_bytes * 0.95 else "downloading" if current_size > 0 else "not_started",
            "timestamp": datetime.now().isoformat()
        }

    def monitor(self, duration_minutes=60):
        """Monitor download progress"""
        print("=" * 80)
        print("🤖 R2D2 Astromech Engineering - Iron Legion Download Monitor")
        print("=" * 80)
        print(f"Monitoring downloads on KAIJU ({self.kaiju_ip})")
        print(f"Update interval: {self.monitor_interval} seconds")
        print(f"Duration: {duration_minutes} minutes")
        print("=" * 80)
        print()

        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)

        while time.time() < end_time:
            print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking status...")

            for model_name in self.models.keys():
                progress = self.check_download_progress(model_name)

                status_icon = {
                    "complete": "✅",
                    "downloading": "⏳",
                    "not_started": "❌"
                }.get(progress["status"], "❓")

                print(f"\n{status_icon} {progress['model']}")
                print(f"   Current: {self.format_size(progress['current_size_bytes'])} "
                      f"({progress['current_size_gb']:.2f} GB)")
                print(f"   Expected: {progress['expected_size_gb']:.2f} GB")
                print(f"   Progress: {progress['progress_percent']:.1f}%")

                if progress["volume_size"] > 0:
                    print(f"   Volume: {self.format_size(progress['volume_size'])}")
                if progress["host_size"] > 0:
                    print(f"   Host: {self.format_size(progress['host_size'])}")

                # Save progress to file for JARVIS
                self.save_progress(progress)

                if progress["status"] == "complete":
                    print(f"   ✅ Download complete!")
                    return progress

            time.sleep(self.monitor_interval)

        print("\n⏰ Monitoring duration expired")
        return None

    def save_progress(self, progress):
        try:
            """Save progress to JSON file for JARVIS integration"""
            data_dir = Path(__file__).parent.parent.parent / "data" / "iron_legion"
            data_dir.mkdir(parents=True, exist_ok=True)

            progress_file = data_dir / "download_progress.json"

            # Load existing data
            if progress_file.exists():
                with open(progress_file, 'r') as f:
                    data = json.load(f)
            else:
                data = {}

            # Update with latest progress
            data[progress["model"]] = progress
            data["last_update"] = datetime.now().isoformat()

            # Save
            with open(progress_file, 'w') as f:
                json.dump(data, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in save_progress: {e}", exc_info=True)
            raise
    def get_status_report(self):
        """Get current status report for JARVIS"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "kaiju_ip": self.kaiju_ip,
            "models": {}
        }

        for model_name in self.models.keys():
            progress = self.check_download_progress(model_name)
            report["models"][model_name] = progress

        return report


if __name__ == "__main__":
    import sys

    monitor = IronLegionDownloadMonitor()

    if len(sys.argv) > 1 and sys.argv[1] == "status":
        # Quick status check
        report = monitor.get_status_report()
        print(json.dumps(report, indent=2))
    else:
        # Continuous monitoring
        duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
        monitor.monitor(duration_minutes=duration)
