"""
model.py

Author:  Nathan Filipowitz
Date:    2026-02-25
Purpose: Handles json database for the app, and methods to interact with it for the controller.

"""
import hashlib
import json
import os
import logging
from pathlib import Path

class Model:
    def __init__(self, config_name="settings.json"):
        # Path.home is cross-platform
        # Windows
        if os.name == "nt":
            # AI Modification to find config path after system installation
            base_path = Path(os.getenv('APPDATA', Path.home()))
        else:
            base_path = Path.home() / ".config"

        self.config_dir = base_path / "SharePlusPlus"
        # create folder if not exists
        self.config_dir.mkdir(parents=True, exist_ok=True)

        self.config_path = self.config_dir / config_name

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
            "qr_enabled": True,
            "remember_path": True,
            "copy_to_clipboard": False,
            "context_menu_enabled": False,
            "hotspot_ssid": "SharePlusPlus",
            "hotspot_password": "sharepp1",
        }
        # Apply saved data
        self.load_settings()

        # Persistent log file path
        self.log_path = self.config_dir / "sharepp.log"
        self._setup_file_logger()
    
    def _setup_file_logger(self):
        # Identify log file (create if not exists)
        self.file_logger = logging.getLogger("sharepp")
        # Accept logs of all severity levels (DEBUG == lowest priority)
        self.file_logger.setLevel(logging.DEBUG)
        
        if not self.file_logger.handlers:
            handler = RotatingFileHandler(
                self.log_path, maxBytes=1_000_000, backupCount=3, encoding="utf-8"
            )
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            self.file_logger.addHandler(handler)
    
    def log_to_file(self, message: str, level: str):
        level_map = {
            "success": logging.INFO,
            "info":    logging.INFO,
            "warning": logging.WARNING,
            "error":   logging.ERROR,
        }
        self.file_logger.log(level_map.get(level, logging.INFO), message)

    # Load settings from settings.json
    def load_settings(self):
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as file:
                    self.data.update(json.load(file))
            except Exception as e:
                print(f"Erreur lors du chargement des paramètres: {e}")

        # Reset protection on every app launch
        self.data["is_protected"] = False
                
    # Write settings to json
    def save_settings(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as file:
                json.dump(self.data, file, indent=4)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde: {e}")
    

    def toggle_remember_path(self):
        self.data["remember_path"] = not self.data["remember_path"]
        if not self.data["remember_path"]:
            self.data["selected_path"] = "" # Clear saved path
        self.save_settings()

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
    
    @property
    def remember_path(self):
        return self.data["remember_path"]

    @property
    def context_menu_enabled(self):
        return self.data["context_menu_enabled"]
    
    @property
    def copy_to_clipboard(self):
        return self.data["copy_to_clipboard"]
    
    @property
    def hotspot_ssid(self):
        return self.data.get("hotspot_ssid", "SharePlusPlus")

    @property
    def hotspot_password(self):
        return self.data.get("hotspot_password", "sharepp1")

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
    
    # Update SSID and password in user settings. password validation is done in hotspot_controller.setup_and_start
    def set_hotspot_credentials(self, ssid, password):
        if ssid:
            self.data["hotspot_ssid"] = ssid
        if password:
            self.data["hotspot_password"] = password
        self.save_settings()
    
    # Togglers
    def toggle_protection(self):
        self.data["is_protected"] = not self.data["is_protected"]
        self.save_settings()
    
    def toggle_qr(self):
        self.data["qr_enabled"] = not self.data["qr_enabled"]
        self.save_settings()
    
    def toggle_logs(self):
        self.data["logs_visible"] = not self.data["logs_visible"]
        self.save_settings()
    
    def toggle_context_menu(self):
        self.data["context_menu_enabled"] = not self.data["context_menu_enabled"]
        self.save_settings()
    
    def toggle_copy_clipboard(self):
        self.data["copy_to_clipboard"] = not self.data["copy_to_clipboard"]
        self.save_settings()

    def check_password(self, input_pwd):
        if not self.data["password"]:
            return True
            
        input_hash = hashlib.sha256(input_pwd.encode()).hexdigest()
        return input_hash == self.data["password"]