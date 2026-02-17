#!/usr/bin/env python3
"""
JARVIS Rollback Manager

Creates rollback plan and manages rollback procedures for project-wide changes.
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISRollbackManager")


class JARVISRollbackManager:
    """
    Manage rollback procedures
    """

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger

    def create_rollback_branch(self) -> Dict[str, Any]:
        """Create rollback branch from current state"""
        try:
            # Get current commit hash
            result = subprocess.run(
                ['git', 'rev-parse', 'HEAD'],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {'success': False, 'error': 'Not a git repository'}

            current_commit = result.stdout.strip()

            # Create rollback branch
            branch_name = f"rollback-{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            result = subprocess.run(
                ['git', 'checkout', '-b', branch_name],
                cwd=self.project_root,
                capture_output=True,
                text=True
            )

            if result.returncode != 0:
                return {'success': False, 'error': f'Failed to create branch: {result.stderr}'}

            self.logger.info(f"✅ Created rollback branch: {branch_name}")

            return {
                'success': True,
                'branch': branch_name,
                'commit': current_commit
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_rollback_plan(self) -> Dict[str, Any]:
        """Create comprehensive rollback plan"""
        plan = {
            'created_at': datetime.now().isoformat(),
            'rollback_steps': [
                {
                    'step': 1,
                    'action': 'Identify problematic commit',
                    'command': 'git log --oneline -10',
                    'description': 'Find the commit that introduced issues'
                },
                {
                    'step': 2,
                    'action': 'Create rollback branch',
                    'command': 'git checkout -b rollback-YYYYMMDD_HHMMSS',
                    'description': 'Create branch for rollback'
                },
                {
                    'step': 3,
                    'action': 'Revert specific files',
                    'command': 'git checkout HEAD~1 -- path/to/file.py',
                    'description': 'Revert specific files if needed'
                },
                {
                    'step': 4,
                    'action': 'Revert entire commit',
                    'command': 'git revert HEAD',
                    'description': 'Revert the problematic commit'
                },
                {
                    'step': 5,
                    'action': 'Test rollback',
                    'command': 'python scripts/python/jarvis_validation_suite.py --validate',
                    'description': 'Validate that rollback fixed issues'
                },
                {
                    'step': 6,
                    'action': 'Merge rollback',
                    'command': 'git checkout main && git merge rollback-branch',
                    'description': 'Merge rollback into main branch'
                }
            ],
            'backup_locations': [
                str(self.project_root / '.git'),
                str(self.project_root / 'scripts' / 'python')
            ],
            'rollback_commands': {
                'full_rollback': 'git reset --hard HEAD~1',
                'selective_rollback': 'git checkout HEAD~1 -- scripts/python/',
                'create_backup': f'git tag backup-{datetime.now().strftime("%Y%m%d_%H%M%S")}'
            }
        }

        return plan

    def save_rollback_plan(self, plan: Dict[str, Any]) -> Path:
        try:
            """Save rollback plan to file"""
            plan_file = self.project_root / "data" / "rollback_plans" / f"rollback_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            plan_file.parent.mkdir(parents=True, exist_ok=True)

            with open(plan_file, 'w') as f:
                json.dump(plan, f, indent=2)

            self.logger.info(f"✅ Rollback plan saved: {plan_file}")

            return plan_file


        except Exception as e:
            self.logger.error(f"Error in save_rollback_plan: {e}", exc_info=True)
            raise
def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Rollback Manager")
        parser.add_argument("--create-branch", action="store_true", help="Create rollback branch")
        parser.add_argument("--create-plan", action="store_true", help="Create rollback plan")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        manager = JARVISRollbackManager(project_root)

        if args.create_branch or args.create_plan or not args:
            # Create rollback branch
            branch_result = manager.create_rollback_branch()
            if branch_result.get('success'):
                print(f"✅ Rollback branch created: {branch_result['branch']}")

            # Create rollback plan
            plan = manager.create_rollback_plan()
            plan_file = manager.save_rollback_plan(plan)

            print(f"✅ Rollback plan created: {plan_file}")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()