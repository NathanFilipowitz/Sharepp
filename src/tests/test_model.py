"""
test_model.py

Author:  Nathan Filipowitz
Date:    2026-03-09
Purpose: Unit tests testing various app's Model methods

"""

import os
import json
import pytest
from models.model import Model

# Tests settings application on app opening, and settings file creation if missing.
def test_model_initialization(tmp_path):
    config_file = tmp_path / "test_settings.json"
    model = Model(config_path=str(config_file))
    model.save_settings()
    
    assert model.data["port"] == 8080
    assert os.path.exists(config_file)

# Tests password hashing from mock settings
def test_password_hashing():
    model = Model(config_path="test_temp.json")
    password = "reallyGoodPassword"
    model.set_password(password)
    
    # pw not in clear, was hashed correctly, doesn't work with another pw
    assert model.data["password"] != password
    assert model.check_password(password) is True
    assert model.check_password("falsePassword") is False
    
    # we remove the file created for the test
    if os.path.exists("test_temp.json"):
        os.remove("test_temp.json")

# Tests qrcode generation and base64 encoding from url
def test_qr_generation():
    model = Model(config_path="test_temp.json")
    qr_url = model.generate_qr_data_url("192.168.1.10")
    
    # just check if image was created
    assert qr_url.startswith("data:image/png;base64,")
    
    if os.path.exists("test_temp.json"):
        os.remove("test_temp.json")