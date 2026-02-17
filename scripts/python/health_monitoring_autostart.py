#!/usr/bin/env python3
"""
Health Monitoring Auto-Start System

Ensures health monitoring is automatically started for all cluster services
and endpoints. Patches existing code to enable auto-start by default.

Tags: #HEALTH_MONITORING #AUTOSTART #CLUSTER @JARVIS @LUMINA
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("health_monitoring_autostart")


class HealthMonitoringPatcher:
    """Patches code to enable auto-start health monitoring"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.patches_applied = []
        self.patches_failed = []

    def find_cluster_files(self) -> List[Path]:
        """Find cluster-related Python files"""
        cluster_files = []

        # Search for cluster-related files
        patterns = ["*cluster*.py", "*ultron*.py", "*iron_legion*.py", "*router*.py"]

        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            for pattern in patterns:
                cluster_files.extend(scripts_dir.rglob(pattern))

        return list(set(cluster_files))  # Remove duplicates

    def patch_health_monitoring_init(self, file_path: Path) -> Tuple[bool, str]:
        """Patch __init__ method to auto-start health monitoring"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            original_content = content

            # Pattern 1: Find self.monitoring = False and change to True
            pattern1 = r"(self\.monitoring\s*=\s*)False"
            replacement1 = r"\1True  # Auto-start enabled by health_monitoring_autostart.py"

            if re.search(pattern1, content):
                content = re.sub(pattern1, replacement1, content)

            # Pattern 2: Find __init__ methods and add auto-start call
            # Look for class definitions with __init__ methods
            class_pattern = r'(class\s+\w+[^:]*:\s*\n(?:\s*"""[^"]*"""\s*\n)?)(\s+def\s+__init__\s*\([^)]*\)\s*:\s*\n(?:\s*"""[^"]*"""\s*\n)?)'

            def add_autostart(match):
                class_def = match.group(1)
                init_def = match.group(2)

                # Check if start_health_monitoring is already called
                if "start_health_monitoring" in content:
                    return match.group(0)

                # Add auto-start call after __init__ definition
                # Find the end of __init__ method (next method or end of class)
                init_start = match.end()
                # Look for next method or class end
                next_method = re.search(r"\n(\s+)(def\s+\w+|class\s+\w+)", content[init_start:])

                if next_method:
                    indent = next_method.group(1)
                    insert_pos = init_start + next_method.start()
                    # Insert before next method
                    autostart_code = f"\n{indent}# Auto-start health monitoring\n{indent}self.start_health_monitoring()\n"
                    return content[:insert_pos] + autostart_code + content[insert_pos:]

                return match.group(0)

            # Pattern 3: Add start_health_monitoring() call if monitoring methods exist
            if "start_health_monitoring" in content or "health_monitoring" in content.lower():
                # Find __init__ method
                init_pattern = (
                    r'(def\s+__init__\s*\([^)]*\)\s*:\s*\n(?:\s*"""[^"]*"""\s*\n)?)(\s+)([^\n]+)'
                )

                def add_to_init(match):
                    init_def = match.group(1)
                    indent = match.group(2)
                    first_line = match.group(3)

                    # Check if already has start_health_monitoring call
                    if "start_health_monitoring()" in content:
                        return match.group(0)

                    # Add after first line of __init__
                    return (
                        init_def
                        + indent
                        + first_line
                        + f"\n{indent}# Auto-start health monitoring\n{indent}self.start_health_monitoring()\n"
                    )

                content = re.sub(init_pattern, add_to_init, content, count=1)

            # Pattern 4: Ensure monitoring thread is started
            if "monitor_thread" in content and "Thread" in content:
                # Find where monitor_thread is created but not started
                thread_pattern = r"(self\.monitor_thread\s*=\s*threading\.Thread[^\n]+\n)"
                if re.search(thread_pattern, content):
                    # Add start() call after thread creation
                    def add_thread_start(match):
                        thread_creation = match.group(1)
                        indent = " " * (len(thread_creation) - len(thread_creation.lstrip()))
                        return (
                            thread_creation
                            + f"{indent}self.monitor_thread.start()  # Auto-start enabled\n"
                        )

                    content = re.sub(thread_pattern, add_thread_start, content)

            # Only write if content changed
            if content != original_content:
                # Create backup
                backup_path = file_path.with_suffix(".py.backup")
                with open(backup_path, "w", encoding="utf-8") as f:
                    f.write(original_content)

                # Write patched content
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(content)

                return True, "Patched successfully"
            else:
                return False, "No changes needed"

        except Exception as e:
            return False, f"Error: {str(e)}"

    def patch_all_files(self) -> Tuple[int, int]:
        """Patch all cluster files"""
        files = self.find_cluster_files()

        patched = 0
        failed = 0

        for file_path in files:
            # Skip this file itself
            if file_path.name == "health_monitoring_autostart.py":
                continue

            logger.info(f"Checking {file_path.name}...")
            success, message = self.patch_health_monitoring_init(file_path)

            if success:
                patched += 1
                self.patches_applied.append((str(file_path), message))
                logger.info(f"  ✅ {message}")
            else:
                if "Error" in message:
                    failed += 1
                    self.patches_failed.append((str(file_path), message))
                    logger.warning(f"  ❌ {message}")
                else:
                    logger.debug(f"  ℹ️  {message}")

        return patched, failed

    def create_monitoring_wrapper(self) -> Path:
        """Create a monitoring wrapper module that ensures auto-start"""
        wrapper_path = self.project_root / "scripts" / "python" / "cluster_health_monitor.py"

        wrapper_code = '''#!/usr/bin/env python3
"""
Cluster Health Monitor Wrapper

Ensures health monitoring is always active for cluster services.
This module patches cluster classes to auto-start health monitoring.

Tags: #HEALTH_MONITORING #AUTOSTART #WRAPPER @JARVIS @LUMINA
"""

import threading
import time
from typing import Dict, Optional
from pathlib import Path
import json
import requests

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("cluster_health_monitor")


class ClusterHealthMonitor:
    """Centralized health monitoring for all cluster endpoints"""

    def __init__(self, registry_path: Optional[Path] = None):
        if registry_path is None:
            project_root = Path(__file__).parent.parent.parent
            registry_path = project_root / "config" / "cluster_endpoint_registry.json"

        self.registry_path = registry_path
        self.endpoints: Dict[str, Dict] = {}
        self.monitoring = True
        self.monitor_thread: Optional[threading.Thread] = None
        self.interval_seconds = 10
        self.timeout_seconds = 5

        self.load_registry()
        self.start_monitoring()  # Auto-start!

    def load_registry(self):
        """Load endpoint registry"""
        if self.registry_path.exists():
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                registry = json.load(f)
                self.endpoints = registry.get("endpoints", {})

    def check_endpoint_health(self, endpoint_id: str, endpoint: Dict) -> Dict:
        """Check health of a single endpoint"""
        health_check = endpoint.get("health_check")
        if not health_check:
            return {"status": "unknown", "error": "No health check URL"}

        try:
            response = requests.get(health_check, timeout=self.timeout_seconds)
            if response.status_code == 200:
                return {"status": "operational", "response_time_ms": response.elapsed.total_seconds() * 1000}
            else:
                return {"status": "degraded", "error": f"HTTP {response.status_code}"}
        except requests.exceptions.Timeout:
            return {"status": "offline", "error": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"status": "offline", "error": "Connection refused"}
        except Exception as e:
            return {"status": "unknown", "error": str(e)}

    def monitor_loop(self):
        """Main monitoring loop"""
        logger.info("Health monitoring started")

        while self.monitoring:
            try:
                for endpoint_id, endpoint in self.endpoints.items():
                    health = self.check_endpoint_health(endpoint_id, endpoint)

                    # Update endpoint status if changed
                    current_status = endpoint.get("status", "unknown")
                    new_status = health.get("status", "unknown")

                    if new_status != current_status:
                        logger.info(f"Endpoint {endpoint_id} status: {current_status} → {new_status}")
                        endpoint["status"] = new_status

                # Save updated registry
                self.save_registry()

            except Exception as e:
                logger.error(f"Monitoring error: {e}")

            time.sleep(self.interval_seconds)

    def save_registry(self):
        """Save updated registry"""
        try:
            registry = {"endpoints": self.endpoints}
            with open(self.registry_path, 'w', encoding='utf-8') as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def start_monitoring(self):
        """Start health monitoring thread"""
        if self.monitor_thread and self.monitor_thread.is_alive():
            logger.debug("Monitoring already running")
            return

        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop, daemon=True)
        self.monitor_thread.start()
        logger.info("Health monitoring thread started")

    def stop_monitoring(self):
        """Stop health monitoring"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        logger.info("Health monitoring stopped")


# Global instance - auto-starts on import
_global_monitor: Optional[ClusterHealthMonitor] = None

def get_global_monitor() -> ClusterHealthMonitor:
    """Get or create global health monitor instance"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = ClusterHealthMonitor()
    return _global_monitor

# Auto-start on import
get_global_monitor()
'''

        wrapper_path.write_text(wrapper_code, encoding="utf-8")
        logger.info(f"Created monitoring wrapper: {wrapper_path}")

        return wrapper_path

    def print_report(self):
        """Print patching report"""
        print("=" * 80)
        print("HEALTH MONITORING AUTO-START PATCHING REPORT")
        print("=" * 80)

        print(f"\n✅ Patches Applied: {len(self.patches_applied)}")
        for file_path, message in self.patches_applied:
            print(f"  {file_path}")
            print(f"    {message}")

        print(f"\n❌ Patches Failed: {len(self.patches_failed)}")
        for file_path, message in self.patches_failed:
            print(f"  {file_path}")
            print(f"    {message}")

        print("\n" + "=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Enable auto-start health monitoring for cluster services"
    )
    parser.add_argument(
        "--create-wrapper", action="store_true", help="Create monitoring wrapper module"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Show what would be patched without making changes"
    )

    args = parser.parse_args()

    patcher = HealthMonitoringPatcher(project_root)

    if args.create_wrapper:
        wrapper_path = patcher.create_monitoring_wrapper()
        print(f"✅ Created monitoring wrapper: {wrapper_path}")

    if not args.dry_run:
        patched, failed = patcher.patch_all_files()
        patcher.print_report()
        print(f"\nSummary: {patched} files patched, {failed} failed")
    else:
        files = patcher.find_cluster_files()
        print(f"Would check {len(files)} files for patching")
        for file_path in files[:10]:  # Show first 10
            print(f"  {file_path.name}")


if __name__ == "__main__":
    main()
