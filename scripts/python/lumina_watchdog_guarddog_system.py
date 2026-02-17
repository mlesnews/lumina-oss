#!/usr/bin/env python3
"""
LUMINA Watchdog & Guarddog System

Monitors and protects critical systems, apps, and processes:
- Layout changes (auto-save on trigger)
- Default browser (Neo browser)
- Extension updates
- Connection health
- Settings changes
- And more...

Tags: #WATCHDOG #GUARDDOG #MONITORING #AUTOMATION #PROTECTION @JARVIS @LUMINA @AIQ
"""

import sys
import json
import time
import threading
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler, FileModifiedEvent, FileCreatedEvent
    WATCHDOG_LIB_AVAILABLE = True
except ImportError:
    WATCHDOG_LIB_AVAILABLE = False
    # Create stub classes for when watchdog is not available
    class Observer:
        def __init__(self): pass
        def schedule(self, *args, **kwargs): pass
        def start(self): pass
        def stop(self): pass
        def join(self): pass

    class FileSystemEventHandler:
        def on_modified(self, event): pass
        def on_created(self, event): pass

    class FileModifiedEvent:
        pass

    class FileCreatedEvent:
        pass

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

logger = get_logger("LUMINAWatchdog")

# Watchdog library availability (already handled above)
WATCHDOG_AVAILABLE = WATCHDOG_LIB_AVAILABLE
if not WATCHDOG_AVAILABLE:
    logger.debug("watchdog library not available - file watching disabled")


@dataclass
class WatchdogTask:
    """Watchdog task definition"""
    id: str
    name: str
    description: str
    trigger_type: str  # "file_change", "time_interval", "event", "condition"
    trigger_config: Dict[str, Any]
    action: str  # "save_layout", "check_browser", "verify_settings", etc.
    action_config: Dict[str, Any]
    enabled: bool = True
    priority: str = "medium"  # "low", "medium", "high", "critical"
    last_run: Optional[str] = None
    run_count: int = 0
    success_count: int = 0
    failure_count: int = 0


@dataclass
class GuarddogRule:
    """Guarddog protection rule"""
    id: str
    name: str
    description: str
    system: str  # "layout", "browser", "settings", "extensions", etc.
    condition: str  # "if_changed", "if_missing", "if_wrong_value", etc.
    condition_config: Dict[str, Any]
    action: str  # "restore", "fix", "alert", "prevent"
    action_config: Dict[str, Any]
    enabled: bool = True
    severity: str = "medium"  # "low", "medium", "high", "critical"


class LayoutChangeHandler(FileSystemEventHandler):
    """Handle layout file changes"""

    def __init__(self, callback: Callable):
        self.callback = callback
        self.last_modified = {}

    def on_modified(self, event):
        try:
            if event.is_directory:
                return

            # Only process layout-related files
            if any(keyword in str(event.src_path).lower() for keyword in ['layout', 'workspace.json', 'settings.json']):
                file_path = Path(event.src_path)

                # Debounce: only trigger if file actually changed
                current_mtime = file_path.stat().st_mtime if file_path.exists() else 0
                last_mtime = self.last_modified.get(str(file_path), 0)

                if current_mtime > last_mtime + 1:  # At least 1 second since last change
                    self.last_modified[str(file_path)] = current_mtime
                    logger.info(f"   📝 Layout file changed: {file_path.name}")
                    self.callback(file_path)


        except Exception as e:
            self.logger.error(f"Error in on_modified: {e}", exc_info=True)
            raise
