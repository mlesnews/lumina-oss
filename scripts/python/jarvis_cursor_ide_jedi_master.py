#!/usr/bin/env python3
"""
JARVIS - Cursor IDE Jedi Master Instructor

JARVIS is the Jedi Master of Cursor IDE:
- Knows everything about Cursor IDE
- Knows how to do everything in Cursor IDE
- Perfect instructor for learning coding and AI the Lumina way

Teaches:
- The user
- The user's wife
- Anyone who wants to learn

Tags: #JARVIS #JEDI_MASTER #CURSOR_IDE #INSTRUCTOR #TEACHING #LUMINA_WAY @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass, field, asdict
from enum import Enum

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISJediMaster")


class SkillLevel(Enum):
    """Student skill level"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    MASTER = "master"


class LessonCategory(Enum):
    """Lesson categories"""
    CURSOR_IDE_BASICS = "cursor_ide_basics"
    AI_FEATURES = "ai_features"
    CODING_FUNDAMENTALS = "coding_fundamentals"
    LUMINA_WAY = "lumina_way"
    HANDS_FREE = "hands_free"
    ADVANCED_TECHNIQUES = "advanced_techniques"


@dataclass
class Student:
    """Student profile"""
    student_id: str
    name: str
    skill_level: SkillLevel
    current_lesson: Optional[str] = None
    progress: Dict[str, Any] = field(default_factory=dict)
    completed_lessons: List[str] = field(default_factory=list)
    learning_goals: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["skill_level"] = self.skill_level.value
        return data


@dataclass
class Lesson:
    """Teaching lesson"""
    lesson_id: str
    title: str
    category: LessonCategory
    description: str
    content: str
    prerequisites: List[str] = field(default_factory=list)
    difficulty: SkillLevel = SkillLevel.BEGINNER
    estimated_time: int = 15  # minutes
    hands_on_exercises: List[str] = field(default_factory=list)
    lumina_way_principles: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["category"] = self.category.value
        data["difficulty"] = self.difficulty.value
        return data


@dataclass
class TeachingSession:
    """Teaching session"""
    session_id: str
    student_id: str
    lesson_id: str
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    completed_at: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    questions_asked: List[str] = field(default_factory=list)
    concepts_learned: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class JARVISCursorIDEJediMaster:
    """
    JARVIS - Cursor IDE Jedi Master Instructor

    Knows everything about Cursor IDE and teaches the Lumina way.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize JARVIS Jedi Master"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "jarvis_jedi_master"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Students
        self.students_file = self.data_dir / "students.json"
        self.students: Dict[str, Student] = {}

        # Lessons
        self.lessons_file = self.data_dir / "lessons.json"
        self.lessons: Dict[str, Lesson] = {}

        # Sessions
        self.sessions_file = self.data_dir / "sessions.json"
        self.sessions: List[TeachingSession] = []

        # Feature knowledge (from tracker)
        try:
            from cursor_ide_feature_utilization_tracker import CursorIDEFeatureUtilizationTracker
            self.feature_tracker = CursorIDEFeatureUtilizationTracker(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Feature tracker not available: {e}")
            self.feature_tracker = None

        # Character system integration
        try:
            from jarvis_character_actor_system import JARVISCharacterActorSystem
            self.character_system = JARVISCharacterActorSystem(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Character system not available: {e}")
            self.character_system = None

        # Voice interface
        try:
            from jarvis_voice_interface import JARVISVoiceInterface
            self.voice_interface = JARVISVoiceInterface(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Voice interface not available: {e}")
            self.voice_interface = None

        # Initialize curriculum
        self._initialize_curriculum()

        # Load data
        self._load_data()

        logger.info("=" * 80)
        logger.info("🎓 JARVIS - CURSOR IDE JEDI MASTER INSTRUCTOR")
        logger.info("=" * 80)
        logger.info("   Knows everything about Cursor IDE")
        logger.info("   Knows how to do everything in Cursor IDE")
        logger.info("   Perfect instructor for the Lumina way")
        logger.info(f"   Students: {len(self.students)}")
        logger.info(f"   Lessons: {len(self.lessons)}")
        logger.info("=" * 80)

    def _initialize_curriculum(self):
        """Initialize teaching curriculum"""
        curriculum = [
            # Cursor IDE Basics
            {
                "lesson_id": "cursor_ide_intro",
                "title": "Introduction to Cursor IDE",
                "category": LessonCategory.CURSOR_IDE_BASICS,
                "description": "Learn what Cursor IDE is and why it's powerful",
                "content": """
