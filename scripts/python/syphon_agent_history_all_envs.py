#!/usr/bin/env python3
"""
SYPHON Agent History Processor - All Environments
Processes all centralized agent history from all environments through SYPHON

IMPORTANT: Agent History = Logs (centralized on NAS)

Extracts actionable intelligence from:
- R5 session files (conversation history)
- Pattern history files
- Fix history files
- Agent communication logs
- Centralized logs on NAS (\\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups\\logs or similar)
- Any other agent interaction data

NAS Access:
- Default NAS path: \\\\<NAS_PRIMARY_IP>\\backups\\MATT_Backups
- SSH access: backupadm@<NAS_PRIMARY_IP> (admin, sudoless)
- Script uses SSH to access centralized logs on NAS

Caching:
- Proxy caching enabled for NAS files (24 hour expiry)
- Files cached in: data/syphon/cache/nas_files/
- Results cached to avoid re-processing
- Expired cache files auto-cleaned
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import tempfile
import subprocess
import hashlib
import shutil
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent

# Cache directories
CACHE_DIR = project_root.parent / "data" / "syphon" / "cache"
NAS_CACHE_DIR = CACHE_DIR / "nas_files"
RESULTS_CACHE_DIR = CACHE_DIR / "results"
CACHE_EXPIRY_HOURS = 24  # Cache expires after 24 hours

# Ensure cache directories exist
CACHE_DIR.mkdir(parents=True, exist_ok=True)
NAS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_CACHE_DIR.mkdir(parents=True, exist_ok=True)

# Try to import NAS SSH integration
try:
    from nas_azure_vault_integration import NASAzureVaultIntegration
    NAS_SSH_AVAILABLE = True
except ImportError:
    NAS_SSH_AVAILABLE = False
    print("⚠️  NAS SSH integration not available - will try direct SSH commands")

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    from r5_living_context_matrix import R5LivingContextMatrix

    syphon = SYPHONSystem(SYPHONConfig(project_root=project_root, subscription_tier=SubscriptionTier.ENTERPRISE))
    r5 = R5LivingContextMatrix(project_root)

    # Register missing extractors
    from syphon.extractors import CodeExtractor, SocialExtractor

            # Register CodeExtractor for CODE type
    if DataSourceType.CODE not in syphon.extractors:
        syphon.register_extractor(DataSourceType.CODE, CodeExtractor(syphon.config))
        print("✅ Registered CodeExtractor")

    # Register IDE Extractor for IDE diagnostics
    if DataSourceType.IDE not in syphon.extractors:
        from syphon.extractors import IDEExtractor
        syphon.register_extractor(DataSourceType.IDE, IDEExtractor(syphon.config))
        print("✅ Registered IDEExtractor")

    # Register SocialExtractor as fallback for DOCUMENT and OTHER types
    # (SocialExtractor can handle general text content)
    if DataSourceType.DOCUMENT not in syphon.extractors:
        syphon.register_extractor(DataSourceType.DOCUMENT, SocialExtractor(syphon.config))
        print("✅ Registered SocialExtractor for DOCUMENT type")

    if DataSourceType.OTHER not in syphon.extractors:
        syphon.register_extractor(DataSourceType.OTHER, SocialExtractor(syphon.config))
        print("✅ Registered SocialExtractor for OTHER type")


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

    def find_cursor_history_on_nas(timeout: int = 10) -> List[Dict[str, Any]]:
        """Find Cursor chat/agent history on NAS from ALL machines (laptop, desktop, etc.)"""
        cursor_history = []

        if not NAS_SSH_AVAILABLE:
            return cursor_history

        try:
            nas = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
            ssh_client = nas.get_ssh_client()

            if not ssh_client:
                return cursor_history

            try:
                # Search for Cursor history on NAS (centralized from all machines)
                search_patterns = [
                    "/volume1/backups/MATT_Backups/logs/**/cursor*",
                    "/volume1/backups/MATT_Backups/logs/**/agent_history/**/*.json",
                    "/volume1/backups/MATT_Backups/logs/**/ide_diagnostics/**/*.json",
                    "/volume1/backups/**/Cursor/**/*.json",
                    "/volume1/backups/**/cursor_chat/**/*.json"
                ]

                for pattern in search_patterns:
                    # Use find command with timeout
                    cmd = f"find {pattern.split('**')[0]} -name '*.json' -type f -mtime -30 2>/dev/null | head -100"
                    stdin, stdout, stderr = ssh_client.exec_command(cmd, timeout=timeout)
                    stdout.settimeout(timeout)

                    result = stdout.read().decode('utf-8').strip()
                    if result:
                        for line in result.split('\n'):
                            if line.strip() and line.endswith('.json'):
                                # Get file info
                                stat_cmd = f"stat -c '%s %Y' '{line.strip()}' 2>/dev/null"
                                stdin_stat, stdout_stat, _ = ssh_client.exec_command(stat_cmd, timeout=timeout)
                                stdout_stat.settimeout(timeout)
                                stat_result = stdout_stat.read().decode('utf-8').strip()

                                if stat_result:
                                    parts = stat_result.split()
                                    if len(parts) >= 2:
                                        file_size = int(parts[0])
                                        modified_time = datetime.fromtimestamp(int(parts[1])).isoformat()

                                        # Filter for conversation files (skip entries.json)
                                        if file_size > 1000 and 'entries.json' not in line:
                                            cursor_history.append({
                                                "path": line.strip(),
                                                "type": "cursor_history_nas",
                                                "size": file_size,
                                                "modified": modified_time,
                                                "source": "nas_centralized_cursor_history",
                                                "machine": "ALL_MACHINES"  # Centralized from all
                                            })

            finally:
                ssh_client.close()

        except Exception as e:
            print(f"⚠️  Error searching NAS for Cursor history: {e}")

        return cursor_history

    def find_nas_logs_via_ssh(timeout: int = 10) -> List[Dict[str, Any]]:
        """Find agent history logs on NAS via SSH with timeout"""
        nas_logs = []

        if not NAS_SSH_AVAILABLE:
            print("⚠️  NAS SSH integration not available - skipping NAS log discovery")
            return nas_logs

        try:
            print("\n🔍 Searching for logs on NAS via SSH (timeout: {}s)...".format(timeout))

            # Initialize NAS integration
            nas = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
            ssh_client = nas.get_ssh_client()

            if not ssh_client:
                print("⚠️  Could not establish SSH connection to NAS - skipping")
                return nas_logs

            try:
                # More specific, faster search paths (limit scope to avoid stalling)
                log_search_paths = [
                    ("/volume1/backups/MATT_Backups/logs", True),
                    ("/volume1/backups/MATT_Backups/agent_history", True),
                    ("/volume1/backups/MATT_Backups/centralized_logs", True),
                ]

                # Find log files with timeout
                for search_path, check_exists in log_search_paths:
                    try:
                        # First check if path exists (faster than find on non-existent paths)
                        if check_exists:
                            check_cmd = f"test -d '{search_path}' && echo 'exists' || echo 'notfound'"
                            stdin_check, stdout_check, stderr_check = ssh_client.exec_command(check_cmd, timeout=timeout)
                            stdout_check.settimeout(timeout)
                            # Read all available data (timeout already set via settimeout above)
                            exists_result = stdout_check.read().decode('utf-8').strip() if hasattr(stdout_check, 'read') else ''
                            if exists_result == 'notfound':
                                continue

                        # Use find command with timeout and limit results
                        # Set channel timeout before exec
                        channel = ssh_client.get_transport().open_session()
                        channel.settimeout(timeout + 5)
                        find_cmd = f"timeout {timeout} find '{search_path}' -maxdepth 3 -type f \\( -name '*.log' -o -name '*.json' \\) 2>/dev/null | head -50"
                        channel.exec_command(find_cmd)

                        # Read with timeout
                        output = ""
                        try:
                            output_bytes = b''
                            while True:
                                try:
                                    data = channel.recv(4096)
                                    if not data:
                                        break
                                    output_bytes += data
                                    if len(output_bytes) > 1024 * 1024:  # Limit to 1MB output
                                        break
                                except:
                                    break
                            output = output_bytes.decode('utf-8', errors='ignore').strip()
                            channel.close()
                        except Exception as read_err:
                            channel.close()
                            print(f"   ⚠️  Timeout reading from {search_path}: {read_err}")
                            continue

                        if output:
                            file_count = 0
                            for line in output.split('\n'):
                                if line.strip() and file_count < 50:  # Limit files per path
                                    file_path = line.strip()
                                    # Quick size check (skip if too large > 100MB to avoid download issues)
                                    try:
                                        size_channel = ssh_client.get_transport().open_session()
                                        size_channel.settimeout(5)
                                        size_cmd = f"stat -f%z '{file_path}' 2>/dev/null || stat -c%s '{file_path}' 2>/dev/null || echo 0"
                                        size_channel.exec_command(size_cmd)
                                        size_bytes = b''
                                        while True:
                                            try:
                                                data = size_channel.recv(1024)
                                                if not data:
                                                    break
                                                size_bytes += data
                                            except:
                                                break
                                        size_str = size_bytes.decode('utf-8', errors='ignore').strip()
                                        size = int(size_str) if size_str.isdigit() else 0
                                        size_channel.close()
                                    except:
                                        size = 0

                                    # Skip very large files (might cause issues)
                                    if size > 100 * 1024 * 1024:  # > 100MB
                                        continue

                                    if size > 0:  # Only include non-empty files
                                        nas_logs.append({
                                            "path": file_path,
                                            "type": "agent_history_log",
                                            "size": size,
                                            "modified": datetime.now().isoformat(),  # Skip mtime fetch to speed up
                                            "source": "nas_ssh",
                                            "ssh_path": file_path
                                        })
                                        file_count += 1

                    except Exception as e:
                        print(f"   ⚠️  Error searching {search_path}: {e}")
                        continue

                print(f"   ✅ Found {len(nas_logs)} log files on NAS")

            finally:
                ssh_client.close()

            return nas_logs

        except Exception as e:
            print(f"⚠️  Error accessing NAS via SSH: {e}")
            print("   Continuing with local files only...")
            return nas_logs

    def get_file_cache_key(ssh_path: str, file_size: int, modified_time: str) -> str:
        """Generate cache key for a file"""
        cache_string = f"{ssh_path}:{file_size}:{modified_time}"
        return hashlib.md5(cache_string.encode()).hexdigest()

    def get_cached_file(ssh_path: str, file_size: int, modified_time: str) -> Optional[str]:
        """Check if file is cached and still valid"""
        cache_key = get_file_cache_key(ssh_path, file_size, modified_time)
        cache_file = NAS_CACHE_DIR / f"{cache_key}.cache"
        cache_meta = NAS_CACHE_DIR / f"{cache_key}.meta"

        if not cache_file.exists() or not cache_meta.exists():
            return None

        try:
            # Check if cache is expired
            with open(cache_meta, 'r') as f:
                cache_data = json.load(f)

            cached_time = datetime.fromisoformat(cache_data.get("cached_at", ""))
            if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
                # Cache expired, delete it
                cache_file.unlink(missing_ok=True)
                cache_meta.unlink(missing_ok=True)
                return None

            # Verify file still exists and is valid
            if cache_file.exists() and cache_file.stat().st_size == file_size:
                print(f"  💾 Using cached file: {Path(ssh_path).name}")
                return str(cache_file)

        except Exception as e:
            # Cache corrupted, delete it
            cache_file.unlink(missing_ok=True)
            cache_meta.unlink(missing_ok=True)

        return None

    def cache_nas_file(ssh_path: str, file_size: int, modified_time: str, temp_file: str) -> str:
        """Cache downloaded NAS file"""
        cache_key = get_file_cache_key(ssh_path, file_size, modified_time)
        cache_file = NAS_CACHE_DIR / f"{cache_key}.cache"
        cache_meta = NAS_CACHE_DIR / f"{cache_key}.meta"

        try:
            # Copy file to cache
            shutil.copy2(temp_file, cache_file)

            # Save metadata
            with open(cache_meta, 'w') as f:
                json.dump({
                    "ssh_path": ssh_path,
                    "file_size": file_size,
                    "modified_time": modified_time,
                    "cached_at": datetime.now().isoformat(),
                    "cache_key": cache_key
                }, f, indent=2)

            return str(cache_file)
        except Exception as e:
            print(f"  ⚠️  Error caching file: {e}")
            return temp_file  # Return original if caching fails

    def download_nas_file_via_ssh(ssh_path: str, file_size: int, modified_time: str, timeout: int = 30) -> Optional[str]:
        """Download a file from NAS via SSH/SFTP with caching proxy"""
        if not NAS_SSH_AVAILABLE:
            return None

        # Check cache first
        cached_file = get_cached_file(ssh_path, file_size, modified_time)
        if cached_file:
            return cached_file

        try:
            nas = NASAzureVaultIntegration(nas_ip="<NAS_PRIMARY_IP>")
            ssh_client = nas.get_ssh_client()

            if not ssh_client:
                return None

            try:
                # Use SFTP to download file with timeout
                sftp = ssh_client.open_sftp()
                sftp.get_channel().settimeout(timeout)

                # Create temp file
                temp_file = tempfile.NamedTemporaryFile(mode='w+b', delete=False, suffix='.log')
                temp_path = temp_file.name
                temp_file.close()

                # Download file with progress (for large files)
                print(f"  ⬇️  Downloading from NAS...")
                sftp.get(ssh_path, temp_path)
                sftp.close()

                # Cache the downloaded file
                cached_path = cache_nas_file(ssh_path, file_size, modified_time, temp_path)

                # Delete temp file if it was cached (cache keeps the file)
                if cached_path != temp_path and Path(temp_path).exists():
                    Path(temp_path).unlink()

                return cached_path

            except Exception as e:
                print(f"  ⚠️  Error downloading {Path(ssh_path).name}: {e}")
                return None
            finally:
                ssh_client.close()

        except Exception as e:
            print(f"  ⚠️  Error connecting to NAS: {e}")
            return None

    def find_cursor_chat_history(include_nas: bool = True) -> List[Dict[str, Any]]:
        """
        Find Cursor chat/agent history from all workspaces AND machines.
        Includes:
        - Current workstation (desktop/laptop)
        - NAS centralized history from all machines
        - History directory (contains conversation JSON files)

        IMPORTANT: This collects agent history from ALL machines (laptop, desktop, etc.)
        not just the current workstation. Agent history is centralized on NAS.
        """
        import os
        cursor_history = []
        current_machine = os.getenv("COMPUTERNAME", "UNKNOWN")

        try:
            appdata = Path(os.getenv("APPDATA", ""))

            # 1. Current workstation: workspaceStorage
            workspace_storage = appdata / "Cursor" / "User" / "workspaceStorage"
            if workspace_storage.exists():
                print(f"🔍 Scanning current workstation ({current_machine}) workspaceStorage...")
                for workspace_dir in workspace_storage.iterdir():
                    if not workspace_dir.is_dir():
                        continue

                    for file_path in workspace_dir.rglob("*"):
                        if not file_path.is_file():
                            continue

                        file_name_lower = file_path.name.lower()

                        if any(keyword in file_name_lower for keyword in [
                            "chat", "conversation", "session", "history", "agent",
                            "message", "thread", "dialogue"
                        ]):
                            if file_path.suffix in [".json", ".db", ".sqlite", ".sqlite3"]:
                                if file_path.stat().st_size > 100:
                                    cursor_history.append({
                                        "path": file_path,
                                        "type": "cursor_chat_history",
                                        "size": file_path.stat().st_size,
                                        "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
                                        "workspace_id": workspace_dir.name,
                                        "source": f"cursor_workspace_storage_{current_machine}",
                                        "machine": current_machine
                                    })
                print(f"   Found {len([h for h in cursor_history if h['source'].startswith('cursor_workspace_storage')])} workspace files")

            # 2. Current workstation: History directory (conversation JSON files)
            history_dir = appdata / "Cursor" / "User" / "History"
            if history_dir.exists():
                print(f"🔍 Scanning current workstation ({current_machine}) History directory...")
                history_count = 0
                for history_file in history_dir.rglob("*.json"):
                    if not history_file.is_file():
                        continue

                    file_size = history_file.stat().st_size
                    file_name = history_file.name.lower()

                    # Skip entries.json (file edit history, not chat)
                    if file_name == "entries.json":
                        continue

                    # Include conversation files (>5KB or chat-related >1KB)
                    is_chat_related = any(kw in file_name for kw in ["chat", "conversation", "session", "agent", "message"])
                    min_size = 5000 if not is_chat_related else 1000

                    if file_size > min_size:
                        cursor_history.append({
                            "path": history_file,
                            "type": "cursor_conversation_history",
                            "size": file_size,
                            "modified": datetime.fromtimestamp(history_file.stat().st_mtime).isoformat(),
                            "source": f"cursor_history_directory_{current_machine}",
                            "machine": current_machine
                        })
                        history_count += 1
                print(f"   Found {history_count} conversation files")

            # 3. NAS: Centralized agent history from ALL machines (laptop, desktop, etc.)
            if include_nas and NAS_SSH_AVAILABLE:
                print("🔍 Scanning NAS for centralized agent history from ALL machines...")
                nas_cursor_history = find_cursor_history_on_nas()
                cursor_history.extend(nas_cursor_history)
                print(f"   Found {len(nas_cursor_history)} files from NAS (all machines)")

        except Exception as e:
            print(f"⚠️  Error searching Cursor chat history: {e}")

        return cursor_history

    def find_agent_history_files(base_path: Path) -> List[Dict[str, Any]]:
        """Find all agent history files across all environments"""
        history_files = []

        # First, find Cursor chat history from workspaceStorage
        print("🔍 Searching Cursor workspaceStorage for chat history...")
        cursor_history = find_cursor_chat_history()
        if cursor_history:
            print(f"   Found {len(cursor_history)} Cursor chat history files")
            history_files.extend(cursor_history)

        # Define search patterns and directories
        # NOTE: Agent History = Logs (centralized on NAS)
        search_patterns = [
            # R5 session files (conversation history)
            ("**/r5_living_matrix/sessions/*.json", "r5_session"),
            ("**/data/r5_living_matrix/sessions/*.json", "r5_session"),

            # Pattern history
            ("**/data/pattern_history.json", "pattern_history"),

            # Fix history
            ("**/data/fix_history_db/error_history.json", "fix_history"),

            # Agent communication
            ("**/config/agent_communication/*.json", "agent_config"),

            # Chat logs / Agent History (LOCAL)
            ("**/logs/**/*.log", "chat_log"),

            # Agent History Logs (NAS - centralized logging location)
            # These are the actual centralized agent history logs
            ("**/logs/**/*.log", "agent_history_log"),
            ("**/agent_history/**/*.log", "agent_history_log"),
            ("**/agent_history/**/*.json", "agent_history_log"),
            ("**/centralized_logs/**/*.log", "agent_history_log"),
            ("**/centralized_logs/**/*.json", "agent_history_log"),
            ("**/logs/ide_diagnostics/**/*.json", "ide_diagnostics_log"),  # IDE diagnostics from NAS

            # Holocron intelligence reports
            ("**/data/holocron/*.json", "holocron"),

            # Jarvis intelligence
            ("**/data/jarvis_intelligence/*.json", "jarvis_intelligence"),

            # Actionable intelligence
            ("**/data/actionable_intelligence/*.json", "actionable_intelligence"),

            # Peak patterns
            ("**/data/peak_patterns/*.json", "peak_patterns"),
        ]

        for pattern, file_type in search_patterns:
            try:
                for file_path in base_path.glob(pattern):
                    if file_path.is_file() and file_path.stat().st_size > 0:
                        history_files.append({
                            "path": file_path,
                            "type": file_type,
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
                        })
            except Exception as e:
                print(f"⚠️  Error searching pattern {pattern}: {e}")
                continue

        return history_files

    def process_file_through_syphon(file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Process a single history file through SYPHON"""
        file_path = file_info["path"]
        file_type = file_info["type"]
        is_nas_file = file_info.get("source") == "nas_ssh"

        try:
            # Handle NAS files via SSH
            if is_nas_file:
                ssh_path = file_info.get("ssh_path", file_path)
                print(f"\n📄 Processing NAS file: {Path(ssh_path).name} ({file_type})")
                print(f"   NAS Path: {ssh_path}")

                # Download file from NAS (with caching)
                file_size = file_info.get("size", 0)
                modified_time = file_info.get("modified", "")
                temp_file = download_nas_file_via_ssh(ssh_path, file_size, modified_time)
                if not temp_file:
                    return {
                        "file_path": str(ssh_path),
                        "file_type": file_type,
                        "success": False,
                        "error": "Could not download from NAS"
                    }

                # Read from cached/temp file
                with open(temp_file, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                # Store original path for metadata
                original_path = ssh_path
                # Don't delete cache files, only delete if it was a real temp file
                import tempfile as tf
                temp_file_to_delete = temp_file if temp_file.startswith(str(tf.gettempdir())) else None

            else:
                # Handle local files
                file_path = Path(file_path)
                print(f"\n📄 Processing: {file_path.name} ({file_type})")
                print(f"   Path: {file_path}")

                # Read file content
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()

                original_path = str(file_path)
                temp_file_to_delete = None

            # Clean up temp file after reading (only if it's a real temp file, not cached)
            try:
                if temp_file_to_delete and Path(temp_file_to_delete).exists():
                    Path(temp_file_to_delete).unlink()
            except:
                pass  # Ignore cleanup errors

            # Parse JSON if applicable
            try:
                data = json.loads(content)
                content_str = json.dumps(data, indent=2)
            except json.JSONDecodeError:
                # Not JSON, use raw content
                data = None
                content_str = content

            # Determine source type based on file type
            source_type_map = {
                "r5_session": DataSourceType.SOCIAL,
                "pattern_history": DataSourceType.OTHER,
                "fix_history": DataSourceType.CODE,
                "agent_config": DataSourceType.OTHER,
                "chat_log": DataSourceType.SOCIAL,
                "agent_history_log": DataSourceType.SOCIAL,
                "ide_diagnostics_log": DataSourceType.IDE,  # IDE diagnostics from NAS
                "holocron": DataSourceType.DOCUMENT,
                "jarvis_intelligence": DataSourceType.SOCIAL,
                "actionable_intelligence": DataSourceType.DOCUMENT,
                "peak_patterns": DataSourceType.OTHER
            }

            source_type = source_type_map.get(file_type, DataSourceType.OTHER)

            # Create metadata
            if is_nas_file:
                file_name = Path(original_path).name
                file_path_str = original_path
            else:
                file_name = Path(original_path).name
                file_path_str = str(Path(original_path))

            metadata = {
                "file_type": file_type,
                "file_path": file_path_str,
                "file_name": file_name,
                "file_size": file_info["size"],
                "modified": file_info["modified"],
                "processed_at": datetime.now().isoformat(),
                "source": "nas_ssh" if is_nas_file else "local"
            }

            # Extract with SYPHON
            result = syphon.extract(
                source_type,
                content_str,
                metadata
            )

            if result.success and result.data:
                sd = result.data
                return {
                    "file_path": str(file_path),
                    "file_type": file_type,
                    "success": True,
                    "actionable_items": len(sd.actionable_items),
                    "tasks": len(sd.tasks),
                    "intelligence": len(sd.intelligence),
                    "data": sd.to_dict() if hasattr(sd, 'to_dict') else {
                        "data_id": sd.data_id,
                        "source_type": sd.source_type.value if hasattr(sd.source_type, 'value') else str(sd.source_type),
                        "source_id": sd.source_id,
                        "content": sd.content[:500] + "..." if len(sd.content) > 500 else sd.content,
                        "metadata": sd.metadata,
                        "extracted_at": sd.extracted_at.isoformat() if hasattr(sd.extracted_at, 'isoformat') else str(sd.extracted_at),
                        "actionable_items": sd.actionable_items,
                        "tasks": sd.tasks,
                        "intelligence": sd.intelligence
                    }
                }
            else:
                error_msg = result.error if hasattr(result, 'error') else 'Unknown error'
                print(f"  ❌ Extraction failed: {error_msg}")
                return {
                    "file_path": original_path if 'original_path' in locals() else str(file_path),
                    "file_type": file_type,
                    "success": False,
                    "error": error_msg
                }

        except Exception as e:
            print(f"  ❌ Error processing file: {e}")
            import traceback
            traceback.print_exc()
            return {
                "file_path": original_path if 'original_path' in locals() else str(file_info.get("path", "unknown")),
                "file_type": file_type,
                "success": False,
                "error": str(e)
            }

    def ingest_to_r5(extraction_result: Dict[str, Any]) -> Optional[str]:
        """Ingest extracted data to R5"""
        if not extraction_result.get("success") or not extraction_result.get("data"):
            return None

        data_dict = extraction_result["data"]
        file_type = extraction_result["file_type"]
        file_path = Path(extraction_result["file_path"])

        # Extract data from dict format
        content = data_dict.get("content", "")
        metadata = data_dict.get("metadata", {})
        actionable_items = data_dict.get("actionable_items", [])
        tasks = data_dict.get("tasks", [])
        intelligence = data_dict.get("intelligence", [])

        try:
            session_id = r5.ingest_session({
                "session_id": f"syphon_agent_history_{file_type}_{file_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "session_type": f"agent_history_{file_type}",
                "timestamp": datetime.now().isoformat(),
                "content": f"Source: {file_type}\nFile: {file_path.name}\nPath: {file_path}\n\n{content}",
                "metadata": {
                    **metadata,
                    "file_type": file_type,
                    "file_path": str(file_path),
                    "actionable_items": actionable_items,
                    "tasks": tasks,
                    "intelligence": intelligence
                }
            })
            return session_id
        except Exception as e:
            print(f"  ⚠️  R5 ingestion failed: {e}")
            return None

    # Main processing
    print("="*70)
    print("SYPHON Agent History Processor - All Environments")
    print("="*70)

    # Find all agent history files
    print("\n🔍 Searching for agent history files...")

    # Search in multiple base paths (local)
    base_paths = [
        project_root.parent,  # .lumina (parent of scripts/python)
        project_root.parent.parent / "<COMPANY>-financial-services_llc-env",
        project_root.parent.parent / "<COMPANY_ID>-env",
        project_root.parent.parent / "<COMPANY>-financial-services_llc-env_portable",
    ]

    # Also try NAS paths via network share (if accessible)
    nas_paths = [
        Path(r"\\<NAS_PRIMARY_IP>\backups\MATT_Backups"),
        Path(r"\\<NAS_PRIMARY_IP>\backups"),
        Path(r"\\<NAS_PRIMARY_IP>\logs"),
        Path("D:\\Dropbox\\my_projects\\logs") if Path("D:\\Dropbox\\my_projects").exists() else None,
        Path("Z:\\logs") if Path("Z:\\").exists() else None,
        Path("Y:\\logs") if Path("Y:\\").exists() else None,
    ]

    # Add accessible NAS paths (with error handling for authentication)
    for nas_path in nas_paths:
        if nas_path:
            try:
                if nas_path.exists():
                    base_paths.append(nas_path)
                    print(f"📁 Added NAS network path: {nas_path}")
            except (OSError, PermissionError) as e:
                continue  # Skip if not accessible

    all_history_files = []

    # Search local paths
    for base_path in base_paths:
        if base_path.exists():
            print(f"\n📁 Searching in: {base_path}")
            files = find_agent_history_files(base_path)
            all_history_files.extend(files)
            print(f"   Found {len(files)} files")

    # Search NAS via SSH (centralized logging location) - with timeout to avoid stalling
    print("\n🔍 Searching NAS for centralized agent history logs (via SSH)...")
    try:
        nas_logs = find_nas_logs_via_ssh(timeout=15)  # 15 second timeout per search
        if nas_logs:
            all_history_files.extend(nas_logs)
            print(f"   ✅ Added {len(nas_logs)} NAS log files to processing queue")
        else:
            print("   ℹ️  No NAS logs found or NAS not accessible - continuing with local files")
    except KeyboardInterrupt:
        print("\n⚠️  NAS search interrupted - continuing with local files only")
    except Exception as e:
        print(f"   ⚠️  NAS search failed: {e} - continuing with local files")

    # Remove duplicates (same file path)
    seen_paths = set()
    unique_files = []
    for f in all_history_files:
        path_str = str(f["path"])
        if path_str not in seen_paths:
            seen_paths.add(path_str)
            unique_files.append(f)

    print(f"\n📊 Total unique files found: {len(unique_files)}")

    if not unique_files:
        print("❌ No agent history files found to process")
        sys.exit(1)

    # Group by type
    by_type = {}
    for f in unique_files:
        file_type = f["type"]
        if file_type not in by_type:
            by_type[file_type] = []
        by_type[file_type].append(f)

    print("\n📋 Files by type:")
    for file_type, files in sorted(by_type.items()):
        print(f"   {file_type}: {len(files)} files")

    # Process all files
    print("\n" + "="*70)
    print("Processing files through SYPHON...")
    print("="*70)

    processed = 0
    failed = 0
    ingested = 0

    results = []

    for file_info in unique_files:
        result = process_file_through_syphon(file_info)
        if result:
            results.append(result)
            if result["success"]:
                processed += 1
                print(f"  ✅ Extracted: {result['actionable_items']} items, {result['tasks']} tasks, {result['intelligence']} intelligence")

                # Ingest to R5
                session_id = ingest_to_r5(result)
                if session_id:
                    ingested += 1
                    print(f"  📥 Ingested to R5: {session_id}")
            else:
                failed += 1

    # Summary
    print("\n" + "="*70)
    print("Processing Summary")
    print("="*70)
    print(f"Total files found: {len(unique_files)}")
    print(f"Successfully processed: {processed}")
    print(f"Failed: {failed}")
    print(f"Ingested to R5: {ingested}")

    # Clean old cache files (older than expiry time)
    print("\n🧹 Cleaning expired cache files...")
    try:
        expired_count = 0
        for cache_meta in RESULTS_CACHE_DIR.glob("*.meta"):
            try:
                with open(cache_meta, 'r') as f:
                    cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data.get("cached_at", ""))
                if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
                    cache_file = cache_meta.with_suffix('.cache')
                    cache_meta.unlink(missing_ok=True)
                    cache_file.unlink(missing_ok=True)
                    expired_count += 1
            except:
                continue

        # Also clean old NAS cache files
        for cache_meta in NAS_CACHE_DIR.glob("*.meta"):
            try:
                with open(cache_meta, 'r') as f:
                    cache_data = json.load(f)
                cached_time = datetime.fromisoformat(cache_data.get("cached_at", ""))
                if datetime.now() - cached_time > timedelta(hours=CACHE_EXPIRY_HOURS):
                    cache_file = cache_meta.with_suffix('.cache')
                    cache_meta.unlink(missing_ok=True)
                    cache_file.unlink(missing_ok=True)
                    expired_count += 1
            except:
                continue

        if expired_count > 0:
            print(f"   ✅ Cleaned {expired_count} expired cache files")
    except Exception as e:
        print(f"   ⚠️  Error cleaning cache: {e}")

    # Save summary (without full data objects to avoid serialization issues)
    summary_file = project_root.parent / "data" / "syphon" / f"agent_history_processing_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    summary_file.parent.mkdir(parents=True, exist_ok=True)

    # Create serializable results (remove full data objects, keep summaries)
    serializable_results = []
    for r in results:
        serializable_result = {
            "file_path": r.get("file_path"),
            "file_type": r.get("file_type"),
            "success": r.get("success"),
            "error": r.get("error"),
        }
        if r.get("success"):
            serializable_result.update({
                "actionable_items_count": r.get("actionable_items", 0),
                "tasks_count": r.get("tasks", 0),
                "intelligence_count": r.get("intelligence", 0),
                "data_id": r.get("data", {}).get("data_id") if isinstance(r.get("data"), dict) else None
            })
        serializable_results.append(serializable_result)

    summary = {
        "processed_at": datetime.now().isoformat(),
        "total_files": len(unique_files),
        "successfully_processed": processed,
        "failed": failed,
        "ingested_to_r5": ingested,
        "files_by_type": {k: len(v) for k, v in by_type.items()},
        "results": serializable_results
    }

    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n📄 Summary saved to: {summary_file}")
    print("\n✅ Complete!")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

