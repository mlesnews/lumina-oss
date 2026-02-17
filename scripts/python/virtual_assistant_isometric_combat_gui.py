#!/usr/bin/env python3
"""
Virtual Assistant Isometric Combat GUI

Visual display for 3D isometric top-down combat system.
Uses Pygame for rendering (falls back to tkinter if unavailable).

Tags: #virtual_assistant #gaming #isometric #3d #combat #gui #visualization
"""

import sys
import math
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import logging

script_dir = Path(__file__).parent
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from lumina_logger import get_logger
except ImportError:
    logging.basicConfig(level=logging.INFO)
    get_logger = lambda name: logging.getLogger(name)

logger = get_logger("IsometricCombatGUI")

# Try pygame first
try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    logger.warning("⚠️  Pygame not available")

# Fallback to tkinter
try:
    import tkinter as tk
    from tkinter import Canvas
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False
    logger.warning("⚠️  Tkinter not available")

from virtual_assistant_isometric_combat import (
    VirtualAssistantIsometricCombat,
    Fighter,
    CombatAction,
    Direction
)


class IsometricCombatGUI:
    """
    Visual GUI for isometric combat system
    """

    def __init__(self, combat_system: VirtualAssistantIsometricCombat):
        self.combat = combat_system
        self.running = False

        if PYGAME_AVAILABLE:
            self._init_pygame()
        elif TKINTER_AVAILABLE:
            self._init_tkinter()
        else:
            logger.error("❌ No graphics library available")
            raise RuntimeError("No graphics library available (pygame or tkinter)")

    def _init_pygame(self):
        """Initialize Pygame GUI"""
        pygame.init()

        self.screen_width = 1024
        self.screen_height = 768
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Virtual Assistant Isometric Combat")

        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)

        # Colors
        self.bg_color = (20, 20, 30)
        self.grid_color = (50, 50, 70)
        self.text_color = (255, 255, 255)

        logger.info("✅ Pygame GUI initialized")

    def _init_tkinter(self):
        """Initialize Tkinter GUI"""
        self.root = tk.Tk()
        self.root.title("Virtual Assistant Isometric Combat")

        self.canvas_width = 1024
        self.canvas_height = 768
        self.canvas = Canvas(
            self.root,
            width=self.canvas_width,
            height=self.canvas_height,
            bg="#14141e"
        )
        self.canvas.pack()

        logger.info("✅ Tkinter GUI initialized")

    def draw_fighter_pygame(self, fighter: Fighter, screen_x: int, screen_y: int):
        """Draw fighter using Pygame"""
        # Draw fighter as colored circle
        color = fighter.color
        radius = 20

        # Draw shadow
        pygame.draw.circle(self.screen, (0, 0, 0, 100), (screen_x, screen_y + 5), radius + 2)

        # Draw fighter
        pygame.draw.circle(self.screen, color, (screen_x, screen_y), radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (screen_x, screen_y), radius, 2)

        # Draw health bar
        bar_width = 40
        bar_height = 4
        bar_x = screen_x - bar_width // 2
        bar_y = screen_y - radius - 10

        # Background
        pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))

        # Health
        health_percent = fighter.stats.health / fighter.stats.max_health
        health_width = int(bar_width * health_percent)
        health_color = (0, 255, 0) if health_percent > 0.5 else (255, 255, 0) if health_percent > 0.25 else (255, 0, 0)
        pygame.draw.rect(self.screen, health_color, (bar_x, bar_y, health_width, bar_height))

        # Name
        name_surface = self.small_font.render(fighter.name, True, self.text_color)
        name_rect = name_surface.get_rect(center=(screen_x, screen_y + radius + 15))
        self.screen.blit(name_surface, name_rect)

    def draw_fighter_tkinter(self, fighter: Fighter, screen_x: int, screen_y: int):
        """Draw fighter using Tkinter"""
        # Convert to canvas coordinates (center origin)
        canvas_x = self.canvas_width // 2 + screen_x
        canvas_y = self.canvas_height // 2 + screen_y

        radius = 20
        color = f"#{fighter.color[0]:02x}{fighter.color[1]:02x}{fighter.color[2]:02x}"

        # Draw shadow
        self.canvas.create_oval(
            canvas_x - radius - 2, canvas_y + 5 - radius - 2,
            canvas_x + radius + 2, canvas_y + 5 + radius + 2,
            fill="#000000", outline=""
        )

        # Draw fighter
        self.canvas.create_oval(
            canvas_x - radius, canvas_y - radius,
            canvas_x + radius, canvas_y + radius,
            fill=color, outline="#ffffff", width=2
        )

        # Draw health bar
        bar_width = 40
        bar_height = 4
        bar_x = canvas_x - bar_width // 2
        bar_y = canvas_y - radius - 10

        health_percent = fighter.stats.health / fighter.stats.max_health
        health_width = bar_width * health_percent

        # Background
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + bar_width, bar_y + bar_height,
            fill="#323232", outline=""
        )

        # Health
        health_color = "#00ff00" if health_percent > 0.5 else "#ffff00" if health_percent > 0.25 else "#ff0000"
        self.canvas.create_rectangle(
            bar_x, bar_y, bar_x + health_width, bar_y + bar_height,
            fill=health_color, outline=""
        )

        # Name
        self.canvas.create_text(
            canvas_x, canvas_y + radius + 15,
            text=fighter.name, fill="#ffffff", font=("Arial", 10)
        )

    def draw_grid_pygame(self):
        """Draw isometric grid using Pygame"""
        # Draw grid lines for isometric view
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        grid_size = 50
        grid_range = 20

        for i in range(-grid_range, grid_range):
            for j in range(-grid_range, grid_range):
                x, y = self.combat.projection.world_to_screen(i, j, 0)
                screen_x = center_x + x
                screen_y = center_y + y

                if 0 <= screen_x < self.screen_width and 0 <= screen_y < self.screen_height:
                    pygame.draw.circle(self.screen, self.grid_color, (screen_x, screen_y), 2)

    def draw_grid_tkinter(self):
        """Draw isometric grid using Tkinter"""
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2

        grid_size = 50
        grid_range = 20

        for i in range(-grid_range, grid_range):
            for j in range(-grid_range, grid_range):
                x, y = self.combat.projection.world_to_screen(i, j, 0)
                canvas_x = center_x + x
                canvas_y = center_y + y

                if 0 <= canvas_x < self.canvas_width and 0 <= canvas_y < self.canvas_height:
                    self.canvas.create_oval(
                        canvas_x - 2, canvas_y - 2,
                        canvas_x + 2, canvas_y + 2,
                        fill="#323246", outline=""
                    )

    def render_pygame(self):
        """Render frame using Pygame"""
        self.screen.fill(self.bg_color)

        # Draw grid
        self.draw_grid_pygame()

        # Draw fighters
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2

        for fighter in self.combat.fighters.values():
            if fighter.is_alive:
                screen_x = center_x + fighter.isometric_position[0]
                screen_y = center_y + fighter.isometric_position[1]
                self.draw_fighter_pygame(fighter, screen_x, screen_y)

        # Draw UI
        y_offset = 10
        ui_text = [
            f"Round: {self.combat.current_round}",
            f"Time: {self.combat.round_time:.1f}s",
            f"Fighters: {len([f for f in self.combat.fighters.values() if f.is_alive])}"
        ]

        for text in ui_text:
            text_surface = self.font.render(text, True, self.text_color)
            self.screen.blit(text_surface, (10, y_offset))
            y_offset += 30

        # Draw fighter stats
        x_offset = self.screen_width - 250
        y_offset = 10

        for fighter in self.combat.fighters.values():
            if fighter.is_alive:
                stats_text = [
                    f"{fighter.name}:",
                    f"  HP: {fighter.stats.health}/{fighter.stats.max_health}",
                    f"  Energy: {fighter.stats.energy}/{fighter.stats.max_energy}",
                    f"  Action: {fighter.current_action.value}"
                ]

                for text in stats_text:
                    text_surface = self.small_font.render(text, True, self.text_color)
                    self.screen.blit(text_surface, (x_offset, y_offset))
                    y_offset += 20
                y_offset += 10

        pygame.display.flip()

    def render_tkinter(self):
        """Render frame using Tkinter"""
        self.canvas.delete("all")

        # Draw grid
        self.draw_grid_tkinter()

        # Draw fighters
        center_x = self.canvas_width // 2
        center_y = self.canvas_height // 2

        for fighter in self.combat.fighters.values():
            if fighter.is_alive:
                screen_x = fighter.isometric_position[0]
                screen_y = fighter.isometric_position[1]
                self.draw_fighter_tkinter(fighter, screen_x, screen_y)

        # Draw UI text
        ui_text = [
            f"Round: {self.combat.current_round}",
            f"Time: {self.combat.round_time:.1f}s",
            f"Fighters: {len([f for f in self.combat.fighters.values() if f.is_alive])}"
        ]

        y_offset = 20
        for text in ui_text:
            self.canvas.create_text(
                10, y_offset, anchor="w",
                text=text, fill="#ffffff", font=("Arial", 12)
            )
            y_offset += 25

        # Draw fighter stats
        x_offset = self.canvas_width - 250
        y_offset = 20

        for fighter in self.combat.fighters.values():
            if fighter.is_alive:
                stats_text = [
                    f"{fighter.name}:",
                    f"  HP: {fighter.stats.health}/{fighter.stats.max_health}",
                    f"  Energy: {fighter.stats.energy}/{fighter.stats.max_energy}",
                    f"  Action: {fighter.current_action.value}"
                ]

                for text in stats_text:
                    self.canvas.create_text(
                        x_offset, y_offset, anchor="w",
                        text=text, fill="#ffffff", font=("Arial", 10)
                    )
                    y_offset += 18
                y_offset += 10

        self.canvas.update()

    def run_pygame(self):
        """Run Pygame main loop"""
        self.running = True

        while self.running:
            delta_time = self.clock.tick(60) / 1000.0

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False

            # Update combat
            if self.combat.is_running:
                self.combat.update(delta_time)

            # Render
            self.render_pygame()

        pygame.quit()

    def run_tkinter(self):
        """Run Tkinter main loop"""
        self.running = True

        def update():
            if self.running:
                delta_time = 0.016  # ~60 FPS

                # Update combat
                if self.combat.is_running:
                    self.combat.update(delta_time)

                # Render
                self.render_tkinter()

                # Schedule next update
                self.root.after(16, update)

        def on_closing():
            self.running = False
            self.root.destroy()

        self.root.protocol("WM_DELETE_WINDOW", on_closing)
        update()
        self.root.mainloop()

    def run(self):
        """Run GUI"""
        if PYGAME_AVAILABLE:
            self.run_pygame()
        elif TKINTER_AVAILABLE:
            self.run_tkinter()
        else:
            logger.error("❌ No graphics library available")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Virtual Assistant Isometric Combat GUI")
    parser.add_argument('--fighters', nargs='+', metavar='FIGHTER_ID', 
                       help='Fighter IDs to include in combat')

    args = parser.parse_args()

    # Create combat system
    combat = VirtualAssistantIsometricCombat()

    # Start combat
    combat.start_combat(args.fighters)

    # Create and run GUI
    try:
        gui = IsometricCombatGUI(combat)
        gui.run()
    except RuntimeError as e:
        logger.error(f"❌ GUI Error: {e}")
        logger.info("💡 Install pygame: pip install pygame")
        logger.info("   Or use tkinter (usually included with Python)")


if __name__ == "__main__":


    main()