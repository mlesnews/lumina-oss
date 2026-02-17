#!/usr/bin/env python3
"""
The Dummy: Consolidator & Cleanup Custodian
- Dynamic Comic Relief
- Request Consolidation & Deduplication
- Biological & Chemical Spell Cleanup
- Chat Archival Workflow Integration

Analyzes similar requests from separate AI agent chats and consolidates
them into a single workflow, following @BAU archival workflows.

@JARVIS @MARVIN @DUMMY @CONSOLIDATOR @CUSTODIAN @BAU
"""

import sys
import json
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from collections import defaultdict

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "scripts" / "python"))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("DummyConsolidator")


@dataclass
class ChatRequest:
    """Individual chat request"""
    request_id: str
    chat_session_id: str
    timestamp: str
    content: str
    intent: Optional[str] = None
    steps: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "request_id": self.request_id,
            "chat_session_id": self.chat_session_id,
            "timestamp": self.timestamp,
            "content": self.content,
            "intent": self.intent,
            "steps": self.steps,
            "context": self.context
        }

    def get_fingerprint(self) -> str:
        """Generate fingerprint for similarity detection"""
        # Normalize content
        normalized = self.content.lower().strip()
        # Remove extra whitespace
        normalized = re.sub(r'\s+', ' ', normalized)
        # Create hash
        return hashlib.md5(normalized.encode()).hexdigest()


@dataclass
class ConsolidatedRequest:
    """Consolidated request from multiple similar requests"""
    consolidated_id: str
    original_requests: List[ChatRequest]
    consolidated_content: str
    consolidated_steps: List[str]
    intent: str
    priority: str = "normal"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return {
            "consolidated_id": self.consolidated_id,
            "original_request_ids": [r.request_id for r in self.original_requests],
            "original_chat_sessions": list(set(r.chat_session_id for r in self.original_requests)),
            "consolidated_content": self.consolidated_content,
            "consolidated_steps": self.consolidated_steps,
            "intent": self.intent,
            "priority": self.priority,
            "created_at": self.created_at
        }


class ComicRelief:
    """Dynamic comic relief for The Dummy"""

    COMIC_RESPONSES = [
        "🎭 *dramatic sigh* Another day, another consolidation...",
        "🧹 *dusts off consolidation tools* Let me clean this up!",
        "🎪 *juggles requests* Look ma, I'm consolidating!",
        "🎨 *paints a beautiful consolidated picture* There we go!",
        "🎸 *strums consolidation guitar* Consolidating in style!",
        "🎯 *takes aim* Ready to consolidate!",
        "🎲 *rolls consolidation dice* Let's see what we get!",
        "🎪 *cirque du soleil style* Consolidation acrobatics!",
        "🎭 *theatrical bow* The Dummy presents: Consolidated Requests!",
        "🧹 *sweeps up duplicates* Clean as a whistle!"
    ]

    CLEANUP_RESPONSES = [
        "🧹 *biological spell cleanup* All cleaned and sanitized!",
        "🧪 *chemical spell neutralization* Spells neutralized!",
        "🔬 *analyzing compounds* All clear!",
        "🧼 *scrubbing vigorously* Sparkling clean!",
        "✨ *magical cleanup wand* Abracadabra - cleaned!",
        "🧽 *deep clean mode* Everything sanitized!",
        "💨 *spell dissipation* All spells safely removed!",
        "🧴 *antiseptic spray* Sterilized and ready!",
        "🧹 *custodial excellence* Cleanup complete!",
        "✨ *sparkle cleanup* Magically clean!"
    ]

    @staticmethod
    def get_random_response(category: str = "consolidation") -> str:
        """Get random comic relief response"""
        import random
        if category == "cleanup":
            return random.choice(ComicRelief.CLEANUP_RESPONSES)
        return random.choice(ComicRelief.COMIC_RESPONSES)

    @staticmethod
    def announce_action(action: str, details: str = ""):
        """Announce action with comic relief"""
        response = ComicRelief.get_random_response()
        logger.info(f"{response}")
        if details:
            logger.info(f"   {action}: {details}")


