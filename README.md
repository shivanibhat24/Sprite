# Sprite! — Game Asset Generator
### Created for Shivani ✦

A comprehensive, fully offline Python-based game asset generation suite. Generate 2D sprites, 3D meshes, tilemaps, animation sheets, and complete PBR asset packs — all from natural language text prompts. **No external APIs. No internet required.**

---

## 🚀 Quick Start

```bash
# 1. Install Python dependencies (one-time)
pip install Pillow numpy scipy matplotlib

# 2. Launch Sprite!
python3 run.py

# 3. Open your browser to http://localhost:7777
```

That's it! The full UI opens in your browser.

---

## 📦 What's Included

```
sprite_project/
├── run.py                          ← Main launcher
├── server.py                       ← Web server (Python built-in, no Flask needed)
├── sprite_engine.py                ← Core generation engine
├── index.html                      ← Full web UI
├── engine_extensions/
│   ├── SpriteGeneratorBridge.cs    ← Unity C# Editor extension
│   ├── sprite_generator_unreal.py  ← Unreal Engine Python plugin
│   ├── sprite_generator_godot/
│   │   └── plugin.gd               ← Godot EditorPlugin
│   └── SpriteGenerator_GameMaker.gml  ← GameMaker GML extension
└── README.md                       ← This file
```

---

## 🎮 Asset Types

| Type | Description |
|------|-------------|
| **Sprite** | Single 2D sprite (16–512px), pixel art / cartoon / neon / fantasy styles |
| **3D Asset** | Wavefront OBJ mesh + MTL materials with 4-angle view renders |
| **Tilemap** | N×M tileset sheet for ground, walls, platforms |
| **Animation** | Horizontal 2–24 frame sprite sheet for walk cycles, attacks, etc. |
| **Full Pack** | Sprite + Normal Map + Emissive + Roughness + 4× upscale + Tilemap |
| **Icon Set** | Same icon at 16, 32, 64, 128px |
| **Atlas** | Multiple sprites auto-packed into a single texture atlas + JSON metadata |

---

## ✨ 15 Addons

| # | Addon | What It Does |
|---|-------|-------------|
| 1 | **Normal Map** | Generates PBR normal map from sprite |
| 2 | **Emissive Map** | Highlights glowing/bright areas |
| 3 | **Roughness Map** | PBR roughness (bright=rough, dark=smooth) |
| 4 | **4× Upscaler** | Nearest-neighbor pixel-art upscale |
| 5 | **Palette Swap** | Recolor sprite with any palette |
| 6 | **Batch Generator** | Generate up to 20 sprites from a list of prompts |
| 7 | **Texture Atlas** | Pack multiple sprites + JSON metadata |
| 8 | **Icon Set** | Export one icon in 4 sizes |
| 9 | **Drop Shadow** | Add drop shadow effect |
| 10 | **Outline/Stroke** | Add pixel-perfect outline |
| 11 | **Animation Preview** | Play the sprite sheet as animation in-browser |
| 12 | **Unity Export** | C# import helper script |
| 13 | **Godot Import** | GDScript EditorPlugin |
| 14 | **Unreal Import** | Python plugin for Content Browser |
| 15 | **GameMaker Script** | Async HTTP + sprite_add GML script |

---

## 🎨 Supported Palettes

`fire` · `ice` · `nature` · `dark` · `gold` · `poison` · `ocean` · `stone` · `magic` · `neon` · `earth` · `blood`

---

## 🔤 Prompt Guide

Be descriptive! Mix category + style + palette + size:

```
pixel art warrior character fire palette 64px
sci-fi spaceship neon blue 128px
dungeon stone floor tile 32px
cartoon wizard ice magic 64px
health potion ui icon red 32px
zombie enemy dark pixel art 64px
wooden chest prop fantasy 64px
```

**Category keywords**: `character, tile, item, weapon, ui, environment, tree, vehicle, prop, particle, icon`  
**Style keywords**: `pixel, 8-bit, cartoon, neon, glow, cyberpunk, fantasy, sci-fi, minimalist`  
**Palette keywords**: `fire, ice, nature, dark, gold, poison, ocean, stone, magic, neon`

---

## 🔌 Engine Integration

### Unity
1. Copy `SpriteGeneratorBridge.cs` to `Assets/Editor/`
2. Open Unity → `Tools > Sprite! Generator`
3. Make sure `server.py` is running

### Godot 4
1. Copy `sprite_generator_godot/` to `addons/`
2. Enable in `Project > Project Settings > Plugins`
3. Use the Sprite! panel in the bottom dock

### Unreal Engine
1. Open `Tools > Python Script Editor`
2. Run `import Content.Python.sprite_generator as sg`
3. Call `sg.import_sprite("pixel warrior fire 64px")`

### GameMaker Studio 2
1. Create extension, add `SpriteGenerator_GameMaker.gml`
2. Call `sprite_gen_init()` in Create event
3. Call `sprite_gen_create("prompt")` to generate
4. Handle in Async - HTTP event

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+Enter` | Generate |
| `Ctrl+S` | Download PNG |
| `Ctrl+Shift+S` | Download full ZIP |
| `Alt+3` | Switch to 3D view |
| `Escape` | Clear prompt / close modal |

---

## 🛠 Configuration

```bash
# Custom port
python3 run.py --port 8080

# No auto-browser
python3 run.py --no-browser

# Environment variables
SPRITE_PORT=8080 python3 server.py
SPRITE_HOST=127.0.0.1 python3 server.py
```

---

## 📡 API Reference

The server exposes a REST API at `http://localhost:7777`:

| Endpoint | Method | Body | Returns |
|----------|--------|------|---------|
| `/api/generate/sprite` | POST | `{"prompt":"..."}` | `{image_b64, info}` |
| `/api/generate/3d` | POST | `{"prompt":"..."}` | `{obj, mtl, views{front,rear,left,top}}` |
| `/api/generate/tilemap` | POST | `{"prompt":"...","cols":4,"rows":4}` | `{image_b64}` |
| `/api/generate/animation` | POST | `{"prompt":"...","frames":8}` | `{image_b64, frames}` |
| `/api/generate/pack` | POST | `{"prompt":"..."}` | `{sprite,normal,emissive,roughness,upscaled}` |
| `/api/generate/iconset` | POST | `{"prompt":"..."}` | `{icons:{16,32,64,128}}` |
| `/api/generate/atlas` | POST | `{"prompts":["...","..."]}` | `{atlas_b64, metadata}` |
| `/api/addon/normalmap` | POST | `{"image_b64":"..."}` | `{normal_b64}` |
| `/api/addon/upscale` | POST | `{"image_b64":"...","factor":4}` | `{upscaled_b64}` |
| `/api/addon/palette_swap` | POST | `{"image_b64":"...","palette":"fire"}` | `{swapped_b64}` |
| `/api/addon/batch` | POST | `{"prompts":["..."]}` | `{results:[...]}` |
| `/api/download/zip` | POST | `{"prompt":"..."}` | `binary/zip` |
| `/api/palettes` | GET | — | `{palettes:[...]}` |
| `/api/health` | GET | — | `{status:"ok"}` |

---

## 📋 Requirements

- Python 3.8+
- `Pillow` (PIL)
- `numpy`
- `scipy`
- `matplotlib`
- No GUI framework needed (browser-based UI)
- No internet connection required

---

*Sprite! — Made with ♥ for Shivani*
