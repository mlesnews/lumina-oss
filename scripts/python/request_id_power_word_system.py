#!/usr/bin/env python3
"""
Request ID Power Word System - @ASK as Word of Command

A request gets a request ID. We call this @ASK.
It's a word of command - Dungeons & Dragons Power Word.
A call to action from someone's three-foot world.

Storytelling is in our DNA - if it doesn't have value, it's "all AI slop."
Nothing BUT AI creating memes of our intent, the "mirror" perspective.

Tags: #REQUEST_ID #POWER_WORD #ASK #STORYTELLING #THREE_FOOT_WORLD #DECISIONING #TROUBLESHOOTING
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import uuid

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RequestIDPowerWord")


class PowerWordType(Enum):
    """Type of power word / word of command"""
    ASK = "@ask"  # Request approval/clarification
    DOIT = "@doit"  # Execute immediately
    SPOCK = "@spock"  # Logical analysis
    BONES = "@bones"  # Medical/diagnostic
    JARVIS = "@jarvis"  # AI control
    FULLAUTO = "@fullauto"  # Full automation


@dataclass
class ThreeFootWorld:
    """The three-foot world - personal reality/context"""
    user_id: str
    context: Dict[str, Any]
    intent: str
    problem: str
    solution_idea: str
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class RequestStory:
    """The story behind a request - prevents AI slop"""
    request_id: str
    three_foot_world: ThreeFootWorld
    power_word: str
    intent: str
    problem: str
    solution_idea: str
    value: str  # Why this matters - prevents "AI slop"
    framework: str  # Decisioning/troubleshooting framework
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class PowerWordRequest:
    """A request with power word / word of command"""
    request_id: str
    power_word: PowerWordType
    command: str
    three_foot_world: ThreeFootWorld
    story: RequestStory
    mirror_perspective: Dict[str, Any]  # AI perspective based on facts/framework
    timestamp: datetime = field(default_factory=datetime.now)


class RequestIDPowerWordSystem:
    """
    Request ID Power Word System - @ASK as Word of Command

    A request gets a request ID. We call this @ASK.
    It's a word of command - Dungeons & Dragons Power Word.
    A call to action from someone's three-foot world.

    Storytelling is in our DNA - prevents "AI slop."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Request ID Power Word System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.request_registry: Dict[str, PowerWordRequest] = {}
        self.story_registry: Dict[str, RequestStory] = {}

        # Military & Civilian Principles
        try:
            from military_civilian_principles_system import get_principles_system
            self.principles_system = get_principles_system()
            logger.info("   ⚖️  Military & Civilian Principles integrated")
        except ImportError:
            self.principles_system = None
            logger.debug("   Military & Civilian Principles not available")

        logger.info("✅ Request ID Power Word System initialized")
        logger.info("   🎯 @ASK is a word of command")
        logger.info("   📖 Storytelling is in our DNA")
        logger.info("   ⚖️  UCMJ: Ignorance is not an excuse")
        logger.info("   👁️  Perception drives reality")

    def create_request(
        self,
        command: str,
        user_id: str = "user",
        context: Optional[Dict[str, Any]] = None,
        problem: Optional[str] = None,
        solution_idea: Optional[str] = None,
        value: Optional[str] = None
    ) -> PowerWordRequest:
        """
        Create a request with power word / word of command

        A request gets a request ID. We call this @ASK.
        It's a call to action from someone's three-foot world.

        Args:
            command: The command (may contain @ask, @doit, etc.)
            user_id: User identifier
            context: Personal context (three-foot world)
            problem: The problem being solved
            solution_idea: The idea for solution
            value: Why this matters (prevents AI slop)

        Returns:
            PowerWordRequest with request ID
        """
        # Generate request ID
        request_id = f"REQ_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8].upper()}"

        # Detect power word
        power_word = self._detect_power_word(command)

        # Extract intent
        intent = self._extract_intent(command, problem)

        # Create three-foot world
        three_foot_world = ThreeFootWorld(
            user_id=user_id,
            context=context or {},
            intent=intent,
            problem=problem or "Unknown problem",
            solution_idea=solution_idea or "Unknown solution"
        )

        # Create story (prevents AI slop)
        story = self._create_story(
            request_id=request_id,
            three_foot_world=three_foot_world,
            power_word=power_word.value,
            intent=intent,
            problem=problem or "Unknown problem",
            solution_idea=solution_idea or "Unknown solution",
            value=value or self._derive_value(intent, problem, solution_idea)
        )

        # Create mirror perspective (AI perspective based on facts/framework)
        mirror_perspective = self._create_mirror_perspective(
            story, three_foot_world, power_word
        )

        # CRITICAL: DECISIONING BASED ON TROUBLESHOOTING
        # @ASK IF $CONTEXT $SCORE <=> #DECISIONING THRESHOLD
        # Based on ANY/ALL #TROUBLESHOOTING and questions asked
        decisioning_ask_required = False
        try:
            from decisioning_troubleshooting_system import get_decisioning_system

            decisioning_system = get_decisioning_system()

            # Check if command contains troubleshooting or is a question
            is_question = "?" in command
            is_troubleshooting = any(word in command.lower() for word in
                ["error", "bug", "fix", "broken", "issue", "problem", "troubleshoot"])

            if is_question or is_troubleshooting:
                # Track question if it's a question
                if is_question:
                    question = decisioning_system.track_question(command, source="request")
                    context_score = question.context_score
                else:
                    # Estimate context score for troubleshooting
                    context_score = 0.6 if is_troubleshooting else 0.5

                # Check if @ASK required based on context score threshold
                ask_required_by_threshold = decisioning_system.check_ask_required(context_score)
                decisioning_ask_required = ask_required_by_threshold

                mirror_perspective["decisioning"] = {
                    "context_score": context_score,
                    "ask_required": ask_required_by_threshold,
                    "troubleshooting": is_troubleshooting,
                    "is_question": is_question
                }

                if ask_required_by_threshold:
                    logger.info(f"   📋 @ASK required: Context score {context_score:.2f} < decisioning threshold")
        except Exception as e:
            logger.debug(f"   Could not apply decisioning: {e}")

        # Apply Military & Civilian Principles
        if self.principles_system:
            try:
                from military_civilian_principles_system import PrincipleDomain
                # Determine domain (default to both)
                domain = PrincipleDomain.BOTH
                if "military" in command.lower() or "ucmj" in command.lower():
                    domain = PrincipleDomain.MILITARY
                elif "banking" in command.lower() or "it" in command.lower() or "business" in command.lower():
                    domain = PrincipleDomain.CIVILIAN

                principles_result = self.principles_system.apply_principle(
                    command, domain, context
                )
                mirror_perspective["principles"] = {
                    "compliant": principles_result["compliant"],
                    "violations": principles_result["violations"],
                    "guidance": principles_result["guidance"]
                }
                logger.info(f"   ⚖️  Principles applied: {principles_result['compliant']}")
            except Exception as e:
                logger.debug(f"   Could not apply principles: {e}")

        # Determine if @ASK required (from story or decisioning threshold)
        final_ask_required = story.requires_clarification or decisioning_ask_required

        # Create power word request
        request = PowerWordRequest(
            request_id=request_id,
            power_word=power_word,
            command=command,
            three_foot_world=three_foot_world,
            story=story,
            mirror_perspective=mirror_perspective
        )

        # Set ask_required based on story or decisioning threshold
        request.ask_required = final_ask_required

        # Register request
        self.request_registry[request_id] = request
        self.story_registry[request_id] = story

        logger.info(f"   🎯 Request created: {request_id}")
        logger.info(f"   ⚡ Power word: {power_word.value}")
        logger.info(f"   📖 Story: {story.value}")
        logger.info(f"   🪞 Mirror perspective: {mirror_perspective.get('framework', 'Unknown')}")

        # Log decisioning info if available
        if "decisioning" in mirror_perspective:
            dec_info = mirror_perspective["decisioning"]
            logger.info(f"   📊 Decisioning: Context score {dec_info.get('context_score', 0):.2f}, @ASK: {dec_info.get('ask_required', False)}")

        return request

    def _detect_power_word(self, command: str) -> PowerWordType:
        """Detect power word / word of command"""
        command_lower = command.lower()

        if "@ask" in command_lower or "/ask" in command_lower:
            return PowerWordType.ASK
        elif "@doit" in command_lower or "/doit" in command_lower:
            return PowerWordType.DOIT
        elif "@spock" in command_lower:
            return PowerWordType.SPOCK
        elif "@bones" in command_lower:
            return PowerWordType.BONES
        elif "@jarvis" in command_lower:
            return PowerWordType.JARVIS
        elif "@fullauto" in command_lower:
            return PowerWordType.FULLAUTO
        else:
            # Default to ASK if no power word detected
            return PowerWordType.ASK

    def _extract_intent(self, command: str, problem: Optional[str]) -> str:
        """Extract intent from command"""
        if problem:
            return f"Solve: {problem}"

        # Try to extract from command
        if "fix" in command.lower():
            return "Fix something"
        elif "create" in command.lower():
            return "Create something"
        elif "check" in command.lower():
            return "Check something"
        elif "analyze" in command.lower():
            return "Analyze something"
        else:
            return "Unknown intent"

    def _create_story(
        self,
        request_id: str,
        three_foot_world: ThreeFootWorld,
        power_word: str,
        intent: str,
        problem: str,
        solution_idea: str,
        value: str
    ) -> RequestStory:
        """
        Create the story behind a request

        Storytelling is in our DNA - if it doesn't have value, it's "all AI slop."
        The story gives meaning and prevents meaningless AI-generated content.
        """
        # Determine framework based on problem type
        framework = self._determine_framework(problem, intent)

        story = RequestStory(
            request_id=request_id,
            three_foot_world=three_foot_world,
            power_word=power_word,
            intent=intent,
            problem=problem,
            solution_idea=solution_idea,
            value=value,
            framework=framework
        )

        logger.info(f"   📖 Story created: {value[:50]}...")

        return story

    def _derive_value(self, intent: str, problem: Optional[str], solution_idea: Optional[str]) -> str:
        """Derive value from intent/problem/solution - prevents AI slop"""
        if problem and solution_idea:
            return f"Solve '{problem}' with '{solution_idea}' - real problem, real solution"
        elif problem:
            return f"Address '{problem}' - real problem needs solving"
        elif solution_idea:
            return f"Implement '{solution_idea}' - valuable solution"
        else:
            return f"Execute '{intent}' - call to action"

    def _determine_framework(self, problem: str, intent: str) -> str:
        """Determine decisioning/troubleshooting framework"""
        problem_lower = problem.lower()
        intent_lower = intent.lower()

        # Troubleshooting framework
        if any(word in problem_lower for word in ["error", "bug", "fix", "broken", "issue"]):
            return "#troubleshooting"

        # Decisioning framework
        if any(word in intent_lower for word in ["decide", "choose", "select", "determine"]):
            return "#decisioning"

        # Analysis framework
        if any(word in intent_lower for word in ["analyze", "examine", "review", "study"]):
            return "#analysis"

        # Default
        return "#framework"

    def _create_mirror_perspective(
        self,
        story: RequestStory,
        three_foot_world: ThreeFootWorld,
        power_word: PowerWordType
    ) -> Dict[str, Any]:
        """
        Create mirror perspective - AI perspective based on facts/framework

        This is the "mirror" - AI's perspective based on:
        - Facts
        - Framework
        - Troubleshooting
        - Decisioning
        """
        return {
            "request_id": story.request_id,
            "power_word": power_word.value,
            "framework": story.framework,
            "facts": {
                "problem": story.problem,
                "intent": story.intent,
                "solution_idea": story.solution_idea,
                "value": story.value
            },
            "three_foot_world": {
                "user_id": three_foot_world.user_id,
                "context": three_foot_world.context
            },
            "perspective": f"AI perspective: {story.framework} approach to '{story.problem}'",
            "not_ai_slop": True,  # Has value, has story, has framework
            "timestamp": datetime.now().isoformat()
        }

    def get_request(self, request_id: str) -> Optional[PowerWordRequest]:
        """Get request by ID"""
        return self.request_registry.get(request_id)

    def get_story(self, request_id: str) -> Optional[RequestStory]:
        """Get story by request ID"""
        return self.story_registry.get(request_id)

    def execute_power_word(self, request_id: str) -> Dict[str, Any]:
        """
        Execute power word / word of command

        This is the call to action - execute based on power word type.
        """
        request = self.get_request(request_id)
        if not request:
            return {
                "success": False,
                "error": f"Request {request_id} not found"
            }

        logger.info(f"   ⚡ Executing power word: {request.power_word.value}")
        logger.info(f"   📖 Story: {request.story.value}")
        logger.info(f"   🪞 Mirror: {request.mirror_perspective.get('perspective', 'Unknown')}")

        # Execute based on power word type
        if request.power_word == PowerWordType.ASK:
            return self._execute_ask(request)
        elif request.power_word == PowerWordType.DOIT:
            return self._execute_doit(request)
        elif request.power_word == PowerWordType.SPOCK:
            return self._execute_spock(request)
        elif request.power_word == PowerWordType.BONES:
            return self._execute_bones(request)
        elif request.power_word == PowerWordType.JARVIS:
            return self._execute_jarvis(request)
        else:
            return {
                "success": False,
                "error": f"Unknown power word: {request.power_word.value}"
            }

    def _execute_ask(self, request: PowerWordRequest) -> Dict[str, Any]:
        """Execute @ASK - request approval/clarification"""
        return {
            "success": True,
            "power_word": "@ask",
            "action": "Request approval/clarification",
            "request_id": request.request_id,
            "story": request.story.value,
            "message": f"@ASK: {request.story.value}"
        }

    def _execute_doit(self, request: PowerWordRequest) -> Dict[str, Any]:
        """Execute @DOIT - immediate execution"""
        return {
            "success": True,
            "power_word": "@doit",
            "action": "Execute immediately",
            "request_id": request.request_id,
            "story": request.story.value,
            "message": f"@DOIT: Executing {request.story.intent}"
        }

    def _execute_spock(self, request: PowerWordRequest) -> Dict[str, Any]:
        """Execute @SPOCK - logical analysis"""
        return {
            "success": True,
            "power_word": "@spock",
            "action": "Logical analysis",
            "request_id": request.request_id,
            "story": request.story.value,
            "message": f"@SPOCK: Analyzing {request.story.problem} logically"
        }

    def _execute_bones(self, request: PowerWordRequest) -> Dict[str, Any]:
        """Execute @BONES - medical/diagnostic"""
        return {
            "success": True,
            "power_word": "@bones",
            "action": "Medical/diagnostic",
            "request_id": request.request_id,
            "story": request.story.value,
            "message": f"@BONES: Diagnosing {request.story.problem}"
        }

    def _execute_jarvis(self, request: PowerWordRequest) -> Dict[str, Any]:
        """Execute @JARVIS - AI control"""
        return {
            "success": True,
            "power_word": "@jarvis",
            "action": "AI control",
            "request_id": request.request_id,
            "story": request.story.value,
            "message": f"@JARVIS: Controlling systems for {request.story.intent}"
        }


