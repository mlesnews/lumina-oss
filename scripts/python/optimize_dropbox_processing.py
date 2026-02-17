#!/usr/bin/env python3
"""
Optimize Dropbox Processing
<COMPANY_NAME> LLC

Main entry point for optimizing Dropbox processing:
- Uses caching to avoid re-processing 144k files
- Parallel batch processing with utilization balance
- Energy-efficient, conservative processing

Run this to optimize Dropbox indexing/uploading.

@JARVIS @MARVIN @SYPHON
"""

import sys
from pathlib import Path
import argparse

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from dropbox_optimized_processor import DropboxOptimizedProcessor, ProcessingConfig


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Optimize Dropbox Processing - Resource-aware, utilization-balanced parallel batch processing",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process all files with default settings (recommended)
  python optimize_dropbox_processing.py

  # Process first 1000 files (test run)
  python optimize_dropbox_processing.py --max-files 1000

  # Custom batch size and workers
  python optimize_dropbox_processing.py --batch-size 200 --max-workers 8

  # Disable caching (not recommended - will re-process everything)
  python optimize_dropbox_processing.py --no-cache

  # Maximum performance (no energy saving)
  python optimize_dropbox_processing.py --no-energy-save --max-workers 16
        """
    )

    parser.add_argument(
        "--path",
        type=str,
        default="C:\\Users\\mlesn\\Dropbox",
        help="Dropbox root path (default: C:\\Users\\mlesn\\Dropbox)"
    )

    parser.add_argument(
        "--max-files",
        type=int,
        help="Maximum number of files to process (default: all files)"
    )

    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for processing (default: 100, adaptive based on utilization)"
    )

    parser.add_argument(
        "--max-workers",
        type=int,
        default=4,
        help="Maximum parallel workers (default: 4, adaptive based on utilization)"
    )

    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Disable caching (not recommended - will re-process all files)"
    )

    parser.add_argument(
        "--no-parallel",
        action="store_true",
        help="Disable parallel processing (slower but uses less resources)"
    )

    parser.add_argument(
        "--no-energy-save",
        action="store_true",
        help="Disable energy save mode (faster but uses more energy)"
    )

    parser.add_argument(
        "--no-adaptive",
        action="store_true",
        help="Disable adaptive batching (use fixed batch size and workers)"
    )

    args = parser.parse_args()

    print("=" * 60)
    print("Dropbox Optimized Processing")
    print("=" * 60)
    print(f"Path: {args.path}")
    print(f"Max files: {args.max_files or 'all'}")
    print(f"Batch size: {args.batch_size}")
    print(f"Max workers: {args.max_workers}")
    print(f"Caching: {'disabled' if args.no_cache else 'enabled'}")
    print(f"Parallel: {'disabled' if args.no_parallel else 'enabled'}")
    print(f"Energy save: {'disabled' if args.no_energy_save else 'enabled'}")
    print(f"Adaptive: {'disabled' if args.no_adaptive else 'enabled'}")
    print("=" * 60)
    print()

    # Create configuration
    config = ProcessingConfig(
        batch_size=args.batch_size,
        max_workers=args.max_workers,
        cache_enabled=not args.no_cache,
        parallel_enabled=not args.no_parallel,
        energy_save_mode=not args.no_energy_save,
        adaptive_batching=not args.no_adaptive
    )

    # Create processor
    processor = DropboxOptimizedProcessor(Path(args.path), config)

    # Process files
    try:
        results = list(processor.process_dropbox_optimized(max_files=args.max_files))

        # Summary
        total = len(results)
        cached = sum(1 for r in results if r.get("cached"))
        processed = sum(1 for r in results if r.get("processed"))
        errors = sum(1 for r in results if r.get("error"))

        print()
        print("=" * 60)
        print("Processing Summary")
        print("=" * 60)
        print(f"Total files: {total}")
        print(f"Cached (skipped re-processing): {cached} ({cached/total*100:.1f}%)")
        print(f"Processed: {processed} ({processed/total*100:.1f}%)")
        print(f"Errors: {errors} ({errors/total*100:.1f}%)")
        print("=" * 60)

        if cached > 0:
            print(f"\n✅ Caching saved {cached} file re-processes!")
            print(f"   This is more energy-efficient and faster.")

        return 0 if errors == 0 else 1

    except KeyboardInterrupt:
        print("\n\n⚠️  Processing interrupted by user")
        return 1
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":



    sys.exit(main())