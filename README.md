<div align="center">

```
 ███████╗██████╗ ██████╗ ██╗████████╗███████╗██╗
 ██╔════╝██╔══██╗██╔══██╗██║╚══██╔══╝██╔════╝██║
 ███████╗██████╔╝██████╔╝██║   ██║   █████╗  ██║
 ╚════██║██╔═══╝ ██╔══██╗██║   ██║   ██╔══╝  ╚═╝
 ███████║██║     ██║  ██║██║   ██║   ███████╗██╗
 ╚══════╝╚═╝     ╚═╝  ╚═╝╚═╝   ╚═╝   ╚══════╝╚═╝
```

### Game Asset Generator

**Created by Shivani ✦**

Generate 2D sprites, 3D meshes, tilemaps, animation sheets, and complete PBR asset packs — all from natural language prompts. Fully offline. No APIs. No internet. Pure Python.

<br/>

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-FF5F1F?style=for-the-badge)](LICENSE)
[![No APIs](https://img.shields.io/badge/External%20APIs-None-22C55E?style=for-the-badge)](.)
[![No Internet](https://img.shields.io/badge/Internet-Not%20Required-A855F7?style=for-the-badge)](.)

<br/>

![Dark Theme](https://img.shields.io/badge/Theme-Dark%20%2F%20Light-22D3EE?style=flat-square)
![Asset Types](https://img.shields.io/badge/Asset%20Types-7-FF5F1F?style=flat-square)
![Addons](https://img.shields.io/badge/Addons-15-A855F7?style=flat-square)
![Engines](https://img.shields.io/badge/Engine%20Integrations-4-22C55E?style=flat-square)

</div>

---

## Table of Contents

- [Quick Start](#-quick-start)
- [What Is Sprite!](#-what-is-sprite)
- [Project Structure](#-project-structure)
- [Asset Types](#-asset-types)
- [Pixel Editor](#-pixel-editor)
- [15 Addons](#-15-addons)
- [Color Palettes](#-color-palettes)
- [Prompt Guide](#-prompt-guide)
- [Engine Integration](#-engine-integration)
  - [Unity](#unity)
  - [Godot 4](#godot-4)
  - [Unreal Engine](#unreal-engine)
  - [GameMaker Studio 2](#gamemaker-studio-2)
- [REST API Reference](#-rest-api-reference)
- [Keyboard Shortcuts](#-keyboard-shortcuts)
- [Configuration](#-configuration)
- [Requirements](#-requirements)

---

## 🚀 Quick Start

```bash
# 1. Install dependencies (one-time)
pip install Pillow numpy scipy matplotlib

# 2. Launch Sprite!
python3 run.py

# 3. Open in browser
# http://localhost:7777
```

> **That's it.** The browser opens automatically. Type a prompt, hit Generate.

---

## 🎮 What Is Sprite!

**Sprite!** is a fully offline game asset generation suite written in pure Python. Describe what you want in plain English and it generates production-ready assets instantly — no cloud services, no sign-ups, no rate limits.

The app runs a lightweight HTTP server using Python's built-in `http.server` and serves a dark-themed (or light-themed) browser UI at `localhost:7777`. All assets are downloadable as PNG, OBJ, MTL, or a complete ZIP pack.

**What makes it different:**

| Feature | Sprite! | Other tools |
|---|---|---|
| Internet required | ❌ Never | ✅ Always |
| External API | ❌ None | ✅ Required |
| Cost per generation | ❌ Free forever | 💰 Pay per use |
| Engine extensions | ✅ Unity, Unreal, Godot, GameMaker | ❌ Manual import |
| Pixel editor built-in | ✅ Yes | ❌ Separate app |
| PBR maps included | ✅ Normal, Emissive, Roughness | ❌ Extra cost |

---

## 📁 Project Structure

```
sprite_project/
│
├── run.py                              ← One-click launcher
├── server.py                           ← Built-in HTTP server (no Flask needed)
├── sprite_engine.py                    ← Core generation engine (54 functions)
├── index.html                          ← Full browser UI (single file, ~2600 lines)
│
└── engine_extensions/
    ├── SpriteGeneratorBridge.cs        ← Unity C# EditorWindow plugin
    ├── sprite_generator_unreal.py      ← Unreal Engine Python plugin
    ├── sprite_generator_godot/
    │   └── plugin.gd                   ← Godot 4 @tool EditorPlugin
    └── SpriteGenerator_GameMaker.gml   ← GameMaker async HTTP + sprite_add
```

---

## 🎨 Asset Types

Sprite! generates **7 distinct asset types**, each available from a dedicated tab or via direct API call.

### 1. 🖼 Sprite
Single 2D sprite from **16×16 to 512×512px**.

Supported styles: `pixel art` · `cartoon` · `neon/glow` · `fantasy` · `sci-fi` · `minimalist`

Supported categories: `character` · `tile` · `item` · `weapon` · `ui` · `environment` · `vehicle` · `prop` · `particle` · `icon`

---

### 2. 📦 3D Asset
Generates a **Wavefront OBJ mesh** with MTL material definitions and renders all **four orthographic views** automatically:

```
┌─────────────┬─────────────┐
│    FRONT    │    REAR     │
├─────────────┼─────────────┤
│  LEFT SIDE  │     TOP     │
└─────────────┴─────────────┘
```

Download: `model.obj` + `model.mtl` (compatible with Blender, Unity, Unreal, Godot)

---

### 3. 🧩 Tilemap
Generates an **N×M tile sheet** for floors, walls, platforms, and terrain. Each tile in the grid gets a unique procedural variation so maps feel hand-crafted.

- Configurable columns and rows (up to 8×8)
- Consistent colour palette across all tiles
- Pixel-perfect grid overlay

---

### 4. 🎬 Animation
Horizontal **sprite sheet** with 2–24 frames for walk cycles, attacks, idle animations, and more.

- In-browser **live preview player** at configurable FPS
- Frames are sized to match your chosen canvas size
- Download as a single strip ready for any engine

---

### 5. 📦 Full Pack
One click generates a complete **PBR-ready asset bundle**:

| File | Description |
|---|---|
| `sprite.png` | Base 2D sprite |
| `sprite_4x.png` | 4× nearest-neighbour upscale |
| `normal_map.png` | Blue-channel encoded normal map |
| `emissive_map.png` | Self-illumination / glow mask |
| `roughness_map.png` | PBR roughness (bright = rough, dark = smooth) |
| `tilemap_sheet.png` | 4×4 tile sheet |
| `animation_sheet.png` | 8-frame animation strip |
| `model.obj` | 3D mesh |
| `model.mtl` | Material definitions |
| `README.md` | Generation metadata |

---

### 6. 🏷 Icon Set
Exports one icon at **four sizes simultaneously**: 16 · 32 · 64 · 128px — ready for UI systems, app icons, and game HUDs.

---

### 7. 🗂 Atlas
Auto-packs **multiple sprites into a single texture sheet** and outputs JSON frame metadata for UV mapping and sprite animation systems.

```json
{
  "frames": {
    "warrior": { "x": 2, "y": 2, "w": 64, "h": 64 },
    "wizard":  { "x": 70, "y": 2, "w": 64, "h": 64 }
  },
  "meta": { "size": { "w": 272, "h": 272 }, "format": "RGBA8" }
}
```

---

## ✏ Pixel Editor

The built-in **Pixel Editor** tab is a full browser-based pixel art studio. Load any generated sprite and tweak it — or paint from scratch.

### Tools

| Tool | Shortcut | Description |
|---|---|---|
| ✏ Pencil | `P` | Single-pixel precision drawing |
| 🖌 Brush | `B` | Round soft brush with size control |
| ◻ Eraser | `E` | Erase to full transparency |
| 🪣 Fill | `F` | Flood fill with Bresenham boundary detection |
| 💧 Eyedropper | `I` | Pick any pixel colour as FG or BG |
| ╱ Line | `L` | Click-drag straight lines with live preview |
| ▭ Rectangle | `R` | Outlined rectangles with live preview |
| ○ Circle | `C` | Circles and ellipses with live preview |
| ⬚ Select | `S` | Marquee selection box |

### Brush Sizes

`1px` · `2px` · `4px` · `8px` — also adjustable with `[` and `]`

### Colour System

- **Dual colours** — Foreground (left-click) and Background (right-click) with one-click swap
- **Hex input** — Type any valid hex colour directly
- **Opacity slider** — Full alpha control from 1 to 255
- **Quick Palette** — 10 preset colours, add any current colour with one click
- **Theme Palettes** — 8 curated palettes (see below)

### Options

| Option | Effect |
|---|---|
| **Mirror X** | Symmetry painting across vertical axis — perfect for characters |
| **Mirror Y** | Symmetry painting across horizontal axis |
| **Grid Overlay** | Toggle pixel grid, hides automatically at small zoom levels |
| **Anti-alias** | Smooth brush edges |

### Canvas Controls

| Control | Detail |
|---|---|
| **Zoom** | 1× to 32× with fit-to-view button |
| **Undo / Redo** | 40-step history stack |
| **Canvas Resize** | 8–512px, preserves existing content |
| **Load Generated** | One click loads the last generated sprite into the editor |
| **Export PNG** | Download as a transparent PNG |

### Pixel Editor Shortcuts

| Key | Action | Key | Action |
|---|---|---|---|
| `P` | Pencil | `F` | Fill |
| `B` | Brush | `L` | Line |
| `E` | Eraser | `R` | Rectangle |
| `I` | Eyedropper | `C` | Circle |
| `X` | Swap colours | `G` | Toggle grid |
| `[` / `]` | Brush size | `+` / `-` | Zoom |
| `Ctrl+Z` | Undo | `Ctrl+Y` | Redo |

---

## ✨ 15 Addons

Every addon is accessible from the sidebar and works directly on generated or edited sprites.

| # | Addon | Badge | What It Does |
|---|---|---|---|
| 1 | **Normal Map** | `PBR` | Blue-channel encoded normal map for lighting in Unity, Unreal, and Godot |
| 2 | **Emissive Map** | `Glow` | Isolates bright accent areas as self-illuminating emissive regions |
| 3 | **Roughness Map** | `PBR` | Greyscale PBR roughness map — bright = rough, dark = smooth |
| 4 | **4× Upscaler** | `HQ` | Nearest-neighbour pixel-art upscale — crisp edges, zero blurring |
| 5 | **Palette Swap** | `Recolor` | Recolours the entire sprite by replacing dominant colour clusters |
| 6 | **Batch Generator** | `Bulk` | Generate up to 20 sprites simultaneously from a list of prompts |
| 7 | **Texture Atlas** | `Pack` | Auto-packs multiple sprites into one sheet with JSON metadata |
| 8 | **Icon Set** | `UI` | Exports one icon at 16, 32, 64, and 128px simultaneously |
| 9 | **Drop Shadow** | `FX` | Soft Gaussian drop shadow for elevated UI art |
| 10 | **Outline / Stroke** | `FX` | Pixel-perfect white outline — ideal for selection highlights |
| 11 | **Animation Preview** | `Play` | Real-time looping animation playback at configurable FPS |
| 12 | **Unity Export** | `C#` | Ready-to-use C# EditorWindow import script |
| 13 | **Godot Import** | `GDScript` | Godot 4 `@tool` EditorPlugin with SpriteFrames setup |
| 14 | **Unreal Import** | `Python` | Python plugin for Unreal's Content Browser import system |
| 15 | **GameMaker Script** | `GML` | Async HTTP + `sprite_add` GML that loads sprites at runtime |

---

## 🎨 Color Palettes

12 built-in palettes, selectable in the UI or via the `palette` keyword in prompts.

| Palette | Best For |
|---|---|
| `fire` | Warriors, lava worlds, dragons, fire magic |
| `ice` | Winter levels, ice mages, frozen environments |
| `nature` | Forests, druids, earth elements, outdoor scenes |
| `dark` | Dungeons, undead, shadow magic, horror |
| `gold` | Treasure, divine characters, sun temples |
| `poison` | Toxic zones, alchemists, swamp creatures |
| `ocean` | Water levels, merfolk, aquatic environments |
| `stone` | Rocks, golems, ruins, grey castles |
| `magic` | Wizards, arcane portals, spell effects |
| `neon` | Cyberpunk cities, synthwave, glowing tech |
| `earth` | Cavemen, desert, natural tones |
| `blood` | Horror, boss fights, dark warriors |

The **Pixel Editor** also ships with 8 curated theme palettes:

`Game Boy` · `NES Classic` · `PICO-8` · `ENDESGA 32` · `Nord` · `Sunset` · `Neon City` · `Earthtones`

---

## 🔤 Prompt Guide

Prompts are plain English. Mix **category**, **style**, **palette**, and **size** keywords in any order.

### Formula

```
[adjectives] + [category] + [style] + [palette] + [size]
```

### Examples

```
pixel art warrior character fire palette 64px
sci-fi spaceship neon blue 128px
dungeon stone floor tile 32px
cartoon wizard ice magic 64px
health potion ui icon red 32px
zombie enemy dark pixel art 64px
wooden chest prop fantasy 64px
dragon boss fire dark 128px
alien robot sci-fi neon 64px
ocean water tile blue 32px
```

### Keyword Reference

| Type | Keywords |
|---|---|
| **Category** | `character` `tile` `item` `weapon` `ui` `environment` `tree` `vehicle` `prop` `particle` `icon` |
| **Style** | `pixel` `8-bit` `cartoon` `neon` `glow` `cyberpunk` `fantasy` `sci-fi` `minimalist` |
| **Palette** | `fire` `ice` `nature` `dark` `gold` `poison` `ocean` `stone` `magic` `neon` `earth` `blood` |
| **Size** | `16px` `32px` `64px` `128px` `256px` `512px` or `tiny` `small` `large` `huge` |

> **Tip:** Auto-detect works for all fields — `warrior fire 64px` is enough.

---

## 🔌 Engine Integration

### Unity

**File:** `engine_extensions/SpriteGeneratorBridge.cs`

1. Copy to `Assets/Editor/` in your Unity project
2. Open Unity → **Tools > Sprite! Generator**
3. Enter a prompt and click **Generate Asset**

The script automatically sets `FilterMode.Point` and `TextureImporterType.Sprite` for pixel art and includes an `AnimatorController` helper for animation sheets.

```csharp
// Opens under Tools > Sprite! Generator
// Connects to http://localhost:7777
// Saves sprites directly into your Assets/ folder
```

---

### Godot 4

**File:** `engine_extensions/sprite_generator_godot/plugin.gd`

1. Copy `sprite_generator_godot/` to your project's `addons/` directory
2. Enable in **Project > Project Settings > Plugins**
3. Use the **Sprite!** panel in the bottom editor dock

```gdscript
# Appears as a bottom-panel dock in the Godot editor
# Creates .tres SpriteFrames files for AnimatedSprite2D
```

---

### Unreal Engine

**File:** `engine_extensions/sprite_generator_unreal.py`

1. Copy to `Content/Python/` in your Unreal project
2. Open **Tools > Python Script Editor**

```python
import Content.Python.sprite_generator as sg

sg.import_sprite("pixel warrior fire 64px")      # Single sprite
sg.import_pack("wizard ice magic")               # Full PBR pack
sg.generate_batch(["warrior", "mage", "archer"]) # Batch generate
sg.open_browser()                                # Open the UI
```

---

### GameMaker Studio 2

**File:** `engine_extensions/SpriteGenerator_GameMaker.gml`

1. Create a new Extension in GameMaker and add this GML file

```gml
// Create event
sprite_gen_init();
request_id = sprite_gen_create("pixel warrior fire 64px");

// Async - HTTP event
if (sprite_gen_handle_async(async_load[? "id"], async_load[? "result"])) {
    sprite_index = global._last_sprite;
}

// More functions
sprite_gen_tilemap("dungeon stone floor", 4, 4);
sprite_gen_animation("walk cycle character", 8);
sprite_gen_open_browser();
```

---

## 📡 REST API Reference

The server exposes a full REST API at `http://localhost:7777`.

### Generation Endpoints

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/generate/sprite` | `POST` | `{"prompt":"..."}` | `{image_b64, info, size}` |
| `/api/generate/3d` | `POST` | `{"prompt":"..."}` | `{obj, mtl, views:{front,rear,left,top}}` |
| `/api/generate/tilemap` | `POST` | `{"prompt":"...","cols":4,"rows":4}` | `{image_b64, cols, rows, tile_size}` |
| `/api/generate/animation` | `POST` | `{"prompt":"...","frames":8}` | `{image_b64, frames, frame_width}` |
| `/api/generate/pack` | `POST` | `{"prompt":"..."}` | `{sprite, normal, emissive, roughness, upscaled}` |
| `/api/generate/iconset` | `POST` | `{"prompt":"..."}` | `{icons:{16,32,64,128}}` |
| `/api/generate/atlas` | `POST` | `{"prompts":["...","..."]}` | `{atlas_b64, metadata}` |

### Addon Endpoints

| Endpoint | Method | Body | Returns |
|---|---|---|---|
| `/api/addon/normalmap` | `POST` | `{"image_b64":"..."}` | `{normal_b64}` |
| `/api/addon/upscale` | `POST` | `{"image_b64":"...","factor":4}` | `{upscaled_b64, size}` |
| `/api/addon/palette_swap` | `POST` | `{"image_b64":"...","palette":"fire"}` | `{swapped_b64}` |
| `/api/addon/batch` | `POST` | `{"prompts":["..."]}` | `{results:[...]}` |

### Utility Endpoints

| Endpoint | Method | Returns |
|---|---|---|
| `/api/download/zip` | `POST` | Binary ZIP file |
| `/api/palettes` | `GET` | `{palettes:[...]}` |
| `/api/categories` | `GET` | `{categories:[...]}` |
| `/api/styles` | `GET` | `{styles:[...]}` |
| `/api/health` | `GET` | `{status:"ok", version:"1.0"}` |

### Example cURL Requests

```bash
# Generate a sprite and save it
curl -X POST http://localhost:7777/api/generate/sprite \
  -H "Content-Type: application/json" \
  -d '{"prompt":"pixel warrior fire 64px"}' \
  | python3 -c "import sys,json,base64; d=json.load(sys.stdin); open('sprite.png','wb').write(base64.b64decode(d['image_b64']))"

# Download a full ZIP pack
curl -X POST http://localhost:7777/api/download/zip \
  -H "Content-Type: application/json" \
  -d '{"prompt":"wizard ice magic","include_3d":true}' \
  --output wizard_pack.zip

# Check server health
curl http://localhost:7777/api/health
```

---

## ⌨ Keyboard Shortcuts

### Main UI

| Shortcut | Action |
|---|---|
| `Ctrl + Enter` | Generate asset from prompt |
| `Ctrl + S` | Download current sprite as PNG |
| `Ctrl + Shift + S` | Download full ZIP pack |
| `Alt + 3` | Switch to 3D Views tab |
| `Escape` | Clear prompt / close modal |

### Pixel Editor

| Shortcut | Action |
|---|---|
| `P` `B` `E` `F` | Pencil / Brush / Eraser / Fill |
| `I` `L` `R` `C` `S` | Eyedropper / Line / Rect / Circle / Select |
| `X` | Swap foreground and background colours |
| `G` | Toggle pixel grid overlay |
| `[` and `]` | Decrease / increase brush size |
| `+` and `-` | Zoom in / zoom out |
| `Ctrl + Z` | Undo |
| `Ctrl + Y` | Redo |

---

## 🛠 Configuration

```bash
# Default (port 7777, auto-opens browser)
python3 run.py

# Custom port
python3 run.py --port 8080

# No auto-browser
python3 run.py --no-browser

# Environment variables
SPRITE_PORT=8080 python3 server.py
SPRITE_HOST=127.0.0.1 python3 server.py
```

The UI ships with both a **dark theme** (default) and a **light theme**. Toggle using the 🌙 / ☀ button in the header. Your preference is saved to `localStorage` and persists between sessions.

---

## 📋 Requirements

| Dependency | Version | Purpose |
|---|---|---|
| Python | 3.8+ | Runtime |
| Pillow | Any | 2D image generation |
| numpy | Any | Array operations and noise |
| scipy | Any | Gaussian blur and smoothing |
| matplotlib | Any | 3D mesh rendering |

```bash
pip install Pillow numpy scipy matplotlib
```

No GUI framework. No tkinter. No PyQt. Just a browser.

---

## 📄 License

MIT — free for personal and commercial use.

---

<div align="center">

**Sprite!** — Made with ♥ by Shivani ✦

*No APIs · No Internet · No Limits*

</div>
