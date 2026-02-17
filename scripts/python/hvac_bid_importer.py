"""
Quick HVAC Bid Importer
Helper script to quickly import HVAC bids interactively or from files.

#JARVIS #LUMINA
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from hvac_bid_comparison import HVACBidComparator, HVACBid


def create_bid_interactive() -> Dict[str, Any]:
    """
    Interactively create a bid entry.

    Returns:
        Dictionary containing bid data
    """
    print("\n" + "="*80)
    print("HVAC BID ENTRY")
    print("="*80)

    bid_data = {}

    # Required fields
    bid_data["contractor_name"] = input("\nContractor Name: ").strip()

    # Optional fields
    contact = input("Contact Info (phone/email) [optional]: ").strip()
    if contact:
        bid_data["contact_info"] = contact

    bid_date = input("Bid Date (YYYY-MM-DD) [optional]: ").strip()
    if bid_date:
        bid_data["bid_date"] = bid_date

    # Costs
    print("\n--- COSTS ---")
    total = input("Total Cost ($): ").strip()
    if total:
        try:
            bid_data["total_cost"] = float(total)
        except ValueError:
            print(f"Warning: Invalid total cost '{total}', skipping")

    equipment = input("Equipment Cost ($) [optional]: ").strip()
    if equipment:
        try:
            bid_data["equipment_cost"] = float(equipment)
        except ValueError:
            print(f"Warning: Invalid equipment cost '{equipment}', skipping")

    labor = input("Labor Cost ($) [optional]: ").strip()
    if labor:
        try:
            bid_data["labor_cost"] = float(labor)
        except ValueError:
            print(f"Warning: Invalid labor cost '{labor}', skipping")

    permit = input("Permit Cost ($) [optional]: ").strip()
    if permit:
        try:
            bid_data["permit_cost"] = float(permit)
        except ValueError:
            print(f"Warning: Invalid permit cost '{permit}', skipping")

    disposal = input("Disposal Cost ($) [optional]: ").strip()
    if disposal:
        try:
            bid_data["disposal_cost"] = float(disposal)
        except ValueError:
            print(f"Warning: Invalid disposal cost '{disposal}', skipping")

    # Equipment details
    print("\n--- EQUIPMENT ---")
    has_equipment = input("Enter equipment details? (y/n) [n]: ").strip().lower()
    if has_equipment == 'y':
        equipment_data = {}

        brand = input("Brand [optional]: ").strip()
        if brand:
            equipment_data["brand"] = brand

        model = input("Model [optional]: ").strip()
        if model:
            equipment_data["model"] = model

        efficiency = input("Efficiency Rating (e.g., '96% AFUE') [optional]: ").strip()
        if efficiency:
            equipment_data["efficiency_rating"] = efficiency

        capacity = input("Capacity (e.g., '80,000 BTU') [optional]: ").strip()
        if capacity:
            equipment_data["capacity"] = capacity

        warranty = input("Warranty Years [optional]: ").strip()
        if warranty:
            try:
                equipment_data["warranty_years"] = int(warranty)
            except ValueError:
                print(f"Warning: Invalid warranty years '{warranty}', skipping")

        # Features
        features = []
        print("Enter features (one per line, empty line to finish):")
        while True:
            feature = input("  Feature: ").strip()
            if not feature:
                break
            features.append(feature)
        if features:
            equipment_data["features"] = features

        if equipment_data:
            bid_data["equipment"] = equipment_data

    # Other details
    print("\n--- OTHER DETAILS ---")
    timeline = input("Installation Timeline [optional]: ").strip()
    if timeline:
        bid_data["installation_timeline"] = timeline

    payment = input("Payment Terms [optional]: ").strip()
    if payment:
        bid_data["payment_terms"] = payment

    warranty_info = input("Warranty Information [optional]: ").strip()
    if warranty_info:
        bid_data["warranty_info"] = warranty_info

    # Notes
    notes = []
    print("Enter notes (one per line, empty line to finish):")
    while True:
        note = input("  Note: ").strip()
        if not note:
            break
        notes.append(note)
    if notes:
        bid_data["notes"] = notes

    return bid_data


def import_bids_from_directory(directory: Path, comparator: HVACBidComparator) -> int:
    """
    Import all JSON bid files from a directory.

    Args:
        directory: Directory containing bid JSON files
        comparator: HVACBidComparator instance

    Returns:
        Number of bids imported
    """
    if not directory.exists():
        print(f"Directory not found: {directory}")
        return 0

    json_files = list(directory.glob("*.json"))
    # Exclude the template and existing bids file
    json_files = [f for f in json_files 
                  if f.name != "bid_template.json" and f.name != "hvac_bids.json"]

    if not json_files:
        print(f"No bid JSON files found in {directory}")
        return 0

    imported = 0
    for json_file in json_files:
        try:
            comparator.import_bid_from_json(json_file)
            imported += 1
            print(f"✓ Imported: {json_file.name}")
        except Exception as e:
            print(f"✗ Failed to import {json_file.name}: {e}")

    return imported


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="HVAC Bid Importer")
    parser.add_argument("--project-root", type=Path,
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--budget", type=float, default=7000.0,
                       help="Project budget in dollars")
    parser.add_argument("--interactive", action="store_true",
                       help="Interactively create a new bid")
    parser.add_argument("--import-dir", type=Path,
                       help="Import all JSON files from directory")
    parser.add_argument("--import-file", type=Path, action="append",
                       help="Import specific JSON file (can be used multiple times)")
    parser.add_argument("--compare", action="store_true",
                       help="Generate comparison after importing")
    parser.add_argument("--save", type=str, default="hvac_bids.json",
                       help="Save bids to JSON file")

    args = parser.parse_args()

    # Initialize comparator
    comparator = HVACBidComparator(args.project_root)
    comparator.set_budget(args.budget)

    # Load existing bids
    try:
        comparator.load_bids(args.save)
        print(f"Loaded {len(comparator.bids)} existing bid(s)")
    except Exception as e:
        print(f"No existing bids found or error loading: {e}")

    # Interactive entry
    if args.interactive:
        bid_data = create_bid_interactive()
        comparator.import_bid_from_dict(bid_data)
        print(f"\n✓ Added bid from {bid_data['contractor_name']}")

    # Import from directory
    if args.import_dir:
        imported = import_bids_from_directory(args.import_dir, comparator)
        print(f"\n✓ Imported {imported} bid(s) from directory")

    # Import specific files
    if args.import_file:
        for bid_file in args.import_file:
            if bid_file.exists():
                try:
                    comparator.import_bid_from_json(bid_file)
                    print(f"✓ Imported: {bid_file.name}")
                except Exception as e:
                    print(f"✗ Failed to import {bid_file.name}: {e}")
            else:
                print(f"✗ File not found: {bid_file}")

    # Save bids
    if comparator.bids:
        comparator.save_bids(args.save)
        print(f"\n✓ Saved {len(comparator.bids)} bid(s) to {args.save}")

    # Compare
    if args.compare and len(comparator.bids) >= 2:
        print("\n")
        comparator.print_summary()
        report_path = comparator.generate_report()
        print(f"\n✓ Generated comparison report: {report_path}")
    elif args.compare and len(comparator.bids) < 2:
        print("\n⚠ Need at least 2 bids to compare")


if __name__ == "__main__":


    main()