"""
Analyze Brian Fletcher's HVAC Bid
Find, extract, and analyze Brian's bid with HVAC SME expertise.

#JARVIS #LUMINA #HVAC #SME #BRIAN-FLETCHER
"""

import json
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from scripts.python.hvac_sme_analysis import HVACSMEAnalyzer
from scripts.python.hvac_bid_extractor import BidExtractor

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AnalyzeBrianBid")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AnalyzeBrianBid")


def find_brian_bid_attachment() -> Optional[Path]:
    try:
        """Find Brian's bid attachment file."""
        # Common locations
        search_paths = [
            project_root / "data" / "hvac_bids" / "attachments",
            project_root / "Downloads",
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            project_root / "data" / "hvac_bids",
        ]

        # Search for files with Brian/Fletcher in name
        search_terms = ["brian", "fletcher", "fletchers", "plumbing", "heating"]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for file_path in search_path.rglob("*"):
                if file_path.is_file():
                    file_name_lower = file_path.name.lower()
                    if any(term in file_name_lower for term in search_terms):
                        if file_path.suffix.lower() in [".pdf", ".docx", ".doc", ".txt"]:
                            logger.info(f"✅ Found potential bid file: {file_path}")
                            return file_path

        return None


    except Exception as e:
        logger.error(f"Error in find_brian_bid_attachment: {e}", exc_info=True)
        raise
def analyze_brian_bid(file_path: Optional[Path] = None):
    """
    Analyze Brian Fletcher's HVAC bid.

    Args:
        file_path: Optional path to bid file (will search if not provided)
    """
    print("\n" + "="*80)
    print("HVAC SME ANALYSIS - BRIAN FLETCHER'S BID")
    print("="*80)
    print("Channeling inner HVAC SME...")
    print()

    # Find file if not provided
    if not file_path:
        print("Searching for Brian's bid attachment...")
        file_path = find_brian_bid_attachment()

        if not file_path:
            print("❌ Could not find Brian's bid attachment automatically")
            print()
            print("Please provide the file path:")
            print("  python scripts/python/analyze_brian_bid.py --file <path_to_bid_file>")
            print()
            print("Or manually place the bid file in one of these locations:")
            print("  - data/hvac_bids/attachments/")
            print("  - Downloads/")
            print("  - Desktop/")
            print()
            print("File should be named with 'brian', 'fletcher', 'plumbing', or 'heating'")
            return

    print(f"📄 Analyzing bid file: {file_path}")
    print()

    # Initialize analyzer
    analyzer = HVACSMEAnalyzer(project_root)

    # Extract and analyze
    try:
        analysis = analyzer.analyze_bid_file(file_path)

        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return

        # Print analysis
        analyzer.print_analysis(analysis)

        # Save analysis
        output_file = project_root / "data" / "hvac_bids" / f"brian_fletcher_sme_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)

        print(f"📄 Full analysis saved to: {output_file}")
        print()
        print("="*80)
        print("ANALYSIS COMPLETE")
        print("="*80)

    except Exception as e:
        logger.error(f"Failed to analyze bid: {e}", exc_info=True)
        print(f"❌ Error analyzing bid: {e}")


def main():
    try:
        """Main function."""
        import argparse
        from datetime import datetime

        parser = argparse.ArgumentParser(description="Analyze Brian Fletcher's HVAC Bid")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--file", type=Path, help="Path to Brian's bid file (PDF, DOCX, TXT)")

        args = parser.parse_args()

        global project_root
        project_root = args.project_root

        analyze_brian_bid(args.file)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()