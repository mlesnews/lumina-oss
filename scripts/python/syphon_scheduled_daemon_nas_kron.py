#!/usr/bin/env python3
"""
SYPHON Scheduled Daemon - NAS KronScheduler Integration

Regularly scheduled task daemon for @SYPHON'ing @sources (both #internal and #external)
via NAS KronScheduler (<SCHEDULER_HOSTNAME>).

Priority Order:
1. Filesystems (FIRST PRIORITY - #internal)
2. Email Sources (Gmail + ProtonMail - #external)
3. Financial Accounts (Personal + Business - #external)
4. External APIs and Services (#external)

#JARVIS #LUMINA #SYPHON #DAEMON #NAS #KRONSCHEDULER #INTERNAL #EXTERNAL
"""

import sys
import os
import json
import time
import signal
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("SyphonScheduledDaemon")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SyphonScheduledDaemon")

try:
    from scripts.python.lumina_comprehensive_syphon_system import LuminaComprehensiveSyphonSystem
    COMPREHENSIVE_SYPHON_AVAILABLE = True
except ImportError:
    COMPREHENSIVE_SYPHON_AVAILABLE = False
    LuminaComprehensiveSyphonSystem = None
    logger.warning("Comprehensive SYPHON system not available")

try:
    from scripts.python.unified_email_service import UnifiedEmailService
    EMAIL_SERVICE_AVAILABLE = True
except ImportError:
    EMAIL_SERVICE_AVAILABLE = False
    UnifiedEmailService = None

try:
    from scripts.python.nas_kron_daemon_manager import NASKronDaemonManager
    NAS_KRON_AVAILABLE = True
except ImportError:
    NAS_KRON_AVAILABLE = False
    NASKronDaemonManager = None

try:
    from scripts.python.integrate_hook_trace import hook_trace, OperationType, TraceLevel
    HOOK_TRACE_AVAILABLE = True
except ImportError:
    HOOK_TRACE_AVAILABLE = False
    OperationType = None
    TraceLevel = None
    hook_trace = None


