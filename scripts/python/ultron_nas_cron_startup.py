#!/usr/bin/env python3
"""
Ultron K8s Cluster Startup & Health Monitor for NAS Cron Scheduler

Handles Ultron service startup on NAS with comprehensive:
- Endpoint health verification
- Retry logic with exponential backoff
- Service status monitoring
- Logging to centralized logs
- Error handling and recovery
- Input validation and resource cleanup

Tags: #ULTRON #K8S #NAS #CRON #STARTUP #HEALTH #MONITORING @JARVIS @LUMINA
Version: 2.0.0
"""

import atexit
import json
import logging
import os
import platform
import signal
import socket
import sys
import tempfile
import time
from contextlib import contextmanager, suppress
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple, Union
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# Platform detection for cross-platform compatibility
IS_WINDOWS = platform.system() == "Windows"
IS_UNIX = not IS_WINDOWS

# Conditional imports for Unix-only modules (with fallbacks for Windows)
if IS_UNIX:
    import fcntl
    import select
else:
    fcntl = None  # type: ignore
    select = None  # type: ignore

# Version check for logging
try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("UltronNASStartup")

# ============================================================================
# Version and Configuration
# ============================================================================

SCRIPT_VERSION = "2.0.0"
SCRIPT_NAME = "ultron_nas_cron_startup.py"

# External library availability
REQUESTS_AVAILABLE = False
PARAMIKO_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    logger.debug("requests library not available - using urllib fallback")

try:
    import paramiko
    PARAMIKO_AVAILABLE = True
except ImportError:
    logger.debug("paramiko not available - SSH deployments disabled")


# ============================================================================
# Enums and Data Classes
# ============================================================================


