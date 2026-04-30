"""
test_new_features.py

Author:  Nathan Filipowitz
Date:    2026-04-29
Purpose: Unit tests for TPI new features:
         TU-04 — Persistent logging (messages written to sharepp.log with correct level)
         TU-06 — Hotspot password validation (short password rejected before any system call)
"""

import pytest
from unittest.mock import patch
from models.model import Model


# AI HELP: Gemini helped with the creation of this function, so tests can be executed 
# Shared helper — mirrors the browser_mock pattern from test_controller.py.
# Redirects all paths to tmp_path and clears stale global logger handlers
# so each test gets a fresh file handler pointing to its own tmp directory.
def make_model(tmp_path):
    model = Model(config_name="test_settings.json")
    model.config_dir = tmp_path
    model.config_path = tmp_path / "test_settings.json"
    model.log_path = tmp_path / "sharepp.log"
    model.file_logger.handlers.clear()
    model._setup_file_logger()
    return model


# TU-04 : Persistent logging
def test_tu04_persistent_logging(tmp_path):
    # Arrange
    model = make_model(tmp_path)

    # Act
    model.log_to_file("serveur démarré", "info")
    model.log_to_file("protection activée", "warning")
    model.log_to_file("connexion échouée", "error")
    model.log_to_file("fichier téléchargé", "success")

    # Assert
    content = model.log_path.read_text(encoding="utf-8")
    assert "[INFO]" in content       # info and success both map to [INFO] in the logs
    assert "[WARNING]" in content
    assert "[ERROR]" in content
    assert "serveur démarré" in content


# TU-05 : Hotspot password validation
# Arrange execute_command to later check if it was called
@patch("controllers.hotspot_controller.execute_command")
def test_tu06_short_password_rejected(mock_exec):
    # Arrange
    from controllers.hotspot_controller import setup_and_start

    # Act & Assert
    # Passwords under 8 chars must be refused without any system call
    assert setup_and_start("SharePlusPlus", "")[0] is False
    assert setup_and_start("Sharepp", "1234")[0] is False
    assert setup_and_start("Sharepp", "1234567")[0] is False
    mock_exec.assert_not_called()


# AI USE: Gemini taught me the @patch syntax and guided me to try to see if a function
# that was only supposed to be called on success was really called, method used in this test
# Patch 1: mock_exec, to check that execute_command was called
# Patch 2: mock_platform to windows so tests also pass on Linux
@patch("controllers.hotspot_controller.execute_command", return_value=(True, "OK"))
@patch("platform.system", return_value="Windows")
def test_tu06_valid_password_accepted(mock_platform, mock_exec):
    # Arrange
    from controllers.hotspot_controller import setup_and_start

    # Act 
    setup_and_start("MonSSID", "12345678")

    # Assert
    assert mock_exec.call_count >= 1