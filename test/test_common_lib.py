import os
from unittest.mock import MagicMock, patch

import numpy as np
import pytest
from nbt.nbt import TAG_Compound, TAG_Int, TAG_List, TAG_String

from modules.common_lib import CommonLib
from modules.point_3d import Point3D


class TestGetAbsPath:
    def test_relative_path(self):
        result = CommonLib.get_abs_path("some/relative/path")
        assert os.path.isabs(result)

    def test_absolute_path_unchanged(self):
        abs_path = os.path.abspath("some/path")
        result = CommonLib.get_abs_path(abs_path)
        assert result == abs_path

    def test_home_dir_expansion(self):
        result = CommonLib.get_abs_path("~/test")
        assert "~" not in result
        assert os.path.isabs(result)


class TestGetBoxCenter:
    def test_basic_center(self):
        start = Point3D(0, 0, 0)
        end = Point3D(10, 10, 10)
        center = CommonLib.get_box_center(start, end)
        assert center.get_x() == 5
        assert center.get_y() == 5
        assert center.get_z() == 5

    def test_asymmetric_box(self):
        start = Point3D(0, 0, 0)
        end = Point3D(4, 6, 8)
        center = CommonLib.get_box_center(start, end)
        assert center.get_x() == 2
        assert center.get_y() == 3
        assert center.get_z() == 4

    def test_negative_coords(self):
        start = Point3D(-10, -10, -10)
        end = Point3D(10, 10, 10)
        center = CommonLib.get_box_center(start, end)
        assert center.get_x() == 0
        assert center.get_y() == 0
        assert center.get_z() == 0

    def test_same_start_end(self):
        start = Point3D(5, 5, 5)
        end = Point3D(5, 5, 5)
        center = CommonLib.get_box_center(start, end)
        assert center.get_x() == 5
        assert center.get_y() == 5
        assert center.get_z() == 5

    def test_integer_truncation(self):
        start = Point3D(0, 0, 0)
        end = Point3D(3, 3, 3)
        center = CommonLib.get_box_center(start, end)
        assert center.get_x() == 1
        assert center.get_y() == 1
        assert center.get_z() == 1


class TestConvertUuid:
    def test_known_uuid(self):
        # 0x12345678, 0x9abcdef0, 0x11223344, 0x55667788
        int_uuid = [0x12345678, 0x9ABCDEF0, 0x11223344, 0x55667788]
        result = CommonLib.convert_uuid(int_uuid)
        assert result == "12345678-9abc-def0-1122-334455667788"

    def test_uuid_format(self):
        int_uuid = [1, 2, 3, 4]
        result = CommonLib.convert_uuid(int_uuid)
        parts = result.split("-")
        assert len(parts) == 5
        assert len(parts[0]) == 8
        assert len(parts[1]) == 4
        assert len(parts[2]) == 4
        assert len(parts[3]) == 4
        assert len(parts[4]) == 12

    def test_negative_int_masked(self):
        # 負の整数は & 0xFFFFFFFF でマスクされる
        int_uuid = [-1, -1, -1, -1]
        result = CommonLib.convert_uuid(int_uuid)
        assert result == "ffffffff-ffff-ffff-ffff-ffffffffffff"

    def test_all_zeros(self):
        int_uuid = [0, 0, 0, 0]
        result = CommonLib.convert_uuid(int_uuid)
        assert result == "00000000-0000-0000-0000-000000000000"


class TestTagListToStr:
    def test_non_tag_list_returns_empty(self):
        assert CommonLib.tag_list_to_str("not a list") == ""
        assert CommonLib.tag_list_to_str(None) == ""
        assert CommonLib.tag_list_to_str(123) == ""

    def test_empty_tag_list(self):
        tag_list = TAG_List(name="test")
        result = CommonLib.tag_list_to_str(tag_list)
        assert result == "[]"

    def test_tag_list_with_compound(self):
        tag_list = TAG_List(name="items")
        compound = TAG_Compound()
        s = TAG_String(value="hello", name="key")
        compound.tags.append(s)
        tag_list.append(compound)
        result = CommonLib.tag_list_to_str(tag_list)
        assert result.startswith("[")
        assert result.endswith("]")
        assert "key:hello" in result


