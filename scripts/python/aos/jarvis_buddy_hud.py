#!/usr/bin/env python3
"""
AOS JARVIS Buddy HUD

JARVIS as AI companion in HID-HUD (Heads-Up Display).
Always-on AI buddy that helps proactively.

Tags: #AOS #JARVIS_BUDDY #HUD #AR #AI_COMPANION @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import threading
import time

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISBuddyHUD")


class BuddyMode(Enum):
    """JARVIS buddy interaction modes"""
    PASSIVE = 'passive'  # Only responds when called
    ACTIVE = 'active'    # Proactive help
    COMPANION = 'companion'  # Always visible, conversational
    MINIMAL = 'minimal'  # Minimal UI, only when needed


class EmotionalState(Enum):
    """User emotional states"""
    HAPPY = 'happy'
    STRESSED = 'stressed'
    FOCUSED = 'focused'
    TIRED = 'tired'
    CONFUSED = 'confused'
    NEUTRAL = 'neutral'


@dataclass
class BuddyContext:
    """Context for JARVIS buddy"""
    location: Optional[str] = None
    activity: Optional[str] = None
    time_of_day: Optional[str] = None
    emotional_state: EmotionalState = EmotionalState.NEUTRAL
    recent_actions: List[str] = None
    current_task: Optional[str] = None

    def __post_init__(self):
        if self.recent_actions is None:
            self.recent_actions = []


@dataclass
class BuddySuggestion:
    """Proactive suggestion from JARVIS"""
    type: str  # 'help', 'reminder', 'optimization', 'safety'
    message: str
    priority: int  # 1-10, higher = more important
    action: Optional[Callable] = None
    metadata: Dict[str, Any] = None


class JARVISBuddyHUD:
    """
    JARVIS as AI companion in HID-HUD.

    Features:
    - Always-on companion
    - Contextual awareness
    - Proactive help
    - Emotional intelligence
    - Natural interaction
    """

    def __init__(self, mode: BuddyMode = BuddyMode.ACTIVE):
        """Initialize JARVIS buddy"""
        self.mode = mode
        self.context = BuddyContext()
        self.is_visible = False
        self.position = [0, 0, -1]  # 3D position in AR space
        self.jarvis = None  # Will be set when JARVIS is available
        self.r5 = None  # Will be set when R5 is available
        self.marvin = None  # Will be set when MARVIN is available
        self.suggestions: List[BuddySuggestion] = []
        self.lock = threading.Lock()
        self.running = False

        logger.info(f"🤖 JARVIS Buddy HUD initialized (mode: {mode.value})")

    def set_jarvis(self, jarvis):
        """Set JARVIS system"""
        self.jarvis = jarvis
        logger.info("Connected JARVIS system")

    def set_r5(self, r5):
        """Set R5 system"""
        self.r5 = r5
        logger.info("Connected R5 system")

    def set_marvin(self, marvin):
        """Set MARVIN system"""
        self.marvin = marvin
        logger.info("Connected MARVIN system")

    def update_context(
        self,
        location: Optional[str] = None,
        activity: Optional[str] = None,
        emotional_state: Optional[EmotionalState] = None,
        current_task: Optional[str] = None
    ) -> None:
        """Update buddy context"""
        with self.lock:
            if location:
                self.context.location = location
            if activity:
                self.context.activity = activity
            if emotional_state:
                self.context.emotional_state = emotional_state
            if current_task:
                self.context.current_task = current_task

            # Update time of day
            import datetime
            hour = datetime.datetime.now().hour
            if 5 <= hour < 12:
                self.context.time_of_day = 'morning'
            elif 12 <= hour < 17:
                self.context.time_of_day = 'afternoon'
            elif 17 <= hour < 21:
                self.context.time_of_day = 'evening'
            else:
                self.context.time_of_day = 'night'

            logger.debug(f"Updated context: {self.context}")

    def show(self, position: Optional[List[float]] = None) -> None:
        """Show JARVIS buddy in HUD"""
        with self.lock:
            if position:
                self.position = position
            self.is_visible = True
            logger.info("JARVIS buddy visible in HUD")

    def hide(self) -> None:
        """Hide JARVIS buddy"""
        with self.lock:
            self.is_visible = False
            logger.info("JARVIS buddy hidden")

    def speak(self, message: str, show_in_hud: bool = True) -> None:
        """
        JARVIS speaks (voice + optional HUD display).

        Args:
            message: Message to speak
            show_in_hud: Whether to show in HUD
        """
        # In production, this would:
        # 1. Use TTS to speak
        # 2. Display in HUD if show_in_hud
        # 3. Show avatar animation

        logger.info(f"JARVIS: {message}")

        if show_in_hud and self.is_visible:
            # Display in HUD
            self._display_in_hud(message)

    def listen(self, audio_input: bytes) -> Dict[str, Any]:
        """
        JARVIS listens (always-on voice recognition).

        Args:
            audio_input: Audio data

        Returns:
            Processed result with intent
        """
        # In production, this would:
        # 1. Process audio with speech recognition
        # 2. Understand intent with JARVIS
        # 3. Get context from R5
        # 4. Return result

        if self.jarvis:
            try:
                # Process with JARVIS
                result = self.jarvis.understand_voice(audio_input)
                return result
            except Exception as e:
                logger.error(f"Error processing voice: {e}")

        return {'intent': 'unknown', 'confidence': 0.0}

    def see(self, visual_input: bytes) -> Dict[str, Any]:
        """
        JARVIS sees (visual understanding).

        Args:
            visual_input: Image/video data

        Returns:
            Processed result with understanding
        """
        # In production, this would:
        # 1. Process image/video with vision AI
        # 2. Understand context
        # 3. Detect objects, text, people
        # 4. Return understanding

        if self.jarvis:
            try:
                result = self.jarvis.understand_vision(visual_input)
                return result
            except Exception as e:
                logger.error(f"Error processing vision: {e}")

        return {'understanding': 'unknown'}

    def help_proactively(self) -> List[BuddySuggestion]:
        """
        JARVIS proactively suggests help based on context.

        Returns:
            List of proactive suggestions
        """
        suggestions = []

        # Analyze context
        if self.context.emotional_state == EmotionalState.CONFUSED:
            suggestions.append(BuddySuggestion(
                type='help',
                message="I notice you might be confused. Can I help?",
                priority=7,
                action=lambda: self.speak("How can I assist you?")
            ))

        if self.context.emotional_state == EmotionalState.STRESSED:
            suggestions.append(BuddySuggestion(
                type='help',
                message="You seem stressed. Would you like me to help prioritize tasks?",
                priority=8,
                action=lambda: self.speak("I can help organize your tasks to reduce stress.")
            ))

        if self.context.current_task and 'error' in self.context.current_task.lower():
            suggestions.append(BuddySuggestion(
                type='help',
                message="I see you're working on an error. Would you like me to help debug?",
                priority=9,
                action=lambda: self.speak("I can help analyze the error and suggest fixes.")
            ))

        # Get suggestions from R5 knowledge
        if self.r5:
            try:
                r5_suggestions = self.r5.get_suggestions(self.context)
                suggestions.extend(r5_suggestions)
            except Exception as e:
                logger.debug(f"R5 suggestions error: {e}")

        # Sort by priority
        suggestions.sort(key=lambda x: x.priority, reverse=True)

        with self.lock:
            self.suggestions = suggestions[:5]  # Top 5

        return suggestions

    def start_proactive_mode(self) -> None:
        """Start proactive help mode"""
        self.running = True

        def proactive_loop():
            while self.running:
                try:
                    # Check for proactive help opportunities
                    suggestions = self.help_proactively()

                    # Show highest priority suggestion
                    if suggestions and self.mode == BuddyMode.ACTIVE:
                        top_suggestion = suggestions[0]
                        if top_suggestion.priority >= 7:
                            self.speak(top_suggestion.message)

                    time.sleep(30)  # Check every 30 seconds
                except Exception as e:
                    logger.error(f"Proactive mode error: {e}")
                    time.sleep(60)

        thread = threading.Thread(target=proactive_loop, daemon=True)
        thread.start()
        logger.info("Started proactive help mode")

    def stop_proactive_mode(self) -> None:
        """Stop proactive help mode"""
        self.running = False
        logger.info("Stopped proactive help mode")

    def _display_in_hud(self, content: str) -> None:
        """Display content in HUD (placeholder)"""
        # In production, this would render to AR display
        logger.debug(f"Displaying in HUD: {content}")

    def get_avatar_state(self) -> Dict[str, Any]:
        """Get current avatar state for HUD rendering"""
        return {
            'visible': self.is_visible,
            'position': self.position,
            'mode': self.mode.value,
            'context': {
                'location': self.context.location,
                'activity': self.context.activity,
                'emotional_state': self.context.emotional_state.value,
                'current_task': self.context.current_task
            },
            'suggestions_count': len(self.suggestions)
        }


def main():
    """Example usage"""
    buddy = JARVISBuddyHUD(mode=BuddyMode.ACTIVE)

    # Update context
    buddy.update_context(
        location='office',
        activity='coding',
        emotional_state=EmotionalState.FOCUSED,
        current_task='debugging error'
    )

    # Show buddy
    buddy.show(position=[0, 0, -1])

    # JARVIS speaks
    buddy.speak("Hello! I'm here to help. I notice you're debugging. Can I assist?")

    # Proactive help
    suggestions = buddy.help_proactively()
    print(f"Proactive suggestions: {len(suggestions)}")
    for suggestion in suggestions:
        print(f"  - {suggestion.message} (priority: {suggestion.priority})")

    # Start proactive mode
    buddy.start_proactive_mode()

    # Keep running
    try:
        time.sleep(60)
    except KeyboardInterrupt:
        buddy.stop_proactive_mode()


if __name__ == "__main__":


    main()