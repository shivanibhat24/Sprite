#!/usr/bin/env python3
"""
Sprite! Launcher — Game Asset Generator
Created by Shivani

Usage:
    python3 run.py              # Start server on http://localhost:7777
    python3 run.py --port 8080  # Custom port
    python3 run.py --no-browser # Don't auto-open browser
"""

import sys
import os
import subprocess
import time
import threading

def check_deps():
    missing = []
    try: import PIL
    except ImportError: missing.append("Pillow")
    try: import numpy
    except ImportError: missing.append("numpy")
    try: import scipy
    except ImportError: missing.append("scipy")
    try: import matplotlib
    except ImportError: missing.append("matplotlib")
    if missing:
        print(f"\n⚠  Missing packages: {', '.join(missing)}")
        print(f"   Run: pip install {' '.join(missing)}")
        sys.exit(1)

def open_browser(port, delay=1.5):
    time.sleep(delay)
    import webbrowser
    webbrowser.open(f"http://localhost:{port}")

def main():
    port = 7777
    open_browser_flag = True

    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--port" and i+2 <= len(sys.argv[1:]):
            port = int(sys.argv[i+2])
        if arg == "--no-browser":
            open_browser_flag = False

    print("""
╔══════════════════════════════════════════════════╗
║         Sprite! — Game Asset Generator           ║
║         Created by Shivani  ✦                   ║
╚══════════════════════════════════════════════════╝""")

    check_deps()

    if open_browser_flag:
        t = threading.Thread(target=open_browser, args=(port,), daemon=True)
        t.start()

    os.environ["SPRITE_PORT"] = str(port)
    import server
    server.main()

if __name__ == "__main__":
    main()
