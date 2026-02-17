#!/usr/bin/env python3
"""
Duplicate Detector - Phase 1 Discovery Tool

Detects duplicate and similar scripts/documentation.
Part of LUMINA 2.0.0 Cleanup Implementation Plan.

Tags: #CLEANUP #DUPLICATE #ANALYSIS #PHASE1 @LUMINA
"""

import hashlib
import json
import sys
from collections import defaultdict
from datetime import datetime
from difflib import SequenceMatcher
from pathlib import Path
from typing import Any, Dict, List

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging

    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DuplicateDetector")


class DuplicateDetector:
    """Detects duplicate and similar files"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.output_dir = project_root / "data" / "cleanup"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.file_hashes: Dict[str, str] = {}
        self.duplicate_groups: List[List[str]] = []
        self.similar_files: List[Dict[str, Any]] = []

    def calculate_hash(self, file_path: Path) -> str:
        """Calculate MD5 hash of file content"""
        try:
            with open(file_path, "rb") as f:
                return hashlib.md5(f.read()).hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {file_path}: {e}")
            return ""

    def calculate_similarity(self, file1: Path, file2: Path) -> float:
        """Calculate similarity ratio between two files"""
        try:
            with open(file1, encoding="utf-8", errors="ignore") as f1:
                content1 = f1.read()
            with open(file2, encoding="utf-8", errors="ignore") as f2:
                content2 = f2.read()

            return SequenceMatcher(None, content1, content2).ratio()
        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def detect_duplicate_scripts(self):
        """Detect duplicate Python scripts"""
        logger.info("Detecting duplicate scripts...")

        scripts_dir = self.project_root / "scripts" / "python"
        script_files = list(scripts_dir.rglob("*.py"))

        # Skip certain directories
        script_files = [
            f
            for f in script_files
            if not any(
                skip in str(f) for skip in ["__pycache__", ".git", "venv", ".venv", "node_modules"]
            )
        ]

        logger.info(f"Analyzing {len(script_files)} scripts...")

        # Calculate hashes
        hash_to_files: Dict[str, List[str]] = defaultdict(list)

        for script_path in script_files:
            file_hash = self.calculate_hash(script_path)
            if file_hash:
                rel_path = str(script_path.relative_to(self.project_root))
                hash_to_files[file_hash].append(rel_path)
                self.file_hashes[rel_path] = file_hash

        # Find duplicates (same hash)
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                self.duplicate_groups.append(files)

        logger.info(f"Found {len(self.duplicate_groups)} duplicate groups")

    def detect_similar_scripts(self, similarity_threshold: float = 0.85):
        """Detect similar scripts (high similarity ratio)"""
        logger.info(f"Detecting similar scripts (threshold: {similarity_threshold})...")

        scripts_dir = self.project_root / "scripts" / "python"
        script_files = list(scripts_dir.rglob("*.py"))

        # Skip certain directories
        script_files = [
            f
            for f in script_files
            if not any(
                skip in str(f) for skip in ["__pycache__", ".git", "venv", ".venv", "node_modules"]
            )
        ]

        logger.info(f"Comparing {len(script_files)} scripts...")

        # Compare all pairs (this is O(n²) but necessary for accuracy)
        compared = set()
        for i, file1 in enumerate(script_files):
            if i % 50 == 0:
                logger.info(f"Comparing script {i}/{len(script_files)}...")

            for file2 in script_files:
                if file1 == file2:
                    continue

                pair = tuple(sorted([str(file1), str(file2)]))
                if pair in compared:
                    continue
                compared.add(pair)

                similarity = self.calculate_similarity(file1, file2)
                if similarity >= similarity_threshold:
                    self.similar_files.append(
                        {
                            "file1": str(file1.relative_to(self.project_root)),
                            "file2": str(file2.relative_to(self.project_root)),
                            "similarity": similarity,
                        }
                    )

        logger.info(f"Found {len(self.similar_files)} similar file pairs")

    def detect_duplicate_documentation(self):
        """Detect duplicate documentation files"""
        logger.info("Detecting duplicate documentation...")

        docs_dir = self.project_root / "docs"
        doc_files = list(docs_dir.rglob("*.md"))

        logger.info(f"Analyzing {len(doc_files)} documentation files...")

        # Calculate hashes
        hash_to_files: Dict[str, List[str]] = defaultdict(list)

        for doc_path in doc_files:
            file_hash = self.calculate_hash(doc_path)
            if file_hash:
                rel_path = str(doc_path.relative_to(self.project_root))
                hash_to_files[file_hash].append(rel_path)

        # Find duplicates
        doc_duplicates = []
        for file_hash, files in hash_to_files.items():
            if len(files) > 1:
                doc_duplicates.append(files)

        logger.info(f"Found {len(doc_duplicates)} duplicate documentation groups")
        return doc_duplicates

    def generate_reports(self):
        """Generate duplicate detection reports"""
        logger.info("Generating reports...")

        # Duplicate scripts
        duplicates_file = self.output_dir / "duplicate_analysis.json"
        with open(duplicates_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "duplicate_groups": self.duplicate_groups,
                    "total_duplicate_groups": len(self.duplicate_groups),
                    "total_duplicate_files": sum(len(group) for group in self.duplicate_groups),
                    "similar_files": self.similar_files,
                    "total_similar_pairs": len(self.similar_files),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(f"✅ Duplicate analysis saved: {duplicates_file}")

        # Documentation duplicates
        doc_duplicates = self.detect_duplicate_documentation()
        doc_duplicates_file = self.output_dir / "doc_duplicates.json"
        with open(doc_duplicates_file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "timestamp": datetime.now().isoformat(),
                    "duplicate_groups": doc_duplicates,
                    "total_duplicate_groups": len(doc_duplicates),
                    "total_duplicate_files": sum(len(group) for group in doc_duplicates),
                },
                f,
                indent=2,
                ensure_ascii=False,
            )
        logger.info(f"✅ Documentation duplicates saved: {doc_duplicates_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("DUPLICATE DETECTION SUMMARY")
        print("=" * 80)
        print(f"Duplicate Script Groups: {len(self.duplicate_groups)}")
        print(f"Total Duplicate Script Files: {sum(len(group) for group in self.duplicate_groups)}")
        print(f"Similar Script Pairs: {len(self.similar_files)}")
        print(f"Duplicate Documentation Groups: {len(doc_duplicates)}")
        print(f"Total Duplicate Documentation Files: {sum(len(group) for group in doc_duplicates)}")
        print("\nTop Duplicate Groups:")
        for i, group in enumerate(sorted(self.duplicate_groups, key=len, reverse=True)[:10], 1):
            print(f"  {i}. {len(group)} files: {group[0]}")
        print("=" * 80)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Duplicate Detector - Phase 1 Discovery")
    parser.add_argument(
        "--similarity-threshold",
        type=float,
        default=0.85,
        help="Similarity threshold (default: 0.85)",
    )
    parser.add_argument(
        "--skip-similarity", action="store_true", help="Skip similarity detection (faster)"
    )

    args = parser.parse_args()

    detector = DuplicateDetector(project_root)

    detector.detect_duplicate_scripts()

    if not args.skip_similarity:
        detector.detect_similar_scripts(args.similarity_threshold)

    detector.generate_reports()


if __name__ == "__main__":
    main()
