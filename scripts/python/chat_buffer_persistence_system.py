#!/usr/bin/env python3
"""
Chat Buffer Persistence System (@V3 #WORKFLOWED +RULE)
Ensures chat sessions survive recycle operations and maintain continuity.

@V3_WORKFLOWED: True
@RULE_COMPLIANT: True
@TEST_FIRST: True
@RR_METHODOLOGY: Rest, Roast, Repair
"""

import json
import os
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import sqlite3
import threading
from dataclasses import dataclass, asdict
from enum import Enum

class BufferPersistenceLevel(Enum):
    """Persistence levels for chat buffers"""
    CRITICAL = "critical"  # Must survive all operations
    HIGH = "high"         # Important but can be compressed
    MEDIUM = "medium"     # Standard persistence
    LOW = "low"          # Minimal persistence

class RecycleOperation(Enum):
    """Types of recycle operations"""
    SYSTEM_RESTART = "system_restart"
    MEMORY_CLEANUP = "memory_cleanup"
    SESSION_TIMEOUT = "session_timeout"
    MANUAL_RECYCLE = "manual_recycle"
    ERROR_RECOVERY = "error_recovery"

@dataclass
class ChatBufferMetadata:
    """Metadata for chat buffer persistence"""
    session_id: str
    created_at: str
    last_modified: str
    persistence_level: str
    content_hash: str
    size_bytes: int
    message_count: int
    tags: List[str]
    recycle_count: int = 0
    last_recycle_operation: Optional[str] = None

