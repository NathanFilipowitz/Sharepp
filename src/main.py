"""
main.py

Author:  Nathan Filipowitz
Date:    2026-02-24
Purpose: Entry point for the application. It should just make calls to other files of the app.

"""

import os
import sys
import flet as ft
import ctypes
from pathlib import Path
from controllers.app_controller import Controller

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False


def main(page: ft.Page):
    # Admin verification, user needs to be admin for Access Point feature to work
    if os.name == 'nt' and not is_admin():
        # Starts app in Administrator mode
        args = " ".join(f'"{arg}"' for arg in sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, args, None, 1)
        sys.exit(0)
    page.title = "Share++"
    # Taille de fenêtre compacte et fixe
    page.window.width = 900
    page.window.height = 560
    page.window.min_width = 900
    page.window.min_height = 560

    app = Controller(page)

    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            app.model.set_path(folder_path)
            page.run_task(app.start_server, None)
            app.view.update_ui_for_path(folder_path)
            page.update()

# Give Flet access to static assets (app_icon)
ft.run(main, assets_dir="assets")