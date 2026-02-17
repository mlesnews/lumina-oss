#!/usr/bin/env python3
"""
NAS Drive Manager - Unified Network Drive Management
Handles all mapped NAS drives consistently

Tags: #NAS #NETWORK_DRIVES #DRIVE_MAPPING @JARVIS @LUMINA @DOIT
"""

import subprocess
import re
from typing import Dict, List, Optional, Tuple
from pathlib import Path


class NASDriveManager:
    """Manages all NAS network drive mappings"""

    def __init__(self, host: Optional[str] = None):
        """
        Initialize NAS Drive Manager

        Args:
            host: Remote host (IP or hostname) for SSH execution, None for local
        """
        self.host = host
        self.drives: Dict[str, Dict[str, str]] = {}

    def run_command(self, command: str) -> Tuple[str, int]:
        """Run command locally or via SSH"""
        if self.host:
            ssh_cmd = ["ssh", self.host, command]
        else:
            ssh_cmd = ["powershell", "-Command", command]

        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            return result.stdout, result.returncode
        except Exception as e:
            return str(e), 1

    def get_all_mapped_drives(self) -> Dict[str, Dict[str, str]]:
        """
        Get all mapped network drives

        Returns:
            Dictionary mapping drive letter to drive info
            {
                'M': {
                    'letter': 'M',
                    'path': '\\\\<NAS_PRIMARY_IP>\\models',
                    'status': 'mapped'
                },
                ...
            }
        """
        # Get all mapped drives
        cmd = "Get-PSDrive -PSProvider FileSystem | Where-Object { $_.DisplayRoot -like '\\\\*' } | ForEach-Object { [PSCustomObject]@{ Letter = $_.Name; Path = $_.DisplayRoot } } | ConvertTo-Json"
        stdout, code = self.run_command(cmd)

        drives = {}
        if code == 0 and stdout.strip():
            try:
                import json
                drive_list = json.loads(stdout) if stdout.strip() else []
                if not isinstance(drive_list, list):
                    drive_list = [drive_list]

                for drive in drive_list:
                    letter = drive.get('Letter', '')
                    path = drive.get('Path', '')
                    if letter and path:
                        drives[letter] = {
                            'letter': letter,
                            'path': path,
                            'status': 'mapped',
                            'local_path': f"{letter}:\\"
                        }
            except:
                pass

        # Also check net use output
        cmd = "net use | Select-String -Pattern '^([A-Z]):' | ForEach-Object { if ($_ -match '^([A-Z]):\\s+(\\\\[^\\s]+)') { [PSCustomObject]@{ Letter = $matches[1]; Path = $matches[2] } } } | ConvertTo-Json"
        stdout, code = self.run_command(cmd)

        if code == 0 and stdout.strip():
            try:
                import json
                drive_list = json.loads(stdout) if stdout.strip() else []
                if not isinstance(drive_list, list):
                    drive_list = [drive_list]

                for drive in drive_list:
                    letter = drive.get('Letter', '').replace(':', '')
                    path = drive.get('Path', '')
                    if letter and path and letter not in drives:
                        drives[letter] = {
                            'letter': letter,
                            'path': path,
                            'status': 'mapped',
                            'local_path': f"{letter}:\\"
                        }
            except:
                pass

        self.drives = drives
        return drives

    def map_drive(self, letter: str, unc_path: str, persistent: bool = True) -> Tuple[bool, str]:
        """
        Map a network drive

        Args:
            letter: Drive letter (e.g., 'M')
            unc_path: UNC path (e.g., '\\\\<NAS_PRIMARY_IP>\\models')
            persistent: Make mapping persistent across reboots

        Returns:
            (success, message)
        """
        persistent_flag = "/persistent:yes" if persistent else "/persistent:no"
        cmd = f"net use {letter}: {unc_path} {persistent_flag}"
        stdout, code = self.run_command(cmd)

        if code == 0:
            # Refresh drives
            self.get_all_mapped_drives()
            return True, f"Drive {letter}: mapped successfully to {unc_path}"
        else:
            return False, f"Failed to map drive {letter}: {stdout}"

    def unmap_drive(self, letter: str) -> Tuple[bool, str]:
        """
        Unmap a network drive

        Args:
            letter: Drive letter

        Returns:
            (success, message)
        """
        cmd = f"net use {letter}: /delete"
        stdout, code = self.run_command(cmd)

        if code == 0:
            # Refresh drives
            self.get_all_mapped_drives()
            return True, f"Drive {letter}: unmapped successfully"
        else:
            return False, f"Failed to unmap drive {letter}: {stdout}"

    def is_drive_mapped(self, letter: str) -> bool:
        """Check if a drive is mapped"""
        self.get_all_mapped_drives()
        return letter.upper() in self.drives

    def get_drive_path(self, letter: str) -> Optional[str]:
        """Get UNC path for a drive letter"""
        self.get_all_mapped_drives()
        drive = self.drives.get(letter.upper())
        return drive.get('path') if drive else None

    def ensure_drive_mapped(self, letter: str, unc_path: str, persistent: bool = True) -> Tuple[bool, str]:
        """
        Ensure a drive is mapped, map it if not

        Args:
            letter: Drive letter
            unc_path: UNC path
            persistent: Make mapping persistent

        Returns:
            (success, message)
        """
        if self.is_drive_mapped(letter):
            current_path = self.get_drive_path(letter)
            if current_path == unc_path:
                return True, f"Drive {letter}: already mapped to {unc_path}"
            else:
                # Unmap and remap
                self.unmap_drive(letter)

        return self.map_drive(letter, unc_path, persistent)

    def list_all_drives(self) -> List[Dict[str, str]]:
        """List all mapped network drives"""
        self.get_all_mapped_drives()
        return list(self.drives.values())

    def verify_drive_access(self, letter: str) -> Tuple[bool, str]:
        """
        Verify a drive is accessible

        Args:
            letter: Drive letter

        Returns:
            (accessible, message)
        """
        cmd = f"Test-Path '{letter}:\\'"
        stdout, code = self.run_command(cmd)

        if code == 0 and 'True' in stdout:
            return True, f"Drive {letter}: is accessible"
        else:
            return False, f"Drive {letter}: is not accessible"


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description='NAS Drive Manager')
    parser.add_argument('--host', help='Remote host (IP or hostname)')
    parser.add_argument('--list', action='store_true', help='List all mapped drives')
    parser.add_argument('--map', nargs=2, metavar=('LETTER', 'PATH'), help='Map a drive')
    parser.add_argument('--unmap', metavar='LETTER', help='Unmap a drive')
    parser.add_argument('--verify', metavar='LETTER', help='Verify drive access')
    parser.add_argument('--ensure', nargs=2, metavar=('LETTER', 'PATH'), help='Ensure drive is mapped')

    args = parser.parse_args()

    manager = NASDriveManager(host=args.host)

    if args.list:
        drives = manager.list_all_drives()
        print("\n📁 Mapped Network Drives:")
        print("=" * 60)
        for drive in drives:
            print(f"  {drive['letter']}: → {drive['path']}")
        print()

    elif args.map:
        letter, path = args.map
        success, message = manager.map_drive(letter, path)
        print(f"{'✅' if success else '❌'} {message}")

    elif args.unmap:
        success, message = manager.unmap_drive(args.unmap)
        print(f"{'✅' if success else '❌'} {message}")

    elif args.verify:
        accessible, message = manager.verify_drive_access(args.verify)
        print(f"{'✅' if accessible else '❌'} {message}")

    elif args.ensure:
        letter, path = args.ensure
        success, message = manager.ensure_drive_mapped(letter, path)
        print(f"{'✅' if success else '❌'} {message}")

    else:
        parser.print_help()


if __name__ == "__main__":


    main()