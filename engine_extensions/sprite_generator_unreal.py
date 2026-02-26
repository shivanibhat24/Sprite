"""
Sprite! — Unreal Engine Python Plugin
File: Content/Python/sprite_generator.py

Usage in Unreal:
  1. Open: Tools > Python Script Editor
  2. Run: exec(open("Content/Python/sprite_generator.py").read())
  3. Or: Tools > Execute Python Script > sprite_generator.py
  4. Also adds a menu entry under Tools > Sprite! Generator
"""

import unreal
import urllib.request
import urllib.error
import json
import os
import base64
import tempfile

SPRITE_SERVER = "http://localhost:7777"
CONTENT_PATH  = "/Game/GeneratedSprites/"

# ─── MENU ENTRY ─────────────────────────────────────────────
menus = unreal.ToolMenus.get()

def _create_menu():
    main_menu = menus.find_menu("LevelEditor.MainMenu")
    if not main_menu:
        unreal.log_warning("[Sprite!] Could not find main menu")
        return

    section_name = "SpriteGeneratorSection"
    menu_entry = unreal.ToolMenuEntry(
        name="SpriteGeneratorMenu",
        type=unreal.MultiBlockType.MENU_ENTRY,
        label="Sprite! Generator"
    )
    menu_entry.set_tool_tip("Open Sprite! Game Asset Generator in browser")
    main_menu.add_menu_entry_object(menu_entry)
    menus.refresh_all_widgets()

# ─── CORE API ────────────────────────────────────────────────
def generate_sprite(prompt: str, asset_type: str = "sprite") -> dict:
    """Call Sprite! server and return JSON response."""
    url = f"{SPRITE_SERVER}/api/generate/{asset_type}"
    payload = json.dumps({"prompt": prompt}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type": "application/json"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.URLError as e:
        unreal.log_error(f"[Sprite!] Server error: {e}. Is server.py running?")
        return {}


def import_sprite(prompt: str, name: str = None, size: int = 64) -> str:
    """
    Generate a sprite and import it into Unreal's Content Browser.
    Returns the asset path or empty string on failure.
    """
    full_prompt = f"{prompt} {size}px"
    unreal.log(f"[Sprite!] Generating: {full_prompt}")

    data = generate_sprite(full_prompt)
    if not data.get("image_b64"):
        unreal.log_error("[Sprite!] No image data returned")
        return ""

    # Decode PNG
    img_bytes = base64.b64decode(data["image_b64"])
    safe_name = (name or prompt.replace(" ", "_"))[:30]
    tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
    tmp.write(img_bytes); tmp.close()

    # Import via AssetTools
    asset_tools = unreal.AssetToolsHelpers.get_asset_tools()
    task = unreal.AssetImportTask()
    task.path             = tmp.name
    task.destination_path = CONTENT_PATH
    task.destination_name = safe_name
    task.replace_existing = True
    task.automated        = True
    task.save             = True
    asset_tools.import_asset_tasks([task])
    os.unlink(tmp.name)

    full_path = f"{CONTENT_PATH}{safe_name}"
    unreal.log(f"[Sprite!] ✓ Imported: {full_path}")
    return full_path


def import_pack(prompt: str) -> dict:
    """Generate and import a full asset pack (sprite + normal + emissive)."""
    data = generate_sprite(prompt + " 64px", "pack")
    results = {}
    maps = [("sprite","_base"), ("normal","_normal"), ("emissive","_emissive")]
    for key, suffix in maps:
        if not data.get(key): continue
        img_bytes = base64.b64decode(data[key])
        safe_name = prompt.replace(" ","_")[:20] + suffix
        tmp = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        tmp.write(img_bytes); tmp.close()
        task = unreal.AssetImportTask()
        task.path             = tmp.name
        task.destination_path = CONTENT_PATH
        task.destination_name = safe_name
        task.replace_existing = True
        task.automated        = True
        task.save             = True
        unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks([task])
        os.unlink(tmp.name)
        results[key] = f"{CONTENT_PATH}{safe_name}"
        unreal.log(f"[Sprite!] ✓ Imported {key}: {results[key]}")
    return results


def open_browser():
    """Open the Sprite! web UI in the default browser."""
    import webbrowser
    webbrowser.open(SPRITE_SERVER)


def generate_batch(prompts: list) -> list:
    """Generate multiple sprites at once."""
    url = f"{SPRITE_SERVER}/api/addon/batch"
    payload = json.dumps({"prompts": prompts}).encode("utf-8")
    req = urllib.request.Request(url, data=payload,
                                  headers={"Content-Type":"application/json"},
                                  method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8")).get("results",[])
    except Exception as e:
        unreal.log_error(f"[Sprite!] Batch error: {e}")
        return []


# ─── QUICK START ────────────────────────────────────────────
unreal.log("=" * 50)
unreal.log("  Sprite! — Game Asset Generator loaded!")
unreal.log(f"  Server: {SPRITE_SERVER}")
unreal.log("  Usage:")
unreal.log("    import_sprite('pixel warrior fire 64px')")
unreal.log("    import_pack('wizard ice magic')")
unreal.log("    open_browser()")
unreal.log("=" * 50)
