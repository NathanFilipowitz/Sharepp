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
import tempfile
import qrcode
import io
import base64
import asyncio
from aiohttp import web
from models.model import Model
from controllers import hotspot_controller
from controllers import network_controller
from controllers.server_controller import build_app, parse_user_agent
from controllers.hotspot_controller import ensure_admin
from pathlib import Path
from views import download_view
from views.view import View

class Controller:
    def __init__(self, page: ft.Page):
        self.model = Model()
        self.view = View(page, self)
    
    # Thread dedicated to rendering logs, because the aiohttp server runs on a different one than Flet's.
    # message: "success", "warning", "error", "info"
    def log(self, message, level):
        self.model.log_to_file(message, level)
        # Use run_thread to call UI-updating methods from other threads
        self.view.page.run_task(self._async_log_entry, message, level)
    
    async def _async_log_entry(self, message, level):
        self.view.add_log_entry(message, level)
    
    async def pick_folder(self, e):
        path = await ft.FilePicker().get_directory_path()
        if path:
            self.model.set_path(path)
            self.view.update_ui_for_path(path)
    
    async def on_file_picker_result(self, e: ft.FilePickerUploadEvent):
        if e.path:
            self.model.set_path(e.path)
            self.view.update_ui_for_path(e.path)
            self.log(f"Dossier sélectionné : {e.path}", "info")
    
    def open_port_dialog(self, e):
        self.view.open_port_dialog()

    def save_port(self, value):
        try:
            new_port = int(value)
            if 1024 <= new_port <= 65535:
                self.model.set_port(new_port)
                self.log(f"Port changé : {new_port}", "info")
            else:
                self.log("Port invalide — doit être entre 1024 et 65535", "warning")
        except Exception as e:
            self.log(f"Valeur de port invalide : {e}", "warning")
    
    def open_hotspot_config_dialog(self, e):
        self.view.open_hotspot_config_dialog()
    
    def save_hotspot_credentials(self, ssid, password):
        if len(password) < 8:
            self.log("Le mot de passe doit faire au moins 8 caractères.", "warning")
            return
        self.model.set_hotspot_credentials(ssid, password)
        self.log(f"Configuration Wi-Fi sauvegardée : {ssid}", "info")
    
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

    def toggle_copy_clipboard(self, event):
        self.model.toggle_copy_clipboard()
        event.control.checked = self.model.data["copy_to_clipboard"]
        self.view.page.update()

    # AI USE: I PARTIALLY USED AI FOR CREATING THIS FUNCTION (journal_travail for more details)
    async def start_server(self, e=None):
        if not self.model.selected_path:
            self.view.update_result("Veuillez d'abord sélectionner un dossier.")
            return
        if self.model.server_running:
            return

        # Récupère le hash du mot de passe si la protection est active
        password_hash = self.model.data["password"] if self.model.data["is_protected"] else ""

        # build_app reçoit self.log comme fonction de logging
        # self.log écrit à la fois dans le fichier et dans l'UI Flet
        app = build_app(self.model.selected_path, password_hash, self.log)

        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.model.port)
        try:
            await site.start()
        except Exception as e:
            self.log(f"Erreur lors du lancement du serveur sur le port {self.model.port} : {e}", "error")
            return

        self.model.server_runner = runner
        self.model.server_running = True
        self.view.update_server_status(True)

        # Automatically start hotspot if enabled in settings
        if self.model.data.get("hotspot_enabled", False):
            await self._start_hotspot_ap(None)

        local_ip, tailscale_ip, hotspot_ip = await asyncio.to_thread(self._detect_all_ips)
        await self._show_connection_info(local_ip, tailscale_ip, hotspot_ip)

        status = "Protection activée" if self.model.data["is_protected"] else "Serveur ouvert (sans protection)"
        self.log(status, "warning" if self.model.data["is_protected"] else "info")
        self.log(f"Serveur ouvert sur le port {self.model.port}", "info")
    
    async def stop_server(self, e):
        if self.model.server_running and self.model.server_runner:
            status = await asyncio.to_thread(hotspot_controller.get_hotspot_status)
            if status["running"]:
                await self._stop_hotspot_ap(None)

            await self.model.server_runner.cleanup()
            self.model.server_runner = None
            self.model.server_running = False
            self.view.update_server_status(False)
            self.view.show_controls()
            self.log("Serveur fermé", "error")

    def generate_qr_data_url(self, url):
        if not url:
            return None

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
        img_b64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_b64}"
    
    async def toggle_hotspot(self, e):
        # prevention against running netsh without admin (app crash)
        if sys.platform == "win32":
            ensure_admin()
        status = await asyncio.to_thread(hotspot_controller.get_hotspot_status)
        if status["running"]:
            await self._stop_hotspot_ap(e)
        else:
            await self._start_hotspot_ap(e)

    
    async def _start_hotspot_ap(self, e):
        self.log("Initialisation du Hotspot...", "info")
        # get wifi details from model
        ssid = self.model.hotspot_ssid
        pwd  = self.model.hotspot_password

        # run in asyncio thread not to block the app
        success, message = await asyncio.to_thread(hotspot_controller.setup_and_start, ssid, pwd)

        if not success:
            self.log(f"Erreur hotspot : {message}", "error")
            return
        self.log(f"Hotspot demarre : {ssid}", "success")
        wifi_string = f"WIFI:T:WPA;S:{ssid};P:{pwd};H:;;"
        self._hotspot_wifi_qr = self.generate_qr_data_url(wifi_string)

    async def _stop_hotspot_ap(self, e):
        ok, msg = await asyncio.to_thread(hotspot_controller.stop_hotspot)
        level = "info" if ok else "error"
        self.log(f"Hotspot : {msg}", level)
        self.view.show_controls()
    
    def _detect_all_ips(self):
        local_ip = network_controller.get_local_ip()
        tailscale_ip = network_controller.get_tailscale_ip(self.model.port)
        hotspot_ip = network_controller.get_hotspot_ip()
        return local_ip, tailscale_ip, hotspot_ip


    # Generate QR Codes and update UI based on available IPs.
    async def _show_connection_info(self, local_ip, tailscale_ip, hotspot_ip):
        local_url = f"http://{local_ip}:{self.model.port}" if local_ip else None
        tailscale_url = f"http://{tailscale_ip}:{self.model.port}" if tailscale_ip else None
        hotspot_url = f"http://{hotspot_ip}:{self.model.port}" if hotspot_ip else None

        local_qr = self.generate_qr_data_url(local_url) if local_url else None
        ts_qr = self.generate_qr_data_url(tailscale_url) if tailscale_url else None
        hotspot_qr = self.generate_qr_data_url(hotspot_url) if hotspot_url else None
        hotspot_wifi_qr = getattr(self, "_hotspot_wifi_qr", None)

        self.view.show_connection_tiles(
            local_qr,     local_url,
            ts_qr,        tailscale_url,
            hotspot_qr,   hotspot_url,
            hotspot_wifi_qr
        )

        if tailscale_url:
            self.log(f"Tailscale détecté : {tailscale_url}", "success")
        if hotspot_url:
            self.log(f"Point d'accès Wi-Fi actif : {hotspot_url}", "success")
    