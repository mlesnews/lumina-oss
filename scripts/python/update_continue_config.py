#!/usr/bin/env python3
"""
Update Continue/Cline config file with Ultron Ollama cluster configuration.

This script updates the Continue VS Code extension config at:
c:\\Users\\mlesn\\.continue\\config.yaml

With configuration for the Ultron Ollama cluster running at localhost:11434.

Tags: #CONFIG #CONTINUE #OLLAMA #ULTRON @JARVIS @LUMINA
"""

import contextlib
import logging
import os
import sys
import traceback
from pathlib import Path
from typing import Any, Dict, Generator, Optional

# Configure logging at module level
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger("UpdateContinueConfig")


@contextlib.contextmanager
def safe_operation(operation_name: str) -> Generator[None, None, None]:
    """Context manager for safe operations with cleanup and logging"""
    try:
        logger.info(f"Starting: {operation_name}")
        yield
    except Exception as e:
        logger.error(f"Error in {operation_name}: {e}")
        logger.debug(f"Traceback: {traceback.format_exc()}")
        raise
    finally:
        logger.info(f"Completed: {operation_name}")


def validate_file_path(path: Path, must_exist: bool = False) -> bool:
    try:
        """Validate file path before use with proper error messages"""
        if not isinstance(path, Path):
            path = Path(path)
        if must_exist and not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        if not must_exist and path.exists():
            raise FileExistsError(f"File already exists: {path}")
        return True


    except Exception as e:
        logger.error(f"Error in validate_file_path: {e}", exc_info=True)
        raise
def validate_input(value: Any, expected_type: type, param_name: str) -> bool:
    """Validate input parameters with proper type checking"""
    if not isinstance(value, expected_type):
        raise TypeError(f"{param_name} must be of type {expected_type.__name__}, got {type(value).__name__}")
    return True


@contextlib.contextmanager
def atomic_file_operation(file_path: Path, mode: str = 'w') -> Generator[int, None, None]:
    """Context manager for atomic file operations with rollback"""
    import tempfile
    import shutil

    temp_file = None
    temp_fd = None
    try:
        temp_fd, temp_file = tempfile.mkstemp(dir=file_path.parent)
        yield temp_fd
        # If successful, copy temp file to actual location
        if mode.startswith('w') or mode.startswith('a'):
            os.fsync(temp_fd)
        shutil.copy2(temp_file, file_path)
        logger.info(f"Atomic write completed: {file_path}")
    except Exception as e:
        logger.error(f"Atomic operation failed: {e}")
        raise
    finally:
        if temp_file and os.path.exists(temp_file):
            if temp_fd:
                os.close(temp_fd)
            os.remove(temp_file)

# Ultron Ollama Cluster Configuration
CONTINUE_CONFIG = """name: ULTRON Local AI Config
version: 2.1.0
schema: v1

models:
  # ULTRON Cluster - Local Ollama at localhost:11434

  # Primary Coding Models
  - name: CodeLlama 13B (ULTRON - Best Coding)
    provider: ollama
    model: codellama:13b
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit
      - autocomplete

  - name: Qwen2.5 Coder 7B (ULTRON - Fast Coding)
    provider: ollama
    model: qwen2.5-coder:7b
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit
      - autocomplete

  # General Purpose Models
  - name: Llama 3.2 3B (ULTRON - General)
    provider: ollama
    model: llama3.2:3b
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit

  - name: Qwen2.5 7B (ULTRON - General)
    provider: ollama
    model: qwen2.5:7b
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit

  - name: Gemma 2B (ULTRON - Lightweight)
    provider: ollama
    model: gemma:2b
    apiBase: http://localhost:11434
    roles:
      - chat
      - edit
      - autocomplete

  # High-Power Models
  - name: Qwen2.5 72B (ULTRON - Maximum Power)
    provider: ollama
    model: qwen2.5:72b
    apiBase: http://localhost:11434
    contextLength: 32768
    roles:
      - chat
      - edit

  - name: Qwen2-72B Latest (ULTRON - Maximum Power)
    provider: ollama
    model: qwen2-72b:latest
    apiBase: http://localhost:11434
    contextLength: 32768
    roles:
      - chat
      - edit
"""


