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
            leading=ft.Text("Share++", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
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

        # Main functionnalities Card (left column)
        self.toggle_card = ft.Card(
            content=ft.Container(
                content=ft.Column([
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
                ),
                alignment=ft.Alignment.CENTER,
                ink=True,
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

    # Updates title and shows/hides server icons if a path was selected
    def update_ui_for_path(self, path, is_running=False):
        if path:
            self.appbar_title.value = f"Path: {path}"
            self.result_text.value = path
            self.start_icon.visible = not is_running
            self.stop_icon.visible = is_running
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