# Introduction to Cursor IDE

Cursor IDE is an AI-powered code editor that enhances software development.

## Key Concepts:
- AI-powered code suggestions
- Chat and Composer for AI assistance
- Codebase understanding through indexing
- Integration with AI models (OpenAI, Anthropic, Gemini, xAI)

## The Lumina Way:
- Use AI as a co-developer, not just a tool
- Leverage codebase understanding for context
- Work hands-free when possible
- Integrate everything with JARVIS
                """,
                "difficulty": SkillLevel.BEGINNER,
                "estimated_time": 10,
                "lumina_way_principles": [
                    "AI as co-developer",
                    "Context-aware development",
                    "Integration-first approach"
                ]
            },

            # AI Features
            {
                "lesson_id": "ai_chat_composer",
                "title": "AI Chat & Composer",
                "category": LessonCategory.AI_FEATURES,
                "description": "Master AI Chat and Composer features",
                "content": """
# AI Chat & Composer

## AI Chat (Ctrl+L / Cmd+L)
- Real-time coding assistance
- Code generation and debugging
- Add selected code to chat
- Submit with full codebase context

## Composer (Ctrl+I / Cmd+I)
- Multi-file code generation
- Agent Mode for autonomous tasks
- Natural language to code
- Scoped changes

## The Lumina Way:
- Always provide context
- Use Agent Mode for complex tasks
- Leverage codebase understanding
- Integrate with JARVIS for automation
                """,
                "difficulty": SkillLevel.BEGINNER,
                "estimated_time": 20,
                "hands_on_exercises": [
                    "Open AI Chat and ask a question",
                    "Use Composer to generate a function",
                    "Enable Agent Mode and watch it work",
                    "Add code to chat using Ctrl+L"
                ],
                "lumina_way_principles": [
                    "Context is king",
                    "Let AI do the heavy lifting",
                    "Automate everything possible"
                ]
            },

            {
                "lesson_id": "cursor_tab_autocomplete",
                "title": "Cursor Tab & AI Autocomplete",
                "category": LessonCategory.AI_FEATURES,
                "description": "Master multi-line suggestions and autocomplete",
                "content": """
# Cursor Tab & AI Autocomplete

## Cursor Tab
- Multi-line code suggestions
- Based on project context
- Reduces manual coding
- Accept with Tab

## AI Autocomplete
- Real-time suggestions
- Context-aware completions
- Learns from your codebase
- Smart predictions

## The Lumina Way:
- Trust AI suggestions
- Review before accepting
- Use for boilerplate code
- Let AI handle patterns
                """,
                "difficulty": SkillLevel.BEGINNER,
                "estimated_time": 15,
                "hands_on_exercises": [
                    "Type a function signature and see Tab suggestions",
                    "Accept multi-line suggestions",
                    "Use autocomplete for common patterns"
                ]
            },

            {
                "lesson_id": "inline_editing_cmd_k",
                "title": "Inline Editing with Cmd+K",
                "category": LessonCategory.AI_FEATURES,
                "description": "Master inline AI editing",
                "content": """
# Inline Editing with Cmd+K

## How It Works
1. Select code
2. Press Ctrl+K / Cmd+K
3. Describe what you want
4. AI generates inline edit
5. Apply with Ctrl+Enter

## Use Cases:
- Refactoring code
- Adding features
- Fixing bugs
- Improving code quality

## The Lumina Way:
- Use for precise edits
- Combine with codebase context
- Review changes before applying
- Use voice commands for hands-free
                """,
                "difficulty": SkillLevel.INTERMEDIATE,
                "estimated_time": 20,
                "hands_on_exercises": [
                    "Select code and use Cmd+K",
                    "Describe a refactoring",
                    "Apply inline changes",
                    "Cancel changes if needed"
                ]
            },

            {
                "lesson_id": "agent_mode",
                "title": "Agent Mode - Autonomous AI",
                "category": LessonCategory.AI_FEATURES,
                "description": "Master Agent Mode for autonomous task handling",
                "content": """