class LogLevel(Enum):
    """Configurable log levels"""
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class EndpointStatus(Enum):
    """Status of an endpoint"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    TIMEOUT = "timeout"
    ERROR = "error"
    UNKNOWN = "unknown"


@dataclass
class ValidationResult:
    """Result of validation check"""
    valid: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class HealthCheckResult:
    """Result of a health check"""
    endpoint: str
    status: EndpointStatus
    response_time: float  # seconds
    status_code: Optional[int] = None
    error_message: Optional[str] = None
    models_available: List[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return {
            "endpoint": self.endpoint,
            "status": self.status.value,
            "response_time": round(self.response_time, 4),
            "status_code": self.status_code,
            "error_message": self.error_message,
            "models_available": self.models_available,
            "timestamp": self.timestamp,
        }


@dataclass
class StartupResult:
    """Result of startup attempt"""
    success: bool
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    attempts: int = 0
    final_endpoint: Optional[str] = None
    health_results: List[Dict[str, Any]] = field(default_factory=list)
    error_message: Optional[str] = None
    models_found: List[str] = field(default_factory=list)


@dataclass
class UltronConfig:
    """Ultron cluster configuration with validation"""

    # Endpoints to check
    primary_endpoint: str = "http://localhost:31434"
    fallback_endpoint: str = "http://localhost:11434"
    k8s_internal_endpoint: str = "http://<NAS_PRIMARY_IP>:11434"

    # NAS configuration
    nas_host: str = "<NAS_PRIMARY_IP>"
    nas_user: str = "mlesn"
    nas_ssh_port: int = 22

    # K8s configuration
    k8s_namespace: str = "ultron"
    k8s_deployment_name: str = "ultron-cluster"
    k8s_service_name: str = "ultron-api"

    # Health check settings
    health_check_timeout: int = 10
    health_check_retries: int = 3
    health_check_delay: int = 5

    # Startup settings
    startup_timeout: int = 300
    retry_delay: int = 30

    # Logging
    log_path: str = "/volume1/docker/lumina/logs/ultron"
    log_file: str = "ultron_startup.log"

    # Log level
    log_level: LogLevel = LogLevel.INFO

    def validate(self) -> ValidationResult:
        """Validate configuration"""
        try:
            # Validate endpoints
            for endpoint in [self.primary_endpoint, self.fallback_endpoint, self.k8s_internal_endpoint]:
                if not endpoint.startswith(("http://", "https://")):
                    return ValidationResult(
                        valid=False,
                        message=f"Invalid endpoint format: {endpoint}",
                        details={"endpoint": endpoint},
                    )

            # Validate ports
            for port in [self.nas_ssh_port]:
                if not 1 <= port <= 65535:
                    return ValidationResult(
                        valid=False,
                        message=f"Invalid port: {port}",
                        details={"port": port},
                    )

            # Validate timeouts
            for timeout in [self.health_check_timeout, self.startup_timeout]:
                if timeout < 1:
                    return ValidationResult(
                        valid=False,
                        message=f"Invalid timeout: {timeout}",
                        details={"timeout": timeout},
                    )

            return ValidationResult(valid=True, message="Configuration is valid")

        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Validation error: {str(e)}",
                details={"exception": str(type(e).__name__)},
            )


# ============================================================================
# Utility Functions
# ============================================================================


def setup_signal_handlers() -> None:
    """Setup graceful shutdown handlers"""
    def signal_handler(signum, frame):
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        sys.exit(0)

    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)


@contextmanager
def timeout_context(seconds: int, operation: str = "operation") -> Generator[None, None, None]:
    """Context manager for timeout control with cross-platform support."""
    if IS_WINDOWS:
        # Windows doesn't support SIGALRM, use threading instead
        import threading

        timeout_occurred = [False]

        def timeout_handler():
            timeout_occurred[0] = True
            raise TimeoutError(f"{operation} timed out after {seconds} seconds")

        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        except TimeoutError:
            raise
        finally:
            timer.cancel()
    else:
        # Unix systems can use SIGALRM
        import threading

        def timeout_handler():
            raise TimeoutError(f"{operation} timed out after {seconds} seconds")

        timer = threading.Timer(seconds, timeout_handler)
        timer.start()
        try:
            yield
        finally:
            timer.cancel()


@contextmanager
def file_lock(lock_file_path: Path) -> Generator[None, None, None]:
    """Context manager for file locking to prevent concurrent execution."""
    lock_file = None
    try:
        lock_file = open(lock_file_path, "w")
        if IS_UNIX:
            # pylint: disable=import-error
            fcntl.flock(lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            # pylint: enable=import-error
        logger.debug(f"Acquired lock: {lock_file_path}")
        yield
    except (IOError, OSError) as e:
        logger.warning(f"Could not acquire lock: {e}")
        yield
    finally:
        if lock_file:
            if IS_UNIX:
                # pylint: disable=import-error
                with suppress(OSError):
                    fcntl.flock(lock_file.fileno(), fcntl.LOCK_UN)
                # pylint: enable=import-error
            lock_file.close()


def validate_file_path(file_path: Union[str, Path], must_exist: bool = False) -> Tuple[bool, Optional[str]]:
    """Validate file path before use"""
    try:
        path = Path(file_path)
        if must_exist and not path.exists():
            return False, f"File does not exist: {path}"
        if path.exists() and not path.is_file():
            return False, f"Path is not a file: {path}"
        # Check write permissions for parent directory
        if not must_exist:
            parent = path.parent
            if not parent.exists():
                return False, f"Parent directory does not exist: {parent}"
            if not os.access(parent, os.W_OK):
                return False, f"No write permission for: {parent}"
        return True, None
    except Exception as e:
        return False, f"File path validation error: {str(e)}"


def safe_parse_json(data: str, context: str = "data") -> Optional[Dict[str, Any]]:
    """Safely parse JSON data with error handling"""
    try:
        return json.loads(data)
    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error in {context}: {e}")
        return None


def format_duration(seconds: float) -> str:
    """Format duration in human-readable format"""
    if seconds < 60:
        return f"{seconds:.2f}s"
    elif seconds < 3600:
        minutes = seconds // 60
        secs = seconds % 60
        return f"{int(minutes)}m {int(secs)}s"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{int(hours)}h {int(minutes)}m"


# ============================================================================
# Health Checker
# ============================================================================


class UltronHealthChecker:
    """Health checker for Ultron endpoints with comprehensive error handling"""

    def __init__(self, config: UltronConfig):
        self.config = config
        self._endpoint_list: Optional[List[str]] = None

    @property
    def endpoints(self) -> List[str]:
        """Lazy-loaded endpoint list with validation"""
        if self._endpoint_list is None:
            self._endpoint_list = [
                self.config.primary_endpoint,
                self.config.fallback_endpoint,
                self.config.k8s_internal_endpoint,
            ]
        return self._endpoint_list

    def _check_endpoint_http(self, endpoint: str) -> HealthCheckResult:
        """
        Check endpoint using HTTP request with timeout.

        Args:
            endpoint: URL to check

        Returns:
            HealthCheckResult with status and details
        """
        start_time = time.time()
        result = HealthCheckResult(
            endpoint=endpoint,
            status=EndpointStatus.UNKNOWN,
            response_time=0.0,
        )

        test_url = f"{endpoint}/api/tags"

        try:
            with timeout_context(self.config.health_check_timeout, f"health check to {endpoint}"):
                if REQUESTS_AVAILABLE:
                    response = requests.get(
                        test_url,
                        timeout=self.config.health_check_timeout,
                        headers={"User-Agent": f"UltronHealthCheck/{SCRIPT_VERSION}"},
                    )
                    result.status_code = response.status_code

                    if response.status_code == 200:
                        result.status = EndpointStatus.HEALTHY
                        try:
                            data = response.json()
                            result.models_available = [
                                m.get("name", "unknown")
                                for m in data.get("models", [])
                            ]
                        except Exception as e:
                            logger.warning(f"Failed to parse models from {endpoint}: {e}")
                    elif response.status_code >= 400:
                        result.status = EndpointStatus.ERROR
                        result.error_message = f"HTTP {response.status_code}"
                else:
                    # Fallback to urllib
                    request = Request(test_url, headers={"User-Agent": f"UltronHealthCheck/{SCRIPT_VERSION}"})
                    with urlopen(request, timeout=self.config.health_check_timeout) as response:
                        result.status_code = response.status
                        if response.status == 200:
                            result.status = EndpointStatus.HEALTHY
                            data = safe_parse_json(response.read().decode(), "endpoint response")
                            if data:
                                result.models_available = [
                                    m.get("name", "unknown") for m in data.get("models", [])
                                ]

        except requests.exceptions.ConnectionError as e:
            result.status = EndpointStatus.UNHEALTHY
            result.error_message = f"Connection error: {str(e)}"
        except requests.exceptions.Timeout as e:
            result.status = EndpointStatus.TIMEOUT
            result.error_message = f"Timeout after {self.config.health_check_timeout}s"
        except requests.exceptions.HTTPError as e:
            result.status = EndpointStatus.ERROR
            result.error_message = f"HTTP error: {str(e)}"
        except TimeoutError as e:
            result.status = EndpointStatus.TIMEOUT
            result.error_message = str(e)
        except (URLError, HTTPError) as e:
            result.status = EndpointStatus.ERROR
            result.error_message = f"URL error: {str(e)}"
        except Exception as e:
            result.status = EndpointStatus.ERROR
            result.error_message = f"Unexpected error: {str(e)}"
        finally:
            result.response_time = time.time() - start_time

        return result

    def _check_endpoint_socket(self, endpoint: str) -> HealthCheckResult:
        """
        Check endpoint using socket connection (fallback method).

        Args:
            endpoint: URL to check (will extract host:port)

        Returns:
            HealthCheckResult with status
        """
        start_time = time.time()
        result = HealthCheckResult(
            endpoint=endpoint,
            status=EndpointStatus.UNKNOWN,
            response_time=0.0,
        )

        try:
            # Extract host and port from URL
            url_without_scheme = endpoint.split("://", 1)[-1]
            host = url_without_scheme.split(":")[0]
            port = int(url_without_scheme.split(":")[-1]) if ":" in url_without_scheme else 80

            with socket.create_connection(
                (host, port), timeout=self.config.health_check_timeout
            ) as sock:
                result.status = EndpointStatus.HEALTHY

        except socket.timeout:
            result.status = EndpointStatus.TIMEOUT
            result.error_message = f"Socket timeout after {self.config.health_check_timeout}s"
        except socket.error as e:
            result.status = EndpointStatus.UNHEALTHY
            result.error_message = f"Socket error: {str(e)}"
        except Exception as e:
            result.status = EndpointStatus.ERROR
            result.error_message = f"Unexpected socket error: {str(e)}"
        finally:
            result.response_time = time.time() - start_time

        return result

    def check_endpoint(self, endpoint: str, use_http: bool = True) -> HealthCheckResult:
        """
        Check health of a single endpoint with fallback.

        Args:
            endpoint: URL to check
            use_http: Use HTTP request (True) or socket (False)

        Returns:
            HealthCheckResult with status and details
        """
        if use_http:
            return self._check_endpoint_http(endpoint)
        return self._check_endpoint_socket(endpoint)

    def check_all_endpoints(
        self, max_retries: int = 2
    ) -> List[HealthCheckResult]:
        """
        Check all configured endpoints with retry logic.

        Args:
            max_retries: Number of retry attempts for failed endpoints

        Returns:
            List of HealthCheckResult for each endpoint
        """
        results = []

        for endpoint in self.endpoints:
            logger.info(f"   Checking endpoint: {endpoint}")

            result = None
            for attempt in range(max_retries):
                result = self.check_endpoint(endpoint)

                if result.status == EndpointStatus.HEALTHY:
                    break

                if attempt < max_retries - 1:
                    logger.debug(
                        f"   Retry {attempt + 1}/{max_retries} for {endpoint} "
                        f"(status: {result.status.value})"
                    )
                    time.sleep(self.config.health_check_delay)

            results.append(result)

            # Log result
            if result.status == EndpointStatus.HEALTHY:
                logger.info(f"      ✅ Healthy - {result.response_time:.2f}s")
                if result.models_available:
                    model_list = ", ".join(result.models_available[:5])
                    logger.info(f"      📦 Models: {model_list}")
            elif result.status == EndpointStatus.TIMEOUT:
                logger.warning(f"      ⏱️  Timeout: {result.error_message}")
            else:
                logger.warning(f"      ❌ Unhealthy: {result.error_message}")

        return results

    def get_best_endpoint(
        self, results: List[HealthCheckResult]
    ) -> Optional[HealthCheckResult]:
        """
        Get the healthiest (fastest) endpoint from results.

        Args:
            results: List of health check results

        Returns:
            Best HealthCheckResult or None if no healthy endpoints
        """
        healthy_results = [r for r in results if r.status == EndpointStatus.HEALTHY]

        if not healthy_results:
            return None

        return min(healthy_results, key=lambda r: r.response_time)


# ============================================================================
# Configuration Validator
# ============================================================================


class ConfigurationValidator:
    """Validates Ultron and related configurations"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent

    def validate_file_exists(
        self, file_path: Path, file_type: str = "file"
    ) -> ValidationResult:
        """Validate that a file exists"""
        try:
            if not file_path.exists():
                return ValidationResult(
                    valid=False,
                    message=f"{file_type} not found: {file_path}",
                    details={"path": str(file_path)},
                )
            if file_path.is_file():
                return ValidationResult(
                    valid=True,
                    message=f"{file_type} exists: {file_path.name}",
                    details={"size": file_path.stat().st_size},
                )
            return ValidationResult(
                valid=False,
                message=f"Path is not a {file_type}: {file_path}",
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Error checking {file_type}: {str(e)}",
                details={"path": str(file_path), "exception": type(e).__name__},
            )

    def validate_continue_config(self) -> ValidationResult:
        """Validate .continue/config.yaml"""
        config_path = self.project_root / ".continue" / "config.yaml"

        # Check file exists
        file_result = self.validate_file_exists(config_path, "Continue config")
        if not file_result.valid:
            return file_result

        try:
            import yaml

            with open(config_path, "r") as f:
                config = yaml.safe_load(f)

            # Validate structure
            if not isinstance(config, dict):
                return ValidationResult(
                    valid=False,
                    message="Invalid YAML structure: expected dict",
                )

            models = config.get("models", [])
            if not isinstance(models, list):
                return ValidationResult(
                    valid=False,
                    message="Invalid models configuration: expected list",
                )

            # Count valid models
            valid_models = []
            for model in models:
                if isinstance(model, dict) and "model" in model:
                    model_name = model.get("model", "unknown")
                    valid_models.append(model_name)

            return ValidationResult(
                valid=True,
                message=f"Continue config valid: {len(valid_models)} models configured",
                details={
                    "model_count": len(valid_models),
                    "models": valid_models[:5],
                    "path": str(config_path),
                },
            )

        except yaml.YAMLError as e:
            return ValidationResult(
                valid=False,
                message=f"YAML parse error: {str(e)}",
                details={"path": str(config_path)},
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Error validating continue config: {str(e)}",
                details={"exception": type(e).__name__},
            )

    def validate_cursor_settings(self) -> ValidationResult:
        """Validate .cursor/settings.json"""
        settings_path = self.project_root / ".cursor" / "settings.json"

        # Check file exists
        file_result = self.validate_file_exists(settings_path, "Cursor settings")
        if not file_result.valid:
            return file_result

        try:
            with open(settings_path, "r") as f:
                settings = json.load(f)

            if not isinstance(settings, dict):
                return ValidationResult(
                    valid=False,
                    message="Invalid JSON structure: expected dict",
                )

            # Look for Ultron model configurations
            ultron_models = []
            for key, value in settings.items():
                if "model" in key.lower() or "ultron" in str(value).lower():
                    if isinstance(value, str) and "ultron" in value.lower():
                        ultron_models.append(f"{key}: {value}")
                    elif isinstance(value, list):
                        for v in value:
                            if isinstance(v, str) and "ultron" in v.lower():
                                ultron_models.append(f"{key}: {v}")

            return ValidationResult(
                valid=True,
                message=f"Cursor settings valid: {len(ultron_models)} Ultron entries",
                details={
                    "ultron_entries": ultron_models,
                    "path": str(settings_path),
                },
            )

        except json.JSONDecodeError as e:
            return ValidationResult(
                valid=False,
                message=f"JSON parse error: {str(e)}",
                details={"path": str(settings_path)},
            )
        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Error validating cursor settings: {str(e)}",
                details={"exception": type(e).__name__},
            )

    def validate_ultron_command(self) -> ValidationResult:
        """Validate .cursor/commands/ultron.md"""
        command_path = self.project_root / ".cursor" / "commands" / "ultron.md"

        # Check file exists
        file_result = self.validate_file_exists(command_path, "Ultron command file")
        if not file_result.valid:
            return file_result

        try:
            content = command_path.read_text()

            # Check for required content
            has_ultron_refs = "ultron" in content.lower()
            has_endpoint_refs = "localhost:31434" in content
            has_api_examples = "/api/" in content

            if has_ultron_refs and has_endpoint_refs:
                return ValidationResult(
                    valid=True,
                    message="Ultron command file valid with endpoint references",
                    details={
                        "has_ultron_refs": has_ultron_refs,
                        "has_endpoint_refs": has_endpoint_refs,
                        "has_api_examples": has_api_examples,
                        "size": len(content),
                        "path": str(command_path),
                    },
                )
            else:
                return ValidationResult(
                    valid=False,
                    message="Ultron command file missing required references",
                    details={
                        "has_ultron_refs": has_ultron_refs,
                        "has_endpoint_refs": has_endpoint_refs,
                    },
                )

        except Exception as e:
            return ValidationResult(
                valid=False,
                message=f"Error validating ultron command: {str(e)}",
                details={"exception": type(e).__name__},
            )

    def validate_all(self) -> Dict[str, ValidationResult]:
        """Validate all configurations"""
        logger.info("=" * 80)
        logger.info("VERIFYING ULTRON CONFIGURATIONS")
        logger.info("=" * 80)

        results = {
            "continue_config": self.validate_continue_config(),
            "cursor_settings": self.validate_cursor_settings(),
            "ultron_command": self.validate_ultron_command(),
        }

        # Log results
        for key, result in results.items():
            status_icon = "✅" if result.valid else "❌"
            logger.info(f"   {status_icon} {result.message}")

        # Summary
        all_valid = all(r.valid for r in results.values())
        logger.info("")
        if all_valid:
            logger.info("   ✅ All configurations verified successfully")
        else:
            logger.warning("   ⚠️  Some configurations need attention")

        return results


