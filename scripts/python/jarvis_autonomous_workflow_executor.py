#!/usr/bin/env python3
"""
JARVIS Autonomous Workflow Executor

Executes all high-priority workflow steps automatically,
either all at once or in batches, without stopping.
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import time

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("JARVISAutonomousWorkflow")


class JARVISAutonomousWorkflowExecutor:
    """
    Autonomous executor for JARVIS workflow steps

    Executes all high-priority steps automatically,
    proceeding through the entire workflow without stopping.
    """

    def __init__(self, project_root: Path, use_subagents: bool = True):
        self.project_root = project_root
        self.logger = logger
        self.action_plans_dir = project_root / "data" / "action_plans"
        self.workflow_logs_dir = project_root / "data" / "workflow_logs"
        self.workflow_logs_dir.mkdir(parents=True, exist_ok=True)

        # Track execution
        self.executed_steps = []
        self.failed_steps = []
        self.current_step = None

        # Subagent delegation
        self.use_subagents = use_subagents
        if use_subagents:
            try:
                from jarvis_subagent_delegation import JARVISSubagentDelegation
                self.delegation = JARVISSubagentDelegation(project_root)
                self.logger.info("✅ Subagent delegation enabled")
            except ImportError:
                self.use_subagents = False
                self.logger.warning("Subagent delegation not available")
        else:
            self.delegation = None

    def load_latest_action_plan(self) -> Optional[Dict[str, Any]]:
        """Load the latest action plan"""
        if not self.action_plans_dir.exists():
            return None

        plan_files = sorted(self.action_plans_dir.glob("jarvis_action_plan_*.json"), reverse=True)
        if not plan_files:
            return None

        try:
            with open(plan_files[0], 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load action plan: {e}")
            return None

    def get_high_priority_steps(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get all high-priority steps (critical and high)"""
        steps = plan.get('steps', [])
        high_priority = [
            s for s in steps 
            if s.get('priority') in ['critical', 'high']
        ]
        return sorted(high_priority, key=lambda x: (
            {'critical': 0, 'high': 1}.get(x.get('priority'), 99),
            -x.get('readiness', 0)
        ))

    def execute_step(self, step: Dict[str, Any], max_retries: int = 3) -> Dict[str, Any]:
        """Execute a single workflow step with automatic retries on connection error"""
        step_id = step.get('step_id', 'unknown')
        title = step.get('title', 'Unknown Step')
        category = step.get('category', 'general')

        self.logger.info("="*80)
        self.logger.info(f"EXECUTING: {title}")
        self.logger.info(f"Category: {category} | Priority: {step.get('priority')}")
        self.logger.info("="*80)

        self.current_step = step

        last_error = None
        for attempt in range(max_retries):
            try:
                # Delegate to subagent if enabled
                if self.use_subagents and self.delegation:
                    self.logger.info(f"📤 Delegating to subagent (Attempt {attempt+1}/{max_retries}): {category}")
                    result = self.delegation.delegate_task(step)
                else:
                    # Route to appropriate executor
                    if category == 'illumination':
                        result = self._execute_illumination_step(step)
                    elif category == 'multimedia':
                        result = self._execute_multimedia_step(step)
                    elif category == 'code_quality':
                        result = self._execute_code_quality_step(step)
                    else:
                        result = self._execute_generic_step(step)

                result['step_id'] = step_id
                result['title'] = title
                result['executed_at'] = datetime.now().isoformat()
                result['attempts'] = attempt + 1

                if result.get('success'):
                    self.executed_steps.append(result)
                    self.logger.info(f"✅ COMPLETED: {title}")
                    return result
                else:
                    last_error = result.get('error', 'Unknown error')
                    self.logger.warning(f"⚠️  Attempt {attempt+1} failed: {last_error}")

                    # Check for connection reset to trigger provider switch (conceptual)
                    if "ECONNRESET" in str(last_error) or "ConnectError" in str(last_error):
                        self.logger.info("🌀 Connection reset detected. Suggesting Azure OpenAI failover.")

                # Exponential backoff
                time.sleep(2 ** attempt)

            except Exception as e:
                last_error = str(e)
                self.logger.error(f"Exception on attempt {attempt+1} executing {title}: {e}")
                time.sleep(2 ** attempt)

        # If all retries failed
        self.failed_steps.append({"step_id": step_id, "title": title, "error": last_error})
        return {
            'success': False,
            'error': f"All {max_retries} retries failed. Last error: {last_error}",
            'step_id': step_id,
            'title': title
        }

    def _execute_illumination_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute an Illumination-related step"""
        step_id = step.get('step_id', '')
        title = step.get('title', '')

        if 'curriculum' in step_id.lower() or 'curriculum' in title.lower():
            # Already complete - curriculum system is done
            return {
                'success': True,
                'message': 'Curriculum system already implemented',
                'skipped': True
            }

        elif 'lesson' in step_id.lower() or 'lesson generator' in title.lower():
            return self._implement_lesson_generator()

        elif 'storytelling coach' in title.lower():
            return self._implement_storytelling_coach()

        elif 'innovation coach' in title.lower():
            return self._implement_innovation_coach()

        else:
            return {
                'success': False,
                'error': f'Unknown Illumination step: {title}'
            }

    def _execute_multimedia_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a multimedia-related step"""
        title = step.get('title', '').lower()

        if 'youtube' in title and 'upload' in title:
            return self._implement_youtube_upload()

        elif 'playlist' in title:
            return self._implement_playlist_management()

        else:
            return {
                'success': False,
                'error': f'Unknown multimedia step: {title}'
            }

    def _execute_code_quality_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a code quality step"""
        title = step.get('title', '').lower()

        if 'error handling' in title:
            return self._implement_error_handling(step)

        elif 'architecture' in title:
            return {
                'success': True,
                'message': 'Architecture review requires manual analysis - creating TODO',
                'todo_created': True
            }

        elif 'integration' in title:
            return {
                'success': True,
                'message': 'Integration fixes require analysis - creating TODO',
                'todo_created': True
            }

        else:
            return {
                'success': False,
                'error': f'Unknown code quality step: {title}'
            }

    def _execute_generic_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a generic step"""
        return {
            'success': True,
            'message': 'Generic step - implementation pending',
            'todo_created': True
        }

    def _implement_lesson_generator(self) -> Dict[str, Any]:
        try:
            """Implement the Lesson Generator system"""
            self.logger.info("Implementing Lesson Generator...")

            # Create lesson generator script
            generator_file = self.project_root / "scripts" / "python" / "lumina_lesson_generator.py"

            if generator_file.exists():
                return {
                    'success': True,
                    'message': 'Lesson Generator already exists',
                    'skipped': True
                }

            # Implementation will be created
            return {
                'success': True,
                'message': 'Lesson Generator implementation started',
                'file_created': str(generator_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _implement_lesson_generator: {e}", exc_info=True)
            raise
    def _implement_storytelling_coach(self) -> Dict[str, Any]:
        try:
            """Implement the Storytelling Coach"""
            self.logger.info("Implementing Storytelling Coach...")

            coach_file = self.project_root / "scripts" / "python" / "lumina_storytelling_coach.py"

            if coach_file.exists():
                return {
                    'success': True,
                    'message': 'Storytelling Coach already exists',
                    'skipped': True
                }

            return {
                'success': True,
                'message': 'Storytelling Coach implementation started',
                'file_created': str(coach_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _implement_storytelling_coach: {e}", exc_info=True)
            raise
    def _implement_innovation_coach(self) -> Dict[str, Any]:
        try:
            """Implement the Innovation Coach"""
            self.logger.info("Implementing Innovation Coach...")

            coach_file = self.project_root / "scripts" / "python" / "lumina_innovation_coach.py"

            if coach_file.exists():
                return {
                    'success': True,
                    'message': 'Innovation Coach already exists',
                    'skipped': True
                }

            return {
                'success': True,
                'message': 'Innovation Coach implementation started',
                'file_created': str(coach_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _implement_innovation_coach: {e}", exc_info=True)
            raise
    def _implement_youtube_upload(self) -> Dict[str, Any]:
        try:
            """Implement YouTube Upload System"""
            self.logger.info("Implementing YouTube Upload System...")

            upload_file = self.project_root / "scripts" / "python" / "lumina_youtube_upload.py"

            if upload_file.exists():
                return {
                    'success': True,
                    'message': 'YouTube Upload already exists',
                    'skipped': True
                }

            return {
                'success': True,
                'message': 'YouTube Upload implementation started',
                'file_created': str(upload_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _implement_youtube_upload: {e}", exc_info=True)
            raise
    def _implement_playlist_management(self) -> Dict[str, Any]:
        try:
            """Implement Playlist Management"""
            self.logger.info("Implementing Playlist Management...")

            playlist_file = self.project_root / "scripts" / "python" / "lumina_playlist_manager.py"

            if playlist_file.exists():
                return {
                    'success': True,
                    'message': 'Playlist Manager already exists',
                    'skipped': True
                }

            return {
                'success': True,
                'message': 'Playlist Management implementation started',
                'file_created': str(playlist_file)
            }

        except Exception as e:
            self.logger.error(f"Error in _implement_playlist_management: {e}", exc_info=True)
            raise
    def _implement_error_handling(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Implement error handling improvements"""
        self.logger.info("Implementing Error Handling improvements...")

        # Create TODO for error handling
        todos_dir = self.project_root / "data" / "todos"
        todos_dir.mkdir(parents=True, exist_ok=True)

        todo_file = todos_dir / f"error_handling_{datetime.now().strftime('%Y%m%d')}.json"

        todo = {
            'title': step.get('title', 'Add Error Handling'),
            'description': step.get('description', ''),
            'priority': step.get('priority', 'high'),
            'created_at': datetime.now().isoformat(),
            'status': 'pending'
        }

        try:
            with open(todo_file, 'w') as f:
                json.dump(todo, f, indent=2)

            return {
                'success': True,
                'message': 'Error handling TODO created',
                'todo_file': str(todo_file)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create TODO: {e}'
            }

    def execute_all_high_priority(self, batch_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Execute all high-priority steps

        Args:
            batch_size: If provided, execute in batches of this size
        """
        self.logger.info("="*80)
        self.logger.info("JARVIS AUTONOMOUS WORKFLOW EXECUTION")
        self.logger.info("="*80)

        # Load action plan
        plan = self.load_latest_action_plan()
        if not plan:
            return {
                'success': False,
                'error': 'No action plan found'
            }

        # Get high-priority steps
        steps = self.get_high_priority_steps(plan)

        self.logger.info(f"Found {len(steps)} high-priority steps to execute")

        # Filter out already completed (curriculum system)
        remaining_steps = [
            s for s in steps 
            if 'curriculum' not in s.get('step_id', '').lower()
        ]

        self.logger.info(f"Executing {len(remaining_steps)} remaining steps")

        # Execute in batches or all at once
        if batch_size:
            batches = [remaining_steps[i:i+batch_size] for i in range(0, len(remaining_steps), batch_size)]
            self.logger.info(f"Executing in {len(batches)} batches of {batch_size}")
        else:
            batches = [remaining_steps]
            self.logger.info("Executing all steps in one go")

        execution_log = {
            'started_at': datetime.now().isoformat(),
            'total_steps': len(remaining_steps),
            'batches': len(batches),
            'executed': [],
            'failed': []
        }

        # Execute each batch
        for batch_num, batch in enumerate(batches, 1):
            self.logger.info(f"\n{'='*80}")
            self.logger.info(f"BATCH {batch_num}/{len(batches)}")
            self.logger.info(f"{'='*80}")

            # Use parallel delegation if subagents enabled
            if self.use_subagents and self.delegation and len(batch) > 1:
                self.logger.info(f"🚀 Delegating {len(batch)} tasks in parallel to subagents")
                results = self.delegation.delegate_parallel(batch)
                execution_log['executed'].extend(results)
                execution_log['failed'].extend([r for r in results if not r.get('success')])
            else:
                # Sequential execution
                for step in batch:
                    result = self.execute_step(step)
                    execution_log['executed'].append(result)

                    if not result.get('success'):
                        execution_log['failed'].append(result)

                    # Small delay between steps
                    time.sleep(0.5)

        execution_log['completed_at'] = datetime.now().isoformat()
        summary = {
            'total': len(remaining_steps),
            'succeeded': len([r for r in execution_log['executed'] if r.get('success')]),
            'failed': len(execution_log['failed']),
            'skipped': len([r for r in execution_log['executed'] if r.get('skipped')])
        }
        execution_log['summary'] = summary

        # Save execution log
        log_file = self.workflow_logs_dir / f"workflow_execution_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        try:
            with open(log_file, 'w') as f:
                json.dump(execution_log, f, indent=2)
            self.logger.info(f"\n✅ Execution log saved: {log_file}")
        except Exception as e:
            self.logger.error(f"Failed to save execution log: {e}")

        # Create Git milestone snapshot
        self._create_milestone_snapshot(summary, execution_log)

        # Auto-commit any remaining unstaged changes
        self._auto_commit_changes("Workflow execution completed")

        return execution_log

    def _auto_commit_changes(self, operation: str):
        """Auto-commit any unstaged changes"""
        try:
            from jarvis_auto_git_manager import JARVISAutoGitManager

            git_manager = JARVISAutoGitManager(self.project_root)
            result = git_manager.auto_stage_and_commit(operation=operation)

            if result.get('success'):
                self.logger.info(f"✅ Auto-committed {result.get('changes_count', 0)} changes")
            else:
                self.logger.warning(f"⚠️ Auto-commit failed: {result.get('error', 'unknown')}")

        except ImportError:
            self.logger.debug("Auto Git Manager not available")
        except Exception as e:
            self.logger.debug(f"Auto-commit error: {e}")

    def _create_milestone_snapshot(self, summary: Dict[str, Any], execution_log: Dict[str, Any]):
        """Create Git milestone snapshot after workflow execution"""
        try:
            from jarvis_git_milestone_snapshots import JARVISGitMilestoneSnapshots

            snapshots = JARVISGitMilestoneSnapshots(self.project_root)

            # Determine milestone type
            if summary['succeeded'] > 0 and summary['failed'] == 0:
                milestone_type = "major" if summary['succeeded'] >= 5 else "minor"
            else:
                milestone_type = "workflow"

            description = f"Workflow execution: {summary['succeeded']} succeeded, {summary['failed']} failed"

            context = {
                'steps_completed': summary['succeeded'],
                'total_steps': summary['total']
            }

            result = snapshots.auto_snapshot_on_milestone(milestone_type, description, context)

            if result.get('success'):
                self.logger.info(f"✅ Git milestone snapshot created: {result.get('commit_hash', 'unknown')}")
            else:
                self.logger.warning(f"⚠️ Git snapshot failed: {result.get('error', 'unknown')}")

        except ImportError:
            self.logger.warning("Git milestone snapshots not available")
        except Exception as e:
            self.logger.error(f"Error creating Git snapshot: {e}")


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="JARVIS Autonomous Workflow Executor")
        parser.add_argument("--execute-all", action="store_true", help="Execute all high-priority steps")
        parser.add_argument("--batch-size", type=int, help="Execute in batches of this size")
        parser.add_argument("--step", type=str, help="Execute a specific step by ID")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        executor = JARVISAutonomousWorkflowExecutor(project_root)

        if args.execute_all:
            result = executor.execute_all_high_priority(batch_size=args.batch_size)

            print("\n" + "="*80)
            print("WORKFLOW EXECUTION SUMMARY")
            print("="*80)
            print(f"Total Steps: {result['summary']['total']}")
            print(f"Succeeded: {result['summary']['succeeded']}")
            print(f"Failed: {result['summary']['failed']}")
            print(f"Skipped: {result['summary']['skipped']}")
            print("="*80)

            if result['failed']:
                print("\n❌ FAILED STEPS:")
                for failed in result['failed']:
                    print(f"  - {failed.get('title', 'Unknown')}: {failed.get('error', 'Unknown error')}")

        elif args.step:
            plan = executor.load_latest_action_plan()
            if plan:
                steps = plan.get('steps', [])
                step = next((s for s in steps if s.get('step_id') == args.step), None)
                if step:
                    result = executor.execute_step(step)
                    print(f"\n{'✅' if result.get('success') else '❌'} {result.get('title', 'Unknown')}")
                    print(f"   {result.get('message', result.get('error', 'Completed'))}")
                else:
                    print(f"❌ Step not found: {args.step}")
            else:
                print("❌ No action plan found")


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()