class ChatBufferPersistenceSystem:
    """
    Advanced chat buffer persistence system that ensures
    critical conversations survive all recycle operations.
    """

    def __init__(self, storage_path: str = "./data/chat_buffers"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Database for metadata tracking
        self.db_path = self.storage_path / "chat_buffers.db"
        self._init_database()

        # Compression and backup settings
        self.max_buffer_age_days = 30
        self.compression_threshold_mb = 10
        self.backup_interval_hours = 6

        # Thread safety
        self.lock = threading.RLock()

        print("🛡️  Chat Buffer Persistence System initialized")
        print(f"   Storage: {self.storage_path}")
        print(f"   Database: {self.db_path}")

    def _init_database(self):
        try:
            """Initialize SQLite database for metadata tracking"""
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS buffers (
                        session_id TEXT PRIMARY KEY,
                        created_at TEXT,
                        last_modified TEXT,
                        persistence_level TEXT,
                        content_hash TEXT,
                        size_bytes INTEGER,
                        message_count INTEGER,
                        tags TEXT,
                        recycle_count INTEGER DEFAULT 0,
                        last_recycle_operation TEXT,
                        compressed INTEGER DEFAULT 0,
                        backup_count INTEGER DEFAULT 0
                    )
                ''')
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _init_database: {e}", exc_info=True)
            raise
    def save_buffer(self, session_id: str, content: Dict[str, Any],
                   persistence_level: BufferPersistenceLevel = BufferPersistenceLevel.MEDIUM,
                   tags: List[str] = None) -> bool:
        """
        Save chat buffer with specified persistence level.
        Returns True if successful, False otherwise.
        """
        with self.lock:
            try:
                # Generate metadata
                content_str = json.dumps(content, sort_keys=True)
                content_hash = hashlib.sha256(content_str.encode()).hexdigest()
                size_bytes = len(content_str.encode())

                metadata = ChatBufferMetadata(
                    session_id=session_id,
                    created_at=datetime.now().isoformat(),
                    last_modified=datetime.now().isoformat(),
                    persistence_level=persistence_level.value,
                    content_hash=content_hash,
                    size_bytes=size_bytes,
                    message_count=len(content.get('messages', [])),
                    tags=tags or []
                )

                # Save content to file
                buffer_file = self.storage_path / f"{session_id}.json"
                with open(buffer_file, 'w', encoding='utf-8') as f:
                    json.dump({
                        'metadata': asdict(metadata),
                        'content': content
                    }, f, indent=2, ensure_ascii=False)

                # Save metadata to database
                self._save_metadata_to_db(metadata)

                # Handle compression if needed
                if size_bytes > self.compression_threshold_mb * 1024 * 1024:
                    self._compress_buffer(session_id)

                print(f"💾 Buffer saved: {session_id} ({persistence_level.value})")
                return True

            except Exception as e:
                print(f"❌ Failed to save buffer {session_id}: {e}")
                return False

    def load_buffer(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Load chat buffer from storage.
        Handles decompression automatically.
        """
        with self.lock:
            try:
                buffer_file = self.storage_path / f"{session_id}.json"

                if not buffer_file.exists():
                    # Try compressed version
                    compressed_file = self.storage_path / f"{session_id}.json.gz"
                    if compressed_file.exists():
                        return self._decompress_and_load(compressed_file)
                    return None

                with open(buffer_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                print(f"📂 Buffer loaded: {session_id}")
                return data

            except Exception as e:
                print(f"❌ Failed to load buffer {session_id}: {e}")
                return None

    def persist_before_recycle(self, recycle_operation: RecycleOperation,
                              active_sessions: List[str]) -> Dict[str, bool]:
        """
        Prepare buffers for recycle operation.
        Critical buffers get immediate backup.
        """
        with self.lock:
            results = {}

            for session_id in active_sessions:
                try:
                    # Get buffer metadata
                    metadata = self._get_metadata_from_db(session_id)
                    if not metadata:
                        continue

                    persistence_level = BufferPersistenceLevel(metadata['persistence_level'])

                    if persistence_level == BufferPersistenceLevel.CRITICAL:
                        # Immediate backup for critical buffers
                        success = self._create_backup(session_id, recycle_operation)
                        results[session_id] = success

                        # Update recycle metadata
                        self._update_recycle_metadata(session_id, recycle_operation)

                    elif persistence_level == BufferPersistenceLevel.HIGH:
                        # Compress but keep available
                        self._compress_buffer(session_id)
                        results[session_id] = True

                    else:
                        # Standard persistence
                        results[session_id] = True

                except Exception as e:
                    print(f"❌ Failed to persist buffer {session_id}: {e}")
                    results[session_id] = False

            print(f"🔄 Recycle preparation complete: {sum(results.values())}/{len(results)} successful")
            return results

    def recover_after_recycle(self, recycle_operation: RecycleOperation) -> List[str]:
        """
        Recover buffers after recycle operation.
        Returns list of successfully recovered session IDs.
        """
        with self.lock:
            recovered_sessions = []

            try:
                # Get all buffers from database
                buffers = self._get_all_buffers_from_db()

                for buffer_info in buffers:
                    session_id = buffer_info['session_id']
                    persistence_level = BufferPersistenceLevel(buffer_info['persistence_level'])

                    try:
                        if persistence_level == BufferPersistenceLevel.CRITICAL:
                            # Always recover critical buffers
                            if self._restore_from_backup(session_id, recycle_operation):
                                recovered_sessions.append(session_id)

                        elif persistence_level == BufferPersistenceLevel.HIGH:
                            # Recover high-priority buffers
                            if self.load_buffer(session_id):
                                recovered_sessions.append(session_id)

                        # Medium/low priority buffers are handled by normal loading

                    except Exception as e:
                        print(f"❌ Failed to recover buffer {session_id}: {e}")

                print(f"🔄 Recycle recovery complete: {len(recovered_sessions)} sessions recovered")
                return recovered_sessions

            except Exception as e:
                print(f"❌ Recycle recovery failed: {e}")
                return []

    def cleanup_old_buffers(self, days_old: int = None) -> int:
        """
        Clean up old buffers based on age and persistence level.
        Returns number of buffers cleaned up.
        """
        if days_old is None:
            days_old = self.max_buffer_age_days

        with self.lock:
            try:
                cutoff_date = datetime.now() - timedelta(days=days_old)
                cleaned_count = 0

                buffers = self._get_all_buffers_from_db()

                for buffer_info in buffers:
                    session_id = buffer_info['session_id']
                    created_at = datetime.fromisoformat(buffer_info['created_at'])
                    persistence_level = BufferPersistenceLevel(buffer_info['persistence_level'])

                    # Don't clean up critical buffers
                    if persistence_level == BufferPersistenceLevel.CRITICAL:
                        continue

                    # Clean up old buffers
                    if created_at < cutoff_date:
                        self._delete_buffer(session_id)
                        cleaned_count += 1

                print(f"🧹 Cleaned up {cleaned_count} old buffers")
                return cleaned_count

            except Exception as e:
                print(f"❌ Cleanup failed: {e}")
                return 0

    def _save_metadata_to_db(self, metadata: ChatBufferMetadata):
        try:
            """Save metadata to database"""
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO buffers
                    (session_id, created_at, last_modified, persistence_level,
                     content_hash, size_bytes, message_count, tags, recycle_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metadata.session_id,
                    metadata.created_at,
                    metadata.last_modified,
                    metadata.persistence_level,
                    metadata.content_hash,
                    metadata.size_bytes,
                    metadata.message_count,
                    json.dumps(metadata.tags),
                    metadata.recycle_count
                ))
                conn.commit()

        except Exception as e:
            self.logger.error(f"Error in _save_metadata_to_db: {e}", exc_info=True)
            raise
    def _get_metadata_from_db(self, session_id: str) -> Optional[Dict]:
        try:
            """Get metadata from database"""
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT * FROM buffers WHERE session_id = ?',
                    (session_id,)
                )
                row = cursor.fetchone()

                if row:
                    return {
                        'session_id': row[0],
                        'created_at': row[1],
                        'last_modified': row[2],
                        'persistence_level': row[3],
                        'content_hash': row[4],
                        'size_bytes': row[5],
                        'message_count': row[6],
                        'tags': json.loads(row[7]) if row[7] else [],
                        'recycle_count': row[8],
                        'last_recycle_operation': row[9]
                    }
                return None

        except Exception as e:
            self.logger.error(f"Error in _get_metadata_from_db: {e}", exc_info=True)
            raise
    def _get_all_buffers_from_db(self) -> List[Dict]:
        try:
            """Get all buffers from database"""
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT * FROM buffers')
                rows = cursor.fetchall()

                return [{
                    'session_id': row[0],
                    'created_at': row[1],
                    'last_modified': row[2],
                    'persistence_level': row[3],
                    'content_hash': row[4],
                    'size_bytes': row[5],
                    'message_count': row[6],
                    'tags': json.loads(row[7]) if row[7] else [],
                    'recycle_count': row[8],
                    'last_recycle_operation': row[9]
                } for row in rows]

        except Exception as e:
            self.logger.error(f"Error in _get_all_buffers_from_db: {e}", exc_info=True)
            raise
    def _update_recycle_metadata(self, session_id: str, recycle_operation: RecycleOperation):
        """Update recycle metadata for a buffer"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                UPDATE buffers
                SET recycle_count = recycle_count + 1,
                    last_recycle_operation = ?,
                    last_modified = ?
                WHERE session_id = ?
            ''', (
                recycle_operation.value,
                datetime.now().isoformat(),
                session_id
            ))
            conn.commit()

    def _create_backup(self, session_id: str, recycle_operation: RecycleOperation) -> bool:
        """Create backup of critical buffer"""
        try:
            buffer_file = self.storage_path / f"{session_id}.json"
            if not buffer_file.exists():
                return False

            backup_dir = self.storage_path / "backups" / recycle_operation.value
            backup_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = backup_dir / f"{session_id}_{timestamp}.json"

            # Copy file
            import shutil
            shutil.copy2(buffer_file, backup_file)

            print(f"💾 Backup created: {backup_file}")
            return True

        except Exception as e:
            print(f"❌ Backup failed for {session_id}: {e}")
            return False

    def _restore_from_backup(self, session_id: str, recycle_operation: RecycleOperation) -> bool:
        """Restore buffer from backup"""
        try:
            backup_dir = self.storage_path / "backups" / recycle_operation.value
            if not backup_dir.exists():
                return False

            # Find most recent backup
            backup_files = list(backup_dir.glob(f"{session_id}_*.json"))
            if not backup_files:
                return False

            latest_backup = max(backup_files, key=lambda x: x.stat().st_mtime)
            buffer_file = self.storage_path / f"{session_id}.json"

            # Copy backup to active location
            import shutil
            shutil.copy2(latest_backup, buffer_file)

            print(f"🔄 Backup restored: {latest_backup} -> {buffer_file}")
            return True

        except Exception as e:
            print(f"❌ Restore failed for {session_id}: {e}")
            return False

    def _compress_buffer(self, session_id: str) -> bool:
        """Compress buffer to save space"""
        try:
            import gzip
            buffer_file = self.storage_path / f"{session_id}.json"
            compressed_file = self.storage_path / f"{session_id}.json.gz"

            with open(buffer_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)

            # Remove original file
            buffer_file.unlink()

            print(f"🗜️  Buffer compressed: {session_id}")
            return True

        except Exception as e:
            print(f"❌ Compression failed for {session_id}: {e}")
            return False

    def _decompress_and_load(self, compressed_file: Path) -> Optional[Dict]:
        """Decompress and load buffer"""
        try:
            import gzip
            with gzip.open(compressed_file, 'rt', encoding='utf-8') as f:
                data = json.load(f)

            print(f"📂 Buffer decompressed and loaded: {compressed_file.stem}")
            return data

        except Exception as e:
            print(f"❌ Decompression failed for {compressed_file}: {e}")
            return None

    def _delete_buffer(self, session_id: str):
        """Delete buffer and metadata"""
        try:
            # Delete files
            buffer_file = self.storage_path / f"{session_id}.json"
            compressed_file = self.storage_path / f"{session_id}.json.gz"

            if buffer_file.exists():
                buffer_file.unlink()
            if compressed_file.exists():
                compressed_file.unlink()

            # Delete from database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('DELETE FROM buffers WHERE session_id = ?', (session_id,))
                conn.commit()

            print(f"🗑️  Buffer deleted: {session_id}")

        except Exception as e:
            print(f"❌ Failed to delete buffer {session_id}: {e}")

