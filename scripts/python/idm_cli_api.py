#!/usr/bin/env python3
"""
Internet Download Manager (IDM) CLI & API Wrapper
Provides Python interface to IDM's command-line and COM API
"""

import subprocess
import os
import sys
from pathlib import Path
from typing import Optional, Dict, List
import win32com.client  # pywin32

class IDMController:
    """IDM Controller - CLI and COM API wrapper"""

    def __init__(self, idm_path: Optional[str] = None):
        """
        Initialize IDM controller

        Args:
            idm_path: Path to IDMan.exe (auto-detected if None)
        """
        self.idm_path = idm_path or self._find_idm()
        if not self.idm_path or not os.path.exists(self.idm_path):
            raise FileNotFoundError("IDM not found. Please install Internet Download Manager.")

        self.idm_dir = os.path.dirname(self.idm_path)

    def _find_idm(self) -> Optional[str]:
        try:
            """Find IDM installation path"""
            common_paths = [
                r"C:\Program Files (x86)\Internet Download Manager\IDMan.exe",
                r"C:\Program Files\Internet Download Manager\IDMan.exe",
                os.path.expanduser(r"~\AppData\Local\Programs\Internet Download Manager\IDMan.exe")
            ]

            for path in common_paths:
                if os.path.exists(path):
                    return path
            return None

        except Exception as e:
            self.logger.error(f"Error in _find_idm: {e}", exc_info=True)
            raise
    def download_cli(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None,
        silent: bool = True,
        quit_after: bool = False,
        hangup: bool = False
    ) -> Dict:
        """
        Download file using IDM CLI

        Args:
            url: URL to download
            save_path: Directory to save file
            filename: Optional filename (auto-detected from URL if None)
            silent: Run in silent mode (/n)
            quit_after: Quit IDM after download (/q)
            hangup: Hang up connection after download (/h)

        Returns:
            Dict with status and command info
        """
        # Ensure save_path exists
        Path(save_path).mkdir(parents=True, exist_ok=True)

        # Build command
        cmd = [self.idm_path]

        if silent:
            cmd.append("/n")

        cmd.append("/d")
        cmd.append(url)

        cmd.append("/p")
        cmd.append(save_path)

        if filename:
            cmd.append("/f")
            cmd.append(filename)

        if quit_after:
            cmd.append("/q")

        if hangup:
            cmd.append("/h")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "command": " ".join(cmd)
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": "Command timeout",
                "command": " ".join(cmd)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(cmd)
            }

    def add_to_queue(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None
    ) -> Dict:
        """
        Add download to IDM queue without starting

        Args:
            url: URL to download
            save_path: Directory to save file
            filename: Optional filename

        Returns:
            Dict with status
        """
        cmd = [self.idm_path, "/a", "/d", url, "/p", save_path]
        if filename:
            cmd.extend(["/f", filename])

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )

            return {
                "success": result.returncode == 0,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def download_com_api(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None,
        referrer: str = "",
        cookies: str = "",
        post_data: str = "",
        user_agent: str = "",
        flags: int = 0
    ) -> Dict:
        """
        Download file using IDM COM API

        Args:
            url: URL to download
            save_path: Directory to save file
            filename: Optional filename
            referrer: Referrer URL
            cookies: Cookie string
            post_data: POST data
            user_agent: User agent string
            flags: Download flags (0 = normal)

        Returns:
            Dict with status
        """
        try:
            idm = win32com.client.Dispatch("IDMan.CIDMLinkTransmitter")

            # Send link to IDM
            idm.SendLinkToIDM(
                url,
                referrer,
                cookies,
                post_data,
                user_agent,
                "",
                save_path,
                filename or "",
                flags
            )

            return {
                "success": True,
                "method": "COM_API",
                "url": url,
                "save_path": save_path,
                "filename": filename
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "method": "COM_API"
            }

    def download(
        self,
        url: str,
        save_path: str,
        filename: Optional[str] = None,
        method: str = "cli",
        **kwargs
    ) -> Dict:
        """
        Download file using specified method

        Args:
            url: URL to download
            save_path: Directory to save file
            filename: Optional filename
            method: "cli" or "com_api"
            **kwargs: Additional arguments for CLI or COM API

        Returns:
            Dict with status
        """
        if method.lower() == "com_api":
            return self.download_com_api(url, save_path, filename, **kwargs)
        else:
            return self.download_cli(url, save_path, filename, **kwargs)

    def get_queue_status(self) -> List[Dict]:
        """
        Get IDM download queue status (requires parsing IDM's queue file)

        Returns:
            List of download items
        """
        # IDM stores queue in registry/ini file
        # This is a placeholder - actual implementation would parse IDM's data
        return []


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="IDM CLI & API Wrapper")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("-p", "--path", required=True, help="Save path")
    parser.add_argument("-f", "--filename", help="Filename (optional)")
    parser.add_argument("-m", "--method", choices=["cli", "com_api"], default="cli", help="Download method")
    parser.add_argument("--silent", action="store_true", default=True, help="Silent mode")
    parser.add_argument("--quit", action="store_true", help="Quit IDM after download")

    args = parser.parse_args()

    try:
        idm = IDMController()

        result = idm.download(
            args.url,
            args.path,
            args.filename,
            method=args.method,
            silent=args.silent,
            quit_after=args.quit
        )

        if result.get("success"):
            print(f"✅ Download added to IDM: {args.url}")
            print(f"   Save path: {args.path}")
            if args.filename:
                print(f"   Filename: {args.filename}")
        else:
            print(f"❌ Failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":


    main()