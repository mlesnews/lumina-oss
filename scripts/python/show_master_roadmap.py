#!/usr/bin/env python3
"""
Quick Command to Show Master Todo List (One Ring)

Simple command to display the master todo list in chat.
Shows collapsed view by default. Use --expanded for full view.

Terminology:
- Master Todo List = One Ring = Persistent todos across all initiatives
- Padawan Todo List = Subagent Todo List = Session-specific todos (per initiative)
- Initiative = Individual agent chat session scope

Usage:
    python show_master_roadmap.py           # Collapsed (default)
    python show_master_roadmap.py --expanded  # Full expanded view

Supports terminology: master todo, roadmap, one ring, master list

Tags: #MASTER-TODO #ONE-RING #PADAWAN #SUBAGENT #INITIATIVE @LUMINA
"""

import sys
import argparse
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

from lumina_master_roadmap_display import get_master_roadmap

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Show Master Todo List (One Ring / Roadmap)")
    parser.add_argument("--expanded", action="store_true", help="Show expanded full view")
    parser.add_argument("--collapsed", action="store_true", help="Show collapsed summary (default)")

    args = parser.parse_args()

    roadmap = get_master_roadmap()
    expanded = args.expanded and not args.collapsed
    roadmap.display_roadmap(expanded=expanded)
