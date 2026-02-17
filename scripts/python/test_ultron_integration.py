#!/usr/bin/env python3
"""
Ultron AI Assistant Integration Test Script

Tests connectivity and validates configurations for:
- Continue configuration (.continue/config.yaml)
- Cursor settings (.cursor/settings.json)
- Ultron endpoints (localhost:31434, localhost:11434)
- Model status tracking

Usage: python scripts/python/test_ultron_integration.py
"""

import json
import sys
import logging
from pathlib import Path
from typing import Dict, Tuple

# PyYAML availability check for YAML config parsing
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False
    logging.basicConfig(level=logging.WARNING, format='%(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)
    logger.warning("PyYAML not installed. YAML config parsing disabled.")

# Configuration
WORKSPACE_ROOT = Path(__file__).parent.parent.parent
CONTINUE_CONFIG = WORKSPACE_ROOT / ".continue" / "config.yaml"
CURSOR_SETTINGS = WORKSPACE_ROOT / ".cursor" / "settings.json"
ULTRON_COMMAND_FILE = WORKSPACE_ROOT / ".cursor" / "commands" / "ultron.md"

# Endpoints to test
ENDPOINTS = [
    ("Ultron Cluster (Primary)", "http://localhost:31434"),
    ("Local Ollama Fallback", "http://localhost:11434"),
    ("K8s Internal", "http://<NAS_PRIMARY_IP>:11434"),
]


class Colors:
    """ANSI color codes for terminal output"""

    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    BOLD = "\033[1m"
    RESET = "\033[0m"


def print_header(text: str) -> None:
    """Print a formatted header"""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.RESET}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'=' * 60}{Colors.RESET}\n")


def print_success(text: str) -> None:
    """Print a success message"""
    print(f"{Colors.GREEN}✓{Colors.RESET} {text}")


def print_warning(text: str) -> None:
    """Print a warning message"""
    print(f"{Colors.YELLOW}⚠{Colors.RESET} {text}")


def print_error(text: str) -> None:
    """Print an error message"""
    print(f"{Colors.RED}✗{Colors.RESET} {text}")


def print_info(text: str) -> None:
    """Print an info message"""
    print(f"{Colors.BLUE}ℹ{Colors.RESET} {text}")


def test_file_exists(file_path: Path, description: str) -> bool:
    try:
        """Test if a file exists"""
        if file_path.exists():
            print_success(f"{description}: {file_path}")
            return True
        else:
            print_error(f"{description} not found: {file_path}")
            return False


    except Exception as e:
        logger.error(f"Error in test_file_exists: {e}", exc_info=True)
        raise
def test_continue_config() -> Tuple[bool, Dict]:
    """Test the Continue configuration file"""
    print_header("Testing Continue Configuration (.continue/config.yaml)")

    result = {
        "file_exists": False,
        "valid_yaml": False,
        "models_count": 0,
        "ultron_endpoint": None,
        "fallback_endpoint": None,
        "models": [],
    }

    if not test_file_exists(CONTINUE_CONFIG, "Continue config file"):
        return False, result

    result["file_exists"] = True

    if not HAS_YAML:
        print_warning("PyYAML not installed. Skipping YAML config validation.")
        result["valid_yaml"] = False
        return False, result

    try:
        with open(CONTINUE_CONFIG) as f:
            config = yaml.safe_load(f)

        result["valid_yaml"] = True
        print_success("Valid YAML format")

        # Count models
        models = config.get("models", [])
        result["models_count"] = len(models)
        print_success(f"Found {len(models)} configured models")

        # Check for Ultron endpoint
        for model in models:
            model_name = model.get("name", "Unknown")
            api_base = model.get("apiBase", "")
            result["models"].append({"name": model_name, "apiBase": api_base})

            if "31434" in api_base:
                result["ultron_endpoint"] = api_base
                print_success(f"Ultron model: {model_name} -> {api_base}")

            if "11434" in api_base and "31434" not in api_base:
                result["fallback_endpoint"] = api_base
                print_warning(f"Fallback model: {model_name} -> {api_base}")

        return True, result

    except Exception as e:
        print_error(f"Failed to parse YAML: {e}")
        return False, result


