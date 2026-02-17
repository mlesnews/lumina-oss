#!/usr/bin/env python3
"""
NAS DSM Download Manager Integration
Integrates with Synology DSM Download Station

Tags: #NAS #DSM #DOWNLOAD_MANAGER @JARVIS @LUMINA @DOIT
"""

import requests
import json
from typing import Dict, Optional, Tuple
from urllib.parse import urlencode
import logging
logger = logging.getLogger("nas_dsm_download_manager")



class NASDSMDownloadManager:
    """Manages downloads via Synology DSM Download Station"""

    def __init__(self, nas_ip: str = "<NAS_PRIMARY_IP>", port: int = 5000, username: Optional[str] = None, password: Optional[str] = None):
        """
        Initialize DSM Download Manager

        Args:
            nas_ip: NAS IP address
            port: DSM port (default 5000)
            username: DSM username (optional, for authenticated requests)
            password: DSM password (optional)
        """
        self.nas_ip = nas_ip
        self.port = port
        self.base_url = f"http://{nas_ip}:{port}/webapi"
        self.username = username
        self.password = password
        self.session_id = None

    def _get_auth_params(self) -> Dict[str, str]:
        """Get authentication parameters"""
        params = {}
        if self.username and self.password:
            params['account'] = self.username
            params['passwd'] = self.password
        return params

    def login(self) -> Tuple[bool, str]:
        """
        Login to DSM (if credentials provided)

        Returns:
            (success, message)
        """
        if not self.username or not self.password:
            return False, "No credentials provided"

        try:
            url = f"{self.base_url}/auth.cgi"
            params = {
                'api': 'SYNO.API.Auth',
                'version': '3',
                'method': 'login',
                'account': self.username,
                'passwd': self.password,
                'session': 'DownloadStation'
            }

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    self.session_id = data.get('data', {}).get('sid')
                    return True, "Login successful"
                else:
                    return False, f"Login failed: {data.get('error', {}).get('code', 'Unknown')}"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def get_info(self) -> Tuple[bool, Dict]:
        """
        Get Download Station info

        Returns:
            (success, info_dict)
        """
        try:
            url = f"{self.base_url}/DownloadStation/info.cgi"
            params = {
                'api': 'SYNO.DownloadStation.Info',
                'version': '1',
                'method': 'getinfo'
            }

            if self.session_id:
                params['_sid'] = self.session_id

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return True, data.get('data', {})
                else:
                    return False, {'error': data.get('error', {})}
            else:
                return False, {'error': f'HTTP {response.status_code}'}
        except Exception as e:
            return False, {'error': str(e)}

    def add_download(self, url: str, destination: Optional[str] = None) -> Tuple[bool, str]:
        """
        Add download to Download Station

        Args:
            url: Download URL
            destination: Optional destination path (relative to download folder)

        Returns:
            (success, message)
        """
        try:
            # First, create download task
            create_url = f"{self.base_url}/DownloadStation/task.cgi"
            params = {
                'api': 'SYNO.DownloadStation.Task',
                'version': '1',
                'method': 'create',
                'uri': url
            }

            if destination:
                params['destination'] = destination

            if self.session_id:
                params['_sid'] = self.session_id

            response = requests.get(create_url, params=params, timeout=30)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return True, f"Download added: {url}"
                else:
                    error = data.get('error', {})
                    return False, f"Failed to add download: {error.get('code', 'Unknown')}"
            else:
                return False, f"HTTP {response.status_code}"
        except Exception as e:
            return False, str(e)

    def list_tasks(self) -> Tuple[bool, list]:
        """
        List all download tasks

        Returns:
            (success, task_list)
        """
        try:
            url = f"{self.base_url}/DownloadStation/task.cgi"
            params = {
                'api': 'SYNO.DownloadStation.Task',
                'version': '1',
                'method': 'list',
                'additional': '["detail", "transfer"]'
            }

            if self.session_id:
                params['_sid'] = self.session_id

            response = requests.get(url, params=params, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data.get('success', False):
                    return True, data.get('data', {}).get('tasks', [])
                else:
                    return False, []
            else:
                return False, []
        except Exception as e:
            return False, []


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description='NAS DSM Download Manager')
        parser.add_argument('--nas-ip', default='<NAS_PRIMARY_IP>', help='NAS IP address')
        parser.add_argument('--port', type=int, default=5000, help='DSM port')
        parser.add_argument('--username', help='DSM username')
        parser.add_argument('--password', help='DSM password')
        parser.add_argument('--info', action='store_true', help='Get Download Station info')
        parser.add_argument('--add', metavar='URL', help='Add download URL')
        parser.add_argument('--list', action='store_true', help='List download tasks')

        args = parser.parse_args()

        manager = NASDSMDownloadManager(
            nas_ip=args.nas_ip,
            port=args.port,
            username=args.username,
            password=args.password
        )

        if args.username and args.password:
            success, message = manager.login()
            print(f"{'✅' if success else '❌'} {message}")
            if not success:
                return

        if args.info:
            success, info = manager.get_info()
            if success:
                print("\n📊 Download Station Info:")
                print(json.dumps(info, indent=2))
            else:
                print(f"❌ Failed to get info: {info}")

        elif args.add:
            success, message = manager.add_download(args.add)
            print(f"{'✅' if success else '❌'} {message}")

        elif args.list:
            success, tasks = manager.list_tasks()
            if success:
                print(f"\n📋 Download Tasks ({len(tasks)}):")
                for task in tasks:
                    print(f"  {task.get('title', 'Unknown')} - {task.get('status', 'Unknown')}")
            else:
                print("❌ Failed to list tasks")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()