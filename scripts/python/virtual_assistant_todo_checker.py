#!/usr/bin/env python3
"""
Virtual Assistant Todo Checker

Checks master and padawan todo lists for outstanding Virtual Assistant items
and compares with current implementation status.

Tags: #TODO #VIRTUAL_ASSISTANT #JARVIS_VA #IMVA #ACE #AVA @JARVIS @LUMINA  # [ADDRESSED]  # [ADDRESSED]
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Any

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)
    CharacterAvatarRegistry = None
    CharacterType = None

logger = get_logger("VATodoChecker")


def load_master_todos() -> Dict[str, Any]:
    """Load master todos"""
    todos_file = project_root / "data" / "todo" / "master_todos.json"
    if todos_file.exists():
        try:
            with open(todos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading master todos: {e}")
    return {}


def load_padawan_todos() -> Dict[str, Any]:
    """Load padawan todos"""
    todos_file = project_root / "data" / "ask_database" / "master_padawan_todos.json"
    if todos_file.exists():
        try:
            with open(todos_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading padawan todos: {e}")
    return {}


def find_va_todos(todos: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Find Virtual Assistant related todos"""
    va_keywords = [
        "virtual assistant", "VA", "JARVIS", "IMVA", "ACE", "AVA",
        "Iron Man", "Armory Crate", "Animated", "VFX", "voice"
    ]

    va_todos = []
    for todo_id, todo in todos.items():
        title = todo.get("title", "").lower()
        description = todo.get("description", "").lower()
        tags = [tag.lower() for tag in todo.get("tags", [])]

        # Check if todo is VA-related
        for keyword in va_keywords:
            if (keyword.lower() in title or 
                keyword.lower() in description or 
                any(keyword.lower() in tag for tag in tags)):
                va_todos.append({
                    "id": todo_id,
                    "title": todo.get("title"),
                    "description": todo.get("description"),
                    "status": todo.get("status"),
                    "priority": todo.get("priority"),
                    "category": todo.get("category"),
                    "tags": todo.get("tags", [])
                })
                break

    return va_todos


def check_va_implementation_status() -> Dict[str, Any]:
    """Check current VA implementation status"""
    if not CharacterAvatarRegistry:
        return {"error": "CharacterAvatarRegistry not available"}

    registry = CharacterAvatarRegistry()
    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    status = {
        "total_vas": len(vas),
        "vas": [],
        "features": {
            "transformation_enabled": 0,
            "combat_mode_enabled": 0,
            "wopr_stances_enabled": 0,
            "voice_enabled": 0
        }
    }

    for va in vas:
        va_info = {
            "id": va.character_id,
            "name": va.name,
            "role": va.role,
            "lore": va.lore,
            "transformation": va.transformation_enabled,
            "combat_mode": va.combat_mode_enabled,
            "wopr_stances": va.wopr_stances_enabled,
            "voice": va.voice_enabled,
            "hierarchy": va.hierarchy_level
        }
        status["vas"].append(va_info)

        if va.transformation_enabled:
            status["features"]["transformation_enabled"] += 1
        if va.combat_mode_enabled:
            status["features"]["combat_mode_enabled"] += 1
        if va.wopr_stances_enabled:
            status["features"]["wopr_stances_enabled"] += 1
        if va.voice_enabled:
            status["features"]["voice_enabled"] += 1

    return status


