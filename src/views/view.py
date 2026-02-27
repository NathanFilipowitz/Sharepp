"""
view.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handle frontend/User Interface for the application

"""


import flet as ft

class View:
    def __init__(self, page: ft.Page, controller):
        self.page = page
        self.controller = controller
        
        self.file_picker = ft.FilePicker()
        
        self.result_text = ft.Text("Aucun dossier n'a encore été sélectionné", selectable=True)
        
        self.page.add(
            ft.Row([
                # ft.Button("Pick File", on_click=self.controller.pick_file),
                ft.Button("Pick Folder", on_click=self.controller.pick_folder),
            ]),
            ft.Text("Selected path:", weight=ft.FontWeight.BOLD),
            self.result_text
        )
        
        # Logs panel (right side)
        self.logs_column = ft.Column(
            [
                ft.Text("192.168.1.56 connecté 2026-03-31 16:34:01", size=12, color=ft.Colors.GREEN),
                ft.Text("192.168.1.56 started download of exemple.txt 2026-03-31 16:34:07", size=12),
                ft.Text("192.168.1.56 disconnected 2026-03-31 16:36:37", size=12, color=ft.Colors.RED),
            ],
            scroll=ft.ScrollMode.AUTO,
            expand=True,
        )
        
        self.logs_container = ft.Container(
            content=self.logs_column,
            width=300,
            bgcolor=ft.Colors.WHITE,
            border_radius=10,
            padding=10,
            shadow=ft.BoxShadow(blur_radius=5, color=ft.Colors.BLACK12),
            visible=True,
        )
        
        # Left side content
        self.path_text = ft.Text("/HOME/USER/FOLDER", weight=ft.FontWeight.BOLD, size=16)
        
        # AppBar
        self.page.appbar = ft.AppBar(
            leading=ft.Text("Share++", size=20, weight=ft.FontWeight.BOLD, color=ft.Colors.WHITE),
            leading_width=100,
            title=ft.Text(
                "SÉLECTIONNER UN DOSSIER POUR DÉMARRER UN PARTAGE",
                size=14,
                weight=ft.FontWeight.W_500,
                color=ft.Colors.WHITE,
            ),
            center_title=True,
            bgcolor=ft.Colors.BLUE_200,
            actions=[
                ft.IconButton(
                    icon=ft.Icons.CHAT_BUBBLE,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Logs",
                    on_click=self.controller.toggle_logs,
                ),
                ft.IconButton(
                    icon=ft.Icons.SETTINGS,
                    icon_color=ft.Colors.WHITE,
                    tooltip="Paramètres",
                    on_click=self.controller.open_settings,
                ),
            ],
        )
        
        # Main layout row (left + right)
        self.main_row = ft.Row(
            [
                # self.left_content,
                self.logs_container,
            ],
            expand=True,
            spacing=20,
        )
        
        self.page.add(self.main_row)
        self.page.bgcolor = ft.Colors.WHITE
    
    def update_path(self, path):
        self.path_text.value = path.upper()
        self.page.update()
    
    def toggle_logs_visibility(self):
        self.logs_container.visible = not self.logs_container.visible
        self.page.update()
    
    def show_settings(self):
        self.page.dialog = self.settings_dialog
        self.settings_dialog.open = True
        self.page.update()
    
    def close_settings_dialog(self):
        self.settings_dialog.open = False
        self.page.update()
    
    def update_result(self, text):
        self.result_text.value = text
        self.page.update()