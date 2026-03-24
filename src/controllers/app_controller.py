"""
app_controller.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles application business logic

"""

import sys
import flet as ft
import os
import shutil
import socket
import tempfile
import qrcode
import io
import base64
from aiohttp import web
from models.model import Model
from pathlib import Path
from views import download_view
from views.view import View

class Controller:
    def __init__(self, page: ft.Page):
        self.model = Model()
        self.view = View(page, self)
    
    # Thread dedicated to rendering logs, because the aiohttp server runs on a different one than Flet's.
    # message: "success", "warning", "error", "info"
    def log(self, message: str, level: str):
        # Use run_thread to call UI-updating methods from other threads
        self.view.page.run_thread(self.view.add_log_entry, message, level)
    
    async def pick_folder(self, e):
        path = await self.view.file_picker.get_directory_path()
        if path:
            self.model.set_path(path)
            self.view.update_ui_for_path(path)
    
    async def on_file_picker_result(self, e: ft.FilePickerUploadEvent):
        if e.path:
            self.model.set_path(e.path)
            self.view.update_ui_for_path(e.path)
            self.log(f"Dossier sélectionné : {e.path}", "info")
    
    def toggle_remember_path(self, e):
        self.model.toggle_remember_path()
        e.control.checked = self.model.remember_path
        self.view.page.update()
    
    def clear_path(self, e):
        self.model.set_path("")
        self.view.update_ui_for_path("")
        self.view.page.update()
        self.log("Path cleared by user", "info")
    
    def update_password(self, value):
        self.model.set_password(value)
    
    def toggle_logs(self, e):
        self.model.toggle_logs()
        self.view.toggle_logs_visibility()
    
    def toggle_protection(self,e):
        self.model.toggle_protection()
        e.control.checked = self.model.data["is_protected"]
        self.view.page.update()
        status = "activée" if self.model.data["is_protected"] else "désactivée"
        self.log(f"Protection du partage {status}", "info")
    
    def get_local_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = None
        finally:
            s.close()
        return ip

    def toggle_copy_clipboard(self, event):
        self.model.toggle_copy_clipboard()
        event.control.checked = self.model.data["copy_to_clipboard"]
        self.view.page.update()

    def toggle_context_menu(self, event):
        # reverse current state
        new_state = not self.model.data.get("context_menu_enabled", False)
        
        # Windows registry logic (AI suggested)
        if sys.platform == "win32":
            try:
                self._update_windows_registry(new_state)
                self.model.data["context_menu_enabled"] = new_state
                self.model.save_settings()
            except Exception as e:
                print(f"Erreur registre : {e}")
        event.control.checked = self.model.data["context_menu_enabled"]
        self.view.page.update()

    # AI USE: I PARTIALLY USED AI FOR CREATING THIS FUNCTION (journal_travail for more details)
    def _update_windows_registry(self, add_menu: bool):
        import winreg
        # Use HKEY_CURRENT_USER to prevent administration privilege requirement
        key_path = r"Software\Classes\Directory\shell\Sharepp"
        
        if add_menu:
            # Create the menu in contextual right-click
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, key_path) as key:
                winreg.SetValue(key, "", winreg.REG_SZ, "Partager avec Share++")
                winreg.SetValueEx(key, "Icon", 0, winreg.REG_SZ, sys.executable)

            # Create the command to open the app
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER, rf"{key_path}\command") as key:
                # AI Implementation of finding app path in system, universally
                # sys.executable = python.exe | sys.argv[0] = main.py
                app_path = os.path.abspath(sys.argv[0])
                # %1 represents the selected folder path (provided by windows)
                winreg.SetValue(key, "", winreg.REG_SZ, f'"{sys.executable}" "{app_path}" "%1"')
        else:
            try:
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, rf"{key_path}\command")
                winreg.DeleteKey(winreg.HKEY_CURRENT_USER, key_path)
            except WindowsError:
                self.log(f"Erreur lors de la suppression du bouton contextuel. Erreur: {WindowsError}", "error")

    # AI USE: I PARTIALLY USED AI FOR CREATING THIS FUNCTION (journal_travail for more details)
    async def start_server(self, e):
        # Check that a path was selected and the server isn't already running
        if not self.model.selected_path:
            self.view.update_result("Veuillez d'abord sélectionner un dossier.")
            return
        if self.model.server_running:
            return

        async def require_auth(request, handler):
            # Skip auth if protection disabled
            if not self.model.data["is_protected"]:
                return await handler(request)
                
            # No password set = allow all
            if not self.model.data["password"]:
                return await handler(request)
            
            # Check for Authorization header
            auth_header = request.headers.get('Authorization', '')
            
            if auth_header.startswith('Basic '):
                import base64
                # Decode "user:password" from base64
                try:
                    encoded = auth_header[6:]  # Remove "Basic "
                    decoded = base64.b64decode(encoded).decode('utf-8')
                    # Format is "username:password", we only care about password
                    _, password = decoded.split(':', 1)
                    
                    if self.model.check_password(password):
                        return await handler(request)
                except Exception:
                    pass  # Invalid auth header
            
            # Password enabled or no auth header triggers browser popup
            return web.Response(
                status=401,
                headers={'WWW-Authenticate': 'Basic realm="Share++ (ignore username field)"'},
                text="Authentication required"
            )


        # First handler, handles serving the files from the selected path to the server. Calls the download_view file for rendering the front page
        async def handle_index(request):
            self.log(f"Nouvelle connexion de {request.remote}", "success")
            try:
                files = os.listdir(self.model.selected_path)
                # It uses the download_view to generate the HTML page.
                return web.Response(text=download_view.generate_html(files), content_type='text/html')
            except Exception as err:
                self.log(f"Erreur serveur: {str(err)}", "error")
                return web.Response(text=str(err), status=500)

        # Second handler, serves a specific file when the user clicks on one.
        async def handle_download(request):
            # sorts the request to only get the filename
            filename = request.match_info.get('filename')
            if not filename:
                return web.Response(text="Bad Request", status=400)

            self.log(f"{request.remote} télécharge {filename}", "warning")

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
            # Check if the path is a folder
            if requested_path.is_dir() and str(requested_path).startswith(str(base_dir)):
                # Create a temporary name for the folder (tmp) to then compress it before sending
                with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                    zip_path = shutil.make_archive(tmp.name.replace('.zip', ''), 'zip', requested_path)
                    return web.FileResponse(zip_path, headers={
                        'Content-Disposition': f'attachment; filename="{filename}.zip"'
                    })
            
            return web.Response(text="File not found", status=404)


        async def protected_index(request):
            return await require_auth(request, handle_index)
        
        async def protected_download(request):
            return await require_auth(request, handle_download)

        app = web.Application()
        # The route for the main page (http://localhost:8080/)
        app.router.add_get('/', protected_index)
        # The route for file downloads (http://localhost:8080/document.pdf)
        app.router.add_get('/{filename}', protected_download)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.model.port)
        try:
            await site.start()
        except error:
            self.log(f"Erreur lors du lancement du serveur, vérifiez votre port {self.model.port}")
        
        self.model.server_runner = runner
        self.model.server_running = True
        self.view.update_server_status(True)

        # Copy to clipboard & QR code generation
        local_ip = self.get_local_ip()
        if local_ip:
            url = f"http://{local_ip}:{self.model.port}"
            if self.model.copy_to_clipboard:
                await ft.Clipboard().set(url)
                self.view.page.show_dialog(ft.SnackBar("Adresse copiée dans le presse-papier"))

            if self.model.qr_enabled:
                qr_data = self.generate_qr_data_url(local_ip)
                if qr_data:
                    self.view.show_qr_code(qr_data, url)
        
        self.log("Protection activée" if self.model.data["is_protected"] else "Serveur ouvert (sans protection)", "warning" if self.model.data["is_protected"] else "info")
        self.log(f"Serveur ouvert sur le port {self.model.port}", "info")
    
    async def stop_server(self, e):
        if self.model.server_running and self.model.server_runner:
            await self.model.server_runner.cleanup()
            self.model.server_runner = None
            self.model.server_running = False
            self.view.update_server_status(False)
            self.view.show_controls()
            self.log("Serveur fermé", "error")
    def generate_qr_data_url(self, ip_address):
        if not ip_address:
            return None
            
        url = f"http://{ip_address}:{self.model.port}"
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for Flet Image src
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_str = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"