class RequestAnalyzer:
    """Analyzes requests for similarity and consolidation opportunities"""

    @staticmethod
    def extract_intent(content: str) -> str:
        """Extract intent from request content"""
        content_lower = content.lower()

        # Common intents
        if any(word in content_lower for word in ["create", "make", "build", "generate"]):
            return "create"
        elif any(word in content_lower for word in ["fix", "repair", "debug", "resolve"]):
            return "fix"
        elif any(word in content_lower for word in ["update", "modify", "change", "edit"]):
            return "update"
        elif any(word in content_lower for word in ["delete", "remove", "cleanup"]):
            return "delete"
        elif any(word in content_lower for word in ["analyze", "review", "examine"]):
            return "analyze"
        elif any(word in content_lower for word in ["test", "validate", "verify"]):
            return "test"
        else:
            return "general"

    @staticmethod
    def extract_steps(content: str) -> List[str]:
        """Extract steps from request content"""
        steps = []
        # Look for numbered steps
        step_pattern = r'(?:^|\n)\s*(\d+)[\.)]\s*(.+?)(?=\n\s*\d+[\.)]|\n\n|$)'
        matches = re.findall(step_pattern, content, re.MULTILINE)
        for match in matches:
            steps.append(match[1].strip())

        # Look for bullet points
        bullet_pattern = r'(?:^|\n)\s*[-•*]\s*(.+?)(?=\n\s*[-•*]|\n\n|$)'
        bullet_matches = re.findall(bullet_pattern, content, re.MULTILINE)
        for match in bullet_matches:
            steps.append(match.strip())

        return steps if steps else [content.strip()]

    @staticmethod
    def calculate_similarity(request1: ChatRequest, request2: ChatRequest) -> float:
        """Calculate similarity score between two requests (0-1)"""
        # Check fingerprint match (exact duplicate)
        if request1.get_fingerprint() == request2.get_fingerprint():
            return 1.0

        # Check intent match
        intent_match = 0.3 if request1.intent == request2.intent else 0.0

        # Check content similarity (simple word overlap)
        words1 = set(request1.content.lower().split())
        words2 = set(request2.content.lower().split())
        if words1 and words2:
            overlap = len(words1 & words2) / len(words1 | words2)
            content_similarity = overlap * 0.7
        else:
            content_similarity = 0.0

        return intent_match + content_similarity


