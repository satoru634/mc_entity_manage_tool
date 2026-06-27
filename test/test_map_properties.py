import math
from unittest.mock import mock_open, patch

import pytest

from modules.map_properties import MapProperties

SAMPLE_JS = """
UnminedMap = {
    minZoom: -3,
    maxZoom: 2,
    minRegionX: -2,
    minRegionZ: -1,
    maxRegionX: 3,
    maxRegionZ: 4,
}
"""


def _make_properties(js_content=SAMPLE_JS, input_path="/fake/path"):
    mp = MapProperties(input_path)
    with patch("builtins.open", mock_open(read_data=js_content)):
        mp.get()
    return mp


class TestMapPropertiesBasicParsing:
    def test_min_zoom_parsed(self):
        mp = _make_properties()
        assert mp.min_zoom == -3

    def test_max_zoom_parsed(self):
        mp = _make_properties()
        assert mp.max_zoom == 2

    def test_min_region_x_parsed(self):
        mp = _make_properties()
        assert mp.min_region_x == -2

    def test_min_region_z_parsed(self):
        mp = _make_properties()
        assert mp.min_region_z == -1

    def test_max_region_x_parsed(self):
        mp = _make_properties()
        assert mp.max_region_x == 3

    def test_max_region_z_parsed(self):
        mp = _make_properties()
        assert mp.max_region_z == 4


class TestMapPropertiesWorldDimensions:
    def test_world_min_x(self):
        mp = _make_properties()
        # min_region_x=-2 → -2 * 512 = -1024
        assert mp.world_min_x == -2 * 512

    def test_world_min_y(self):
        mp = _make_properties()
        # min_region_z=-1 → -1 * 512 = -512
        assert mp.world_min_y == -1 * 512

    def test_world_width(self):
        mp = _make_properties()
        # (max_region_x+1 - min_region_x) * 512 = (3+1-(-2)) * 512 = 6 * 512
        expected = (3 + 1 - (-2)) * 512
        assert mp.world_width == expected

    def test_world_height(self):
        mp = _make_properties()
        # (max_region_z+1 - min_region_z) * 512 = (4+1-(-1)) * 512 = 6 * 512
        expected = (4 + 1 - (-1)) * 512
        assert mp.world_height == expected

    def test_world_max_zoom_factor(self):
        mp = _make_properties()
        # 2 ** max_zoom = 2 ** 2 = 4
        assert mp.world_max_zoom_factor == 4

    def test_map_zoom_levels(self):
        mp = _make_properties()
        # max_zoom - min_zoom = 2 - (-3) = 5
        assert mp.map_zoom_levels == 5


class TestMapPropertiesZoomInfoList:
    def test_zoom_info_list_has_correct_number_of_entries(self):
        mp = _make_properties()
        # map_zoom_levels + 1 = 6
        assert len(mp.zoom_info_list) == 6

    def test_zoom_info_list_keys(self):
        mp = _make_properties()
        # min_zoom=-3 to max_zoom=2
        expected_keys = set(range(-3, 3))
        assert set(mp.zoom_info_list.keys()) == expected_keys

    def test_zoom_info_has_required_fields(self):
        mp = _make_properties()
        for zoom, info in mp.zoom_info_list.items():
            assert "resolutions" in info
            assert "world_zoom_factor" in info
            assert "min_tile_x" in info
            assert "min_tile_y" in info
            assert "max_tile_x" in info
            assert "max_tile_y" in info

    def test_world_zoom_factor_at_min_zoom(self):
        mp = _make_properties()
        # min_zoom=-3, world_zoom_factor = 2**(-3)
        assert mp.zoom_info_list[-3]["world_zoom_factor"] == 2 ** (-3)

    def test_world_zoom_factor_at_max_zoom(self):
        mp = _make_properties()
        # max_zoom=2, world_zoom_factor = 2**2 = 4
        assert mp.zoom_info_list[2]["world_zoom_factor"] == 4

    def test_tile_ranges_are_integers(self):
        mp = _make_properties()
        for zoom, info in mp.zoom_info_list.items():
            assert isinstance(info["min_tile_x"], int)
            assert isinstance(info["min_tile_y"], int)
            assert isinstance(info["max_tile_x"], int)
            assert isinstance(info["max_tile_y"], int)

    def test_tile_min_le_max(self):
        mp = _make_properties()
        for zoom, info in mp.zoom_info_list.items():
            assert info["min_tile_x"] <= info["max_tile_x"]
            assert info["min_tile_y"] <= info["max_tile_y"]


class TestMapPropertiesAllPositive:
    """全値が正の場合のパターン網羅テスト"""

    ALL_POSITIVE_JS = """
    UnminedMap = {
        minZoom: 0,
        maxZoom: 3,
        minRegionX: 0,
        minRegionZ: 0,
        maxRegionX: 5,
        maxRegionZ: 5,
    }
    """

    def test_all_positive_parsing(self):
        mp = _make_properties(self.ALL_POSITIVE_JS)
        assert mp.min_zoom == 0
        assert mp.max_zoom == 3
        assert mp.min_region_x == 0
        assert mp.min_region_z == 0
        assert mp.max_region_x == 5
        assert mp.max_region_z == 5

    def test_all_positive_world_min_x_is_zero(self):
        mp = _make_properties(self.ALL_POSITIVE_JS)
        assert mp.world_min_x == 0
        assert mp.world_min_y == 0
