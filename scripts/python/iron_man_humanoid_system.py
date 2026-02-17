#!/usr/bin/env python3
"""
Iron Man Humanoid System - Full Body Avatars

Enhanced Iron Man avatar system with full humanoid forms (not just bobbleheads).
Includes comprehensive action phases, Android JARVIS mobile demo quality detail,
and random action stages similar to ACE.

Tags: #IRON_MAN #HUMANOID #FULL_BODY #ACTION_PHASES #ANDROID_JARVIS @JARVIS @LUMINA
"""

import sys
import math
import random
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    import logging
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IronManHumanoid")


class IronManActionPhase(Enum):
    """Comprehensive action phases for Iron Man avatars"""
    IDLE = "IDLE"  # Standing still, relaxed
    WALKING = "WALKING"  # Walking animation
    RUNNING = "RUNNING"  # Running animation
    FLYING = "FLYING"  # Flying/hovering
    COMBAT = "COMBAT"  # Fighting/combat stance
    THINKING = "THINKING"  # Processing/analyzing
    TALKING = "TALKING"  # Speaking/communicating
    POWER_UP = "POWER_UP"  # Charging up
    COOLING = "COOLING"  # Cooling down after action
    TRANSFORMING = "TRANSFORMING"  # Transforming between forms
    REPULSOR_CHARGE = "REPULSOR_CHARGE"  # Charging repulsors
    REPULSOR_FIRE = "REPULSOR_FIRE"  # Firing repulsors
    UNIBEAM_CHARGE = "UNIBEAM_CHARGE"  # Charging unibeam
    UNIBEAM_FIRE = "UNIBEAM_FIRE"  # Firing unibeam
    LANDING = "LANDING"  # Landing from flight
    TAKE_OFF = "TAKE_OFF"  # Taking off to fly
    DEFENSIVE_STANCE = "DEFENSIVE_STANCE"  # Defensive posture
    VICTORY = "VICTORY"  # Victory pose
    DAMAGED = "DAMAGED"  # Taking damage


@dataclass
class IronManPose:
    """Pose data for action phases"""
    phase: IronManActionPhase
    arm_left_angle: float  # Left arm angle in degrees
    arm_right_angle: float  # Right arm angle in degrees
    leg_left_angle: float  # Left leg angle in degrees
    leg_right_angle: float  # Right leg angle in degrees
    body_lean: float  # Body lean angle
    head_tilt: float  # Head tilt angle
    repulsor_charge: float  # Repulsor charge level (0.0 to 1.0)
    animation_frame: int  # Current animation frame
    animation_speed: float  # Animation speed multiplier


