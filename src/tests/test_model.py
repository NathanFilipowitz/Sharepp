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

