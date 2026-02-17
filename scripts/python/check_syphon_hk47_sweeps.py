#!/usr/bin/env python3
"""
Check SYPHON Sources, HK-47 Intelligence Retrieval, and NAS Sweeps Status

This script checks:
1. SYPHON external sources (YouTube, white papers, etc.)
2. HK-47 intelligence retrieval tasks
3. NAS sweep schedules and status
4. Whether sweeps are actually running

Tags: #SYPHON #HK47 #NAS #SWEEPS #INTELLIGENCE #VERIFICATION @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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

logger = get_logger("SyphonHK47SweepsCheck")


class SyphonHK47SweepsChecker:
    """Check SYPHON sources, HK-47 tasks, and NAS sweeps"""

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "syphon_scheduled"
        self.logs_dir = self.data_dir / "logs" if self.data_dir.exists() else None

    def check_syphon_sources(self) -> Dict[str, Any]:
        """Check SYPHON external sources configuration"""
        logger.info("=" * 80)
        logger.info("🔍 Checking SYPHON External Sources")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "sources": [],
            "youtube_sources": [],
            "white_paper_sources": [],
            "video_sources": [],
            "total_sources": 0,
            "enabled_sources": 0
        }

        # Check scheduled sources config
        config_file = self.project_root / "config" / "syphon_scheduled_sources.json"
        if config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)

                sources = config.get("sources", [])
                result["total_sources"] = len(sources)
                result["enabled_sources"] = len([s for s in sources if s.get("enabled", True)])

                for source in sources:
                    source_info = {
                        "id": source.get("source_id"),
                        "name": source.get("source_name"),
                        "type": source.get("source_type"),
                        "category": source.get("source_category"),
                        "enabled": source.get("enabled", True),
                        "priority": source.get("priority"),
                        "interval_hours": source.get("schedule_interval_hours"),
                        "last_syphon": source.get("last_syphon"),
                        "metadata": source.get("metadata", {})
                    }
                    result["sources"].append(source_info)

                    # Categorize sources
                    name_lower = source_info["name"].lower()
                    if "youtube" in name_lower or "video" in name_lower:
                        result["youtube_sources"].append(source_info)
                    if "white" in name_lower and "paper" in name_lower:
                        result["white_paper_sources"].append(source_info)
                    if "video" in name_lower:
                        result["video_sources"].append(source_info)

                logger.info(f"✅ Found {result['total_sources']} SYPHON sources ({result['enabled_sources']} enabled)")

            except Exception as e:
                logger.error(f"❌ Error reading SYPHON sources config: {e}")
                result["error"] = str(e)
        else:
            logger.warning("⚠️  SYPHON sources config file not found")
            result["error"] = "Config file not found"

        # Check for YouTube-specific SYPHON scripts
        youtube_scripts = list(self.project_root.glob("**/*youtube*syphon*.py"))
        if youtube_scripts:
            result["youtube_scripts"] = [str(s.relative_to(self.project_root)) for s in youtube_scripts]
            logger.info(f"✅ Found {len(youtube_scripts)} YouTube SYPHON scripts")

        # Check for white paper/document SYPHON scripts
        doc_scripts = list(self.project_root.glob("**/*document*syphon*.py"))
        doc_scripts.extend(list(self.project_root.glob("**/*paper*syphon*.py")))
        if doc_scripts:
            result["document_scripts"] = [str(s.relative_to(self.project_root)) for s in doc_scripts]
            logger.info(f"✅ Found {len(doc_scripts)} document/paper SYPHON scripts")

        return result

    def check_hk47_intelligence_tasks(self) -> Dict[str, Any]:
        """Check HK-47 intelligence retrieval tasks"""
        logger.info("=" * 80)
        logger.info("🔫 Checking HK-47 Intelligence Retrieval Tasks")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "hk47_scripts": [],
            "intelligence_tasks": [],
            "youtube_tasks": [],
            "retrieval_tasks": []
        }

        # Find HK-47 scripts
        hk47_scripts = list(self.project_root.glob("**/hk47*.py"))
        for script in hk47_scripts:
            script_info = {
                "path": str(script.relative_to(self.project_root)),
                "name": script.name
            }
            result["hk47_scripts"].append(script_info)

            # Check if it's an intelligence retrieval script
            try:
                content = script.read_text(encoding='utf-8', errors='ignore')
                if "intelligence" in content.lower() or "retrieve" in content.lower():
                    script_info["is_intelligence"] = True
                    result["intelligence_tasks"].append(script_info)
                if "youtube" in content.lower():
                    script_info["is_youtube"] = True
                    result["youtube_tasks"].append(script_info)
                if "retrieve" in content.lower() or "fetch" in content.lower():
                    script_info["is_retrieval"] = True
                    result["retrieval_tasks"].append(script_info)
            except:
                pass

        logger.info(f"✅ Found {len(result['hk47_scripts'])} HK-47 scripts")
        logger.info(f"   Intelligence tasks: {len(result['intelligence_tasks'])}")
        logger.info(f"   YouTube tasks: {len(result['youtube_tasks'])}")
        logger.info(f"   Retrieval tasks: {len(result['retrieval_tasks'])}")

        # Check HK-47 integration for intelligence retrieval
        hk47_integration = self.project_root / "scripts" / "python" / "hk47_integration.py"
        if hk47_integration.exists():
            result["hk47_integration_available"] = True
            logger.info("✅ HK-47 Integration available")
        else:
            result["hk47_integration_available"] = False
            logger.warning("⚠️  HK-47 Integration not found")

        return result

    def check_nas_sweeps(self) -> Dict[str, Any]:
        """Check NAS sweep schedules and status"""
        logger.info("=" * 80)
        logger.info("📅 Checking NAS Sweep Schedules")
        logger.info("=" * 80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "cron_file_exists": False,
            "cron_file_path": None,
            "scheduled_sweeps": [],
            "syphon_sweeps": [],
            "log_files": [],
            "recent_logs": []
        }

        # Check cron file
        cron_file = self.project_root / "scripts" / "nas_cron" / "jarvis_crontab"
        if cron_file.exists():
            result["cron_file_exists"] = True
            result["cron_file_path"] = str(cron_file.relative_to(self.project_root))

            try:
                content = cron_file.read_text(encoding='utf-8')
                lines = content.split('\n')

                # Find SYPHON-related cron entries
                for line in lines:
                    if 'syphon' in line.lower() or 'SYPHON' in line:
                        if not line.strip().startswith('#'):
                            result["syphon_sweeps"].append(line.strip())
                            result["scheduled_sweeps"].append({
                                "schedule": line.split()[0:5] if len(line.split()) >= 6 else [],
                                "command": ' '.join(line.split()[5:]) if len(line.split()) > 5 else line,
                                "type": "syphon"
                            })

                logger.info(f"✅ Found {len(result['syphon_sweeps'])} SYPHON sweeps in cron file")

            except Exception as e:
                logger.error(f"❌ Error reading cron file: {e}")
                result["error"] = str(e)
        else:
            logger.warning("⚠️  Cron file not found")

        # Check for scheduled daemon
        daemon_file = self.project_root / "scripts" / "python" / "syphon_scheduled_daemon_nas_kron.py"
        if daemon_file.exists():
            result["daemon_available"] = True
            logger.info("✅ SYPHON Scheduled Daemon available")
        else:
            result["daemon_available"] = False
            logger.warning("⚠️  SYPHON Scheduled Daemon not found")

        # Check log files
        if self.logs_dir and self.logs_dir.exists():
            log_files = list(self.logs_dir.glob("*.log"))
            result["log_files"] = [str(f.name) for f in log_files]

            # Check recent logs
            for log_file in log_files[:5]:  # Check last 5 log files
                try:
                    stat = log_file.stat()
                    mod_time = datetime.fromtimestamp(stat.st_mtime)
                    if (datetime.now() - mod_time).days < 7:  # Last 7 days
                        result["recent_logs"].append({
                            "file": log_file.name,
                            "modified": mod_time.isoformat(),
                            "size": stat.st_size
                        })
                except:
                    pass

            logger.info(f"✅ Found {len(result['log_files'])} log files")
            logger.info(f"   Recent logs (last 7 days): {len(result['recent_logs'])}")

        # Check for NAS verification script
        verify_script = self.project_root / "scripts" / "python" / "verify_nas_cron_tasks.py"
        if verify_script.exists():
            result["verification_script_available"] = True
            logger.info("✅ NAS Cron Verification script available")
        else:
            result["verification_script_available"] = False

        return result

    def get_full_status(self) -> Dict[str, Any]:
        """Get complete status report"""
        return {
            "timestamp": datetime.now().isoformat(),
            "syphon_sources": self.check_syphon_sources(),
            "hk47_tasks": self.check_hk47_intelligence_tasks(),
            "nas_sweeps": self.check_nas_sweeps()
        }

    def print_status(self, json_output: bool = False):
        try:
            """Print status report"""
            status = self.get_full_status()

            if json_output:
                print(json.dumps(status, indent=2, default=str))
            else:
                print("=" * 80)
                print("🔍 SYPHON / HK-47 / NAS SWEEPS STATUS REPORT")
                print("=" * 80)
                print(f"Generated: {status['timestamp']}")
                print()

                # SYPHON Sources
                syphon = status["syphon_sources"]
                print("📊 SYPHON EXTERNAL SOURCES")
                print("-" * 80)
                if "error" in syphon:
                    print(f"  ❌ Error: {syphon['error']}")
                else:
                    print(f"  Total Sources: {syphon['total_sources']}")
                    print(f"  Enabled Sources: {syphon['enabled_sources']}")
                    print(f"  YouTube Sources: {len(syphon['youtube_sources'])}")
                    print(f"  White Paper Sources: {len(syphon['white_paper_sources'])}")
                    print(f"  Video Sources: {len(syphon['video_sources'])}")

                    if syphon.get("youtube_scripts"):
                        print(f"\n  YouTube SYPHON Scripts:")
                        for script in syphon["youtube_scripts"][:5]:
                            print(f"    • {script}")

                print()

                # HK-47 Tasks
                hk47 = status["hk47_tasks"]
                print("🔫 HK-47 INTELLIGENCE RETRIEVAL")
                print("-" * 80)
                print(f"  HK-47 Scripts: {len(hk47['hk47_scripts'])}")
                print(f"  Intelligence Tasks: {len(hk47['intelligence_tasks'])}")
                print(f"  YouTube Tasks: {len(hk47['youtube_tasks'])}")
                print(f"  Retrieval Tasks: {len(hk47['retrieval_tasks'])}")

                if hk47.get("intelligence_tasks"):
                    print(f"\n  Intelligence Retrieval Scripts:")
                    for task in hk47["intelligence_tasks"][:5]:
                        print(f"    • {task['path']}")

                print()

                # NAS Sweeps
                sweeps = status["nas_sweeps"]
                print("📅 NAS SWEEP SCHEDULES")
                print("-" * 80)
                if sweeps.get("cron_file_exists"):
                    print(f"  ✅ Cron file exists: {sweeps['cron_file_path']}")
                    print(f"  SYPHON Sweeps Scheduled: {len(sweeps['syphon_sweeps'])}")

                    if sweeps.get("syphon_sweeps"):
                        print(f"\n  Scheduled SYPHON Sweeps:")
                        for i, sweep in enumerate(sweeps["syphon_sweeps"][:5], 1):
                            print(f"    {i}. {sweep[:100]}...")
                else:
                    print("  ⚠️  Cron file not found")

                if sweeps.get("daemon_available"):
                    print("  ✅ SYPHON Scheduled Daemon available")
                else:
                    print("  ⚠️  SYPHON Scheduled Daemon not found")

                if sweeps.get("recent_logs"):
                    print(f"\n  Recent Log Activity (last 7 days): {len(sweeps['recent_logs'])}")
                    for log in sweeps["recent_logs"][:3]:
                        print(f"    • {log['file']} (modified: {log['modified'][:10]})")

                print()
                print("=" * 80)
                print()
                print("💡 RECOMMENDATIONS:")
                print()

                # Generate recommendations
                recommendations = []

                if syphon.get("total_sources", 0) == 0:
                    recommendations.append("  ⚠️  No SYPHON sources configured - need to set up external sources")

                if len(syphon.get("youtube_sources", [])) == 0:
                    recommendations.append("  ⚠️  No YouTube sources configured - add YouTube intelligence gathering")

                if len(syphon.get("white_paper_sources", [])) == 0:
                    recommendations.append("  ⚠️  No white paper sources configured - add document intelligence gathering")

                if len(sweeps.get("syphon_sweeps", [])) == 0:
                    recommendations.append("  ⚠️  No SYPHON sweeps scheduled on NAS - need to deploy cron jobs")

                if not sweeps.get("recent_logs"):
                    recommendations.append("  ⚠️  No recent log activity - sweeps may not be running")

                if len(hk47.get("intelligence_tasks", [])) == 0:
                    recommendations.append("  ⚠️  No HK-47 intelligence retrieval tasks found - need to configure")

                if recommendations:
                    for rec in recommendations:
                        print(rec)
                else:
                    print("  ✅ All systems appear to be configured")

                print()


        except Exception as e:
            self.logger.error(f"Error in print_status: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(
            description="Check SYPHON Sources, HK-47 Tasks, and NAS Sweeps"
        )
        parser.add_argument("--json", action="store_true", help="JSON output")
        parser.add_argument("--syphon-only", action="store_true", help="Check SYPHON only")
        parser.add_argument("--hk47-only", action="store_true", help="Check HK-47 only")
        parser.add_argument("--sweeps-only", action="store_true", help="Check sweeps only")

        args = parser.parse_args()

        checker = SyphonHK47SweepsChecker()

        if args.syphon_only:
            result = checker.check_syphon_sources()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("📊 SYPHON Sources:")
                print(f"  Total: {result.get('total_sources', 0)}")
                print(f"  Enabled: {result.get('enabled_sources', 0)}")
        elif args.hk47_only:
            result = checker.check_hk47_intelligence_tasks()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("🔫 HK-47 Tasks:")
                print(f"  Intelligence Tasks: {len(result.get('intelligence_tasks', []))}")
        elif args.sweeps_only:
            result = checker.check_nas_sweeps()
            if args.json:
                print(json.dumps(result, indent=2, default=str))
            else:
                print("📅 NAS Sweeps:")
                print(f"  SYPHON Sweeps: {len(result.get('syphon_sweeps', []))}")
        else:
            checker.print_status(json_output=args.json)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()