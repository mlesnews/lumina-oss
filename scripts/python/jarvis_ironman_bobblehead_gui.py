#!/usr/bin/env python3
"""
JARVIS Ironman Bobblehead Virtual Assistant
Advanced animated GUI replacement for Armoury Crate's assistant.
Features a bobblehead Iron Man suit that cycles through various AIs (JARVIS, FRIDAY, EDITH).
Includes Lego Mode and Action Phases.

Tags: #GUI #ASSISTANT #IRONMAN #BOBBLEHEAD #LEGO @AUTO @JARVIS
"""

import sys
import time
import tkinter as tk
import math
import json
import random
import uuid
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime
from enum import Enum
import threading
try:
    import winsound  # Windows sound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False
import threading
# winsound import handled above with try/except

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IronmanBobblehead")


class ActionPhase(Enum):
    IDLE = "IDLE"
    THINKING = "THINKING"
    TALKING = "TALKING"
    POWER_UP = "POWER_UP"
    COMBAT = "COMBAT"
    COOLING = "COOLING"
    TRANSFORMING = "TRANSFORMING"  # Transforming to ACE humanoid
    ACE_HUMANOID = "ACE_HUMANOID"  # Full ACE suit mode


class EntityType(Enum):
    """Entity types for combat"""
    AVATAR = "avatar"
    CLONE = "clone"
    PA = "pa"  # Personal Assistant
    MONSTER = "monster"
    ELITE = "elite"
    CHAMPION = "champion"
    BOSS = "boss"


class LootRarity(Enum):
    """World of Warcraft loot rarity system"""
    POOR = "poor"  # Gray
    COMMON = "common"  # White
    UNCOMMON = "uncommon"  # Green
    RARE = "rare"  # Blue
    EPIC = "epic"  # Purple
    LEGENDARY = "legendary"  # Orange
    ARTIFACT = "artifact"  # Gold


