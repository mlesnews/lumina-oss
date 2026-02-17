#!/usr/bin/env python3
"""
Enhance SYPHON Sources, HK-47 Intelligence Retrieval, and NAS Sweeps

Adds:
1. YouTube and white paper sources to SYPHON configuration
2. HK-47 intelligence retrieval tasks
3. SYPHON sweeps to NAS cron schedule

Tags: #SYPHON #HK47 #NAS #SWEEPS #ENHANCEMENT @JARVIS @LUMINA
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

logger = get_logger("EnhanceSyphonHK47Sweeps")


class SyphonHK47SweepsEnhancer:
    """Enhance SYPHON sources, HK-47 tasks, and NAS sweeps"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.config_file = self.project_root / "config" / "syphon_scheduled_sources.json"
        self.cron_file = self.project_root / "scripts" / "nas_cron" / "jarvis_crontab"

    def add_youtube_white_paper_sources(self) -> Dict[str, Any]:
        try:
            """Add YouTube and white paper sources to SYPHON configuration"""
            logger.info("=" * 80)
            logger.info("📊 Adding YouTube and White Paper Sources to SYPHON")
            logger.info("=" * 80)

            # Load existing config
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            else:
                config = {"sources": []}

            existing_source_ids = {s.get("source_id") for s in config.get("sources", [])}

            # New sources to add
            new_sources = [
                {
                    "source_id": "youtube_videos",
                    "source_type": "external",
                    "source_name": "YouTube Videos",
                    "source_category": "video",
                    "enabled": True,
                    "priority": 4,
                    "schedule_interval_hours": 12,
                    "last_syphon": None,
                    "metadata": {
                        "description": "YouTube video intelligence gathering - external",
                        "script": "scripts/python/jarvis_syphon_youtube_financial_creators.py",
                        "hk47_task": "hk47_youtube_intelligence_retrieval",
                        "tags": ["#external", "#youtube", "#video", "#intelligence"]
                    }
                },
                {
                    "source_id": "youtube_channels",
                    "source_type": "external",
                    "source_name": "YouTube Channels",
                    "source_category": "video",
                    "enabled": True,
                    "priority": 4,
                    "schedule_interval_hours": 24,
                    "last_syphon": None,
                    "metadata": {
                        "description": "YouTube channel monitoring and intelligence - external",
                        "script": "scripts/python/ingest_youtube_channel_syphon.py",
                        "hk47_task": "hk47_youtube_channel_intelligence",
                        "tags": ["#external", "#youtube", "#channel", "#intelligence"]
                    }
                },
                {
                    "source_id": "white_papers",
                    "source_type": "external",
                    "source_name": "White Papers & Documents",
                    "source_category": "document",
                    "enabled": True,
                    "priority": 5,
                    "schedule_interval_hours": 24,
                    "last_syphon": None,
                    "metadata": {
                        "description": "White papers, research papers, and document intelligence - external",
                        "script": "scripts/python/jarvis_syphon_complete_web_extraction.py",
                        "hk47_task": "hk47_white_paper_intelligence_retrieval",
                        "tags": ["#external", "#whitepaper", "#document", "#research", "#intelligence"]
                    }
                },
                {
                    "source_id": "external_apis",
                    "source_type": "external",
                    "source_name": "External APIs & Services",
                    "source_category": "api",
                    "enabled": True,
                    "priority": 6,
                    "schedule_interval_hours": 24,
                    "last_syphon": None,
                    "metadata": {
                        "description": "External APIs and services intelligence gathering - external",
                        "script": "scripts/python/syphon_system.py",
                        "hk47_task": "hk47_external_api_intelligence",
                        "tags": ["#external", "#api", "#services", "#intelligence"]
                    }
                }
            ]

            added_sources = []
            for source in new_sources:
                if source["source_id"] not in existing_source_ids:
                    config["sources"].append(source)
                    added_sources.append(source["source_id"])
                    logger.info(f"  ✅ Added source: {source['source_name']} ({source['source_id']})")
                else:
                    logger.info(f"  ⚠️  Source already exists: {source['source_id']}")

            # Save updated config
            if added_sources:
                with open(self.config_file, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Added {len(added_sources)} new sources to SYPHON configuration")
            else:
                logger.info("ℹ️  No new sources to add")

            return {
                "success": True,
                "added_sources": added_sources,
                "total_sources": len(config.get("sources", []))
            }

        except Exception as e:
            self.logger.error(f"Error in add_youtube_white_paper_sources: {e}", exc_info=True)
            raise
    def add_syphon_sweeps_to_cron(self) -> Dict[str, Any]:
        try:
            """Add SYPHON sweeps to NAS cron schedule"""
            logger.info("=" * 80)
            logger.info("📅 Adding SYPHON Sweeps to NAS Cron Schedule")
            logger.info("=" * 80)

            if not self.cron_file.exists():
                logger.error(f"❌ Cron file not found: {self.cron_file}")
                return {"success": False, "error": "Cron file not found"}

            # Read existing cron file
            with open(self.cron_file, 'r', encoding='utf-8') as f:
                cron_content = f.read()

            # Check if SYPHON sweeps already exist
            if "syphon_scheduled_daemon_nas_kron.py" in cron_content:
                logger.info("  ⚠️  SYPHON sweeps already in cron file")
                return {"success": True, "message": "SYPHON sweeps already scheduled"}

            # NAS paths
            nas_python = "/volume1/@appstore/python3/bin/python3"
            nas_project = "/volume1/docker/jarvis/.lumina"
            nas_logs = f"{nas_project}/data/syphon_scheduled/logs"

            # New SYPHON sweep entries
            syphon_sweeps = f"""
# SYPHON Scheduled Daemon - Intelligence Gathering Sweeps
# Runs every 6 hours to SYPHON external sources (YouTube, white papers, etc.)
# HK-47 tasked with intelligence retrieval
0 */6 * * * {nas_python} {nas_project}/scripts/python/syphon_scheduled_daemon_nas_kron.py --cycle >> {nas_logs}/syphon_scheduled.log 2>&1

# SYPHON YouTube Intelligence - Daily
# HK-47 retrieves YouTube video and channel intelligence
0 2 * * * {nas_python} {nas_project}/scripts/python/jarvis_syphon_youtube_financial_creators.py >> {nas_logs}/syphon_youtube.log 2>&1

# SYPHON YouTube Channel Intelligence - Daily
0 3 * * * {nas_python} {nas_project}/scripts/python/ingest_youtube_channel_syphon.py >> {nas_logs}/syphon_youtube_channels.log 2>&1

# SYPHON White Papers & Documents - Daily
# HK-47 retrieves white papers and research documents
0 4 * * * {nas_python} {nas_project}/scripts/python/jarvis_syphon_complete_web_extraction.py >> {nas_logs}/syphon_whitepapers.log 2>&1

# SYPHON External APIs - Daily
0 5 * * * {nas_python} {nas_project}/scripts/python/syphon_system.py --external >> {nas_logs}/syphon_external_apis.log 2>&1
"""

            # Append to cron file
            updated_content = cron_content.rstrip() + "\n" + syphon_sweeps

            # Backup original
            backup_file = self.cron_file.with_suffix('.backup')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(cron_content)
            logger.info(f"  ✅ Created backup: {backup_file.name}")

            # Write updated cron file
            with open(self.cron_file, 'w', encoding='utf-8') as f:
                f.write(updated_content)

            logger.info("✅ Added SYPHON sweeps to NAS cron schedule")
            logger.info("  • SYPHON Scheduled Daemon: Every 6 hours")
            logger.info("  • YouTube Intelligence: Daily at 02:00")
            logger.info("  • YouTube Channels: Daily at 03:00")
            logger.info("  • White Papers: Daily at 04:00")
            logger.info("  • External APIs: Daily at 05:00")

            return {
                "success": True,
                "sweeps_added": 5,
                "backup_created": str(backup_file)
            }
        except Exception as e:
            logger.error(f"❌ Error adding SYPHON sweeps: {e}")
            return {"success": False, "error": str(e)}

    def create_hk47_intelligence_retrieval_task(self) -> Dict[str, Any]:
        try:
            """Create HK-47 intelligence retrieval task configuration"""
            logger.info("=" * 80)
            logger.info("🔫 Creating HK-47 Intelligence Retrieval Task")
            logger.info("=" * 80)

            task_file = self.project_root / "config" / "hk47_intelligence_tasks.json"

            tasks = {
                "timestamp": datetime.now().isoformat(),
                "description": "HK-47 Intelligence Retrieval Tasks - SYPHON External Sources",
                "tasks": [
                    {
                        "task_id": "hk47_youtube_intelligence",
                        "name": "YouTube Intelligence Retrieval",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/hk47_get_watch_history.py",
                        "syphon_source": "youtube_videos",
                        "description": "HK-47 retrieves YouTube video intelligence via SYPHON",
                        "hk47_statement": "Statement: Acquiring YouTube intelligence, master. Observation: Video data required for actionable intelligence. Query: Shall we extract video intelligence? Conclusion: Yes, master. We shall acquire the data."
                    },
                    {
                        "task_id": "hk47_youtube_channels",
                        "name": "YouTube Channel Intelligence",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/ingest_youtube_channel_syphon.py",
                        "syphon_source": "youtube_channels",
                        "description": "HK-47 monitors YouTube channels for intelligence",
                        "hk47_statement": "Statement: Monitoring YouTube channels, master. Observation: Channel data provides ongoing intelligence. Conclusion: Yes, master. We shall monitor the channels."
                    },
                    {
                        "task_id": "hk47_white_paper_intelligence",
                        "name": "White Paper Intelligence Retrieval",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/jarvis_syphon_complete_web_extraction.py",
                        "syphon_source": "white_papers",
                        "description": "HK-47 retrieves white papers and research documents",
                        "hk47_statement": "Statement: Acquiring white paper intelligence, master. Observation: Research documents contain valuable intelligence. Query: Shall we extract document intelligence? Conclusion: Yes, master. We shall acquire the documents."
                    },
                    {
                        "task_id": "hk47_external_api_intelligence",
                        "name": "External API Intelligence",
                        "enabled": True,
                        "schedule": "daily",
                        "script": "scripts/python/syphon_system.py",
                        "syphon_source": "external_apis",
                        "description": "HK-47 retrieves intelligence from external APIs",
                        "hk47_statement": "Statement: Acquiring external API intelligence, master. Observation: API data provides real-time intelligence. Conclusion: Yes, master. We shall query the APIs."
                    }
                ]
            }

            # Save task configuration
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(tasks, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Created HK-47 intelligence retrieval tasks: {task_file}")
            logger.info(f"  • {len(tasks['tasks'])} tasks configured")

            return {
                "success": True,
                "tasks_created": len(tasks["tasks"]),
                "task_file": str(task_file.relative_to(self.project_root))
            }

        except Exception as e:
            self.logger.error(f"Error in create_hk47_intelligence_retrieval_task: {e}", exc_info=True)
            raise
    def enhance_all(self) -> Dict[str, Any]:
        """Enhance all systems"""
        logger.info("=" * 80)
        logger.info("🚀 ENHANCING SYPHON / HK-47 / NAS SWEEPS")
        logger.info("=" * 80)
        logger.info("")

        results = {
            "timestamp": datetime.now().isoformat(),
            "sources": {},
            "cron": {},
            "hk47": {}
        }

        # 1. Add YouTube and white paper sources
        results["sources"] = self.add_youtube_white_paper_sources()
        logger.info("")

        # 2. Add SYPHON sweeps to cron
        results["cron"] = self.add_syphon_sweeps_to_cron()
        logger.info("")

        # 3. Create HK-47 intelligence tasks
        results["hk47"] = self.create_hk47_intelligence_retrieval_task()
        logger.info("")

        logger.info("=" * 80)
        logger.info("✅ ENHANCEMENT COMPLETE")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 SUMMARY:")
        logger.info(f"  • SYPHON Sources: {results['sources'].get('total_sources', 0)} total")
        logger.info(f"  • NAS Sweeps: {results['cron'].get('sweeps_added', 0)} sweeps added")
        logger.info(f"  • HK-47 Tasks: {results['hk47'].get('tasks_created', 0)} tasks created")
        logger.info("")
        logger.info("💡 NEXT STEPS:")
        logger.info("  1. Review the updated SYPHON sources configuration")
        logger.info("  2. Deploy the updated cron file to NAS")
        logger.info("  3. Verify sweeps are running: python scripts/python/verify_nas_cron_tasks.py")
        logger.info("  4. Check logs: data/syphon_scheduled/logs/")
        logger.info("")

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Enhance SYPHON Sources, HK-47 Tasks, and NAS Sweeps"
        )
        parser.add_argument("--sources-only", action="store_true", help="Add sources only")
        parser.add_argument("--cron-only", action="store_true", help="Add cron sweeps only")
        parser.add_argument("--hk47-only", action="store_true", help="Create HK-47 tasks only")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        enhancer = SyphonHK47SweepsEnhancer()

        if args.sources_only:
            result = enhancer.add_youtube_white_paper_sources()
        elif args.cron_only:
            result = enhancer.add_syphon_sweeps_to_cron()
        elif args.hk47_only:
            result = enhancer.create_hk47_intelligence_retrieval_task()
        else:
            result = enhancer.enhance_all()

        if args.json:
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()