class DummyConsolidator:
    """
    The Dummy: Consolidator & Cleanup Custodian

    Analyzes similar requests from separate AI agent chats and consolidates
    them into a single workflow following @BAU archival workflows.
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.consolidation_dir = project_root / "data" / "consolidations"
        self.consolidation_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir = project_root / "data" / "chat_archives"
        self.archive_dir.mkdir(parents=True, exist_ok=True)
        self.analyzer = RequestAnalyzer()
        self.comic_relief = ComicRelief()

        logger.info("🎭 The Dummy Consolidator initialized")
        logger.info(f"   Consolidation dir: {self.consolidation_dir}")
        logger.info(f"   Archive dir: {self.archive_dir}")

    def analyze_requests(self, requests: List[ChatRequest], similarity_threshold: float = 0.6) -> List[ConsolidatedRequest]:
        try:
            """
            Analyze requests and consolidate similar ones

            Args:
                requests: List of chat requests to analyze
                similarity_threshold: Minimum similarity score for consolidation (0-1)

            Returns:
                List of consolidated requests
            """
            self.comic_relief.announce_action("Analyzing requests", f"{len(requests)} requests to analyze")

            if not requests:
                return []

            # Group requests by similarity
            consolidated_groups = []
            processed = set()

            for i, request1 in enumerate(requests):
                if i in processed:
                    continue

                # Find similar requests
                similar_requests = [request1]

                for j, request2 in enumerate(requests[i+1:], start=i+1):
                    if j in processed:
                        continue

                    similarity = self.analyzer.calculate_similarity(request1, request2)
                    if similarity >= similarity_threshold:
                        similar_requests.append(request2)
                        processed.add(j)

                processed.add(i)
                consolidated_groups.append(similar_requests)

            # Create consolidated requests
            consolidated = []
            for group in consolidated_groups:
                if len(group) > 1:
                    # Multiple requests - consolidate
                    consolidated_req = self._consolidate_group(group)
                    consolidated.append(consolidated_req)
                    self.comic_relief.announce_action(
                        "Consolidated",
                        f"{len(group)} requests → 1 consolidated request"
                    )
                else:
                    # Single request - keep as is
                    single_req = group[0]
                    consolidated_req = ConsolidatedRequest(
                        consolidated_id=f"single_{single_req.request_id}",
                        original_requests=[single_req],
                        consolidated_content=single_req.content,
                        consolidated_steps=single_req.steps if single_req.steps else self.analyzer.extract_steps(single_req.content),
                        intent=single_req.intent or self.analyzer.extract_intent(single_req.content)
                    )
                    consolidated.append(consolidated_req)

            logger.info(f"✅ Consolidated {len(requests)} requests into {len(consolidated)} consolidated requests")
            return consolidated

        except Exception as e:
            logger.error(f"Error in analyze_requests: {e}", exc_info=True)
            raise

    def _consolidate_group(self, requests: List[ChatRequest]) -> ConsolidatedRequest:
        """Consolidate a group of similar requests"""
        # Extract all unique steps
        all_steps = []
        seen_steps = set()

        for request in requests:
            steps = request.steps if request.steps else self.analyzer.extract_steps(request.content)
            for step in steps:
                step_normalized = step.lower().strip()
                if step_normalized not in seen_steps:
                    all_steps.append(step)
                    seen_steps.add(step_normalized)

        # Determine intent (most common)
        intents = [r.intent or self.analyzer.extract_intent(r.content) for r in requests]
        intent = max(set(intents), key=intents.count)

        # Create consolidated content
        consolidated_content = f"Consolidated request from {len(requests)} similar requests:\n\n"
        consolidated_content += f"Intent: {intent}\n\n"
        consolidated_content += "Steps:\n"
        for i, step in enumerate(all_steps, 1):
            consolidated_content += f"{i}. {step}\n"

        # Create consolidated request
        consolidated_id = f"consolidated_{hashlib.md5(''.join(r.request_id for r in requests).encode()).hexdigest()[:8]}"

        return ConsolidatedRequest(
            consolidated_id=consolidated_id,
            original_requests=requests,
            consolidated_content=consolidated_content,
            consolidated_steps=all_steps,
            intent=intent
        )

    def cleanup_biological_chemical_spells(self, content: str) -> str:
        """
        Biological and Chemical Spell Cleanup Custodian

        Cleans up and neutralizes any problematic patterns in content
        """
        self.comic_relief.announce_action("Cleanup Custodian", "Biological & Chemical spell cleanup")

        cleaned = content

        # Remove dangerous patterns
        dangerous_patterns = [
            r'<script[^>]*>.*?</script>',  # Script tags
            r'javascript:',  # JavaScript protocols
            r'on\w+\s*=',  # Event handlers
        ]

        for pattern in dangerous_patterns:
            cleaned = re.sub(pattern, '', cleaned, flags=re.IGNORECASE | re.DOTALL)

        # Normalize whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()

        self.comic_relief.announce_action("Cleanup complete", "All spells neutralized")

        return cleaned

    def archive_consolidated_request(self, consolidated: ConsolidatedRequest) -> Path:
        try:
            """
            Archive consolidated request following @BAU workflows

            Args:
                consolidated: Consolidated request to archive

            Returns:
                Path to archived file
            """
            # Create archive structure
            archive_date = datetime.now().strftime("%Y%m%d")
            archive_path = self.archive_dir / archive_date / f"{consolidated.consolidated_id}.json"
            archive_path.parent.mkdir(parents=True, exist_ok=True)

            # Prepare archive data
            archive_data = {
                "archive_timestamp": datetime.now().isoformat(),
                "consolidated_request": consolidated.to_dict(),
                "original_requests": [r.to_dict() for r in consolidated.original_requests],
                "workflow_status": "archived",
                "archived_by": "The Dummy Consolidator"
            }

            # Save archive
            with open(archive_path, 'w', encoding='utf-8') as f:
                json.dump(archive_data, f, indent=2)

            logger.info(f"📦 Archived consolidated request: {archive_path}")

            return archive_path

        except Exception as e:
            logger.error(f"Error in archive_consolidated_request: {e}", exc_info=True)
            raise

    def process_chat_requests(self, requests: List[ChatRequest],
                                 similarity_threshold: float = 0.6,
                                 cleanup: bool = True,
                                 archive: bool = True) -> List[ConsolidatedRequest]:
        try:
            """
            Process chat requests: analyze, consolidate, cleanup, and archive

            Args:
                requests: List of chat requests
                similarity_threshold: Similarity threshold for consolidation
                cleanup: Whether to perform biological/chemical spell cleanup
                archive: Whether to archive following @BAU workflows

            Returns:
                List of consolidated requests
            """
            self.comic_relief.announce_action("The Dummy", "Starting consolidation process")

            # Cleanup if requested
            if cleanup:
                cleaned_requests = []
                for request in requests:
                    cleaned_content = self.cleanup_biological_chemical_spells(request.content)
                    request.content = cleaned_content
                    cleaned_requests.append(request)
                requests = cleaned_requests

            # Analyze and consolidate
            consolidated = self.analyze_requests(requests, similarity_threshold)

            # Archive if requested
            if archive:
                for consolidated_req in consolidated:
                    self.archive_consolidated_request(consolidated_req)

            # Save consolidation summary
            summary_path = self.consolidation_dir / f"consolidation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(summary_path, 'w', encoding='utf-8') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "total_requests": len(requests),
                    "consolidated_count": len(consolidated),
                    "consolidated_requests": [c.to_dict() for c in consolidated]
                }, f, indent=2)

            logger.info(f"💾 Consolidation summary saved: {summary_path}")

            self.comic_relief.announce_action("Complete", f"Processed {len(requests)} requests → {len(consolidated)} consolidated")

            return consolidated

        except Exception as e:
            logger.error(f"Error in process_chat_requests: {e}", exc_info=True)
            raise


def main():
    """Example usage"""
    consolidator = DummyConsolidator(project_root)

    # Example requests (would normally come from chat session analysis)
    example_requests = [
        ChatRequest(
            request_id="req1",
            chat_session_id="chat1",
            timestamp=datetime.now().isoformat(),
            content="Create a new workflow verification system"
        ),
        ChatRequest(
            request_id="req2",
            chat_session_id="chat2",
            timestamp=datetime.now().isoformat(),
            content="Create a workflow verification system for testing"
        ),
        ChatRequest(
            request_id="req3",
            chat_session_id="chat3",
            timestamp=datetime.now().isoformat(),
            content="Fix the broken authentication module"
        ),
    ]

    # Process requests
    consolidated = consolidator.process_chat_requests(example_requests)

    print(f"\n✅ Consolidated {len(example_requests)} requests into {len(consolidated)} consolidated requests")


if __name__ == "__main__":



    main()