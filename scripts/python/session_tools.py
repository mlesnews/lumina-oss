#!/usr/bin/env python3
"""
Session tools — OpenClaw-style agent-to-agent session API.

Exposes:
  sessions_list   — discover active JARVIS/character sessions (master + data/agent_sessions).
  sessions_history — fetch transcript/summary for a session (master or by id).
  sessions_send   — send a message to the master session (delegate/reply-back style).

Usage:
  python scripts/python/session_tools.py list [--json]
  python scripts/python/session_tools.py history [session_id] [--json]
  python scripts/python/session_tools.py send "message" [--agent-id delegate] [--reply-back]

Tags: #session_tools #control_plane #OpenClaw @JARVIS @PEAK
See: docs/system/CONTROL_PLANE_CONTRACT.md, docs/system/OPENCLAW_UNIQUE_FEATURES_AND_LUMINA_FIT.md
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent


def _add_paths() -> None:
    if str(PROJECT_ROOT) not in sys.path:
        sys.path.insert(0, str(PROJECT_ROOT))
    if str(SCRIPT_DIR) not in sys.path:
        sys.path.insert(0, str(SCRIPT_DIR))


def sessions_list(project_root: Path, as_json: bool = False) -> List[Dict[str, Any]]:
    """List active sessions: master + data/agent_sessions/*.json."""
    _add_paths()
    result: List[Dict[str, Any]] = []

    # Master session
    master_file = project_root / "data" / "jarvis_master_chat" / "master_session.json"
    if master_file.exists():
        try:
            data = json.loads(master_file.read_text(encoding="utf-8"))
            result.append(
                {
                    "session_id": data.get("session_id", "jarvis_master_chat"),
                    "session_name": data.get("session_name", "JARVIS Master Chat"),
                    "pinned": data.get("pinned", True),
                    "message_count": len(data.get("messages", [])),
                    "last_activity": data.get("last_activity"),
                    "source": "master",
                }
            )
        except (json.JSONDecodeError, OSError):
            result.append(
                {"session_id": "jarvis_master_chat", "source": "master", "error": "read_failed"}
            )

    # Agent sessions
    agent_dir = project_root / "data" / "agent_sessions"
    if agent_dir.exists():
        for f in agent_dir.glob("*.json"):
            if (
                f.name.startswith("session_")
                or f.name.endswith("_session.json")
                or "session" in f.name.lower()
            ):
                try:
                    data = json.loads(f.read_text(encoding="utf-8"))
                    sid = data.get("session_id") or data.get("sessionId") or f.stem
                    result.append(
                        {
                            "session_id": sid,
                            "file_name": f.name,
                            "source": "agent_sessions",
                            "last_activity": data.get("last_activity") or data.get("lastActivity"),
                        }
                    )
                except (json.JSONDecodeError, OSError):
                    result.append(
                        {
                            "session_id": f.stem,
                            "file_name": f.name,
                            "source": "agent_sessions",
                            "error": "read_failed",
                        }
                    )

    if as_json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for s in result:
            print(
                f"  {s.get('session_id', '?')}  {s.get('session_name', s.get('file_name', ''))}  ({s.get('source', '')})"
            )
    return result


def sessions_history(
    project_root: Path, session_id: Optional[str] = None, as_json: bool = False
) -> Dict[str, Any]:
    """Fetch transcript/summary for master session or a given session_id."""
    _add_paths()
    if session_id in (None, "", "jarvis_master_chat", "master"):
        master_file = project_root / "data" / "jarvis_master_chat" / "master_session.json"
        if not master_file.exists():
            out = {"session_id": "jarvis_master_chat", "error": "master_session not found"}
            if as_json:
                print(json.dumps(out, indent=2, ensure_ascii=False))
            return out
        try:
            data = json.loads(master_file.read_text(encoding="utf-8"))
            summary = {
                "session_id": data.get("session_id", "jarvis_master_chat"),
                "message_count": len(data.get("messages", [])),
                "last_activity": data.get("last_activity"),
                "recent_messages": data.get("messages", [])[-10:],
            }
            if as_json:
                print(json.dumps(summary, indent=2, ensure_ascii=False))
            return summary
        except (json.JSONDecodeError, OSError) as e:
            out = {"session_id": "jarvis_master_chat", "error": str(e)}
            if as_json:
                print(json.dumps(out, indent=2, ensure_ascii=False))
            return out

    # Look up by session_id in agent_sessions
    agent_dir = project_root / "data" / "agent_sessions"
    for f in agent_dir.glob("*.json"):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            sid = data.get("session_id") or data.get("sessionId") or f.stem
            if sid == session_id or f.stem == session_id:
                out = {"session_id": sid, "file_name": f.name, "data": data}
                if as_json:
                    print(json.dumps(out, indent=2, ensure_ascii=False))
                return out
        except (json.JSONDecodeError, OSError):
            continue
    out = {"session_id": session_id, "error": "session not found"}
    if as_json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def sessions_send(
    project_root: Path,
    message: str,
    agent_id: str = "delegate",
    reply_back: bool = False,
    as_json: bool = False,
) -> Dict[str, Any]:
    """Send a message to the master session (append as coordination message)."""
    _add_paths()
    try:
        from jarvis_master_chat_session import JARVISMasterChatSession

        chat = JARVISMasterChatSession(project_root=project_root)
        chat.add_message(
            agent_id=agent_id,
            agent_name=agent_id,
            message=message,
            message_type="coordination" if reply_back else "chat",
            metadata={"reply_back": reply_back},
        )
        out = {
            "ok": True,
            "session_id": "jarvis_master_chat",
            "agent_id": agent_id,
            "reply_back": reply_back,
        }
    except (ImportError, OSError, TypeError, AttributeError) as e:
        out = {"ok": False, "error": str(e)}
    if as_json:
        print(json.dumps(out, indent=2, ensure_ascii=False))
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Session tools: list, history, send.")
    parser.add_argument("command", choices=["list", "history", "send"], help="Command")
    parser.add_argument(
        "args", nargs="*", help="Arguments (e.g. session_id for history, message for send)"
    )
    parser.add_argument("--json", action="store_true", help="Output JSON")
    parser.add_argument(
        "--agent-id", default="delegate", help="Agent id for send (default: delegate)"
    )
    parser.add_argument("--reply-back", action="store_true", help="Mark send as reply-back")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="Project root")
    args = parser.parse_args()

    root = args.project_root

    if args.command == "list":
        sessions_list(root, as_json=args.json)
        return 0
    if args.command == "history":
        session_id = args.args[0] if args.args else None
        sessions_history(root, session_id=session_id, as_json=args.json)
        return 0
    if args.command == "send":
        message = " ".join(args.args) if args.args else ""
        if not message:
            print("Error: send requires a message", file=sys.stderr)
            return 1
        out = sessions_send(
            root, message, agent_id=args.agent_id, reply_back=args.reply_back, as_json=args.json
        )
        return 0 if out.get("ok") else 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
