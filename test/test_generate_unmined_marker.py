import pathlib

import pandas as pd
import pytest

from modules.generate_unmined_marker import GenerateUnminedMarker


def _make_villager_row(
    name="テスト太郎",
    gender="男",
    x=100,
    z=200,
    profession="農民",
):
    return {
        "name": name,
        "gender": gender,
        "position(coordinate_x)": x,
        "position(coordinate_z)": z,
        "profession": profession,
    }


def _make_village_row(name="テスト村", cx=0, cz=0):
    return {"village_name": name, "center_x": cx, "center_z": cz}


@pytest.fixture
def base_path(tmp_path):
    return tmp_path


@pytest.fixture
def single_villager_df():
    return pd.DataFrame([_make_villager_row()])


@pytest.fixture
def single_village_df():
    return pd.DataFrame([_make_village_row()])


class TestGenerateUnminedMarkerVillager:
    def test_male_villager_color_is_skyblue(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(gender="男")])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "skyblue" in js

    def test_female_villager_color_is_salmon(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(gender="女")])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "salmon" in js

    def test_maid_uses_maid_image(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(profession="メイド")])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "maid.png" in js

    def test_villager_uses_villager_image(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(profession="農民")])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "villager.png" in js

    def test_villager_name_in_output(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(name="花子")])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "花子" in js

    def test_villager_coordinates_in_output(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row(x=512, z=-256)])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "512" in js
        assert "-256" in js


class TestGenerateUnminedMarkerVillage:
    def test_village_color_is_gold(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row()])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "gold" in js

    def test_village_uses_village_image(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row()])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "village.png" in js

    def test_village_name_in_output(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row()])
        df_vil = pd.DataFrame([_make_village_row(name="東の村")])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "東の村" in js


class TestGenerateUnminedMarkerJsStructure:
    def test_output_file_created(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row()])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        assert (tmp_path / "custom.markers.js").exists()

    def test_js_has_unmined_structure(self, tmp_path):
        df_v = pd.DataFrame([_make_villager_row()])
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "UnminedCustomMarkers" in js
        assert "isEnabled: true" in js
        assert "markers:" in js

    def test_empty_dataframes(self, tmp_path):
        df_v = pd.DataFrame(
            columns=[
                "name",
                "gender",
                "position(coordinate_x)",
                "position(coordinate_z)",
                "profession",
            ]
        )
        df_vil = pd.DataFrame(columns=["village_name", "center_x", "center_z"])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "UnminedCustomMarkers" in js

    def test_multiple_villagers(self, tmp_path):
        rows = [
            _make_villager_row(name="太郎", gender="男"),
            _make_villager_row(name="花子", gender="女"),
        ]
        df_v = pd.DataFrame(rows)
        df_vil = pd.DataFrame([_make_village_row()])
        gen = GenerateUnminedMarker(df_v, df_vil, str(tmp_path))
        gen.generate()
        js = (tmp_path / "custom.markers.js").read_text(encoding="utf-8")
        assert "太郎" in js
        assert "花子" in js
        assert "skyblue" in js
        assert "salmon" in js
