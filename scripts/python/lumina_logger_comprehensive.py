#!/usr/bin/env python3
"""
Lumina Comprehensive Logger - Fully Robust & Comprehensive (@frc) Logging Module

Comprehensive logging with:
- Azure Monitor/Application Insights integration
- Azure Service Bus event publishing
- Azure Storage for log archival
- Azure Event Grid for real-time events
- Azure Cognitive Services (Speech, Text Analytics, Vision)
- Azure Cosmos DB for structured data
- Azure Functions for serverless processing
- Helpdesk/Change Management integration
- Rules management integration
- Harmony across all systems (old and new)
- Structured logging with context
- Performance metrics
- Error tracking and alerting

Tags: #LOGGING #AZURE #FRC #FULL_ROBUST_COMPREHENSIVE #CLOUD #ECOSYSTEM @JARVIS @LUMINA
"""

import sys
import json
import logging
import traceback
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
from contextvars import ContextVar
import threading

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

# Import base logger
try:
    from lumina_logger import get_logger as base_get_logger, LuminaLogger as BaseLuminaLogger
    BASE_LOGGER_AVAILABLE = True
except ImportError:
    BASE_LOGGER_AVAILABLE = False
    base_get_logger = None
    BaseLuminaLogger = None

# Azure Monitor/Application Insights
try:
    from opencensus.ext.azure.log_exporter import AzureLogHandler
    from opencensus.ext.azure.trace_exporter import AzureExporter
    from opencensus.trace.tracer import Tracer
    from opencensus.trace.samplers import ProbabilitySampler
    AZURE_MONITOR_AVAILABLE = True
except ImportError:
    AZURE_MONITOR_AVAILABLE = False
    # Don't use logger here - it may not be defined yet
    pass

# Azure Service Bus for event publishing
try:
    from jarvis_azure_service_bus_integration import AzureServiceBusIntegration
    SERVICE_BUS_AVAILABLE = True
except ImportError:
    SERVICE_BUS_AVAILABLE = False

# Azure Storage for log archival
try:
    from jarvis_azure_storage_integration import get_azure_storage
    AZURE_STORAGE_AVAILABLE = True
except ImportError:
    AZURE_STORAGE_AVAILABLE = False

# Azure Event Grid for real-time events
try:
    from jarvis_azure_event_grid_integration import get_azure_event_grid
    AZURE_EVENT_GRID_AVAILABLE = True
except ImportError:
    AZURE_EVENT_GRID_AVAILABLE = False

# Azure Cognitive Services
try:
    from jarvis_azure_cognitive_services_integration import get_azure_cognitive_services
    AZURE_COGNITIVE_AVAILABLE = True
except ImportError:
    AZURE_COGNITIVE_AVAILABLE = False

# Azure Cosmos DB
try:
    from jarvis_azure_cosmosdb_integration import get_azure_cosmos_db
    AZURE_COSMOS_AVAILABLE = True
except ImportError:
    AZURE_COSMOS_AVAILABLE = False

# Azure Functions
try:
    from jarvis_azure_functions_integration import get_azure_functions
    AZURE_FUNCTIONS_AVAILABLE = True
except ImportError:
    AZURE_FUNCTIONS_AVAILABLE = False

# Context for request tracking
request_context: ContextVar[Dict[str, Any]] = ContextVar('request_context', default={})


