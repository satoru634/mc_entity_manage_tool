import argparse
import pathlib
import sys
import json

from modules.villager_info import VillagerInfo


def _load_config(config_path: str) -> dict:
    path = pathlib.Path(config_path)
    if path.suffix.lower() != ".json":
        print(
            f"エラー: --config にはJSONファイル(.json)のみ指定できます: {config_path}"
        )
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main():
    parser = argparse.ArgumentParser(description="村人情報抽出ツール")
    parser.add_argument(
        "-c",
        "--config",
        default="config.json",
        help="設定ファイル(JSON形式、省略時はconfig.json)",
    )
    args = parser.parse_args()

    config = _load_config(args.config)
    info = VillagerInfo(
        config["input_base_path"],
        config["unmined_path"],
        config["target_village_name"],
        config["output_path"],
        True,
    )
    info.get_info()
    return


if __name__ == "__main__":
    main()
