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
    run_cli()
else:
    # Start GUI app in administrator mode for exectuing netsh commands
    if os.name == 'nt' and not is_admin():
        args = " ".join(f'"{a}"' for a in sys.argv[1:])
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, args,
            os.path.dirname(sys.executable),  # WorkingDirectory explicite
            1
        )
        sys.exit(0)

    import flet as ft
    from controllers.app_controller import Controller

    def main(page: ft.Page):
        page.title = "Share++"
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

    ft.run(main, assets_dir="assets")