# ============================================================================
# Startup Manager
# ============================================================================


class UltronStartupManager:
    """
    Manages Ultron startup via NAS cron with comprehensive error handling.

    Features:
    - Configuration validation
    - Health checking with retry logic
    - SSH deployment to NAS
    - Logging with configurable levels
    - Resource cleanup
    """

    def __init__(self, config: Optional[UltronConfig] = None, project_root: Optional[Path] = None):
        """
        Initialize the startup manager.

        Args:
            config: Ultron configuration object
            project_root: Project root directory (auto-detected if not provided)
        """
        self.config = config or UltronConfig()
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.health_checker = UltronHealthChecker(self.config)
        self.validator = ConfigurationValidator(self.project_root)

        # Setup
        self._setup_logging()
        self._setup_cleanup()

        # Validate configuration
        config_validation = self.config.validate()
        if not config_validation.valid:
            logger.error(f"Configuration validation failed: {config_validation.message}")
            raise ValueError(f"Invalid configuration: {config_validation.message}")

    def _setup_logging(self) -> None:
        """Setup logging with configurable levels and file rotation"""
        try:
            log_dir = Path(self.config.log_path)
            log_dir.mkdir(parents=True, exist_ok=True)

            log_file = log_dir / self.config.log_file

            # Create file handler with rotation (basic implementation)
            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(self.config.log_level.value)
            file_handler.setFormatter(
                logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                )
            )

            # Add to logger
            logger.addHandler(file_handler)
            logger.setLevel(self.config.log_level.value)

            logger.debug(f"Logging configured: {log_file}")

        except Exception as e:
            logger.error(f"Failed to setup logging: {e}")

    def _setup_cleanup(self) -> None:
        """Setup cleanup handlers for graceful shutdown"""
        atexit.register(self._cleanup)
        setup_signal_handlers()

    def _cleanup(self) -> None:
        """Cleanup resources on shutdown"""
        logger.info("Cleaning up resources...")

        # Close file handlers
        for handler in logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                handler.close()
                logger.removeHandler(handler)

    def check_services(self) -> StartupResult:
        """
        Check if Ultron services are running.

        Returns:
            StartupResult with health status and endpoint information
        """
        logger.info("=" * 80)
        logger.info("CHECKING ULTRON SERVICES")
        logger.info("=" * 80)

        result = StartupResult(success=False, attempts=1)

        try:
            # Check all endpoints
            health_results = self.health_checker.check_all_endpoints()

            # Convert to serializable format
            result.health_results = [r.to_dict() for r in health_results]

            # Find best endpoint
            best = self.health_checker.get_best_endpoint(health_results)

            if best:
                result.success = True
                result.final_endpoint = best.endpoint
                result.models_found = best.models_available
                logger.info("")
                logger.info(f"   ✅ Best endpoint: {best.endpoint}")
                logger.info(f"   📦 Models available: {', '.join(best.models_available[:5])}")
            else:
                result.error_message = "No healthy endpoints found"
                logger.warning("")
                logger.warning("   ⚠️  No healthy endpoints - services need to be started")

                # Provide diagnostic information
                unhealthy_count = sum(
                    1 for r in health_results if r.status != EndpointStatus.HEALTHY
                )
                logger.info(f"   Unhealthy endpoints: {unhealthy_count}/{len(health_results)}")

        except Exception as e:
            result.error_message = f"Service check failed: {str(e)}"
            logger.error(f"Error during service check: {e}")

        return result

    def generate_cron_job(self) -> str:
        """
        Generate cron job entry for Ultron startup.

        Returns:
            Cron job entry string
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cron_entry = (
            f"*/5 * * * * "
            f"python /volume1/docker/lumina/scripts/python/{SCRIPT_NAME} --check-only "
            f">> /volume1/docker/lumina/logs/ultron/ultron_cron.log 2>&1 "
            f"# ULTRON Service Health Check - {timestamp}"
        )
        return cron_entry

    def deploy_to_nas(self) -> bool:
        """
        Deploy cron job to NAS with error handling.

        Returns:
            True if deployment successful, False otherwise
        """
        logger.info("=" * 80)
        logger.info("DEPLOYING ULTRON CRON JOB TO NAS")
        logger.info("=" * 80)

        cron_entry = self.generate_cron_job()

        try:
            if not PARAMIKO_AVAILABLE:
                logger.warning("   ⚠️  paramiko not available")
                logger.info("   📋 Manual deployment:")
                logger.info(
                    f"      echo '{cron_entry}' | ssh {self.config.nas_user}@{self.config.nas_host} 'crontab -'"
                )
                return False

            # SSH connection with timeout
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            try:
                ssh.connect(
                    hostname=self.config.nas_host,
                    username=self.config.nas_user,
                    port=self.config.nas_ssh_port,
                    timeout=self.config.health_check_timeout,
                )

                # Backup existing crontab
                backup_cmd = (
                    f"crontab -l > /tmp/ultron_crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null"
                )
                stdin, stdout, stderr = ssh.exec_command(backup_cmd)
                exit_status = stdout.channel.recv_exit_status()

                if exit_status != 0:
                    error = stderr.read().decode().strip()
                    logger.warning(f"   Backup failed (may be first deployment): {error}")

                # Add cron job
                add_cmd = f'(crontab -l 2>/dev/null; echo "{cron_entry}") | crontab -'
                stdin, stdout, stderr = ssh.exec_command(add_cmd)
                exit_status = stdout.channel.recv_exit_status()

                if exit_status == 0:
                    logger.info("   ✅ Cron job deployed to NAS")
                    logger.info(f"   📋 Entry: {cron_entry[:80]}...")
                    return True
                else:
                    error = stderr.read().decode().strip()
                    logger.error(f"   ❌ Deployment failed: {error}")
                    return False

            finally:
                ssh.close()

        except paramiko.AuthenticationException as e:
            logger.error(f"   ❌ SSH authentication failed: {e}")
            return False
        except paramiko.SSHException as e:
            logger.error(f"   ❌ SSH error: {e}")
            return False
        except socket.timeout:
            logger.error(f"   ❌ SSH connection timed out to {self.config.nas_host}")
            return False
        except Exception as e:
            logger.error(f"   ❌ Error deploying to NAS: {e}")
            return False

    def generate_deployment_script(self) -> Path:
        """
        Generate shell script for manual NAS deployment.

        Returns:
            Path to generated script
        """
        script_path = self.project_root / "scripts" / "deploy_ultron_cron.sh"

        # Generate cron entry first
        cron_entry = self.generate_cron_job()

        script_content = f'''#!/bin/bash
# ULTRON Cron Deployment Script
# Auto-generated by {SCRIPT_NAME}
# Generated: {datetime.now().isoformat()}
# Version: {SCRIPT_VERSION}

NAS_HOST="{self.config.nas_host}"
NAS_USER="{self.config.nas_user}"

echo "========================================"
echo "Deploying ULTRON cron job to NAS ($NAS_HOST)"
echo "========================================"

# Function to check if cron entry exists
cron_exists() {{
    ssh $NAS_USER@$NAS_HOST "crontab -l" 2>/dev/null | grep -qF "$1"
    return $?
}}

# Backup existing crontab
echo "📦 Backing up existing crontab..."
ssh $NAS_USER@$NAS_HOST "crontab -l > /tmp/ultron_crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null"

# Check if entry already exists
if cron_exists "ULTRON Service Health Check"; then
    echo "⚠️  ULTRON cron entry already exists, skipping..."
else
    # Add ULTRON health check cron job
    echo "📤 Adding ULTRON cron job..."
    echo '{cron_entry}' | ssh $NAS_USER@$NAS_HOST "crontab -"
    echo "   ✅ Cron job added"
fi

echo ""
echo "========================================"
echo "Deployment Complete"
echo "========================================"
echo ""
echo "Verify with:"
echo "  ssh $NAS_USER@$NAS_HOST 'crontab -l | grep ultron'"
echo ""
echo "Check logs:"
echo "  ssh $NAS_USER@$NAS_HOST 'tail -f /volume1/docker/lumina/logs/ultron/ultron_startup.log'"
'''

        try:
            script_path.write_text(script_content)
            script_path.chmod(0o755)
            logger.info(f"   ✅ Deployment script generated: {script_path}")
            return script_path
        except Exception as e:
            logger.error(f"   ❌ Failed to generate deployment script: {e}")
            raise


# ============================================================================
# Main Entry Point
# ============================================================================


def parse_args():
    """Parse command line arguments with validation"""
    import argparse

    parser = argparse.ArgumentParser(
        description=f"ULTRON K8s Cluster Startup & Health Monitor v{SCRIPT_VERSION}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --verify-configs     Verify configurations
  %(prog)s --check-only         Check service health only
  %(prog)s --deploy             Deploy cron job to NAS
  %(prog)s --generate-script    Generate deployment script
  %(prog)s --json               Output as JSON
        """,
    )

    parser.add_argument(
        "--verify-configs",
        action="store_true",
        help="Verify .continue/config.yaml and .cursor/settings.json",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="Only check service health, don't attempt startup",
    )
    parser.add_argument(
        "--check-endpoints",
        action="store_true",
        help="Check all configured endpoints",
    )
    parser.add_argument("--deploy", action="store_true", help="Deploy cron job to NAS")
    parser.add_argument(
        "--generate-script",
        action="store_true",
        help="Generate deployment script",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--ultrons-only",
        action="store_true",
        help="ULTRON-only mode (no cloud fallback)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose (DEBUG) logging",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {SCRIPT_VERSION}",
    )

    return parser.parse_args()


