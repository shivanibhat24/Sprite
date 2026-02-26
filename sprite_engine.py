"""
Sprite! — Game Asset Generator Engine
Core generation logic for 2D sprites, 3D assets, tilemaps, and more.
Created by Shivani. No external APIs required.
"""

import math
import random
import colorsys
import hashlib
import struct
import io
import json
import base64
import zipfile
import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance, ImageFont
import numpy as np
from scipy.ndimage import gaussian_filter


# ─────────────────────────────────────────────
#  UTILITY HELPERS
# ─────────────────────────────────────────────

def parse_prompt(prompt: str) -> dict:
    """Extract tags, style, colors, and intent from a natural language prompt."""
    prompt_lower = prompt.lower()

    # Category detection
    categories = {
        "character": ["character", "hero", "enemy", "npc", "player", "warrior", "wizard", "knight",
                      "monster", "creature", "robot", "alien", "zombie", "dragon", "boss"],
        "tile": ["tile", "tileset", "floor", "wall", "ground", "platform", "terrain", "brick", "stone"],
        "item": ["item", "weapon", "sword", "gun", "potion", "chest", "key", "coin", "gem", "shield", "bow"],
        "ui": ["ui", "button", "hud", "icon", "cursor", "frame", "panel", "bar", "health", "mana"],
        "environment": ["tree", "rock", "bush", "cloud", "mountain", "house", "castle", "dungeon", "cave", "water"],
        "vehicle": ["car", "ship", "spaceship", "tank", "plane", "boat", "rocket"],
        "prop": ["barrel", "crate", "table", "chair", "lamp", "door", "window", "sign", "fence", "pillar"],
        "particle": ["particle", "explosion", "fire", "smoke", "spark", "magic", "effect", "trail"],
        "icon": ["icon", "logo", "badge", "medal", "star", "heart", "diamond"],
    }
    detected_category = "character"
    for cat, keywords in categories.items():
        if any(k in prompt_lower for k in keywords):
            detected_category = cat
            break

    # Style detection
    styles = {
        "pixel": ["pixel", "8-bit", "8bit", "16-bit", "16bit", "retro", "nes", "snes", "gameboy"],
        "cartoon": ["cartoon", "toon", "comic", "cel", "flat", "chibi", "cute", "kawaii"],
        "realistic": ["realistic", "realistic", "detailed", "hd", "high detail", "gritty"],
        "neon": ["neon", "glow", "cyberpunk", "cyber", "synthwave", "glowing"],
        "minimalist": ["minimal", "simple", "clean", "flat design", "icon style"],
        "fantasy": ["fantasy", "magical", "medieval", "rpg", "enchanted", "arcane"],
        "sci-fi": ["sci-fi", "scifi", "futuristic", "space", "alien", "cyber"],
    }
    detected_style = "pixel"
    for sty, keywords in styles.items():
        if any(k in prompt_lower for k in keywords):
            detected_style = sty
            break

    # Color palette detection
    palettes = {
        "fire": ["fire", "flame", "lava", "hot", "red", "orange", "ember"],
        "ice": ["ice", "frost", "frozen", "cold", "blue", "winter", "snow"],
        "nature": ["nature", "forest", "green", "grass", "plant", "leaf", "jungle"],
        "dark": ["dark", "shadow", "black", "night", "void", "evil", "undead", "demon"],
        "gold": ["gold", "treasure", "rich", "yellow", "sunny", "divine"],
        "poison": ["poison", "toxic", "purple", "venom", "acid", "swamp"],
        "ocean": ["ocean", "water", "sea", "aqua", "cyan", "underwater"],
        "stone": ["stone", "rock", "gray", "grey", "iron", "steel", "metal"],
        "magic": ["magic", "arcane", "mystical", "ethereal", "enchanted", "spell"],
    }
    detected_palette = "magic"
    for pal, keywords in palettes.items():
        if any(k in prompt_lower for k in keywords):
            detected_palette = pal
            break

    # Size detection
    size = 64
    if any(x in prompt_lower for x in ["128", "large"]):    size = 128
    if any(x in prompt_lower for x in ["256", "big"]):      size = 256
    if any(x in prompt_lower for x in ["32", "small"]):     size = 32
    if any(x in prompt_lower for x in ["16", "tiny"]):      size = 16
    if any(x in prompt_lower for x in ["512", "huge"]):     size = 512

    # Seed from prompt for reproducibility
    seed = int(hashlib.md5(prompt.encode()).hexdigest(), 16) % (2**32)

    return {
        "prompt": prompt,
        "category": detected_category,
        "style": detected_style,
        "palette": detected_palette,
        "size": size,
        "seed": seed,
    }


def get_palette(name: str) -> list:
    """Return a list of (R,G,B) colors for a named palette."""
    palettes = {
        "fire":      [(255,60,0),(255,120,0),(255,200,0),(180,20,0),(255,255,180),(100,10,0)],
        "ice":       [(180,230,255),(100,180,255),(50,120,220),(200,240,255),(255,255,255),(20,60,160)],
        "nature":    [(34,120,20),(80,180,40),(150,210,80),(60,90,30),(200,230,100),(30,60,10)],
        "dark":      [(20,10,30),(60,20,60),(100,30,80),(150,50,100),(200,80,120),(10,5,20)],
        "gold":      [(220,180,0),(255,220,50),(180,130,0),(255,240,150),(150,100,0),(255,255,200)],
        "poison":    [(80,180,0),(40,120,0),(120,220,30),(200,255,100),(20,80,0),(180,255,50)],
        "ocean":     [(0,80,180),(0,140,220),(50,200,250),(0,200,200),(100,230,255),(0,50,130)],
        "stone":     [(80,80,90),(120,120,130),(160,160,170),(60,60,70),(200,200,210),(40,40,50)],
        "magic":     [(120,0,200),(180,50,255),(80,0,150),(230,150,255),(255,200,255),(40,0,100)],
        "neon":      [(0,255,150),(255,0,150),(0,200,255),(255,255,0),(200,0,255),(255,100,0)],
        "earth":     [(120,80,40),(160,110,60),(200,150,90),(80,50,20),(230,200,150),(50,30,10)],
        "blood":     [(150,0,0),(200,20,20),(255,50,50),(100,0,0),(255,150,150),(50,0,0)],
    }
    return palettes.get(name, palettes["magic"])


def color_to_hex(rgb):
    return "#{:02x}{:02x}{:02x}".format(*rgb)


def lerp_color(c1, c2, t):
    return tuple(int(c1[i] + (c2[i]-c1[i])*t) for i in range(3))


def perlin_like_noise(w, h, scale=8, seed=0):
    """Simple deterministic noise without external libs."""
    rng = np.random.RandomState(seed)
    grid_w = w // scale + 2
    grid_h = h // scale + 2
    grid = rng.rand(grid_h, grid_w)
    # Upsample with smooth interpolation
    from scipy.ndimage import zoom
    factor_y = h / (grid_h * scale)
    factor_x = w / (grid_w * scale)
    big = zoom(grid, (h / grid_h, w / grid_w), order=3)
    big = big[:h, :w]
    big = (big - big.min()) / (big.max() - big.min() + 1e-9)
    return big