def main():
    """Main entry point"""
    print("=" * 80)
    print("📋 VIRTUAL ASSISTANT TODO CHECKER")
    print("=" * 80)
    print()

    # Load todos
    master_todos = load_master_todos()
    padawan_todos = load_padawan_todos()

    print(f"📋 Master Todos: {len(master_todos)}")
    print(f"📋 Padawan Todos: {len(padawan_todos)}")
    print()

    # Find VA-related todos
    master_va_todos = find_va_todos(master_todos)
    padawan_va_todos = find_va_todos(padawan_todos)

    print("=" * 80)
    print("📋 OUTSTANDING VA TODOS")
    print("=" * 80)
    print()

    # Master todos
    if master_va_todos:
        print(f"MASTER TODOS - VA Related: {len(master_va_todos)}")
        for todo in master_va_todos:
            status_icon = "✅" if todo["status"] == "complete" else "⏳" if todo["status"] == "in_progress" else "📋"
            print(f"  {status_icon} [{todo['priority'].upper()}] {todo['title']}")
            print(f"     Status: {todo['status']}")
            print(f"     Category: {todo['category']}")
            if todo['description']:
                desc = todo['description'][:100] + "..." if len(todo['description']) > 100 else todo['description']
                print(f"     Description: {desc}")
            if todo.get('notes'):
                print(f"     Notes: {', '.join(todo['notes'][:2])}")
            print()
    else:
        print("  No VA-related todos found in master list")
        print()

    # Padawan todos
    if padawan_va_todos:
        print(f"PADAWAN TODOS - VA Related: {len(padawan_va_todos)}")
        for todo in padawan_va_todos:
            print(f"  📋 {todo.get('master_todo', todo.get('title', 'N/A'))}")
            print(f"     Master Status: {todo.get('master_status', 'N/A')}")
            print(f"     Padawan Status: {todo.get('padawan_status', 'N/A')}")
            print()
    else:
        print("  No VA-related todos found in padawan list")
        print()

    # Check implementation status
    print("=" * 80)
    print("✅ CURRENT VA IMPLEMENTATION STATUS")
    print("=" * 80)
    print()

    va_status = check_va_implementation_status()
    if "error" not in va_status:
        print(f"Total Virtual Assistants: {va_status['total_vas']}")
        print()

        for va in va_status["vas"]:
            print(f"  • {va['name']} ({va['id']})")
            print(f"    Role: {va['role']}")
            print(f"    Lore: {va['lore']}")
            print(f"    Hierarchy: {va['hierarchy']}")
            print(f"    Features:")
            if va['transformation']:
                print(f"      ✅ Transformation Enabled")
            if va['combat_mode']:
                print(f"      ✅ Combat Mode Enabled")
            if va['wopr_stances']:
                print(f"      ✅ WOPR Stances Enabled")
            if va['voice']:
                print(f"      ✅ Voice Enabled")
            print()

        print("Feature Summary:")
        print(f"  Transformation: {va_status['features']['transformation_enabled']}/{va_status['total_vas']}")
        print(f"  Combat Mode: {va_status['features']['combat_mode_enabled']}/{va_status['total_vas']}")
        print(f"  WOPR Stances: {va_status['features']['wopr_stances_enabled']}/{va_status['total_vas']}")
        print(f"  Voice: {va_status['features']['voice_enabled']}/{va_status['total_vas']}")
        print()

    # Compare todos with implementation
    print("=" * 80)
    print("🔍 TODO vs IMPLEMENTATION COMPARISON")
    print("=" * 80)
    print()

    pending_va_todos = [t for t in master_va_todos if t["status"] in ["pending", "in_progress"]]

    if pending_va_todos:
        print(f"Outstanding VA Todos: {len(pending_va_todos)}")
        for todo in pending_va_todos:
            print(f"  📋 {todo['title']}")
            print(f"     Priority: {todo['priority']}")
            print(f"     Status: {todo['status']}")
            print()

            # Check if this relates to existing VAs
            if "JARVIS" in todo['title'] or "IMVA" in todo['title']:
                print(f"     → Relates to: JARVIS_VA, IMVA")
            if "ACE" in todo['title'] or "Armory" in todo['title']:
                print(f"     → Relates to: ACE (ACE's Armory Crate)")
            if "AVA" in todo['title']:
                print(f"     → Relates to: AVA (placeholder system)")
            print()
    else:
        print("✅ No outstanding VA todos found")
        print()

    print("=" * 80)


if __name__ == "__main__":


    main()