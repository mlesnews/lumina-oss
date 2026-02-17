#!/usr/bin/env python3
"""
JARVIS Iron Legion Core - Mark VII "Final State" Chassis
Merged Ace behavior (Tortoise movement, Sleeping) with Stark technical core.
"""
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
import math
import random
import time
import io
from enum import Enum
from pathlib import Path

# Remote compute integration
try:
    from jarvis_remote_renderer import HybridRenderer
    REMOTE_RENDER_AVAILABLE = True
except ImportError:
    REMOTE_RENDER_AVAILABLE = False
    HybridRenderer = None

class LegionState(Enum):
    SUITCASE = "suitcase"
    TRANSFORMING = "transforming"
    ARMOR = "armor"
    WORKING = "working"
    SLEEPING = "sleeping"

class JarvisCore:
    def __init__(self, use_remote_compute: bool = True):
        self.size = 180
        self.state = LegionState.SUITCASE
        self.animation_frame = 0
        self.tp = 0.0 # Transformation progress

        # REMOTE COMPUTE INTEGRATION
        self.use_remote_compute = use_remote_compute and REMOTE_RENDER_AVAILABLE
        if self.use_remote_compute:
            try:
                self.remote_renderer = HybridRenderer()
                print("✅ Remote compute enabled - pushing rendering to Azure framework")
            except Exception as e:
                print(f"⚠️  Remote compute unavailable: {e}")
                self.use_remote_compute = False
                self.remote_renderer = None
        else:
            self.remote_renderer = None

        # Interactions
        self.root = tk.Tk()
        self.root.overrideredirect(True)
        self.root.attributes('-topmost', True)
        self.root.attributes('-transparentcolor', '#000001')
        self.canvas = tk.Canvas(self.root, width=self.size, height=self.size, bg='#000001', highlightthickness=0)
        self.canvas.pack()

        # ACE-STYLE PHYSICS
        self.x, self.y = 300, 300
        self.target_x, self.target_y = 300, 300
        self.interpolation = 0.05 # Tortoise pace
        self.drag_x, self.drag_y = 0, 0
        self.is_dragging = False

        self.canvas.bind("<Button-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.canvas.bind("<Double-Button-1>", self.toggle_mode)
        self.canvas.bind("<Button-3>", self.cycle_state)  # Right-click to cycle states

        self.run_loop()

    def start_drag(self, event): 
        self.drag_x, self.drag_y = event.x, event.y
        self.is_dragging = False

    def do_drag(self, event):
        self.is_dragging = True
        nx = self.root.winfo_x() + (event.x - self.drag_x)
        ny = self.root.winfo_y() + (event.y - self.drag_y)
        self.root.geometry(f"+{nx}+{ny}")
        self.x, self.y = nx, ny
        self.target_x, self.target_y = nx, ny

    def end_drag(self, event):
        # Only cycle state if it was a click (not a drag)
        if not hasattr(self, 'is_dragging') or not self.is_dragging:
            self.cycle_state(event)
        self.is_dragging = False

    def toggle_mode(self, event):
        """Double-click: Toggle between Suitcase and Armor"""
        self.target_tp = 1.0 if self.tp < 0.5 else 0.0
        self.state = LegionState.TRANSFORMING

    def cycle_state(self, event):
        """Right-click or click (without drag): Cycle behavioral states"""
        if self.tp < 0.5:
            return  # Only cycle in armor mode

        states = [LegionState.ARMOR, LegionState.WORKING, LegionState.SLEEPING]
        try:
            idx = states.index(self.state)
            self.state = states[(idx + 1) % len(states)]
        except ValueError:
            self.state = LegionState.ARMOR

    def render_frame(self):
        """STARK INTERFACE CHASSIS - High-Fidelity Mark V with Sophisticated Details"""
        try:
            self.canvas.delete("all")

            # REMOTE RENDERING: Try remote first to offload compute
            if self.use_remote_compute and self.remote_renderer:
                remote_image = self.remote_renderer.render(
                    state=self.state.value,
                    animation_frame=self.animation_frame,
                    transformation_progress=self.tp,
                    size=self.size
                )

                if remote_image:
                    # Use remote-rendered image
                    from PIL import Image as PILImage
                    img = PILImage.open(io.BytesIO(remote_image))
                    img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
                    if hasattr(self, 'tk_img'): del self.tk_img
                    self.tk_img = ImageTk.PhotoImage(img_final)
                    self.canvas.create_image(self.size/2, self.size/2, image=self.tk_img)
                    return  # Successfully rendered remotely

            # LOCAL RENDERING FALLBACK (or if remote unavailable)
            scale = 4  # Higher resolution for detail
            img = Image.new('RGBA', (self.size*scale, self.size*scale), (0,0,0,0))
            draw = ImageDraw.Draw(img)
            cx, cy = (self.size/2)*scale, (self.size/2)*scale

            # --- STARK MCU COLOR PALETTE ---
            c_hot_rod = (178, 34, 34, 255)      # Hot Rod Red (#B22222)
            c_stark_gold = (255, 215, 0, 255)   # Stark Gold (#FFD700)
            c_reactor = (0, 255, 255, 255)      # Reactor Cyan (#00FFFF)
            c_steel = (70, 75, 80, 255)         # Industrial Steel
            c_silver = (192, 192, 192, 255)     # Mark V Silver
            c_hologram = (0, 255, 255, 120)     # Translucent Data
            c_black = (5, 5, 5, 255)            # Recessed Pit
            c_dim_reactor = (0, 80, 80, 180)    # Sleeping reactor

            th = int(2 * scale)  # Sharp technical lines
            b_w = (self.size * 0.45) * scale
            tp = self.tp  # Transformation progress: 0 = Suitcase, 1 = Armor

            # Helper: Draw beveled polygon
            def draw_beveled_poly(cx, cy, r, sides, color, trim, rot=0, width=th):
                pts = [(cx + r * math.cos(2*math.pi*i/sides + rot), 
                        cy + r * math.sin(2*math.pi*i/sides + rot)) for i in range(sides)]
                draw.polygon(pts, fill=color, outline=trim, width=width)
                return pts

            # ========== SUITCASE MODE (tp < 0.3) ==========
            if tp < 0.3:
                # Folding suitcase with Mark V silver/red ribbed plating
                case_h = b_w * 0.4
                case_w = b_w * 1.2

                # Main case body
                draw.rectangle([cx-case_w/2, cy-case_h/2, cx+case_w/2, cy+case_h/2], 
                              fill=c_silver, outline=c_stark_gold, width=th)

                # Ribbed plating details
                for i in range(5):
                    rib_x = cx - case_w/2 + (i * case_w/4)
                    draw.line([rib_x, cy-case_h/2, rib_x, cy+case_h/2], 
                             fill=c_black, width=int(scale))

                # Handle
                draw.rectangle([cx-case_w*0.15, cy-case_h/2-5*scale, cx+case_w*0.15, cy-case_h/2], 
                              fill=c_steel, outline=c_black, width=1)

                # Latches
                draw.ellipse([cx-case_w*0.35, cy-case_h/2-2*scale, cx-case_w*0.25, cy-case_h/2+2*scale], 
                            fill=c_stark_gold, outline=c_black)
                draw.ellipse([cx+case_w*0.25, cy-case_h/2-2*scale, cx+case_w*0.35, cy-case_h/2+2*scale], 
                            fill=c_stark_gold, outline=c_black)

                # Subtle arc reactor glow (dimmed in suitcase)
                ar_r = b_w * 0.15
                draw.ellipse([cx-ar_r, cy-ar_r, cx+ar_r, cy+ar_r], 
                            fill=(0, 100, 100, 100), outline=c_reactor, width=1)

            # ========== TRANSFORMING / ARMOR MODE (tp >= 0.3) ==========
            else:
                # 1. MECHANICAL INTERNAL STRUTS (Steel framework)
                strut_w = b_w * 0.08
                draw.rectangle([cx - strut_w, cy - b_w*1.6, cx + strut_w, cy + b_w*1.6], 
                              fill=c_steel, outline=c_black, width=1)
                draw.rectangle([cx - b_w*1.6, cy - strut_w, cx + b_w*1.6, cy + strut_w], 
                              fill=c_steel, outline=c_black, width=1)

                # 2. LAYERED ARMOR PLATING (Multi-layer hexagonal core)
                # Primary chassis plate (beveled hexagon)
                chassis_pts = draw_beveled_poly(cx, cy, b_w * 1.1, 6, c_hot_rod, c_stark_gold, rot=math.pi/6)

                # Secondary layer (slightly smaller, rotated)
                draw_beveled_poly(cx, cy, b_w * 0.95, 6, (200, 40, 40, 255), c_stark_gold, rot=-math.pi/6, width=int(scale))

                # 3. VENTILATION SLITS & DATA SHELVES
                for i in range(4):
                    offset = (i - 1.5) * (b_w * 0.3)
                    # Ventilation slits
                    draw.line([cx - b_w*0.5, cy + offset, cx + b_w*0.5, cy + offset], 
                             fill=c_black, width=int(1.5*scale))
                    # Data blips on slats
                    if random.random() > 0.5:
                        draw.rectangle([cx + b_w*0.4, cy + offset - 2*scale, 
                                       cx + b_w*0.5, cy + offset + 2*scale], 
                                      fill=c_reactor)

                # 4. SHOULDER ASSEMBLIES (Modular plating with hydraulic details)
                shoulder_h = b_w * 0.5 * tp
                # Left shoulder
                draw.polygon([(cx - b_w*1.1, cy - b_w*0.4), 
                             (cx - b_w*1.8, cy), 
                             (cx - b_w*1.1, cy + b_w*0.4)], 
                            fill=c_hot_rod, outline=c_stark_gold, width=th)
                # Right shoulder
                draw.polygon([(cx + b_w*1.1, cy - b_w*0.4), 
                             (cx + b_w*1.8, cy), 
                             (cx + b_w*1.1, cy + b_w*0.4)], 
                            fill=c_hot_rod, outline=c_stark_gold, width=th)

                # Hydraulic pistons on shoulders
                for sx in [cx - b_w*1.45, cx + b_w*1.45]:
                    draw.rectangle([sx - 3*scale, cy - b_w*0.2, sx + 3*scale, cy + b_w*0.2], 
                                  fill=c_steel, outline=c_black)

                # 5. THE HEAD: MARK V HELMET (Technical Core with HUD)
                if tp > 0.4:
                    hx, hy = cx, cy - b_w*1.2 - (b_w * 0.3 * (1-tp))
                    hr = b_w * 0.8

                    # Helmet base (hexagonal)
                    draw_beveled_poly(hx, hy, hr, 6, c_hot_rod, c_stark_gold, rot=math.pi/6)

                    # --- SCROLLING HUD REPLACEMENT (No Face, Just Data) ---
                    # HUD background (recessed)
                    draw.rectangle([hx - hr*0.7, hy - hr*0.3, hx + hr*0.7, hy + hr*0.3], 
                                  fill=c_black, outline=c_reactor, width=int(scale))

                    # Holographic "Code" lines (scrolling effect)
                    scroll_offset = (self.animation_frame * 2) % (hr * 0.6)
                    for i in range(3):
                        y_off = (i - 1) * (hr * 0.15) + (scroll_offset * 0.1)
                        line_end = hx + hr*(random.uniform(-0.5, 0.6))
                        draw.line([hx - hr*0.6, hy + y_off, line_end, hy + y_off], 
                                 fill=c_hologram, width=int(scale))

                    # Technical Eyes (Dual Slits - Reactor Cyan when active, dimmed when sleeping)
                    eye_c = c_reactor if self.state != LegionState.SLEEPING else c_dim_reactor
                    draw.rectangle([hx - hr*0.6, hy - hr*0.1, hx - hr*0.2, hy + hr*0.1], 
                                  fill=eye_c, outline=c_black, width=1)
                    draw.rectangle([hx + hr*0.2, hy - hr*0.1, hx + hr*0.6, hy + hr*0.1], 
                                  fill=eye_c, outline=c_black, width=1)

                    # Faceplate trim (gold accent)
                    draw.line([hx - hr*0.7, hy - hr*0.3, hx + hr*0.7, hy - hr*0.3], 
                             fill=c_stark_gold, width=int(scale))
                    draw.line([hx - hr*0.7, hy + hr*0.3, hx + hr*0.7, hy + hr*0.3], 
                             fill=c_stark_gold, width=int(scale))

                # 6. RECESSED ARC REACTOR ASSEMBLY (Sophisticated pulsing core)
                ar_x, ar_y = cx, cy - b_w*0.2

                # Draw the "Pit" (recessed housing)
                pit_r = b_w * 0.35
                draw.ellipse([ar_x - pit_r, ar_y - pit_r, ar_x + pit_r, ar_y + pit_r], 
                            fill=c_black, outline=c_steel, width=th)

                # Inner ring (steel)
                draw.ellipse([ar_x - pit_r*0.85, ar_y - pit_r*0.85, 
                             ar_x + pit_r*0.85, ar_y + pit_r*0.85], 
                            fill=None, outline=c_steel, width=int(scale))

                # The Core (pulsing with animation)
                pulse_intensity = 0.15 if self.state == LegionState.SLEEPING else 0.25
                p = 1.0 + pulse_intensity * math.sin(self.animation_frame * 0.15)
                ar_r = (b_w * 0.25) * p

                reactor_color = c_dim_reactor if self.state == LegionState.SLEEPING else c_reactor
                draw.ellipse([ar_x - ar_r, ar_y - ar_r, ar_x + ar_r, ar_y + ar_r], 
                            fill=reactor_color, outline=(255,255,255,255), width=int(scale))

                # Internal Struts over the reactor (rotating)
                for angle in [0, 120, 240]:
                    rad = math.radians(angle + (self.animation_frame * 2))
                    draw.line([ar_x, ar_y, ar_x + ar_r*math.cos(rad), ar_y + ar_r*math.sin(rad)], 
                             fill=c_black, width=int(scale))

                # Reactor center dot
                draw.ellipse([ar_x - 2*scale, ar_y - 2*scale, ar_x + 2*scale, ar_y + 2*scale], 
                            fill=(255,255,255,255), outline=None)

                # 7. BEHAVIORAL OVERLAYS
                if self.state == LegionState.WORKING:
                    # Holographic keyboard projection
                    kb_y_start = cy + b_w*0.8
                    for i in range(6):
                        kb_y = kb_y_start + (i * 8*scale)
                        kb_w = b_w * 0.6
                        draw.line([cx - kb_w, kb_y, cx + kb_w, kb_y], 
                                 fill=c_hologram, width=int(scale))
                        # Typing indicators
                        if random.random() > 0.7:
                            key_x = cx - kb_w + random.uniform(0, kb_w*2)
                            draw.rectangle([key_x - 3*scale, kb_y - 2*scale, 
                                           key_x + 3*scale, kb_y + 2*scale], 
                                          fill=c_reactor)

                if self.state == LegionState.SLEEPING:
                    # Zzz animation (visual representation)
                    zzz_y = cy - b_w*1.8 if tp > 0.4 else cy - b_w*0.6
                    zzz_x = cx + b_w*0.3
                    # Draw Z shapes as simple lines
                    for i in range(3):
                        zx = zzz_x + i*12*scale
                        zy = zzz_y + i*2*scale
                        # Z shape: top, diagonal, bottom
                        draw.line([zx, zy, zx+8*scale, zy], fill=c_hologram, width=int(scale))
                        draw.line([zx+8*scale, zy, zx, zy+8*scale], fill=c_hologram, width=int(scale))
                        draw.line([zx, zy+8*scale, zx+8*scale, zy+8*scale], fill=c_hologram, width=int(scale))

            # Final render with high-quality resampling
            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'tk_img'): del self.tk_img
            self.tk_img = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.tk_img)
        except Exception as e: 
            print(f"💥 RENDER ERROR: {e}")
            import traceback
            traceback.print_exc()

    def run_loop(self):
        self.animation_frame += 1

        # Transformation animation
        if hasattr(self, 'target_tp'):
            diff = self.target_tp - self.tp
            self.tp += diff * 0.12
            if abs(diff) < 0.01:
                self.tp = self.target_tp
                self.state = LegionState.ARMOR if self.tp == 1.0 else LegionState.SUITCASE
                del self.target_tp

        # Behavioral state machine (Ace-style)
        if self.tp > 0.5:  # Only in armor mode
            # Auto-transition to working after movement
            if self.state == LegionState.ARMOR and self.animation_frame % 300 == 0:
                if random.random() > 0.5:
                    self.state = LegionState.WORKING
            # Auto-transition to sleeping
            if self.state == LegionState.WORKING and self.animation_frame % 600 == 0:
                if random.random() > 0.7:
                    self.state = LegionState.SLEEPING
            # Wake up from sleep
            if self.state == LegionState.SLEEPING and self.animation_frame % 400 == 0:
                if random.random() > 0.6:
                    self.state = LegionState.ARMOR

        # ACE MOVEMENT (Tortoise pace)
        if self.state in [LegionState.ARMOR, LegionState.WORKING]:
            self.x += (self.target_x - self.x) * self.interpolation
            self.y += (self.target_y - self.y) * self.interpolation
            # New target every ~6 seconds (200 frames * 30ms = 6s)
            if self.animation_frame % 200 == 0:
                self.target_x = random.randint(100, self.root.winfo_screenwidth()-200)
                self.target_y = random.randint(100, self.root.winfo_screenheight()-200)
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")
        elif self.state == LegionState.SLEEPING:
            # Slow drift when sleeping
            self.x += (self.target_x - self.x) * (self.interpolation * 0.3)
            self.y += (self.target_y - self.y) * (self.interpolation * 0.3)
            self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

        self.render_frame()
        self.root.after(30, self.run_loop)

if __name__ == "__main__":
    JarvisCore().root.mainloop()
