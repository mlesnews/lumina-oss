"""
Complete Brian Fletcher Bid Analysis
Get email summary, extract attachment, and provide HVAC SME analysis.

Works with:
1. N8N Email Hub (if accessible)
2. Direct file path (if you have the attachment)
3. Email content (if you paste it)

#JARVIS #LUMINA #HVAC #SME #BRIAN-FLETCHER
"""

import json
import sys
from pathlib import Path
from typing import Dict, Optional

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("AnalyzeBrianBidComplete")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("AnalyzeBrianBidComplete")

from scripts.python.hvac_sme_analysis import HVACSMEAnalyzer
from scripts.python.hvac_bid_extractor import BidExtractor
from scripts.python.get_brian_bid_from_n8n import N8NEmailHubClient


def analyze_brian_bid_complete(file_path: Optional[Path] = None, email_text: Optional[str] = None):
    """
    Complete analysis of Brian's bid.

    Args:
        file_path: Optional path to bid file
        email_text: Optional email text content
    """
    print("\n" + "="*80)
    print("HVAC SME ANALYSIS - BRIAN FLETCHER'S BID")
    print("="*80)
    print("Channeling inner HVAC SME...")
    print()

    analyzer = HVACSMEAnalyzer(project_root)
    extractor = BidExtractor(project_root)

    # Try N8N first if no file provided
    if not file_path:
        print("Attempting to retrieve from N8N Email Hub...")
        try:
            n8n_client = N8NEmailHubClient(project_root)
            result = n8n_client.get_brian_bid()

            if "error" not in result:
                print("\n✅ Successfully retrieved from N8N!")
                return result

            print("⚠️  N8N not accessible, trying file search...")
        except Exception as e:
            print(f"⚠️  N8N access failed: {e}")
            print("Trying file search...")

    # Search for file
    if not file_path:
        print("\nSearching for Brian's bid file...")

        search_paths = [
            project_root / "data" / "hvac_bids" / "attachments",
            Path.home() / "Downloads",
            Path.home() / "Desktop",
            project_root / "data" / "hvac_bids"
        ]

        search_terms = ["brian", "fletcher", "plumbing", "heating", "hvac", "bid", "quote"]

        for search_path in search_paths:
            if not search_path.exists():
                continue

            for file_path_candidate in search_path.rglob("*"):
                if file_path_candidate.is_file():
                    file_name_lower = file_path_candidate.name.lower()
                    if any(term in file_name_lower for term in search_terms):
                        if file_path_candidate.suffix.lower() in [".pdf", ".docx", ".doc", ".txt"]:
                            file_path = file_path_candidate
                            print(f"✅ Found: {file_path}")
                            break

                if file_path:
                    break

            if file_path:
                break

    # Extract from file
    if file_path and file_path.exists():
        print(f"\n📄 Analyzing bid file: {file_path}")

        # Extract bid data
        bid_data = extractor.extract_from_file(file_path, "Brian Fletcher - Fletcher's Heating & Plumbing")

        if not bid_data:
            print("❌ Failed to extract bid data from file")
            return

        # Analyze
        analysis = analyzer.analyze_bid(bid_data, "Brian Fletcher - Fletcher's Heating & Plumbing")

        # Print analysis
        analyzer.print_analysis(analysis)

        # Save
        output_file = project_root / "data" / "hvac_bids" / f"brian_fletcher_complete_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump({
                "bid_data": bid_data,
                "sme_analysis": analysis,
                "file_path": str(file_path)
            }, f, indent=2, ensure_ascii=False)

        print(f"\n📄 Complete analysis saved to: {output_file}")

        return analysis

    # Extract from email text
    elif email_text:
        print("\n📧 Extracting from email text...")

        bid_data = extractor.extract_from_text(email_text, "Brian Fletcher - Fletcher's Heating & Plumbing")

        if bid_data:
            analysis = analyzer.analyze_bid(bid_data, "Brian Fletcher - Fletcher's Heating & Plumbing")
            analyzer.print_analysis(analysis)
            return analysis

    # No data found
    print("\n❌ Could not find Brian's bid")
    print("\nPlease provide:")
    print("  1. File path: --file <path_to_bid_file>")
    print("  2. Or email text: --email-text <email_content>")
    print("  3. Or place file in: data/hvac_bids/attachments/")
    print("\nExample:")
    print("  python scripts/python/analyze_brian_bid_complete.py --file \"path/to/brian_bid.pdf\"")


def main():
    try:
        """Main function."""
        import argparse
        from datetime import datetime

        parser = argparse.ArgumentParser(description="Complete Brian Fletcher Bid Analysis")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--file", type=Path, help="Path to Brian's bid file")
        parser.add_argument("--email-text", type=str, help="Email text content")
        parser.add_argument("--n8n-url", type=str, help="N8N URL (default: http://<NAS_PRIMARY_IP>:5678)")

        args = parser.parse_args()

        global project_root
        project_root = args.project_root

        analyze_brian_bid_complete(args.file, args.email_text)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()