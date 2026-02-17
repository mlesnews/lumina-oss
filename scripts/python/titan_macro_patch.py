import sys
from pathlib import Path

def macro_transformation():
    file_path = Path("scripts/python/kenny_imva_enhanced.py")
    content = file_path.read_text(encoding='utf-8')

    new_method = """    def draw_kenny(self):
        \"\"\"Draw Kenny sprite with components - TITAN MACRO VERSION\"\"\"
        try:
            if not self.canvas: return
            self.canvas.delete("all")
            if not PIL_AVAILABLE: return

            # MACRO SCALE: Increase render quality and thickness
            scale = 3
            img_size = int(self.size * scale)
            img = Image.new('RGBA', (img_size, img_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)

            c_x, c_y = (self.size / 2) * scale, (self.size / 2) * scale
            s_s = self.size * scale

            # --- MACRO COLOR PALETTE ---
            cb = (180, 0, 0, 255)    # Deep Metallic Red (Titan Red)
            ch = (180, 0, 0, 255)    # Deep Metallic Red
            cu = (10, 10, 10, 255)   # Obsidian Black HUD
            ca = (0, 255, 255, 255)  # Hyper-Cyan Arc
            ct = (255, 215, 0, 255)  # Bright Gold Trim
            cs = (150, 150, 150, 255) # Industrial Steel Gray

            # MACRO THICKNESS
            th = int(3 * scale) 

            # --- DRAWING SEQUENCE: TITAN BUILD ---
            b_r = (self.size * 0.45) * scale # Massive Body Radius

            # 1. EXTENDED MECHANICAL NECK
            neck_w, neck_h = b_r * 0.8, b_r * 0.5
            draw.rectangle([c_x - neck_w/2, c_y - b_r*1.2, c_x + neck_w/2, c_y - b_r*0.6], fill=cs, outline=ct, width=th)

            # 2. TITAN SHOULDER PAULDRONS (V-TAPER)
            # Doubled width and height from previous build
            draw.polygon([(c_x - b_r, c_y - b_r*0.5), (c_x - b_r*2.2, c_y), (c_x - b_r, c_y + b_r*0.5)], fill=cb, outline=ct, width=th)
            draw.polygon([(c_x + b_r, c_y - b_r*0.5), (c_x + b_r*2.2, c_y), (c_x + b_r, c_y + b_r*0.5)], fill=cb, outline=ct, width=th)

            # 3. ANGULAR HULL (Diamond Armor)
            draw.polygon([(c_x - b_r, c_y), (c_x, c_y + b_r*1.3), (c_x + b_r, c_y), (c_x, c_y - b_r*0.8)], fill=cb, outline=ct, width=th)

            # 4. TITAN HEX-HELMET
            hx, hy = c_x, c_y - b_r*1.1
            hr = b_r * 0.9 # Massive Helmet
            import math
            hex_pts = [(hx + hr * math.cos(2*math.pi*i/6 - math.pi/2), hy + hr * math.sin(2*math.pi*i/6 - math.pi/2)) for i in range(6)]
            draw.polygon(hex_pts, fill=ch, outline=ct, width=th)

            # 5. INDUSTRIAL HUD & EYES
            hud_w, hud_h = hr * 1.2, hr * 0.6
            draw.rectangle([hx - hud_w/2, hy - hud_h/2, hx + hud_w/2, hy + hud_h/2], fill=cu, outline=ct, width=int(scale))

            # Massive Glowing Eyes
            ew, eh, ey = int(s_s*0.25), int(s_s*0.08), hy - int(s_s*0.05)
            draw.rectangle([hx - s_s*0.1 - ew, ey - eh/2, hx - s_s*0.1, ey + eh/2], fill=ca)
            draw.rectangle([hx + s_s*0.1, ey - eh/2, hx + s_s*0.1 + ew, ey + eh/2], fill=ca)

            # 6. OVERSIZED ARC REACTOR
            p = 1.0 + getattr(self, 'arc_reactor_current_intensity', 0.1) * math.sin(getattr(self, 'arc_reactor_pulse_base', 0))
            ar = (b_r * 0.3) * p
            draw.ellipse([c_x - ar, c_y - ar, c_x + ar, c_y + ar], fill=ca, outline=(255,255,255,255), width=th)

            # 7. FINAL COMPOSITION
            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'kenny_photo'): del self.kenny_photo
            self.kenny_photo = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.kenny_photo)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"❌ TITAN CORE CRASH: {e}", exc_info=True)
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
    print("✅ Titan surgeons successfully installed the macro core.")

if __name__ == "__main__":
    macro_transformation()
