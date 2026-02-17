#!/usr/bin/env python3
"""
Lumina Core Memory System

Maintains core memories that guide Lumina's development.
Prevents falling in love with tools and keeps us agile.

Tags: #LUMINA #CORE_MEMORY #TOOL_AGNOSTICISM #AGILITY @JARVIS @LUMINA
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("LuminaCoreMemory")


class MemoryPriority(Enum):
    """Priority levels for core memories"""
    CRITICAL = 'critical'  # Must remember always
    HIGH = 'high'  # Important, check frequently
    MEDIUM = 'medium'  # Good to remember
    LOW = 'low'  # Nice to remember


@dataclass
class CoreMemory:
    """A core memory that guides Lumina development"""
    id: str
    title: str
    content: str
    priority: MemoryPriority
    created: datetime
    last_reminded: Optional[datetime] = None
    reminder_interval: Optional[timedelta] = None
    tags: List[str] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.last_reminded is None:
            self.last_reminded = self.created


class LuminaCoreMemory:
    """
    Core Memory System for Lumina

    Maintains critical memories that guide development:
    - Tool agnosticism
    - Principles over implementation
    - Agility and flexibility
    - Competitive advantage
    """

    def __init__(self):
        self.memories: Dict[str, CoreMemory] = {}
        self._initialize_core_memories()
        logger.info("🧠 Lumina Core Memory System initialized")

    def _initialize_core_memories(self) -> None:
        """Initialize core memories"""
        # Core Memory: Tool Agnosticism
        self.add_memory(
            CoreMemory(
                id='tool_agnosticism',
                title='Tool Agnosticism',
                content=(
                    "OS, frameworks, infrastructure stacks are just TOOLS - "
                    "methods to achieve our means, not the ends themselves. "
                    "This enables agility, flexibility, and the ability to pivot quickly "
                    "to outmaneuver industry behemoths and titan companies."
                ),
                priority=MemoryPriority.CRITICAL,
                created=datetime.now(),
                reminder_interval=timedelta(days=1),  # Daily reminder
                tags=['tool_agnosticism', 'agility', 'flexibility', 'competitive_advantage']
            )
        )

        # Core Memory: Principles Over Implementation
        self.add_memory(
            CoreMemory(
                id='principles_over_implementation',
                title='Principles Over Implementation',
                content=(
                    "Principles define what Lumina IS, not what it USES. "
                    "Stay true to the spirit, flexible with the implementation. "
                    "Don't fall in love with specific technologies."
                ),
                priority=MemoryPriority.CRITICAL,
                created=datetime.now(),
                reminder_interval=timedelta(days=7),  # Weekly reminder
                tags=['principles', 'flexibility', 'spirit']
            )
        )

        # Core Memory: Competitive Advantage
        self.add_memory(
            CoreMemory(
                id='competitive_advantage',
                title='Competitive Advantage Through Agility',
                content=(
                    "Industry giants are slow to pivot (legacy systems, sunk costs). "
                    "Lumina stays agile and light. We can outmaneuver them by: "
                    "adopting better tools faster, pivoting when needed, "
                    "staying light and flexible, not being locked into anything."
                ),
                priority=MemoryPriority.HIGH,
                created=datetime.now(),
                reminder_interval=timedelta(days=7),  # Weekly reminder
                tags=['competitive_advantage', 'agility', 'pivot']
            )
        )

    def add_memory(self, memory: CoreMemory) -> None:
        """Add a core memory"""
        self.memories[memory.id] = memory
        logger.info(f"Added core memory: {memory.title}")

    def get_memory(self, memory_id: str) -> Optional[CoreMemory]:
        """Get a core memory by ID"""
        return self.memories.get(memory_id)

    def get_all_memories(self, priority: Optional[MemoryPriority] = None) -> List[CoreMemory]:
        """Get all memories, optionally filtered by priority"""
        memories = list(self.memories.values())
        if priority:
            memories = [m for m in memories if m.priority == priority]
        return sorted(memories, key=lambda m: m.priority.value, reverse=True)

    def get_critical_memories(self) -> List[CoreMemory]:
        """Get all critical memories"""
        return self.get_all_memories(MemoryPriority.CRITICAL)

    def check_reminders(self) -> List[CoreMemory]:
        """
        Check which memories need reminding.

        Returns:
            List of memories that need reminding
        """
        now = datetime.now()
        reminders = []

        for memory in self.memories.values():
            if memory.reminder_interval:
                time_since_reminder = now - memory.last_reminded
                if time_since_reminder >= memory.reminder_interval:
                    reminders.append(memory)

        return reminders

    def remind(self, memory_id: str) -> Optional[str]:
        """
        Get reminder for a memory.

        Args:
            memory_id: Memory ID to remind

        Returns:
            Reminder content
        """
        memory = self.memories.get(memory_id)
        if memory:
            memory.last_reminded = datetime.now()
            logger.info(f"Reminded: {memory.title}")
            return f"🧠 {memory.title}: {memory.content}"
        return None

    def check_tool_attachment(self, tool_name: str) -> Dict[str, Any]:
        """
        Check if we're becoming emotionally attached to a tool.

        Args:
            tool_name: Name of tool to check

        Returns:
            Assessment of attachment risk
        """
        assessment = {
            'tool': tool_name,
            'at_risk': False,
            'warnings': [],
            'recommendations': []
        }

        # Check for signs of attachment
        # In production, this would analyze code, documentation, discussions

        # Warning signs
        warning_signs = [
            f"Hard-coded references to {tool_name}",
            f"Emotional language about {tool_name}",
            f"Resistance to replacing {tool_name}",
            f"{tool_name} mentioned as 'the only way'"
        ]

        assessment['warnings'] = warning_signs
        assessment['recommendations'] = [
            "Remember: Tools are just tools",
            "Create abstraction layer",
            "Consider alternatives",
            "Stay flexible"
        ]

        return assessment

    def get_daily_reminder(self) -> str:
        """Get daily reminder of core memories"""
        critical = self.get_critical_memories()
        reminders = []

        for memory in critical:
            reminders.append(f"🧠 {memory.title}: {memory.content}")

        return "\n\n".join(reminders)

    def validate_decision(
        self,
        decision: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate a decision against core memories.

        Args:
            decision: Decision to validate

        Returns:
            Validation result
        """
        result = {
            'valid': True,
            'warnings': [],
            'recommendations': []
        }

        # Check tool agnosticism
        tool_agnosticism = self.get_memory('tool_agnosticism')
        if tool_agnosticism:
            # Check if decision involves tools
            if decision.get('involves_tools'):
                # Check for emotional attachment
                if decision.get('emotionally_attached'):
                    result['warnings'].append(
                        f"⚠️  {tool_agnosticism.title}: "
                        "Decision shows emotional attachment to tools"
                    )
                    result['valid'] = False

                # Check for lock-in
                if decision.get('locks_us_in'):
                    result['warnings'].append(
                        f"⚠️  {tool_agnosticism.title}: "
                        "Decision locks us into specific tools"
                    )
                    result['valid'] = False

                # Check for pivot ability
                if not decision.get('can_pivot'):
                    result['warnings'].append(
                        f"⚠️  {tool_agnosticism.title}: "
                        "Decision doesn't allow easy pivoting"
                    )
                    result['recommendations'].append(
                        "Consider abstraction layer for flexibility"
                    )

        return result


