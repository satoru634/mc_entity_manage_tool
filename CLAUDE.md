# CLAUDE.md — mc_entity_manage_tool

このファイルは、リポジトリ内のコードを扱う際に Claude Code (claude.ai/code) へ指針を提供します。

## 言語設定
- 常に日本語で会話する
- コメントも日本語で記述する
- エラーメッセージの説明も日本語で行う
- ドキュメントも日本語で生成する

## プロジェクト概要

MCA Reborn Mod および LittleMaidReBirth を導入した Minecraft ワールドのエンティティデータを解析するツール。
ワールドの `.mca` ファイルから村人・メイドのステータス・位置・インベントリを抽出し、村ごとに CSV 形式で出力する。
また、uNmined マップビューア用のカスタムマーカー JS ファイルと、属性更新用の Minecraft データパックコマンドを自動生成する。

詳細は [.claude/project_overview.md](.claude/project_overview.md) を参照。

## セットアップ

依存ライブラリは `requirements.txt` に記載済み。venv のセットアップは以下のスクリプトで行う。

- Windows: `setup\setup.bat`
- Linux/Mac: `bash setup/setup.sh`

## テスト

- テストの実装はpytestで行う
- ComfyUI への実際の通信は `unittest.mock` でモックする
- テスト関数・クラス名は **英語** で記述する
- 新機能を実装したら必ず対応するテストも追加し、全件パスを確認してから完了とする
- テスト実装後はblackフォーマッターでフォーマットする。

## 開発ルール

- 関数は 30 行以内を目安にする。
- 関連する機能はクラスにまとめる。
- 実装後はblackフォーマッターでフォーマットする。
- 実装後は、各ツール配下にあるREADME.mdを更新する。doc/README_english.mdも同様に更新する。
- ファイルやディレクトリ構成を変更した場合は、CLAUDE.mdおよび.claude配下に記載の該当箇所も変更する。

## git操作ルール

- 修正を始める前に、作業ブランチを切ること。
- 作業ブランチを切る前に、必ずmasterブランチの最新であるかを確認すること。
- 指示があるまでコミットしないこと。
- masterへのコミットは厳禁。
- プルリクマージ後は作業ブランチを削除すること。
