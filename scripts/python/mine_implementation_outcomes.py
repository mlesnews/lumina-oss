#!/usr/bin/env python3
"""
Mine Implementation Outcomes from Code Markers

Scans codebase for implementation markers and extracts outcomes to feed
into the Lumina Data Mining Feedback Loop.

@LUMINA @DATA_MINING @IMPLEMENTATION_MARKERS
"""

import sys
import re
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

from lumina_data_mining_feedback_loop import LuminaDataMiner, Outcome

logger = get_logger("MineImplementationOutcomes")


# Implementation marker patterns
IMPLEMENTATION_PATTERNS = [
    # Completed/Implemented markers
    (re.compile(r'#\s*IMPLEMENTED:\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'implementation'),
    (re.compile(r'#\s*COMPLETED:\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'completion'),
    (re.compile(r'#\s*DONE:\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'completion'),
    (re.compile(r'#\s*FIXED:\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'fix'),
    (re.compile(r'#\s*RESOLVED:\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'fix'),

    # TODO completion markers  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
    (re.compile(r'#\s*TODO.*?DONE|COMPLETE|FIXED', re.IGNORECASE | re.MULTILINE), 'completion'),

    # Function/class completion markers
    (re.compile(r'def\s+\w+.*?:\s*#\s*(?:IMPLEMENTED|COMPLETED|FIXED):\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'implementation'),

    # Docstring markers
    (re.compile(r'""".*?(?:IMPLEMENTED|COMPLETED|FIXED):\s*(.+?)(?=\n|""")', re.IGNORECASE | re.MULTILINE | re.DOTALL), 'implementation'),

    # File-level markers
    (re.compile(r'^#\s*FILE:\s*(?:IMPLEMENTED|COMPLETED):\s*(.+?)(?=\n|$)', re.IGNORECASE | re.MULTILINE), 'completion'),
]

# Outcome metadata patterns
METADATA_PATTERNS = [
    (re.compile(r'#\s*OUTCOME:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'outcome'),
    (re.compile(r'#\s*RESULT:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'result'),
    (re.compile(r'#\s*STATUS:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'status'),
    (re.compile(r'#\s*METRICS:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'metrics'),
]

# Intent linking patterns
INTENT_LINKING_PATTERNS = [
    (re.compile(r'#\s*@ASK:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'ask_id'),
    (re.compile(r'#\s*INTENT:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'intent_id'),
    (re.compile(r'#\s*TASK:\s*(.+?)(?=\n|$)', re.IGNORECASE), 'task_id'),
]


def extract_metrics_from_text(text: str) -> Dict[str, float]:
    """Extract numeric metrics from text"""
    metrics = {}

    # Common metric patterns
    metric_patterns = {
        'duration': r'(?:duration|time|execution_time)[:\s]+([\d.]+)\s*(?:s|sec|seconds|ms)?',
        'latency': r'(?:latency|delay)[:\s]+([\d.]+)\s*(?:ms|milliseconds)?',
        'performance': r'(?:performance|speed)[:\s]+([\d.]+)',
        'accuracy': r'(?:accuracy|precision)[:\s]+([\d.]+)',
        'efficiency': r'(?:efficiency)[:\s]+([\d.]+)',
        'throughput': r'(?:throughput|rate)[:\s]+([\d.]+)',
    }

    for metric_name, pattern in metric_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            try:
                metrics[metric_name] = float(matches[0])
            except ValueError:
                pass

    return metrics


def mine_file(file_path: Path, data_miner: LuminaDataMiner) -> List[Outcome]:
    """Mine implementation outcomes from a single file"""
    outcomes = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        file_stat = file_path.stat()
        relative_path = file_path.relative_to(data_miner.project_root)

        # Extract implementation markers
        for pattern, outcome_type in IMPLEMENTATION_PATTERNS:
            matches = pattern.finditer(content)
            for match in matches:
                outcome_text = match.group(1).strip() if match.lastindex else match.group(0).strip()

                # Skip if too short or just whitespace
                if len(outcome_text) < 3:
                    continue

                # Extract metadata
                metadata = {}
                intent_id = None

                # Find intent linking
                line_start = content.rfind('\n', 0, match.start()) + 1
                line_end = content.find('\n', match.end())
                if line_end == -1:
                    line_end = len(content)
                line_context = content[line_start:line_end]

                for meta_pattern, meta_key in INTENT_LINKING_PATTERNS:
                    meta_match = meta_pattern.search(line_context)
                    if meta_match:
                        if meta_key in ['ask_id', 'intent_id', 'task_id']:
                            intent_id = meta_match.group(1).strip()
                        else:
                            metadata[meta_key] = meta_match.group(1).strip()

                # Extract metrics from outcome text
                metrics = extract_metrics_from_text(outcome_text)

                # Add file metrics
                metrics['file_size'] = file_stat.st_size
                metrics['lines'] = content.count('\n')

                # Determine success based on outcome type
                success = outcome_type in ['implementation', 'completion', 'fix']

                outcome = Outcome(
                    outcome_id=f"code_{relative_path}_{len(outcomes)}_{datetime.now().timestamp()}",
                    intent_id=intent_id or 'unknown',
                    outcome_type=outcome_type,
                    outcome_text=outcome_text,
                    metrics=metrics,
                    timestamp=datetime.fromtimestamp(file_stat.st_mtime),
                    implementation_details={
                        'file': str(relative_path),
                        'line': content[:match.start()].count('\n') + 1,
                        'pattern': pattern.pattern,
                        'metadata': metadata,
                        'file_size': file_stat.st_size,
                        'last_modified': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    }
                )
                outcomes.append(outcome)

    except Exception as e:
        logger.debug(f"Error mining {file_path}: {e}")

    return outcomes


def mine_codebase(project_root: Optional[Path] = None, 
                  file_patterns: Optional[List[str]] = None,
                  exclude_dirs: Optional[List[str]] = None) -> List[Outcome]:
    """
    Mine implementation outcomes from entire codebase

    Args:
        project_root: Project root directory
        file_patterns: File patterns to search (default: ['*.py', '*.js', '*.ts'])
        exclude_dirs: Directories to exclude (default: ['node_modules', '.git', '__pycache__', 'venv', '.venv'])

    Returns:
        List of Outcome objects
    """
    if project_root is None:
        project_root = Path(__file__).parent.parent.parent

    project_root = Path(project_root)

    if file_patterns is None:
        file_patterns = ['*.py', '*.js', '*.ts', '*.java', '*.cpp', '*.c', '*.go', '*.rs']

    if exclude_dirs is None:
        exclude_dirs = ['node_modules', '.git', '__pycache__', 'venv', '.venv', 
                       'dist', 'build', '.pytest_cache', '.mypy_cache', 'target']

    logger.info(f"🔍 Mining implementation outcomes from {project_root}")

    # Initialize data miner
    data_miner = LuminaDataMiner(project_root)

    all_outcomes = []

    # Find all matching files
    files_to_process = []
    for pattern in file_patterns:
        files_to_process.extend(project_root.rglob(pattern))

    # Filter out excluded directories
    files_to_process = [
        f for f in files_to_process
        if not any(excluded in f.parts for excluded in exclude_dirs)
    ]

    logger.info(f"📄 Processing {len(files_to_process)} files...")

    # Mine each file
    for file_path in files_to_process:
        try:
            outcomes = mine_file(file_path, data_miner)
            all_outcomes.extend(outcomes)
            if outcomes:
                logger.debug(f"  Found {len(outcomes)} outcomes in {file_path.relative_to(project_root)}")
        except Exception as e:
            logger.debug(f"Error processing {file_path}: {e}")

    logger.info(f"✅ Mined {len(all_outcomes)} implementation outcomes")

    # Add to data miner
    data_miner.outcomes.extend(all_outcomes)
    data_miner._save_mined_data()

    # Create OTS entries
    logger.info("Creating OTS entries...")
    ots_entries = data_miner.create_outcomes_of_intent()
    logger.info(f"✅ Created {len(ots_entries)} OTS entries")

    return all_outcomes


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Mine implementation outcomes from code markers")
        parser.add_argument("--project-root", type=Path, help="Project root directory")
        parser.add_argument("--file-patterns", nargs='+', help="File patterns to search", 
                           default=['*.py', '*.js', '*.ts'])
        parser.add_argument("--exclude-dirs", nargs='+', help="Directories to exclude",
                           default=['node_modules', '.git', '__pycache__', 'venv', '.venv'])
        parser.add_argument("--output", type=Path, help="Output JSON file for outcomes")

        args = parser.parse_args()

        outcomes = mine_codebase(
            project_root=args.project_root,
            file_patterns=args.file_patterns,
            exclude_dirs=args.exclude_dirs
        )

        if args.output:
            with open(args.output, 'w') as f:
                json.dump([o.to_dict() for o in outcomes], f, indent=2, default=str)
            print(f"✅ Outcomes saved to: {args.output}")
        else:
            print(f"✅ Mined {len(outcomes)} implementation outcomes")
            print(f"   Outcomes saved to data miner")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()