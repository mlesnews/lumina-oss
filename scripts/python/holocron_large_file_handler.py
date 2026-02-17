#!/usr/bin/env python3
"""
Holocron Large File Handler
Handles files that are "TOO LARGE" for standard reading/processing by chunking and indexing them.

Tags: #HOLOCRON #LARGE_FILES #CHUNKING #INDEXING @AUTO @JARVIS
"""

import sys
import json
import os
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("HolocronLargeFileHandler")


class HolocronLargeFileHandler:
    """
    Handles large files in the Holocron system by chunking and indexing.
    """

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.logger = logger
        self.intelligence_dir = self.project_root / "data" / "intelligence"
        self.holocron_dir = self.project_root / "data" / "holocron"
        self.chunks_dir = self.holocron_dir / "chunks"
        self.chunks_dir.mkdir(parents=True, exist_ok=True)

        # Thresholds
        self.max_file_size_mb = 1.0  # Threshold for chunking (1MB)
        self.chunk_size_limit = 500 * 1024  # Target chunk size (500KB)

        self.logger.info("✅ Holocron Large File Handler initialized")

    def process_large_files(self):
        try:
            """Scan and process large files in the intelligence directory"""
            self.logger.info("="*80)
            self.logger.info("SCANNING FOR LARGE FILES IN @HOLOCRON")
            self.logger.info("="*80)

            # Files to target specifically
            targets = [
                "LUMINA_ALL_ASKS_ORDERED.json",
                "LUMINA_ASKS_SUMMARY.md",
                "LUMINA_SEQUENTIAL_STORYTELLING.md"
            ]

            results = []
            for target in targets:
                target_path = self.intelligence_dir / target
                if target_path.exists():
                    size_mb = target_path.stat().st_size / (1024 * 1024)
                    if size_mb > self.max_file_size_mb:
                        self.logger.info(f"📂 Found large file: {target} ({size_mb:.2f} MB)")
                        if target.endswith(".json"):
                            result = self.chunk_json_file(target_path)
                        else:
                            result = self.chunk_text_file(target_path)
                        results.append(result)
                    else:
                        self.logger.debug(f"ℹ️  File {target} is within size limits ({size_mb:.2f} MB)")

            return results

        except Exception as e:
            self.logger.error(f"Error in process_large_files: {e}", exc_info=True)
            raise
    def chunk_json_file(self, file_path: Path) -> Dict[str, Any]:
        """Chunk a large JSON file into smaller pieces"""
        self.logger.info(f"🧩 Chunking JSON: {file_path.name}...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Determine list to chunk (assume it's in a key like 'asks' or 'messages' or is the root)
            list_to_chunk = None
            key_name = None

            if isinstance(data, list):
                list_to_chunk = data
            elif isinstance(data, dict):
                # Try common keys
                for key in ['asks', 'messages', 'entries', 'logs']:
                    if key in data and isinstance(data[key], list):
                        list_to_chunk = data[key]
                        key_name = key
                        break

                if not list_to_chunk:
                    # Just take the first list found
                    for key, value in data.items():
                        if isinstance(value, list):
                            list_to_chunk = value
                            key_name = key
                            break

            if not list_to_chunk:
                self.logger.warning(f"⚠️  No list found to chunk in {file_path.name}")
                return {"success": False, "error": "No list found to chunk"}

            # Calculate chunks
            total_items = len(list_to_chunk)
            # Estimate item size
            total_size = file_path.stat().st_size
            avg_item_size = total_size / total_items
            items_per_chunk = max(1, int(self.chunk_size_limit / avg_item_size))
            num_chunks = math.ceil(total_items / items_per_chunk)

            self.logger.info(f"   Items: {total_items} | Chunks: {num_chunks} | Items/Chunk: {items_per_chunk}")

            chunk_files = []
            for i in range(num_chunks):
                start_idx = i * items_per_chunk
                end_idx = min((i + 1) * items_per_chunk, total_items)
                chunk_data = list_to_chunk[start_idx:end_idx]

                chunk_name = f"{file_path.stem}_part_{i+1:03d}.json"
                chunk_path = self.chunks_dir / chunk_name

                # Keep metadata in chunks if available
                save_data = chunk_data
                if key_name:
                    save_data = {
                        "metadata": {
                            "source_file": file_path.name,
                            "chunk_index": i + 1,
                            "total_chunks": num_chunks,
                            "items_range": [start_idx, end_idx],
                            "generated_at": datetime.now().isoformat()
                        },
                        key_name: chunk_data
                    }

                with open(chunk_path, 'w', encoding='utf-8') as f:
                    json.dump(save_data, f, indent=2, ensure_ascii=False)

                chunk_files.append({
                    "name": chunk_name,
                    "path": str(chunk_path.relative_to(self.project_root)),
                    "range": [start_idx, end_idx]
                })

            # Create Index
            index_name = f"{file_path.stem}_INDEX.json"
            index_path = self.intelligence_dir / index_name

            index_data = {
                "metadata": {
                    "source_file": file_path.name,
                    "total_items": total_items,
                    "total_chunks": num_chunks,
                    "last_processed": datetime.now().isoformat()
                },
                "chunks": chunk_files
            }

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Created index: {index_name} with {num_chunks} chunks")

            return {
                "success": True,
                "file": file_path.name,
                "index": index_name,
                "chunks": num_chunks
            }

        except Exception as e:
            self.logger.error(f"❌ Error chunking JSON {file_path.name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}

    def chunk_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Chunk a large text/markdown file into smaller pieces"""
        self.logger.info(f"🧩 Chunking Text: {file_path.name}...")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            total_lines = len(lines)
            total_size = file_path.stat().st_size
            avg_line_size = total_size / total_lines
            lines_per_chunk = max(1, int(self.chunk_size_limit / avg_line_size))
            num_chunks = math.ceil(total_lines / lines_per_chunk)

            self.logger.info(f"   Lines: {total_lines} | Chunks: {num_chunks} | Lines/Chunk: {lines_per_chunk}")

            chunk_files = []
            for i in range(num_chunks):
                start_idx = i * lines_per_chunk
                end_idx = min((i + 1) * lines_per_chunk, total_lines)
                chunk_content = lines[start_idx:end_idx]

                chunk_name = f"{file_path.stem}_part_{i+1:03d}{file_path.suffix}"
                chunk_path = self.chunks_dir / chunk_name

                with open(chunk_path, 'w', encoding='utf-8') as f:
                    f.writelines(chunk_content)

                chunk_files.append({
                    "name": chunk_name,
                    "path": str(chunk_path.relative_to(self.project_root)),
                    "range": [start_idx, end_idx]
                })

            # Create Index
            index_name = f"{file_path.stem}_INDEX.json"
            index_path = self.intelligence_dir / index_name

            index_data = {
                "metadata": {
                    "source_file": file_path.name,
                    "total_lines": total_lines,
                    "total_chunks": num_chunks,
                    "last_processed": datetime.now().isoformat()
                },
                "chunks": chunk_files
            }

            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index_data, f, indent=2, ensure_ascii=False)

            self.logger.info(f"✅ Created index: {index_name} with {num_chunks} chunks")

            return {
                "success": True,
                "file": file_path.name,
                "index": index_name,
                "chunks": num_chunks
            }

        except Exception as e:
            self.logger.error(f"❌ Error chunking text {file_path.name}: {e}", exc_info=True)
            return {"success": False, "error": str(e)}


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Holocron Large File Handler")
        parser.add_argument("--process", action="store_true", help="Scan and process large files")
        parser.add_argument("--file", type=str, help="Process a specific file")

        args = parser.parse_args()

        handler = HolocronLargeFileHandler()

        if args.process:
            results = handler.process_large_files()
            print(json.dumps(results, indent=2))
        elif args.file:
            file_path = Path(args.file)
            if file_path.exists():
                if file_path.suffix == ".json":
                    result = handler.chunk_json_file(file_path)
                else:
                    result = handler.chunk_text_file(file_path)
                print(json.dumps(result, indent=2))
            else:
                print(f"File not found: {args.file}")
        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()