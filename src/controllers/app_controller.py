"""
app_controller.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles application business logic

"""

from models.model import Model
from views.view import View
import flet as ft
import os
import shutil
import tempfile
from aiohttp import web
from views import download_view
from pathlib import Path

class Controller:
    def __init__(self, page: ft.Page):
        self.model = Model()
        self.view = View(page, self)
    
    # async def pick_file(self, e):
    #     result = await self.view.file_picker.pick_files()
    #     if result and result.files:
    #         path = result.files[0].path
    #         self.model.set_path(path)
    #         self.view.update_result(path)
    
    async def pick_folder(self, e):
        path = await self.view.file_picker.get_directory_path()
        if path:
            self.model.set_path(path)
            self.view.update_result(path)
    
    def toggle_logs(self, e):
        self.model.toggle_logs()
        self.view.toggle_logs_visibility()
    
    def open_settings(self, e):
        self.view.show_settings()
    
    def close_settings(self, e):
        self.view.close_settings_dialog()

    # AI USE: I PARTIALLY USED AI FOR CREATING THIS FUNCTION (journal_travail for more details)
    async def start_server(self, e):
        # Check that a path was selected and the server isn't already running
        if not self.model.selected_path:
            self.view.update_result("Veuillez d'abord sélectionner un dossier.")
            return
        if self.model.server_running:
            return

        # First handler, handles serving the files from the selected path to the server. Calls the download_view file for rendering
        async def handle_index(request):
            try:
                files = os.listdir(self.model.selected_path)
                # It uses the download_view to generate an HTML page with links to the files.
                return web.Response(text=download_view.generate_html(files), content_type='text/html')
            except Exception as err:
                return web.Response(text=str(err), status=500)

        # Second handler, serves a specific file when the user clicks on one.
        async def handle_download(request):
            # sorts the request to only get the filename
            filename = request.match_info.get('filename')
            if not filename:
                return web.Response(text="Bad Request", status=400)

            # Security feature (AI Implemantation):
            # To prevent users from accessing files outside the shared folder (directory traversal attack),
            # we build a full, absolute path and verify it's still inside the shared folder.
            base_dir = Path(self.model.selected_path).resolve()
            requested_path = (base_dir / filename).resolve()

            # Check if the path is a file and is within the allowed directory
            if requested_path.is_file() and str(requested_path).startswith(str(base_dir)):
                # Add a header to the response so the downloaded file doesn't just open in the browser
                return web.FileResponse(requested_path, headers={
                    'Content-Disposition': f'attachment; filename="{filename}"',
                    'Content-Type': 'application/octet-stream'
                })
            # Check if the path is a folder, create a temporary
            if requested_path.is_dir():
                # Create a temporary name for the folder (tmp) to then compress it before sending
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                    zip_path = shutil.make_archive(tmp.name.replace('.zip', ''), 'zip', requested_path)
                    return web.FileResponse(zip_path, headers={
                        'Content-Disposition': f'attachment; filename="{filename}.zip"'
                    })
            
            return web.Response(text="File not found", status=404)

        app = web.Application()

        # The route for the main page (e.g., http://localhost:8080/)
        app.router.add_get('/', handle_index)
        # The route for file downloads (e.g., http://localhost:8080/document.pdf)
        app.router.add_get('/{filename}', handle_download)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', 8080)
        await site.start()
        
        self.model.server_runner = runner
        self.model.server_running = True
        self.view.update_server_status(True)
        self.view.update_result(f"Serveur démarré sur http://localhost:8080 (Dossier: {self.model.selected_path})")

    
    async def stop_server(self, e):
        if self.model.server_running and self.model.server_runner:
            await self.model.server_runner.cleanup()
            self.model.server_runner = None
            self.model.server_running = False
            self.view.update_server_status(False)
            self.view.update_result("Serveur arrêté.")