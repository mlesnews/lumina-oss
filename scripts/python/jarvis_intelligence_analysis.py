#!/usr/bin/env python3
"""
JARVIS Intelligence Analysis System

Analyze intelligence from all life domains:
- News media and current events
- Business and financial events
- Geopolitical mapping (@MONKEYWERKS)
- Market manipulation detection
- WOPR strategy generation
- Live reaction to events
- Threat assessment

Tags: #INTELLIGENCE #ANALYSIS #CURRENT_EVENTS #GEOPOLITICAL #MARKET_MANIPULATION #WOPR @JARVIS @LUMINA
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
    logger = get_comprehensive_logger("JARVISIntelligence")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISIntelligence")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISIntelligence")

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
        logger.warning("SYPHON system not available - intelligence extraction will be limited")


class IntelligenceAnalyzer:
    """Intelligence analysis system"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "intelligence_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analysis_file = self.data_dir / "intelligence_analysis.jsonl"
        self.current_events_file = self.data_dir / "current_events.jsonl"
        self.wopr_strategies_file = self.data_dir / "wopr_strategies_daily.jsonl"
        self.market_manipulation_file = self.data_dir / "market_manipulation.jsonl"
        self.geopolitical_file = self.data_dir / "geopolitical_mapping.jsonl"

        # Initialize SYPHON system for intelligence extraction
        if SYPHON_AVAILABLE:
            try:
                self.syphon = SYPHONSystem(project_root)
                logger.info("✅ SYPHON system initialized for intelligence extraction")
            except Exception as e:
                logger.warning(f"SYPHON initialization failed: {e}")
                self.syphon = None
        else:
            self.syphon = None

        # Life domains
        self.life_domains = {
            "news_media": "News and media current events",
            "business_financial": "Business and financial events",
            "geopolitical": "Geopolitical events and mapping (@MONKEYWERKS)",
            "market_manipulation": "Market manipulation detection",
            "cybersecurity": "Cybersecurity threats",
            "domestic_threats": "Domestic security threats",
            "foreign_threats": "Foreign security threats",
            "technology": "Technology developments",
            "social": "Social and cultural events",
            "environmental": "Environmental events",
            "health": "Health and medical events"
        }

    def analyze_current_events(
        self,
        domain: str,
        event_data: Dict[str, Any],
        live: bool = True
    ) -> Dict[str, Any]:
        """Analyze current events from any life domain"""
        analysis = {
            "analysis_id": f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "domain": domain,
            "event_data": event_data,
            "live": live,
            "insights": [],
            "threat_indicators": [],
            "opportunities": [],
            "recommendations": [],
            "wopr_strategies": [],
            "syphon_intelligence": {},
            "status": "analyzed"
        }

        # Use SYPHON to extract intelligence from event data
        if self.syphon and event_data:
            try:
                # Extract intelligence using SYPHON
                event_content = json.dumps(event_data)
                syphon_result = self._syphon_extract_intelligence(event_content, domain)
                if syphon_result:
                    analysis["syphon_intelligence"] = syphon_result
                    # Add actionable items from SYPHON to recommendations
                    if syphon_result.get("actionable_items"):
                        analysis["recommendations"].extend(syphon_result["actionable_items"])
                    if syphon_result.get("intelligence"):
                        analysis["insights"].extend([item.get("summary", "") for item in syphon_result["intelligence"]])
            except Exception as e:
                logger.warning(f"SYPHON extraction failed: {e}")

        # Domain-specific analysis
        if domain == "geopolitical":
            analysis["geopolitical_mapping"] = self._analyze_geopolitical(event_data)
            analysis["monkeywerks"] = True  # @MONKEYWERKS mapping

        if domain == "business_financial":
            analysis["market_analysis"] = self._analyze_market(event_data)
            analysis["manipulation_detection"] = self._detect_market_manipulation(event_data)

        if domain == "news_media":
            analysis["media_analysis"] = self._analyze_media(event_data)

        # Generate insights
        analysis["insights"] = self._generate_insights(analysis)

        # Detect threats
        analysis["threat_indicators"] = self._detect_threats(analysis)

        # Generate WOPR strategies
        if analysis["threat_indicators"]:
            analysis["wopr_strategies"] = self._generate_wopr_strategies(analysis)

        # Save analysis
        try:
            with open(self.analysis_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(analysis) + '\n')

            with open(self.current_events_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps({
                    "event_id": analysis["analysis_id"],
                    "timestamp": analysis["timestamp"],
                    "domain": domain,
                    "live": live
                }) + '\n')
        except Exception as e:
            logger.error(f"Error saving analysis: {e}")

        logger.info(f"📊 Current events analyzed: {domain}")
        logger.info(f"   Live: {live}")
        logger.info(f"   Insights: {len(analysis['insights'])}")
        logger.info(f"   Threats: {len(analysis['threat_indicators'])}")

        return analysis

    def _analyze_geopolitical(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze geopolitical events (@MONKEYWERKS)"""
        return {
            "mapping": "@MONKEYWERKS",
            "targeting": "Geopolitical targeting analysis",
            "actors": event_data.get("actors", []),
            "regions": event_data.get("regions", []),
            "conflicts": event_data.get("conflicts", []),
            "alliances": event_data.get("alliances", [])
        }

    def _analyze_market(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze market events"""
        return {
            "market_conditions": event_data.get("conditions", {}),
            "volatility": event_data.get("volatility", 0),
            "trends": event_data.get("trends", []),
            "indicators": event_data.get("indicators", [])
        }

    def _detect_market_manipulation(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Detect market manipulation"""
        manipulation = {
            "detected": False,
            "indicators": [],
            "confidence": 0.0,
            "recommendations": []
        }

        # Detection logic (simplified)
        if event_data.get("unusual_volume"):
            manipulation["detected"] = True
            manipulation["indicators"].append("Unusual trading volume")
            manipulation["confidence"] += 0.3

        if event_data.get("price_anomaly"):
            manipulation["detected"] = True
            manipulation["indicators"].append("Price anomaly")
            manipulation["confidence"] += 0.4

        if manipulation["detected"]:
            manipulation["recommendations"].append("Report to SEC")
            manipulation["recommendations"].append("Generate WOPR strategy")

        return manipulation

    def _analyze_media(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze media events"""
        return {
            "sources": event_data.get("sources", []),
            "narrative": event_data.get("narrative", ""),
            "bias_indicators": event_data.get("bias", []),
            "fact_check": event_data.get("fact_check", {})
        }

    def _generate_insights(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate insights from analysis"""
        insights = []

        if analysis.get("threat_indicators"):
            insights.append("Threat indicators detected - escalation recommended")

        if analysis.get("geopolitical_mapping"):
            insights.append("Geopolitical mapping updated (@MONKEYWERKS)")

        if analysis.get("market_manipulation", {}).get("detected"):
            insights.append("Market manipulation detected - investigation recommended")

        return insights

    def _detect_threats(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        try:
            """Detect threats from analysis"""
            threats = []

            # Check for threat indicators in event data
            event_data = analysis.get("event_data", {})

            threat_keywords = ["attack", "threat", "danger", "crisis", "emergency", "violence", "terror"]
            event_text = json.dumps(event_data).lower()

            for keyword in threat_keywords:
                if keyword in event_text:
                    threats.append({
                        "type": "keyword_match",
                        "keyword": keyword,
                        "severity": "medium"
                    })

            return threats

        except Exception as e:
            self.logger.error(f"Error in _detect_threats: {e}", exc_info=True)
            raise
    def _generate_wopr_strategies(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate WOPR strategies based on analysis"""
        strategies = []

        for threat in analysis.get("threat_indicators", []):
            strategy = {
                "strategy_id": f"wopr_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "timestamp": datetime.now().isoformat(),
                "based_on": threat,
                "type": "response_strategy",
                "priority": "high",
                "actions": [
                    "Assess threat level",
                    "Escalate through decision trees",
                    "Coordinate with law enforcement if needed",
                    "Generate actionable response"
                ],
                "live_reaction": True
            }
            strategies.append(strategy)

        return strategies

    def _syphon_extract_intelligence(self, content: str, source_type: str) -> Dict[str, Any]:
        """Extract intelligence using SYPHON system"""
        if not self.syphon:
            return {}

        try:
            # Determine data source type
            ds_type = DataSourceType.OTHER
            if "email" in source_type.lower():
                ds_type = DataSourceType.EMAIL
            elif "sms" in source_type.lower() or "text" in source_type.lower():
                ds_type = DataSourceType.SMS
            elif "social" in source_type.lower():
                ds_type = DataSourceType.SOCIAL
            elif "document" in source_type.lower():
                ds_type = DataSourceType.DOCUMENT

            # Use SYPHON to extract intelligence
            syphon_data = self.syphon.syphon_generic(
                content=content,
                source_type=ds_type,
                source_id=f"intelligence_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                metadata={"domain": source_type, "intelligence_analysis": True}
            )

            return {
                "actionable_items": syphon_data.actionable_items,
                "tasks": syphon_data.tasks,
                "decisions": syphon_data.decisions,
                "intelligence": [item for item in syphon_data.intelligence]
            }
        except Exception as e:
            logger.error(f"SYPHON extraction error: {e}")
            return {}

    def generate_daily_wopr_strategies(self) -> Dict[str, Any]:
        """Generate tens of thousands of WOPR strategies daily based on current events"""
        daily_strategies = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "timestamp": datetime.now().isoformat(),
            "strategies_generated": 0,
            "based_on": "current_events",
            "live_reaction": True,
            "syphon_enabled": self.syphon is not None,
            "strategies": []
        }

        # Use SYPHON to extract intelligence from all sources before generating strategies
        if self.syphon:
            try:
                # Load recent SYPHON data for strategy generation
                syphon_intelligence = self._load_syphon_intelligence_for_strategies()
                if syphon_intelligence:
                    daily_strategies["syphon_intelligence_count"] = len(syphon_intelligence)
                    logger.info(f"📊 Using {len(syphon_intelligence)} SYPHON intelligence items for strategy generation")
            except Exception as e:
                logger.warning(f"Error loading SYPHON intelligence: {e}")

        # Generate strategies (in production, this would analyze all intelligence batches)
        # For now, generate sample strategies
        for i in range(100):  # Sample - would be tens of thousands
            strategy = {
                "strategy_id": f"wopr_daily_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}",
                "timestamp": datetime.now().isoformat(),
                "type": "daily_strategy",
                "based_on": "current_events_analysis",
                "syphon_informed": self.syphon is not None,
                "priority": "medium",
                "actions": ["Monitor", "Analyze", "Respond", "Use SYPHON for intelligence extraction"],
                "live": True
            }
            daily_strategies["strategies"].append(strategy)
            daily_strategies["strategies_generated"] += 1

        # Save daily strategies
        try:
            with open(self.wopr_strategies_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(daily_strategies) + '\n')
        except Exception as e:
            logger.error(f"Error saving daily strategies: {e}")

        logger.info(f"🎯 Daily WOPR strategies generated: {daily_strategies['strategies_generated']}")
        if self.syphon:
            logger.info(f"   SYPHON-enabled: Intelligence extraction integrated")

        return daily_strategies

    def _load_syphon_intelligence_for_strategies(self) -> List[Dict[str, Any]]:
        """Load recent SYPHON intelligence for strategy generation"""
        if not self.syphon:
            return []

        try:
            # Get recent SYPHON data (last 24 hours)
            recent_data = []
            for item in self.syphon.extracted_data:
                if (datetime.now() - item.extracted_at).total_seconds() < 86400:  # 24 hours
                    recent_data.append(item.to_dict())
            return recent_data
        except Exception as e:
            logger.error(f"Error loading SYPHON intelligence: {e}")
            return []


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Intelligence Analysis")
        parser.add_argument("--analyze", type=str, metavar="DOMAIN", help="Analyze current events from domain")
        parser.add_argument("--generate-daily", action="store_true", help="Generate daily WOPR strategies")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        analyzer = IntelligenceAnalyzer(project_root)

        if args.analyze:
            event_data = {"description": "Sample event", "source": "test"}
            analysis = analyzer.analyze_current_events(args.analyze, event_data)
            print("=" * 80)
            print("📊 INTELLIGENCE ANALYSIS")
            print("=" * 80)
            print(f"Domain: {analysis['domain']}")
            print(f"Insights: {len(analysis['insights'])}")
            print(f"Threats: {len(analysis['threat_indicators'])}")
            print(f"WOPR Strategies: {len(analysis['wopr_strategies'])}")
            print("=" * 80)
            print(json.dumps(analysis, indent=2, default=str))

        elif args.generate_daily:
            strategies = analyzer.generate_daily_wopr_strategies()
            print("=" * 80)
            print("🎯 DAILY WOPR STRATEGIES")
            print("=" * 80)
            print(f"Date: {strategies['date']}")
            print(f"Strategies generated: {strategies['strategies_generated']}")
            print(f"Based on: {strategies['based_on']}")
            print(f"Live reaction: {strategies['live_reaction']}")
            print("=" * 80)
            print(json.dumps(strategies, indent=2, default=str))

        else:
            print("=" * 80)
            print("📊 JARVIS INTELLIGENCE ANALYSIS")
            print("=" * 80)
            print("Use --analyze DOMAIN to analyze current events")
            print("Use --generate-daily to generate daily WOPR strategies")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()