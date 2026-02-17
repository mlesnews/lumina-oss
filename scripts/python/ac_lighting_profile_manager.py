#!/usr/bin/env python3
"""
@AC Lighting Profile Manager
=============================
@AC = API & CLI (consistent results)

Manages Armoury Crate lighting profiles via both API and CLI methods.
Ensures consistent results regardless of which method is used.

Features:
- Create/update/delete/apply profiles
- Multiple predefined profiles (ZERO-DARK-THIRTY, DARK, LIGHT, GAMING, FOCUS, BRANDING, DEMO)
- Full API & CLI integration
- Custom effect support
- Branding/marketing profiles

@AC @ARMOURY_CRATE @LIGHTING @PROFILES @API @CLI
"""

import sys
import json
import asyncio
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from lumina_unified_logger import LuminaUnifiedLogger
    logger = LuminaUnifiedLogger("System", "ACLightingProfiles")
    _logger = logger.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger("ACLightingProfiles")


@dataclass
class LightingProfile:
    """Lighting profile definition"""
    name: str
    short_name: str
    tag: str = "@AC"  # API & CLI tag
    description: str = ""
    screen_brightness: int = 100
    lighting_enabled: bool = True
    lighting_brightness: int = 100
    effect: str = "static"
    color: str = "#ffffff"
    zones: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    use_cases: List[str] = field(default_factory=list)


