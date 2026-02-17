#!/usr/bin/env python3
"""
@MARVIN Dropbox Cleanup System

Intelligently sorts out 20 years of Dropbox mess:
- Nested Dropbox folders
- Duplicate folders
- "Dropbox_Flattened" folders
- Software licensing duplicates (10x!)
- Logical organization

@MARVIN provides the intelligence and reality checks.
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from dataclasses import dataclass, field
import json
import hashlib
import shutil
from universal_decision_tree import decide, DecisionContext, DecisionOutcome

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("MarvinDropboxCleanup")

try:
    from lumina_always_marvin_jarvis import always_assess
except ImportError:
    always_assess = None


@dataclass

# @SYPHON: Decision tree logic applied
# Use: result = decide('ai_fallback', DecisionContext(...))

class DuplicateFolder:
    """Duplicate folder information"""
    folder_id: str
    path: str
    size: int
    file_count: int
    hash: str
    duplicate_of: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""


@dataclass
class DropboxIssue:
    """Dropbox organization issue"""
    issue_id: str
    issue_type: str  # "nested_dropbox", "duplicate", "flattened", "orphaned"
    path: str
    severity: str  # "high", "medium", "low"
    description: str
    suggested_action: str
    confidence: float = 0.0


class MarvinDropboxCleanup:
    """
    @MARVIN's intelligent Dropbox cleanup system.

    "20 years of Dropbox mess? <SIGH> Fine. Let's sort this out properly."
    """

    def __init__(self, dropbox_root: Optional[Path] = None, project_root: Optional[Path] = None):
        self.project_root = project_root or Path(".").resolve()
        self.dropbox_root = dropbox_root or Path.home() / "Dropbox"

        self.logger = get_logger("MarvinDropboxCleanup")

        self.data_dir = self.project_root / "data" / "dropbox_cleanup"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Analysis results
        self.duplicate_folders: List[DuplicateFolder] = []
        self.nested_dropbox_folders: List[Path] = []
        self.flattened_folders: List[Path] = []
        self.issues: List[DropboxIssue] = []

        # File hashes for duplicate detection
        self.file_hashes: Dict[str, List[Path]] = {}

        self.logger.info("😟 @MARVIN Dropbox Cleanup initialized")
        self.logger.info(f"   Dropbox root: {self.dropbox_root}")

        # Get @MARVIN's assessment
        if always_assess:
            assessment = always_assess(
                "We have 20 years of Dropbox mess with nested folders, duplicates, "
                "and 'Dropbox_Flattened' folders. Software licensing is duplicated 10 times. "
                "How should we intelligently clean this up?"
            )
            if hasattr(assessment, 'marvin_perspective'):
                self.logger.info(f"   @MARVIN: {assessment.marvin_perspective[:200]}...")

    def analyze_dropbox(self) -> Dict[str, Any]:
        try:
            """Analyze Dropbox structure and find issues"""
            self.logger.info("🔍 @MARVIN analyzing Dropbox structure...")

            if not self.dropbox_root.exists():
                self.logger.error(f"❌ Dropbox root not found: {self.dropbox_root}")
                return {}

            # Find nested Dropbox folders
            self._find_nested_dropbox_folders()

            # Find "Dropbox_Flattened" folders
            self._find_flattened_folders()

            # Find duplicate folders
            self._find_duplicate_folders()

            # Find software licensing duplicates (special case)
            self._find_software_licensing_duplicates()

            # Generate issues
            self._generate_issues()

            analysis = {
                "timestamp": datetime.now().isoformat(),
                "dropbox_root": str(self.dropbox_root),
                "nested_dropbox_folders": len(self.nested_dropbox_folders),
                "flattened_folders": len(self.flattened_folders),
                "duplicate_folders": len(self.duplicate_folders),
                "total_issues": len(self.issues),
                "issues_by_severity": self._count_issues_by_severity()
            }

            # Save analysis
            analysis_file = self.data_dir / f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(analysis_file, 'w', encoding='utf-8') as f:
                json.dump({
                    **analysis,
                    "nested_folders": [str(p) for p in self.nested_dropbox_folders],
                    "flattened_folders": [str(p) for p in self.flattened_folders],
                    "duplicates": [self._duplicate_to_dict(d) for d in self.duplicate_folders],
                    "issues": [self._issue_to_dict(i) for i in self.issues]
                }, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Analysis saved: {analysis_file}")

            return analysis

        except Exception as e:
            self.logger.error(f"Error in analyze_dropbox: {e}", exc_info=True)
            raise
    def _find_nested_dropbox_folders(self):
        """Find nested Dropbox folders (Dropbox inside Dropbox)"""
        self.logger.info("   Finding nested Dropbox folders...")

        for item in self.dropbox_root.rglob("Dropbox"):
            if item.is_dir() and item != self.dropbox_root:
                # Check if it's actually a nested Dropbox folder
                if self._is_nested_dropbox(item):
                    self.nested_dropbox_folders.append(item)
                    self.logger.debug(f"   Found nested: {item}")

    def _is_nested_dropbox(self, folder: Path) -> bool:
        try:
            """Check if folder is a nested Dropbox folder"""
            # Look for Dropbox indicators
            indicators = [
                ".dropbox",
                ".dropbox.cache",
                "my_projects",
                "Repository"
            ]

            for indicator in indicators:
                if (folder / indicator).exists():
                    return True

            return False

        except Exception as e:
            self.logger.error(f"Error in _is_nested_dropbox: {e}", exc_info=True)
            raise
    def _find_flattened_folders(self):
        """Find 'Dropbox_Flattened' folders"""
        self.logger.info("   Finding 'Dropbox_Flattened' folders...")

        for item in self.dropbox_root.rglob("*Flattened*"):
            if item.is_dir() and "dropbox" in item.name.lower():
                self.flattened_folders.append(item)
                self.logger.debug(f"   Found flattened: {item}")

    def _find_duplicate_folders(self):
        """Find duplicate folders by content hash"""
        self.logger.info("   Finding duplicate folders...")

        # Focus on common duplicate patterns
        target_folders = [
            "Repository",
            "my_projects",
            "Documents",
            "Pictures",
            "Videos"
        ]

        folder_hashes: Dict[str, List[Path]] = {}

        for target in target_folders:
            for folder in self.dropbox_root.rglob(target):
                if folder.is_dir():
                    folder_hash = self._hash_folder(folder)
                    if folder_hash:
                        if folder_hash not in folder_hashes:
                            folder_hashes[folder_hash] = []
                        folder_hashes[folder_hash].append(folder)

        # Find duplicates
        for folder_hash, folders in folder_hashes.items():
            if len(folders) > 1:
                # Keep the shortest path as "original"
                folders.sort(key=lambda p: len(str(p)))
                original = folders[0]

                for duplicate in folders[1:]:
                    dup = DuplicateFolder(
                        folder_id=f"dup_{hashlib.md5(str(duplicate).encode()).hexdigest()[:8]}",
                        path=str(duplicate),
                        size=self._get_folder_size(duplicate),
                        file_count=self._count_files(duplicate),
                        hash=folder_hash,
                        duplicate_of=str(original),
                        confidence=0.9,  # High confidence if hash matches
                        reason="Content hash match"
                    )
                    self.duplicate_folders.append(dup)

    def _find_software_licensing_duplicates(self):
        """Special case: Find software licensing duplicates (user said 10x!)"""
        self.logger.info("   Finding software licensing duplicates...")

        # Look for Repository folders
        repository_folders = list(self.dropbox_root.rglob("Repository"))

        if len(repository_folders) > 1:
            self.logger.warning(f"   ⚠️  Found {len(repository_folders)} Repository folders!")

            # Hash each Repository folder
            repo_hashes: Dict[str, List[Path]] = {}

            for repo in repository_folders:
                repo_hash = self._hash_folder(repo)
                if repo_hash:
                    if repo_hash not in repo_hashes:
                        repo_hashes[repo_hash] = []
                    repo_hashes[repo_hash].append(repo)

            # Report duplicates
            for repo_hash, repos in repo_hashes.items():
                if len(repos) > 1:
                    repos.sort(key=lambda p: len(str(p)))
                    original = repos[0]

                    for duplicate in repos[1:]:
                        dup = DuplicateFolder(
                            folder_id=f"repo_dup_{hashlib.md5(str(duplicate).encode()).hexdigest()[:8]}",
                            path=str(duplicate),
                            size=self._get_folder_size(duplicate),
                            file_count=self._count_files(duplicate),
                            hash=repo_hash,
                            duplicate_of=str(original),
                            confidence=0.95,
                            reason="Repository folder duplicate (software licensing)"
                        )
                        self.duplicate_folders.append(dup)

    def _hash_folder(self, folder: Path) -> Optional[str]:
        """Generate hash for folder contents"""
        try:
            # Hash based on file names and sizes (faster than content)
            file_info = []
            for item in folder.rglob("*"):
                if item.is_file():
                    try:
                        stat = item.stat()
                        file_info.append(f"{item.name}:{stat.st_size}:{stat.st_mtime}")
                    except:
                        pass

            if not file_info:
                return None

            file_info.sort()
            content = "\n".join(file_info)
            return hashlib.md5(content.encode()).hexdigest()
        except Exception as e:
            self.logger.debug(f"Hash error for {folder}: {e}")
            return None

    def _get_folder_size(self, folder: Path) -> int:
        """Get total size of folder"""
        total = 0
        try:
            for item in folder.rglob("*"):
                if item.is_file():
                    try:
                        total += item.stat().st_size
                    except:
                        pass
        except:
            pass
        return total

    def _count_files(self, folder: Path) -> int:
        """Count files in folder"""
        count = 0
        try:
            for item in folder.rglob("*"):
                if item.is_file():
                    count += 1
        except:
            pass
        return count

    def _generate_issues(self):
        try:
            """Generate cleanup issues with @MARVIN's intelligence"""
            issue_id = 0

            # Nested Dropbox folders
            for nested in self.nested_dropbox_folders:
                issue = DropboxIssue(
                    issue_id=f"issue_{issue_id:04d}",
                    issue_type="nested_dropbox",
                    path=str(nested),
                    severity="high",
                    description=f"Nested Dropbox folder found: {nested.name}",
                    suggested_action=f"Merge contents with main Dropbox or move to separate location",
                    confidence=0.9
                )
                self.issues.append(issue)
                issue_id += 1

            # Flattened folders
            for flattened in self.flattened_folders:
                issue = DropboxIssue(
                    issue_id=f"issue_{issue_id:04d}",
                    issue_type="flattened",
                    path=str(flattened),
                    severity="medium",
                    description=f"'Dropbox_Flattened' folder found: {flattened.name}",
                    suggested_action="Review contents and merge with main Dropbox if needed",
                    confidence=0.8
                )
                self.issues.append(issue)
                issue_id += 1

            # Duplicate folders
            for dup in self.duplicate_folders:
                issue = DropboxIssue(
                    issue_id=f"issue_{issue_id:04d}",
                    issue_type="duplicate",
                    path=dup.path,
                    duplicate_of=dup.duplicate_of,
                    severity="high" if "Repository" in dup.path else "medium",
                    description=f"Duplicate folder: {Path(dup.path).name} (duplicate of {Path(dup.duplicate_of).name})",
                    suggested_action=f"Remove duplicate at {dup.path} (keep {dup.duplicate_of})",
                    confidence=dup.confidence
                )
                self.issues.append(issue)
                issue_id += 1

        except Exception as e:
            self.logger.error(f"Error in _generate_issues: {e}", exc_info=True)
            raise
    def _count_issues_by_severity(self) -> Dict[str, int]:
        """Count issues by severity"""
        counts = {"high": 0, "medium": 0, "low": 0}
        for issue in self.issues:
            counts[issue.severity] = counts.get(issue.severity, 0) + 1
        return counts

    def _duplicate_to_dict(self, dup: DuplicateFolder) -> Dict[str, Any]:
        """Convert duplicate to dict"""
        return {
            "folder_id": dup.folder_id,
            "path": dup.path,
            "size": dup.size,
            "file_count": dup.file_count,
            "duplicate_of": dup.duplicate_of,
            "confidence": dup.confidence,
            "reason": dup.reason
        }

    def _issue_to_dict(self, issue: DropboxIssue) -> Dict[str, Any]:
        """Convert issue to dict"""
        return {
            "issue_id": issue.issue_id,
            "issue_type": issue.issue_type,
            "path": issue.path,
            "severity": issue.severity,
            "description": issue.description,
            "suggested_action": issue.suggested_action,
            "confidence": issue.confidence
        }

    def generate_cleanup_plan(self) -> Dict[str, Any]:
        try:
            """Generate intelligent cleanup plan with @MARVIN's guidance"""
            self.logger.info("😟 @MARVIN generating cleanup plan...")

            plan = {
                "timestamp": datetime.now().isoformat(),
                "marvin_assessment": self._marvin_assessment(),
                "phases": [
                    {
                        "phase": 1,
                        "name": "High Priority Issues",
                        "description": "Fix nested Dropbox folders and critical duplicates",
                        "issues": [i for i in self.issues if i.severity == "high"],
                        "estimated_time": "2-4 hours",
                        "risk": "Low (backup first)"
                    },
                    {
                        "phase": 2,
                        "name": "Duplicate Cleanup",
                        "description": "Remove duplicate folders (especially Repository/software licensing)",
                        "issues": [i for i in self.issues if i.issue_type == "duplicate"],
                        "estimated_time": "1-2 hours",
                        "risk": "Medium (verify duplicates first)"
                    },
                    {
                        "phase": 3,
                        "name": "Flattened Folder Review",
                        "description": "Review and merge 'Dropbox_Flattened' folders",
                        "issues": [i for i in self.issues if i.issue_type == "flattened"],
                        "estimated_time": "1 hour",
                        "risk": "Low"
                    }
                ],
                "recommendations": self._marvin_recommendations()
            }

            # Save plan
            plan_file = self.data_dir / f"cleanup_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(plan_file, 'w', encoding='utf-8') as f:
                json.dump(plan, f, indent=2, ensure_ascii=False)

            self.logger.info(f"📁 Cleanup plan saved: {plan_file}")

            return plan

        except Exception as e:
            self.logger.error(f"Error in generate_cleanup_plan: {e}", exc_info=True)
            raise
    def _marvin_assessment(self) -> str:
        """@MARVIN's assessment of the situation"""
        return (
            "<SIGH> 20 years of Dropbox mess. Here's the reality:\n\n"
            "PROBLEMS:\n"
            f"- {len(self.nested_dropbox_folders)} nested Dropbox folders\n"
            f"- {len(self.flattened_folders)} 'Dropbox_Flattened' folders\n"
            f"- {len(self.duplicate_folders)} duplicate folders\n"
            f"- Software licensing duplicated multiple times\n\n"
            "SOLUTION:\n"
            "1. BACKUP FIRST - Always backup before cleanup\n"
            "2. Start with high-priority issues (nested folders)\n"
            "3. Remove duplicates carefully (verify they're actually duplicates)\n"
            "4. Merge flattened folders if needed\n"
            "5. Organize logically (not just 'fix duplicates')\n\n"
            "This will take time. Don't rush it. <SIGH>"
        )

    def _marvin_recommendations(self) -> List[str]:
        """@MARVIN's recommendations"""
        return [
            "BACKUP FIRST - Create full backup before any cleanup",
            "Start with nested Dropbox folders (highest priority)",
            "Verify duplicates before deleting (check file counts, sizes)",
            "Keep shortest path as 'original' when removing duplicates",
            "Use software repository vault for software/licenses (not just Dropbox)",
            "Consider moving old 'Dropbox_Flattened' folders to archive",
            "Document what you're doing (this system logs everything)",
            "Do cleanup in phases (don't do everything at once)",
            "Test after each phase (make sure nothing broke)",
            "Consider using NAS for long-term storage (not just Dropbox)"
        ]


