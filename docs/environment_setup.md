# 環境構築手順書

## 1. 前提条件

### 1.1 必要なソフトウェア
- Python 3.10以上
- uv（Pythonパッケージマネージャー）

### 1.2 推奨環境
- macOS 14.0以上
- 8GB以上のRAM
- 10GB以上の空き容量

## 2. uvのインストール

### 2.1 uvのインストール確認
```bash
# uvが既にインストールされているか確認
uv --version

# インストールされていない場合は以下を実行
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2.2 uvの設定
```bash
# uvの設定ディレクトリを作成
mkdir -p ~/.config/uv

# 設定ファイルを作成（必要に応じて）
# ~/.config/uv/config.toml
```

## 3. プロジェクト環境の構築

### 3.1 プロジェクトディレクトリの作成
```bash
# プロジェクトディレクトリに移動
cd /Users/ks/Documents/wolf/round_the_clock_midi_recording

# 既存のpyproject.tomlがあることを確認
ls -la pyproject.toml
```

### 3.2 仮想環境の初期化
```bash
# uvで仮想環境を初期化
uv sync

# 仮想環境が正しく作成されたか確認
uv run python --version
```

### 3.3 依存関係の確認
```bash
# 現在の依存関係を確認
uv tree

# 依存関係の詳細を確認
uv pip list
```

## 4. 開発環境のセットアップ

### 4.1 プロジェクト構造の作成
```bash
# 必要なディレクトリを作成
mkdir -p src/midi src/gui src/config src/utils
mkdir -p config logs recordings tests

# __init__.pyファイルを作成
touch src/__init__.py
touch src/midi/__init__.py
touch src/gui/__init__.py
touch src/config/__init__.py
touch src/utils/__init__.py
touch tests/__init__.py
```

### 4.2 設定ファイルの作成
```bash
# 設定ファイルディレクトリを作成
mkdir -p config

# デフォルト設定ファイルを作成
cat > config/config.yaml << 'EOF'
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
EOF
```

### 4.3 ログディレクトリの作成
```bash
# ログディレクトリを作成
mkdir -p logs

# ログファイルを作成
touch logs/midi_recorder.log
```

## 5. 依存関係の管理

### 5.1 開発用依存関係の追加
```bash
# 開発用依存関係を追加
uv add --dev pytest
uv add --dev black
uv add --dev flake8
uv add --dev mypy
```

### 5.2 依存関係の更新
```bash
# 依存関係を最新版に更新
uv sync --upgrade

# 依存関係の整合性を確認
uv sync --frozen
```

## 6. 開発ツールの設定

### 6.1 コードフォーマッターの設定
```bash
# Blackの設定ファイルを作成
cat > pyproject.toml << 'EOF'
[tool.black]
line-length = 88
target-version = ['py310']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.hg
  | \.mypy_cache
  | \.tox
  | \.venv
  | build
  | dist
)/
'''
EOF
```

### 6.2 リンターの設定
```bash
# flake8の設定ファイルを作成
cat > .flake8 << 'EOF'
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,.venv,build,dist
EOF
```

### 6.3 型チェッカーの設定
```bash
# mypyの設定ファイルを作成
cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
warn_unreachable = True
strict_equality = True

[mypy-mido.*]
ignore_missing_imports = True

[mypy-flet.*]
ignore_missing_imports = True
EOF
```

## 7. 動作確認

### 7.1 基本的な動作確認
```bash
# Pythonの動作確認
uv run python -c "print('Hello, World!')"

# 依存関係のインポート確認
uv run python -c "import mido; print('mido version:', mido.__version__)"
uv run python -c "import flet; print('flet version:', flet.__version__)"
```

### 7.2 MIDIデバイスの確認
```bash
# 利用可能なMIDIポートの確認
uv run python -c "import mido; print('Available ports:', mido.get_input_names())"
```

### 7.3 開発ツールの確認
```bash
# コードフォーマッターの確認
uv run black --check .

# リンターの確認
uv run flake8 .

# 型チェッカーの確認
uv run mypy src/
```

## 8. トラブルシューティング

### 8.1 よくある問題と解決方法

#### uvが見つからない
```bash
# PATHにuvを追加
export PATH="$HOME/.cargo/bin:$PATH"
# または
source ~/.bashrc
```

#### 仮想環境が正しく作成されない
```bash
# 既存の仮想環境を削除して再作成
rm -rf .venv
uv sync
```

#### 依存関係の競合
```bash
# 依存関係をクリーンアップして再インストール
uv sync --reinstall
```

#### MIDIデバイスが認識されない
```bash
# macOSの場合、Audio MIDI Setupでデバイスを確認
open -a "Audio MIDI Setup"
```

## 9. 開発ワークフロー

### 9.1 日常的な開発コマンド
```bash
# 開発サーバーの起動
uv run python main.py

# テストの実行
uv run pytest

# コードフォーマット
uv run black .

# リンターの実行
uv run flake8 .

# 型チェック
uv run mypy src/
```

### 9.2 新しい依存関係の追加
```bash
# 新しい依存関係を追加
uv add package_name

# 開発用依存関係を追加
uv add --dev package_name

# 依存関係を同期
uv sync
```

### 9.3 依存関係の更新
```bash
# 依存関係を最新版に更新
uv sync --upgrade

# 特定のパッケージを更新
uv add package_name@latest
```

## 10. 本番環境への展開

### 10.1 本番環境用の依存関係
```bash
# 本番環境用の依存関係のみをインストール
uv sync --production
```

### 10.2 実行可能ファイルの作成
```bash
# PyInstallerを使用して実行可能ファイルを作成
uv add --dev pyinstaller
uv run pyinstaller --onefile main.py
```

## 11. メンテナンス

### 11.1 定期的なメンテナンス
```bash
# 依存関係の更新確認
uv sync --upgrade

# 不要な依存関係の削除
uv sync --clean

# キャッシュのクリア
uv cache clean
```

### 11.2 セキュリティアップデート
```bash
# セキュリティ脆弱性の確認
uv audit

# 脆弱性のある依存関係の更新
uv sync --upgrade
``` 
