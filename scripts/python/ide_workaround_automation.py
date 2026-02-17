#!/usr/bin/env python3
"""
IDE Integration Workaround Automation

Automates workarounds for IDE validation limitations:
- SSH port forwarding
- Localhost endpoint mapping
- Configuration patching

Tags: #IDE #WORKAROUND #AUTOMATION #CURSOR @JARVIS @LUMINA
"""

import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ide_workaround_automation")


@dataclass
class PortForward:
    """Represents an SSH port forward"""

    local_port: int
    remote_host: str
    remote_port: int
    ssh_host: str
    ssh_user: str
    ssh_key_path: Optional[str] = None
    process: Optional[subprocess.Popen] = None
    pid: Optional[int] = None


class IDEWorkaroundAutomation:
    """Automates IDE integration workarounds"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.registry_path = project_root / "config" / "cluster_endpoint_registry.json"
        self.active_forwards: Dict[str, PortForward] = {}
        self.registry: Dict = {}

    def load_registry(self):
        """Load endpoint registry"""
        if self.registry_path.exists():
            with open(self.registry_path, encoding="utf-8") as f:
                self.registry = json.load(f)

    def setup_ssh_key(self, ssh_host: str, ssh_user: str) -> Optional[Path]:
        """Setup SSH key for passwordless authentication"""
        ssh_dir = Path.home() / ".ssh"
        ssh_dir.mkdir(exist_ok=True)

        key_name = f"id_ed25519_{ssh_host.replace('.', '_')}"
        private_key = ssh_dir / key_name
        public_key = ssh_dir / f"{key_name}.pub"

        if private_key.exists():
            logger.info(f"SSH key already exists: {private_key}")
            return private_key

        # Generate SSH key
        logger.info(f"Generating SSH key: {private_key}")
        try:
            subprocess.run(
                [
                    "ssh-keygen",
                    "-t",
                    "ed25519",
                    "-f",
                    str(private_key),
                    "-N",
                    "",  # No passphrase
                    "-C",
                    f"ide-workaround-{ssh_host}",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"✅ SSH key generated: {private_key}")
            return private_key
        except Exception as e:
            logger.error(f"Failed to generate SSH key: {e}")
            return None

    def copy_ssh_key(self, ssh_host: str, ssh_user: str, key_path: Path) -> bool:
        """Copy SSH public key to remote host"""
        public_key = key_path.with_suffix(".pub")

        if not public_key.exists():
            logger.error(f"Public key not found: {public_key}")
            return False

        try:
            # Read public key
            with open(public_key) as f:
                public_key_content = f.read().strip()

            # Copy to remote host
            logger.info(f"Copying SSH key to {ssh_user}@{ssh_host}...")
            subprocess.run(
                [
                    "ssh",
                    f"{ssh_user}@{ssh_host}",
                    f"mkdir -p ~/.ssh && echo '{public_key_content}' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys",
                ],
                check=True,
                capture_output=True,
            )

            logger.info(f"✅ SSH key copied to {ssh_host}")
            return True
        except Exception as e:
            logger.error(f"Failed to copy SSH key: {e}")
            return False

    def start_port_forward(
        self,
        forward_id: str,
        local_port: int,
        remote_host: str,
        remote_port: int,
        ssh_host: str,
        ssh_user: str,
        ssh_key: Optional[Path] = None,
    ) -> bool:
        """Start SSH port forward"""
        if forward_id in self.active_forwards:
            logger.warning(f"Port forward {forward_id} already active")
            return True

        # Setup SSH key if needed
        if ssh_key is None:
            ssh_key = self.setup_ssh_key(ssh_host, ssh_user)
            if ssh_key:
                self.copy_ssh_key(ssh_host, ssh_user, ssh_key)

        # Build SSH command
        ssh_cmd = [
            "ssh",
            "-N",  # No remote command
            "-L",
            f"{local_port}:{remote_host}:{remote_port}",  # Port forward
            "-o",
            "StrictHostKeyChecking=no",
            "-o",
            "UserKnownHostsFile=/dev/null",
        ]

        if ssh_key:
            ssh_cmd.extend(["-i", str(ssh_key)])

        ssh_cmd.append(f"{ssh_user}@{ssh_host}")

        try:
            logger.info(f"Starting port forward: localhost:{local_port} → {ssh_host}:{remote_port}")
            process = subprocess.Popen(
                ssh_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE
            )

            # Wait a moment to check if it started successfully
            time.sleep(1)
            if process.poll() is not None:
                # Process exited immediately (error)
                stdout, stderr = process.communicate()
                logger.error(f"Port forward failed: {stderr.decode()}")
                return False

            port_forward = PortForward(
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port,
                ssh_host=ssh_host,
                ssh_user=ssh_user,
                ssh_key_path=str(ssh_key) if ssh_key else None,
                process=process,
                pid=process.pid,
            )

            self.active_forwards[forward_id] = port_forward
            logger.info(f"✅ Port forward started (PID: {process.pid})")
            return True

        except Exception as e:
            logger.error(f"Failed to start port forward: {e}")
            return False

    def stop_port_forward(self, forward_id: str) -> bool:
        """Stop SSH port forward"""
        if forward_id not in self.active_forwards:
            logger.warning(f"Port forward {forward_id} not found")
            return False

        port_forward = self.active_forwards[forward_id]

        try:
            if port_forward.process:
                port_forward.process.terminate()
                port_forward.process.wait(timeout=5)

            del self.active_forwards[forward_id]
            logger.info(f"✅ Port forward {forward_id} stopped")
            return True
        except Exception as e:
            logger.error(f"Failed to stop port forward: {e}")
            return False

    def setup_all_forwards_from_registry(self) -> Dict[str, bool]:
        """Setup all port forwards defined in registry"""
        self.load_registry()

        results = {}
        endpoints = self.registry.get("endpoints", {})

        for endpoint_id, endpoint in endpoints.items():
            forwarding = endpoint.get("forwarding")
            if not forwarding or forwarding.get("type") != "ssh_tunnel":
                continue

            forward_id = endpoint_id
            local_port = forwarding.get("local_port")
            remote_host = forwarding.get("remote_host")
            remote_port = forwarding.get("remote_port")
            ssh_host = forwarding.get("ssh_host")
            ssh_user = forwarding.get("ssh_user", "mlesn")

            success = self.start_port_forward(
                forward_id=forward_id,
                local_port=local_port,
                remote_host=remote_host,
                remote_port=remote_port,
                ssh_host=ssh_host,
                ssh_user=ssh_user,
            )

            results[endpoint_id] = success

        return results

    def update_cursor_settings_for_localhost(self) -> bool:
        """Update Cursor settings to use localhost endpoints"""
        appdata = os.environ.get("APPDATA", "")
        if not appdata:
            logger.error("APPDATA not set")
            return False

        cursor_settings_path = Path(appdata) / "Cursor" / "User" / "settings.json"
        if not cursor_settings_path.exists():
            logger.warning(f"Cursor settings not found: {cursor_settings_path}")
            return False

        try:
            with open(cursor_settings_path, encoding="utf-8") as f:
                settings = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load Cursor settings: {e}")
            return False

        # Update model endpoints to use localhost forwards
        sections = [
            "cursor.chat.customModels",
            "cursor.composer.customModels",
            "cursor.agent.customModels",
        ]

        updated = False
        for section_key in sections:
            models = settings.get(section_key, [])
            for model in models:
                api_base = model.get("apiBase", "")

                # Check if this endpoint has a port forward
                for forward_id, port_forward in self.active_forwards.items():
                    # Replace remote URLs with localhost
                    if port_forward.remote_host in api_base:
                        new_url = f"http://localhost:{port_forward.local_port}"
                        if api_base != new_url:
                            model["apiBase"] = new_url
                            model["localOnly"] = True
                            model["skipProviderSelection"] = True
                            updated = True
                            logger.info(
                                f"Updated {model.get('name')} to use localhost:{port_forward.local_port}"
                            )

        if updated:
            # Backup existing settings
            backup_path = cursor_settings_path.with_suffix(".json.backup")
            if cursor_settings_path.exists():
                import shutil

                shutil.copy2(cursor_settings_path, backup_path)

            # Write updated settings
            with open(cursor_settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Updated Cursor settings: {cursor_settings_path}")
            return True

        return False

    def create_windows_service(self) -> bool:
        """Create Windows service for persistent port forwarding"""
        # This would require additional setup with NSSM or similar
        logger.info("Windows service creation not yet implemented")
        return False

    def print_status(self):
        """Print status of active port forwards"""
        print("=" * 80)
        print("IDE WORKAROUND AUTOMATION STATUS")
        print("=" * 80)

        if self.active_forwards:
            print(f"\nActive Port Forwards: {len(self.active_forwards)}")
            for forward_id, port_forward in self.active_forwards.items():
                status = (
                    "✅ Running"
                    if port_forward.process and port_forward.process.poll() is None
                    else "❌ Stopped"
                )
                print(f"  {forward_id}:")
                print(f"    Status: {status}")
                print(
                    f"    Forward: localhost:{port_forward.local_port} → {port_forward.ssh_host}:{port_forward.remote_port}"
                )
                if port_forward.pid:
                    print(f"    PID: {port_forward.pid}")
                print()
        else:
            print("\nNo active port forwards")

        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Automate IDE integration workarounds")
    parser.add_argument(
        "--setup-all", action="store_true", help="Setup all port forwards from registry"
    )
    parser.add_argument(
        "--update-cursor",
        action="store_true",
        help="Update Cursor settings to use localhost endpoints",
    )
    parser.add_argument("--status", action="store_true", help="Show status of active port forwards")
    parser.add_argument("--stop", metavar="FORWARD_ID", help="Stop a specific port forward")

    args = parser.parse_args()

    automation = IDEWorkaroundAutomation(project_root)

    if args.setup_all:
        results = automation.setup_all_forwards_from_registry()
        print("\nSetup Results:")
        for endpoint_id, success in results.items():
            print(f"  {'✅' if success else '❌'} {endpoint_id}")

        if args.update_cursor:
            automation.update_cursor_settings_for_localhost()

    if args.update_cursor:
        automation.update_cursor_settings_for_localhost()

    if args.stop:
        automation.stop_port_forward(args.stop)

    if args.status or (not args.setup_all and not args.update_cursor and not args.stop):
        automation.print_status()


if __name__ == "__main__":
    main()
