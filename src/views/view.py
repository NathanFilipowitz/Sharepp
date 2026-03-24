"""
view.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handle frontend/User Interface for the application

"""


import flet as ft
import datetime

class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        
        self.file_picker = ft.FilePicker()

        self.pick_button = ft.ElevatedButton("Ouvrir un dossier", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_folder)
        
        self.result_text = ft.Text(
            "Aucun dossier n'a encore été sélectionné",
            selectable=True,
            italic=True,
            overflow=ft.TextOverflow.CLIP
        )

        # Start/Stop Server icon initially hidden
        self.start_icon = ft.IconButton(
            icon=ft.Icons.PLAY_ARROW_ROUNDED,
            icon_color=ft.Colors.WHITE,
            visible=False, 
            on_click=self.controller.start_server,
        )
        self.stop_icon = ft.IconButton(
            icon=ft.Icons.STOP_ROUNDED,
            icon_color=ft.Colors.WHITE,
            visible=False,
            on_click=self.controller.stop_server,
        )
        
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
        self.path_text = ft.Text("/HOME/USER/FOLDER", weight=ft.FontWeight.BOLD, size=16)
        
        # AppBar
        self.appbar_title = ft.Text(
            "SÉLECTIONNER UN DOSSIER POUR DÉMARRER UN PARTAGE",
            size=14,
            weight=ft.FontWeight.W_500,
            color=ft.Colors.WHITE,
        )
        
        self.page.appbar = ft.AppBar(
            leading=ft.Image(src="icons/app_icon.svg", color=ft.Colors.BLUE_200),
            leading_width=100,
            title=self.appbar_title,
            center_title=True,
            bgcolor=ft.Colors.BLUE_200,
            actions=[
                self.start_icon,
                self.stop_icon,
                ft.IconButton(
                    icon=ft.Icons.CHAT_OUTLINED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Afficher les logs",
                    on_click=self.controller.toggle_logs,
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem(
                            content="Remember Last Path", 
                            checked=self.controller.model.data["remember_path"],
                            on_click=self.controller.toggle_remember_path
                        ),
                        ft.PopupMenuItem("Clear Saved Path", on_click=self.controller.clear_path),
                        ft.PopupMenuItem(
                            content=ft.Text("Add to Context Menu"),
                            checked=self.controller.model.data.get("context_menu_enabled", False),
                            on_click=self.controller.toggle_context_menu
                        ),
                        ft.PopupMenuItem(
                            content="Clear l'adresse",
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
            )
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER
        )

        # QR code content, starts hidden
        self.qr_image = ft.Image(
            src=None,
            width=250,
            height=250,
            fit=ft.BoxFit.CONTAIN
        )
        self.qr_url_text = ft.Text(
            "",
            size=12,
            text_align=ft.TextAlign.CENTER,
            selectable=True
        )
        self.qr_content = ft.Column([
            ft.Text("Scan to download", weight=ft.FontWeight.BOLD, size=16),
            self.qr_image,
            self.qr_url_text
        ],
        spacing=10,
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
        )

        # Main functionnalities Card (left column)
        self.toggle_card = ft.Card(
            content=ft.Container(
                content=self.controls_content,
                alignment=ft.Alignment.CENTER,
                ink=True,
                padding=20
            ),
            height=400,
            margin=20,
            elevation=10,
            expand=True
        )
        
        # Main layout row
        self.main_row = ft.Row(
            [
                self.toggle_card,
                self.logs_container,
            ],
            expand=True,
            spacing=20,
        )
        
        self.page.add(self.main_row)
    
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
        
        log_text = ft.Text(f"[{timestamp}] {message}", size=12, color=log_color)
        self.logs_column.controls.append(log_text)
        self.page.update()
    
    def toggle_logs_visibility(self):
        self.logs_container.visible = not self.logs_container.visible
        self.page.update()
    
    # turns the password TextField widget visible and gives a pressed look to the chip when enabled
    def toggle_password_visibility(self, e):
        self.password_entry.visible = not self.password_entry.visible
        e.control.selected = self.password_entry.visible
        self.controller.toggle_protection() 
        self.page.update()

    def toggle_context_menu(self, e):
        self.controller.model.toggle_context_menu()
        e.control.selected = self.controller.model.data.context_menu_enabled
        self.page.update()

    # Updates title and shows/hides server icons if a path was selected
    def update_ui_for_path(self, path, is_running=False):
        if path:
            self.appbar_title.value = f"Path: {path}"
            self.result_text.value = path
            self.start_icon.visible = not is_running
            self.stop_icon.visible = is_running
            self.pick_button.icon = ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED
        else:
            self.appbar_title.value = "SÉLECTIONNER UN DOSSIER"
            self.start_icon.visible = False
            self.stop_icon.visible = False
        self.page.update()

    # Toggle the icons between start and stop, and turns the left Card unavailable whenever the server is started.
    def update_server_status(self, running):
        self.start_icon.visible = not running
        self.stop_icon.visible = running
        self.toggle_card.disabled = running
        self.page.update()
    
    # Replace controls with QR code for the card content
    def show_qr_code(self, qr_data_url, url_text):
        self.qr_image.src = qr_data_url
        self.qr_url_text.value = url_text
        self.toggle_card.content.content = self.qr_content
        self.page.update()
    
    # replace QR code with controls for the card content
    def show_controls(self):
        self.toggle_card.content.content = self.controls_content
        self.qr_image.src = None
        self.page.update()