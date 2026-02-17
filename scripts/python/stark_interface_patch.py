import sys
from pathlib import Path

def stark_interface_transformation():
    file_path = Path("scripts/python/kenny_imva_enhanced.py")
    content = file_path.read_text(encoding='utf-8')

    new_method = """    def draw_kenny(self):
        \"\"\"Draw Kenny sprite with components - STARK INTERFACE CHASSIS v1\"\"\"
        try:
            if not self.canvas: return
            self.canvas.delete("all")
            if not PIL_AVAILABLE: return

            scale = 3
            img_size = int(self.size * scale)
            img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            c_x, c_y = (self.size / 2) * scale, (self.size / 2) * scale
            s_s = self.size * scale

            # --- STARK MCU COLOR PALETTE ---
            c_hot_rod = (178, 34, 34, 255)   # Hot Rod Red (#B22222)
            c_stark_gold = (255, 215, 0, 255) # Stark Gold (#FFD700)
            c_reactor = (0, 255, 255, 255)   # Reactor Cyan (#00FFFF)
            c_steel = (70, 75, 80, 255)      # Industrial Steel
            c_hologram = (0, 255, 255, 100)  # Translucent Data
            c_black = (5, 5, 5, 255)         # Recessed Pit

            th = int(2 * scale) # Sharp technical lines

            # --- DRAWING SEQUENCE: THE STARK CHASSIS ---
            b_w = (self.size * 0.45) * scale 

            # 1. MECHANICAL INTERNAL STRUTS (Steel)
            draw.rectangle([c_x - b_w*0.1, c_y - b_w*1.5, c_x + b_w*0.1, c_y + b_w*1.5], fill=c_steel)
            draw.rectangle([c_x - b_w*1.5, c_y - b_w*0.1, c_x + b_w*1.5, c_y + b_w*0.1], fill=c_steel)

            # 2. LAYERED ARMOR PLATING (Red/Gold)
            import math
            def draw_beveled_poly(cx, cy, r, sides, color, trim, rot=0):
                pts = [(cx + r * math.cos(2*math.pi*i/sides + rot), cy + r * math.sin(2*math.pi*i/sides + rot)) for i in range(sides)]
                draw.polygon(pts, fill=color, outline=trim, width=th)
                return pts

            # Primary Chassis Plate
            chassis_pts = draw_beveled_poly(c_x, c_y, b_w * 1.1, 6, c_hot_rod, c_stark_gold, rot=math.pi/6)

            # 3. VENTILATION SLITS & DATA SHELVES
            # Draw technical "slats" on the armor
            for i in range(4):
                offset = (i - 1.5) * (b_w * 0.3)
                draw.line([c_x - b_w*0.5, c_y + offset, c_x + b_w*0.5, c_y + offset], fill=c_black, width=int(1.5*scale))
                # Add tiny "data blips" on the slats
                if random.random() > 0.5:
                    draw.rectangle([c_x + b_w*0.4, c_y + offset - 2, c_x + b_w*0.5, c_y + offset + 2], fill=c_reactor)

            # 4. SHOULDER ASSEMBLIES (Modular Plating)
            # Left Assembly
            draw.polygon([(c_x - b_w*1.1, c_y - b_w*0.4), (c_x - b_w*1.8, c_y), (c_x - b_w*1.1, c_y + b_w*0.4)], fill=c_hot_rod, outline=c_stark_gold, width=th)
            # Right Assembly
            draw.polygon([(c_x + b_w*1.1, c_y - b_w*0.4), (c_x + b_w*1.8, c_y), (c_x + b_w*1.1, c_y + b_w*0.4)], fill=c_hot_rod, outline=c_stark_gold, width=th)

            # 5. THE HEAD: MARK VI HELMET (Technical Core)
            hx, hy = c_x, c_y - b_w*1.2
            hr = b_w * 0.8
            draw_beveled_poly(hx, hy, hr, 6, c_hot_rod, c_stark_gold)

            # --- HUD REPLACEMENT (No Face, Just Data) ---
            # Scrolling HUD background
            draw.rectangle([hx - hr*0.7, hy - hr*0.3, hx + hr*0.7, hy + hr*0.3], fill=c_black, outline=c_reactor, width=1)

            # Holographic "Code" lines
            for i in range(3):
                y_off = (i - 1) * (hr * 0.15)
                draw.line([hx - hr*0.6, hy + y_off, hx + hr*(random.uniform(-0.5, 0.6)), hy + y_off], fill=c_hologram, width=1)

            # Technical Eyes (Dual Slits)
            draw.rectangle([hx - hr*0.6, hy - hr*0.1, hx - hr*0.2, hy + hr*0.1], fill=c_reactor)
            draw.rectangle([hx + hr*0.2, hy - hr*0.1, hx + hr*0.6, hy + hr*0.1], fill=c_reactor)

            # 6. RECESSED ARC REACTOR ASSEMBLY
            # Draw the "Pit"
            draw.ellipse([c_x - b_w*0.35, c_y - b_w*0.35, c_x + b_w*0.35, c_y + b_w*0.35], fill=c_black, outline=c_steel, width=th)

            # The Core
            p = 1.0 + getattr(self, 'arc_reactor_current_intensity', 0.1) * math.sin(getattr(self, 'arc_reactor_pulse_base', 0))
            ar = (b_w * 0.25) * p
            draw.ellipse([c_x - ar, c_y - ar, c_x + ar, c_y + ar], fill=c_reactor, outline=(255,255,255,255), width=int(scale))

            # Internal Struts over the reactor
            for angle in [0, 120, 240]:
                rad = math.radians(angle + (self.animation_frame * 2))
                draw.line([c_x, c_y, c_x + ar*math.cos(rad), c_y + ar*math.sin(rad)], fill=c_black, width=1)

            # 7. FINAL STARK COMPOSITION
            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'kenny_photo'): del self.kenny_photo
            self.kenny_photo = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.kenny_photo)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"❌ STARK CORE CRASH: {e}", exc_info=True)
"""

    start_marker = "    def draw_kenny(self):"
    end_marker = "    def smooth_interpolate_position(self):"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"❌ Could not find markers: {start_idx}, {end_idx}")
        return

    new_content = content[:start_idx] + new_method + "\n" + content[end_idx:]
    file_path.write_text(new_content, encoding='utf-8')
    print("✅ Stark Industries surgeons successfully installed the Mark VI Core.")

if __name__ == "__main__":
    stark_interface_transformation()