def update_continue_config(config_path: str) -> bool:
    """
    Update the Continue config file with Ultron Ollama configuration.

    Args:
        config_path: Full path to the config.yaml file

    Returns:
        True if successful, False otherwise
    """
    with safe_operation("update_continue_config"):
        validate_input(config_path, str, "config_path")

        try:
            # Ensure the parent directory exists
            config_file = Path(config_path)
            config_file.parent.mkdir(parents=True, exist_ok=True)

            # Atomic file write with rollback
            with atomic_file_operation(config_file, 'w') as fd:
                os.write(fd, CONTINUE_CONFIG.encode('utf-8'))

            logger.info(f"Successfully updated Continue config at: {config_path}")
            logger.info(f"Bytes written: {len(CONTINUE_CONFIG)}")

            print(f"Successfully updated Continue config at:")
            print(f"   {config_path}")
            print(f"   ({len(CONTINUE_CONFIG)} bytes written)")

            return True

        except (OSError, PermissionError, IOError) as e:
            logger.error(f"Error updating config: {e}")
            print(f"Error updating config: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error updating config: {e}", exc_info=True)
            print(f"Unexpected error updating config: {e}")
            return False


def verify_config(config_path: str) -> bool:
    """
    Verify the config file was written correctly.

    Args:
        config_path: Full path to the config.yaml file

    Returns:
        True if file exists and is readable, False otherwise
    """
    with safe_operation("verify_config"):
        validate_input(config_path, str, "config_path")

        try:
            config_file = Path(config_path)

            if not config_file.exists():
                logger.error(f"Config file not found: {config_path}")
                print(f"Config file not found: {config_path}")
                return False

            content = config_file.read_text()

            # Basic validation - check for key elements
            validations = [
                ("ULTRON Local AI Config" in content, "Config name"),
                ("ollama" in content, "Ollama provider"),
                ("localhost:11434" in content, "API base URL"),
                ("qwen2.5-coder:7b" in content, "Qwen Coder model"),
                ("qwen2.5:72b" in content, "Qwen 72B model"),
            ]

            print(f"Verifying config at: {config_path}")
            print(f"   File size: {len(content)} bytes")
            print("Validation checks:")

            all_passed = True
            for check, name in validations:
                status = "PASS" if check else "FAIL"
                print(f"   {status}: {name}")
                if not check:
                    all_passed = False

            # Show first few lines
            print("First 15 lines of config:")
            print("-" * 50)
            for i, line in enumerate(content.split("\n")[:15], 1):
                print(f"{i:3} | {line}")
            print("   | ...")
            print("-" * 50)

            if all_passed:
                print("All validations passed!")
            else:
                print("Some validations failed - please review")

            return all_passed

        except (OSError, PermissionError, IOError) as e:
            logger.error(f"Error verifying config: {e}")
            print(f"Error verifying config: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error verifying config: {e}", exc_info=True)
            print(f"Unexpected error verifying config: {e}")
            return False


def main() -> int:
    """Main entry point with proper error handling."""
    # Default config path for Continue
    config_path = r"c:\Users\mlesn\.continue\config.yaml"

    print("=" * 60)
    print("  ULTRON Ollama - Continue Config Updater")
    print("=" * 60)

    try:
        # Update the config
        print(f"Target: {config_path}")
        success = update_continue_config(config_path)

        if success:
            # Verify the config
            verify_config(config_path)

        print("\n" + "=" * 60)

        return 0 if success else 1

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except Exception as e:
        logger.error(f"Unexpected error in main: {e}", exc_info=True)
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":

    sys.exit(main())