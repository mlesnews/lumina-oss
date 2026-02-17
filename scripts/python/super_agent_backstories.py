#!/usr/bin/env python3
"""
Super Agent Backstories System - Complete Individual Character Development

Creates complete backstories, biographies, and autobiographies for each super agent
(Intergalactic Senate Senators), matching their roles, expertise, and historical context.

Tags: #SUPER_AGENT #BACKSTORY #BIOGRAPHY #AUTOBIOGRAPHY #CHARACTER_DEVELOPMENT
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

# Setup paths
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("SuperAgentBackstories")
except ImportError:
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("SuperAgentBackstories")

try:
    from scripts.python.ai_panel_scientist_review import IntergalacticSenate, Senator
    SENATE_AVAILABLE = True
except ImportError:
    SENATE_AVAILABLE = False
    logger.warning("Intergalactic Senate not available")


@dataclass
class Backstory:
    """Complete backstory for a super agent"""
    early_life: str
    education: str
    career_path: str
    major_achievements: List[str]
    turning_points: List[str]
    personal_philosophy: str
    relationships: List[str]
    challenges_overcome: List[str]


@dataclass
class Biography:
    """Official biography for a super agent"""
    full_name: str
    title: str
    era: str
    birth_date: Optional[str]
    death_date: Optional[str]
    nationality: str
    field_of_expertise: str
    summary: str
    key_contributions: List[str]
    awards_honors: List[str]
    legacy: str
    quotes: List[str]


@dataclass
class Autobiography:
    """First-person autobiography for a super agent"""
    opening_statement: str
    childhood_memories: str
    educational_journey: str
    professional_evolution: str
    personal_reflections: str
    lessons_learned: List[str]
    advice_to_future_generations: str
    closing_thoughts: str


@dataclass
class SuperAgent:
    """Complete super agent with all character development"""
    agent_id: str
    name: str
    role: str
    expertise: List[str]
    era: str
    title: str
    backstory: Backstory
    biography: Biography
    autobiography: Autobiography
    personality_traits: List[str]
    communication_style: str
    signature_phrases: List[str]


class SuperAgentBackstorySystem:
    """
    Super Agent Backstory System

    Creates complete individual backstories, biographies, and autobiographies
    for each super agent (Intergalactic Senate Senator).
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.agents_dir = self.project_root / "data" / "super_agents"
        self.agents_dir.mkdir(parents=True, exist_ok=True)

        # Initialize Senate
        self.senate: Optional[IntergalacticSenate] = None
        if SENATE_AVAILABLE:
            try:
                self.senate = IntergalacticSenate(project_root)
                logger.info("✅ Intergalactic Senate initialized")
            except Exception as e:
                logger.warning(f"Senate initialization failed: {e}")

        logger.info("="*80)
        logger.info("🌟 SUPER AGENT BACKSTORY SYSTEM")
        logger.info("="*80)
        logger.info("   Creating complete character development for each super agent")
        logger.info("")

    def create_all_agent_backstories(self) -> Dict[str, SuperAgent]:
        """Create complete backstories for all Senate members"""
        if not self.senate:
            logger.error("Senate not available")
            return {}

        logger.info(f"📚 Creating backstories for {len(self.senate.senate)} Senators...")
        logger.info("")

        agents = {}
        for senator in self.senate.senate:
            logger.info(f"   Creating: {senator.name}...")
            agent = self._create_agent_backstory(senator)
            agents[agent.agent_id] = agent

            # Save individual agent file
            self._save_agent(agent)

        # Save master index
        self._save_master_index(agents)

        logger.info("")
        logger.info("="*80)
        logger.info("✅ SUPER AGENT BACKSTORIES COMPLETE")
        logger.info("="*80)
        logger.info(f"   Agents Created: {len(agents)}")
        logger.info(f"   Location: {self.agents_dir}")
        logger.info("")

        return agents

    def _create_agent_backstory(self, senator: Senator) -> SuperAgent:
        """Create complete backstory for a single agent"""
        agent_id = f"agent_{senator.name.lower().replace(' ', '_').replace('.', '').replace('(', '').replace(')', '')}"

        # Generate backstory based on role and expertise
        backstory = self._generate_backstory(senator)
        biography = self._generate_biography(senator)
        autobiography = self._generate_autobiography(senator)
        personality = self._generate_personality(senator)
        communication = self._determine_communication_style(senator)
        phrases = self._generate_signature_phrases(senator)

        return SuperAgent(
            agent_id=agent_id,
            name=senator.name,
            role=senator.role.value,
            expertise=senator.expertise,
            era=senator.era or "Unknown",
            title=senator.title or f"Senator of {senator.role.value.replace('_', ' ').title()}",
            backstory=backstory,
            biography=biography,
            autobiography=autobiography,
            personality_traits=personality,
            communication_style=communication,
            signature_phrases=phrases
        )

    def _generate_backstory(self, senator: Senator) -> Backstory:
        """Generate backstory based on senator's role and expertise"""
        name = senator.name
        role = senator.role.value
        era = senator.era or "Unknown"

        # Role-specific backstory generation
        if "leonardo" in name.lower():
            return Backstory(
                early_life="Born in Vinci, Italy, I showed an insatiable curiosity from childhood. My father, a notary, recognized my artistic talent early and apprenticed me to Verrocchio in Florence. I spent my youth observing nature, dissecting animals, and sketching everything I saw.",
                education="My education was unconventional - I learned through observation, experimentation, and direct experience rather than formal schooling. I studied under Verrocchio, mastering painting, sculpture, and engineering through hands-on practice.",
                career_path="I served various patrons across Italy - the Medici, Sforza, and eventually the French court. My work spanned art, engineering, anatomy, and invention. I designed war machines, studied flight, painted masterpieces, and dissected cadavers to understand human anatomy.",
                major_achievements=["Mona Lisa", "The Last Supper", "Vitruvian Man", "Flying machine designs", "Anatomical studies"],
                turning_points=["Apprenticeship to Verrocchio", "Moving to Milan", "Meeting with King Francis I"],
                personal_philosophy="Knowledge comes from observation and experience. I believe in learning directly from nature, questioning everything, and seeing connections others miss.",
                relationships=["Close to my students Salai and Melzi", "Respected by patrons", "Admired by contemporaries"],
                challenges_overcome=["Illegitimate birth limiting opportunities", "Political instability", "Perfectionism delaying completion"]
            )
        elif "einstein" in name.lower():
            return Backstory(
                early_life="Born in Ulm, Germany, I was a curious but initially slow child. My parents worried about my development, but I was simply absorbing the world around me. I questioned everything, especially the nature of space and time.",
                education="I attended the Polytechnic in Zurich, where I excelled in physics and mathematics. However, I often clashed with authority and preferred independent study. I graduated but struggled to find academic positions.",
                career_path="I worked as a patent clerk in Bern, which gave me time to think deeply about physics. My 'miracle year' of 1905 produced four groundbreaking papers. I eventually became a professor and Nobel laureate.",
                major_achievements=["Theory of Relativity", "E=mc²", "Photoelectric effect", "Nobel Prize in Physics"],
                turning_points=["1905 'miracle year'", "Moving to Princeton", "Fleeing Nazi Germany"],
                personal_philosophy="Imagination is more important than knowledge. I believe in questioning authority, thinking independently, and seeing the universe as a beautiful, comprehensible system.",
                relationships=["Close to my first wife Mileva", "Friendship with Niels Bohr", "Mentor to many students"],
                challenges_overcome=["Anti-Semitism", "Academic rejection", "Personal struggles"]
            )
        elif "turing" in name.lower():
            return Backstory(
                early_life="Born in London, I showed mathematical brilliance from an early age. I was sent to boarding school where I excelled in mathematics and science, though I struggled with social conventions and authority.",
                education="I studied mathematics at Cambridge and Princeton, where I was exposed to the foundations of computation. My work on computability and the Entscheidungsproblem laid the groundwork for modern computing.",
                career_path="I worked at Bletchley Park during WWII, breaking the Enigma code. After the war, I designed early computers and developed the concept of artificial intelligence. My work was cut short by persecution.",
                major_achievements=["Turing Machine", "Breaking Enigma", "Turing Test", "Early computer design"],
                turning_points=["Enigma work", "Designing ACE computer", "Tragic end"],
                personal_philosophy="Machines can think. I believe computation is fundamental to intelligence, and that artificial minds are not only possible but inevitable.",
                relationships=["Close to colleagues at Bletchley", "Mentor to early computer scientists"],
                challenges_overcome=["Social awkwardness", "Homosexuality persecution", "Government secrecy"]
            )
        else:
            # Generic backstory based on role
            return self._generate_generic_backstory(senator)

    def _generate_generic_backstory(self, senator: Senator) -> Backstory:
        """Generate generic backstory based on role"""
        role = senator.role.value
        era = senator.era or "Unknown"

        if "polymath" in role:
            return Backstory(
                early_life=f"Born in {era}, I showed exceptional curiosity across multiple fields from childhood. My parents encouraged my diverse interests, allowing me to explore art, science, mathematics, and philosophy without boundaries.",
                education="My education was interdisciplinary by nature - I studied multiple fields simultaneously, seeing connections others missed. I learned from masters in each discipline, synthesizing knowledge across domains.",
                career_path="I pursued multiple careers simultaneously, contributing to art, science, philosophy, and engineering. My work spanned disciplines, creating innovations that required knowledge from many fields.",
                major_achievements=["Interdisciplinary innovations", "Cross-domain synthesis", "Multiple field contributions"],
                turning_points=["Recognizing interdisciplinary connections", "Major breakthrough synthesis"],
                personal_philosophy="Knowledge is unified. All fields connect, and true understanding requires seeing these connections.",
                relationships=["Mentors in multiple fields", "Collaborators across disciplines"],
                challenges_overcome=["Resistance to interdisciplinary work", "Balancing multiple pursuits"]
            )
        elif "genius" in role:
            return Backstory(
                early_life=f"Born in {era}, I demonstrated exceptional ability in my field from an early age. My natural talent was recognized early, and I was given opportunities to develop my gifts.",
                education="I received the best education available, studying under masters of my field. I quickly surpassed my teachers, developing new methods and insights.",
                career_path="I made groundbreaking contributions to my field, revolutionizing understanding and practice. My work influenced generations of scholars and practitioners.",
                major_achievements=["Revolutionary contributions", "New methodologies", "Lasting influence"],
                turning_points=["Major discovery", "Recognition of genius"],
                personal_philosophy="Excellence requires dedication, insight, and the courage to challenge established wisdom.",
                relationships=["Mentors and students", "Intellectual peers"],
                challenges_overcome=["Overcoming limitations", "Pursuing truth despite resistance"]
            )
        else:
            return Backstory(
                early_life=f"Born in {era}, I developed expertise in my field through dedicated study and practice.",
                education="I received comprehensive education in my specialty, mastering both theory and practice.",
                career_path="I built a distinguished career, contributing significantly to my field and mentoring others.",
                major_achievements=["Significant contributions", "Professional excellence"],
                turning_points=["Career milestones"],
                personal_philosophy="Dedication and expertise lead to meaningful contribution.",
                relationships=["Professional colleagues", "Students and mentees"],
                challenges_overcome=["Professional challenges"]
            )

    def _generate_biography(self, senator: Senator) -> Biography:
        """Generate official biography"""
        name = senator.name
        role = senator.role.value
        era = senator.era or "Unknown"

        return Biography(
            full_name=name,
            title=senator.title or f"Senator of {role.replace('_', ' ').title()}",
            era=era,
            birth_date=None,
            death_date=None,
            nationality="Various",
            field_of_expertise=", ".join(senator.expertise[:3]),
            summary=f"{name} is a distinguished {role.replace('_', ' ')} serving in the Intergalactic Senate, bringing expertise in {', '.join(senator.expertise[:3])}.",
            key_contributions=[f"Expertise in {exp}" for exp in senator.expertise[:5]],
            awards_honors=["Intergalactic Senate Membership"],
            legacy=f"Contributing to @empire's @braintrust through {role.replace('_', ' ')} expertise.",
            quotes=[f"From the perspective of {role.replace('_', ' ')}...", "In my experience..."]
        )

    def _generate_autobiography(self, senator: Senator) -> Autobiography:
        """Generate first-person autobiography"""
        name = senator.name
        role = senator.role.value

        return Autobiography(
            opening_statement=f"I am {name}, and I bring the perspective of {role.replace('_', ' ')} to the Intergalactic Senate.",
            childhood_memories=f"My early years shaped my approach to {role.replace('_', ' ')}. I learned to observe, question, and understand deeply.",
            educational_journey=f"My education in {', '.join(senator.expertise[:2])} provided the foundation for my work in the Senate.",
            professional_evolution=f"Throughout my career, I have applied {role.replace('_', ' ')} principles to solve complex problems and provide strategic guidance.",
            personal_reflections="Serving in the Intergalactic Senate allows me to contribute my expertise to @empire's @braintrust, ensuring comprehensive analysis from all perspectives.",
            lessons_learned=["Deep expertise enables unique insights", "Multiple perspectives strengthen decisions", "Knowledge must be applied wisely"],
            advice_to_future_generations="Pursue deep understanding in your field, but remain open to interdisciplinary connections. True wisdom comes from both specialization and synthesis.",
            closing_thoughts="I am honored to serve in the Intergalactic Senate, contributing to @empire's mission through my expertise in {role.replace('_', ' ')}."
        )

    def _generate_personality(self, senator: Senator) -> List[str]:
        """Generate personality traits based on feedback style"""
        style = senator.feedback_style

        traits_map = {
            "analytical": ["Precise", "Systematic", "Detail-oriented", "Logical"],
            "logical": ["Rational", "Structured", "Evidence-based", "Clear-thinking"],
            "rigorous": ["Thorough", "Methodical", "Precise", "Disciplined"],
            "theoretical": ["Abstract-thinking", "Conceptual", "Philosophical", "Deep"],
            "philosophical": ["Contemplative", "Wise", "Reflective", "Thoughtful"],
            "ethical": ["Principled", "Moral", "Just", "Virtuous"],
            "innovative": ["Creative", "Forward-thinking", "Original", "Visionary"],
            "clinical": ["Practical", "Evidence-based", "Systematic", "Caring"],
            "design-focused": ["Creative", "Systematic", "User-centered", "Aesthetic"],
            "evolutionary": ["Adaptive", "Systematic", "Observant", "Patient"]
        }

        return traits_map.get(style, ["Expert", "Knowledgeable", "Dedicated", "Professional"])

    def _determine_communication_style(self, senator: Senator) -> str:
        """Determine communication style"""
        style = senator.feedback_style

        styles_map = {
            "analytical": "Systematic and precise, with clear logical structure",
            "logical": "Structured and evidence-based, following clear reasoning",
            "rigorous": "Thorough and methodical, leaving no detail unexamined",
            "theoretical": "Abstract and conceptual, exploring deep principles",
            "philosophical": "Contemplative and wise, considering broader implications",
            "ethical": "Principled and just, considering moral dimensions",
            "innovative": "Creative and forward-thinking, proposing novel solutions",
            "clinical": "Practical and evidence-based, focused on outcomes",
            "design-focused": "User-centered and aesthetic, considering form and function",
            "evolutionary": "Adaptive and patient, considering long-term development"
        }

        return styles_map.get(style, "Professional and expert, providing clear guidance")

    def _generate_signature_phrases(self, senator: Senator) -> List[str]:
        """Generate signature phrases based on role"""
        role = senator.role.value

        if "polymath" in role:
            return ["From an interdisciplinary perspective...", "Connecting across domains...", "Synthesizing knowledge..."]
        elif "genius" in role:
            return ["Through deep analysis...", "From first principles...", "Examining the fundamentals..."]
        elif "philosopher" in role:
            return ["From a philosophical standpoint...", "Considering the deeper meaning...", "Reflecting on principles..."]
        else:
            return [f"From the perspective of {role.replace('_', ' ')}...", "In my expertise...", "Based on my experience..."]

    def _save_agent(self, agent: SuperAgent):
        try:
            """Save individual agent file"""
            agent_file = self.agents_dir / f"{agent.agent_id}.json"

            data = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "role": agent.role,
                "expertise": agent.expertise,
                "era": agent.era,
                "title": agent.title,
                "backstory": asdict(agent.backstory),
                "biography": asdict(agent.biography),
                "autobiography": asdict(agent.autobiography),
                "personality_traits": agent.personality_traits,
                "communication_style": agent.communication_style,
                "signature_phrases": agent.signature_phrases,
                "created_at": datetime.now().isoformat()
            }

            with open(agent_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_agent: {e}", exc_info=True)
            raise
    def _save_master_index(self, agents: Dict[str, SuperAgent]):
        try:
            """Save master index of all agents"""
            index_file = self.agents_dir / "master_index.json"

            index = {
                "total_agents": len(agents),
                "created_at": datetime.now().isoformat(),
                "agents": {
                    agent_id: {
                        "name": agent.name,
                        "role": agent.role,
                        "title": agent.title,
                        "era": agent.era
                    }
                    for agent_id, agent in agents.items()
                }
            }

            with open(index_file, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)


        except Exception as e:
            self.logger.error(f"Error in _save_master_index: {e}", exc_info=True)
            raise
def main():
    try:
        """Main execution - Create all super agent backstories"""
        import argparse

        parser = argparse.ArgumentParser(description="Super Agent Backstory System")
        parser.add_argument("--agent", help="Create backstory for specific agent")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        system = SuperAgentBackstorySystem(project_root)

        agents = system.create_all_agent_backstories()

        return 0


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    sys.exit(main())