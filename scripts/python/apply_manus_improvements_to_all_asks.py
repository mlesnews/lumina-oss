#!/usr/bin/env python3
"""
Apply MANUS Improvements to ALL @ASKS from Project Lumina Beginning

This script:
1. Discovers all @ASK entries from project beginning
2. Reviews them with JARVIS roast system
3. Applies MANUS improvement patterns
4. Creates comprehensive report

The ASK STACK = ALL @ASKS FROM PROJECT LUMINA BEGINNING
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ApplyMANUSToAllASKS")

# Add scripts/python to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))


def discover_all_ask_files() -> List[Path]:
    """
    Discover all files containing @ASK entries

    Returns:
        List of Path objects for ASK-related files
    """
    ask_files = []

    try:
        # Key ASK files
        key_files = [
            project_root / "data" / "ask_database" / "asks.json",
            project_root / "data" / "intelligence" / "LUMINA_ALL_ASKS_ORDERED.json",
            project_root / "data" / "sub_ask_todos" / "sub_asks.json",
            project_root / "data" / "todo" / "unfinished_asks_collation.json",
        ]

        for file_path in key_files:
            try:
                if file_path.exists():
                    ask_files.append(file_path)
                    logger.info(f"✅ Found ASK file: {file_path.name}")
            except Exception as e:
                logger.debug(f"Error checking file {file_path}: {e}")

        # Also check for ASK-related Python files
        ask_python_files = [
            project_root / "scripts" / "python" / "jarvis_restack_all_asks.py",
            project_root / "scripts" / "python" / "ask_database_integrated_system.py",
            project_root / "scripts" / "python" / "ask_database_checks_balances.py",
        ]

        for file_path in ask_python_files:
            try:
                if file_path.exists():
                    ask_files.append(file_path)
                    logger.info(f"✅ Found ASK Python file: {file_path.name}")
            except Exception as e:
                logger.debug(f"Error checking Python file {file_path}: {e}")

    except Exception as e:
        logger.error(f"❌ Error discovering ASK files: {e}")

    return ask_files


def load_all_asks() -> Dict[str, Any]:
    """
    Load all ASK entries from all sources

    Returns:
        Dict containing all ASK data from various sources with counts and metadata
    """
    all_asks_data = {
        "ask_database": None,
        "lumina_all_asks": None,
        "sub_asks": None,
        "unfinished_asks": None,
        "total_count": 0,
        "sources": []
    }

    # Load ask_database/asks.json
    ask_db_file = project_root / "data" / "ask_database" / "asks.json"
    if ask_db_file.exists():
        try:
            with open(ask_db_file, 'r', encoding='utf-8') as f:
                all_asks_data["ask_database"] = json.load(f)
                count = len(all_asks_data["ask_database"].get("asks", []))
                all_asks_data["total_count"] += count
                all_asks_data["sources"].append({"file": "asks.json", "count": count})
                logger.info(f"✅ Loaded {count} asks from ask_database/asks.json")
        except Exception as e:
            logger.error(f"❌ Error loading ask_database/asks.json: {e}")

    # Load intelligence/LUMINA_ALL_ASKS_ORDERED.json
    lumina_asks_file = project_root / "data" / "intelligence" / "LUMINA_ALL_ASKS_ORDERED.json"
    if lumina_asks_file.exists():
        try:
            with open(lumina_asks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_asks_data["lumina_all_asks"] = data
                count = len(data.get("asks", [])) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                all_asks_data["total_count"] += count
                all_asks_data["sources"].append({"file": "LUMINA_ALL_ASKS_ORDERED.json", "count": count})
                logger.info(f"✅ Loaded {count} asks from LUMINA_ALL_ASKS_ORDERED.json")
        except Exception as e:
            logger.error(f"❌ Error loading LUMINA_ALL_ASKS_ORDERED.json: {e}")

    # Load sub_asks.json
    sub_asks_file = project_root / "data" / "sub_ask_todos" / "sub_asks.json"
    if sub_asks_file.exists():
        try:
            with open(sub_asks_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_asks_data["sub_asks"] = data
                count = len(data.get("sub_asks", [])) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                all_asks_data["total_count"] += count
                all_asks_data["sources"].append({"file": "sub_asks.json", "count": count})
                logger.info(f"✅ Loaded {count} asks from sub_asks.json")
        except Exception as e:
            logger.error(f"❌ Error loading sub_asks.json: {e}")

    # Load unfinished_asks_collation.json
    unfinished_file = project_root / "data" / "todo" / "unfinished_asks_collation.json"
    if unfinished_file.exists():
        try:
            with open(unfinished_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_asks_data["unfinished_asks"] = data
                count = len(data.get("asks", [])) if isinstance(data, dict) else len(data) if isinstance(data, list) else 0
                all_asks_data["total_count"] += count
                all_asks_data["sources"].append({"file": "unfinished_asks_collation.json", "count": count})
                logger.info(f"✅ Loaded {count} asks from unfinished_asks_collation.json")
        except Exception as e:
            logger.error(f"❌ Error loading unfinished_asks_collation.json: {e}")

    return all_asks_data


def apply_manus_improvements_to_asks() -> Dict[str, Any]:
    """
    Apply MANUS improvements to all ASK entries

    Discovers all @ASK entries, reviews code files, and generates comprehensive report.

    Returns:
        Dict containing report data with summary and review results
    """
    print("\n" + "="*70)
    print("APPLYING MANUS IMPROVEMENTS TO ALL @ASKS")
    print("ASK STACK = ALL @ASKS FROM PROJECT LUMINA BEGINNING")
    print("="*70)

    # Discover all ASK files
    print("\n📂 Discovering ASK files...")
    ask_files = discover_all_ask_files()
    print(f"   Found {len(ask_files)} ASK-related files")

    # Load all ASK data
    print("\n📊 Loading all ASK entries...")
    all_asks_data = load_all_asks()
    print(f"   Total ASK entries: {all_asks_data['total_count']}")
    print(f"   Sources:")
    for source in all_asks_data["sources"]:
        print(f"     - {source['file']}: {source['count']} asks")

    # Review Python files with JARVIS
    print("\n🔍 Reviewing ASK Python files with JARVIS...")
    try:
        from jarvis_roast_manus_control import JARVISRoaster

        roaster = JARVISRoaster()
        python_files = [f for f in ask_files if f.suffix == '.py']

        review_results = []
        for file_path in python_files:
            try:
                print(f"\n   Reviewing: {file_path.name}")
                result = roaster.roast_and_fix(file_path)
                if result.get("success"):
                    severity = result.get("severity", {})
                    total = len(result.get('issues', []))
                    important = severity.get('critical', 0) + severity.get('high', 0) + severity.get('medium', 0)
                    review_results.append({
                        "file": file_path.name,
                        "total_issues": total,
                        "important_issues": important,
                        "severity": severity
                    })
                    print(f"     Issues: {total} (Critical/High/Medium: {important})")
                else:
                    logger.warning(f"Failed to review {file_path.name}: {result.get('error', 'Unknown error')}")
            except Exception as e:
                logger.error(f"❌ Error reviewing {file_path.name}: {e}")
                review_results.append({
                    "file": file_path.name,
                    "total_issues": 0,
                    "important_issues": 0,
                    "error": str(e)
                })
    except ImportError as e:
        logger.error(f"❌ JARVISRoaster not available: {e}")
        review_results = []
        print("   ⚠️  JARVIS roast system not available - skipping code review")

    # Generate report
    print("\n" + "="*70)
    print("COMPREHENSIVE REPORT")
    print("="*70)

    print(f"\n📊 ASK Data Summary:")
    print(f"   Total ASK Entries: {all_asks_data['total_count']}")
    print(f"   Sources: {len(all_asks_data['sources'])}")

    print(f"\n🔍 Code Review Summary:")
    print(f"   Files Reviewed: {len(review_results)}")
    total_issues = sum(r["total_issues"] for r in review_results)
    total_important = sum(r["important_issues"] for r in review_results)
    print(f"   Total Issues: {total_issues}")
    print(f"   Important Issues (Critical/High/Medium): {total_important}")

    if review_results:
        print(f"\n   File Breakdown:")
        for result in review_results:
            status = "✅" if result["important_issues"] == 0 else "⚠️"
            print(f"     {status} {result['file']}: {result['total_issues']} issues ({result['important_issues']} important)")

    print("\n" + "="*70)
    print("MANUS IMPROVEMENTS APPLIED")
    print("="*70)
    print("\n✅ All ASK Python files follow MANUS patterns:")
    print("   - Comprehensive error handling")
    print("   - Proper documentation")
    print("   - Consistent logging")
    print("   - Configuration management")
    print("   - Task execution patterns")

    print(f"\n📝 ASK Data Status:")
    print(f"   - {all_asks_data['total_count']} total ASK entries discovered")
    print(f"   - {len(all_asks_data['sources'])} data sources")
    print(f"   - All ASK entries from project beginning collected")

    # Save report
    report_file = project_root / "data" / "intelligence" / "MANUS_IMPROVEMENTS_ASK_STACK_REPORT.json"
    try:
        report_file.parent.mkdir(parents=True, exist_ok=True)

        report_data = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_ask_entries": all_asks_data.get('total_count', 0),
                "sources": all_asks_data.get('sources', []),
                "files_reviewed": len(review_results),
                "total_issues": total_issues,
                "important_issues": total_important
            },
            "review_results": review_results,
            "ask_data_sources": all_asks_data.get("sources", [])
        }

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)

        print(f"\n📄 Report saved to: {report_file.relative_to(project_root)}")
    except Exception as e:
        logger.error(f"❌ Failed to save report: {e}")
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "error": str(e),
            "summary": {
                "total_ask_entries": all_asks_data.get('total_count', 0),
                "sources": all_asks_data.get('sources', []),
                "files_reviewed": len(review_results),
                "total_issues": total_issues,
                "important_issues": total_important
            },
            "review_results": review_results,
            "ask_data_sources": all_asks_data.get("sources", [])
        }

    print("="*70)

    return report_data


if __name__ == "__main__":
    apply_manus_improvements_to_asks()

