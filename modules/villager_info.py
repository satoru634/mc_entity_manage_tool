import pathlib
import sys
import json
from typing import Dict, List
from tqdm import tqdm

import anvil
import pandas as pd
from nbt.nbt import NBTFile, TAG_Compound, TAG_List

from modules import const
from modules.common_lib import CommonLib
from modules.point_3d import Point3D
from modules.generate_unmined_marker import GenerateUnminedMarker


class VillagerInfo:
    def __init__(
        self,
        input_base_path: str,
        unmined_path: str,
        target_village_name: str,
        output_path: str,
        filter_all_maid: bool,
    ) -> None:
        self.__input_base_path = pathlib.Path(input_base_path)
        self.__unmined_path = pathlib.Path(unmined_path)
        self.__target_village_name = target_village_name
        self.__output_path = pathlib.Path(output_path) / "villagers_info"
        self.__filter_all_maid = filter_all_maid

        # self.__MAID_ID = ["littlemaidrebirth:little_maid_mob", "touhou_little_maid:maid"]
        self.__MAID_ID = ["littlemaidrebirth:little_maid_mob"]
        self.__BOAT_ID = ["minecraft:boat"]
        self.__VILLAGER_ID = ["mca:male_villager", "mca:female_villager"]

        self.__UPDATE_ATTR_PATH = pathlib.Path(
            "datapacks/my_functions/data/mca/functions/update_max_health.mcfunction"
        )

        self.__VILLAGER_COLS = list(const.EXTRACT_TABLE.keys())
        self.__INVENTORY_COLS = self.__generate_inventory_cols()
        self.__COLUMNS = self.__VILLAGER_COLS + self.__INVENTORY_COLS

        self.__df_village_info = pd.DataFrame(
            columns=list(const.VILLAGE_INFO_TABLE.keys())
        )
        self.__village_info = self.__get_villager_info()

        self.__df_villagers_info = pd.DataFrame(columns=self.__COLUMNS)
        return

    def __get_villager_info(self) -> Dict:
        nbt_file = NBTFile(
            str(self.__input_base_path / "data" / "mca_villages.dat"), "rb"
        )
        villages: TAG_Compound = nbt_file["data"]["villages"]

        village_info = {}
        for village in villages:
            village_name = village["name"].value
            villagers: TAG_Compound = village["residentNames"]
            for key in villagers:
                village_info[key] = {
                    "village_name": village_name,
                }

            self.__generate_village_info(village["buildings"], village_name)

        return village_info

    def __generate_village_info(
        self, buildings: TAG_Compound, village_name: str
    ) -> None:
        left_top = Point3D(sys.maxsize, sys.maxsize, sys.maxsize)
        right_bottom = Point3D(-sys.maxsize, -sys.maxsize, -sys.maxsize)
        for building in buildings:
            left_top.min(
                building["pos0X"].value,
                building["pos0Y"].value,
                building["pos0Z"].value,
            )
            right_bottom.max(
                building["pos1X"].value,
                building["pos1Y"].value,
                building["pos1Z"].value,
            )

        left_top.shift_all(-32)
        right_bottom.shift_all(32)
        center = CommonLib.get_box_center(left_top, right_bottom)

        row = {}
        for key in const.VILLAGE_INFO_TABLE.keys():
            row[key] = [eval(const.VILLAGE_INFO_TABLE[key])]

        df = pd.DataFrame(row, columns=list(row.keys()))
        self.__df_village_info = pd.concat([self.__df_village_info, df])
        return

    def __generate_inventory_cols(self) -> List[str]:
        return [f"inventory_{str(index).zfill(2)}" for index in range(27)]

    def __get_entities_file_list(self) -> List[pathlib.Path]:
        # エンティティファイル一覧取得
        p_dir = self.__input_base_path / "entities"
        return sorted(p_dir.glob("**/*.mca"))

    def __read_region(
        self, path: pathlib.Path, region_x: int, region_z: int
    ) -> pd.DataFrame:
        try:
            region = anvil.Region.from_file(str(path))
        except AttributeError as e:
            return

        df_region = pd.DataFrame(columns=self.__COLUMNS)

        for chunk_x in range(32):
            for chunk_z in range(32):
                try:
                    chunk = region.chunk_data(chunk_x, chunk_z)
                except IndexError as e:
                    continue

                if chunk is None:
                    continue

                for entity in chunk["Entities"]:
                    row = None
                    if entity["id"].value in self.__MAID_ID:
                        row = self.__extract_maid_info(
                            entity, region_x, region_z, chunk_x, chunk_z
                        )
                    elif entity["id"].value in self.__BOAT_ID:
                        row = {}
                        for villager in entity["Passengers"]:
                            row = self.__extract_villagers_info(
                                villager, region_x, region_z, chunk_x, chunk_z, row
                            )

                    elif entity["id"].value in self.__VILLAGER_ID:
                        row = self.__extract_villagers_info(
                            entity, region_x, region_z, chunk_x, chunk_z
                        )
                        # print(row)

                    if row is None:
                        continue

                    if len(df_region) > 0:
                        df = pd.DataFrame(row, columns=self.__COLUMNS)
                        df_region = pd.concat([df_region, df])
                    else:
                        df_region = pd.DataFrame(row, columns=self.__COLUMNS)

        if len(df_region) > 0:
            if len(self.__df_villagers_info) > 0:
                self.__df_villagers_info = pd.concat(
                    [self.__df_villagers_info, df_region]
                )
            else:
                self.__df_villagers_info = df_region.copy()

        region_base_path = self.__output_path / "_region"
        region_base_path.mkdir(parents=True, exist_ok=True)

        region_path = region_base_path / f"region_{region_x}_{region_z}.csv"
        df_region.to_csv(region_path, index=False)
        return

    def __extract_maid_info(
        self,
        entity: TAG_Compound,
        region_x: int,
        region_z: int,
        chunk_x: int,
        chunk_z: int,
    ) -> Dict:
        name = "リトルメイド"
        uuid = CommonLib.convert_uuid(entity["UUID"].value)
        profession = "メイド"
        if "CustomName" in entity:
            name_table = eval(entity["CustomName"].value)
            name = name_table["text"]
        elif entity["IsContract"].value == 0:
            name = "リトルメイド(未契約)"
            profession = "メイド(未契約)"

        world_chunk_x = CommonLib.get_world_chunk(region_x, chunk_x)
        world_chunk_z = CommonLib.get_world_chunk(region_z, chunk_z)

        row = {}
        for key in const.MAID_EXTRACT_TABLE.keys():
            row[key] = [eval(const.MAID_EXTRACT_TABLE[key])]

        inventory_info = self.__get_inventories(entity["Inventory"])
        for key in inventory_info.keys():
            row[key] = [inventory_info[key]]

        return row

    def __extract_villagers_info(
        self,
        entity: TAG_Compound,
        region_x: int,
        region_z: int,
        chunk_x: int,
        chunk_z: int,
        row: Dict = None,
        inv_row: Dict = None,
    ) -> Dict:
        villager_name = entity["villagerName"].value
        uuid = CommonLib.convert_uuid(entity["UUID"].value)
        village_info = self.__village_info
        world_chunk_x = CommonLib.get_world_chunk(region_x, chunk_x)
        world_chunk_z = CommonLib.get_world_chunk(region_z, chunk_z)
        gender = "女" if entity["gender"].value == 2 else "男"

        albinism = 1.0
        hetero = False
        for traits in entity["traits"]:
            if traits == "ALBINISM":
                albinism = 0.1
            if traits == "HETEROCHROMIA":
                hetero = True

        has_baby = True if entity["hasBaby"].value == 1 else False
        has_trading = True if entity["Xp"].value > 0 else False

        org_profession = entity["VillagerData"]["profession"].value
        profession = (
            const.PROFESSION_TABLE[org_profession]
            if org_profession in const.PROFESSION_TABLE
            else "未知の職業"
        )

        if row is None:
            row = {}

        for key in const.EXTRACT_TABLE.keys():
            try:
                if key in row:
                    row[key].append(eval(const.EXTRACT_TABLE[key]))
                else:
                    row[key] = [eval(const.EXTRACT_TABLE[key])]
            except:
                if key in row:
                    if key == "hearts":
                        row[key].append(0)
                    else:
                        row[key].append("-")
                else:
                    if key == "hearts":
                        row[key] = [0]
                    else:
                        row[key] = ["-"]

        inventory_info = self.__get_inventories(entity["Inventory"])
        for key in inventory_info.keys():
            if key in row:
                row[key].append(inventory_info[key])
            else:
                row[key] = [inventory_info[key]]

        return row

    def __get_inventories(self, inventory: TAG_List) -> Dict[str, str]:
        inventory_info = {}
        for index in range(27):
            key = self.__INVENTORY_COLS[index]

            if len(inventory) <= index:
                inventory_info[key] = "-"
            else:
                inventory_info[key] = CommonLib.get_item_info(inventory[index])

        return inventory_info

    def __generate_attr_update_cmd(self, df_villagers: pd.DataFrame) -> None:
        cmd_list = {}
        uuid_list = df_villagers["UUID"].values
        profession_list = df_villagers["profession"].values

        # 体力最大値アップ・回復コマンド生成
        for uuid, profession in zip(uuid_list, profession_list):
            for key in const.ATTR_TABLE.keys():
                if not key in cmd_list:
                    cmd_list[key] = []

                attr = const.ATTR_TABLE[key].format(uuid)
                if key == "movement_speed":
                    attr += "0.4" if profession == "メイド" else "0.55"

                cmd_list[key].append(attr)

        # ファイルに書き出す
        with open(self.__input_base_path / self.__UPDATE_ATTR_PATH, "w") as f:
            for key in cmd_list.keys():
                f.write("\n".join(cmd_list[key]))
                f.write("\n\n")

            for cmd in const.HEAL_COMMANDS:
                f.write("{}\n".format(cmd))

        return

    def __filter_villagers(
        self, row: pd.Series, df_villagers_info: pd.DataFrame
    ) -> pd.Series:
        output_path = self.__output_path / row["village_name"]
        output_path.mkdir(parents=True, exist_ok=True)

        df_village_filter = df_villagers_info[
            df_villagers_info["village_name"] == row["village_name"]
        ]
        df_no_village_filter = df_villagers_info[
            (df_villagers_info["village_name"] == "-")
            & (df_villagers_info["position(coordinate_x)"] >= row["left_top_x"])
            & (df_villagers_info["position(coordinate_y)"] >= row["left_top_y"])
            & (df_villagers_info["position(coordinate_z)"] >= row["left_top_z"])
            & (df_villagers_info["position(coordinate_x)"] <= row["right_bottom_x"])
            & (df_villagers_info["position(coordinate_y)"] <= row["right_bottom_y"])
            & (df_villagers_info["position(coordinate_z)"] <= row["right_bottom_z"])
        ]

        df_village_filter = pd.concat([df_village_filter, df_no_village_filter])
        df_basic_info = df_village_filter[self.__VILLAGER_COLS]
        df_basic_info = df_basic_info.sort_values("hearts")
        df_basic_info.to_csv(output_path / "all_villagers.csv", index=False)

        df_inventory_info = df_village_filter[
            ["name", "UUID", "profession"] + self.__INVENTORY_COLS
        ]
        df_inventory_info.to_csv(
            output_path / "all_villagers_inventory.csv", index=False
        )

        df_not_best_friend = df_basic_info[df_basic_info["hearts"] < 100]
        df_not_best_friend.to_csv(output_path / "not_best_friends.csv", index=False)

        df_not_trading_list = df_basic_info[
            (df_basic_info["has_trading"] == False)
            & (df_basic_info["profession"] != "衛兵")
            & (df_basic_info["profession"] != "弓兵")
            & (df_basic_info["profession"] != "無法者")
            & (df_basic_info["profession"] != "メイド")
        ]
        df_not_trading_list.to_csv(output_path / "not_trading_list.csv", index=False)

        df_has_baby = df_basic_info[df_basic_info["has_baby"] == True]
        has_baby_path = output_path / "has_baby.csv"
        if len(df_has_baby) > 0:
            df_has_baby.to_csv(has_baby_path, index=False)
        else:
            if has_baby_path.exists():
                has_baby_path.unlink()

        # 体力最大値アップ・回復コマンド生成
        if row["village_name"] == self.__target_village_name:
            self.__generate_attr_update_cmd(
                df_village_filter[df_village_filter["profession"] != "無法者"]
            )

        df_mca_villagers = df_basic_info[
            (df_basic_info["profession"] != "メイド")
            & (df_basic_info["profession"] != "無法者")
        ]
        df_mca_guard_villagers = df_mca_villagers[
            (df_mca_villagers["profession"] == "衛兵")
            | (df_mca_villagers["profession"] == "弓兵")
        ]

        guard_rate = "0.00%"
        if len(df_mca_villagers) > 0:
            guard_rate = "{:.2f}%".format(
                (len(df_mca_guard_villagers) / len(df_mca_villagers)) * 100.0
            )

        return pd.Series(
            [len(df_mca_villagers), len(df_mca_guard_villagers), guard_rate]
        )

    def __output_csv(self) -> None:
        df_villagers_info = self.__df_villagers_info[
            self.__df_villagers_info["profession"] != "メイド(未契約)"
        ]
        df_maid_info = self.__df_villagers_info[
            self.__df_villagers_info["profession"] == "メイド(未契約)"
        ]
        df_villagers_info.to_csv(self.__output_path / "all_villagers.csv", index=False)
        df_maid_info.to_csv(self.__output_path / "maid_info.csv", index=False)

        self.__df_village_info[["population", "guards", "guard_rate"]] = (
            self.__df_village_info.apply(
                self.__filter_villagers, axis=1, df_villagers_info=df_villagers_info
            )
        )

        self.__df_village_info = self.__df_village_info.sort_values(
            "population", ascending=False
        )
        self.__df_village_info.to_csv(
            self.__output_path / "all_villages.csv", index=False
        )
        return

    def get_info(self) -> None:
        self.__output_path.mkdir(parents=True, exist_ok=True)

        self.__df_villagers_info = pd.DataFrame(columns=self.__COLUMNS)
        entities_list_path = self.__output_path / "entities_list.json"
        if entities_list_path.exists():
            with open(entities_list_path, "r") as f:
                entities_list = json.load(f)
        else:
            entities_list = {}

        for path in tqdm(self.__get_entities_file_list()):
            filename = path.name
            split_region = filename.split(".")

            prev_st_mtime = -1.0
            if filename in entities_list:
                prev_st_mtime = entities_list[filename]

            new_st_mtime = path.stat().st_mtime
            if prev_st_mtime != new_st_mtime:
                entities_list[filename] = new_st_mtime
                self.__read_region(path, int(split_region[1]), int(split_region[2]))
            else:
                region_base_path = self.__output_path / "_region"
                region_path = region_base_path / "region_{0}_{1}.csv".format(
                    int(split_region[1]), int(split_region[2])
                )
                df = pd.read_csv(region_path, low_memory=False)
                df["updated"] = False
                if len(df) > 0:
                    if len(self.__df_villagers_info) > 0:
                        self.__df_villagers_info = pd.concat(
                            [self.__df_villagers_info, df]
                        )
                    else:
                        self.__df_villagers_info = df.copy()

        with open(entities_list_path, "w") as f:
            json.dump(entities_list, f, indent=2)

        with open(self.__output_path / "village_info.json", "w") as f:
            json.dump(self.__village_info, f, indent=2)

        df_villagers = (
            self.__df_villagers_info
            if self.__filter_all_maid
            else self.__df_villagers_info[
                self.__df_villagers_info["profession"] != "メイド(未契約)"
            ]
        )

        marker = GenerateUnminedMarker(
            df_villagers,
            self.__df_village_info,
            self.__unmined_path,
        )
        marker.generate()

        # csv出力
        self.__output_csv()
        return
