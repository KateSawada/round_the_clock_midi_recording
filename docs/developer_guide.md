# 開発者ガイド

## 1. 概要

### 1.1 目的
このドキュメントは、Round the Clock MIDI Recording Systemの開発者向けガイドです。

### 1.2 対象読者
- 開発者
- コードレビュアー
- 将来のメンテナー

## 2. 開発環境セットアップ

### 2.1 必要なツール
- Python 3.10以上
- uv（Pythonパッケージマネージャー）
- Git
- コードエディタ（VS Code推奨）

### 2.2 開発環境の構築
```bash
# 1. リポジトリのクローン
git clone <repository-url>
cd round_the_clock_midi_recording

# 2. 仮想環境の構築
uv sync

# 3. 開発用依存関係のインストール
uv add --dev pytest black flake8 mypy pytest-cov pytest-mock

# 4. プロジェクト構造の作成
mkdir -p src/midi src/gui src/config src/utils
mkdir -p config logs recordings tests
touch src/__init__.py src/midi/__init__.py src/gui/__init__.py src/config/__init__.py src/utils/__init__.py tests/__init__.py
```

### 2.3 開発ツールの設定

#### 2.3.1 VS Code設定
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.flake8Enabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests"],
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
        "source.organizeImports": true
    }
}
```

#### 2.3.2 Git Hooks
```bash
# pre-commitフックの設定
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
set -e

echo "Running pre-commit checks..."

# コードフォーマット
uv run black .

# リンター
uv run flake8 src/ tests/

# 型チェック
uv run mypy src/

# テスト実行
uv run pytest tests/ --cov=src --cov-report=term-missing

echo "Pre-commit checks passed!"
EOF

chmod +x .git/hooks/pre-commit
```

## 3. コーディング規約

### 3.1 Pythonコーディング規約

#### 3.1.1 基本ルール
- **PEP 8**に準拠
- **Black**による自動フォーマット
- **flake8**によるリント
- **MyPy**による型チェック

#### 3.1.2 命名規約
```python
# クラス名: PascalCase
class MIDIReceiver:
    pass

# 関数・メソッド名: snake_case
def start_recording():
    pass

# 定数: UPPER_SNAKE_CASE
DEFAULT_TIMEOUT = 300

# 変数名: snake_case
port_name = "default"
```

#### 3.1.3 ドキュメント規約
```python
class MIDIReceiver:
    """MIDIデバイスからのメッセージを受信するクラス。
    
    Attributes:
        port_name (str): MIDIポート名
        messages (List[mido.Message]): 受信したメッセージのリスト
        is_recording (bool): 録音状態
    """
    
    def start_recording(self) -> None:
        """MIDI受信を開始する。
        
        Raises:
            MIDIError: ポートのオープンに失敗した場合
        """
        pass
```

### 3.2 ファイル構造規約

#### 3.2.1 ディレクトリ構造
```
src/
├── __init__.py
├── midi/
│   ├── __init__.py
│   ├── receiver.py
│   ├── writer.py
│   └── monitor.py
├── gui/
│   ├── __init__.py
│   └── main_window.py
├── config/
│   ├── __init__.py
│   └── manager.py
└── utils/
    ├── __init__.py
    ├── logger.py
    └── timer.py
```

#### 3.2.2 ファイル命名
- モジュール名: `snake_case`
- クラス名: `PascalCase`
- ファイル名: `snake_case.py`

### 3.3 エラーハンドリング規約

#### 3.3.1 カスタム例外
```python
class MIDIError(Exception):
    """MIDI関連のエラー"""
    pass

class FileWriteError(Exception):
    """ファイル書き込みエラー"""
    pass

class ConfigError(Exception):
    """設定ファイルエラー"""
    pass
