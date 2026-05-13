"""
main.py

Author:  Nathan Filipowitz
Date:    2026-02-24
Purpose: Entry point for the application (GUI mode only).
         The CLI mode is packaged as a separate executable (sharepp-cli.exe)
         built with PyInstaller — see cli.py.
"""

import os
import sys
import ctypes
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

# AI USE (Gemini): On Windows, when the app is launched via the explorer
# context menu, the current working directory is the selected folder.
# Flet/Flutter then tries to create its data folder inside the CWD, which
# causes "PathAccessException: Cannot create file" if the user has no
# write access there. We force CWD to the executable's directory before
# importing Flet to avoid this crash.
if sys.platform == "win32" and getattr(sys, "frozen", False):
    try:
        os.chdir(os.path.dirname(sys.executable))
    except Exception:
        pass

# AI FIX (Gemini): use asyncio correct event loop for Windows
if sys.platform == "win32":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import flet as ft
from controllers.app_controller import Controller

def main(page: ft.Page):
    page.title = "Share++"
    page.window.width = 1000
    page.window.height = 800
    page.window.min_width = 1000
    page.window.min_height = 800

    app = Controller(page)

    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            app.model.set_path(folder_path)
            page.run_task(app.start_server, None)
            app.view.update_ui_for_path(folder_path)
            page.update()

# ft.run(main, assets_dir="assets")
ft.run(main)