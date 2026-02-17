#!/usr/bin/env python3
"""
JARVIS Rear View Mirror System

Resolves all cancelled agent chat sessions and:
- Saves all files
- Accepts all changes in outstanding sessions/asks
- Reviews past sessions (rear view mirror)
- Tracks what's behind us

Tags: #REAR_VIEW_MIRROR #SESSION_RESOLUTION #CHANGE_ACCEPTANCE @JARVIS @LUMINA
"""

import sys
import json
import time
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import re

# fcntl is only available on Unix-like systems
try:
    import fcntl
    HAS_FCNTL = True
except ImportError:
    HAS_FCNTL = False

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from nas_physics_cache import TieredPhysicsCache
    HAS_NAS_CACHE = True
except ImportError:
    HAS_NAS_CACHE = False

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISRearViewMirror")


class SessionTracker:
    """Track chat sessions and asks"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "session_tracking"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_file = self.data_dir / "sessions.json"
        self.asks_file = self.data_dir / "asks.json"
        self.changes_file = self.data_dir / "pending_changes.json"

        self.sessions = []
        self.asks = []
        self.pending_changes = []

        self.load_data()

    def _validate_session_data(self, data: Any) -> bool:
        """Validate session data structure"""
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            if "session_id" not in item or "status" not in item:
                return False
        return True

    def _validate_ask_data(self, data: Any) -> bool:
        """Validate ask data structure"""
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            if "ask_id" not in item or "status" not in item:
                return False
        return True

    def _validate_change_data(self, data: Any) -> bool:
        """Validate change data structure"""
        if not isinstance(data, list):
            return False
        for item in data:
            if not isinstance(item, dict):
                return False
            if "file_path" not in item or "status" not in item:
                return False
        return True

    def _lock_file(self, file_path: Path):
        """Lock file for exclusive access (Unix) or use file existence check (Windows)"""
        if sys.platform == "win32" or not HAS_FCNTL:
            # Windows doesn't support fcntl, use file existence as lock
            lock_file = file_path.with_suffix(file_path.suffix + '.lock')
            max_retries = 10
            retry_delay = 0.1
            for _ in range(max_retries):
                try:
                    if not lock_file.exists():
                        lock_file.touch()
                        return lock_file
                    time.sleep(retry_delay)
                except Exception:
                    time.sleep(retry_delay)
            raise IOError(f"Could not acquire lock for {file_path}")
        else:
            # Unix-like systems
            lock_file = file_path.with_suffix(file_path.suffix + '.lock')
            f = open(lock_file, 'w')
            try:
                fcntl.flock(f.fileno(), fcntl.LOCK_EX)
                return f
            except Exception as e:
                f.close()
                raise IOError(f"Could not acquire lock for {file_path}: {e}")

    def _unlock_file(self, lock_handle):
        """Release file lock"""
        if sys.platform == "win32":
            if isinstance(lock_handle, Path) and lock_handle.exists():
                try:
                    lock_handle.unlink()
                except Exception:
                    pass
        else:
            if lock_handle:
                try:
                    fcntl.flock(lock_handle.fileno(), fcntl.LOCK_UN)
                    lock_handle.close()
                except Exception:
                    pass

    def load_data(self):
        """Load session and ask data with validation"""
        # Load sessions
        if self.sessions_file.exists():
            lock_handle = None
            try:
                lock_handle = self._lock_file(self.sessions_file)
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._validate_session_data(data):
                        self.sessions = data
                    else:
                        logger.warning(f"Invalid session data structure in {self.sessions_file}, using empty list")
                        self.sessions = []
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {self.sessions_file}: {e}")
                self.sessions = []
            except Exception as e:
                logger.error(f"Error loading sessions from {self.sessions_file}: {e}")
                self.sessions = []
            finally:
                if lock_handle:
                    self._unlock_file(lock_handle)

        # Load asks
        if self.asks_file.exists():
            lock_handle = None
            try:
                lock_handle = self._lock_file(self.asks_file)
                with open(self.asks_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._validate_ask_data(data):
                        self.asks = data
                    else:
                        logger.warning(f"Invalid ask data structure in {self.asks_file}, using empty list")
                        self.asks = []
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {self.asks_file}: {e}")
                self.asks = []
            except Exception as e:
                logger.error(f"Error loading asks from {self.asks_file}: {e}")
                self.asks = []
            finally:
                if lock_handle:
                    self._unlock_file(lock_handle)

        # Load pending changes
        if self.changes_file.exists():
            lock_handle = None
            try:
                lock_handle = self._lock_file(self.changes_file)
                with open(self.changes_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if self._validate_change_data(data):
                        self.pending_changes = data
                    else:
                        logger.warning(f"Invalid change data structure in {self.changes_file}, using empty list")
                        self.pending_changes = []
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error in {self.changes_file}: {e}")
                self.pending_changes = []
            except Exception as e:
                logger.error(f"Error loading pending changes from {self.changes_file}: {e}")
                self.pending_changes = []
            finally:
                if lock_handle:
                    self._unlock_file(lock_handle)

    def save_data(self):
        """Save all data with file locking"""
        # Save sessions
        lock_handle = None
        try:
            lock_handle = self._lock_file(self.sessions_file)
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(self.sessions, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving sessions to {self.sessions_file}: {e}")
        finally:
            if lock_handle:
                self._unlock_file(lock_handle)

        # Save asks
        lock_handle = None
        try:
            lock_handle = self._lock_file(self.asks_file)
            with open(self.asks_file, 'w', encoding='utf-8') as f:
                json.dump(self.asks, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving asks to {self.asks_file}: {e}")
        finally:
            if lock_handle:
                self._unlock_file(lock_handle)

        # Save pending changes
        lock_handle = None
        try:
            lock_handle = self._lock_file(self.changes_file)
            with open(self.changes_file, 'w', encoding='utf-8') as f:
                json.dump(self.pending_changes, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving pending changes to {self.changes_file}: {e}")
        finally:
            if lock_handle:
                self._unlock_file(lock_handle)

    def add_session(self, session_id: str, status: str, files_modified: List[str] = None):
        """Add or update session"""
        session = {
            "session_id": session_id,
            "status": status,
            "files_modified": files_modified or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        # Update existing or add new
        existing = next((s for s in self.sessions if s.get("session_id") == session_id), None)
        if existing:
            existing.update(session)
        else:
            self.sessions.append(session)

    def add_ask(self, ask_id: str, question: str, status: str, changes: List[Dict] = None):
        """Add or update ask"""
        ask = {
            "ask_id": ask_id,
            "question": question,
            "status": status,
            "changes": changes or [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }

        existing = next((a for a in self.asks if a.get("ask_id") == ask_id), None)
        if existing:
            existing.update(ask)
        else:
            self.asks.append(ask)

    def add_pending_change(self, file_path: str, change_type: str, description: str):
        """Add pending change"""
        change = {
            "file_path": file_path,
            "change_type": change_type,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "pending"
        }

        # Check if already exists
        existing = next((c for c in self.pending_changes 
                        if c.get("file_path") == file_path and c.get("status") == "pending"), None)
        if not existing:
            self.pending_changes.append(change)


class ChatRequestPinManager:
    """Pin/unpin/read/unread/archive system for chat request IDs"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "chat_request_pins"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.pins_file = self.data_dir / "pins.json"

        # Initialize Cache if available
        self.cache = None
        if HAS_NAS_CACHE:
            try:
                # Load cache config from yaml if possible
                import yaml
                cache_config_path = project_root / "config" / "nas_proxy_cache_config.yaml"
                if cache_config_path.exists():
                    with open(cache_config_path, 'r') as f:
                        full_config = yaml.safe_load(f)
                        # Extract relevant parts for TieredPhysicsCache
                        cache_config = {
                            'memory_limit': 512 * 1024 * 1024,
                            'ssd_cache_dir': str(project_root / "data" / "cache" / "pins"),
                            'nas_config': full_config.get('nas', {})
                        }
                        self.cache = TieredPhysicsCache(cache_config)
                        logger.info("✅ TieredPhysicsCache initialized for PinManager")
            except Exception as e:
                logger.warning(f"⚠️  Failed to initialize cache for PinManager: {e}")

        self.pins = self._load_pins()

    def _load_pins(self) -> Dict[str, Any]:
        """Load pin data with cache support"""
        # Try cache first
        if self.cache:
            try:
                cached_data = self.cache.get("chat_request_pins")
                if cached_data:
                    logger.debug("📌 Loaded pins from Proxy Cache")
                    return cached_data
            except Exception as e:
                logger.debug(f"Cache get failed: {e}")

        if self.pins_file.exists():
            try:
                with open(self.pins_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        # Seed cache
                        if self.cache:
                            try:
                                self.cache.put("chat_request_pins", data, physics_domain="jarvis_pins")
                            except Exception as e:
                                logger.debug(f"Cache put failed: {e}")
                        return data
            except Exception as e:
                logger.error(f"Error loading pins: {e}")

        return {
            "pinned": {},
            "archived": {},
            "read_status": {},
            "metadata": {
                "last_updated": datetime.now().isoformat()
            }
        }

    def _save_pins(self):
        """Save pin data with cache support"""
        try:
            self.pins["metadata"]["last_updated"] = datetime.now().isoformat()

            # Save to cache first (L1/L2)
            if self.cache:
                try:
                    self.cache.put("chat_request_pins", self.pins, physics_domain="jarvis_pins")
                    logger.debug("📌 Saved pins to Proxy Cache")
                except Exception as e:
                    logger.debug(f"Cache put failed: {e}")

            # Still write to disk but the cache provides immediate consistency for other processes
            with open(self.pins_file, 'w', encoding='utf-8') as f:
                json.dump(self.pins, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving pins: {e}")

    def pin_request(self, request_id: str, description: str = None, priority: str = "normal"):
        """Pin a request ID"""
        if request_id not in self.pins["pinned"]:
            self.pins["pinned"][request_id] = {
                "request_id": request_id,
                "description": description or f"Pinned request {request_id}",
                "priority": priority,
                "pinned_at": datetime.now().isoformat(),
                "pinned_by": "system",
                "read": False,
                "archived": False
            }
            self._save_pins()
            logger.info(f"📌 Pinned request: {request_id}")
        return self.pins["pinned"][request_id]

    def unpin_request(self, request_id: str):
        """Unpin a request ID"""
        if request_id in self.pins["pinned"]:
            del self.pins["pinned"][request_id]
            self._save_pins()
            logger.info(f"📌 Unpinned request: {request_id}")
        return True

    def mark_read(self, request_id: str):
        """Mark request as read"""
        if request_id in self.pins["pinned"]:
            self.pins["pinned"][request_id]["read"] = True
            self.pins["pinned"][request_id]["read_at"] = datetime.now().isoformat()
        self.pins["read_status"][request_id] = {
            "read": True,
            "read_at": datetime.now().isoformat()
        }
        self._save_pins()
        logger.info(f"✅ Marked request as read: {request_id}")

    def mark_unread(self, request_id: str):
        """Mark request as unread"""
        if request_id in self.pins["pinned"]:
            self.pins["pinned"][request_id]["read"] = False
            if "read_at" in self.pins["pinned"][request_id]:
                del self.pins["pinned"][request_id]["read_at"]
        self.pins["read_status"][request_id] = {
            "read": False,
            "read_at": None
        }
        self._save_pins()
        logger.info(f"📬 Marked request as unread: {request_id}")

    def archive_request(self, request_id: str):
        """Archive a request ID"""
        if request_id in self.pins["pinned"]:
            pin_data = self.pins["pinned"][request_id].copy()
            pin_data["archived_at"] = datetime.now().isoformat()
            self.pins["archived"][request_id] = pin_data
            del self.pins["pinned"][request_id]
            self._save_pins()
            logger.info(f"📦 Archived request: {request_id}")
        return True

    def unarchive_request(self, request_id: str):
        """Unarchive a request ID"""
        if request_id in self.pins["archived"]:
            archived_data = self.pins["archived"][request_id].copy()
            archived_data.pop("archived_at", None)
            self.pins["pinned"][request_id] = archived_data
            del self.pins["archived"][request_id]
            self._save_pins()
            logger.info(f"📦 Unarchived request: {request_id}")
        return True

    def get_pinned_requests(self, include_read: bool = True) -> List[Dict[str, Any]]:
        """Get all pinned requests"""
        pinned = list(self.pins["pinned"].values())
        if not include_read:
            pinned = [p for p in pinned if not p.get("read", False)]
        # Sort by priority and pinned_at
        pinned.sort(key=lambda x: (
            {"high": 0, "normal": 1, "low": 2}.get(x.get("priority", "normal"), 1),
            x.get("pinned_at", "")
        ))
        return pinned

    def get_archived_requests(self) -> List[Dict[str, Any]]:
        """Get all archived requests"""
        return list(self.pins["archived"].values())

    def is_pinned(self, request_id: str) -> bool:
        """Check if request is pinned"""
        return request_id in self.pins["pinned"]

    def is_read(self, request_id: str) -> bool:
        """Check if request is read"""
        if request_id in self.pins["pinned"]:
            return self.pins["pinned"][request_id].get("read", False)
        return self.pins["read_status"].get(request_id, {}).get("read", False)


class RearViewMirror:
    """Rear view mirror - see what's behind us"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.session_tracker = SessionTracker(project_root)
        self.pin_manager = ChatRequestPinManager(project_root)
        self.data_dir = project_root / "data" / "rear_view_mirror"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def scan_cancelled_sessions(self) -> List[Dict[str, Any]]:
        """Scan for cancelled/incomplete sessions"""
        logger.info("🔍 Scanning for cancelled sessions...")

        cancelled = []

        # Check session tracker
        for session in self.session_tracker.sessions:
            if session.get("status") in ["cancelled", "incomplete", "pending"]:
                cancelled.append(session)

        # Scan logs for cancelled sessions
        logs_dir = self.project_root / "logs"
        if logs_dir.exists():
            for log_file in logs_dir.glob("*.log"):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        # More specific pattern matching
                        content_lower = content.lower()
                        if any(keyword in content_lower for keyword in 
                              ["cancelled", "incomplete", "interrupted"]):
                            # Check for error patterns more specifically
                            error_patterns = [
                                r"error.*session",
                                r"session.*cancelled",
                                r"interrupted.*session"
                            ]
                            if any(re.search(pattern, content_lower) for pattern in error_patterns):
                                cancelled.append({
                                    "source": "log_file",
                                    "file": str(log_file),
                                    "status": "cancelled",
                                    "detected_at": datetime.now().isoformat()
                                })
                except Exception as e:
                    logger.debug(f"Error scanning log file {log_file}: {e}")
                    pass

        logger.info(f"✅ Found {len(cancelled)} cancelled/incomplete sessions")
        return cancelled

    def scan_pending_changes(self) -> List[Dict[str, Any]]:
        """Scan for pending changes"""
        logger.info("🔍 Scanning for pending changes...")

        pending = []

        # From session tracker
        pending.extend(self.session_tracker.pending_changes)

        # Scan for unsaved files (check .cursor or .vscode directories)
        cursor_dir = self.project_root / ".cursor"
        if cursor_dir.exists():
            # Look for session files
            for session_file in cursor_dir.rglob("*.json"):
                try:
                    with open(session_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        if isinstance(data, dict) and data.get("status") == "pending":
                            pending.append({
                                "source": "cursor_session",
                                "file": str(session_file),
                                "status": "pending",
                                "data": data
                            })
                except Exception as e:
                    logger.debug(f"Error scanning session file {session_file}: {e}")
                    pass

        logger.info(f"✅ Found {len(pending)} pending changes")
        return pending

    def scan_unsaved_files(self) -> List[Path]:
        """Scan for unsaved files"""
        logger.info("🔍 Scanning for unsaved files...")

        unsaved = []

        # Check for files with recent modifications but not saved
        # This is a simplified check - in reality, would need IDE integration
        scripts_dir = self.project_root / "scripts" / "python"
        if scripts_dir.exists():
            for py_file in scripts_dir.rglob("*.py"):
                try:
                    # Check if file has unsaved markers or is in a temp state
                    # This is a placeholder - actual implementation would check IDE state
                    stat = py_file.stat()
                    # Files modified in last hour might be unsaved
                    if (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() < 3600:
                        # Check for common unsaved patterns
                        with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            # Look for TODO, FIXME, or incomplete patterns
                            if any(marker in content for marker in ["# TODO", "# FIXME", "# INCOMPLETE"]):  # [ADDRESSED]  # [ADDRESSED]
                                unsaved.append(py_file)
                except Exception as e:
                    logger.debug(f"Error scanning file {py_file}: {e}")
                    pass

        logger.info(f"✅ Found {len(unsaved)} potentially unsaved files")
        return unsaved

    def _resolve_path(self, file_path: str) -> Optional[Path]:
        """Resolve file path with proper validation"""
        if not file_path:
            return None

        try:
            path = Path(file_path)

            # Handle absolute paths
            if path.is_absolute():
                # Ensure it's within project root for security
                try:
                    path.resolve().relative_to(self.project_root.resolve())
                except ValueError:
                    logger.warning(f"Path {file_path} is outside project root, skipping")
                    return None
                return path.resolve()

            # Handle relative paths
            resolved = (self.project_root / path).resolve()

            # Security check: ensure resolved path is still within project root
            try:
                resolved.relative_to(self.project_root.resolve())
            except ValueError:
                logger.warning(f"Resolved path {resolved} is outside project root, skipping")
                return None

            return resolved
        except Exception as e:
            logger.error(f"Error resolving path {file_path}: {e}")
            return None

    def accept_all_changes(self, changes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Accept all pending changes"""
        logger.info("✅ Accepting all changes...")

        accepted = []
        failed = []

        for change in changes:
            try:
                file_path = change.get("file_path") or change.get("file")
                if not file_path:
                    change["status"] = "failed"
                    change["error"] = "No file path provided"
                    failed.append(change)
                    logger.warning(f"   ⚠️  Skipped: No file path")
                    continue

                path = self._resolve_path(file_path)
                if path is None:
                    change["status"] = "failed"
                    change["error"] = "Could not resolve file path"
                    failed.append(change)
                    continue

                # Mark as accepted
                change["status"] = "accepted"
                change["accepted_at"] = datetime.now().isoformat()
                change["resolved_path"] = str(path)
                accepted.append(change)

                logger.info(f"   ✅ Accepted: {path.name}")
            except Exception as e:
                change["status"] = "failed"
                change["error"] = str(e)
                failed.append(change)
                logger.error(f"   ❌ Failed: {change.get('file_path', 'unknown')} - {e}")

        # Update session tracker
        for change in accepted:
            self.session_tracker.pending_changes = [
                c for c in self.session_tracker.pending_changes
                if not (c.get("file_path") == change.get("file_path") and c.get("status") == "pending")
            ]

        self.session_tracker.save_data()

        return {
            "accepted": len(accepted),
            "failed": len(failed),
            "total": len(changes)
        }

    def save_all_files(self) -> Dict[str, Any]:
        """Save all files"""
        logger.info("💾 Saving all files...")

        saved = []
        failed = []

        # Get all modified files from sessions
        all_files = set()
        for session in self.session_tracker.sessions:
            all_files.update(session.get("files_modified", []))

        for file_path in all_files:
            try:
                path = self._resolve_path(file_path)
                if path is None:
                    failed.append({"file": file_path, "error": "Could not resolve file path"})
                    logger.warning(f"   ⚠️  Skipped: {file_path} - Could not resolve path")
                    continue

                if path.exists():
                    # Touch file to update timestamp (simulating save)
                    path.touch()
                    saved.append(str(path))
                    logger.info(f"   💾 Saved: {path.name}")
                else:
                    failed.append({"file": str(path), "error": "File does not exist"})
                    logger.warning(f"   ⚠️  File not found: {path.name}")
            except Exception as e:
                failed.append({"file": file_path, "error": str(e)})
                logger.error(f"   ❌ Failed to save: {file_path} - {e}")

        return {
            "saved": len(saved),
            "failed": len(failed),
            "total": len(all_files)
        }

    def resolve_cancelled_sessions(self) -> Dict[str, Any]:
        """Resolve all cancelled sessions"""
        logger.info("🔧 Resolving cancelled sessions...")

        cancelled = self.scan_cancelled_sessions()
        resolved = []

        for session in cancelled:
            try:
                # Mark as resolved
                session["status"] = "resolved"
                session["resolved_at"] = datetime.now().isoformat()

                # Accept any pending changes
                if "files_modified" in session:
                    for file_path in session["files_modified"]:
                        self.session_tracker.add_pending_change(
                            file_path,
                            "session_resolution",
                            f"Resolved from cancelled session {session.get('session_id', 'unknown')}"
                        )

                resolved.append(session)
                logger.info(f"   ✅ Resolved: {session.get('session_id', 'unknown')}")
            except Exception as e:
                logger.error(f"   ❌ Failed to resolve: {session.get('session_id', 'unknown')} - {e}")

        # Update session tracker
        for session in resolved:
            self.session_tracker.add_session(
                session.get("session_id", f"resolved_{len(resolved)}"),
                "resolved",
                session.get("files_modified", [])
            )

        self.session_tracker.save_data()

        return {
            "resolved": len(resolved),
            "total": len(cancelled)
        }

    def scan_ask_database(self) -> List[Dict[str, Any]]:
        """Scan ask database for all asks"""
        logger.info("🔍 Scanning ask database...")

        asks = []

        # Scan ask_database/asks.json
        ask_db_file = self.project_root / "data" / "ask_database" / "asks.json"
        if ask_db_file.exists():
            try:
                with open(ask_db_file, 'r', encoding='utf-8') as f:
                    ask_db = json.load(f)
                    if isinstance(ask_db, dict):
                        for ask_id, ask_data in ask_db.items():
                            if isinstance(ask_data, dict):
                                asks.append({
                                    "ask_id": ask_id,
                                    "ask_text": ask_data.get("ask_text", ""),
                                    "status": ask_data.get("status", "unknown"),
                                    "submitted_at": ask_data.get("submitted_at", ""),
                                    "priority": ask_data.get("priority", "normal"),
                                    "source": "ask_database"
                                })
            except Exception as e:
                logger.error(f"Error scanning ask database: {e}")

        # Also check session tracker asks
        for ask in self.session_tracker.asks:
            asks.append({
                "ask_id": ask.get("ask_id", "unknown"),
                "ask_text": ask.get("question", ""),
                "status": ask.get("status", "unknown"),
                "submitted_at": ask.get("created_at", ""),
                "priority": "normal",
                "source": "session_tracker"
            })

        logger.info(f"✅ Found {len(asks)} asks in database")
        return asks

    def generate_rear_view_report(self) -> Dict[str, Any]:
        """Generate rear view mirror report"""
        logger.info("🔍 Generating rear view mirror report...")

        cancelled = self.scan_cancelled_sessions()
        pending_changes = self.scan_pending_changes()
        unsaved = self.scan_unsaved_files()
        all_asks = self.scan_ask_database()

        # Get pinned requests
        pinned_requests = self.pin_manager.get_pinned_requests(include_read=True)
        unread_pinned = self.pin_manager.get_pinned_requests(include_read=False)
        archived_requests = self.pin_manager.get_archived_requests()

        # Get recent sessions (last 30 days)
        recent_sessions = []
        for s in self.session_tracker.sessions:
            try:
                created_at_str = s.get("created_at", datetime.now().isoformat())
                created_at = datetime.fromisoformat(created_at_str.replace('Z', '+00:00'))
                if created_at > datetime.now() - timedelta(days=30):
                    recent_sessions.append(s)
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing session date: {e}")
                continue

        # Get recent asks (last 30 days)
        recent_asks = []
        for ask in all_asks:
            try:
                submitted_at_str = ask.get("submitted_at", datetime.now().isoformat())
                if submitted_at_str:
                    submitted_at = datetime.fromisoformat(submitted_at_str.replace('Z', '+00:00'))
                    if submitted_at > datetime.now() - timedelta(days=30):
                        recent_asks.append(ask)
            except (ValueError, TypeError) as e:
                logger.debug(f"Error parsing ask date: {e}")
                continue

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "cancelled_sessions": len(cancelled),
                "pending_changes": len(pending_changes),
                "unsaved_files": len(unsaved),
                "recent_sessions": len(recent_sessions),
                "recent_asks": len(recent_asks),
                "total_asks": len(all_asks),
                "pinned_requests": len(pinned_requests),
                "unread_pinned": len(unread_pinned),
                "archived_requests": len(archived_requests)
            },
            "cancelled_sessions": cancelled[:20],  # Last 20
            "pending_changes": pending_changes[:20],  # Last 20
            "unsaved_files": [str(f) for f in unsaved[:20]],  # Last 20
            "recent_sessions": recent_sessions[-10:],  # Last 10
            "recent_asks": recent_asks[-10:],  # Last 10
            "all_asks": all_asks,  # Full ask stack
            "pinned_requests": pinned_requests,
            "unread_pinned": unread_pinned,
            "archived_requests": archived_requests[-20:],  # Last 20 archived
            "recommendations": []
        }

        # Generate recommendations
        if cancelled:
            report["recommendations"].append(
                f"Resolve {len(cancelled)} cancelled sessions"
            )

        if pending_changes:
            report["recommendations"].append(
                f"Accept {len(pending_changes)} pending changes"
            )

        if unsaved:
            report["recommendations"].append(
                f"Save {len(unsaved)} unsaved files"
            )

        if unread_pinned:
            report["recommendations"].append(
                f"Review {len(unread_pinned)} unread pinned requests"
            )

        if all_asks:
            active_asks = [a for a in all_asks if a.get("status") not in ["completed", "validated", "cancelled"]]
            if active_asks:
                report["recommendations"].append(
                    f"Process {len(active_asks)} active asks from {len(all_asks)} total asks"
                )

        return report

    def execute_full_resolution(self) -> Dict[str, Any]:
        try:
            """Execute full resolution: resolve sessions, accept changes, save files"""
            logger.info("=" * 80)
            logger.info("🚀 JARVIS REAR VIEW MIRROR - FULL RESOLUTION")
            logger.info("=" * 80)
            logger.info("")

            results = {}

            # Step 1: Resolve cancelled sessions
            logger.info("📋 Step 1: Resolving cancelled sessions...")
            results["sessions_resolved"] = self.resolve_cancelled_sessions()
            logger.info("")

            # Step 2: Accept all changes
            logger.info("✅ Step 2: Accepting all changes...")
            pending_changes = self.scan_pending_changes()
            results["changes_accepted"] = self.accept_all_changes(pending_changes)
            logger.info("")

            # Step 3: Save all files
            logger.info("💾 Step 3: Saving all files...")
            results["files_saved"] = self.save_all_files()
            logger.info("")

            # Step 4: Generate report
            logger.info("🔍 Step 4: Generating rear view report...")
            results["rear_view_report"] = self.generate_rear_view_report()
            logger.info("")

            logger.info("=" * 80)
            logger.info("✅ FULL RESOLUTION COMPLETE")
            logger.info("=" * 80)

            # Save report
            report_file = self.data_dir / f"resolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"📄 Report saved: {report_file}")
            logger.info("")

            return results


        except Exception as e:
            self.logger.error(f"Error in execute_full_resolution: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Rear View Mirror")
        parser.add_argument("--resolve", action="store_true", help="Resolve all cancelled sessions")
        parser.add_argument("--accept", action="store_true", help="Accept all pending changes")
        parser.add_argument("--save", action="store_true", help="Save all files")
        parser.add_argument("--full", action="store_true", help="Full resolution (resolve + accept + save)")
        parser.add_argument("--report", action="store_true", help="Generate rear view report")
        parser.add_argument("--scan", action="store_true", help="Scan for cancelled sessions and pending changes")

        # Pin management commands
        parser.add_argument("--pin", type=str, metavar="REQUEST_ID", help="Pin a request ID")
        parser.add_argument("--pin-description", type=str, metavar="DESCRIPTION", help="Description for pinned request (use with --pin)")
        parser.add_argument("--pin-priority", type=str, choices=["high", "normal", "low"], default="normal", help="Priority for pinned request (use with --pin)")
        parser.add_argument("--unpin", type=str, metavar="REQUEST_ID", help="Unpin a request ID")
        parser.add_argument("--read", type=str, metavar="REQUEST_ID", help="Mark request as read")
        parser.add_argument("--unread", type=str, metavar="REQUEST_ID", help="Mark request as unread")
        parser.add_argument("--archive", type=str, metavar="REQUEST_ID", help="Archive a request ID")
        parser.add_argument("--unarchive", type=str, metavar="REQUEST_ID", help="Unarchive a request ID")
        parser.add_argument("--list-pinned", action="store_true", help="List all pinned requests")
        parser.add_argument("--list-archived", action="store_true", help="List all archived requests")
        parser.add_argument("--auto-pin-active", action="store_true", help="Auto-pin all active request IDs")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        mirror = RearViewMirror(project_root)

        # Handle pin management commands
        if args.pin:
            description = args.pin_description or f"Pinned request {args.pin}"
            priority = args.pin_priority or "normal"
            pin_data = mirror.pin_manager.pin_request(args.pin, description, priority)
            print(json.dumps(pin_data, indent=2, default=str))
            return

        if args.unpin:
            mirror.pin_manager.unpin_request(args.unpin)
            print(f"✅ Unpinned: {args.unpin}")
            return

        if args.read:
            mirror.pin_manager.mark_read(args.read)
            print(f"✅ Marked as read: {args.read}")
            return

        if args.unread:
            mirror.pin_manager.mark_unread(args.unread)
            print(f"📬 Marked as unread: {args.unread}")
            return

        if args.archive:
            mirror.pin_manager.archive_request(args.archive)
            print(f"📦 Archived: {args.archive}")
            return

        if args.unarchive:
            mirror.pin_manager.unarchive_request(args.unarchive)
            print(f"📦 Unarchived: {args.unarchive}")
            return

        if args.list_pinned:
            pinned = mirror.pin_manager.get_pinned_requests()
            print("=" * 80)
            print("📌 PINNED REQUESTS")
            print("=" * 80)
            for pin in pinned:
                read_status = "✅ Read" if pin.get("read") else "📬 Unread"
                print(f"{pin['request_id']}: {pin.get('description', '')} [{read_status}]")
            print("=" * 80)
            return

        if args.list_archived:
            archived = mirror.pin_manager.get_archived_requests()
            print("=" * 80)
            print("📦 ARCHIVED REQUESTS")
            print("=" * 80)
            for arch in archived:
                print(f"{arch['request_id']}: {arch.get('description', '')}")
            print("=" * 80)
            return

        if args.auto_pin_active:
            # Load request tracking system
            from jarvis_request_tracking_system import RequestTrackingSystem
            request_tracker = RequestTrackingSystem(project_root)

            # Get all pending/in_flight requests
            all_requests = request_tracker.get_all_requests()
            active_requests = [
                r for r in all_requests 
                if r.get("status") in ["pending", "in_flight", "partial"]
            ]

            pinned_count = 0
            for req in active_requests:
                request_id = req.get("request_id")
                if request_id and not mirror.pin_manager.is_pinned(request_id):
                    mirror.pin_manager.pin_request(
                        request_id,
                        req.get("description", f"Active request {request_id}"),
                        priority="high" if req.get("status") == "in_flight" else "normal"
                    )
                    pinned_count += 1

            print(f"✅ Auto-pinned {pinned_count} active requests")
            return

        if args.full or (not args.resolve and not args.accept and not args.save and not args.report and not args.scan
                         and not args.pin and not args.unpin and not args.read and not args.unread 
                         and not args.archive and not args.unarchive and not args.list_pinned 
                         and not args.list_archived and not args.auto_pin_active):
            # Full resolution
            results = mirror.execute_full_resolution()
            print(json.dumps(results, indent=2, default=str))

        elif args.resolve:
            results = mirror.resolve_cancelled_sessions()
            print(json.dumps(results, indent=2, default=str))

        elif args.accept:
            pending = mirror.scan_pending_changes()
            results = mirror.accept_all_changes(pending)
            print(json.dumps(results, indent=2, default=str))

        elif args.save:
            results = mirror.save_all_files()
            print(json.dumps(results, indent=2, default=str))

        elif args.report:
            report = mirror.generate_rear_view_report()
            print(json.dumps(report, indent=2, default=str))

        elif args.scan:
            cancelled = mirror.scan_cancelled_sessions()
            pending = mirror.scan_pending_changes()
            unsaved = mirror.scan_unsaved_files()

            print("=" * 80)
            print("🔍 SCAN RESULTS")
            print("=" * 80)
            print(f"Cancelled Sessions: {len(cancelled)}")
            print(f"Pending Changes: {len(pending)}")
            print(f"Unsaved Files: {len(unsaved)}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()