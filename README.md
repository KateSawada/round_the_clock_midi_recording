# Round the Clock MIDI Recording System

## 概要

Round the Clock MIDI Recording Systemは、MIDIデバイスからのリアルタイムデータを受信し、一定時間イベントなし時に自動的にMIDIファイルに保存するシステムです。

## 機能

- **リアルタイムMIDI受信**: MIDIデバイスからのメッセージをリアルタイムで受信
- **自動保存**: 一定時間イベントなし時に自動的にMIDIファイルに保存
- **手動保存**: GUIからの手動保存機能
- **デバイス再接続**: MIDIデバイスの切断・再接続を自動検出・処理
- **プラットフォーム対応**: macOS、Linux（Raspberry Pi含む）、Windows対応
- **GUIインターフェース**: fletを使用したモダンなGUI
- **設定管理**: YAML形式の設定ファイルによる柔軟な設定
- **ログ機能**: システム動作の詳細なログ記録

## インストール

### 前提条件

- Python 3.10以上
- macOS 14.0以上
- MIDIデバイスまたは仮想MIDIデバイス

### セットアップ

```bash
# 1. リポジトリのクローン
git clone git@github.com:KateSawada/round_the_clock_midi_recording.git
cd round_the_clock_midi_recording

# 2. 依存関係のインストール
uv sync

# 3. 開発用依存関係のインストール（開発者のみ）
uv add --dev pytest black flake8 mypy
```

## 使用方法

### 基本的な使用方法

```bash
# アプリケーションを起動
uv run python main.py

# 設定ファイルを指定して起動
uv run python main.py --config config/custom_config.yaml

# デバッグモードで起動
uv run python main.py --debug
```

### 設定ファイル

設定ファイルは`config/config.yaml`にあります：

```yaml
midi:
  port_name: "default"
  timeout_seconds: 300

output:
  directory: "./recordings"

gui:
  window_title: "MIDI Recording System"
  theme_mode: "light"

logging:
  level: "INFO"
  file: "./logs/midi_recorder.log"
```

## 開発

### テスト実行

```bash
# 全テスト実行
uv run pytest tests/ -v

# カバレッジ付きテスト実行
uv run pytest tests/ --cov=src --cov-report=html

# 特定のテスト実行
uv run pytest tests/test_midi_receiver.py -v
```

### コード品質チェック

```bash
# コードフォーマット
uv run black .

# リンター
uv run flake8 src/ tests/

# 型チェック
uv run mypy src/
```

## プロジェクト構造

```
round_the_clock_midi_recording/
├── src/
│   ├── midi/
│   │   ├── receiver.py      # MIDI受信クラス
│   │   ├── writer.py        # MIDIファイル書き込みクラス
│   │   └── monitor.py       # MIDI監視クラス
│   ├── gui/
│   │   └── main_window.py   # GUIメインウィンドウ
│   ├── config/
│   │   └── manager.py       # 設定管理クラス
│   └── utils/
│       ├── exceptions.py    # カスタム例外
│       ├── logger.py        # ログ管理クラス
│       └── timer.py         # 自動保存タイマー
├── config/
│   └── config.yaml          # 設定ファイル
├── logs/                    # ログファイル
├── recordings/              # 録音ファイル
├── tests/                   # テストファイル
└── docs/                    # ドキュメント
```

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 貢献

1. このリポジトリをフォーク
2. 機能ブランチを作成 (`git checkout -b feature/amazing-feature`)
3. 変更をコミット (`git commit -m 'Add amazing feature'`)
4. ブランチにプッシュ (`git push origin feature/amazing-feature`)
5. プルリクエストを作成

## サポート

問題や質問がある場合は、GitHubのIssuesページで報告してください。
