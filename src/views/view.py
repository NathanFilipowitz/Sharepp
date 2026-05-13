"""
view.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handle frontend/User Interface for the application

"""


import datetime
import os
import flet as ft
import subprocess
import sys
import webbrowser

class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        
        self.pick_button = ft.Button("Ouvrir un dossier", icon=ft.Icons.FOLDER_OPEN_ROUNDED, on_click=self.controller.pick_folder)
        
        self.result_text = ft.Text(
            "Aucun dossier n'a encore été sélectionné",
            selectable=True,
            italic=True,
            overflow=ft.TextOverflow.CLIP
        )

        # Start/Stop Server buttons initially hidden
        self.start_button = ft.Button(
            "Démarrer le partage",
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            visible=False,
            on_click=self.controller.start_server,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.BLUE_400},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
            ),
        )
        # Stop button shown under the QR code
        self.stop_button_qr = ft.Button(
            "Arrêter le partage",
            icon=ft.Icons.STOP_ROUNDED,
            visible=False,
            on_click=self.controller.stop_server,
            style=ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.RED_400},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
            ),
        )
        
        # Store used urls to show them later
        self._primary_url = ""
        self._secondary_url = ""  # Tailscale url

        
        # Logs panel (right side)
        self.logs_column = ft.Column(
            [],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.logs_container = ft.Container(
            content=self.logs_column,
            bgcolor=ft.Colors.SURFACE_CONTAINER,
            border_radius=10,
            padding=10,
            visible=True,
            expand=True,
            margin=20,
            ink=True
        )
        
        # Left side content
        self.path_text = ft.Text("", weight=ft.FontWeight.BOLD, size=16)
        
        # AppBar
        self.appbar_title = ft.Text(
            "SÉLECTIONNER UN DOSSIER POUR DÉMARRER UN PARTAGE",
            size=14,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.WHITE,
            selectable=True
        )
        
        self.page.appbar = ft.AppBar(
            leading=ft.Icon(ft.Icons.SHARE, color=ft.Colors.WHITE, size=30),
            leading_width=60,
            title=self.appbar_title,
            center_title=True,
            bgcolor=ft.Colors.BLUE_200,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.CHAT_OUTLINED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Afficher les logs",
                    on_click=self.controller.toggle_logs,
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content="Enregistrer le chemin", 
                            checked=self.controller.model.data["remember_path"],
                            on_click=self.controller.toggle_remember_path
                        ),
                        ft.PopupMenuItem(
                            content="Copier l'adresse automatiquement",
                            checked=self.controller.model.data["copy_to_clipboard"],
                            on_click=self.controller.toggle_copy_clipboard
                        ),
                        ft.PopupMenuItem(),  # divider
                        ft.PopupMenuItem(
                            content="Effacer l'adresse",
                            on_click=self.controller.clear_path),
                        ft.PopupMenuItem(
                            content="Changer le port",
                            on_click=self.controller.open_port_dialog
                        ),
                        ft.PopupMenuItem(
                            content="Historique des téléchargements",
                            on_click=self.controller.open_history,
                        ),
                    ],
                    icon_color=ft.Colors.WHITE
                ),
            ],
        )

        self.password_entry = ft.TextField(
            label="Mot de passe",
            password=True,
            icon=ft.Icons.LOCK,
            can_reveal_password=True,
            visible=False,
            on_change=lambda e: self.controller.update_password(e.control.value)
        )

        self.password_protect_control_chip = ft.Chip(
                label=ft.Text("Protéger le partage"),
                on_click=self.toggle_password_visibility,
            )

        self.hotspot_chip = ft.Chip(
            label=ft.Text("Créer un point d'accès Wi-Fi au démarrage"),
            on_click=self._toggle_hotspot_enabled,
            selected=self.controller.model.data.get("hotspot_enabled", False),
            # Greyed out on non-windows platforms
            disabled=sys.platform != "win32",
            tooltip="Nécessite Windows et une carte Wi-Fi compatible" if sys.platform != "win32" else "",
        )

        self.hotspot_config_button = ft.TextButton(
            "Configurer le réseau Wi-Fi",
            icon=ft.Icons.SETTINGS_OUTLINED,
            on_click=self.controller.open_hotspot_config_dialog,
            disabled=sys.platform != "win32",
        )

        self.controls_content = ft.Column([
            self.pick_button,
            ft.Text("Répertoire:", weight=ft.FontWeight.BOLD),
            ft.Container(
                self.result_text,
                width=200
            ),
            self.password_protect_control_chip,
            ft.Container(
                self.password_entry,
                width=200,
            ),
            ft.Divider(height=8),
            self.hotspot_chip,
            self.hotspot_config_button,
            self.start_button,
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
        )

        # Main functionnalities Card (left column)
        self.toggle_card = ft.Card(
            content=ft.Container(
                content=self.controls_content,
                alignment=ft.Alignment.CENTER,
                ink=True,
                padding=20
            ),
            margin=ft.margin.only(left=20, right=20, top=20, bottom=0),
            elevation=10,
            expand=True
        )

        self.left_column = ft.Column(
            [self.toggle_card],
            spacing=0,
            expand=True,
        )
        
        # Main layout row
        self.main_row = ft.Row(
            [
                self.left_column,
                self.logs_container,
            ],
            expand=True,
            spacing=20,
        )
        
        self.page.add(ft.Column([self.main_row], expand=True, spacing=0))

        if self.controller.model.selected_path:
            self.update_ui_for_path(self.controller.model.selected_path)
    
    # View function to add a log to the logs container
    def add_log_entry(self, message, level):
        color_map = {
            "success": ft.Colors.LIGHT_GREEN_400,
            "warning": ft.Colors.LIME_400,
            "error": ft.Colors.DEEP_ORANGE_400,
            "info": ft.Colors.INVERSE_PRIMARY,
        }
        log_color = color_map.get(level, ft.Colors.BLACK)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        log_text = ft.Text(f"[{timestamp}] {message}", size=12, color=log_color, selectable=True)
        self.logs_column.controls.append(log_text)
        self.page.update()
    
    def toggle_logs_visibility(self):
        self.logs_container.visible = not self.logs_container.visible
        self.page.update()
    
    # turns the password TextField widget visible and gives a pressed look to the chip when enabled
    def toggle_password_visibility(self, e):
        self.password_entry.visible = not self.password_entry.visible
        e.control.selected = self.password_entry.visible
        self.controller.toggle_protection(e) 
        self.page.update()
    
    def open_port_dialog(self):
        port_field = ft.TextField(
            label="Port",
            value=str(self.controller.model.port),
            keyboard_type=ft.KeyboardType.NUMBER,
            width=150,
        )

        def save(e):
            self.controller.save_port(port_field.value)
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Changer le port du serveur"),
            content=port_field,
            actions=[
                ft.TextButton(
                    "Annuler",
                    on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()
                ),
                ft.TextButton("Enregistrer", on_click=save),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    def open_hotspot_config_dialog(self):
        ssid_field = ft.TextField(
            label="Nom du réseau (SSID)",
            value=self.controller.model.hotspot_ssid,
            width=250,
        )
        pwd_field = ft.TextField(
            label="Mot de passe Wi-Fi",
            value=self.controller.model.hotspot_password,
            password=True,
            can_reveal_password=True,
            width=250,
            helper="Minimum 8 caractères (WPA2)",
        )

        def save(e):
            self.controller.save_hotspot_credentials(
                ssid_field.value, pwd_field.value
            )
            dialog.open = False
            self.page.update()

        dialog = ft.AlertDialog(
            title=ft.Text("Configuration réseau Wi-Fi"),
            content=ft.Column([ssid_field, pwd_field], spacing=12, tight=True),
            actions=[
                ft.TextButton("Annuler", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
                ft.TextButton("Enregistrer", on_click=save),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()
    
    def open_history_dialog(self, history, shared_path):
        # open file in file explorer if shared path was successfully recovered and path still exists
        def open_in_explorer(filename):
            if not shared_path:
                return
            filepath = os.path.join(shared_path, filename)
            if os.path.exists(filepath):
                subprocess.run(["explorer", "/select,", filepath], shell=False)

        if not history:
            rows = [ft.Text("Aucun téléchargement enregistré.", italic=True, color=ft.Colors.GREY_500)]
        else:
            rows = []
            for entry in history:
                filepath = os.path.join(shared_path or "", entry["filename"])
                file_exists = shared_path and os.path.exists(filepath)

                rows.append(
                    ft.Container(
                        content=ft.Row(
                            [
                                ft.Column(
                                    [
                                        ft.Text(entry["filename"], weight=ft.FontWeight.BOLD, size=13, overflow=ft.TextOverflow.ELLIPSIS),
                                        ft.Text(f"{entry['timestamp']}  ·  {entry['ip']}  ·  {entry['device']}", size=11, color=ft.Colors.GREY_600),
                                    ],
                                    spacing=2,
                                    expand=True,
                                ),
                                ft.IconButton(
                                    icon=ft.Icons.FOLDER_OPEN_ROUNDED,
                                    icon_size=18,
                                    tooltip="Ouvrir dans l'explorateur",
                                    disabled=not file_exists,
                                    on_click=lambda e, f=entry["filename"]: open_in_explorer(f),
                                ),
                            ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER,
                        ),
                        padding=ft.padding.symmetric(horizontal=12, vertical=8),
                        border=ft.border.only(bottom=ft.BorderSide(1, ft.Colors.GREY_200)),
                    )
                )

        dialog = ft.AlertDialog(
            modal=True,  # Freezes app while window is openend
            title=ft.Row([
                ft.Icon(ft.Icons.HISTORY_ROUNDED, color=ft.Colors.BLUE_400),
                ft.Text("Historique des téléchargements"),
            ], spacing=8),
            content=ft.Container(
                content=ft.Column(rows, scroll=ft.ScrollMode.AUTO, spacing=0),
                width=520,
                height=400,
            ),
            actions=[
                ft.TextButton("Fermer", on_click=lambda e: setattr(dialog, 'open', False) or self.page.update()),
            ],
        )
        self.page.overlay.append(dialog)
        dialog.open = True
        self.page.update()

    # Updates title and shows/hides server icons if a path was selected
    def update_ui_for_path(self, path, is_running=False):
        if path:
            self.appbar_title.value = f"Chemin: {path}"
            self.result_text.value = path
            self.start_button.visible = not is_running
            self.pick_button.icon = ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
        else:
            self.appbar_title.value = "SÉLECTIONNER UN DOSSIER"
            self.result_text.value = f"Aucun dossier n'a encore été sélectionné"
            self.start_button.visible = False
            self.pick_button.icon = ft.Icons.FOLDER_OPEN_ROUNDED
        self.page.update()

    # Toggle the icons between start and stop, and turns the left Card unavailable whenever the server is started.
    def update_server_status(self, running):
        self.start_button.visible = not running
        self.stop_button_qr.visible = running
        # Don't deactivate the entire card, just each widgets independently. Prevention to unclickable button when qr is shown
        self.pick_button.disabled = running
        self.password_protect_control_chip.disabled = running
        self.toggle_card.disabled = False
        self.page.update()
    
    def _toggle_hotspot_enabled(self, e):
        self.controller.model.toggle_hotspot_enabled()
        e.control.selected = self.controller.model.data["hotspot_enabled"]
        self.page.update()

    def show_connection_tiles(self, local_qr, local_url, ts_qr, ts_url, hotspot_qr, hotspot_url, hotspot_wifi_qr=None):
        self._primary_url   = local_url   or ""
        self._secondary_url = ts_url      or ""
        self.stop_button_qr.visible = True

        tiles = [
            ft.Container(self.stop_button_qr, alignment=ft.Alignment.CENTER, padding=8),
            ft.Divider(height=1),
        ]

        # Hotspot usage guide, only active if hotspot is active
        if hotspot_url:
            tiles.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.WIFI_TETHERING, color=ft.Colors.BLUE_600, size=16),
                        ft.Text("Point d'accès Wi-Fi", weight=ft.FontWeight.BOLD, size=13, italic=True, expand=True,),
                    ], spacing=8),
                    bgcolor=ft.Colors.BLUE_50,
                    border_radius=8,
                    padding=ft.padding.symmetric(horizontal=12, vertical=8),
                    margin=ft.margin.symmetric(horizontal=8),
                )
            )

        if hotspot_wifi_qr:
            tiles.append(self._make_qr_expansion_tile(
                "1 · Se connecter au Wi-Fi Share++",
                hotspot_wifi_qr, "",
                icon=ft.Icons.WIFI_ROUNDED,
                expanded=True,       # ouvert par défaut
            ))
            tiles.append(self._make_qr_expansion_tile(
                "2 · Télécharger les fichiers",
                hotspot_qr, hotspot_url,
                icon=ft.Icons.DOWNLOAD_ROUNDED,
            ))
            tiles.append(ft.Divider(height=8, thickness=2))

            # Bloc réseau local
        if local_url:
            tiles.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.LAN, color=ft.Colors.GREY_600, size=16),
                        ft.Text("Réseau local", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.GREY_600),
                    ], spacing=6),
                    padding=ft.padding.only(left=16, top=4, bottom=4),
                )
            )
            tiles.append(self._make_qr_expansion_tile("Réseau local", local_qr, local_url))

        # Bloc Tailscale
        if ts_url:
            tiles.append(ft.Divider(height=8, thickness=2))
            tiles.append(
                ft.Container(
                    content=ft.Row([
                        ft.Icon(ft.Icons.VPN_LOCK_ROUNDED, color=ft.Colors.PURPLE_400, size=16),
                        ft.Text("Tunnel (Tailscale)", weight=ft.FontWeight.BOLD, size=13, color=ft.Colors.PURPLE_400),
                    ], spacing=6),
                    padding=ft.padding.only(left=16, top=4, bottom=4),
                )
            )
            tiles.append(self._make_qr_expansion_tile("Tailscale", ts_qr, ts_url))
        self.toggle_card.content.content = ft.Column(tiles, spacing=0)
        self.page.update()
        
    # replace QR code with controls for the card content
    def show_controls(self):
        self.toggle_card.content.content = self.controls_content
        self.stop_button_qr.visible = False
        self.start_button.visible = bool(self.controller.model.selected_path)
        self._primary_url = ""
        self._secondary_url = ""
        self.page.update()

    def show_hotspot_qr_codes(self, wifi_qr, url_qr, ssid, password, download_url):
        async def _copy_url(e):
            await ft.Clipboard().set(download_url)
            self.page.show_dialog(ft.SnackBar(ft.Text("Adresse copiée !"), duration=1500))
            self.page.update()

        self.hotspot_card.content.content = ft.Column(
            [
                # Stop Button. Always visible
                ft.Container(
                    ft.Button(
                        "Arrêter le point d'accès",
                        icon=ft.Icons.WIFI_TETHERING_OFF,
                        on_click=self.controller.toggle_hotspot,
                        style=ft.ButtonStyle(
                            bgcolor={ft.ControlState.DEFAULT: ft.Colors.RED_400},
                            color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
                        ),
                    ),
                    alignment=ft.Alignment.CENTER,
                    padding=8,
                ),
                ft.Divider(height=1),
                # QR Wi-Fi, step 1, connect to Wi-Fi
                ft.ExpansionTile(
                    leading=ft.Icon(ft.Icons.WIFI_ROUNDED),
                    title=ft.Text("1 · Se connecter au Wi-Fi", size=13),
                    subtitle=ft.Text(f"{ssid}  ·  mdp : {password}", size=11),
                    expanded=False,
                    maintain_state=True,
                    controls_padding=ft.padding.symmetric(horizontal=8, vertical=8),
                    controls=[
                        ft.Column(
                            [ft.Image(src=wifi_qr, width=180, height=180, fit=ft.BoxFit.CONTAIN)],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ] if wifi_qr else [ft.Text("QR indisponible", italic=True, size=12)],
                ),
                # QR URL, step 2, download files
                ft.ExpansionTile(
                    leading=ft.Icon(ft.Icons.DOWNLOAD_ROUNDED),
                    title=ft.Text("2 · Télécharger les fichiers", size=13),
                    subtitle=ft.Row(
                        [
                            ft.Text(
                                download_url or "Serveur non démarré",
                                size=11,
                                selectable=True,
                                expand=True,
                                overflow=ft.TextOverflow.ELLIPSIS,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.OPEN_IN_BROWSER_ROUNDED,
                                tooltip="Ouvrir dans le navigateur",
                                icon_size=16,
                                on_click=lambda _: webbrowser.open(download_url) if download_url else None,
                            ),
                            ft.IconButton(
                                icon=ft.Icons.COPY_ROUNDED,
                                tooltip="Copier l'adresse",
                                icon_size=16,
                                on_click=_copy_url,
                            ),
                        ],
                        spacing=0,
                        vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    ),
                    expanded=False,
                    maintain_state=True,
                    controls_padding=ft.padding.symmetric(horizontal=8, vertical=8),
                    controls=[
                        ft.Column(
                            [ft.Image(src=url_qr, width=180, height=180, fit=ft.BoxFit.CONTAIN)],
                            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        )
                    ] if url_qr else [ft.Text("QR indisponible", italic=True, size=12)],
                ),
            ],
            spacing=0,
        )
        self.page.update()

    def _make_qr_expansion_tile(self, title, qr_data, url, icon=ft.Icons.QR_CODE_ROUNDED, expanded=False):
        async def _copy(e, u=url):
            await ft.Clipboard().set(u)
            self.page.show_dialog(ft.SnackBar(ft.Text("Adresse copiée !"), duration=1500))
            self.page.update()

        return ft.ExpansionTile(
            title=ft.Text(title, size=13),
            subtitle=ft.Row(
                [
                    ft.Text(url, size=11, selectable=True, expand=True, overflow=ft.TextOverflow.ELLIPSIS),
                    *([ 
                        ft.IconButton(
                            icon=ft.Icons.OPEN_IN_BROWSER_ROUNDED,
                            tooltip="Ouvrir dans le navigateur",
                            icon_size=16,
                            on_click=lambda _, u=url: webbrowser.open(u),
                        ),
                        ft.IconButton(
                            icon=ft.Icons.COPY_ROUNDED,
                            tooltip="Copier l'adresse",
                            icon_size=16,
                            on_click=_copy,
                        ),
                    ] if url else []),
                ],
                spacing=0,
                vertical_alignment=ft.CrossAxisAlignment.CENTER,
            ),
            leading=ft.Icon(icon),
            expanded=expanded,
            maintain_state=True,
            controls_padding=ft.padding.symmetric(horizontal=8, vertical=8),
            controls=[
                ft.Column(
                    [
                        ft.Image(src=qr_data, width=180, height=180, fit=ft.BoxFit.CONTAIN),
                    ],
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=6,
                ),
            ] if qr_data else [ft.Text("QR indisponible", italic=True, size=12)],
        )