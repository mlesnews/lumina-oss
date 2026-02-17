#!/usr/bin/env python3
"""
JARVIS Synology Command Interface
Simple command-line interface for JARVIS to execute Synology AI actions
#JARVIS #MANUS #NAS #SYNOLOGY #AI #COMMAND
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from jarvis_synology_ai_actions import JARVISSynologyAIActions
    from lumina_logger import get_logger
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("JARVISSynologyCommand")


def main():
    """JARVIS Synology Command Interface"""
    import argparse

    parser = argparse.ArgumentParser(
        description="JARVIS Synology AI Direct Actions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # List scheduled tasks
  python jarvis_synology_command.py list-tasks

  # Get system information
  python jarvis_synology_command.py system-info

  # Get storage information
  python jarvis_synology_command.py storage-info

  # Get package status
  python jarvis_synology_command.py package-status

  # Create a scheduled task
  python jarvis_synology_command.py create-task \\
    --name "JARVIS Health Check" \\
    --schedule "0 */2 * * *" \\
    --command "python /path/to/health_check.py"
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # List tasks
    list_parser = subparsers.add_parser("list-tasks", help="List scheduled tasks")
    list_parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    list_parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    list_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # System info
    sysinfo_parser = subparsers.add_parser("system-info", help="Get system information")
    sysinfo_parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    sysinfo_parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    sysinfo_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Storage info
    storage_parser = subparsers.add_parser("storage-info", help="Get storage information")
    storage_parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    storage_parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    storage_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Package status
    package_parser = subparsers.add_parser("package-status", help="Get package status")
    package_parser.add_argument("--package", help="Specific package name (optional)")
    package_parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    package_parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    package_parser.add_argument("--json", action="store_true", help="Output as JSON")

    # Create task
    create_parser = subparsers.add_parser("create-task", help="Create a scheduled task")
    create_parser.add_argument("--name", required=True, help="Task name")
    create_parser.add_argument("--schedule", required=True, help="Cron schedule (minute hour day month weekday)")
    create_parser.add_argument("--command", required=True, help="Command to execute")
    create_parser.add_argument("--enabled", action="store_true", default=True, help="Enable task (default: True)")
    create_parser.add_argument("--nas-ip", default="<NAS_PRIMARY_IP>", help="NAS IP address")
    create_parser.add_argument("--nas-port", type=int, default=5001, help="NAS port")
    create_parser.add_argument("--json", action="store_true", help="Output as JSON")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    try:
        with JARVISSynologyAIActions(nas_ip=args.nas_ip, nas_port=args.nas_port) as jarvis:
            result = None

            if args.command == "list-tasks":
                result = jarvis.list_scheduled_tasks()

            elif args.command == "system-info":
                result = jarvis.get_system_info()

            elif args.command == "storage-info":
                result = jarvis.get_storage_info()

            elif args.command == "package-status":
                result = jarvis.get_package_status(package_name=args.package if hasattr(args, 'package') else None)

            elif args.command == "create-task":
                result = jarvis.create_scheduled_task(
                    task_name=args.name,
                    schedule=args.schedule,
                    command=args.command,
                    enabled=args.enabled
                )

            if result:
                if args.json:
                    print(json.dumps(result, indent=2))
                else:
                    # Pretty print
                    if result.get("success"):
                        print("✅ Success!")
                        if "tasks" in result:
                            print(f"\n📋 Found {result.get('count', 0)} scheduled tasks:")
                            for task in result.get("tasks", []):
                                print(f"  • {task.get('name', 'Unknown')}")
                        elif "system_info" in result:
                            print("\n🖥️  System Information:")
                            print(json.dumps(result["system_info"], indent=2))
                        elif "storage" in result:
                            print("\n💾 Storage Information:")
                            print(json.dumps(result["storage"], indent=2))
                        elif "packages" in result:
                            print("\n📦 Package Status:")
                            print(json.dumps(result["packages"], indent=2))
                        elif "message" in result:
                            print(f"\n{result['message']}")
                    else:
                        print(f"❌ Error: {result.get('error', 'Unknown error')}")
                        return 1

                return 0 if result.get("success") else 1
            else:
                print("❌ No result returned")
                return 1

    except Exception as e:
        logger.error(f"❌ Error: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        return 1


if __name__ == "__main__":


    sys.exit(main())