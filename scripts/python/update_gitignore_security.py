#!/usr/bin/env python3
"""
Update .gitignore with Security Patterns

Adds comprehensive security patterns to .gitignore to prevent
private data from being committed.

Tags: #SECURITY #GITIGNORE @MARVIN @JARVIS
"""

import sys
from pathlib import Path
from typing import List
import logging
logger = logging.getLogger("update_gitignore_security")


script_dir = Path(__file__).parent
project_root = script_dir.parent.parent

# Security patterns to add
SECURITY_PATTERNS = [
    "",
    "# Security - Private Data Patterns",
    "# Credentials and Secrets",
    "**/*.key",
    "**/*.pem",
    "**/*.p12",
    "**/*.pfx",
    "**/*.secret",
    "**/secrets*.json",
    "**/credentials*.json",
    "**/*credentials*.json",
    "**/*secrets*.json",
    "",
    "# Environment files with potential secrets",
    "**/.env.local",
    "**/.env.production",
    "**/.env.staging",
    "**/.env.*.local",
    "",
    "# Private company data",
    "**/company_data/**",
    "**/private_data/**",
    "**/confidential/**",
    "",
    "# API Keys and Tokens",
    "**/*api_key*.json",
    "**/*token*.json",
    "**/*access_token*.json",
    "",
    "# Database credentials",
    "**/*database*.credentials*",
    "**/*db*.credentials*",
    "",
    "# AWS and Cloud credentials",
    "**/*aws*.credentials*",
    "**/*azure*.credentials*",
    "**/*gcp*.credentials*",
    "",
    "# Backup files that might contain secrets",
    "**/*.backup",
    "**/*backup*.json",
    "**/*backup*.db",
]


def update_gitignore():
    try:
        """Update .gitignore with security patterns"""
        gitignore_path = project_root / ".gitignore"

        # Read existing .gitignore
        existing_lines = []
        if gitignore_path.exists():
            with open(gitignore_path, 'r', encoding='utf-8') as f:
                existing_lines = f.read().splitlines()

        # Check if security section already exists
        has_security_section = any("# Security" in line for line in existing_lines)

        if has_security_section:
            print("✅ Security section already exists in .gitignore")
            return

        # Add security patterns
        with open(gitignore_path, 'a', encoding='utf-8') as f:
            f.write("\n")
            f.write("\n".join(SECURITY_PATTERNS))
            f.write("\n")

        print("✅ Security patterns added to .gitignore")
        print(f"   Added {len([p for p in SECURITY_PATTERNS if p and not p.startswith('#')])} patterns")


    except Exception as e:
        logger.error(f"Error in update_gitignore: {e}", exc_info=True)
        raise
if __name__ == "__main__":
    update_gitignore()
