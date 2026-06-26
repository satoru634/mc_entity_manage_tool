import cv2
import os
from typing import List
from modules.point_3d import Point3D
from nbt.nbt import TAG_Compound, TAG_List


class CommonLib:
    @staticmethod
    def get_abs_path(input_path: str) -> str:
        """絶対パスを返す。相対パスの場合はカレントディレクトリからの絶対パスに変換する。"""
        input_abs_path = os.path.expanduser(input_path)
        input_abs_path = os.path.abspath(input_abs_path)
        return input_abs_path

    @staticmethod
    def get_box_center(start: Point3D, end: Point3D) -> Point3D:
        """2つのPoint3Dで定義される立方体の中心座標を返す。"""
        center = Point3D()

        center.set_x(int((end.get_x() - start.get_x()) / 2) + start.get_x())
        center.set_y(int((end.get_y() - start.get_y()) / 2) + start.get_y())
        center.set_z(int((end.get_z() - start.get_z()) / 2) + start.get_z())
        return center

    @staticmethod
    def convert_uuid(int_uuid: List) -> str:
        """整数のUUIDリストを文字列形式のUUIDに変換する。"""
        org_uuid = ""
        for id in int_uuid:
            org_uuid += format(id & 0xFFFFFFFF, "x").zfill(8)

        uuid = "{0}-{1}-{2}-{3}-{4}".format(
            org_uuid[0:8],
            org_uuid[8:12],
            org_uuid[12:16],
            org_uuid[16:20],
            org_uuid[20:],
        )

        return uuid

    @staticmethod
    def tag_list_to_str(tag_list: TAG_List):
        """TAG_Listを文字列形式に変換する。"""
        if type(tag_list) != TAG_List:
            return ""

        tag_str_list = []
        for tag in tag_list:
            tag_str_list.append(CommonLib.tag_compound_to_str(tag))

        return f"[{','.join(tag_str_list)}]"

    @staticmethod
    def tag_compound_to_str(tag_compound: TAG_Compound):
        """TAG_Compoundを文字列形式に変換する。"""
        if type(tag_compound) != TAG_Compound:
            return ""

        tag_str_list = []
        for tag in tag_compound.tags:
            tag_str = f"{tag.name}:"
            if type(tag) == TAG_Compound:
                tag_str += CommonLib.tag_compound_to_str(tag)
            elif type(tag) == TAG_List:
                tag_str += CommonLib.tag_list_to_str(tag)
            else:
                tag_str += f"{tag.value}"

            tag_str_list.append(tag_str)

        return "{" + ",".join(tag_str_list) + "}"

    @staticmethod
    def get_item_info(item) -> str:
        """TAG_Compound形式のアイテム情報を文字列形式に変換する。"""
        id = item["id"].value
        count = item["Count"].value

        tag = ""
        if "tag" in item:
            tag = CommonLib.tag_compound_to_str(item["tag"])

        item_info = f"{id}{tag} = {count}"
        return item_info

    @staticmethod
    def get_world_chunk(region_pos: int, chunk_pos: int) -> int:
        return region_pos * 32 + chunk_pos

    @staticmethod
    def clamp_floor(val, max_val):
        """値を0からmax_valの範囲にクランプする。"""
        return min(max_val, max(val * max_val, 0))

    @staticmethod
    def imwrite(filename, img, params=None):
        """画像をファイルに書き込む。"""
        try:
            ext = os.path.splitext(filename)[1]
            result, n = cv2.imencode(ext, img, params)

            if result:
                with open(filename, mode="w+b") as f:
                    n.tofile(f)
                return True
            else:
                return False
        except Exception as e:
            print(e)
            return False
