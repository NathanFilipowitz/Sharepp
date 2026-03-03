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
        
        self.result_text = ft.Text(
            "Aucun dossier n'a encore été sélectionné",
            selectable=True,
            italic=True,
            overflow=ft.TextOverflow.CLIP
        )
        
        self.btn_start = ft.Button("Démarrer le partage", on_click=self.controller.start_server, bgcolor=ft.Colors.GREEN, color=ft.Colors.WHITE)
        self.btn_stop = ft.Button("Arrêter le partage", on_click=self.controller.stop_server, bgcolor=ft.Colors.RED, color=ft.Colors.WHITE, disabled=True)
        
        # Logs panel (right side)
        self.logs_column = ft.Column(
            [],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.logs_container = ft.Container(
            content=self.logs_column,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=10,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
            visible=True,
            expand=True,
            margin=20
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
                ft.IconButton(
                    icon=ft.Icons.PLAY_ARROW_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Lancer le partage",
                    on_click=self.controller.start_server,
                ),
                ft.IconButton(
                    icon=ft.Icons.STOP_ROUNDED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Fermer le partage",
                    on_click=self.controller.stop_server,
                ),
                ft.IconButton(
                    icon=ft.Icons.CHAT_OUTLINED,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Afficher les logs",
                    on_click=self.controller.toggle_logs,
                ),
                ft.PopupMenuButton(
                    items=[
                        ft.PopupMenuItem("About"),
                        ft.PopupMenuItem(),  # divider
                        ft.PopupMenuItem(
                            content="J'aime le CPNV",
                            checked=False,
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

        self.toggle_card = ft.Card(
            shadow_color=ft.Colors.ON_SURFACE_VARIANT,
            content=ft.Container(
                content=ft.Column([
                    ft.ElevatedButton("Pick Folder", icon=ft.Icons.FOLDER_OPEN, on_click=self.controller.pick_folder),
                    # self.btn_start,
                    # self.btn_stop,
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
        # self.page.bgcolor = ft.Colors.WHITE
    
    def add_log_entry(self, message, level):
        color_map = {
            "success": ft.Colors.GREEN,
            "warning": ft.Colors.ORANGE,
            "error": ft.Colors.RED,
            "info": ft.Colors.BLACK,
        }
        log_color = color_map.get(level, ft.Colors.BLACK)

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        log_text = ft.Text(f"[{timestamp}] {message}", size=12, color=log_color)
        self.logs_column.controls.append(log_text)
        self.page.update()
    
    def toggle_logs_visibility(self):
        self.logs_container.visible = not self.logs_container.visible
        self.page.update()
    
    # rend le widget TextField visible et donne un aspect appuyé au chip lorsque l'entrée mdp est affichée
    def toggle_password_visibility(self, e):
        self.password_entry.visible = not self.password_entry.visible
        e.control.selected = self.password_entry.visible
        self.page.update()
    
    def update_result(self, text):
        self.result_text.value = text
        self.page.update()

    def update_server_status(self, running):
        self.btn_start.disabled = running
        self.btn_stop.disabled = not running
        self.page.update()