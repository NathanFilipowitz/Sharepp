"""
main.py

Author:  Nathan Filipowitz
Date:    2026-02-24
Purpose: Entry point for the application. It should just make calls to other files of the app.

"""

import flet as ft
import sys
import os
from pathlib import Path
from controllers.app_controller import Controller

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def main(page: ft.Page):
    page.title = "Share++"
    app = Controller(page)

    if len(sys.argv) > 1:
        folder_path = sys.argv[1]
        if os.path.isdir(folder_path):
            app.model.set_path(folder_path)
            page.run_task(app.start_server, None)
            app.view.update_ui_for_path(folder_path)
            page.update()

ft.run(main)