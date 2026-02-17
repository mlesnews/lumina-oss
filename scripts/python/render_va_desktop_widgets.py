#!/usr/bin/env python3
"""
Render VA Desktop Widgets - Actual Visual Display

Actually renders VA widgets on desktop using a GUI framework.
This makes VAs visible on screen.

Tags: #RENDERING #GUI #VISUALIZATION #DESKTOP_WIDGETS @JARVIS @LUMINA
"""

import sys
from pathlib import Path

script_dir = Path(__file__).parent
project_root = script_dir.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
if str(script_dir) not in sys.path:
    sys.path.insert(0, str(script_dir))

try:
    from va_visibility_system import VAVisibilitySystem
    from va_desktop_visualization import (VADesktopVisualization, WidgetType, VFXType)
    from character_avatar_registry import CharacterAvatarRegistry, CharacterType
    from lumina_logger import get_logger
except ImportError as e:
    import logging
    logging.basicConfig(level=logging.ERROR)
    print(f"❌ Import error: {e}")
    sys.exit(1)

logger = get_logger("RenderVAWidgets")


def render_with_tkinter(visibility_system=None):
    """Render VA widgets using tkinter with drag-and-drop, resize, animations, grouping, and themes"""
    try:
        import tkinter as tk
        from tkinter import ttk
    except ImportError:
        logger.error("tkinter not available")
        return False

    print("=" * 80)
    print("🖥️  RENDERING VA WIDGETS ON DESKTOP")
    print("=" * 80)
    print()
    print("Creating desktop widgets for all VAs...")
    print()

    # Reuse existing visibility system or create new one
    if visibility_system is None:
        visibility = VAVisibilitySystem()
        visibility.show_all_vas()
        registry = visibility.registry
        viz = visibility.viz
        vas = visibility.vas
    else:
        visibility = visibility_system
        # Only show VAs if they haven't been shown yet
        existing_widgets = sum(len(visibility.viz.get_va_widgets(va.character_id)) for va in visibility.vas)
        if existing_widgets == 0:
            visibility.show_all_vas()
        registry = visibility.registry
        viz = visibility.viz
        vas = visibility.vas

    # Create main window
    root = tk.Tk()
    root.title("LUMINA Virtual Assistants - Enhanced")
    root.geometry("1400x900")
    root.configure(bg='#1e1e1e')

    # Store widget frames for drag/resize
    widget_frames = {}
    drag_data = {"widget": None, "x": 0, "y": 0}
    resize_data = {"widget": None, "corner": None, "x": 0, "y": 0}

    def start_drag(event, widget_id):
        """Start dragging a widget"""
        if widget_id in widget_frames:
            widget = viz.widgets.get(widget_id)
            if widget and widget.draggable:
                drag_data["widget"] = widget_id
                drag_data["x"] = event.x_root
                drag_data["y"] = event.y_root

                # RECORD DRAG START FOR EYE TRACKING FINE-TUNING
                try:
                    from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
                    movement_system = get_va_movement_fine_tuning()
                    va_char = registry.get_character(widget.va_id)
                    va_name = va_char.name if va_char else widget.va_id
                    start_x = widget.position.get("x", 0)
                    start_y = widget.position.get("y", 0)
                    movement_system.record_movement(
                        va_id=widget.va_id,
                        va_name=va_name,
                        movement_type=MovementType.DRAG_START,
                        screen_position=(start_x, start_y),
                        window_size=(widget.size.get("width", 0), widget.size.get("height", 0)),
                        context={"widget_id": widget_id, "widget_type": widget.widget_type.value}
                    )
                except (ImportError, Exception):
                    pass  # Fine-tuning system not available

    def on_drag(event, widget_id):
        """Handle widget dragging"""
        if drag_data["widget"] == widget_id:
            dx = event.x_root - drag_data["x"]
            dy = event.y_root - drag_data["y"]

            widget = viz.widgets.get(widget_id)
            if widget:
                new_x = widget.position["x"] + dx
                new_y = widget.position["y"] + dy

                # Keep within screen bounds
                new_x = max(0, min(new_x, root.winfo_width() - widget.size["width"]))
                new_y = max(0, min(new_y, root.winfo_height() - widget.size["height"]))

                viz.update_widget_position(widget_id, {"x": new_x, "y": new_y})

                if widget_id in widget_frames:
                    frame = widget_frames[widget_id]["frame"]
                    frame.place(x=new_x, y=new_y)

                # RECORD MOVEMENT FOR EYE TRACKING FINE-TUNING
                # User moved VA widget - they were looking at it, valuable learning data!
                try:
                    from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
                    movement_system = get_va_movement_fine_tuning()
                    va_char = registry.get_character(widget.va_id)
                    va_name = va_char.name if va_char else widget.va_id
                    movement_system.record_movement(
                        va_id=widget.va_id,
                        va_name=va_name,
                        movement_type=MovementType.DRAG_MOVE,
                        screen_position=(new_x, new_y),
                        window_size=(widget.size.get("width", 0), widget.size.get("height", 0)),
                        context={"widget_id": widget_id, "widget_type": widget.widget_type.value}
                    )
                except (ImportError, Exception) as e:
                    pass  # Fine-tuning system not available or error

            drag_data["x"] = event.x_root
            drag_data["y"] = event.y_root

    def stop_drag(event, widget_id):
        """Stop dragging"""
        if drag_data["widget"] == widget_id:
            # RECORD DRAG END FOR EYE TRACKING FINE-TUNING
            widget = viz.widgets.get(widget_id)
            if widget:
                try:
                    from va_movement_fine_tuning import get_va_movement_fine_tuning, MovementType
                    movement_system = get_va_movement_fine_tuning()
                    va_char = registry.get_character(widget.va_id)
                    va_name = va_char.name if va_char else widget.va_id
                    final_x = widget.position.get("x", 0)
                    final_y = widget.position.get("y", 0)
                    movement_system.record_movement(
                        va_id=widget.va_id,
                        va_name=va_name,
                        movement_type=MovementType.DRAG_END,
                        screen_position=(final_x, final_y),
                        window_size=(widget.size.get("width", 0), widget.size.get("height", 0)),
                        context={"widget_id": widget_id, "was_dragging": True}
                    )
                except (ImportError, Exception):
                    pass  # Fine-tuning system not available

            drag_data["widget"] = None

    def start_resize(event, widget_id, corner):
        """Start resizing a widget"""
        if widget_id in widget_frames:
            widget = viz.widgets.get(widget_id)
            if widget and widget.resizable:
                resize_data["widget"] = widget_id
                resize_data["corner"] = corner
                resize_data["x"] = event.x_root
                resize_data["y"] = event.y_root

    def on_resize(event, widget_id):
        """Handle widget resizing"""
        if resize_data["widget"] == widget_id:
            dx = event.x_root - resize_data["x"]
            dy = event.y_root - resize_data["y"]

            widget = viz.widgets.get(widget_id)
            if widget:
                new_width = widget.size["width"]
                new_height = widget.size["height"]

                corner = resize_data.get("corner", "")
                if corner and "right" in str(corner):
                    new_width += dx
                if corner and "left" in str(corner):
                    new_width -= dx
                    if new_width > 0:
                        widget.position["x"] += dx
                if corner and "bottom" in str(corner):
                    new_height += dy
                if corner and "top" in str(corner):
                    new_height -= dy
                    if new_height > 0:
                        widget.position["y"] += dy

                viz.update_widget_size(widget_id, {"width": new_width, "height": new_height})

                if widget_id in widget_frames:
                    frame = widget_frames[widget_id]["frame"]
                    frame.place(width=new_width, height=new_height)

            resize_data["x"] = event.x_root
            resize_data["y"] = event.y_root

    def stop_resize(event, widget_id):
        """Stop resizing"""
        if resize_data["widget"] == widget_id:
            resize_data["widget"] = None

    def toggle_collapse(widget_id):
        """Toggle widget collapse"""
        viz.toggle_widget_collapse(widget_id)
        if widget_id in widget_frames:
            refresh_widget_display(widget_id)

    def refresh_widget_display(widget_id):
        """Refresh widget display after state change"""
        if widget_id not in widget_frames:
            return

        widget = viz.widgets.get(widget_id)
        if not widget:
            return

        frame_data = widget_frames[widget_id]
        frame = frame_data["frame"]
        content_frame = frame_data.get("content_frame")

        if widget.collapsed:
            # Show collapsed view
            if content_frame:
                content_frame.pack_forget()
            if "collapse_label" not in frame_data:
                collapse_label = tk.Label(
                    frame,
                    text="▶ Collapsed",
                    font=('Arial', 10),
                    bg=frame.cget('bg'),
                    fg='#90a4ae',
                    cursor='hand2'
                )
                collapse_label.pack()
                collapse_label.bind("<Button-1>", lambda e: toggle_collapse(widget_id))
                frame_data["collapse_label"] = collapse_label
        else:
            # Show expanded view
            if "collapse_label" in frame_data:
                frame_data["collapse_label"].pack_forget()
            if content_frame:
                content_frame.pack(fill=tk.BOTH, expand=True)

    # Create widgets for each VA
    widgets_created = []

    # Track widget positions to prevent overlaps
    used_positions = []

    # First, render DEFCON widgets (they should be on top)
    defcon_widgets = viz.get_defcon_widgets()
    for defcon_widget in defcon_widgets:
        if defcon_widget.visible:
            # Get WOPR character for DEFCON widget
            wopr_char = registry.get_character("wopr")
            if not wopr_char:
                # Create placeholder character for WOPR
                from character_avatar_registry import CharacterAvatar, CharacterType
                wopr_char = CharacterAvatar(
                    character_id="wopr",
                    name="WOPR",
                    character_type=CharacterType.INANIMATE_OBJECT,
                    primary_color="#ff0000",
                    secondary_color="#ff6600",
                    avatar_style="system",
                    avatar_template="wopr_widget",
                    role="Strategic Planning & Simulation System"
                )

            # Render DEFCON widget (treat as VA for rendering)
            va = wopr_char
            widget = defcon_widget
            i = len(vas)  # Place after VAs

            # Get theme colors
            theme_name = widget.theme or "default"
            theme_colors = viz.get_theme_colors(theme_name)

            # Use red theme for DEFCON
            bg_color = '#1a1a1a'
            fg_color = '#ffffff'
            border_color = widget.properties.get("defcon_color", "#ff0000")

            # Create draggable frame
            outer_frame = tk.Frame(
                root,
                bg=border_color,
                padx=2,
                pady=2,
                relief=tk.RAISED,
                borderwidth=2
            )

            widget_frames[widget.widget_id] = {
                "frame": outer_frame,
                "widget": widget
            }

            # Position
            x = widget.position.get("x", 1800)
            y = widget.position.get("y", 20)
            width = widget.size.get("width", 80)
            height = widget.size.get("height", 200)

            # Place widget
            outer_frame.place(x=x, y=y, width=width, height=height)
            outer_frame.lift()  # Always on top

            # Make draggable
            if widget.draggable:
                outer_frame.bind("<Button-1>", lambda e, wid=widget.widget_id: start_drag(e, wid))
                outer_frame.bind("<B1-Motion>", lambda e, wid=widget.widget_id: on_drag(e, wid))
                outer_frame.bind("<ButtonRelease-1>", lambda e, wid=widget.widget_id: stop_drag(e, wid))
                outer_frame.configure(cursor="hand2")

            # Create inner frame
            frame = tk.Frame(outer_frame, bg=bg_color, relief=tk.FLAT)
            frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            content_frame = tk.Frame(frame, bg=bg_color)
            if not widget.collapsed:
                content_frame.pack(fill=tk.BOTH, expand=True)

            # Collapse button
            collapse_btn = tk.Button(
                frame,
                text="−" if not widget.collapsed else "+",
                font=('Arial', 10, 'bold'),
                bg=bg_color,
                fg=fg_color,
                relief=tk.FLAT,
                command=lambda wid=widget.widget_id: toggle_collapse(wid),
                cursor='hand2'
            )
            collapse_btn.pack(anchor='ne', padx=2, pady=2)

            # DEFCON streetlight rendering (same as above)
            defcon_level = widget.properties.get("defcon_level", 5)
            defcon_color = widget.properties.get("defcon_color", "#00ccff")
            alerts_count = len(widget.properties.get("alerts", []))
            problems_count = len(widget.properties.get("problems", []))

            # Title
            title_label = tk.Label(
                content_frame,
                text="🚦 DEFCON",
                font=('Arial', 10, 'bold'),
                bg=bg_color,
                fg=fg_color
            )
            title_label.pack(pady=2)

            # DEFCON level indicator
            defcon_frame = tk.Frame(content_frame, bg=bg_color)
            defcon_frame.pack(pady=5)

            for level in range(5, 0, -1):
                light_color = "#333333"
                if level <= defcon_level:
                    if level == 1:
                        light_color = "#ff0000"
                    elif level == 2:
                        light_color = "#ff6600"
                    elif level == 3:
                        light_color = "#ffcc00"
                    elif level == 4:
                        light_color = "#00ff00"
                    else:
                        light_color = "#00ccff"

                light = tk.Label(
                    defcon_frame,
                    text="●",
                    font=('Arial', 16, 'bold'),
                    bg=bg_color,
                    fg=light_color
                )
                light.pack(pady=1)

            # DEFCON level text
            level_label = tk.Label(
                content_frame,
                text=f"LEVEL {defcon_level}",
                font=('Arial', 12, 'bold'),
                bg=bg_color,
                fg=defcon_color
            )
            level_label.pack(pady=2)

            # Status
            if alerts_count > 0 or problems_count > 0:
                status_text = f"⚠️ {alerts_count} alerts, {problems_count} problems"
                status_color = "#ff0000" if defcon_level <= 2 else "#ffcc00"
            else:
                status_text = "✅ All Clear"
                status_color = "#00ff00"

            status_label = tk.Label(
                content_frame,
                text=status_text,
                font=('Arial', 8),
                bg=bg_color,
                fg=status_color
            )
            status_label.pack(pady=2)

            # WOPR status
            if widget.properties.get("wopr_tied"):
                wopr_label = tk.Label(
                    content_frame,
                    text="🔗 WOPR Linked",
                    font=('Arial', 7),
                    bg=bg_color,
                    fg='#90a4ae'
                )
                wopr_label.pack()

            widgets_created.append(widget.widget_id)
            used_positions.append({"x": x, "y": y, "width": width, "height": height})

    for i, va in enumerate(vas):
        va_widgets = viz.get_va_widgets(va.character_id)

        if not va_widgets:
            # Create widget if doesn't exist
            widget = viz.create_va_widget(va.character_id)
            va_widgets = [widget]

        for widget in va_widgets:
            # Skip if widget is not visible
            if not widget.visible:
                logger.info(f"⏭️  Skipping invisible widget: {widget.widget_id}")
                continue

            # Get theme colors
            theme_name = widget.theme or "default"
            theme_colors = viz.get_theme_colors(theme_name)

            # Get avatar colors from widget properties or VA
            primary_color = widget.properties.get('primary_color', va.primary_color)
            secondary_color = widget.properties.get('secondary_color', va.secondary_color)

            # Use theme colors if available, otherwise use VA colors
            bg_color = theme_colors.get("bg", '#2d2d2d')
            fg_color = theme_colors.get("fg", primary_color)
            border_color = theme_colors.get("border", primary_color)

            # Create draggable frame
            outer_frame = tk.Frame(
                root,
                bg=border_color,
                padx=2,
                pady=2,
                relief=tk.RAISED,
                borderwidth=2
            )

            # Position using place for drag-and-drop
            # Check if position causes overlap, if so find new position
            # Use smaller default sizes and organized grid
            cols = 4
            row = i // cols
            col = i % cols
            x = widget.position.get("x", 20 + (col * 140))
            y = widget.position.get("y", 20 + (row * 110))
            width = widget.size.get("width", 120)  # Smaller default
            height = widget.size.get("height", 90)  # Smaller default

            # Check for overlaps with existing widgets
            overlap = False
            for pos in used_positions:
                if not (x + width < pos["x"] or x > pos["x"] + pos["width"] or
                       y + height < pos["y"] or y > pos["y"] + pos["height"]):
                    overlap = True
                    break

            # If overlap, find new position
            if overlap:
                new_pos = viz.find_available_position(
                    {"width": width, "height": height},
                    existing_widgets=[w for w in viz.widgets.values() if w.visible]
                )
                x = new_pos["x"]
                y = new_pos["y"]
                # Update widget position
                viz.update_widget_position(widget.widget_id, {"x": x, "y": y})

            # Track this position
            used_positions.append({"x": x, "y": y, "width": width, "height": height})

            # Ensure position is on screen
            screen_width = root.winfo_screenwidth()
            screen_height = root.winfo_screenheight()

            # Clamp position to screen bounds
            x = max(0, min(x, screen_width - width))
            y = max(0, min(y, screen_height - height))

            # Place widget with z-index ordering (higher z_index = on top)
            outer_frame.place(x=x, y=y, width=width, height=height)

            # Bring to front if z_index > 0
            if widget.z_index > 0:
                outer_frame.lift()

            # Ensure widget is raised to top (so all are visible)
            outer_frame.lift()

            # Make frame draggable
            if widget.draggable:
                outer_frame.bind("<Button-1>", lambda e, wid=widget.widget_id: start_drag(e, wid))
                outer_frame.bind("<B1-Motion>", lambda e, wid=widget.widget_id: on_drag(e, wid))
                outer_frame.bind("<ButtonRelease-1>", lambda e, wid=widget.widget_id: stop_drag(e, wid))
                outer_frame.configure(cursor="hand2")

            # Add double-click functionality
            def on_double_click(event, widget_id):
                """Handle double-click on widget"""
                widget = viz.widgets.get(widget_id)
                if widget:
                    va_char = registry.get_character(widget.va_id)
                    va_name = va_char.name if va_char else widget.va_id
                    logger.info(f"🖱️  Double-clicked on {va_name} widget: {widget_id}")

                    # Show widget info or perform action
                    # For prototypes: show identification info
                    if "m5" in widget.va_id.lower() and "suitcase" in widget.va_id.lower():
                        logger.info(f"   📦 M5 Suitcase (Model 5 - Ultra-light, Ultra-mobile Iron Man suit) identified")
                    elif "mark" in widget.va_id.lower() and "1" in widget.va_id.lower():
                        logger.info(f"   📜 Mark 1 Psalm prototype identified")

                    # Record interaction
                    try:
                        from jarvis_interaction_recorder import get_jarvis_interaction_recorder, InteractionType
                        recorder = get_jarvis_interaction_recorder()
                        recorder.record_interaction(
                            InteractionType.CLICK,
                            content=f"Double-clicked {va_name} widget",
                            context={"widget_id": widget_id, "va_id": widget.va_id, "widget_type": widget.widget_type.value},
                            outcome={"success": True, "action": "double_click"}
                        )
                    except Exception:
                        pass

            outer_frame.bind("<Double-Button-1>", lambda e, wid=widget.widget_id: on_double_click(e, wid))

            # Create inner frame for content
            frame = tk.Frame(outer_frame, bg=bg_color, relief=tk.FLAT)
            frame.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)

            # Content frame (can be collapsed)
            content_frame = tk.Frame(frame, bg=bg_color)
            if not widget.collapsed:
                content_frame.pack(fill=tk.BOTH, expand=True)

            # Collapse/Expand button
            collapse_btn = tk.Button(
                frame,
                text="−" if not widget.collapsed else "+",
                font=('Arial', 10, 'bold'),
                bg=bg_color,
                fg=fg_color,
                relief=tk.FLAT,
                command=lambda wid=widget.widget_id: toggle_collapse(wid),
                cursor='hand2'
            )
            collapse_btn.pack(anchor='ne', padx=2, pady=2)

            # VA name with theme color
            name_label = tk.Label(
                content_frame,
                text=va.name,
                font=('Arial', 12, 'bold'),
                bg=bg_color,
                fg=fg_color
            )
            name_label.pack(pady=3)

            # VISUAL INDICATORS FOR PROTOTYPES
            # Add identification badges for M5 Suitcase and Mark 1 Psalm
            prototype_type = None
            if "m5" in va.character_id.lower() and "suitcase" in va.character_id.lower():
                prototype_type = "M5_SUITCASE"
                # Add M5 Suitcase indicator badge with distinctive border
                m5_badge_frame = tk.Frame(
                    content_frame,
                    bg='#0066cc',
                    relief=tk.RAISED,
                    borderwidth=2
                )
                m5_badge_frame.pack(pady=2, padx=2, fill=tk.X)
                m5_badge = tk.Label(
                    m5_badge_frame,
                    text="📦 M5 SUITCASE",
                    font=('Arial', 9, 'bold'),
                    bg='#0066cc',
                    fg='#ffffff'
                )
                m5_badge.pack(pady=2, padx=4)
            elif "mark" in va.character_id.lower() and "1" in va.character_id.lower() and "psalm" in va.character_id.lower():
                prototype_type = "MARK_1_PSALM"
                # Add Mark 1 Psalm indicator badge with distinctive border
                psalm_badge_frame = tk.Frame(
                    content_frame,
                    bg='#cc6600',
                    relief=tk.RAISED,
                    borderwidth=2
                )
                psalm_badge_frame.pack(pady=2, padx=2, fill=tk.X)
                psalm_badge = tk.Label(
                    psalm_badge_frame,
                    text="📜 MARK 1 PSALM",
                    font=('Arial', 9, 'bold'),
                    bg='#cc6600',
                    fg='#ffffff'
                )
                psalm_badge.pack(pady=2, padx=4)

            # Add unique ID indicator for all prototypes
            if prototype_type:
                id_label = tk.Label(
                    content_frame,
                    text=f"ID: {va.character_id}",
                    font=('Arial', 7, 'monospace'),
                    bg=bg_color,
                    fg='#90a4ae'
                )
                id_label.pack()

                # Add prototype status indicator
                status_label = tk.Label(
                    content_frame,
                    text="🔬 PROTOTYPE",
                    font=('Arial', 7, 'italic'),
                    bg=bg_color,
                    fg='#ffcc00'
                )
                status_label.pack()

            # VA role with secondary color
            role_label = tk.Label(
                content_frame,
                text=va.role,
                font=('Arial', 9),
                bg=bg_color,
                fg=secondary_color
            )
            role_label.pack()

            # Avatar style indicator
            avatar_style = widget.properties.get('avatar_style', va.avatar_style)
            style_label = tk.Label(
                content_frame,
                text=f"Style: {avatar_style}",
                font=('Arial', 7, 'italic'),
                bg=bg_color,
                fg=secondary_color
            )
            style_label.pack()

            # Add double-click hint for prototypes
            if prototype_type:
                hint_label = tk.Label(
                    content_frame,
                    text="💡 Double-click for info",
                    font=('Arial', 6, 'italic'),
                    bg=bg_color,
                    fg='#90a4ae'
                )
                hint_label.pack(pady=1)

            # Special rendering for bobblehead widgets (like Kenny)
            if widget.widget_type.value == "bobblehead":
                # Clear existing content for bobblehead
                for widget_item in content_frame.winfo_children():
                    widget_item.destroy()

                # Bobblehead widgets should show the actual avatar
                # For Kenny, this means showing the Iron Man design
                bobblehead_icon = "🤖"  # Robot icon for Kenny/IMVA
                if va.character_id == "kenny":
                    bobblehead_icon = "🤖"  # Iron Man style
                elif va.character_id == "imva":
                    bobblehead_icon = "⚡"  # IMVA style

                bobblehead_label = tk.Label(
                    content_frame,
                    text=bobblehead_icon,
                    font=('Arial', 32, 'bold'),
                    bg=bg_color,
                    fg=primary_color
                )
                bobblehead_label.pack(pady=5)

                # Add note that actual avatar process should be running
                avatar_note = tk.Label(
                    content_frame,
                    text="Avatar Active",
                    font=('Arial', 7, 'italic'),
                    bg=bg_color,
                    fg=secondary_color
                )
                avatar_note.pack()

                # Double-click handler to start/restart avatar
                def start_avatar_process(va_id, va_name):
                    """Start avatar process for specific VA"""
                    try:
                        import subprocess
                        if va_id == "kenny":
                            avatar_script = script_dir / "kenny_imva_enhanced.py"
                        elif va_id == "imva":
                            avatar_script = script_dir / "kenny_imva_enhanced.py"  # Same for now
                        else:
                            avatar_script = None

                        if avatar_script and avatar_script.exists():
                            subprocess.Popen(
                                [sys.executable, str(avatar_script)],
                                cwd=str(project_root),
                                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                            )
                            logger.info(f"✅ Started {va_name} avatar process")
                    except Exception as e:
                        logger.debug(f"Could not start avatar: {e}")

                # Make widget double-clickable to start avatar
                outer_frame.bind(
                    "<Double-Button-1>",
                    lambda e, vid=va.character_id, vname=va.name: start_avatar_process(vid, vname)
                )

                # Store widget frame data
                widget_frames[widget.widget_id] = {
                    "frame": outer_frame,
                    "content_frame": content_frame,
                    "va": va,
                    "widget": widget
                }

                widgets_created.append((va, widget, frame))
                print(f"  ✅ Rendered {va.name} bobblehead widget (double-click to start avatar)")
                continue

            # Special rendering for DEFCON streetlight widget
            if widget.widget_type.value == "defcon_streetlight":
                # DEFCON streetlight display
                defcon_level = widget.properties.get("defcon_level", 5)
                defcon_color = widget.properties.get("defcon_color", "#00ccff")
                defcon_name = widget.properties.get("defcon_name", "PEACEFUL")
                alerts_count = len(widget.properties.get("alerts", []))
                problems_count = len(widget.properties.get("problems", []))

                # Clear existing content for streetlight
                for widget_item in content_frame.winfo_children():
                    widget_item.destroy()

                # Title
                title_label = tk.Label(
                    content_frame,
                    text="🚦 DEFCON",
                    font=('Arial', 10, 'bold'),
                    bg=bg_color,
                    fg=fg_color
                )
                title_label.pack(pady=2)

                # DEFCON level indicator (streetlight)
                defcon_frame = tk.Frame(content_frame, bg=bg_color)
                defcon_frame.pack(pady=5)

                # Create 5 lights (DEFCON 5 to 1)
                for level in range(5, 0, -1):
                    light_color = "#333333"  # Off
                    if level <= defcon_level:
                        # Color based on level
                        if level == 1:
                            light_color = "#ff0000"  # Red
                        elif level == 2:
                            light_color = "#ff6600"  # Orange
                        elif level == 3:
                            light_color = "#ffcc00"  # Yellow
                        elif level == 4:
                            light_color = "#00ff00"  # Green
                        else:
                            light_color = "#00ccff"  # Blue

                    light = tk.Label(
                        defcon_frame,
                        text="●",
                        font=('Arial', 16, 'bold'),
                        bg=bg_color,
                        fg=light_color
                    )
                    light.pack(pady=1)

                # DEFCON level text
                level_label = tk.Label(
                    content_frame,
                    text=f"LEVEL {defcon_level}",
                    font=('Arial', 12, 'bold'),
                    bg=bg_color,
                    fg=defcon_color
                )
                level_label.pack(pady=2)

                # Status
                if alerts_count > 0 or problems_count > 0:
                    status_text = f"⚠️ {alerts_count} alerts, {problems_count} problems"
                    status_color = "#ff0000" if defcon_level <= 2 else "#ffcc00"
                else:
                    status_text = "✅ All Clear"
                    status_color = "#00ff00"

                status_label = tk.Label(
                    content_frame,
                    text=status_text,
                    font=('Arial', 8),
                    bg=bg_color,
                    fg=status_color
                )
                status_label.pack(pady=2)

                # WOPR status
                if widget.properties.get("wopr_tied"):
                    wopr_label = tk.Label(
                        content_frame,
                        text="🔗 WOPR Linked",
                        font=('Arial', 7),
                        bg=bg_color,
                        fg='#90a4ae'
                    )
                    wopr_label.pack()
            else:
                # Regular widget type display
                widget_type_label = tk.Label(
                    content_frame,
                    text=f"Widget: {widget.widget_type.value}",
                    font=('Arial', 8),
                    bg=bg_color,
                    fg=theme_colors.get("accent", '#90a4ae')
                )
                widget_type_label.pack()

            # Theme indicator
            if widget.theme:
                theme_label = tk.Label(
                    content_frame,
                    text=f"Theme: {widget.theme}",
                    font=('Arial', 7),
                    bg=bg_color,
                    fg=theme_colors.get("accent", '#90a4ae')
                )
                theme_label.pack()

            # Status
            status_text = "✅ Active" if widget.animation_state == "idle" else f"✨ {widget.animation_state}"
            status_label = tk.Label(
                content_frame,
                text=status_text,
                font=('Arial', 9, 'bold'),
                bg=bg_color,
                fg=theme_colors.get("accent", '#66bb6a')
            )
            status_label.pack(pady=3)

            # Position info
            pos_label = tk.Label(
                content_frame,
                text=f"({int(widget.position['x'])}, {int(widget.position['y'])})",
                font=('Arial', 7),
                bg=bg_color,
                fg='#78909c'
            )
            pos_label.pack()

            # Resize handles (if resizable)
            if widget.resizable:
                resize_handle = tk.Frame(
                    outer_frame,
                    bg=border_color,
                    width=10,
                    height=10,
                    cursor='sizing'
                )
                resize_handle.place(relx=1.0, rely=1.0, anchor='se')
                resize_handle.bind("<Button-1>", lambda e, wid=widget.widget_id: start_resize(e, wid, "bottom-right"))
                resize_handle.bind("<B1-Motion>", lambda e, wid=widget.widget_id: on_resize(e, wid))
                resize_handle.bind("<ButtonRelease-1>", lambda e, wid=widget.widget_id: stop_resize(e, wid))

            # Store widget frame data
            widget_frames[widget.widget_id] = {
                "frame": outer_frame,
                "content_frame": content_frame,
                "va": va,
                "widget": widget
            }

            widgets_created.append((va, widget, frame))

            print(f"  ✅ Rendered {va.name} widget ({widget.widget_type.value})")

    # Add theme selector menu
    menu_bar = tk.Menu(root)
    root.config(menu=menu_bar)

    theme_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Themes", menu=theme_menu)

    for theme_name in viz.themes.keys():
        theme_menu.add_command(
            label=theme_name.title(),
            command=lambda t=theme_name: apply_theme_to_all(t)
        )

    def apply_theme_to_all(theme_name):
        """Apply theme to all widgets"""
        for widget_id in widget_frames.keys():
            viz.set_widget_theme(widget_id, theme_name)
        print(f"🎨 Applied theme '{theme_name}' to all widgets")
        # Refresh display
        root.after(100, lambda: refresh_all_widgets())

    def refresh_all_widgets():
        """Refresh all widget displays"""
        for widget_id in widget_frames.keys():
            refresh_widget_display(widget_id)

    # Animation controls
    anim_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="Animations", menu=anim_menu)

    anim_menu.add_command(
        label="Fade In All",
        command=lambda: animate_all(VFXType.FADE_IN)
    )
    anim_menu.add_command(
        label="Pulse All",
        command=lambda: animate_all(VFXType.PULSE)
    )
    anim_menu.add_command(
        label="Bounce All",
        command=lambda: animate_all(VFXType.BOUNCE)
    )

    def animate_all(anim_type):
        """Animate all widgets"""
        for widget_id in widget_frames.keys():
            viz.animate_widget(widget_id, anim_type, duration=1.0)
        print(f"✨ Animating all widgets with {anim_type.value}")

    print()
    print(f"✅ Rendered {len(widgets_created)} VA widgets with enhanced features")
    print()
    print("=" * 80)
    print("✅ VA WIDGETS NOW VISIBLE ON DESKTOP")
    print("=" * 80)
    print()
    print("Features available:")
    print("  🖱️  Drag widgets by clicking and dragging")
    print("  📏 Resize widgets using the corner handle")
    print("  📦 Collapse/Expand widgets using the +/- button")
    print("  🎨 Change themes from the Themes menu")
    print("  ✨ Apply animations from the Animations menu")
    print()
    print("VAs visible:")
    for va, widget, frame in widgets_created:
        print(f"  ✅ {va.name} ({va.character_id}) - {widget.widget_type.value}")
    print()

    # Keep window open
    root.mainloop()

    return True


