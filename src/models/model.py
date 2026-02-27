"""
model.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles Key-Value Database for the app, and methods to interact with it.

"""

class Model:
    def __init__(self):
        self.selected_path = None
        self.is_protected = False
        self.password = ""
        self.logs_visible = True
    
    def set_path(self, path):
        self.selected_path = path
    
    def toggle_protection(self):
        self.is_protected = not self.is_protected
    
    def set_password(self, pwd):
        self.password = pwd
    
    def toggle_logs(self):
        self.logs_visible = not self.logs_visible