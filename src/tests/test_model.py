"""
test_model.py

Author:  Nathan Filipowitz
Date:    2026-03-09
Purpose: Unit tests testing various app's Model methods

"""

import os
import pytest
from models.model import Model

# Tests settings application on app opening, and settings file creation if missing.
def test_tu01_model_initialization(tmp_path):
    # Arrange
    config_file = tmp_path / "test_settings.json"
    model = Model(config_name="test_settings.json")
    model.config_dir = tmp_path
    model.config_path = config_file

    # Act
    model.save_settings()

    # Assert
    assert model.data["port"] == 8080
    assert os.path.exists(config_file)


def test_tu02_password_hashing(tmp_path):
    # Arrange
    model = Model(config_name="test_settings.json")
    model.config_dir = tmp_path
    model.config_path = tmp_path / "test_temp_pwd.json"
    password = "reallyGoodPassword"

    # Act
    model.set_password(password)

    # Assert
    # pw not in clear, was hashed correctly
    assert model.data["password"] != password
    # wrong pw check
    assert model.check_password(password) is True
    assert model.check_password("falsePassword") is False