# MikuLogger

[English](README.en.md) | 日本語

Discord の参加/退出ログを記録するデモ用ロガーです。ログは **/activelogger** を実行したサーバーのみ有効になります。\
**Miku playful モード**で、メッセージはかわいく軽いトーンになっています（EN/JA）。

## 機能
- 参加/退出のリアルタイムログ（embed）
- 最終参加/最終退出の記録（UTC）
- サーバーごとにログチャンネルを設定
- allowlist 方式でデモ利用を制御
- スラッシュ/プレフィックス両対応（hybrid command）

## 必要環境
- Python 3.10+ 推奨
- `discord.py>=2.3`

## セットアップ
1. 依存関係をインストール
   ```bash
   pip install -r requirements.txt
   ```
2. Bot トークンを設定
   ```bash
   export DISCORD_TOKEN="YOUR_TOKEN"
   ```
3. allowlist にサーバー ID を追加
   ```json
   {
     "guild_ids": [123456789012345678]
   }
   ```
4. 起動
   ```bash
   python main.py
   ```

## インテント設定
Discord Developer Portal で以下を有効にしてください。
- Server Members Intent
- Message Content Intent（プレフィックスコマンド用）

## コマンド
- `/activelogger #channel` または `!activelogger #channel`
  - ログを有効化してチャンネルを設定
- `/inactive` または `!inactive`
  - ログを無効化
- `/showlog` または `!showlog`
  - 現在の設定を表示（有効時のみ）
- `/lastjoin [member]` または `!lastjoin [member]`
  - 最終参加の表示（有効時のみ）
- `/lastout [member]` または `!lastout [member]`
  - 最終退出の表示（有効時のみ）

## 仕様メモ
- 時刻は `dd/mm/yyyy HH:MM:SS UTC` 形式です。
- allowlist にないサーバーではコマンドが使用できません。
- allowlist が無い場合は全てのコマンドが無効になります。

## 環境変数
- `DISCORD_TOKEN`：Bot トークン
- `MIKU_DB`：SQLite DB パス（デフォルト `miku.db`）
- `MIKU_ALLOWLIST`：allowlist JSON パス（デフォルト `allowlist.json`）
- `MIKU_REPO_URL`：使用不可時に案内する URL
