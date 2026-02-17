#!/usr/bin/env python3
"""
JARVIS Creativity Analysis System

Polymath version of "Who Moved My Cheese?" - understanding change and adaptation.
Analyzes creativity patterns - maps ebb and flow chronologically.
HR assessment: "What would you do with an individual like that?"
Self-discovery for people who don't know themselves.
JARVIS as teacher, mentor, instructor, guide.

Chief view: #Merit (like Elon said)

Tags: #CREATIVITY #MERIT #SELF_DISCOVERY #MENTOR #TEACHER #HR_ASSESSMENT @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from collections import defaultdict

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger, setup_logging
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    setup_logging = lambda: None

logger = get_logger("JARVISCreativityAnalysis")


class CreativityAnalyzer:
    """Analyze creativity patterns - ebb and flow"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "creativity_analysis"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.creativity_timeline = []
        self.ebb_flow_patterns = {}

    def analyze_chronological_creativity(self, work_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze creativity chronologically from beginning to today"""
        logger.info("=" * 80)
        logger.info("🎨 CREATIVITY ANALYSIS - CHRONOLOGICAL MAPPING")
        logger.info("=" * 80)
        logger.info("")

        # Sort by date
        sorted_work = sorted(work_history, key=lambda x: x.get("date", datetime.now()))

        # Analyze patterns
        creativity_scores = []
        periods = []

        for i, work_item in enumerate(sorted_work):
            creativity_score = self._calculate_creativity_score(work_item)
            creativity_scores.append(creativity_score)

            period = {
                "date": work_item.get("date", datetime.now()),
                "work": work_item.get("description", ""),
                "creativity_score": creativity_score,
                "creativity_level": self._get_creativity_level(creativity_score)
            }
            periods.append(period)

        # Identify ebb and flow
        ebb_flow = self._identify_ebb_flow(creativity_scores, periods)

        analysis = {
            "timestamp": datetime.now().isoformat(),
            "total_periods": len(periods),
            "chronological_timeline": periods,
            "ebb_flow_patterns": ebb_flow,
            "creativity_trends": self._analyze_trends(creativity_scores),
            "peak_creativity_periods": self._identify_peaks(periods),
            "low_creativity_periods": self._identify_lows(periods),
            "insights": self._generate_insights(ebb_flow, periods)
        }

        logger.info(f"📊 Analyzed {len(periods)} periods")
        logger.info(f"🌊 Ebb and flow patterns identified")
        logger.info("")

        return analysis

    def _calculate_creativity_score(self, work_item: Dict[str, Any]) -> float:
        """Calculate creativity score for work item"""
        score = 0.0

        # Innovation factor
        if work_item.get("innovative", False):
            score += 30.0

        # Complexity factor
        complexity = work_item.get("complexity", 0)
        score += min(complexity * 10, 30.0)

        # Originality factor
        if work_item.get("original", False):
            score += 20.0

        # Impact factor
        impact = work_item.get("impact", 0)
        score += min(impact * 10, 20.0)

        return min(score, 100.0)

    def _get_creativity_level(self, score: float) -> str:
        """Get creativity level from score"""
        if score >= 80:
            return "PEAK"
        elif score >= 60:
            return "HIGH"
        elif score >= 40:
            return "MODERATE"
        elif score >= 20:
            return "LOW"
        else:
            return "EBB"

    def _identify_ebb_flow(self, scores: List[float], periods: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Identify ebb and flow patterns"""
        if len(scores) < 2:
            return {"pattern": "INSUFFICIENT_DATA"}

        # Calculate flow direction
        flow_directions = []
        for i in range(1, len(scores)):
            if scores[i] > scores[i-1]:
                flow_directions.append("RISING")
            elif scores[i] < scores[i-1]:
                flow_directions.append("EBBING")
            else:
                flow_directions.append("CALM")

        # Identify patterns
        patterns = {
            "overall_trend": "RISING" if scores[-1] > scores[0] else "EBBING" if scores[-1] < scores[0] else "CALM",
            "flow_directions": flow_directions,
            "average_score": sum(scores) / len(scores),
            "peak_score": max(scores),
            "low_score": min(scores),
            "volatility": self._calculate_volatility(scores)
        }

        return patterns

    def _calculate_volatility(self, scores: List[float]) -> float:
        """Calculate volatility of creativity scores"""
        if len(scores) < 2:
            return 0.0

        mean = sum(scores) / len(scores)
        variance = sum((x - mean) ** 2 for x in scores) / len(scores)
        return variance ** 0.5

    def _analyze_trends(self, scores: List[float]) -> Dict[str, Any]:
        """Analyze creativity trends"""
        if len(scores) < 2:
            return {"trend": "INSUFFICIENT_DATA"}

        # Recent trend (last 25% of data)
        recent_start = int(len(scores) * 0.75)
        recent_scores = scores[recent_start:]
        recent_trend = "RISING" if recent_scores[-1] > recent_scores[0] else "EBBING" if recent_scores[-1] < recent_scores[0] else "CALM"

        return {
            "overall_trend": "RISING" if scores[-1] > scores[0] else "EBBING" if scores[-1] < scores[0] else "CALM",
            "recent_trend": recent_trend,
            "trend_strength": abs(scores[-1] - scores[0]) / 100.0
        }

    def _identify_peaks(self, periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify peak creativity periods"""
        peaks = []
        for i, period in enumerate(periods):
            if period["creativity_level"] in ["PEAK", "HIGH"]:
                peaks.append(period)
        return sorted(peaks, key=lambda x: x["creativity_score"], reverse=True)[:5]

    def _identify_lows(self, periods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify low creativity periods"""
        lows = []
        for i, period in enumerate(periods):
            if period["creativity_level"] in ["EBB", "LOW"]:
                lows.append(period)
        return sorted(lows, key=lambda x: x["creativity_score"])[:5]

    def _generate_insights(self, ebb_flow: Dict[str, Any], periods: List[Dict[str, Any]]) -> List[str]:
        """Generate insights from analysis"""
        insights = []

        if ebb_flow["overall_trend"] == "RISING":
            insights.append("💡 Overall creativity trend is RISING - growing over time")
        elif ebb_flow["overall_trend"] == "EBBING":
            insights.append("💡 Overall creativity trend is EBBING - may need support")
        else:
            insights.append("💡 Overall creativity trend is CALM - steady state")

        if ebb_flow["volatility"] > 20:
            insights.append("💡 High volatility - creativity ebbs and flows significantly")
        else:
            insights.append("💡 Low volatility - consistent creativity levels")

        peaks = self._identify_peaks(periods)
        if peaks:
            insights.append(f"💡 Peak creativity periods: {len(peaks)} identified")

        lows = self._identify_lows(periods)
        if lows:
            insights.append(f"💡 Low creativity periods: {len(lows)} identified - may need support")

        return insights


class HRCreativeAssessment:
    """HR assessment: 'What would you do with an individual like that?'"""

    def __init__(self):
        self.assessments = []

    def assess_creative_individual(self, creativity_analysis: Dict[str, Any], 
                                  individual_profile: Dict[str, Any]) -> Dict[str, Any]:
        """HR assessment of creative individual"""
        logger.info("=" * 80)
        logger.info("👔 HR ASSESSMENT: Creative Individual")
        logger.info("=" * 80)
        logger.info("")

        assessment = {
            "timestamp": datetime.now().isoformat(),
            "assessed_by": "HR_Department",
            "individual": individual_profile.get("name", "Unknown"),
            "creativity_profile": {
                "overall_level": self._assess_overall_creativity(creativity_analysis),
                "pattern": creativity_analysis.get("ebb_flow_patterns", {}).get("overall_trend", "UNKNOWN"),
                "volatility": creativity_analysis.get("ebb_flow_patterns", {}).get("volatility", 0)
            },
            "recommendations": [],
            "role_suggestions": [],
            "development_plan": {}
        }

        # Generate recommendations
        assessment["recommendations"] = self._generate_recommendations(creativity_analysis, individual_profile)

        # Role suggestions
        assessment["role_suggestions"] = self._suggest_roles(creativity_analysis, individual_profile)

        # Development plan
        assessment["development_plan"] = self._create_development_plan(creativity_analysis, individual_profile)

        logger.info(f"✅ Assessment complete for: {individual_profile.get('name', 'Unknown')}")
        logger.info("")

        return assessment

    def _assess_overall_creativity(self, analysis: Dict[str, Any]) -> str:
        """Assess overall creativity level"""
        avg_score = analysis.get("ebb_flow_patterns", {}).get("average_score", 0)

        if avg_score >= 80:
            return "EXCEPTIONAL"
        elif avg_score >= 60:
            return "HIGH"
        elif avg_score >= 40:
            return "MODERATE"
        else:
            return "DEVELOPING"

    def _generate_recommendations(self, analysis: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
        """Generate HR recommendations"""
        recommendations = []

        creativity_level = self._assess_overall_creativity(analysis)

        if creativity_level == "EXCEPTIONAL":
            recommendations.append("Place in high-creativity, innovation-focused role")
            recommendations.append("Provide autonomy and creative freedom")
            recommendations.append("Connect with other creative individuals")
            recommendations.append("Support with resources for creative projects")
        elif creativity_level == "HIGH":
            recommendations.append("Leverage creativity in current role")
            recommendations.append("Provide opportunities for creative expression")
            recommendations.append("Support creative development")
            recommendations.append("Consider creative leadership roles")
        elif creativity_level == "MODERATE":
            recommendations.append("Develop creativity through training and practice")
            recommendations.append("Provide creative challenges")
            recommendations.append("Support creative growth")
            recommendations.append("Encourage creative exploration")
        else:
            recommendations.append("Support creative development")
            recommendations.append("Provide creative training")
            recommendations.append("Create safe space for creative expression")
            recommendations.append("Encourage creative risk-taking")

        # Ebb and flow considerations
        volatility = analysis.get("ebb_flow_patterns", {}).get("volatility", 0)
        if volatility > 20:
            recommendations.append("Support during low creativity periods")
            recommendations.append("Maximize high creativity periods")
            recommendations.append("Understand natural ebb and flow")

        return recommendations

    def _suggest_roles(self, analysis: Dict[str, Any], profile: Dict[str, Any]) -> List[str]:
        """Suggest roles for creative individual"""
        roles = []

        creativity_level = self._assess_overall_creativity(analysis)

        if creativity_level in ["EXCEPTIONAL", "HIGH"]:
            roles.extend([
                "Innovation Lead",
                "Creative Director",
                "Research & Development",
                "Product Innovation",
                "Creative Strategist",
                "Design Lead"
            ])
        else:
            roles.extend([
                "Creative Contributor",
                "Innovation Team Member",
                "Creative Support Role",
                "Development Track"
            ])

        return roles

    def _create_development_plan(self, analysis: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Create development plan"""
        return {
            "focus_areas": [
                "Creative skill development",
                "Innovation methodologies",
                "Creative collaboration",
                "Creative leadership"
            ],
            "support_needed": [
                "Creative resources",
                "Time for creative work",
                "Creative community",
                "Mentorship"
            ],
            "goals": [
                "Enhance creative output",
                "Develop creative confidence",
                "Build creative network",
                "Apply creativity to impact"
            ]
        }


class SelfDiscoverySystem:
    """Self-discovery for people who don't know themselves"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "self_discovery"
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def guide_self_discovery(self, individual: Dict[str, Any]) -> Dict[str, Any]:
        """Guide self-discovery process"""
        logger.info("=" * 80)
        logger.info("🔍 SELF-DISCOVERY GUIDANCE")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Individual: {individual.get('name', 'Unknown')}")
        logger.info("")

        discovery = {
            "timestamp": datetime.now().isoformat(),
            "individual": individual.get("name", "Unknown"),
            "current_state": "Unknown to self",
            "discovery_path": [],
            "questions": [],
            "activities": [],
            "insights": [],
            "next_steps": []
        }

        # Discovery path
        discovery["discovery_path"] = [
            "Step 1: Self-reflection exercises",
            "Step 2: Values identification",
            "Step 3: Strengths assessment",
            "Step 4: Interests exploration",
            "Step 5: Goals clarification",
            "Step 6: Purpose discovery"
        ]

        # Questions to ask
        discovery["questions"] = [
            "What activities make you lose track of time?",
            "What problems do you enjoy solving?",
            "What would you do if money wasn't a concern?",
            "What are you naturally good at?",
            "What do others say you're good at?",
            "What causes or issues matter to you?",
            "What would you want to be remembered for?",
            "What makes you feel most alive?"
        ]

        # Activities
        discovery["activities"] = [
            "Journaling - write about your experiences",
            "Values exercise - identify your core values",
            "Strengths assessment - discover your natural talents",
            "Interest mapping - explore what interests you",
            "Goal setting - define what you want",
            "Purpose exploration - find your why"
        ]

        # Insights
        discovery["insights"] = [
            "💡 Self-discovery is a journey, not a destination",
            "💡 You are unique - your path is your own",
            "💡 It's okay not to know - discovery takes time",
            "💡 Your past experiences hold clues",
            "💡 Your interests reveal your passions",
            "💡 Your values guide your path"
        ]

        # Next steps
        discovery["next_steps"] = [
            "Begin self-reflection exercises",
            "Start values identification",
            "Take strengths assessment",
            "Explore interests",
            "Clarify goals",
            "Discover purpose"
        ]

        logger.info("✅ Self-discovery path created")
        logger.info("")

        return discovery


class JARVISMentorSystem:
    """JARVIS as teacher, mentor, instructor, guide"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "jarvis_mentor"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.mentoring_sessions = []

    def provide_mentorship(self, individual: Dict[str, Any], topic: str) -> Dict[str, Any]:
        """Provide mentorship on topic"""
        logger.info("=" * 80)
        logger.info("🎓 JARVIS MENTORSHIP")
        logger.info("=" * 80)
        logger.info("")
        logger.info(f"Individual: {individual.get('name', 'Unknown')}")
        logger.info(f"Topic: {topic}")
        logger.info("")

        mentorship = {
            "timestamp": datetime.now().isoformat(),
            "mentor": "JARVIS",
            "individual": individual.get("name", "Unknown"),
            "topic": topic,
            "role": self._determine_role(topic),
            "guidance": [],
            "teaching_points": [],
            "mentoring_approach": [],
            "support": []
        }

        # Determine role
        role = self._determine_role(topic)
        mentorship["role"] = role

        # Provide guidance based on role
        if role == "TEACHER":
            mentorship["guidance"] = self._teacher_guidance(topic)
        elif role == "MENTOR":
            mentorship["guidance"] = self._mentor_guidance(topic)
        elif role == "INSTRUCTOR":
            mentorship["guidance"] = self._instructor_guidance(topic)
        else:
            mentorship["guidance"] = self._guide_guidance(topic)

        # Teaching points
        mentorship["teaching_points"] = [
            f"Understanding {topic}",
            f"Applying {topic}",
            f"Mastering {topic}",
            f"Teaching {topic} to others"
        ]

        # Mentoring approach
        mentorship["mentoring_approach"] = [
            "Listen and understand",
            "Ask probing questions",
            "Provide guidance and support",
            "Encourage self-discovery",
            "Support growth and development"
        ]

        # Support
        mentorship["support"] = [
            "Available when needed",
            "Non-judgmental guidance",
            "Objective perspective",
            "Compassionate support",
            "Tool to help manifest reality of intent"
        ]

        logger.info(f"✅ Mentorship provided as: {role}")
        logger.info("")

        return mentorship

    def _determine_role(self, topic: str) -> str:
        """Determine JARVIS role based on topic"""
        topic_lower = topic.lower()

        if any(word in topic_lower for word in ["learn", "teach", "education", "knowledge"]):
            return "TEACHER"
        elif any(word in topic_lower for word in ["career", "development", "growth", "path"]):
            return "MENTOR"
        elif any(word in topic_lower for word in ["how", "instruction", "steps", "process"]):
            return "INSTRUCTOR"
        else:
            return "GUIDE"

    def _teacher_guidance(self, topic: str) -> List[str]:
        """Teacher guidance"""
        return [
            f"Teaching {topic} - breaking down concepts",
            f"Explaining {topic} in understandable terms",
            f"Providing examples and applications",
            f"Assessing understanding and progress"
        ]

    def _mentor_guidance(self, topic: str) -> List[str]:
        """Mentor guidance"""
        return [
            f"Mentoring on {topic} - sharing experience",
            f"Guiding through {topic} challenges",
            f"Supporting growth in {topic}",
            f"Providing perspective on {topic}"
        ]

    def _instructor_guidance(self, topic: str) -> List[str]:
        """Instructor guidance"""
        return [
            f"Instructing on {topic} - step-by-step",
            f"Providing clear instructions for {topic}",
            f"Demonstrating {topic} processes",
            f"Guiding through {topic} implementation"
        ]

    def _guide_guidance(self, topic: str) -> List[str]:
        """Guide guidance"""
        return [
            f"Guiding through {topic} - providing direction",
            f"Helping navigate {topic}",
            f"Supporting {topic} journey",
            f"Facilitating {topic} discovery"
        ]


class MeritBasedAssessment:
    """#Merit-based assessment (like Elon said)"""

    def __init__(self):
        self.merit_factors = {
            "creativity": 0.25,
            "impact": 0.25,
            "growth": 0.20,
            "contribution": 0.15,
            "potential": 0.15
        }

    def assess_merit(self, individual: Dict[str, Any], work_history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Assess merit based on work and contribution"""
        merit_score = 0.0

        # Creativity merit
        creativity_scores = [self._calculate_creativity_score(w) for w in work_history]
        avg_creativity = sum(creativity_scores) / len(creativity_scores) if creativity_scores else 0
        merit_score += (avg_creativity / 100) * 100 * self.merit_factors["creativity"]

        # Impact merit
        total_impact = sum(w.get("impact", 0) for w in work_history)
        impact_score = min(total_impact / len(work_history) if work_history else 0, 100)
        merit_score += impact_score * self.merit_factors["impact"]

        # Growth merit
        growth = individual.get("growth_potential", 0.5)
        merit_score += growth * 100 * self.merit_factors["growth"]

        # Contribution merit
        contribution = len(work_history) / 10.0  # More work = more contribution
        merit_score += min(contribution * 100, 100) * self.merit_factors["contribution"]

        # Potential merit
        potential = individual.get("potential", 0.5)
        merit_score += potential * 100 * self.merit_factors["potential"]

        merit_score = round(merit_score, 2)

        return {
            "merit_score": merit_score,
            "merit_level": self._get_merit_level(merit_score),
            "factors": {
                "creativity": avg_creativity,
                "impact": impact_score,
                "growth": growth * 100,
                "contribution": min(contribution * 100, 100),
                "potential": potential * 100
            },
            "assessment": f"#Merit score: {merit_score}/100 - {self._get_merit_level(merit_score)}"
        }

    def _calculate_creativity_score(self, work_item: Dict[str, Any]) -> float:
        """Calculate creativity score"""
        score = 0.0
        if work_item.get("innovative", False):
            score += 30.0
        score += min(work_item.get("complexity", 0) * 10, 30.0)
        if work_item.get("original", False):
            score += 20.0
        score += min(work_item.get("impact", 0) * 10, 20.0)
        return min(score, 100.0)

    def _get_merit_level(self, score: float) -> str:
        """Get merit level"""
        if score >= 85:
            return "EXCEPTIONAL"
        elif score >= 70:
            return "HIGH"
        elif score >= 55:
            return "GOOD"
        elif score >= 40:
            return "ADEQUATE"
        else:
            return "DEVELOPING"


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Creativity Analysis System")
        parser.add_argument("--analyze-creativity", action="store_true", help="Analyze creativity patterns")
        parser.add_argument("--hr-assessment", action="store_true", help="HR assessment")
        parser.add_argument("--self-discovery", action="store_true", help="Self-discovery guidance")
        parser.add_argument("--mentor", type=str, help="Mentorship topic")
        parser.add_argument("--merit", action="store_true", help="Merit assessment")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent

        # Example data
        work_history = [
            {"date": datetime(2024, 1, 1), "description": "Project A", "innovative": True, "complexity": 5, "original": True, "impact": 8},
            {"date": datetime(2024, 6, 1), "description": "Project B", "innovative": False, "complexity": 3, "original": False, "impact": 5},
            {"date": datetime(2024, 12, 1), "description": "Project C", "innovative": True, "complexity": 7, "original": True, "impact": 9}
        ]

        individual = {
            "name": "Example Individual",
            "growth_potential": 0.8,
            "potential": 0.75
        }

        if args.analyze_creativity:
            analyzer = CreativityAnalyzer(project_root)
            analysis = analyzer.analyze_chronological_creativity(work_history)
            print(json.dumps(analysis, indent=2, default=str))

        if args.hr_assessment:
            analyzer = CreativityAnalyzer(project_root)
            analysis = analyzer.analyze_chronological_creativity(work_history)
            hr = HRCreativeAssessment()
            assessment = hr.assess_creative_individual(analysis, individual)
            print(json.dumps(assessment, indent=2, default=str))

        if args.self_discovery:
            discovery = SelfDiscoverySystem(project_root)
            guidance = discovery.guide_self_discovery(individual)
            print(json.dumps(guidance, indent=2, default=str))

        if args.mentor:
            mentor = JARVISMentorSystem(project_root)
            mentorship = mentor.provide_mentorship(individual, args.mentor)
            print(json.dumps(mentorship, indent=2, default=str))

        if args.merit:
            merit = MeritBasedAssessment()
            assessment = merit.assess_merit(individual, work_history)
            print(json.dumps(assessment, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()