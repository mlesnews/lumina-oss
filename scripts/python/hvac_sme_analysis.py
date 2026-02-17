"""
HVAC SME Analysis Tool
Analyze HVAC bids with expert HVAC knowledge and provide recommendations.

#JARVIS #LUMINA #HVAC #SME #ANALYSIS #RECOMMENDATIONS
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("HVACSMEAnalysis")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("HVACSMEAnalysis")

from scripts.python.hvac_bid_extractor import BidExtractor
from scripts.python.hvac_bid_comparison import HVACBidComparator


@dataclass
class HVACSMERecommendation:
    """HVAC SME recommendation."""
    category: str  # "equipment", "cost", "warranty", "timeline", "overall"
    priority: str  # "critical", "high", "medium", "low"
    recommendation: str
    reasoning: str
    cost_impact: Optional[str] = None
    risk_level: Optional[str] = None


class HVACSMEAnalyzer:
    """
    HVAC Subject Matter Expert Analyzer

    Provides expert analysis and recommendations for HVAC bids.
    """

    def __init__(self, project_root: Path):
        """
        Initialize HVAC SME Analyzer.

        Args:
            project_root: Project root directory
        """
        self.project_root = Path(project_root)
        self.bid_extractor = BidExtractor(project_root)
        self.bid_comparator = HVACBidComparator(project_root)
        self.bid_comparator.set_budget(20000)  # $20,000 budget

        # HVAC Expert Knowledge Base
        self.expert_knowledge = {
            "efficiency_ratings": {
                "minimum_acceptable": 80,  # AFUE for furnaces
                "good": 90,
                "excellent": 95,
                "premium": 98
            },
            "warranty_standards": {
                "parts": {"minimum": 5, "good": 10, "excellent": 15},
                "labor": {"minimum": 1, "good": 2, "excellent": 5}
            },
            "cost_benchmarks": {
                "oil_to_gas_conversion": {"low": 8000, "mid": 12000, "high": 18000},
                "furnace_only": {"low": 3000, "mid": 6000, "high": 10000},
                "furnace_ac_combo": {"low": 8000, "mid": 12000, "high": 20000}
            },
            "equipment_brands": {
                "tier_1": ["Carrier", "Trane", "Lennox", "Rheem", "Goodman"],
                "tier_2": ["York", "Bryant", "American Standard", "Amana"],
                "value": ["Goodman", "Amana", "Rheem"]
            }
        }

    def analyze_bid(self, bid_data: Dict[str, Any], contractor_name: str = "") -> Dict[str, Any]:
        """
        Analyze a single HVAC bid with expert knowledge.

        Args:
            bid_data: Bid data dictionary
            contractor_name: Name of contractor

        Returns:
            Comprehensive analysis with recommendations
        """
        logger.info("="*80)
        logger.info("HVAC SME ANALYSIS")
        logger.info("="*80)
        logger.info(f"Contractor: {contractor_name or bid_data.get('contractor_name', 'Unknown')}")
        logger.info("")

        analysis = {
            "contractor": contractor_name or bid_data.get("contractor_name", "Unknown"),
            "analysis_date": datetime.now().isoformat(),
            "bid_summary": self._summarize_bid(bid_data),
            "cost_analysis": self._analyze_costs(bid_data),
            "equipment_analysis": self._analyze_equipment(bid_data),
            "warranty_analysis": self._analyze_warranty(bid_data),
            "timeline_analysis": self._analyze_timeline(bid_data),
            "recommendations": [],
            "overall_assessment": "",
            "risk_assessment": {}
        }

        # Generate recommendations
        recommendations = self._generate_recommendations(bid_data)
        analysis["recommendations"] = recommendations

        # Overall assessment
        analysis["overall_assessment"] = self._generate_overall_assessment(bid_data, recommendations)

        # Risk assessment
        analysis["risk_assessment"] = self._assess_risks(bid_data)

        return analysis

    def _summarize_bid(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Summarize the bid."""
        total_cost = bid_data.get("total_cost")
        equipment = bid_data.get("equipment", {})

        summary = {
            "total_cost": f"${total_cost:,.2f}" if total_cost else "Not specified",
            "equipment_brand": equipment.get("brand", "Not specified"),
            "equipment_model": equipment.get("model", "Not specified"),
            "efficiency_rating": equipment.get("efficiency_rating", "Not specified"),
            "warranty_years": equipment.get("warranty_years", "Not specified"),
            "installation_timeline": bid_data.get("installation_timeline", "Not specified"),
            "key_points": []
        }

        # Extract key points
        if total_cost:
            summary["key_points"].append(f"Total Cost: ${total_cost:,.2f}")
        if equipment.get("brand"):
            summary["key_points"].append(f"Equipment: {equipment.get('brand')} {equipment.get('model', '')}")
        if equipment.get("efficiency_rating"):
            summary["key_points"].append(f"Efficiency: {equipment.get('efficiency_rating')}")

        return summary

    def _analyze_costs(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze costs with expert knowledge."""
        total_cost = bid_data.get("total_cost")
        equipment_cost = bid_data.get("equipment_cost")
        labor_cost = bid_data.get("labor_cost")

        analysis = {
            "total_cost": total_cost,
            "cost_breakdown": {
                "equipment": equipment_cost,
                "labor": labor_cost,
                "permits": bid_data.get("permit_cost"),
                "disposal": bid_data.get("disposal_cost")
            },
            "cost_assessment": "",
            "budget_comparison": "",
            "value_assessment": ""
        }

        if total_cost:
            # Compare to budget
            budget = 20000
            if total_cost <= budget:
                analysis["budget_comparison"] = f"✅ Within budget (${budget:,.2f})"
            elif total_cost <= budget * 1.1:
                analysis["budget_comparison"] = f"⚠️  Slightly over budget (${total_cost - budget:,.2f} over)"
            else:
                analysis["budget_comparison"] = f"❌ Significantly over budget (${total_cost - budget:,.2f} over)"

            # Compare to benchmarks
            benchmarks = self.expert_knowledge["cost_benchmarks"]["furnace_ac_combo"]
            if total_cost <= benchmarks["mid"]:
                analysis["cost_assessment"] = "✅ Competitive pricing"
            elif total_cost <= benchmarks["high"]:
                analysis["cost_assessment"] = "⚠️  Premium pricing - ensure value"
            else:
                analysis["cost_assessment"] = "❌ High pricing - negotiate or compare"

        return analysis

    def _analyze_equipment(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze equipment with expert knowledge."""
        equipment = bid_data.get("equipment", {})
        brand = equipment.get("brand", "")
        model = equipment.get("model", "")
        efficiency = equipment.get("efficiency_rating", "")
        capacity = equipment.get("capacity", "")

        analysis = {
            "brand": brand,
            "model": model,
            "efficiency_rating": efficiency,
            "capacity": capacity,
            "brand_tier": "",
            "efficiency_assessment": "",
            "equipment_quality": ""
        }

        # Brand tier assessment
        if brand:
            brand_lower = brand.lower()
            if any(tier1.lower() in brand_lower for tier1 in self.expert_knowledge["equipment_brands"]["tier_1"]):
                analysis["brand_tier"] = "Tier 1 - Premium brand"
                analysis["equipment_quality"] = "✅ High quality, reliable"
            elif any(tier2.lower() in brand_lower for tier2 in self.expert_knowledge["equipment_brands"]["tier_2"]):
                analysis["brand_tier"] = "Tier 2 - Good brand"
                analysis["equipment_quality"] = "✅ Good quality"
            elif any(value.lower() in brand_lower for value in self.expert_knowledge["equipment_brands"]["value"]):
                analysis["brand_tier"] = "Value brand"
                analysis["equipment_quality"] = "⚠️  Value brand - verify quality"
            else:
                analysis["brand_tier"] = "Unknown brand"
                analysis["equipment_quality"] = "⚠️  Research brand reputation"

        # Efficiency assessment
        if efficiency:
            try:
                eff_num = float(efficiency.replace("%", "").replace("AFUE", "").strip())
                if eff_num >= 95:
                    analysis["efficiency_assessment"] = "✅ Excellent efficiency (95%+)"
                elif eff_num >= 90:
                    analysis["efficiency_assessment"] = "✅ Good efficiency (90-94%)"
                elif eff_num >= 80:
                    analysis["efficiency_assessment"] = "⚠️  Acceptable efficiency (80-89%)"
                else:
                    analysis["efficiency_assessment"] = "❌ Low efficiency (<80%) - not recommended"
            except:
                analysis["efficiency_assessment"] = "⚠️  Efficiency rating unclear"

        return analysis

    def _analyze_warranty(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze warranty with expert knowledge."""
        equipment = bid_data.get("equipment", {})
        warranty_years = equipment.get("warranty_years")
        warranty_info = bid_data.get("warranty_info", "")

        analysis = {
            "warranty_years": warranty_years,
            "warranty_info": warranty_info,
            "parts_warranty": "",
            "labor_warranty": "",
            "warranty_assessment": ""
        }

        if warranty_years:
            if warranty_years >= 10:
                analysis["parts_warranty"] = "✅ Excellent parts warranty (10+ years)"
            elif warranty_years >= 5:
                analysis["parts_warranty"] = "✅ Good parts warranty (5-9 years)"
            else:
                analysis["parts_warranty"] = "⚠️  Short parts warranty (<5 years)"

        # Check warranty info text
        if warranty_info:
            if "labor" in warranty_info.lower():
                if "2" in warranty_info or "two" in warranty_info.lower():
                    analysis["labor_warranty"] = "✅ 2+ year labor warranty"
                elif "1" in warranty_info or "one" in warranty_info.lower():
                    analysis["labor_warranty"] = "⚠️ 1 year labor warranty (standard minimum)"
                else:
                    analysis["labor_warranty"] = "⚠️  Labor warranty unclear"

        return analysis

    def _analyze_timeline(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze installation timeline."""
        timeline = bid_data.get("installation_timeline", "")

        analysis = {
            "timeline": timeline,
            "timeline_assessment": ""
        }

        if timeline:
            timeline_lower = timeline.lower()
            if "day" in timeline_lower or "week" in timeline_lower:
                if "1" in timeline or "one" in timeline_lower:
                    analysis["timeline_assessment"] = "✅ Quick installation timeline"
                elif "2" in timeline or "two" in timeline_lower:
                    analysis["timeline_assessment"] = "✅ Reasonable timeline (2 days/weeks)"
                else:
                    analysis["timeline_assessment"] = "⚠️  Verify timeline is realistic"
            else:
                analysis["timeline_assessment"] = "⚠️  Timeline unclear - request clarification"

        return analysis

    def _generate_recommendations(self, bid_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate expert recommendations."""
        recommendations = []

        total_cost = bid_data.get("total_cost")
        equipment = bid_data.get("equipment", {})

        # Cost recommendations
        if total_cost:
            if total_cost > 20000:
                recommendations.append({
                    "category": "cost",
                    "priority": "high",
                    "recommendation": "Negotiate price or request itemized breakdown",
                    "reasoning": f"Bid exceeds budget by ${total_cost - 20000:,.2f}",
                    "cost_impact": "Could save $2,000-$5,000",
                    "risk_level": "medium"
                })
            elif total_cost < 15000:
                recommendations.append({
                    "category": "cost",
                    "priority": "medium",
                    "recommendation": "Verify equipment quality matches low price",
                    "reasoning": "Price seems low - ensure not cutting corners",
                    "cost_impact": "None",
                    "risk_level": "high"
                })

        # Equipment recommendations
        brand = equipment.get("brand", "")
        efficiency = equipment.get("efficiency_rating", "")

        if brand:
            if brand.lower() not in [b.lower() for b in self.expert_knowledge["equipment_brands"]["tier_1"] + 
                                     self.expert_knowledge["equipment_brands"]["tier_2"]]:
                recommendations.append({
                    "category": "equipment",
                    "priority": "medium",
                    "recommendation": "Research brand reputation and reliability",
                    "reasoning": f"Brand '{brand}' not in known tier 1/2 list",
                    "cost_impact": "None",
                    "risk_level": "medium"
                })

        if efficiency:
            try:
                eff_num = float(efficiency.replace("%", "").replace("AFUE", "").strip())
                if eff_num < 90:
                    recommendations.append({
                        "category": "equipment",
                        "priority": "high",
                        "recommendation": "Consider higher efficiency model for long-term savings",
                        "reasoning": f"Current efficiency ({eff_num}%) is below optimal (90%+)",
                        "cost_impact": "May cost $1,000-$3,000 more but saves on fuel costs",
                        "risk_level": "low"
                    })
            except:
                pass

        # Warranty recommendations
        warranty_years = equipment.get("warranty_years")
        if warranty_years and warranty_years < 10:
            recommendations.append({
                "category": "warranty",
                "priority": "medium",
                "recommendation": "Request extended warranty or negotiate warranty terms",
                "reasoning": f"Current warranty ({warranty_years} years) is below excellent standard (10+ years)",
                "cost_impact": "May cost $500-$1,500 for extended warranty",
                "risk_level": "low"
            })

        return recommendations

    def _generate_overall_assessment(self, bid_data: Dict[str, Any], recommendations: List[Dict]) -> str:
        """Generate overall assessment."""
        total_cost = bid_data.get("total_cost")
        equipment = bid_data.get("equipment", {})

        assessment_parts = []

        # Cost assessment
        if total_cost:
            if total_cost <= 20000:
                assessment_parts.append("✅ Cost is within budget")
            else:
                assessment_parts.append("⚠️  Cost exceeds budget")

        # Equipment assessment
        brand = equipment.get("brand", "")
        efficiency = equipment.get("efficiency_rating", "")

        if brand:
            assessment_parts.append(f"Equipment: {brand}")
        if efficiency:
            assessment_parts.append(f"Efficiency: {efficiency}")

        # Recommendation summary
        critical_recs = [r for r in recommendations if r.get("priority") == "critical"]
        high_recs = [r for r in recommendations if r.get("priority") == "high"]

        if critical_recs:
            assessment_parts.append(f"⚠️  {len(critical_recs)} critical recommendations")
        if high_recs:
            assessment_parts.append(f"⚠️  {len(high_recs)} high-priority recommendations")

        if not assessment_parts:
            return "✅ Bid appears reasonable - review details carefully"

        return " | ".join(assessment_parts)

    def _assess_risks(self, bid_data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risks in the bid."""
        risks = {
            "cost_risk": "low",
            "equipment_risk": "low",
            "warranty_risk": "low",
            "timeline_risk": "low",
            "overall_risk": "low"
        }

        total_cost = bid_data.get("total_cost")
        equipment = bid_data.get("equipment", {})

        # Cost risk
        if total_cost:
            if total_cost > 20000:
                risks["cost_risk"] = "high"
            elif total_cost < 10000:
                risks["cost_risk"] = "medium"  # Too low might indicate issues

        # Equipment risk
        brand = equipment.get("brand", "")
        if brand and brand.lower() not in [b.lower() for b in 
                                           self.expert_knowledge["equipment_brands"]["tier_1"] + 
                                           self.expert_knowledge["equipment_brands"]["tier_2"]]:
            risks["equipment_risk"] = "medium"

        efficiency = equipment.get("efficiency_rating", "")
        if efficiency:
            try:
                eff_num = float(efficiency.replace("%", "").replace("AFUE", "").strip())
                if eff_num < 80:
                    risks["equipment_risk"] = "high"
            except:
                pass

        # Warranty risk
        warranty_years = equipment.get("warranty_years")
        if warranty_years and warranty_years < 5:
            risks["warranty_risk"] = "medium"

        # Overall risk
        high_risks = [k for k, v in risks.items() if v == "high" and k != "overall_risk"]
        medium_risks = [k for k, v in risks.items() if v == "medium" and k != "overall_risk"]

        if high_risks:
            risks["overall_risk"] = "high"
        elif medium_risks:
            risks["overall_risk"] = "medium"
        else:
            risks["overall_risk"] = "low"

        return risks

    def analyze_bid_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Analyze a bid file (PDF, DOCX, TXT).

        Args:
            file_path: Path to bid file

        Returns:
            Analysis results
        """
        logger.info(f"Extracting bid from: {file_path}")

        # Extract bid data
        extracted = self.bid_extractor.extract_from_file(file_path)

        if not extracted:
            return {"error": "Failed to extract bid data from file"}

        # Analyze
        contractor_name = extracted.get("contractor_name", "")
        analysis = self.analyze_bid(extracted, contractor_name)

        return analysis

    def print_analysis(self, analysis: Dict[str, Any]):
        """Print formatted analysis."""
        print("\n" + "="*80)
        print("HVAC SME ANALYSIS REPORT")
        print("="*80)
        print(f"Contractor: {analysis['contractor']}")
        print(f"Analysis Date: {analysis['analysis_date']}")
        print()

        # Bid Summary
        print("BID SUMMARY")
        print("-" * 80)
        summary = analysis['bid_summary']
        print(f"Total Cost: {summary['total_cost']}")
        print(f"Equipment: {summary['equipment_brand']} {summary['equipment_model']}")
        print(f"Efficiency: {summary['efficiency_rating']}")
        print(f"Warranty: {summary['warranty_years']} years")
        print(f"Timeline: {summary['installation_timeline']}")
        print()

        # Cost Analysis
        print("COST ANALYSIS")
        print("-" * 80)
        cost_analysis = analysis['cost_analysis']
        if cost_analysis.get('total_cost'):
            print(f"Total Cost: ${cost_analysis['total_cost']:,.2f}")
            print(f"Assessment: {cost_analysis.get('cost_assessment', 'N/A')}")
            print(f"Budget: {cost_analysis.get('budget_comparison', 'N/A')}")
        print()

        # Equipment Analysis
        print("EQUIPMENT ANALYSIS")
        print("-" * 80)
        equip_analysis = analysis['equipment_analysis']
        print(f"Brand: {equip_analysis.get('brand', 'N/A')}")
        print(f"Brand Tier: {equip_analysis.get('brand_tier', 'N/A')}")
        print(f"Efficiency: {equip_analysis.get('efficiency_assessment', 'N/A')}")
        print(f"Quality: {equip_analysis.get('equipment_quality', 'N/A')}")
        print()

        # Recommendations
        print("RECOMMENDATIONS")
        print("-" * 80)
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"{i}. [{rec['priority'].upper()}] {rec['category'].upper()}")
            print(f"   {rec['recommendation']}")
            print(f"   Reasoning: {rec['reasoning']}")
            if rec.get('cost_impact'):
                print(f"   Cost Impact: {rec['cost_impact']}")
            print()

        # Overall Assessment
        print("OVERALL ASSESSMENT")
        print("-" * 80)
        print(analysis['overall_assessment'])
        print()

        # Risk Assessment
        print("RISK ASSESSMENT")
        print("-" * 80)
        risks = analysis['risk_assessment']
        for risk_type, risk_level in risks.items():
            if risk_type != "overall_risk":
                print(f"{risk_type.replace('_', ' ').title()}: {risk_level.upper()}")
        print(f"\nOverall Risk: {risks.get('overall_risk', 'unknown').upper()}")
        print()


def main():
    try:
        """Main function."""
        import argparse

        parser = argparse.ArgumentParser(description="HVAC SME Analysis")
        parser.add_argument("--project-root", type=Path, default=Path(__file__).parent.parent.parent)
        parser.add_argument("--file", type=Path, help="Bid file to analyze (PDF, DOCX, TXT)")
        parser.add_argument("--json-file", type=Path, help="JSON bid file to analyze")
        parser.add_argument("--contractor", type=str, default="Brian Fletcher", help="Contractor name")

        args = parser.parse_args()

        analyzer = HVACSMEAnalyzer(args.project_root)

        if args.file:
            # Analyze from file
            analysis = analyzer.analyze_bid_file(args.file)
            analyzer.print_analysis(analysis)

            # Save analysis
            output_file = args.project_root / "data" / "hvac_bids" / f"sme_analysis_{args.contractor.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"📄 Analysis saved to: {output_file}")

        elif args.json_file:
            # Analyze from JSON
            with open(args.json_file, 'r') as f:
                bid_data = json.load(f)
            analysis = analyzer.analyze_bid(bid_data, args.contractor)
            analyzer.print_analysis(analysis)

            # Save analysis
            output_file = args.project_root / "data" / "hvac_bids" / f"sme_analysis_{args.contractor.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w') as f:
                json.dump(analysis, f, indent=2, ensure_ascii=False)
            print(f"📄 Analysis saved to: {output_file}")

        else:
            # Try to find and analyze Brian's bid
            bid_file = args.project_root / "data" / "hvac_bids" / "fletchers_plumbing_bid.json"
            if bid_file.exists():
                with open(bid_file, 'r') as f:
                    bid_data = json.load(f)

                if bid_data.get("total_cost") or bid_data.get("equipment", {}).get("brand"):
                    analysis = analyzer.analyze_bid(bid_data, "Brian Fletcher - Fletcher's Heating & Plumbing")
                    analyzer.print_analysis(analysis)
                else:
                    print("⚠️  Brian's bid template is empty - need actual bid data")
                    print("\nPlease provide:")
                    print("  1. The bid file (PDF/DOCX) from Brian's email")
                    print("  2. Or the file path to analyze")
                    print("\nUsage:")
                    print("  python scripts/python/hvac_sme_analysis.py --file <path_to_bid_file>")
            else:
                parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()