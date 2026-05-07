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


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# AI USE (Gemini): a Flet build is "windowed" (no attached console), so
# print() goes nowhere when launched from a terminal. AttachConsole(-1)
# (ATTACH_PARENT_PROCESS) attaches the running process to the console
# of the parent (cmd.exe / PowerShell), so stdout/stderr show up there.
def _attach_parent_console_windows():
    if sys.platform != "win32":
        return
    try:
        ATTACH_PARENT_PROCESS = -1
        if ctypes.windll.kernel32.AttachConsole(ATTACH_PARENT_PROCESS):
            # Re-bind Python stdio to the now-attached console.
            sys.stdout = open("CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace")
            sys.stderr = open("CONOUT$", "w", buffering=1, encoding="utf-8", errors="replace")
            sys.stdin  = open("CONIN$",  "r", encoding="utf-8", errors="replace")
    except Exception:
        # If attaching fails (no parent console), CLI mode will simply have no output.
        pass


if "--nogui" in sys.argv:
    _attach_parent_console_windows()
    from cli import run_cli
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