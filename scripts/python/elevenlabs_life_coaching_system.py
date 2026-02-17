"""
ElevenLabs Life-Domain Coaching System
Human-level, client-personalized coaching for navigating extreme volatility

Context: Post-COVID era, rapid tech innovation surge, market volatility
Metaphor: Surfing a tsunami in shark-infested waters (retail investing)

Features:
- Personalized life-domain coaching (career, finance, health, relationships, growth)
- Human-level voice interaction via ElevenLabs
- Real-time adaptation to volatility
- Multi-domain integration
- Personalized strategies for rapid pivoting

#JARVIS #LUMINA #ELEVENLABS #COACHING #LIFE_COACH #VOLATILITY #PERSONALIZED
"""
import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from enum import Enum

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from scripts.python.lumina_logger import get_logger
    logger = get_logger("ElevenLabsLifeCoaching")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ElevenLabsLifeCoaching")

try:
    from scripts.python.elevenlabs_tts_integration import ElevenLabsTTS
    from scripts.python.jarvis_elevenlabs_integration import JARVISElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError:
    ELEVENLABS_AVAILABLE = False
    logger.warning("ElevenLabs integration not available")

try:
    from azure_service_bus_integration import AzureKeyVaultClient
    KEY_VAULT_AVAILABLE = True
except ImportError:
    KEY_VAULT_AVAILABLE = False


class LifeDomain(Enum):
    """Life domains for coaching"""
    CAREER = "career"
    FINANCE = "finance"
    HEALTH = "health"
    RELATIONSHIPS = "relationships"
    PERSONAL_GROWTH = "personal_growth"
    TECHNOLOGY_ADAPTATION = "technology_adaptation"
    MARKET_NAVIGATION = "market_navigation"
    RESILIENCE = "resilience"


class VolatilityLevel(Enum):
    """Current volatility context"""
    EXTREME = "extreme"  # Post-COVID, rapid innovation, market chaos
    HIGH = "high"
    MODERATE = "moderate"
    STABLE = "stable"


@dataclass
class CoachingSession:
    """Coaching session data"""
    session_id: str
    timestamp: datetime
    domain: LifeDomain
    client_context: Dict[str, Any]
    coaching_insights: List[str]
    action_items: List[Dict[str, Any]]
    voice_guidance: Optional[str] = None
    personalized_strategies: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("timestamp"):
            data["timestamp"] = data["timestamp"].isoformat()
        if data.get("domain"):
            data["domain"] = data["domain"].value
        return data


@dataclass
class ClientProfile:
    """Client profile for personalized coaching"""
    client_id: str
    name: Optional[str] = None
    domains_of_focus: List[LifeDomain] = field(default_factory=list)
    current_challenges: List[str] = field(default_factory=list)
    goals: Dict[str, Any] = field(default_factory=dict)
    volatility_tolerance: VolatilityLevel = VolatilityLevel.EXTREME
    preferred_coaching_style: str = "supportive_challenge"  # supportive, challenging, supportive_challenge
    risk_profile: str = "moderate"  # conservative, moderate, aggressive
    tech_adaptation_level: str = "high"  # low, moderate, high
    market_experience: str = "retail_investor"  # beginner, retail_investor, experienced
    session_history: List[str] = field(default_factory=list)
    progress_tracking: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        if data.get("domains_of_focus"):
            data["domains_of_focus"] = [d.value for d in data["domains_of_focus"]]
        if data.get("volatility_tolerance"):
            data["volatility_tolerance"] = data["volatility_tolerance"].value
        return data


