import copy
import pathlib

import pandas as pd


class GenerateUnminedMarker:
    def __init__(
        self,
        df_villagers_info: pd.DataFrame,
        df_village_info: pd.DataFrame,
        base_path: str,
    ) -> None:
        self.__df_villagers_info = df_villagers_info
        self.__df_village_info = df_village_info
        self.__base_path = pathlib.Path(base_path)

        self.__marker_list = []

        self.__MARKER_TEMPLATE = {
            "x": 0,
            "z": 0,
            "image": "",
            "imageAnchor": [0.5, 1],
            "imageScale": 0.25,
            "text": "",
            "textColor": "",
            "textStrokeColor": "black",
            "textStrokeWidth": 2,
            "offsetX": 0,
            "offsetY": -35,
            "font": "bold 14px Calibri,sans serif",
        }

        self.__PIN_IMG_PATH_LIST = {
            "village": "village.png",
            "villager": "villager.png",
            "maid": "maid.png",
        }

        self.__JS_TEMPLATE = (
            "UnminedCustomMarkers = {\n    isEnabled: true,\n<replace>}"
        )

        self.__INDENT = " " * 4
        self.__KEY_VALUE = "{0}: {1},\n"
        self.__KEY_STR_VALUE = '{0}: "{1}",\n'
        return

    def __generate_villagers_marker(self, row: pd.Series) -> None:
        marker = copy.deepcopy(self.__MARKER_TEMPLATE)
        marker["x"] = row["position(coordinate_x)"]
        marker["z"] = row["position(coordinate_z)"]
        marker["text"] = row["name"]
        marker["textColor"] = "skyblue" if row["gender"] == "男" else "salmon"
        marker["image"] = (
            self.__PIN_IMG_PATH_LIST["villager"]
            if row["profession"] != "メイド"
            else self.__PIN_IMG_PATH_LIST["maid"]
        )
        self.__marker_list.append(marker)
        return

    def __generate_village_marker(self, row: pd.Series) -> None:
        marker = copy.deepcopy(self.__MARKER_TEMPLATE)
        marker["x"] = row["center_x"]
        marker["z"] = row["center_z"]
        marker["text"] = row["village_name"]
        marker["textColor"] = "gold"
        marker["image"] = self.__PIN_IMG_PATH_LIST["village"]
        self.__marker_list.append(marker)
        return

    def __output_js(self) -> None:
        out_text = self.__INDENT + "markers: [\n"
        for marker in self.__marker_list:
            out_text += self.__INDENT * 2 + "{\n"
            for key in marker.keys():
                if type(marker[key]) == str:
                    out_text += self.__INDENT * 3 + self.__KEY_STR_VALUE.format(
                        key, marker[key]
                    )
                else:
                    out_text += self.__INDENT * 3 + self.__KEY_VALUE.format(
                        key, marker[key]
                    )

            out_text += self.__INDENT * 2 + "},\n"

        out_text += self.__INDENT + "]\n"
        out_text = self.__JS_TEMPLATE.replace("<replace>", out_text)
        with open(self.__base_path / "custom.markers.js", "w", encoding="utf-8") as f:
            f.write(out_text)

        return

    def generate(self) -> None:
        self.__df_villagers_info.apply(self.__generate_villagers_marker, axis=1)
        self.__df_village_info.apply(self.__generate_village_marker, axis=1)

        self.__output_js()
        return
