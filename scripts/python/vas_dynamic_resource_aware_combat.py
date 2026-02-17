#!/usr/bin/env python3
"""
Dynamic Resource-Aware Combat Scaling System

Dynamically scales VA combat (Streetfighter/WoW Jedi battles, Force abilities,
Hero powers, Monster/Champion/Boss battles) based on system resources.

Scales combat intensity, frequency, and abilities based on:
- CPU usage
- Memory usage
- System load
- Available resources

Tags: #VAS #COMBAT #RESOURCE #SCALING #DYNAMIC #BALANCE @JARVIS @TEAM
"""

import sys
import psutil
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("VAsDynamicCombat")


class ResourceLevel(Enum):
    """System resource availability levels"""
    CRITICAL = "critical"  # < 20% resources available
    LOW = "low"  # 20-40% resources available
    MODERATE = "moderate"  # 40-60% resources available
    HIGH = "high"  # 60-80% resources available
    EXCELLENT = "excellent"  # > 80% resources available


class CombatTier(Enum):
    """Combat intensity tiers"""
    MINIMAL = "minimal"  # Minimal combat (low resources)
    LIGHT = "light"  # Light combat
    BALANCED = "balanced"  # Balanced combat (default)
    INTENSE = "intense"  # Intense combat
    EPIC = "epic"  # Epic combat (high resources)


@dataclass
class SystemResources:
    """Current system resource state"""
    cpu_percent: float
    memory_percent: float
    cpu_available: float  # 100 - cpu_percent
    memory_available: float  # 100 - memory_percent
    load_average: float = 0.0  # System load average (Unix)
    resource_level: ResourceLevel = ResourceLevel.MODERATE
    timestamp: float = field(default_factory=time.time)


@dataclass
class CombatScaling:
    """Combat scaling parameters based on resources"""
    tier: CombatTier
    fight_frequency_multiplier: float  # 0.0 to 2.0
    damage_multiplier: float  # 0.5 to 2.0
    ability_frequency_multiplier: float  # 0.0 to 2.0
    animation_speed_multiplier: float  # 0.5 to 2.0
    special_ability_enabled: bool
    boss_battle_enabled: bool
    epic_effects_enabled: bool