class ComprehensiveLogger:
    """
    Comprehensive logger with Azure Monitor, Service Bus, and Helpdesk integration
    """

    def __init__(
        self,
        name: str,
        project_root: Path = None,
        enable_azure_monitor: bool = True,
        enable_service_bus: bool = True,
        enable_helpdesk: bool = True
    ):
        self.name = name
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.data_dir = self.project_root / "data" / "comprehensive_logging"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Base logger
        if BASE_LOGGER_AVAILABLE:
            self.base_logger = base_get_logger(name)
        else:
            self.base_logger = logging.getLogger(name)
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
            self.base_logger.addHandler(handler)
            self.base_logger.setLevel(logging.INFO)

        # @frc: Add file logging to comprehensive logger (always)
        self._setup_file_logging()

        # Azure Monitor
        self.azure_monitor_enabled = enable_azure_monitor and AZURE_MONITOR_AVAILABLE
        self.azure_handler = None
        if self.azure_monitor_enabled:
            self._setup_azure_monitor()

        # Azure Service Bus
        self.service_bus_enabled = enable_service_bus and SERVICE_BUS_AVAILABLE
        self.service_bus = None
        if self.service_bus_enabled:
            try:
                self.service_bus = AzureServiceBusIntegration(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Service Bus not available: {e}")
                self.service_bus_enabled = False

        # Azure Storage (for log archival)
        self.storage_enabled = AZURE_STORAGE_AVAILABLE
        self.azure_storage = None
        if self.storage_enabled:
            try:
                self.azure_storage = get_azure_storage(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Azure Storage not available: {e}")
                self.storage_enabled = False

        # Azure Event Grid (for real-time events)
        self.event_grid_enabled = AZURE_EVENT_GRID_AVAILABLE
        self.azure_event_grid = None
        if self.event_grid_enabled:
            try:
                self.azure_event_grid = get_azure_event_grid(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Azure Event Grid not available: {e}")
                self.event_grid_enabled = False

        # Azure Cognitive Services (for AI enhancements)
        self.cognitive_enabled = AZURE_COGNITIVE_AVAILABLE
        self.azure_cognitive = None
        if self.cognitive_enabled:
            try:
                self.azure_cognitive = get_azure_cognitive_services(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Azure Cognitive Services not available: {e}")
                self.cognitive_enabled = False

        # Azure Cosmos DB (for structured data)
        self.cosmos_enabled = AZURE_COSMOS_AVAILABLE
        self.azure_cosmos = None
        if self.cosmos_enabled:
            try:
                self.azure_cosmos = get_azure_cosmos_db(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Azure Cosmos DB not available: {e}")
                self.cosmos_enabled = False

        # Azure Functions (for serverless processing)
        self.functions_enabled = AZURE_FUNCTIONS_AVAILABLE
        self.azure_functions = None
        if self.functions_enabled:
            try:
                self.azure_functions = get_azure_functions(self.project_root)
            except Exception as e:
                self.base_logger.debug(f"Azure Functions not available: {e}")
                self.functions_enabled = False

        # Helpdesk integration
        self.helpdesk_enabled = enable_helpdesk
        self.helpdesk_config = self._load_helpdesk_config()

        # Rules management
        self.rules_config = self._load_rules_config()

        # Performance metrics
        self.metrics = {
            "log_count": 0,
            "error_count": 0,
            "warning_count": 0,
            "azure_events_sent": 0,
            "helpdesk_tickets_created": 0
        }

        # Thread safety
        self._lock = threading.Lock()

        # File logging path
        self.log_file = None

    def _setup_file_logging(self):
        """@frc: Setup file logging for comprehensive logger"""
        try:
            log_dir = self.project_root / "data" / "logs"
            log_dir.mkdir(parents=True, exist_ok=True)

            # Create timestamped log file
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = log_dir / f"{self.name}_{timestamp}.log"

            # Check if file handler already exists for this file
            has_file_handler = False
            for handler in self.base_logger.handlers:
                if isinstance(handler, logging.FileHandler):
                    try:
                        if hasattr(handler, 'baseFilename') and str(log_file) == str(handler.baseFilename):
                            has_file_handler = True
                            self.log_file = log_file
                            break
                    except Exception:
                        pass

            if not has_file_handler:
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)  # File gets all levels
                file_formatter = logging.Formatter(
                    "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S"
                )
                file_handler.setFormatter(file_formatter)
                self.base_logger.addHandler(file_handler)
                self.log_file = log_file
        except Exception as e:
            # Don't fail if file logging can't be set up
            try:
                self.base_logger.debug(f"File logging setup failed: {e}")
            except Exception:
                pass

    def _setup_azure_monitor(self):
        """Setup Azure Monitor/Application Insights"""
        try:
            config_file = self.project_root / "config" / "azure_services_config.json"
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    monitor_config = config.get("azure_services_config", {}).get("monitor", {})
                    app_insights = monitor_config.get("application_insights", {})

                    # Get instrumentation key from Key Vault or config
                    instrumentation_key = None
                    if app_insights.get("instrumentation_key_secret"):
                        # Try to get from Key Vault
                        try:
                            from azure.keyvault.secrets import SecretClient
                            from azure.identity import DefaultAzureCredential
                            vault_url = "https://jarvis-lumina.vault.azure.net/"
                            credential = DefaultAzureCredential(

                                                exclude_interactive_browser_credential=False,

                                                exclude_shared_token_cache_credential=False

                                            )
                            secret_client = SecretClient(vault_url=vault_url, credential=credential)
                            instrumentation_key = secret_client.get_secret(
                                app_insights.get("instrumentation_key_secret")
                            ).value
                        except Exception:
                            pass

                    if instrumentation_key:
                        self.azure_handler = AzureLogHandler(
                            connection_string=f"InstrumentationKey={instrumentation_key}"
                        )
                        self.base_logger.addHandler(self.azure_handler)
                        self.base_logger.info("✅ Azure Monitor logging enabled")
        except Exception as e:
            self.base_logger.debug(f"Azure Monitor setup failed: {e}")

    def _load_helpdesk_config(self) -> Dict[str, Any]:
        """Load helpdesk configuration"""
        helpdesk_file = self.project_root / "config" / "helpdesk" / "helpdesk_structure.json"
        if helpdesk_file.exists():
            try:
                with open(helpdesk_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _load_rules_config(self) -> Dict[str, Any]:
        """Load rules configuration"""
        rules_file = self.project_root / ".cursorrules"
        rules_config = {
            "rules_file": str(rules_file),
            "rules_exist": rules_file.exists(),
            "last_updated": None
        }

        if rules_file.exists():
            try:
                stat = rules_file.stat()
                rules_config["last_updated"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            except Exception:
                pass

        return rules_config

    def _get_context(self) -> Dict[str, Any]:
        """Get current request context"""
        context = request_context.get({}).copy()
        context.update({
            "logger_name": self.name,
            "timestamp": datetime.now().isoformat()
        })
        return context

    def _publish_to_service_bus(self, level: str, message: str, context: Dict[str, Any] = None):
        """Publish log event to Azure Service Bus"""
        if not self.service_bus_enabled or not self.service_bus:
            return

        try:
            event_data = {
                "level": level,
                "message": message,
                "logger": self.name,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }

            # Send to appropriate topic based on level
            if level in ["error", "critical"]:
                self.service_bus.send_system_event("log_error", event_data)
            elif level == "warning":
                self.service_bus.send_system_event("log_warning", event_data)
            else:
                self.service_bus.send_system_event("log_info", event_data)

            with self._lock:
                self.metrics["azure_events_sent"] += 1
        except Exception as e:
            self.base_logger.debug(f"Service Bus publish failed: {e}")

    def _check_rules_and_helpdesk(self, level: str, message: str, context: Dict[str, Any] = None):
        """Check if rules need updating and create helpdesk ticket if needed"""
        if not self.helpdesk_enabled:
            return

        # Check for rules-related issues
        rules_keywords = ["rule", "rules", ".cursorrules", "missing rule", "rule update", "rule required"]
        if any(keyword in message.lower() for keyword in rules_keywords):
            # Check if rules file exists or needs updating
            if not self.rules_config.get("rules_exist"):
                self._create_helpdesk_ticket(
                    "rules_missing",
                    f"Rules file missing: {message}",
                    context
                )
            elif level in ["error", "warning"]:
                # Rules may need updating
                self._create_helpdesk_ticket(
                    "rules_update_required",
                    f"Rules may need updating: {message}",
                    context
                )

    def _publish_to_event_grid(self, level: str, message: str, context: Dict[str, Any] = None):
        """Publish log event to Azure Event Grid"""
        if not self.event_grid_enabled or not self.azure_event_grid:
            return

        try:
            event_data = {
                "level": level,
                "message": message,
                "logger": self.name,
                "context": context or {},
                "timestamp": datetime.now().isoformat()
            }

            # Publish to system-events topic
            self.azure_event_grid.publish_system_event(f"lumina.log.{level.lower()}", event_data)
        except Exception as e:
            self.base_logger.debug(f"Event Grid publish failed: {e}")

    def _archive_log_to_storage(self):
        """Archive log file to Azure Storage"""
        if not self.storage_enabled or not self.azure_storage or not self.log_file:
            return

        try:
            # Archive terminal logs periodically (every 100 log entries or daily)
            if hasattr(self, '_archive_counter'):
                self._archive_counter += 1
            else:
                self._archive_counter = 1

            # Archive every 100 entries or if it's a new day
            if self._archive_counter % 100 == 0 or not hasattr(self, '_last_archive_date'):
                result = self.azure_storage.archive_terminal_log(self.log_file)
                if result.get("success"):
                    self._last_archive_date = datetime.now().date()
                    self.base_logger.debug(f"✅ Log archived to Azure Storage: {result.get('url')}")
        except Exception as e:
            self.base_logger.debug(f"Log archival failed: {e}")

    def _create_helpdesk_ticket(
        self,
        ticket_type: str,
        description: str,
        context: Dict[str, Any] = None
    ):
        """Create helpdesk ticket for rules management"""
        try:
            tickets_file = self.project_root / "data" / "notification_tickets" / "tickets.json"
            tickets_file.parent.mkdir(parents=True, exist_ok=True)

            # Load existing tickets
            tickets = []
            if tickets_file.exists():
                try:
                    with open(tickets_file, 'r', encoding='utf-8') as f:
                        tickets = json.load(f)
                except Exception:
                    pass

            # Create new ticket
            ticket = {
                "ticket_id": f"rules-{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "type": ticket_type,
                "title": f"Rules Management: {ticket_type}",
                "description": description,
                "context": context or {},
                "created_at": datetime.now().isoformat(),
                "status": "open",
                "priority": "medium",
                "assigned_to": "change_management_team",
                "tags": ["#RULES", "#CHANGE_MANAGEMENT", "#LOGGING"]
            }

            tickets.append(ticket)

            # Save tickets
            with open(tickets_file, 'w', encoding='utf-8') as f:
                json.dump(tickets, f, indent=2, default=str)

            with self._lock:
                self.metrics["helpdesk_tickets_created"] += 1

            self.base_logger.info(f"📋 Helpdesk ticket created: {ticket['ticket_id']}")
        except Exception as e:
            self.base_logger.debug(f"Helpdesk ticket creation failed: {e}")

    def _log_with_context(
        self,
        level: str,
        message: str,
        context: Dict[str, Any] = None,
        exception: Exception = None
    ):
        """Log with full context and integrations"""
        context = context or {}
        full_context = self._get_context()
        full_context.update(context)

        # Format message with context
        if full_context:
            context_str = " | ".join([f"{k}={v}" for k, v in full_context.items() if k != "message"])
            formatted_message = f"{message} | {context_str}" if context_str else message
        else:
            formatted_message = message

        # Log to base logger
        log_method = getattr(self.base_logger, level.lower(), self.base_logger.info)
        if exception:
            log_method(formatted_message, exc_info=exception)
        else:
            log_method(formatted_message)

        # Update metrics
        with self._lock:
            self.metrics["log_count"] += 1
            if level.lower() in ["error", "critical"]:
                self.metrics["error_count"] += 1
            elif level.lower() == "warning":
                self.metrics["warning_count"] += 1

        # Store in Cosmos DB for structured queries (errors and critical only to reduce cost)
        if self.cosmos_enabled and self.azure_cosmos and level.lower() in ["error", "critical"]:
            try:
                log_entry = {
                    "id": f"{self.name}_{datetime.now().isoformat()}",
                    "logger": self.name,
                    "level": level,
                    "message": message,
                    "context": full_context,
                    "timestamp": datetime.now().isoformat()
                }
                self.azure_cosmos.create_item("terminal_logs", log_entry)
            except Exception as e:
                self.base_logger.debug(f"Cosmos DB storage failed: {e}")

        # Publish to Service Bus
        self._publish_to_service_bus(level, message, full_context)

        # Publish to Event Grid (for real-time event routing)
        self._publish_to_event_grid(level, message, full_context)

        # Archive to Azure Storage (for terminal logs)
        if level.lower() in ["info", "warning", "error", "critical"] and self.log_file:
            self._archive_log_to_storage()

        # Check rules and helpdesk
        self._check_rules_and_helpdesk(level, message, full_context)

        # Add custom properties for Azure Monitor
        if self.azure_handler and full_context:
            # Azure Monitor will automatically capture these
            pass

    def debug(self, message: str, *args, context: Dict[str, Any] = None, **kwargs):
        """Log debug message - supports both string formatting and context"""
        # Check if first arg is a dict (context passed positionally)
        if args and isinstance(args[0], dict) and context is None:
            context = args[0]
            args = args[1:]

        if args:
            # String formatting (e.g., logger.info("Value: %s", value))
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                # If formatting fails, just use message as-is
                formatted_message = message
            self._log_with_context("debug", formatted_message, context)
        else:
            self._log_with_context("debug", message, context)

    def info(self, message: str, *args, context: Dict[str, Any] = None, **kwargs):
        """Log info message - supports both string formatting and context"""
        # Check if first arg is a dict (context passed positionally)
        if args and isinstance(args[0], dict) and context is None:
            context = args[0]
            args = args[1:]

        if args:
            # String formatting (e.g., logger.info("Value: %s", value))
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                # If formatting fails, just use message as-is
                formatted_message = message
            self._log_with_context("info", formatted_message, context)
        else:
            self._log_with_context("info", message, context)

    def warning(self, message: str, *args, context: Dict[str, Any] = None, **kwargs):
        """Log warning message - supports both string formatting and context"""
        # Check if first arg is a dict (context passed positionally)
        if args and isinstance(args[0], dict) and context is None:
            context = args[0]
            args = args[1:]

        if args:
            # String formatting (e.g., logger.warning("Value: %s", value))
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                # If formatting fails, just use message as-is
                formatted_message = message
            self._log_with_context("warning", formatted_message, context)
        else:
            self._log_with_context("warning", message, context)

    def error(self, message: str, *args, context: Dict[str, Any] = None, exception: Exception = None, **kwargs):
        """Log error message - supports both string formatting and context"""
        # Check if first arg is a dict (context passed positionally)
        if args and isinstance(args[0], dict) and context is None:
            context = args[0]
            args = args[1:]

        if args:
            # String formatting (e.g., logger.error("Value: %s", value))
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                # If formatting fails, just use message as-is
                formatted_message = message
            self._log_with_context("error", formatted_message, context, exception)
        else:
            self._log_with_context("error", message, context, exception)

    def critical(self, message: str, *args, context: Dict[str, Any] = None, exception: Exception = None, **kwargs):
        """Log critical message - supports both string formatting and context"""
        # Check if first arg is a dict (context passed positionally)
        if args and isinstance(args[0], dict) and context is None:
            context = args[0]
            args = args[1:]

        if args:
            # String formatting (e.g., logger.critical("Value: %s", value))
            try:
                formatted_message = message % args
            except (TypeError, ValueError):
                # If formatting fails, just use message as-is
                formatted_message = message
            self._log_with_context("critical", formatted_message, context, exception)
        else:
            self._log_with_context("critical", message, context, exception)
        # Critical errors should create helpdesk tickets
        self._create_helpdesk_ticket("critical_error", message, context)

    def exception(self, message: str, context: Dict[str, Any] = None):
        """Log exception with traceback"""
        exc_type, exc_value, exc_traceback = sys.exc_info()
        self._log_with_context("error", message, context, exc_value)

    def get_metrics(self) -> Dict[str, Any]:
        """Get logging metrics"""
        with self._lock:
            return self.metrics.copy()

    def set_context(self, **kwargs):
        """Set request context"""
        current = request_context.get({})
        current.update(kwargs)
        request_context.set(current)


def get_comprehensive_logger(
    name: str,
    project_root: Path = None,
    enable_azure_monitor: bool = True,
    enable_service_bus: bool = True,
    enable_helpdesk: bool = True
) -> ComprehensiveLogger:
    """
    Get comprehensive logger instance

    Args:
        name: Logger name
        project_root: Project root path
        enable_azure_monitor: Enable Azure Monitor integration
        enable_service_bus: Enable Service Bus event publishing
        enable_helpdesk: Enable helpdesk integration

    Returns:
        ComprehensiveLogger instance
    """
    return ComprehensiveLogger(
        name=name,
        project_root=project_root,
        enable_azure_monitor=enable_azure_monitor,
        enable_service_bus=enable_service_bus,
        enable_helpdesk=enable_helpdesk
    )


# Backward compatibility - enhance base logger
def get_logger(name: str, level: int = logging.INFO, comprehensive: bool = True) -> Union[logging.Logger, ComprehensiveLogger]:
    """
    Get logger - returns comprehensive logger if available, otherwise base logger

    Args:
        name: Logger name
        level: Logging level
        comprehensive: Use comprehensive logger (default: True)

    Returns:
        Logger instance
    """
    if comprehensive:
        try:
            return get_comprehensive_logger(name)
        except Exception:
            # Fallback to base logger
            if BASE_LOGGER_AVAILABLE:
                return base_get_logger(name, level)
            else:
                logger = logging.getLogger(name)
                logger.setLevel(level)
                return logger
    else:
        if BASE_LOGGER_AVAILABLE:
            return base_get_logger(name, level)
        else:
            logger = logging.getLogger(name)
            logger.setLevel(level)
            return logger


if __name__ == "__main__":
    # Demo
    print("Comprehensive Logger Demo")
    print("=" * 80)

    logger = get_comprehensive_logger("demo")
    logger.info("Info message with context", {"component": "demo", "action": "test"})
    logger.warning("Warning message", {"issue": "test_warning"})
    logger.error("Error message", {"error_code": "TEST_ERROR"})

    print("\nMetrics:")
    print(json.dumps(logger.get_metrics(), indent=2))