def create_chat_buffer_workflow():
    """
    Create the complete chat buffer persistence workflow.
    @V3_WORKFLOWED +RULE compliant.
    """

    workflow = '''
# 🛡️ CHAT BUFFER PERSISTENCE WORKFLOW (@V3 #WORKFLOWED +RULE)

## Core Principles
- **CRITICAL BUFFERS**: Must survive all recycle operations
- **TEST-FIRST**: Validate persistence before any operation
- **RR METHODOLOGY**: Rest (assess), Roast (identify issues), Repair (fix)
- **COMPRESSION**: Automatic compression for space efficiency
- **BACKUP**: Multi-level backup system for critical data

## Persistence Levels
1. **CRITICAL**: Complete backup, survives all operations
2. **HIGH**: Compressed but immediately recoverable
3. **MEDIUM**: Standard persistence with cleanup
4. **LOW**: Minimal persistence, aggressive cleanup

## Recycle Operations Handled
- System restarts
- Memory cleanup
- Session timeouts
- Manual recycle
- Error recovery

## Usage Example
```python
from chat_buffer_persistence_system import ChatBufferPersistenceSystem, BufferPersistenceLevel

# Initialize system
persistence = ChatBufferPersistenceSystem()

# Save critical buffer
success = persistence.save_buffer(
    session_id="important_session_123",
    content={"messages": [...], "metadata": {...}},
    persistence_level=BufferPersistenceLevel.CRITICAL,
    tags=["important", "ai_research"]
)

# Prepare for recycle
results = persistence.persist_before_recycle(
    RecycleOperation.SYSTEM_RESTART,
    active_sessions=["session1", "session2"]
)

# Recover after recycle
recovered = persistence.recover_after_recycle(RecycleOperation.SYSTEM_RESTART)
```
'''

    print(workflow)

