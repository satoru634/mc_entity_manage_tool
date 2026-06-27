import json
import pathlib
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

import mc_entity_manage_tool
from mc_entity_manage_tool import _load_config


class TestLoadConfig:
    def test_valid_json_file(self, tmp_path):
        config = {"input_base_path": "/world", "output_path": "/out"}
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config), encoding="utf-8")
        result = _load_config(str(config_file))
        assert result == config

    def test_non_json_extension_exits(self, tmp_path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("key: value")
        with pytest.raises(SystemExit) as exc_info:
            _load_config(str(config_file))
        assert exc_info.value.code == 1

    def test_txt_extension_exits(self, tmp_path):
        config_file = tmp_path / "config.txt"
        config_file.write_text("{}")
        with pytest.raises(SystemExit):
            _load_config(str(config_file))

    def test_uppercase_json_extension_is_accepted(self, tmp_path):
        config = {"key": "value"}
        config_file = tmp_path / "config.JSON"
        config_file.write_text(json.dumps(config), encoding="utf-8")
        result = _load_config(str(config_file))
        assert result == config

    def test_file_not_found_raises(self, tmp_path):
        missing_path = str(tmp_path / "nonexistent.json")
        with pytest.raises(FileNotFoundError):
            _load_config(missing_path)

    def test_invalid_json_raises(self, tmp_path):
        config_file = tmp_path / "bad.json"
        config_file.write_text("this is not json", encoding="utf-8")
        with pytest.raises(json.JSONDecodeError):
            _load_config(str(config_file))

    def test_empty_json_object(self, tmp_path):
        config_file = tmp_path / "empty.json"
        config_file.write_text("{}", encoding="utf-8")
        result = _load_config(str(config_file))
        assert result == {}

    def test_nested_json(self, tmp_path):
        config = {"level1": {"level2": [1, 2, 3]}}
        config_file = tmp_path / "nested.json"
        config_file.write_text(json.dumps(config), encoding="utf-8")
        result = _load_config(str(config_file))
        assert result["level1"]["level2"] == [1, 2, 3]


class TestMain:
    def test_main_calls_get_info(self, tmp_path):
        config = {
            "input_base_path": str(tmp_path),
            "unmined_path": str(tmp_path),
            "target_village_name": "テスト村",
            "output_path": str(tmp_path),
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config), encoding="utf-8")

        mock_info = MagicMock()
        with patch("mc_entity_manage_tool.VillagerInfo", return_value=mock_info), patch(
            "sys.argv", ["mc_entity_manage_tool.py", "-c", str(config_file)]
        ):
            mc_entity_manage_tool.main()

        mock_info.get_info.assert_called_once()

    def test_main_default_config(self, tmp_path):
        config = {
            "input_base_path": str(tmp_path),
            "unmined_path": str(tmp_path),
            "target_village_name": "村",
            "output_path": str(tmp_path),
        }
        config_file = tmp_path / "config.json"
        config_file.write_text(json.dumps(config), encoding="utf-8")

        mock_info = MagicMock()
        with patch("mc_entity_manage_tool.VillagerInfo", return_value=mock_info), patch(
            "sys.argv", ["mc_entity_manage_tool.py"]
        ), patch("mc_entity_manage_tool._load_config", return_value=config):
            mc_entity_manage_tool.main()

        mock_info.get_info.assert_called_once()