class TestTagCompoundToStr:
    def test_non_tag_compound_returns_empty(self):
        assert CommonLib.tag_compound_to_str("not a compound") == ""
        assert CommonLib.tag_compound_to_str(None) == ""
        assert CommonLib.tag_compound_to_str(42) == ""

    def test_empty_compound(self):
        compound = TAG_Compound()
        result = CommonLib.tag_compound_to_str(compound)
        assert result == "{}"

    def test_compound_with_string(self):
        compound = TAG_Compound()
        s = TAG_String(value="world", name="hello")
        compound.tags.append(s)
        result = CommonLib.tag_compound_to_str(compound)
        assert result == "{hello:world}"

    def test_compound_with_int(self):
        compound = TAG_Compound()
        i = TAG_Int(value=42, name="count")
        compound.tags.append(i)
        result = CommonLib.tag_compound_to_str(compound)
        assert result == "{count:42}"

    def test_nested_compound(self):
        outer = TAG_Compound(name="outer")
        inner = TAG_Compound(name="inner")
        s = TAG_String(value="val", name="key")
        inner.tags.append(s)
        outer.tags.append(inner)
        result = CommonLib.tag_compound_to_str(outer)
        assert "inner:{key:val}" in result

    def test_compound_with_list(self):
        compound = TAG_Compound()
        tag_list = TAG_List(name="items")
        compound.tags.append(tag_list)
        result = CommonLib.tag_compound_to_str(compound)
        assert "items:[]" in result

    def test_multiple_tags(self):
        compound = TAG_Compound()
        compound.tags.append(TAG_String(value="Alice", name="name"))
        compound.tags.append(TAG_Int(value=10, name="age"))
        result = CommonLib.tag_compound_to_str(compound)
        assert "name:Alice" in result
        assert "age:10" in result


class TestGetItemInfo:
    def _make_item(self, id_val, count_val, tag_compound=None):
        item = TAG_Compound()
        item.tags.append(TAG_String(value=id_val, name="id"))
        item["id"] = TAG_String(value=id_val, name="id")
        item["Count"] = TAG_Int(value=count_val, name="Count")
        if tag_compound is not None:
            item["tag"] = tag_compound
        return item

    def test_item_without_tag(self):
        item = self._make_item("minecraft:apple", 3)
        result = CommonLib.get_item_info(item)
        assert result == "minecraft:apple = 3"

    def test_item_with_tag(self):
        tag = TAG_Compound(name="tag")
        tag.tags.append(TAG_String(value="Sword", name="display"))
        item = self._make_item("minecraft:iron_sword", 1, tag)
        result = CommonLib.get_item_info(item)
        assert result.startswith("minecraft:iron_sword")
        assert "= 1" in result
        assert "display:Sword" in result


class TestGetWorldChunk:
    def test_basic(self):
        assert CommonLib.get_world_chunk(0, 0) == 0
        assert CommonLib.get_world_chunk(1, 0) == 32
        assert CommonLib.get_world_chunk(0, 15) == 15
        assert CommonLib.get_world_chunk(1, 15) == 47

    def test_negative_region(self):
        assert CommonLib.get_world_chunk(-1, 0) == -32
        assert CommonLib.get_world_chunk(-1, 31) == -1

    def test_large_values(self):
        assert CommonLib.get_world_chunk(10, 5) == 325


class TestClampFloor:
    def test_normal_case(self):
        result = CommonLib.clamp_floor(0.5, 100)
        assert result == 50.0

    def test_zero_value(self):
        result = CommonLib.clamp_floor(0, 100)
        assert result == 0

    def test_value_exceeds_max(self):
        result = CommonLib.clamp_floor(2.0, 100)
        assert result == 100

    def test_negative_value_clamped_to_zero(self):
        result = CommonLib.clamp_floor(-1.0, 100)
        assert result == 0

    def test_exactly_one(self):
        result = CommonLib.clamp_floor(1.0, 100)
        assert result == 100


class TestImwrite:
    def test_success(self, tmp_path):
        filename = str(tmp_path / "test.png")
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        with patch("modules.common_lib.cv2.imencode") as mock_encode:
            mock_buf = MagicMock()
            mock_buf.tofile = MagicMock()
            mock_encode.return_value = (True, mock_buf)
            result = CommonLib.imwrite(filename, img)
        assert result is True

    def test_encode_failure(self, tmp_path):
        filename = str(tmp_path / "test.png")
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        with patch("modules.common_lib.cv2.imencode") as mock_encode:
            mock_encode.return_value = (False, None)
            result = CommonLib.imwrite(filename, img)
        assert result is False

    def test_exception_returns_false(self, tmp_path):
        filename = str(tmp_path / "test.png")
        img = np.zeros((10, 10, 3), dtype=np.uint8)
        with patch("modules.common_lib.cv2.imencode", side_effect=Exception("error")):
            result = CommonLib.imwrite(filename, img)
        assert result is False