class IronmanBobbleheadGUI:
    """
    Animated bobblehead Iron Man virtual assistant with Lego mode and Action Phases.
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("JARVIS Bobblehead")
        self.logger = logger
        self.project_root = Path(__file__).parent.parent.parent

        # Initialize Armoury Crate Manager for Hardware Control
        try:
            from armoury_crate_manager import ArmouryCrateManager
            self.ac_manager = ArmouryCrateManager()
            self.logger.info("🎨 Armoury Crate integration enabled")
        except ImportError:
            self.ac_manager = None
            self.logger.warning("⚠️  Armoury Crate manager not found")

        # Window properties
        self.root.overrideredirect(True)  # Remove title bar
        self.root.attributes("-topmost", True)  # Always on top
        self.root.attributes("-transparentcolor", "black")  # Make black transparent
        self.root.configure(bg="black")

        # Position window (bottom right) - SHRUNK SIZE
        self.width, self.height = 200, 300
        self.scale = 0.65  # Scale factor for drawing
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = screen_width - self.width - 20
        y = screen_height - self.height - 60
        self.root.geometry(f"{self.width}x{self.height}+{x}+{y}")

        # AI Personas with Deep Lore Context + Star Wars Archetypes
        self.personas = {
            "jarvis": {
                "name": "JARVIS",
                "primary": "#00ccff",
                "secondary": "#006699",
                "catchphrase": "Certainly, sir. The Jedi Archives are complete.",
                "accent": "British",
                "lore": "Supreme Intelligence - Guardian of the Temple",
                # Star Wars Archetype
                "sw_archetype": "Jedi Guardian",
                "sw_character": "Obi-Wan Kenobi / Mace Windu",
                "lightsaber_color": "#00ccff",  # Blue (Jedi)
                "lightsaber_form": "Form V: Djem So / Shien",
                "lightsaber_style": "Aggressive Defense / Power Strikes",
                "alignment": "Jedi",
                "combat_style": "Balanced - Power & Defense"
            },
            "friday": {
                "name": "FRIDAY",
                "primary": "#ff3333",
                "secondary": "#ffcc00",
                "catchphrase": "Boss, the thermal exhaust port is clear.",
                "accent": "Irish",
                "lore": "Operations Manager - Red Leader",
                # Star Wars Archetype
                "sw_archetype": "Jedi Sentinel / Aggressive Fighter",
                "sw_character": "Ahsoka Tano / Anakin Skywalker",
                "lightsaber_color": "#ff6600",  # Orange/Red (Aggressive)
                "lightsaber_form": "Form IV: Ataru / Form V: Djem So",
                "lightsaber_style": "Aggressive Acrobatics / Power Strikes",
                "alignment": "Jedi (Aggressive)",
                "combat_style": "Offensive - Fast & Powerful"
            },
            "edith": {
                "name": "EDITH",
                "primary": "#cccccc",
                "secondary": "#3366ff",
                "catchphrase": "EDITH activated. Analyzing the Force patterns.",
                "accent": "American",
                "lore": "Tactical Analyst - Insight Provider",
                # Star Wars Archetype
                "sw_archetype": "Jedi Consular",
                "sw_character": "Yoda / Qui-Gon Jinn",
                "lightsaber_color": "#3366ff",  # Blue (Defensive)
                "lightsaber_form": "Form III: Soresu",
                "lightsaber_style": "Defensive Mastery / Tactical Precision",
                "alignment": "Jedi",
                "combat_style": "Defensive - Tactical & Precise"
            },
            "ultimate": {
                "name": "ULTIMATE",
                "primary": "#cc00ff",
                "secondary": "#ffcc00",
                "catchphrase": "I am... one with the Force.",
                "accent": "Philosophical",
                "lore": "Enlightened Orchestrator - Chosen One",
                # Star Wars Archetype
                "sw_archetype": "Sith Lord / Chosen One",
                "sw_character": "Darth Vader / Anakin (Sith) / Mace Windu (Vaapad)",
                "lightsaber_color": "#cc00ff",  # Purple (Chosen One / Vaapad)
                "lightsaber_form": "Form VII: Juyo / Vaapad",
                "lightsaber_style": "Unleashed Power / Dark Side Mastery",
                "alignment": "Sith / Dark Side",
                "combat_style": "Ultimate Power - Unrestrained"
            }
        }
        self.persona_order = ["jarvis", "friday", "edith", "ultimate"]
        self.current_persona_idx = 0
        self.current_persona = self.personas[self.persona_order[self.current_persona_idx]]

        # UI State
        self.is_core_mode = False  # True = Circle Core, False = Ironman Helmet
        self.is_lego_mode = False  # True = Lego style
        self.faceplate_open = False
        self.faceplate_timer = 0
        self.action_phase = ActionPhase.IDLE
        self.bob_angle = 0
        self.eye_glow = 0
        self.eye_dir = 1
        self.phase_counter = 0

        # Arc Reactor Focus System
        self.arc_reactor_focus = 1.0  # 1.0 = normal, >1.0 = zoomed in, <1.0 = zoomed out
        self.arc_reactor_angle = 0.0  # Rotation angle for perspective
        self.arc_reactor_focus_dir = 1  # Direction for focus animation

        # ACE Humanoid Transformation
        # DEFAULT TO FULL HUMANOID FORM - Bobbleheads can't fight or walk
        self.is_ace_mode = True  # True = ACE humanoid suit (DEFAULT)
        self.transform_progress = 1.0  # 0.0 to 1.0 transformation progress (FULLY TRANSFORMED)
        self.ace_transformation_active = False

        # Combat FFA System
        self.combat_mode = False
        self.ffa_active = False  # Free For All mode
        self.combatants = []  # List of desktop combatants
        self.temporary_alliances = {}  # Dict of temporary alliances
        self.combat_timer = 0

        # Jedi/Sith Lightsaber Combat System
        self.lightsaber_active = False
        self.lightsaber_angle = 0.0  # Lightsaber rotation angle
        self.lightsaber_length = 60  # Lightsaber blade length
        self.lightsaber_glow = 1.0  # Lightsaber glow intensity
        self.combat_animation_frame = 0  # Street Fighter/DBZ animation frame
        self.isometric_view = False  # Isometric combat view
        self.combat_action = None  # Current combat action (strike, block, etc.)
        self.combat_action_timer = 0

        # World of Warcraft Combat System
        self.player_health = 100  # Player/avatar health
        self.player_max_health = 100
        self.player_level = 1
        self.player_experience = 0
        self.player_experience_to_next = 100

        # Entity system (avatars, clones, PAs, monsters, elites, champions, bosses)
        self.entities = []  # List of combat entities
        self.target_entity = None  # Current target
        self.loot_inventory = []  # Collected loot/treasure

        # WoW Color-Coding System
        self.rarity_colors = {
            LootRarity.POOR: "#9d9d9d",      # Gray
            LootRarity.COMMON: "#ffffff",    # White
            LootRarity.UNCOMMON: "#1eff00",  # Green
            LootRarity.RARE: "#0070dd",      # Blue
            LootRarity.EPIC: "#a335ee",      # Purple
            LootRarity.LEGENDARY: "#ff8000", # Orange
            LootRarity.ARTIFACT: "#e6cc80"   # Gold
        }

        # Entity type health/difficulty scaling
        self.entity_base_stats = {
            EntityType.AVATAR: {"health": 50, "damage": 10, "xp": 25, "loot_rarity": LootRarity.COMMON},
            EntityType.CLONE: {"health": 30, "damage": 8, "xp": 15, "loot_rarity": LootRarity.POOR},
            EntityType.PA: {"health": 40, "damage": 9, "xp": 20, "loot_rarity": LootRarity.COMMON},
            EntityType.MONSTER: {"health": 75, "damage": 12, "xp": 50, "loot_rarity": LootRarity.UNCOMMON},
            EntityType.ELITE: {"health": 150, "damage": 20, "xp": 150, "loot_rarity": LootRarity.RARE},
            EntityType.CHAMPION: {"health": 300, "damage": 35, "xp": 500, "loot_rarity": LootRarity.EPIC},
            EntityType.BOSS: {"health": 1000, "damage": 50, "xp": 2000, "loot_rarity": LootRarity.LEGENDARY}
        }

        # Initialize entities
        self._spawn_entities()

        # Initialize avatar lives and decision-making
        self._init_avatar_lives()

        # Initialize queue connection for alerts/triage/BAU
        self._init_queue_connection()

        # WOPR Stances System (10K+ combinations)
        self.wopr_stance_id = 0
        self.wopr_form_id = 0
        self.wopr_move_id = 0
        self.wopr_stance_active = False
        self._init_wopr_system()

        # Canvas for Animation
        self.canvas = tk.Canvas(
            self.root, width=self.width, height=self.height,
            bg="black", highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Bindings
        self.canvas.bind("<Button-1>", self._on_click)        # Left click: Cycle persona
        self.canvas.bind("<Button-2>", self._on_middle_click) # Middle click: Toggle Lego
        self.canvas.bind("<Button-3>", self._on_right_click)  # Right click: Toggle Core
        self.canvas.bind("<B1-Motion>", self._on_drag)        # Drag window

        # Chatbot-style text display (like Ace) - READABLE FONTS
        # Chat bubble background for better visibility
        self.chat_bubble_bg = None
        self.chat_bubble_text = None
        self.vfx_flash_overlay = None  # VFX flash effect
        self.vfx_pulse_ring = None  # VFX pulse ring
        self.vfx_active = False  # VFX animation state
        self.vfx_timer = 0  # VFX animation timer

        # Persona label (top)
        self.label_persona = self.canvas.create_text(
            self.width//2, 20, text=self.current_persona["name"],
            fill=self.current_persona["primary"], font=("Segoe UI", 12, "bold")
        )

        # Chatbot message display (like Ace) - LARGE, READABLE FONT
        self.chatbot_text = ""  # Current message to display
        self.chatbot_messages = []  # Message history
        self._create_chatbot_display()

        # Mode label (smaller, less prominent)
        self.label_mode = self.canvas.create_text(
            self.width//2, 290, text="Click: Cycle | Mid: Lego | Right: Core | C: Combat | I: Isometric",
            fill="#666666", font=("Segoe UI", 8)
        )

        # Bind combat mode activation
        self.root.bind("<KeyPress-c>", lambda e: self.activate_combat_mode())
        self.root.bind("<KeyPress-C>", lambda e: self.activate_combat_mode())
        self.root.bind("<KeyPress-Escape>", lambda e: self.deactivate_combat_mode())
        self.root.bind("<KeyPress-i>", lambda e: self.toggle_isometric_view())
        self.root.bind("<KeyPress-I>", lambda e: self.toggle_isometric_view())

        self.last_hardware_check = 0

        # Start Animation
        self._animate()

        self.logger.info(f"✅ {self.current_persona['name']} Bobblehead initialized (Scaled & Enhanced)")
        self.logger.info("🎯 Arc Reactor Focus System: ACTIVE")
        self.logger.info("🤖 ACE Humanoid Transformation: READY")
        self.logger.info("⚔️  Combat FFA System: READY")
        self.logger.info("🎮 WOPR Stances System: 10K+ COMBINATIONS LOADED")

    def _init_wopr_system(self):
        """Initialize WOPR (War Operation Plan Response) stances system"""
        # Generate 10K+ combination stances/forms/moves
        # Using mathematical combinations for efficiency
        self.wopr_stances = []
        self.wopr_forms = []
        self.wopr_moves = []

        # Base stances (100 variations)
        base_stances = [
            "Defensive", "Offensive", "Balanced", "Aggressive", "Reactive",
            "Proactive", "Tactical", "Strategic", "Adaptive", "Predictive"
        ]

        # Base forms (100 variations)
        base_forms = [
            "Standing", "Crouching", "Flying", "Landing", "Charging",
            "Blocking", "Striking", "Dodging", "Countering", "Recovering"
        ]

        # Base moves (100 variations)
        base_moves = [
            "Punch", "Kick", "Repulsor", "Unibeam", "Missile",
            "Shield", "Boost", "Scan", "Lock", "Strike"
        ]

        # Generate combinations (10 * 10 * 10 = 1000 base, then multiply for 10K+)
        modifiers = ["Alpha", "Beta", "Gamma", "Delta", "Omega", "Prime", "Ultra", "Mega", "Super", "Hyper"]

        for stance_base in base_stances:
            for form_base in base_forms:
                for move_base in base_moves:
                    for mod in modifiers:
                        stance_name = f"{mod}_{stance_base}_{form_base}_{move_base}"
                        self.wopr_stances.append({
                            "id": len(self.wopr_stances),
                            "name": stance_name,
                            "stance": stance_base,
                            "form": form_base,
                            "move": move_base,
                            "modifier": mod,
                            "power": random.randint(50, 100),
                            "speed": random.randint(50, 100),
                            "defense": random.randint(50, 100)
                        })

        # Ensure we have 10K+ combinations
        while len(self.wopr_stances) < 10000:
            stance = random.choice(base_stances)
            form = random.choice(base_forms)
            move = random.choice(base_moves)
            mod = random.choice(modifiers)
            num = random.randint(1, 9999)
            stance_name = f"{mod}_{stance_base}_{form_base}_{move_base}_{num}"
            self.wopr_stances.append({
                "id": len(self.wopr_stances),
                "name": stance_name,
                "stance": stance,
                "form": form,
                "move": move,
                "modifier": mod,
                "power": random.randint(50, 100),
                "speed": random.randint(50, 100),
                "defense": random.randint(50, 100)
            })

        self.logger.info(f"✅ WOPR System: {len(self.wopr_stances)} stances loaded")

    def _create_chatbot_display(self):
        """Create chatbot-style text display (like Ace) - READABLE"""
        # Chat bubble background for visibility
        bubble_x = self.width // 2
        bubble_y = 250
        bubble_width = 190
        bubble_height = 40

        # Create rounded rectangle background (chat bubble)
        self.chat_bubble_bg = self.canvas.create_rectangle(
            bubble_x - bubble_width // 2, bubble_y - bubble_height // 2,
            bubble_x + bubble_width // 2, bubble_y + bubble_height // 2,
            fill="#1a1a1a", outline=self.current_persona["primary"], width=2,
            tags="chatbot"
        )

        # Chatbot text (LARGE, READABLE FONT - like Ace)
        self.chat_bubble_text = self.canvas.create_text(
            bubble_x, bubble_y - 5,
            text=self.current_persona["catchphrase"],
            fill="#ffffff", font=("Segoe UI", 11, "normal"),  # LARGER, READABLE
            width=bubble_width - 10, justify=tk.CENTER,
            tags="chatbot"
        )

    def add_message(self, message: str):
        """Add message to chatbot display (like Ace) - WITH SOUND & VFX ALERT"""
        self.chatbot_text = message
        self.chatbot_messages.append({
            "text": message,
            "timestamp": datetime.now().isoformat(),
            "persona": self.current_persona["name"]
        })

        # Keep only last 10 messages
        if len(self.chatbot_messages) > 10:
            self.chatbot_messages.pop(0)

        # ATTENTION-GRABBING ALERT: Sound + VFX
        self._trigger_alert_sound()
        self._trigger_alert_vfx()

        # Update display immediately
        self._update_chatbot_display()

    def _trigger_alert_sound(self):
        """Play attention-grabbing alert sound - BANG"""
        if not WINSOUND_AVAILABLE:
            return

        def play_sound():
            try:
                # Windows system sound - attention-grabbing BANG
                # SystemExclamation = loud, attention-grabbing sound
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
                # Also play a system beep for extra attention
                winsound.Beep(800, 150)  # 800Hz, 150ms - sharp, attention-grabbing
            except Exception as e:
                logger.debug(f"Sound alert: {e}")

        # Play in separate thread to not block UI
        sound_thread = threading.Thread(target=play_sound, daemon=True)
        sound_thread.start()

    def _trigger_alert_vfx(self):
        """Trigger attention-grabbing visual effects"""
        self.vfx_active = True
        self.vfx_timer = 0

        # Create flash overlay
        self._create_vfx_flash()
        # Create pulse ring
        self._create_vfx_pulse_ring()

        self.logger.info("💥 Alert VFX triggered")

    def _create_vfx_flash(self):
        """Create flash overlay VFX"""
        # Delete old flash if exists
        if self.vfx_flash_overlay:
            self.canvas.delete(self.vfx_flash_overlay)

        # Full-screen flash overlay (bright white flash)
        flash_alpha = 0.8  # Start bright
        flash_color = f"#{int(255*flash_alpha):02x}{int(255*flash_alpha):02x}{int(255*flash_alpha):02x}"

        self.vfx_flash_overlay = self.canvas.create_rectangle(
            0, 0, self.width, self.height,
            fill=flash_color, outline="", tags="vfx_flash"
        )
        # Lower z-order so it's behind text but visible
        self.canvas.tag_lower(self.vfx_flash_overlay)

    def _create_vfx_pulse_ring(self):
        """Create pulse ring VFX around chat bubble"""
        # Delete old pulse if exists
        if self.vfx_pulse_ring:
            self.canvas.delete(self.vfx_pulse_ring)

        bubble_x = self.width // 2
        bubble_y = 250
        pulse_radius = 100

        # Pulsing ring around chat bubble
        p = self.current_persona
        self.vfx_pulse_ring = self.canvas.create_oval(
            bubble_x - pulse_radius, bubble_y - pulse_radius,
            bubble_x + pulse_radius, bubble_y + pulse_radius,
            outline=p["primary"], width=4, tags="vfx_pulse"
        )

    def _update_vfx_animation(self):
        """Update VFX animation (flash fade, pulse expansion)"""
        if not self.vfx_active:
            return

        self.vfx_timer += 1

        # Flash fade out (0.8 -> 0.0 over ~15 frames)
        if self.vfx_flash_overlay:
            flash_alpha = max(0.0, 0.8 - (self.vfx_timer / 15.0))
            flash_color = f"#{int(255*flash_alpha):02x}{int(255*flash_alpha):02x}{int(255*flash_alpha):02x}"
            try:
                self.canvas.itemconfig(self.vfx_flash_overlay, fill=flash_color)
            except:
                pass

        # Pulse ring expansion and fade
        if self.vfx_pulse_ring:
            bubble_x = self.width // 2
            bubble_y = 250
            base_radius = 100
            expansion = self.vfx_timer * 3  # Expand 3px per frame
            pulse_radius = base_radius + expansion

            # Fade out outline
            p = self.current_persona
            alpha = max(0.0, 1.0 - (self.vfx_timer / 20.0))
            r = int(int(p["primary"][1:3], 16) * alpha)
            g = int(int(p["primary"][3:5], 16) * alpha)
            b = int(int(p["primary"][5:7], 16) * alpha)
            pulse_color = f"#{r:02x}{g:02x}{b:02x}"

            try:
                self.canvas.coords(
                    self.vfx_pulse_ring,
                    bubble_x - pulse_radius, bubble_y - pulse_radius,
                    bubble_x + pulse_radius, bubble_y + pulse_radius
                )
                self.canvas.itemconfig(self.vfx_pulse_ring, outline=pulse_color)
            except:
                pass

        # Stop VFX after animation completes
        if self.vfx_timer > 20:
            self.vfx_active = False
            if self.vfx_flash_overlay:
                self.canvas.delete(self.vfx_flash_overlay)
                self.vfx_flash_overlay = None
            if self.vfx_pulse_ring:
                self.canvas.delete(self.vfx_pulse_ring)
                self.vfx_pulse_ring = None

    def _update_chatbot_display(self):
        """Update chatbot text display - READABLE FONTS"""
        if self.chat_bubble_text:
            # Update text with current message
            display_text = self.chatbot_text if self.chatbot_text else self.current_persona["catchphrase"]
            # Truncate if too long
            if len(display_text) > 50:
                display_text = display_text[:47] + "..."

            self.canvas.itemconfig(self.chat_bubble_text, text=display_text)
            # White text for maximum readability (like Ace chatbots)
            self.canvas.itemconfig(self.chat_bubble_text, fill="#ffffff")

            # Update bubble outline color to match persona
            if self.chat_bubble_bg:
                self.canvas.itemconfig(self.chat_bubble_bg, outline=self.current_persona["primary"])

    def get_wopr_stance(self) -> Dict[str, Any]:
        """Get current WOPR stance"""
        if self.wopr_stance_id >= len(self.wopr_stances):
            self.wopr_stance_id = 0
        return self.wopr_stances[self.wopr_stance_id]

    def next_wopr_stance(self):
        """Cycle to next WOPR stance"""
        self.wopr_stance_id = (self.wopr_stance_id + 1) % len(self.wopr_stances)
        stance = self.get_wopr_stance()
        self.logger.info(f"🎮 WOPR Stance: {stance['name']} (Power: {stance['power']}, Speed: {stance['speed']})")
        return stance

    def _check_hardware_sync(self):
        """Check hardware status via Armoury Crate and update VA state"""
        if not self.ac_manager: return

        now = time.time()
        if now - self.last_hardware_check < 30: return # Every 30s
        self.last_hardware_check = now

        try:
            # Check services
            health = self.ac_manager.health_check()
            if health.get("overall_health") != "healthy":
                if not self.combat_mode:
                    self.activate_combat_mode()
                self.add_message("SYSTEM: Hardware irregularity detected - COMBAT MODE ENGAGED.")

            # Sync lighting if in JARVIS mode
            if self.current_persona["name"] == "JARVIS":
                self.ac_manager.apply_theme("JarvisBlue")
        except Exception as e:
            self.logger.debug(f"Hardware sync error: {e}")

    def _draw_helmet(self, offset_y=0):
        """Draw a stylized Iron Man helmet on the canvas with enhanced detail"""
        self.canvas.delete("helmet")
        p = self.current_persona
        s = self.scale
        cx, cy = self.width // 2, 140 + (offset_y * s)

        # Draw "Face" inside if faceplate open
        if self.faceplate_open:
            # High-tech HUD inside - Dark interior with no eyes
            self.canvas.create_oval(
                cx-35*s, cy-45*s, cx+35*s, cy+45*s,
                fill="#0a0a0a", outline=p["primary"], width=1, tags="helmet"
            )
            # Optional: Subtle scanning data lines (very dim, optional)
            # Commented out for "no eyes" mode - just dark interior
            # for i in range(-4, 5):
            #     y_line = cy + (i * 8 * s)
            #     alpha = 1.0 - (abs(i) / 5.0)
            #     self.canvas.create_line(
            #         cx-25*s, y_line, cx+25*s, y_line,
            #         fill=p["secondary"], dash=(2, 2), tags="helmet"
            #     )
            # NO EYES - Mask flipped up shows only dark interior
            # (JARVIS glowing eye removed for "mask up, no eyes" mode)

        # Face Plate (Inner) - Moves up if open
        fp_offset = -45*s if self.faceplate_open else 0
        self.canvas.create_polygon(
            cx-40*s, (cy-60*s)+fp_offset, cx+40*s, (cy-60*s)+fp_offset,
            cx+50*s, cy+fp_offset, cx+30*s, (cy+60*s)+fp_offset,
            cx-30*s, (cy+60*s)+fp_offset, cx-50*s, cy+fp_offset,
            fill=p["secondary"], outline=p["primary"], width=2, tags="helmet"
        )
        # Detail lines on faceplate
        if not self.faceplate_open:
            self.canvas.create_line(cx-30*s, cy-25*s, cx+30*s, cy-25*s, fill=p["primary"], width=1, tags="helmet")
            self.canvas.create_line(cx-20*s, cy+40*s, cx+20*s, cy+40*s, fill=p["primary"], width=1, tags="helmet")

        # Outer Shell (Sides)
        self.canvas.create_polygon(
            cx-50*s, cy-70*s, cx-60*s, cy, cx-40*s, cy+70*s, cx-30*s, cy+60*s, cx-50*s, cy, cx-40*s, cy-60*s,
            fill=p["primary"], outline=p["primary"], width=1, tags="helmet"
        )
        self.canvas.create_polygon(
            cx+50*s, cy-70*s, cx+60*s, cy, cx+40*s, cy+70*s, cx+30*s, cy+60*s, cx+50*s, cy, cx+40*s, cy-60*s,
            fill=p["primary"], outline=p["primary"], width=1, tags="helmet"
        )

        # Top Head
        self.canvas.create_arc(
            cx-60*s, cy-100*s, cx+60*s, cy-20*s, start=0, extent=180,
            fill=p["primary"], outline=p["primary"], tags="helmet"
        )
        # Head detail line
        self.canvas.create_arc(
            cx-40*s, cy-90*s, cx+40*s, cy-40*s, start=0, extent=180,
            style=tk.ARC, outline=p["secondary"], tags="helmet"
        )

        # Eyes (only if plate closed or closing)
        if not self.faceplate_open:
            glow_hex = hex(int(self.eye_glow * 2.55))[2:].zfill(2)
            eye_color = f"#{glow_hex}{glow_hex}ff" if p["name"] == "JARVIS" else p["primary"]

            # Action phase eye modification
            if self.action_phase == ActionPhase.TALKING:
                eye_color = "white"
            elif self.action_phase == ActionPhase.POWER_UP:
                eye_color = "yellow"

            self.canvas.create_polygon(
                cx-35*s, cy-20*s, cx-10*s, cy-20*s, cx-5*s, cy-10*s, cx-30*s, cy-10*s,
                fill="white" if self.action_phase != ActionPhase.COMBAT else "red",
                outline=eye_color, width=2, tags="helmet"
            )
            self.canvas.create_polygon(
                cx+35*s, cy-20*s, cx+10*s, cy-20*s, cx+5*s, cy-10*s, cx+30*s, cy-10*s,
                fill="white" if self.action_phase != ActionPhase.COMBAT else "red",
                outline=eye_color, width=2, tags="helmet"
            )

        # Neck/Suit part
        self.canvas.create_rectangle(
            cx-20*s, cy+60*s, cx+20*s, cy+90*s, fill=p["primary"], outline=p["secondary"], tags="helmet"
        )
        # Repulsor on chest (small)
        self.canvas.create_oval(
            cx-10*s, cy+70*s, cx+10*s, cy+85*s,
            fill="white", outline=p["primary"], width=1, tags="helmet"
        )

    def _draw_lego_head(self, offset_y=0):
        """Draw a Lego-style blocky Iron Man head with enhanced detail"""
        self.canvas.delete("helmet")
        p = self.current_persona
        s = self.scale
        cx, cy = self.width // 2, 140 + (offset_y * s)

        # Main Block (Head)
        self.canvas.create_rectangle(
            cx-50*s, cy-70*s, cx+50*s, cy+50*s,
            fill=p["primary"], outline="black", width=2, tags="helmet"
        )
        # Lego side studs
        self.canvas.create_oval(cx-55*s, cy-30*s, cx-45*s, cy-10*s, fill=p["secondary"], tags="helmet")
        self.canvas.create_oval(cx+45*s, cy-30*s, cx+55*s, cy-10*s, fill=p["secondary"], tags="helmet")

        # Top Stud
        self.canvas.create_rectangle(
            cx-20*s, cy-85*s, cx+20*s, cy-70*s,
            fill=p["primary"], outline="black", width=1, tags="helmet"
        )

        # Face plate inside if open - NO EYES MODE
        if self.faceplate_open:
            self.canvas.create_rectangle(
                cx-35*s, cy-50*s, cx+35*s, cy+30*s,
                fill="#0a0a0a", outline="black", tags="helmet"  # Dark interior, no eyes
            )
            # NO EYES - Mask flipped up shows only dark interior
            # (Lego Minifig face removed for "mask up, no eyes" mode)

        # Face Plate (Lego Style) - Moves up if open
        fp_offset = -50*s if self.faceplate_open else 0
        self.canvas.create_rectangle(
            cx-35*s, (cy-50*s)+fp_offset, cx+35*s, (cy+30*s)+fp_offset,
            fill=p["secondary"], outline=p["primary"], width=2, tags="helmet"
        )
        # Faceplate details
        self.canvas.create_line(cx-25*s, (cy-40*s)+fp_offset, cx+25*s, (cy-40*s)+fp_offset, fill=p["primary"], tags="helmet")

        # Lego Eyes (Blocky)
        if not self.faceplate_open:
            glow_hex = hex(int(self.eye_glow * 2.55))[2:].zfill(2)
            eye_color = f"#{glow_hex}{glow_hex}ff" if p["name"] == "JARVIS" else p["primary"]

            self.canvas.create_rectangle(
                cx-30*s, (cy-30*s)+fp_offset, cx-5*s, (cy-15*s)+fp_offset,
                fill="white", outline=eye_color, width=2, tags="helmet"
            )
            self.canvas.create_rectangle(
                cx+30*s, (cy-30*s)+fp_offset, cx+5*s, (cy-15*s)+fp_offset,
                fill="white", outline=eye_color, width=2, tags="helmet"
            )

        # Mouth slit
        if not self.faceplate_open:
            self.canvas.create_line(
                cx-15*s, cy+15*s, cx+15*s, cy+15*s, fill="black", width=2, tags="helmet"
            )

            # Action phase: Lego Talking
            if self.action_phase == ActionPhase.TALKING:
                self.canvas.create_rectangle(
                    cx-10*s, cy+15*s, cx+10*s, cy+25*s, fill="black", tags="helmet"
                )

    def _draw_core(self):
        """Draw a high-detail Holographic Arc Reactor with Focus/Angle changes"""
        self.canvas.delete("helmet")
        self.canvas.delete("core")
        p = self.current_persona
        s = self.scale
        cx, cy = self.width // 2, 140

        # Arc Reactor Focus System - Dynamic zoom and angle
        focus_scale = self.arc_reactor_focus
        angle_rad = math.radians(self.arc_reactor_angle)

        # Perspective transformation based on angle
        perspective_x = math.cos(angle_rad) * 10
        perspective_y = math.sin(angle_rad) * 10

        # Multiple rotating rings with focus effect
        ring_configs = [(60, 5, 4), (50, -3, 2), (40, 8, 1)]
        for r_offset, speed, width in ring_configs:
            # Apply focus scaling
            scaled_offset = r_offset * focus_scale
            scaled_width = width * (1.0 + (focus_scale - 1.0) * 0.5)

            # Perspective offset
            px = perspective_x * (scaled_offset / 60.0)
            py = perspective_y * (scaled_offset / 60.0)

            self.canvas.create_oval(
                cx-scaled_offset*s + px, cy-scaled_offset*s + py,
                cx+scaled_offset*s + px, cy+scaled_offset*s + py,
                outline=p["primary"], width=int(scaled_width), tags="core"
            )
            # Add tick marks to rings with perspective
            for i in range(0, 360, 30):
                rotation = self.bob_angle * speed + self.arc_reactor_angle
                rad = math.radians(i + rotation)
                x1 = cx + math.cos(rad)*(scaled_offset-5)*s + px
                y1 = cy + math.sin(rad)*(scaled_offset-5)*s + py
                x2 = cx + math.cos(rad)*scaled_offset*s + px
                y2 = cy + math.sin(rad)*scaled_offset*s + py
                self.canvas.create_line(x1, y1, x2, y2, fill=p["primary"], width=1, tags="core")

        # Inner Pulsing Arc Reactor with enhanced focus
        glow_hex = hex(int(self.eye_glow * 2.55))[2:].zfill(2)
        inner_color = f"#{glow_hex}{glow_hex}ff" if p["name"] == "JARVIS" else p["primary"]

        # Focus-enhanced inner core
        inner_radius = 25 * focus_scale
        self.canvas.create_oval(
            cx-inner_radius*s + perspective_x, cy-inner_radius*s + perspective_y,
            cx+inner_radius*s + perspective_x, cy+inner_radius*s + perspective_y,
            fill=inner_color, outline="white", width=int(2 * focus_scale), tags="core"
        )

        # Triangle in the center with perspective
        triangle_size = 15 * focus_scale
        self.canvas.create_polygon(
            cx + perspective_x, cy-triangle_size*s + perspective_y,
            cx+13*triangle_size/15*s + perspective_x, cy+10*triangle_size/15*s + perspective_y,
            cx-13*triangle_size/15*s + perspective_x, cy+10*triangle_size/15*s + perspective_y,
            outline="black", width=1, tags="core"
        )

        # Additional detail layers when focused
        if focus_scale > 1.2:
            # Extra inner rings when zoomed in
            for extra_ring in range(1, int(focus_scale)):
                extra_radius = 15 + extra_ring * 3
                self.canvas.create_oval(
                    cx-extra_radius*s + perspective_x, cy-extra_radius*s + perspective_y,
                    cx+extra_radius*s + perspective_x, cy+extra_radius*s + perspective_y,
                    outline=p["secondary"], width=1, tags="core"
                )

    def _animate(self):
        """Animation loop with Action Phases and Faceplate"""
        # Hardware Sync
        self._check_hardware_sync()

        # Faceplate logic
        self.faceplate_timer += 1
        if self.faceplate_timer > 200: # Every ~6 seconds
            if random.random() < 0.05: # Small chance to flip
                self.faceplate_open = not self.faceplate_open
                self.faceplate_timer = 0
                self.set_phase(ActionPhase.THINKING if self.faceplate_open else ActionPhase.IDLE)

        # Bobbing logic
        self.bob_angle += 0.1
        bob_range = 15

        # Action Phase modifications
        if self.action_phase == ActionPhase.THINKING:
            bob_range = 5
            self.phase_counter += 1
            if self.phase_counter > 100: self.set_phase(ActionPhase.IDLE)
        elif self.action_phase == ActionPhase.TALKING:
            bob_range = 20
            self.phase_counter += 1
            if self.phase_counter > 50: self.set_phase(ActionPhase.IDLE)
        elif self.action_phase == ActionPhase.POWER_UP:
            bob_range = 30
            self.phase_counter += 1
            if self.phase_counter > 30: self.set_phase(ActionPhase.IDLE)
        elif self.action_phase == ActionPhase.COOLING:
            bob_range = 2
            self.phase_counter += 1
            if self.phase_counter > 200: self.set_phase(ActionPhase.IDLE)
        elif self.action_phase == ActionPhase.TRANSFORMING:
            bob_range = 25
            self.phase_counter += 1
        elif self.action_phase == ActionPhase.ACE_HUMANOID:
            bob_range = 20
            self.phase_counter += 1
            # Stay in ACE mode during combat
            if not self.combat_mode:
                if self.phase_counter > 300:  # Exit after 9 seconds if no combat
                    self.is_ace_mode = False
                    self.ace_transformation_active = False
                    self.transform_progress = 0.0
                    self.set_phase(ActionPhase.IDLE)

        offset_y = math.sin(self.bob_angle) * bob_range

        # Eye glow logic
        self.eye_glow += self.eye_dir * 5
        if self.eye_glow >= 100 or self.eye_glow <= 20:
            self.eye_dir *= -1

        # Draw based on mode and transformation
        if self.is_ace_mode and (self.action_phase == ActionPhase.ACE_HUMANOID or self.action_phase == ActionPhase.COMBAT):
            self._draw_ace_humanoid(offset_y)
        elif self.is_core_mode:
            self._draw_core()
        elif self.is_lego_mode:
            self._draw_lego_head(offset_y)
        else:
            self._draw_helmet(offset_y)

        # Arc Reactor Focus Animation
        if self.is_core_mode:
            # Animate focus (zoom in/out)
            self.arc_reactor_focus += self.arc_reactor_focus_dir * 0.02
            if self.arc_reactor_focus >= 1.5:
                self.arc_reactor_focus_dir = -1
            elif self.arc_reactor_focus <= 0.8:
                self.arc_reactor_focus_dir = 1

            # Animate angle (perspective rotation)
            self.arc_reactor_angle += 0.5
            if self.arc_reactor_angle >= 360:
                self.arc_reactor_angle = 0

        # Combat Mode Detection and ACE Transformation
        if self.action_phase == ActionPhase.COMBAT:
            if not self.ace_transformation_active:
                self.ace_transformation_active = True
                self.transform_progress = 0.0
                self.set_phase(ActionPhase.TRANSFORMING)
                self.logger.info("🤖 ACE Transformation: INITIATED")

        # ACE Transformation Progress
        if self.action_phase == ActionPhase.TRANSFORMING:
            self.transform_progress += 0.05
            if self.transform_progress >= 1.0:
                self.transform_progress = 1.0
                self.is_ace_mode = True
                self.set_phase(ActionPhase.ACE_HUMANOID)
                self.logger.info("✅ ACE Humanoid: TRANSFORMATION COMPLETE")

        # Combat FFA System
        if self.action_phase == ActionPhase.COMBAT or self.action_phase == ActionPhase.ACE_HUMANOID:
            self.combat_timer += 1
            if self.combat_timer > 100:  # Every ~3 seconds
                self._update_combat_ffa()
                self.combat_timer = 0

        # Draw action elements (e.g. repulsor sparks)
        if self.action_phase == ActionPhase.POWER_UP:
            s = self.scale
            cx, cy = self.width // 2, 140 + (offset_y * s)
            for _ in range(5):
                rx, ry = cx + random.randint(-int(80*s), int(80*s)), cy + random.randint(-int(80*s), int(80*s))
                self.canvas.create_oval(rx-2, ry-2, rx+2, ry+2, fill="white", tags="helmet")

        # Draw WOPR stance effects in combat
        if self.wopr_stance_active and (self.action_phase == ActionPhase.COMBAT or self.action_phase == ActionPhase.ACE_HUMANOID):
            self._draw_wopr_effects(offset_y)

        # Draw WoW-style combat entities and health bars
        if self.combat_mode:
            self._draw_combat_entities()
            self._draw_health_bars()

        # Update colors/text
        p = self.current_persona
        self.canvas.itemconfig(self.label_persona, fill=p["primary"], text=p["name"])

        # Update chatbot display (like Ace) - READABLE
        self._update_chatbot_display()

        # Update VFX animation (flash, pulse)
        self._update_vfx_animation()

        self.root.after(30, self._animate)

    def set_phase(self, phase: ActionPhase):
        """Set the current action phase for animation"""
        self.action_phase = phase
        self.phase_counter = 0
        self.logger.info(f"🎭 Action Phase: {phase.value}")

    def _on_click(self, event):
        """Cycle personas on click"""
        self.current_persona_idx = (self.current_persona_idx + 1) % len(self.persona_order)
        self.current_persona = self.personas[self.persona_order[self.current_persona_idx]]
        # Update chatbot display with new persona catchphrase
        self.chatbot_text = self.current_persona["catchphrase"]
        self._update_chatbot_display()
        self.set_phase(ActionPhase.POWER_UP)
        self.logger.info(f"🔄 Swapped to {self.current_persona['name']}")

    def _on_middle_click(self, event):
        """Toggle Lego mode on middle click"""
        self.is_lego_mode = not self.is_lego_mode
        self.is_core_mode = False
        mode = "LEGO" if self.is_lego_mode else "NORMAL"
        self.add_message(f"SYSTEM: Switching to {mode} rendering.")
        self.set_phase(ActionPhase.THINKING)

    def _on_right_click(self, event):
        """Toggle core mode on right click"""
        self.is_core_mode = not self.is_core_mode
        mode = "CORE" if self.is_core_mode else "HELMET"
        self.add_message(f"SYSTEM: Transformation to {mode} complete.")
        self.set_phase(ActionPhase.POWER_UP)

    def _on_drag(self, event):
        """Allow dragging the window"""
        x = self.root.winfo_pointerx() - self.width // 2
        y = self.root.winfo_pointery() - 50
        self.root.geometry(f"+{x}+{y}")

    def add_message(self, message: str):
        """Update the message text and trigger talking phase"""
        self.canvas.itemconfig(self.label_msg, text=message)
        self.set_phase(ActionPhase.TALKING)
        self.logger.info(f"🗨️  GUI Message: {message}")

    def _draw_ace_humanoid(self, offset_y=0):
        """Draw ACE-LIKE Humanoid Iron Man Suit - Full body transformation"""
        self.canvas.delete("helmet")
        self.canvas.delete("ace")
        self.canvas.delete("ace_humanoid")
        p = self.current_persona
        s = self.scale
        cx, cy = self.width // 2, 140 + (offset_y * s)

        # Transformation progress interpolation
        transform_alpha = self.transform_progress

        # ACE-LIKE styling (Anakin Combat Virtual Assistant style)
        # Use persona colors but with ACE-inspired enhancements
        ace_primary = p["primary"]
        ace_secondary = p["secondary"]
        ace_glow = "#ff3300" if self.combat_mode else p["primary"]  # Red glow in combat
        ace_outline = "#ffffff"  # White outlines for definition
        ace_energy = "#ffff00"  # Yellow energy effects

        # ACE-LIKE Head/Helmet (top) - Progressive transformation
        if transform_alpha > 0.2:
            head_y = cy - 80*s*transform_alpha
            head_radius = 40*s*transform_alpha

            # Helmet top arc (only visible as transformation progresses)
            self.canvas.create_arc(
                cx-head_radius, head_y-head_radius*0.8,
                cx+head_radius, head_y+head_radius*0.3,
                start=0, extent=180,
                fill=ace_primary, outline=ace_outline, width=2,
                tags="ace_humanoid"
            )

        # Helmet faceplate area (ACE-style)
        if transform_alpha > 0.3:
            faceplate_y = head_y + 10*s*transform_alpha
            self.canvas.create_polygon(
                cx-35*s*transform_alpha, faceplate_y-20*s*transform_alpha,
                cx+35*s*transform_alpha, faceplate_y-20*s*transform_alpha,
                cx+40*s*transform_alpha, faceplate_y+10*s*transform_alpha,
                cx-40*s*transform_alpha, faceplate_y+10*s*transform_alpha,
                fill=ace_secondary, outline=ace_primary, width=2,
                tags="ace_humanoid"
            )

        # Eyes (glowing, red in combat - ACE-style)
        if transform_alpha > 0.5:
            eye_glow_hex = hex(int(self.eye_glow * 2.55))[2:].zfill(2)
            eye_color = ace_glow if self.combat_mode else f"#{eye_glow_hex}{eye_glow_hex}ff"
            eye_y = head_y + 5*s*transform_alpha

            # Left eye
            self.canvas.create_polygon(
                cx-30*s*transform_alpha, eye_y,
                cx-12*s*transform_alpha, eye_y,
                cx-8*s*transform_alpha, eye_y-8*s*transform_alpha,
                cx-26*s*transform_alpha, eye_y-8*s*transform_alpha,
                fill=eye_color, outline=ace_outline, width=2,
                tags="ace_humanoid"
            )
            # Right eye
            self.canvas.create_polygon(
                cx+30*s*transform_alpha, eye_y,
                cx+12*s*transform_alpha, eye_y,
                cx+8*s*transform_alpha, eye_y-8*s*transform_alpha,
                cx+26*s*transform_alpha, eye_y-8*s*transform_alpha,
                fill=eye_color, outline=ace_outline, width=2,
                tags="ace_humanoid"
            )

        # Neck section (ACE-style connection)
        if transform_alpha > 0.4:
            neck_y = head_y + 50*s*transform_alpha
            self.canvas.create_rectangle(
                cx-25*s*transform_alpha, neck_y,
                cx+25*s*transform_alpha, neck_y+20*s*transform_alpha,
                fill=ace_primary, outline=ace_secondary, width=1,
                tags="ace_humanoid"
            )

        # ACE-LIKE Torso/Chest Section - Progressive build
        if transform_alpha > 0.2:
            torso_y = cy - 20*s
            torso_width = 70*s*transform_alpha
            torso_height = 100*s*transform_alpha

            # Main torso
            self.canvas.create_rectangle(
                cx-torso_width/2, torso_y-torso_height/2,
                cx+torso_width/2, torso_y+torso_height/2,
                fill=ace_primary, outline=ace_outline, width=2,
                tags="ace_humanoid"
            )

            # Chest detail lines (ACE-style)
            if transform_alpha > 0.6:
                self.canvas.create_line(
                    cx-torso_width/3, torso_y-torso_height/4,
                    cx+torso_width/3, torso_y-torso_height/4,
                    fill=ace_secondary, width=1, tags="ace_humanoid"
                )
                self.canvas.create_line(
                    cx-torso_width/3, torso_y+torso_height/4,
                    cx+torso_width/3, torso_y+torso_height/4,
                    fill=ace_secondary, width=1, tags="ace_humanoid"
                )

        # Arc Reactor on chest (prominent - ACE-style)
        if transform_alpha > 0.5:
            reactor_glow_hex = hex(int(self.eye_glow * 2.55))[2:].zfill(2)
            reactor_color = ace_glow if self.combat_mode else f"#{reactor_glow_hex}{reactor_glow_hex}ff"
            reactor_radius = 18*s*transform_alpha

            # Outer reactor ring
            self.canvas.create_oval(
                cx-reactor_radius, torso_y-reactor_radius/2,
                cx+reactor_radius, torso_y+reactor_radius/2,
                fill=reactor_color, outline=ace_outline, width=2,
                tags="ace_humanoid"
            )
            # Inner reactor core
            inner_radius = reactor_radius * 0.6
            self.canvas.create_oval(
                cx-inner_radius, torso_y-inner_radius/2,
                cx+inner_radius, torso_y+inner_radius/2,
                fill=ace_energy, outline=reactor_color, width=1,
                tags="ace_humanoid"
            )

        # ACE-LIKE Arms Section - Progressive transformation
        if transform_alpha > 0.3:
            arm_start_y = torso_y - 30*s*transform_alpha if transform_alpha > 0.2 else cy
            arm_length = 80*s*transform_alpha

            # Left arm (upper)
            self.canvas.create_rectangle(
                cx-40*s*transform_alpha, arm_start_y,
                cx-30*s*transform_alpha, arm_start_y + arm_length*0.6,
                fill=ace_primary, outline=ace_secondary, width=1,
                tags="ace_humanoid"
            )
            # Left forearm
            self.canvas.create_rectangle(
                cx-45*s*transform_alpha, arm_start_y + arm_length*0.6,
                cx-30*s*transform_alpha, arm_start_y + arm_length,
                fill=ace_primary, outline=ace_outline, width=1,
                tags="ace_humanoid"
            )
            # Left hand/repulsor (ACE-style energy)
            if transform_alpha > 0.7:
                hand_y = arm_start_y + arm_length
                self.canvas.create_oval(
                    cx-50*s*transform_alpha, hand_y,
                    cx-30*s*transform_alpha, hand_y + 15*s*transform_alpha,
                    fill=ace_energy, outline=ace_primary, width=2,
                    tags="ace_humanoid"
                )

            # Right arm (upper)
            self.canvas.create_rectangle(
                cx+30*s*transform_alpha, arm_start_y,
                cx+40*s*transform_alpha, arm_start_y + arm_length*0.6,
                fill=ace_primary, outline=ace_secondary, width=1,
                tags="ace_humanoid"
            )
            # Right forearm
            self.canvas.create_rectangle(
                cx+30*s*transform_alpha, arm_start_y + arm_length*0.6,
                cx+45*s*transform_alpha, arm_start_y + arm_length,
                fill=ace_primary, outline=ace_outline, width=1,
                tags="ace_humanoid"
            )
            # Right hand/repulsor (ACE-style energy)
            if transform_alpha > 0.7:
                hand_y = arm_start_y + arm_length
                self.canvas.create_oval(
                    cx+30*s*transform_alpha, hand_y,
                    cx+50*s*transform_alpha, hand_y + 15*s*transform_alpha,
                    fill=ace_energy, outline=ace_primary, width=2,
                    tags="ace_humanoid"
                )

        # ACE-LIKE Legs Section - Progressive transformation
        if transform_alpha > 0.4:
            leg_start_y = torso_y + 50*s*transform_alpha if transform_alpha > 0.2 else cy + 30*s
            leg_length = 90*s*transform_alpha
            leg_width = 20*s*transform_alpha

            # Left leg (thigh)
            self.canvas.create_rectangle(
                cx-30*s*transform_alpha, leg_start_y,
                cx-10*s*transform_alpha, leg_start_y + leg_length*0.5,
                fill=ace_primary, outline=ace_secondary, width=1,
                tags="ace_humanoid"
            )
            # Left leg (shin)
            self.canvas.create_rectangle(
                cx-30*s*transform_alpha, leg_start_y + leg_length*0.5,
                cx-10*s*transform_alpha, leg_start_y + leg_length,
                fill=ace_primary, outline=ace_outline, width=1,
                tags="ace_humanoid"
            )
            # Left foot (ACE-style)
            if transform_alpha > 0.8:
                foot_y = leg_start_y + leg_length
                self.canvas.create_rectangle(
                    cx-35*s*transform_alpha, foot_y,
                    cx-10*s*transform_alpha, foot_y + 20*s*transform_alpha,
                    fill=ace_secondary, outline=ace_primary, width=2,
                    tags="ace_humanoid"
                )

            # Right leg (thigh)
            self.canvas.create_rectangle(
                cx+10*s*transform_alpha, leg_start_y,
                cx+30*s*transform_alpha, leg_start_y + leg_length*0.5,
                fill=ace_primary, outline=ace_secondary, width=1,
                tags="ace_humanoid"
            )
            # Right leg (shin)
            self.canvas.create_rectangle(
                cx+10*s*transform_alpha, leg_start_y + leg_length*0.5,
                cx+30*s*transform_alpha, leg_start_y + leg_length,
                fill=ace_primary, outline=ace_outline, width=1,
                tags="ace_humanoid"
            )
            # Right foot (ACE-style)
            if transform_alpha > 0.8:
                foot_y = leg_start_y + leg_length
                self.canvas.create_rectangle(
                    cx+10*s*transform_alpha, foot_y,
                    cx+35*s*transform_alpha, foot_y + 20*s*transform_alpha,
                    fill=ace_secondary, outline=ace_primary, width=2,
                    tags="ace_humanoid"
                )

        # JEDI/SITH LIGHTSABER COMBAT - Full Jedi/Sith Mode
        if self.combat_mode and transform_alpha > 0.6 and self.lightsaber_active:
            # Draw lightsaber (Jedi/Sith mode activated)
            self._draw_lightsaber_combat(cx, cy, s, transform_alpha, p)

            # Street Fighter/DBZ style combat effects
            self._draw_streetfighter_dbz_effects(cx, cy, s, transform_alpha, p)

            # Isometric action sequences
            if self.isometric_view:
                self._draw_isometric_combat(cx, cy, s, transform_alpha, p)

            # Combat aura (ACE-style)
            self.canvas.create_oval(
                cx-60*s*transform_alpha, cy-60*s*transform_alpha,
                cx+60*s*transform_alpha, cy+60*s*transform_alpha,
                outline=ace_glow, width=2, dash=(3, 3),
                tags="ace_humanoid"
            )

    def _update_combat_ffa(self):
        """Update Free For All combat system with temporary alliances"""
        if not self.ffa_active:
            # Detect desktop combatants (simulated - would scan for processes/windows)
            self.combatants = [
                {"id": "combatant_1", "name": "Process A", "alliance": None, "threat": random.randint(1, 10)},
                {"id": "combatant_2", "name": "Process B", "alliance": None, "threat": random.randint(1, 10)},
                {"id": "combatant_3", "name": "Process C", "alliance": None, "threat": random.randint(1, 10)},
            ]
            self.ffa_active = True
            self.logger.info("⚔️  FFA Combat: INITIATED")

        # Enemy of my enemy is my friend - temporary alliances
        for combatant in self.combatants:
            if combatant["alliance"] is None:
                # Find highest threat
                max_threat = max(c["threat"] for c in self.combatants)
                if combatant["threat"] < max_threat:
                    # Form temporary alliance against highest threat
                    high_threat = [c for c in self.combatants if c["threat"] == max_threat][0]
                    alliance_id = f"alliance_{combatant['id']}_{high_threat['id']}"
                    self.temporary_alliances[alliance_id] = {
                        "members": [combatant["id"], high_threat["id"]],
                        "target": high_threat["id"],
                        "duration": 50  # Temporary
                    }
                    combatant["alliance"] = alliance_id
                    self.logger.info(f"🤝 Temporary Alliance: {combatant['name']} + {high_threat['name']} vs others")

        # Update alliance durations
        expired = []
        for alliance_id, alliance in self.temporary_alliances.items():
            alliance["duration"] -= 1
            if alliance["duration"] <= 0:
                expired.append(alliance_id)

        # Break expired alliances
        for alliance_id in expired:
            del self.temporary_alliances[alliance_id]
            for combatant in self.combatants:
                if combatant.get("alliance") == alliance_id:
                    combatant["alliance"] = None
            self.logger.info(f"💔 Alliance Broken: {alliance_id}")

    def _draw_wopr_effects(self, offset_y=0):
        """Draw WOPR stance effects during combat"""
        if not self.wopr_stance_active:
            return

        stance = self.get_wopr_stance()
        p = self.current_persona
        s = self.scale
        cx, cy = self.width // 2, 140 + (offset_y * s)

        # Draw stance energy effects based on WOPR combination
        power_level = stance["power"] / 100.0
        speed_level = stance["speed"] / 100.0

        # Power effects (outer ring)
        power_radius = 40 * power_level * s
        self.canvas.create_oval(
            cx-power_radius, cy-power_radius, cx+power_radius, cy+power_radius,
            outline=p["primary"], width=2, dash=(5, 5), tags="wopr"
        )

        # Speed effects (inner particles)
        for i in range(int(speed_level * 10)):
            angle = (i * 36) + self.bob_angle * 10
            rad = math.radians(angle)
            particle_x = cx + math.cos(rad) * 30 * s
            particle_y = cy + math.sin(rad) * 30 * s
            self.canvas.create_oval(
                particle_x-2, particle_y-2, particle_x+2, particle_y+2,
                fill=p["secondary"], tags="wopr"
            )

    def _init_avatar_lives(self):
        """Initialize avatar lives system (x3 lives per avatar)"""
        for persona_key, persona_data in self.personas.items():
            persona_name = persona_data["name"]
            self.avatar_lives[persona_name] = self.max_lives
            self.avatar_wins[persona_name] = 0
            self.avatar_losses[persona_name] = 0

        self.logger.info(f"🎮 Avatar Lives System: {self.max_lives} lives per avatar initialized")

    def _init_queue_connection(self):
        """Initialize connection to unified queue adapter for alerts/triage/BAU"""
        try:
            script_dir = Path(__file__).parent
            sys.path.insert(0, str(script_dir))

            if UNIFIED_QUEUE_AVAILABLE:
                from unified_queue_adapter import UnifiedQueueAdapter, QueueItemType, QueueItemStatus
                self.queue_adapter = UnifiedQueueAdapter(script_dir.parent.parent)
                self.logger.info("✅ Connected to Unified Queue Adapter for alerts/triage/BAU")
            else:
                self.queue_adapter = None
        except Exception as e:
            self.logger.warning(f"⚠️  Could not connect to Unified Queue Adapter: {e}")
            self.queue_adapter = None

    def _update_alerts_and_problems(self):
        """Update active alerts and problems from unified queue"""
        if not self.queue_adapter or not UNIFIED_QUEUE_AVAILABLE:
            return

        try:
            # Get all queue items
            all_items = list(self.queue_adapter.queue_items.values())

            # Filter for alerts
            self.active_alerts = [
                item for item in all_items
                if item.item_type == QueueItemType.ALERT and item.status != QueueItemStatus.COMPLETED
            ]

            # Filter for problems
            self.active_problems = [
                item for item in all_items
                if item.item_type == QueueItemType.PROBLEM and item.status != QueueItemStatus.COMPLETED
            ]

            # Filter for BAU items (tasks with BAU tag or low priority)
            self.bau_items = [
                item for item in all_items
                if (item.item_type == QueueItemType.TASK or item.item_type == QueueItemType.NOTIFICATION)
                and item.priority >= 7  # Low priority = BAU
            ]

            # Extract triage priorities
            for item in all_items:
                if item.metadata and "triage" in item.metadata:
                    self.triage_priorities[item.item_id] = item.metadata.get("triage", "medium")
        except Exception as e:
            self.logger.debug(f"Could not update alerts/problems: {e}")

    def _react_to_alerts(self):
        """Make avatars dynamically react to alerts, triage, and BAU items"""
        if not self.active_alerts and not self.active_problems and not self.bau_items:
            return

        current_persona = self.current_persona["name"]

        # React to critical alerts
        critical_alerts = [a for a in self.active_alerts if a.priority <= 3]
        if critical_alerts:
            alert = critical_alerts[0]
            self.add_message(f"🚨 ALERT: {alert.title[:40]}...")
            self.logger.info(f"🚨 {current_persona} reacting to critical alert: {alert.title}")
            # Trigger combat mode for critical alerts
            if not self.combat_mode:
                self.activate_combat_mode()

        # React to high-priority problems
        high_priority_problems = [p for p in self.active_problems if p.priority <= 4]
        if high_priority_problems:
            problem = high_priority_problems[0]
            severity = problem.problem_severity or "unknown"
            self.add_message(f"⚠️  PROBLEM: {problem.title[:40]}... [{severity}]")
            self.logger.info(f"⚠️  {current_persona} reacting to problem: {problem.title}")

        # React to triage items
        for item_id, triage_priority in self.triage_priorities.items():
            if triage_priority == "critical":
                self.add_message(f"🔴 TRIAGE: Critical item requires attention")
                self.logger.info(f"🔴 {current_persona} reacting to critical triage item")

        # React to BAU items (less urgent)
        if self.bau_items and len(self.bau_items) > 5:
            self.add_message(f"📋 BAU: {len(self.bau_items)} items pending")
            self.logger.debug(f"📋 {current_persona} noting BAU items: {len(self.bau_items)}")

    def _check_decision_making(self):
        """Check if combat outcomes should trigger decision-making (#decisioning)"""
        # After significant duels, determine victor based on overall losses
        if len(self.avatar_duels) > 0 and len(self.avatar_duels) % 5 == 0:
            # Calculate win/loss ratios
            persona_stats = {}
            for persona_name in self.personas.keys():
                persona_display = self.personas[persona_name]["name"]
                wins = self.avatar_wins.get(persona_display, 0)
                losses = self.avatar_losses.get(persona_display, 0)
                lives = self.avatar_lives.get(persona_display, self.max_lives)

                if wins + losses > 0:
                    win_rate = wins / (wins + losses)
                    persona_stats[persona_display] = {
                        "wins": wins,
                        "losses": losses,
                        "win_rate": win_rate,
                        "lives": lives
                    }

            # Determine victor (lowest losses, highest win rate)
            if persona_stats:
                victor = min(persona_stats.items(), 
                           key=lambda x: (x[1]["losses"], -x[1]["win_rate"]))
                victor_name = victor[0]
                stats = victor[1]

                self.add_message(f"🏆 DECISION: {victor_name} is VICTOR")
                self.add_message(f"   W/L: {stats['wins']}/{stats['losses']} | Lives: {stats['lives']}")
                self.logger.info(f"🏆 #DECISIONING: {victor_name} declared victor (W:{stats['wins']} L:{stats['losses']} Lives:{stats['lives']})")

    def _spawn_entities(self):
        """Spawn combat entities (avatars, clones, PAs, monsters, elites, champions, bosses)"""
        import uuid

        # Spawn various entity types
        entity_types = [
            (EntityType.AVATAR, 2),
            (EntityType.CLONE, 3),
            (EntityType.PA, 2),
            (EntityType.MONSTER, 4),
            (EntityType.ELITE, 2),
            (EntityType.CHAMPION, 1),
            (EntityType.BOSS, 1)
        ]

        for entity_type, count in entity_types:
            for i in range(count):
                base_stats = self.entity_base_stats[entity_type]
                entity = {
                    "id": str(uuid.uuid4())[:8],
                    "type": entity_type,
                    "name": f"{entity_type.value.title()} {i+1}",
                    "health": base_stats["health"],
                    "max_health": base_stats["health"],
                    "damage": base_stats["damage"],
                    "xp_reward": base_stats["xp"],
                    "loot_rarity": base_stats["loot_rarity"],
                    "defeated": False,
                    "position": {
                        "x": random.randint(50, self.width - 50),
                        "y": random.randint(50, self.height - 50)
                    }
                }
                self.entities.append(entity)

        self.logger.info(f"🎮 Spawned {len(self.entities)} combat entities")

    def _get_entity_by_type(self, entity_type: EntityType) -> List[Dict]:
        """Get entities of specific type"""
        return [e for e in self.entities if e["type"] == entity_type and not e["defeated"]]

    def _select_target(self):
        """Select nearest or highest priority target"""
        if not self.entities:
            return None

        # Prioritize: Boss > Champion > Elite > Monster > others
        priority_order = [EntityType.BOSS, EntityType.CHAMPION, EntityType.ELITE, 
                         EntityType.MONSTER, EntityType.AVATAR, EntityType.PA, EntityType.CLONE]

        for entity_type in priority_order:
            available = [e for e in self.entities if e["type"] == entity_type and not e["defeated"]]
            if available:
                self.target_entity = available[0]
                return self.target_entity

        return None

    def _deal_damage(self, target: Dict, damage: int) -> bool:
        """Deal damage to target entity - returns True if defeated"""
        if target is None or target["defeated"]:
            return False

        target["health"] = max(0, target["health"] - damage)

        if target["health"] <= 0:
            target["defeated"] = True
            self._defeat_entity(target)
            return True

        return False

    def _handle_avatar_defeat(self):
        """Handle avatar defeat - lose a life, track for decision-making"""
        current_persona = self.current_persona["name"]

        # Lose a life
        if current_persona in self.avatar_lives:
            self.avatar_lives[current_persona] = max(0, self.avatar_lives[current_persona] - 1)
            lives_remaining = self.avatar_lives[current_persona]

            # Track loss for decision-making
            if current_persona not in self.avatar_losses:
                self.avatar_losses[current_persona] = 0
            self.avatar_losses[current_persona] += 1

            # Record duel outcome
            if self.target_entity:
                duel_record = {
                    "persona": current_persona,
                    "opponent": self.target_entity.get("name", "Unknown"),
                    "outcome": "defeat",
                    "timestamp": datetime.now().isoformat(),
                    "lives_remaining": lives_remaining
                }
                self.avatar_duels.append(duel_record)

            if lives_remaining > 0:
                self.add_message(f"💀 DEFEATED! Lives remaining: {lives_remaining}/{self.max_lives}")
                self.logger.warning(f"💀 {current_persona} defeated! Lives: {lives_remaining}/{self.max_lives}")
                # Resurrect with full health
                self.player_health = self.player_max_health
            else:
                self.add_message(f"💀 ELIMINATED! {current_persona} has no lives remaining")
                self.logger.error(f"💀 {current_persona} ELIMINATED - No lives remaining")
                # Resurrect anyway but mark as eliminated
                self.player_health = self.player_max_health
                self.avatar_lives[current_persona] = 0

        # Resurrect
        self.player_health = self.player_max_health

    def _defeat_entity(self, entity: Dict):
        """Handle entity defeat - award XP and loot, track win for decision-making"""
        current_persona = self.current_persona["name"]

        # Award experience
        xp_gained = entity["xp_reward"]
        self.player_experience += xp_gained

        # Track win for decision-making
        if current_persona not in self.avatar_wins:
            self.avatar_wins[current_persona] = 0
        self.avatar_wins[current_persona] += 1

        # Record duel outcome
        duel_record = {
            "persona": current_persona,
            "opponent": entity.get("name", "Unknown"),
            "outcome": "victory",
            "timestamp": datetime.now().isoformat(),
            "xp_gained": xp_gained
        }
        self.avatar_duels.append(duel_record)

        # Check level up
        while self.player_experience >= self.player_experience_to_next:
            self.player_experience -= self.player_experience_to_next
            self.player_level += 1
            self.player_max_health += 20
            self.player_health = self.player_max_health
            self.player_experience_to_next = int(self.player_experience_to_next * 1.5)
            self.add_message(f"⭐ LEVEL UP! Level {self.player_level} - Health: {self.player_max_health}")

        # Generate loot
        loot = self._generate_loot(entity)
        self.loot_inventory.append(loot)

        # Display defeat message
        rarity_color = self.rarity_colors[entity["loot_rarity"]]
        self.add_message(f"💀 DEFEATED: {entity['name']} (+{xp_gained} XP)")
        self.add_message(f"💎 LOOT: {loot['name']} [{entity['loot_rarity'].value.upper()}]")

        self.logger.info(f"💀 Defeated: {entity['name']} | XP: +{xp_gained} | Loot: {loot['name']}")

        # Check for decision-making trigger
        self._check_decision_making()

    def _generate_loot(self, entity: Dict) -> Dict:
        """Generate WoW-style loot based on entity rarity"""
        rarity = entity["loot_rarity"]
        rarity_color = self.rarity_colors[rarity]

        # Loot names based on rarity
        loot_names = {
            LootRarity.POOR: ["Junk Scrap", "Broken Component", "Worn Item"],
            LootRarity.COMMON: ["Standard Item", "Basic Component", "Common Resource"],
            LootRarity.UNCOMMON: ["Enhanced Item", "Quality Component", "Uncommon Resource"],
            LootRarity.RARE: ["Rare Artifact", "Precious Component", "Rare Resource"],
            LootRarity.EPIC: ["Epic Relic", "Legendary Component", "Epic Resource"],
            LootRarity.LEGENDARY: ["Legendary Artifact", "Mythic Component", "Legendary Resource"],
            LootRarity.ARTIFACT: ["Artifact of Power", "Divine Component", "Ultimate Resource"]
        }

        loot_name = random.choice(loot_names[rarity])

        return {
            "id": f"loot_{len(self.loot_inventory)}",
            "name": loot_name,
            "rarity": rarity,
            "color": rarity_color,
            "value": self._get_loot_value(rarity),
            "dropped_from": entity["name"],
            "timestamp": datetime.now().isoformat()
        }

    def _get_loot_value(self, rarity: LootRarity) -> int:
        """Get loot value based on rarity"""
        values = {
            LootRarity.POOR: 1,
            LootRarity.COMMON: 5,
            LootRarity.UNCOMMON: 25,
            LootRarity.RARE: 100,
            LootRarity.EPIC: 500,
            LootRarity.LEGENDARY: 2500,
            LootRarity.ARTIFACT: 10000
        }
        return values.get(rarity, 1)

    def activate_combat_mode(self):
        """Manually activate combat mode - FULL JEDI/SITH MODE"""
        self.combat_mode = True
        self.lightsaber_active = True
        self.set_phase(ActionPhase.COMBAT)
        self.wopr_stance_active = True
        self.next_wopr_stance()

        # Select target
        self._select_target()

        # Activate Jedi/Sith mode
        p = self.current_persona
        self.add_message(f"⚔️ {p['sw_archetype']} MODE: {p['lightsaber_form']} - {p['lightsaber_style']}")
        self.add_message(f"🔴 Lightsaber: {p['lightsaber_color']} | Alignment: {p['alignment']}")

        if self.target_entity:
            self.add_message(f"🎯 TARGET: {self.target_entity['name']} (HP: {self.target_entity['health']}/{self.target_entity['max_health']})")

        # Initialize combat animation
        self.combat_animation_frame = 0
        self.combat_action = "ready"  # ready, strike, block, dodge, special

        self.logger.info("⚔️  Combat Mode: ACTIVATED - FULL JEDI/SITH MODE")
        self.logger.info(f"🎮 WOPR Stance: {self.get_wopr_stance()['name']}")
        self.logger.info(f"⚔️  Lightsaber Form: {p['lightsaber_form']}")
        self.logger.info(f"🔴 Lightsaber Color: {p['lightsaber_color']}")
        self.logger.info(f"⭐ Alignment: {p['alignment']}")
        if self.target_entity:
            self.logger.info(f"🎯 Target: {self.target_entity['name']} (HP: {self.target_entity['health']}/{self.target_entity['max_health']})")

    def deactivate_combat_mode(self):
        """Deactivate combat mode"""
        self.combat_mode = False
        self.lightsaber_active = False
        self.ffa_active = False
        self.wopr_stance_active = False
        self.combat_action = None
        self.isometric_view = False
        if self.is_ace_mode:
            self.is_ace_mode = False
            self.ace_transformation_active = False
            self.transform_progress = 0.0
        self.set_phase(ActionPhase.IDLE)
        self.add_message("⚔️ Combat Mode: DEACTIVATED - Lightsaber deactivated")
        self.logger.info("⚔️  Combat Mode: DEACTIVATED")

    def _draw_lightsaber_combat(self, cx, cy, s, transform_alpha, p):
        """Draw lightsaber in Jedi/Sith combat mode - Street Fighter/DBZ style"""
        self.canvas.delete("lightsaber")

        # Get lightsaber properties from persona
        ls_color = p.get("lightsaber_color", p["primary"])
        ls_form = p.get("lightsaber_form", "Form I: Shii-Cho")
        alignment = p.get("alignment", "Jedi")

        # Lightsaber hilt (in hand)
        hand_x = cx + 30 * s * transform_alpha
        hand_y = cy + 50 * s * transform_alpha

        # Hilt (metallic)
        hilt_length = 15 * s
        self.canvas.create_rectangle(
            hand_x - 2, hand_y - hilt_length // 2,
            hand_x + 2, hand_y + hilt_length // 2,
            fill="#888888", outline="#aaaaaa", width=1, tags="lightsaber"
        )

        # Lightsaber blade angle based on combat action
        if self.combat_action == "strike":
            blade_angle = self.lightsaber_angle + 45  # Striking angle
        elif self.combat_action == "block":
            blade_angle = self.lightsaber_angle - 45  # Blocking angle
        elif self.combat_action == "dodge":
            blade_angle = self.lightsaber_angle + 90  # Dodging angle
        else:
            blade_angle = self.lightsaber_angle  # Ready stance

        # Convert angle to radians
        blade_rad = math.radians(blade_angle)

        # Lightsaber blade (glowing energy)
        blade_length = self.lightsaber_length * s * transform_alpha
        blade_end_x = hand_x + math.cos(blade_rad) * blade_length
        blade_end_y = hand_y + math.sin(blade_rad) * blade_length

        # Blade glow (outer glow)
        glow_width = 6
        self.canvas.create_line(
            hand_x, hand_y, blade_end_x, blade_end_y,
            fill=ls_color, width=glow_width + 4, tags="lightsaber"
        )

        # Blade core (bright center)
        self.canvas.create_line(
            hand_x, hand_y, blade_end_x, blade_end_y,
            fill="#ffffff", width=glow_width, tags="lightsaber"
        )

        # Lightsaber trail (Street Fighter/DBZ style motion blur)
        if self.combat_action in ["strike", "dodge"]:
            for i in range(3):
                trail_alpha = 0.3 * (1.0 - i / 3.0)
                trail_offset = i * 5
                trail_x1 = hand_x + math.cos(blade_rad) * trail_offset
                trail_y1 = hand_y + math.sin(blade_rad) * trail_offset
                trail_x2 = blade_end_x + math.cos(blade_rad) * trail_offset
                trail_y2 = blade_end_y + math.sin(blade_rad) * trail_offset

                # Convert color to rgba-like for trail
                r = int(ls_color[1:3], 16)
                g = int(ls_color[3:5], 16)
                b = int(ls_color[5:7], 16)
                trail_color = f"#{int(r*trail_alpha):02x}{int(g*trail_alpha):02x}{int(b*trail_alpha):02x}"

                self.canvas.create_line(
                    trail_x1, trail_y1, trail_x2, trail_y2,
                    fill=trail_color, width=glow_width - i, tags="lightsaber"
                )

        # Update lightsaber angle for animation
        self.lightsaber_angle += 5  # Rotate lightsaber

        # Combat action timing
        self.combat_action_timer += 1
        if self.combat_action_timer > 10:
            # Cycle combat actions
            actions = ["ready", "strike", "block", "dodge", "special"]
            current_idx = actions.index(self.combat_action) if self.combat_action in actions else 0
            self.combat_action = actions[(current_idx + 1) % len(actions)]
            self.combat_action_timer = 0

    def _draw_streetfighter_dbz_effects(self, cx, cy, s, transform_alpha, p):
        """Draw Street Fighter / Dragon Ball Z style combat effects"""
        self.canvas.delete("sf_dbz_effects")

        # Combat animation frame
        self.combat_animation_frame += 1

        # Impact effects (when striking)
        if self.combat_action == "strike":
            # Impact flash
            impact_x = cx + 40 * s
            impact_y = cy
            flash_size = 20 * s * (1.0 + math.sin(self.combat_animation_frame * 0.5))

            # Impact flash (white)
            self.canvas.create_oval(
                impact_x - flash_size, impact_y - flash_size,
                impact_x + flash_size, impact_y + flash_size,
                fill="#ffffff", outline="", tags="sf_dbz_effects"
            )

            # Impact particles (DBZ style)
            for i in range(8):
                particle_angle = (i * 45) + self.combat_animation_frame * 10
                particle_rad = math.radians(particle_angle)
                particle_dist = 30 * s + self.combat_animation_frame * 2
                particle_x = impact_x + math.cos(particle_rad) * particle_dist
                particle_y = impact_y + math.sin(particle_rad) * particle_dist

                self.canvas.create_oval(
                    particle_x - 3, particle_y - 3,
                    particle_x + 3, particle_y + 3,
                    fill=p["primary"], outline="", tags="sf_dbz_effects"
                )

        # Power aura (DBZ style - when charging)
        if self.combat_action == "special":
            aura_radius = 50 * s + math.sin(self.combat_animation_frame * 0.3) * 10 * s

            # Outer aura ring
            self.canvas.create_oval(
                cx - aura_radius, cy - aura_radius,
                cx + aura_radius, cy + aura_radius,
                outline=p["primary"], width=3, dash=(5, 5), tags="sf_dbz_effects"
            )

            # Inner energy core
            core_radius = 20 * s
            self.canvas.create_oval(
                cx - core_radius, cy - core_radius,
                cx + core_radius, cy + core_radius,
                fill=p["primary"], outline="#ffffff", width=2, tags="sf_dbz_effects"
            )

        # Speed lines (Street Fighter style - when dodging)
        if self.combat_action == "dodge":
            for i in range(5):
                line_x = cx - 30 * s - i * 10
                line_y1 = cy - 20 * s + i * 8
                line_y2 = cy + 20 * s - i * 8

                self.canvas.create_line(
                    line_x, line_y1, line_x - 10, line_y2,
                    fill=p["secondary"], width=2, tags="sf_dbz_effects"
                )

        # Block spark effects (when blocking)
        if self.combat_action == "block":
            block_x = cx + 20 * s
            block_y = cy

            # Block sparks
            for i in range(6):
                spark_angle = random.randint(0, 360)
                spark_rad = math.radians(spark_angle)
                spark_dist = 15 * s
                spark_x = block_x + math.cos(spark_rad) * spark_dist
                spark_y = block_y + math.sin(spark_rad) * spark_dist

                self.canvas.create_line(
                    block_x, block_y, spark_x, spark_y,
                    fill="#ffff00", width=1, tags="sf_dbz_effects"
                )

    def _draw_isometric_combat(self, cx, cy, s, transform_alpha, p):
        """Draw isometric action sequences (top-down combat view)"""
        self.canvas.delete("isometric")

        # Isometric view: 45-degree angle, scaled
        iso_scale = 0.7
        iso_angle = 45  # degrees

        # Character position in isometric space
        iso_x = cx
        iso_y = cy - 20 * s  # Slightly elevated

        # Draw character silhouette (isometric)
        char_width = 30 * s * iso_scale
        char_height = 40 * s * iso_scale

        # Character body (isometric diamond)
        iso_points = [
            iso_x, iso_y - char_height // 2,  # Top
            iso_x + char_width // 2, iso_y,  # Right
            iso_x, iso_y + char_height // 2,  # Bottom
            iso_x - char_width // 2, iso_y   # Left
        ]

        self.canvas.create_polygon(
            iso_points,
            fill=p["primary"], outline=p["secondary"], width=2,
            tags="isometric"
        )

        # Lightsaber in isometric view
        if self.lightsaber_active:
            ls_color = p.get("lightsaber_color", p["primary"])
            ls_angle_iso = self.lightsaber_angle + iso_angle
            ls_rad_iso = math.radians(ls_angle_iso)
            ls_length_iso = 40 * s * iso_scale

            ls_end_x_iso = iso_x + math.cos(ls_rad_iso) * ls_length_iso
            ls_end_y_iso = iso_y + math.sin(ls_rad_iso) * ls_length_iso

            # Lightsaber blade (isometric)
            self.canvas.create_line(
                iso_x, iso_y, ls_end_x_iso, ls_end_y_iso,
                fill=ls_color, width=4, tags="isometric"
            )
            self.canvas.create_line(
                iso_x, iso_y, ls_end_x_iso, ls_end_y_iso,
                fill="#ffffff", width=2, tags="isometric"
            )

        # Ground plane (isometric grid)
        for i in range(3):
            grid_y = cy + 30 * s + i * 10 * s
            grid_x1 = cx - 40 * s
            grid_x2 = cx + 40 * s

            # Isometric grid lines
            self.canvas.create_line(
                grid_x1, grid_y, grid_x2, grid_y,
                fill="#444444", width=1, dash=(2, 2), tags="isometric"
            )

    def _draw_combat_entities(self):
        """Draw combat entities (avatars, clones, PAs, monsters, elites, champions, bosses)"""
        self.canvas.delete("combat_entity")

        for entity in self.entities:
            if entity["defeated"]:
                continue

            x = entity["position"]["x"]
            y = entity["position"]["y"]

            # Entity type colors
            entity_colors = {
                EntityType.AVATAR: "#00ccff",
                EntityType.CLONE: "#888888",
                EntityType.PA: "#3366ff",
                EntityType.MONSTER: "#ff3333",
                EntityType.ELITE: "#ff6600",
                EntityType.CHAMPION: "#cc00ff",
                EntityType.BOSS: "#ff0000"
            }

            color = entity_colors.get(entity["type"], "#ffffff")
            size = {
                EntityType.AVATAR: 8,
                EntityType.CLONE: 6,
                EntityType.PA: 7,
                EntityType.MONSTER: 10,
                EntityType.ELITE: 12,
                EntityType.CHAMPION: 15,
                EntityType.BOSS: 20
            }.get(entity["type"], 8)

            # Draw entity (circle)
            self.canvas.create_oval(
                x - size, y - size,
                x + size, y + size,
                fill=color, outline="#ffffff", width=2, tags="combat_entity"
            )

            # Highlight target
            if self.target_entity and entity["id"] == self.target_entity["id"]:
                # Target indicator ring
                self.canvas.create_oval(
                    x - size - 5, y - size - 5,
                    x + size + 5, y + size + 5,
                    outline="#ffff00", width=2, dash=(3, 3), tags="combat_entity"
                )

    def _draw_health_bars(self):
        """Draw WoW-style health bars for player and target"""
        self.canvas.delete("health_bar")

        # Player health bar (top left)
        bar_x = 10
        bar_y = 10
        bar_width = 80
        bar_height = 8

        # Player health background
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            fill="#333333", outline="#ffffff", width=1, tags="health_bar"
        )

        # Player health fill
        health_percent = self.player_health / self.player_max_health
        health_width = int(bar_width * health_percent)
        health_color = "#00ff00" if health_percent > 0.5 else "#ffaa00" if health_percent > 0.25 else "#ff0000"

        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + health_width, bar_y + bar_height,
            fill=health_color, outline="", tags="health_bar"
        )

        # Player health text
        self.canvas.create_text(
            bar_x + bar_width // 2, bar_y - 10,
            text=f"Lv.{self.player_level} HP: {self.player_health}/{self.player_max_health}",
            fill="#ffffff", font=("Segoe UI", 7, "bold"), tags="health_bar"
        )

        # Target health bar (if target exists)
        if self.target_entity and not self.target_entity["defeated"]:
            target = self.target_entity
            target_x = target["position"]["x"]
            target_y = target["position"]["y"] - 20

            target_bar_width = 60
            target_bar_height = 6

            # Target health background
            self.canvas.create_rectangle(
                target_x - target_bar_width // 2, target_y,
                target_x + target_bar_width // 2, target_y + target_bar_height,
                fill="#333333", outline="#ffffff", width=1, tags="health_bar"
            )

            # Target health fill
            target_health_percent = target["health"] / target["max_health"]
            target_health_width = int(target_bar_width * target_health_percent)
            target_health_color = "#ff0000"  # Red for enemies

            self.canvas.create_rectangle(
                target_x - target_bar_width // 2, target_y,
                target_x - target_bar_width // 2 + target_health_width, target_y + target_bar_height,
                fill=target_health_color, outline="", tags="health_bar"
            )

            # Target name and health text
            entity_type_name = target["type"].value.upper()
            self.canvas.create_text(
                target_x, target_y - 12,
                text=f"{entity_type_name} {target['health']}/{target['max_health']}",
                fill="#ffffff", font=("Segoe UI", 6, "bold"), tags="health_bar"
            )

        # Loot inventory display (top right)
        if self.loot_inventory:
            loot_x = self.width - 10
            loot_y = 10
            recent_loot = self.loot_inventory[-5:]  # Show last 5 items

            for i, loot in enumerate(recent_loot):
                loot_text_y = loot_y + i * 12
                rarity_color = loot["color"]
                loot_text = f"{loot['name']} [{loot['rarity'].value.upper()}]"

                self.canvas.create_text(
                    loot_x, loot_text_y,
                    text=loot_text,
                    fill=rarity_color, font=("Segoe UI", 6, "bold"),
                    anchor=tk.E, tags="health_bar"
                )

        # Avatar lives display (bottom left)
        current_persona = self.current_persona["name"]
        lives = self.avatar_lives.get(current_persona, self.max_lives)
        lives_x = 10
        lives_y = self.height - 20

        # Lives indicator
        lives_color = "#00ff00" if lives > 1 else "#ffaa00" if lives == 1 else "#ff0000"
        lives_text = f"Lives: {lives}/{self.max_lives}"
        self.canvas.create_text(
            lives_x, lives_y,
            text=lives_text,
            fill=lives_color, font=("Segoe UI", 7, "bold"),
            anchor=tk.W, tags="health_bar"
        )

        # Wins/Losses display
        wins = self.avatar_wins.get(current_persona, 0)
        losses = self.avatar_losses.get(current_persona, 0)
        if wins + losses > 0:
            wl_text = f"W:{wins} L:{losses}"
            self.canvas.create_text(
                lives_x, lives_y - 12,
                text=wl_text,
                fill="#ffffff", font=("Segoe UI", 6),
                anchor=tk.W, tags="health_bar"
            )

    def toggle_isometric_view(self):
        """Toggle isometric combat view"""
        self.isometric_view = not self.isometric_view
        if self.isometric_view:
            self.add_message("📐 Isometric View: ACTIVATED - Top-down combat view")
            self.logger.info("📐 Isometric View: ACTIVATED")
        else:
            self.add_message("📐 Isometric View: DEACTIVATED")
            self.logger.info("📐 Isometric View: DEACTIVATED")

    def show_avatar_stats(self):
        """Display avatar lives, wins, and losses"""
        current_persona = self.current_persona["name"]
        lives = self.avatar_lives.get(current_persona, self.max_lives)
        wins = self.avatar_wins.get(current_persona, 0)
        losses = self.avatar_losses.get(current_persona, 0)

        self.add_message(f"👤 {current_persona} STATS:")
        self.add_message(f"   Lives: {lives}/{self.max_lives}")
        self.add_message(f"   Wins: {wins} | Losses: {losses}")
        if wins + losses > 0:
            win_rate = (wins / (wins + losses)) * 100
            self.add_message(f"   Win Rate: {win_rate:.1f}%")

        self.logger.info(f"👤 {current_persona} - Lives: {lives}/{self.max_lives}, W:{wins} L:{losses}")

    def run(self):
        """Start the GUI loop"""
        self.root.mainloop()


if __name__ == "__main__":
    assistant = IronmanBobbleheadGUI()
    assistant.run()
