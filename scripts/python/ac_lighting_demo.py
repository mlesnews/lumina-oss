#!/usr/bin/env python3
"""
@AC Lighting Demo
=================
Showcases all lighting effects and profiles for marketing/branding.

Features:
- Cycles through all available lighting effects
- Demonstrates all profiles
- Custom branding effects
- Marketing-ready presentation mode

@AC @ARMOURY_CRATE @LIGHTING @DEMO @MARKETING @BRANDING
"""

import sys
import asyncio
import time
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# Project setup
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "src"))

try:
    from lumina_unified_logger import LuminaUnifiedLogger
    logger = LuminaUnifiedLogger("System", "ACLightingDemo")
    _logger = logger.get_logger()
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    _logger = logging.getLogger("ACLightingDemo")


class ACLightingDemo:
    """
    @AC Lighting Demo

    Showcases all lighting effects and profiles.
    Perfect for marketing, branding, and demonstrations.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize @AC lighting demo"""
        self.project_root = project_root or PROJECT_ROOT
        self.logger = _logger

        # Initialize profile manager
        try:
            from ac_lighting_profile_manager import ACLightingProfileManager
            self.profile_manager = ACLightingProfileManager(project_root=self.project_root)
        except ImportError as e:
            self.logger.error(f"Failed to import profile manager: {e}")
            self.profile_manager = None

        # Demo configuration
        self.effect_duration_seconds = 3  # How long to show each effect
        self.profile_duration_seconds = 5  # How long to show each profile
        self.transition_delay_seconds = 0.5  # Delay between transitions

        self.logger.info("✅ @AC Lighting Demo initialized")

    async def demo_all_effects(self) -> Dict[str, Any]:
        """
        Demo all available lighting effects

        Cycles through: static, breathing, rainbow, wave, strobe, comet
        """
        self.logger.info("=" * 70)
        self.logger.info("@AC LIGHTING DEMO - ALL EFFECTS")
        self.logger.info("=" * 70)
        self.logger.info("")

        effects = [
            {"name": "Static", "description": "Solid color, no animation"},
            {"name": "Breathing", "description": "Pulsing brightness effect"},
            {"name": "Rainbow", "description": "Color cycling rainbow effect"},
            {"name": "Wave", "description": "Wave animation across zones"},
            {"name": "Strobe", "description": "Rapid flashing effect"},
            {"name": "Comet", "description": "Comet trail effect"},
        ]

        results = []

        for i, effect in enumerate(effects, 1):
            self.logger.info(f"[{i}/{len(effects)}] Demonstrating: {effect['name']}")
            self.logger.info(f"   {effect['description']}")

            # Apply effect via profile manager
            if self.profile_manager and self.profile_manager.ac_integration:
                try:
                    # Create temporary demo profile with this effect
                    demo_result = await self._apply_effect_demo(effect["name"].lower())
                    results.append({
                        "effect": effect["name"],
                        "success": demo_result.get("success", False)
                    })

                    if demo_result.get("success"):
                        self.logger.info(f"   ✅ {effect['name']} effect applied")
                    else:
                        self.logger.warning(f"   ⚠️  {effect['name']} effect had issues")
                except Exception as e:
                    self.logger.error(f"   ❌ {effect['name']} effect failed: {e}")
                    results.append({
                        "effect": effect["name"],
                        "success": False,
                        "error": str(e)
                    })

            # Wait before next effect
            if i < len(effects):
                self.logger.info(f"   Waiting {self.effect_duration_seconds}s before next effect...")
                await asyncio.sleep(self.effect_duration_seconds)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("EFFECTS DEMO COMPLETE")
        self.logger.info("=" * 70)

        return {
            "success": all(r.get("success", False) for r in results),
            "effects_demoed": len(results),
            "results": results
        }

    async def demo_all_profiles(self) -> Dict[str, Any]:
        """
        Demo all available lighting profiles

        Shows: ZERO-DARK-THIRTY, DARK, LIGHT, GAMING, FOCUS, BRANDING, DEMO
        """
        self.logger.info("=" * 70)
        self.logger.info("@AC LIGHTING DEMO - ALL PROFILES")
        self.logger.info("=" * 70)
        self.logger.info("")

        if not self.profile_manager:
            return {"success": False, "error": "Profile manager not available"}

        profiles = self.profile_manager.list_profiles()
        results = []

        for i, profile in enumerate(profiles, 1):
            self.logger.info(f"[{i}/{len(profiles)}] Demonstrating: {profile.name} ({profile.tag})")
            self.logger.info(f"   {profile.description}")
            self.logger.info(f"   Brightness: {profile.lighting_brightness}%, Effect: {profile.effect}")

            # Apply profile
            try:
                apply_result = await self.profile_manager.apply_profile(
                    profile.name,
                    use_api=True,
                    use_cli=True
                )

                if apply_result.get("success"):
                    methods = ", ".join(apply_result.get("methods_used", []))
                    self.logger.info(f"   ✅ Profile applied via @AC ({methods})")
                    results.append({
                        "profile": profile.name,
                        "success": True,
                        "methods": apply_result.get("methods_used", [])
                    })
                else:
                    self.logger.warning(f"   ⚠️  Profile application had issues")
                    results.append({
                        "profile": profile.name,
                        "success": False,
                        "error": apply_result.get("error", "Unknown")
                    })
            except Exception as e:
                self.logger.error(f"   ❌ Profile failed: {e}")
                results.append({
                    "profile": profile.name,
                    "success": False,
                    "error": str(e)
                })

            # Wait before next profile
            if i < len(profiles):
                self.logger.info(f"   Waiting {self.profile_duration_seconds}s before next profile...")
                await asyncio.sleep(self.profile_duration_seconds)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("PROFILES DEMO COMPLETE")
        self.logger.info("=" * 70)

        return {
            "success": all(r.get("success", False) for r in results),
            "profiles_demoed": len(results),
            "results": results
        }

    async def demo_branding_effects(self) -> Dict[str, Any]:
        """
        Demo custom branding effects

        Shows Lumina/<COMPANY> branding colors and effects
        """
        self.logger.info("=" * 70)
        self.logger.info("@AC LIGHTING DEMO - BRANDING EFFECTS")
        self.logger.info("=" * 70)
        self.logger.info("")

        branding_effects = [
            {
                "name": "Lumina Blue",
                "color": "#00a8ff",
                "effect": "breathing",
                "description": "Lumina brand color - breathing effect"
            },
            {
                "name": "<COMPANY> Green",
                "color": "#00ff88",
                "effect": "wave",
                "description": "<COMPANY> brand color - wave effect"
            },
            {
                "name": "Brand Rainbow",
                "color": "#ffffff",
                "effect": "rainbow",
                "description": "Full spectrum branding showcase"
            },
            {
                "name": "Brand Pulse",
                "color": "#00a8ff",
                "effect": "breathing",
                "description": "Pulsing brand identity"
            }
        ]

        results = []

        for i, effect in enumerate(branding_effects, 1):
            self.logger.info(f"[{i}/{len(branding_effects)}] {effect['name']}")
            self.logger.info(f"   {effect['description']}")
            self.logger.info(f"   Color: {effect['color']}, Effect: {effect['effect']}")

            # Apply branding effect
            try:
                demo_result = await self._apply_branding_effect(effect)
                if demo_result.get("success"):
                    self.logger.info(f"   ✅ {effect['name']} applied")
                    results.append({"effect": effect["name"], "success": True})
                else:
                    self.logger.warning(f"   ⚠️  {effect['name']} had issues")
                    results.append({"effect": effect["name"], "success": False})
            except Exception as e:
                self.logger.error(f"   ❌ {effect['name']} failed: {e}")
                results.append({"effect": effect["name"], "success": False, "error": str(e)})

            # Wait before next effect
            if i < len(branding_effects):
                await asyncio.sleep(self.effect_duration_seconds)

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("BRANDING DEMO COMPLETE")
        self.logger.info("=" * 70)

        return {
            "success": all(r.get("success", False) for r in results),
            "branding_effects_demoed": len(results),
            "results": results
        }

    async def full_demo(self) -> Dict[str, Any]:
        """
        Full demo - showcases everything

        Sequence:
        1. All effects
        2. All profiles
        3. Branding effects
        """
        self.logger.info("=" * 70)
        self.logger.info("@AC LIGHTING - FULL DEMO SHOWCASE")
        self.logger.info("Perfect for marketing, branding, and demonstrations")
        self.logger.info("=" * 70)
        self.logger.info("")

        results = {
            "effects": None,
            "profiles": None,
            "branding": None,
            "total_duration_seconds": 0
        }

        start_time = datetime.now()

        # Part 1: Effects
        self.logger.info("PART 1: ALL EFFECTS")
        self.logger.info("-" * 70)
        results["effects"] = await self.demo_all_effects()
        await asyncio.sleep(self.transition_delay_seconds)

        # Part 2: Profiles
        self.logger.info("")
        self.logger.info("PART 2: ALL PROFILES")
        self.logger.info("-" * 70)
        results["profiles"] = await self.demo_all_profiles()
        await asyncio.sleep(self.transition_delay_seconds)

        # Part 3: Branding
        self.logger.info("")
        self.logger.info("PART 3: BRANDING EFFECTS")
        self.logger.info("-" * 70)
        results["branding"] = await self.demo_branding_effects()

        # Summary
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        results["total_duration_seconds"] = duration

        self.logger.info("")
        self.logger.info("=" * 70)
        self.logger.info("FULL DEMO COMPLETE")
        self.logger.info("=" * 70)
        self.logger.info(f"Total duration: {duration:.1f} seconds")
        self.logger.info(f"Effects demoed: {results['effects'].get('effects_demoed', 0) if results['effects'] else 0}")
        self.logger.info(f"Profiles demoed: {results['profiles'].get('profiles_demoed', 0) if results['profiles'] else 0}")
        self.logger.info(f"Branding effects demoed: {results['branding'].get('branding_effects_demoed', 0) if results['branding'] else 0}")
        self.logger.info("=" * 70)

        results["success"] = (
            (results["effects"] and results["effects"].get("success", False)) and
            (results["profiles"] and results["profiles"].get("success", False)) and
            (results["branding"] and results["branding"].get("success", False))
        )

        return results

    async def _apply_effect_demo(self, effect_name: str) -> Dict[str, Any]:
        """Apply a specific effect for demo"""
        if not self.profile_manager or not self.profile_manager.ac_integration:
            return {"success": False, "error": "Integration not available"}

        try:
            # Use DEMO profile and modify effect
            demo_profile = self.profile_manager.get_profile("DEMO")
            if demo_profile:
                # Temporarily modify effect
                original_effect = demo_profile.effect
                demo_profile.effect = effect_name

                result = await self.profile_manager.apply_profile("DEMO")

                # Restore original
                demo_profile.effect = original_effect

                return result
            else:
                return {"success": False, "error": "DEMO profile not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def _apply_branding_effect(self, effect_config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply branding effect"""
        if not self.profile_manager or not self.profile_manager.ac_integration:
            return {"success": False, "error": "Integration not available"}

        try:
            # Use BRANDING profile
            branding_profile = self.profile_manager.get_profile("BRANDING")
            if branding_profile:
                # Temporarily modify for this specific branding effect
                original_color = branding_profile.color
                original_effect = branding_profile.effect

                branding_profile.color = effect_config["color"]
                branding_profile.effect = effect_config["effect"]

                result = await self.profile_manager.apply_profile("BRANDING")

                # Restore original
                branding_profile.color = original_color
                branding_profile.effect = original_effect

                return result
            else:
                return {"success": False, "error": "BRANDING profile not found"}
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """CLI entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="@AC Lighting Demo - Showcase all effects and profiles",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
@AC = API & CLI (consistent results)

Examples:
  %(prog)s effects              Demo all lighting effects
  %(prog)s profiles            Demo all lighting profiles
  %(prog)s branding            Demo branding effects
  %(prog)s full                Full demo (all effects + profiles + branding)
        """
    )

    parser.add_argument(
        "demo_type",
        choices=["effects", "profiles", "branding", "full"],
        help="Type of demo to run"
    )

    parser.add_argument(
        "--duration",
        type=int,
        help="Duration per effect/profile in seconds (default: 3 for effects, 5 for profiles)"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    # Initialize demo
    demo = ACLightingDemo()

    if args.duration:
        demo.effect_duration_seconds = args.duration
        demo.profile_duration_seconds = args.duration

    async def run():
        if args.demo_type == "effects":
            result = await demo.demo_all_effects()
        elif args.demo_type == "profiles":
            result = await demo.demo_all_profiles()
        elif args.demo_type == "branding":
            result = await demo.demo_branding_effects()
        elif args.demo_type == "full":
            result = await demo.full_demo()
        else:
            result = {"success": False, "error": "Unknown demo type"}

        if args.json:
            import json
            print(json.dumps(result, indent=2, default=str))
        else:
            if result.get("success"):
                print("\n✅ Demo completed successfully")
            else:
                print(f"\n❌ Demo had issues: {result.get('error', 'Unknown')}")

        return 0 if result.get("success") else 1

    exit_code = asyncio.run(run())
    sys.exit(exit_code)


if __name__ == "__main__":

    main()