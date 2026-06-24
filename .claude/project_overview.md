# mc_entity_manage_tool — プロジェクト概要

## 目的

Minecraft のワールドデータ（MCA Reborn & LittleMaidReBirth 導入環境）を解析し、村人・メイドのステータスや位置情報を CSV に出力するツール。
また、uNmined マップビューア用のカスタムマーカー JS ファイルや、Minecraft データパック用コマンドファイルを自動生成する。

---

## 必要MOD

- [MCA Reborn](https://github.com/Luke100000/minecraft-comes-alive)
- [LittleMaidReBirth](https://github.com/SistrScarlet/LittleMaidReBirth-Architectury)

---

## アーキテクチャ概要

```
villagers_info.py        ... メインエントリーポイント・VillagerInfo クラス
common_libs/
  common_lib.py          ... 汎用ユーティリティ（UUID変換、NBT変換、画像書き込み等）
  const.py               ... 定数・抽出テーブル・職業名テーブル・コマンドテンプレート
  generate_unmined_marker.py  ... uNmined マーカー JS 生成
  map_properties.py      ... uNmined マッププロパティ読み込み・ズーム計算
  point_3d.py            ... 3次元座標クラス
requirements.txt         ... 依存ライブラリ一覧
setup/
  setup_venv.bat         ... venv セットアップスクリプト（Windows）
  setup_venv.sh          ... venv セットアップスクリプト（Linux/Mac）
```

---

## データフロー

1. `mca_villages.dat`（NBT形式）を読み込み → 村一覧・住民マッピングを生成
2. `entities/*.mca`（Anvil形式）を走査 → リージョン/チャンクごとにエンティティを抽出
3. 村人・メイドの属性を DataFrame に集約 → CSV 出力
4. `custom.markers.js` を生成 → uNmined マップに表示
5. `update_max_health.mcfunction` を生成 → Minecraft データパックとして適用

インクリメンタル処理: `.mca` ファイルのタイムスタンプを `entities_list.json` に記録し、変更のないファイルはキャッシュ（`_region/region_X_Z.csv`）から読み込む。

---

## 対応エンティティ

| エンティティ ID | 種別 |
|---|---|
| `mca:male_villager` | MCA Reborn Mod 男性村人 |
| `mca:female_villager` | MCA Reborn Mod 女性村人 |
| `littlemaidrebirth:little_maid_mob` | LittleMaidReBirth メイド |
| `minecraft:boat` | ボート（乗客として村人を含む場合がある） |

---

## 主要クラス・モジュール

### VillagerInfo（villagers_info.py）

| メソッド | 役割 |
|---|---|
| `__get_villager_info()` | mca_villages.dat を読み込み、村人→村名マッピングを生成 |
| `__generate_village_info()` | 建物座標から村の境界ボックス・中心を計算（±32ブロック拡張） |
| `__get_entities_file_list()` | entities/*.mca のパス一覧を取得 |
| `__read_region()` | .mca リージョンファイルを読み込み、エンティティを抽出 |
| `__extract_maid_info()` | メイドエンティティから属性を抽出 |
| `__extract_villagers_info()` | 村人エンティティから属性を抽出 |
| `__get_inventories()` | インベントリ27スロット分を文字列形式で取得 |
| `__generate_attr_update_cmd()` | 体力・防具・速度・視野範囲のアップデートコマンドを生成 |
| `__filter_villagers()` | 村ごとに村人をフィルタリングして各種 CSV を出力 |
| `get_info()` | メイン処理（全リージョン走査 → CSV・JS・mcfunction 出力） |

### GenerateUnminedMarker（generate_unmined_marker.py）

- 村人・村のマーカーを `custom.markers.js` 形式で出力
- 性別で色分け（男: skyblue / 女: salmon）、職業でアイコン変更

### CommonLib（common_lib.py）

- `convert_uuid()`: 整数配列 UUID → ハイフン区切り UUID 文字列
- `get_item_info()`: TAG_Compound のアイテム情報を文字列化
- `tag_compound_to_str()` / `tag_list_to_str()`: NBT タグの文字列変換
- `get_world_chunk()`: リージョン座標・チャンク座標からワールドチャンク座標を計算
- `imwrite()`: OpenCV で日本語パス対応の画像書き込み

### MapProperties（map_properties.py）

- `unmined.map.properties.js` を読み込み、ズームレベルごとのタイル範囲を計算
- `humps` ライブラリで camelCase → snake_case 変換

---

## 定数（const.py）

| 定数 | 用途 |
|---|---|
| `EXTRACT_TABLE` | 村人属性の抽出マッピング（キー→eval式） |
| `MAID_EXTRACT_TABLE` | メイド属性の抽出マッピング（固定値中心） |
| `VILLAGE_INFO_TABLE` | 村情報の抽出マッピング |
| `PROFESSION_TABLE` | 職業 ID → 日本語名マッピング（40種類以上） |
| `AGE_STATE` | 年齢ステート → 日本語名マッピング |
| `ATTR_TABLE` | Minecraft attribute コマンドテンプレート |
| `HEAL_COMMANDS` | 即時回復エフェクト付与コマンド |
| `FACE_COUNT` | 顔パターン数（22） |

**eval 式の評価コンテキスト**: EXTRACT_TABLE / MAID_EXTRACT_TABLE / VILLAGE_INFO_TABLE の値は `__extract_villagers_info()` 等のローカル変数スコープで `eval()` される。変数名（entity, uuid, region_x 等）はそのスコープ内で定義されている必要がある。

---

## 出力ファイル一覧

### CSV（`out/{world_name}/villagers_info/` 配下）

| ファイル | 内容 |
|---|---|
| `all_villagers.csv` | 全村人一覧（未契約メイド除く） |
| `maid_info.csv` | 未契約メイド一覧 |
| `all_villages.csv` | 全村一覧（人口・衛兵数・衛兵率含む） |
| `village_info.json` | 村人UUID → 村名マッピング |
| `entities_list.json` | リージョンファイルのタイムスタンプキャッシュ |
| `_region/region_X_Z.csv` | リージョン別キャッシュ CSV |
| `{village_name}/all_villagers.csv` | 村別全村人 |
| `{village_name}/all_villagers_inventory.csv` | 村別インベントリ情報 |
| `{village_name}/not_best_friends.csv` | ハート100未満の村人 |
| `{village_name}/not_trading_list.csv` | 取引未経験の村人（衛兵・弓兵・無法者・メイド除く） |
| `{village_name}/has_baby.csv` | 赤ちゃんを持つ村人（存在する場合のみ） |

### その他

| ファイル | パス | 内容 |
|---|---|---|
| `custom.markers.js` | `{unmined_path}/` | uNmined マップ用マーカー |
| `update_max_health.mcfunction` | `{world}/datapacks/my_functions/data/mca/functions/` | 属性更新コマンド |

---

## 依存ライブラリ

| ライブラリ | 用途 |
|---|---|
| `anvil` | Minecraft Anvil 形式（.mca）読み込み |
| `nbt` | Minecraft NBT 形式読み込み |
| `pandas` | データ処理・CSV 出力 |
| `tqdm` | 進捗バー表示 |
| `opencv-python` (`cv2`) | 日本語パス対応画像書き込み |
| `humps` | camelCase ↔ snake_case 変換 |

---

## 実行方法（現状）

`villagers_info.py` の `main()` 関数内にパスをハードコーディングして直接実行する。

```python
info = VillagerInfo(
    input_base_path,   # Minecraftワールドディレクトリ
    unmined_path,      # uNmined 出力ディレクトリ
    target_village_name,  # 属性更新コマンドを生成する対象村名
    output_path,       # CSV出力先
    filter_all_maid,   # True: 未契約メイドも含む / False: 除外
)
info.get_info()
```

---

## 既知の課題・注意点

- `const.py` の `eval()` による動的抽出は柔軟だが、型安全性がない
- `__extract_villagers_info()` の except 節が広すぎる（全例外を握りつぶしている）
- `main()` のパスがハードコーディング → 将来的には引数化・設定ファイル化が望ましい
- `map_properties.py` の `MapProperties` クラスは現在 `villagers_info.py` から呼び出されていない（将来用の可能性）
- `common_lib.py` の `imwrite()` も現状 `villagers_info.py` から直接は使われていない