class IronManHumanoidRenderer:
    """Enhanced Iron Man humanoid renderer with Android JARVIS mobile demo quality"""

    def __init__(self, persona_colors: Dict[str, str]):
        """
        Initialize renderer

        Args:
            persona_colors: Dict with 'primary', 'secondary', 'glow', 'outline', 'energy'
        """
        self.persona_colors = persona_colors
        self.detail_level = "high"  # high, medium, low (Android JARVIS = high)

        # Enhanced detail layers - Android JARVIS Mobile Demo Quality
        # Additional levels/layers matching Android JARVIS mobile demo
        self.layers = {
            "base": True,  # Base suit structure
            "plating": True,  # Armor plating details (Android JARVIS quality)
            "joints": True,  # Joint articulation (Android JARVIS quality)
            "reactor": True,  # Arc reactor details (Android JARVIS quality)
            "repulsors": True,  # Hand repulsors (Android JARVIS quality)
            "unibeam": True,  # Chest unibeam (Android JARVIS quality)
            "glow": True,  # Energy glow effects (Android JARVIS quality)
            "particles": True,  # Particle effects (Android JARVIS quality)
            "shadows": True,  # Shadow details (Android JARVIS quality)
            "reflections": True,  # Surface reflections (Android JARVIS quality)
            "damage": True,  # Damage indicators (Android JARVIS quality)
            "hud_overlay": True,  # HUD overlay elements (Android JARVIS quality)
            "texture": True,  # Surface texture details (Android JARVIS quality)
            "lighting": True,  # Dynamic lighting (Android JARVIS quality)
            "motion_blur": True,  # Motion blur effects (Android JARVIS quality)
            "depth": True,  # Depth of field effects (Android JARVIS quality)
            "anisotropic": True,  # Anisotropic filtering (Android JARVIS quality)
            "anti_aliasing": True,  # Anti-aliasing (Android JARVIS quality)
            "normal_mapping": True,  # Normal mapping (Android JARVIS quality)
            "specular": True,  # Specular highlights (Android JARVIS quality)
            "ambient_occlusion": True  # Ambient occlusion (Android JARVIS quality)
        }

    def draw_humanoid(self, canvas, cx: float, cy: float, scale: float,
                     pose: IronManPose, combat_mode: bool = False,
                     detail_level: str = "high") -> None:
        """
        Draw full Iron Man humanoid with enhanced detail

        Args:
            canvas: Tkinter canvas
            cx: Center X
            cy: Center Y
            scale: Scale factor
            pose: Current pose data
            combat_mode: Whether in combat
            detail_level: Detail level (high/medium/low)
        """
        self.detail_level = detail_level
        s = scale
        p = self.persona_colors

        # Convert angles to radians
        arm_l_rad = math.radians(pose.arm_left_angle)
        arm_r_rad = math.radians(pose.arm_right_angle)
        leg_l_rad = math.radians(pose.leg_left_angle)
        leg_r_rad = math.radians(pose.leg_right_angle)
        body_lean_rad = math.radians(pose.body_lean)
        head_tilt_rad = math.radians(pose.head_tilt)

        # Base body position (with lean)
        body_cx = cx + math.sin(body_lean_rad) * 5 * s
        body_cy = cy + math.cos(body_lean_rad) * 5 * s

        # Draw shadow first (if enabled)
        if self.layers["shadows"] and detail_level in ["high", "medium"]:
            self._draw_shadow(canvas, body_cx, body_cy, s, pose)

        # Draw base suit structure
        if self.layers["base"]:
            self._draw_base_suit(canvas, body_cx, body_cy, s, pose, p, combat_mode)

        # Draw armor plating details
        if self.layers["plating"] and detail_level == "high":
            self._draw_armor_plating(canvas, body_cx, body_cy, s, pose, p)

        # Draw joints
        if self.layers["joints"] and detail_level == "high":
            self._draw_joints(canvas, body_cx, body_cy, s, pose, p)

        # Draw arc reactor
        if self.layers["reactor"]:
            self._draw_arc_reactor(canvas, body_cx, body_cy, s, pose, p, combat_mode)

        # Draw repulsors
        if self.layers["repulsors"]:
            self._draw_repulsors(canvas, body_cx, body_cy, s, pose, p, combat_mode)

        # Draw unibeam
        if self.layers["unibeam"] and pose.phase in [IronManActionPhase.UNIBEAM_CHARGE, IronManActionPhase.UNIBEAM_FIRE]:
            self._draw_unibeam(canvas, body_cx, body_cy, s, pose, p)

        # Draw energy glow
        if self.layers["glow"]:
            self._draw_energy_glow(canvas, body_cx, body_cy, s, pose, p, combat_mode)

        # Draw particle effects
        if self.layers["particles"] and detail_level == "high":
            self._draw_particles(canvas, body_cx, body_cy, s, pose, p, combat_mode)

        # Draw reflections
        if self.layers["reflections"] and detail_level == "high":
            self._draw_reflections(canvas, body_cx, body_cy, s, pose, p)

        # Draw damage indicators
        if self.layers["damage"] and pose.phase == IronManActionPhase.DAMAGED:
            self._draw_damage(canvas, body_cx, body_cy, s, pose, p)

        # Draw HUD overlay
        if self.layers["hud_overlay"] and detail_level == "high":
            self._draw_hud_overlay(canvas, body_cx, body_cy, s, pose, p)

    def _draw_shadow(self, canvas, cx: float, cy: float, s: float, pose: IronManPose):
        """Draw shadow beneath avatar"""
        shadow_y = cy + 120 * s
        shadow_width = 60 * s
        shadow_height = 15 * s

        canvas.create_oval(
            cx - shadow_width, shadow_y - shadow_height,
            cx + shadow_width, shadow_y + shadow_height,
            fill="#000000", outline="", stipple="gray25",
            tags="iron_man_humanoid"
        )

    def _draw_base_suit(self, canvas, cx: float, cy: float, s: float,
                       pose: IronManPose, colors: Dict[str, str], combat: bool):
        """Draw base suit structure"""
        # Head/Helmet
        head_y = cy - 80 * s
        head_radius = 40 * s

        # Helmet
        canvas.create_arc(
            cx - head_radius, head_y - head_radius * 0.8,
            cx + head_radius, head_y + head_radius * 0.3,
            start=0, extent=180,
            fill=colors["primary"], outline=colors["outline"], width=2,
            tags="iron_man_humanoid"
        )

        # Faceplate
        faceplate_y = head_y + 10 * s
        canvas.create_polygon(
            cx - 35 * s, faceplate_y - 20 * s,
            cx + 35 * s, faceplate_y - 20 * s,
            cx + 40 * s, faceplate_y + 10 * s,
            cx - 40 * s, faceplate_y + 10 * s,
            fill=colors["secondary"], outline=colors["primary"], width=2,
            tags="iron_man_humanoid"
        )

        # Eyes
        eye_color = colors["glow"] if combat else colors["primary"]
        eye_y = head_y + 5 * s

        # Left eye
        canvas.create_polygon(
            cx - 30 * s, eye_y,
            cx - 12 * s, eye_y,
            cx - 8 * s, eye_y - 8 * s,
            cx - 26 * s, eye_y - 8 * s,
            fill=eye_color, outline=colors["outline"], width=2,
            tags="iron_man_humanoid"
        )

        # Right eye
        canvas.create_polygon(
            cx + 30 * s, eye_y,
            cx + 12 * s, eye_y,
            cx + 8 * s, eye_y - 8 * s,
            cx + 26 * s, eye_y - 8 * s,
            fill=eye_color, outline=colors["outline"], width=2,
            tags="iron_man_humanoid"
        )

        # Neck
        neck_y = head_y + 50 * s
        canvas.create_rectangle(
            cx - 25 * s, neck_y,
            cx + 25 * s, neck_y + 20 * s,
            fill=colors["primary"], outline=colors["secondary"], width=1,
            tags="iron_man_humanoid"
        )

        # Torso
        torso_y = cy - 20 * s
        torso_width = 70 * s
        torso_height = 100 * s

        canvas.create_rectangle(
            cx - torso_width / 2, torso_y - torso_height / 2,
            cx + torso_width / 2, torso_y + torso_height / 2,
            fill=colors["primary"], outline=colors["outline"], width=2,
            tags="iron_man_humanoid"
        )

        # Arms (with pose angles)
        self._draw_arm(canvas, cx, torso_y, s, pose.arm_left_angle, "left", colors)
        self._draw_arm(canvas, cx, torso_y, s, pose.arm_right_angle, "right", colors)

        # Legs (with pose angles)
        self._draw_leg(canvas, cx, torso_y, s, pose.leg_left_angle, "left", colors)
        self._draw_leg(canvas, cx, torso_y, s, pose.leg_right_angle, "right", colors)

    def _draw_arm(self, canvas, cx: float, torso_y: float, s: float,
                  angle: float, side: str, colors: Dict[str, str]):
        """Draw arm with pose angle"""
        arm_rad = math.radians(angle)
        sign = -1 if side == "left" else 1

        # Shoulder position
        shoulder_x = cx + sign * 35 * s
        shoulder_y = torso_y - 30 * s

        # Upper arm
        upper_arm_length = 50 * s
        upper_arm_end_x = shoulder_x + math.cos(arm_rad) * upper_arm_length * sign
        upper_arm_end_y = shoulder_y + math.sin(arm_rad) * upper_arm_length

        canvas.create_line(
            shoulder_x, shoulder_y,
            upper_arm_end_x, upper_arm_end_y,
            fill=colors["primary"], width=12 * s,
            tags="iron_man_humanoid"
        )

        # Forearm
        forearm_length = 40 * s
        forearm_end_x = upper_arm_end_x + math.cos(arm_rad) * forearm_length * sign
        forearm_end_y = upper_arm_end_y + math.sin(arm_rad) * forearm_length

        canvas.create_line(
            upper_arm_end_x, upper_arm_end_y,
            forearm_end_x, forearm_end_y,
            fill=colors["primary"], width=10 * s,
            tags="iron_man_humanoid"
        )

        # Hand/Repulsor
        canvas.create_oval(
            forearm_end_x - 8 * s, forearm_end_y - 8 * s,
            forearm_end_x + 8 * s, forearm_end_y + 8 * s,
            fill=colors["energy"], outline=colors["primary"], width=2,
            tags="iron_man_humanoid"
        )

    def _draw_leg(self, canvas, cx: float, torso_y: float, s: float,
                  angle: float, side: str, colors: Dict[str, str]):
        """Draw leg with pose angle"""
        leg_rad = math.radians(angle)
        sign = -1 if side == "left" else 1

        # Hip position
        hip_x = cx + sign * 20 * s
        hip_y = torso_y + 50 * s

        # Thigh
        thigh_length = 50 * s
        thigh_end_x = hip_x + math.cos(leg_rad) * thigh_length * sign
        thigh_end_y = hip_y + math.sin(leg_rad) * thigh_length

        canvas.create_line(
            hip_x, hip_y,
            thigh_end_x, thigh_end_y,
            fill=colors["primary"], width=14 * s,
            tags="iron_man_humanoid"
        )

        # Shin
        shin_length = 50 * s
        shin_end_x = thigh_end_x + math.cos(leg_rad) * shin_length * sign
        shin_end_y = thigh_end_y + math.sin(leg_rad) * shin_length

        canvas.create_line(
            thigh_end_x, thigh_end_y,
            shin_end_x, shin_end_y,
            fill=colors["primary"], width=12 * s,
            tags="iron_man_humanoid"
        )

        # Foot
        canvas.create_rectangle(
            shin_end_x - 12 * s, shin_end_y,
            shin_end_x + 12 * s, shin_end_y + 20 * s,
            fill=colors["secondary"], outline=colors["primary"], width=2,
            tags="iron_man_humanoid"
        )

    def _draw_armor_plating(self, canvas, cx: float, cy: float, s: float,
                           pose: IronManPose, colors: Dict[str, str]):
        """Draw armor plating details (Android JARVIS quality)"""
        # Chest plating lines
        torso_y = cy - 20 * s
        canvas.create_line(
            cx - 20 * s, torso_y - 30 * s,
            cx + 20 * s, torso_y - 30 * s,
            fill=colors["secondary"], width=1,
            tags="iron_man_humanoid"
        )
        canvas.create_line(
            cx - 20 * s, torso_y + 30 * s,
            cx + 20 * s, torso_y + 30 * s,
            fill=colors["secondary"], width=1,
            tags="iron_man_humanoid"
        )

    def _draw_joints(self, canvas, cx: float, cy: float, s: float,
                    pose: IronManPose, colors: Dict[str, str]):
        """Draw joint articulation details"""
        # Shoulder joints
        torso_y = cy - 20 * s
        for side in [-1, 1]:
            joint_x = cx + side * 35 * s
            joint_y = torso_y - 30 * s
            canvas.create_oval(
                joint_x - 5 * s, joint_y - 5 * s,
                joint_x + 5 * s, joint_y + 5 * s,
                fill=colors["secondary"], outline=colors["outline"], width=1,
                tags="iron_man_humanoid"
            )

    def _draw_arc_reactor(self, canvas, cx: float, cy: float, s: float,
                         pose: IronManPose, colors: Dict[str, str], combat: bool):
        """Draw arc reactor on chest"""
        torso_y = cy - 20 * s
        reactor_radius = 18 * s
        reactor_color = colors["glow"] if combat else colors["primary"]

        # Outer ring
        canvas.create_oval(
            cx - reactor_radius, torso_y - reactor_radius / 2,
            cx + reactor_radius, torso_y + reactor_radius / 2,
            fill=reactor_color, outline=colors["outline"], width=2,
            tags="iron_man_humanoid"
        )

        # Inner core
        inner_radius = reactor_radius * 0.6
        canvas.create_oval(
            cx - inner_radius, torso_y - inner_radius / 2,
            cx + inner_radius, torso_y + inner_radius / 2,
            fill=colors["energy"], outline=reactor_color, width=1,
            tags="iron_man_humanoid"
        )

    def _draw_repulsors(self, canvas, cx: float, cy: float, s: float,
                       pose: IronManPose, colors: Dict[str, str], combat: bool):
        """Draw hand repulsors with charge effects"""
        if pose.phase in [IronManActionPhase.REPULSOR_CHARGE, IronManActionPhase.REPULSOR_FIRE]:
            charge = pose.repulsor_charge
            # Draw repulsor glow effects
            # (Implementation would calculate hand positions and draw glow)
            pass

    def _draw_unibeam(self, canvas, cx: float, cy: float, s: float,
                     pose: IronManPose, colors: Dict[str, str]):
        """Draw unibeam from chest"""
        torso_y = cy - 20 * s
        if pose.phase == IronManActionPhase.UNIBEAM_FIRE:
            # Draw unibeam beam
            canvas.create_line(
                cx, torso_y,
                cx, torso_y + 200 * s,
                fill=colors["energy"], width=10 * s,
                tags="iron_man_humanoid"
            )

    def _draw_energy_glow(self, canvas, cx: float, cy: float, s: float,
                         pose: IronManPose, colors: Dict[str, str], combat: bool):
        """Draw energy glow effects"""
        if combat or pose.phase in [IronManActionPhase.POWER_UP, IronManActionPhase.REPULSOR_CHARGE]:
            # Draw combat aura
            canvas.create_oval(
                cx - 60 * s, cy - 60 * s,
                cx + 60 * s, cy + 60 * s,
                outline=colors["glow"], width=2, dash=(3, 3),
                tags="iron_man_humanoid"
            )

    def _draw_particles(self, canvas, cx: float, cy: float, s: float,
                        pose: IronManPose, colors: Dict[str, str], combat: bool):
        """Draw particle effects"""
        if combat or pose.phase in [IronManActionPhase.FLYING, IronManActionPhase.REPULSOR_FIRE]:
            # Draw particles
            for i in range(5):
                angle = (i * 72) * math.pi / 180
                particle_x = cx + math.cos(angle) * 50 * s
                particle_y = cy + math.sin(angle) * 50 * s
                canvas.create_oval(
                    particle_x - 2, particle_y - 2,
                    particle_x + 2, particle_y + 2,
                    fill=colors["energy"], outline="",
                    tags="iron_man_humanoid"
                )

    def _draw_reflections(self, canvas, cx: float, cy: float, s: float,
                         pose: IronManPose, colors: Dict[str, str]):
        """Draw surface reflections"""
        # High-quality reflections on armor surfaces
        # (Implementation would add highlight effects)
        pass

    def _draw_damage(self, canvas, cx: float, cy: float, s: float,
                    pose: IronManPose, colors: Dict[str, str]):
        """Draw damage indicators"""
        # Damage sparks and cracks
        # (Implementation would show damage effects)
        pass

    def _draw_hud_overlay(self, canvas, cx: float, cy: float, s: float,
                         pose: IronManPose, colors: Dict[str, str]):
        """Draw HUD overlay elements"""
        # Status indicators, targeting reticles, etc.
        # (Implementation would add HUD elements)
        pass


