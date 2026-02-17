#!/usr/bin/env python3
"""
Fix All Azure Credential Certificate Prompts

This script finds and fixes all DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                ) calls that might trigger
certificate prompts during startup. It updates them to exclude certificate authentication.

Run this script to automatically fix all instances across the codebase.
"""

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "python"


def fix_default_azure_credential(file_path: Path) -> bool:
    """Fix DefaultAzureCredential(
                    exclude_interactive_browser_credential=False,
                    exclude_shared_token_cache_credential=False
                ) calls in a file"""
    try:
        content = file_path.read_text(encoding='utf-8')
        original_content = content

        # Pattern 1: DefaultAzureCredential() - simple case
        pattern1 = r'DefaultAzureCredential\(\)'
        replacement1 = r'DefaultAzureCredential(\n                    exclude_interactive_browser_credential=False,\n                    exclude_shared_token_cache_credential=False\n                )'

        # Pattern 2: DefaultAzureCredential(exclude_interactive_browser_credential=False, exclude_shared_token_cache_credential=False) with existing parameters (more complex)
        # We'll handle this case by case

        # Check if file needs fixing
        if 'DefaultAzureCredential(exclude_interactive_browser_credential=False, exclude_shared_token_cache_credential=False)' in content:
            # Simple replacement for basic cases
            content = re.sub(
                r'(\s+)credential\s*=\s*DefaultAzureCredential\(\)',
                r'\1credential = DefaultAzureCredential(\n\1                    exclude_interactive_browser_credential=False,\n\1                    exclude_shared_token_cache_credential=False\n\1                )',
                content
            )

            # Also handle direct assignments
            content = re.sub(
                r'DefaultAzureCredential\(\)',
                r'DefaultAzureCredential(\n                    exclude_interactive_browser_credential=False,\n                    exclude_shared_token_cache_credential=False\n                )',
                content
            )

            if content != original_content:
                file_path.write_text(content, encoding='utf-8')
                return True

        return False
    except Exception as e:
        print(f"Error fixing {file_path}: {e}", file=sys.stderr)
        return False


def find_all_python_files() -> list[Path]:
    """Find all Python files in scripts directory"""
    python_files = []
    for file_path in SCRIPTS_DIR.rglob("*.py"):
        python_files.append(file_path)
    return python_files


def main():
    """Main function"""
    print("🔍 Finding all DefaultAzureCredential(...) calls...")

    python_files = find_all_python_files()
    files_with_credential = []

    for file_path in python_files:
        try:
            content = file_path.read_text(encoding='utf-8')
            if 'DefaultAzureCredential(' in content:
                files_with_credential.append(file_path)
        except Exception:
            continue

    if not files_with_credential:
        print("✅ No files found with DefaultAzureCredential(...)")
        return 0

    print(f"\n📋 Found {len(files_with_credential)} file(s) with DefaultAzureCredential(...):")
    for file_path in files_with_credential:
        print(f"   - {file_path.relative_to(PROJECT_ROOT)}")

    print("\n🔧 Fixing files...")
    fixed_count = 0

    for file_path in files_with_credential:
        if fix_default_azure_credential(file_path):
            print(f"   ✅ Fixed: {file_path.relative_to(PROJECT_ROOT)}")
            fixed_count += 1
        else:
            print(f"   ⚠️  Skipped (may already be fixed): {file_path.relative_to(PROJECT_ROOT)}")

    print(f"\n✅ Fixed {fixed_count} file(s)")
    print("\n💡 Note: Some files may need manual review if they have complex DefaultAzureCredential usage")

    return 0


if __name__ == "__main__":

    sys.exit(main())