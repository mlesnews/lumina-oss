#!/usr/bin/env python3
"""
JARVIS Model and Space Issue Resolver
Resolves invalid model issues and space/storage problems.

Tags: #FIX #MODELS #STORAGE #CLEANUP @AUTO
"""

import sys
import json
import subprocess
import shutil
import os
from pathlib import Path
from typing import Dict, Any, List, Optional
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

logger = get_logger("JARVISModelSpaceFix")


class ModelAndSpaceResolver:
    """Resolve invalid model issues and space problems"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.logger = logger
        self.invalid_models_found: List[Dict[str, Any]] = []
        self.space_issues: Dict[str, Any] = {}

        # Known invalid model names (system names used as model names - INVALID)
        # Note: "iron legion" is a SYSTEM NAME, not a model name
        # Only flag when used as a MODEL NAME (in model fields)
        self.invalid_model_names = [
            "iron legion",      # System name, not model
            "iron_legion",      # System name, not model
            "iron-legion",      # System name, not model
            "llama2",           # Should be llama3 or specific version
            "llama-2",          # Should be llama3 or specific version
            "llama_2"           # Should be llama3 or specific version
        ]

        # Valid model replacements
        self.model_replacements = {
            "iron legion": "llama3.2:3b",
            "iron_legion": "llama3.2:3b",
            "iron-legion": "llama3.2:3b",
            "llama2": "llama3.2:3b",
            "llama-2": "llama3.2:3b",
            "llama_2": "llama3.2:3b"
        }

        self.logger.info("✅ Model and Space Resolver initialized")

    def check_disk_space(self) -> Dict[str, Any]:
        """Check disk space on all drives"""
        self.logger.info("="*80)
        self.logger.info("CHECKING DISK SPACE")
        self.logger.info("="*80)

        space_info = {
            "drives": [],
            "total_space_gb": 0,
            "total_free_gb": 0,
            "total_used_gb": 0,
            "low_space_drives": [],
            "critical_space_drives": []
        }

        try:
            # Windows disk space check
            result = subprocess.run(
                ["powershell", "-Command", 
                 "Get-PSDrive -PSProvider FileSystem | Select-Object Name, @{Name='Used(GB)';Expression={[math]::Round($_.Used/1GB,2)}}, @{Name='Free(GB)';Expression={[math]::Round($_.FreeSpace/1GB,2)}}, @{Name='Total(GB)';Expression={[math]::Round(($_.Used+$_.FreeSpace)/1GB,2)}} | ConvertTo-Json"],
                capture_output=True,
                text=True,
                timeout=10
            )

            if result.returncode == 0:
                drives_data = json.loads(result.stdout.strip())
                if not isinstance(drives_data, list):
                    drives_data = [drives_data]

                for drive in drives_data:
                    drive_name = drive.get("Name", "Unknown")
                    used_gb = drive.get("Used(GB)", 0)
                    free_gb = drive.get("Free(GB)", 0)
                    total_gb = drive.get("Total(GB)", 0)
                    used_percent = (used_gb / total_gb * 100) if total_gb > 0 else 0

                    drive_info = {
                        "drive": drive_name,
                        "used_gb": round(used_gb, 2),
                        "free_gb": round(free_gb, 2),
                        "total_gb": round(total_gb, 2),
                        "used_percent": round(used_percent, 2),
                        "status": "ok"
                    }

                    # Check for low space (< 10GB free or > 90% used)
                    if free_gb < 10 or used_percent > 90:
                        drive_info["status"] = "critical"
                        space_info["critical_space_drives"].append(drive_info)
                        self.logger.warning(f"   🔴 {drive_name}: CRITICAL - {free_gb:.2f}GB free ({used_percent:.1f}% used)")
                    elif free_gb < 20 or used_percent > 80:
                        drive_info["status"] = "low"
                        space_info["low_space_drives"].append(drive_info)
                        self.logger.warning(f"   ⚠️  {drive_name}: LOW - {free_gb:.2f}GB free ({used_percent:.1f}% used)")
                    else:
                        self.logger.info(f"   ✅ {drive_name}: OK - {free_gb:.2f}GB free ({used_percent:.1f}% used)")

                    space_info["drives"].append(drive_info)
                    space_info["total_space_gb"] += total_gb
                    space_info["total_free_gb"] += free_gb
                    space_info["total_used_gb"] += used_gb
        except Exception as e:
            self.logger.error(f"   ❌ Failed to check disk space: {e}")
            space_info["error"] = str(e)

        self.space_issues = space_info
        return space_info

    def find_invalid_models(self) -> List[Dict[str, Any]]:
        """Find all invalid model references in the codebase

        Only flags when invalid names are used as MODEL NAMES, not system/config names.
        """
        self.logger.info("="*80)
        self.logger.info("FINDING INVALID MODEL REFERENCES")
        self.logger.info("="*80)

        import re
        invalid_refs = []
        scripts_dir = self.project_root / "scripts" / "python"
        config_dir = self.project_root / "config"

        # Patterns that indicate invalid model usage (in model fields)
        model_field_patterns = [
            (r'["\']model["\']\s*:\s*["\'](iron\s+legion|iron_legion|iron-legion)["\']', "iron legion"),
            (r'["\']model["\']\s*:\s*["\'](llama2|llama-2|llama_2)["\']', "llama2"),
            (r'model\s*=\s*["\'](iron\s+legion|iron_legion|iron-legion)["\']', "iron legion"),
            (r'model\s*=\s*["\'](llama2|llama-2|llama_2)["\']', "llama2"),
        ]

        # Search in Python files
        for py_file in scripts_dir.rglob("*.py"):
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')

                    for line_num, line in enumerate(lines, 1):
                        for pattern, invalid_model in model_field_patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                invalid_refs.append({
                                    "file": str(py_file.relative_to(self.project_root)),
                                    "line": line_num,
                                    "invalid_model": invalid_model,
                                    "line_content": line.strip()[:100],
                                    "replacement": self.model_replacements.get(invalid_model, "llama3.2:3b")
                                })
            except Exception as e:
                self.logger.debug(f"   Error reading {py_file}: {e}")

        # Search in config files (JSON)
        for config_file in config_dir.rglob("*.json"):
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Check for model fields with invalid values
                    for pattern, invalid_model in model_field_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            invalid_refs.append({
                                "file": str(config_file.relative_to(self.project_root)),
                                "line": 0,
                                "invalid_model": invalid_model,
                                "line_content": "JSON config file - model field",
                                "replacement": self.model_replacements.get(invalid_model, "llama3.2:3b")
                            })
            except Exception as e:
                self.logger.debug(f"   Error reading {config_file}: {e}")

        self.invalid_models_found = invalid_refs

        if invalid_refs:
            self.logger.warning(f"   ⚠️  Found {len(invalid_refs)} invalid model references")
            # Group by file
            files_with_issues = {}
            for ref in invalid_refs:
                file = ref["file"]
                if file not in files_with_issues:
                    files_with_issues[file] = []
                files_with_issues[file].append(ref)

            for file, refs in files_with_issues.items():
                self.logger.warning(f"      {file}: {len(refs)} issues")
        else:
            self.logger.info("   ✅ No invalid model references found")

        return invalid_refs

    def fix_invalid_models(self, dry_run: bool = False) -> Dict[str, Any]:
        """Fix invalid model references"""
        self.logger.info("="*80)
        self.logger.info("FIXING INVALID MODEL REFERENCES")
        self.logger.info("="*80)

        if not self.invalid_models_found:
            self.logger.info("   ✅ No invalid models to fix")
            return {"fixed": 0, "files_modified": 0}

        fixed_count = 0
        files_modified = set()

        # Group by file
        files_to_fix = {}
        for ref in self.invalid_models_found:
            file_path = self.project_root / ref["file"]
            if file_path not in files_to_fix:
                files_to_fix[file_path] = []
            files_to_fix[file_path].append(ref)

        for file_path, refs in files_to_fix.items():
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    original_content = content

                # Fix each invalid model reference
                for ref in refs:
                    invalid_model = ref["invalid_model"]
                    replacement = ref["replacement"]

                    # Replace in content (case-insensitive)
                    import re
                    # Replace quoted strings
                    content = re.sub(
                        rf'["\']{re.escape(invalid_model)}["\']',
                        f'"{replacement}"',
                        content,
                        flags=re.IGNORECASE
                    )
                    # Replace in variable assignments
                    content = re.sub(
                        rf'=\s*["\']?{re.escape(invalid_model)}["\']?',
                        f'="{replacement}"',
                        content,
                        flags=re.IGNORECASE
                    )

                if content != original_content:
                    if not dry_run:
                        with open(file_path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        self.logger.info(f"   ✅ Fixed {file_path.name}: {len(refs)} references")
                    else:
                        self.logger.info(f"   [DRY RUN] Would fix {file_path.name}: {len(refs)} references")
                    fixed_count += len(refs)
                    files_modified.add(str(file_path))
            except Exception as e:
                self.logger.error(f"   ❌ Failed to fix {file_path}: {e}")

        return {
            "fixed": fixed_count,
            "files_modified": len(files_modified),
            "dry_run": dry_run
        }

    def cleanup_space(self) -> Dict[str, Any]:
        """Clean up space using Docker cleanup and other methods"""
        self.logger.info("="*80)
        self.logger.info("CLEANING UP SPACE")
        self.logger.info("="*80)

        cleanup_results = {
            "docker_cleanup": {},
            "python_cache": {},
            "temp_files": {},
            "total_freed_gb": 0
        }

        # 1. Docker cleanup
        self.logger.info("1. Running Docker cleanup...")
        try:
            from jarvis_docker_cleanup import DockerCleanup
            cleanup = DockerCleanup(self.project_root)
            docker_result = cleanup.run_cleanup()
            cleanup_results["docker_cleanup"] = docker_result

            # Calculate total freed
            ultron_freed = docker_result.get("ultron_cleanup", {}).get("freed_space_gb", 0)
            kaiju_freed = docker_result.get("kaiju_cleanup", {}).get("freed_space_gb", 0)
            cleanup_results["total_freed_gb"] += ultron_freed + kaiju_freed

            self.logger.info(f"   ✅ Docker cleanup complete - Freed: {ultron_freed + kaiju_freed:.2f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Docker cleanup failed: {e}")
            # Fallback to direct commands
            self.logger.info("   Trying direct Docker cleanup...")
            docker_result = self._run_docker_cleanup_direct()
            cleanup_results["docker_cleanup"] = docker_result
            cleanup_results["total_freed_gb"] += docker_result.get("freed_space_gb", 0)

        # 2. Python cache cleanup
        self.logger.info("2. Cleaning Python cache...")
        try:
            cache_dirs = [
                self.project_root / "__pycache__",
                self.project_root / "scripts" / "python" / "__pycache__"
            ]

            cache_freed = 0
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for pycache in cache_dir.rglob("*.pyc"):
                        size = pycache.stat().st_size
                        pycache.unlink()
                        cache_freed += size
                    # Remove empty __pycache__ dirs
                    for pycache_dir in cache_dir.rglob("__pycache__"):
                        try:
                            if not any(pycache_dir.iterdir()):
                                pycache_dir.rmdir()
                        except:
                            pass

            cache_freed_gb = cache_freed / (1024**3)
            cleanup_results["python_cache"] = {"freed_gb": cache_freed_gb}
            cleanup_results["total_freed_gb"] += cache_freed_gb
            self.logger.info(f"   ✅ Python cache cleanup - Freed: {cache_freed_gb:.3f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Python cache cleanup failed: {e}")

        # 3. Temp files cleanup
        self.logger.info("3. Cleaning temp files...")
        try:
            temp_dirs = [
                self.project_root / "data" / "temp",
                self.project_root / "data" / "cache"
            ]

            temp_freed = 0
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    for temp_file in temp_dir.rglob("*"):
                        if temp_file.is_file():
                            try:
                                size = temp_file.stat().st_size
                                # Only delete files older than 7 days
                                age_days = (datetime.now().timestamp() - temp_file.stat().st_mtime) / (24*3600)
                                if age_days > 7:
                                    temp_file.unlink()
                                    temp_freed += size
                            except:
                                pass

            temp_freed_gb = temp_freed / (1024**3)
            cleanup_results["temp_files"] = {"freed_gb": temp_freed_gb}
            cleanup_results["total_freed_gb"] += temp_freed_gb
            self.logger.info(f"   ✅ Temp files cleanup - Freed: {temp_freed_gb:.3f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Temp files cleanup failed: {e}")

        return cleanup_results

    def _run_docker_cleanup_direct(self) -> Dict[str, Any]:
        """Run Docker cleanup directly using subprocess"""
        freed_gb = 0.0

        try:
            # Docker system prune
            result = subprocess.run(
                ["docker", "system", "prune", "-a", "--volumes", "-f"],
                capture_output=True,
                text=True,
                timeout=300
            )

            if result.returncode == 0:
                # Parse output for freed space
                output = result.stdout
                if "Total reclaimed space:" in output:
                    space_str = output.split("Total reclaimed space:")[1].strip().split('\n')[0].strip()
                    freed_gb = self._parse_docker_space(space_str)
                    self.logger.info(f"   ✅ Direct Docker cleanup - Freed: {freed_gb:.2f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Direct Docker cleanup failed: {e}")

        return {"freed_space_gb": freed_gb, "method": "direct"}

    def _parse_docker_space(self, space_str: str) -> float:
        """Parse Docker space string (e.g., '1.23GB') into GB"""
        space_str = space_str.strip().upper()
        if "GB" in space_str:
            return float(space_str.replace("GB", ""))
        elif "MB" in space_str:
            return float(space_str.replace("MB", "")) / 1024
        elif "KB" in space_str:
            return float(space_str.replace("KB", "")) / (1024**2)
        return 0.0

    def aggressive_space_cleanup(self) -> Dict[str, Any]:
        """Aggressive space cleanup for critical situations"""
        self.logger.info("="*80)
        self.logger.info("AGGRESSIVE SPACE CLEANUP - CRITICAL SITUATION")
        self.logger.info("="*80)

        cleanup_results = {
            "docker_cleanup": {},
            "python_cache": {},
            "temp_files": {},
            "node_modules": {},
            "build_artifacts": {},
            "log_files": {},
            "total_freed_gb": 0
        }

        # 1. Docker aggressive cleanup
        self.logger.info("1. Aggressive Docker cleanup...")
        try:
            docker_result = self._run_docker_cleanup_direct()
            cleanup_results["docker_cleanup"] = docker_result
            cleanup_results["total_freed_gb"] += docker_result.get("freed_space_gb", 0)
        except Exception as e:
            self.logger.warning(f"   ⚠️  Docker cleanup failed: {e}")

        # 2. Python cache (all, not just old)
        self.logger.info("2. Aggressive Python cache cleanup...")
        try:
            cache_dirs = [
                self.project_root / "__pycache__",
                self.project_root / "scripts" / "python" / "__pycache__"
            ]

            cache_freed = 0
            for cache_dir in cache_dirs:
                if cache_dir.exists():
                    for pycache in cache_dir.rglob("*.pyc"):
                        try:
                            size = pycache.stat().st_size
                            pycache.unlink()
                            cache_freed += size
                        except:
                            pass
                    # Remove all __pycache__ dirs
                    for pycache_dir in cache_dir.rglob("__pycache__"):
                        try:
                            shutil.rmtree(pycache_dir)
                        except:
                            pass

            cache_freed_gb = cache_freed / (1024**3)
            cleanup_results["python_cache"] = {"freed_gb": cache_freed_gb}
            cleanup_results["total_freed_gb"] += cache_freed_gb
            self.logger.info(f"   ✅ Python cache cleanup - Freed: {cache_freed_gb:.3f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Python cache cleanup failed: {e}")

        # 3. Temp files (all, not just 7 days old)
        self.logger.info("3. Aggressive temp files cleanup...")
        try:
            username = os.getenv("USERNAME", "mlesn")
            temp_dirs = [
                self.project_root / "data" / "temp",
                self.project_root / "data" / "cache",
                Path(f"C:/Windows/Temp"),
                Path(f"C:/Users/{username}/AppData/Local/Temp")
            ]

            temp_freed = 0
            files_deleted = 0
            for temp_dir in temp_dirs:
                if temp_dir.exists():
                    try:
                        for temp_file in temp_dir.rglob("*"):
                            if temp_file.is_file():
                                try:
                                    size = temp_file.stat().st_size
                                    # Only delete files older than 1 day for system temp dirs
                                    if "Windows" in str(temp_dir) or "AppData" in str(temp_dir):
                                        age_days = (datetime.now().timestamp() - temp_file.stat().st_mtime) / (24*3600)
                                        if age_days > 1:
                                            temp_file.unlink()
                                            temp_freed += size
                                            files_deleted += 1
                                    else:
                                        # Project temp dirs - delete all
                                        temp_file.unlink()
                                        temp_freed += size
                                        files_deleted += 1
                                except Exception as e:
                                    self.logger.debug(f"   Could not delete {temp_file}: {e}")
                    except Exception as e:
                        self.logger.debug(f"   Error accessing {temp_dir}: {e}")

            temp_freed_gb = temp_freed / (1024**3)
            cleanup_results["temp_files"] = {"freed_gb": temp_freed_gb, "files_deleted": files_deleted}
            cleanup_results["total_freed_gb"] += temp_freed_gb
            self.logger.info(f"   ✅ Temp files cleanup - Freed: {temp_freed_gb:.3f}GB ({files_deleted} files)")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Temp files cleanup failed: {e}")

        # 4. Log files cleanup
        self.logger.info("4. Cleaning old log files...")
        try:
            import os
            log_dirs = [
                self.project_root / "data" / "logs",
                self.project_root / "logs"
            ]

            log_freed = 0
            for log_dir in log_dirs:
                if log_dir.exists():
                    for log_file in log_dir.rglob("*.log"):
                        try:
                            # Delete logs older than 1 day
                            age_days = (datetime.now().timestamp() - log_file.stat().st_mtime) / (24*3600)
                            if age_days > 1:
                                size = log_file.stat().st_size
                                log_file.unlink()
                                log_freed += size
                        except:
                            pass

            log_freed_gb = log_freed / (1024**3)
            cleanup_results["log_files"] = {"freed_gb": log_freed_gb}
            cleanup_results["total_freed_gb"] += log_freed_gb
            self.logger.info(f"   ✅ Log files cleanup - Freed: {log_freed_gb:.3f}GB")
        except Exception as e:
            self.logger.warning(f"   ⚠️  Log files cleanup failed: {e}")

        return cleanup_results

    def resolve_all_issues(self, dry_run: bool = False) -> Dict[str, Any]:
        """Resolve all model and space issues"""
        self.logger.info("="*80)
        self.logger.info("RESOLVING MODEL AND SPACE ISSUES")
        self.logger.info("="*80)

        results = {
            "timestamp": datetime.now().isoformat(),
            "dry_run": dry_run,
            "disk_space": {},
            "invalid_models": {},
            "space_cleanup": {},
            "summary": {}
        }

        # 1. Check disk space
        results["disk_space"] = self.check_disk_space()

        # 2. Find invalid models
        invalid_models = self.find_invalid_models()
        results["invalid_models"]["found"] = len(invalid_models)
        results["invalid_models"]["references"] = invalid_models

        # 3. Fix invalid models
        if invalid_models:
            fix_result = self.fix_invalid_models(dry_run=dry_run)
            results["invalid_models"]["fixed"] = fix_result

        # 4. Clean up space (aggressive if critical)
        if results["disk_space"].get("critical_space_drives"):
            self.logger.warning("   🔴 CRITICAL: Drive(s) at 100% - Running aggressive cleanup")
            results["space_cleanup"] = self.aggressive_space_cleanup()
        elif results["disk_space"].get("low_space_drives"):
            results["space_cleanup"] = self.cleanup_space()

        # Summary
        results["summary"] = {
            "invalid_models_found": len(invalid_models),
            "invalid_models_fixed": results["invalid_models"].get("fixed", {}).get("fixed", 0),
            "space_freed_gb": results["space_cleanup"].get("total_freed_gb", 0),
            "low_space_drives": len(results["disk_space"].get("low_space_drives", [])),
            "critical_space_drives": len(results["disk_space"].get("critical_space_drives", []))
        }

        # Print summary
        self.logger.info("\n" + "="*80)
        self.logger.info("RESOLUTION SUMMARY")
        self.logger.info("="*80)
        self.logger.info(f"Invalid Models Found: {results['summary']['invalid_models_found']}")
        self.logger.info(f"Invalid Models Fixed: {results['summary']['invalid_models_fixed']}")
        self.logger.info(f"Space Freed: {results['summary']['space_freed_gb']:.2f}GB")
        self.logger.info(f"Low Space Drives: {results['summary']['low_space_drives']}")
        self.logger.info(f"Critical Space Drives: {results['summary']['critical_space_drives']}")
        self.logger.info("="*80)

        return results


def main():
    try:
        """CLI interface"""
        import argparse

        parser = argparse.ArgumentParser(description="Resolve Model and Space Issues")
        parser.add_argument("--dry-run", action="store_true", help="Dry run - don't make changes")
        parser.add_argument("--check-space", action="store_true", help="Only check disk space")
        parser.add_argument("--check-models", action="store_true", help="Only check invalid models")
        parser.add_argument("--fix-models", action="store_true", help="Fix invalid models")
        parser.add_argument("--cleanup", action="store_true", help="Clean up space")

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        resolver = ModelAndSpaceResolver(project_root)

        if args.check_space:
            result = resolver.check_disk_space()
            print(json.dumps(result, indent=2, default=str))
        elif args.check_models:
            result = resolver.find_invalid_models()
            print(json.dumps(result, indent=2, default=str))
        elif args.fix_models:
            resolver.find_invalid_models()
            result = resolver.fix_invalid_models(dry_run=args.dry_run)
            print(json.dumps(result, indent=2, default=str))
        elif args.cleanup:
            result = resolver.cleanup_space()
            print(json.dumps(result, indent=2, default=str))
        else:
            # Full resolution
            result = resolver.resolve_all_issues(dry_run=args.dry_run)
            print(json.dumps(result, indent=2, default=str))


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()