def test_cursor_settings() -> Tuple[bool, Dict]:
    """Test the Cursor settings file"""
    print_header("Testing Cursor Settings (.cursor/settings.json)")

    result = {
        "file_exists": False,
        "valid_json": False,
        "ultron_models_count": 0,
        "default_model": None,
        "local_only": False,
        "cloud_blocked": False,
    }

    if not test_file_exists(CURSOR_SETTINGS, "Cursor settings file"):
        return False, result

    result["file_exists"] = True

    try:
        with open(CURSOR_SETTINGS) as f:
            settings = json.load(f)

        result["valid_json"] = True
        print_success("Valid JSON format")

        # Check for ULTRON models
        custom_models = settings.get("cursor.model", {}).get("customModels", [])
        chat_models = settings.get("cursor.chat.customModels", [])
        composer_models = settings.get("cursor.composer.customModels", [])
        agent_models = settings.get("cursor.agent.customModels", [])

        all_ultron_models = custom_models + chat_models + composer_models + agent_models
        ultron_count = len(
            set(m.get("name") for m in all_ultron_models if "ULTRON" in m.get("name", "").upper())
        )

        result["ultron_models_count"] = ultron_count
        print_success(f"Found {ultron_count} unique ULTRON models configured")

        # Check default model
        default_model = settings.get("cursor.chat.defaultModel")
        if default_model:
            result["default_model"] = default_model
            print_success(f"Default chat model: {default_model}")

        # Check local-only settings
        local_only = settings.get("cursor.agent.localOnly", False)
        result["local_only"] = local_only
        if local_only:
            print_success("Local-only mode enabled for agent")
        else:
            print_warning("Local-only mode not enabled for agent")

        # Check cloud blocking
        block_cloud = settings.get("cursor.agent.blockCloudModels", False)
        result["cloud_blocked"] = block_cloud
        if block_cloud:
            print_success("Cloud models blocked for agent")
        else:
            print_warning("Cloud models not blocked for agent")

        # Check endpoint configuration
        ultron_config = settings.get("ultron", {})
        if ultron_config:
            endpoint = ultron_config.get("endpoint")
            print_success(f"Ultron endpoint configured: {endpoint}")

        return True, result

    except Exception as e:
        print_error(f"Failed to parse JSON: {e}")
        return False, result


def test_ultron_command_file() -> Tuple[bool, Dict]:
    """Test the Ultron command file"""
    print_header("Testing Ultron Command File (.cursor/commands/ultron.md)")

    result = {
        "file_exists": False,
        "file_size": 0,
        "has_architecture": False,
        "has_api_examples": False,
        "has_kubectl_commands": False,
        "keywords_found": [],
    }

    if not test_file_exists(ULTRON_COMMAND_FILE, "Ultron command file"):
        return False, result

    result["file_exists"] = True

    try:
        with open(ULTRON_COMMAND_FILE) as f:
            content = f.read()

        result["file_size"] = len(content)
        print_success(f"File size: {len(content)} bytes")

        # Check for key sections
        checks = [
            ("Architecture diagram", "has_architecture", "ULTRON Architecture"),
            ("API examples", "has_api_examples", "API Access"),
            ("kubectl commands", "has_kubectl_commands", "kubectl Commands"),
            ("Command syntax", "has_kubectl_commands", "Command Syntax"),
        ]

        for desc, key, keyword in checks:
            if keyword.lower() in content.lower():
                result[key] = True
                print_success(f"Found: {desc}")
            else:
                print_warning(f"Missing: {desc}")

        # Check for keywords
        keywords = ["@ULTRON", "localhost:31434", "ollama", "kubernetes"]
        for keyword in keywords:
            if keyword in content:
                result["keywords_found"].append(keyword)
                print_success(f"Found keyword: {keyword}")

        return True, result

    except Exception as e:
        print_error(f"Failed to read file: {e}")
        return False, result