# Global instance
_request_id_system_instance = None


def get_request_id_system() -> RequestIDPowerWordSystem:
    """Get or create global Request ID Power Word System"""
    global _request_id_system_instance
    if _request_id_system_instance is None:
        _request_id_system_instance = RequestIDPowerWordSystem()
        logger.info("✅ Request ID Power Word System initialized - @ASK IS A WORD OF COMMAND")
    return _request_id_system_instance


def create_request(
    command: str,
    user_id: str = "user",
    problem: Optional[str] = None,
    solution_idea: Optional[str] = None,
    value: Optional[str] = None
) -> PowerWordRequest:
    """Create a request with power word"""
    system = get_request_id_system()
    return system.create_request(
        command=command,
        user_id=user_id,
        problem=problem,
        solution_idea=solution_idea,
        value=value
    )


if __name__ == "__main__":
    # Test
    system = get_request_id_system()

    # Create a request with @ASK
    print("\n🎯 Creating request with @ASK...")
    request = system.create_request(
        command="@ask fix the grammar",
        user_id="user",
        problem="Grammar errors in text",
        solution_idea="Use Grammarly CLI to auto-accept corrections",
        value="Improve text quality and clarity"
    )
    print(f"   Request ID: {request.request_id}")
    print(f"   Power Word: {request.power_word.value}")
    print(f"   Story: {request.story.value}")
    print(f"   Framework: {request.story.framework}")

    # Execute power word
    print("\n⚡ Executing power word...")
    result = system.execute_power_word(request.request_id)
    print(f"   Result: {result['message']}")