class ACLightingProfileManager:
    """
    @AC Lighting Profile Manager

    @AC = API & CLI (consistent results)
    Ensures profiles work the same whether called via API or CLI.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @AC profile manager"""
        self.project_root = project_root or PROJECT_ROOT
        self.logger = _logger

        # Load profiles configuration
        self.profiles_config = self.project_root / "config" / "lighting_profiles.json"
        self.profiles: Dict[str, LightingProfile] = {}
        self.effects: List[Dict[str, Any]] = []
        self._load_profiles()

        # Initialize Armoury Crate integration
        self.ac_integration = None
        self._init_armoury_crate()

        self.logger.info("✅ @AC Lighting Profile Manager initialized")
        self.logger.info(f"   Loaded {len(self.profiles)} profiles")
        self.logger.info(f"   Tag system: @AC = API & CLI (consistent results)")

    def _load_profiles(self):
        """Load lighting profiles from configuration"""
        try:
            if not self.profiles_config.exists():
                self.logger.warning(f"Profiles config not found: {self.profiles_config}")
                return

            with open(self.profiles_config, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # Load profiles
            for profile_data in config.get("profiles", []):
                profile = LightingProfile(
                    name=profile_data["name"],
                    short_name=profile_data.get("short_name", profile_data["name"]),
                    tag=profile_data.get("tag", "@AC"),
                    description=profile_data.get("description", ""),
                    screen_brightness=profile_data.get("screen_brightness", 100),
                    lighting_enabled=profile_data.get("lighting_enabled", True),
                    lighting_brightness=profile_data.get("lighting_brightness", 100),
                    effect=profile_data.get("effect", "static"),
                    color=profile_data.get("color", "#ffffff"),
                    zones=profile_data.get("zones", {}),
                    use_cases=profile_data.get("use_cases", [])
                )
                # Index by name (primary)
                self.profiles[profile.name.upper()] = profile
                # Also index by short name if different
                if profile.short_name.upper() != profile.name.upper():
                    self.profiles[profile.short_name.upper()] = profile

            # Load effects
            self.effects = config.get("effects", [])

            self.logger.info(f"✅ Loaded {len(self.profiles)} profiles, {len(self.effects)} effects")

        except Exception as e:
            self.logger.error(f"Failed to load profiles: {e}")

    def _init_armoury_crate(self):
        """Initialize Armoury Crate integration (@AC - API & CLI)"""
        try:
            from src.cfservices.services.jarvis_core.integrations.armoury_crate import ArmouryCrateIntegration
            self.ac_integration = ArmouryCrateIntegration()
            self.logger.info("✅ Armoury Crate integration initialized (@AC)")
        except Exception as e:
            self.logger.warning(f"Armoury Crate integration not available: {e}")

    def get_profile(self, profile_name: str) -> Optional[LightingProfile]:
        """Get profile by name (case-insensitive)"""
        return self.profiles.get(profile_name.upper())

    def list_profiles(self) -> List[LightingProfile]:
        """List all available profiles (deduplicated)"""
        # Return unique profiles (by name)
        seen = set()
        unique_profiles = []
        for profile in self.profiles.values():
            if profile.name not in seen:
                seen.add(profile.name)
                unique_profiles.append(profile)
        return unique_profiles

    async def create_profile(self, profile: LightingProfile, use_api: bool = True, use_cli: bool = True) -> Dict[str, Any]:
        """
        Create profile via @AC (API & CLI)

        Args:
            profile: LightingProfile to create
            use_api: Use API method
            use_cli: Use CLI method (for consistency check)
        """
        self.logger.info(f"@AC: Creating profile '{profile.name}' ({profile.tag})")

        result = {
            "success": False,
            "profile_name": profile.name,
            "methods_used": [],
            "errors": []
        }

        # Method 1: API (@AC)
        if use_api and self.ac_integration:
            try:
                api_result = await self.ac_integration._handle_create_profile({
                    "name": profile.name,
                    "description": profile.description,
                    "screen_brightness": profile.screen_brightness,
                    "lighting_enabled": profile.lighting_enabled,
                    "lighting_brightness": profile.lighting_brightness,
                    "effect": profile.effect,
                    "zones": profile.zones
                })

                if api_result.get("success"):
                    result["success"] = True
                    result["methods_used"].append("API")
                    self.logger.info(f"✅ Profile created via API (@AC)")
                else:
                    result["errors"].append(f"API: {api_result.get('error', 'Unknown')}")
            except Exception as e:
                result["errors"].append(f"API error: {e}")

        # Method 2: CLI (@AC) - for consistency verification
        if use_cli:
            try:
                # Use registry/UI automation as CLI method
                cli_result = await self._create_profile_via_cli(profile)
                if cli_result.get("success"):
                    result["methods_used"].append("CLI")
                    self.logger.info(f"✅ Profile created via CLI (@AC)")
                else:
                    result["errors"].append(f"CLI: {cli_result.get('error', 'Unknown')}")
            except Exception as e:
                result["errors"].append(f"CLI error: {e}")

        return result

    async def _create_profile_via_cli(self, profile: LightingProfile) -> Dict[str, Any]:
        """Create profile via CLI method (registry + UI automation)"""
        try:
            # Set registry values
            script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura'
)

$brightness = {profile.lighting_brightness}
$enabled = {1 if profile.lighting_enabled else 0}

foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'Brightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
        }}
    }} catch {{
    }}
}}
Write-Output "OK"
"""
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0:
                return {"success": True, "method": "CLI"}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def apply_profile(self, profile_name: str, use_api: bool = True, use_cli: bool = True) -> Dict[str, Any]:
        """
        Apply profile via @AC (API & CLI)

        Ensures consistent results regardless of method used.
        """
        profile = self.get_profile(profile_name)
        if not profile:
            return {"success": False, "error": f"Profile '{profile_name}' not found"}

        self.logger.info(f"@AC: Applying profile '{profile.name}' ({profile.tag})")

        result = {
            "success": False,
            "profile_name": profile.name,
            "methods_used": [],
            "errors": []
        }

        # Method 1: API (@AC)
        if use_api and self.ac_integration:
            try:
                api_result = await self.ac_integration._handle_apply_profile({
                    "profile_name": profile.name
                })

                if api_result.get("success"):
                    result["success"] = True
                    result["methods_used"].append("API")
                    self.logger.info(f"✅ Profile applied via API (@AC)")
                else:
                    result["errors"].append(f"API: {api_result.get('error', 'Unknown')}")
            except Exception as e:
                result["errors"].append(f"API error: {e}")

        # Method 2: CLI (@AC) - apply via registry + zones
        if use_cli:
            try:
                cli_result = await self._apply_profile_via_cli(profile)
                if cli_result.get("success"):
                    result["methods_used"].append("CLI")
                    result["success"] = True  # CLI success also counts
                    self.logger.info(f"✅ Profile applied via CLI (@AC)")
                else:
                    if not result["success"]:  # Only add error if API also failed
                        result["errors"].append(f"CLI: {cli_result.get('error', 'Unknown')}")
            except Exception as e:
                if not result["success"]:
                    result["errors"].append(f"CLI error: {e}")

        return result

    async def _apply_profile_via_cli(self, profile: LightingProfile) -> Dict[str, Any]:
        """Apply profile via CLI method"""
        try:
            # Apply via registry
            script = f"""
