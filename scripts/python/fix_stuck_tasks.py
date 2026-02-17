#!/usr/bin/env python3
"""Fix stuck tasks in production"""
import json
from pathlib import Path

project_root = Path("C:/Users/mlesn/Dropbox/my_projects/.lumina")
tasks_file = project_root / "data" / "quantum_anime" / "production" / "production_tasks.json"

tasks = json.load(open(tasks_file))
fixed = 0
for task in tasks:
    if task['status'] == 'in_progress':
        # Check if output exists
        output_path = Path(task.get('output_path', ''))
        if output_path.exists() or 'storyboard' in task['task_id']:
            task['status'] = 'complete'
            fixed += 1
            print(f"Fixed: {task['task_id']}")

json.dump(tasks, open(tasks_file, 'w'), indent=2)
print(f"Fixed {fixed} stuck tasks")
