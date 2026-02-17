#!/usr/bin/env python3
"""
Mine Implementation Markers from Code

Scans codebase for implementation markers (# IMPLEMENTED, # COMPLETED, # FIXED, etc.)
and extracts outcomes for integration with Lumina Data Mining Feedback Loop.

@MINING @OUTCOMES @IMPLEMENTATION_MARKERS
"""

import sys
import re
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

logger = get_logger("MineImplementationMarkers")


class ImplementationMarkerMiner:
    """Mine implementation markers from code"""

    # Common implementation marker patterns
    MARKER_PATTERNS = [
        (re.compile(r'#\s*IMPLEMENTED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'implementation'),
        (re.compile(r'#\s*COMPLETED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'completion'),
        (re.compile(r'#\s*FIXED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'fix'),
        (re.compile(r'#\s*DONE[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'completion'),
        (re.compile(r'#\s*RESOLVED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'resolution'),
        (re.compile(r'#\s*TODO\s*:\s*DONE[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'completion'),
        (re.compile(r'@IMPLEMENTED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'implementation'),
        (re.compile(r'@COMPLETED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'completion'),
        (re.compile(r'@FIXED[:\s]+(.+?)(?=\n|$)', re.IGNORECASE), 'fix'),
    ]

    # Pattern to extract intent references
    INTENT_PATTERNS = [
        re.compile(r'@ASK\s+ID[:\s]+(\S+)', re.IGNORECASE),
        re.compile(r'intent[_\s]*id[:\s]+(\S+)', re.IGNORECASE),
        re.compile(r'ask[_\s]*id[:\s]+(\S+)', re.IGNORECASE),
    ]

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.logger = get_logger("ImplementationMarkerMiner")

        # Outcomes storage
        try:
            from lumina_data_mining_feedback_loop import LuminaDataMiner, Outcome
            self.data_miner = LuminaDataMiner(project_root)
            self.Outcome = Outcome
        except ImportError:
            self.data_miner = None
            self.Outcome = None
            self.logger.warning("LuminaDataMiner not available")

    def mine_all_markers(self) -> List[Dict[str, Any]]:
        """Mine all implementation markers from codebase"""
        self.logger.info("🔍 Mining implementation markers from codebase...")

        outcomes = []
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                file_outcomes = self.mine_file_markers(py_file)
                outcomes.extend(file_outcomes)
            except Exception as e:
                self.logger.debug(f"Error processing {py_file}: {e}")

        self.logger.info(f"✅ Mined {len(outcomes)} implementation markers")

        # Integrate with data miner
        if self.data_miner and self.Outcome:
            self._integrate_outcomes(outcomes)

        return outcomes

    def mine_file_markers(self, file_path: Path) -> List[Dict[str, Any]]:
        """Mine implementation markers from a single file"""
        outcomes = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')

            file_stat = file_path.stat()
            relative_path = file_path.relative_to(self.project_root)

            # Search for all marker patterns
            for pattern, outcome_type in self.MARKER_PATTERNS:
                matches = pattern.finditer(content)

                for match in matches:
                    marker_text = match.group(1).strip()
                    match_line = content[:match.start()].count('\n') + 1

                    # Extract intent_id if present
                    intent_id = self._extract_intent_id(content, match_line)

                    # Get surrounding context
                    context_lines = self._get_context_lines(lines, match_line - 1, context_size=5)

                    outcome = {
                        'outcome_id': f"code_{relative_path}_{match_line}_{datetime.now().timestamp()}",
                        'file_path': str(relative_path),
                        'line_number': match_line,
                        'outcome_type': outcome_type,
                        'outcome_text': marker_text,
                        'intent_id': intent_id,
                        'context': context_lines,
                        'metrics': {
                            'file_size': file_stat.st_size,
                            'total_lines': len(lines),
                            'last_modified': file_stat.st_mtime
                        },
                        'timestamp': datetime.fromtimestamp(file_stat.st_mtime).isoformat()
                    }

                    outcomes.append(outcome)

        except Exception as e:
            self.logger.debug(f"Error reading {file_path}: {e}")

        return outcomes

    def _extract_intent_id(self, content: str, line_number: int) -> Optional[str]:
        """Extract intent_id from context around the marker"""
        # Look in nearby lines for intent references
        lines = content.split('\n')
        start_line = max(0, line_number - 10)
        end_line = min(len(lines), line_number + 10)

        context = '\n'.join(lines[start_line:end_line])

        for pattern in self.INTENT_PATTERNS:
            match = pattern.search(context)
            if match:
                return match.group(1)

        return None

    def _get_context_lines(self, lines: List[str], line_index: int, context_size: int = 5) -> List[str]:
        """Get context lines around a marker"""
        start = max(0, line_index - context_size)
        end = min(len(lines), line_index + context_size + 1)
        return lines[start:end]

    def _integrate_outcomes(self, outcomes: List[Dict[str, Any]]) -> None:
        """Integrate mined outcomes with data miner"""
        if not self.data_miner or not self.Outcome:
            return

        integrated_count = 0

        for outcome_data in outcomes:
            try:
                outcome = self.Outcome(
                    outcome_id=outcome_data['outcome_id'],
                    intent_id=outcome_data.get('intent_id', 'unknown'),
                    outcome_type=outcome_data['outcome_type'],
                    outcome_text=outcome_data['outcome_text'],
                    metrics=outcome_data.get('metrics', {}),
                    timestamp=datetime.fromisoformat(outcome_data['timestamp']),
                    implementation_details={
                        'file_path': outcome_data['file_path'],
                        'line_number': outcome_data['line_number'],
                        'context': outcome_data.get('context', [])
                    }
                )

                # Add to data miner if not already present
                existing = [o for o in self.data_miner.outcomes if o.outcome_id == outcome.outcome_id]
                if not existing:
                    self.data_miner.outcomes.append(outcome)
                    integrated_count += 1
            except Exception as e:
                self.logger.warning(f"Error integrating outcome {outcome_data.get('outcome_id')}: {e}")

        if integrated_count > 0:
            self.data_miner._save_mined_data()
            self.logger.info(f"✅ Integrated {integrated_count} outcomes with data miner")

    def find_intent_references(self, intent_text: str) -> List[Dict[str, Any]]:
        """Find code locations that reference a specific intent"""
        references = []

        python_files = list(self.project_root.rglob("*.py"))

        intent_lower = intent_text.lower()
        intent_words = set(intent_lower.split())

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                relative_path = py_file.relative_to(self.project_root)

                # Search for intent text in code
                for i, line in enumerate(lines, 1):
                    line_lower = line.lower()
                    line_words = set(line_lower.split())

                    # Calculate similarity (simple word overlap)
                    if intent_words & line_words:  # Any word overlap
                        overlap = len(intent_words & line_words) / len(intent_words) if intent_words else 0
                        if overlap > 0.3:  # At least 30% word overlap
                            references.append({
                                'file': str(relative_path),
                                'line': i,
                                'content': line.strip(),
                                'similarity': overlap
                            })
            except Exception as e:
                self.logger.debug(f"Error reading {py_file}: {e}")

        # Sort by similarity
        references.sort(key=lambda x: x['similarity'], reverse=True)
        return references


def main():
    try:
        """Main entry point"""
        import argparse
        import json

        parser = argparse.ArgumentParser(description="Mine implementation markers from code")
        parser.add_argument("--file", type=Path, help="Mine markers from specific file")
        parser.add_argument("--intent", type=str, help="Find references to specific intent text")
        parser.add_argument("--output", type=Path, help="Output file path (JSON)")
        parser.add_argument("--integrate", action="store_true", help="Integrate with data miner")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        miner = ImplementationMarkerMiner(project_root)

        if args.file:
            outcomes = miner.mine_file_markers(args.file)
            print(f"Found {len(outcomes)} markers in {args.file}")
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(outcomes, f, indent=2, default=str)
            else:
                print(json.dumps(outcomes, indent=2, default=str))

        elif args.intent:
            references = miner.find_intent_references(args.intent)
            print(f"Found {len(references)} references to intent: {args.intent}")
            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(references, f, indent=2, default=str)
            else:
                print(json.dumps(references, indent=2, default=str))

        else:
            outcomes = miner.mine_all_markers()
            print(f"✅ Mined {len(outcomes)} implementation markers")

            if args.output:
                with open(args.output, 'w') as f:
                    json.dump(outcomes, f, indent=2, default=str)
                print(f"✅ Saved to {args.output}")
            elif args.integrate:
                print(f"✅ Integrated {len(outcomes)} outcomes with data miner")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()