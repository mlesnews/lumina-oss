#!/usr/bin/env python3
"""
Resume All Agent Sessions - @doit Integration
Resumes incomplete agent chat sessions with resource-aware staggering and @doit execution
"""

import sys
import json
import time
import psutil
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("ResumeSessionsDoit")

class SessionResumer:
    """Resume incomplete agent sessions with resource balancing"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.sessions_dir = self.project_root / "data" / "r5_living_matrix" / "sessions"
        self.output_dir = self.project_root / "data" / "resumed_sessions"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Resource limits
        self.max_cpu = 75.0
        self.max_memory = 80.0

        # Stagger delays by priority (seconds)
        self.stagger_delays = {
            "Immediate": 1.0,
            "Urgent": 2.0,
            "Elevated": 5.0,
            "Routine": 10.0
        }

    def get_resources(self) -> Dict[str, float]:
        """Get current resource usage"""
        return {
            "cpu": psutil.cpu_percent(interval=0.1),
            "memory": psutil.virtual_memory().percent
        }

    def should_throttle(self) -> bool:
        """Check if should throttle"""
        res = self.get_resources()
        return res["cpu"] > self.max_cpu or res["memory"] > self.max_memory

    def find_incomplete_sessions(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Find incomplete sessions (limit to prevent overload)"""
        logger.info("🔍 Finding incomplete sessions...")
        incomplete = []

        if not self.sessions_dir.exists():
            logger.warning(f"Sessions directory not found: {self.sessions_dir}")
            return incomplete

        session_files = list(self.sessions_dir.glob("cursor_chat_json*.json"))
        logger.info(f"Found {len(session_files)} cursor chat session files")

        # Limit processing to prevent overload
        session_files = sorted(session_files, key=lambda p: p.stat().st_mtime, reverse=True)[:limit]

        for session_file in session_files:
            try:
                with open(session_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                messages = data.get("messages", [])

                # Check if incomplete (few messages or no clear completion)
                if len(messages) < 3:
                    incomplete.append({
                        "file": session_file,
                        "session_id": data.get("session_id", session_file.stem),
                        "messages": len(messages),
                        "timestamp": datetime.fromtimestamp(session_file.stat().st_mtime)
                    })
            except Exception as e:
                logger.debug(f"Error reading {session_file.name}: {e}")
                continue

        logger.info(f"Found {len(incomplete)} incomplete sessions")
        return incomplete

    def calculate_priority(self, session: Dict[str, Any]) -> str:
        """Calculate priority based on age"""
        age_hours = (datetime.now() - session["timestamp"]).total_seconds() / 3600

        if age_hours < 1:
            return "Immediate"
        elif age_hours < 6:
            return "Urgent"
        elif age_hours < 24:
            return "Elevated"
        else:
            return "Routine"

    def resume_session(self, session: Dict[str, Any]) -> bool:
        """Resume a session"""
        try:
            session_id = session["session_id"]

            # Mark as resumed
            with open(session["file"], 'r', encoding='utf-8') as f:
                data = json.load(f)

            data["resumed"] = True
            data["resume_timestamp"] = datetime.now().isoformat()

            output_file = self.output_dir / f"resumed_{session_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            logger.info(f"✅ Resumed: {session_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to resume {session['session_id']}: {e}")
            return False

    def resume_all(self, max_sessions: int = 50) -> Dict[str, Any]:
        """Resume all incomplete sessions with staggering"""
        logger.info("=" * 60)
        logger.info("🚀 RESUMING INCOMPLETE SESSIONS")
        logger.info("=" * 60)

        # Find incomplete sessions
        incomplete = self.find_incomplete_sessions(limit=max_sessions)

        if not incomplete:
            logger.info("✅ No incomplete sessions found")
            return {"status": "complete", "resumed": 0}

        # Sort by timestamp (oldest first)
        incomplete.sort(key=lambda s: s["timestamp"])

        # Calculate priorities
        for session in incomplete:
            session["priority"] = self.calculate_priority(session)

        # Sort by priority
        priority_order = {"Immediate": 0, "Urgent": 1, "Elevated": 2, "Routine": 3}
        incomplete.sort(key=lambda s: priority_order.get(s["priority"], 999))

        # Resume with staggering
        resumed = 0
        failed = 0

        logger.info(f"\nProcessing {len(incomplete)} sessions...")

        for i, session in enumerate(incomplete):
            # Throttle if needed
            if self.should_throttle():
                res = self.get_resources()
                logger.warning(f"⚠️  High resource usage (CPU: {res['cpu']:.1f}%, Memory: {res['memory']:.1f}%)")
                logger.info("⏸️  Pausing 5 seconds...")
                time.sleep(5.0)

            # Stagger delay
            if i > 0:
                delay = self.stagger_delays.get(session["priority"], 10.0)
                logger.info(f"⏳ Staggering {delay:.1f}s ({session['priority']}) - {session['session_id']}")
                time.sleep(delay)

            # Resume
            if self.resume_session(session):
                resumed += 1
            else:
                failed += 1

            # Progress
            if (i + 1) % 10 == 0:
                logger.info(f"📊 Progress: {i+1}/{len(incomplete)} ({(i+1)/len(incomplete)*100:.1f}%)")

        # Summary
        logger.info("=" * 60)
        logger.info(f"✅ COMPLETE: Resumed {resumed}, Failed {failed}")
        logger.info("=" * 60)

        final_res = self.get_resources()
        logger.info(f"📊 Final resources: CPU {final_res['cpu']:.1f}%, Memory {final_res['memory']:.1f}%")

        return {
            "status": "complete",
            "total": len(incomplete),
            "resumed": resumed,
            "failed": failed
        }

def main():
    """Main execution - @doit pattern"""
    import argparse

    parser = argparse.ArgumentParser(description="Resume incomplete agent sessions")
    parser.add_argument("--max-sessions", type=int, default=50, help="Max sessions to process")
    parser.add_argument("--max-cpu", type=float, default=75.0, help="Max CPU percent")
    parser.add_argument("--max-memory", type=float, default=80.0, help="Max memory percent")

    args = parser.parse_args()

    resumer = SessionResumer()
    resumer.max_cpu = args.max_cpu
    resumer.max_memory = args.max_memory

    # Initial resources
    initial = resumer.get_resources()
    logger.info(f"📊 Initial: CPU {initial['cpu']:.1f}%, Memory {initial['memory']:.1f}%")
    logger.info("")

    # Resume all
    result = resumer.resume_all(max_sessions=args.max_sessions)

    return result

if __name__ == "__main__":
    sys.exit(0 if result.get("status") == "complete" else 1)



    result = main()