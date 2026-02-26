"""
Sprite! — Game Asset Generator
Web Server (Python built-in http.server — no external dependencies)
Run: python3 server.py
Then open: http://localhost:7777
"""

import os
import sys
import json
import base64
import io
import urllib.parse
import traceback
from http.server import HTTPServer, BaseHTTPRequestHandler

# Add project root to path
sys.path.insert(0, os.path.dirname(__file__))
import sprite_engine as eng


class SpriteHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[Sprite!] {self.address_string()} {fmt % args}")

    def _send(self, code, content_type, body):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, data, code=200):
        self._send(code, "application/json", json.dumps(data))

    def _read_body(self):
        length = int(self.headers.get("Content-Length", 0))
        return self.rfile.read(length).decode("utf-8") if length else ""

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        path = self.path.split("?")[0].rstrip("/")

        if path == "" or path == "/":
            self._serve_html()
        elif path == "/api/palettes":
            self._api_palettes()
        elif path == "/api/categories":
            self._api_categories()
        elif path == "/api/styles":
            self._api_styles()
        elif path == "/api/health":
            self._send_json({"status": "ok", "version": "1.0", "app": "Sprite!"})
        else:
            self._send(404, "text/plain", "Not Found")

    def do_POST(self):
        path = self.path.rstrip("/")
        body = self._read_body()

        try:
            data = json.loads(body) if body else {}
        except Exception:
            self._send_json({"error": "Invalid JSON"}, 400)
            return

        try:
            if path == "/api/generate/sprite":
                self._api_gen_sprite(data)
            elif path == "/api/generate/3d":
                self._api_gen_3d(data)
            elif path == "/api/generate/tilemap":
                self._api_gen_tilemap(data)
            elif path == "/api/generate/animation":
                self._api_gen_animation(data)
            elif path == "/api/generate/pack":
                self._api_gen_pack(data)
            elif path == "/api/generate/iconset":
                self._api_gen_iconset(data)
            elif path == "/api/generate/atlas":
                self._api_gen_atlas(data)
            elif path == "/api/addon/normalmap":
                self._api_normalmap(data)
            elif path == "/api/addon/upscale":
                self._api_upscale(data)
            elif path == "/api/addon/palette_swap":
                self._api_palette_swap(data)
            elif path == "/api/addon/batch":
                self._api_batch(data)
            elif path == "/api/download/zip":
                self._api_download_zip(data)
            else:
                self._send_json({"error": f"Unknown endpoint: {path}"}, 404)
        except Exception as e:
            tb = traceback.format_exc()
            print(f"[ERROR] {e}\n{tb}")
            self._send_json({"error": str(e)}, 500)

    # ── API HANDLERS ──────────────────────────────────────

    def _api_gen_sprite(self, data):
        prompt = data.get("prompt", "pixel character")
        result = eng.generate_sprite(prompt)
        self._send_json(result)

    def _api_gen_3d(self, data):
        prompt = data.get("prompt", "character")
        result = eng.generate_3d_asset(prompt)
        self._send_json(result)

    def _api_gen_tilemap(self, data):
        prompt = data.get("prompt", "stone floor tile")
        cols = int(data.get("cols", 4))
        rows = int(data.get("rows", 4))
        result = eng.generate_tilemap(prompt, cols, rows)
        self._send_json(result)

    def _api_gen_animation(self, data):
        prompt = data.get("prompt", "walk cycle character")
        frames = int(data.get("frames", 8))
        result = eng.generate_animation(prompt, frames)
        self._send_json(result)

    def _api_gen_pack(self, data):
        prompt = data.get("prompt", "character")
        result = eng.generate_full_pack(prompt)
        self._send_json(result)

    def _api_gen_iconset(self, data):
        prompt = data.get("prompt", "star icon")
        info = eng.parse_prompt(prompt)
        icons = eng.generate_icon_set(info)
        out = {}
        for sz, img in icons.items():
            buf = io.BytesIO(); img.save(buf, "PNG"); buf.seek(0)
            out[str(sz)] = base64.b64encode(buf.read()).decode()
        self._send_json({"icons": out, "info": info})

    def _api_gen_atlas(self, data):
        prompts = data.get("prompts", ["warrior", "wizard", "archer", "knight"])
        items = []
        for p in prompts[:16]:
            result = eng.generate_sprite(p)
            img_data = base64.b64decode(result["image_b64"])
            from PIL import Image
            img = Image.open(io.BytesIO(img_data))
            items.append((p, img))
        from sprite_engine import AtlasGenerator
        atlas_gen = AtlasGenerator(items)
        atlas_img, meta_json = atlas_gen.pack()
        buf = io.BytesIO(); atlas_img.save(buf, "PNG"); buf.seek(0)
        self._send_json({
            "atlas_b64": base64.b64encode(buf.read()).decode(),
            "metadata": json.loads(meta_json),
        })

    def _api_normalmap(self, data):
        img_b64 = data.get("image_b64")
        if not img_b64:
            self._send_json({"error": "No image_b64 provided"}, 400); return
        from PIL import Image
        img_data = base64.b64decode(img_b64)
        img = Image.open(io.BytesIO(img_data))
        nm = eng.generate_normal_map(img)
        buf = io.BytesIO(); nm.save(buf, "PNG"); buf.seek(0)
        self._send_json({"normal_b64": base64.b64encode(buf.read()).decode()})

    def _api_upscale(self, data):
        img_b64 = data.get("image_b64")
        factor = int(data.get("factor", 4))
        if not img_b64:
            self._send_json({"error": "No image_b64 provided"}, 400); return
        from PIL import Image
        img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
        up = eng.upscale_sprite(img, factor)
        buf = io.BytesIO(); up.save(buf, "PNG"); buf.seek(0)
        self._send_json({"upscaled_b64": base64.b64encode(buf.read()).decode(),
                         "size": f"{up.width}x{up.height}"})

    def _api_palette_swap(self, data):
        img_b64 = data.get("image_b64")
        new_palette_name = data.get("palette", "fire")
        if not img_b64:
            self._send_json({"error": "No image_b64 provided"}, 400); return
        from PIL import Image
        img = Image.open(io.BytesIO(base64.b64decode(img_b64)))
        old_colors = eng.extract_dominant_colors(img, 6)
        new_colors = eng.get_palette(new_palette_name)
        swapped = eng.swap_palette(img, old_colors, new_colors)
        buf = io.BytesIO(); swapped.save(buf, "PNG"); buf.seek(0)
        self._send_json({"swapped_b64": base64.b64encode(buf.read()).decode()})

    def _api_batch(self, data):
        prompts = data.get("prompts", [])
        results = []
        for p in prompts[:20]:
            try:
                r = eng.generate_sprite(p)
                results.append({"prompt": p, "image_b64": r["image_b64"], "info": r["info"]})
            except Exception as e:
                results.append({"prompt": p, "error": str(e)})
        self._send_json({"results": results})

    def _api_download_zip(self, data):
        prompt = data.get("prompt", "game asset")
        include_3d = data.get("include_3d", True)
        zip_bytes = eng.build_download_zip(prompt, include_3d)
        safe_name = prompt[:30].replace(" ", "_").replace("/","")
        self.send_response(200)
        self.send_header("Content-Type", "application/zip")
        self.send_header("Content-Disposition", f'attachment; filename="sprite_{safe_name}.zip"')
        self.send_header("Content-Length", len(zip_bytes))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(zip_bytes)

    def _api_palettes(self):
        palettes = ["fire","ice","nature","dark","gold","poison","ocean","stone","magic","neon","earth","blood"]
        self._send_json({"palettes": palettes})

    def _api_categories(self):
        cats = ["character","tile","item","ui","environment","vehicle","prop","particle","icon"]
        self._send_json({"categories": cats})

    def _api_styles(self):
        styles = ["pixel","cartoon","realistic","neon","minimalist","fantasy","sci-fi"]
        self._send_json({"styles": styles})

    # ── HTML SERVE ────────────────────────────────────────

    def _serve_html(self):
        html_path = os.path.join(os.path.dirname(__file__), "index.html")
        with open(html_path, "rb") as f:
            content = f.read()
        self._send(200, "text/html; charset=utf-8", content)


def main():
    port = int(os.environ.get("SPRITE_PORT", 7777))
    host = os.environ.get("SPRITE_HOST", "0.0.0.0")

    print("""
╔══════════════════════════════════════════════════╗
║         Sprite! — Game Asset Generator           ║
║         Created by Shivani  ✦                   ║
╠══════════════════════════════════════════════════╣
║  No external APIs. No limits. Pure Python.       ║
╚══════════════════════════════════════════════════╝
""")
    print(f"  🎮  Server starting on http://{host}:{port}")
    print(f"  🎨  Supports: 2D Sprites, 3D Assets, Tilemaps, Animations")
    print(f"  🔌  Engine extensions: Unity, Unreal, Godot, GameMaker")
    print(f"  📦  15 addons included\n")

    server = HTTPServer((host, port), SpriteHandler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Sprite! server stopped.")


if __name__ == "__main__":
    main()