def render_with_web_dashboard(visibility_system=None):
    """Render VA widgets using web dashboard (alternative)"""
    try:
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        import webbrowser
        from threading import Thread
    except ImportError:
        logger.error("HTTP server not available")
        return False

    print("Creating web dashboard for VAs...")

    # Reuse existing visibility system or create new one
    if visibility_system is None:
        visibility = VAVisibilitySystem()
        visibility.show_all_vas()
        registry = visibility.registry
        viz = visibility.viz
        vas = visibility.vas
    else:
        visibility = visibility_system
        # Only show VAs if they haven't been shown yet
        existing_widgets = sum(len(visibility.viz.get_va_widgets(va.character_id)) for va in visibility.vas)
        if existing_widgets == 0:
            visibility.show_all_vas()
        registry = visibility.registry
        viz = visibility.viz
        vas = visibility.vas

    dashboard_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>LUMINA Virtual Assistants</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #0A0A0A; color: #fff; padding: 20px; }}
            .header-hud {{ 
                display: flex; justify-content: space-between; align-items: center; 
                background: #1A1A2E; padding: 15px 30px; border-radius: 15px; margin-bottom: 30px;
                border: 1px solid #333; box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            }}
            .time-section {{ display: flex; flex-direction: column; }}
            .time {{ font-size: 24px; font-weight: bold; margin-bottom: 5px; }}
            .activity-lines {{ display: flex; gap: 3px; height: 15px; align-items: flex-end; }}
            .line {{ width: 4px; border-radius: 2px; }}
            .line.green {{ background: #00B894; }}
            .line.red {{ background: #E74C3C; }}

            .model-section {{ text-align: center; }}
            .model-name {{ font-size: 18px; font-weight: bold; color: #00D4FF; }}
            .mode-status {{ font-size: 10px; color: #90a4ae; text-transform: uppercase; letter-spacing: 1px; }}

            .money-tachometer {{ text-align: right; }}
            .tacho-title {{ font-size: 10px; color: #4ECDC4; font-weight: bold; margin-bottom: 5px; }}
            .cost {{ font-family: 'Consolas', monospace; font-size: 22px; color: #FFC857; }}
            .progress-bg {{ width: 150px; height: 6px; background: #333; border-radius: 3px; margin-top: 5px; }}
            .progress-fill {{ height: 100%; background: #FFC857; border-radius: 3px; }}

            .va-container {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
            .va-card {{ background: #1A1A2E; border-radius: 15px; padding: 25px; border: 2px solid; transition: transform 0.3s; }}
            .va-card:hover {{ transform: translateY(-5px); }}
            .va-name {{ font-size: 20px; font-weight: bold; margin-bottom: 10px; }}
            .va-role {{ font-size: 14px; margin-bottom: 15px; opacity: 0.8; }}
            .va-status {{ color: #66bb6a; font-weight: bold; display: flex; align-items: center; gap: 8px; }}
        </style>
        <script>
            function updateTime() {{
                const now = new Date();
                document.getElementById('clock').innerText = now.toLocaleTimeString();
            }}
            setInterval(updateTime, 1000);
        </script>
    </head>
    <body>
        <div class="header-hud">
            <div class="time-section">
                <div class="time" id="clock">00:00:00</div>
                <div class="activity-lines">
                    <div class="line green" style="height: 8px;"></div>
                    <div class="line green" style="height: 12px;"></div>
                    <div class="line green" style="height: 10px;"></div>
                    <div class="line red" style="height: 15px;"></div>
                    <div class="line green" style="height: 9px;"></div>
                </div>
            </div>

            <div class="model-section">
                <div class="model-name">AUTO/GEMINI 3 FLASH</div>
                <div class="mode-status">Local First Enforced</div>
            </div>

            <div class="money-tachometer">
                <div class="tacho-title">MONEY TACHOMETER</div>
                <div class="cost">$0.004250</div>
                <div class="progress-bg"><div class="progress-fill" style="width: 45%;"></div></div>
            </div>
        </div>

        <div class="va-container">
    """

    for va in vas:
        va_widgets = viz.get_va_widgets(va.character_id)
        widget_count = len(va_widgets)

        # Get avatar colors
        primary_color = va.primary_color
        secondary_color = va.secondary_color
        avatar_style = va.avatar_style

        dashboard_html += f"""
            <div class="va-card" style="border-color: {primary_color};">
                <div class="va-name" style="color: {primary_color};">{va.name}</div>
                <div class="va-role" style="color: {secondary_color};">{va.role}</div>
                <div class="va-style" style="color: {secondary_color};">Style: {avatar_style}</div>
                <div class="va-status">✅ Active - {widget_count} widget(s)</div>
            </div>
        """

    dashboard_html += """
        </div>
    </body>
    </html>
    """

    # Save HTML
    html_file = project_root / "data" / "va_desktop_viz" / "dashboard.html"
    html_file.parent.mkdir(parents=True, exist_ok=True)
    html_file.write_text(dashboard_html, encoding='utf-8')

    print(f"✅ Web dashboard created: {html_file}")
    print("Opening in browser...")

    # Open in browser
    webbrowser.open(f"file://{html_file}")

    return True


def main(visibility_system=None):
    """Main function"""
    print("=" * 80)
    print("🖥️  RENDERING VA DESKTOP WIDGETS")
    print("=" * 80)
    print()
    print("Choose rendering method:")
    print("  1. Desktop Window (tkinter) - Shows in separate window")
    print("  2. Web Dashboard - Opens in browser")
    print("  3. Replika-Inspired - Modern, animated design")
    print()

    # Try Replika-inspired first (most beautiful)
    try:
        from replika_inspired_va_renderer import render_replika_inspired
        print("Attempting Replika-inspired rendering...")
        if render_replika_inspired(visibility_system):
            return 0
    except ImportError:
        print("Replika-inspired renderer not available, using standard...")
    except Exception as e:
        print(f"Replika-inspired failed: {e}")
        print("Falling back to standard rendering...")
    print()

    # Try tkinter first
    print("Attempting desktop window rendering...")
    try:
        if render_with_tkinter(visibility_system):
            return 0
    except Exception as e:
        print(f"Desktop window failed: {e}")
        print()
        print("Falling back to web dashboard...")

    # Fallback to web dashboard
    try:
        if render_with_web_dashboard(visibility_system):
            return 0
    except Exception as e:
        print(f"Web dashboard failed: {e}")
        return 1

    print("❌ Could not render widgets")
    return 1


if __name__ == "__main__":
    sys.exit(exit_code)


    exit_code = main()