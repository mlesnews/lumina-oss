#!/usr/bin/env python3
"""
LUMINA Standardization Migrator

Migrates existing code to use lumina_core modules. Runs as part of @bau workflows.

Tags: #STANDARDIZATION #MIGRATION #LUMINA_CORE #BAU @JARVIS @LUMINA
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional

# Setup paths for lumina_core
script_dir = Path(__file__).parent
project_root_global = script_dir.parent.parent

try:
    from lumina_core.paths import get_project_root, setup_paths
    from lumina_core.logging import get_logger
    setup_paths()
    project_root = get_project_root()
except ImportError:
    from lumina_core.logging import get_logger
    project_root = script_dir.parent.parent

logger = get_logger("LuminaStandardizationMigrator")
scripts_dir = project_root / "scripts" / "python"


@dataclass
class MigrationRule:
    """Migration rule for code transformation"""
    pattern: str
    replacement: str
    description: str
    priority: str = "high"
    flags: int = 0


class LuminaStandardizationMigrator:
    """
    Automated migrator for standardization

    Migrates existing code to use lumina_core modules following @bau workflows.
    """

    def __init__(self):
        """Initialize migrator"""
        self.migration_rules = self._get_migration_rules()
        self.migrated_files = []
        self.failed_files = []

        logger.info("✅ LUMINA Standardization Migrator initialized")

    def _get_migration_rules(self) -> List[MigrationRule]:
        """Get migration rules for code transformation"""
        return [
            # Logger migration
            MigrationRule(
                pattern=r'from\s+lumina_logger\s+import\s+get_logger',
                replacement='from lumina_core.logging import get_logger',
                description="Migrate lumina_logger to lumina_core.logging",
                priority="high"
            ),
            MigrationRule(
                pattern=r'from\s+lumina_adaptive_logger\s+import\s+get_adaptive_logger',
                replacement='from lumina_core.logging import get_logger',
                description="Migrate lumina_adaptive_logger to lumina_core.logging",
                priority="high"
            ),
            MigrationRule(
                pattern=r'get_logger\s*=\s*get_adaptive_logger',
                replacement='# Using lumina_core.logging.get_logger',
                description="Remove adaptive logger assignment",
                priority="high"
            ),
            MigrationRule(
                pattern=(r'except\s+ImportError:.*?get_logger\s*=\s*lambda\s+name'
                         r':\s+logging\.getLogger\(name\)'),
                replacement='except ImportError:\n    from lumina_core.logging import get_logger',
                description="Replace lambda fallback with lumina_core",
                priority="high",
                flags=re.DOTALL
            ),

            # Path migration
            MigrationRule(
                pattern=r'script_dir\s*=\s*Path\(__file__\)\.parent',
                replacement=('from lumina_core.paths import get_script_dir\n'
                             'script_dir = get_script_dir()'),
                description="Migrate script_dir to lumina_core.paths",
                priority="high"
            ),
            MigrationRule(
                pattern=r'project_root\s*=\s*Path\(__file__\)\.parent\.parent\.parent',
                replacement=('from lumina_core.paths import get_project_root\n'
                             'project_root = get_project_root()'),
                description="Migrate project_root detection to lumina_core.paths",
                priority="high"
            ),
            MigrationRule(
                pattern=r'project_root\s*=\s*Path\(__file__\)\.parent\.parent',
                replacement=('from lumina_core.paths import get_project_root\n'
                             'project_root = get_project_root()'),
                description="Migrate project_root detection (2 levels) to lumina_core.paths",
                priority="high"
            ),
            MigrationRule(
                pattern=(r'if\s+str\(project_root\)\s+not\s+in\s+sys\.path:.*?'
                         r'sys\.path\.insert\(0,\s*str\(project_root\)\)'),
                replacement='from lumina_core.paths import setup_paths\nsetup_paths()',
                description="Replace sys.path management with lumina_core.paths.setup_paths",
                priority="high",
                flags=re.DOTALL
            ),
        ]

    def migrate_file(self, file_path: Path) -> Tuple[bool, str]:
        """Migrate a single file"""
        try:
            content = file_path.read_text(encoding='utf-8')
            original_content = content
            changes_made = False

            # Apply migration rules
            for rule in self.migration_rules:
                flags = 0
                if hasattr(rule, 'flags'):
                    flags = rule.flags

                new_content = re.sub(rule.pattern, rule.replacement, content, flags=flags)
                if new_content != original_content: # Compare with original
                    content = new_content
                    changes_made = True
                    logger.debug("   Applied: %s", rule.description)

            # Only write if changes were made
            if changes_made:
                file_path.write_text(content, encoding='utf-8')
                return True, "Migrated successfully"

            return False, "No changes needed"
        except (IOError, UnicodeDecodeError) as e:
            logger.error("   Error migrating %s: %s", file_path, e)
            return False, str(e)

    def migrate_all(self, directory: Optional[Path] = None):
        """Migrate all Python files in directory"""
        if directory is None:
            directory = scripts_dir

        logger.info("🚀 Starting migration in %s...", directory)

        files = list(directory.rglob("*.py"))
        logger.info("📁 Found %d Python files", len(files))

        for file_path in files:
            success, message = self.migrate_file(file_path)
            if success:
                self.migrated_files.append(file_path)
            elif message != "No changes needed":
                self.failed_files.append((file_path, message))

        logger.info("✅ Migration complete")
        logger.info("   Files migrated: %d", len(self.migrated_files))
        logger.info("   Files failed: %d", len(self.failed_files))


def main():
    try:
        """Main entry point"""
        import argparse

        parser = argparse.ArgumentParser(
            description="LUMINA Standardization Migrator - @BAU Workflow"
        )
        parser.add_argument("--dir", type=str, help="Directory to migrate")
        parser.add_argument("--file", type=str, help="Single file to migrate")

        args = parser.parse_args()

        migrator = LuminaStandardizationMigrator()

        if args.file:
            success, message = migrator.migrate_file(Path(args.file))
            if success:
                print(f"✅ Migrated: {args.file}")
            else:
                print(f"ℹ️  {args.file}: {message}")
        else:
            migrator.migrate_all(Path(args.dir) if args.dir else None)


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":


    main()