def main():
    try:
        """Main execution"""
        import argparse

        parser = argparse.ArgumentParser(description="@MARVIN Dropbox Cleanup")
        parser.add_argument("--analyze", action="store_true", help="Analyze Dropbox structure")
        parser.add_argument("--plan", action="store_true", help="Generate cleanup plan")
        parser.add_argument("--dropbox-root", help="Dropbox root path (default: ~/Dropbox)")

        args = parser.parse_args()

        print("\n" + "="*80)
        print("😟 @MARVIN DROPBOX CLEANUP SYSTEM")
        print("="*80 + "\n")

        dropbox_root = Path(args.dropbox_root) if args.dropbox_root else None
        cleanup = MarvinDropboxCleanup(dropbox_root=dropbox_root)

        if args.analyze or args.plan:
            print("🔍 Analyzing Dropbox structure...\n")
            analysis = cleanup.analyze_dropbox()

            print("📊 ANALYSIS RESULTS:\n")
            print(f"  Nested Dropbox folders: {analysis.get('nested_dropbox_folders', 0)}")
            print(f"  Flattened folders: {analysis.get('flattened_folders', 0)}")
            print(f"  Duplicate folders: {analysis.get('duplicate_folders', 0)}")
            print(f"  Total issues: {analysis.get('total_issues', 0)}")
            print()

            if args.plan:
                print("😟 @MARVIN generating cleanup plan...\n")
                plan = cleanup.generate_cleanup_plan()

                print("📋 CLEANUP PLAN:\n")
                for phase in plan["phases"]:
                    print(f"Phase {phase['phase']}: {phase['name']}")
                    print(f"  Description: {phase['description']}")
                    print(f"  Issues: {len(phase['issues'])}")
                    print(f"  Estimated time: {phase['estimated_time']}")
                    print(f"  Risk: {phase['risk']}")
                    print()

                print("💡 @MARVIN'S RECOMMENDATIONS:\n")
                for i, rec in enumerate(plan["recommendations"], 1):
                    print(f"  {i}. {rec}")
                print()

        else:
            print("Usage:")
            print("  --analyze      : Analyze Dropbox structure")
            print("  --plan         : Generate cleanup plan")
            print("  --dropbox-root : Specify Dropbox root path")
            print()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":



    main()