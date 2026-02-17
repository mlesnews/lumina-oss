#!/usr/bin/env python3
"""
@ASK Extension Handler - Default Format and Action

When @ASK refers to an "extension", what is the default format/type?
Default: VSIX format (.vsix)
Default Extension: Lumina VSIX (lumina-ai-0.1.0.vsix)

The Lumina VSIX is the actual extension - no confusion, no temp placeholder.

Tags: #ASK #EXTENSION #VSIX #DEFAULT-FORMAT #LUMINA @JARVIS @TEAM
"""

import sys
from pathlib import Path
from typing import Dict, Optional, Any

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
    try:
        from standardized_timestamp_logging import get_timestamp_logger
    except ImportError:
        get_timestamp_logger = lambda: get_logger("Timestamp")
except ImportError as e:
    print(f"❌ Error importing modules: {e}")
    sys.exit(1)

logger = get_logger("ASKExtensionHandler")
try:
    ts_logger = get_timestamp_logger()
except:
    ts_logger = logger


class ASKEXTENSIONHANDLER:
    """
    @ASK Extension Handler - Default Format and Action

    When @ASK refers to an "extension":
    - Default format: VSIX (.vsix)
    - Default extension: Lumina VSIX (lumina-ai-0.1.0.vsix)
    - Not temp, not JSON (unless specified)
    - Workspace scope
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @ASK Extension Handler"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)

        # Default extension
        self.default_extension_format = "VSIX"
        self.default_extension_file = "lumina-ai-0.1.0.vsix"
        self.default_extension_path = self.project_root / self.default_extension_file

        # Also check vscode-extensions directory
        self.vsix_dir = self.project_root / "vscode-extensions"
        self.vsix_file_alt = self.vsix_dir / self.default_extension_file

        logger.info("📦 @ASK Extension Handler initialized")
        logger.info(f"   Default format: {self.default_extension_format}")
        logger.info(f"   Default extension: {self.default_extension_file}")
        logger.info("   Lumina VSIX is the actual extension - no confusion")

    def get_default_extension(self) -> Dict[str, Any]:
        try:
            """Get default extension information"""
            # Check for VSIX file
            vsix_path = None
            if self.default_extension_path.exists():
                vsix_path = self.default_extension_path
            elif self.vsix_file_alt.exists():
                vsix_path = self.vsix_file_alt

            return {
                "format": self.default_extension_format,
                "file": self.default_extension_file,
                "extension": ".vsix",
                "path": str(vsix_path) if vsix_path else None,
                "exists": vsix_path is not None and vsix_path.exists(),
                "type": "VSIX",
                "is_lumina_vsix": True,
                "is_temp": False,
                "workspace_scope": True,
            }

        except Exception as e:
            self.logger.error(f"Error in get_default_extension: {e}", exc_info=True)
            raise
    def handle_ask_extension(self, ask_content: str) -> Dict[str, Any]:
        """Handle @ASK that refers to extension"""
        logger.info("📦 Handling @ASK extension reference")
        logger.info(f"   Ask: {ask_content[:100]}...")

        default_info = self.get_default_extension()

        result = {
            "default_format": default_info["format"],
            "default_extension": default_info["file"],
            "default_type": default_info["type"],
            "extension_path": default_info["path"],
            "exists": default_info["exists"],
            "is_lumina_vsix": True,
            "is_temp": False,
            "workspace_scope": True,
            "ask_content": ask_content,
        }

        logger.info(f"   Default format: {result['default_format']}")
        logger.info(f"   Default extension: {result['default_extension']}")
        logger.info(f"   Is Lumina VSIX: {result['is_lumina_vsix']}")
        logger.info(f"   Is temp: {result['is_temp']}")

        return result


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description="@ASK Extension Handler - Default Format and Action")
    parser.add_argument("--ask", type=str, help="Handle @ASK that refers to extension")
    parser.add_argument("--default", action="store_true", help="Show default extension info")

    args = parser.parse_args()

    print("="*80)
    print("📦 @ASK EXTENSION HANDLER - DEFAULT FORMAT AND ACTION")
    print("="*80)
    print()
    print("When @ASK refers to 'extension':")
    print("  Default format: VSIX (.vsix)")
    print("  Default extension: Lumina VSIX (lumina-ai-0.1.0.vsix)")
    print("  The Lumina VSIX is the actual extension - no confusion")
    print()

    handler = ASKEXTENSIONHANDLER()

    if args.default:
        info = handler.get_default_extension()
        print("📦 DEFAULT EXTENSION INFO:")
        print(f"   Format: {info['format']}")
        print(f"   File: {info['file']}")
        print(f"   Extension: {info['extension']}")
        print(f"   Type: {info['type']}")
        print(f"   Path: {info['path']}")
        print(f"   Exists: {info['exists']}")
        print(f"   Is Lumina VSIX: {info['is_lumina_vsix']}")
        print(f"   Is temp: {info['is_temp']}")
        print(f"   Workspace scope: {info['workspace_scope']}")
        print()

    if args.ask:
        result = handler.handle_ask_extension(args.ask)
        print("📦 @ASK EXTENSION HANDLED:")
        print(f"   Default format: {result['default_format']}")
        print(f"   Default extension: {result['default_extension']}")
        print(f"   Is Lumina VSIX: {result['is_lumina_vsix']}")
        print(f"   Is temp: {result['is_temp']}")
        print()

    if not args.default and not args.ask:
        # Default: show info
        info = handler.get_default_extension()
        print("📦 DEFAULT EXTENSION:")
        print(f"   Format: {info['format']} ({info['extension']})")
        print(f"   File: {info['file']}")
        print(f"   Type: {info['type']}")
        print(f"   Exists: {info['exists']}")
        print()
        print("Use --default to show full default extension info")
        print("Use --ask CONTENT to handle @ASK that refers to extension")
        print()


if __name__ == "__main__":


    main()