def test_endpoint_connectivity() -> Tuple[bool, Dict]:
    """Test connectivity to Ultron endpoints"""
    print_header("Testing Endpoint Connectivity")

    result = {"endpoints_tested": 0, "endpoints_reachable": 0, "details": {}}

    import socket

    for name, endpoint in ENDPOINTS:
        result["endpoints_tested"] += 1
        detail = {"name": name, "endpoint": endpoint, "reachable": False, "error": None}

        # Extract host and port from endpoint
        try:
            from urllib.parse import urlparse

            parsed = urlparse(endpoint)
            host = parsed.hostname
            port = parsed.port

            # Try socket connection
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            sock.connect((host, port))
            sock.close()

            detail["reachable"] = True
            result["endpoints_reachable"] += 1
            print_success(f"{name}: {endpoint} - REACHABLE")

        except Exception as e:
            detail["error"] = str(e)
            print_warning(f"{name}: {endpoint} - NOT REACHABLE ({type(e).__name__})")

        result["details"][name] = detail

    return result["endpoints_reachable"] > 0, result


def test_model_status_tracking() -> Tuple[bool, Dict]:
    """Test model status tracking configuration"""
    print_header("Testing Model Status Tracking")

    result = {"status_file_exists": False, "extension_configured": False, "tracking_enabled": False}

    # Check if model status file location exists
    status_file = WORKSPACE_ROOT / "data" / "cursor_active_model_status.json"
    result["status_file_exists"] = status_file.exists()
    if status_file.exists():
        print_success(f"Model status file exists: {status_file}")
    else:
        print_info("Model status file not yet created (will be created by tracker script)")

    # Check VS Code extension configuration
    try:
        package_json = WORKSPACE_ROOT / "vscode-extensions" / "lumina-complete" / "package.json"
        if package_json.exists():
            with open(package_json) as f:
                package = json.load(f)

            # Check for activeModelStatus commands
            commands = package.get("contributions", {}).get("commands", [])
            has_model_status = any("activeModelStatus" in c.get("command", "") for c in commands)

            if has_model_status:
                result["extension_configured"] = True
                print_success("Active model status extension commands configured")
            else:
                print_warning("Active model status commands not found in extension")
    except Exception as e:
        print_warning(f"Could not check extension configuration: {e}")

    return result["extension_configured"], result


def generate_report(
    continue_result, cursor_result, ultron_result, connectivity_result, tracking_result
) -> None:
    """Generate a summary report"""
    print_header("Test Summary Report")

    # Calculate overall status
    all_passed = continue_result[0] and cursor_result[0] and ultron_result[0]

    if all_passed:
        print_success("All configuration tests PASSED")
    else:
        print_warning("Some configuration tests need attention")

    # Configuration status
    print("\nConfiguration Status:")
    print(f"  • Continue Config: {'✓ Valid' if continue_result[0] else '✗ Invalid'}")
    print(f"  • Cursor Settings: {'✓ Valid' if cursor_result[0] else '✗ Invalid'}")
    print(f"  • Ultron Command File: {'✓ Valid' if ultron_result[0] else '✗ Invalid'}")

    # Connectivity status
    print("\nConnectivity Status:")
    reachable = connectivity_result[1].get("endpoints_reachable", 0)
    total = connectivity_result[1].get("endpoints_tested", 0)
    print(f"  • Endpoints Reachable: {reachable}/{total}")

    if reachable == 0:
        print_warning("\n⚠️  No Ultron endpoints are currently reachable.")
        print_warning("To start Ultron services, run:")
        print("  • kubectl apply -f k8s/ultron-deployment.yaml")
        print("  • Or start local Ollama: ollama serve")

    # Next steps
    print("\nNext Steps:")
    print("  1. Start Ultron cluster: kubectl apply -f k8s/")
    print("  2. Or start local Ollama: ollama serve")
    print("  3. Verify models: curl http://localhost:31434/api/tags")
    print("  4. Open Cursor and select 'ULTRON' model")
    print("  5. Run integration test: python scripts/python/test_ultron_integration.py")


def main():
    """Main test function"""
    print(f"{Colors.BOLD}Ultron AI Assistant Integration Test{Colors.RESET}")
    print(f"Workspace: {WORKSPACE_ROOT}")

    # Run all tests
    continue_result = test_continue_config()
    cursor_result = test_cursor_settings()
    ultron_result = test_ultron_command_file()
    connectivity_result = test_endpoint_connectivity()
    tracking_result = test_model_status_tracking()

    # Generate report
    generate_report(
        continue_result, cursor_result, ultron_result, connectivity_result, tracking_result
    )

    return 0


if __name__ == "__main__":

    sys.exit(main())