#!/usr/bin/env python3
"""
Team Status Report
Quick status report of all teams and their tasks

Tags: #TEAMS #STATUS #REPORT @JARVIS @LUMINA
"""
import sys
from pathlib import Path
from datetime import datetime

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from company_it_teams_ai_clustering import CompanyITTeams, TaskStatus

def main():
    teams = CompanyITTeams(project_root)

    print("=" * 80)
    print("📊 COMPANY IT TEAMS - QUICK STATUS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
    print("")

    # Summary by team
    for team_name, team in teams.teams.items():
        team_tasks = teams.get_team_tasks(team_name)
        pending = [t for t in team_tasks if t.status == TaskStatus.PENDING]
        in_progress = [t for t in team_tasks if t.status == TaskStatus.IN_PROGRESS]
        completed = [t for t in team_tasks if t.status == TaskStatus.COMPLETED]

        print(f"👥 {team.name}")
        print(f"   Total Tasks: {len(team_tasks)}")
        print(f"   ⏳ Pending: {len(pending)}")
        print(f"   🔄 In Progress: {len(in_progress)}")
        print(f"   ✅ Completed: {len(completed)}")
        if pending:
            print("   Pending Tasks:")
            for task in pending:
                priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
                print(f"      {priority_icon} [{task.id}] {task.title}")
        print("")

    # Critical path
    critical = teams.get_critical_tasks()
    if critical:
        print("=" * 80)
        print("🔴 CRITICAL PATH")
        print("=" * 80)
        for task in critical:
            print(f"   [{task.id}] {task.title}")
            print(f"      Team: {teams.teams[task.assigned_team].name}")
            print(f"      Assigned: {task.assigned_to}")
        print("")

    print("=" * 80)
    print("💡 To execute tasks:")
    print("   python scripts/python/execute_team_tasks.py --task <TASK_ID>")
    print("   python scripts/python/execute_team_tasks.py --team <team_name>")
    print("   python scripts/python/execute_team_tasks.py --critical")
    print("=" * 80)

    return 0

if __name__ == "__main__":

    sys.exit(main())