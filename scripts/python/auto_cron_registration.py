#!/usr/bin/env python3
"""
Automatic Cron Registration System

Automatically registers services with cron scheduler when they're created,
ensuring scheduled services are not just sitting there unused.

Features:
- Decorator-based cron registration
- Automatic detection of services needing scheduling
- Integration with NASCronScheduler
- Dynamic/evolutionary scheduling (Adapt, Improvise, Overcome)

Tags: #CRON #AUTOMATION #SCHEDULING #REGISTRATION @JARVIS @LUMINA @PEAK @DTN @EVO
"""

import sys
import json
import inspect
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable, Type
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps

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

logger = get_logger("AutoCronRegistration")

try:
    from nas_cron_scheduler import NASCronScheduler, CronJob
    NAS_SCHEDULER_AVAILABLE = True
except ImportError:
    NAS_SCHEDULER_AVAILABLE = False
    logger.warning("   ⚠️  NAS Cron Scheduler not available")


class ScheduleFrequency(Enum):
    """Schedule frequency types"""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    CUSTOM = "custom"
    REAL_TIME = "real_time"  # Not for cron, but for tracking


@dataclass
class CronScheduleConfig:
    """Configuration for cron scheduling"""
    schedule: str  # Cron expression (e.g., "0 * * * *" for hourly)
    frequency: ScheduleFrequency
    enabled: bool = True
    description: str = ""
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def hourly(cls, minute: int = 0, description: str = "", tags: List[str] = None) -> 'CronScheduleConfig':
        """Create hourly schedule"""
        return cls(
            schedule=f"{minute} * * * *",
            frequency=ScheduleFrequency.HOURLY,
            description=description,
            tags=tags or []
        )

    @classmethod
    def daily(cls, hour: int = 2, minute: int = 0, description: str = "", tags: List[str] = None) -> 'CronScheduleConfig':
        """Create daily schedule"""
        return cls(
            schedule=f"{minute} {hour} * * *",
            frequency=ScheduleFrequency.DAILY,
            description=description,
            tags=tags or []
        )

    @classmethod
    def weekly(cls, day: int = 1, hour: int = 0, minute: int = 0, description: str = "", tags: List[str] = None) -> 'CronScheduleConfig':
        """Create weekly schedule (day: 0=Sunday, 1=Monday, etc.)"""
        return cls(
            schedule=f"{minute} {hour} * * {day}",
            frequency=ScheduleFrequency.WEEKLY,
            description=description,
            tags=tags or []
        )

    @classmethod
    def custom(cls, cron_expr: str, description: str = "", tags: List[str] = None) -> 'CronScheduleConfig':
        """Create custom schedule"""
        return cls(
            schedule=cron_expr,
            frequency=ScheduleFrequency.CUSTOM,
            description=description,
            tags=tags or []
        )


