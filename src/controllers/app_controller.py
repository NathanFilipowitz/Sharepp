"""
app_controller.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles application business logic

"""

from models.model import Model
from views.view import View
import flet as ft

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