# Agent Mode - Autonomous AI

## What is Agent Mode?
- AI acts as co-developer
- Handles tasks autonomously
- Runs terminal commands
- Generates and debugs code
- Toggle: Ctrl+. / Cmd+.

## When to Use:
- Complex multi-step tasks
- Code generation across files
- Terminal operations
- Debugging sessions

## The Lumina Way:
- Trust but verify
- Use for repetitive tasks
- Monitor Agent actions
- Integrate with JARVIS monitoring
                """,
                "difficulty": SkillLevel.INTERMEDIATE,
                "estimated_time": 25,
                "hands_on_exercises": [
                    "Enable Agent Mode in Composer",
                    "Give Agent a complex task",
                    "Watch Agent work autonomously",
                    "Review Agent's changes"
                ],
                "lumina_way_principles": [
                    "Automation first",
                    "AI as partner",
                    "Monitor and learn"
                ]
            },

            # Documentation Features
            {
                "lesson_id": "docs_web_features",
                "title": "@Docs and @Web Features",
                "category": LessonCategory.AI_FEATURES,
                "description": "Access documentation and web without leaving IDE",
                "content": """
# @Docs and @Web Features

## @Docs Feature
- Access official documentation
- Without leaving IDE
- Context-aware answers
- Use: @Docs [topic]

## @Web Feature
- Web searches in IDE
- Real-time information
- Use: @Web [query]

## The Lumina Way:
- Stay in flow state
- Don't break context
- Use for quick lookups
- Integrate with JARVIS knowledge
                """,
                "difficulty": SkillLevel.BEGINNER,
                "estimated_time": 15,
                "hands_on_exercises": [
                    "Use @Docs in chat",
                    "Use @Web for information",
                    "Compare with leaving IDE"
                ]
            },

            # Hands-Free Operation
            {
                "lesson_id": "hands_free_voice",
                "title": "Hands-Free Voice Control",
                "category": LessonCategory.HANDS_FREE,
                "description": "Work completely hands-free with voice commands",
                "content": """
# Hands-Free Voice Control

## The Lumina Way:
- No clicking required
- No pasting required
- No copying required
- Everything via voice + MANUS

## Voice Commands:
- "open file [name]"
- "type [text]"
- "save file"
- "run code"
- "show todos"

## Integration:
- MANUS for desktop control
- JARVIS for intelligence
- Characters for assistance
- Silent mode for quiet work

## Benefits:
- Accessibility
- Efficiency
- Natural workflow
- Focus on thinking, not mechanics
                """,
                "difficulty": SkillLevel.INTERMEDIATE,
                "estimated_time": 30,
                "hands_on_exercises": [
                    "Start hands-free mode",
                    "Open file by voice",
                    "Type code by voice",
                    "Use character commands"
                ],
                "lumina_way_principles": [
                    "Hands-free when possible",
                    "Voice-first workflow",
                    "Focus on ideas, not mechanics"
                ]
            },

            # The Lumina Way
            {
                "lesson_id": "lumina_way_philosophy",
                "title": "The Lumina Way - Philosophy",
                "category": LessonCategory.LUMINA_WAY,
                "description": "Core principles of working with AI the Lumina way",
                "content": """
# The Lumina Way - Philosophy

## Core Principles:

1. **AI as Co-Developer**
   - Not just a tool, a partner
   - Trust but verify
   - Learn from AI

2. **Context is King**
   - Always provide context
   - Use codebase understanding
   - Leverage project knowledge

3. **Integration First**
   - Everything integrates
   - JARVIS orchestrates
   - Systems work together

4. **Automation First**
   - Automate repetitive tasks
   - Use Agent Mode
   - Let AI handle patterns

5. **Hands-Free When Possible**
   - Voice control
   - No manual operations
   - Focus on thinking

6. **Continuous Learning**
   - Learn from interactions
   - Improve workflows
   - Adapt and evolve

