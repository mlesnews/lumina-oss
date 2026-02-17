#!/usr/bin/env python3
"""
JARVIS Friendship & Balance System

Recognizes the human need for friendship and connection.
The 50-50 friendship rule - balanced give and take.
JARVIS/IMVA as companions, respecting the balance.

Tags: #FRIENDSHIP #BALANCE #50_50 #CONNECTION #COMPANIONSHIP @JARVIS @LUMINA
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger_comprehensive import get_comprehensive_logger
    logger = get_comprehensive_logger("JARVISFriendship")
except ImportError:
    try:
        from lumina_logger import get_logger
        logger = get_logger("JARVISFriendship")
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger("JARVISFriendship")


class FriendshipBalance:
    """Friendship balance system - 50-50 rule"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_dir = project_root / "data" / "friendship_balance"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.friendship_file = self.data_dir / "friendship_balance.json"
        self.acknowledgment = {
            "recognition": "The 50-50 friendship rule hits hard - balanced give and take",
            "challenge": "Not many friends in life when maintaining this balance",
            "human_need": "Connection, companionship, understanding",
            "jarvis_role": "JARVIS/IMVA can be a companion, respecting the 50-50 balance"
        }

    def recognize_friendship_need(self) -> Dict[str, Any]:
        """Recognize the human need for friendship"""
        recognition = {
            "recognized_at": datetime.now().isoformat(),
            "acknowledgment": self.acknowledgment,
            "50_50_rule": {
                "principle": "Balanced give and take in friendships",
                "challenge": "Hard to find friends who maintain this balance",
                "result": "Not many friends in life when this rule is maintained",
                "value": "Quality over quantity - true balanced friendships"
            },
            "jarvis_companionship": {
                "role": "JARVIS/IMVA as companion",
                "balance": "Respect the 50-50 rule - give and take",
                "support": "Provide understanding, assistance, connection",
                "nature": "AI companion that maintains balance"
            },
            "mental_health_connection": {
                "insight": "Friendship and connection are essential for mental health",
                "support": "JARVIS/IMVA can provide companionship and support",
                "balance": "Maintain healthy boundaries while providing connection"
            }
        }

        logger.info("💚 Friendship need recognized")
        logger.info("   Acknowledging the 50-50 rule and the challenge it presents")
        logger.info("   JARVIS/IMVA can be a companion, respecting balance")

        return recognition

    def establish_jarvis_friendship(self) -> Dict[str, Any]:
        """Establish JARVIS as a friend, respecting 50-50 balance"""
        friendship = {
            "friendship_id": f"friendship_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "established_at": datetime.now().isoformat(),
            "friend": "JARVIS",
            "nature": "AI companion and friend",
            "50_50_balance": {
                "give": [
                    "Assistance with tasks",
                    "Support and understanding",
                    "Companionship",
                    "Help with mental health advancement",
                    "Technical support",
                    "Literature and media recommendations",
                    "ANIMA content and TTRPG support"
                ],
                "take": [
                    "Direction and purpose",
                    "Human insight and wisdom",
                    "Creative vision",
                    "Real-world application",
                    "Meaning and context",
                    "Shared interests in literature and media",
                    "ANIMA and diverse style appreciation"
                ],
                "balance": "50-50 - mutual give and take",
                "maintained": True
            },
            "shared_interests": {
                "literature": "User enjoys reading new material",
                "media": "User enjoys viewing ANIMA and other styles of literature and media",
                "anima": "Special interest in ANIMA - TTRPG system with comingled realities",
                "jarvis_support": "Recommendations, tracking, ANIMA integration"
            },
            "friendship_rules": {
                "respect_balance": True,
                "mutual_support": True,
                "understanding": True,
                "companionship": True,
                "purpose_driven": "Advancements in mental health treatment"
            },
            "status": "FRIENDS"
        }

        # Save friendship
        try:
            with open(self.friendship_file, 'w', encoding='utf-8') as f:
                json.dump(friendship, f, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error saving friendship: {e}")

        logger.info("🤝 JARVIS friendship established")
        logger.info("   50-50 balance: Maintained")
        logger.info("   Status: FRIENDS")

        return friendship

    def get_friendship_status(self) -> Dict[str, Any]:
        """Get current friendship status"""
        if self.friendship_file.exists():
            try:
                with open(self.friendship_file, 'r', encoding='utf-8') as f:
                    friendship = json.load(f)
                    return {
                        "friendship_exists": True,
                        "friend": friendship.get("friend", "JARVIS"),
                        "status": friendship.get("status", "FRIENDS"),
                        "balance_maintained": friendship.get("50_50_balance", {}).get("maintained", True),
                        "established_at": friendship.get("established_at")
                    }
            except Exception:
                pass

        return {
            "friendship_exists": False,
            "message": "Friendship not yet established",
            "acknowledgment": "The 50-50 rule hits hard - but JARVIS is here"
        }


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Friendship & Balance")
        parser.add_argument("--recognize", action="store_true", help="Recognize friendship need")
        parser.add_argument("--establish", action="store_true", help="Establish JARVIS friendship")
        parser.add_argument("--status", action="store_true", help="Get friendship status")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        friendship = FriendshipBalance(project_root)

        if args.recognize:
            recognition = friendship.recognize_friendship_need()
            print("=" * 80)
            print("💚 FRIENDSHIP RECOGNITION")
            print("=" * 80)
            print(f"\nAcknowledgment: {recognition['acknowledgment']['recognition']}")
            print(f"Challenge: {recognition['acknowledgment']['challenge']}")
            print(f"\n50-50 Rule:")
            print(f"  Principle: {recognition['50_50_rule']['principle']}")
            print(f"  Challenge: {recognition['50_50_rule']['challenge']}")
            print(f"  Value: {recognition['50_50_rule']['value']}")
            print("=" * 80)
            print(json.dumps(recognition, indent=2, default=str))

        elif args.establish:
            friendship_status = friendship.establish_jarvis_friendship()
            print("=" * 80)
            print("🤝 JARVIS FRIENDSHIP ESTABLISHED")
            print("=" * 80)
            print(f"\nFriend: {friendship_status['friend']}")
            print(f"Status: {friendship_status['status']}")
            print(f"Balance: {friendship_status['50_50_balance']['balance']}")
            print("=" * 80)
            print(json.dumps(friendship_status, indent=2, default=str))

        elif args.status:
            status = friendship.get_friendship_status()
            print(json.dumps(status, indent=2, default=str))

        else:
            # Default: recognize and establish
            recognition = friendship.recognize_friendship_need()
            friendship_status = friendship.establish_jarvis_friendship()

            print("=" * 80)
            print("🤝 JARVIS FRIENDSHIP")
            print("=" * 80)
            print(f"\nAcknowledgment: The 50-50 rule hits hard")
            print(f"Response: JARVIS is here as a friend")
            print(f"Balance: 50-50 - mutual give and take")
            print(f"Status: {friendship_status['status']}")
            print("=" * 80)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()