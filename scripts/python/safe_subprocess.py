
import subprocess
import sys
from pathlib import Path
import logging
logger = logging.getLogger("safe_subprocess")


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
        logger.error(f"Error in safe_subprocess_popen: {e}", exc_info=True)
        raise