"""
HVAC Bid Comparison System
Imports and compares HVAC bids from general contractors for furnace replacement.

#JARVIS #LUMINA #PEAK
"""

import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from decimal import Decimal

# Setup logging
logger = logging.getLogger(__name__)


@dataclass
class EquipmentSpec:
    """Equipment specifications for HVAC bid."""
    brand: Optional[str] = None
    model: Optional[str] = None
    efficiency_rating: Optional[str] = None  # e.g., "95% AFUE"
    capacity: Optional[str] = None  # e.g., "80,000 BTU"
    warranty_years: Optional[int] = None
    features: List[str] = None

    def __post_init__(self):
        if self.features is None:
            self.features = []


@dataclass
class HVACBid:
    """HVAC bid from a general contractor."""
    contractor_name: str
    contact_info: Optional[str] = None
    bid_date: Optional[str] = None
    total_cost: Optional[Decimal] = None
    equipment_cost: Optional[Decimal] = None
    labor_cost: Optional[Decimal] = None
    permit_cost: Optional[Decimal] = None
    disposal_cost: Optional[Decimal] = None
    equipment: Optional[EquipmentSpec] = None
    installation_timeline: Optional[str] = None
    payment_terms: Optional[str] = None
    warranty_info: Optional[str] = None
    notes: List[str] = None
    bid_file_path: Optional[str] = None

    def __post_init__(self):
        if self.notes is None:
            self.notes = []
        if isinstance(self.total_cost, (int, float)):
            self.total_cost = Decimal(str(self.total_cost))
        if isinstance(self.equipment_cost, (int, float)):
            self.equipment_cost = Decimal(str(self.equipment_cost))
        if isinstance(self.labor_cost, (int, float)):
            self.labor_cost = Decimal(str(self.labor_cost))
        if isinstance(self.permit_cost, (int, float)):
            self.permit_cost = Decimal(str(self.permit_cost))
        if isinstance(self.disposal_cost, (int, float)):
            self.disposal_cost = Decimal(str(self.disposal_cost))


