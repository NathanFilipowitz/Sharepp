"""
view.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handle frontend/User Interface for the application

"""


import flet as ft
import datetime
import sys
import webbrowser

class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        
        self.file_picker = ft.FilePicker()

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
            leading=ft.Image(src="icons/app_icon_compressed.svg"),
            leading_width=100,
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
                            content="Ajouter au menu contextuel",
                            checked=self.controller.model.data.get("context_menu_enabled", False),
                            on_click=self.controller.toggle_context_menu
                        ),
                        ft.PopupMenuItem(
                            content="Effacer l'adresse",
                            on_click=self.controller.clear_path),
                        ft.PopupMenuItem(
                            content="Copier l'adresse automatiquement",
                            checked=self.controller.model.data["copy_to_clipboard"],
                            on_click=self.controller.toggle_copy_clipboard
                        )
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

        self.hotspot_ssid_field = ft.TextField(
            label="Nom du réseau Wi-Fi (SSID)",
            value=self.controller.model.hotspot_ssid,
            prefix_icon=ft.Icons.WIFI,
            width=200,
            on_change=lambda e: self.controller.model.set_hotspot_credentials(
                e.control.value, self.hotspot_password_field.value
            ),
        )

        self.hotspot_password_field = ft.TextField(
            label="Mot de passe hotspot",
            value=self.controller.model.hotspot_password,
            prefix_icon=ft.Icons.LOCK_OUTLINE,
            password=True,
            can_reveal_password=True,
            width=200,
            helper="Minimum 8 caractères (WPA2)",
            on_change=lambda e: self.controller.model.set_hotspot_credentials(
                self.hotspot_ssid_field.value, e.control.value
            ),
        )

        self.hotspot_button = ft.Button(
            content="Créer un hotspot Wi-Fi",
            icon=ft.Icons.WIFI_TETHERING,
            on_click=self.controller.toggle_hotspot,
        )

        self.password_protect_control_chip = ft.Chip(
                label=ft.Text("Protéger le partage"),
                on_click=self.toggle_password_visibility,
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
            self.start_button,
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
        )


        # Hotspot card. Independant from control card
        self.hotspot_controls_content = ft.Column([
            ft.Text("Connectivité avancée", weight=ft.FontWeight.BOLD, size=13),
            self.hotspot_ssid_field,
            self.hotspot_password_field,
            self.hotspot_button,
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
            height=280,
            margin=ft.margin.only(left=20, right=20, top=20, bottom=0),
            elevation=10,
            expand=True
        )

        self.hotspot_card = ft.Card(
            content=ft.Container(
                content=self.hotspot_controls_content,
                alignment=ft.Alignment.CENTER,
                ink=True,
                padding=20
            ),
            height=220,
            margin=ft.margin.only(left=20, right=20, top=8, bottom=20),
            elevation=10,
            expand=True
        )

        self.left_column = ft.Column(
            [self.toggle_card, self.hotspot_card],
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
        
        self.page.add(self.main_row)

        # netsh is windows only, hide card if not on windows.
        if sys.platform != "win32":
            self.hotspot_card.visible = False
            self.page.update()
    
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

    def toggle_context_menu(self, e):
        self.controller.toggle_context_menu()
        e.control.selected = self.controller.model.data.context_menu_enabled
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
        self.toggle_card.disabled = False  # ne jamais disabled la card entière
        self.page.update()
    
    # Replace controls with QR code for the card content
    def show_qr_code(self, qr_data, url_text):
        self._primary_url = url_text
        self._secondary_url = ""
        self.stop_button_qr.visible = True

        self.toggle_card.content.content = ft.Column(
            [
                ft.Container(self.stop_button_qr, alignment=ft.Alignment.CENTER, padding=8),
                ft.Divider(height=1),
                self._make_qr_expansion_tile("Réseau local", qr_data, url_text),
            ],
            spacing=0,
        )
        self.page.update()
    
    def show_dual_qr(self, local_qr, local_url, ts_qr, ts_url):
        self._primary_url = local_url
        self._secondary_url = ts_url
        self.stop_button_qr.visible = True

        self.toggle_card.content.content = ft.Column(
            [
                ft.Container(self.stop_button_qr, alignment=ft.Alignment.CENTER, padding=8),
                ft.Divider(height=1),
                self._make_qr_expansion_tile("Réseau local", local_qr, local_url),
                self._make_qr_expansion_tile("Tailscale", ts_qr, ts_url),
            ],
            spacing=0,
        )
        self.page.update()
    # replace QR code with controls for the card content
    def show_controls(self):
        self.toggle_card.content.content = self.controls_content
        self.hotspot_card.content.content = self.hotspot_controls_content
        self.stop_button_qr.visible = False
        self.start_button.visible = bool(self.controller.model.selected_path)
        self._primary_url = ""
        self._secondary_url = ""
        self.page.update()
    
    # Update hotspot creation button based on hotspot status
    def update_hotspot_button(self, is_running):
        if is_running:
            self.hotspot_button.text = "Arrêter le point d'accès"
            self.hotspot_button.icon = ft.Icons.WIFI_TETHERING_OFF
            self.hotspot_button.style = ft.ButtonStyle(
                bgcolor={ft.ControlState.DEFAULT: ft.Colors.RED_400},
                color={ft.ControlState.DEFAULT: ft.Colors.WHITE},
            )
        else:
            self.hotspot_button.text = "Créer un point d'accès Wi-Fi"
            self.hotspot_button.icon = ft.Icons.WIFI_TETHERING
            self.hotspot_button.style = None
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
