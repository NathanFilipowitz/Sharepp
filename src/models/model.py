"""
model.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles json database for the app, and methods to interact with it for the controller.

"""
import json
import os

class Model:
    def __init__(self, config_path="settings.json"):
        self.config_path = config_path

        # Temporary data
        self.server_running = False
        self.server_runner = None

        # Saved data (initialization)
        self.data = {
            "selected_path": "",
            "port": 8080,
            "is_protected": False,
            "password": "",
            "logs_visible": True,
            "qr_enabled": True
        }
        # Apply saved data
        self.load_settings()
    
    # Load settings from settings.json if it exists
    def load_settings(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, "r") as file:
                self.data.update(json.load(file))
                
    # Write settings to json
    def save_settings(self):
        with open(self.config_path, "w") as f:
            json.dump(self.data, f, indent=4)

    # Get
    @property
    def selected_path(self): 
        return self.data["selected_path"]
    
    @property
    def port(self): 
        return self.data["port"]

    @property
    def qr_enabled(self): 
        return self.data["qr_enabled"]

    # Set
    def set_path(self, path):
        self.data["selected_path"] = path
        self.save_settings()
    
    def set_port(self, port):
        self.data["port"] = int(port)
        self.save_settings()
    
    def set_password(self, pwd):
        if not pwd: # Delete password in database if the user removed it in the app
            self.data["password"] = ""
        else:
            hashed_pwd = hashlib.sha256(pwd.encode()).hexdigest()
            self.data["password"] = hashed_pwd
        self.save_settings()
    
    def toggle_protection(self):
        self.data["is_protected"] = not self.data["is_protected"]
        self.save_settings()
    
    def toggle_qr(self):
        self.data["qr_enabled"] = not self.data["qr_enabled"]
        self.save_settings()
    
    def toggle_logs(self):
        self.data["logs_visible"] = not self.data["logs_visible"]
        self.save_settings()
    

    def check_password(self, input_pwd):
        if not self.data["password"]:
            return True
            
        input_hash = hashlib.sha256(input_pwd.encode()).hexdigest()
        return input_hash == self.data["password"]