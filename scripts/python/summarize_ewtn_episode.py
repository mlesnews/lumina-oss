#!/usr/bin/env python3
"""
Summarize EWTN Father Spitzer's Universe Episode
Displays and summarizes syphoned episode content for HK-47
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("SummarizeEWTN")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def find_latest_extraction() -> Path:
    try:
        """Find the latest EWTN extraction file"""
        hk47_data_dir = project_root / "data" / "hk47" / "ewtn_spitzer_multiverse"
        if not hk47_data_dir.exists():
            raise FileNotFoundError(f"HK-47 data directory not found: {hk47_data_dir}")

        extraction_files = list(hk47_data_dir.glob("extraction_*.json"))
        if not extraction_files:
            raise FileNotFoundError(f"No extraction files found in {hk47_data_dir}")

        # Get the latest file
        latest = max(extraction_files, key=lambda p: p.stat().st_mtime)
        return latest


    except Exception as e:
        logger.error(f"Error in find_latest_extraction: {e}", exc_info=True)
        raise
def load_extraction(file_path: Path) -> dict:
    try:
        """Load extraction data from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)


    except Exception as e:
        logger.error(f"Error in load_extraction: {e}", exc_info=True)
        raise
def format_summary(data: dict) -> str:
    """Format extraction data as a readable summary"""
    lines = []
    lines.append("=" * 80)
    lines.append("EWTN FATHER SPITZER'S UNIVERSE - EPISODE SUMMARY")
    lines.append("=" * 80)
    lines.append("")

    # Metadata
    metadata = data.get("metadata", {})
    lines.append("📺 SHOW INFORMATION")
    lines.append("-" * 80)
    lines.append(f"Show: {metadata.get('show', 'N/A')}")
    lines.append(f"Host: {metadata.get('host', 'N/A')}")
    lines.append(f"Topic: {metadata.get('topic', 'N/A')}")
    lines.append(f"Network: {metadata.get('network', 'N/A')}")
    lines.append(f"Extraction Date: {data.get('extraction_date', 'N/A')}")
    lines.append("")

    # URLs
    urls = data.get("urls", {})
    lines.append("🔗 RESOURCES & LINKS")
    lines.append("-" * 80)
    for key, url in urls.items():
        key_display = key.replace("_", " ").title()
        lines.append(f"  {key_display:20s}: {url}")
    lines.append("")

    # Content Summary
    content = data.get("content", "")
    if content:
        lines.append("📝 CONTENT SUMMARY")
        lines.append("-" * 80)
        # Clean up the content
        content_lines = content.strip().split('\n')
        for line in content_lines:
            if line.strip():
                lines.append(line)
        lines.append("")

    # SYPHON Data (if available)
    if "syphon_data" in data:
        syphon_data = data["syphon_data"]
        lines.append("🧠 SYPHON EXTRACTION ANALYSIS")
        lines.append("-" * 80)

        # Actionable Items
        actionable = syphon_data.get("actionable_items", [])
        if actionable:
            lines.append(f"Actionable Items ({len(actionable)}):")
            for i, item in enumerate(actionable[:10], 1):  # Limit to first 10
                lines.append(f"  {i}. {item}")
            if len(actionable) > 10:
                lines.append(f"  ... and {len(actionable) - 10} more")
            lines.append("")

        # Tasks
        tasks = syphon_data.get("tasks", [])
        if tasks:
            lines.append(f"Tasks ({len(tasks)}):")
            for i, task in enumerate(tasks[:10], 1):
                task_text = task.get("description", str(task)) if isinstance(task, dict) else task
                lines.append(f"  {i}. {task_text}")
            if len(tasks) > 10:
                lines.append(f"  ... and {len(tasks) - 10} more")
            lines.append("")

        # Intelligence
        intelligence = syphon_data.get("intelligence", [])
        if intelligence:
            lines.append(f"Intelligence Points ({len(intelligence)}):")
            for i, item in enumerate(intelligence[:10], 1):
                item_text = item.get("summary", str(item)) if isinstance(item, dict) else item
                lines.append(f"  {i}. {item_text}")
            if len(intelligence) > 10:
                lines.append(f"  ... and {len(intelligence) - 10} more")
            lines.append("")

        # Metadata
        syphon_metadata = syphon_data.get("metadata", {})
        if syphon_metadata:
            lines.append("Extraction Metadata:")
            for key, value in syphon_metadata.items():
                if key not in ["urls"]:  # URLs already shown above
                    key_display = key.replace("_", " ").title()
                    lines.append(f"  {key_display:20s}: {value}")
            lines.append("")

    # Notes
    lines.append("📌 NOTES")
    lines.append("-" * 80)
    lines.append("This episode discusses multiverse theories in physics and cosmology,")
    lines.append("their relationship to faith and reason, and theological considerations.")
    lines.append("")
    lines.append("The content was extracted using @syphon for @hk-47 processing.")
    lines.append("For full video content extraction, video processing would be required.")
    lines.append("")

    lines.append("=" * 80)

    return "\n".join(lines)


def enhance_with_syphon(data: dict) -> dict:
    """Enhance extraction data with SYPHON analysis if not already present"""
    if "syphon_data" in data and data["syphon_data"]:
        # Already has SYPHON data
        return data

    try:
        from scripts.python.syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
        from scripts.python.syphon.extractors import SocialExtractor

        # Initialize SYPHON
        config = SYPHONConfig(
            project_root=project_root,
            subscription_tier=SubscriptionTier.ENTERPRISE,
            enable_cache=True
        )
        syphon = SYPHONSystem(config)

        # Extract content
        content = data.get("content", "")
        metadata = data.get("metadata", {})

        if content:
            extractor = SocialExtractor(config)
            result = extractor.extract(
                content=content,
                metadata={
                    **metadata,
                    "urls": data.get("urls", {}),
                    "extraction_method": "summary_enhancement",
                    "target_system": "hk-47"
                }
            )

            if result.success and result.data:
                syphon.storage.save(result.data)
                data["syphon_data"] = result.data.to_dict()
                data["extraction_id"] = result.data.data_id
                logger.info(f"Enhanced with SYPHON extraction: {result.data.data_id}")

        return data
    except Exception as e:
        logger.debug(f"SYPHON enhancement failed (non-critical): {e}")
        return data


def main():
    """Main function"""
    try:
        # Find latest extraction
        extraction_file = find_latest_extraction()
        logger.info(f"Loading extraction from: {extraction_file}")

        # Load data
        data = load_extraction(extraction_file)

        # Enhance with SYPHON if needed
        data = enhance_with_syphon(data)

        # Format and display summary
        summary = format_summary(data)
        print(summary)

        # Save summary to file
        summary_file = extraction_file.parent / f"summary_{extraction_file.stem.replace('extraction_', '')}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        logger.info(f"Summary saved to: {summary_file}")

        return 0

    except FileNotFoundError as e:
        logger.error(f"Extraction file not found: {e}")
        print(f"\n❌ Error: {e}")
        print("\nRun syphon_ewtn_spitzer_multiverse.py first to extract content.")
        return 1
    except Exception as e:
        logger.error(f"Failed to summarize: {e}")
        print(f"\n❌ Error: {e}")
        return 1


if __name__ == "__main__":



    sys.exit(main())