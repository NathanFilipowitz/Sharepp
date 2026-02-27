"""
main.py

Author:  Nathan Filipowitz
Date:    2026-02-24
Purpose: Entry point for the application. It should just make calls to other files of the app.

"""

import flet as ft
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from controllers.app_controller import Controller

def main(page: ft.Page):
    page.title = "Share++"
    page.window_width = 900
    page.window_height = 600
    Controller(page)

ft.run(main)