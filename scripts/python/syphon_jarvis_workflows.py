#!/usr/bin/env python3
"""
SYPHON JARVIS Workflows Extraction Script
Extracts intelligence from JARVIS workflows, agent coordination, and collaboration patterns

Usage:
    python scripts/python/syphon_jarvis_workflows.py [--scan-all] [--workflow-id ID] [--output-dir DIR]

#SYPHON #JARVIS #WORKFLOWS #AGENTS #COORDINATION #COLLABORATION #CTO
"""

import sys
import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from syphon.core import SYPHONSystem, SYPHONConfig, SubscriptionTier
    from syphon.models import DataSourceType
    SYPHON_AVAILABLE = True
except ImportError as e:
    SYPHON_AVAILABLE = False
    print(f"SYPHON not available: {e}")

logger = get_logger("SYPHONJARVISWorkflows")


def find_workflow_files(project_root: Path) -> List[Path]:
    try:
        """Find all workflow-related files"""
        workflow_files = []

        # Search in various directories
        search_dirs = [
            project_root / "data" / "workflow_logs",
            project_root / "data" / "jarvis_intelligence",
            project_root / "data" / "r5_living_matrix" / "sessions",
            project_root / "data" / "telemetry",
        ]

        for search_dir in search_dirs:
            if search_dir.exists():
                # Find JSON files
                for json_file in search_dir.rglob("*.json"):
                    workflow_files.append(json_file)

        return workflow_files


    except Exception as e:
        logger.error(f"Error in find_workflow_files: {e}", exc_info=True)
        raise
def extract_workflow_intelligence(
    syphon: SYPHONSystem,
    workflow_file: Path,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """Extract intelligence from a single workflow file"""
    try:
        logger.info(f"Extracting intelligence from: {workflow_file}")

        # Load workflow data
        with open(workflow_file, 'r', encoding='utf-8') as f:
            workflow_data = json.load(f)

        # Extract intelligence
        result = syphon.extract(
            source_type=DataSourceType.WORKFLOW,
            content=workflow_data,
            metadata={
                "source_file": str(workflow_file),
                "extraction_timestamp": datetime.now().isoformat(),
            }
        )

        if result.success and result.data:
            # Save extracted intelligence
            if output_dir:
                output_dir.mkdir(parents=True, exist_ok=True)
                output_file = output_dir / f"extracted_{workflow_file.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(result.data.to_dict(), f, indent=2, default=str)
                logger.info(f"Saved extracted intelligence to: {output_file}")

            return {
                "success": True,
                "file": str(workflow_file),
                "extracted_count": result.extracted_count if hasattr(result, 'extracted_count') else 0,
                "intelligence": result.data.to_dict(),
            }
        else:
            logger.warning(f"Extraction failed for {workflow_file}: {result.error}")
            return {
                "success": False,
                "file": str(workflow_file),
                "error": result.error,
            }

    except Exception as e:
        logger.error(f"Error processing {workflow_file}: {e}", exc_info=True)
        return {
            "success": False,
            "file": str(workflow_file),
            "error": str(e),
        }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Extract intelligence from JARVIS workflows using SYPHON"
    )
    parser.add_argument(
        "--scan-all",
        action="store_true",
        help="Scan all workflow files and extract intelligence"
    )
    parser.add_argument(
        "--workflow-id",
        type=str,
        help="Extract intelligence from a specific workflow ID"
    )
    parser.add_argument(
        "--workflow-file",
        type=str,
        help="Extract intelligence from a specific workflow file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Output directory for extracted intelligence (default: data/syphon/jarvis_workflows)"
    )

    args = parser.parse_args()

    if not SYPHON_AVAILABLE:
        logger.error("SYPHON system not available. Cannot extract intelligence.")
        return 1

    # Initialize SYPHON
    config = SYPHONConfig(
        project_root=project_root,
        subscription_tier=SubscriptionTier.ENTERPRISE,
        enable_self_healing=True,
    )
    syphon = SYPHONSystem(config)

    # Set output directory
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        output_dir = project_root / "data" / "syphon" / "jarvis_workflows"

    output_dir.mkdir(parents=True, exist_ok=True)

    results = []

    if args.workflow_file:
        # Extract from specific file
        workflow_file = Path(args.workflow_file)
        if workflow_file.exists():
            result = extract_workflow_intelligence(syphon, workflow_file, output_dir)
            results.append(result)
        else:
            logger.error(f"Workflow file not found: {workflow_file}")
            return 1

    elif args.workflow_id:
        # Find workflow by ID
        workflow_files = find_workflow_files(project_root)
        found = False
        for workflow_file in workflow_files:
            try:
                with open(workflow_file, 'r', encoding='utf-8') as f:
                    workflow_data = json.load(f)
                    if workflow_data.get("workflow_id") == args.workflow_id or workflow_data.get("id") == args.workflow_id:
                        result = extract_workflow_intelligence(syphon, workflow_file, output_dir)
                        results.append(result)
                        found = True
                        break
            except Exception as e:
                logger.debug(f"Error reading {workflow_file}: {e}")

        if not found:
            logger.error(f"Workflow ID not found: {args.workflow_id}")
            return 1

    elif args.scan_all:
        # Scan all workflow files
        logger.info("Scanning all workflow files...")
        workflow_files = find_workflow_files(project_root)
        logger.info(f"Found {len(workflow_files)} workflow files")

        for workflow_file in workflow_files:
            result = extract_workflow_intelligence(syphon, workflow_file, output_dir)
            results.append(result)

    else:
        parser.print_help()
        return 1

    # Summary
    successful = sum(1 for r in results if r.get("success", False))
    failed = len(results) - successful

    logger.info("=" * 80)
    logger.info("SYPHON JARVIS Workflow Extraction Summary")
    logger.info("=" * 80)
    logger.info(f"Total workflows processed: {len(results)}")
    logger.info(f"Successful extractions: {successful}")
    logger.info(f"Failed extractions: {failed}")
    logger.info(f"Output directory: {output_dir}")

    # Save summary
    summary_file = output_dir / f"extraction_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(summary_file, 'w', encoding='utf-8') as f:
        json.dump({
            "extraction_timestamp": datetime.now().isoformat(),
            "total_processed": len(results),
            "successful": successful,
            "failed": failed,
            "results": results,
        }, f, indent=2, default=str)

    logger.info(f"Summary saved to: {summary_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":


    sys.exit(main())