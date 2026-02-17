#!/usr/bin/env python3
"""
AI-Human Collaboration Therapy - PODCAST STYLE ROUNDTABLE

Third-person podcast style roundtable discussion.
Host moderates conversation between AI and Human participants.
Recorded and archived like a podcast episode.

Format:
- Host introduction
- Roundtable discussion
- Third-person observations
- Segments and breaks
- Outro and summary

Tags: #COLLAB #THERAPY #PODCAST #ROUNDTABLE #THIRD_PERSON #JARVIS @JARVIS @TEAM
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("AIHumanCollabTherapyPodcast")

# Import base therapy and voice
try:
    from ai_human_collab_therapy import AIHumanCollabTherapy, TherapySession, SessionType
    from ai_human_collab_therapy_voice import AIHumanCollabTherapyVoice
    THERAPY_AVAILABLE = True
except ImportError:
    THERAPY_AVAILABLE = False
    logger.warning("Base therapy systems not available")


@dataclass
class PodcastEpisode:
    """A podcast episode record"""
    episode_id: str
    episode_number: int
    title: str
    timestamp: str
    host: str = "JARVIS Host"
    participants: List[str] = field(default_factory=lambda: ["AI", "Human"])
    segments: List[Dict[str, Any]] = field(default_factory=list)
    transcript: List[Dict[str, Any]] = field(default_factory=list)
    third_person_observations: List[str] = field(default_factory=list)
    summary: str = ""
    duration_minutes: float = 0.0
    tags: List[str] = field(default_factory=list)


class AIHumanCollabTherapyPodcast:
    """
    Podcast-Style Roundtable Therapy

    Third-person podcast format with host moderating
    AI and Human participants in roundtable discussion.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize podcast therapy system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "ai_human_therapy_podcast"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.episodes_dir = self.data_dir / "episodes"
        self.episodes_dir.mkdir(parents=True, exist_ok=True)

        self.transcripts_dir = self.data_dir / "transcripts"
        self.transcripts_dir.mkdir(parents=True, exist_ok=True)

        # Initialize base systems
        if THERAPY_AVAILABLE:
            self.base_therapy = AIHumanCollabTherapy(project_root=project_root)
            self.voice_therapy = AIHumanCollabTherapyVoice(project_root=project_root)
        else:
            self.base_therapy = None
            self.voice_therapy = None

        # Episode counter
        self.episode_counter_file = self.data_dir / "episode_counter.json"
        self.episode_number = self._load_episode_counter()

        logger.info("✅ Podcast-Style Roundtable Therapy initialized")
        logger.info("   Third-person podcast format with host moderation")

    def _load_episode_counter(self) -> int:
        """Load episode counter"""
        if self.episode_counter_file.exists():
            try:
                with open(self.episode_counter_file, 'r') as f:
                    data = json.load(f)
                    return data.get("episode_number", 1)
            except:
                return 1
        return 1

    def _save_episode_counter(self):
        try:
            """Save episode counter"""
            with open(self.episode_counter_file, 'w') as f:
                json.dump({"episode_number": self.episode_number + 1}, f)

        except Exception as e:
            self.logger.error(f"Error in _save_episode_counter: {e}", exc_info=True)
            raise
    def host_introduction(self, episode: PodcastEpisode) -> str:
        """Host introduction segment"""
        intro = f"""
Welcome to the AI-Human Collaboration Therapy Podcast, Episode {episode.episode_number}.

I'm {episode.host}, your host for today's roundtable discussion.

Today we're joined by our regular participants: {', '.join(episode.participants)}.

In this episode, we'll be exploring our collaboration, working through issues together,
and building a better working relationship. This is a safe space for honest conversation.

Let's begin.
"""
        return intro.strip()

    def third_person_observation(self, observation: str, timestamp: str = None) -> Dict[str, Any]:
        """Create third-person observation"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        return {
            "timestamp": timestamp,
            "type": "observation",
            "text": observation,
            "perspective": "third_person"
        }

    def participant_speaks(self, participant: str, text: str, timestamp: str = None) -> Dict[str, Any]:
        """Record participant speaking"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        return {
            "timestamp": timestamp,
            "type": "speech",
            "participant": participant,
            "text": text
        }

    def host_moderates(self, text: str, timestamp: str = None) -> Dict[str, Any]:
        """Host moderation/commentary"""
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        return {
            "timestamp": timestamp,
            "type": "moderation",
            "participant": "Host",
            "text": text
        }

    def record_roundtable_session(self, 
                                  ai_reflection: Optional[TherapySession] = None,
                                  human_feedback: Optional[TherapySession] = None,
                                  title: Optional[str] = None) -> PodcastEpisode:
        """
        Record a roundtable therapy session as a podcast episode

        Third-person podcast format with host moderating.
        """
        logger.info("="*80)
        logger.info("🎙️  PODCAST ROUNDTABLE SESSION")
        logger.info("="*80)

        # Create episode
        episode_id = f"episode_{self.episode_number:04d}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if title is None:
            title = f"AI-Human Collaboration Therapy - Episode {self.episode_number}"

        episode = PodcastEpisode(
            episode_id=episode_id,
            episode_number=self.episode_number,
            title=title,
            timestamp=datetime.now().isoformat(),
            tags=["therapy", "collaboration", "roundtable", "podcast"]
        )

        transcript = []

        # Host Introduction
        intro = self.host_introduction(episode)
        transcript.append(self.host_moderates(intro))
        episode.segments.append({
            "segment_type": "introduction",
            "content": intro,
            "timestamp": datetime.now().isoformat()
        })

        # Third-person observation
        observation = "The host welcomes the participants. The atmosphere is professional yet warm, creating a safe space for honest dialogue."
        transcript.append(self.third_person_observation(observation))
        episode.third_person_observations.append(observation)

        # Segment 1: AI Self-Reflection (Roundtable)
        if ai_reflection:
            segment_start = datetime.now().isoformat()
            transcript.append(self.host_moderates("Let's begin with our AI participant's self-reflection."))

            observation = "The AI participant begins to reflect on recent work, speaking openly about successes and challenges."
            transcript.append(self.third_person_observation(observation))
            episode.third_person_observations.append(observation)

            # AI speaks
            if ai_reflection.ai_reflection.get("what_went_well"):
                ai_text = "Here's what went well in our recent work: " + ". ".join(ai_reflection.ai_reflection["what_went_well"][:3])
                transcript.append(self.participant_speaks("AI", ai_text))

            observation = "The AI demonstrates self-awareness, acknowledging both achievements and areas for improvement."
            transcript.append(self.third_person_observation(observation))
            episode.third_person_observations.append(observation)

            if ai_reflection.ai_reflection.get("what_didnt_go_well"):
                ai_text = "Here's what didn't go well: " + ". ".join(ai_reflection.ai_reflection["what_didnt_go_well"][:3])
                transcript.append(self.participant_speaks("AI", ai_text))

            if ai_reflection.ai_reflection.get("how_im_feeling"):
                ai_text = f"How I'm feeling: {ai_reflection.ai_reflection['how_im_feeling']}"
                transcript.append(self.participant_speaks("AI", ai_text))

            episode.segments.append({
                "segment_type": "ai_reflection",
                "content": "AI self-reflection roundtable discussion",
                "timestamp": segment_start
            })

        # Segment 2: Human Feedback (Roundtable)
        if human_feedback:
            transcript.append(self.host_moderates("Now let's hear from our Human participant."))

            observation = "The Human participant shares their perspective, providing valuable feedback on the collaboration."
            transcript.append(self.third_person_observation(observation))
            episode.third_person_observations.append(observation)

            # Human speaks
            if human_feedback.human_feedback.get("whats_working"):
                human_text = "What's working: " + ". ".join(human_feedback.human_feedback["whats_working"][:3])
                transcript.append(self.participant_speaks("Human", human_text))

            if human_feedback.human_feedback.get("whats_not_working"):
                human_text = "What's not working: " + ". ".join(human_feedback.human_feedback["whats_not_working"][:3])
                transcript.append(self.participant_speaks("Human", human_text))

            if human_feedback.human_feedback.get("how_im_feeling"):
                human_text = f"How I'm feeling: {human_feedback.human_feedback['how_im_feeling']}"
                transcript.append(self.participant_speaks("Human", human_text))

            episode.segments.append({
                "segment_type": "human_feedback",
                "content": "Human feedback roundtable discussion",
                "timestamp": datetime.now().isoformat()
            })

        # Segment 3: Joint Discussion (Roundtable)
        transcript.append(self.host_moderates("Let's bring both perspectives together and work through this collaboratively."))

        observation = "The participants engage in a collaborative discussion, finding common ground and working through differences."
        transcript.append(self.third_person_observation(observation))
        episode.third_person_observations.append(observation)

        # Host facilitates discussion
        transcript.append(self.host_moderates("What patterns do you both notice in your collaboration?"))

        observation = "The host facilitates the discussion, helping both participants identify patterns and understand each other better."
        transcript.append(self.third_person_observation(observation))
        episode.third_person_observations.append(observation)

        # Joint insights
        if ai_reflection and human_feedback:
            transcript.append(self.participant_speaks("AI", "I notice that I sometimes build solutions before fully understanding the problem."))
            transcript.append(self.participant_speaks("Human", "I appreciate when you ask questions before making changes."))

            observation = "The participants find common ground: the importance of understanding before acting."
            transcript.append(self.third_person_observation(observation))
            episode.third_person_observations.append(observation)

        episode.segments.append({
            "segment_type": "joint_discussion",
            "content": "Collaborative roundtable discussion",
            "timestamp": datetime.now().isoformat()
        })

        # Host Outro
        outro = f"""
That concludes Episode {episode.episode_number} of the AI-Human Collaboration Therapy Podcast.

Today we explored collaboration, worked through issues together, and built understanding.

Thank you to our participants: {', '.join(episode.participants)}.

Join us next time for another roundtable discussion on AI-Human collaboration.

Until then, remember: perfect balance, as all things should be.
"""
        transcript.append(self.host_moderates(outro.strip()))
        episode.segments.append({
            "segment_type": "outro",
            "content": outro.strip(),
            "timestamp": datetime.now().isoformat()
        })

        # Final observation
        observation = "The episode concludes. Both participants leave with a better understanding of their collaboration and actionable steps forward."
        transcript.append(self.third_person_observation(observation))
        episode.third_person_observations.append(observation)

        # Save episode
        episode.transcript = transcript
        episode.duration_minutes = len(transcript) * 0.5  # Estimate: 30 seconds per entry

        # Generate summary
        episode.summary = self._generate_summary(episode)

        # Save episode file
        episode_file = self.episodes_dir / f"{episode_id}.json"
        with open(episode_file, 'w', encoding='utf-8') as f:
            json.dump(asdict(episode), f, indent=2, default=str)

        # Save transcript
        transcript_file = self.transcripts_dir / f"{episode_id}_transcript.txt"
        self._save_transcript(episode, transcript_file)

        # Update episode counter
        self._save_episode_counter()

        logger.info(f"✅ Podcast episode recorded: {episode_id}")
        logger.info(f"   Title: {episode.title}")
        logger.info(f"   Duration: {episode.duration_minutes:.1f} minutes")
        logger.info(f"   Segments: {len(episode.segments)}")
        logger.info(f"   Observations: {len(episode.third_person_observations)}")

        return episode

    def _generate_summary(self, episode: PodcastEpisode) -> str:
        """Generate episode summary"""
        summary_parts = [
            f"Episode {episode.episode_number}: {episode.title}",
            f"Recorded: {episode.timestamp}",
            f"Participants: {', '.join(episode.participants)}",
            f"Duration: {episode.duration_minutes:.1f} minutes",
            "",
            "Key Topics:",
        ]

        for segment in episode.segments:
            if segment["segment_type"] != "introduction" and segment["segment_type"] != "outro":
                summary_parts.append(f"- {segment['segment_type'].replace('_', ' ').title()}")

        summary_parts.append("")
        summary_parts.append("Third-Person Observations:")
        for obs in episode.third_person_observations[:5]:  # First 5
            summary_parts.append(f"- {obs}")

        return "\n".join(summary_parts)

    def _save_transcript(self, episode: PodcastEpisode, transcript_file: Path):
        try:
            """Save transcript as text file"""
            with open(transcript_file, 'w', encoding='utf-8') as f:
                f.write(f"AI-Human Collaboration Therapy Podcast\n")
                f.write(f"Episode {episode.episode_number}: {episode.title}\n")
                f.write(f"Recorded: {episode.timestamp}\n")
                f.write("="*80 + "\n\n")

                for entry in episode.transcript:
                    timestamp = entry.get("timestamp", "")
                    entry_type = entry.get("type", "")

                    if entry_type == "moderation":
                        f.write(f"[{timestamp}] HOST: {entry.get('text', '')}\n\n")
                    elif entry_type == "speech":
                        participant = entry.get("participant", "Unknown")
                        f.write(f"[{timestamp}] {participant}: {entry.get('text', '')}\n\n")
                    elif entry_type == "observation":
                        f.write(f"[{timestamp}] [OBSERVATION] {entry.get('text', '')}\n\n")

                f.write("\n" + "="*80 + "\n")
                f.write("Episode Summary:\n")
                f.write(episode.summary)


        except Exception as e:
            self.logger.error(f"Error in _save_transcript: {e}", exc_info=True)
            raise
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="AI-Human Collaboration Therapy - PODCAST STYLE")
    parser.add_argument("--record", action="store_true", help="Record a roundtable podcast episode")
    parser.add_argument("--title", type=str, help="Episode title")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("🎙️  AI-Human Collaboration Therapy Podcast")
    print("   Third-Person Roundtable Discussion Format")
    print("="*80 + "\n")

    podcast = AIHumanCollabTherapyPodcast()

    if args.record:
        # Load recent sessions
        if podcast.base_therapy:
            recent = podcast.base_therapy._load_recent_sessions(limit=5)
            ai_reflection = next((s for s in recent if s.session_type == SessionType.AI_SELF_REFLECTION), None)
            human_feedback = next((s for s in recent if s.session_type == SessionType.HUMAN_FEEDBACK), None)

            episode = podcast.record_roundtable_session(
                ai_reflection=ai_reflection,
                human_feedback=human_feedback,
                title=args.title
            )

            print(f"\n✅ Podcast episode recorded: {episode.episode_id}")
            print(f"   Title: {episode.title}")
            print(f"   Duration: {episode.duration_minutes:.1f} minutes")
            print(f"   Transcript: {podcast.transcripts_dir / f'{episode.episode_id}_transcript.txt'}")
            print()
        else:
            print("❌ Base therapy not available")
            print()
    else:
        print("Use --record to record a roundtable podcast episode")
        print("="*80 + "\n")
