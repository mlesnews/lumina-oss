#!/usr/bin/env python3
"""
Verify TightVNC Server configuration (installed and running).
Used so we can use TightVNC + Manus capture as the agent's video feed (@mdv).

No secrets are read or printed; only presence and service state.
Tags: #TIGHTVNC #MANUS #MDV #VERIFY
"""

import os
import subprocess
import sys
from pathlib import Path


def check_tightvnc_server_windows() -> dict:
    """Check if TightVNC Server is installed and running on Windows."""
    out = {"installed": False, "running": False, "service_name": None, "error": None}
    try:
        # Check for tvnserver process (TightVNC Server)
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq tvnserver.exe", "/NH"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        running = "tvnserver.exe" in (r.stdout or "").lower()
        out["running"] = running
        # Check if executable exists (common install path)
        for base in [
            Path(os.environ.get("ProgramFiles", "C:\\Program Files")),
            Path(os.environ.get("ProgramFiles(x86)", "C:\\Program Files (x86)")),
        ]:
            exe = base / "TightVNC" / "tvnserver.exe"
            if exe.exists():
                out["installed"] = True
                break
        if not out["installed"] and running:
            out["installed"] = True  # Clearly installed if process exists
    except Exception as e:
        out["error"] = str(e)
    return out


def main():
    if sys.platform != "win32":
        print("TightVNC verification is implemented for Windows only.")
        print(
            "On this machine, ensure TightVNC Server is running if you want the agent to use the VNC session as the video feed."
        )
        return 0
    result = check_tightvnc_server_windows()
    print("TightVNC Server check:")
    print(f"  Installed: {result['installed']}")
    print(f"  Running:   {result['running']}")
    if result.get("error"):
        print(f"  Error:     {result['error']}")
    if result["installed"] and result["running"]:
        print("")
        print("OK: TightVNC Server is running. Use TightVNC Viewer to connect; then run:")
        print("  python scripts/python/manus_rdp_screenshot_capture.py --feed")
        print(
            "to update the MDV feed (data/manus_rdp_captures/mdv_feed_latest.png) so the agent can see."
        )
    elif result["installed"] and not result["running"]:
        print("")
        print(
            "TightVNC Server is installed but not running. Start the TightVNC Server service or tvnserver.exe."
        )
    else:
        print("")
        print("TightVNC Server not detected. Install from https://www.tightvnc.com/download.php")
        print(
            "Install TightVNC Server on the machine to be controlled (e.g. Kaiju); use TightVNC Viewer on the machine from which you connect."
        )
    return 0 if result.get("installed") else 1


if __name__ == "__main__":
    sys.exit(main())