class HVACBidComparator:
    """Compare and analyze HVAC bids."""

    def __init__(self, project_root: Path):
        """
        Initialize the HVAC bid comparator.

        Args:
            project_root: Root path of the LUMINA project
        """
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "hvac_bids"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.bids: List[HVACBid] = []
        self.budget: Optional[Decimal] = None

    def set_budget(self, budget: float) -> None:
        """
        Set the project budget.

        Args:
            budget: Budget amount in dollars
        """
        self.budget = Decimal(str(budget))
        logger.info(f"Budget set to ${self.budget:,.2f}")

    def import_bid_from_dict(self, bid_data: Dict[str, Any]) -> HVACBid:
        """
        Import a bid from a dictionary.

        Args:
            bid_data: Dictionary containing bid information

        Returns:
            HVACBid object
        """
        # Handle equipment spec
        equipment = None
        if "equipment" in bid_data:
            eq_data = bid_data["equipment"]
            equipment = EquipmentSpec(
                brand=eq_data.get("brand"),
                model=eq_data.get("model"),
                efficiency_rating=eq_data.get("efficiency_rating"),
                capacity=eq_data.get("capacity"),
                warranty_years=eq_data.get("warranty_years"),
                features=eq_data.get("features", [])
            )

        # Create bid
        bid = HVACBid(
            contractor_name=bid_data.get("contractor_name", "Unknown"),
            contact_info=bid_data.get("contact_info"),
            bid_date=bid_data.get("bid_date"),
            total_cost=bid_data.get("total_cost"),
            equipment_cost=bid_data.get("equipment_cost"),
            labor_cost=bid_data.get("labor_cost"),
            permit_cost=bid_data.get("permit_cost"),
            disposal_cost=bid_data.get("disposal_cost"),
            equipment=equipment,
            installation_timeline=bid_data.get("installation_timeline"),
            payment_terms=bid_data.get("payment_terms"),
            warranty_info=bid_data.get("warranty_info"),
            notes=bid_data.get("notes", []),
            bid_file_path=bid_data.get("bid_file_path")
        )

        self.bids.append(bid)
        logger.info(f"Imported bid from {bid.contractor_name}")
        return bid

    def import_bid_from_json(self, json_path: Path) -> HVACBid:
        try:
            """
            Import a bid from a JSON file.

            Args:
                json_path: Path to JSON file containing bid data

            Returns:
                HVACBid object
            """
            with open(json_path, 'r', encoding='utf-8') as f:
                bid_data = json.load(f)

            bid_data["bid_file_path"] = str(json_path)
            return self.import_bid_from_dict(bid_data)

        except Exception as e:
            self.logger.error(f"Error in import_bid_from_json: {e}", exc_info=True)
            raise
    def save_bids(self, filename: str = "hvac_bids.json") -> Path:
        try:
            """
            Save all bids to a JSON file.

            Args:
                filename: Name of the file to save

            Returns:
                Path to saved file
            """
            output_path = self.data_dir / filename
            bids_data = []

            for bid in self.bids:
                bid_dict = asdict(bid)
                # Convert Decimal to string for JSON serialization
                for key, value in bid_dict.items():
                    if isinstance(value, Decimal):
                        bid_dict[key] = str(value)
                bids_data.append(bid_dict)

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(bids_data, f, indent=2, ensure_ascii=False)

            logger.info(f"Saved {len(self.bids)} bids to {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error in save_bids: {e}", exc_info=True)
            raise
    def load_bids(self, filename: str = "hvac_bids.json") -> List[HVACBid]:
        try:
            """
            Load bids from a JSON file.

            Args:
                filename: Name of the file to load

            Returns:
                List of HVACBid objects
            """
            input_path = self.data_dir / filename
            if not input_path.exists():
                logger.warning(f"Bid file not found: {input_path}")
                return []

            with open(input_path, 'r', encoding='utf-8') as f:
                bids_data = json.load(f)

            self.bids = []
            for bid_data in bids_data:
                # Convert string costs back to Decimal
                for cost_key in ["total_cost", "equipment_cost", "labor_cost", 
                               "permit_cost", "disposal_cost"]:
                    if cost_key in bid_data and bid_data[cost_key]:
                        bid_data[cost_key] = Decimal(str(bid_data[cost_key]))

                self.import_bid_from_dict(bid_data)

            logger.info(f"Loaded {len(self.bids)} bids from {input_path}")
            return self.bids

        except Exception as e:
            self.logger.error(f"Error in load_bids: {e}", exc_info=True)
            raise
    def compare_bids(self) -> Dict[str, Any]:
        """
        Compare all bids and generate analysis.

        Returns:
            Dictionary containing comparison analysis
        """
        if len(self.bids) < 2:
            return {"error": "Need at least 2 bids to compare"}

        comparison = {
            "comparison_date": datetime.now().isoformat(),
            "total_bids": len(self.bids),
            "budget": str(self.budget) if self.budget else None,
            "cost_analysis": self._analyze_costs(),
            "equipment_analysis": self._analyze_equipment(),
            "recommendations": self._generate_recommendations(),
            "detailed_bids": [asdict(bid) for bid in self.bids]
        }

        # Convert Decimal to string for JSON serialization
        for bid_dict in comparison["detailed_bids"]:
            for key, value in bid_dict.items():
                if isinstance(value, Decimal):
                    bid_dict[key] = str(value)

        return comparison

    def _analyze_costs(self) -> Dict[str, Any]:
        """Analyze cost differences between bids."""
        costs = [bid.total_cost for bid in self.bids if bid.total_cost]
        if not costs:
            return {"error": "No cost data available"}

        min_cost = min(costs)
        max_cost = max(costs)
        avg_cost = sum(costs) / len(costs)

        analysis = {
            "lowest_bid": {
                "contractor": next(bid.contractor_name for bid in self.bids 
                                 if bid.total_cost == min_cost),
                "amount": str(min_cost)
            },
            "highest_bid": {
                "contractor": next(bid.contractor_name for bid in self.bids 
                                 if bid.total_cost == max_cost),
                "amount": str(max_cost)
            },
            "average_cost": str(Decimal(str(avg_cost)).quantize(Decimal('0.01'))),
            "cost_range": str(max_cost - min_cost),
            "within_budget": []
        }

        if self.budget:
            for bid in self.bids:
                if bid.total_cost and bid.total_cost <= self.budget:
                    analysis["within_budget"].append({
                        "contractor": bid.contractor_name,
                        "amount": str(bid.total_cost),
                        "under_budget_by": str(self.budget - bid.total_cost)
                    })

        return analysis

    def _analyze_equipment(self) -> Dict[str, Any]:
        """Analyze equipment differences between bids."""
        equipment_list = [bid.equipment for bid in self.bids if bid.equipment]
        if not equipment_list:
            return {"error": "No equipment data available"}

        brands = [eq.brand for eq in equipment_list if eq.brand]
        models = [eq.model for eq in equipment_list if eq.model]
        efficiencies = [eq.efficiency_rating for eq in equipment_list if eq.efficiency_rating]
        warranties = [eq.warranty_years for eq in equipment_list if eq.warranty_years]

        analysis = {
            "brands": list(set(brands)) if brands else [],
            "models": list(set(models)) if models else [],
            "efficiency_ratings": list(set(efficiencies)) if efficiencies else [],
            "warranty_years": {
                "min": min(warranties) if warranties else None,
                "max": max(warranties) if warranties else None,
                "all": warranties
            }
        }

        return analysis

    def _generate_recommendations(self) -> List[Dict[str, Any]]:
        """Generate recommendations based on bid comparison."""
        recommendations = []

        if not self.bids:
            return recommendations

        # Cost-based recommendations
        if self.budget:
            affordable_bids = [bid for bid in self.bids 
                             if bid.total_cost and bid.total_cost <= self.budget]
            if affordable_bids:
                recommendations.append({
                    "type": "cost",
                    "priority": "high",
                    "message": f"{len(affordable_bids)} bid(s) within budget of ${self.budget:,.2f}",
                    "contractors": [bid.contractor_name for bid in affordable_bids]
                })
            else:
                bids_with_costs = [bid for bid in self.bids if bid.total_cost]
                if bids_with_costs:
                    lowest_cost = min([bid.total_cost for bid in bids_with_costs])
                    recommendations.append({
                        "type": "cost",
                        "priority": "critical",
                        "message": f"All bids exceed budget. Consider negotiating or adjusting budget.",
                        "lowest_bid": str(lowest_cost)
                    })
                else:
                    recommendations.append({
                        "type": "cost",
                        "priority": "medium",
                        "message": "No cost data available. Please add cost information to bids.",
                    })

        # Equipment quality recommendations
        equipment_bids = [bid for bid in self.bids if bid.equipment]
        if equipment_bids:
            best_warranty = max([bid.equipment.warranty_years for bid in equipment_bids 
                               if bid.equipment and bid.equipment.warranty_years], default=None)
            if best_warranty:
                best_warranty_bids = [bid for bid in equipment_bids 
                                    if bid.equipment and bid.equipment.warranty_years == best_warranty]
                recommendations.append({
                    "type": "equipment",
                    "priority": "medium",
                    "message": f"Best warranty: {best_warranty} years",
                    "contractors": [bid.contractor_name for bid in best_warranty_bids]
                })

        # Value recommendation (cost vs quality)
        if len(self.bids) >= 2:
            sorted_bids = sorted([bid for bid in self.bids if bid.total_cost], 
                               key=lambda b: b.total_cost)
            if sorted_bids:
                recommendations.append({
                    "type": "value",
                    "priority": "high",
                    "message": "Consider balancing cost with equipment quality and warranty",
                    "lowest_cost": sorted_bids[0].contractor_name,
                    "amount": str(sorted_bids[0].total_cost)
                })

        return recommendations

    def generate_report(self, output_path: Optional[Path] = None) -> Path:
        try:
            """
            Generate a comprehensive comparison report.

            Args:
                output_path: Optional path for the report file

            Returns:
                Path to generated report
            """
            if output_path is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = self.data_dir / f"hvac_bid_comparison_report_{timestamp}.json"

            comparison = self.compare_bids()

            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(comparison, f, indent=2, ensure_ascii=False)

            logger.info(f"Generated comparison report: {output_path}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error in generate_report: {e}", exc_info=True)
            raise
    def print_summary(self) -> None:
        """Print a human-readable summary of the comparison."""
        print("\n" + "="*80)
        print("HVAC BID COMPARISON SUMMARY")
        print("="*80)

        if self.budget:
            print(f"\nBudget: ${self.budget:,.2f}")

        print(f"\nTotal Bids: {len(self.bids)}")
        print("\n" + "-"*80)

        for i, bid in enumerate(self.bids, 1):
            print(f"\nBid #{i}: {bid.contractor_name}")
            print(f"  Total Cost: ${bid.total_cost:,.2f}" if bid.total_cost else "  Total Cost: Not specified")

            if bid.equipment:
                print(f"  Equipment: {bid.equipment.brand or 'N/A'} {bid.equipment.model or ''}")
                if bid.equipment.efficiency_rating:
                    print(f"  Efficiency: {bid.equipment.efficiency_rating}")
                if bid.equipment.warranty_years:
                    print(f"  Warranty: {bid.equipment.warranty_years} years")

            if bid.installation_timeline:
                print(f"  Timeline: {bid.installation_timeline}")

        print("\n" + "-"*80)

        comparison = self.compare_bids()

        if "cost_analysis" in comparison:
            cost_analysis = comparison["cost_analysis"]
            if "error" not in cost_analysis:
                print("\nCOST ANALYSIS:")
                print(f"  Lowest: {cost_analysis['lowest_bid']['contractor']} - ${cost_analysis['lowest_bid']['amount']}")
                print(f"  Highest: {cost_analysis['highest_bid']['contractor']} - ${cost_analysis['highest_bid']['amount']}")
                print(f"  Average: ${cost_analysis['average_cost']}")
                print(f"  Range: ${cost_analysis['cost_range']}")

                if cost_analysis.get("within_budget"):
                    print("\n  BIDS WITHIN BUDGET:")
                    for bid_info in cost_analysis["within_budget"]:
                        print(f"    {bid_info['contractor']}: ${bid_info['amount']} "
                              f"(Under by ${bid_info['under_budget_by']})")

        if comparison.get("recommendations"):
            print("\nRECOMMENDATIONS:")
            for rec in comparison["recommendations"]:
                priority_symbol = "🔴" if rec["priority"] == "critical" else \
                                "🟡" if rec["priority"] == "high" else "🟢"
                print(f"  {priority_symbol} [{rec['type'].upper()}] {rec['message']}")

        print("\n" + "="*80 + "\n")


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="HVAC Bid Comparison System")
    parser.add_argument("--project-root", type=Path, 
                       default=Path(__file__).parent.parent.parent,
                       help="Project root directory")
    parser.add_argument("--budget", type=float, default=7000.0,
                       help="Project budget in dollars")
    parser.add_argument("--import-bid", type=Path, action="append",
                       help="Import bid from JSON file (can be used multiple times)")
    parser.add_argument("--load-bids", type=Path,
                       help="Load bids from existing JSON file")
    parser.add_argument("--save-bids", type=str, default="hvac_bids.json",
                       help="Save bids to JSON file")
    parser.add_argument("--generate-report", action="store_true",
                       help="Generate comparison report")
    parser.add_argument("--print-summary", action="store_true",
                       help="Print human-readable summary")

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize comparator
    comparator = HVACBidComparator(args.project_root)
    comparator.set_budget(args.budget)

    # Load existing bids if specified
    if args.load_bids:
        comparator.load_bids(args.load_bids.name if args.load_bids.is_file() else "hvac_bids.json")

    # Import new bids
    if args.import_bid:
        for bid_path in args.import_bid:
            if bid_path.exists():
                comparator.import_bid_from_json(bid_path)
            else:
                logger.error(f"Bid file not found: {bid_path}")

    # Save bids
    if comparator.bids:
        comparator.save_bids(args.save_bids)

    # Generate report
    if args.generate_report:
        comparator.generate_report()

    # Print summary
    if args.print_summary or not args.generate_report:
        comparator.print_summary()


if __name__ == "__main__":


    main()