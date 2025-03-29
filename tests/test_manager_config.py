# -*- coding: utf-8 -*-

import pytest
from unittest.mock import mock_open
from src.managers.configManager import ConfigManager


# General mocks, builders and fixtures


@pytest.fixture
def default_config():
    return "key1: value1\ngroup:\n  subkey: subvalue"


@pytest.fixture
def custom_config():
    return "key1: custom_value\ngroup:\n  subkey: custom_subvalue"


def test_load_default_config(mocker, default_config):
    """Tests that config.yaml is loaded when custom.yaml does not exist"""
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("builtins.open", mock_open(read_data=default_config))

    config_manager = ConfigManager()

    assert config_manager.getConfigValue("key1") == "value1"
    assert config_manager.getCurrentFilePath().endswith("config.yaml")


def test_load_custom_config(mocker, custom_config):
    """Tests that custom.yaml is loaded when it exists"""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data=custom_config))

    config_manager = ConfigManager()

    assert config_manager.getConfigValue("key1") == "custom_value"
    assert config_manager.getCurrentFilePath().endswith("custom.yaml")


def test_get_config_value(mocker, default_config):
    """Tests retrieving values from config.yaml"""
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("builtins.open", mock_open(read_data=default_config))

    config_manager = ConfigManager()

    assert config_manager.getConfigValue("key1") == "value1"
    assert config_manager.getConfigValue("group.subkey", "default") == "subvalue"
    assert config_manager.getConfigValue("nonexistent.key", "default") == "default"


def test_set_config_value(mocker, default_config):
    """Tests sending values to config.yaml"""
    mocker.patch("os.path.exists", return_value=False)
    mocker.patch("builtins.open", mock_open(read_data=default_config))

    config_manager = ConfigManager()

    config_manager.setConfigValue("key1", "newvalue1")
    config_manager.setConfigValue("group.subkey", "newgroupvalue")

    assert config_manager.getConfigValue("key1") == "newvalue1"
    assert config_manager.getConfigValue("group.subkey") == "newgroupvalue"


def test_is_custom_config(mocker, custom_config):
    """Tests whether the use of custom.yaml is correctly detected"""
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("builtins.open", mock_open(read_data=custom_config))

    config_manager = ConfigManager()

    assert config_manager.isCustomConfig()


def test_update_custom_config(mocker, custom_config):
    """Tests updating the custom.yaml configuration using a file-like object"""
    mocker.patch("os.path.exists", return_value=True)
    mock_open_obj = mock_open()
    mocker.patch("builtins.open", mock_open_obj)

    config_manager = ConfigManager()

    # Simulate a file upload (streamlit_file_uploader is expected to be a file-like object)
    file_mock = mock_open(read_data=custom_config).return_value

    config_manager.updateCustomConfig(file_mock)

    # Ensure the config dictionary is updated correctly
    assert config_manager.getConfigValue("key1") == "custom_value"
    assert config_manager.getConfigValue("group.subkey") == "custom_subvalue"

    # Verify that saveConfig() was called, meaning the file was written
    mock_open_obj.assert_called_with(config_manager.getCurrentFilePath(), "w")