class IronManActionPhaseManager:
    """Manages action phases and random action stages"""

    def __init__(self):
        """Initialize action phase manager"""
        self.current_phase = IronManActionPhase.IDLE
        self.phase_timer = 0
        self.phase_duration = 0
        self.animation_frame = 0
        self.random_actions_enabled = True

    def get_pose_for_phase(self, phase: IronManActionPhase, frame: int) -> IronManPose:
        """Get pose data for specific action phase"""
        # Base pose angles
        arm_l = 0.0
        arm_r = 0.0
        leg_l = 0.0
        leg_r = 0.0
        body_lean = 0.0
        head_tilt = 0.0
        repulsor_charge = 0.0

        # Phase-specific poses
        if phase == IronManActionPhase.IDLE:
            arm_l = 10.0
            arm_r = 10.0
            leg_l = 0.0
            leg_r = 0.0

        elif phase == IronManActionPhase.WALKING:
            # Walking animation
            cycle = (frame % 60) / 60.0
            leg_l = math.sin(cycle * math.pi * 2) * 30.0
            leg_r = -math.sin(cycle * math.pi * 2) * 30.0
            arm_l = -leg_r * 0.5
            arm_r = -leg_l * 0.5
            body_lean = 5.0

        elif phase == IronManActionPhase.RUNNING:
            # Running animation
            cycle = (frame % 40) / 40.0
            leg_l = math.sin(cycle * math.pi * 2) * 45.0
            leg_r = -math.sin(cycle * math.pi * 2) * 45.0
            arm_l = -leg_r * 0.7
            arm_r = -leg_l * 0.7
            body_lean = 15.0

        elif phase == IronManActionPhase.FLYING:
            # Flying pose
            arm_l = -45.0
            arm_r = -45.0
            leg_l = -20.0
            leg_r = -20.0
            body_lean = -10.0

        elif phase == IronManActionPhase.COMBAT:
            # Combat stance
            arm_l = -30.0
            arm_r = 30.0
            leg_l = -10.0
            leg_r = 10.0
            body_lean = 5.0

        elif phase == IronManActionPhase.REPULSOR_CHARGE:
            # Repulsor charge pose
            arm_l = -90.0
            arm_r = -90.0
            repulsor_charge = min(1.0, frame / 30.0)

        elif phase == IronManActionPhase.REPULSOR_FIRE:
            # Repulsor fire pose
            arm_l = -90.0
            arm_r = -90.0
            repulsor_charge = 1.0

        return IronManPose(
            phase=phase,
            arm_left_angle=arm_l,
            arm_right_angle=arm_r,
            leg_left_angle=leg_l,
            leg_right_angle=leg_r,
            body_lean=body_lean,
            head_tilt=head_tilt,
            repulsor_charge=repulsor_charge,
            animation_frame=frame,
            animation_speed=1.0
        )

    def get_random_action_phase(self) -> IronManActionPhase:
        """Get random action phase (similar to ACE random actions)"""
        if not self.random_actions_enabled:
            return IronManActionPhase.IDLE

        # Weighted random selection
        phases = [
            (IronManActionPhase.IDLE, 30),
            (IronManActionPhase.WALKING, 15),
            (IronManActionPhase.THINKING, 10),
            (IronManActionPhase.TALKING, 10),
            (IronManActionPhase.POWER_UP, 5),
            (IronManActionPhase.COMBAT, 5),
            (IronManActionPhase.FLYING, 5),
            (IronManActionPhase.REPULSOR_CHARGE, 5),
            (IronManActionPhase.VICTORY, 5)
        ]

        total_weight = sum(weight for _, weight in phases)
        rand = random.randint(1, total_weight)

        cumulative = 0
        for phase, weight in phases:
            cumulative += weight
            if rand <= cumulative:
                return phase

        return IronManActionPhase.IDLE

    def update(self, dt: float):
        """Update action phase manager"""
        self.phase_timer += dt
        self.animation_frame += 1

        # Auto-transition to random action after duration
        if self.phase_timer >= self.phase_duration and self.random_actions_enabled:
            self.current_phase = self.get_random_action_phase()
            self.phase_timer = 0.0
            self.phase_duration = random.uniform(2.0, 5.0)  # Random duration


# Export main classes
__all__ = [
    "IronManActionPhase",
    "IronManPose",
    "IronManHumanoidRenderer",
    "IronManActionPhaseManager"
]
