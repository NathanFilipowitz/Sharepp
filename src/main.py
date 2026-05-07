"""
main.py

Author:  Nathan Filipowitz
Date:    2026-02-24
Purpose: Entry point for the application. It should just make calls to other files of the app.

"""

import os
import sys
import ctypes
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if "--nogui" in sys.argv:
    from cli import run_cli
    # AI code (Gemini): hide flet's window immediatly after opening in headless mode
    if sys.platform == "win32" and getattr(sys, 'frozen', False):
        import ctypes
        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        # makes window invisible
        ctypes.windll.user32.ShowWindow(hwnd, 0)
    run_cli()
else:
    import flet as ft
    from controllers.app_controller import Controller

    # AI FIX (Gemini): use asyncio correct event loop for Windows
    if sys.platform == "win32":
        import asyncio
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

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

    ft.run(main, assets_dir="assets")