class AutoCronRegistry:
    """
    Automatic Cron Registration Registry

    Tracks and automatically registers services with cron scheduler
    """

    _instance: Optional['AutoCronRegistry'] = None
    _registered_services: Dict[str, Dict[str, Any]] = {}
    _scheduler: Optional[NASCronScheduler] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.project_root = project_root
        self.data_dir = self.project_root / "data" / "auto_cron"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.registry_file = self.data_dir / "registered_services.json"

        # Initialize scheduler
        if NAS_SCHEDULER_AVAILABLE:
            try:
                self._scheduler = NASCronScheduler(project_root=self.project_root)
                logger.info("✅ Auto Cron Registry initialized with scheduler")
            except Exception as e:
                logger.warning(f"   ⚠️  Could not initialize scheduler: {e}")
                self._scheduler = None
        else:
            self._scheduler = None

        # Load existing registry
        self._load_registry()

        self._initialized = True
        logger.info(f"   Registered services: {len(self._registered_services)}")

    def _load_registry(self):
        """Load registered services"""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self._registered_services = json.load(f)
            except Exception as e:
                logger.debug(f"   Could not load registry: {e}")

    def _save_registry(self):
        """Save registered services"""
        try:
            with open(self.registry_file, 'w', encoding='utf-8') as f:
                json.dump(self._registered_services, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"   ❌ Error saving registry: {e}")

    def register_service(
        self,
        service_id: str,
        service_name: str,
        script_path: str,
        schedule_config: CronScheduleConfig,
        command_template: Optional[str] = None,
        auto_deploy: bool = True
    ) -> bool:
        """
        Register a service with cron scheduler

        Args:
            service_id: Unique identifier for the service
            service_name: Human-readable name
            script_path: Path to script (relative to project_root)
            schedule_config: Cron schedule configuration
            command_template: Optional command template (defaults to python script_path)
            auto_deploy: Whether to automatically deploy to cron scheduler

        Returns:
            True if registration successful
        """
        logger.info(f"   📋 Registering service: {service_name}")

        # Build command
        if command_template:
            command = command_template.format(
                script_path=script_path,
                project_root=self.project_root
            )
        else:
            # Default: python script on NAS
            nas_script_path = f"/volume1/docker/lumina/{script_path}"
            command = f"python {nas_script_path}"

        # Check if already registered
        if service_id in self._registered_services:
            logger.info(f"   ⚠️  Service already registered: {service_id}")
            # Update if schedule changed
            existing = self._registered_services[service_id]
            if existing.get("schedule") != schedule_config.schedule:
                logger.info(f"   🔄 Updating schedule for: {service_id}")
            else:
                return True

        # Register with scheduler
        if self._scheduler and auto_deploy:
            try:
                # Create cron job
                cron_job = CronJob(
                    id=service_id,
                    name=service_name,
                    description=schedule_config.description or f"Auto-registered: {service_name}",
                    schedule=schedule_config.schedule,
                    command=command,
                    script_path=script_path,
                    enabled=schedule_config.enabled,
                    tags=schedule_config.tags,
                    metadata={
                        "frequency": schedule_config.frequency.value,
                        "auto_registered": True,
                        "registered_at": datetime.now().isoformat(),
                        **schedule_config.metadata
                    }
                )

                # Add to scheduler
                self._scheduler.cron_jobs[service_id] = cron_job
                self._scheduler._save_cron_jobs()

                logger.info(f"   ✅ Registered with cron scheduler: {service_name}")
                logger.info(f"      Schedule: {schedule_config.schedule}")

            except Exception as e:
                logger.error(f"   ❌ Error registering with scheduler: {e}")
                return False

        # Save to registry
        self._registered_services[service_id] = {
            "service_id": service_id,
            "service_name": service_name,
            "script_path": script_path,
            "schedule": schedule_config.schedule,
            "frequency": schedule_config.frequency.value,
            "enabled": schedule_config.enabled,
            "description": schedule_config.description,
            "tags": schedule_config.tags,
            "command": command,
            "registered_at": datetime.now().isoformat(),
            "metadata": schedule_config.metadata
        }
        self._save_registry()

        return True

    def get_registered_services(self) -> Dict[str, Dict[str, Any]]:
        """Get all registered services"""
        return self._registered_services.copy()

    def is_registered(self, service_id: str) -> bool:
        """Check if service is registered"""
        return service_id in self._registered_services

    def unregister_service(self, service_id: str) -> bool:
        """Unregister a service"""
        if service_id not in self._registered_services:
            return False

        # Remove from scheduler
        if self._scheduler and service_id in self._scheduler.cron_jobs:
            del self._scheduler.cron_jobs[service_id]
            self._scheduler._save_cron_jobs()

        # Remove from registry
        del self._registered_services[service_id]
        self._save_registry()

        logger.info(f"   ✅ Unregistered service: {service_id}")
        return True


# Global registry instance
_registry = None

def get_registry() -> AutoCronRegistry:
    """Get global registry instance"""
    global _registry
    if _registry is None:
        _registry = AutoCronRegistry()
    return _registry


def cron_scheduled(
    schedule_config: CronScheduleConfig,
    service_id: Optional[str] = None,
    service_name: Optional[str] = None,
    command_template: Optional[str] = None,
    auto_deploy: bool = True
):
    """
    Decorator to automatically register a service/class with cron scheduler

    Usage:
        @cron_scheduled(CronScheduleConfig.hourly(minute=0, description="Hourly intelligence collection"))
        class LUMINAIntelligenceCollection:
            ...

    Or for functions:
        @cron_scheduled(CronScheduleConfig.daily(hour=2, description="Daily aggregation"))
        def aggregate_daily_intelligence():
            ...
    """
    def decorator(obj: Any):
        # Determine service ID and name
        if service_id:
            svc_id = service_id
        else:
            svc_id = obj.__name__ if hasattr(obj, '__name__') else str(obj)
            svc_id = svc_id.lower().replace('_', '-')

        if service_name:
            svc_name = service_name
        else:
            svc_name = obj.__name__ if hasattr(obj, '__name__') else str(obj)
            svc_name = svc_name.replace('_', ' ').title()

        # Get script path
        if inspect.isclass(obj) or inspect.isfunction(obj):
            # Try to get file path
            try:
                file_path = inspect.getfile(obj)
                rel_path = Path(file_path).relative_to(project_root)
                script_path = str(rel_path).replace('\\', '/')
            except:
                # Fallback: construct from module
                if hasattr(obj, '__module__'):
                    module_path = obj.__module__.replace('.', '/')
                    script_path = f"scripts/python/{module_path}.py"
                else:
                    script_path = f"scripts/python/{svc_id}.py"
        else:
            script_path = f"scripts/python/{svc_id}.py"

        # Register with registry
        registry = get_registry()
        registry.register_service(
            service_id=svc_id,
            service_name=svc_name,
            script_path=script_path,
            schedule_config=schedule_config,
            command_template=command_template,
            auto_deploy=auto_deploy
        )

        # Store metadata on object
        obj._cron_scheduled = True
        obj._cron_schedule_config = schedule_config
        obj._cron_service_id = svc_id

        return obj

    return decorator


