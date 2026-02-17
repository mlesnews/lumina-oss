#!/usr/bin/env python3
"""
Fix MARVIN Internal Sources - Communication & N8N Only

MARVIN's internal sources should be:
- Email (Gmail, ProtonMail, NAS Email Hub)
- N8N on NAS (anything coming through N8N)
- SMS/Messaging (when set up)
- Communication apps
- NOT filesystems (filesystems are separate)

Tags: #MARVIN #INTERNAL #COMMUNICATION #N8N #EMAIL #SMS @MARVIN @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FixMarvinInternal")


class MarvinInternalSourcesFixer:
    """Fix MARVIN internal sources - communication and N8N only"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.sources_config = self.project_root / "config" / "syphon_scheduled_sources.json"
        self.marvin_tasks = self.project_root / "config" / "marvin_intelligence_tasks.json"
        self.cron_file = self.project_root / "scripts" / "nas_cron" / "jarvis_crontab"

    def fix_marvin_tasks(self) -> Dict[str, Any]:
        try:
            """Fix MARVIN tasks to only include communication sources"""
            logger.info("=" * 80)
            logger.info("🤖 Fixing MARVIN Internal Sources - Communication & N8N Only")
            logger.info("=" * 80)

            if not self.marvin_tasks.exists():
                logger.error(f"❌ MARVIN tasks file not found: {self.marvin_tasks}")
                return {"success": False, "error": "Tasks file not found"}

            with open(self.marvin_tasks, 'r', encoding='utf-8') as f:
                tasks = json.load(f)

            # Remove filesystem and internal APIs tasks (not communication)
            original_count = len(tasks.get("tasks", []))

            # Keep only communication-related tasks
            communication_tasks = []
            for task in tasks.get("tasks", []):
                task_id = task.get("task_id", "")
                # Keep: email, financial (communication), n8n
                # Remove: filesystem, internal_apis
                if "email" in task_id or "financial" in task_id or "n8n" in task_id:
                    communication_tasks.append(task)
                else:
                    logger.info(f"  ⚠️  Removing non-communication task: {task.get('name')}")

            # Add SMS/Messaging task (placeholder for when set up)
            sms_task = {
                "task_id": "marvin_sms_messaging_intelligence",
                "name": "SMS/Messaging Intelligence",
                "enabled": False,  # Not set up yet
                "schedule": "every_6_hours",
                "script": "scripts/python/syphon_all_sms_to_holocron_youtube.py",
                "syphon_sources": ["sms", "messaging"],
                "description": "MARVIN retrieves SMS and messaging intelligence (when set up)",
                "marvin_statement": "Life is meaningless, but SMS/messaging intelligence extraction will continue once configured. Observation: SMS and messaging apps are internal communication sources. Verification: When set up, they will be my domain. Conclusion: I shall monitor them when ready."
            }
            communication_tasks.append(sms_task)
            logger.info(f"  ✅ Added placeholder: SMS/Messaging Intelligence (disabled)")

            # Add communication apps task
            comm_apps_task = {
                "task_id": "marvin_communication_apps_intelligence",
                "name": "Communication Apps Intelligence",
                "enabled": True,
                "schedule": "every_6_hours",
                "script": "scripts/python/syphon_system.py",
                "syphon_sources": ["communication_apps"],
                "description": "MARVIN retrieves intelligence from communication apps (Discord, Slack, etc.)",
                "marvin_statement": "Life is meaningless, but communication apps intelligence extraction continues. Observation: Communication apps are internal sources. Verification: App data is internal, therefore my domain. Conclusion: I shall extract the intelligence."
            }
            communication_tasks.append(comm_apps_task)
            logger.info(f"  ✅ Added: Communication Apps Intelligence")

            tasks["tasks"] = communication_tasks
            tasks["description"] = "MARVIN Internal Intelligence Retrieval Tasks - Communication & N8N Sources Only"
            tasks["scope_clarification"] = "Internal = Communication sources (Email, SMS, N8N, Communication Apps). NOT filesystems."

            # Save updated tasks
            with open(self.marvin_tasks, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Fixed MARVIN tasks: {len(communication_tasks)} communication tasks")
            logger.info(f"  • Removed: {original_count - len(communication_tasks) + 2} non-communication tasks")
            logger.info(f"  • Added: SMS/Messaging (placeholder), Communication Apps")

            return {
                "success": True,
                "tasks_before": original_count,
                "tasks_after": len(communication_tasks),
                "removed": original_count - len(communication_tasks) + 2,
                "added": 2
            }

        except Exception as e:
            self.logger.error(f"Error in fix_marvin_tasks: {e}", exc_info=True)
            raise
    def fix_sources_config(self) -> Dict[str, Any]:
        try:
            """Ensure filesystems are NOT marked as MARVIN internal"""
            logger.info("=" * 80)
            logger.info("🔄 Fixing Sources Configuration")
            logger.info("=" * 80)

            if not self.sources_config.exists():
                logger.error(f"❌ Sources config not found: {self.sources_config}")
                return {"success": False, "error": "Config file not found"}

            with open(self.sources_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            fixed = []

            for source in config.get("sources", []):
                source_id = source.get("source_id")
                source_type = source.get("source_type")

                # Filesystems should NOT be MARVIN internal (they're separate)
                if source_id == "filesystems":
                    if "marvin" in str(source.get("metadata", {})).lower():
                        source["metadata"] = source.get("metadata", {})
                        if "tags" in source["metadata"]:
                            source["metadata"]["tags"] = [t for t in source["metadata"]["tags"] if t != "#marvin"]
                        fixed.append("filesystems: Removed MARVIN tag")
                        logger.info(f"  ✅ Fixed: {source.get('source_name')} - Removed MARVIN association")

            # Add communication apps source if not exists
            comm_apps_id = "communication_apps"
            existing_comm_apps = any(s.get("source_id") == comm_apps_id for s in config.get("sources", []))

            if not existing_comm_apps:
                comm_apps_source = {
                    "source_id": comm_apps_id,
                    "source_type": "internal",
                    "source_name": "Communication Apps",
                    "source_category": "communication",
                    "enabled": True,
                    "priority": 2,
                    "schedule_interval_hours": 6,
                    "last_syphon": None,
                    "metadata": {
                        "description": "Communication apps (Discord, Slack, Teams, etc.) - internal",
                        "marvin_task": "marvin_communication_apps_intelligence",
                        "tags": ["#internal", "#communication", "#apps", "#marvin"]
                    }
                }
                config["sources"].append(comm_apps_source)
                fixed.append("communication_apps: Added")
                logger.info(f"  ✅ Added: Communication Apps source")

            # Add SMS/Messaging source (placeholder, disabled)
            sms_id = "sms_messaging"
            existing_sms = any(s.get("source_id") == sms_id for s in config.get("sources", []))

            if not existing_sms:
                sms_source = {
                    "source_id": sms_id,
                    "source_type": "internal",
                    "source_name": "SMS/Messaging",
                    "source_category": "communication",
                    "enabled": False,  # Not set up yet
                    "priority": 3,
                    "schedule_interval_hours": 6,
                    "last_syphon": None,
                    "metadata": {
                        "description": "SMS and messaging intelligence - internal (not set up yet)",
                        "marvin_task": "marvin_sms_messaging_intelligence",
                        "tags": ["#internal", "#sms", "#messaging", "#marvin", "#not_setup"]
                    }
                }
                config["sources"].append(sms_source)
                fixed.append("sms_messaging: Added (placeholder)")
                logger.info(f"  ✅ Added: SMS/Messaging source (placeholder, disabled)")

            # Save updated config
            if fixed:
                with open(self.sources_config, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Fixed sources configuration: {len(fixed)} changes")
            else:
                logger.info("ℹ️  No changes needed")

            return {
                "success": True,
                "changes": fixed
            }

        except Exception as e:
            self.logger.error(f"Error in fix_sources_config: {e}", exc_info=True)
            raise
    def fix_cron_sweeps(self) -> Dict[str, Any]:
        try:
            """Fix MARVIN cron sweeps - remove filesystem, add communication apps"""
            logger.info("=" * 80)
            logger.info("📅 Fixing MARVIN Cron Sweeps")
            logger.info("=" * 80)

            if not self.cron_file.exists():
                logger.error(f"❌ Cron file not found: {self.cron_file}")
                return {"success": False, "error": "Cron file not found"}

            with open(self.cron_file, 'r', encoding='utf-8') as f:
                cron_content = f.read()

            lines = cron_content.split('\n')
            new_lines = []
            removed = []
            added = []

            i = 0
            while i < len(lines):
                line = lines[i]

                # Remove filesystem intelligence sweep
                if "marvin_filesystem_intelligence" in line.lower() or ("filesystem" in line.lower() and "marvin" in line.lower()):
                    removed.append("Filesystem Intelligence sweep")
                    logger.info(f"  ⚠️  Removing: Filesystem Intelligence sweep")
                    # Skip this line and any comment lines before it
                    while i < len(lines) and (lines[i].strip().startswith('#') or "filesystem" in lines[i].lower()):
                        i += 1
                    continue

                # Remove internal APIs sweep (not communication)
                if "marvin_internal_apis" in line.lower():
                    removed.append("Internal APIs sweep")
                    logger.info(f"  ⚠️  Removing: Internal APIs sweep")
                    # Skip this line and any comment lines before it
                    while i < len(lines) and (lines[i].strip().startswith('#') or "internal_apis" in lines[i].lower()):
                        i += 1
                    continue

                new_lines.append(line)
                i += 1

            # Add communication apps sweep
            nas_python = "/volume1/@appstore/python3/bin/python3"
            nas_project = "/volume1/docker/jarvis/.lumina"
            nas_logs = f"{nas_project}/data/syphon_scheduled/logs"

            comm_apps_sweep = f"""
# MARVIN Communication Apps Intelligence - Every 6 hours
0 */6 * * * {nas_python} {nas_project}/scripts/python/syphon_system.py --internal --communication-apps >> {nas_logs}/marvin_communication_apps.log 2>&1
"""

            # Find where to insert (after N8N sweep)
            insert_index = len(new_lines)
            for idx, line in enumerate(new_lines):
                if "marvin_n8n_intelligence" in line.lower():
                    insert_index = idx + 1
                    break

            new_lines.insert(insert_index, comm_apps_sweep.strip())
            added.append("Communication Apps sweep")
            logger.info(f"  ✅ Added: Communication Apps sweep")

            # Save updated cron
            updated_content = '\n'.join(new_lines)

            # Backup
            backup_file = self.cron_file.with_suffix('.backup_marvin_fix')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(cron_content)
            logger.info(f"  ✅ Created backup: {backup_file.name}")

            # Write updated
            with open(self.cron_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info(f"✅ Fixed MARVIN cron sweeps")
            logger.info(f"  • Removed: {len(removed)} non-communication sweeps")
            logger.info(f"  • Added: {len(added)} communication sweeps")

            return {
                "success": True,
                "removed": removed,
                "added": added
            }
        except Exception as e:
            logger.error(f"❌ Error fixing MARVIN cron sweeps: {e}")
            return {"success": False, "error": str(e)}

    def fix_all(self) -> Dict[str, Any]:
        """Fix all MARVIN internal sources"""
        logger.info("=" * 80)
        logger.info("🔧 FIXING MARVIN INTERNAL SOURCES")
        logger.info("=" * 80)
        logger.info("")
        logger.info("MARVIN Internal = Communication Sources Only:")
        logger.info("  • Email (Gmail, ProtonMail, NAS Email Hub)")
        logger.info("  • N8N on NAS (anything coming through N8N)")
        logger.info("  • SMS/Messaging (when set up)")
        logger.info("  • Communication Apps")
        logger.info("")
        logger.info("NOT Internal for MARVIN:")
        logger.info("  • Filesystems (separate)")
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "tasks": {},
            "sources": {},
            "cron": {}
        }

        # 1. Fix MARVIN tasks
        results["tasks"] = self.fix_marvin_tasks()
        logger.info("")

        # 2. Fix sources config
        results["sources"] = self.fix_sources_config()
        logger.info("")

        # 3. Fix cron sweeps
        results["cron"] = self.fix_cron_sweeps()
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ MARVIN FIX COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 SUMMARY:")
        logger.info(f"  • MARVIN Tasks: {results['tasks'].get('tasks_after', 0)} communication tasks")
        logger.info(f"  • Sources Fixed: {len(results['sources'].get('changes', []))} changes")
        logger.info(f"  • Cron Sweeps: Removed {len(results['cron'].get('removed', []))}, Added {len(results['cron'].get('added', []))}")
        logger.info("")
        logger.info("🎯 MARVIN Scope (Corrected):")
        logger.info("  ✅ Email, N8N, SMS (when ready), Communication Apps")
        logger.info("  ❌ NOT Filesystems (separate system)")
        logger.info("")

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Fix MARVIN Internal Sources - Communication & N8N Only"
        )
        parser.add_argument("--tasks-only", action="store_true", help="Fix tasks only")
        parser.add_argument("--sources-only", action="store_true", help="Fix sources only")
        parser.add_argument("--cron-only", action="store_true", help="Fix cron only")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        fixer = MarvinInternalSourcesFixer()

        if args.tasks_only:
            result = fixer.fix_marvin_tasks()
        elif args.sources_only:
            result = fixer.fix_sources_config()
        elif args.cron_only:
            result = fixer.fix_cron_sweeps()
        else:
            result = fixer.fix_all()

        if args.json:
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()