class VAsDynamicResourceAwareCombat:
    """
    Dynamic Resource-Aware Combat Scaling System

    Monitors system resources and scales combat intensity accordingly.
    """

    def __init__(self, project_root: Optional[Path] = None):
        """Initialize resource-aware combat system"""
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent

        self.project_root = Path(project_root)
        self.data_dir = self.project_root / "data" / "vas_combat_scaling"
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Resource monitoring
        self.resource_check_interval = 5.0  # Check resources every 5 seconds
        self.last_resource_check = 0.0
        self.current_resources: Optional[SystemResources] = None
        self.current_scaling: Optional[CombatScaling] = None

        # Resource thresholds
        self.cpu_thresholds = {
            ResourceLevel.CRITICAL: 80.0,  # > 80% CPU = critical
            ResourceLevel.LOW: 60.0,  # > 60% CPU = low
            ResourceLevel.MODERATE: 40.0,  # > 40% CPU = moderate
            ResourceLevel.HIGH: 20.0,  # > 20% CPU = high
            ResourceLevel.EXCELLENT: 0.0  # < 20% CPU = excellent
        }

        self.memory_thresholds = {
            ResourceLevel.CRITICAL: 85.0,  # > 85% memory = critical
            ResourceLevel.LOW: 70.0,  # > 70% memory = low
            ResourceLevel.MODERATE: 50.0,  # > 50% memory = moderate
            ResourceLevel.HIGH: 30.0,  # > 30% memory = high
            ResourceLevel.EXCELLENT: 0.0  # < 30% memory = excellent
        }

        logger.info("✅ Dynamic Resource-Aware Combat System initialized")

    def get_system_resources(self) -> SystemResources:
        """Get current system resource state"""
        try:
            cpu_percent = psutil.cpu_percent(interval=0.1)
            memory = psutil.virtual_memory()
            memory_percent = memory.percent

            cpu_available = 100.0 - cpu_percent
            memory_available = 100.0 - memory_percent

            # Get load average (Unix) or approximate (Windows)
            try:
                load_avg = psutil.getloadavg()[0] if hasattr(psutil, 'getloadavg') else 0.0
            except:
                load_avg = cpu_percent / 100.0  # Approximate load from CPU

            # Determine resource level (use worst of CPU or memory)
            resource_level = self._determine_resource_level(cpu_percent, memory_percent)

            return SystemResources(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                cpu_available=cpu_available,
                memory_available=memory_available,
                load_average=load_avg,
                resource_level=resource_level,
                timestamp=time.time()
            )
        except Exception as e:
            logger.error(f"Error getting system resources: {e}")
            # Return safe defaults
            return SystemResources(
                cpu_percent=50.0,
                memory_percent=50.0,
                cpu_available=50.0,
                memory_available=50.0,
                resource_level=ResourceLevel.MODERATE,
                timestamp=time.time()
            )

    def _determine_resource_level(self, cpu_percent: float, memory_percent: float) -> ResourceLevel:
        """Determine resource level based on CPU and memory"""
        # Use worst of CPU or memory
        worst_metric = max(cpu_percent, memory_percent)

        if worst_metric >= self.cpu_thresholds[ResourceLevel.CRITICAL]:
            return ResourceLevel.CRITICAL
        elif worst_metric >= self.cpu_thresholds[ResourceLevel.LOW]:
            return ResourceLevel.LOW
        elif worst_metric >= self.cpu_thresholds[ResourceLevel.MODERATE]:
            return ResourceLevel.MODERATE
        elif worst_metric >= self.cpu_thresholds[ResourceLevel.HIGH]:
            return ResourceLevel.HIGH
        else:
            return ResourceLevel.EXCELLENT

    def calculate_combat_scaling(self, resources: SystemResources) -> CombatScaling:
        """
        Calculate combat scaling based on system resources

        Scales:
        - Fight frequency (how often fights occur)
        - Damage (combat intensity)
        - Ability frequency (Force abilities, Hero powers)
        - Animation speed
        - Special abilities (enabled/disabled)
        - Boss battles (enabled/disabled)
        - Epic effects (enabled/disabled)
        """
        level = resources.resource_level

        if level == ResourceLevel.CRITICAL:
            # Minimal combat - system under heavy load
            return CombatScaling(
                tier=CombatTier.MINIMAL,
                fight_frequency_multiplier=0.1,  # 10% of normal frequency
                damage_multiplier=0.5,  # 50% damage
                ability_frequency_multiplier=0.0,  # No special abilities
                animation_speed_multiplier=0.5,  # Slower animations
                special_ability_enabled=False,
                boss_battle_enabled=False,
                epic_effects_enabled=False
            )

        elif level == ResourceLevel.LOW:
            # Light combat - conserve resources
            return CombatScaling(
                tier=CombatTier.LIGHT,
                fight_frequency_multiplier=0.3,  # 30% of normal frequency
                damage_multiplier=0.7,  # 70% damage
                ability_frequency_multiplier=0.2,  # 20% ability frequency
                animation_speed_multiplier=0.7,  # Slightly slower
                special_ability_enabled=False,
                boss_battle_enabled=False,
                epic_effects_enabled=False
            )

        elif level == ResourceLevel.MODERATE:
            # Balanced combat - default behavior
            return CombatScaling(
                tier=CombatTier.BALANCED,
                fight_frequency_multiplier=1.0,  # Normal frequency
                damage_multiplier=1.0,  # Normal damage
                ability_frequency_multiplier=1.0,  # Normal ability frequency
                animation_speed_multiplier=1.0,  # Normal speed
                special_ability_enabled=True,
                boss_battle_enabled=True,
                epic_effects_enabled=False
            )

        elif level == ResourceLevel.HIGH:
            # Intense combat - system has resources
            return CombatScaling(
                tier=CombatTier.INTENSE,
                fight_frequency_multiplier=1.5,  # 150% frequency
                damage_multiplier=1.3,  # 130% damage
                ability_frequency_multiplier=1.5,  # 150% ability frequency
                animation_speed_multiplier=1.2,  # Faster animations
                special_ability_enabled=True,
                boss_battle_enabled=True,
                epic_effects_enabled=True
            )

        else:  # EXCELLENT
            # Epic combat - system has plenty of resources
            return CombatScaling(
                tier=CombatTier.EPIC,
                fight_frequency_multiplier=2.0,  # 200% frequency (max)
                damage_multiplier=1.5,  # 150% damage (max)
                ability_frequency_multiplier=2.0,  # 200% ability frequency (max)
                animation_speed_multiplier=1.5,  # Much faster animations
                special_ability_enabled=True,
                boss_battle_enabled=True,
                epic_effects_enabled=True
            )

    def get_current_scaling(self) -> CombatScaling:
        """Get current combat scaling (checks resources if needed)"""
        now = time.time()

        # Check resources if needed
        if (now - self.last_resource_check) >= self.resource_check_interval or self.current_resources is None:
            self.current_resources = self.get_system_resources()
            self.current_scaling = self.calculate_combat_scaling(self.current_resources)
            self.last_resource_check = now

            logger.debug(f"📊 Resources: CPU={self.current_resources.cpu_percent:.1f}%, "
                        f"Memory={self.current_resources.memory_percent:.1f}%, "
                        f"Level={self.current_resources.resource_level.value}, "
                        f"Tier={self.current_scaling.tier.value}")

        return self.current_scaling

    def apply_scaling_to_imva(self) -> Dict[str, Any]:
        """
        Apply combat scaling to IMVA configuration

        Returns scaling parameters to apply to IMVA
        """
        scaling = self.get_current_scaling()
        resources = self.current_resources

        # Calculate adjusted values
        base_fight_probability = 0.12  # Base 12% (from user's changes)
        base_fight_check_interval = 20.0  # Base 20 seconds (from user's changes)
        base_min_fight_duration = 12.0  # Base 12 seconds (from user's changes)
        base_damage_multiplier = 1.0  # Base damage multiplier

        # Apply scaling
        adjusted_fight_probability = base_fight_probability * scaling.fight_frequency_multiplier
        adjusted_fight_check_interval = base_fight_check_interval / max(scaling.fight_frequency_multiplier, 0.1)
        adjusted_min_fight_duration = base_min_fight_duration * (1.0 / max(scaling.animation_speed_multiplier, 0.5))
        adjusted_damage_multiplier = base_damage_multiplier * scaling.damage_multiplier

        # Cap values
        adjusted_fight_probability = min(adjusted_fight_probability, 0.5)  # Max 50% chance
        adjusted_fight_check_interval = max(adjusted_fight_check_interval, 5.0)  # Min 5 seconds
        adjusted_min_fight_duration = max(adjusted_min_fight_duration, 5.0)  # Min 5 seconds

        return {
            "fight_probability": adjusted_fight_probability,
            "fight_check_interval": adjusted_fight_check_interval,
            "min_fight_duration": adjusted_min_fight_duration,
            "damage_multiplier": adjusted_damage_multiplier,
            "ability_frequency_multiplier": scaling.ability_frequency_multiplier,
            "animation_speed_multiplier": scaling.animation_speed_multiplier,
            "special_ability_enabled": scaling.special_ability_enabled,
            "boss_battle_enabled": scaling.boss_battle_enabled,
            "epic_effects_enabled": scaling.epic_effects_enabled,
            "resource_level": resources.resource_level.value if resources else "unknown",
            "tier": scaling.tier.value,
            "cpu_percent": resources.cpu_percent if resources else 0.0,
            "memory_percent": resources.memory_percent if resources else 0.0
        }

    def get_combat_status(self) -> Dict[str, Any]:
        """Get current combat scaling status"""
        resources = self.get_system_resources()
        scaling = self.calculate_combat_scaling(resources)
        imva_scaling = self.apply_scaling_to_imva()

        return {
            "timestamp": time.time(),
            "resources": {
                "cpu_percent": resources.cpu_percent,
                "memory_percent": resources.memory_percent,
                "cpu_available": resources.cpu_available,
                "memory_available": resources.memory_available,
                "load_average": resources.load_average,
                "resource_level": resources.resource_level.value
            },
            "combat_scaling": {
                "tier": scaling.tier.value,
                "fight_frequency_multiplier": scaling.fight_frequency_multiplier,
                "damage_multiplier": scaling.damage_multiplier,
                "ability_frequency_multiplier": scaling.ability_frequency_multiplier,
                "animation_speed_multiplier": scaling.animation_speed_multiplier,
                "special_ability_enabled": scaling.special_ability_enabled,
                "boss_battle_enabled": scaling.boss_battle_enabled,
                "epic_effects_enabled": scaling.epic_effects_enabled
            },
            "imva_adjusted_values": imva_scaling
        }


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Dynamic Resource-Aware Combat Scaling")
    parser.add_argument("--status", action="store_true", help="Show current combat scaling status")
    parser.add_argument("--monitor", action="store_true", help="Monitor and display resource-aware scaling")
    parser.add_argument("--interval", type=float, default=5.0, help="Monitoring interval (seconds)")

    args = parser.parse_args()

    print("\n" + "="*80)
    print("⚔️  Dynamic Resource-Aware Combat Scaling System")
    print("="*80 + "\n")

    combat_system = VAsDynamicResourceAwareCombat()

    if args.monitor:
        print("📊 Monitoring system resources and combat scaling...")
        print("   (Press Ctrl+C to stop)\n")
        try:
            while True:
                status = combat_system.get_combat_status()
                resources = status["resources"]
                scaling = status["combat_scaling"]
                imva = status["imva_adjusted_values"]

                print(f"📊 Resources: CPU={resources['cpu_percent']:.1f}% | "
                      f"Memory={resources['memory_percent']:.1f}% | "
                      f"Level={resources['resource_level'].upper()}")
                print(f"⚔️  Combat Tier: {scaling['tier'].upper()}")
                print(f"   Fight Frequency: {scaling['fight_frequency_multiplier']:.2f}x | "
                      f"Damage: {scaling['damage_multiplier']:.2f}x | "
                      f"Abilities: {scaling['ability_frequency_multiplier']:.2f}x")
                print(f"🎮 IMVA Adjusted: "
                      f"Fight Prob={imva['fight_probability']:.3f} | "
                      f"Check Interval={imva['fight_check_interval']:.1f}s | "
                      f"Min Duration={imva['min_fight_duration']:.1f}s")
                print()

                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n✅ Monitoring stopped")

    elif args.status:
        status = combat_system.get_combat_status()
        print(json.dumps(status, indent=2, default=str))

    else:
        # Default: show current status
        status = combat_system.get_combat_status()
        resources = status["resources"]
        scaling = status["combat_scaling"]
        imva = status["imva_adjusted_values"]

        print("📊 CURRENT SYSTEM RESOURCES")
        print("="*80)
        print(f"CPU Usage: {resources['cpu_percent']:.1f}% (Available: {resources['cpu_available']:.1f}%)")
        print(f"Memory Usage: {resources['memory_percent']:.1f}% (Available: {resources['memory_available']:.1f}%)")
        print(f"Load Average: {resources['load_average']:.2f}")
        print(f"Resource Level: {resources['resource_level'].upper()}")
        print()

        print("⚔️  COMBAT SCALING")
        print("="*80)
        print(f"Tier: {scaling['tier'].upper()}")
        print(f"Fight Frequency Multiplier: {scaling['fight_frequency_multiplier']:.2f}x")
        print(f"Damage Multiplier: {scaling['damage_multiplier']:.2f}x")
        print(f"Ability Frequency Multiplier: {scaling['ability_frequency_multiplier']:.2f}x")
        print(f"Animation Speed Multiplier: {scaling['animation_speed_multiplier']:.2f}x")
        print(f"Special Abilities: {'✅ Enabled' if scaling['special_ability_enabled'] else '❌ Disabled'}")
        print(f"Boss Battles: {'✅ Enabled' if scaling['boss_battle_enabled'] else '❌ Disabled'}")
        print(f"Epic Effects: {'✅ Enabled' if scaling['epic_effects_enabled'] else '❌ Disabled'}")
        print()

        print("🎮 IMVA ADJUSTED VALUES")
        print("="*80)
        print(f"Fight Probability: {imva['fight_probability']:.3f} ({imva['fight_probability']*100:.1f}%)")
        print(f"Fight Check Interval: {imva['fight_check_interval']:.1f} seconds")
        print(f"Min Fight Duration: {imva['min_fight_duration']:.1f} seconds")
        print(f"Damage Multiplier: {imva['damage_multiplier']:.2f}x")
        print()

        print("💡 Use --monitor to continuously monitor resources")
        print("="*80 + "\n")
