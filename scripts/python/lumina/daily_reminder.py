#!/usr/bin/env python3
"""
Lumina Daily Reminder

Daily reminder of core memories to stay agile and tool-agnostic.

Tags: #LUMINA #CORE_MEMORY #DAILY_REMINDER @JARVIS @LUMINA
"""

from lumina.core_memory import LuminaCoreMemory

def main():
    """Print daily reminder"""
    core_memory = LuminaCoreMemory()

    print("=" * 80)
    print("🧠 LUMINA DAILY REMINDER")
    print("=" * 80)
    print()
    print(core_memory.get_daily_reminder())
    print()
    print("=" * 80)
    print("Remember: Tools are just tools. Principles are what matter.")
    print("Stay agile, stay light, stay flexible. Outmaneuver the giants.")
    print("=" * 80)

if __name__ == "__main__":


    main()