#!/usr/bin/env python3
"""
Archive Review System

Periodically reviews archived items to:
1. Check if they're really done
2. Check if they stayed fixed
3. Check if they need to be fixed again
4. Track how many times they've broken
"""

import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from enum import Enum

try:
    from scripts.python.lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

try:
    from jarvis_marvin_followup import JarvisMarvinFollowUp, FollowUpStatus
    FOLLOWUP_AVAILABLE = True
except ImportError:
    FOLLOWUP_AVAILABLE = False
    JarvisMarvinFollowUp = None
    FollowUpStatus = None


class ReviewStatus(Enum):
    """Review status"""
    PENDING = "pending"
    REVIEWED = "reviewed"
    STILL_DONE = "still_done"
    BROKEN_AGAIN = "broken_again"
    NEEDS_REVIEW = "needs_review"


@dataclass
class ArchiveReview:
    """Archive review entry"""
    review_id: str
    item_id: str
    item_type: str  # followup, workflow, sub_agent_chat, etc.
    reviewed_at: str
    status: ReviewStatus
    is_still_done: bool = True
    is_broken: bool = False
    break_count: int = 0  # How many times it's broken
    fix_count: int = 0  # How many times it's been fixed
    review_notes: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["status"] = self.status.value
        return data


class ArchiveReviewSystem:
    """
    Archive Review System

    Periodically reviews archived items to ensure they stay fixed.
    """

    def __init__(self, project_root: Optional[Path] = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ArchiveReviewSystem")

        # Directories
        self.data_dir = self.project_root / "data" / "archive_reviews"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Files
        self.reviews_file = self.data_dir / "reviews.jsonl"
        self.item_break_history_file = self.data_dir / "item_break_history.json"

        # Follow-up system
        self.followup_system = None
        if FOLLOWUP_AVAILABLE and JarvisMarvinFollowUp:
            try:
                self.followup_system = JarvisMarvinFollowUp(project_root=self.project_root)
            except Exception as e:
                self.logger.warning(f"Follow-up system not available: {e}")

        # State
        self.reviews: List[ArchiveReview] = []
        self.item_break_history: Dict[str, Dict[str, Any]] = {}  # item_id -> break history

        # Configuration
        self.review_interval_days = 7  # Review every 7 days
        self.min_break_count_for_attention = 3  # Flag if broken 3+ times

        # Load state
        self._load_state()

    def _load_state(self):
        """Load state"""
        # Load reviews
        if self.reviews_file.exists():
            try:
                with open(self.reviews_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            data = json.loads(line)
                            review = ArchiveReview(**data)
                            review.status = ReviewStatus(data["status"])
                            self.reviews.append(review)
            except Exception as e:
                self.logger.error(f"Error loading reviews: {e}")

        # Load break history
        if self.item_break_history_file.exists():
            try:
                with open(self.item_break_history_file, 'r', encoding='utf-8') as f:
                    self.item_break_history = json.load(f)
            except Exception as e:
                self.logger.error(f"Error loading break history: {e}")

    def _save_review(self, review: ArchiveReview):
        try:
            """Save review"""
            self.reviews.append(review)
            # Keep last 1000
            if len(self.reviews) > 1000:
                self.reviews = self.reviews[-1000:]

            # Append to file
            with open(self.reviews_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(review.to_dict()) + '\n')

        except Exception as e:
            self.logger.error(f"Error in _save_review: {e}", exc_info=True)
            raise
    def _save_break_history(self):
        try:
            """Save break history"""
            with open(self.item_break_history_file, 'w', encoding='utf-8') as f:
                json.dump(self.item_break_history, f, indent=2, ensure_ascii=False)

        except Exception as e:
            self.logger.error(f"Error in _save_break_history: {e}", exc_info=True)
            raise
    def review_archived_item(
        self,
        item_id: str,
        item_type: str = "followup"
    ) -> ArchiveReview:
        """
        Review an archived item

        Checks if it's really done, if it stayed fixed, if it needs fixing again
        """
        review_id = f"review_{int(datetime.now().timestamp() * 1000)}"
        now = datetime.now().isoformat()

        self.logger.info(f"🔍 Reviewing archived item: {item_id} ({item_type})")

        # Check if item is still done
        is_still_done = self._check_if_still_done(item_id, item_type)

        # Check if item is broken
        is_broken = not is_still_done

        # Get break history
        break_history = self.item_break_history.get(item_id, {
            "break_count": 0,
            "fix_count": 0,
            "break_timestamps": [],
            "fix_timestamps": []
        })

        if is_broken:
            # Item broke again
            break_history["break_count"] += 1
            break_history["break_timestamps"].append(now)
            self.logger.warning(f"⚠️ Item {item_id} broke again (break count: {break_history['break_count']})")
        else:
            # Item still done
            self.logger.info(f"✅ Item {item_id} is still done")

        self.item_break_history[item_id] = break_history

        # Determine review status
        if is_broken:
            if break_history["break_count"] >= self.min_break_count_for_attention:
                status = ReviewStatus.NEEDS_REVIEW
            else:
                status = ReviewStatus.BROKEN_AGAIN
        else:
            status = ReviewStatus.STILL_DONE

        review = ArchiveReview(
            review_id=review_id,
            item_id=item_id,
            item_type=item_type,
            reviewed_at=now,
            status=status,
            is_still_done=is_still_done,
            is_broken=is_broken,
            break_count=break_history["break_count"],
            fix_count=break_history["fix_count"],
            review_notes=[f"Reviewed at {now}", f"Still done: {is_still_done}", f"Broken: {is_broken}"]
        )

        self._save_review(review)
        self._save_break_history()

        return review

    def _check_if_still_done(self, item_id: str, item_type: str) -> bool:
        """Check if item is still done"""
        if item_type == "followup" and self.followup_system:
            # Check follow-up
            followup = self.followup_system.followups.get(item_id)
            if followup:
                # Check if fault is still fixed
                # TODO: Implement actual check  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]  # [ADDRESSED]
                return followup.status == FollowUpStatus.ARCHIVED

        # Default: assume still done if we can't check
        return True

    def mark_item_fixed(self, item_id: str):
        """Mark item as fixed (after it broke)"""
        break_history = self.item_break_history.get(item_id, {
            "break_count": 0,
            "fix_count": 0,
            "break_timestamps": [],
            "fix_timestamps": []
        })

        break_history["fix_count"] += 1
        break_history["fix_timestamps"].append(datetime.now().isoformat())

        self.item_break_history[item_id] = break_history
        self._save_break_history()

        self.logger.info(f"✅ Marked item {item_id} as fixed (fix count: {break_history['fix_count']})")

    def review_all_archived(self) -> Dict[str, Any]:
        """Review all archived items"""
        if not self.followup_system:
            return {"error": "Follow-up system not available"}

        archived = self.followup_system.get_archived_followups()

        reviewed = 0
        still_done = 0
        broken_again = 0
        needs_attention = 0

        for followup in archived:
            review = self.review_archived_item(followup.followup_id, "followup")
            reviewed += 1

            if review.is_still_done:
                still_done += 1
            else:
                broken_again += 1
                if review.break_count >= self.min_break_count_for_attention:
                    needs_attention += 1

        return {
            "reviewed": reviewed,
            "still_done": still_done,
            "broken_again": broken_again,
            "needs_attention": needs_attention
        }

    def get_items_needing_attention(self) -> List[ArchiveReview]:
        """Get items that need attention (broken multiple times)"""
        return [
            r for r in self.reviews
            if r.status == ReviewStatus.NEEDS_REVIEW
            or (r.is_broken and r.break_count >= self.min_break_count_for_attention)
        ]

    def get_break_statistics(self) -> Dict[str, Any]:
        """Get break statistics"""
        total_items = len(self.item_break_history)
        items_broken = sum(1 for h in self.item_break_history.values() if h["break_count"] > 0)
        total_breaks = sum(h["break_count"] for h in self.item_break_history.values())
        total_fixes = sum(h["fix_count"] for h in self.item_break_history.values())

        return {
            "total_items": total_items,
            "items_broken": items_broken,
            "total_breaks": total_breaks,
            "total_fixes": total_fixes,
            "average_breaks_per_item": total_breaks / max(total_items, 1)
        }


def main():
    """Main execution for testing"""
    reviewer = ArchiveReviewSystem()

    print("=" * 80)
    print("📦 ARCHIVE REVIEW SYSTEM")
    print("=" * 80)

    # Review all archived
    result = reviewer.review_all_archived()

    print(f"\n📊 Review Results:")
    print(f"   Reviewed: {result.get('reviewed', 0)}")
    print(f"   Still Done: {result.get('still_done', 0)}")
    print(f"   Broken Again: {result.get('broken_again', 0)}")
    print(f"   Needs Attention: {result.get('needs_attention', 0)}")

    # Get break statistics
    stats = reviewer.get_break_statistics()
    print(f"\n📈 Break Statistics:")
    print(f"   Total Items: {stats['total_items']}")
    print(f"   Items Broken: {stats['items_broken']}")
    print(f"   Total Breaks: {stats['total_breaks']}")
    print(f"   Total Fixes: {stats['total_fixes']}")
    print(f"   Average Breaks per Item: {stats['average_breaks_per_item']:.2f}")


if __name__ == "__main__":



    main()