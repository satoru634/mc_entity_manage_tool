# mc_entity_manage_tool

> **注意: 現在のコードは仮実装です。**  
> パス設定・機能・出力形式は今後変更される可能性があります。

Minecraft ワールドのエンティティデータを解析し、村人・メイドのステータス情報を CSV に出力するツール。  
[MCA Reborn](https://github.com/Luke100000/minecraft-comes-alive) および [LittleMaidReBirth](https://github.com/SistrScarlet/LittleMaidReBirth-Architectury) を導入した環境向け。

---

## 機能

- ワールドの `.mca` ファイルから村人・メイドのステータス・位置・インベントリを抽出
- 村ごとに CSV ファイルを出力（ハート数・職業・取引状況など）
- uNmined マップビューア用カスタムマーカー JS ファイル（`custom.markers.js`）を生成
- Minecraft データパック用の属性更新コマンド（`update_max_health.mcfunction`）を生成
- `.mca` ファイルのタイムスタンプを記録し、変更のないファイルはキャッシュから読み込む

---

## 必要環境

- Python 3.12.6
- Minecraft Java Edition（MCA Reborn + LittleMaidReBirth 導入済みワールド）
- [uNmined](https://unmined.net/)（マーカー表示機能を使う場合）

---

## セットアップ

### 1. venv の作成と依存ライブラリのインストール

**Windows:**

```bat
setup\setup_venv.bat
```

**Linux / Mac:**

```bash
bash setup/setup_venv.sh
```

### 2. venv の有効化

**Windows:**

```bat
.venv\Scripts\activate
```

**Linux / Mac:**

```bash
source .venv/bin/activate
```

---

## 設定

`config.json` を編集して各パスを設定してください。  
テンプレートとして `config.json` が同梱されています。

```json
{
    "input_base_path": "/path/to/minecraft/saves/world_name",
    "unmined_path": "/path/to/unmined/world_name",
    "target_village_name": "village_name",
    "output_path": "./out/world_name"
}
```

| キー | 説明 |
|---|---|
| `input_base_path` | Minecraft ワールドディレクトリのパス |
| `unmined_path` | uNmined の出力ディレクトリのパス |
| `target_village_name` | 属性更新コマンドを生成する対象の村名 |
| `output_path` | CSV 等の出力先ディレクトリ |

---

## 実行

```bash
python mc_entity_manage_tool.py
```

設定ファイルを明示的に指定する場合:

```bash
python mc_entity_manage_tool.py -c config.json
```

---

## 出力ファイル

出力先: `{output_path}/villagers_info/`

### 全体集計

| ファイル | 内容 |
|---|---|
| `all_villagers.csv` | 全村人一覧（未契約メイド除く） |
| `maid_info.csv` | 未契約メイド一覧 |
| `all_villages.csv` | 全村一覧（人口・衛兵数・衛兵率） |
| `village_info.json` | 村人 UUID → 村名マッピング |

### 村別

| ファイル | 内容 |
|---|---|
| `{village_name}/all_villagers.csv` | 村別全村人一覧 |
| `{village_name}/all_villagers_inventory.csv` | 村別インベントリ情報 |
| `{village_name}/not_best_friends.csv` | ハート 100 未満の村人 |
| `{village_name}/not_trading_list.csv` | 取引未経験の村人（衛兵・弓兵・無法者・メイド除く） |
| `{village_name}/has_baby.csv` | 赤ちゃんを持つ村人（存在する場合のみ生成） |

### その他

| ファイル | パス |
|---|---|
| `custom.markers.js` | `{unmined_path}/` |
| `update_max_health.mcfunction` | `{input_base_path}/datapacks/my_functions/data/mca/functions/` |

---

## 対応エンティティ

| エンティティ ID | 種別 |
|---|---|
| `mca:male_villager` | MCA Reborn Mod 男性村人 |
| `mca:female_villager` | MCA Reborn Mod 女性村人 |
| `littlemaidrebirth:little_maid_mob` | LittleMaidReBirth メイド |
| `minecraft:boat` | ボート（村人が乗船している場合） |

---

## ファイル構成

```
mc_entity_manage_tool/
├── mc_entity_manage_tool.py      # メインエントリポイント
├── modules/
│   ├── villager_info.py          # VillagerInfo クラス（主処理）
│   ├── common_lib.py             # 汎用ユーティリティ
│   ├── const.py                  # 定数・テーブル定義
│   ├── generate_unmined_marker.py # uNmined マーカー生成
│   ├── map_properties.py         # uNmined マッププロパティ読み込み
│   └── point_3d.py               # 3次元座標クラス
├── config.json                   # 設定ファイル（テンプレート）
├── requirements.txt              # 依存ライブラリ一覧
└── setup/
    ├── setup_venv.bat            # venv セットアップ（Windows）
    └── setup_venv.sh             # venv セットアップ（Linux/Mac）
```

---

## ライセンス

[MIT License](LICENSE)
