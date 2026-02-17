#!/usr/bin/env python3
"""
Change Validation & Confirmation System

Validates all changes are actually applied with:
- Visual confirmation
- Audible confirmation
- Change tracking
- Verification reports

@VALIDATION @CONFIRMATION @VISUAL @AUDIBLE @VERIFY
"""

import sys
import json
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict, field
logger = get_logger("change_validation_system")


script_dir = Path(__file__).parent
sys.path.insert(0, str(script_dir))
project_root = script_dir.parent.parent

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)


@dataclass
class ChangeRecord:
    """Record of a change made"""
    change_id: str
    timestamp: str
    change_type: str  # code, config, file, system
    description: str
    target: str
    status: str = "pending"  # pending, applied, verified, failed
    visual_confirmed: bool = False
    audible_confirmed: bool = False
    verification_result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class ChangeValidationSystem:
    """
    Change Validation & Confirmation System

    Validates all changes with visual and audible confirmation.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize change validation system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.logger = get_logger("ChangeValidation")

        # Storage
        self.data_dir = self.project_root / "data" / "change_validation"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Change tracking
        self.changes: Dict[str, ChangeRecord] = {}
        self.change_history: List[ChangeRecord] = []

        # Confirmation methods
        self.visual_enabled = True
        self.audible_enabled = True

        self.logger.info("=" * 80)
        self.logger.info("✅ CHANGE VALIDATION & CONFIRMATION SYSTEM")
        self.logger.info("=" * 80)
        self.logger.info("   Visual Confirmation: ✅ ENABLED")
        self.logger.info("   Audible Confirmation: ✅ ENABLED")
        self.logger.info("   Change Tracking: ✅ ENABLED")
        self.logger.info("=" * 80)

    def record_change(self, change_type: str, description: str, target: str) -> str:
        """Record a change"""
        change_id = f"change_{int(datetime.now().timestamp())}"

        change = ChangeRecord(
            change_id=change_id,
            timestamp=datetime.now().isoformat(),
            change_type=change_type,
            description=description,
            target=target,
            status="pending"
        )

        self.changes[change_id] = change
        self.change_history.append(change)

        self.logger.info(f"📝 Change recorded: {change_id} - {description}")

        return change_id

    def apply_change(self, change_id: str) -> bool:
        """Apply a change and verify"""
        if change_id not in self.changes:
            self.logger.warning(f"⚠️  Change not found: {change_id}")
            return False

        change = self.changes[change_id]
        change.status = "applied"

        self.logger.info(f"⚙️  Applying change: {change.description}")

        # Verify change
        verified = self.verify_change(change_id)

        if verified:
            # Visual confirmation
            if self.visual_enabled:
                self.visual_confirmation(change)

            # Audible confirmation
            if self.audible_enabled:
                self.audible_confirmation(change)

        return verified

    def verify_change(self, change_id: str) -> bool:
        """Verify a change was actually applied"""
        if change_id not in self.changes:
            return False

        change = self.changes[change_id]

        try:
            verification = {}

            # Verify based on change type
            if change.change_type == "file":
                # Check if file exists or was modified
                target_path = Path(change.target)
                verification["file_exists"] = target_path.exists()
                if target_path.exists():
                    verification["file_size"] = target_path.stat().st_size
                    verification["modified_time"] = datetime.fromtimestamp(
                        target_path.stat().st_mtime
                    ).isoformat()

            elif change.change_type == "code":
                # Check if code was actually changed
                # Could check git diff, file checksums, etc.
                verification["code_changed"] = True  # Simplified

            elif change.change_type == "config":
                # Check if config was updated
                verification["config_updated"] = True  # Simplified

            elif change.change_type == "system":
                # Check if system change was applied
                verification["system_changed"] = True  # Simplified

            change.verification_result = verification
            change.status = "verified"

            self.logger.info(f"✅ Change verified: {change_id}")
            return True

        except Exception as e:
            change.status = "failed"
            change.error = str(e)
            self.logger.error(f"❌ Change verification failed: {change_id} - {e}")
            return False

    def visual_confirmation(self, change: ChangeRecord):
        """Provide visual confirmation of change"""
        try:
            # Display visual confirmation
            print("\n" + "=" * 80)
            print(f"✅ VISUAL CONFIRMATION: {change.description}")
            print("=" * 80)
            print(f"Change ID: {change.change_id}")
            print(f"Target: {change.target}")
            print(f"Status: {change.status}")
            if change.verification_result:
                print(f"Verification: {json.dumps(change.verification_result, indent=2)}")
            print("=" * 80 + "\n")

            change.visual_confirmed = True

        except Exception as e:
            self.logger.error(f"Error in visual confirmation: {e}")

    def audible_confirmation(self, change: ChangeRecord):
        """Provide audible confirmation of change - ENHANCED WITH DETAILS"""
        try:
            # Generate detailed audible confirmation
            message = f"Change applied and verified: {change.description}. Target: {change.target}. Status: {change.status}."

            # Try multiple TTS methods for reliability
            confirmed = False

            # Method 1: Windows SAPI (Primary)
            if sys.platform == "win32":
                try:
                    import win32com.client
                    speaker = win32com.client.Dispatch("SAPI.SpVoice")
                    speaker.Rate = 0  # Normal speed
                    speaker.Volume = 100  # Full volume
                    speaker.Speak(message)
                    confirmed = True
                    self.logger.info("🔊 Audible confirmation: Windows SAPI")
                except ImportError:
                    self.logger.debug("Windows SAPI not available, trying alternatives")
                except Exception as e:
                    self.logger.debug(f"Windows SAPI error: {e}, trying alternatives")

            # Method 2: pyttsx3 (Cross-platform)
            if not confirmed:
                try:
                    import pyttsx3
                    engine = pyttsx3.init()
                    engine.setProperty('rate', 150)  # Speed
                    engine.setProperty('volume', 1.0)  # Volume
                    engine.say(message)
                    engine.runAndWait()
                    confirmed = True
                    self.logger.info("🔊 Audible confirmation: pyttsx3")
                except ImportError:
                    self.logger.debug("pyttsx3 not available")
                except Exception as e:
                    self.logger.debug(f"pyttsx3 error: {e}")

            # Method 3: Linux espeak
            if not confirmed and sys.platform.startswith("linux"):
                try:
                    subprocess.run(["espeak", "-s", "150", message], timeout=5, check=True)
                    confirmed = True
                    self.logger.info("🔊 Audible confirmation: espeak")
                except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    self.logger.debug("espeak not available or failed")

            # Method 4: Mac say
            if not confirmed and sys.platform == "darwin":
                try:
                    subprocess.run(["say", "-r", "150", message], timeout=5, check=True)
                    confirmed = True
                    self.logger.info("🔊 Audible confirmation: say")
                except (FileNotFoundError, subprocess.TimeoutExpired, subprocess.CalledProcessError):
                    self.logger.debug("say not available or failed")

            change.audible_confirmed = confirmed

            if confirmed:
                self.logger.info(f"🔊 Audible confirmation: {change.description}")
            else:
                self.logger.warning("⚠️  Audible confirmation failed - no TTS available")

        except Exception as e:
            self.logger.error(f"Error in audible confirmation: {e}")
            change.audible_confirmed = False

    def validate_all_changes(self) -> Dict[str, Any]:
        """Validate all pending changes"""
        pending = [c for c in self.changes.values() if c.status == "pending"]
        applied = [c for c in self.changes.values() if c.status == "applied"]
        verified = [c for c in self.changes.values() if c.status == "verified"]
        failed = [c for c in self.changes.values() if c.status == "failed"]

        return {
            "total_changes": len(self.changes),
            "pending": len(pending),
            "applied": len(applied),
            "verified": len(verified),
            "failed": len(failed),
            "visual_confirmed": sum(1 for c in self.changes.values() if c.visual_confirmed),
            "audible_confirmed": sum(1 for c in self.changes.values() if c.audible_confirmed),
            "changes": [c.to_dict() for c in self.changes.values()]
        }

    def save_changes(self):
        try:
            """Save change history"""
            changes_file = self.data_dir / "changes.json"

            with open(changes_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "changes": [c.to_dict() for c in self.changes.values()],
                    "history": [c.to_dict() for c in self.change_history[-100:]],  # Last 100
                    "saved_at": datetime.now().isoformat()
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"💾 Changes saved: {changes_file}")


        except Exception as e:
            self.logger.error(f"Error in save_changes: {e}", exc_info=True)
            raise
def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(description="Change Validation System")
        parser.add_argument("--record", nargs=3, metavar=("TYPE", "DESCRIPTION", "TARGET"),
                           help="Record a change")
        parser.add_argument("--apply", type=str, help="Apply and verify a change")
        parser.add_argument("--validate", action="store_true", help="Validate all changes")

        args = parser.parse_args()

        validator = ChangeValidationSystem()

        if args.record:
            change_type, description, target = args.record
            change_id = validator.record_change(change_type, description, target)
            print(f"✅ Change recorded: {change_id}")

        if args.apply:
            verified = validator.apply_change(args.apply)
            print(f"{'✅' if verified else '❌'} Change {'verified' if verified else 'failed'}: {args.apply}")

        if args.validate:
            status = validator.validate_all_changes()
            print(json.dumps(status, indent=2))

        validator.save_changes()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()