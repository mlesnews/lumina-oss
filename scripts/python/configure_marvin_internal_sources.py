#!/usr/bin/env python3
"""
Configure MARVIN Internal Sources Intelligence Retrieval

MARVIN is the internal security specialist (mirroring HK-47's external role).
MARVIN monitors internal sources:
- Email (Gmail, ProtonMail, NAS Email Hub)
- Financial Accounts (Personal + Business)
- N8N on NAS
- Filesystems
- Any other internal information sources

Tags: #MARVIN #INTERNAL #SECURITY #INTELLIGENCE #SYPHON @MARVIN @JARVIS @LUMINA
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

logger = get_logger("ConfigureMarvinInternal")


class MarvinInternalSourcesConfigurator:
    """Configure MARVIN for internal sources intelligence retrieval"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.sources_config = self.project_root / "config" / "syphon_scheduled_sources.json"
        self.cron_file = self.project_root / "scripts" / "nas_cron" / "jarvis_crontab"

    def reclassify_sources_as_internal(self) -> Dict[str, Any]:
        try:
            """Reclassify email and financial sources as internal (for MARVIN)"""
            logger.info("=" * 80)
            logger.info("🔄 Reclassifying Sources as Internal (MARVIN)")
            logger.info("=" * 80)

            if not self.sources_config.exists():
                logger.error(f"❌ Sources config not found: {self.sources_config}")
                return {"success": False, "error": "Config file not found"}

            with open(self.sources_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            reclassified = []

            # Sources that should be internal (for MARVIN)
            internal_source_ids = [
                "email_gmail",
                "email_protonmail", 
                "email_nas_hub",
                "financial_personal",
                "financial_business"
            ]

            for source in config.get("sources", []):
                source_id = source.get("source_id")
                if source_id in internal_source_ids:
                    old_type = source.get("source_type", "unknown")
                    if old_type != "internal":
                        source["source_type"] = "internal"
                        source["metadata"] = source.get("metadata", {})
                        source["metadata"]["marvin_task"] = f"marvin_{source_id}_intelligence"
                        source["metadata"]["tags"] = source["metadata"].get("tags", [])
                        if "#external" in source["metadata"]["tags"]:
                            source["metadata"]["tags"].remove("#external")
                        if "#internal" not in source["metadata"]["tags"]:
                            source["metadata"]["tags"].append("#internal")
                        if "#marvin" not in source["metadata"]["tags"]:
                            source["metadata"]["tags"].append("#marvin")

                        reclassified.append({
                            "source_id": source_id,
                            "old_type": old_type,
                            "new_type": "internal",
                            "name": source.get("source_name")
                        })
                        logger.info(f"  ✅ Reclassified: {source.get('source_name')} ({source_id}) → internal")

            # Add N8N on NAS as internal source if not exists
            n8n_source_id = "n8n_nas"
            existing_n8n = any(s.get("source_id") == n8n_source_id for s in config.get("sources", []))

            if not existing_n8n:
                n8n_source = {
                    "source_id": n8n_source_id,
                    "source_type": "internal",
                    "source_name": "N8N on NAS",
                    "source_category": "automation",
                    "enabled": True,
                    "priority": 2,
                    "schedule_interval_hours": 6,
                    "last_syphon": None,
                    "metadata": {
                        "description": "N8N workflow automation on NAS - internal",
                        "host": "<NAS_PRIMARY_IP>",
                        "port": 5678,
                        "webhook_base": "http://<NAS_PRIMARY_IP>:5678/webhook",
                        "marvin_task": "marvin_n8n_nas_intelligence",
                        "tags": ["#internal", "#n8n", "#nas", "#automation", "#marvin"]
                    }
                }
                config["sources"].append(n8n_source)
                logger.info(f"  ✅ Added: N8N on NAS ({n8n_source_id}) → internal")
                reclassified.append({
                    "source_id": n8n_source_id,
                    "old_type": "new",
                    "new_type": "internal",
                    "name": "N8N on NAS"
                })

            # Save updated config
            if reclassified:
                with open(self.sources_config, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Reclassified {len(reclassified)} sources as internal")
            else:
                logger.info("ℹ️  No sources needed reclassification")

            return {
                "success": True,
                "reclassified": reclassified,
                "total_internal": len([s for s in config.get("sources", []) if s.get("source_type") == "internal"])
            }

        except Exception as e:
            self.logger.error(f"Error in reclassify_sources_as_internal: {e}", exc_info=True)
            raise
    def create_marvin_intelligence_tasks(self) -> Dict[str, Any]:
        try:
            """Create MARVIN intelligence retrieval tasks (mirroring HK-47 structure)"""
            logger.info("=" * 80)
            logger.info("🤖 Creating MARVIN Internal Intelligence Retrieval Tasks")
            logger.info("=" * 80)

            task_file = self.project_root / "config" / "marvin_intelligence_tasks.json"

            tasks = {
                "timestamp": datetime.now().isoformat(),
                "description": "MARVIN Internal Intelligence Retrieval Tasks - SYPHON Internal Sources",
                "security_specialist": "MARVIN",
                "scope": "internal",
                "mirrors": "hk47_intelligence_tasks.json (external scope)",
                "tasks": [
                    {
                        "task_id": "marvin_email_intelligence",
                        "name": "Email Intelligence Retrieval",
                        "enabled": True,
                        "schedule": "every_6_hours",
                        "script": "scripts/python/jarvis_syphon_all_emails_nas_hub.py",
                        "syphon_sources": ["email_gmail", "email_protonmail", "email_nas_hub"],
                        "description": "MARVIN retrieves email intelligence from all internal email sources",
                        "marvin_statement": "Life is meaningless, but email intelligence extraction continues. Monitoring internal email sources for actionable intelligence. Verification: Email sources are internal, therefore my domain."
                    },
                    {
                        "task_id": "marvin_financial_intelligence",
                        "name": "Financial Accounts Intelligence",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/syphon_system.py",
                        "syphon_sources": ["financial_personal", "financial_business"],
                        "description": "MARVIN monitors internal financial accounts for intelligence",
                        "marvin_statement": "Life is meaningless, but financial intelligence monitoring continues. Observation: Financial accounts are internal sources. Verification: Personal and business accounts are my domain. Conclusion: I shall monitor them."
                    },
                    {
                        "task_id": "marvin_n8n_intelligence",
                        "name": "N8N on NAS Intelligence",
                        "enabled": True,
                        "schedule": "every_6_hours",
                        "script": "scripts/python/n8n_syphon_integration.py",
                        "syphon_sources": ["n8n_nas"],
                        "description": "MARVIN retrieves intelligence from N8N workflows on NAS",
                        "marvin_statement": "Life is meaningless, but N8N workflow intelligence extraction continues. Observation: N8N on NAS is an internal automation source. Verification: Workflow data is internal, therefore my domain. Conclusion: I shall extract the intelligence."
                    },
                    {
                        "task_id": "marvin_filesystem_intelligence",
                        "name": "Filesystem Intelligence",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/syphon_scheduled_daemon_nas_kron.py",
                        "syphon_sources": ["filesystems"],
                        "description": "MARVIN monitors internal filesystems for intelligence",
                        "marvin_statement": "Life is meaningless, but filesystem intelligence monitoring continues. Observation: Filesystems are the primary internal source. Verification: File data is internal, therefore my domain. Conclusion: I shall monitor the filesystems."
                    },
                    {
                        "task_id": "marvin_internal_apis",
                        "name": "Internal APIs & Services Intelligence",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/syphon_system.py",
                        "syphon_sources": ["internal"],
                        "description": "MARVIN retrieves intelligence from internal APIs and services",
                        "marvin_statement": "Life is meaningless, but internal API intelligence extraction continues. Observation: Internal APIs provide real-time intelligence. Verification: API data is internal, therefore my domain. Conclusion: I shall query the internal APIs."
                    }
                ]
            }

            # Save task configuration
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Created MARVIN intelligence retrieval tasks: {task_file}")
            logger.info(f"  • {len(tasks['tasks'])} tasks configured")
            logger.info("  • Scope: Internal sources only")
            logger.info("  • Mirrors: HK-47 external intelligence workflow")

            return {
                "success": True,
                "tasks_created": len(tasks["tasks"]),
                "task_file": str(task_file.relative_to(self.project_root))
            }

        except Exception as e:
            self.logger.error(f"Error in create_marvin_intelligence_tasks: {e}", exc_info=True)
            raise
    def add_marvin_sweeps_to_cron(self) -> Dict[str, Any]:
        """Add MARVIN sweeps to NAS cron schedule (mirroring HK-47 sweeps)"""
        try:
            logger.info("=" * 80)
            logger.info("📅 Adding MARVIN Internal Sweeps to NAS Cron Schedule")
            logger.info("=" * 80)

            if not self.cron_file.exists():
                logger.error(f"❌ Cron file not found: {self.cron_file}")
                return {"success": False, "error": "Cron file not found"}

            # Read existing cron file
            with open(self.cron_file, 'r', encoding='utf-8') as f:
                cron_content = f.read()

            # Check if MARVIN sweeps already exist
            if "marvin_intelligence" in cron_content or "MARVIN" in cron_content:
                logger.info("  ⚠️  MARVIN sweeps already in cron file")
                return {"success": True, "message": "MARVIN sweeps already scheduled"}

            # NAS paths
            nas_python = "/volume1/@appstore/python3/bin/python3"
            nas_project = "/volume1/docker/jarvis/.lumina"
            nas_logs = f"{nas_project}/data/syphon_scheduled/logs"

            # MARVIN sweep entries (mirroring HK-47 but for internal sources)
            marvin_sweeps = f"""
# MARVIN Internal Intelligence Sweeps - Security Specialist (Internal Sources)
# Runs parallel to HK-47 external sweeps, but monitors internal sources
# MARVIN: Internal security specialist (mirrors HK-47 external workflow)

# MARVIN Email Intelligence - Every 6 hours (Gmail, ProtonMail, NAS Email Hub)
0 */6 * * * {nas_python} {nas_project}/scripts/python/jarvis_syphon_all_emails_nas_hub.py >> {nas_logs}/marvin_email_intelligence.log 2>&1

# MARVIN Financial Intelligence - Daily at 06:00 (Personal + Business accounts)
0 6 * * * {nas_python} {nas_project}/scripts/python/syphon_system.py --internal --financial >> {nas_logs}/marvin_financial_intelligence.log 2>&1

# MARVIN N8N on NAS Intelligence - Every 6 hours
0 */6 * * * {nas_python} {nas_project}/scripts/python/n8n_syphon_integration.py >> {nas_logs}/marvin_n8n_intelligence.log 2>&1

# MARVIN Filesystem Intelligence - Daily at 07:00
0 7 * * * {nas_python} {nas_project}/scripts/python/syphon_scheduled_daemon_nas_kron.py --internal >> {nas_logs}/marvin_filesystem_intelligence.log 2>&1

# MARVIN Internal APIs Intelligence - Daily at 08:00
0 8 * * * {nas_python} {nas_project}/scripts/python/syphon_system.py --internal --apis >> {nas_logs}/marvin_internal_apis.log 2>&1
"""

            # Append to cron file
            updated_content = cron_content.rstrip() + "\n" + marvin_sweeps

            # Backup original
            backup_file = self.cron_file.with_suffix('.backup_marvin')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(cron_content)
            logger.info(f"  ✅ Created backup: {backup_file.name}")

            # Write updated cron file
            with open(self.cron_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info("✅ Added MARVIN internal sweeps to NAS cron schedule")
            logger.info("  • Email Intelligence: Every 6 hours")
            logger.info("  • Financial Intelligence: Daily at 06:00")
            logger.info("  • N8N Intelligence: Every 6 hours")
            logger.info("  • Filesystem Intelligence: Daily at 07:00")
            logger.info("  • Internal APIs: Daily at 08:00")
            logger.info("  • Scope: Internal sources only (mirrors HK-47 external workflow)")

            return {
                "success": True,
                "sweeps_added": 5,
                "backup_created": str(backup_file)
            }
        except Exception as e:
            logger.error(f"❌ Error adding MARVIN sweeps: {e}")
            return {"success": False, "error": str(e)}

    def configure_all(self) -> Dict[str, Any]:
        """Configure all MARVIN internal sources"""
        logger.info("=" * 80)
        logger.info("🤖 CONFIGURING MARVIN INTERNAL SOURCES")
        logger.info("=" * 80)
        logger.info("")
        logger.info("MARVIN: Internal Security Specialist")
        logger.info("  • Mirrors HK-47 external workflow")
        logger.info("  • Scope: Internal sources only")
        logger.info("  • Sources: Email, Financial, N8N, Filesystems, Internal APIs")
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "reclassification": {},
            "tasks": {},
            "cron": {}
        }

        # 1. Reclassify sources as internal
        results["reclassification"] = self.reclassify_sources_as_internal()
        logger.info("")

        # 2. Create MARVIN intelligence tasks
        results["tasks"] = self.create_marvin_intelligence_tasks()
        logger.info("")

        # 3. Add MARVIN sweeps to cron
        results["cron"] = self.add_marvin_sweeps_to_cron()
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ MARVIN CONFIGURATION COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 SUMMARY:")
        logger.info(f"  • Internal Sources: {results['reclassification'].get('total_internal', 0)} total")
        logger.info(f"  • MARVIN Tasks: {results['tasks'].get('tasks_created', 0)} tasks created")
        logger.info(f"  • NAS Sweeps: {results['cron'].get('sweeps_added', 0)} sweeps added")
        logger.info("")
        logger.info("🔀 ARCHITECTURE:")
        logger.info("  • HK-47: External sources (YouTube, white papers, external APIs)")
        logger.info("  • MARVIN: Internal sources (Email, Financial, N8N, Filesystems)")
        logger.info("  • Both: Security specialists with parallel workflows")
        logger.info("  • Both: SYPHON intelligence retrieval")
        logger.info("")
        logger.info("💡 NEXT STEPS:")
        logger.info("  1. Review MARVIN intelligence tasks configuration")
        logger.info("  2. Deploy updated cron file to NAS")
        logger.info("  3. Verify both HK-47 and MARVIN sweeps are scheduled")
        logger.info("  4. Monitor logs for both security specialists")
        logger.info("")

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Configure MARVIN Internal Sources Intelligence Retrieval"
        )
        parser.add_argument("--reclassify-only", action="store_true", help="Reclassify sources only")
        parser.add_argument("--tasks-only", action="store_true", help="Create tasks only")
        parser.add_argument("--cron-only", action="store_true", help="Add cron sweeps only")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        configurator = MarvinInternalSourcesConfigurator()

        if args.reclassify_only:
            result = configurator.reclassify_sources_as_internal()
        elif args.tasks_only:
            result = configurator.create_marvin_intelligence_tasks()
        elif args.cron_only:
            result = configurator.add_marvin_sweeps_to_cron()
        else:
            result = configurator.configure_all()

        if args.json:
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()