class ElevenLabsLifeCoachingSystem:
    """
    Human-level, client-personalized life-domain coaching system

    Designed for navigating extreme volatility in post-COVID era:
    - Rapid technology innovation surge
    - Market volatility (surfing shark-infested waters)
    - Multiple simultaneous transitions
    - Need for quick pivoting
    """

    def __init__(self, project_root: Path):
        """Initialize coaching system."""
        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "life_coaching"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.profiles_dir = self.data_dir / "client_profiles"
        self.profiles_dir.mkdir(parents=True, exist_ok=True)

        self.sessions_dir = self.data_dir / "sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)

        # Initialize ElevenLabs TTS
        self.tts = None
        if ELEVENLABS_AVAILABLE:
            try:
                self.tts = JARVISElevenLabsTTS(project_root=self.project_root)
                logger.info("✅ ElevenLabs TTS initialized for coaching")
            except Exception as e:
                logger.warning(f"ElevenLabs TTS not available: {e}")

        # Coaching frameworks
        self.volatility_context = VolatilityLevel.EXTREME  # Current era context

        logger.info("✅ ElevenLabs Life Coaching System initialized")
        logger.info(f"   Volatility Context: {self.volatility_context.value}")

    def create_client_profile(
        self,
        client_id: str,
        name: Optional[str] = None,
        **kwargs
    ) -> ClientProfile:
        """Create or update client profile."""
        profile_file = self.profiles_dir / f"{client_id}_profile.json"

        if profile_file.exists():
            with open(profile_file, 'r') as f:
                data = json.load(f)
                profile = ClientProfile(**data)
                # Update with new data
                for key, value in kwargs.items():
                    if hasattr(profile, key):
                        setattr(profile, key, value)
        else:
            profile = ClientProfile(client_id=client_id, name=name, **kwargs)

        # Save profile
        with open(profile_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Client profile created/updated: {client_id}")
        return profile

    def get_coaching_guidance(
        self,
        profile: ClientProfile,
        domain: LifeDomain,
        current_situation: str,
        specific_challenge: Optional[str] = None
    ) -> CoachingSession:
        """
        Generate personalized coaching guidance for a life domain.

        Args:
            profile: Client profile
            domain: Life domain to coach on
            current_situation: Current situation description
            specific_challenge: Specific challenge to address

        Returns:
            CoachingSession with personalized guidance
        """
        session_id = f"{profile.client_id}_{domain.value}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Build coaching context
        context = {
            "domain": domain.value,
            "current_situation": current_situation,
            "specific_challenge": specific_challenge,
            "volatility_level": self.volatility_context.value,
            "client_risk_profile": profile.risk_profile,
            "market_experience": profile.market_experience,
            "tech_adaptation_level": profile.tech_adaptation_level
        }

        # Generate personalized insights
        insights = self._generate_coaching_insights(profile, domain, context)

        # Generate action items
        action_items = self._generate_action_items(profile, domain, context, insights)

        # Generate personalized strategies
        strategies = self._generate_strategies(profile, domain, context)

        # Generate voice guidance script
        voice_guidance = self._generate_voice_guidance(profile, domain, insights, strategies, action_items)

        session = CoachingSession(
            session_id=session_id,
            timestamp=datetime.now(),
            domain=domain,
            client_context=context,
            coaching_insights=insights,
            action_items=action_items,
            voice_guidance=voice_guidance,
            personalized_strategies=strategies
        )

        # Save session
        session_file = self.sessions_dir / f"{session_id}.json"
        with open(session_file, 'w') as f:
            json.dump(session.to_dict(), f, indent=2, ensure_ascii=False, default=str)

        logger.info(f"✅ Coaching session created: {session_id}")
        return session

    def _generate_coaching_insights(
        self,
        profile: ClientProfile,
        domain: LifeDomain,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized coaching insights."""
        insights = []

        # Domain-specific insights
        if domain == LifeDomain.MARKET_NAVIGATION:
            insights.append(
                "We're in a period of extreme market volatility - like surfing a tsunami. "
                "The key isn't avoiding the waves, it's learning to read them and position yourself wisely."
            )
            if profile.market_experience == "retail_investor":
                insights.append(
                    "As a retail investor, you're in shark-infested waters. But remember: "
                    "sharks aren't inherently bad - they're just part of the ecosystem. "
                    "The key is understanding their patterns and staying agile."
                )
            insights.append(
                "The fastest technology surge in human history creates both opportunity and risk. "
                "Those who adapt quickly gain advantage; those who resist get left behind."
            )

        elif domain == LifeDomain.TECHNOLOGY_ADAPTATION:
            insights.append(
                "We're experiencing the fastest technology surge across the entire human population. "
                "This isn't gradual change - it's a tsunami of innovation."
            )
            insights.append(
                f"Your tech adaptation level is {profile.tech_adaptation_level}. "
                "The goal isn't to master everything, but to identify which innovations "
                "will give you the biggest advantage in your specific situation."
            )
            insights.append(
                "In this rapid innovation cycle, the ability to pivot quickly is more valuable "
                "than deep expertise in any single technology."
            )

        elif domain == LifeDomain.FINANCE:
            insights.append(
                "Post-COVID poly-legacy-market means traditional strategies don't always apply. "
                "You need adaptive financial strategies that can pivot with market conditions."
            )
            insights.append(
                f"With a {profile.risk_profile} risk profile in {context['volatility_level']} volatility, "
                "you need strategies that balance growth potential with protection."
            )

        elif domain == LifeDomain.CAREER:
            insights.append(
                "Career navigation in this era requires rapid skill adaptation. "
                "The skills that got you here may not be the skills that take you forward."
            )
            insights.append(
                "The ability to pivot quickly is now a core career skill. "
                "Those who can adapt to new technologies and market conditions thrive."
            )

        elif domain == LifeDomain.RESILIENCE:
            insights.append(
                "Navigating extreme volatility requires mental and emotional resilience. "
                "This isn't about avoiding stress - it's about building capacity to handle it."
            )
            insights.append(
                "In shark-infested waters, panic is the real danger. "
                "Building resilience means staying calm and strategic even when things get chaotic."
            )

        # Volatility-specific insights
        if context['volatility_level'] == "extreme":
            insights.append(
                "We're in extreme volatility - the old rules don't always apply. "
                "Success comes from being adaptable, not rigid."
            )
            insights.append(
                "In periods of extreme volatility, small pivots executed quickly "
                "are more valuable than perfect plans executed slowly."
            )

        return insights

    def _generate_action_items(
        self,
        profile: ClientProfile,
        domain: LifeDomain,
        context: Dict[str, Any],
        insights: List[str]
    ) -> List[Dict[str, Any]]:
        """Generate actionable items for the client."""
        action_items = []

        if domain == LifeDomain.MARKET_NAVIGATION:
            action_items.append({
                "priority": "high",
                "action": "Develop a volatility-aware investment strategy",
                "description": "Create a strategy that can adapt to rapid market changes",
                "timeframe": "1-2 weeks",
                "domain": domain.value
            })
            if profile.market_experience == "retail_investor":
                action_items.append({
                    "priority": "high",
                    "action": "Learn to identify market patterns quickly",
                    "description": "Develop skills to read market signals and adapt positions",
                    "timeframe": "ongoing",
                    "domain": domain.value
                })
            action_items.append({
                "priority": "medium",
                "action": "Diversify across asset classes and time horizons",
                "description": "Build a portfolio that can weather volatility",
                "timeframe": "2-4 weeks",
                "domain": domain.value
            })

        elif domain == LifeDomain.TECHNOLOGY_ADAPTATION:
            action_items.append({
                "priority": "high",
                "action": "Identify 3-5 key technologies to focus on",
                "description": "Don't try to master everything - focus on high-impact areas",
                "timeframe": "1 week",
                "domain": domain.value
            })
            action_items.append({
                "priority": "high",
                "action": "Create a learning system for rapid skill acquisition",
                "description": "Build a system that lets you quickly learn and apply new tech",
                "timeframe": "2 weeks",
                "domain": domain.value
            })

        elif domain == LifeDomain.FINANCE:
            action_items.append({
                "priority": "high",
                "action": "Review and adjust financial strategy for volatility",
                "description": "Ensure your financial plan can handle rapid changes",
                "timeframe": "1 week",
                "domain": domain.value
            })
            action_items.append({
                "priority": "medium",
                "action": "Build emergency fund for volatility periods",
                "description": "Maintain liquidity for quick pivots when needed",
                "timeframe": "1-3 months",
                "domain": domain.value
            })

        elif domain == LifeDomain.RESILIENCE:
            action_items.append({
                "priority": "high",
                "action": "Develop stress management routines",
                "description": "Build daily practices that maintain resilience under pressure",
                "timeframe": "immediate",
                "domain": domain.value
            })
            action_items.append({
                "priority": "medium",
                "action": "Create a support network",
                "description": "Build connections with others navigating similar challenges",
                "timeframe": "ongoing",
                "domain": domain.value
            })

        return action_items

    def _generate_strategies(
        self,
        profile: ClientProfile,
        domain: LifeDomain,
        context: Dict[str, Any]
    ) -> List[str]:
        """Generate personalized strategies."""
        strategies = []

        # General volatility strategies
        strategies.append(
            "Small, rapid pivots beat slow, perfect plans in volatile environments"
        )
        strategies.append(
            "Focus on what you can control - your responses, your learning, your positioning"
        )
        strategies.append(
            "Build optionality - create multiple paths forward, not just one"
        )

        # Domain-specific strategies
        if domain == LifeDomain.MARKET_NAVIGATION:
            strategies.append(
                "In shark-infested waters, stay alert but don't panic. "
                "Most 'sharks' are just market participants - understand their behavior."
            )
            strategies.append(
                "Use volatility as information, not just noise. "
                "Extreme movements reveal underlying patterns."
            )
            if profile.market_experience == "retail_investor":
                strategies.append(
                    "As a retail investor, focus on long-term fundamentals while "
                    "staying agile enough to adjust positions when needed."
                )

        elif domain == LifeDomain.TECHNOLOGY_ADAPTATION:
            strategies.append(
                "Master the fundamentals of a few key technologies deeply, "
                "then learn to quickly evaluate and adopt new ones."
            )
            strategies.append(
                "Build a learning system, not just knowledge. "
                "The ability to learn quickly is more valuable than any single skill."
            )

        # Risk profile strategies
        if profile.risk_profile == "conservative":
            strategies.append(
                "In extreme volatility, conservative doesn't mean inactive. "
                "It means calculated moves with strong risk management."
            )
        elif profile.risk_profile == "aggressive":
            strategies.append(
                "Aggressive strategies in volatile markets require rapid decision-making. "
                "Ensure you have the information and systems to make quick, informed choices."
            )

        return strategies

    def _generate_voice_guidance(
        self,
        profile: ClientProfile,
        domain: LifeDomain,
        insights: List[str],
        strategies: List[str],
        action_items: List[Dict[str, Any]]
    ) -> str:
        """Generate voice guidance script for ElevenLabs TTS."""
        script_parts = []

        # Personalized opening
        if profile.name:
            script_parts.append(f"Hey {profile.name}, let's talk about navigating {domain.value.replace('_', ' ')} in these volatile times.")
        else:
            script_parts.append(f"Let's talk about navigating {domain.value.replace('_', ' ')} in these volatile times.")

        script_parts.append("\nWe're in an era of extreme volatility - like surfing a tsunami in shark-infested waters. But here's the thing: you've got this. Let me share some insights that are specific to your situation.")

        # Share insights
        script_parts.append("\nFirst, let's talk about what's really happening:")
        for insight in insights[:3]:  # Top 3 insights
            script_parts.append(f"\n{insight}")

        # Share strategies
        script_parts.append("\n\nHere's how we're going to approach this:")
        for strategy in strategies[:3]:  # Top 3 strategies
            script_parts.append(f"\n{strategy}")

        # Action items
        script_parts.append("\n\nNow, let's get specific about what you can do:")
        high_priority = [item for item in action_items if item.get("priority") == "high"]
        for item in high_priority[:2]:  # Top 2 high-priority actions
            script_parts.append(f"\n{item['action']}. {item.get('description', '')}")

        # Closing
        script_parts.append(
            "\n\nRemember: in this era of rapid change, the ability to pivot quickly "
            "is your superpower. Small, strategic moves executed rapidly beat perfect plans "
            "that take too long to execute. You're building the skills to navigate this volatility - "
            "and that's exactly what's needed right now."
        )

        script_parts.append("\n\nLet's check in again soon and see how these strategies are working for you.")

        return " ".join(script_parts)

    def deliver_coaching_session(
        self,
        session: CoachingSession,
        speak: bool = True,
        save_audio: bool = True
    ) -> Dict[str, Any]:
        """
        Deliver coaching session via ElevenLabs voice.

        Args:
            session: CoachingSession to deliver
            speak: If True, speak the guidance
            save_audio: If True, save audio file

        Returns:
            Dictionary with delivery results
        """
        if not self.tts:
            logger.warning("ElevenLabs TTS not available - cannot deliver voice coaching")
            return {"success": False, "error": "TTS not available"}

        if not session.voice_guidance:
            logger.warning("No voice guidance script in session")
            return {"success": False, "error": "No voice guidance"}

        result = {
            "success": True,
            "session_id": session.session_id,
            "delivered_at": datetime.now().isoformat(),
            "audio_saved": False
        }

        try:
            # Generate and speak guidance
            if speak:
                logger.info(f"🎤 Delivering coaching session: {session.session_id}")

                # Use ElevenLabs to generate audio
                audio_path = None
                if save_audio:
                    audio_dir = self.sessions_dir / "audio"
                    audio_dir.mkdir(parents=True, exist_ok=True)
                    audio_path = audio_dir / f"{session.session_id}.mp3"

                # Generate audio using ElevenLabs
                if hasattr(self.tts, 'generate_audio'):
                    audio_data = self.tts.generate_audio(
                        text=session.voice_guidance,
                        voice_id=self.tts.current_voice_id,
                        output_path=str(audio_path) if audio_path else None
                    )
                    if audio_path and audio_path.exists():
                        result["audio_saved"] = True
                        result["audio_path"] = str(audio_path)
                elif hasattr(self.tts, 'speak'):
                    # Fallback to speak method
                    self.tts.speak(session.voice_guidance, wait=True)
                    if audio_path:
                        result["audio_saved"] = False  # May not save with speak()

                logger.info(f"✅ Coaching session delivered via ElevenLabs voice")

            return result

        except Exception as e:
            logger.error(f"Error delivering coaching session: {e}")
            return {"success": False, "error": str(e)}

    def conduct_coaching_session(
        self,
        client_id: str,
        domain: LifeDomain,
        current_situation: str,
        specific_challenge: Optional[str] = None,
        deliver_voice: bool = True
    ) -> CoachingSession:
        """
        Complete coaching session workflow.

        Args:
            client_id: Client identifier
            domain: Life domain to coach on
            current_situation: Current situation description
            specific_challenge: Specific challenge
            deliver_voice: If True, deliver via ElevenLabs voice

        Returns:
            CoachingSession
        """
        # Load or create profile
        profile_file = self.profiles_dir / f"{client_id}_profile.json"
        if profile_file.exists():
            with open(profile_file, 'r') as f:
                data = json.load(f)
                # Convert enum strings back to enums
                if 'domains_of_focus' in data:
                    data['domains_of_focus'] = [LifeDomain(d) for d in data['domains_of_focus']]
                if 'volatility_tolerance' in data:
                    data['volatility_tolerance'] = VolatilityLevel(data['volatility_tolerance'])
                profile = ClientProfile(**data)
        else:
            # Create default profile
            profile = self.create_client_profile(client_id)

        # Generate coaching session
        session = self.get_coaching_guidance(
            profile=profile,
            domain=domain,
            current_situation=current_situation,
            specific_challenge=specific_challenge
        )

        # Deliver via voice if requested
        if deliver_voice:
            delivery_result = self.deliver_coaching_session(session, speak=True, save_audio=True)
            session.metadata = session.metadata or {}
            session.metadata["delivery"] = delivery_result

        # Update profile with session
        profile.session_history.append(session.session_id)
        profile_file = self.profiles_dir / f"{client_id}_profile.json"
        with open(profile_file, 'w') as f:
            json.dump(profile.to_dict(), f, indent=2, ensure_ascii=False, default=str)

        return session


def main():
    """Main function for CLI usage."""
    import argparse

    parser = argparse.ArgumentParser(description="ElevenLabs Life-Domain Coaching System")
    parser.add_argument("--project-root", type=Path, default=project_root)
    parser.add_argument("--client-id", type=str, required=True, help="Client identifier")
    parser.add_argument("--domain", type=str, required=True, 
                       choices=[d.value for d in LifeDomain],
                       help="Life domain to coach on")
    parser.add_argument("--situation", type=str, required=True,
                       help="Current situation description")
    parser.add_argument("--challenge", type=str, help="Specific challenge to address")
    parser.add_argument("--no-voice", action="store_true", help="Don't deliver via voice")
    parser.add_argument("--create-profile", action="store_true", help="Create new client profile")
    parser.add_argument("--name", type=str, help="Client name (for profile creation)")

    args = parser.parse_args()

    system = ElevenLabsLifeCoachingSystem(args.project_root)

    # Create profile if requested
    if args.create_profile:
        system.create_client_profile(
            client_id=args.client_id,
            name=args.name
        )

    # Conduct coaching session
    domain = LifeDomain(args.domain)
    session = system.conduct_coaching_session(
        client_id=args.client_id,
        domain=domain,
        current_situation=args.situation,
        specific_challenge=args.challenge,
        deliver_voice=not args.no_voice
    )

    # Print session summary
    print("\n" + "="*80)
    print("COACHING SESSION SUMMARY")
    print("="*80)
    print(f"\nSession ID: {session.session_id}")
    print(f"Domain: {session.domain.value}")
    print(f"\nKey Insights ({len(session.coaching_insights)}):")
    for i, insight in enumerate(session.coaching_insights[:3], 1):
        print(f"  {i}. {insight[:100]}...")

    print(f"\nAction Items ({len(session.action_items)}):")
    for i, item in enumerate(session.action_items[:3], 1):
        print(f"  {i}. [{item.get('priority', 'medium').upper()}] {item.get('action', 'N/A')}")

    print(f"\nStrategies ({len(session.personalized_strategies)}):")
    for i, strategy in enumerate(session.personalized_strategies[:3], 1):
        print(f"  {i}. {strategy[:100]}...")

    if session.voice_guidance and not args.no_voice:
        print("\n✅ Voice coaching delivered via ElevenLabs")

    print("\n" + "="*80)


if __name__ == "__main__":


    main()