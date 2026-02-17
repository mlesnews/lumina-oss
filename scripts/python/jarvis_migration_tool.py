#!/usr/bin/env python3
"""
Jarvis Migration Tool - Transfer Extension Functionality to Jarvis

This tool helps migrate functionality from coding assistant extensions
into Jarvis with proper accreditation.
"""

from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import json
import argparse
import shutil


@dataclass
class ExtensionInfo:
    """Information about a coding assistant extension"""
    name: str
    display_name: str
    authors: List[str]
    license_type: str
    repository: str
    website: str
    description: str
    key_features: List[str]
    license_text: Optional[str] = None
    contributors: List[str] = field(default_factory=list)


class ExtensionRegistry:
    """Registry of coding assistant extensions"""

    def __init__(self):
        self.extensions = self._initialize_extensions()

    def _initialize_extensions(self) -> Dict[str, ExtensionInfo]:
        """Initialize known extensions"""
        return {
            "github-copilot": ExtensionInfo(
                name="github-copilot",
                display_name="GitHub Copilot",
                authors=["GitHub, Inc."],
                license_type="Proprietary (with open-source components)",
                repository="https://github.com/features/copilot",
                website="https://github.com/features/copilot",
                description="AI-powered code completion and chat",
                key_features=[
                    "Code completion",
                    "Inline suggestions",
                    "Chat interface",
                    "Multi-line completions",
                    "Function-level suggestions"
                ],
                contributors=["GitHub Engineering Team", "OpenAI (Codex model)"]
            ),
            "cursor-ide": ExtensionInfo(
                name="cursor-ide",
                display_name="Cursor IDE",
                authors=["Cursor, Inc."],
                license_type="Proprietary",
                repository="https://github.com/getcursor/cursor",
                website="https://cursor.sh",
                description="AI-powered code editor with semantic understanding",
                key_features=[
                    "Semantic codebase understanding",
                    "Multi-file editing",
                    "Context-aware suggestions",
                    "Codebase indexing",
                    "Cross-file references"
                ],
                contributors=["Cursor Engineering Team"]
            ),
            "claude-code": ExtensionInfo(
                name="claude-code",
                display_name="Claude Code (Anthropic)",
                authors=["Anthropic"],
                license_type="Proprietary",
                repository="https://github.com/anthropics",
                website="https://www.anthropic.com",
                description="Long-context AI coding assistant",
                key_features=[
                    "Long context handling",
                    "Iterative refinement",
                    "Step-by-step reasoning",
                    "Alternative implementations",
                    "Design pattern suggestions"
                ],
                contributors=["Anthropic Engineering Team"]
            ),
            "codeium": ExtensionInfo(
                name="codeium",
                display_name="Codeium",
                authors=["Codeium, Inc."],
                license_type="Proprietary (Free tier available)",
                repository="https://github.com/Exafunction/codeium",
                website="https://codeium.com",
                description="AI coding assistant with multi-model support",
                key_features=[
                    "Multi-model support",
                    "Security scanning",
                    "Dependency checking",
                    "Code review suggestions",
                    "Free tier available"
                ],
                contributors=["Codeium Engineering Team"]
            ),
            "tabnine": ExtensionInfo(
                name="tabnine",
                display_name="Tabnine",
                authors=["Tabnine, Inc."],
                license_type="Proprietary (with open-source components)",
                repository="https://github.com/codota/TabNine",
                website="https://www.tabnine.com",
                description="AI code completion with local models",
                key_features=[
                    "Local model support",
                    "Privacy-first architecture",
                    "Offline capabilities",
                    "Custom model training",
                    "Enterprise security"
                ],
                contributors=["Tabnine Engineering Team"]
            ),
            "sourcegraph-cody": ExtensionInfo(
                name="sourcegraph-cody",
                display_name="Sourcegraph Cody",
                authors=["Sourcegraph, Inc."],
                license_type="Open Source (Apache 2.0)",
                repository="https://github.com/sourcegraph/cody",
                website="https://sourcegraph.com/cody",
                description="Open-source AI coding assistant",
                key_features=[
                    "Codebase search",
                    "Context aggregation",
                    "Symbol navigation",
                    "Code intelligence",
                    "Open source"
                ],
                contributors=["Sourcegraph Engineering Team", "Community Contributors"]
            )
        }

    def get_extension(self, name: str) -> Optional[ExtensionInfo]:
        """Get extension information"""
        return self.extensions.get(name)

    def list_extensions(self) -> List[str]:
        """List all registered extensions"""
        return list(self.extensions.keys())


