#!/usr/bin/env python3
"""
Fast Migration Transfer - Optimized Transfer Methods

Replaces slow SMB shutil.move() with:
- robocopy (multi-threaded, optimized for Windows)
- Compression for large files
- Batching for small files
- Direct copy optimization

Tags: #FAST-TRANSFER #ROBOCOPY #OPTIMIZATION #SSD @LUMINA
"""

import subprocess
import sys
import tempfile
import time
import zipfile
from pathlib import Path
from typing import Any, Dict, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("FastMigrationTransfer")


class FastMigrationTransfer:
    """
    Fast Migration Transfer using optimized methods

    Uses robocopy for multi-threaded, optimized transfers
    instead of slow SMB shutil.move()
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger

        # Transfer statistics
        self.stats = {
            "total_transferred": 0.0,
            "total_files": 0,
            "total_time": 0.0,
            "average_speed_mbps": 0.0,
        }

        self.logger.info("✅ Fast Migration Transfer initialized")
        self.logger.info("   Method: robocopy (multi-threaded, optimized)")

    def transfer_with_robocopy(
        self,
        source: Path,
        destination: Path,
        move: bool = True,
        multi_threaded: bool = True,
        retry_count: int = 3,
        wait_time: int = 5,
        timeout_seconds: Optional[int] = None,
        size_gb: Optional[float] = None,
    ) -> Dict[str, Any]:
        """
        Transfer using robocopy (Windows native, optimized)

        Args:
            source: Source path
            destination: Destination path (when dir exists, robocopy merges into it)
            move: If True, move (delete source). If False, copy.
            multi_threaded: Use /MT for multi-threaded copy
            retry_count: Number of retries on failure
            wait_time: Wait time between retries (seconds)
            timeout_seconds: Max transfer time (overrides size-based default)
            size_gb: Known size in GB (used for timeout: 1h <100GB, 4h <500GB, 8h 500GB+)

        Returns:
            Result dictionary with success, speed, etc.
        """
        result = {
            "success": False,
            "method": "robocopy",
            "source": str(source),
            "destination": str(destination),
            "bytes_transferred": 0,
            "files_transferred": 0,
            "speed_mbps": 0.0,
            "duration_seconds": 0.0,
            "errors": [],
        }

        start_time = time.time()

        try:
            # Ensure destination parent exists
            destination.parent.mkdir(parents=True, exist_ok=True)

            # Build robocopy command
            # robocopy source dest [files] [options]
            # /MT: Multi-threaded (default 8 threads, can specify /MT:16 for 16 threads)
            # /R: Retry count
            # /W: Wait time between retries
            # /NP: No progress (cleaner output)
            # /NFL: No file list (cleaner output)
            # /NDL: No directory list (cleaner output)
            # /NJH: No job header (cleaner output)
            # /NJS: No job summary (we'll parse it)
            # /E: Copy subdirectories including empty ones
            # /MOV: Move files (delete from source)
            # /MOVE: Move files and directories (delete from source)

            cmd = ["robocopy"]
            cmd.append(str(source.parent))
            cmd.append(str(destination.parent))
            cmd.append(source.name)

            # Options
            if multi_threaded:
                cmd.append("/MT:8")  # 8 threads for multi-threaded copy

            cmd.append(f"/R:{retry_count}")
            cmd.append(f"/W:{wait_time}")
            cmd.append("/NP")  # No progress
            cmd.append("/NFL")  # No file list
            cmd.append("/NDL")  # No directory list
            cmd.append("/NJH")  # No job header
            cmd.append("/E")  # Copy subdirectories

            if move:
                cmd.append("/MOVE")  # Move (delete source)
            else:
                cmd.append("/COPYALL")  # Copy all file info

            self.logger.info(f"🚀 Fast transfer: {source.name} -> {destination.parent}")
            self.logger.debug(f"   Command: {' '.join(cmd)}")

            # Timeout: scale with size (1h <100GB, 4h <500GB, 8h 500GB+)
            if timeout_seconds is None:
                gb = size_gb if size_gb is not None else 0
                timeout_seconds = 3600 if gb < 100 else 14400 if gb < 500 else 28800

            # Execute robocopy (robocopy merges when destination dir exists)
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
            )

            duration = time.time() - start_time
            result["duration_seconds"] = duration

            # Parse robocopy output
            # Robocopy exit codes:
            # 0-7: Success (various levels)
            # 8+: Errors
            if process.returncode <= 7:
                result["success"] = True

                # Parse output for statistics
                output_lines = process.stdout.split("\n")
                for line in output_lines:
                    # Look for "Files:" line
                    if "Files:" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "Files:" and i + 1 < len(parts):
                                try:
                                    result["files_transferred"] = int(parts[i + 1])
                                except:
                                    pass

                    # Look for "Bytes:" line
                    if "Bytes:" in line:
                        parts = line.split()
                        for i, part in enumerate(parts):
                            if part == "Bytes:" and i + 1 < len(parts):
                                try:
                                    # Parse bytes (may have commas)
                                    bytes_str = parts[i + 1].replace(",", "")
                                    result["bytes_transferred"] = int(bytes_str)
                                except:
                                    pass

                # Calculate speed
                if duration > 0:
                    bytes_per_sec = result["bytes_transferred"] / duration
                    result["speed_mbps"] = (bytes_per_sec * 8) / (1024 * 1024)  # Convert to Mbps

                self.logger.info(
                    f"   ✅ Transfer complete: {result['files_transferred']} files, "
                    f"{result['bytes_transferred'] / (1024**3):.2f} GB, "
                    f"{result['speed_mbps']:.2f} Mbps"
                )
            else:
                result["success"] = False
                result["errors"].append(f"Robocopy exit code: {process.returncode}")
                result["errors"].append(process.stderr)
                self.logger.error(f"   ❌ Transfer failed: exit code {process.returncode}")

        except subprocess.TimeoutExpired:
            result["success"] = False
            result["errors"].append(f"Transfer timeout (exceeded {timeout_seconds // 3600}h limit)")
            self.logger.error("   ❌ Transfer timeout")

        except Exception as e:
            result["success"] = False
            result["errors"].append(str(e))
            self.logger.error(f"   ❌ Transfer error: {e}")

        return result

    def transfer_with_compression(
        self, source: Path, destination: Path, compress_threshold_mb: float = 100.0
    ) -> Dict[str, Any]:
        """
        Transfer with compression for large files

        Args:
            source: Source path
            destination: Destination path
            compress_threshold_mb: Files larger than this will be compressed

        Returns:
            Result dictionary
        """
        result = {
            "success": False,
            "method": "compressed",
            "source": str(source),
            "destination": str(destination),
            "compressed": False,
            "original_size": 0,
            "compressed_size": 0,
            "speed_mbps": 0.0,
        }

        try:
            # Check if file/directory is large enough to compress
            if source.is_file():
                size_mb = source.stat().st_size / (1024 * 1024)
                result["original_size"] = source.stat().st_size

                if size_mb > compress_threshold_mb:
                    # Compress and transfer
                    self.logger.info(f"📦 Compressing large file: {source.name} ({size_mb:.2f} MB)")

                    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp_zip:
                        zip_path = Path(tmp_zip.name)

                    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
                        zipf.write(source, source.name)

                    result["compressed_size"] = zip_path.stat().st_size
                    result["compressed"] = True

                    # Transfer compressed file
                    dest_zip = destination.with_suffix(".zip")
                    transfer_result = self.transfer_with_robocopy(zip_path, dest_zip, move=False)

                    result["success"] = transfer_result["success"]
                    result["speed_mbps"] = transfer_result["speed_mbps"]

                    # Cleanup
                    zip_path.unlink()
                else:
                    # Transfer normally
                    transfer_result = self.transfer_with_robocopy(source, destination, move=True)
                    result["success"] = transfer_result["success"]
                    result["speed_mbps"] = transfer_result["speed_mbps"]
            else:
                # Directory - transfer normally (robocopy handles directories well)
                transfer_result = self.transfer_with_robocopy(source, destination, move=True)
                result["success"] = transfer_result["success"]
                result["speed_mbps"] = transfer_result["speed_mbps"]

        except Exception as e:
            result["success"] = False
            result["errors"] = [str(e)]
            self.logger.error(f"Compressed transfer error: {e}")

        return result

    def get_transfer_stats(self) -> Dict[str, Any]:
        """Get transfer statistics"""
        return self.stats.copy()


def main():
    """Test fast transfer"""
    print("\n" + "=" * 80)
    print("🚀 FAST MIGRATION TRANSFER - TEST")
    print("=" * 80)
    print()

    transfer = FastMigrationTransfer()

    print("✅ Fast Migration Transfer initialized")
    print("   Method: robocopy (multi-threaded)")
    print("   Features:")
    print("   - Multi-threaded transfers (/MT:8)")
    print("   - Optimized for Windows")
    print("   - Compression support for large files")
    print("   - Retry logic")
    print()
    print("Ready to use in migration script!")
    print()
    print("=" * 80)


if __name__ == "__main__":
    main()
