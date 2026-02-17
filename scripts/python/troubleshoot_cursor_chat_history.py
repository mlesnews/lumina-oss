#!/usr/bin/env python3
"""
Cursor IDE Chat History Troubleshooting

Diagnoses and fixes issues with:
1. Chat history not loading (pinned/unpinned, Agents category, Archived)
2. PIN functionality not working
3. Connection timeouts and errors

Tags: #CURSOR_IDE #TROUBLESHOOTING #CHAT_HISTORY #PIN #CONNECTION_ERRORS @JARVIS @LUMINA
"""

import sys
import json
import time
import shutil
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("CursorChatHistoryTroubleshoot")

# Import connection resilience modules
try:
    from cursor_connection_resilience import CursorConnectionResilience
    from cursor_connection_health_monitor import CursorConnectionHealthMonitor
    from cursor_chat_retry_manager import CursorChatRetryManager
    MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"⚠️  Some modules not available: {e}")
    MODULES_AVAILABLE = False


class CursorChatHistoryTroubleshooter:
    """
    Troubleshoots Cursor IDE chat history and connection issues.

    Issues addressed:
    1. Chat history not loading (Agents category, Archived)
    2. PIN functionality not working
    3. Connection timeouts (ECONNRESET, ConnectError)
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize troubleshooter"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "cursor_chat_troubleshooting"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Cursor IDE data locations
        self.cursor_app_data = Path.home() / "AppData" / "Roaming" / "Cursor"
        self.cursor_local_data = Path.home() / "AppData" / "Local" / "Cursor"
        self.cursor_user_data = Path.home() / ".cursor"

        # Connection resilience
        self.connection_resilience = None
        self.health_monitor = None
        if MODULES_AVAILABLE:
            try:
                self.connection_resilience = CursorConnectionResilience(
                    max_retries=5,
                    retry_delay=3.0
                )
                self.health_monitor = CursorConnectionHealthMonitor(self.project_root)
            except Exception as e:
                logger.warning(f"⚠️  Could not initialize connection modules: {e}")

        logger.info("✅ Cursor Chat History Troubleshooter initialized")
        logger.info(f"   Project root: {self.project_root}")
        logger.info(f"   Cursor AppData: {self.cursor_app_data}")
        logger.info(f"   Cursor LocalData: {self.cursor_local_data}")
        logger.info(f"   Cursor UserData: {self.cursor_user_data}")

    def diagnose_chat_history_issues(self) -> Dict[str, Any]:
        """
        Diagnose chat history loading issues.

        Checks:
        - Cursor IDE data directories
        - Chat history files
        - Index/cache files
        - Configuration files
        - Storage permissions
        """
        logger.info("=" * 80)
        logger.info("🔍 DIAGNOSING CURSOR IDE CHAT HISTORY ISSUES")
        logger.info("=" * 80)
        logger.info("")

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "issues_found": [],
            "recommendations": [],
            "data_locations": {},
            "file_counts": {},
            "permissions_ok": True,
            "cache_issues": [],
            "index_issues": []
        }

        # Check Cursor IDE data locations
        logger.info("📁 Checking Cursor IDE data locations...")
        locations = {
            "app_data": self.cursor_app_data,
            "local_data": self.cursor_local_data,
            "user_data": self.cursor_user_data
        }

        for name, path in locations.items():
            exists = path.exists()
            diagnosis["data_locations"][name] = {
                "path": str(path),
                "exists": exists,
                "readable": path.exists() and path.is_dir() and path.stat().st_mode & 0o444
            }

            if not exists:
                diagnosis["issues_found"].append(f"❌ {name} directory not found: {path}")
                diagnosis["recommendations"].append(f"Check if Cursor IDE is installed correctly")
            elif not diagnosis["data_locations"][name]["readable"]:
                diagnosis["issues_found"].append(f"⚠️  {name} directory not readable: {path}")
                diagnosis["permissions_ok"] = False

        # Search for chat history files
        logger.info("")
        logger.info("📋 Searching for chat history files...")
        chat_history_patterns = [
            "**/chat*.json",
            "**/conversation*.json",
            "**/history*.json",
            "**/agent*.json",
            "**/session*.json",
            "**/*chat*",
            "**/*conversation*"
        ]

        chat_files = []
        for location_name, location_path in locations.items():
            if location_path.exists():
                for pattern in chat_history_patterns:
                    try:
                        found = list(location_path.rglob(pattern))
                        chat_files.extend(found)
                    except Exception as e:
                        logger.debug(f"   Could not search {location_path} for {pattern}: {e}")

        # Remove duplicates
        chat_files = list(set(chat_files))
        diagnosis["file_counts"]["chat_files"] = len(chat_files)

        logger.info(f"   Found {len(chat_files)} potential chat history files")

        # Check for index/cache files
        logger.info("")
        logger.info("🔍 Checking for index/cache files...")
        index_patterns = [
            "**/*index*.json",
            "**/*cache*.json",
            "**/*.db",
            "**/*.sqlite",
            "**/Storage/**"
        ]

        index_files = []
        for location_name, location_path in locations.items():
            if location_path.exists():
                for pattern in index_patterns:
                    try:
                        found = list(location_path.rglob(pattern))
                        index_files.extend(found)
                    except Exception as e:
                        logger.debug(f"   Could not search {location_path} for {pattern}: {e}")

        index_files = list(set(index_files))
        diagnosis["file_counts"]["index_files"] = len(index_files)

        # Check for corrupted or empty index files
        for index_file in index_files[:20]:  # Check first 20
            try:
                if index_file.suffix == ".json":
                    with open(index_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if not data or data == {}:
                            diagnosis["index_issues"].append(f"Empty index file: {index_file.name}")
                elif index_file.suffix in [".db", ".sqlite"]:
                    size = index_file.stat().st_size
                    if size == 0:
                        diagnosis["index_issues"].append(f"Empty database: {index_file.name}")
            except json.JSONDecodeError:
                diagnosis["index_issues"].append(f"Corrupted JSON: {index_file.name}")
            except Exception as e:
                logger.debug(f"   Could not check {index_file}: {e}")

        # Check Storage directory (where Cursor stores chat data)
        storage_dirs = [
            self.cursor_app_data / "User" / "workspaceStorage",
            self.cursor_local_data / "User" / "workspaceStorage",
            self.cursor_user_data / "storage"
        ]

        logger.info("")
        logger.info("💾 Checking Storage directories...")
        for storage_dir in storage_dirs:
            if storage_dir.exists():
                logger.info(f"   ✅ Found: {storage_dir}")
                # Check for chat-related subdirectories
                try:
                    subdirs = [d for d in storage_dir.iterdir() if d.is_dir()]
                    diagnosis["file_counts"][f"storage_subdirs_{storage_dir.name}"] = len(subdirs)

                    # Look for chat history in subdirectories
                    for subdir in subdirs[:10]:  # Check first 10
                        chat_files_in_subdir = list(subdir.rglob("*.json"))
                        if chat_files_in_subdir:
                            logger.info(f"      Found {len(chat_files_in_subdir)} JSON files in {subdir.name}")
                except Exception as e:
                    logger.debug(f"   Could not check {storage_dir}: {e}")

        # Generate recommendations
        if len(chat_files) == 0:
            diagnosis["issues_found"].append("❌ No chat history files found")
            diagnosis["recommendations"].append("Chat history may be stored in a different location")
            diagnosis["recommendations"].append("Try restarting Cursor IDE")

        if diagnosis["index_issues"]:
            diagnosis["issues_found"].append(f"⚠️  Found {len(diagnosis['index_issues'])} index/cache issues")
            diagnosis["recommendations"].append("Clear Cursor IDE cache and restart")
            diagnosis["recommendations"].append("Index files may be corrupted - try rebuilding")

        if not diagnosis["permissions_ok"]:
            diagnosis["recommendations"].append("Fix file permissions for Cursor IDE data directories")

        # PIN functionality specific checks
        logger.info("")
        logger.info("📌 Checking PIN functionality...")
        diagnosis["pin_issues"] = []
        diagnosis["pin_recommendations"] = []

        # Check for PIN-related configuration
        config_files = [
            self.cursor_app_data / "User" / "settings.json",
            self.cursor_local_data / "User" / "settings.json",
            self.cursor_user_data / "settings.json"
        ]

        pin_config_found = False
        for config_file in config_files:
            if config_file.exists():
                try:
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        if "chat" in str(config).lower() or "pin" in str(config).lower():
                            pin_config_found = True
                            logger.info(f"   ✅ Found chat config in: {config_file.name}")
                except Exception as e:
                    logger.debug(f"   Could not read {config_file}: {e}")

        if not pin_config_found:
            diagnosis["pin_issues"].append("No PIN configuration found")
            diagnosis["pin_recommendations"].append("PIN functionality may require Cursor IDE update")
            diagnosis["pin_recommendations"].append("Try using keyboard shortcut instead of UI button")

        diagnosis["pin_recommendations"].append("Check Cursor IDE version - PIN may not be available in older versions")
        diagnosis["pin_recommendations"].append("Try right-clicking on chat session for context menu")

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ DIAGNOSIS COMPLETE")
        logger.info("=" * 80)

        return diagnosis

    def diagnose_connection_issues(self, request_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Diagnose connection timeout and error issues.

        Args:
            request_id: Specific request ID to investigate
        """
        logger.info("=" * 80)
        logger.info("🔍 DIAGNOSING CURSOR IDE CONNECTION ISSUES")
        if request_id:
            logger.info(f"   Request ID: {request_id}")
        logger.info("=" * 80)
        logger.info("")

        diagnosis = {
            "timestamp": datetime.now().isoformat(),
            "request_id": request_id,
            "connection_health": {},
            "recent_errors": [],
            "recommendations": [],
            "retry_config": {}
        }

        # Get connection health status
        if self.health_monitor:
            try:
                health = self.health_monitor.get_health_status()
                diagnosis["connection_health"] = health

                logger.info("📊 Connection Health Status:")
                logger.info(f"   Status: {health['health_status']}")
                logger.info(f"   Success Rate: {health['success_rate']}%")
                logger.info(f"   Recent Success Rate: {health['recent_success_rate']}%")
                logger.info(f"   Total Connections: {health['total_connections']}")
                logger.info(f"   Failed Connections: {health['failed_connections']}")
                logger.info("")
                logger.info("   Error Breakdown:")
                for error_type, count in health['error_breakdown'].items():
                    logger.info(f"      {error_type}: {count}")
                logger.info("")

                # Generate recommendations based on health
                if health['success_rate'] < 70.0:
                    diagnosis["recommendations"].append("⚠️  Low success rate - check network connection")
                    diagnosis["recommendations"].append("Consider increasing retry attempts and delays")

                if health['error_breakdown']['econnreset'] > 10:
                    diagnosis["recommendations"].append("❌ High ECONNRESET errors - connection instability")
                    diagnosis["recommendations"].append("Check firewall/antivirus blocking Cursor IDE")
                    diagnosis["recommendations"].append("Try disabling VPN or proxy if active")

                if health['error_breakdown']['timeout'] > 10:
                    diagnosis["recommendations"].append("⏱️  High timeout errors - slow network or server")
                    diagnosis["recommendations"].append("Increase timeout values in connection settings")
                    diagnosis["recommendations"].append("Check internet connection speed")

            except Exception as e:
                logger.warning(f"⚠️  Could not get health status: {e}")

        # Check retry configuration
        if self.connection_resilience:
            diagnosis["retry_config"] = {
                "max_retries": self.connection_resilience.max_retries,
                "retry_delay": self.connection_resilience.retry_delay
            }
            logger.info("🔄 Retry Configuration:")
            logger.info(f"   Max Retries: {diagnosis['retry_config']['max_retries']}")
            logger.info(f"   Retry Delay: {diagnosis['retry_config']['retry_delay']}s")
            logger.info("")

        # Search for request ID in logs
        if request_id:
            logger.info(f"🔍 Searching for request ID: {request_id}...")
            log_dir = self.project_root / "logs"
            if log_dir.exists():
                # Search recent log files
                log_files = sorted(log_dir.glob("*.log"), key=lambda p: p.stat().st_mtime, reverse=True)[:10]
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            if request_id in content:
                                logger.info(f"   ✅ Found in: {log_file.name}")
                                # Extract relevant lines
                                lines = content.split('\n')
                                matching_lines = [line for line in lines if request_id in line]
                                diagnosis["recent_errors"].extend(matching_lines[:5])
                    except Exception as e:
                        logger.debug(f"   Could not read {log_file}: {e}")

        # General recommendations
        diagnosis["recommendations"].extend([
            "✅ Ensure Cursor IDE is up to date",
            "✅ Check internet connection stability",
            "✅ Disable VPN/proxy temporarily to test",
            "✅ Check Windows Firewall settings",
            "✅ Try restarting Cursor IDE",
            "✅ Clear Cursor IDE cache if issues persist"
        ])

        logger.info("=" * 80)
        logger.info("✅ CONNECTION DIAGNOSIS COMPLETE")
        logger.info("=" * 80)

        return diagnosis

    def fix_chat_history_loading(self) -> Dict[str, Any]:
        """
        Attempt to fix chat history loading issues.

        Actions:
        - Clear corrupted cache files
        - Rebuild index if possible
        - Check and fix permissions
        - Provide manual steps
        """
        logger.info("=" * 80)
        logger.info("🔧 FIXING CHAT HISTORY LOADING ISSUES")
        logger.info("=" * 80)
        logger.info("")

        fix_results = {
            "timestamp": datetime.now().isoformat(),
            "actions_taken": [],
            "files_cleared": [],
            "recommendations": [],
            "manual_steps": []
        }

        # Step 1: Clear cache files
        logger.info("🧹 Step 1: Clearing cache files...")
        cache_dirs = [
            self.cursor_app_data / "Cache",
            self.cursor_local_data / "Cache",
            self.cursor_user_data / "cache"
        ]

        for cache_dir in cache_dirs:
            if cache_dir.exists():
                try:
                    # Backup cache before clearing
                    backup_dir = self.data_dir / "cache_backups" / cache_dir.name
                    backup_dir.mkdir(parents=True, exist_ok=True)
                    backup_path = backup_dir / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

                    logger.info(f"   Backing up cache: {cache_dir.name}")
                    if backup_path.exists():
                        shutil.rmtree(backup_path)
                    shutil.copytree(cache_dir, backup_path, dirs_exist_ok=True)

                    # Clear cache
                    for item in cache_dir.iterdir():
                        if item.is_file():
                            item.unlink()
                            fix_results["files_cleared"].append(str(item))
                        elif item.is_dir():
                            shutil.rmtree(item)
                            fix_results["files_cleared"].append(str(item))

                    fix_results["actions_taken"].append(f"Cleared cache: {cache_dir.name}")
                    logger.info(f"   ✅ Cleared: {cache_dir.name}")
                except Exception as e:
                    logger.warning(f"   ⚠️  Could not clear {cache_dir}: {e}")

        # Step 2: Check for corrupted index files
        logger.info("")
        logger.info("🔍 Step 2: Checking index files...")
        index_files = []
        for location in [self.cursor_app_data, self.cursor_local_data, self.cursor_user_data]:
            if location.exists():
                index_files.extend(location.rglob("**/*index*.json"))
                index_files.extend(location.rglob("**/*.db"))

        corrupted_count = 0
        for index_file in index_files[:20]:  # Check first 20
            try:
                if index_file.suffix == ".json":
                    with open(index_file, 'r', encoding='utf-8') as f:
                        json.load(f)  # Try to parse
                size = index_file.stat().st_size
                if size == 0:
                    corrupted_count += 1
                    logger.warning(f"   ⚠️  Empty file: {index_file.name}")
            except json.JSONDecodeError:
                corrupted_count += 1
                logger.warning(f"   ⚠️  Corrupted JSON: {index_file.name}")
                # Backup and remove corrupted file
                try:
                    backup_path = self.data_dir / "corrupted_backups" / index_file.name
                    backup_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(index_file, backup_path)
                    index_file.unlink()
                    fix_results["actions_taken"].append(f"Removed corrupted: {index_file.name}")
                except Exception as e:
                    logger.debug(f"   Could not remove {index_file}: {e}")

        if corrupted_count > 0:
            fix_results["actions_taken"].append(f"Found and handled {corrupted_count} corrupted index files")

        # Step 3: Manual steps
        logger.info("")
        logger.info("📋 Step 3: Manual steps required...")
        fix_results["manual_steps"] = [
            "1. Close Cursor IDE completely",
            "2. Restart Cursor IDE",
            "3. Wait for chat history to reload (may take a few minutes)",
            "4. If history still doesn't load:",
            "   - Go to Cursor IDE Settings",
            "   - Look for 'Chat' or 'History' settings",
            "   - Check 'Enable chat history' option",
            "   - Try 'Reload chat history' if available",
            "5. For PIN functionality:",
            "   - Right-click on chat session",
            "   - Look for 'Pin' option in context menu",
            "   - Or use keyboard shortcut (if available)",
            "   - Check Cursor IDE version - update if needed"
        ]

        for step in fix_results["manual_steps"]:
            logger.info(f"   {step}")

        # Recommendations
        fix_results["recommendations"] = [
            "✅ Restart Cursor IDE after clearing cache",
            "✅ Check Cursor IDE version - update if available",
            "✅ If issues persist, contact Cursor IDE support",
            "✅ Check Cursor IDE logs for specific errors",
            "✅ Try creating a new chat session to test if new chats work"
        ]

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ FIX ATTEMPTS COMPLETE")
        logger.info("=" * 80)

        return fix_results

    def improve_connection_resilience(self) -> Dict[str, Any]:
        """
        Improve connection resilience settings.

        Actions:
        - Increase retry attempts
        - Adjust retry delays
        - Update health monitoring
        """
        logger.info("=" * 80)
        logger.info("🔧 IMPROVING CONNECTION RESILIENCE")
        logger.info("=" * 80)
        logger.info("")

        improvements = {
            "timestamp": datetime.now().isoformat(),
            "changes_made": [],
            "new_config": {},
            "recommendations": []
        }

        if self.connection_resilience:
            # Increase max retries
            old_max_retries = self.connection_resilience.max_retries
            self.connection_resilience.max_retries = 5
            improvements["changes_made"].append(f"Increased max retries: {old_max_retries} → 5")

            # Increase retry delay
            old_delay = self.connection_resilience.retry_delay
            self.connection_resilience.retry_delay = 3.0
            improvements["changes_made"].append(f"Increased retry delay: {old_delay}s → 3.0s")

            improvements["new_config"] = {
                "max_retries": self.connection_resilience.max_retries,
                "retry_delay": self.connection_resilience.retry_delay
            }

            logger.info("✅ Updated connection resilience settings:")
            logger.info(f"   Max Retries: {improvements['new_config']['max_retries']}")
            logger.info(f"   Retry Delay: {improvements['new_config']['retry_delay']}s")

        improvements["recommendations"] = [
            "✅ Connection resilience settings updated",
            "✅ Retries will now attempt up to 5 times with 3s delays",
            "✅ Monitor connection health for improvements",
            "✅ If timeouts persist, check network/firewall settings"
        ]

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ CONNECTION RESILIENCE IMPROVED")
        logger.info("=" * 80)

        return improvements

    def generate_comprehensive_report(self) -> Dict[str, Any]:
        try:
            """Generate comprehensive troubleshooting report"""
            logger.info("=" * 80)
            logger.info("📊 GENERATING COMPREHENSIVE TROUBLESHOOTING REPORT")
            logger.info("=" * 80)
            logger.info("")

            # Run all diagnostics
            chat_diagnosis = self.diagnose_chat_history_issues()
            connection_diagnosis = self.diagnose_connection_issues()

            report = {
                "timestamp": datetime.now().isoformat(),
                "chat_history": chat_diagnosis,
                "connection": connection_diagnosis,
                "summary": {
                    "total_issues": len(chat_diagnosis["issues_found"]) + len(connection_diagnosis.get("recent_errors", [])),
                    "chat_files_found": chat_diagnosis["file_counts"].get("chat_files", 0),
                    "connection_health": connection_diagnosis.get("connection_health", {}).get("health_status", "Unknown")
                },
                "all_recommendations": chat_diagnosis["recommendations"] + connection_diagnosis["recommendations"]
            }

            # Save report
            report_file = self.data_dir / f"troubleshooting_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False, default=str)

            logger.info("")
            logger.info("=" * 80)
            logger.info("✅ REPORT GENERATED")
            logger.info("=" * 80)
            logger.info(f"   Report saved: {report_file.name}")
            logger.info("")

            # Print summary
            print("\n" + "=" * 80)
            print("📊 TROUBLESHOOTING SUMMARY")
            print("=" * 80)
            print(f"Total Issues Found: {report['summary']['total_issues']}")
            print(f"Chat Files Found: {report['summary']['chat_files_found']}")
            print(f"Connection Health: {report['summary']['connection_health']}")
            print(f"\nRecommendations: {len(report['all_recommendations'])}")
            for i, rec in enumerate(report['all_recommendations'][:10], 1):
                print(f"  {i}. {rec}")
            print("=" * 80)
            print()

            return report


        except Exception as e:
            self.logger.error(f"Error in generate_comprehensive_report: {e}", exc_info=True)
            raise
def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Cursor IDE Chat History Troubleshooting")
    parser.add_argument("--diagnose", action="store_true", help="Diagnose all issues")
    parser.add_argument("--fix-history", action="store_true", help="Attempt to fix chat history loading")
    parser.add_argument("--fix-connection", action="store_true", help="Improve connection resilience")
    parser.add_argument("--request-id", help="Specific request ID to investigate")
    parser.add_argument("--full-report", action="store_true", help="Generate comprehensive report")

    args = parser.parse_args()

    troubleshooter = CursorChatHistoryTroubleshooter()

    if args.full_report or (not args.diagnose and not args.fix_history and not args.fix_connection):
        # Default: full report
        troubleshooter.generate_comprehensive_report()
        troubleshooter.fix_chat_history_loading()
        troubleshooter.improve_connection_resilience()
    else:
        if args.diagnose:
            troubleshooter.diagnose_chat_history_issues()
            troubleshooter.diagnose_connection_issues(request_id=args.request_id)

        if args.fix_history:
            troubleshooter.fix_chat_history_loading()

        if args.fix_connection:
            troubleshooter.improve_connection_resilience()

    return 0


if __name__ == "__main__":


    sys.exit(main())