#!/usr/bin/env python3
"""
Xbox Controller Mapping for LUMINA & Cursor IDE

Maps Xbox controller buttons to intuitive, peak-level functions for:
- LUMINA operations
- Cursor IDE navigation and commands
- Workflow execution
- Voice control

Human-intuitive mapping with ease of use at peak level.
"""

import sys
from pathlib import Path
from typing import Dict, Callable, Optional
from dataclasses import dataclass

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

try:
    from lumina_adaptive_logger import get_adaptive_logger
    get_logger = get_adaptive_logger
except ImportError:
    try:
        from lumina_logger import get_logger
    except ImportError:
        import logging
        logging.basicConfig(level=logging.INFO)
        get_logger = lambda name: logging.getLogger(name)

logger = get_logger("XboxController")


@dataclass
class ControllerAction:
    """Represents a controller button/trigger action"""
    name: str
    description: str
    handler: Callable
    enabled: bool = True


class XboxControllerMapper:
    """
    Maps Xbox controller inputs to LUMINA/Cursor IDE functions

    Provides human-intuitive, peak-level ease of use for:
    - Navigation
    - Command execution
    - Workflow control
    - Voice interaction
    """

    def __init__(self):
        self.mappings: Dict[str, ControllerAction] = {}
        self.running = False
        self.controller = None

        # Initialize controller library
        self._init_controller()

        # Setup default mappings
        self._setup_default_mappings()

        logger.info("✅ Xbox Controller Mapper initialized")

    def _init_controller(self):
        """Initialize controller input library"""
        try:
            import pygame
            pygame.init()
            pygame.joystick.init()

            # Check for connected controllers
            joystick_count = pygame.joystick.get_count()
            if joystick_count > 0:
                self.controller = pygame.joystick.Joystick(0)
                self.controller.init()
                logger.info(f"✅ Xbox Controller connected: {self.controller.get_name()}")
            else:
                logger.warning("⚠️  No controller detected")

        except ImportError:
            logger.error("pygame not installed - install with: pip install pygame")
            logger.info("Controller mapping will use keyboard simulation")
        except Exception as e:
            logger.error(f"Failed to initialize controller: {e}")

    def _setup_default_mappings(self):
        """Setup human-intuitive default button mappings"""

        # === FACE BUTTONS (Primary Actions) ===
        self.register_action(
            "A",  # Bottom button (Green)
            "Execute / Accept / Confirm",
            self._execute_action
        )

        self.register_action(
            "B",  # Right button (Red)
            "Cancel / Back / Undo",
            self._cancel_action
        )

        self.register_action(
            "X",  # Left button (Blue)
            "Open / Select / Context Menu",
            self._open_action
        )

        self.register_action(
            "Y",  # Top button (Yellow)
            "Quick Action / Search / Command Palette",
            self._quick_action
        )

        # === BUMPERS (Secondary Actions) ===
        self.register_action(
            "LB",  # Left Bumper
            "Previous Tab / Previous File",
            self._previous_tab
        )

        self.register_action(
            "RB",  # Right Bumper
            "Next Tab / Next File",
            self._next_tab
        )

        # === TRIGGERS (Modifiers / Continuous Actions) ===
        self.register_action(
            "LT",  # Left Trigger
            "Voice Input / Start Recording",
            self._voice_input
        )

        self.register_action(
            "RT",  # Right Trigger
            "Auto-Send / Execute Command",
            self._auto_send
        )

        # === D-PAD (Navigation) ===
        self.register_action(
            "DPAD_UP",
            "Scroll Up / Previous Line",
            self._scroll_up
        )

        self.register_action(
            "DPAD_DOWN",
            "Scroll Down / Next Line",
            self._scroll_down
        )

        self.register_action(
            "DPAD_LEFT",
            "Previous Word / Left",
            self._move_left
        )

        self.register_action(
            "DPAD_RIGHT",
            "Next Word / Right",
            self._move_right
        )

        # === STICKS (Precision Navigation) ===
        self.register_action(
            "LEFT_STICK",
            "Cursor Movement / Text Navigation",
            self._cursor_movement
        )

        self.register_action(
            "RIGHT_STICK",
            "Scroll / View Navigation",
            self._view_scroll
        )

        # === SPECIAL BUTTONS ===
        self.register_action(
            "BACK",  # View button
            "Toggle Sidebar / Explorer",
            self._toggle_sidebar
        )

        self.register_action(
            "START",  # Menu button
            "Command Palette / Quick Open",
            self._command_palette
        )

        self.register_action(
            "LEFT_STICK_CLICK",
            "Go to Definition / Jump to Definition",
            self._go_to_definition
        )

        self.register_action(
            "RIGHT_STICK_CLICK",
            "Find References / Show References",
            self._find_references
        )

        logger.info(f"✅ {len(self.mappings)} controller mappings registered")

    def register_action(
        self,
        button: str,
        description: str,
        handler: Callable,
        enabled: bool = True
    ):
        """Register a button mapping"""
        self.mappings[button] = ControllerAction(
            name=button,
            description=description,
            handler=handler,
            enabled=enabled
        )
        logger.debug(f"   Mapped {button}: {description}")

    # === ACTION HANDLERS ===

    def _execute_action(self):
        """A Button: Execute/Accept/Confirm"""
        logger.info("🎮 A Button: Execute/Accept")
        self._send_keyboard_shortcut("enter")
        # Also trigger auto-accept if available
        self._trigger_auto_accept()

    def _cancel_action(self):
        """B Button: Cancel/Back/Undo"""
        logger.info("🎮 B Button: Cancel/Back")
        self._send_keyboard_shortcut("escape")

    def _open_action(self):
        """X Button: Open/Select/Context Menu"""
        logger.info("🎮 X Button: Open/Select")
        self._send_keyboard_shortcut("f1")  # Command Palette alternative

    def _quick_action(self):
        """Y Button: Quick Action/Search"""
        logger.info("🎮 Y Button: Quick Action")
        self._send_keyboard_shortcut("ctrl+p")  # Quick Open

    def _previous_tab(self):
        """LB: Previous Tab"""
        logger.info("🎮 LB: Previous Tab")
        self._send_keyboard_shortcut("ctrl+pageup")

    def _next_tab(self):
        """RB: Next Tab"""
        logger.info("🎮 RB: Next Tab")
        self._send_keyboard_shortcut("ctrl+pagedown")

    def _voice_input(self):
        """LT: Voice Input"""
        logger.info("🎮 LT: Voice Input")
        # Trigger voice input (if available)
        self._send_keyboard_shortcut("ctrl+shift+v")  # Example shortcut

    def _auto_send(self):
        """RT: Auto-Send"""
        logger.info("🎮 RT: Auto-Send")
        self._send_keyboard_shortcut("enter")

    def _scroll_up(self):
        """DPAD UP: Scroll Up"""
        self._send_keyboard_shortcut("up")

    def _scroll_down(self):
        """DPAD DOWN: Scroll Down"""
        self._send_keyboard_shortcut("down")

    def _move_left(self):
        """DPAD LEFT: Move Left"""
        self._send_keyboard_shortcut("left")

    def _move_right(self):
        """DPAD RIGHT: Move Right"""
        self._send_keyboard_shortcut("right")

    def _cursor_movement(self, x: float, y: float):
        """LEFT STICK: Cursor Movement"""
        # Map stick movement to cursor/arrow keys
        if abs(x) > 0.3:
            if x > 0:
                self._send_keyboard_shortcut("right")
            else:
                self._send_keyboard_shortcut("left")
        if abs(y) > 0.3:
            if y > 0:
                self._send_keyboard_shortcut("down")
            else:
                self._send_keyboard_shortcut("up")

    def _view_scroll(self, x: float, y: float):
        """RIGHT STICK: View Scroll"""
        # Map stick movement to scroll
        if abs(y) > 0.3:
            if y > 0:
                self._send_keyboard_shortcut("pagedown")
            else:
                self._send_keyboard_shortcut("pageup")

    def _toggle_sidebar(self):
        """BACK: Toggle Sidebar"""
        logger.info("🎮 BACK: Toggle Sidebar")
        self._send_keyboard_shortcut("ctrl+b")

    def _command_palette(self):
        """START: Command Palette"""
        logger.info("🎮 START: Command Palette")
        self._send_keyboard_shortcut("ctrl+shift+p")

    def _go_to_definition(self):
        """LEFT STICK CLICK: Go to Definition"""
        logger.info("🎮 LEFT STICK CLICK: Go to Definition")
        self._send_keyboard_shortcut("f12")

    def _find_references(self):
        """RIGHT STICK CLICK: Find References"""
        logger.info("🎮 RIGHT STICK CLICK: Find References")
        self._send_keyboard_shortcut("shift+f12")

    def _send_keyboard_shortcut(self, shortcut: str):
        """Send keyboard shortcut"""
        try:
            import keyboard
            keyboard.press_and_release(shortcut)
        except ImportError:
            logger.warning("keyboard library not available")
        except Exception as e:
            logger.error(f"Failed to send shortcut {shortcut}: {e}")

    def _trigger_auto_accept(self):
        """Trigger auto-accept if available"""
        try:
            from cursor_ide_auto_accept import auto_accept_all_changes
            auto_accept_all_changes()
        except ImportError:
            pass  # Auto-accept not available

    def start_monitoring(self):
        """Start monitoring controller input"""
        if not self.controller:
            logger.warning("⚠️  No controller connected - cannot monitor")
            return

        self.running = True
        logger.info("🎮 Starting controller monitoring...")

        try:
            import pygame

            clock = pygame.time.Clock()
            while self.running:
                for event in pygame.event.get():
                    if event.type == pygame.JOYBUTTONDOWN:
                        self._handle_button_press(event.button)
                    elif event.type == pygame.JOYAXISMOTION:
                        self._handle_axis_motion(event.axis, event.value)
                    elif event.type == pygame.JOYHATMOTION:
                        self._handle_hat_motion(event.hat, event.value)

                clock.tick(60)  # 60 FPS

        except Exception as e:
            logger.error(f"Error in controller monitoring: {e}")

    def _handle_button_press(self, button: int):
        """Handle button press event"""
        # Map button numbers to names (Xbox controller)
        button_map = {
            0: "A",
            1: "B",
            2: "X",
            3: "Y",
            4: "LB",
            5: "RB",
            6: "BACK",
            7: "START",
            8: "LEFT_STICK_CLICK",
            9: "RIGHT_STICK_CLICK"
        }

        button_name = button_map.get(button)
        if button_name and button_name in self.mappings:
            action = self.mappings[button_name]
            if action.enabled:
                action.handler()

    def _handle_axis_motion(self, axis: int, value: float):
        """Handle analog stick/trigger motion"""
        # Left stick: axis 0 (X), 1 (Y)
        # Right stick: axis 3 (X), 4 (Y)
        # Triggers: axis 2 (LT), 5 (RT)

        if axis == 0 or axis == 1:  # Left stick
            if abs(value) > 0.3:
                self._cursor_movement(
                    value if axis == 0 else 0,
                    value if axis == 1 else 0
                )
        elif axis == 3 or axis == 4:  # Right stick
            if abs(value) > 0.3:
                self._view_scroll(
                    value if axis == 3 else 0,
                    value if axis == 4 else 0
                )
        elif axis == 2:  # Left Trigger
            if value > 0.5:
                self._voice_input()
        elif axis == 5:  # Right Trigger
            if value > 0.5:
                self._auto_send()

    def _handle_hat_motion(self, hat: int, value: tuple):
        """Handle D-pad motion"""
        x, y = value
        if y == 1:
            self._scroll_up()
        elif y == -1:
            self._scroll_down()
        if x == -1:
            self._move_left()
        elif x == 1:
            self._move_right()

    def stop_monitoring(self):
        """Stop monitoring controller input"""
        self.running = False
        logger.info("⏹️  Controller monitoring stopped")

    def get_mappings(self) -> Dict[str, str]:
        """Get all current mappings as description dict"""
        return {
            button: action.description
            for button, action in self.mappings.items()
        }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Xbox Controller Mapper for LUMINA")
    parser.add_argument("--list", action="store_true", help="List all mappings")
    parser.add_argument("--start", action="store_true", help="Start monitoring")

    args = parser.parse_args()

    mapper = XboxControllerMapper()

    if args.list:
        print("\n🎮 Xbox Controller Mappings:")
        print("=" * 60)
        for button, description in mapper.get_mappings().items():
            print(f"  {button:20s} → {description}")
        print("=" * 60)

    if args.start:
        mapper.start_monitoring()


if __name__ == "__main__":


    main()