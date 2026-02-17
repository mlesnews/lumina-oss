#!/usr/bin/env python3
"""
Fix Docker Tasks - Convert docker-run/docker-build task types to shell tasks

Fixes VSCode tasks that use docker-run or docker-build task types
(which require Docker extension) by converting them to shell tasks.
"""

import json
import sys
from pathlib import Path
from universal_decision_tree import decide, DecisionContext, DecisionOutcome
import logging
logger = logging.getLogger("fix_docker_tasks")




# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

def fix_docker_tasks(tasks_file: Path):
    try:
        """Fix docker tasks in tasks.json"""
        if not tasks_file.exists():
            print(f"❌ Tasks file not found: {tasks_file}")
            return False

        # Read tasks
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_data = json.load(f)

        tasks = tasks_data.get('tasks', [])
        modified = False

        for task in tasks:
            task_type = task.get('type', '')

            # Fix docker-build
            if task_type == 'docker-build':
                docker_build = task.get('dockerBuild', {})

                task['type'] = 'shell'
                task['command'] = 'docker'
                task['args'] = [
                    'build',
                    '-t',
                    docker_build.get('tag', '${workspaceFolderBasename}:latest'),
                    '-f',
                    docker_build.get('dockerfile', '${workspaceFolder}/Dockerfile'),
                    docker_build.get('context', '${workspaceFolder}')
                ]

                if docker_build.get('pull'):
                    task['args'].insert(1, '--pull')

                # Remove dockerBuild
                if 'dockerBuild' in task:
                    del task['dockerBuild']

                # Ensure presentation
                if 'presentation' not in task:
                    task['presentation'] = {
                        'reveal': 'always',
                        'panel': 'dedicated',
                        'clear': True
                    }

                # Ensure problemMatcher
                if 'problemMatcher' not in task:
                    task['problemMatcher'] = []

                modified = True
                print(f"✅ Fixed docker-build task: {task.get('label', 'unnamed')}")

            # Fix docker-run
            elif task_type == 'docker-run':
                # Extract docker run configuration
                python_config = task.get('python', {})
                docker_run = task.get('dockerRun', {})

                # Build docker run command
                args = ['run', '--rm']

                # Add port mapping if specified
                if docker_run.get('ports'):
                    for port in docker_run['ports']:
                        args.extend(['-p', port])
                elif python_config.get('port'):
                    args.extend(['-p', f"{python_config['port']}:{python_config['port']}"])
                else:
                    args.extend(['-p', '8000:8000'])

                # Add container name if specified
                if docker_run.get('containerName'):
                    args.extend(['--name', docker_run['containerName']])

                # Add image
                image = docker_run.get('image') or task.get('image') or '${workspaceFolderBasename}:latest'
                args.append(image)

                # Add Python command if specified
                if python_config:
                    if python_config.get('module'):
                        args.append(python_config['module'])
                    if python_config.get('args'):
                        args.extend(python_config['args'])

                task['type'] = 'shell'
                task['command'] = 'docker'
                task['args'] = args

                # Remove docker-specific configs
                for key in ['dockerRun', 'python', 'image']:
                    if key in task:
                        del task[key]

                # Ensure presentation
                if 'presentation' not in task:
                    task['presentation'] = {
                        'reveal': 'always',
                        'panel': 'dedicated',
                        'clear': True
                    }

                # Ensure problemMatcher
                if 'problemMatcher' not in task:
                    task['problemMatcher'] = []

                modified = True
                print(f"✅ Fixed docker-run task: {task.get('label', 'unnamed')}")

        if modified:
            # Write back
            with open(tasks_file, 'w', encoding='utf-8') as f:
                json.dump(tasks_data, f, indent=2, ensure_ascii=False)
            print(f"✅ Updated tasks file: {tasks_file}")
            return True
        else:
            print(f"✓ No docker tasks found to fix in: {tasks_file}")
            return False


    except Exception as e:
        logger.error(f"Error in fix_docker_tasks: {e}", exc_info=True)
        raise
def main():
    try:
        """Main function"""
        import argparse

        parser = argparse.ArgumentParser(description="Fix Docker tasks in VSCode tasks.json")
        parser.add_argument("--workspace", help="Workspace path (default: current directory)")
        parser.add_argument("--all", action="store_true", help="Fix all workspaces")

        args = parser.parse_args()

        if args.all:
            # Find all tasks.json files
            workspaces = [
                Path(".").resolve(),
                Path("../<COMPANY>-financial-services_llc-env").resolve(),
                Path("../<COMPANY_ID>-env").resolve(),
            ]

            fixed_count = 0
            for workspace in workspaces:
                tasks_file = workspace / ".vscode" / "tasks.json"
                if tasks_file.exists():
                    print(f"\n📋 Checking: {workspace.name}")
                    if fix_docker_tasks(tasks_file):
                        fixed_count += 1

            print(f"\n✅ Fixed {fixed_count} workspace(s)")

        else:
            workspace = Path(args.workspace) if args.workspace else Path(".").resolve()
            tasks_file = workspace / ".vscode" / "tasks.json"

            if not tasks_file.exists():
                print(f"❌ Tasks file not found: {tasks_file}")
                print("   Try: python scripts/python/fix_docker_tasks.py --all")
                sys.exit(1)

            fix_docker_tasks(tasks_file)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()