#!/usr/bin/env python3
"""
Show VAs Persistently - Always Visible

Shows Virtual Assistants in a persistent window that stays on screen.

Tags: #PERSISTENT #ALWAYS_VISIBLE #DESKTOP_OVERLAY @JARVIS @LUMINA
"""

import sys
import threading
import time
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from va_visibility_system import VAVisibilitySystem
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from va_desktop_visualization import VADesktopVisualization
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("ShowVAsPersistent")


def create_persistent_window():
    """Create persistent window showing all VAs"""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        logger.error("tkinter not available")
        return False

    print("=" * 80)
    print("🖥️  CREATING PERSISTENT VA WINDOW")
    print("=" * 80)
    print()

    # Initialize VAs
    visibility = VAVisibilitySystem()
    visibility.ensure_iron_man_vas_visible()
    visibility.show_all_vas()

    registry = CharacterAvatarRegistry()
    viz = VADesktopVisualization(registry)
    vas = registry.get_characters_by_type(CharacterType.VIRTUAL_ASSISTANT)

    # Create window
    root = tk.Tk()
    root.title("LUMINA Virtual Assistants - Always Visible")
    root.geometry("400x600")
    root.configure(bg='#1e1e1e')

    # Make window stay on top
    root.attributes('-topmost', True)

    # Position in top-right corner
    root.geometry("+1400+50")

    # Header
    header = tk.Label(
        root,
        text="🦾 LUMINA Virtual Assistants",
        font=('Arial', 16, 'bold'),
        bg='#1e1e1e',
        fg='#4fc3f7'
    )
    header.pack(pady=10)

    # Create frame for VAs
    va_frame = tk.Frame(root, bg='#1e1e1e')
    va_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    # Create cards for each VA
    va_cards = {}

    def update_va_status():
        """Update VA status periodically"""
        for va in vas:
            if va.character_id in va_cards:
                card = va_cards[va.character_id]
                widgets = viz.get_va_widgets(va.character_id)

                # Update status label
                status_text = f"✅ Active - {len(widgets)} widget(s)"
                if hasattr(card, 'status_label'):
                    card.status_label.config(text=status_text)

        # Schedule next update
        root.after(5000, update_va_status)

    for i, va in enumerate(vas):
        # Card frame
        card = tk.Frame(va_frame, bg='#2d2d2d', relief=tk.RAISED, borderwidth=2)
        card.pack(fill=tk.X, padx=5, pady=5)

        # VA name
        name_color = '#4fc3f7' if va.character_id in ['jarvis_va', 'imva'] else '#81c784'
        name_label = tk.Label(
            card,
            text=va.name,
            font=('Arial', 12, 'bold'),
            bg='#2d2d2d',
            fg=name_color
        )
        name_label.pack(pady=5)

        # VA role
        role_label = tk.Label(
            card,
            text=va.role,
            font=('Arial', 9),
            bg='#2d2d2d',
            fg='#b0bec5'
        )
        role_label.pack()

        # Status
        widgets = viz.get_va_widgets(va.character_id)
        status_label = tk.Label(
            card,
            text=f"✅ Active - {len(widgets)} widget(s)",
            font=('Arial', 9, 'bold'),
            bg='#2d2d2d',
            fg='#66bb6a'
        )
        status_label.pack(pady=5)
        card.status_label = status_label  # Store for updates

        va_cards[va.character_id] = card

        print(f"  ✅ Created card for {va.name}")

    # Start status updates
    root.after(5000, update_va_status)

    print()
    print("=" * 80)
    print("✅ PERSISTENT VA WINDOW CREATED")
    print("=" * 80)
    print()
    print("Window is now visible and will stay on top.")
    print("All Virtual Assistants are displayed!")
    print()
    print("VAs visible:")
    for va in vas:
        print(f"  ✅ {va.name} ({va.character_id})")
    print()

    # Keep window open
    root.mainloop()

    return True


def main():
    """Main function"""
    try:
        if create_persistent_window():
            return 0
        else:
            print("❌ Could not create persistent window")
            return 1
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()