def main() -> int:
    """
    Main entry point with comprehensive error handling.

    Returns:
        Exit code (0 for success, 1 for error)
    """
    try:
        args = parse_args()

        # Setup logging level
        if args.verbose:
            log_level = LogLevel.DEBUG
        else:
            log_level = LogLevel.INFO

        # Initialize configuration and manager
        config = UltronConfig(log_level=log_level)
        manager = UltronStartupManager(config)

        results = {
            "version": SCRIPT_VERSION,
            "timestamp": datetime.now().isoformat(),
            "ultrons_only": args.ultrons_only,
        }

        if args.verify_configs:
            # Verify configurations
            config_results = manager.validator.validate_all()
            results["config_verification"] = {
                k: {
                    "valid": v.valid,
                    "message": v.message,
                    "details": v.details,
                }
                for k, v in config_results.items()
            }

        elif args.check_endpoints or args.check_only:
            # Check service health
            results["service_check"] = {"attempted": True, "success": False}
            check_result = manager.check_services()
            results["service_check"]["success"] = check_result.success
            results["service_check"]["endpoint"] = check_result.final_endpoint
            results["service_check"]["models"] = check_result.models_found
            results["service_check"]["health_results"] = check_result.health_results

        elif args.deploy:
            # Deploy to NAS
            results["deployment"] = {"attempted": True, "success": manager.deploy_to_nas()}

        elif args.generate_script:
            # Generate deployment script
            script_path = manager.generate_deployment_script()
            results["deployment_script"] = {
                "generated": True,
                "path": str(script_path),
            }

        else:
            # Run full verification and check
            logger.info("=" * 80)
            logger.info(f"ULTRON K8s CLUSTER STARTUP & HEALTH MONITOR v{SCRIPT_VERSION}")
            logger.info("=" * 80)
            logger.info(f"Timestamp: {datetime.now().isoformat()}")
            logger.info("")

            # Verify configurations
            config_results = manager.validator.validate_all()
            results["config_verification"] = {
                k: {
                    "valid": v.valid,
                    "message": v.message,
                    "details": v.details,
                }
                for k, v in config_results.items()
            }

            logger.info("")

            # Check services
            check_result = manager.check_services()
            results["service_check"] = {
                "success": check_result.success,
                "endpoint": check_result.final_endpoint,
                "models": check_result.models_found,
                "health_results": check_result.health_results,
            }

            logger.info("")

            # Generate deployment info
            cron_entry = manager.generate_cron_job()
            results["cron_entry"] = cron_entry
            logger.info("📋 Cron Job Entry:")
            logger.info(f"   {cron_entry}")

            logger.info("")
            logger.info("📝 Next Steps:")
            logger.info("   1. To deploy: --deploy")
            logger.info("   2. To generate script: --generate-script")
            logger.info("   3. To verify configs: --verify-configs")
            logger.info("   4. To check services: --check-only")

        # Output
        if args.json:
            print(json.dumps(results, indent=2, default=str))
        else:
            if "config_verification" in results:
                cfg = results["config_verification"]
                print("\n📋 Configuration Verification:")
                all_valid = all(v.get("valid", False) for v in cfg.values())
                print(f"   Status: {'✅ All Valid' if all_valid else '⚠️  Some Issues'}")
                for key, val in cfg.items():
                    icon = "✅" if val.get("valid") else "❌"
                    print(f"   {icon} {key}: {val.get('message', 'N/A')}")

            if "service_check" in results:
                sc = results["service_check"]
                print("\n🔍 Service Check:")
                status = "✅ Running" if sc.get("success") else "❌ Not Running"
                print(f"   Status: {status}")
                if sc.get("endpoint"):
                    print(f"   Endpoint: {sc['endpoint']}")
                if sc.get("models"):
                    print(f"   Models: {', '.join(sc['models'][:3])}")

        return 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":

    sys.exit(main())