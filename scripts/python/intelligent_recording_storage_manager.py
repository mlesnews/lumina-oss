#!/usr/bin/env python3
"""
Intelligent Recording Storage Manager

Prevents "dev/null" scenario by managing recording storage intelligently.
Real-world solution for space issues - automated storage management.

Features:
1. Intelligent recording policies (not everything)
2. Automatic cleanup/archival
3. Storage monitoring and alerts
4. Tiered storage (hot/cold/archive)
5. Compression and deduplication
6. Automated space management

Tags: #STORAGE #RECORDING #AUTOMATION #SPACE-MANAGEMENT #PREVENT-DEV-NULL @JARVIS @TEAM
"""

import sys
import json
import shutil
import gzip
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    from standardized_timestamp_logging import get_timestamp_logger, TimestampFormat
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    get_timestamp_logger = lambda: None

logger = get_logger("IntelligentRecordingStorage")
ts_logger = get_timestamp_logger()


@dataclass
class StoragePolicy:
    """Storage management policy"""
    max_size_gb: float = 10.0  # Maximum storage for recordings
    retention_days: int = 30  # Keep recordings for N days
    compression_enabled: bool = True  # Compress old recordings
    archive_enabled: bool = True  # Archive to external storage
    deduplication_enabled: bool = True  # Remove duplicate recordings
    auto_cleanup: bool = True  # Automatic cleanup
    alert_threshold_percent: float = 80.0  # Alert at 80% capacity


@dataclass
class RecordingMetadata:
    """Recording file metadata"""
    file_path: str
    size_bytes: int
    created_time: str
    last_accessed: str
    session_id: str
    transcript_available: bool = False
    compressed: bool = False
    archived: bool = False
    hash: Optional[str] = None  # For deduplication