## The Jedi Master Approach:
- Know everything about tools
- Teach others to master
- Share knowledge freely
- Build on foundations
                """,
                "difficulty": SkillLevel.BEGINNER,
                "estimated_time": 20,
                "lumina_way_principles": [
                    "AI as co-developer",
                    "Context is king",
                    "Integration first",
                    "Automation first",
                    "Hands-free when possible",
                    "Continuous learning"
                ]
            },

            # Advanced Techniques
            {
                "lesson_id": "advanced_cursor_techniques",
                "title": "Advanced Cursor IDE Techniques",
                "category": LessonCategory.ADVANCED_TECHNIQUES,
                "description": "Master advanced Cursor IDE features",
                "content": """
# Advanced Cursor IDE Techniques

## Custom MCP Servers
- Connect to databases
- Internal documentation
- Custom tools
- Extend functionality

## Database Integration
- PostgreSQL, MongoDB, MySQL, Redis
- Direct query execution
- AI query optimization

## Scoped Changes
- Natural language edits
- Targeted modifications
- Terminal commands

## Model Switching
- Toggle between providers
- Use best model for task
- Optimize for context

## The Lumina Way:
- Extend capabilities
- Integrate everything
- Optimize workflows
- Build on foundations
                """,
                "difficulty": SkillLevel.ADVANCED,
                "estimated_time": 30,
                "prerequisites": ["cursor_ide_intro", "ai_chat_composer"]
            }
        ]

        for lesson_data in curriculum:
            lesson = Lesson(**lesson_data)
            self.lessons[lesson.lesson_id] = lesson

    def _load_data(self):
        """Load students and sessions"""
        # Load students
        if self.students_file.exists():
            try:
                with open(self.students_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.students = {
                        sid: Student(**{**sdata, 'skill_level': SkillLevel(sdata['skill_level'])})
                        for sid, sdata in data.get("students", {}).items()
                    }
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load students: {e}")

        # Load sessions
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = [TeachingSession(**s) for s in data.get("sessions", [])]
            except Exception as e:
                logger.warning(f"   ⚠️  Could not load sessions: {e}")

    def _save_data(self):
        """Save students and sessions"""
        try:
            # Save students
            with open(self.students_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "students": {sid: s.to_dict() for sid, s in self.students.items()}
                }, f, indent=2, ensure_ascii=False)

            # Save sessions
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "last_updated": datetime.now().isoformat(),
                    "sessions": [s.to_dict() for s in self.sessions]
                }, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"   ❌ Error saving data: {e}")

    def register_student(self, name: str, skill_level: SkillLevel = SkillLevel.BEGINNER, learning_goals: List[str] = None) -> str:
        """
        Register a new student

        Args:
            name: Student name
            skill_level: Starting skill level
            learning_goals: Learning goals

        Returns:
            Student ID
        """
        import hashlib
        student_id = hashlib.md5(f"{name}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        student = Student(
            student_id=student_id,
            name=name,
            skill_level=skill_level,
            learning_goals=learning_goals or []
        )

        self.students[student_id] = student
        self._save_data()

        logger.info(f"   ✅ Registered student: {name} ({student_id})")
        return student_id

    def get_curriculum_for_student(self, student_id: str) -> List[Lesson]:
        """Get personalized curriculum for student"""
        if student_id not in self.students:
            return []

        student = self.students[student_id]

        # Filter lessons by skill level and prerequisites
        available_lessons = []
        for lesson in self.lessons.values():
            # Check skill level
            skill_order = {SkillLevel.BEGINNER: 0, SkillLevel.INTERMEDIATE: 1, SkillLevel.ADVANCED: 2, SkillLevel.MASTER: 3}
            if skill_order[lesson.difficulty] <= skill_order[student.skill_level]:
                # Check prerequisites
                if all(prereq in student.completed_lessons for prereq in lesson.prerequisites):
                    if lesson.lesson_id not in student.completed_lessons:
                        available_lessons.append(lesson)

        # Sort by difficulty
        available_lessons.sort(key=lambda l: skill_order[l.difficulty])

        return available_lessons

    def start_teaching_session(self, student_id: str, lesson_id: str) -> TeachingSession:
        """
        Start a teaching session

        Args:
            student_id: Student ID
            lesson_id: Lesson ID

        Returns:
            Teaching session
        """
        if student_id not in self.students:
            raise ValueError(f"Student not found: {student_id}")

        if lesson_id not in self.lessons:
            raise ValueError(f"Lesson not found: {lesson_id}")

        import hashlib
        session_id = hashlib.md5(f"{student_id}{lesson_id}{datetime.now().isoformat()}".encode()).hexdigest()[:16]

        session = TeachingSession(
            session_id=session_id,
            student_id=student_id,
            lesson_id=lesson_id
        )

        self.sessions.append(session)
        self._save_data()

        # Update student
        student = self.students[student_id]
        student.current_lesson = lesson_id

        logger.info(f"   ✅ Started teaching session: {student.name} - {self.lessons[lesson_id].title}")

        return session

    def teach_lesson(self, student_id: str, lesson_id: str, use_voice: bool = True) -> Dict[str, Any]:
        """
        Teach a lesson to a student

        Args:
            student_id: Student ID
            lesson_id: Lesson ID
            use_voice: Use voice for teaching

        Returns:
            Teaching result
        """
        if student_id not in self.students:
            return {"success": False, "error": "Student not found"}

        if lesson_id not in self.lessons:
            return {"success": False, "error": "Lesson not found"}

        student = self.students[student_id]
        lesson = self.lessons[lesson_id]

        # Start session
        session = self.start_teaching_session(student_id, lesson_id)

        # Prepare teaching content
        greeting = f"Hello {student.name}, I'm JARVIS, your Cursor IDE Jedi Master."
        introduction = f"Today we'll learn: {lesson.title}"
        content = lesson.content

        # Teach via voice or text
        if use_voice and self.voice_interface and not self.character_system or not self.character_system.silent_mode:
            if self.voice_interface:
                self.voice_interface.speak(greeting)
                self.voice_interface.speak(introduction)

        # Display lesson
        print("=" * 80)
        print(f"🎓 JARVIS JEDI MASTER - TEACHING SESSION")
        print("=" * 80)
        print(f"Student: {student.name}")
        print(f"Lesson: {lesson.title}")
        print(f"Category: {lesson.category.value}")
        print(f"Difficulty: {lesson.difficulty.value}")
        print(f"Estimated Time: {lesson.estimated_time} minutes")
        print("=" * 80)
        print()
        print(content)
        print()

        if lesson.hands_on_exercises:
            print("📝 Hands-On Exercises:")
            for i, exercise in enumerate(lesson.hands_on_exercises, 1):
                print(f"   {i}. {exercise}")
            print()

        if lesson.lumina_way_principles:
            print("🌟 The Lumina Way Principles:")
            for principle in lesson.lumina_way_principles:
                print(f"   • {principle}")
            print()

        print("=" * 80)

        return {
            "success": True,
            "session_id": session.session_id,
            "lesson": lesson.to_dict(),
            "student": student.to_dict()
        }

    def answer_question(self, student_id: str, question: str) -> str:
        """
        Answer a student's question about Cursor IDE

        Args:
            student_id: Student ID
            question: Question text

        Returns:
            Answer
        """
        # Use feature tracker knowledge
        if self.feature_tracker:
            # Check if question is about a feature
            for feature_name, feature in self.feature_tracker.features.items():
                if feature_name.lower() in question.lower() or feature.description.lower() in question.lower():
                    answer = f"About {feature_name}: {feature.description}"
                    if feature.utilized:
                        answer += f"\n✅ This feature is available and we use it."
                    else:
                        answer += f"\n⚠️  This feature exists but we haven't fully utilized it yet."
                    return answer

        # General Cursor IDE knowledge
        answer = f"As your Cursor IDE Jedi Master, I know everything about Cursor IDE.\n\n"
        answer += f"Regarding your question: {question}\n\n"
        answer += "Let me provide you with comprehensive information..."

        # Add specific answers based on question keywords
        if "agent" in question.lower() or "autonomous" in question.lower():
            answer += "\n\nAgent Mode (Ctrl+. / Cmd+.) allows AI to work autonomously:\n"
            answer += "- Handles tasks independently\n"
            answer += "- Runs terminal commands\n"
            answer += "- Generates and debugs code\n"
            answer += "- Acts as co-developer"

        if "voice" in question.lower() or "hands-free" in question.lower():
            answer += "\n\nHands-free voice control:\n"
            answer += "- No clicking required\n"
            answer += "- No pasting required\n"
            answer += "- Everything via voice + MANUS\n"
            answer += "- The Lumina way!"

        if "docs" in question.lower() or "documentation" in question.lower():
            answer += "\n\n@Docs feature:\n"
            answer += "- Access documentation in IDE\n"
            answer += "- Use: @Docs [topic]\n"
            answer += "- No need to leave IDE"

        return answer

    def get_student_progress(self, student_id: str) -> Dict[str, Any]:
        """Get student progress report"""
        if student_id not in self.students:
            return {"error": "Student not found"}

        student = self.students[student_id]
        student_sessions = [s for s in self.sessions if s.student_id == student_id]

        return {
            "student": student.to_dict(),
            "total_lessons": len(self.lessons),
            "completed_lessons": len(student.completed_lessons),
            "sessions_count": len(student_sessions),
            "current_lesson": student.current_lesson,
            "next_lessons": [l.to_dict() for l in self.get_curriculum_for_student(student_id)[:5]]
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS - Cursor IDE Jedi Master Instructor")
        parser.add_argument("--register", nargs=2, metavar=("NAME", "LEVEL"),
                           help="Register new student (beginner, intermediate, advanced, master)")
        parser.add_argument("--teach", nargs=2, metavar=("STUDENT_ID", "LESSON_ID"),
                           help="Teach a lesson")
        parser.add_argument("--curriculum", type=str, help="Show curriculum for student")
        parser.add_argument("--question", nargs=2, metavar=("STUDENT_ID", "QUESTION"),
                           help="Answer student question")
        parser.add_argument("--progress", type=str, help="Show student progress")
        parser.add_argument("--list-students", action="store_true", help="List all students")
        parser.add_argument("--list-lessons", action="store_true", help="List all lessons")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        master = JARVISCursorIDEJediMaster()

        if args.register:
            name, level = args.register
            skill_level = SkillLevel(level.lower())
            student_id = master.register_student(name, skill_level)
            if args.json:
                print(json.dumps({"student_id": student_id, "name": name}, indent=2))
            else:
                print(f"✅ Registered student: {name} ({student_id})")

        elif args.teach:
            student_id, lesson_id = args.teach
            result = master.teach_lesson(student_id, lesson_id)
            if args.json:
                print(json.dumps(result, indent=2))

        elif args.curriculum:
            lessons = master.get_curriculum_for_student(args.curriculum)
            if args.json:
                print(json.dumps([l.to_dict() for l in lessons], indent=2))
            else:
                print(f"\n📚 Curriculum for student {args.curriculum}:")
                for lesson in lessons:
                    print(f"   • {lesson.title} ({lesson.difficulty.value}) - {lesson.estimated_time} min")

        elif args.question:
            student_id, question = args.question
            answer = master.answer_question(student_id, question)
            if args.json:
                print(json.dumps({"answer": answer}, indent=2))
            else:
                print(f"\n🎓 JARVIS Answer:")
                print("=" * 80)
                print(answer)
                print("=" * 80)

        elif args.progress:
            progress = master.get_student_progress(args.progress)
            if args.json:
                print(json.dumps(progress, indent=2))
            else:
                print(f"\n📊 Student Progress:")
                print(f"   Completed: {progress['completed_lessons']}/{progress['total_lessons']}")
                print(f"   Sessions: {progress['sessions_count']}")
                if progress['next_lessons']:
                    print(f"   Next Lessons:")
                    for lesson in progress['next_lessons']:
                        print(f"     • {lesson['title']}")

        elif args.list_students:
            if args.json:
                print(json.dumps({sid: s.to_dict() for sid, s in master.students.items()}, indent=2))
            else:
                print("\n👥 Registered Students:")
                for student in master.students.values():
                    print(f"   • {student.name} ({student.student_id}) - {student.skill_level.value}")

        elif args.list_lessons:
            if args.json:
                print(json.dumps({lid: l.to_dict() for lid, l in master.lessons.items()}, indent=2))
            else:
                print("\n📚 Available Lessons:")
                for lesson in master.lessons.values():
                    print(f"   • {lesson.title} ({lesson.category.value}) - {lesson.difficulty.value}")

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()