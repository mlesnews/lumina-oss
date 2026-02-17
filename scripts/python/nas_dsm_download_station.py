#!/usr/bin/env python3
"""
NAS DSM Download Station API Integration
Synology Download Station automation
"""

import requests
import json
from typing import Optional, Dict, List
from urllib.parse import urlencode

class NASDownloadStation:
    """Synology Download Station API client"""

    def __init__(self, host: str = "<NAS_PRIMARY_IP>", port: int = 5000, username: str = "mlesn"):
        """
        Initialize NAS Download Station client

        Args:
            host: NAS IP address
            port: DSM port (default 5000)
            username: DSM username
        """
        self.host = host
        self.port = port
        self.username = username
        self.base_url = f"http://{host}:{port}/webapi"
        self.sid = None  # Session ID (requires login)

    def login(self, password: str) -> Dict:
        """
        Authenticate with DSM

        Args:
            password: DSM password

        Returns:
            Dict with login status and SID
        """
        url = f"{self.base_url}/auth.cgi"
        params = {
            "api": "SYNO.API.Auth",
            "version": "3",
            "method": "login",
            "account": self.username,
            "passwd": password,
            "session": "DownloadStation",
            "format": "sid"
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            if data.get("success"):
                self.sid = data.get("data", {}).get("sid")
                return {
                    "success": True,
                    "sid": self.sid
                }
            else:
                return {
                    "success": False,
                    "error": data.get("error", {}).get("code", "Unknown error")
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def create_task(self, uri: str, destination: Optional[str] = None) -> Dict:
        """
        Create download task

        Args:
            uri: URL or magnet link to download
            destination: Optional destination folder

        Returns:
            Dict with task creation status
        """
        if not self.sid:
            return {
                "success": False,
                "error": "Not authenticated. Call login() first."
            }

        url = f"{self.base_url}/DownloadStation/task.cgi"
        params = {
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "create",
            "uri": uri,
            "_sid": self.sid
        }

        if destination:
            params["destination"] = destination

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            return {
                "success": data.get("success", False),
                "task_id": data.get("data", {}).get("task_id") if data.get("success") else None,
                "error": data.get("error", {}).get("code") if not data.get("success") else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def list_tasks(self) -> Dict:
        """
        List all download tasks

        Returns:
            Dict with task list
        """
        if not self.sid:
            return {
                "success": False,
                "error": "Not authenticated"
            }

        url = f"{self.base_url}/DownloadStation/task.cgi"
        params = {
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "list",
            "_sid": self.sid
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            return {
                "success": data.get("success", False),
                "tasks": data.get("data", {}).get("tasks", []) if data.get("success") else [],
                "error": data.get("error", {}).get("code") if not data.get("success") else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def get_task_info(self, task_id: str) -> Dict:
        """
        Get task information

        Args:
            task_id: Task ID

        Returns:
            Dict with task info
        """
        if not self.sid:
            return {
                "success": False,
                "error": "Not authenticated"
            }

        url = f"{self.base_url}/DownloadStation/task.cgi"
        params = {
            "api": "SYNO.DownloadStation.Task",
            "version": "3",
            "method": "getinfo",
            "id": task_id,
            "_sid": self.sid
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            data = response.json()

            return {
                "success": data.get("success", False),
                "task": data.get("data", {}).get("task", {}) if data.get("success") else {},
                "error": data.get("error", {}).get("code") if not data.get("success") else None
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="NAS DSM Download Station API")
    parser.add_argument("url", help="URL to download")
    parser.add_argument("--host", default="<NAS_PRIMARY_IP>", help="NAS host")
    parser.add_argument("--username", default="mlesn", help="DSM username")
    parser.add_argument("--password", help="DSM password (or use env var)")
    parser.add_argument("--destination", help="Destination folder")

    args = parser.parse_args()

    password = args.password or os.getenv("DSM_PASSWORD")
    if not password:
        print("❌ Password required (--password or DSM_PASSWORD env var)")
        sys.exit(1)

    nas = NASDownloadStation(host=args.host, username=args.username)

    # Login
    login_result = nas.login(password)
    if not login_result.get("success"):
        print(f"❌ Login failed: {login_result.get('error')}")
        sys.exit(1)

    print("✅ Authenticated with NAS")

    # Create task
    task_result = nas.create_task(args.url, args.destination)
    if task_result.get("success"):
        print(f"✅ Download task created: {task_result.get('task_id')}")
        print(f"   URL: {args.url}")
    else:
        print(f"❌ Failed to create task: {task_result.get('error')}")
        sys.exit(1)


if __name__ == "__main__":
    import os
    import sys


    main()