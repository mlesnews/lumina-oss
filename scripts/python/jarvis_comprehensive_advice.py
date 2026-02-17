#!/usr/bin/env python3
"""
JARVIS Comprehensive Advice System

Provides advice based on all life domains:
- News media and current events
- Business and financial events
- Geopolitical mapping
- Market manipulation detection
- All collected intelligence
- Current events analysis

Tags: #ADVICE #LIFE_DOMAINS #COMPREHENSIVE #INTELLIGENCE_SYNTHESIS @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISAdvice")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISAdvice")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISAdvice")

# Import SYPHON system
try:
    from syphon_system import SYPHONSystem, DataSourceType
    SYPHON_AVAILABLE = True
except ImportError:
    try:
        from scripts.python.syphon_system import SYPHONSystem, DataSourceType
        SYPHON_AVAILABLE = True
    except ImportError:
        SYPHON_AVAILABLE = False
        logger.warning("SYPHON system not available - comprehensive advice will be limited")


class ComprehensiveAdvisor:
    """Comprehensive advice system based on all life domains"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "comprehensive_advice"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.advice_file = self.data_dir / "advice.jsonl"
        self.synthesis_file = self.data_dir / "synthesis.json"

        # Initialize SYPHON system for intelligence extraction
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for comprehensive advice intelligence extraction")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Life domains
        self.life_domains = {
            "news_media": "Current news and media events",
            "business_financial": "Business and financial events",
            "geopolitical": "Geopolitical events (@MONKEYWERKS)",
            "market_manipulation": "Market manipulation detection",
            "cybersecurity": "Cybersecurity threats",
            "domestic_threats": "Domestic security threats",
            "foreign_threats": "Foreign security threats",
            "technology": "Technology developments",
            "social": "Social and cultural events",
            "environmental": "Environmental events",
            "health": "Health and medical events",
            "legal": "Legal and regulatory events",
            "military": "Military and defense events"
        }

    def generate_comprehensive_advice(
        self,
        include_domains: List[str] = None
    ) -> Dict[str, Any]:
        """Generate comprehensive advice based on all life domains"""
        advice = {
            "advice_id": f"advice_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "domains_analyzed": include_domains or list(self.life_domains.keys()),
            "synthesis": {},
            "recommendations": {},
            "threat_assessment": {},
            "opportunities": {},
            "actions": [],
            "status": "generated"
        }

        # Synthesize advice from each domain
        for domain in advice["domains_analyzed"]:
            if domain in self.life_domains:
                domain_advice = self._analyze_domain(domain)
                advice["synthesis"][domain] = domain_advice
                advice["recommendations"][domain] = domain_advice.get("recommendations", [])

        # Use SYPHON to extract intelligence from all domains
        if self.syphon:
            try:
                # Aggregate all domain data for SYPHON extraction
                all_domain_data = json.dumps(advice["synthesis"])
                syphon_result = self._syphon_extract_advice_intelligence(all_domain_data)
                if syphon_result:
                    advice["syphon_intelligence"] = syphon_result
                    # Enhance recommendations with SYPHON-extracted actionable items
                    if syphon_result.get("actionable_items"):
                        for item in syphon_result["actionable_items"]:
                            if item not in advice["actions"]:
                                advice["actions"].append(item)
            except Exception as e:
                logger.warning(f"SYPHON advice extraction failed: {e}")

        # Generate overall recommendations
        advice["actions"] = self._generate_actions(advice)

        # Save advice
        try:
            with open(self.advice_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(advice) + '\n')
        except Exception as e:
            logger.error(f"Error saving advice: {e}")

        logger.info("=" * 80)
        logger.info("💡 COMPREHENSIVE ADVICE")
        logger.info("=" * 80)
        logger.info(f"Domains analyzed: {len(advice['domains_analyzed'])}")
        logger.info(f"Recommendations: {len(advice['actions'])}")
        logger.info("=" * 80)

        return advice

    def _analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Analyze specific life domain"""
        analysis = {
            "domain": domain,
            "description": self.life_domains.get(domain, "Unknown domain"),
            "current_state": "analyzing",
            "trends": [],
            "threats": [],
            "opportunities": [],
            "recommendations": []
        }

        # Domain-specific analysis
        if domain == "geopolitical":
            analysis["monkeywerks_mapping"] = True
            analysis["recommendations"].append("Monitor @MONKEYWERKS geopolitical mapping")

        if domain == "market_manipulation":
            analysis["recommendations"].append("Continue market manipulation detection")
            analysis["recommendations"].append("Report suspicious activity to SEC")

        if domain == "business_financial":
            analysis["recommendations"].append("Monitor financial markets and business events")
            analysis["recommendations"].append("Generate WOPR strategies based on events")

        if domain in ["domestic_threats", "foreign_threats"]:
            analysis["recommendations"].append("Coordinate with law enforcement")
            analysis["recommendations"].append("Use threat response framework")

        return analysis

    def _syphon_extract_advice_intelligence(self, content: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system for comprehensive advice"""
        if not self.syphon:
            return {}

        try:
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=DataSourceType.DOCUMENT,
                source_id=f"advice_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"comprehensive_advice": True, "all_life_domains": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON advice extraction error: {e}")
            return {}

    def _generate_actions(self, advice: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations"""
        actions = [
            "Use SYPHON system to extract intelligence from all communications and data sources",
            "Monitor all life domains continuously",
            "Analyze current events in real-time",
            "Generate WOPR strategies daily",
            "Detect market manipulation",
            "Assess threats using decision trees",
            "Coordinate with law enforcement when needed",
            "Engage legal framework appropriately",
            "Seek judicial board approval when required",
            "React live to events as they unfold",
            "Move forward, upward, and outward",
            "Save mankind from all threats"
        ]

        return actions

    def get_advice_summary(self) -> Dict[str, Any]:
        """Get summary of comprehensive advice"""
        return {
            "life_domains": len(self.life_domains),
            "domains": list(self.life_domains.keys()),
            "capabilities": [
                "SYPHON intelligence extraction from all sources",
                "News media analysis",
                "Business and financial analysis",
                "Geopolitical mapping (@MONKEYWERKS)",
                "Market manipulation detection",
                "Threat assessment",
                "WOPR strategy generation",
                "Live event reaction",
                "Comprehensive advice synthesis"
            ],
            "syphon_enabled": self.syphon is not None
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Comprehensive Advice")
        parser.add_argument("--generate", action="store_true", help="Generate comprehensive advice")
        parser.add_argument("--summary", action="store_true", help="Get advice summary")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        advisor = ComprehensiveAdvisor(project_root)

        if args.generate:
            advice = advisor.generate_comprehensive_advice()
            print("=" * 80)
            print("💡 COMPREHENSIVE ADVICE")
            print("=" * 80)
            print(f"Domains analyzed: {len(advice['domains_analyzed'])}")
            print(f"Actions: {len(advice['actions'])}")
            print("\nKey Recommendations:")
            for action in advice['actions'][:10]:
                print(f"  - {action}")
            print("=" * 80)
            print(json.dumps(advice, indent=2, default=str))

        elif args.summary:
            summary = advisor.get_advice_summary()
            print(json.dumps(summary, indent=2, default=str))

        else:
            # Default: generate advice
            advice = advisor.generate_comprehensive_advice()
            print("=" * 80)
            print("💡 COMPREHENSIVE ADVICE")
            print("=" * 80)
            print(f"Based on all life domains: {len(advice['domains_analyzed'])}")
            print(f"Actionable recommendations: {len(advice['actions'])}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()