class MigrationTool:
    """Tool for migrating extension functionality to Jarvis"""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.agents_dir = project_root / "lumina" / "agents" / "coding-agents"
        self.registry = ExtensionRegistry()

    def create_directory_structure(self, extension_name: str) -> Path:
        """Create directory structure for an extension"""
        ext_dir = self.agents_dir / extension_name
        ext_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (ext_dir / "features").mkdir(exist_ok=True)
        (ext_dir / "integration").mkdir(exist_ok=True)
        (ext_dir / "tests").mkdir(exist_ok=True)
        (ext_dir / "docs").mkdir(exist_ok=True)

        return ext_dir

    def create_accreditation_file(self, extension_name: str) -> Path:
        """Create accreditation file for an extension"""
        ext_info = self.registry.get_extension(extension_name)
        if not ext_info:
            raise ValueError(f"Unknown extension: {extension_name}")

        ext_dir = self.agents_dir / extension_name
        acc_file = ext_dir / "ACCREDITATION.md"

        content = f"""# {ext_info.display_name} - Accreditation

## Original Project
- **Name**: {ext_info.display_name}
- **Authors**: {', '.join(ext_info.authors)}
- **License**: {ext_info.license_type}
- **Repository**: {ext_info.repository}
- **Website**: {ext_info.website}

## Description
{ext_info.description}

## Key Features
{chr(10).join(f'- {feature}' for feature in ext_info.key_features)}

## Attribution
This implementation is inspired by {ext_info.display_name}'s architecture
and best practices. We acknowledge the innovation and hard work of the
original authors and contributors.

## Contributors
{chr(10).join(f'- {contributor}' for contributor in ext_info.contributors)}

## License
{ext_info.license_text or f"See original repository: {ext_info.repository}"}

## Usage in Jarvis
The functionality from {ext_info.display_name} has been integrated into
Jarvis to provide:
{chr(10).join(f'- {feature}' for feature in ext_info.key_features)}

## Modifications
- Integrated into Jarvis architecture
- Adapted to work with Jarvis core systems
- Enhanced with additional security and verification layers

## Contact
For questions about the original project, please contact:
- Repository: {ext_info.repository}
- Website: {ext_info.website}

---
*This accreditation file ensures proper credit to the original authors
and contributors of {ext_info.display_name}. We are grateful for their
open-source contributions and innovation in AI-powered coding assistance.*
"""

        with open(acc_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return acc_file

    def create_readme(self, extension_name: str) -> Path:
        """Create README for an extension"""
        ext_info = self.registry.get_extension(extension_name)
        if not ext_info:
            raise ValueError(f"Unknown extension: {extension_name}")

        ext_dir = self.agents_dir / extension_name
        readme_file = ext_dir / "README.md"

        content = f"""# {ext_info.display_name} Integration

## Overview
This module contains functionality inspired by {ext_info.display_name},
integrated into the Jarvis coding assistant system.

## Features
{chr(10).join(f'- **{feature}**: Implementation of {ext_info.display_name} feature' for feature in ext_info.key_features)}

## Integration
This module integrates with Jarvis core through:
- `integration/jarvis_integration.py` - Main integration interface
- Feature modules in `features/` directory
- Test suite in `tests/` directory

## Usage
```python
from lumina.agents.coding_agents.{extension_name}.integration import JarvisIntegration

integration = JarvisIntegration()
# Use integration features
```

## Accreditation
See [ACCREDITATION.md](./ACCREDITATION.md) for full credit to original authors.

## License
{ext_info.license_type}

See [LICENSE.md](./LICENSE.md) for full license information.
"""

        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return readme_file

    def create_license_file(self, extension_name: str) -> Path:
        """Create license file for an extension"""
        ext_info = self.registry.get_extension(extension_name)
        if not ext_info:
            raise ValueError(f"Unknown extension: {extension_name}")

        ext_dir = self.agents_dir / extension_name
        license_file = ext_dir / "LICENSE.md"

        content = f"""# License Information - {ext_info.display_name}

## Original License
{ext_info.license_type}

## Source
{ext_info.repository}

## License Text
{ext_info.license_text or "See original repository for full license text."}

## Usage in Jarvis
This functionality is used in Jarvis under the terms of the original license.
Please refer to the original repository for complete license information.

## Attribution
All credit goes to the original authors and contributors of {ext_info.display_name}.
"""
        with open(license_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return license_file

    def create_integration_template(self, extension_name: str) -> Path:
        """Create integration template"""
        ext_dir = self.agents_dir / extension_name
        integration_file = ext_dir / "integration" / "jarvis_integration.py"

        content = f'''#!/usr/bin/env python3
"""
Jarvis Integration for {extension_name}

This module integrates {extension_name} functionality into Jarvis.
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
logger = logging.getLogger("jarvis_migration_tool")



class JarvisIntegration:
    """Integration interface for {extension_name} features"""

    def __init__(self, project_root: Optional[Path] = None):
        self.project_root = project_root
        self.features = self._initialize_features()

    def _initialize_features(self) -> Dict[str, Any]:
        """Initialize {extension_name} features"""
        return {{
            # Add feature implementations here
        }}

    def get_available_features(self) -> List[str]:
        """Get list of available features"""
        return list(self.features.keys())

    def execute_feature(self, feature_name: str, **kwargs) -> Any:
        """Execute a specific feature"""
        if feature_name not in self.features:
            raise ValueError(f"Unknown feature: {{feature_name}}")
        return self.features[feature_name](**kwargs)
'''
        with open(integration_file, 'w', encoding='utf-8') as f:
            f.write(content)

        return integration_file

    def setup_extension(self, extension_name: str) -> Dict[str, Path]:
        """Set up complete extension structure"""
        print(f"📦 Setting up {extension_name}...")

        # Create directory structure
        ext_dir = self.create_directory_structure(extension_name)

        # Create files
        files = {
            "accreditation": self.create_accreditation_file(extension_name),
            "readme": self.create_readme(extension_name),
            "license": self.create_license_file(extension_name),
            "integration": self.create_integration_template(extension_name)
        }

        print(f"✅ Created structure for {extension_name}")
        return files

    def setup_all_extensions(self) -> Dict[str, Dict[str, Path]]:
        """Set up all registered extensions"""
        results = {}
        for ext_name in self.registry.list_extensions():
            results[ext_name] = self.setup_extension(ext_name)
        return results


def main():
    try:
        """Main entry point"""
        parser = argparse.ArgumentParser(
            description="Jarvis Migration Tool - Transfer Extension Functionality"
        )
        parser.add_argument(
            "--setup", type=str, metavar="EXTENSION",
            help="Set up a specific extension"
        )
        parser.add_argument(
            "--setup-all", action="store_true",
            help="Set up all registered extensions"
        )
        parser.add_argument(
            "--list", action="store_true",
            help="List all registered extensions"
        )
        parser.add_argument(
            "--info", type=str, metavar="EXTENSION",
            help="Show information about an extension"
        )

        args = parser.parse_args()

        project_root = Path(__file__).parent.parent.parent
        tool = MigrationTool(project_root)

        if args.list:
            print("📋 Registered Extensions:")
            for ext_name in tool.registry.list_extensions():
                ext_info = tool.registry.get_extension(ext_name)
                print(f"   - {ext_info.display_name} ({ext_name})")
            return

        if args.info:
            ext_info = tool.registry.get_extension(args.info)
            if ext_info:
                print(f"📄 {ext_info.display_name}")
                print(f"   Authors: {', '.join(ext_info.authors)}")
                print(f"   License: {ext_info.license_type}")
                print(f"   Repository: {ext_info.repository}")
                print(f"   Features: {len(ext_info.key_features)}")
            else:
                print(f"❌ Unknown extension: {args.info}")
            return

        if args.setup:
            tool.setup_extension(args.setup)
            print(f"\n✅ Setup complete for {args.setup}")
            print(f"   Directory: {tool.agents_dir / args.setup}")
            return

        if args.setup_all:
            print("🚀 Setting up all extensions...\n")
            results = tool.setup_all_extensions()
            print(f"\n✅ Set up {len(results)} extensions")
            print(f"   Location: {tool.agents_dir}")
            return

        parser.print_help()


    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
        raise
if __name__ == "__main__":

    main()