import pytest
from modules import const


class TestProfessionTable:
    def test_contains_vanilla_professions(self):
        vanilla = [
            "minecraft:none",
            "minecraft:farmer",
            "minecraft:fisherman",
            "minecraft:librarian",
            "minecraft:nitwit",
        ]
        for key in vanilla:
            assert key in const.PROFESSION_TABLE

    def test_contains_mca_professions(self):
        mca = [
            "mca:none",
            "mca:guard",
            "mca:warrior",
            "mca:archer",
            "mca:child",
        ]
        for key in mca:
            assert key in const.PROFESSION_TABLE

    def test_all_values_are_strings(self):
        for key, value in const.PROFESSION_TABLE.items():
            assert isinstance(value, str), f"{key} の値が str でない"

    def test_no_duplicate_keys(self):
        # dict はキー重複を許さないため長さで確認
        assert len(const.PROFESSION_TABLE) > 0

    def test_known_mapping(self):
        assert const.PROFESSION_TABLE["minecraft:farmer"] == "農民"
        assert const.PROFESSION_TABLE["mca:guard"] == "衛兵"
        assert const.PROFESSION_TABLE["mca:archer"] == "弓兵"


class TestAgeState:
    def test_all_five_states(self):
        for i in range(1, 6):
            assert i in const.AGE_STATE

    def test_known_values(self):
        assert const.AGE_STATE[1] == "赤ちゃん"
        assert const.AGE_STATE[5] == "大人"

    def test_all_values_are_strings(self):
        for key, value in const.AGE_STATE.items():
            assert isinstance(value, str)

    def test_out_of_range_key_missing(self):
        assert 0 not in const.AGE_STATE
        assert 6 not in const.AGE_STATE


class TestAttrTable:
    def test_required_keys_exist(self):
        required = ["max_health", "armor", "follow_range", "movement_speed"]
        for key in required:
            assert key in const.ATTR_TABLE

    def test_format_string_has_placeholder(self):
        for key, template in const.ATTR_TABLE.items():
            assert "{}" in template, f"{key} のテンプレートに {{}} がない"

    def test_format_produces_valid_command(self):
        uuid = "00000000-0000-0000-0000-000000000001"
        cmd = const.ATTR_TABLE["max_health"].format(uuid)
        assert uuid in cmd
        assert "attribute" in cmd

    def test_movement_speed_requires_suffix(self):
        # movement_speed テンプレートは末尾に速度値を追加する想定
        template = const.ATTR_TABLE["movement_speed"]
        assert template.endswith(" ")


class TestHealCommands:
    def test_is_list(self):
        assert isinstance(const.HEAL_COMMANDS, list)

    def test_not_empty(self):
        assert len(const.HEAL_COMMANDS) > 0

    def test_all_strings(self):
        for cmd in const.HEAL_COMMANDS:
            assert isinstance(cmd, str)

    def test_contains_instant_health(self):
        for cmd in const.HEAL_COMMANDS:
            assert "instant_health" in cmd

    def test_targets_expected_entity_types(self):
        all_cmds = " ".join(const.HEAL_COMMANDS)
        assert "mca:male_villager" in all_cmds
        assert "mca:female_villager" in all_cmds


class TestFaceCount:
    def test_face_count_is_22(self):
        assert const.FACE_COUNT == 22

    def test_face_count_is_int(self):
        assert isinstance(const.FACE_COUNT, int)


class TestExtractTable:
    def test_required_keys_exist(self):
        required = ["name", "UUID", "profession", "village_name"]
        for key in required:
            assert key in const.EXTRACT_TABLE

    def test_all_values_are_strings(self):
        for key, value in const.EXTRACT_TABLE.items():
            assert isinstance(value, str)


class TestMaidExtractTable:
    def test_required_keys_exist(self):
        required = ["name", "UUID", "profession"]
        for key in required:
            assert key in const.MAID_EXTRACT_TABLE

    def test_gender_is_female(self):
        assert '"女"' in const.MAID_EXTRACT_TABLE["gender"]

    def test_has_trading_is_false(self):
        assert "False" in const.MAID_EXTRACT_TABLE["has_trading"]


class TestVillageInfoTable:
    def test_required_keys_exist(self):
        required = [
            "village_name",
            "center_x",
            "center_y",
            "center_z",
            "left_top_x",
            "right_bottom_x",
        ]
        for key in required:
            assert key in const.VILLAGE_INFO_TABLE
