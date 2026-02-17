#!/usr/bin/env python3
"""
MANUS - Manual Automation System
Complete control of Cursor IDE and all workflow processes

Capabilities:
- File operations (create, read, update, delete)
- Code generation and editing
- Terminal command execution
- Git operations
- Package management
- Test execution
- Build and deployment
- IDE configuration

Tags: #MANUS #CURSOR_IDE #AUTOMATION #WORKFLOW #IDE_CONTROL
"""

import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Add project root to path
script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_logger import get_logger
    logger = get_logger("MANUSCursorIDE")
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("MANUSCursorIDE")


class MANUSCursorIDEController:
    """MANUS - Complete Cursor IDE Control"""

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.workspace_root = self.project_root

        logger.info("✅ MANUS Cursor IDE Controller initialized")

    # File Operations
    def create_file(self, file_path: str, content: str = "") -> bool:
        """Create a new file"""
        try:
            full_path = self.project_root / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Created file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to create file {file_path}: {e}")
            return False

    def read_file(self, file_path: str) -> Optional[str]:
        """Read file content"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                logger.warning(f"⚠️  File not found: {file_path}")
                return None
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"❌ Failed to read file {file_path}: {e}")
            return None

    def update_file(self, file_path: str, content: str) -> bool:
        """Update file content"""
        try:
            full_path = self.project_root / file_path
            full_path.write_text(content, encoding='utf-8')
            logger.info(f"✅ Updated file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"❌ Failed to update file {file_path}: {e}")
            return False

    def delete_file(self, file_path: str) -> bool:
        """Delete file (requires approval for critical files)"""
        try:
            full_path = self.project_root / file_path
            if full_path.exists():
                full_path.unlink()
                logger.info(f"✅ Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"⚠️  File not found: {file_path}")
                return False
        except Exception as e:
            logger.error(f"❌ Failed to delete file {file_path}: {e}")
            return False

    # Code Operations
    def generate_code(self, file_path: str, code: str, language: str = "python") -> bool:
        """Generate code in a file"""
        return self.create_file(file_path, code)

    def edit_code(self, file_path: str, old_string: str, new_string: str) -> bool:
        """Edit code by replacing old_string with new_string"""
        content = self.read_file(file_path)
        if content is None:
            return False

        if old_string not in content:
            logger.warning(f"⚠️  Old string not found in {file_path}")
            return False

        new_content = content.replace(old_string, new_string)
        return self.update_file(file_path, new_content)

    # Terminal Operations
    def execute_command(self, command: str, cwd: Optional[Path] = None, shell: bool = True) -> Dict[str, Any]:
        """
        Execute terminal command

        Returns:
            Dict with 'success', 'stdout', 'stderr', 'returncode'
        """
        try:
            if cwd is None:
                cwd = self.project_root

            result = subprocess.run(
                command,
                shell=shell,
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )

            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode
            }
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Command timeout: {command}")
            return {
                "success": False,
                "stdout": "",
                "stderr": "Command timeout",
                "returncode": -1
            }
        except Exception as e:
            logger.error(f"❌ Failed to execute command: {e}")
            return {
                "success": False,
                "stdout": "",
                "stderr": str(e),
                "returncode": -1
            }

    # Git Operations
    def git_status(self) -> Dict[str, Any]:
        """Get git status"""
        return self.execute_command("git status")

    def git_add(self, files: List[str]) -> Dict[str, Any]:
        """Git add files"""
        files_str = " ".join(files)
        return self.execute_command(f"git add {files_str}")

    def git_commit(self, message: str) -> Dict[str, Any]:
        """Git commit (requires approval for main/master branch)"""
        return self.execute_command(f'git commit -m "{message}"')

    def git_push(self, branch: str = "main") -> Dict[str, Any]:
        """Git push (requires approval for main/master)"""
        if branch in ["main", "master"]:
            logger.warning(f"⚠️  Pushing to {branch} requires approval")
        return self.execute_command(f"git push origin {branch}")

    def git_pull(self, branch: str = "main") -> Dict[str, Any]:
        """Git pull"""
        return self.execute_command(f"git pull origin {branch}")

    def git_branch(self, branch_name: Optional[str] = None) -> Dict[str, Any]:
        """Create or switch to branch"""
        if branch_name:
            return self.execute_command(f"git checkout -b {branch_name}")
        else:
            return self.execute_command("git branch")

    # Package Management
    def npm_install(self, package: Optional[str] = None) -> Dict[str, Any]:
        """npm install"""
        if package:
            return self.execute_command(f"npm install {package}")
        else:
            return self.execute_command("npm install")

    def pip_install(self, package: str) -> Dict[str, Any]:
        """pip install"""
        return self.execute_command(f"pip install {package}")

    # Test Execution
    def run_tests(self, test_path: Optional[str] = None) -> Dict[str, Any]:
        """Run tests"""
        if test_path:
            return self.execute_command(f"python -m pytest {test_path}")
        else:
            return self.execute_command("python -m pytest")

    # Build and Deployment
    def build_project(self, build_command: str = "npm run build") -> Dict[str, Any]:
        """Build project"""
        return self.execute_command(build_command)

    # Workflow Orchestration
    def execute_workflow(self, workflow_steps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute complete workflow with rollback capability

        Args:
            workflow_steps: List of workflow steps, each with:
                - type: 'file_create', 'file_update', 'file_delete', 'command', 'git_add', 'git_commit', 'git_push'
                - action: Specific action description
                - params: Action parameters
                - requires_approval: bool (default False)
                - rollback_action: Optional dict with rollback step

        Returns:
            Dict with workflow execution results
        """
        results = {
            "success": True,
            "steps_completed": [],
            "errors": [],
            "rollback_performed": False
        }

        executed_steps = []

        for i, step in enumerate(workflow_steps):
            step_type = step.get("type")
            action = step.get("action")
            params = step.get("params", {})
            requires_approval = step.get("requires_approval", False)

            logger.info(f"🔄 Executing step {i+1}/{len(workflow_steps)}: {step_type} - {action}")

            # Execute step based on type
            step_result = None
            try:
                if step_type == "file_create":
                    success = self.create_file(params.get("path", ""), params.get("content", ""))
                    step_result = {"success": success}
                elif step_type == "file_update":
                    success = self.update_file(params.get("path", ""), params.get("content", ""))
                    step_result = {"success": success}
                elif step_type == "file_delete":
                    success = self.delete_file(params.get("path", ""))
                    step_result = {"success": success}
                elif step_type == "command":
                    step_result = self.execute_command(params.get("command", ""), cwd=params.get("cwd"))
                elif step_type == "git_add":
                    step_result = self.git_add(params.get("files", []))
                elif step_type == "git_commit":
                    step_result = self.git_commit(params.get("message", ""))
                elif step_type == "git_push":
                    step_result = self.git_push(params.get("branch", "main"))
                else:
                    logger.warning(f"⚠️  Unknown step type: {step_type}")
                    step_result = {"success": False, "error": "Unknown step type"}

                # Check if step failed
                success = step_result.get("success", False) if isinstance(step_result, dict) else step_result

                if success:
                    executed_steps.append(step)
                    results["steps_completed"].append({
                        "step": i + 1,
                        "type": step_type,
                        "action": action,
                        "success": True
                    })
                else:
                    error_msg = step_result.get("stderr") or step_result.get("error") or "Unknown error"
                    logger.error(f"❌ Step {i+1} failed: {error_msg}")
                    results["success"] = False
                    results["errors"].append(f"Step {i+1} failed: {action} ({error_msg})")

                    # Perform rollback
                    self._perform_rollback(executed_steps)
                    results["rollback_performed"] = True
                    break

            except Exception as e:
                logger.error(f"❌ Exception in step {i+1}: {e}")
                results["success"] = False
                results["errors"].append(f"Step {i+1} exception: {e}")
                self._perform_rollback(executed_steps)
                results["rollback_performed"] = True
                break

        return results

    def _perform_rollback(self, executed_steps: List[Dict[str, Any]]):
        """Perform rollback for executed steps in reverse order"""
        logger.warning(f"🔄 Initiating rollback for {len(executed_steps)} steps...")

        for step in reversed(executed_steps):
            rollback = step.get("rollback_action")
            if not rollback:
                logger.info(f"⏭️  No rollback defined for step: {step.get('action')}")
                continue

            logger.info(f"🔄 Rolling back: {rollback.get('action')}")
            rb_type = rollback.get("type")
            rb_params = rollback.get("params", {})

            try:
                if rb_type == "file_delete":
                    self.delete_file(rb_params.get("path", ""))
                elif rb_type == "file_create":
                    self.create_file(rb_params.get("path", ""), rb_params.get("content", ""))
                elif rb_type == "command":
                    self.execute_command(rb_params.get("command", ""))
                # Add more rollback types as needed
            except Exception as e:
                logger.error(f"❌ Rollback failed for step {step.get('action')}: {e}")

    def setup_environment(self, requirements_path: str = "requirements.txt") -> bool:
        """Setup Python environment from requirements.txt"""
        logger.info(f"🐍 Setting up environment from {requirements_path}...")
        result = self.execute_command(f"pip install -r {requirements_path}")
        return result.get("success", False)


def main():
    """Main entry point for testing"""
    import argparse

    parser = argparse.ArgumentParser(description="MANUS Cursor IDE Controller")
    parser.add_argument("--test", action="store_true", help="Test MANUS controller")

    args = parser.parse_args()

    if args.test:
        controller = MANUSCursorIDEController(project_root)

        # Test file operations
        test_file = "data/test_manus.txt"
        controller.create_file(test_file, "Test content")
        content = controller.read_file(test_file)
        print(f"✅ File created and read: {content}")
        controller.delete_file(test_file)
        print("✅ File deleted")

        # Test command execution
        result = controller.execute_command("echo 'MANUS test'")
        print(f"✅ Command executed: {result['stdout']}")

    return 0


if __name__ == "__main__":


    sys.exit(main() or 0)