class IntelligentRecordingStorageManager:
    """
    Intelligent Recording Storage Manager

    Prevents storage overflow by:
    - Intelligent recording policies
    - Automatic cleanup
    - Compression
    - Archival
    - Deduplication
    """

    def __init__(self, project_root: Optional[Path] = None, 
                 policy: Optional[StoragePolicy] = None):
        """
        Initialize storage manager

        Args:
            project_root: Project root directory
            policy: Storage management policy
        """
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.policy = policy or StoragePolicy()

        # Storage directories
        self.recordings_dir = self.project_root / "data" / "cursor_recording_sessions"
        self.audio_dir = self.recordings_dir / "audio"
        self.transcripts_dir = self.recordings_dir / "transcripts"
        self.archive_dir = self.project_root / "data" / "recordings_archive"
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Metadata tracking
        self.metadata_file = self.recordings_dir / "storage_metadata.json"
        self.metadata: Dict[str, RecordingMetadata] = {}
        self._load_metadata()

        logger.info("💾 Intelligent Recording Storage Manager initialized")
        logger.info(f"   Max storage: {self.policy.max_size_gb} GB")
        logger.info(f"   Retention: {self.policy.retention_days} days")

    def _load_metadata(self):
        """Load storage metadata"""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.metadata = {
                        k: RecordingMetadata(**v) for k, v in data.items()
                    }
                logger.info(f"✅ Loaded metadata for {len(self.metadata)} recordings")
            except Exception as e:
                logger.warning(f"⚠️  Error loading metadata: {e}")
                self.metadata = {}
        else:
            self.metadata = {}

    def _save_metadata(self):
        """Save storage metadata"""
        try:
            data = {
                k: asdict(v) for k, v in self.metadata.items()
            }
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"❌ Error saving metadata: {e}")

    def get_storage_usage(self) -> Dict[str, Any]:
        try:
            """Get current storage usage"""
            total_size = 0
            file_count = 0

            # Scan audio directory
            if self.audio_dir.exists():
                for file_path in self.audio_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1

            # Scan transcripts
            if self.transcripts_dir.exists():
                for file_path in self.transcripts_dir.rglob("*"):
                    if file_path.is_file():
                        total_size += file_path.stat().st_size
                        file_count += 1

            total_gb = total_size / (1024 ** 3)
            max_gb = self.policy.max_size_gb
            usage_percent = (total_gb / max_gb * 100) if max_gb > 0 else 0

            return {
                "total_size_bytes": total_size,
                "total_size_gb": total_gb,
                "max_size_gb": max_gb,
                "usage_percent": usage_percent,
                "file_count": file_count,
                "available_gb": max_gb - total_gb,
                "needs_cleanup": usage_percent >= self.policy.alert_threshold_percent,
            }

        except Exception as e:
            self.logger.error(f"Error in get_storage_usage: {e}", exc_info=True)
            raise
    def should_record(self) -> Tuple[bool, str]:
        """
        Determine if we should record based on storage policy

        Also checks C: drive space to prevent dev/null scenario

        Returns:
            (should_record, reason)
        """
        # Check C: drive space first (prevent dev/null)
        try:
            import psutil
            c_drive_usage = psutil.disk_usage("C:")
            c_drive_percent = (c_drive_usage.used / c_drive_usage.total) * 100

            if c_drive_percent >= 95:
                return False, f"C: drive at {c_drive_percent:.1f}% capacity - migration required"
            elif c_drive_percent >= 90:
                logger.warning(f"⚠️  C: drive at {c_drive_percent:.1f}% - consider migration")
        except Exception as e:
            logger.debug(f"Could not check C: drive: {e}")

        # Check recording storage
        usage = self.get_storage_usage()

        # Check if we're at capacity
        if usage["usage_percent"] >= 100:
            return False, "Storage at capacity - cleanup required"

        # Check if we're near capacity
        if usage["usage_percent"] >= self.policy.alert_threshold_percent:
            # Try to cleanup first
            self.cleanup_old_recordings()
            usage = self.get_storage_usage()

            if usage["usage_percent"] >= 100:
                return False, "Storage still at capacity after cleanup"

        return True, "Storage available"

    def cleanup_old_recordings(self, force: bool = False) -> Dict[str, Any]:
        """
        Cleanup old recordings based on retention policy

        Args:
            force: Force cleanup even if not needed

        Returns:
            Cleanup statistics
        """
        stats = {
            "files_deleted": 0,
            "space_freed_gb": 0.0,
            "files_compressed": 0,
            "files_archived": 0,
        }

        usage = self.get_storage_usage()

        # Only cleanup if needed or forced
        if not force and not usage["needs_cleanup"]:
            logger.info("✅ Storage usage OK - no cleanup needed")
            return stats

        logger.info("🧹 Starting storage cleanup...")

        cutoff_date = datetime.now() - timedelta(days=self.policy.retention_days)

        # Process recordings
        recordings_to_process = []

        if self.audio_dir.exists():
            for file_path in self.audio_dir.rglob("*.wav"):
                recordings_to_process.append(file_path)

        # Sort by creation time (oldest first)
        recordings_to_process.sort(key=lambda p: p.stat().st_ctime)

        for file_path in recordings_to_process:
            try:
                file_stat = file_path.stat()
                file_age = datetime.fromtimestamp(file_stat.st_ctime)
                file_size = file_stat.st_size

                # Check if file is old enough to delete
                if file_age < cutoff_date:
                    # Check if transcript exists
                    transcript_path = self.transcripts_dir / f"{file_path.stem}.txt"
                    transcript_exists = transcript_path.exists()

                    # If transcript exists, we can delete audio (transcript is smaller)
                    if transcript_exists:
                        file_path.unlink()
                        stats["files_deleted"] += 1
                        stats["space_freed_gb"] += file_size / (1024 ** 3)
                        logger.info(f"🗑️  Deleted old recording: {file_path.name} (transcript preserved)")

                    # If no transcript and compression enabled, compress
                    elif self.policy.compression_enabled:
                        compressed_path = self._compress_file(file_path)
                        if compressed_path:
                            stats["files_compressed"] += 1
                            stats["space_freed_gb"] += (file_size - compressed_path.stat().st_size) / (1024 ** 3)
                            logger.info(f"📦 Compressed: {file_path.name}")

                    # Archive if enabled
                    elif self.policy.archive_enabled:
                        archived = self._archive_file(file_path)
                        if archived:
                            stats["files_archived"] += 1
                            stats["space_freed_gb"] += file_size / (1024 ** 3)
                            logger.info(f"📦 Archived: {file_path.name}")

                    # Last resort: delete if no transcript and no compression/archive
                    else:
                        file_path.unlink()
                        stats["files_deleted"] += 1
                        stats["space_freed_gb"] += file_size / (1024 ** 3)
                        logger.info(f"🗑️  Deleted old recording: {file_path.name}")

                # Check current usage after each deletion
                usage = self.get_storage_usage()
                if usage["usage_percent"] < self.policy.alert_threshold_percent:
                    break

            except Exception as e:
                logger.warning(f"⚠️  Error processing {file_path}: {e}")

        # Deduplication
        if self.policy.deduplication_enabled:
            dup_stats = self._deduplicate_recordings()
            stats["files_deleted"] += dup_stats["duplicates_removed"]
            stats["space_freed_gb"] += dup_stats["space_freed_gb"]

        logger.info(f"✅ Cleanup complete: {stats}")
        return stats

    def _compress_file(self, file_path: Path) -> Optional[Path]:
        """Compress a file"""
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + ".gz")

            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)

            # Delete original
            file_path.unlink()

            return compressed_path
        except Exception as e:
            logger.warning(f"⚠️  Compression failed for {file_path}: {e}")
            return None

    def _archive_file(self, file_path: Path) -> bool:
        """Archive file to external storage"""
        try:
            # Move to archive directory
            archive_path = self.archive_dir / file_path.name
            shutil.move(str(file_path), str(archive_path))
            return True
        except Exception as e:
            logger.warning(f"⚠️  Archive failed for {file_path}: {e}")
            return False

    def _deduplicate_recordings(self) -> Dict[str, Any]:
        """Remove duplicate recordings"""
        stats = {
            "duplicates_removed": 0,
            "space_freed_gb": 0.0,
        }

        # Calculate hashes for all files
        file_hashes = {}

        if self.audio_dir.exists():
            for file_path in self.audio_dir.rglob("*.wav"):
                try:
                    file_hash = self._calculate_file_hash(file_path)
                    if file_hash in file_hashes:
                        # Duplicate found - delete the newer one
                        existing_path = file_hashes[file_hash]
                        if file_path.stat().st_ctime > existing_path.stat().st_ctime:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            stats["duplicates_removed"] += 1
                            stats["space_freed_gb"] += file_size / (1024 ** 3)
                            logger.info(f"🔍 Removed duplicate: {file_path.name}")
                        else:
                            file_size = existing_path.stat().st_size
                            existing_path.unlink()
                            file_hashes[file_hash] = file_path
                            stats["duplicates_removed"] += 1
                            stats["space_freed_gb"] += file_size / (1024 ** 3)
                            logger.info(f"🔍 Removed duplicate: {existing_path.name}")
                    else:
                        file_hashes[file_hash] = file_path
                except Exception as e:
                    logger.warning(f"⚠️  Error hashing {file_path}: {e}")

        return stats

    def _calculate_file_hash(self, file_path: Path) -> str:
        try:
            """Calculate file hash for deduplication"""
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()

        except Exception as e:
            self.logger.error(f"Error in _calculate_file_hash: {e}", exc_info=True)
            raise
    def monitor_storage(self) -> Dict[str, Any]:
        """Monitor storage and alert if needed"""
        usage = self.get_storage_usage()

        alert = None
        if usage["usage_percent"] >= 100:
            alert = "CRITICAL: Storage at 100% capacity - recording disabled"
        elif usage["usage_percent"] >= self.policy.alert_threshold_percent:
            alert = f"WARNING: Storage at {usage['usage_percent']:.1f}% capacity"

        if alert:
            logger.warning(f"⚠️  {alert}")
            # Could send notification here

        return {
            "usage": usage,
            "alert": alert,
            "recommendations": self._get_recommendations(usage),
        }

    def _get_recommendations(self, usage: Dict[str, Any]) -> List[str]:
        """Get storage management recommendations"""
        recommendations = []

        if usage["usage_percent"] >= 90:
            recommendations.append("URGENT: Run cleanup immediately")
            recommendations.append("Consider reducing retention period")
            recommendations.append("Enable compression for old recordings")

        elif usage["usage_percent"] >= self.policy.alert_threshold_percent:
            recommendations.append("Run cleanup to free space")
            recommendations.append("Consider archiving old recordings")

        if usage["file_count"] > 1000:
            recommendations.append("Consider deduplication")

        return recommendations


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="Intelligent Recording Storage Manager")
    parser.add_argument("--check", action="store_true", help="Check storage usage")
    parser.add_argument("--cleanup", action="store_true", help="Cleanup old recordings")
    parser.add_argument("--monitor", action="store_true", help="Monitor storage")
    parser.add_argument("--force", action="store_true", help="Force cleanup")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("💾 Intelligent Recording Storage Manager")
    print("   Prevent dev/null - automated storage management")
    print("="*80 + "\n")

    manager = IntelligentRecordingStorageManager()

    if args.check:
        usage = manager.get_storage_usage()
        print(f"📊 STORAGE USAGE:")
        print(f"   Total: {usage['total_size_gb']:.2f} GB / {usage['max_size_gb']:.2f} GB")
        print(f"   Usage: {usage['usage_percent']:.1f}%")
        print(f"   Available: {usage['available_gb']:.2f} GB")
        print(f"   Files: {usage['file_count']}")
        print(f"   Status: {'⚠️  Needs cleanup' if usage['needs_cleanup'] else '✅ OK'}\n")

    if args.cleanup:
        stats = manager.cleanup_old_recordings(force=args.force)
        print(f"🧹 CLEANUP RESULTS:")
        print(f"   Files deleted: {stats['files_deleted']}")
        print(f"   Files compressed: {stats['files_compressed']}")
        print(f"   Files archived: {stats['files_archived']}")
        print(f"   Space freed: {stats['space_freed_gb']:.2f} GB\n")

    if args.monitor:
        result = manager.monitor_storage()
        print(f"📊 MONITORING:")
        print(f"   Usage: {result['usage']['usage_percent']:.1f}%")
        if result['alert']:
            print(f"   ⚠️  {result['alert']}")
        if result['recommendations']:
            print(f"   Recommendations:")
            for rec in result['recommendations']:
                print(f"      - {rec}")
        print()

    if not any([args.check, args.cleanup, args.monitor]):
        # Default: check and monitor
        usage = manager.get_storage_usage()
        print(f"📊 Storage: {usage['usage_percent']:.1f}% used ({usage['total_size_gb']:.2f} GB / {usage['max_size_gb']:.2f} GB)")

        if usage['needs_cleanup']:
            print("⚠️  Storage needs cleanup - run with --cleanup")
        else:
            print("✅ Storage OK")
        print()


if __name__ == "__main__":


    main()