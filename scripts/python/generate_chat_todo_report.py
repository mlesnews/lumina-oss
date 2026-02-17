#!/usr/bin/env python3
"""
Generate a dual Master/Padawan To-Do report for display in chat sessions.
"""

import json
from pathlib import Path
from datetime import datetime
import logging
logger = logging.getLogger("generate_chat_todo_report")


def generate_chat_todo_report():
    try:
        project_root = Path(__file__).parent.parent.parent
        master_file = project_root / "data" / "todo" / "master_todos.json"
        padawan_file = project_root / "data" / "ask_database" / "master_padawan_todos.json"

        report = []
        report.append("# 📋 LUMINA To-Do Lists")
        report.append(f"Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")

        # 1. Master To-Do List
        report.append("## 🏆 #MASTER To-Do List")
        if master_file.exists():
            with open(master_file, 'r', encoding='utf-8') as f:
                master_data = json.load(f)

            # Get active tasks
            active_master = [t for t in master_data.values() if t['status'] in ['in_progress', 'pending']]
            active_master.sort(key=lambda t: t.get('priority', 'medium'), reverse=True)

            if active_master:
                for t in active_master[:10]: # Show top 10
                    status_icon = "🔄" if t['status'] == 'in_progress' else "📅"
                    report.append(f"- {status_icon} **{t['title']}** [{t.get('priority', 'medium').upper()}]")
            else:
                report.append("- No active tasks in Master list.")
        else:
            report.append("- Master to-do file not found.")

        report.append("")

        # 2. Padawan To-Do List
        report.append("## 🎓 #PADAWAN To-Do List")
        if padawan_file.exists():
            with open(padawan_file, 'r', encoding='utf-8') as f:
                padawan_data = json.load(f)

            active_padawan = [t for t in padawan_data.values() if t['padawan_status'] != 'completed']

            if active_padawan:
                for t in active_padawan[:10]:
                    status_icon = "⏳"
                    report.append(f"- {status_icon} **{t['padawan_todo']}**")
            else:
                report.append("- No active tasks in Padawan list.")
        else:
            report.append("- Padawan to-do file not found.")

        return "\n".join(report)

    except Exception as e:
        logger.error(f"Error in generate_chat_todo_report: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    print(generate_chat_todo_report())