class LUMINAWatchdogGuarddogSystem:
    """
    LUMINA Watchdog & Guarddog System

    Monitors and protects critical systems.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize watchdog/guarddog system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "watchdog_guarddog"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Configuration files
        self.watchdog_tasks_file = self.data_dir / "watchdog_tasks.json"
        self.guarddog_rules_file = self.data_dir / "guarddog_rules.json"

        # Tasks and rules
        self.watchdog_tasks: Dict[str, WatchdogTask] = {}
        self.guarddog_rules: Dict[str, GuarddogRule] = {}

        # File watchers
        self.observer = None
        self.watching = False

        # Load existing tasks and rules
        self._load_tasks_and_rules()

        # Initialize default tasks and rules
        self._initialize_default_tasks()
        self._initialize_default_rules()

        # Initialize @EVO + @SYPHON + @PENTEST + @V3 + @FoF integration
        self._initialize_evo_syphon_pentest_fof()

        logger.info("✅ LUMINA Watchdog & Guarddog System initialized")
        logger.info(f"   Watchdog tasks: {len(self.watchdog_tasks)}")
        logger.info(f"   Guarddog rules: {len(self.guarddog_rules)}")

    def _load_tasks_and_rules(self):
        """Load existing tasks and rules"""
        # Load watchdog tasks
        if self.watchdog_tasks_file.exists():
            try:
                with open(self.watchdog_tasks_file, 'r') as f:
                    data = json.load(f)
                    self.watchdog_tasks = {
                        task_id: WatchdogTask(**task_data)
                        for task_id, task_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load tasks: {e}")

        # Load guarddog rules
        if self.guarddog_rules_file.exists():
            try:
                with open(self.guarddog_rules_file, 'r') as f:
                    data = json.load(f)
                    self.guarddog_rules = {
                        rule_id: GuarddogRule(**rule_data)
                        for rule_id, rule_data in data.items()
                    }
            except Exception as e:
                logger.debug(f"   Could not load rules: {e}")

    def _save_tasks_and_rules(self):
        """Save tasks and rules"""
        # Save watchdog tasks
        try:
            with open(self.watchdog_tasks_file, 'w') as f:
                json.dump({
                    task_id: {
                        "id": task.id,
                        "name": task.name,
                        "description": task.description,
                        "trigger_type": task.trigger_type,
                        "trigger_config": task.trigger_config,
                        "action": task.action,
                        "action_config": task.action_config,
                        "enabled": task.enabled,
                        "priority": task.priority,
                        "last_run": task.last_run,
                        "run_count": task.run_count,
                        "success_count": task.success_count,
                        "failure_count": task.failure_count
                    }
                    for task_id, task in self.watchdog_tasks.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving tasks: {e}")

        # Save guarddog rules
        try:
            with open(self.guarddog_rules_file, 'w') as f:
                json.dump({
                    rule_id: {
                        "id": rule.id,
                        "name": rule.name,
                        "description": rule.description,
                        "system": rule.system,
                        "condition": rule.condition,
                        "condition_config": rule.condition_config,
                        "action": rule.action,
                        "action_config": rule.action_config,
                        "enabled": rule.enabled,
                        "severity": rule.severity
                    }
                    for rule_id, rule in self.guarddog_rules.items()
                }, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving rules: {e}")

    def _initialize_default_tasks(self):
        """Initialize default watchdog tasks"""
        # Task 1: Save layout on change
        if "layout_auto_save" not in self.watchdog_tasks:
            self.watchdog_tasks["layout_auto_save"] = WatchdogTask(
                id="layout_auto_save",
                name="Auto-Save Layout on Change",
                description="Automatically save JARVIS layout when workspace.json or settings.json changes",
                trigger_type="file_change",
                trigger_config={
                    "files": [
                        ".cursor/workspace.json",
                        ".cursor/settings.json",
                        ".cursor/layout_state.json"
                    ],
                    "debounce_seconds": 2
                },
                action="save_layout",
                action_config={
                    "layout_name": "JARVIS",
                    "backup": True
                },
                enabled=True,
                priority="high"
            )

        # Task 2: Monitor default browser
        if "browser_default_monitor" not in self.watchdog_tasks:
            self.watchdog_tasks["browser_default_monitor"] = WatchdogTask(
                id="browser_default_monitor",
                name="Monitor Default Browser",
                description="Monitor and fix if Neo browser is not default",
                trigger_type="time_interval",
                trigger_config={
                    "interval_seconds": 300  # Every 5 minutes
                },
                action="check_browser",
                action_config={
                    "expected_browser": "Neo",
                    "auto_fix": True
                },
                enabled=True,
                priority="high"
            )

        # Task 3: Monitor extension updates
        if "extension_update_monitor" not in self.watchdog_tasks:
            self.watchdog_tasks["extension_update_monitor"] = WatchdogTask(
                id="extension_update_monitor",
                name="Monitor Extension Updates",
                description="Check for extension updates across all marketplaces",
                trigger_type="time_interval",
                trigger_config={
                    "interval_seconds": 3600  # Every hour
                },
                action="check_extensions",
                action_config={
                    "marketplaces": ["vscode", "docker", "openvsx"]
                },
                enabled=True,
                priority="medium"
            )

        # Task 4: Monitor connection health
        if "connection_health_monitor" not in self.watchdog_tasks:
            self.watchdog_tasks["connection_health_monitor"] = WatchdogTask(
                id="connection_health_monitor",
                name="Monitor Connection Health",
                description="Monitor Cursor IDE connection health and log issues",
                trigger_type="time_interval",
                trigger_config={
                    "interval_seconds": 60  # Every minute
                },
                action="check_connection_health",
                action_config={},
                enabled=True,
                priority="critical"
            )

        # Task 5: Monitor settings changes
        if "settings_change_monitor" not in self.watchdog_tasks:
            self.watchdog_tasks["settings_change_monitor"] = WatchdogTask(
                id="settings_change_monitor",
                name="Monitor Settings Changes",
                description="Monitor Cursor IDE settings for unauthorized changes",
                trigger_type="file_change",
                trigger_config={
                    "files": [
                        ".cursor/environment.json",
                        ".cursor/settings.json"
                    ],
                    "debounce_seconds": 5
                },
                action="verify_settings",
                action_config={
                    "backup_on_change": True
                },
                enabled=True,
                priority="high"
            )

        # Task 6: Monitor MailPlus IMAP/SMTP services
        if "mailplus_service_monitor" not in self.watchdog_tasks:
            self.watchdog_tasks["mailplus_service_monitor"] = WatchdogTask(
                id="mailplus_service_monitor",
                name="Monitor MailPlus Services",
                description="Monitor MailPlus IMAP (993) and SMTP (587) services on NAS",
                trigger_type="time_interval",
                trigger_config={
                    "interval_seconds": 300  # Every 5 minutes
                },
                action="check_mailplus_services",
                action_config={
                    "nas_host": "<NAS_PRIMARY_IP>",
                    "imap_port": 993,
                    "smtp_port": 587,
                    "auto_restart": True,
                    "alert_on_failure": True
                },
                enabled=True,
                priority="critical"
            )

        self._save_tasks_and_rules()

    def _initialize_default_rules(self):
        """Initialize default guarddog rules"""
        # Rule 1: Protect JARVIS layout
        if "protect_jarvis_layout" not in self.guarddog_rules:
            self.guarddog_rules["protect_jarvis_layout"] = GuarddogRule(
                id="protect_jarvis_layout",
                name="Protect JARVIS Layout",
                description="Ensure JARVIS layout is always set as default",
                system="layout",
                condition="if_wrong_value",
                condition_config={
                    "file": ".cursor/workspace.json",
                    "path": "layout",
                    "expected_value": "JARVIS"
                },
                action="restore",
                action_config={
                    "restore_to": "JARVIS"
                },
                enabled=True,
                severity="high"
            )

        # Rule 2: Protect Neo browser default
        if "protect_neo_browser" not in self.guarddog_rules:
            self.guarddog_rules["protect_neo_browser"] = GuarddogRule(
                id="protect_neo_browser",
                name="Protect Neo Browser Default",
                description="Ensure Neo browser remains default",
                system="browser",
                condition="if_wrong_value",
                condition_config={
                    "check_command": "get_default_browser",
                    "expected_value": "Neo"
                },
                action="fix",
                action_config={
                    "fix_command": "set_neo_default"
                },
                enabled=True,
                severity="high"
            )

        # Rule 3: Protect local-only mode
        if "protect_local_only" not in self.guarddog_rules:
            self.guarddog_rules["protect_local_only"] = GuarddogRule(
                id="protect_local_only",
                name="Protect Local-Only Mode",
                description="Ensure local-only mode is enforced",
                system="settings",
                condition="if_wrong_value",
                condition_config={
                    "file": ".cursor/environment.json",
                    "path": "localOnlyMode",
                    "expected_value": True
                },
                action="restore",
                action_config={
                    "restore_value": True
                },
                enabled=True,
                severity="critical"
            )

        # Rule 4: Protect ULTRON as default model
        if "protect_ultron_default" not in self.guarddog_rules:
            self.guarddog_rules["protect_ultron_default"] = GuarddogRule(
                id="protect_ultron_default",
                name="Protect ULTRON as Default Model",
                description="Ensure ULTRON is always the default model",
                system="settings",
                condition="if_wrong_value",
                condition_config={
                    "file": ".cursor/environment.json",
                    "path": "defaultModel",
                    "expected_value": "ULTRON"
                },
                action="restore",
                action_config={
                    "restore_value": "ULTRON"
                },
                enabled=True,
                severity="critical"
            )

        # Rule 5: Protect MailPlus IMAP service
        if "protect_mailplus_imap" not in self.guarddog_rules:
            self.guarddog_rules["protect_mailplus_imap"] = GuarddogRule(
                id="protect_mailplus_imap",
                name="Protect MailPlus IMAP Service",
                description="Ensure MailPlus IMAP service (993) is always running",
                system="mailplus",
                condition="if_service_down",
                condition_config={
                    "service": "imap",
                    "host": "<NAS_PRIMARY_IP>",
                    "port": 993
                },
                action="restart",
                action_config={
                    "restart_command": "ensure_mailplus_autostart",
                    "max_retries": 3
                },
                enabled=True,
                severity="critical"
            )

        # Rule 6: Protect MailPlus SMTP service
        if "protect_mailplus_smtp" not in self.guarddog_rules:
            self.guarddog_rules["protect_mailplus_smtp"] = GuarddogRule(
                id="protect_mailplus_smtp",
                name="Protect MailPlus SMTP Service",
                description="Ensure MailPlus SMTP service (587) is always running",
                system="mailplus",
                condition="if_service_down",
                condition_config={
                    "service": "smtp",
                    "host": "<NAS_PRIMARY_IP>",
                    "port": 587
                },
                action="restart",
                action_config={
                    "restart_command": "ensure_mailplus_autostart",
                    "max_retries": 3
                },
                enabled=True,
                severity="critical"
            )

        self._save_tasks_and_rules()

    def _initialize_evo_syphon_pentest_fof(self):
        """Initialize @EVO + @SYPHON + @PENTEST + @V3 + @FoF integration"""
        try:
            from evo_syphon_pentest_fof_watchdog import EVOSyphonPentestFoFWatchdog
            self.evo_syphon_pentest_fof = EVOSyphonPentestFoFWatchdog(self.project_root)

            # Add watchdog tasks for @EVO, @SYPHON, @PENTEST, @V3, @FoF
            if "evo_tag_monitor" not in self.watchdog_tasks:
                self.watchdog_tasks["evo_tag_monitor"] = WatchdogTask(
                    id="evo_tag_monitor",
                    name="@EVO Tag Evolution Monitor",
                    description="Monitor @EVO tag evolution and track changes",
                    trigger_type="time_interval",
                    trigger_config={"interval_seconds": 300},  # Every 5 minutes
                    action="monitor_tag_evolution",
                    action_config={},
                    enabled=True,
                    priority="high"
                )

            if "syphon_refactor_monitor" not in self.watchdog_tasks:
                self.watchdog_tasks["syphon_refactor_monitor"] = WatchdogTask(
                    id="syphon_refactor_monitor",
                    name="@SYPHON Refactoring Monitor",
                    description="Monitor @SYPHON refactoring operations for threats/intent",
                    trigger_type="event",
                    trigger_config={"event_type": "syphon_refactoring"},
                    action="monitor_syphon_refactoring",
                    action_config={},
                    enabled=True,
                    priority="critical"
                )

            if "fof_detection" not in self.watchdog_tasks:
                self.watchdog_tasks["fof_detection"] = WatchdogTask(
                    id="fof_detection",
                    name="@FoF Detection",
                    description="Friend-or-Foe identification and counterstrike",
                    trigger_type="event",
                    trigger_config={"event_type": "fof_detection"},
                    action="detect_fof",
                    action_config={},
                    enabled=True,
                    priority="critical"
                )

            logger.info("   ✅ @EVO + @SYPHON + @PENTEST + @V3 + @FoF: Integrated")
        except Exception as e:
            self.evo_syphon_pentest_fof = None
            logger.debug(f"   @EVO + @SYPHON + @PENTEST + @V3 + @FoF: Not available ({e})")

    def _save_layout_on_change(self, file_path: Path):
        """Save layout when file changes"""
        logger.info(f"   💾 Auto-saving layout from {file_path.name}")

        try:
            from cursor_jarvis_layout_manager import CursorJARVISLayoutManager
            manager = CursorJARVISLayoutManager(self.project_root)
            manager.save_jarvis_layout()
            logger.info("   ✅ Layout auto-saved")
            return True
        except Exception as e:
            logger.error(f"   ❌ Error auto-saving layout: {e}")
            return False

    def _check_browser_default(self):
        """Check and fix default browser"""
        logger.info("   🌐 Checking default browser...")

        try:
            from set_neo_default_browser import NeoDefaultBrowserSetter
            setter = NeoDefaultBrowserSetter(self.project_root)
            status = setter.get_status()

            if not status.get("is_default"):
                logger.warning("   ⚠️  Neo is not default - fixing...")
                setter.set_neo_as_default()
                logger.info("   ✅ Browser default fixed")
            else:
                logger.info("   ✅ Neo is default")

            return True
        except Exception as e:
            logger.error(f"   ❌ Error checking browser: {e}")
            return False

    def _check_connection_health(self):
        """Check connection health"""
        try:
            from cursor_connection_health_monitor import CursorConnectionHealthMonitor
            monitor = CursorConnectionHealthMonitor(self.project_root)
            health = monitor.get_health_status()

            if health["health_status"] == "Poor":
                logger.warning(f"   ⚠️  Connection health: {health['health_status']}")
                logger.warning(f"   Success rate: {health['success_rate']}%")
            else:
                logger.debug(f"   Connection health: {health['health_status']}")

            return True
        except Exception as e:
            logger.debug(f"   Could not check connection health: {e}")
            return False

    def _check_mailplus_services(self, task_config: Dict[str, Any]) -> bool:
        """Check MailPlus IMAP and SMTP services"""
        logger.info("   📧 Checking MailPlus services...")

        try:
            from ensure_mailplus_autostart import MailPlusAutoStartConfigurator

            nas_config = {
                "server": task_config.get("nas_host", "<NAS_PRIMARY_IP>"),
                "domain": "<LOCAL_HOSTNAME>"
            }

            configurator = MailPlusAutoStartConfigurator(nas_config)
            results = configurator.verify_services()

            imap_ok = results.get("imap_accessible", False)
            smtp_ok = results.get("smtp_accessible", False)

            if imap_ok and smtp_ok:
                logger.info("   ✅ MailPlus services: Both IMAP and SMTP are accessible")
                return True
            else:
                logger.warning("   ⚠️  MailPlus services: Some services are not accessible")
                if not imap_ok:
                    logger.warning(f"      ❌ IMAP (port {results.get('imap_port', 993)}) is NOT accessible")
                if not smtp_ok:
                    logger.warning(f"      ❌ SMTP (port {results.get('smtp_port', 587)}) is NOT accessible")

                # Auto-restart if configured
                if task_config.get("auto_restart", False):
                    logger.info("   🔄 Attempting to ensure services are configured for auto-start...")
                    try:
                        configurator.configure_autostart()
                        logger.info("   ✅ Auto-start configuration checked")
                    except Exception as e:
                        logger.warning(f"   ⚠️  Could not configure auto-start: {e}")

                return imap_ok and smtp_ok

        except Exception as e:
            logger.error(f"   ❌ Error checking MailPlus services: {e}")
            return False

    def _verify_settings(self, file_path: Path):
        """Verify settings haven't been changed incorrectly"""
        logger.info(f"   🔍 Verifying settings: {file_path.name}")

        try:
            with open(file_path, 'r') as f:
                settings = json.load(f)

            # Check critical settings
            issues = []

            if file_path.name == "environment.json":
                if settings.get("localOnlyMode") != True:
                    issues.append("localOnlyMode should be True")
                if settings.get("defaultModel") != "ULTRON":
                    issues.append("defaultModel should be ULTRON")

            if issues:
                logger.warning(f"   ⚠️  Settings issues found: {issues}")
                # Could auto-fix here
            else:
                logger.debug("   ✅ Settings verified")

            return True
        except Exception as e:
            logger.error(f"   ❌ Error verifying settings: {e}")
            return False

    def start_watching(self):
        try:
            """Start file watching"""
            if not WATCHDOG_AVAILABLE:
                logger.error("   ❌ watchdog library not available")
                logger.info("   📦 Install: pip install watchdog")
                return False

            if self.watching:
                logger.warning("   ⚠️  Already watching")
                return False

            logger.info("=" * 80)
            logger.info("👁️  STARTING WATCHDOG FILE MONITORING")
            logger.info("=" * 80)

            self.observer = Observer()

            # Watch for layout file changes
            cursor_dir = self.project_root / ".cursor"
            if cursor_dir.exists():
                handler = LayoutChangeHandler(self._save_layout_on_change)
                self.observer.schedule(handler, str(cursor_dir), recursive=False)
                logger.info(f"   👁️  Watching: {cursor_dir}")

            # Watch for settings changes
            handler_settings = FileSystemEventHandler()
            handler_settings.on_modified = lambda e: self._verify_settings(Path(e.src_path)) if not e.is_directory else None
            self.observer.schedule(handler_settings, str(cursor_dir), recursive=False)

            self.observer.start()
            self.watching = True

            logger.info("   ✅ Watchdog monitoring active")
            logger.info("")

            return True

        except Exception as e:
            self.logger.error(f"Error in start_watching: {e}", exc_info=True)
            raise
    def stop_watching(self):
        """Stop file watching"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
            self.watching = False
            logger.info("   ✅ Watchdog monitoring stopped")

    def run_interval_tasks(self):
        """Run time-interval based tasks"""
        logger.info("   ⏰ Running interval tasks...")

        for task in self.watchdog_tasks.values():
            if not task.enabled:
                continue

            if task.trigger_type != "time_interval":
                continue

            # Check if it's time to run
            interval = task.trigger_config.get("interval_seconds", 3600)
            last_run = datetime.fromisoformat(task.last_run) if task.last_run else datetime.min
            next_run = last_run + timedelta(seconds=interval)

            if datetime.now() >= next_run:
                logger.info(f"   🔄 Running task: {task.name}")

                success = False
                try:
                    if task.action == "check_browser":
                        success = self._check_browser_default()
                    elif task.action == "check_extensions":
                        # Would call extension update checker
                        success = True
                    elif task.action == "check_connection_health":
                        success = self._check_connection_health()
                    elif task.action == "check_mailplus_services":
                        success = self._check_mailplus_services(task.action_config)
                    else:
                        logger.warning(f"   ⚠️  Unknown action: {task.action}")

                    task.run_count += 1
                    if success:
                        task.success_count += 1
                    else:
                        task.failure_count += 1
                    task.last_run = datetime.now().isoformat()

                except Exception as e:
                    logger.error(f"   ❌ Task error: {e}")
                    task.failure_count += 1

                self._save_tasks_and_rules()

    def check_guarddog_rules(self):
        """Check and enforce guarddog rules"""
        logger.info("   🛡️  Checking guarddog rules...")

        for rule in self.guarddog_rules.values():
            if not rule.enabled:
                continue

            try:
                if rule.system == "layout":
                    # Check layout
                    workspace_file = self.project_root / ".cursor" / "workspace.json"
                    if workspace_file.exists():
                        with open(workspace_file, 'r') as f:
                            workspace = json.load(f)

                        current_layout = workspace.get("layout")
                        if current_layout != rule.condition_config.get("expected_value"):
                            logger.warning(f"   ⚠️  Layout mismatch: {current_layout} != JARVIS")
                            if rule.action == "restore":
                                self._save_layout_on_change(workspace_file)

                elif rule.system == "browser":
                    # Check browser
                    self._check_browser_default()

                elif rule.system == "settings":
                    # Check settings
                    env_file = self.project_root / ".cursor" / rule.condition_config.get("file")
                    if env_file.exists():
                        with open(env_file, 'r') as f:
                            settings = json.load(f)

                        path = rule.condition_config.get("path")
                        current_value = settings
                        for key in path.split("."):
                            current_value = current_value.get(key) if isinstance(current_value, dict) else None

                        expected = rule.condition_config.get("expected_value")
                        if current_value != expected:
                            logger.warning(f"   ⚠️  Setting mismatch: {path} = {current_value} != {expected}")
                            if rule.action == "restore":
                                # Restore value
                                settings_path = settings
                                path_parts = path.split(".")
                                for key in path_parts[:-1]:
                                    settings_path = settings_path.setdefault(key, {})
                                settings_path[path_parts[-1]] = rule.action_config.get("restore_value")

                                with open(env_file, 'w') as f:
                                    json.dump(settings, f, indent=2)
                                logger.info(f"   ✅ Restored setting: {path}")

                elif rule.system == "mailplus":
                    # Check MailPlus services
                    service = rule.condition_config.get("service")
                    host = rule.condition_config.get("host", "<NAS_PRIMARY_IP>")
                    port = rule.condition_config.get("port")

                    import socket
                    try:
                        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        sock.settimeout(5)
                        result = sock.connect_ex((host, port))
                        sock.close()
                        service_up = (result == 0)

                        if not service_up:
                            logger.warning(f"   ⚠️  MailPlus {service.upper()} service (port {port}) is DOWN")
                            if rule.action == "restart":
                                logger.info(f"   🔄 Attempting to ensure {service.upper()} service auto-start...")
                                try:
                                    from ensure_mailplus_autostart import MailPlusAutoStartConfigurator
                                    nas_config = {"server": host, "domain": "<LOCAL_HOSTNAME>"}
                                    configurator = MailPlusAutoStartConfigurator(nas_config)
                                    configurator.configure_autostart()
                                    logger.info(f"   ✅ {service.upper()} service auto-start configuration checked")
                                except Exception as e:
                                    logger.error(f"   ❌ Could not configure {service.upper()} service: {e}")
                        else:
                            logger.debug(f"   ✅ MailPlus {service.upper()} service (port {port}) is UP")
                    except Exception as e:
                        logger.error(f"   ❌ Error checking MailPlus {service} service: {e}")

            except Exception as e:
                logger.error(f"   ❌ Rule check error: {e}")

    def run_continuous(self):
        """Run watchdog/guarddog continuously"""
        logger.info("=" * 80)
        logger.info("🔄 STARTING CONTINUOUS WATCHDOG/GUARDDOG")
        logger.info("=" * 80)

        # Start file watching
        self.start_watching()

        # Run continuously
        try:
            while True:
                # Run interval tasks
                self.run_interval_tasks()

                # Check guarddog rules
                self.check_guarddog_rules()

                # Sleep
                time.sleep(60)  # Check every minute

        except KeyboardInterrupt:
            logger.info("   ⏹️  Stopping watchdog...")
            self.stop_watching()

    def get_status(self) -> Dict[str, Any]:
        """Get watchdog/guarddog status"""
        active_tasks = sum(1 for t in self.watchdog_tasks.values() if t.enabled)
        active_rules = sum(1 for r in self.guarddog_rules.values() if r.enabled)

        return {
            "watching": self.watching,
            "active_tasks": active_tasks,
            "total_tasks": len(self.watchdog_tasks),
            "active_rules": active_rules,
            "total_rules": len(self.guarddog_rules),
            "tasks_by_priority": {
                "critical": sum(1 for t in self.watchdog_tasks.values() if t.enabled and t.priority == "critical"),
                "high": sum(1 for t in self.watchdog_tasks.values() if t.enabled and t.priority == "high"),
                "medium": sum(1 for t in self.watchdog_tasks.values() if t.enabled and t.priority == "medium"),
                "low": sum(1 for t in self.watchdog_tasks.values() if t.enabled and t.priority == "low")
            }
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="LUMINA Watchdog & Guarddog System")
        parser.add_argument("--start", action="store_true", help="Start continuous monitoring")
        parser.add_argument("--status", action="store_true", help="Show status")
        parser.add_argument("--run-once", action="store_true", help="Run tasks once")
        parser.add_argument("--check-rules", action="store_true", help="Check guarddog rules")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        system = LUMINAWatchdogGuarddogSystem()

        if args.start:
            system.run_continuous()

        elif args.run_once:
            system.run_interval_tasks()
            system.check_guarddog_rules()
            print("✅ Tasks and rules executed")

        elif args.check_rules:
            system.check_guarddog_rules()
            print("✅ Guarddog rules checked")

        elif args.status or args.json:
            status = system.get_status()
            if args.json:
                print(json.dumps(status, indent=2, default=str))
            else:
                print(f"Watching: {status['watching']}")
                print(f"Active Tasks: {status['active_tasks']}/{status['total_tasks']}")
                print(f"Active Rules: {status['active_rules']}/{status['total_rules']}")
                print(f"Critical Tasks: {status['tasks_by_priority']['critical']}")

        else:
            # Default: show status
            status = system.get_status()
            print(f"Watching: {status['watching']}")
            print(f"Active Tasks: {status['active_tasks']}")
            print(f"Active Rules: {status['active_rules']}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()