#!/usr/bin/env python3
"""
SYPHON IDE Diagnostics Processor
Extracts and processes IDE diagnostics, problems, notifications, and queues from VS Code/Cursor

IMPORTANT: IDE Diagnostics = Logs (centralized on NAS)
- All IDE diagnostics, problems, notifications are stored on NAS
- Processed through SYPHON and ingested into R5
- Logs stored in: \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\logs\\ide_diagnostics\\

Processes:
- IDE diagnostics/problems (errors, warnings, info)
- IDE notifications
- Task outputs
- Extension logs
- Workspace storage data

NAS Access:
- Default NAS path: \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups
- Log storage: \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\logs\\ide_diagnostics\\
- SSH access: backupadm@<NAS_PRIMARY_IP> (admin, sudoless)
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import os
import tempfile
import subprocess
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("ingest_ide_diagnostics_syphon")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

# NAS configuration
NAS_BASE_PATH = Path("\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups")
NAS_LOG_PATH = NAS_BASE_PATH / "logs" / "ide_diagnostics"
NAS_SSH_HOST = "<NAS_PRIMARY_IP>"
NAS_SSH_USER = "backupadm"

# Try to import NAS SSH integration
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_SSH_AVAILABLE = True
except ImportError:
    NAS_SSH_AVAILABLE = False
    print("⚠️  NAS SSH integration not available - will use local storage only")

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from syphon.extractors import IDEExtractor
    from r5_living_context_matrix import R5LivingContextMatrix

    syphon = SYPHONSystem(SYPHONConfig(project_root=project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(project_root)

    # Register IDE extractor
    if DataSourceType.IDE not in syphon.extractors:
        syphon.register_extractor(DataSourceType.IDE, IDEExtractor(syphon.config))
        print("✅ Registered IDEExtractor")


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

    def find_ide_storage_paths() -> Dict[str, Path]:
        try:
            """Find VS Code/Cursor storage paths"""
            paths = {}

            appdata = Path(os.getenv("APPDATA", ""))

            # VS Code paths
            vscode_user = appdata / "Code" / "User" / "workspaceStorage"
            vscode_insiders_user = appdata / "Code - Insiders" / "User" / "workspaceStorage"

            # Cursor paths
            cursor_user = appdata / "Cursor" / "User" / "workspaceStorage"

            # Global storage
            vscode_global = appdata / "Code" / "User" / "globalStorage"
            cursor_global = appdata / "Cursor" / "User" / "globalStorage"

            if vscode_user.exists():
                paths["vscode_workspace"] = vscode_user
            if vscode_insiders_user.exists():
                paths["vscode_insiders_workspace"] = vscode_insiders_user
            if cursor_user.exists():
                paths["cursor_workspace"] = cursor_user
            if vscode_global.exists():
                paths["vscode_global"] = vscode_global
            if cursor_global.exists():
                paths["cursor_global"] = cursor_global

            return paths

        except Exception as e:
            logger.error(f"Error in find_ide_storage_paths: {e}", exc_info=True)
            raise
    def extract_diagnostics_from_workspace(workspace_path: Path, ide_type: str) -> List[Dict[str, Any]]:
        """Extract diagnostics from workspace storage"""
        diagnostics = []

        # Look for workspace storage files
        for workspace_dir in workspace_path.iterdir():
            if not workspace_dir.is_dir():
                continue

            # Check for diagnostics in workspace.json
            workspace_json = workspace_dir / "workspace.json"
            if workspace_json.exists():
                try:
                    with open(workspace_json, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if "diagnostics" in data or "problems" in data:
                            diagnostics.append({
                                "workspace": str(workspace_dir),
                                "ide_type": ide_type,
                                "data": data
                            })
                except Exception as e:
                    print(f"⚠️  Error reading {workspace_json}: {e}")

            # Check for state files that might contain diagnostics
            state_files = list(workspace_dir.glob("*.json"))
            for state_file in state_files:
                if state_file.name in ["workspace.json", "state.vscdb", "diagnostics.json"]:
                    try:
                        with open(state_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            if isinstance(data, dict) and ("diagnostics" in data or "problems" in data or "errors" in data):
                                diagnostics.append({
                                    "workspace": str(workspace_dir),
                                    "ide_type": ide_type,
                                    "file": str(state_file),
                                    "data": data
                                })
                    except Exception:
                        pass  # Skip binary or invalid JSON files

        return diagnostics

    def read_linter_diagnostics(workspace_root: Path) -> List[Dict[str, Any]]:
        """Read diagnostics using read_lints tool output format"""
        # This would ideally use VS Code's Language Server Protocol
        # For now, we'll look for common linter output files
        diagnostics = []

        # Check for linter output files
        lint_files = [
            workspace_root / ".eslintcache",
            workspace_root / "tsconfig.tsbuildinfo",
        ]

        # We could also use the read_lints tool programmatically if available
        # For now, return empty - this would need integration with VS Code API

        return diagnostics

    def extract_notifications_from_logs(log_path: Path, ide_type: str) -> List[Dict[str, Any]]:
        """Extract notifications from IDE log files"""
        notifications = []

        if not log_path.exists():
            return notifications

        # Look for log files
        log_files = list(log_path.glob("*.log"))

        for log_file in log_files:
            try:
                with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                    # Extract notification patterns
                    # VS Code logs often have format like: [timestamp] [level] message
                    import re
                    pattern = r'\[(\d{4}-\d{2}-\d{2}T[\d:\.]+)\] \[(\w+)\] (.+)'
                    matches = re.finditer(pattern, content)

                    for match in matches:
                        timestamp, level, message = match.groups()
                        if level.upper() in ["ERROR", "WARN", "INFO"]:
                            notifications.append({
                                "timestamp": timestamp,
                                "severity": level.lower(),
                                "message": message[:500],  # Limit message length
                                "source": log_file.name,
                                "ide_type": ide_type
                            })
            except Exception as e:
                print(f"⚠️  Error reading {log_file}: {e}")

        return notifications

    def ensure_nas_log_directory():
        """Ensure NAS log directory exists"""
        if not NAS_SSH_AVAILABLE:
            # Try direct SMB access
            try:
                NAS_LOG_PATH.mkdir(parents=True, exist_ok=True)
                return True
            except Exception:
                print("⚠️  Could not access NAS via SMB, will use local storage")
                return False

        # Use SSH to create directory
        try:
            nas = NASAzureVaultIntegration(nas_ip=NAS_SSH_HOST)
            ssh_client = nas.get_ssh_client()
            if ssh_client:
                # Create directory via SSH
                cmd = f"mkdir -p /volume1/backups/MATT_Backups/logs/ide_diagnostics"
                stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=10)
                stdout.channel.recv_exit_status()
                ssh_client.close()
                return True
        except Exception as e:
            print(f"⚠️  Could not create NAS directory via SSH: {e}")

        return False

    def save_to_nas(data: Dict[str, Any], filename: str) -> bool:
        """Save extracted IDE diagnostics to NAS"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_filename = f"ide_diagnostics_{timestamp}_{filename}.json"

        # Ensure NAS directory exists
        nas_available = ensure_nas_log_directory()

        if not nas_available:
            # Fallback to local storage
            local_log_dir = project_root.parent / "logs" / "ide_diagnostics"
            local_log_dir.mkdir(parents=True, exist_ok=True)
            log_path = local_log_dir / log_filename
        else:
            if NAS_SSH_AVAILABLE:
                # Use SSH/SFTP to save to NAS
                try:
                    nas = NASAzureVaultIntegration(nas_ip=NAS_SSH_HOST)
                    sftp = nas.get_sftp_client()
                    if sftp:
                        remote_path = f"/volume1/backups/MATT_Backups/logs/ide_diagnostics/{log_filename}"

                        # Write to temp file first, then upload
                        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
                            json.dump(data, tmp, indent=2, default=str)
                            tmp_path = tmp.name

                        try:
                            sftp.put(tmp_path, remote_path)
                            os.unlink(tmp_path)
                            print(f"   💾 Saved to NAS: {remote_path}")
                            return True
                        except Exception as e:
                            print(f"   ⚠️  Error uploading to NAS: {e}")
                            os.unlink(tmp_path)
                            # Fallback to local
                            local_log_dir = project_root.parent / "logs" / "ide_diagnostics"
                            local_log_dir.mkdir(parents=True, exist_ok=True)
                            log_path = local_log_dir / log_filename
                            with open(log_path, 'w') as f:
                                json.dump(data, f, indent=2, default=str)
                            print(f"   💾 Saved locally (fallback): {log_path}")
                            return True
                except Exception as e:
                    print(f"   ⚠️  NAS SSH/SFTP error: {e}")

            # Try direct SMB access
            try:
                log_path = NAS_LOG_PATH / log_filename
                with open(log_path, 'w') as f:
                    json.dump(data, f, indent=2, default=str)
                print(f"   💾 Saved to NAS (SMB): {log_path}")
                return True
            except Exception as e:
                print(f"   ⚠️  SMB access failed: {e}")

        # Final fallback: local storage
        local_log_dir = project_root.parent / "logs" / "ide_diagnostics"
        local_log_dir.mkdir(parents=True, exist_ok=True)
        log_path = local_log_dir / log_filename
        with open(log_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        print(f"   💾 Saved locally: {log_path}")
        return True

    def read_from_nas_via_ssh() -> List[Dict[str, Any]]:
        """Read existing IDE diagnostics logs from NAS via SSH"""
        nas_logs = []

        if not NAS_SSH_AVAILABLE:
            return nas_logs

        try:
            nas = NASAzureVaultIntegration(nas_ip=NAS_SSH_HOST)
            ssh_client = nas.get_ssh_client()

            if not ssh_client:
                return nas_logs

            try:
                # Find existing log files
                find_cmd = "find /volume1/backups/MATT_Backups/logs/ide_diagnostics -maxdepth 1 -name 'ide_diagnostics_*.json' -type f | head -100"
                stdin, stdout, stderr = ssh_client.exec_command(find_cmd, timeout=10)

                output = stdout.read().decode('utf-8', errors='ignore').strip()
                if output:
                    log_files = [line.strip() for line in output.split('\n') if line.strip()]
                    print(f"   Found {len(log_files)} existing IDE diagnostics logs on NAS")
                    nas_logs.extend(log_files)
            except Exception as e:
                print(f"   ⚠️  Error reading NAS logs: {e}")
            finally:
                ssh_client.close()
        except Exception as e:
            print(f"   ⚠️  Error accessing NAS: {e}")

        return nas_logs

    def main():
        """Main processing function"""
        print("🔍 Extracting IDE diagnostics, problems, and notifications...")
        print("=" * 60)
        print(f"📁 NAS Log Path: {NAS_LOG_PATH}")
        print(f"🌐 NAS SSH: {NAS_SSH_USER}@{NAS_SSH_HOST}")
        print()

        # Find IDE storage paths
        storage_paths = find_ide_storage_paths()

        if not storage_paths:
            print("⚠️  No IDE storage paths found")
            return

        print(f"\n✅ Found {len(storage_paths)} IDE storage locations:")
        for name, path in storage_paths.items():
            print(f"   - {name}: {path}")

        all_extracted = []

        # Process workspace storage
        for name, path in storage_paths.items():
            if "workspace" in name:
                ide_type = "vscode" if "vscode" in name else "cursor"
                print(f"\n📂 Processing {ide_type} workspace storage: {path}")

                diagnostics = extract_diagnostics_from_workspace(path, ide_type)
                if diagnostics:
                    print(f"   Found {len(diagnostics)} diagnostic sets")
                    all_extracted.extend(diagnostics)

        # Process log files for notifications
        appdata = Path(os.getenv("APPDATA", ""))
        log_paths = {
            "vscode": appdata / "Code" / "logs",
            "cursor": appdata / "Cursor" / "logs"
        }

        all_notifications = []
        for ide_type, log_path in log_paths.items():
            if log_path.exists():
                print(f"\n📋 Processing {ide_type} logs: {log_path}")
                notifications = extract_notifications_from_logs(log_path, ide_type)
                if notifications:
                    print(f"   Found {len(notifications)} notifications")
                    all_notifications.extend(notifications)

        # Process through SYPHON
        processed_count = 0

        # Process diagnostics
        for diag_data in all_extracted:
            try:
                metadata = {
                    "workspace": diag_data.get("workspace", ""),
                    "ide_type": diag_data.get("ide_type", "unknown"),
                    "file": diag_data.get("file", "")
                }

                result = syphon.extract(
                    source_type=DataSourceType.IDE,
                    content=diag_data.get("data", {}),
                    metadata=metadata
                )

                if result.success and result.data:
                    processed_count += 1
                    print(f"   ✅ Extracted diagnostics from {metadata['workspace']}")

                    # Save to NAS
                    save_to_nas(result.data.to_dict(), f"diagnostics_{diag_data.get('workspace', 'unknown').replace('/', '_')}")

                    # Ingest into R5
                    r5.ingest_session(result.data.to_dict())
            except Exception as e:
                print(f"   ❌ Error processing diagnostics: {e}")

        # Process notifications
        if all_notifications:
            try:
                metadata = {
                    "ide_type": "multiple",
                    "notification_count": len(all_notifications)
                }

                result = syphon.extract(
                    source_type=DataSourceType.IDE,
                    content={"notifications": all_notifications},
                    metadata=metadata
                )

                if result.success and result.data:
                    processed_count += 1
                    print(f"   ✅ Extracted {len(all_notifications)} notifications")

                    # Save to NAS
                    save_to_nas(result.data.to_dict(), "notifications")

                    # Ingest into R5
                    r5.ingest_session(result.data.to_dict())
            except Exception as e:
                print(f"   ❌ Error processing notifications: {e}")

        # Also check for existing logs on NAS
        print("\n📂 Checking for existing IDE diagnostics logs on NAS...")
        existing_logs = read_from_nas_via_ssh()
        if existing_logs:
            print(f"   Found {len(existing_logs)} existing log files on NAS")

        print("\n" + "=" * 60)
        print(f"✅ Processing complete!")
        print(f"   - Processed {processed_count} IDE data sets")
        print(f"   - Extracted diagnostics: {len(all_extracted)}")
        print(f"   - Extracted notifications: {len(all_notifications)}")
        print(f"   - Logs saved to NAS: {NAS_LOG_PATH}")
        print(f"   - NAS SSH: {NAS_SSH_USER}@{NAS_SSH_HOST}")

    if __name__ == "__main__":

        main()
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Make sure SYPHON and R5 are properly configured")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

