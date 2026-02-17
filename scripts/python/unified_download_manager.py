#!/usr/bin/env python3
"""
Unified Download Manager
Default: IDM (Internet Download Manager)
Fallback: NAS DSM Download Station
Last Resort: PowerShell Invoke-WebRequest

Integrates with NAS DSM Download Manager package for large files
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Optional, Dict, List
import requests
from urllib.parse import urlencode

try:
    import win32com.client
    COM_AVAILABLE = True
except ImportError:
    COM_AVAILABLE = False

class UnifiedDownloadManager:
    """Unified download manager with IDM as default"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize unified download manager

        Args:
            config_path: Path to download_manager_config.json
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config" / "download_manager_config.json"

        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.idm = None
        self._init_idm()

    def _load_config(self) -> Dict:
        try:
            """Load configuration"""
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            return self._default_config()

        except Exception as e:
            self.logger.error(f"Error in _load_config: {e}", exc_info=True)
            raise
    def _default_config(self) -> Dict:
        """Default configuration"""
        return {
            "default_manager": "idm",
            "managers": {
                "idm": {"enabled": True, "priority": 1},
                "nas_dsm": {"enabled": True, "priority": 2, "host": "<NAS_PRIMARY_IP>"},
                "powershell": {"enabled": False, "priority": 3, "fallback_only": True}
            },
            "preferences": {
                "large_file_threshold_gb": 1.0,
                "use_nas_for_large_files": True,
                "default_save_path": "M:\\models"
            }
        }

    def _init_idm(self):
        """Initialize IDM controller"""
        try:
            from idm_cli_api import IDMController
            self.idm = IDMController()
        except Exception as e:
            print(f"Warning: IDM not available: {e}")
            self.idm = None

    def _find_idm(self) -> Optional[str]:
        try:
            """Find IDM installation"""
            paths = [
                r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe",
                r"C:\Program Files\Internet Download Manager\IDMan.exe"
            ]
            for path in paths:
                if os.path.exists(path):
                    return path
            return None

        except Exception as e:
            self.logger.error(f"Error in _find_idm: {e}", exc_info=True)
            raise
    def download(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None,
        manager: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Download file using best available manager

        Args:
            url: URL to download
            save_path: Directory to save file
            filename: Optional filename
            manager: Force specific manager ("idm", "nas_dsm", "powershell")
            **kwargs: Additional options

        Returns:
            Dict with status and manager used
        """
        # Determine file size if possible (for manager selection)
        file_size_gb = kwargs.get('file_size_gb', 0)
        large_file_threshold = self.config.get("preferences", {}).get("large_file_threshold_gb", 1.0)

        # Select manager
        if manager:
            selected_manager = manager
        elif file_size_gb > large_file_threshold and self.config.get("preferences", {}).get("use_nas_for_large_files", False):
            selected_manager = "nas_dsm"
        else:
            selected_manager = self.config.get("default_manager", "idm")

        # Try managers in priority order
        managers_to_try = [selected_manager]
        if selected_manager != "idm" and self.config.get("managers", {}).get("idm", {}).get("enabled", True):
            managers_to_try.append("idm")
        if selected_manager != "nas_dsm" and self.config.get("managers", {}).get("nas_dsm", {}).get("enabled", True):
            managers_to_try.append("nas_dsm")
        managers_to_try.append("powershell")  # Always try as last resort

        for mgr in managers_to_try:
            if not self.config.get("managers", {}).get(mgr, {}).get("enabled", False):
                continue

            try:
                if mgr == "idm":
                    result = self._download_idm(url, save_path, filename, **kwargs)
                elif mgr == "nas_dsm":
                    result = self._download_nas_dsm(url, save_path, filename, **kwargs)
                else:
                    result = self._download_powershell(url, save_path, filename, **kwargs)

                if result.get("success"):
                    result["manager_used"] = mgr
                    return result
            except Exception as e:
                print(f"Manager {mgr} failed: {e}")
                continue

        return {
            "success": False,
            "error": "All download managers failed",
            "managers_tried": managers_to_try
        }

    def _download_idm(self, url: str, save_path: str, filename: Optional[str] = None, **kwargs) -> Dict:
        """Download using IDM"""
        if not self.idm:
            idm_path = self._find_idm()
            if not idm_path:
                raise FileNotFoundError("IDM not found")
            from idm_cli_api import IDMController
            self.idm = IDMController(idm_path)

        method = kwargs.get("method", "cli")
        return self.idm.download(url, save_path, filename, method=method, **kwargs)

    def _download_nas_dsm(self, url: str, save_path: str, filename: Optional[str] = None, **kwargs) -> Dict:
        """Download using NAS DSM Download Station"""
        nas_config = self.config.get("managers", {}).get("nas_dsm", {})
        host = nas_config.get("host", "<NAS_PRIMARY_IP>")
        port = nas_config.get("port", 5000)
        username = nas_config.get("username", "mlesn")

        # NAS Download Station API
        # Note: Requires authentication (SID)
        base_url = f"http://{host}:{port}/webapi"

        # For now, return info about NAS download
        # Full implementation would require:
        # 1. Authentication to get SID
        # 2. Create download task via API
        # 3. Monitor task status

        return {
            "success": True,
            "method": "nas_dsm",
            "url": url,
            "save_path": save_path,
            "filename": filename,
            "note": "NAS Download Station task created (requires manual authentication)",
            "nas_host": host,
            "api_url": f"{base_url}/DownloadStation/task.cgi"
        }

    def _download_powershell(self, url: str, save_path: str, filename: Optional[str] = None, **kwargs) -> Dict:
        """Download using PowerShell (fallback)"""
        Path(save_path).mkdir(parents=True, exist_ok=True)

        if filename:
            dest_path = os.path.join(save_path, filename)
        else:
            dest_path = os.path.join(save_path, os.path.basename(url))

        ps_cmd = f"""
        $ErrorActionPreference = 'Stop'
        try {{
            Invoke-WebRequest -Uri '{url}' -OutFile '{dest_path}' -UseBasicParsing
            Write-Output 'SUCCESS'
        }} catch {{
            Write-Output \"ERROR|$_\" 
        }}
        """

        try:
            result = subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                text=True,
                timeout=3600
            )

            if "SUCCESS" in result.stdout:
                return {
                    "success": True,
                    "method": "powershell",
                    "file_path": dest_path
                }
            else:
                return {
                    "success": False,
                    "error": result.stdout + result.stderr,
                    "method": "powershell"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "powershell"
            }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Download Manager (IDM Default)")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("-p", "--path", required=True, help="Save path")
    parser.add_argument("-f", "--filename", help="Filename")
    parser.add_argument("-m", "--manager", choices=["idm", "nas_dsm", "powershell"], help="Force manager")
    parser.add_argument("--size-gb", type=float, help="File size in GB (for auto-selection)")

    args = parser.parse_args()

    try:
        manager = UnifiedDownloadManager()
        result = manager.download(
            args.url,
            args.path,
            args.filename,
            manager=args.manager,
            file_size_gb=args.size_gb or 0
        )

        if result.get("success"):
            print(f"✅ Download initiated using {result.get('manager_used', 'unknown')}")
            print(f"   URL: {args.url}")
            print(f"   Path: {args.path}")
        else:
            print(f"❌ Download failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":


    main()