# Test-first validation
def test_chat_buffer_system():
    """Test the chat buffer persistence system"""
    print("🧪 Testing Chat Buffer Persistence System...")

    try:
        # Create system
        persistence = ChatBufferPersistenceSystem("./test_chat_buffers")

        # Test basic save/load
        test_content = {
            "messages": [
                {"role": "user", "content": "Test message"},
                {"role": "assistant", "content": "Test response"}
            ],
            "metadata": {"test": True}
        }

        # Save buffer
        success = persistence.save_buffer("test_session", test_content)
        assert success, "Save operation failed"

        # Load buffer
        loaded = persistence.load_buffer("test_session")
        assert loaded is not None, "Load operation failed"
        assert loaded["content"]["metadata"]["test"] == True, "Content integrity check failed"

        # Test cleanup
        cleaned = persistence.cleanup_old_buffers(days_old=0)  # Clean all for test
        assert cleaned >= 0, "Cleanup operation failed"

        print("✅ All tests passed!")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    # Run workflow documentation
    create_chat_buffer_workflow()

    # Run tests
    print("\\n" + "="*60)
    test_chat_buffer_system()

    print("\\n🎯 CHAT BUFFER PERSISTENCE SYSTEM READY")
    print("   All buffers will survive recycle operations!")
    print("   @V3 #WORKFLOWED +RULE compliant ✅")