def auto_register_existing_services():
    """
    Automatically detect and register existing services that should be scheduled

    Scans for services with scheduling hints and registers them
    """
    logger.info("   🔍 Scanning for services needing cron registration...")

    registry = get_registry()

    # Known services that need scheduling
    services_to_register = [
        {
            "service_id": "lumina-intelligence-hourly",
            "service_name": "LUMINA Intelligence Collection - Hourly",
            "script_path": "scripts/python/lumina_intelligence_collection.py",
            "schedule_config": CronScheduleConfig.hourly(
                minute=0,
                description="Hourly intelligence data collection",
                tags=["intelligence", "hourly", "data_collection"]
            ),
            "command_template": "python /volume1/docker/lumina/scripts/python/lumina_intelligence_collection.py --collect-hourly"
        },
        {
            "service_id": "lumina-intelligence-daily",
            "service_name": "LUMINA Intelligence Collection - Daily",
            "script_path": "scripts/python/lumina_intelligence_collection.py",
            "schedule_config": CronScheduleConfig.daily(
                hour=2,
                minute=0,
                description="Daily intelligence aggregation",
                tags=["intelligence", "daily", "aggregation"]
            ),
            "command_template": "python /volume1/docker/lumina/scripts/python/lumina_intelligence_collection.py --aggregate-daily"
        },
        {
            "service_id": "lumina-quality-reporting",
            "service_name": "LUMINA Quality Reporting",
            "script_path": "scripts/python/lumina_quality_reporter.py",
            "schedule_config": CronScheduleConfig.daily(
                hour=3,
                minute=0,
                description="Daily quality reporting (Accessibility, Compatibility, Security)",
                tags=["quality", "reporting", "accessibility", "security", "compatibility"]
            ),
            "command_template": "python /volume1/docker/lumina/scripts/python/lumina_quality_reporter.py"
        },
    ]

    registered_count = 0
    for service in services_to_register:
        if not registry.is_registered(service["service_id"]):
            if registry.register_service(
                service_id=service["service_id"],
                service_name=service["service_name"],
                script_path=service["script_path"],
                schedule_config=service["schedule_config"],
                command_template=service.get("command_template"),
                auto_deploy=True
            ):
                registered_count += 1

    logger.info(f"   ✅ Auto-registered {registered_count} services")
    return registered_count


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Auto Cron Registration")
        parser.add_argument("--auto-register", action="store_true", help="Auto-register existing services")
        parser.add_argument("--list", action="store_true", help="List registered services")
        parser.add_argument("--deploy", action="store_true", help="Deploy all registered services to NAS")
        parser.add_argument("--json", action="store_true", help="Output as JSON")

        args = parser.parse_args()

        registry = get_registry()

        if args.auto_register:
            count = auto_register_existing_services()
            if args.json:
                print(json.dumps({"registered": count}, indent=2))
            else:
                print(f"✅ Auto-registered {count} services")

        elif args.list:
            services = registry.get_registered_services()
            if args.json:
                print(json.dumps(services, indent=2, default=str))
            else:
                print(f"Registered Services: {len(services)}")
                for svc_id, svc_data in services.items():
                    status = "✅" if svc_data.get("enabled", True) else "⏸️"
                    print(f"  {status} {svc_data.get('service_name', svc_id)}: {svc_data.get('schedule', 'N/A')}")

        elif args.deploy:
            if registry._scheduler:
                results = registry._scheduler.deploy_all_cron_jobs()
                deployed = sum(1 for r in results.values() if r is True)
                if args.json:
                    print(json.dumps(results, indent=2, default=str))
                else:
                    print(f"✅ Deployed {deployed} cron jobs to NAS")
            else:
                print("❌ Scheduler not available")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()