```

#### 3.3.2 例外処理
```python
def safe_midi_operation(func):
    """MIDI操作の安全な実行デコレータ"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"MIDI operation failed: {e}")
            raise MIDIError(f"Operation failed: {e}")
    return wrapper
```

## 4. 開発ワークフロー

### 4.1 機能開発フロー

#### 4.1.1 ブランチ戦略
```bash
# メインブランチ
main          # 本番環境用
develop       # 開発環境用

# 機能ブランチ
feature/midi-receiver     # MIDI受信機能
feature/auto-save         # 自動保存機能
feature/gui-basic         # 基本GUI機能
feature/config-management  # 設定管理機能

# 修正ブランチ
hotfix/critical-bug       # 緊急修正
bugfix/memory-leak        # バグ修正
```

#### 4.1.2 開発手順
1. **機能ブランチの作成**
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/new-feature
   ```

2. **開発・テスト**
   ```bash
   # コード実装
   # 単体テスト作成
   uv run pytest tests/test_new_feature.py -v
   
   # 統合テスト
   uv run pytest tests/test_integration.py -v
   ```

3. **コードレビュー**
   ```bash
   # コードフォーマット
   uv run black .
   
   # リンター
   uv run flake8 src/ tests/
   
   # 型チェック
   uv run mypy src/
   
   # コミット
   git add .
   git commit -m "feat: add new feature"
   ```

4. **プルリクエスト作成**
   ```bash
   git push origin feature/new-feature
   # GitHub/GitLabでプルリクエスト作成
   ```

### 4.2 テスト駆動開発（TDD）

#### 4.2.1 TDDサイクル
1. **Red**: 失敗するテストを書く
2. **Green**: テストが通る最小限のコードを書く
3. **Refactor**: コードをリファクタリングする

#### 4.2.2 テスト例
```python
# tests/test_midi_receiver.py
import pytest
from unittest.mock import Mock, patch
from src.midi.receiver import MIDIReceiver

class TestMIDIReceiver:
    def test_init_with_valid_port(self):
        """有効なポート名で初期化できることを確認"""
        receiver = MIDIReceiver("test_port")
        assert receiver.port_name == "test_port"
        assert receiver.is_recording == False
        assert len(receiver.messages) == 0
    
    def test_start_recording_success(self):
        """録音開始が正常に動作することを確認"""
        with patch('mido.open_input') as mock_open:
            mock_port = Mock()
            mock_open.return_value = mock_port
            
            receiver = MIDIReceiver("test_port")
            receiver.start_recording()
            
            assert receiver.is_recording == True
            mock_open.assert_called_once_with("test_port")
    
    def test_start_recording_failure(self):
        """録音開始失敗時のエラーハンドリングを確認"""
        with patch('mido.open_input') as mock_open:
            mock_open.side_effect = Exception("Port not found")
            
            receiver = MIDIReceiver("invalid_port")
            
            with pytest.raises(MIDIError):
                receiver.start_recording()
```

### 4.3 デバッグ手法

#### 4.3.1 ログデバッグ
```python
import logging

# ログ設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def debug_function():
    logger.debug("Function called")
    # 処理
    logger.debug("Function completed")
```

#### 4.3.2 デバッガー使用
```python
import pdb

def problematic_function():
    # 問題のある処理
    pdb.set_trace()  # ブレークポイント
    # デバッグしたい処理
```

#### 4.3.3 プロファイリング
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # プロファイルしたい処理
    target_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats()
```

## 5. パフォーマンス最適化

### 5.1 メモリ最適化

#### 5.1.1 メモリ使用量監視
```python
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"Memory usage: {memory_info.rss / 1024 / 1024:.2f} MB")
```

#### 5.1.2 メモリリーク検出
```python
import gc
import sys

def check_memory_leak():
    gc.collect()
    objects = gc.get_objects()
    print(f"Number of objects: {len(objects)}")
    
    # 特定のオブジェクトの数をカウント
    midi_objects = [obj for obj in objects if 'MIDI' in str(type(obj))]
    print(f"MIDI objects: {len(midi_objects)}")
```

### 5.2 パフォーマンス測定

#### 5.2.1 実行時間測定
```python
import time
from functools import wraps

def measure_time(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        print(f"{func.__name__} took {end_time - start_time:.4f} seconds")
        return result
    return wrapper

@measure_time
def slow_function():
    # 重い処理
    pass
```

#### 5.2.2 プロファイリング
```python
import cProfile
import pstats
from io import StringIO

def profile_code():
    pr = cProfile.Profile()
    pr.enable()
    
    # プロファイルしたいコード
    target_function()
    
    pr.disable()
    s = StringIO()
    ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
    ps.print_stats()
    print(s.getvalue())
```

## 6. セキュリティ考慮事項

### 6.1 入力検証
```python
def validate_midi_port(port_name: str) -> bool:
    """MIDIポート名の検証"""
    if not isinstance(port_name, str):
        raise ValueError("Port name must be a string")
    
    if len(port_name) == 0:
        raise ValueError("Port name cannot be empty")
    
    if len(port_name) > 100:
        raise ValueError("Port name too long")
    
    return True
```

### 6.2 ファイル操作の安全性
```python
import os
from pathlib import Path

def safe_file_write(filepath: str, content: bytes) -> None:
    """安全なファイル書き込み"""
    # パスの正規化
    normalized_path = os.path.normpath(filepath)
    
    # ディレクトリトラバーサル攻撃の防止
    if '..' in normalized_path:
        raise ValueError("Invalid file path")
    
    # 一時ファイルに書き込み
    temp_path = normalized_path + '.tmp'
    with open(temp_path, 'wb') as f:
        f.write(content)
    
    # アトミックな移動
    os.rename(temp_path, normalized_path)
```

### 6.3 ログセキュリティ
```python
import re

def sanitize_log_message(message: str) -> str:
    """ログメッセージのサニタイズ"""
    # 機密情報の除去
    patterns = [
        r'password\s*=\s*\S+',
        r'api_key\s*=\s*\S+',
        r'token\s*=\s*\S+'
    ]
    
    sanitized = message
    for pattern in patterns:
        sanitized = re.sub(pattern, '[REDACTED]', sanitized, flags=re.IGNORECASE)
    
    return sanitized
```

## 7. 継続的インテグレーション（CI）

### 7.1 GitHub Actions設定
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main, develop ]

jobs:
  test:
    runs-on: macos-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    
    - name: Install dependencies
      run: |
        uv sync
    
    - name: Run tests
      run: |
        uv run pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

### 7.2 品質ゲート
```yaml
# 品質チェックの自動化
- name: Code quality checks
  run: |
    uv run black --check .
    uv run flake8 src/ tests/
    uv run mypy src/
    uv run pytest tests/ --cov=src --cov-fail-under=80
```

## 8. ドキュメント作成

### 8.1 コードドキュメント
```python
def complex_function(param1: str, param2: int) -> bool:
    """複雑な関数の説明
    
    Args:
        param1: 文字列パラメータの説明
        param2: 整数パラメータの説明
    
    Returns:
        処理結果の真偽値
    
    Raises:
        ValueError: パラメータが無効な場合
        RuntimeError: 実行時エラーが発生した場合
    
    Example:
        >>> result = complex_function("test", 42)
        >>> print(result)
        True
    """
    pass
```

### 8.2 APIドキュメント
```python
# docstringからAPIドキュメントを自動生成
# sphinxを使用したドキュメント生成

# docs/source/conf.py
project = 'Round the Clock MIDI Recording System'
copyright = '2024'
author = 'Your Name'

# docs/source/index.rst
Welcome to Round the Clock MIDI Recording System's documentation!
==============================================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   api
   user_guide
   developer_guide
```

## 9. リリース管理

### 9.1 バージョニング
```python
# src/__init__.py
__version__ = "0.1.0"

# セマンティックバージョニング
# MAJOR.MINOR.PATCH
# 0.1.0 - 初期リリース
# 0.1.1 - バグ修正
# 0.2.0 - 新機能追加
# 1.0.0 - 正式リリース
```

### 9.2 リリース手順
```bash
# 1. バージョン更新
vim src/__init__.py  # バージョン番号更新

# 2. 変更ログ更新
vim CHANGELOG.md

# 3. タグ作成
git tag -a v0.1.0 -m "Release version 0.1.0"
git push origin v0.1.0

# 4. リリース作成
# GitHub/GitLabでリリース作成
```

## 10. トラブルシューティング

### 10.1 よくある開発問題

#### 10.1.1 依存関係の競合
```bash
# 依存関係の競合解決
uv sync --reinstall

# 特定バージョンの強制インストール
uv add package_name==specific_version
```

#### 10.1.2 テストの失敗
```bash
# テストの詳細実行
uv run pytest tests/ -v -s

# 特定のテストのみ実行
uv run pytest tests/test_specific.py::test_function -v

# デバッグモードでテスト実行
uv run pytest tests/ --pdb
```

#### 10.1.3 型チェックエラー
```bash
# 型チェックの詳細出力
uv run mypy src/ --verbose

# 特定ファイルの型チェック
uv run mypy src/midi/receiver.py

# 型チェックの無視設定
# mypy.iniで設定
```

### 10.2 デバッグツール

#### 10.2.1 ログデバッグ
```python
import logging

# デバッグログの設定
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

#### 10.2.2 プロファイリング
```python
import cProfile
import pstats

def profile_function():
    profiler = cProfile.Profile()
    profiler.enable()
    
    # プロファイルしたい処理
    target_function()
    
    profiler.disable()
    stats = pstats.Stats(profiler)
    stats.sort_stats('cumulative')
    stats.print_stats(10)  # 上位10件を表示
```

## 11. ベストプラクティス

### 11.1 コード品質
- **単一責任の原則**: 各クラス・関数は一つの責任を持つ
- **DRY原則**: 重複コードを避ける
- **KISS原則**: シンプルに保つ
- **SOLID原則**: オブジェクト指向設計の原則に従う

### 11.2 パフォーマンス
- **効率的なアルゴリズム**: 適切なデータ構造とアルゴリズムを使用
- **メモリ管理**: 適切なメモリ使用量の管理
- **非同期処理**: 必要に応じて非同期処理を使用

### 11.3 セキュリティ
- **入力検証**: 全ての入力を検証する
- **最小権限の原則**: 必要最小限の権限のみ使用
- **セキュアコーディング**: セキュリティを考慮したコーディング

### 11.4 保守性
- **明確な命名**: 意図が分かる名前を使用
- **適切なコメント**: 複雑な処理にはコメントを追加
- **テストカバレッジ**: 十分なテストカバレッジを維持 
