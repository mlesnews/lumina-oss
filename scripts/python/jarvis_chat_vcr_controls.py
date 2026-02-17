#!/usr/bin/env python3
"""
JARVIS Chat VCR Controls

VCR-style controls (Play, Pause, Stop) for Cursor IDE chat window.
Readily available controls for voice requests and responses.

Tags: #JARVIS #VCR_CONTROLS #CHAT #VOICE @JARVIS @LUMINA
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

logger = get_logger("JARVISVCRControls")


class VCRState(Enum):
    """VCR control state"""
    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"
    RECORDING = "recording"


@dataclass
class VCRControlStatus:
    """VCR control status"""
    state: VCRState
    current_request_id: Optional[str] = None
    queue_size: int = 0
    can_play: bool = True
    can_pause: bool = False
    can_stop: bool = False
    can_record: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["state"] = self.state.value
        return data


class JARVISChatVCRControls:
    """
    VCR Controls for Cursor IDE Chat Window

    Provides Play, Pause, Stop controls for voice requests.
    Readily available in chat window.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize VCR controls"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # State
        self.state = VCRState.STOPPED
        self.current_request_id: Optional[str] = None

        # Voice queue integration
        try:
            from jarvis_voice_request_queue import JARVISVoiceRequestQueue
            self.voice_queue = JARVISVoiceRequestQueue(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Voice queue not available: {e}")
            self.voice_queue = None

        # Kenjar integration
        try:
            from kenjar_virtual_assistant import KenjarVirtualAssistant
            self.kenjar = KenjarVirtualAssistant(self.project_root)
        except Exception as e:
            logger.warning(f"   ⚠️  Kenjar not available: {e}")
            self.kenjar = None

        logger.info("✅ JARVIS Chat VCR Controls initialized")
        logger.info("   ▶️  Play - Start/Resume voice request")
        logger.info("   ⏸️  Pause - Pause current request")
        logger.info("   ⏹️  Stop - Stop current request")
        logger.info("   🎤 Record - Start voice input")

    def play(self, text: Optional[str] = None) -> Dict[str, Any]:
        """
        Play/Resume voice request

        Args:
            text: Optional text to queue (if not resuming)

        Returns:
            Status dictionary
        """
        if self.state == VCRState.PAUSED:
            # Resume paused request
            if self.voice_queue:
                resumed = self.voice_queue.resume_current_request()
                if resumed:
                    self.state = VCRState.PLAYING
                    logger.info("   ▶️  Resumed voice request")
                    return {
                        "action": "resumed",
                        "state": self.state.value,
                        "success": True
                    }

        elif text:
            # Queue new request
            if self.voice_queue:
                request_id = self.voice_queue.add_request(text)
                self.current_request_id = request_id
                self.state = VCRState.PLAYING
                logger.info(f"   ▶️  Queued voice request: {request_id}")
                return {
                    "action": "queued",
                    "request_id": request_id,
                    "state": self.state.value,
                    "success": True
                }

        # No action
        return {
            "action": "play",
            "state": self.state.value,
            "success": False,
            "message": "Nothing to play or resume"
        }

    def pause(self) -> Dict[str, Any]:
        """
        Pause current voice request

        Returns:
            Status dictionary
        """
        if self.state == VCRState.PLAYING:
            if self.voice_queue:
                paused = self.voice_queue.pause_current_request()
                if paused:
                    self.state = VCRState.PAUSED
                    logger.info("   ⏸️  Paused voice request")
                    return {
                        "action": "paused",
                        "state": self.state.value,
                        "success": True
                    }

        return {
            "action": "pause",
            "state": self.state.value,
            "success": False,
            "message": "Nothing to pause"
        }

    def stop(self) -> Dict[str, Any]:
        """
        Stop current voice request

        Returns:
            Status dictionary
        """
        if self.state in [VCRState.PLAYING, VCRState.PAUSED]:
            if self.voice_queue:
                stopped = self.voice_queue.stop_current_request()
                if stopped:
                    self.state = VCRState.STOPPED
                    self.current_request_id = None
                    logger.info("   ⏹️  Stopped voice request")
                    return {
                        "action": "stopped",
                        "state": self.state.value,
                        "success": True
                    }

        return {
            "action": "stop",
            "state": self.state.value,
            "success": False,
            "message": "Nothing to stop"
        }

    def record(self) -> Dict[str, Any]:
        """
        Start voice recording (microphone input)

        Returns:
            Status dictionary
        """
        if self.state == VCRState.RECORDING:
            # Already recording
            return {
                "action": "record",
                "state": self.state.value,
                "success": False,
                "message": "Already recording"
            }

        # Start recording
        if self.kenjar:
            try:
                text = self.kenjar.listen()
                if text:
                    # Queue the recorded text
                    if self.voice_queue:
                        request_id = self.voice_queue.add_request(text)
                        self.current_request_id = request_id
                        self.state = VCRState.PLAYING
                        logger.info(f"   🎤 Recorded and queued: {request_id}")
                        return {
                            "action": "recorded",
                            "request_id": request_id,
                            "text": text,
                            "state": self.state.value,
                            "success": True
                        }
                else:
                    self.state = VCRState.STOPPED
                    return {
                        "action": "record",
                        "state": self.state.value,
                        "success": False,
                        "message": "No voice input detected"
                    }
            except Exception as e:
                logger.error(f"   ❌ Recording error: {e}")
                self.state = VCRState.STOPPED
                return {
                    "action": "record",
                    "state": self.state.value,
                    "success": False,
                    "error": str(e)
                }

        return {
            "action": "record",
            "state": self.state.value,
            "success": False,
            "message": "Kenjar not available"
        }

    def get_status(self) -> VCRControlStatus:
        """Get current VCR control status"""
        queue_status = {}
        if self.voice_queue:
            queue_status = self.voice_queue.get_queue_status()

        return VCRControlStatus(
            state=self.state,
            current_request_id=self.current_request_id,
            queue_size=queue_status.get("queue_size", 0),
            can_play=self.state in [VCRState.STOPPED, VCRState.PAUSED] or queue_status.get("queue_size", 0) > 0,
            can_pause=self.state == VCRState.PLAYING,
            can_stop=self.state in [VCRState.PLAYING, VCRState.PAUSED],
            can_record=self.state != VCRState.RECORDING
        )

    def get_controls_html(self) -> str:
        """
        Get HTML for VCR controls (for chat window integration)

        Returns:
            HTML string with VCR controls
        """
        status = self.get_status()

        html = f"""
        <div class="jarvis-vcr-controls" style="display: flex; gap: 10px; padding: 10px; background: #1e1e1e; border-radius: 5px;">
            <button id="vcr-play" class="vcr-button" style="padding: 8px 16px; background: #007acc; color: white; border: none; border-radius: 4px; cursor: pointer;" {'disabled' if not status.can_play else ''}>
                ▶️ Play
            </button>
            <button id="vcr-pause" class="vcr-button" style="padding: 8px 16px; background: #ffa500; color: white; border: none; border-radius: 4px; cursor: pointer;" {'disabled' if not status.can_pause else ''}>
                ⏸️ Pause
            </button>
            <button id="vcr-stop" class="vcr-button" style="padding: 8px 16px; background: #dc3545; color: white; border: none; border-radius: 4px; cursor: pointer;" {'disabled' if not status.can_stop else ''}>
                ⏹️ Stop
            </button>
            <button id="vcr-record" class="vcr-button" style="padding: 8px 16px; background: #28a745; color: white; border: none; border-radius: 4px; cursor: pointer;" {'disabled' if not status.can_record else ''}>
                🎤 Record
            </button>
            <span style="color: #ccc; margin-left: 10px;">
                State: {status.state.value} | Queue: {status.queue_size}
            </span>
        </div>
        """

        return html

    def get_controls_json(self) -> Dict[str, Any]:
        """Get VCR controls as JSON (for API)"""
        status = self.get_status()
        return {
            "controls": {
                "play": {
                    "enabled": status.can_play,
                    "action": "play"
                },
                "pause": {
                    "enabled": status.can_pause,
                    "action": "pause"
                },
                "stop": {
                    "enabled": status.can_stop,
                    "action": "stop"
                },
                "record": {
                    "enabled": status.can_record,
                    "action": "record"
                }
            },
            "status": status.to_dict()
        }


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Chat VCR Controls")
        parser.add_argument("--play", type=str, nargs='?', const=True,
                           help="Play/Resume (optionally with text)")
        parser.add_argument("--pause", action="store_true", help="Pause")
        parser.add_argument("--stop", action="store_true", help="Stop")
        parser.add_argument("--record", action="store_true", help="Record")
        parser.add_argument("--status", action="store_true", help="Get status")
        parser.add_argument("--html", action="store_true", help="Get HTML controls")
        parser.add_argument("--json", action="store_true", help="JSON output")

        args = parser.parse_args()

        controls = JARVISChatVCRControls()

        if args.play is not None:
            if args.play is True:
                result = controls.play()
            else:
                result = controls.play(args.play)
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{'✅' if result['success'] else '❌'} {result['action']}: {result.get('message', '')}")

        elif args.pause:
            result = controls.pause()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{'✅' if result['success'] else '❌'} {result['action']}: {result.get('message', '')}")

        elif args.stop:
            result = controls.stop()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{'✅' if result['success'] else '❌'} {result['action']}: {result.get('message', '')}")

        elif args.record:
            result = controls.record()
            if args.json:
                print(json.dumps(result, indent=2))
            else:
                print(f"{'✅' if result['success'] else '❌'} {result['action']}: {result.get('message', '')}")

        elif args.html:
            print(controls.get_controls_html())

        elif args.status or not any([args.play, args.pause, args.stop, args.record, args.html]):
            status = controls.get_status()
            if args.json:
                print(json.dumps(status.to_dict(), indent=2))
            else:
                print("=" * 80)
                print("🎮 JARVIS CHAT VCR CONTROLS")
                print("=" * 80)
                print(f"State: {status.state.value}")
                print(f"Current Request: {status.current_request_id or 'None'}")
                print(f"Queue Size: {status.queue_size}")
                print(f"\nControls:")
                print(f"  ▶️  Play: {'✅ Enabled' if status.can_play else '❌ Disabled'}")
                print(f"  ⏸️  Pause: {'✅ Enabled' if status.can_pause else '❌ Disabled'}")
                print(f"  ⏹️  Stop: {'✅ Enabled' if status.can_stop else '❌ Disabled'}")
                print(f"  🎤 Record: {'✅ Enabled' if status.can_record else '❌ Disabled'}")
                print("=" * 80)

        else:
            parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()