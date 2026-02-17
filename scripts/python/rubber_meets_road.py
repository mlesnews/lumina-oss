#!/usr/bin/env python3
"""
The Rubber Meets the Road - Meaning, Value, and Storytelling

"Either we are doing something meaningful, of value, or perhaps of none."

Consider:
- Robert Frost's "The Road Not Taken"
- Other great works of human poetry and literature
- The personal individual story
- Retelling to someone, anyone
- Sharing the joy of exploration
- Human adversity, struggles, and victories

As Deckard Cain profoundly invites:
"Stay awhile and listen..."
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum
import logging
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("RubberMeetsRoad")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class WorkValue(Enum):
    """Value of work"""
    MEANINGFUL = "meaningful"
    OF_VALUE = "of_value"
    PERHAPS_OF_NONE = "perhaps_of_none"
    UNKNOWN = "unknown"


class StoryType(Enum):
    """Type of story"""
    EXPLORATION = "exploration"
    ADVERSITY = "adversity"
    STRUGGLE = "struggle"
    VICTORY = "victory"
    JOY = "joy"
    PERSONAL = "personal"
    SHARED = "shared"


@dataclass
class MeaningfulWork:
    """Work that is meaningful, of value"""
    work_id: str
    description: str
    value: WorkValue
    meaning: str
    impact: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['value'] = self.value.value
        return data


@dataclass
class PersonalStory:
    """
    Personal individual story

    "It really has only ever been about the story,
    our personal individual story,
    and it's retelling to someone, anyone,
    to share the joy of exploration,
    of human adversity, our struggles and our victories."
    """
    story_id: str
    title: str
    story_type: StoryType
    content: str
    themes: List[str]  # exploration, adversity, struggle, victory, joy
    shared_with: List[str] = field(default_factory=list)  # Who it was shared with
    deckard_cain_invitation: bool = True  # "Stay awhile and listen..."
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data['story_type'] = self.story_type.value
        return data


@dataclass
class GreatWork:
    """Great work of human poetry and literature"""
    work_id: str
    title: str
    author: str
    type: str  # poetry, literature, etc.
    quote: str
    relevance: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class RubberMeetsRoad:
    """
    The Rubber Meets the Road - Meaning, Value, and Storytelling

    "Either we are doing something meaningful, of value, or perhaps of none."

    Consider:
    - Robert Frost's "The Road Not Taken"
    - Other great works of human poetry and literature
    - The personal individual story
    - Retelling to someone, anyone
    - Sharing the joy of exploration
    - Human adversity, struggles, and victories

    As Deckard Cain profoundly invites:
    "Stay awhile and listen..."
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize The Rubber Meets the Road"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("RubberMeetsRoad")

        # Meaningful work
        self.meaningful_works: List[MeaningfulWork] = []

        # Personal stories
        self.personal_stories: List[PersonalStory] = []

        # Great works
        self.great_works: List[GreatWork] = []

        # Data storage
        self.data_dir = self.project_root / "data" / "rubber_meets_road"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Initialize with great works
        self._initialize_great_works()

        self.logger.info("🛣️  The Rubber Meets the Road initialized")
        self.logger.info("   'Either we are doing something meaningful, of value, or perhaps of none.'")
        self.logger.info("   'It really has only ever been about the story'")
        self.logger.info("   'Stay awhile and listen...' - Deckard Cain")

    def _initialize_great_works(self):
        """Initialize with great works of poetry and literature"""
        # Robert Frost - The Road Not Taken
        self.great_works.append(GreatWork(
            work_id="frost_road_not_taken",
            title="The Road Not Taken",
            author="Robert Frost",
            type="poetry",
            quote="Two roads diverged in a yellow wood, And sorry I could not travel both...",
            relevance="The choice between paths, the road less traveled, meaning in decisions"
        ))

        # Deckard Cain - Diablo
        self.great_works.append(GreatWork(
            work_id="deckard_cain_listen",
            title="Deckard Cain's Invitation",
            author="Diablo (Blizzard)",
            type="literature",
            quote="Stay awhile and listen...",
            relevance="The invitation to share stories, to listen, to connect through narrative"
        ))

        self.logger.info(f"  📚 Initialized {len(self.great_works)} great works")

    def record_meaningful_work(self, description: str, meaning: str,
                              impact: str, value: WorkValue = WorkValue.MEANINGFUL) -> MeaningfulWork:
        """
        Record meaningful work

        "Either we are doing something meaningful, of value, or perhaps of none."
        """
        work = MeaningfulWork(
            work_id=f"work_{len(self.meaningful_works) + 1}_{int(datetime.now().timestamp())}",
            description=description,
            value=value,
            meaning=meaning,
            impact=impact
        )

        self.meaningful_works.append(work)
        self._save_meaningful_work(work)

        self.logger.info(f"  ✅ Meaningful work recorded: {description[:50]}...")
        self.logger.info(f"     Value: {value.value}")
        self.logger.info(f"     Meaning: {meaning[:50]}...")

        return work

    def record_personal_story(self, title: str, content: str,
                             story_type: StoryType, themes: List[str],
                             shared_with: Optional[List[str]] = None) -> PersonalStory:
        """
        Record personal individual story

        "It really has only ever been about the story,
        our personal individual story,
        and it's retelling to someone, anyone,
        to share the joy of exploration,
        of human adversity, our struggles and our victories."
        """
        story = PersonalStory(
            story_id=f"story_{len(self.personal_stories) + 1}_{int(datetime.now().timestamp())}",
            title=title,
            story_type=story_type,
            content=content,
            themes=themes,
            shared_with=shared_with or [],
            deckard_cain_invitation=True  # "Stay awhile and listen..."
        )

        self.personal_stories.append(story)
        self._save_personal_story(story)

        self.logger.info(f"  📖 Personal story recorded: {title}")
        self.logger.info(f"     Type: {story_type.value}")
        self.logger.info(f"     Themes: {', '.join(themes)}")
        self.logger.info(f"     'Stay awhile and listen...'")

        return story

    def add_great_work(self, title: str, author: str, work_type: str,
                      quote: str, relevance: str) -> GreatWork:
        """
        Add a great work of human poetry and literature
        """
        work = GreatWork(
            work_id=f"great_work_{len(self.great_works) + 1}_{int(datetime.now().timestamp())}",
            title=title,
            author=author,
            type=work_type,
            quote=quote,
            relevance=relevance
        )

        self.great_works.append(work)
        self._save_great_work(work)

        self.logger.info(f"  📚 Great work added: {title} by {author}")
        self.logger.info(f"     Relevance: {relevance[:50]}...")

        return work

    def get_philosophy(self) -> Dict[str, Any]:
        """
        Get the philosophy

        "Either we are doing something meaningful, of value, or perhaps of none."
        "It really has only ever been about the story"
        "Stay awhile and listen..."
        """
        return {
            "philosophy": "The rubber meets the road",
            "meaningful_work": "Either we are doing something meaningful, of value, or perhaps of none.",
            "storytelling": "It really has only ever been about the story, our personal individual story, and it's retelling to someone, anyone, to share the joy of exploration, of human adversity, our struggles and our victories.",
            "deckard_cain": "Stay awhile and listen...",
            "great_works_count": len(self.great_works),
            "meaningful_works_count": len(self.meaningful_works),
            "personal_stories_count": len(self.personal_stories),
            "themes": ["exploration", "adversity", "struggle", "victory", "joy", "personal", "shared"]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics"""
        meaningful_count = sum(1 for w in self.meaningful_works 
                              if w.value in [WorkValue.MEANINGFUL, WorkValue.OF_VALUE])
        perhaps_none_count = sum(1 for w in self.meaningful_works 
                                if w.value == WorkValue.PERHAPS_OF_NONE)

        story_types = {}
        for story in self.personal_stories:
            story_type = story.story_type.value
            story_types[story_type] = story_types.get(story_type, 0) + 1

        return {
            "total_meaningful_works": len(self.meaningful_works),
            "meaningful_or_valuable": meaningful_count,
            "perhaps_of_none": perhaps_none_count,
            "total_personal_stories": len(self.personal_stories),
            "story_types": story_types,
            "total_great_works": len(self.great_works),
            "rubber_meets_road": "Either we are doing something meaningful, of value, or perhaps of none."
        }

    def _save_meaningful_work(self, work: MeaningfulWork) -> None:
        try:
            """Save meaningful work"""
            work_file = self.data_dir / "meaningful_works" / f"{work.work_id}.json"
            work_file.parent.mkdir(parents=True, exist_ok=True)
            with open(work_file, 'w', encoding='utf-8') as f:
                json.dump(work.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_meaningful_work: {e}", exc_info=True)
            raise
    def _save_personal_story(self, story: PersonalStory) -> None:
        try:
            """Save personal story"""
            story_file = self.data_dir / "personal_stories" / f"{story.story_id}.json"
            story_file.parent.mkdir(parents=True, exist_ok=True)
            with open(story_file, 'w', encoding='utf-8') as f:
                json.dump(story.to_dict(), f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_personal_story: {e}", exc_info=True)
            raise
    def _save_great_work(self, work: GreatWork) -> None:
        try:
            """Save great work"""
            work_file = self.data_dir / "great_works" / f"{work.work_id}.json"
            work_file.parent.mkdir(parents=True, exist_ok=True)
            with open(work_file, 'w', encoding='utf-8') as f:
                json.dump(work.to_dict(), f, indent=2)


        except Exception as e:
            self.logger.error(f"Error in _save_great_work: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="The Rubber Meets the Road - Meaning, Value, and Storytelling")
    parser.add_argument("--record-work", nargs=4, metavar=("DESCRIPTION", "MEANING", "IMPACT", "VALUE"),
                       help="Record meaningful work (VALUE: meaningful, of_value, perhaps_of_none)")
    parser.add_argument("--record-story", nargs=4, metavar=("TITLE", "CONTENT", "TYPE", "THEMES"),
                       help="Record personal story (TYPE: exploration, adversity, struggle, victory, joy)")
    parser.add_argument("--add-great-work", nargs=5, metavar=("TITLE", "AUTHOR", "TYPE", "QUOTE", "RELEVANCE"),
                       help="Add great work of poetry/literature")
    parser.add_argument("--philosophy", action="store_true", help="Get philosophy")
    parser.add_argument("--statistics", action="store_true", help="Get statistics")
    parser.add_argument("--list-great-works", action="store_true", help="List great works")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    rubber_meets_road = RubberMeetsRoad()

    if args.record_work:
        description, meaning, impact, value_str = args.record_work
        value = WorkValue(value_str) if value_str in [v.value for v in WorkValue] else WorkValue.MEANINGFUL
        work = rubber_meets_road.record_meaningful_work(description, meaning, impact, value)
        if args.json:
            print(json.dumps(work.to_dict(), indent=2))
        else:
            print(f"\n✅ Meaningful Work Recorded")
            print(f"   Description: {work.description}")
            print(f"   Value: {work.value.value}")
            print(f"   Meaning: {work.meaning}")
            print(f"   Impact: {work.impact}")

    elif args.record_story:
        title, content, story_type_str, themes_str = args.record_story
        story_type = StoryType(story_type_str) if story_type_str in [s.value for s in StoryType] else StoryType.PERSONAL
        themes = themes_str.split(',') if themes_str else []
        story = rubber_meets_road.record_personal_story(title, content, story_type, themes)
        if args.json:
            print(json.dumps(story.to_dict(), indent=2))
        else:
            print(f"\n📖 Personal Story Recorded")
            print(f"   Title: {story.title}")
            print(f"   Type: {story.story_type.value}")
            print(f"   Themes: {', '.join(story.themes)}")
            print(f"   'Stay awhile and listen...'")

    elif args.add_great_work:
        title, author, work_type, quote, relevance = args.add_great_work
        work = rubber_meets_road.add_great_work(title, author, work_type, quote, relevance)
        if args.json:
            print(json.dumps(work.to_dict(), indent=2))
        else:
            print(f"\n📚 Great Work Added")
            print(f"   Title: {work.title}")
            print(f"   Author: {work.author}")
            print(f"   Quote: {work.quote[:100]}...")
            print(f"   Relevance: {work.relevance}")

    elif args.list_great_works:
        if args.json:
            print(json.dumps([w.to_dict() for w in rubber_meets_road.great_works], indent=2))
        else:
            print(f"\n📚 Great Works of Poetry and Literature")
            for work in rubber_meets_road.great_works:
                print(f"\n   {work.title} by {work.author}")
                print(f"   '{work.quote[:80]}...'")
                print(f"   Relevance: {work.relevance}")

    elif args.philosophy:
        philosophy = rubber_meets_road.get_philosophy()
        if args.json:
            print(json.dumps(philosophy, indent=2))
        else:
            print(f"\n🛣️  The Rubber Meets the Road - Philosophy")
            print(f"   {philosophy['meaningful_work']}")
            print(f"\n   Storytelling:")
            print(f"   {philosophy['storytelling']}")
            print(f"\n   {philosophy['deckard_cain']}")
            print(f"\n   Great Works: {philosophy['great_works_count']}")
            print(f"   Meaningful Works: {philosophy['meaningful_works_count']}")
            print(f"   Personal Stories: {philosophy['personal_stories_count']}")

    elif args.statistics:
        stats = rubber_meets_road.get_statistics()
        if args.json:
            print(json.dumps(stats, indent=2))
        else:
            print(f"\n📊 The Rubber Meets the Road - Statistics")
            print(f"   {stats['rubber_meets_road']}")
            print(f"\n   Meaningful Works: {stats['total_meaningful_works']}")
            print(f"   Meaningful or Valuable: {stats['meaningful_or_valuable']}")
            print(f"   Perhaps of None: {stats['perhaps_of_none']}")
            print(f"\n   Personal Stories: {stats['total_personal_stories']}")
            print(f"   Story Types: {stats['story_types']}")
            print(f"\n   Great Works: {stats['total_great_works']}")

    else:
        parser.print_help()
        print("\n🛣️  The Rubber Meets the Road - Meaning, Value, and Storytelling")
        print("   'Either we are doing something meaningful, of value, or perhaps of none.'")
        print("   'It really has only ever been about the story'")
        print("   'Stay awhile and listen...' - Deckard Cain")