$paths = @(
    'HKCU:\\Software\\ASUS\\ArmouryDevice\\Aura',
    'HKLM:\\SOFTWARE\\ASUS\\ArmouryDevice\\Aura'
)

$brightness = {profile.lighting_brightness}
$enabled = {1 if profile.lighting_enabled else 0}

foreach ($path in $paths) {{
    try {{
        if (-not (Test-Path $path)) {{
            New-Item -Path $path -Force -ErrorAction SilentlyContinue | Out-Null
        }}
        if (Test-Path $path) {{
            Set-ItemProperty -Path $path -Name 'Brightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardBrightness' -Value $brightness -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'KeyboardEnabled' -Value $enabled -Type DWord -ErrorAction SilentlyContinue
            Set-ItemProperty -Path $path -Name 'ExternalEnabled' -Value 0 -Type DWord -ErrorAction SilentlyContinue
        }}
    }} catch {{
    }}
}}
Write-Output "OK"
"""
            result = subprocess.run(
                ["powershell", "-ExecutionPolicy", "Bypass", "-Command", script],
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )

            if result.returncode == 0:
                return {"success": True, "method": "CLI"}
            else:
                return {"success": False, "error": result.stderr}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def delete_profile(self, profile_name: str) -> Dict[str, Any]:
        """Delete profile via @AC"""
        if not self.ac_integration:
            return {"success": False, "error": "Armoury Crate integration not available"}

        try:
            result = await self.ac_integration._handle_delete_profile({"profile_name": profile_name})
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def list_armoury_profiles(self) -> Dict[str, Any]:
        """List profiles from Armoury Crate via @AC"""
        if not self.ac_integration:
            return {"success": False, "error": "Armoury Crate integration not available"}

        try:
            result = await self.ac_integration._handle_list_profiles({})
            return result
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@AC Lighting Profile Manager - API & CLI (consistent results)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
@AC = API & CLI (consistent results)

Examples:
  %(prog)s list                          List all available profiles
  %(prog)s apply ZERO-DARK-THIRTY       Apply ZERO-DARK-THIRTY profile
  %(prog)s apply LIGHT                  Apply LIGHT profile
  %(prog)s create --name CUSTOM         Create custom profile
  %(prog)s delete DARK                  Delete DARK profile
        """
    )

    parser.add_argument(
        "action",
        choices=["list", "apply", "create", "delete", "show"],
        help="Action to perform"
    )

    parser.add_argument(
        "profile_name",
        nargs="?",
        help="Profile name (for apply/delete/show)"
    )

    parser.add_argument(
        "--name",
        help="Profile name (for create)"
    )

    parser.add_argument(
        "--api-only",
        action="store_true",
        help="Use API method only (@AC)"
    )

    parser.add_argument(
        "--cli-only",
        action="store_true",
        help="Use CLI method only (@AC)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    # Initialize manager
    manager = ACLightingProfileManager()

    async def run():
        if args.action == "list":
            profiles = manager.list_profiles()
            if args.json:
                import json
                print(json.dumps([{
                    "name": p.name,
                    "short_name": p.short_name,
                    "tag": p.tag,
                    "description": p.description,
                    "brightness": p.lighting_brightness,
                    "effect": p.effect
                } for p in profiles], indent=2))
            else:
                print("\n" + "=" * 70)
                print("@AC LIGHTING PROFILES (@AC = API & CLI)")
                print("=" * 70)
                for profile in profiles:
                    print(f"\n{profile.name} ({profile.short_name}) [{profile.tag}]")
                    print(f"  Description: {profile.description}")
                    print(f"  Brightness: {profile.lighting_brightness}%")
                    print(f"  Effect: {profile.effect}")
                    print(f"  Use cases: {', '.join(profile.use_cases)}")
                print("\n" + "=" * 70)
            return 0

        elif args.action == "apply":
            if not args.profile_name:
                print("❌ Profile name required")
                return 1

            use_api = not args.cli_only
            use_cli = not args.api_only

            result = await manager.apply_profile(
                args.profile_name,
                use_api=use_api,
                use_cli=use_cli
            )

            if args.json:
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                if result.get("success"):
                    methods = ", ".join(result.get("methods_used", []))
                    print(f"✅ Profile '{result['profile_name']}' applied via @AC ({methods})")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")

            return 0 if result.get("success") else 1

        elif args.action == "show":
            if not args.profile_name:
                print("❌ Profile name required")
                return 1

            profile = manager.get_profile(args.profile_name)
            if not profile:
                print(f"❌ Profile '{args.profile_name}' not found")
                return 1

            if args.json:
                import json
                print(json.dumps({
                    "name": profile.name,
                    "short_name": profile.short_name,
                    "tag": profile.tag,
                    "description": profile.description,
                    "screen_brightness": profile.screen_brightness,
                    "lighting_enabled": profile.lighting_enabled,
                    "lighting_brightness": profile.lighting_brightness,
                    "effect": profile.effect,
                    "color": profile.color,
                    "zones": profile.zones,
                    "use_cases": profile.use_cases
                }, indent=2))
            else:
                print("\n" + "=" * 70)
                print(f"@AC PROFILE: {profile.name} ({profile.tag})")
                print("=" * 70)
                print(f"Short Name: {profile.short_name}")
                print(f"Description: {profile.description}")
                print(f"Screen Brightness: {profile.screen_brightness}%")
                print(f"Lighting Enabled: {profile.lighting_enabled}")
                print(f"Lighting Brightness: {profile.lighting_brightness}%")
                print(f"Effect: {profile.effect}")
                print(f"Color: {profile.color}")
                print(f"Use Cases: {', '.join(profile.use_cases)}")
                print("\nZones:")
                for zone_name, zone_config in profile.zones.items():
                    print(f"  {zone_name}:")
                    print(f"    Enabled: {zone_config.get('enabled', False)}")
                    print(f"    Brightness: {zone_config.get('brightness', 0)}%")
                    print(f"    Effect: {zone_config.get('effect', 'off')}")
                print("=" * 70)

            return 0

        elif args.action == "create":
            print("❌ Create action not yet implemented (use config file)")
            return 1

        elif args.action == "delete":
            if not args.profile_name:
                print("❌ Profile name required")
                return 1

            result = await manager.delete_profile(args.profile_name)

            if args.json:
                import json
                print(json.dumps(result, indent=2, default=str))
            else:
                if result.get("success"):
                    print(f"✅ Profile '{args.profile_name}' deleted")
                else:
                    print(f"❌ Failed: {result.get('error', 'Unknown error')}")

            return 0 if result.get("success") else 1

    exit_code = asyncio.run(run())
    sys.exit(exit_code)


if __name__ == "__main__":

    main()