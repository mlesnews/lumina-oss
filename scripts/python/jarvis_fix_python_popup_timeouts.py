#!/usr/bin/env python3
"""
JARVIS Fix Python Popup Timeouts
Prevents Python subprocess calls from creating popup windows that timeout

Tags: #JARVIS #FIX #PYTHON #TIMEOUT @JARVIS @DOIT
"""

import sys
import os
from pathlib import Path
from typing import Dict, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISFixPythonPopupTimeouts")


def fix_subprocess_calls():
    """Document best practices for preventing popup timeouts"""

    fixes = {
        "always_use_timeout": "All subprocess calls must include timeout parameter",
        "capture_output": "Use capture_output=True or stdout/stderr=PIPE to prevent popup windows",
        "non_interactive": "Use --non-interactive, --yes, or similar flags for commands",
        "use_shell_false": "Avoid shell=True unless necessary (security + popup prevention)",
        "handle_timeout_exception": "Always catch subprocess.TimeoutExpired",
        "background_processes": "Use Popen for background processes, ensure stdout/stderr are redirected",
        "disable_windows_error_dialogs": "Set Windows error mode to suppress dialogs"
    }

    logger.info("=" * 80)
    logger.info("🔧 PYTHON POPUP TIMEOUT FIX GUIDELINES")
    logger.info("=" * 80)
    logger.info("")

    for key, value in fixes.items():
        logger.info(f"✅ {key}: {value}")

    logger.info("")
    logger.info("Windows-Specific Fix:")
    logger.info("  Set environment variable: PYTHONUNBUFFERED=1")
    logger.info("  Use CREATE_NO_WINDOW flag for subprocess on Windows")
    logger.info("")

    return fixes


def create_subprocess_wrapper():
    """Create a safe subprocess wrapper that prevents popups"""

    wrapper_code = '''
import subprocess
import sys
from pathlib import Path

# Windows-specific: Prevent popup windows
if sys.platform == "win32":
    import ctypes
    # Set error mode to suppress error dialogs
    SEM_NOGPFAULTERRORBOX = 0x0002
    ctypes.windll.kernel32.SetErrorMode(SEM_NOGPFAULTERRORBOX)

    # Use CREATE_NO_WINDOW flag
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0

def safe_subprocess_run(*args, **kwargs):
    """Safe subprocess.run that prevents popup windows"""
    # Always capture output to prevent popups
    if "stdout" not in kwargs:
        kwargs["stdout"] = subprocess.PIPE
    if "stderr" not in kwargs:
        kwargs["stderr"] = subprocess.PIPE

    # Always use timeout (default 30 seconds if not specified)
    if "timeout" not in kwargs:
        kwargs["timeout"] = 30

    # Use CREATE_NO_WINDOW on Windows
    if sys.platform == "win32" and "creationflags" not in kwargs:
        kwargs["creationflags"] = CREATE_NO_WINDOW

    # Never use shell=True unless absolutely necessary
    if "shell" not in kwargs:
        kwargs["shell"] = False

    try:
        return subprocess.run(*args, **kwargs)
    except subprocess.TimeoutExpired as e:
        logger.warning(f"Subprocess timeout: {e}")
        # Terminate the process
        if hasattr(e, "process") and e.process:
            try:
                e.process.kill()
                e.process.wait(timeout=5)
            except:
                pass
        raise
    except Exception as e:
        logger.error(f"Subprocess error: {e}")
        raise

def safe_subprocess_popen(*args, **kwargs):
    try:
        """Safe subprocess.Popen that prevents popup windows"""
        # Always redirect stdout/stderr
        if "stdout" not in kwargs:
            kwargs["stdout"] = subprocess.PIPE
        if "stderr" not in kwargs:
            kwargs["stderr"] = subprocess.PIPE

        # Use CREATE_NO_WINDOW on Windows
        if sys.platform == "win32" and "creationflags" not in kwargs:
            kwargs["creationflags"] = CREATE_NO_WINDOW

        # Never use shell=True unless absolutely necessary
        if "shell" not in kwargs:
            kwargs["shell"] = False

        return subprocess.Popen(*args, **kwargs)
    except Exception as e:
        self.logger.error(f"Error in safe_subprocess_popen: {e}", exc_info=True)
        raise
'''

    wrapper_file = Path(__file__).parent / "safe_subprocess.py"
    try:
        with open(wrapper_file, 'w', encoding='utf-8') as f:
            f.write(wrapper_code)
        logger.info(f"✅ Created safe subprocess wrapper: {wrapper_file}")
        return wrapper_file
    except Exception as e:
        logger.error(f"Failed to create wrapper: {e}")
        return None


def main():
    try:
        """Main function"""
        logger.info("=" * 80)
        logger.info("🔧 FIXING PYTHON POPUP TIMEOUT ISSUES")
        logger.info("=" * 80)
        logger.info("")

        # Document fixes
        fixes = fix_subprocess_calls()

        # Create safe wrapper
        wrapper_file = create_subprocess_wrapper()

        logger.info("")
        logger.info("=" * 80)
        logger.info("✅ FIX GUIDELINES DOCUMENTED")
        logger.info("=" * 80)
        logger.info("")
        logger.info("📋 Next Steps:")
        logger.info("   1. Update all subprocess calls to use timeout and capture_output")
        logger.info("   2. Use safe_subprocess.py wrapper for new code")
        logger.info("   3. Set PYTHONUNBUFFERED=1 environment variable")
        logger.info("   4. Test all automated scripts for popup prevention")
        logger.info("")

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())