# ─────────────────────────────────────────────
#  2D SPRITE GENERATORS
# ─────────────────────────────────────────────

class SpriteGenerator:
    """Generates pixel-art and styled 2D sprites from parsed prompt info."""

    def __init__(self, info: dict):
        self.info = info
        self.size = info["size"]
        self.palette = get_palette(info["palette"])
        random.seed(info["seed"])
        np.random.seed(info["seed"] % (2**31))

    def generate(self) -> Image.Image:
        cat = self.info["category"]
        style = self.info["style"]

        if cat == "character":
            img = self._gen_character()
        elif cat == "tile":
            img = self._gen_tile()
        elif cat == "item":
            img = self._gen_item()
        elif cat == "ui":
            img = self._gen_ui()
        elif cat == "environment":
            img = self._gen_environment()
        elif cat == "vehicle":
            img = self._gen_vehicle()
        elif cat == "prop":
            img = self._gen_prop()
        elif cat == "particle":
            img = self._gen_particle_effect()
        elif cat == "icon":
            img = self._gen_icon()
        else:
            img = self._gen_character()

        # Apply style post-processing
        if style == "pixel":
            img = self._pixelize(img)
        elif style == "neon":
            img = self._add_glow(img)
        elif style == "cartoon":
            img = self._cartoonify(img)

        return img

    def _base_canvas(self, alpha=True):
        mode = "RGBA" if alpha else "RGB"
        return Image.new(mode, (self.size, self.size), (0, 0, 0, 0) if alpha else (0, 0, 0))

    def _pick(self, palette=None, idx=None):
        p = palette or self.palette
        if idx is not None:
            return p[idx % len(p)]
        return random.choice(p)

    def _gen_character(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette

        # Color assignments
        skin = p[random.randint(0, len(p)//2)]
        body = p[random.randint(0, len(p)-1)]
        accent = p[(self.palette.index(body) + 2) % len(p)]
        dark = tuple(max(0, c-60) for c in body)
        highlight = tuple(min(255, c+80) for c in body)

        # --- Body proportions ---
        head_r = s // 7
        body_w = s // 4
        body_h = s // 3

        cx = s // 2
        head_cy = s // 4
        body_top = head_cy + head_r
        body_bot = body_top + body_h
        leg_h = s // 5

        # Legs
        leg_w = body_w // 2 - 2
        lleg_x = cx - body_w // 2
        rleg_x = cx + 2
        for ly in range(body_bot, body_bot + leg_h, 2):
            draw.rectangle([lleg_x, ly, lleg_x + leg_w, ly+2], fill=dark)
            draw.rectangle([rleg_x, ly, rleg_x + leg_w, ly+2], fill=dark)
        # Feet
        draw.ellipse([lleg_x-2, body_bot+leg_h-4, lleg_x+leg_w+2, body_bot+leg_h+4], fill=dark)
        draw.ellipse([rleg_x-2, body_bot+leg_h-4, rleg_x+leg_w+2, body_bot+leg_h+4], fill=dark)

        # Body
        draw.rounded_rectangle([cx-body_w//2, body_top, cx+body_w//2, body_bot], radius=4, fill=body)
        # Body detail line
        draw.line([(cx, body_top+4), (cx, body_bot-4)], fill=dark, width=1)
        # Chest emblem
        ew = body_w // 3
        draw.ellipse([cx-ew//2, body_top+body_h//4, cx+ew//2, body_top+body_h//4+ew], fill=accent)

        # Arms
        arm_w = s // 12
        arm_h = body_h // 2 + 4
        draw.rounded_rectangle([cx-body_w//2-arm_w-1, body_top+2, cx-body_w//2, body_top+arm_h], radius=3, fill=body)
        draw.rounded_rectangle([cx+body_w//2+1, body_top+2, cx+body_w//2+arm_w+1, body_top+arm_h], radius=3, fill=body)
        # Hands
        hw = arm_w + 2
        draw.ellipse([cx-body_w//2-arm_w-1, body_top+arm_h-4, cx-body_w//2+2, body_top+arm_h+hw], fill=skin)
        draw.ellipse([cx+body_w//2-2, body_top+arm_h-4, cx+body_w//2+arm_w+2, body_top+arm_h+hw], fill=skin)

        # Neck
        nw = 6
        draw.rectangle([cx-nw//2, head_cy+head_r-2, cx+nw//2, body_top+2], fill=skin)

        # Head
        draw.ellipse([cx-head_r, head_cy-head_r, cx+head_r, head_cy+head_r], fill=skin)
        # Eyes
        ey = head_cy - 2
        ex_off = head_r // 2
        draw.ellipse([cx-ex_off-3, ey-3, cx-ex_off+3, ey+3], fill=(255,255,255))
        draw.ellipse([cx+ex_off-3, ey-3, cx+ex_off+3, ey+3], fill=(255,255,255))
        draw.ellipse([cx-ex_off-1, ey-1, cx-ex_off+2, ey+2], fill=accent)
        draw.ellipse([cx+ex_off-1, ey-1, cx+ex_off+2, ey+2], fill=accent)
        draw.ellipse([cx-ex_off, ey, cx-ex_off+1, ey+1], fill=(0,0,0))
        draw.ellipse([cx+ex_off, ey, cx+ex_off+1, ey+1], fill=(0,0,0))
        # Mouth
        draw.arc([cx-4, head_cy+2, cx+4, head_cy+6], 0, 180, fill=(0,0,0), width=1)
        # Hair
        hair_pts = [(cx-head_r+1, head_cy-2)]
        for i in range(7):
            ang = math.pi - i * math.pi / 6
            hx = int(cx + (head_r+1)*math.cos(ang))
            hy = int(head_cy + (head_r+1)*math.sin(ang))
            hair_pts.append((hx, hy))
        if len(hair_pts) > 2:
            draw.polygon(hair_pts, fill=accent)

        # Shadow
        draw.ellipse([cx-body_w//2, s-10, cx+body_w//2, s-2], fill=(0,0,0,80))
        return img

    def _gen_tile(self) -> Image.Image:
        img = self._base_canvas(alpha=False)
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette

        # Background base
        base = p[0]
        img.paste(base + (255,) if len(base)==3 else base, [0,0,s,s])

        noise = perlin_like_noise(s, s, scale=max(4, s//8), seed=self.info["seed"])
        arr = np.array(img.convert("RGB"), dtype=float)

        # Apply noise texture
        c1 = np.array(p[0][:3], dtype=float)
        c2 = np.array(p[1][:3], dtype=float)
        for y in range(s):
            for x in range(s):
                t = noise[y, x]
                color = c1 * (1-t) + c2 * t
                arr[y, x] = color
        img = Image.fromarray(arr.astype(np.uint8), "RGB")
        draw = ImageDraw.Draw(img)

        # Grid lines
        tile_sub = max(s//4, 8)
        for i in range(0, s, tile_sub):
            draw.line([(i, 0), (i, s)], fill=tuple(max(0,c-30) for c in p[0][:3]), width=1)
            draw.line([(0, i), (s, i)], fill=tuple(max(0,c-30) for c in p[0][:3]), width=1)

        # Random details
        rng = random.Random(self.info["seed"])
        for _ in range(rng.randint(3, 8)):
            x, y = rng.randint(4, s-12), rng.randint(4, s-12)
            w2, h2 = rng.randint(3, 8), rng.randint(3, 8)
            col = p[rng.randint(1, len(p)-1)][:3]
            draw.rectangle([x, y, x+w2, y+h2], fill=col)

        # Edge highlight
        draw.rectangle([0,0,s-1,s-1], outline=tuple(min(255,c+40) for c in p[0][:3]), width=1)
        return img.convert("RGBA")

    def _gen_item(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        prompt = self.info["prompt"].lower()
        cx, cy = s//2, s//2

        if any(w in prompt for w in ["sword","blade","knife","dagger"]):
            # Sword
            blade_col = p[2][:3]
            hilt_col = p[0][:3]
            guard_col = p[1][:3]
            bw = max(4, s//12)
            bh = int(s*0.65)
            # Blade
            blade_pts = [(cx, cy-bh//2), (cx+bw//2, cy+bh//4), (cx, cy+bh//2), (cx-bw//2, cy+bh//4)]
            draw.polygon(blade_pts, fill=blade_col)
            # Shine
            draw.line([(cx-1, cy-bh//2+4), (cx-1, cy+bh//4-4)], fill=(255,255,255,180), width=1)
            # Guard
            gw = bw*3
            draw.rectangle([cx-gw//2, cy+bh//4-4, cx+gw//2, cy+bh//4+4], fill=guard_col)
            # Handle
            hw = bw
            draw.rounded_rectangle([cx-hw//2, cy+bh//4+4, cx+hw//2, cy+bh//2+8], radius=2, fill=hilt_col)
            draw.ellipse([cx-hw//2-2, cy+bh//2+6, cx+hw//2+2, cy+bh//2+14], fill=guard_col)

        elif any(w in prompt for w in ["potion","bottle","vial","flask"]):
            # Potion
            liq_col = p[0][:3]
            glass_col = (200,230,255)
            # Bottle body
            by1 = cy-s//6; by2 = cy+s//3
            bw2 = s//4
            draw.ellipse([cx-bw2, by1, cx+bw2, by2], fill=glass_col)
            # Liquid fill
            liq_y = by1 + (by2-by1)//3
            draw.ellipse([cx-bw2+3, liq_y, cx+bw2-3, by2-3], fill=liq_col)
            # Neck
            nw2 = s//10
            draw.rectangle([cx-nw2, cy-s//3, cx+nw2, by1+4], fill=glass_col)
            # Cork
            draw.rectangle([cx-nw2-2, cy-s//3-6, cx+nw2+2, cy-s//3], fill=(160,100,40))
            # Shine
            draw.ellipse([cx-bw2+4, by1+4, cx-bw2+12, by1+14], fill=(255,255,255,150))
            # Bubble
            draw.ellipse([cx+4, liq_y+6, cx+10, liq_y+12], fill=(255,255,255,120))

        elif any(w in prompt for w in ["coin","gold","medal"]):
            # Coin
            col = p[0][:3]
            dark2 = tuple(max(0,c-50) for c in col)
            light = tuple(min(255,c+60) for c in col)
            r = s//2-8
            draw.ellipse([cx-r, cy-r, cx+r, cy+r], fill=col)
            draw.ellipse([cx-r+4, cy-r+4, cx+r-4, cy+r-4], outline=dark2, width=1)
            # Star emblem
            pts = []
            for i in range(10):
                ang = i * math.pi/5 - math.pi/2
                rad = (r-8) if i%2==0 else (r-14)
                pts.append((cx + int(rad*math.cos(ang)), cy + int(rad*math.sin(ang))))
            if len(pts) >= 3:
                draw.polygon(pts, fill=light)
        else:
            # Generic gem/item
            col = p[0][:3]
            shine = tuple(min(255,c+100) for c in col)
            dark2 = tuple(max(0,c-80) for c in col)
            r = s//3
            # Diamond shape
            gem_pts = [(cx, cy-r), (cx+r*2//3, cy), (cx, cy+r), (cx-r*2//3, cy)]
            draw.polygon(gem_pts, fill=col)
            draw.polygon([(cx, cy-r), (cx+r*2//3, cy), (cx, cy)], fill=shine)
            draw.polygon(gem_pts, outline=dark2, width=1)

        return img

    def _gen_ui(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        prompt = self.info["prompt"].lower()

        if any(w in prompt for w in ["health","hp","heart","life"]):
            # Heart icon
            col = p[0][:3]
            light = tuple(min(255,c+80) for c in col)
            cx, cy = s//2, s//2+4
            r = s//3
            # Two circles for top of heart
            draw.ellipse([cx-r, cy-r, cx, cy], fill=col)
            draw.ellipse([cx, cy-r, cx+r, cy], fill=col)
            # Triangle bottom
            draw.polygon([(cx-r, cy), (cx+r, cy), (cx, cy+r+4)], fill=col)
            # Shine
            draw.ellipse([cx-r+4, cy-r+4, cx-r+12, cy-r+10], fill=(*light,180))
        elif any(w in prompt for w in ["button","btn"]):
            # Stylized button
            col = p[0][:3]
            border = tuple(min(255,c+60) for c in col)
            draw.rounded_rectangle([8, s//3, s-8, s*2//3], radius=8, fill=col)
            draw.rounded_rectangle([8, s//3, s-8, s*2//3], radius=8, outline=border, width=2)
            draw.rounded_rectangle([10, s//3+2, s-10, s//3+6], radius=2, fill=(*border,100))
        else:
            # Generic panel frame
            col = p[0][:3]
            border = p[1][:3]
            draw.rounded_rectangle([4,4,s-4,s-4], radius=6, fill=(*col,200), outline=border, width=2)
            # Corner gems
            for cx2, cy2 in [(8,8),(s-8,8),(8,s-8),(s-8,s-8)]:
                draw.ellipse([cx2-4,cy2-4,cx2+4,cy2+4], fill=p[2][:3])

        return img

    def _gen_environment(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        prompt = self.info["prompt"].lower()

        if any(w in prompt for w in ["tree","plant","bush","forest"]):
            # Tree
            trunk_col = (100, 60, 20)
            leaf_col = p[0][:3]
            leaf_dark = tuple(max(0,c-40) for c in leaf_col)
            leaf_light = tuple(min(255,c+40) for c in leaf_col)
            cx2 = s//2
            # Trunk
            tw = s//8
            draw.rectangle([cx2-tw//2, s*2//3, cx2+tw//2, s-6], fill=trunk_col)
            # Layered canopy
            for i, (ry, rr) in enumerate([(s//2, s//3), (s//3, s//4), (s//4, s//5)]):
                lc = leaf_dark if i==0 else (leaf_col if i==1 else leaf_light)
                draw.ellipse([cx2-rr, ry-rr//2, cx2+rr, ry+rr//2+4], fill=lc)

        elif any(w in prompt for w in ["rock","stone","boulder"]):
            col = p[0][:3]
            light2 = tuple(min(255,c+60) for c in col)
            dark2 = tuple(max(0,c-60) for c in col)
            cx2, cy2 = s//2, s*3//5
            rx, ry = s//3, s//4
            draw.ellipse([cx2-rx, cy2-ry, cx2+rx, cy2+ry], fill=col)
            draw.ellipse([cx2-rx//3, cy2-ry, cx2+rx//4, cy2], fill=light2)
            draw.ellipse([cx2+rx//4, cy2, cx2+rx, cy2+ry], fill=dark2)
            # Cracks
            draw.line([(cx2-10, cy2+5),(cx2+5, cy2-8)], fill=dark2, width=1)
            draw.line([(cx2+8, cy2+8),(cx2+15, cy2-2)], fill=dark2, width=1)

        elif any(w in prompt for w in ["cloud","sky"]):
            col = (220,230,255)
            cx2, cy2 = s//2, s//2
            for ox, oy, r2 in [(-s//5, 4, s//5), (0, -4, s//4), (s//5, 2, s//6), (-s//8, s//8, s//8)]:
                draw.ellipse([cx2+ox-r2, cy2+oy-r2, cx2+ox+r2, cy2+oy+r2], fill=col)

        else:
            # Generic environment object — hill
            col = p[0][:3]
            draw.ellipse([-s//4, s//3, s+s//4, s+10], fill=col)
            draw.ellipse([s//6, s*2//3, s*5//6, s-4], fill=tuple(min(255,c+30) for c in col))

        return img

    def _gen_vehicle(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        prompt = self.info["prompt"].lower()
        col = p[0][:3]; dark2 = tuple(max(0,c-60) for c in col)
        light2 = tuple(min(255,c+80) for c in col)
        cx = s//2

        if any(w in prompt for w in ["spaceship","rocket","ufo"]):
            # Spaceship
            body_pts = [(cx, s//6), (cx+s//3, s*2//3), (cx, s*3//4), (cx-s//3, s*2//3)]
            draw.polygon(body_pts, fill=col)
            # Cockpit
            draw.ellipse([cx-s//8, s//4, cx+s//8, s*2//5], fill=(100,200,255,200))
            # Engine glow
            for ex in [cx-s//8, cx, cx+s//8]:
                draw.ellipse([ex-4, s*3//4-2, ex+4, s*3//4+10], fill=(255,150,0))
            # Wings
            draw.polygon([(cx-s//3, s*2//3), (cx-s//2, s*3//4+4), (cx-s//6, s*3//5)], fill=dark2)
            draw.polygon([(cx+s//3, s*2//3), (cx+s//2, s*3//4+4), (cx+s//6, s*3//5)], fill=dark2)
        else:
            # Car top view
            draw.rounded_rectangle([cx-s//3, s//5, cx+s//3, s*4//5], radius=s//8, fill=col)
            # Windshields
            draw.rounded_rectangle([cx-s//4, s//4, cx+s//4, s*2//5], radius=4, fill=(100,180,255,180))
            draw.rounded_rectangle([cx-s//4, s*3//5, cx+s//4, s*3//4], radius=4, fill=(100,180,255,180))
            # Wheels
            for wx2, wy2 in [(cx-s//3-4, s//4), (cx+s//3-4, s//4),(cx-s//3-4, s*3//5),(cx+s//3-4, s*3//5)]:
                draw.ellipse([wx2, wy2, wx2+10, wy2+14], fill=dark2)

        return img

    def _gen_prop(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        prompt = self.info["prompt"].lower()
        col = p[0][:3]; dark2 = tuple(max(0,c-60) for c in col)
        light2 = tuple(min(255,c+60) for c in col)
        cx = s//2

        if any(w in prompt for w in ["barrel","crate","chest","box"]):
            # Chest/crate
            cx2, cy2 = s//2, s//2
            bw2, bh2 = s*2//3, s//2
            draw.rectangle([cx2-bw2//2, cy2-bh2//2, cx2+bw2//2, cy2+bh2//2], fill=col)
            draw.rectangle([cx2-bw2//2, cy2-bh2//2, cx2+bw2//2, cy2+bh2//2], outline=dark2, width=2)
            # Bands
            for by3 in [cy2-bh2//4, cy2+bh2//4]:
                draw.rectangle([cx2-bw2//2, by3-2, cx2+bw2//2, by3+2], fill=dark2)
            # Lock
            draw.rectangle([cx2-6, cy2-4, cx2+6, cy2+4], fill=p[1][:3])
            draw.ellipse([cx2-4, cy2-6, cx2+4, cy2+0], outline=p[1][:3], width=2)
        else:
            # Generic pillar/column
            pw = s//5
            draw.rectangle([cx-pw//2, s//8, cx+pw//2, s*7//8], fill=col)
            draw.ellipse([cx-pw//2-4, s//8-8, cx+pw//2+4, s//8+6], fill=light2)
            draw.ellipse([cx-pw//2-4, s*7//8-6, cx+pw//2+4, s*7//8+8], fill=dark2)

        return img

    def _gen_particle_effect(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        cx, cy = s//2, s//2
        rng = random.Random(self.info["seed"])

        for i in range(40):
            ang = rng.uniform(0, 2*math.pi)
            dist = rng.uniform(4, s//2-4)
            x = cx + int(dist * math.cos(ang))
            y = cy + int(dist * math.sin(ang))
            size2 = rng.randint(2, max(3, s//16))
            col = rng.choice(p)[:3]
            alpha = int(255 * (1 - dist/(s//2)))
            draw.ellipse([x-size2, y-size2, x+size2, y+size2], fill=(*col, alpha))

        # Center burst
        for r2 in range(s//4, 0, -4):
            alpha = int(200 * (1 - r2/(s//4)))
            draw.ellipse([cx-r2, cy-r2, cx+r2, cy+r2], outline=(*p[0][:3], alpha), width=1)

        return img

    def _gen_icon(self) -> Image.Image:
        img = self._base_canvas()
        draw = ImageDraw.Draw(img)
        s = self.size
        p = self.palette
        cx, cy = s//2, s//2

        # Star icon
        col = p[0][:3]
        light2 = tuple(min(255,c+100) for c in col)
        r_out = s//2 - 6
        r_in  = r_out // 2
        pts = []
        for i in range(10):
            ang = i * math.pi/5 - math.pi/2
            r2 = r_out if i%2==0 else r_in
            pts.append((cx + int(r2*math.cos(ang)), cy + int(r2*math.sin(ang))))
        draw.polygon(pts, fill=col)
        # Shine
        draw.polygon(pts[:4], fill=(*light2, 120))
        return img

    def _pixelize(self, img: Image.Image, factor: int = None) -> Image.Image:
        """Reduce then upscale for pixel art look."""
        s = self.size
        factor = factor or max(2, s // 16)
        small_w, small_h = max(1, s//factor), max(1, s//factor)
        small = img.resize((small_w, small_h), Image.NEAREST)
        return small.resize((s, s), Image.NEAREST)

    def _add_glow(self, img: Image.Image) -> Image.Image:
        """Add neon glow effect."""
        glow = img.filter(ImageFilter.GaussianBlur(radius=6))
        glow = ImageEnhance.Brightness(glow).enhance(1.8)
        result = Image.blend(glow, img, 0.55)
        return result

    def _cartoonify(self, img: Image.Image) -> Image.Image:
        """Cartoonify with edge enhancement."""
        edges = img.filter(ImageFilter.FIND_EDGES)
        result = img.filter(ImageFilter.SMOOTH_MORE)
        result = ImageEnhance.Color(result).enhance(1.5)
        return result


# ─────────────────────────────────────────────
#  3D ASSET GENERATORS (OBJ + multi-view renders)
# ─────────────────────────────────────────────

class Asset3DGenerator:
    """Generates simple 3D mesh data + renders multi-view images."""

    def __init__(self, info: dict):
        self.info = info
        self.size = min(info["size"], 256)
        self.palette = get_palette(info["palette"])
        random.seed(info["seed"])
        np.random.seed(info["seed"] % (2**31))

    def generate_obj(self) -> str:
        """Generate a .obj mesh string based on category."""
        cat = self.info["category"]
        if cat == "character":   return self._char_obj()
        elif cat == "vehicle":   return self._vehicle_obj()
        elif cat == "environment": return self._env_obj()
        else:                    return self._generic_obj()

    def generate_mtl(self) -> str:
        """Generate .mtl material string."""
        col = self.palette[0]
        r, g, b = col[0]/255, col[1]/255, col[2]/255
        col2 = self.palette[1]
        r2,g2,b2 = col2[0]/255, col2[1]/255, col2[2]/255
        return f"""# Sprite! Material File
newmtl Material_Base
Ka {r:.3f} {g:.3f} {b:.3f}
Kd {r:.3f} {g:.3f} {b:.3f}
Ks 0.5 0.5 0.5
Ns 32.0
d 1.0

newmtl Material_Accent
Ka {r2:.3f} {g2:.3f} {b2:.3f}
Kd {r2:.3f} {g2:.3f} {b2:.3f}
Ks 0.8 0.8 0.8
Ns 64.0
d 1.0
"""

    def _char_obj(self) -> str:
        """Simple humanoid mesh (body parts as boxes/cylinders approximated)."""
        verts = []
        faces = []

        def add_box(cx, cy, cz, w, h, d, mat="Material_Base"):
            base = len(verts) + 1
            hw, hh, hd = w/2, h/2, d/2
            box_verts = [
                (cx-hw,cy-hh,cz-hd),(cx+hw,cy-hh,cz-hd),(cx+hw,cy+hh,cz-hd),(cx-hw,cy+hh,cz-hd),
                (cx-hw,cy-hh,cz+hd),(cx+hw,cy-hh,cz+hd),(cx+hw,cy+hh,cz+hd),(cx-hw,cy+hh,cz+hd),
            ]
            for v in box_verts: verts.append(v)
            box_faces = [
                f"usemtl {mat}\n"
                f"f {base} {base+1} {base+2} {base+3}\n"
                f"f {base+7} {base+6} {base+5} {base+4}\n"
                f"f {base} {base+4} {base+5} {base+1}\n"
                f"f {base+2} {base+6} {base+7} {base+3}\n"
                f"f {base+1} {base+5} {base+6} {base+2}\n"
                f"f {base+3} {base+7} {base+4} {base}\n"
            ]
            faces.extend(box_faces)

        # Body parts (y=up convention)
        add_box(0, 0.5, 0, 0.5, 0.7, 0.3, "Material_Base")       # torso
        add_box(0, 1.3, 0, 0.35, 0.35, 0.35, "Material_Accent")  # head
        add_box(-0.4, 0.5, 0, 0.15, 0.6, 0.25, "Material_Base")  # left arm
        add_box(0.4, 0.5, 0, 0.15, 0.6, 0.25, "Material_Base")   # right arm
        add_box(-0.15, -0.2, 0, 0.18, 0.6, 0.25, "Material_Base") # left leg
        add_box(0.15, -0.2, 0, 0.18, 0.6, 0.25, "Material_Base")  # right leg

        lines = ["# Sprite! OBJ Export", f"# {self.info['prompt']}", "mtllib asset.mtl", ""]
        for v in verts:
            lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
        lines.append("")
        for f in faces:
            lines.append(f.strip())
        return "\n".join(lines)

    def _vehicle_obj(self) -> str:
        verts = []
        faces = []

        def add_box(cx, cy, cz, w, h, d, mat="Material_Base"):
            base = len(verts) + 1
            hw, hh, hd = w/2, h/2, d/2
            for v in [(cx-hw,cy-hh,cz-hd),(cx+hw,cy-hh,cz-hd),(cx+hw,cy+hh,cz-hd),(cx-hw,cy+hh,cz-hd),
                      (cx-hw,cy-hh,cz+hd),(cx+hw,cy-hh,cz+hd),(cx+hw,cy+hh,cz+hd),(cx-hw,cy+hh,cz+hd)]:
                verts.append(v)
            faces.append(f"usemtl {mat}\nf {base} {base+1} {base+2} {base+3}\nf {base+7} {base+6} {base+5} {base+4}\nf {base} {base+4} {base+5} {base+1}\nf {base+2} {base+6} {base+7} {base+3}\nf {base+1} {base+5} {base+6} {base+2}\nf {base+3} {base+7} {base+4} {base}")

        # Car body
        add_box(0, 0.2, 0, 1.8, 0.4, 0.9, "Material_Base")
        add_box(0, 0.6, 0.05, 1.0, 0.4, 0.75, "Material_Accent")
        # Wheels
        for wx, wz in [(-0.7,-0.5),( 0.7,-0.5),(-0.7, 0.5),(0.7, 0.5)]:
            add_box(wx, -0.05, wz, 0.15, 0.3, 0.3, "Material_Base")

        lines = ["# Sprite! OBJ - Vehicle", f"# {self.info['prompt']}", "mtllib asset.mtl", ""]
        for v in verts: lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
        lines.append("")
        for f in faces: lines.append(f.strip())
        return "\n".join(lines)

    def _env_obj(self) -> str:
        """Tree-like environment object."""
        verts, faces = [], []

        def add_box(cx,cy,cz,w,h,d,mat="Material_Base"):
            base=len(verts)+1
            hw,hh,hd=w/2,h/2,d/2
            for v in [(cx-hw,cy-hh,cz-hd),(cx+hw,cy-hh,cz-hd),(cx+hw,cy+hh,cz-hd),(cx-hw,cy+hh,cz-hd),
                      (cx-hw,cy-hh,cz+hd),(cx+hw,cy-hh,cz+hd),(cx+hw,cy+hh,cz+hd),(cx-hw,cy+hh,cz+hd)]:
                verts.append(v)
            faces.append(f"usemtl {mat}\nf {base} {base+1} {base+2} {base+3}\nf {base+7} {base+6} {base+5} {base+4}\nf {base} {base+4} {base+5} {base+1}\nf {base+2} {base+6} {base+7} {base+3}\nf {base+1} {base+5} {base+6} {base+2}\nf {base+3} {base+7} {base+4} {base}")

        add_box(0, 0.5, 0, 0.2, 1.0, 0.2, "Material_Base")  # trunk
        add_box(0, 1.4, 0, 0.9, 0.5, 0.9, "Material_Accent")  # canopy low
        add_box(0, 1.9, 0, 0.65, 0.4, 0.65, "Material_Accent") # canopy mid
        add_box(0, 2.3, 0, 0.4, 0.35, 0.4, "Material_Accent")  # canopy top

        lines = ["# Sprite! OBJ - Environment", f"# {self.info['prompt']}", "mtllib asset.mtl", ""]
        for v in verts: lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
        lines.append("")
        for f in faces: lines.append(f.strip())
        return "\n".join(lines)

    def _generic_obj(self) -> str:
        """Cube with chamfered-look layering."""
        verts, faces = [], []

        def add_box(cx,cy,cz,w,h,d,mat="Material_Base"):
            base=len(verts)+1
            hw,hh,hd=w/2,h/2,d/2
            for v in [(cx-hw,cy-hh,cz-hd),(cx+hw,cy-hh,cz-hd),(cx+hw,cy+hh,cz-hd),(cx-hw,cy+hh,cz-hd),
                      (cx-hw,cy-hh,cz+hd),(cx+hw,cy-hh,cz+hd),(cx+hw,cy+hh,cz+hd),(cx-hw,cy+hh,cz+hd)]:
                verts.append(v)
            faces.append(f"usemtl {mat}\nf {base} {base+1} {base+2} {base+3}\nf {base+7} {base+6} {base+5} {base+4}\nf {base} {base+4} {base+5} {base+1}\nf {base+2} {base+6} {base+7} {base+3}\nf {base+1} {base+5} {base+6} {base+2}\nf {base+3} {base+7} {base+4} {base}")

        add_box(0,0,0,1,1,1,"Material_Base")
        add_box(0,0,0,0.8,0.8,0.8,"Material_Accent")

        lines = ["# Sprite! OBJ - Generic", f"# {self.info['prompt']}", "mtllib asset.mtl", ""]
        for v in verts: lines.append(f"v {v[0]:.4f} {v[1]:.4f} {v[2]:.4f}")
        lines.append("")
        for f in faces: lines.append(f.strip())
        return "\n".join(lines)

    def render_views(self) -> dict:
        """
        Render front, rear, side (left), top views using matplotlib 3D.
        Returns dict of view_name -> PNG bytes (base64).
        """
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection

        obj_str = self.generate_obj()
        verts_list = []
        faces_data = []
        current_mat = "Material_Base"

        for line in obj_str.split('\n'):
            line = line.strip()
            if line.startswith('v '):
                parts = line.split()
                verts_list.append([float(parts[1]), float(parts[2]), float(parts[3])])
            elif line.startswith('usemtl'):
                current_mat = line.split()[-1]
            elif line.startswith('f '):
                indices = [int(x)-1 for x in line.split()[1:]]
                faces_data.append((indices, current_mat))

        V = np.array(verts_list) if verts_list else np.zeros((8,3))
        col_base = [c/255 for c in self.palette[0][:3]] + [0.85]
        col_accent = [c/255 for c in self.palette[1][:3]] + [0.85]

        def render(elev, azim, title):
            fig = plt.figure(figsize=(3,3), facecolor='#0a0a0f')
            ax = fig.add_subplot(111, projection='3d', facecolor='#111118')
            ax.set_facecolor('#111118')

            polys_base, polys_accent = [], []
            for indices, mat in faces_data:
                if len(indices) >= 3:
                    poly = [V[i].tolist() for i in indices]
                    if mat == "Material_Accent":
                        polys_accent.append(poly)
                    else:
                        polys_base.append(poly)

            ec1 = [c/255 for c in self.palette[0][:3]] + [0.3]
            ec2 = [c/255 for c in self.palette[1][:3]] + [0.3]
            if polys_base:
                coll = Poly3DCollection(polys_base, alpha=0.85, linewidths=0.3,
                                        edgecolors=[ec1],
                                        facecolors=[col_base])
                ax.add_collection3d(coll)
            if polys_accent:
                coll2 = Poly3DCollection(polys_accent, alpha=0.85, linewidths=0.3,
                                         edgecolors=[ec2],
                                         facecolors=[col_accent])
                ax.add_collection3d(coll2)

            if len(V) > 0:
                mn, mx = V.min(axis=0), V.max(axis=0)
                pad = 0.3
                ax.set_xlim(mn[0]-pad, mx[0]+pad)
                ax.set_ylim(mn[1]-pad, mx[1]+pad)
                ax.set_zlim(mn[2]-pad, mx[2]+pad)

            ax.view_init(elev=elev, azim=azim)
            ax.set_axis_off()
            ax.grid(False)

            # Title
            ax.text2D(0.5, 0.02, title, transform=ax.transAxes,
                      ha='center', fontsize=8, color='#a0a0b0',
                      fontfamily='monospace')

            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=80, bbox_inches='tight',
                       facecolor='#0a0a0f', edgecolor='none')
            plt.close()
            buf.seek(0)
            return base64.b64encode(buf.read()).decode()

        return {
            "front": render(10, -90, "FRONT"),
            "rear":  render(10, 90, "REAR"),
            "left":  render(10, 0, "LEFT SIDE"),
            "top":   render(90, -90, "TOP"),
        }


# ─────────────────────────────────────────────
#  TILEMAP GENERATOR
# ─────────────────────────────────────────────

class TilemapGenerator:
    """Generates a full tilemap sheet from a prompt."""

    def __init__(self, info: dict, cols=4, rows=4):
        self.info = info
        self.cols = cols
        self.rows = rows
        self.tile_size = info.get("tile_size", 32)

    def generate(self) -> Image.Image:
        total_w = self.cols * self.tile_size
        total_h = self.rows * self.tile_size
        sheet = Image.new("RGBA", (total_w, total_h), (0,0,0,0))

        for row in range(self.rows):
            for col in range(self.cols):
                varied_info = dict(self.info)
                varied_info["seed"] = self.info["seed"] + row*100 + col
                gen = SpriteGenerator(varied_info)
                tile = gen._gen_tile().resize((self.tile_size, self.tile_size), Image.LANCZOS)
                sheet.paste(tile, (col*self.tile_size, row*self.tile_size))

        # Grid overlay
        draw = ImageDraw.Draw(sheet)
        for r in range(self.rows+1):
            draw.line([(0, r*self.tile_size), (total_w, r*self.tile_size)], fill=(255,255,255,40), width=1)
        for c in range(self.cols+1):
            draw.line([(c*self.tile_size, 0), (c*self.tile_size, total_h)], fill=(255,255,255,40), width=1)

        return sheet


# ─────────────────────────────────────────────
#  ANIMATION SPRITE SHEET GENERATOR
# ─────────────────────────────────────────────

class AnimationGenerator:
    """Generates a horizontal sprite animation sheet (walk cycle etc.)."""

    def __init__(self, info: dict, frames=8):
        self.info = info
        self.frames = frames
        self.frame_size = min(info["size"], 64)

    def generate(self) -> Image.Image:
        sheet = Image.new("RGBA", (self.frame_size * self.frames, self.frame_size), (0,0,0,0))
        for i in range(self.frames):
            frame_info = dict(self.info)
            frame_info["seed"] = self.info["seed"] + i
            frame_info["size"] = self.frame_size
            # Slight variation per frame for animation feel
            frame_info["_frame"] = i
            gen = SpriteGenerator(frame_info)
            frame = gen.generate()
            # Slight vertical bob
            bob = int(math.sin(i * math.pi / (self.frames/2)) * 3)
            sheet.paste(frame, (i * self.frame_size, bob))
        return sheet


# ─────────────────────────────────────────────
#  SPRITE ATLAS GENERATOR
# ─────────────────────────────────────────────

class AtlasGenerator:
    """Packs multiple generated sprites into a texture atlas with JSON metadata."""

    def __init__(self, items: list):
        """items: list of (name, PIL.Image)"""
        self.items = items

    def pack(self) -> tuple:
        """Returns (atlas_image, json_metadata_str)."""
        if not self.items:
            return Image.new("RGBA", (64,64)), "{}"
        max_dim = max(max(img.width, img.height) for _,img in self.items)
        cols = math.ceil(math.sqrt(len(self.items)))
        rows = math.ceil(len(self.items)/cols)
        pad = 2
        cell = max_dim + pad*2
        atlas = Image.new("RGBA", (cols*cell, rows*cell), (0,0,0,0))
        meta = {"frames": {}}
        for idx, (name, img) in enumerate(self.items):
            r, c = divmod(idx, cols)
            x, y = c*cell + pad, r*cell + pad
            atlas.paste(img.resize((max_dim,max_dim), Image.NEAREST), (x,y))
            meta["frames"][name] = {"x": x, "y": y, "w": max_dim, "h": max_dim}
        meta["meta"] = {"size": {"w": atlas.width, "h": atlas.height}, "format": "RGBA8"}
        return atlas, json.dumps(meta, indent=2)


# ─────────────────────────────────────────────
#  ICON SET GENERATOR
# ─────────────────────────────────────────────

def generate_icon_set(base_info: dict, sizes=(16,32,64,128)):
    """Generate a single icon in multiple sizes."""
    results = {}
    for sz in sizes:
        info = dict(base_info)
        info["size"] = sz
        info["category"] = "icon"
        gen = SpriteGenerator(info)
        results[sz] = gen.generate()
    return results


# ─────────────────────────────────────────────
#  PALETTE EXTRACTOR / SWAPPER
# ─────────────────────────────────────────────

def extract_dominant_colors(img: Image.Image, n=6) -> list:
    """Quantize to n colors and return palette."""
    small = img.resize((64,64)).convert("RGB")
    quantized = small.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    raw_pal = quantized.getpalette()[:n*3]
    return [(raw_pal[i*3], raw_pal[i*3+1], raw_pal[i*3+2]) for i in range(n)]


def swap_palette(img: Image.Image, old_colors: list, new_colors: list, threshold=40) -> Image.Image:
    """Swap approximate colors in an image."""
    result = img.copy().convert("RGBA")
    arr = np.array(result, dtype=np.int32)
    for old, new in zip(old_colors, new_colors):
        old = np.array(old[:3], dtype=np.int32)
        new_c = np.array(new[:3], dtype=np.int32)
        diff = np.abs(arr[:,:,:3] - old).sum(axis=2)
        mask = diff < threshold
        arr[mask, 0] = new_c[0]
        arr[mask, 1] = new_c[1]
        arr[mask, 2] = new_c[2]
    return Image.fromarray(arr.astype(np.uint8), "RGBA")


# ─────────────────────────────────────────────
#  NORMAL MAP GENERATOR
# ─────────────────────────────────────────────

def generate_normal_map(img: Image.Image) -> Image.Image:
    """Generate a normal map from a grayscale heightmap or sprite."""
    gray = np.array(img.convert("L"), dtype=float) / 255.0
    smoothed = gaussian_filter(gray, sigma=1.5)
    # Compute gradients
    dx = np.gradient(smoothed, axis=1)
    dy = np.gradient(smoothed, axis=0)
    # Build normal (R=x, G=y, B=z)
    strength = 4.0
    nx = -dx * strength
    ny = dy * strength
    nz = np.ones_like(nx)
    length = np.sqrt(nx**2 + ny**2 + nz**2) + 1e-8
    nx, ny, nz = nx/length, ny/length, nz/length
    r = ((nx + 1) / 2 * 255).astype(np.uint8)
    g = ((ny + 1) / 2 * 255).astype(np.uint8)
    b = (nz * 255).astype(np.uint8)
    return Image.fromarray(np.stack([r,g,b], axis=2), "RGB")


# ─────────────────────────────────────────────
#  EMISSIVE / ROUGHNESS MAP GENERATORS
# ─────────────────────────────────────────────

def generate_emissive_map(img: Image.Image, palette: list) -> Image.Image:
    """Highlight bright/accent areas as emissive (glowing) regions."""
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    result = np.zeros((arr.shape[0], arr.shape[1], 3), dtype=np.uint8)
    for col in palette[:2]:
        c = np.array(col[:3], dtype=np.float32)
        diff = np.abs(arr[:,:,:3] - c).sum(axis=2)
        mask = diff < 80
        result[mask] = col[:3]
    # Blur for glow
    from PIL import ImageFilter
    out = Image.fromarray(result, "RGB")
    return out.filter(ImageFilter.GaussianBlur(radius=2))


def generate_roughness_map(img: Image.Image) -> Image.Image:
    """Roughness map: bright = rough, dark = smooth."""
    gray = img.convert("L")
    arr = np.array(gray, dtype=np.float32)
    arr = gaussian_filter(arr, sigma=2)
    arr = (arr - arr.min()) / (arr.max() - arr.min() + 1e-8) * 255
    return Image.fromarray(arr.astype(np.uint8), "L")


# ─────────────────────────────────────────────
#  UPSCALER (pixel-art aware)
# ─────────────────────────────────────────────

def upscale_sprite(img: Image.Image, factor=4) -> Image.Image:
    """Scale2x-like upscale preserving pixel art edges."""
    w, h = img.size
    return img.resize((w*factor, h*factor), Image.NEAREST)


# ─────────────────────────────────────────────
#  MAIN PUBLIC API
# ─────────────────────────────────────────────

def generate_sprite(prompt: str) -> dict:
    """Full pipeline: parse prompt → generate sprite → return result dict."""
    info = parse_prompt(prompt)
    gen = SpriteGenerator(info)
    img = gen.generate()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return {
        "image_b64": base64.b64encode(buf.read()).decode(),
        "info": info,
        "format": "PNG",
        "size": f"{img.width}x{img.height}",
    }


def generate_3d_asset(prompt: str) -> dict:
    """Full 3D pipeline: parse → OBJ + MTL + multi-view renders."""
    info = parse_prompt(prompt)
    gen3d = Asset3DGenerator(info)
    obj_str = gen3d.generate_obj()
    mtl_str = gen3d.generate_mtl()
    views = gen3d.render_views()
    return {
        "obj": obj_str,
        "mtl": mtl_str,
        "views": views,
        "info": info,
    }


def generate_tilemap(prompt: str, cols=4, rows=4) -> dict:
    """Generate a tilemap sheet."""
    info = parse_prompt(prompt)
    info["category"] = "tile"
    gen = TilemapGenerator(info, cols, rows)
    img = gen.generate()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return {
        "image_b64": base64.b64encode(buf.read()).decode(),
        "width": img.width,
        "height": img.height,
        "cols": cols,
        "rows": rows,
        "tile_size": gen.tile_size,
    }


def generate_animation(prompt: str, frames=8) -> dict:
    """Generate animation sprite sheet."""
    info = parse_prompt(prompt)
    gen = AnimationGenerator(info, frames)
    img = gen.generate()
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return {
        "image_b64": base64.b64encode(buf.read()).decode(),
        "frames": frames,
        "frame_width": gen.frame_size,
        "frame_height": gen.frame_size,
    }


def generate_full_pack(prompt: str) -> dict:
    """Generate a full asset pack: sprite, normal map, emissive, roughness, animation sheet."""
    info = parse_prompt(prompt)
    palette = get_palette(info["palette"])

    # Base sprite
    gen = SpriteGenerator(info)
    sprite = gen.generate()

    # Extra maps
    normal  = generate_normal_map(sprite)
    emissive = generate_emissive_map(sprite, palette)
    roughness = generate_roughness_map(sprite)
    upscaled = upscale_sprite(sprite, 4)

    def img_b64(img, mode="RGBA"):
        buf = io.BytesIO()
        img.convert(mode).save(buf, "PNG")
        buf.seek(0)
        return base64.b64encode(buf.read()).decode()

    return {
        "sprite":    img_b64(sprite),
        "normal":    img_b64(normal, "RGB"),
        "emissive":  img_b64(emissive, "RGB"),
        "roughness": img_b64(roughness, "L"),
        "upscaled":  img_b64(upscaled),
        "info": info,
    }


def build_download_zip(prompt: str, include_3d=True) -> bytes:
    """Build a complete downloadable ZIP with all assets."""
    info = parse_prompt(prompt)
    palette = get_palette(info["palette"])

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        # 2D Sprite
        gen = SpriteGenerator(info)
        sprite = gen.generate()
        sb = io.BytesIO(); sprite.save(sb, "PNG"); sb.seek(0)
        zf.writestr("sprite.png", sb.read())

        # Upscaled
        up = upscale_sprite(sprite, 4)
        ub = io.BytesIO(); up.save(ub, "PNG"); ub.seek(0)
        zf.writestr("sprite_4x.png", ub.read())

        # Normal map
        nm = generate_normal_map(sprite)
        nb = io.BytesIO(); nm.save(nb, "PNG"); nb.seek(0)
        zf.writestr("normal_map.png", nb.read())

        # Emissive
        em = generate_emissive_map(sprite, palette)
        eb = io.BytesIO(); em.save(eb, "PNG"); eb.seek(0)
        zf.writestr("emissive_map.png", eb.read())

        # Roughness
        rm = generate_roughness_map(sprite)
        rb = io.BytesIO(); rm.save(rb, "PNG"); rb.seek(0)
        zf.writestr("roughness_map.png", rb.read())

        # Tilemap
        ti = dict(info); ti["category"] = "tile"
        tgen = TilemapGenerator(ti, 4, 4)
        tmap = tgen.generate()
        tb = io.BytesIO(); tmap.save(tb, "PNG"); tb.seek(0)
        zf.writestr("tilemap_sheet.png", tb.read())

        # Animation sheet
        agen = AnimationGenerator(info, 8)
        anim = agen.generate()
        ab = io.BytesIO(); anim.save(ab, "PNG"); ab.seek(0)
        zf.writestr("animation_sheet.png", ab.read())

        # 3D OBJ + MTL
        if include_3d:
            gen3d = Asset3DGenerator(info)
            zf.writestr("model.obj", gen3d.generate_obj())
            zf.writestr("model.mtl", gen3d.generate_mtl())

        # README
        readme = f"""# Sprite! Asset Pack
Prompt: "{prompt}"
Category: {info['category']}
Style: {info['style']}
Palette: {info['palette']}
Seed: {info['seed']}

## Files
- sprite.png          — Main 2D sprite ({info['size']}x{info['size']})
- sprite_4x.png       — 4x upscaled sprite
- normal_map.png      — Normal map (for lighting)
- emissive_map.png    — Emissive/glow map
- roughness_map.png   — PBR roughness map
- tilemap_sheet.png   — 4x4 tile sheet
- animation_sheet.png — 8-frame animation strip
- model.obj           — 3D mesh (Wavefront OBJ)
- model.mtl           — Material definitions

## Engine Import
- Unity: drag .png into Assets, .obj into scene
- Unreal: import via Content Browser
- Godot: drag into FileSystem dock
- GameMaker: Sprite → Import from file

Generated by Sprite! — Game Asset Generator by Shivani
"""
        zf.writestr("README.md", readme)

    buf.seek(0)
    return buf.read()


if __name__ == "__main__":
    # Quick test
    result = generate_sprite("pixel art warrior character fire palette 64px")
    print(f"Generated sprite: {result['info']['category']} / {result['info']['style']} / {result['size']}")
    res3d = generate_3d_asset("low poly spaceship sci-fi blue 64px")
    print(f"Generated 3D asset OBJ lines: {len(res3d['obj'].splitlines())}")
    print("Engine OK!")
