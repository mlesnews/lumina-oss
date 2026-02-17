#!/usr/bin/env python3
"""
LUMINA Decisioning Engine - WITH ALL SMART AGENTS & SUBAGENTS
                    -LUM THE MODERN

Enhanced #DECISIONING that includes ALL smart agents and subagents to:
- Explore which agents provide @PEAK solutions
- Map out over time which agents work best for which contexts
- Track patterns of agent effectiveness

@LUMINA @JARVIS @DECISIONING @PEAK -LUM_THE_MODERN
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, field

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("DecisioningWithAllAgents")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("DecisioningWithAllAgents")

# Import enhanced decisioning
try:
    from scripts.python.lumina_decisioning_engine_enhanced import LuminaDecisioningEngineEnhanced
    ENHANCED_DECISIONING_AVAILABLE = True
except ImportError:
    ENHANCED_DECISIONING_AVAILABLE = False
    logger.warning("⚠️  Enhanced decisioning not available")


@dataclass
class Agent:
    """Represents a smart agent or subagent"""
    agent_id: str
    name: str
    role: str
    agent_type: str  # master_agent, droid, specialized, verification, system
    capabilities: List[str] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    expertise: List[str] = field(default_factory=list)
    status: str = "active"
    location: Optional[str] = None
    module: Optional[str] = None
    peak_solutions: int = 0  # Count of @PEAK solutions provided
    total_requests: int = 0  # Total requests handled
    success_rate: float = 0.0
    contexts_handled: List[str] = field(default_factory=list)


@dataclass
class PeakSolution:
    """Tracks a @PEAK solution provided by an agent"""
    solution_id: str
    agent_id: str
    agent_name: str
    context: str
    scope: str
    ask_text: str
    timestamp: str
    quality_score: float
    effectiveness_score: float
    user_satisfaction: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class LuminaDecisioningWithAllAgents(LuminaDecisioningEngineEnhanced):
    """
    Enhanced Decisioning Engine that includes ALL smart agents and subagents.

    Features:
    - Agent registry with all agents
    - @PEAK solution tracking
    - Pattern mapping over time
    - Learning which agents work best for which contexts
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize decisioning engine with all agents"""
        super().__init__(project_root)

        # Agent registry
        self.agents: Dict[str, Agent] = {}
        self.peak_solutions: List[PeakSolution] = []
        self.peak_mapping_file = self.project_root / "data" / "decisioning" / "peak_solutions_mapping.jsonl"
        self.agent_performance_file = self.project_root / "data" / "decisioning" / "agent_performance.json"

        # Load agent registry
        self._load_all_agents()

        # Load historical @PEAK solutions
        self._load_peak_solutions()

        logger.info("=" * 80)
        logger.info("🚀 LUMINA DECISIONING - WITH ALL AGENTS")
        logger.info("                    -LUM THE MODERN")
        logger.info("=" * 80)
        logger.info(f"   Total Agents: {len(self.agents)}")
        logger.info(f"   @PEAK Solutions Tracked: {len(self.peak_solutions)}")
        logger.info("=" * 80)

    def _load_all_agents(self):
        try:
            """Load all smart agents and subagents from configs"""
            # Load homelab AI ecosystem
            ecosystem_file = self.project_root / "config" / "homelab_ai_ecosystem.json"
            if ecosystem_file.exists():
                with open(ecosystem_file, 'r', encoding='utf-8') as f:
                    ecosystem = json.load(f)

                    # Master agents
                    for agent_id, agent_data in ecosystem.get("ecosystem", {}).get("master_agents", {}).items():
                        self.agents[agent_id] = Agent(
                            agent_id=agent_id,
                            name=agent_data.get("name", agent_id),
                            role=agent_data.get("role", ""),
                            agent_type="master_agent",
                            capabilities=agent_data.get("capabilities", []),
                            status=agent_data.get("status", "active"),
                            location=agent_data.get("location")
                        )

                    # Droid agents
                    for agent_id, agent_data in ecosystem.get("ecosystem", {}).get("droid_agents", {}).items():
                        self.agents[agent_id] = Agent(
                            agent_id=agent_id,
                            name=agent_data.get("name", agent_id),
                            role=agent_data.get("role", ""),
                            agent_type="droid",
                            capabilities=agent_data.get("capabilities", []),
                            status=agent_data.get("status", "active"),
                            location=agent_data.get("location"),
                            module=agent_data.get("module")
                        )

                    # Specialized agents
                    for agent_id, agent_data in ecosystem.get("ecosystem", {}).get("specialized_agents", {}).items():
                        self.agents[agent_id] = Agent(
                            agent_id=agent_id,
                            name=agent_data.get("name", agent_id),
                            role=agent_data.get("role", ""),
                            agent_type="specialized",
                            capabilities=agent_data.get("capabilities", []),
                            status=agent_data.get("status", "active"),
                            module=agent_data.get("module")
                        )

                    # Verification systems
                    for system_id, system_data in ecosystem.get("ecosystem", {}).get("verification_systems", {}).items():
                        self.agents[system_id] = Agent(
                            agent_id=system_id,
                            name=system_data.get("name", system_id),
                            role=system_data.get("role", ""),
                            agent_type="verification",
                            capabilities=system_data.get("capabilities", []),
                            status=system_data.get("status", "active"),
                            location=system_data.get("location")
                        )

                    # Core systems
                    for system_id, system_data in ecosystem.get("ecosystem", {}).get("core_systems", {}).items():
                        self.agents[system_id] = Agent(
                            agent_id=system_id,
                            name=system_data.get("name", system_id),
                            role=system_data.get("role", ""),
                            agent_type="system",
                            capabilities=system_data.get("capabilities", []),
                            status=system_data.get("status", "active"),
                            location=system_data.get("location")
                        )

            # Load Iron Legion experts
            iron_legion_file = self.project_root / "config" / "iron_legion_experts_config.json"
            if iron_legion_file.exists():
                with open(iron_legion_file, 'r', encoding='utf-8') as f:
                    iron_legion = json.load(f)
                    for expert_id, expert_data in iron_legion.get("experts", {}).items():
                        agent_id = f"iron_legion_{expert_id}"
                        self.agents[agent_id] = Agent(
                            agent_id=agent_id,
                            name=expert_data.get("name", expert_id),
                            role=expert_data.get("specialization", ""),
                            agent_type="iron_legion",
                            capabilities=expert_data.get("expertise", []),
                            keywords=expert_data.get("keywords", []),
                            expertise=expert_data.get("expertise", []),
                            status=expert_data.get("status", "active")
                        )

            # Load helpdesk team
            helpdesk_file = self.project_root / "config" / "helpdesk" / "helpdesk_support_team.json"
            if helpdesk_file.exists():
                with open(helpdesk_file, 'r', encoding='utf-8') as f:
                    helpdesk = json.load(f)
                    for slot_id, slot_data in helpdesk.get("job_slots", {}).items():
                        agent_id = f"helpdesk_{slot_id}"
                        assigned_to = slot_data.get("assigned_to", "")
                        if assigned_to.startswith("@"):
                            # It's a droid, already loaded
                            continue
                        self.agents[agent_id] = Agent(
                            agent_id=agent_id,
                            name=slot_data.get("role", slot_id),
                            role=slot_data.get("role", ""),
                            agent_type="helpdesk",
                            capabilities=slot_data.get("capabilities", []),
                            status=slot_data.get("status", "active"),
                            module=slot_data.get("module")
                        )

            logger.info(f"✅ Loaded {len(self.agents)} agents")

        except Exception as e:
            self.logger.error(f"Error in _load_all_agents: {e}", exc_info=True)
            raise
    def _load_peak_solutions(self):
        """Load historical @PEAK solutions"""
        if self.peak_mapping_file.exists():
            try:
                with open(self.peak_mapping_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            self.peak_solutions.append(PeakSolution(**data))
                logger.info(f"✅ Loaded {len(self.peak_solutions)} @PEAK solutions")
            except Exception as e:
                logger.warning(f"⚠️  Error loading @PEAK solutions: {e}")

    def decide_with_all_agents(
        self,
        ask_text: str,
        context: str = "",
        scope: str = "",
        user_preference: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        #DECISIONING: Decide which agent(s) to use, considering ALL agents.

        Explores all agents to find @PEAK solution for given context/scope.
        """
        logger.info("=" * 80)
        logger.info("🤔 #DECISIONING: WITH ALL AGENTS")
        logger.info("=" * 80)
        logger.info(f"   Ask: {ask_text[:100]}...")
        logger.info(f"   Context: {context}")
        logger.info(f"   Scope: {scope}")

        # Step 1: Analyze ask to extract requirements
        requirements = self._analyze_ask_requirements(ask_text, context, scope)

        # Step 2: Find matching agents
        matching_agents = self._find_matching_agents(requirements)

        # Step 3: Check historical @PEAK solutions for similar contexts
        peak_recommendations = self._get_peak_recommendations(context, scope, requirements)

        # Step 4: Score agents based on match + historical performance
        scored_agents = self._score_agents(matching_agents, peak_recommendations, requirements)

        # Step 5: Select best agent(s)
        selected_agents = self._select_best_agents(scored_agents, requirements)

        # Step 6: Build decision
        decision = {
            "timestamp": datetime.now().isoformat(),
            "ask_text": ask_text,
            "context": context,
            "scope": scope,
            "requirements": requirements,
            "matching_agents": [a.agent_id for a in matching_agents],
            "peak_recommendations": peak_recommendations,
            "selected_agents": selected_agents,
            "reasoning": self._build_reasoning(selected_agents, requirements, peak_recommendations)
        }

        logger.info(f"   ✅ Selected: {', '.join([a['agent_id'] for a in selected_agents])}")

        return decision

    def _analyze_ask_requirements(
        self,
        ask_text: str,
        context: str,
        scope: str
    ) -> Dict[str, Any]:
        """Analyze ask to extract requirements"""
        ask_lower = ask_text.lower()
        context_lower = context.lower()
        scope_lower = scope.lower()

        requirements = {
            "keywords": [],
            "domains": [],
            "complexity": "moderate",
            "expertise_needed": [],
            "capabilities_needed": []
        }

        # Extract keywords
        all_text = f"{ask_text} {context} {scope}".lower()
        requirements["keywords"] = all_text.split()[:20]  # First 20 words as keywords

        # Domain detection
        if any(kw in all_text for kw in ["code", "function", "class", "bug", "fix", "implement", "pipeline", "python", "programming"]):
            requirements["domains"].append("code")
            requirements["expertise_needed"].append("code_generation")
            requirements["expertise_needed"].append("code")
        if any(kw in all_text for kw in ["security", "threat", "access", "monitor"]):
            requirements["domains"].append("security")
            requirements["expertise_needed"].append("security")
        if any(kw in all_text for kw in ["health", "medical", "recovery", "prevention"]):
            requirements["domains"].append("medical")
            requirements["expertise_needed"].append("health_monitoring")
        if any(kw in all_text for kw in ["knowledge", "context", "pattern", "matrix"]):
            requirements["domains"].append("knowledge")
            requirements["expertise_needed"].append("knowledge_management")
        if any(kw in all_text for kw in ["analysis", "deep", "philosophical", "verification"]):
            requirements["domains"].append("analysis")
            requirements["expertise_needed"].append("deep_analysis")

        # If no domains detected, add general
        if not requirements["domains"]:
            requirements["domains"].append("general")
            requirements["expertise_needed"].append("general")

        # Complexity detection
        if any(kw in all_text for kw in ["complex", "advanced", "comprehensive", "sophisticated"]):
            requirements["complexity"] = "complex"
        elif any(kw in all_text for kw in ["simple", "quick", "basic", "easy"]):
            requirements["complexity"] = "simple"

        return requirements

    def _find_matching_agents(
        self,
        requirements: Dict[str, Any]
    ) -> List[Agent]:
        """Find agents that match requirements"""
        matching = []

        for agent in self.agents.values():
            if agent.status != "active":
                continue

            score = 0

            # Check capabilities match
            for capability in requirements.get("expertise_needed", []):
                capability_lower = capability.lower()
                for agent_cap in agent.capabilities:
                    if capability_lower in agent_cap.lower() or agent_cap.lower() in capability_lower:
                        score += 2

            # Check keywords match
            for keyword in requirements.get("keywords", []):
                keyword_lower = keyword.lower()
                for agent_keyword in agent.keywords:
                    if keyword_lower in agent_keyword.lower() or agent_keyword.lower() in keyword_lower:
                        score += 1

            # Check domain match
            for domain in requirements.get("domains", []):
                domain_lower = domain.lower()
                agent_role_lower = str(agent.role).lower()
                agent_name_lower = agent.name.lower()
                if (domain_lower in agent_role_lower or 
                    domain_lower in agent_name_lower or
                    any(domain_lower in exp.lower() for exp in agent.expertise)):
                    score += 3

            # Always include at least top agents if no matches
            if score > 0 or not matching:
                matching.append(agent)

        # Sort by relevance
        matching.sort(key=lambda a: self._calculate_agent_relevance(a, requirements), reverse=True)

        return matching

    def _calculate_agent_relevance(self, agent: Agent, requirements: Dict[str, Any]) -> float:
        """Calculate how relevant an agent is to requirements"""
        score = 0.0

        # Capability match
        for capability in requirements.get("expertise_needed", []):
            if capability in agent.capabilities:
                score += 2.0

        # Domain match
        for domain in requirements.get("domains", []):
            if domain in agent.expertise or domain in str(agent.role).lower():
                score += 3.0

        # Historical @PEAK performance
        if agent.peak_solutions > 0:
            peak_ratio = agent.peak_solutions / max(agent.total_requests, 1)
            score += peak_ratio * 5.0  # Bonus for @PEAK track record

        return score

    def _get_peak_recommendations(
        self,
        context: str,
        scope: str,
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get @PEAK solution recommendations based on historical data"""
        recommendations = []

        # Find similar @PEAK solutions
        for solution in self.peak_solutions:
            similarity = self._calculate_context_similarity(
                context, scope, requirements,
                solution.context, solution.scope
            )

            if similarity > 0.5:  # Threshold for similarity
                recommendations.append({
                    "agent_id": solution.agent_id,
                    "agent_name": solution.agent_name,
                    "similarity": similarity,
                    "quality_score": solution.quality_score,
                    "effectiveness_score": solution.effectiveness_score,
                    "solution_id": solution.solution_id
                })

        # Sort by similarity and quality
        recommendations.sort(key=lambda x: x["similarity"] * x["quality_score"], reverse=True)

        return recommendations[:5]  # Top 5 recommendations

    def _calculate_context_similarity(
        self,
        context1: str,
        scope1: str,
        requirements1: Dict[str, Any],
        context2: str,
        scope2: str
    ) -> float:
        """Calculate similarity between two contexts"""
        # Simple keyword-based similarity
        words1 = set(f"{context1} {scope1}".lower().split())
        words2 = set(f"{context2} {scope2}".lower().split())

        if not words1 or not words2:
            return 0.0

        intersection = words1.intersection(words2)
        union = words1.union(words2)

        if not union:
            return 0.0

        return len(intersection) / len(union)

    def _score_agents(
        self,
        matching_agents: List[Agent],
        peak_recommendations: List[Dict[str, Any]],
        requirements: Dict[str, Any]
    ) -> List[Tuple[Agent, float]]:
        """Score agents based on match + historical performance"""
        scored = []

        # Build peak recommendation map
        peak_map = {rec["agent_id"]: rec for rec in peak_recommendations}

        for agent in matching_agents:
            score = self._calculate_agent_relevance(agent, requirements)

            # Add @PEAK bonus
            if agent.agent_id in peak_map:
                peak_rec = peak_map[agent.agent_id]
                score += peak_rec["similarity"] * peak_rec["quality_score"] * 3.0

            # Add success rate bonus
            if agent.total_requests > 0:
                score += agent.success_rate * 2.0

            scored.append((agent, score))

        # Sort by score
        scored.sort(key=lambda x: x[1], reverse=True)

        return scored

    def _select_best_agents(
        self,
        scored_agents: List[Tuple[Agent, float]],
        requirements: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Select best agent(s) for the task"""
        if not scored_agents:
            return []

        selected = []

        # Top agent
        top_agent, top_score = scored_agents[0]
        selected.append({
            "agent_id": top_agent.agent_id,
            "name": top_agent.name,
            "role": top_agent.role,
            "agent_type": top_agent.agent_type,
            "score": top_score,
            "primary": True
        })

        # Add secondary agents if score is close (within 20%)
        if len(scored_agents) > 1:
            threshold = top_score * 0.8
            for agent, score in scored_agents[1:3]:  # Max 2 secondary
                if score >= threshold:
                    selected.append({
                        "agent_id": agent.agent_id,
                        "name": agent.name,
                        "role": agent.role,
                        "agent_type": agent.agent_type,
                        "score": score,
                        "primary": False
                    })

        return selected

    def _build_reasoning(
        self,
        selected_agents: List[Dict[str, Any]],
        requirements: Dict[str, Any],
        peak_recommendations: List[Dict[str, Any]]
    ) -> str:
        """Build reasoning for decision"""
        parts = []

        if selected_agents:
            primary = selected_agents[0]
            parts.append(f"Primary: {primary['name']} ({primary['role']}) - Score: {primary['score']:.2f}")

            if len(selected_agents) > 1:
                secondary = selected_agents[1]
                parts.append(f"Secondary: {secondary['name']} - Score: {secondary['score']:.2f}")

        if peak_recommendations:
            top_peak = peak_recommendations[0]
            parts.append(f"@PEAK Recommendation: {top_peak['agent_name']} (similarity: {top_peak['similarity']:.2f})")

        return " | ".join(parts)

    def record_peak_solution(
        self,
        agent_id: str,
        context: str,
        scope: str,
        ask_text: str,
        quality_score: float,
        effectiveness_score: float,
        user_satisfaction: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Record a @PEAK solution for learning"""
        agent = self.agents.get(agent_id)
        if not agent:
            logger.warning(f"⚠️  Agent {agent_id} not found")
            return

        solution = PeakSolution(
            solution_id=f"peak_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}",
            agent_id=agent_id,
            agent_name=agent.name,
            context=context,
            scope=scope,
            ask_text=ask_text,
            timestamp=datetime.now().isoformat(),
            quality_score=quality_score,
            effectiveness_score=effectiveness_score,
            user_satisfaction=user_satisfaction,
            metadata=metadata or {}
        )

        self.peak_solutions.append(solution)

        # Update agent stats
        agent.peak_solutions += 1
        agent.total_requests += 1
        agent.contexts_handled.append(context)
        if agent.total_requests > 0:
            agent.success_rate = agent.peak_solutions / agent.total_requests

        # Save to file
        self.peak_mapping_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.peak_mapping_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps({
                "solution_id": solution.solution_id,
                "agent_id": solution.agent_id,
                "agent_name": solution.agent_name,
                "context": solution.context,
                "scope": solution.scope,
                "ask_text": solution.ask_text,
                "timestamp": solution.timestamp,
                "quality_score": solution.quality_score,
                "effectiveness_score": solution.effectiveness_score,
                "user_satisfaction": solution.user_satisfaction,
                "metadata": solution.metadata
            }) + '\n')

        logger.info(f"✅ Recorded @PEAK solution: {agent.name} for context '{context}'")

    def get_peak_mapping_report(self) -> Dict[str, Any]:
        """Generate report of @PEAK solution mappings"""
        report = {
            "total_peak_solutions": len(self.peak_solutions),
            "agents_by_peak_count": {},
            "contexts_by_peak_count": {},
            "top_agents": [],
            "top_contexts": []
        }

        # Count by agent
        for solution in self.peak_solutions:
            agent_id = solution.agent_id
            if agent_id not in report["agents_by_peak_count"]:
                report["agents_by_peak_count"][agent_id] = 0
            report["agents_by_peak_count"][agent_id] += 1

        # Count by context
        for solution in self.peak_solutions:
            context = solution.context
            if context not in report["contexts_by_peak_count"]:
                report["contexts_by_peak_count"][context] = 0
            report["contexts_by_peak_count"][context] += 1

        # Top agents
        sorted_agents = sorted(
            report["agents_by_peak_count"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        report["top_agents"] = [
            {"agent_id": agent_id, "peak_count": count}
            for agent_id, count in sorted_agents[:10]
        ]

        # Top contexts
        sorted_contexts = sorted(
            report["contexts_by_peak_count"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        report["top_contexts"] = [
            {"context": context, "peak_count": count}
            for context, count in sorted_contexts[:10]
        ]

        return report


def main():
    """CLI interface"""
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Decisioning with All Agents")
    parser.add_argument("--ask", type=str, help="@ask text")
    parser.add_argument("--context", type=str, default="", help="Context")
    parser.add_argument("--scope", type=str, default="", help="Scope")
    parser.add_argument("--record-peak", action="store_true", help="Record @PEAK solution")
    parser.add_argument("--report", action="store_true", help="Generate @PEAK mapping report")

    args = parser.parse_args()

    engine = LuminaDecisioningWithAllAgents()

    if args.report:
        report = engine.get_peak_mapping_report()
        print(f"\n📊 @PEAK MAPPING REPORT:")
        print(f"   Total @PEAK Solutions: {report['total_peak_solutions']}")
        print(f"\n   Top Agents:")
        for agent in report['top_agents']:
            print(f"     {agent['agent_id']}: {agent['peak_count']} @PEAK solutions")
        print(f"\n   Top Contexts:")
        for context in report['top_contexts']:
            print(f"     {context['context']}: {context['peak_count']} @PEAK solutions")

    elif args.ask:
        decision = engine.decide_with_all_agents(
            ask_text=args.ask,
            context=args.context,
            scope=args.scope
        )

        print(f"\n🎯 DECISION:")
        print(f"   Selected Agents: {', '.join([a['name'] for a in decision['selected_agents']])}")
        print(f"   Reasoning: {decision['reasoning']}")

        if args.record_peak:
            # Record as @PEAK (would need quality scores from user)
            print("\n💡 To record as @PEAK, provide quality scores")

    else:
        print("\n🚀 LUMINA Decisioning with All Agents")
        print("   Use --ask 'your question' --context 'context' --scope 'scope'")
        print("   Use --report to see @PEAK mapping")
        print(f"   Total Agents: {len(engine.agents)}")


if __name__ == "__main__":


    main()