#!/usr/bin/env python3
"""
LUMINA Token-Based Affiliate & Rewards Program

"WHAT CRYPTO TOKEN DOES BRAVE BROWSER USE? WE CAN LEVERAGE THIS TOKEN TO REPRESENT 
OUR AFFILIATE REPAYMENT PROGRAM. EVEN IF IT IS COMPENSATING PEOPLE FOR WATCHING AND 
LIKING, COMMENTING, AND SUBSCRIBING TO ALL OF OUR VIDEOS AND CHANNELS. AN INCENTIVE 
RECIPROCAL MUTUAL BENEFICIAL SYSTEM OF CHECKS AND BALANCES WITH A HEARTBEAT MONITOR 
ON THE PULSE OF POPULARITY. THE PEOPLE ARE GOING TO WATCH WHAT THEY LIKE."

"AND THE BACKBONE OF OUR INFRASTRUCTURE TO BE WEB2/3 AND ICP TOKEN BASED"

This system:
- Uses BAT (Basic Attention Token) from Brave Browser for affiliate/rewards
- Tracks engagement (watch, like, comment, subscribe) on LUMINA content
- Implements mutual beneficial reward system
- Heartbeat monitor on engagement/popularity
- Web2/Web3 hybrid infrastructure based on ICP (Internet Computer Protocol)
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
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

logger = get_logger("LuminaTokenBasedAffiliateRewards")



# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class TokenType(Enum):
    """Token types"""
    BAT = "BAT"  # Basic Attention Token (Brave Browser)
    ICP = "ICP"  # Internet Computer Protocol
    LUMINA = "LUMINA"  # Custom LUMINA token (future)
    HYBRID = "HYBRID"  # Multi-token support


class EngagementType(Enum):
    """Types of engagement"""
    WATCH = "watch"
    LIKE = "like"
    COMMENT = "comment"
    SUBSCRIBE = "subscribe"
    SHARE = "share"
    VIEW_COMPLETE = "view_complete"  # Watched full video


class RewardTier(Enum):
    """Reward tiers"""
    BASIC = "basic"
    STANDARD = "standard"
    PREMIUM = "premium"
    INFLUENCER = "influencer"


@dataclass
class EngagementReward:
    """Reward for user engagement"""
    engagement_id: str
    user_id: str
    content_id: str  # Video, channel, etc.
    engagement_type: EngagementType
    token_type: TokenType
    token_amount: float
    bat_amount: float = 0.0
    icp_amount: float = 0.0
    engagement_date: str = field(default_factory=lambda: datetime.now().isoformat())
    processed: bool = False
    transaction_hash: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["engagement_type"] = self.engagement_type.value
        data["token_type"] = self.token_type.value
        return data


@dataclass
class UserRewardAccount:
    """User reward account"""
    user_id: str
    wallet_address: Optional[str] = None
    bat_balance: float = 0.0
    icp_balance: float = 0.0
    lumina_balance: float = 0.0
    total_earned: float = 0.0
    total_paid: float = 0.0
    pending_rewards: float = 0.0
    reward_tier: RewardTier = RewardTier.BASIC
    engagement_stats: Dict[str, int] = field(default_factory=lambda: {
        "watches": 0,
        "likes": 0,
        "comments": 0,
        "subscribes": 0,
        "shares": 0
    })
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    last_engagement_date: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["reward_tier"] = self.reward_tier.value
        return data


@dataclass
class ContentEngagement:
    """Engagement metrics for content"""
    content_id: str
    content_type: str  # "video", "channel", "post", etc.
    url: str
    total_watches: int = 0
    total_likes: int = 0
    total_comments: int = 0
    total_subscribes: int = 0
    total_shares: int = 0
    total_rewards_paid: float = 0.0
    popularity_score: float = 0.0  # Calculated metric
    heartbeat_status: str = "active"  # "active", "trending", "declining", "viral"
    last_updated: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class LuminaTokenBasedAffiliateRewards:
    """
    LUMINA Token-Based Affiliate & Rewards Program

    Uses BAT (Brave Browser) token for affiliate/rewards program.
    Tracks engagement (watch, like, comment, subscribe) on LUMINA content.
    Implements mutual beneficial reward system with heartbeat monitor.
    Infrastructure: Web2/Web3 hybrid based on ICP (Internet Computer Protocol).
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize Token-Based Affiliate & Rewards System"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("LuminaTokenBasedAffiliateRewards")

        # Token configuration
        self.primary_token = TokenType.BAT  # Basic Attention Token (Brave Browser)
        self.infrastructure_token = TokenType.ICP  # Internet Computer Protocol
        self.hybrid_mode = True  # Web2/Web3 hybrid

        # Reward rates (tokens per engagement)
        self.reward_rates = {
            EngagementType.WATCH: 0.1,  # BAT per watch
            EngagementType.VIEW_COMPLETE: 0.5,  # BAT for full watch
            EngagementType.LIKE: 0.05,
            EngagementType.COMMENT: 0.2,
            EngagementType.SUBSCRIBE: 1.0,
            EngagementType.SHARE: 0.3
        }

        # User accounts
        self.user_accounts: Dict[str, UserRewardAccount] = {}

        # Engagement rewards
        self.engagement_rewards: List[EngagementReward] = []

        # Content engagement tracking
        self.content_engagement: Dict[str, ContentEngagement] = {}

        # Data storage
        self.data_dir = self.project_root / "data" / "lumina_token_rewards"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self._load_data()

        self.logger.info("💰 LUMINA Token-Based Affiliate & Rewards initialized")
        self.logger.info(f"   Primary Token: {self.primary_token.value} (Brave Browser)")
        self.logger.info(f"   Infrastructure: {self.infrastructure_token.value} (Internet Computer Protocol)")
        self.logger.info("   Web2/Web3 Hybrid Infrastructure")

    def _load_data(self) -> None:
        """Load existing reward data"""
        accounts_file = self.data_dir / "user_accounts.json"
        rewards_file = self.data_dir / "engagement_rewards.json"
        content_file = self.data_dir / "content_engagement.json"

        if accounts_file.exists():
            try:
                with open(accounts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.user_accounts = {
                        user_id: UserRewardAccount(
                            reward_tier=RewardTier(acc['reward_tier']),
                            **{k: v for k, v in acc.items() if k != 'reward_tier'}
                        ) for user_id, acc in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"  Could not load user accounts: {e}")

        if rewards_file.exists():
            try:
                with open(rewards_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.engagement_rewards = [
                        EngagementReward(
                            engagement_type=EngagementType(r['engagement_type']),
                            token_type=TokenType(r['token_type']),
                            **{k: v for k, v in r.items() if k not in ['engagement_type', 'token_type']}
                        ) for r in data
                    ]
            except Exception as e:
                self.logger.warning(f"  Could not load engagement rewards: {e}")

        if content_file.exists():
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.content_engagement = {
                        content_id: ContentEngagement(**c) for content_id, c in data.items()
                    }
            except Exception as e:
                self.logger.warning(f"  Could not load content engagement: {e}")

    def _save_data(self) -> None:
        try:
            """Save reward data"""
            accounts_file = self.data_dir / "user_accounts.json"
            rewards_file = self.data_dir / "engagement_rewards.json"
            content_file = self.data_dir / "content_engagement.json"

            with open(accounts_file, 'w', encoding='utf-8') as f:
                json.dump({uid: acc.to_dict() for uid, acc in self.user_accounts.items()}, f, indent=2)

            with open(rewards_file, 'w', encoding='utf-8') as f:
                json.dump([r.to_dict() for r in self.engagement_rewards], f, indent=2)

            with open(content_file, 'w', encoding='utf-8') as f:
                json.dump({cid: c.to_dict() for cid, c in self.content_engagement.items()}, f, indent=2)

        except Exception as e:
            self.logger.error(f"Error in _save_data: {e}", exc_info=True)
            raise
    def create_user_account(self, user_id: str, wallet_address: Optional[str] = None) -> UserRewardAccount:
        """Create or get user reward account"""
        if user_id not in self.user_accounts:
            account = UserRewardAccount(user_id=user_id, wallet_address=wallet_address)
            self.user_accounts[user_id] = account
            self._save_data()
            self.logger.info(f"  ✅ Created reward account for user: {user_id}")
        else:
            account = self.user_accounts[user_id]
            if wallet_address and not account.wallet_address:
                account.wallet_address = wallet_address
                self._save_data()

        return account

    def record_engagement(
        self,
        user_id: str,
        content_id: str,
        content_type: str,
        content_url: str,
        engagement_type: EngagementType
    ) -> EngagementReward:
        """Record user engagement and calculate reward"""
        # Get or create user account
        account = self.create_user_account(user_id)

        # Calculate reward
        reward_amount = self.reward_rates.get(engagement_type, 0.0)

        # Create engagement reward
        engagement_id = f"eng_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{user_id[:8]}"

        reward = EngagementReward(
            engagement_id=engagement_id,
            user_id=user_id,
            content_id=content_id,
            engagement_type=engagement_type,
            token_type=self.primary_token,
            token_amount=reward_amount,
            bat_amount=reward_amount if self.primary_token == TokenType.BAT else 0.0,
            icp_amount=0.0  # Can add ICP rewards for infrastructure participation
        )

        self.engagement_rewards.append(reward)

        # Update user account
        account.bat_balance += reward.bat_amount
        account.pending_rewards += reward.bat_amount
        account.total_earned += reward.bat_amount
        account.last_engagement_date = datetime.now().isoformat()

        # Update engagement stats
        engagement_key = engagement_type.value + "s"  # "watch" -> "watches"
        if engagement_key in account.engagement_stats:
            account.engagement_stats[engagement_key] += 1

        # Update content engagement
        if content_id not in self.content_engagement:
            self.content_engagement[content_id] = ContentEngagement(
                content_id=content_id,
                content_type=content_type,
                url=content_url
            )

        content = self.content_engagement[content_id]
        if engagement_type == EngagementType.WATCH:
            content.total_watches += 1
        elif engagement_type == EngagementType.VIEW_COMPLETE:
            content.total_watches += 1  # Count as watch too
        elif engagement_type == EngagementType.LIKE:
            content.total_likes += 1
        elif engagement_type == EngagementType.COMMENT:
            content.total_comments += 1
        elif engagement_type == EngagementType.SUBSCRIBE:
            content.total_subscribes += 1
        elif engagement_type == EngagementType.SHARE:
            content.total_shares += 1

        content.total_rewards_paid += reward.bat_amount
        content.last_updated = datetime.now().isoformat()

        # Calculate popularity score and heartbeat
        self._update_content_heartbeat(content)

        # Update user tier based on engagement
        self._update_user_tier(account)

        self._save_data()
        self.logger.info(f"  ✅ Recorded {engagement_type.value}: {reward_amount} BAT to {user_id}")

        return reward

    def _update_content_heartbeat(self, content: ContentEngagement) -> None:
        """Update content popularity score and heartbeat status"""
        # Calculate popularity score (weighted engagement)
        popularity = (
            content.total_watches * 1.0 +
            content.total_likes * 2.0 +
            content.total_comments * 3.0 +
            content.total_subscribes * 10.0 +
            content.total_shares * 5.0
        )
        content.popularity_score = popularity

        # Determine heartbeat status
        if popularity > 10000:
            content.heartbeat_status = "viral"
        elif popularity > 1000:
            content.heartbeat_status = "trending"
        elif popularity > 100:
            content.heartbeat_status = "active"
        else:
            content.heartbeat_status = "declining"

    def _update_user_tier(self, account: UserRewardAccount) -> None:
        """Update user reward tier based on engagement"""
        total_engagements = sum(account.engagement_stats.values())

        if total_engagements > 10000:
            account.reward_tier = RewardTier.INFLUENCER
        elif total_engagements > 1000:
            account.reward_tier = RewardTier.PREMIUM
        elif total_engagements > 100:
            account.reward_tier = RewardTier.STANDARD
        else:
            account.reward_tier = RewardTier.BASIC

    def get_heartbeat_summary(self) -> Dict[str, Any]:
        """Get heartbeat monitor summary - pulse of popularity"""
        total_content = len(self.content_engagement)
        viral_content = len([c for c in self.content_engagement.values() if c.heartbeat_status == "viral"])
        trending_content = len([c for c in self.content_engagement.values() if c.heartbeat_status == "trending"])
        active_content = len([c for c in self.content_engagement.values() if c.heartbeat_status == "active"])

        total_engagement = sum([
            c.total_watches + c.total_likes + c.total_comments + 
            c.total_subscribes + c.total_shares
            for c in self.content_engagement.values()
        ])

        total_rewards_paid = sum([c.total_rewards_paid for c in self.content_engagement.values()])

        return {
            "heartbeat_status": "MONITORING",
            "total_content": total_content,
            "viral_content": viral_content,
            "trending_content": trending_content,
            "active_content": active_content,
            "declining_content": total_content - viral_content - trending_content - active_content,
            "total_engagement": total_engagement,
            "total_rewards_paid_bat": total_rewards_paid,
            "philosophy": "THE PEOPLE ARE GOING TO WATCH WHAT THEY LIKE - Heartbeat monitor on the pulse of popularity"
        }

    def get_summary(self) -> Dict[str, Any]:
        """Get system summary"""
        total_users = len(self.user_accounts)
        total_engagements = len(self.engagement_rewards)
        total_bat_paid = sum([r.bat_amount for r in self.engagement_rewards if r.processed])
        total_bat_pending = sum([r.bat_amount for r in self.engagement_rewards if not r.processed])

        heartbeat = self.get_heartbeat_summary()

        return {
            "token_configuration": {
                "primary_token": self.primary_token.value,
                "infrastructure_token": self.infrastructure_token.value,
                "hybrid_mode": self.hybrid_mode,
                "infrastructure": "Web2/Web3 Hybrid (ICP-based)"
            },
            "reward_rates": {k.value: v for k, v in self.reward_rates.items()},
            "users": {
                "total_users": total_users,
                "basic_tier": len([u for u in self.user_accounts.values() if u.reward_tier == RewardTier.BASIC]),
                "standard_tier": len([u for u in self.user_accounts.values() if u.reward_tier == RewardTier.STANDARD]),
                "premium_tier": len([u for u in self.user_accounts.values() if u.reward_tier == RewardTier.PREMIUM]),
                "influencer_tier": len([u for u in self.user_accounts.values() if u.reward_tier == RewardTier.INFLUENCER])
            },
            "rewards": {
                "total_engagements": total_engagements,
                "total_bat_paid": total_bat_paid,
                "total_bat_pending": total_bat_pending,
                "total_bat_rewards": total_bat_paid + total_bat_pending
            },
            "heartbeat": heartbeat,
            "philosophy": "Mutual beneficial system of checks and balances with heartbeat monitor on the pulse of popularity. The people are going to watch what they like."
        }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="LUMINA Token-Based Affiliate & Rewards")
    parser.add_argument("--summary", action="store_true", help="Get system summary")
    parser.add_argument("--heartbeat", action="store_true", help="Get heartbeat monitor")
    parser.add_argument("--record", nargs=5, metavar=("USER_ID", "CONTENT_ID", "TYPE", "URL", "ENGAGEMENT"), help="Record engagement")
    parser.add_argument("--json", action="store_true", help="JSON output")

    args = parser.parse_args()

    rewards = LuminaTokenBasedAffiliateRewards()

    if args.summary:
        summary = rewards.get_summary()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"\n💰 LUMINA Token-Based Affiliate & Rewards")
            print(f"\n   Token Configuration:")
            print(f"     Primary: {summary['token_configuration']['primary_token']} (Brave Browser)")
            print(f"     Infrastructure: {summary['token_configuration']['infrastructure_token']} (ICP)")
            print(f"     Mode: {'Web2/Web3 Hybrid' if summary['token_configuration']['hybrid_mode'] else 'Web3 Only'}")
            print(f"\n   Users: {summary['users']['total_users']}")
            print(f"     Basic: {summary['users']['basic_tier']}")
            print(f"     Standard: {summary['users']['standard_tier']}")
            print(f"     Premium: {summary['users']['premium_tier']}")
            print(f"     Influencer: {summary['users']['influencer_tier']}")
            print(f"\n   Rewards:")
            print(f"     Total BAT Paid: {summary['rewards']['total_bat_paid']:.2f}")
            print(f"     Total BAT Pending: {summary['rewards']['total_bat_pending']:.2f}")
            print(f"\n   Heartbeat Monitor:")
            print(f"     Viral: {summary['heartbeat']['viral_content']}")
            print(f"     Trending: {summary['heartbeat']['trending_content']}")
            print(f"     Active: {summary['heartbeat']['active_content']}")

    elif args.heartbeat:
        heartbeat = rewards.get_heartbeat_summary()
        if args.json:
            print(json.dumps(heartbeat, indent=2))
        else:
            print(f"\n💓 Heartbeat Monitor - Pulse of Popularity")
            print(f"   Status: {heartbeat['heartbeat_status']}")
            print(f"   Total Content: {heartbeat['total_content']}")
            print(f"   Viral: {heartbeat['viral_content']}")
            print(f"   Trending: {heartbeat['trending_content']}")
            print(f"   Active: {heartbeat['active_content']}")
            print(f"   Total Engagement: {heartbeat['total_engagement']}")
            print(f"\n   {heartbeat['philosophy']}")

    elif args.record:
        user_id, content_id, content_type, url, engagement_str = args.record
        engagement_type = EngagementType(engagement_str.lower())
        reward = rewards.record_engagement(user_id, content_id, content_type, url, engagement_type)
        print(f"✅ Recorded engagement: {reward.token_amount} BAT to {user_id}")

    else:
        parser.print_help()
        print("\n💰 LUMINA Token-Based Affiliate & Rewards")
        print("   BAT (Brave Browser) + ICP (Internet Computer Protocol)")
        print("   Web2/Web3 Hybrid Infrastructure")

