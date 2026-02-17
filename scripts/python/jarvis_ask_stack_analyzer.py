#!/usr/bin/env python3
"""
JARVIS @ASK Stack Analyzer - Inception to Present

Delve into @ASK stack from inception to present.
Find incomplete, unvalidated @asks.
Use @REARVIEW_MIRROR as rudder/helm for course correction.
Remain vigilant as @JEDI @PATHFINDER.

Tags: #ASK_STACK #REARVIEW_MIRROR #JEDI #PATHFINDER #COURSE_CORRECTION @JARVIS @LUMINA
"""

import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISAskStackAnalyzer")


class AskStackAnalyzer:
    """Analyze @ASK stack from inception to present"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_stack_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.asks = []
        self.incomplete_asks = []
        self.unvalidated_asks = []
        self.ask_timeline = []

    def extract_asks_from_codebase(self) -> Dict[str, Any]:
        """Extract all @ASK mentions from codebase"""
        logger.info("=" * 80)
        logger.info("🔍 @ASK STACK ANALYSIS - INCEPTION TO PRESENT")
        logger.info("=" * 80)
        logger.info("")
        logger.info("Extracting @ASK mentions from codebase...")

        asks_found = []

        # Search Python files
        scripts_dir = project_root / "scripts" / "python"
        if scripts_dir.exists():
            for script_file in scripts_dir.rglob("*.py"):
                try:
                    content = script_file.read_text(encoding='utf-8', errors='ignore')
                    # Find @ASK mentions
                    ask_matches = re.finditer(r'@ASK|@ask|#ASK|#ask', content, re.IGNORECASE)
                    for match in ask_matches:
                        # Get context around the match
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]

                        ask = {
                            "file": str(script_file.relative_to(project_root)),
                            "line": content[:match.start()].count('\n') + 1,
                            "match": match.group(),
                            "context": context.strip(),
                            "timestamp": datetime.fromtimestamp(script_file.stat().st_mtime).isoformat()
                        }
                        asks_found.append(ask)
                except:
                    pass

        # Search documentation
        docs_dir = project_root / "docs"
        if docs_dir.exists():
            for doc_file in docs_dir.rglob("*.md"):
                try:
                    content = doc_file.read_text(encoding='utf-8', errors='ignore')
                    ask_matches = re.finditer(r'@ASK|@ask|#ASK|#ask', content, re.IGNORECASE)
                    for match in ask_matches:
                        start = max(0, match.start() - 100)
                        end = min(len(content), match.end() + 100)
                        context = content[start:end]

                        ask = {
                            "file": str(doc_file.relative_to(project_root)),
                            "line": content[:match.start()].count('\n') + 1,
                            "match": match.group(),
                            "context": context.strip(),
                            "timestamp": datetime.fromtimestamp(doc_file.stat().st_mtime).isoformat()
                        }
                        asks_found.append(ask)
                except:
                    pass

        logger.info(f"✅ Found {len(asks_found)} @ASK mentions")
        logger.info("")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_asks": len(asks_found),
            "asks": asks_found
        }

    def analyze_ask_completion_status(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze completion status of asks"""
        logger.info("Analyzing @ASK completion status...")

        incomplete = []
        unvalidated = []
        completed = []

        for ask in asks:
            context = ask.get("context", "").lower()
            file_path = ask.get("file", "")

            # Check for completion indicators
            completion_indicators = [
                "complete", "completed", "done", "finished", "resolved",
                "implemented", "created", "built", "established"
            ]

            # Check for incomplete indicators
            incomplete_indicators = [
                "todo", "pending", "incomplete", "not done", "missing",
                "needs", "required", "should", "must", "will"
            ]

            # Check for validation indicators
            validation_indicators = [
                "validated", "verified", "tested", "confirmed", "proven",
                "poc", "proof", "test", "check"
            ]

            is_complete = any(indicator in context for indicator in completion_indicators)
            is_incomplete = any(indicator in context for indicator in incomplete_indicators)
            is_validated = any(indicator in context for indicator in validation_indicators)

            ask_status = {
                "ask": ask,
                "status": "UNKNOWN",
                "completion": is_complete,
                "validation": is_validated
            }

            if is_complete and is_validated:
                ask_status["status"] = "COMPLETED_VALIDATED"
                completed.append(ask_status)
            elif is_complete and not is_validated:
                ask_status["status"] = "COMPLETED_UNVALIDATED"
                unvalidated.append(ask_status)
            elif is_incomplete:
                ask_status["status"] = "INCOMPLETE"
                incomplete.append(ask_status)
            else:
                ask_status["status"] = "UNKNOWN"
                incomplete.append(ask_status)  # Assume incomplete if unclear

        logger.info(f"   ✅ Completed & Validated: {len(completed)}")
        logger.info(f"   ⚠️  Completed & Unvalidated: {len(unvalidated)}")
        logger.info(f"   ❌ Incomplete: {len(incomplete)}")
        logger.info("")

        return {
            "timestamp": datetime.now().isoformat(),
            "total_asks": len(asks),
            "completed_validated": len(completed),
            "completed_unvalidated": len(unvalidated),
            "incomplete": len(incomplete),
            "incomplete_asks": incomplete,
            "unvalidated_asks": unvalidated,
            "completed_asks": completed
        }

    def build_ask_timeline(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Build timeline of asks from inception to present"""
        logger.info("Building @ASK timeline from inception to present...")

        # Sort by timestamp
        sorted_asks = sorted(asks, key=lambda x: x.get("timestamp", ""))

        timeline = {
            "inception": sorted_asks[0].get("timestamp", "") if sorted_asks else "",
            "present": datetime.now().isoformat(),
            "total_period": len(sorted_asks),
            "timeline": []
        }

        # Group by time periods
        for ask in sorted_asks:
            timeline["timeline"].append({
                "timestamp": ask.get("timestamp", ""),
                "file": ask.get("file", ""),
                "ask": ask.get("match", ""),
                "context": ask.get("context", "")[:200]  # Truncate for readability
            })

        logger.info(f"✅ Timeline built: {len(timeline['timeline'])} asks from inception to present")
        logger.info("")

        return timeline


class RearViewMirrorIntegration:
    """Integrate with @REARVIEW_MIRROR for course correction"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.rear_view_data = {}

    def load_rear_view_data(self) -> Dict[str, Any]:
        """Load rear view mirror data"""
        rear_view_dir = project_root / "data" / "rear_view_mirror"
        if rear_view_dir.exists():
            # Load recent resolution data
            resolution_files = list(rear_view_dir.glob("resolution_*.json"))
            if resolution_files:
                latest = max(resolution_files, key=lambda p: p.stat().st_mtime)
                try:
                    with open(latest, 'r', encoding='utf-8') as f:
                        self.rear_view_data = json.load(f)
                except:
                    self.rear_view_data = {}

        return self.rear_view_data

    def correlate_with_asks(self, asks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Correlate rear view mirror data with asks"""
        correlation = {
            "timestamp": datetime.now().isoformat(),
            "rear_view_insights": self.rear_view_data,
            "ask_correlation": [],
            "course_corrections": []
        }

        # Correlate incomplete asks with rear view data
        for ask in asks:
            correlation["ask_correlation"].append({
                "ask": ask.get("file", ""),
                "rear_view_status": "Unknown",
                "needs_attention": True
            })

        return correlation


class JediPathfinderVigilance:
    """@JEDI @PATHFINDER - Remain vigilant"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.vigilance_checks = []

    def maintain_vigilance(self, ask_analysis: Dict[str, Any], 
                         rear_view_data: Dict[str, Any]) -> Dict[str, Any]:
        """Maintain vigilance as @JEDI @PATHFINDER"""
        logger.info("=" * 80)
        logger.info("⚔️ @JEDI @PATHFINDER - MAINTAINING VIGILANCE")
        logger.info("=" * 80)
        logger.info("")

        vigilance = {
            "timestamp": datetime.now().isoformat(),
            "role": "@JEDI @PATHFINDER",
            "vigilance_level": "HIGH",
            "checks": [],
            "course_corrections": [],
            "recommendations": []
        }

        # Vigilance checks
        incomplete_count = ask_analysis.get("incomplete", 0)
        unvalidated_count = ask_analysis.get("completed_unvalidated", 0)

        if incomplete_count > 0:
            vigilance["checks"].append({
                "check": "Incomplete @asks detected",
                "count": incomplete_count,
                "severity": "HIGH",
                "action": "Review and complete incomplete asks"
            })
            logger.info(f"⚠️  Incomplete @asks: {incomplete_count}")

        if unvalidated_count > 0:
            vigilance["checks"].append({
                "check": "Unvalidated @asks detected",
                "count": unvalidated_count,
                "severity": "MEDIUM",
                "action": "Validate completed asks"
            })
            logger.info(f"⚠️  Unvalidated @asks: {unvalidated_count}")

        # Course corrections
        if incomplete_count > 0 or unvalidated_count > 0:
            vigilance["course_corrections"].append({
                "correction": "Review incomplete and unvalidated asks",
                "priority": "HIGH",
                "method": "Use @REARVIEW_MIRROR to identify patterns and course correct"
            })
            logger.info("📊 Course correction needed")

        # Recommendations
        vigilance["recommendations"] = [
            "Always look to the past - @REARVIEW_MIRROR guides the rudder",
            "Maintain course - course correct as needed",
            "Remain vigilant - @JEDI @PATHFINDER role",
            "Validate all completed asks",
            "Complete all incomplete asks"
        ]

        logger.info("")
        logger.info("✅ Vigilance maintained")
        logger.info("")

        return vigilance


class AskStackDelver:
    """Delve into @ASK stack from inception to present"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "ask_stack_delver"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analyzer = AskStackAnalyzer(project_root)
        self.rear_view = RearViewMirrorIntegration(project_root)
        self.jedi = JediPathfinderVigilance(project_root)

    def delve_ask_stack(self) -> Dict[str, Any]:
        try:
            """Complete delve into @ASK stack"""
            logger.info("=" * 80)
            logger.info("🔍 DELVING @ASK STACK - INCEPTION TO PRESENT")
            logger.info("=" * 80)
            logger.info("")

            # Extract asks
            asks_data = self.analyzer.extract_asks_from_codebase()
            asks = asks_data.get("asks", [])

            # Analyze completion status
            completion_analysis = self.analyzer.analyze_ask_completion_status(asks)

            # Build timeline
            timeline = self.analyzer.build_ask_timeline(asks)

            # Load rear view mirror
            rear_view_data = self.rear_view.load_rear_view_data()
            correlation = self.rear_view.correlate_with_asks(asks)

            # Maintain vigilance
            vigilance = self.jedi.maintain_vigilance(completion_analysis, rear_view_data)

            # Complete analysis
            analysis = {
                "timestamp": datetime.now().isoformat(),
                "analysis_type": "ASK_STACK_DELVE",
                "scope": "INCEPTION_TO_PRESENT",
                "asks_extracted": asks_data,
                "completion_analysis": completion_analysis,
                "timeline": timeline,
                "rear_view_correlation": correlation,
                "jedi_vigilance": vigilance,
                "course_correction": {
                    "needed": completion_analysis.get("incomplete", 0) > 0 or completion_analysis.get("completed_unvalidated", 0) > 0,
                    "incomplete_count": completion_analysis.get("incomplete", 0),
                    "unvalidated_count": completion_analysis.get("completed_unvalidated", 0),
                    "recommendations": vigilance.get("recommendations", [])
                }
            }

            logger.info("=" * 80)
            logger.info("✅ @ASK STACK DELVE COMPLETE")
            logger.info("=" * 80)
            logger.info("")
            logger.info("📊 Summary:")
            logger.info(f"   Total @asks found: {len(asks)}")
            logger.info(f"   Incomplete: {completion_analysis.get('incomplete', 0)}")
            logger.info(f"   Unvalidated: {completion_analysis.get('completed_unvalidated', 0)}")
            logger.info(f"   Completed & Validated: {completion_analysis.get('completed_validated', 0)}")
            logger.info("")

            # Save analysis
            analysis_file = self.data_dir / f"ask_stack_delve_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, indent=2, default=str)

            logger.info(f"📄 Analysis saved: {analysis_file}")
            logger.info("")

            return analysis


        except Exception as e:
            self.logger.error(f"Error in delve_ask_stack: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS @ASK Stack Delver")
        parser.add_argument("--delve", action="store_true", help="Complete delve into @ASK stack")
        parser.add_argument("--extract", action="store_true", help="Extract asks only")
        parser.add_argument("--analyze", action="store_true", help="Analyze completion status only")
        parser.add_argument("--vigilance", action="store_true", help="Maintain Jedi Pathfinder vigilance")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        delver = AskStackDelver(project_root)

        if args.delve or (not args.extract and not args.analyze and not args.vigilance):
            analysis = delver.delve_ask_stack()
            print(json.dumps(analysis, indent=2, default=str))
        elif args.extract:
            asks_data = delver.analyzer.extract_asks_from_codebase()
            print(json.dumps(asks_data, indent=2, default=str))
        elif args.analyze:
            asks_data = delver.analyzer.extract_asks_from_codebase()
            analysis = delver.analyzer.analyze_ask_completion_status(asks_data.get("asks", []))
            print(json.dumps(analysis, indent=2, default=str))
        elif args.vigilance:
            asks_data = delver.analyzer.extract_asks_from_codebase()
            completion_analysis = delver.analyzer.analyze_ask_completion_status(asks_data.get("asks", []))
            rear_view_data = delver.rear_view.load_rear_view_data()
            vigilance = delver.jedi.maintain_vigilance(completion_analysis, rear_view_data)
            print(json.dumps(vigilance, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()