@dataclass
class SyphonSourceConfig:
    """Configuration for a SYPHON source"""
    source_id: str
    source_type: str  # "internal" or "external"
    source_name: str
    source_category: str  # "filesystem", "email", "financial", "api"
    enabled: bool = True
    priority: int = 1  # 1 = highest
    schedule_interval_hours: int = 24
    last_syphon: Optional[str] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SyphonScheduledDaemon:
    """
    SYPHON Scheduled Daemon - NAS KronScheduler Integration

    Regularly scheduled task daemon for @SYPHON'ing @sources:
    - #internal sources (filesystems, local data)
    - #external sources (email, financial accounts, APIs)
    """

    def __init__(
        self,
        project_root: Path = None,
        nas_kron_host: str = "<SCHEDULER_HOSTNAME>",
        interval_hours: int = 24
    ):
        """
        Initialize SYPHON Scheduled Daemon.

        Args:
            project_root: Project root directory
            nas_kron_host: NAS KronScheduler hostname
            interval_hours: Default interval between runs (hours)
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.nas_kron_host = nas_kron_host
        self.interval_hours = interval_hours

        # Data directories
        self.data_dir = self.project_root / "data" / "syphon_scheduled"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.logs_dir = self.data_dir / "logs"
        self.logs_dir.mkdir(parents=True, exist_ok=True)

        self.results_dir = self.data_dir / "results"
        self.results_dir.mkdir(parents=True, exist_ok=True)

        # Initialize systems
        self.syphon_system = None
        if COMPREHENSIVE_SYPHON_AVAILABLE:
            try:
                self.syphon_system = LuminaComprehensiveSyphonSystem(self.project_root)
                logger.info("✅ Comprehensive SYPHON System initialized")
            except Exception as e:
                logger.warning(f"⚠️  Comprehensive SYPHON System not available: {e}")

        self.email_service = None
        if EMAIL_SERVICE_AVAILABLE:
            try:
                self.email_service = UnifiedEmailService(self.project_root)
                logger.info("✅ Unified Email Service initialized")
            except Exception as e:
                logger.warning(f"⚠️  Unified Email Service not available: {e}")

        self.nas_kron = None
        if NAS_KRON_AVAILABLE:
            try:
                self.nas_kron = NASKronDaemonManager(project_root=self.project_root)
                logger.info("✅ NAS Kron Daemon Manager initialized")
            except Exception as e:
                logger.warning(f"⚠️  NAS Kron Daemon Manager not available: {e}")

        # Load source configurations
        self.sources = self._load_source_configs()

        # Daemon state
        self.running = False
        self.pid_file = self.data_dir / "syphon_daemon.pid"

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logger.info("✅ SYPHON Scheduled Daemon initialized")
        logger.info(f"   NAS KronScheduler: {self.nas_kron_host}")
        logger.info(f"   Default Interval: {self.interval_hours} hours")

    def _load_source_configs(self) -> List[SyphonSourceConfig]:
        """Load SYPHON source configurations"""
        config_file = self.project_root / "config" / "syphon_scheduled_sources.json"

        if not config_file.exists():
            # Create default configuration
            default_sources = [
                {
                    "source_id": "filesystems",
                    "source_type": "internal",
                    "source_name": "Filesystems",
                    "source_category": "filesystem",
                    "enabled": True,
                    "priority": 1,
                    "schedule_interval_hours": 24,
                    "metadata": {
                    "description": "Internal filesystem sources - FIRST PRIORITY"
                }
                },
                {
                    "source_id": "email_gmail",
                    "source_type": "external",
                    "source_name": "Gmail",
                    "source_category": "email",
                    "enabled": True,
                    "priority": 2,
                    "schedule_interval_hours": 6,
                    "metadata": {
                        "description": "Gmail email source - external"
                    }
                },
                {
                    "source_id": "email_protonmail",
                    "source_type": "external",
                    "source_name": "ProtonMail",
                    "source_category": "email",
                    "enabled": True,
                    "priority": 2,
                    "schedule_interval_hours": 6,
                    "metadata": {
                        "description": "ProtonMail email source - external"
                    }
                },
                {
                    "source_id": "email_nas_hub",
                    "source_type": "external",
                    "source_name": "NAS Email Hub",
                    "source_category": "email",
                    "enabled": True,
                    "priority": 2,
                    "schedule_interval_hours": 5,
                    "metadata": {
                        "description": "NAS email hub (<EMAIL_HUB_HOSTNAME>) - external",
                        "host": "<EMAIL_HUB_HOSTNAME>"
                    }
                },
                {
                    "source_id": "financial_personal",
                    "source_type": "external",
                    "source_name": "Personal Financial Accounts",
                    "source_category": "financial",
                    "enabled": True,
                    "priority": 3,
                    "schedule_interval_hours": 24,
                    "metadata": {
                        "description": "Personal financial accounts - external"
                    }
                },
                {
                    "source_id": "financial_business",
                    "source_type": "external",
                    "source_name": "Business Financial Accounts",
                    "source_category": "financial",
                    "enabled": True,
                    "priority": 3,
                    "schedule_interval_hours": 24,
                    "metadata": {
                        "description": "Business financial accounts (<COMPANY>-FINANCIAL-SERVICES-LLC) - external",
                        "company": "<COMPANY>-FINANCIAL-SERVICES-LLC"
                    }
                }
            ]

            try:
                with open(config_file, 'w', encoding='utf-8') as f:
                    json.dump({"sources": default_sources}, f, indent=2, ensure_ascii=False)
                logger.info(f"✅ Created default source configuration: {config_file}")
            except Exception as e:
                logger.warning(f"⚠️  Failed to create default config: {e}")
                return []

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)

            sources = []
            for source_data in config.get("sources", []):
                sources.append(SyphonSourceConfig(**source_data))

            # Sort by priority
            sources.sort(key=lambda x: x.priority)

            logger.info(f"✅ Loaded {len(sources)} SYPHON source configurations")
            return sources

        except Exception as e:
            logger.error(f"❌ Error loading source configurations: {e}")
            return []

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"\nReceived signal {signum}, shutting down gracefully...")
        self.running = False

    def _save_pid(self):
        """Save daemon PID"""
        try:
            with open(self.pid_file, 'w') as f:
                f.write(str(os.getpid()))
        except Exception as e:
            logger.warning(f"⚠️  Failed to save PID: {e}")

    def _remove_pid(self):
        """Remove daemon PID file"""
        try:
            if self.pid_file.exists():
                self.pid_file.unlink()
        except Exception as e:
            logger.warning(f"⚠️  Failed to remove PID: {e}")

    def syphon_internal_sources(self) -> Dict[str, Any]:
        """
        SYPHON internal sources (#internal).

        Priority 1: Filesystems
        """
        logger.info("="*80)
        logger.info("🔍 SYPHON'ing INTERNAL Sources (#internal)")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source_type": "internal",
            "sources": [],
            "total_items": 0,
            "success": False
        }

        if not self.syphon_system:
            logger.error("❌ SYPHON System not available")
            result["error"] = "SYPHON System not available"
            return result

        try:
            # Get internal sources (filesystems)
            internal_sources = [s for s in self.sources if s.source_type == "internal" and s.enabled]

            for source in internal_sources:
                logger.info(f"🔍 SYPHON'ing {source.source_name} ({source.source_category})...")

                if source.source_category == "filesystem":
                    # Use comprehensive SYPHON system for filesystems
                    syphon_result = self.syphon_system.syphon_all(days_back=30)

                    if syphon_result:
                        filesystem_data = syphon_result.get("filesystems", {})
                        items = filesystem_data.get("total_sources", 0)

                        result["sources"].append({
                            "source_id": source.source_id,
                            "source_name": source.source_name,
                            "items": items,
                            "success": True
                        })
                        result["total_items"] += items

                        logger.info(f"✅ {source.source_name}: {items} items extracted")

                # Update last syphon time
                source.last_syphon = datetime.now().isoformat()

            result["success"] = True
            logger.info(f"✅ INTERNAL Sources SYPHON complete: {result['total_items']} total items")

        except Exception as e:
            logger.error(f"❌ Error SYPHON'ing internal sources: {e}", exc_info=True)
            result["error"] = str(e)

        return result

    def syphon_external_sources(self) -> Dict[str, Any]:
        """
        SYPHON external sources (#external).

        Priority 2: Email (Gmail, ProtonMail, NAS Email Hub)
        Priority 3: Financial Accounts (Personal + Business)
        """
        logger.info("="*80)
        logger.info("🔍 SYPHON'ing EXTERNAL Sources (#external)")
        logger.info("="*80)

        result = {
            "timestamp": datetime.now().isoformat(),
            "source_type": "external",
            "sources": [],
            "total_items": 0,
            "success": False
        }

        # Get external sources
        external_sources = [s for s in self.sources if s.source_type == "external" and s.enabled]
        external_sources.sort(key=lambda x: x.priority)

        # SYPHON email sources
        email_sources = [s for s in external_sources if s.source_category == "email"]
        for source in email_sources:
            logger.info(f"🔍 SYPHON'ing {source.source_name} (email - #external)...")

            try:
                if source.source_id == "email_nas_hub":
                    # NAS Email Hub - use N8N integration
                    items = self._syphon_nas_email_hub()
                elif self.email_service:
                    # Gmail or ProtonMail - use unified email service
                    items = self._syphon_email_source(source)
                else:
                    logger.warning(f"⚠️  Email service not available for {source.source_name}")
                    items = 0

                result["sources"].append({
                    "source_id": source.source_id,
                    "source_name": source.source_name,
                    "items": items,
                    "success": items > 0
                })
                result["total_items"] += items

                source.last_syphon = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"❌ Error SYPHON'ing {source.source_name}: {e}", exc_info=True)
                result["sources"].append({
                    "source_id": source.source_id,
                    "source_name": source.source_name,
                    "items": 0,
                    "success": False,
                    "error": str(e)
                })

        # SYPHON financial sources
        financial_sources = [s for s in external_sources if s.source_category == "financial"]
        for source in financial_sources:
            logger.info(f"🔍 SYPHON'ing {source.source_name} (financial - #external)...")

            try:
                if self.syphon_system:
                    syphon_result = self.syphon_system.syphon_all(days_back=30)
                    financial_data = syphon_result.get("financial", {})
                    items = financial_data.get("total_accounts", 0)
                else:
                    items = 0

                result["sources"].append({
                    "source_id": source.source_id,
                    "source_name": source.source_name,
                    "items": items,
                    "success": items > 0
                })
                result["total_items"] += items

                source.last_syphon = datetime.now().isoformat()

            except Exception as e:
                logger.error(f"❌ Error SYPHON'ing {source.source_name}: {e}", exc_info=True)
                result["sources"].append({
                    "source_id": source.source_id,
                    "source_name": source.source_name,
                    "items": 0,
                    "success": False,
                    "error": str(e)
                })

        result["success"] = True
        logger.info(f"✅ EXTERNAL Sources SYPHON complete: {result['total_items']} total items")

        return result

    def _syphon_nas_email_hub(self) -> int:
        """SYPHON NAS Email Hub via N8N"""
        logger.info("   📧 Checking NAS Email Hub (<EMAIL_HUB_HOSTNAME>)...")

        # Use N8N webhook to trigger email hub receive workflow
        try:
            import requests
            n8n_url = f"http://<NAS_PRIMARY_IP>:5678/webhook/email/hub/receive"

            response = requests.post(n8n_url, timeout=30)
            if response.status_code == 200:
                data = response.json()
                emails = data.get("emails", [])
                logger.info(f"   ✅ NAS Email Hub: {len(emails)} emails retrieved")
                return len(emails)
            else:
                logger.warning(f"   ⚠️  NAS Email Hub: HTTP {response.status_code}")
                return 0
        except Exception as e:
            logger.warning(f"   ⚠️  NAS Email Hub: {e}")
            return 0

    def _syphon_email_source(self, source: SyphonSourceConfig) -> int:
        """SYPHON email source (Gmail or ProtonMail)"""
        if not self.email_service:
            return 0

        try:
            # Search for recent emails
            if "gmail" in source.source_id.lower():
                provider = "gmail"
            elif "proton" in source.source_id.lower():
                provider = "protonmail"
            else:
                return 0

            # Search for emails from last 24 hours
            emails = self.email_service.search_emails(
                provider=provider,
                query="",
                days_back=1
            )

            logger.info(f"   ✅ {source.source_name}: {len(emails)} emails found")
            return len(emails)

        except Exception as e:
            logger.warning(f"   ⚠️  {source.source_name}: {e}")
            return 0

    def run_single_cycle(self) -> Dict[str, Any]:
        """
        Run a single SYPHON cycle.

        Priority Order:
        1. Internal sources (filesystems)
        2. External sources (email, financial)
        """
        logger.info("="*80)
        logger.info("🔄 SYPHON Scheduled Daemon - Single Cycle")
        logger.info("="*80)

        cycle_result = {
            "timestamp": datetime.now().isoformat(),
            "cycle_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "internal": {},
            "external": {},
            "success": False
        }

        try:
            # 1. SYPHON internal sources (FIRST PRIORITY)
            internal_result = self.syphon_internal_sources()
            cycle_result["internal"] = internal_result

            # 2. SYPHON external sources
            external_result = self.syphon_external_sources()
            cycle_result["external"] = external_result

            cycle_result["success"] = (
                internal_result.get("success", False) or
                external_result.get("success", False)
            )

            # Save cycle result
            result_file = self.results_dir / f"cycle_{cycle_result['cycle_id']}.json"
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(cycle_result, f, indent=2, ensure_ascii=False, default=str)

            logger.info("="*80)
            logger.info(f"✅ SYPHON Cycle Complete: {cycle_result['cycle_id']}")
            logger.info(f"   Internal: {internal_result.get('total_items', 0)} items")
            logger.info(f"   External: {external_result.get('total_items', 0)} items")
            logger.info("="*80)

            # Trace with hook & trace
            if HOOK_TRACE_AVAILABLE:
                hook_trace.trace(
                    operation_type=OperationType.SYPHON,
                    operation_name="syphon_scheduled_cycle",
                    level=TraceLevel.INFO,
                    message=f"SYPHON scheduled cycle complete: {cycle_result['cycle_id']}",
                    metadata={
                        "internal_items": internal_result.get("total_items", 0),
                        "external_items": external_result.get("total_items", 0),
                        "cycle_id": cycle_result["cycle_id"]
                    }
                )

        except Exception as e:
            logger.error(f"❌ Error in SYPHON cycle: {e}", exc_info=True)
            cycle_result["error"] = str(e)

        return cycle_result

    def run_daemon(self):
        """Run as continuous daemon"""
        self.running = True
        self._save_pid()

        logger.info("="*80)
        logger.info("🔄 SYPHON Scheduled Daemon - Continuous Mode")
        logger.info("="*80)
        logger.info(f"   NAS KronScheduler: {self.nas_kron_host}")
        logger.info(f"   Interval: {self.interval_hours} hours")
        logger.info(f"   PID: {os.getpid()}")
        logger.info(f"   PID File: {self.pid_file}")
        logger.info("")
        logger.info("   Sources:")
        logger.info("     #internal: Filesystems (Priority 1)")
        logger.info("     #external: Email, Financial Accounts (Priority 2-3)")
        logger.info("")
        logger.info("   Press Ctrl+C to stop.\n")

        last_run = datetime.now()
        cycle_count = 0

        try:
            while self.running:
                current_time = datetime.now()
                time_since_last = (current_time - last_run).total_seconds()
                interval_seconds = self.interval_hours * 3600

                if time_since_last >= interval_seconds:
                    cycle_count += 1
                    logger.info(f"\n[{current_time.strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"SYPHON Cycle #{cycle_count} - Starting...")

                    self.run_single_cycle()

                    last_run = current_time

                    # Save source configurations
                    self._save_source_configs()
                else:
                    # Sleep for a bit before checking again
                    time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("\nReceived keyboard interrupt, shutting down...")
        finally:
            self._remove_pid()
            logger.info("✅ SYPHON Scheduled Daemon stopped")

    def _save_source_configs(self):
        """Save source configurations"""
        config_file = self.project_root / "config" / "syphon_scheduled_sources.json"

        try:
            sources_data = [asdict(source) for source in self.sources]
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump({"sources": sources_data}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.warning(f"⚠️  Failed to save source configs: {e}")

    def create_nas_kron_cron_file(self) -> Path:
        """Create cron file for NAS KronScheduler"""
        logger.info("📅 Creating cron file for NAS KronScheduler...")

        # NAS paths (Synology DSM)
        nas_python = "/volume1/@appstore/python3/bin/python3"
        nas_project_root = "/volume1/homes/backupadm/Dropbox/my_projects/.lumina"
        nas_script = f"{nas_project_root}/scripts/python/syphon_scheduled_daemon_nas_kron.py"
        nas_log = f"{nas_project_root}/data/syphon_scheduled/logs/syphon_scheduled.log"

        # Create cron entry (runs every 4 hours - dynamic scaling 3-6h)
        cron_entry = f"""# SYPHON Scheduled Daemon - NAS KronScheduler
# Runs every 4 hours (dynamic scaling: 3-6 hours based on sweep duration)
# SYPHONs both #internal and #external sources
#
# Schedule: 0 */4 * * * (every 4 hours at minute 0)
# Runs at: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00
#
# Dynamic Scaling Notes:
# - If sweep takes >2 hours or has errors: scale up to 6 hours
# - If sweep completes quickly (<30 min) with good results: scale down to 3 hours
# - Scaling is handled by the daemon itself, not cron interval changes
#
# Current Coverage (Partial):
# - YouTube Videos & Channels (HK-47)
# - White Papers & Documents  
# - External APIs & Services
# - Communication Apps
#
# NOT YET IMPLEMENTED:
# - College/University white papers
# - Thesis papers (Masters, PhD)
# - Scientific journals, arXiv, PubMed
# - Scientific books and literature
#
# ============================================================================
# NAS Configuration (Synology DSM) - ACTIVE
# ============================================================================
0 */4 * * * {nas_python} {nas_script} --cycle --all-sources >> {nas_log} 2>&1
"""

        # Save cron file
        cron_file = self.data_dir / "syphon_scheduled.cron"
        with open(cron_file, 'w', encoding='utf-8') as f:
            f.write(cron_entry)

        logger.info(f"✅ Cron file created: {cron_file}")
        logger.info(f"   Schedule: Every 4 hours (dynamic scaling 3-6h)")
        logger.info(f"   NAS Python: {nas_python}")
        logger.info(f"   NAS Script: {nas_script}")

        return cron_file

    def deploy_to_nas_kron(self) -> bool:
        """Deploy to NAS KronScheduler"""
        if not self.nas_kron:
            logger.warning("⚠️  NAS Kron Daemon Manager not available")
            return False

        try:
            logger.info("📅 Deploying SYPHON Scheduled Daemon to NAS KronScheduler...")

            # Create cron file
            cron_file = self.create_nas_kron_cron_file()

            # Deploy to NAS
            if self.nas_kron.deploy_cron_to_nas(cron_file):
                logger.info("✅ SYPHON Scheduled Daemon deployed to NAS KronScheduler")
                logger.info(f"   Host: {self.nas_kron_host}")
                logger.info(f"   Schedule: Every 6 hours")
                return True
            else:
                logger.error("❌ Failed to deploy to NAS KronScheduler")
                return False

        except Exception as e:
            logger.error(f"❌ Error deploying to NAS KronScheduler: {e}", exc_info=True)
            return False


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="SYPHON Scheduled Daemon - NAS KronScheduler Integration"
    )
    parser.add_argument(
        "--cycle",
        action="store_true",
        help="Run single cycle (for cron execution)"
    )
    parser.add_argument(
        "--daemon",
        action="store_true",
        help="Run as continuous daemon"
    )
    parser.add_argument(
        "--deploy",
        action="store_true",
        help="Deploy to NAS KronScheduler"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=24,
        help="Interval between cycles (hours, default: 24)"
    )
    parser.add_argument(
        "--nas-kron-host",
        default="<SCHEDULER_HOSTNAME>",
        help="NAS KronScheduler hostname"
    )

    args = parser.parse_args()

    daemon = SyphonScheduledDaemon(
        nas_kron_host=args.nas_kron_host,
        interval_hours=args.interval
    )

    if args.deploy:
        # Deploy to NAS KronScheduler
        success = daemon.deploy_to_nas_kron()
        sys.exit(0 if success else 1)

    elif args.cycle:
        # Run single cycle (for cron)
        result = daemon.run_single_cycle()
        sys.exit(0 if result.get("success", False) else 1)

    elif args.daemon:
        # Run as continuous daemon
        daemon.run_daemon()

    else:
        # Default: run single cycle
        result = daemon.run_single_cycle()
        sys.exit(0 if result.get("success", False) else 1)


if __name__ == "__main__":


    main()