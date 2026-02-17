import sys
from pathlib import Path

def super_macro_transformation():
    file_path = Path("scripts/python/kenny_imva_enhanced.py")
    content = file_path.read_text(encoding='utf-8')

    new_method = """    def draw_kenny(self):
        \"\"\"Draw Kenny sprite with components - SUPER MACRO CHASSIS v1\"\"\"
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

            # --- INDUSTRIAL COLOR PALETTE ---
            c_red = (150, 0, 0, 255)      # Industrial Crimson
            c_steel = (100, 105, 110, 255) # Titanium Steel
            c_gold = (255, 215, 0, 255)    # Bolt Gold
            c_cyan = (0, 255, 255, 255)    # Power Cyan
            c_black = (5, 5, 5, 255)       # Vent Black

            th = int(4 * scale) # Massive Line Thickness

            # --- DRAWING SEQUENCE: THE CHASSIS ---
            # Total size reference
            b_w = (self.size * 0.5) * scale 

            # 1. HYDRAULIC NECK COLUMN (Center connection)
            draw.rectangle([c_x - b_w*0.4, c_y - b_w*1.5, c_x + b_w*0.4, c_y - b_w*0.8], fill=c_steel, outline=c_gold, width=th)

            # 2. THE OCTAGON CHASSIS (No more circles!)
            # Main torso plates
            import math
            def get_poly(cx, cy, r, sides, rot=0):
                return [(cx + r * math.cos(2*math.pi*i/sides + rot), cy + r * math.sin(2*math.pi*i/sides + rot)) for i in range(sides)]

            chassis_pts = get_poly(c_x, c_y, b_w * 1.2, 8, rot=math.pi/8)
            draw.polygon(chassis_pts, fill=c_red, outline=c_gold, width=th)

            # 3. INDUSTRIAL VENTILATION SLATS (Breaking the surface)
            for i in range(3):
                v_y = c_y + (i-1) * (b_w*0.4)
                draw.rectangle([c_x - b_w*0.6, v_y - b_w*0.1, c_x + b_w*0.6, v_y + b_w*0.1], fill=c_black)

            # 4. BOLTED SHOULDER PLATES (Massive angularity)
            # Left Plate
            draw.polygon([(c_x - b_w*1.2, c_y - b_w*0.8), (c_x - b_w*2.5, c_y), (c_x - b_w*1.2, c_y + b_w*0.8)], fill=c_steel, outline=c_gold, width=th)
            # Right Plate
            draw.polygon([(c_x + b_w*1.2, c_y - b_w*0.8), (c_x + b_w*2.5, c_y), (c_x + b_w*1.2, c_y + b_w*0.8)], fill=c_steel, outline=c_gold, width=th)

            # 5. THE HEAD: HEAVY ARMOR BOX (Geometric Helmet)
            hx, hy = c_x, c_y - b_w*1.4
            hr = b_w * 1.1
            head_pts = get_poly(hx, hy, hr, 6) # Hex-head
            draw.polygon(head_pts, fill=c_red, outline=c_gold, width=th)

            # Massive Industrial HUD
            draw.rectangle([hx - hr*0.8, hy - hr*0.4, hx + hr*0.8, hy + hr*0.4], fill=c_black, outline=c_gold, width=int(scale))

            # Linear Power Eyes
            draw.rectangle([hx - hr*0.7, hy - hr*0.1, hx - hr*0.2, hy + hr*0.1], fill=c_cyan)
            draw.rectangle([hx + hr*0.2, hy - hr*0.1, hx + hr*0.7, hy + hr*0.1], fill=c_cyan)

            # 6. CENTRAL POWER CORE (Rectangular Housing)
            draw.rectangle([c_x - b_w*0.3, c_y - b_w*0.3, c_x + b_w*0.3, c_y + b_w*0.3], fill=c_black, outline=c_steel, width=th)
            p = 1.0 + getattr(self, 'arc_reactor_current_intensity', 0.1) * math.sin(getattr(self, 'arc_reactor_pulse_base', 0))
            ar = (b_w * 0.25) * p
            draw.ellipse([c_x - ar, c_y - ar, c_x + ar, c_y + ar], fill=c_cyan, outline=(255,255,255,255), width=int(scale))

            # 7. EXPOSED BOLTS (Rivets on corners)
            for pt in chassis_pts[::2]: # Every other corner
                draw.ellipse([pt[0]-5, pt[1]-5, pt[0]+5, pt[1]+5], fill=c_gold)

            # 8. FINAL COMPOSITION
            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'kenny_photo'): del self.kenny_photo
            self.kenny_photo = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.kenny_photo)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"❌ SUPER MACRO CRASH: {e}", exc_info=True)
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
    print("✅ Super Macro patch installed. The circle is dead.")

if __name__ == "__main__":
    super_macro_transformation()
