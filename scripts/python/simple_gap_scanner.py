#!/usr/bin/env python3
"""
Simple Gap Scanner - Quick identification of critical gaps
"""

import os
import sys
from pathlib import Path
from typing import List, Dict
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("simple_gap_scanner")


project_root = Path(__file__).parent.parent


# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def scan_todos_fixmes() -> List[Dict]:
    """Scan for TODO and FIXME comments"""
    gaps = []
    for root, dirs, files in os.walk(project_root):
        # Skip certain directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.pytest_cache']]

        for file in files:
            if file.endswith(('.py', '.js', '.ts', '.md', '.ps1')):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()

                    for line_num, line in enumerate(lines, 1):
                        line_lower = line.lower()
                        if 'todo' in line_lower or 'fixme' in line_lower or 'xxx' in line_lower:
                            gaps.append({
                                'type': 'todo_fixme',
                                'file': str(filepath.relative_to(project_root)),
                                'line': line_num,
                                'content': line.strip(),
                                'severity': 'low'
                            })
                except:
                    pass
    return gaps

def scan_missing_implementations() -> List[Dict]:
    """Scan for 'not implemented' statements"""
    gaps = []
    for root, dirs, files in os.walk(project_root):
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', '.pytest_cache']]

        for file in files:
            if file.endswith(('.py', '.js', '.ts')):
                filepath = Path(root) / file
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read().lower()

                    if 'not implemented' in content or 'not yet implemented' in content:
                        gaps.append({
                            'type': 'missing_implementation',
                            'file': str(filepath.relative_to(project_root)),
                            'severity': 'medium'
                        })
                except:
                    pass
    return gaps

def scan_missing_readmes() -> List[Dict]:
    try:
        """Scan for missing README files"""
        gaps = []
        important_dirs = [
            project_root,
            project_root / "scripts",
            project_root / "config",
            project_root / "containerization"
        ]

        for dir_path in important_dirs:
            if dir_path.exists():
                readme_files = list(dir_path.glob("README*")) + list(dir_path.glob("readme*"))
                if not readme_files:
                    gaps.append({
                        'type': 'missing_documentation',
                        'file': str(dir_path.relative_to(project_root)),
                        'severity': 'low'
                    })

        return gaps

    except Exception as e:
        logger.error(f"Error in scan_missing_readmes: {e}", exc_info=True)
        raise
def scan_config_issues() -> List[Dict]:
    try:
        """Scan for configuration issues"""
        gaps = []

        # Check for missing config files
        required_configs = [
            "config/service_orchestration.yaml",
            ".vscode/tasks.json",
            ".vscode/launch.json"
        ]

        for config in required_configs:
            config_path = project_root / config
            if not config_path.exists():
                gaps.append({
                    'type': 'missing_config',
                    'file': config,
                    'severity': 'high'
                })

        return gaps

    except Exception as e:
        logger.error(f"Error in scan_config_issues: {e}", exc_info=True)
        raise
def main():
    """Main scanner"""
    print("🔍 Scanning for gaps in Lumina system...")

    all_gaps = []

    # Run all scans
    scans = [
        ("TODO/FIXME comments", scan_todos_fixmes),
        ("Missing implementations", scan_missing_implementations),
        ("Missing documentation", scan_missing_readmes),
        ("Config issues", scan_config_issues)
    ]

    for scan_name, scan_func in scans:
        print(f"  Scanning {scan_name}...")
        gaps = scan_func()
        all_gaps.extend(gaps)
        print(f"    Found {len(gaps)} gaps")

    # Report results
    print(f"\n📊 Gap Analysis Complete")
    print(f"Total gaps found: {len(all_gaps)}")

    if all_gaps:
        print("\n🎯 Gaps by severity:")

        severity_counts = {'critical': 0, 'high': 0, 'medium': 0, 'low': 0}
        for gap in all_gaps:
            severity_counts[gap['severity']] = severity_counts.get(gap['severity'], 0) + 1

        for severity, count in severity_counts.items():
            if count > 0:
                emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[severity]
                print(f"  {emoji} {severity.title()}: {count}")

        print("\n🔧 Top gaps to address:")
        # Sort by severity
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_gaps = sorted(all_gaps, key=lambda x: severity_order.get(x['severity'], 99))

        for i, gap in enumerate(sorted_gaps[:10], 1):
            emoji = {'critical': '🔴', 'high': '🟠', 'medium': '🟡', 'low': '🟢'}[gap['severity']]
            print(f"  {i}. {emoji} [{gap['type']}] {gap.get('file', 'N/A')}")
            if 'line' in gap:
                print(f"     Line {gap['line']}: {gap['content'][:60]}{'...' if len(gap['content']) > 60 else ''}")
    else:
        print("✅ No gaps found!")

if __name__ == "__main__":


    main()