def main():
    """Example usage"""
    core_memory = LuminaCoreMemory()

    # Get critical memories
    print("CRITICAL MEMORIES")
    print("=" * 80)
    for memory in core_memory.get_critical_memories():
        print(f"\n{memory.title}")
        print(f"  {memory.content}")
        print(f"  Tags: {', '.join(memory.tags)}")

    # Daily reminder
    print("\n\nDAILY REMINDER")
    print("=" * 80)
    print(core_memory.get_daily_reminder())

    # Check tool attachment
    print("\n\nTOOL ATTACHMENT CHECK")
    print("=" * 80)
    assessment = core_memory.check_tool_attachment("Ollama")
    print(f"Tool: {assessment['tool']}")
    print(f"Warnings: {len(assessment['warnings'])}")
    for warning in assessment['warnings']:
        print(f"  ⚠️  {warning}")

    # Validate decision
    print("\n\nDECISION VALIDATION")
    print("=" * 80)
    decision = {
        'involves_tools': True,
        'emotionally_attached': False,
        'locks_us_in': False,
        'can_pivot': True
    }
    validation = core_memory.validate_decision(decision)
    status = "✅" if validation['valid'] else "❌"
    print(f"{status} Decision is {'valid' if validation['valid'] else 'invalid'}")
    if validation['warnings']:
        for warning in validation['warnings']:
            print(f"  {warning}")


if __name__ == "__main__":


    main()