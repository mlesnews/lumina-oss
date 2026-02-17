import sys
from pathlib import Path

def patch_kenny():
    file_path = Path("scripts/python/kenny_imva_enhanced.py")
    if not file_path.exists():
        print(f"❌ File not found: {file_path}")
        return

    content = file_path.read_text(encoding='utf-8')

    # 1. Define the new Bulletproof Drawing Method
    new_method = """    def draw_kenny(self):
        \"\"\"Draw Kenny sprite with components - MECHANICAL CORE v2\"\"\"
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

            # --- SAFE ZONE: Component & Color Validation ---
            try:
                if not self.sprite_components: raise ValueError("No components")

                cb = self.validate_color(self.sprite_components.body.color, (220, 20, 60, 255))
                ch = self.validate_color(self.sprite_components.helmet.color, (220, 20, 60, 255))
                cu = self.validate_color(self.sprite_components.hud.color, (0, 0, 0, 255))
                cf = self.validate_color(self.sprite_components.face.color, (0, 0, 0, 255))
                ca = self.validate_color(self.sprite_components.arc_reactor.color, (0, 217, 255, 255))
                ct = (255, 215, 0, 255) # Gold trim

                body_comp = self.sprite_components.body
                helm_comp = self.sprite_components.helmet
                hud_comp  = self.sprite_components.hud
                face_comp = self.sprite_components.face
                arc_comp  = self.sprite_components.arc_reactor
            except Exception as e:
                cb, ch, cu, cf, ca, ct = (220,20,60,255), (220,20,60,255), (0,0,0,255), (0,0,0,255), (0,217,255,255), (255,215,0,255)
                from kenny_sprite_components import BodyComponent, HelmetComponent, HUDComponent, FaceComponent, ArcReactorComponent
                body_comp, helm_comp, hud_comp, face_comp, arc_comp = BodyComponent(), HelmetComponent(), HUDComponent(), FaceComponent(), ArcReactorComponent()

            # --- DRAWING SEQUENCE ---
            if body_comp.enabled:
                b_r = body_comp.get_scaled_size(s_s) * body_comp.radius_ratio
                draw.rectangle([c_x - b_r*0.3, c_y - b_r*1.1, c_x + b_r*0.3, c_y - b_r*0.7], fill=(80,80,80,255), outline=ct)
                draw.polygon([(c_x - b_r, c_y), (c_x, c_y + b_r), (c_x + b_r, c_y), (c_x, c_y - b_r*0.6)], fill=cb, outline=ct)
                sh_h = b_r * 0.3
                draw.polygon([(c_x - b_r, c_y - sh_h), (c_x - b_r*1.4, c_y), (c_x - b_r, c_y + sh_h)], fill=cb, outline=ct)
                draw.polygon([(c_x + b_r, c_y - sh_h), (c_x + b_r*1.4, c_y), (c_x + b_r, c_y + sh_h)], fill=cb, outline=ct)
                draw.ellipse([c_x - b_r*0.6, c_y - b_r*0.6, c_x + b_r*0.6, c_y + b_r*0.6], fill=cb, outline=(184, 134, 11, 255))

            if helm_comp.enabled:
                hx, hy = helm_comp.get_position(c_x, c_y, s_s)
                hw, hh = helm_comp.get_scaled_size(s_s) * helm_comp.width_ratio, helm_comp.get_scaled_size(s_s) * helm_comp.height_ratio
                hr = min(hw, hh) / 2
                import math
                hex_pts = [(hx + hr * math.cos(2*math.pi*i/6 - math.pi/2), hy + hr * math.sin(2*math.pi*i/6 - math.pi/2)) for i in range(6)]
                draw.polygon(hex_pts, fill=ch, outline=ct)
                if hud_comp.enabled:
                    hdw, hdh = hud_comp.get_scaled_size(s_s) * hud_comp.width_ratio, hud_comp.get_scaled_size(s_s) * hud_comp.height_ratio
                    draw.rectangle([hx - hdw/2, hy - hdh/2, hx + hdw/2, hy + hdh/2], fill=cu)
                    ew, eh, ey = int(s_s*0.12), int(s_s*0.04), hy - int(s_s*0.08)
                    draw.rectangle([hx - s_s*0.15 - ew, ey - eh/2, hx - s_s*0.15, ey + eh/2], fill=(0,217,255,255))
                    draw.rectangle([hx + s_s*0.15, ey - eh/2, hx + s_s*0.15 + ew, ey + eh/2], fill=(0,217,255,255))

            if arc_comp.enabled:
                ax, ay = arc_comp.get_position(c_x, c_y, s_s)
                import math
                p = 1.0 + getattr(self, 'arc_reactor_current_intensity', 0.1) * math.sin(getattr(self, 'arc_reactor_pulse_base', 0))
                ar = (arc_comp.get_scaled_size(s_s) * arc_comp.radius_ratio) * p
                draw.ellipse([ax - ar, ay - ar, ax + ar, ay + ar], fill=ca, outline=(255,255,255,255), width=int(scale))

            img_final = img.resize((self.size, self.size), Image.Resampling.LANCZOS)
            if hasattr(self, 'kenny_photo'): del self.kenny_photo
            self.kenny_photo = ImageTk.PhotoImage(img_final)
            self.canvas.create_image(self.size/2, self.size/2, image=self.kenny_photo)
            self.root.update_idletasks()
        except Exception as e:
            logger.error(f"❌ MECHANICAL CORE CRASH: {e}", exc_info=True)
"""

    # 2. Extract and Replace
    import re
    # Find the start of draw_kenny and the end (start of smooth_interpolate_position)
    start_marker = "    def draw_kenny(self):"
    end_marker = "    def smooth_interpolate_position(self):"

    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker)

    if start_idx == -1 or end_idx == -1:
        print(f"❌ Could not find markers: {start_idx}, {end_idx}")
        return

    new_content = content[:start_idx] + new_method + "\n" + content[end_idx:]
    file_path.write_text(new_content, encoding='utf-8')
    print("✅ Kenny surgeons successfully patched the core.")

if __name__ == "__main__":
    patch_kenny()
