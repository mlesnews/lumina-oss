#!/usr/bin/env python3
"""
RoamWise Tag Aggregator
Aggregates tags from @REPORT files and @DOIT workflows for Word Cloud visualization.

Tags: #HYPERSPACELANES #ROAMWISE #WORDCLOUD #AGGREGATION @JARVIS @ROAMWISE
"""

import json
import os
from pathlib import Path
from collections import Counter
from datetime import datetime
import logging
logger = logging.getLogger("roamwise_tag_aggregator")


def aggregate_tags(project_root: Path):
    """Scan data directories and aggregate tags"""
    tag_counter = Counter()

    # Directories to scan
    scan_dirs = [
        project_root / "data" / "doit_enhanced",
        project_root / "data" / "doit_workflows",
        project_root / "data" / "helpdesk" / "tickets"
    ]

    for scan_dir in scan_dirs:
        if not scan_dir.exists():
            continue

        for file in scan_dir.glob("*.json"):
            try:
                with open(file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract tags from different possible locations
                tags = data.get('tags', [])
                if not tags and 'ticket_data' in data:
                    tags = data['ticket_data'].get('tags', [])

                for tag in tags:
                    tag_counter[tag] += 1
            except Exception:
                continue

    # Also scan markdown reports for tags
    reports_dir = project_root / "docs" / "system"
    for file in reports_dir.glob("*.md"):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Find hashtags and @mentions (simple regex-like approach)
            import re
            found_tags = re.findall(r'[#@][\w-]+', content)
            for tag in found_tags:
                tag_counter[tag] += 1
        except Exception:
            continue

    return tag_counter

def main():
    try:
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / "data" / "roamwise_word_cloud.json"

        print("🌌 Scanning #HYPERSPACELANES for @ROAMWISE...")
        tags = aggregate_tags(project_root)

        # Sort by frequency
        sorted_tags = dict(sorted(tags.items(), key=lambda item: item[1], reverse=True))

        result = {
            "timestamp": datetime.now().isoformat(),
            "total_tags": len(tags),
            "tag_cloud": sorted_tags
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)

        print(f"✅ RoamWise Word Cloud data generated: {output_file}")
        print(f"📊 Top Tags: {', '.join(list(sorted_tags.keys())[:10])}")

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()