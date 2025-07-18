# テスト計画書

## 1. 概要

### 1.1 目的
このドキュメントは、Round the Clock MIDI Recording Systemのテスト計画を定義します。

### 1.2 テスト戦略
- 単体テスト: 各クラス・メソッドの動作確認
- 統合テスト: コンポーネント間の連携確認
- システムテスト: エンドツーエンドの動作確認
- 性能テスト: メモリ使用量と応答時間の確認

## 2. テスト環境

### 2.1 開発環境
- **OS**: macOS 14.0以上
- **Python**: 3.10以上
- **テストフレームワーク**: pytest
- **カバレッジ**: pytest-cov

### 2.2 テスト用MIDIデバイス
- **物理デバイス**: MIDIキーボード、MIDIコントローラー
- **仮想デバイス**: IAC Driver Bus（macOS）
- **テストデータ**: 事前に準備したMIDIファイル

## 3. 単体テスト

### 3.1 MIDIReceiver テスト

#### テストケース
```python
class TestMIDIReceiver:
    def test_init_with_valid_port(self):
        """有効なポート名で初期化できることを確認"""
        
    def test_init_with_invalid_port(self):
        """無効なポート名で初期化時にエラーが発生することを確認"""
        
    def test_start_recording(self):
        """録音開始が正常に動作することを確認"""
        
    def test_stop_recording(self):
        """録音停止が正常に動作することを確認"""
        
    def test_get_messages_empty_buffer(self):
        """空のバッファからメッセージを取得した場合の動作確認"""
        
    def test_get_messages_with_data(self):
        """データがあるバッファからメッセージを取得した場合の動作確認"""
        
    def test_is_recording_status(self):
        """録音状態の取得が正常に動作することを確認"""
```

#### テストデータ
- 有効なMIDIポート名
- 無効なMIDIポート名
- 空のメッセージリスト
- 複数のMIDIメッセージを含むリスト

### 3.2 MIDIFileWriter テスト

#### テストケース
```python
class TestMIDIFileWriter:
    def test_init_with_valid_directory(self):
        """有効なディレクトリで初期化できることを確認"""
        
    def test_write_messages_with_filename(self):
        """指定したファイル名でメッセージを書き出せることを確認"""
        
    def test_write_messages_without_filename(self):
        """自動生成ファイル名でメッセージを書き出せることを確認"""
        
    def test_generate_filename_format(self):
        """生成されるファイル名が正しい形式であることを確認"""
        
    def test_write_messages_empty_list(self):
        """空のメッセージリストを書き出した場合の動作確認"""
        
    def test_write_messages_invalid_directory(self):
        """無効なディレクトリでの書き出しエラー処理を確認"""
```

#### テストデータ
- 有効な出力ディレクトリ
- 無効な出力ディレクトリ
- 空のMIDIメッセージリスト
- 複数のMIDIメッセージを含むリスト
- 各種MIDIメッセージタイプ（note_on, note_off, control_change等）

### 3.3 AutoSaveTimer テスト

#### テストケース
```python
class TestAutoSaveTimer:
    def test_init_with_timeout(self):
        """タイムアウト時間で初期化できることを確認"""
        
    def test_start_timer(self):
        """タイマー開始が正常に動作することを確認"""
        
    def test_reset_timer(self):
        """タイマーリセットが正常に動作することを確認"""
        
    def test_stop_timer(self):
        """タイマー停止が正常に動作することを確認"""
        
    def test_timer_callback_execution(self):
        """タイマーコールバックが正常に実行されることを確認"""
        
    def test_timer_reset_before_timeout(self):
        """タイムアウト前にタイマーをリセットした場合の動作確認"""
```

#### テストデータ
- 短いタイムアウト時間（テスト用）
- 長いタイムアウト時間
- 各種コールバック関数

### 3.4 MIDIMonitor テスト

#### テストケース
```python
class TestMIDIMonitor:
    def test_init_with_valid_params(self):
        """有効なパラメータで初期化できることを確認"""
        
    def test_start_monitoring(self):
        """監視開始が正常に動作することを確認"""
        
    def test_stop_monitoring(self):
        """監視停止が正常に動作することを確認"""
        
    def test_save_current_buffer_with_data(self):
        """データがある場合のバッファ保存が正常に動作することを確認"""
        
    def test_save_current_buffer_empty(self):
        """空のバッファ保存時の動作確認"""
        
    def test_has_buffered_events(self):
        """バッファイベント存在確認が正常に動作することを確認"""
        
    def test_auto_save_functionality(self):
        """自動保存機能が正常に動作することを確認"""
```

#### テストデータ
- 有効なMIDIポート名
- 有効な出力ディレクトリ
- 各種タイムアウト時間
- バッファにデータがある場合とない場合

### 3.5 Logger テスト

#### テストケース
```python
class TestLogger:
    def test_init_with_log_file(self):
        """ログファイルで初期化できることを確認"""
        
    def test_log_file_saved(self):
        """ファイル保存ログが正常に記録されることを確認"""
        
    def test_log_recording_started(self):
        """録音開始ログが正常に記録されることを確認"""
        
    def test_log_recording_stopped(self):
        """録音停止ログが正常に記録されることを確認"""
        
    def test_log_error(self):
        """エラーログが正常に記録されることを確認"""
        
    def test_log_file_format(self):
        """ログファイルの形式が正しいことを確認"""
```

#### テストデータ
- 有効なログファイルパス
- 無効なログファイルパス
- 各種ログメッセージ
- エラーメッセージ

### 3.6 ConfigManager テスト

#### テストケース
```python
class TestConfigManager:
    def test_init_with_config_file(self):
        """設定ファイルで初期化できることを確認"""
        
    def test_load_config_valid_file(self):
        """有効な設定ファイルを読み込めることを確認"""
        
    def test_load_config_invalid_file(self):
        """無効な設定ファイルの読み込みエラー処理を確認"""
        
    def test_get_midi_config(self):
        """MIDI設定の取得が正常に動作することを確認"""
        
    def test_get_output_config(self):
        """出力設定の取得が正常に動作することを確認"""
        
    def test_get_gui_config(self):
        """GUI設定の取得が正常に動作することを確認"""
```

#### テストデータ
- 有効な設定ファイル
- 無効な設定ファイル
- 不完全な設定ファイル
- 各種設定値

## 4. 統合テスト

### 4.1 MIDI受信からファイル保存までの統合テスト

#### テストケース
```python
class TestMIDIIntegration:
    def test_midi_to_file_workflow(self):
        """MIDI受信からファイル保存までの一連の流れをテスト"""
        
    def test_auto_save_integration(self):
        """自動保存機能の統合テスト"""
        
    def test_manual_save_integration(self):
        """手動保存機能の統合テスト"""
        
    def test_error_handling_integration(self):
        """エラーハンドリングの統合テスト"""
```

#### テストシナリオ
1. MIDIデバイスからのメッセージ受信
2. メッセージのバッファ蓄積
3. タイムアウトによる自動保存
4. ファイル書き込み確認
5. ログ記録確認

### 4.2 GUI統合テスト

#### テストケース
```python
class TestGUIIntegration:
    def test_gui_start_recording(self):
        """GUIからの録音開始テスト"""
        
    def test_gui_stop_recording(self):
        """GUIからの録音停止テスト"""
        
    def test_gui_manual_save(self):
        """GUIからの手動保存テスト"""
        
    def test_gui_status_display(self):
        """GUIの状態表示テスト"""
```

#### テストシナリオ
1. GUIアプリケーション起動
2. 録音開始ボタンクリック
3. 状態表示の確認
4. 手動保存ボタンクリック
5. 保存完了メッセージの確認

## 5. システムテスト

### 5.1 エンドツーエンドテスト

#### テストケース
```python
class TestEndToEnd:
    def test_complete_recording_workflow(self):
        """完全な録音ワークフローのテスト"""
        
    def test_long_duration_recording(self):
        """長時間録音のテスト"""
        
    def test_multiple_save_cycles(self):
        """複数回の保存サイクルのテスト"""
        
    def test_system_recovery(self):
        """システム復旧のテスト"""
```

#### テストシナリオ
1. システム起動
2. MIDIデバイス接続
3. 録音開始
4. MIDIメッセージ送信
5. 自動保存実行
6. ファイル確認
7. システム停止

### 5.2 性能テスト

#### テストケース
```python
class TestPerformance:
    def test_memory_usage(self):
        """メモリ使用量のテスト"""
        
    def test_response_time(self):
        """応答時間のテスト"""
        
    def test_throughput(self):
        """スループットのテスト"""
        
    def test_concurrent_operations(self):
        """並行処理のテスト"""
```

#### 性能基準
- メモリ使用量: 1GB以下
- MIDIメッセージ受信応答時間: 1ms以下
- ファイル書き込み時間: 100ms以下
- GUI応答時間: 50ms以下
- 最大スループット: 1000 MIDIメッセージ/秒

## 6. テスト実行計画

### 6.1 テスト実行順序
1. **単体テスト**（各クラス・メソッド）
2. **統合テスト**（コンポーネント間連携）
3. **システムテスト**（エンドツーエンド）
4. **性能テスト**（メモリ・応答時間）

### 6.2 テスト実行コマンド
```bash
# 単体テスト実行
uv run pytest tests/test_midi_receiver.py -v
uv run pytest tests/test_file_writer.py -v
uv run pytest tests/test_timer.py -v
uv run pytest tests/test_monitor.py -v
uv run pytest tests/test_logger.py -v
uv run pytest tests/test_config_manager.py -v

# 全テスト実行
uv run pytest tests/ -v

# カバレッジ付きテスト実行
uv run pytest tests/ --cov=src --cov-report=html

# 性能テスト実行
uv run pytest tests/test_performance.py -v
```

### 6.3 テスト環境セットアップ
```bash
# テスト用依存関係の追加
uv add --dev pytest-cov
uv add --dev pytest-mock

# テストディレクトリの作成
mkdir -p tests
touch tests/__init__.py

# テストファイルの作成
touch tests/test_midi_receiver.py
touch tests/test_file_writer.py
touch tests/test_timer.py
touch tests/test_monitor.py
touch tests/test_logger.py
touch tests/test_config_manager.py
touch tests/test_integration.py
touch tests/test_performance.py
```

## 7. テストデータ

### 7.1 MIDIテストデータ
```python
# 基本的なMIDIメッセージ
basic_messages = [
    mido.Message('note_on', note=60, velocity=64, time=0),
    mido.Message('note_off', note=60, velocity=64, time=1000),
    mido.Message('control_change', control=1, value=64, time=0),
]

# 複雑なMIDIメッセージ
complex_messages = [
    mido.Message('note_on', note=60, velocity=64, time=0),
    mido.Message('note_on', note=62, velocity=64, time=0),
    mido.Message('note_on', note=64, velocity=64, time=0),
    mido.Message('note_off', note=60, velocity=64, time=1000),
    mido.Message('note_off', note=62, velocity=64, time=0),
    mido.Message('note_off', note=64, velocity=64, time=0),
    mido.Message('control_change', control=1, value=64, time=0),
    mido.Message('control_change', control=7, value=100, time=0),
]
```

### 7.2 設定テストデータ
```yaml
# 有効な設定ファイル
valid_config = """
midi:
  port_name: "IAC Driver Bus 1"
  timeout_seconds: 300

output:
  directory: "./test_recordings"

gui:
  window_title: "MIDI Recording System"
  theme_mode: "light"

logging:
  level: "INFO"
  file: "./test_logs/midi_recorder.log"
"""

# 無効な設定ファイル
invalid_config = """
midi:
  port_name: "invalid_port"
  timeout_seconds: -1

output:
  directory: "/invalid/path"

gui:
  window_title: ""
  theme_mode: "invalid"
"""
```

## 8. テスト結果の評価

### 8.1 成功基準
- **単体テスト**: 全テストケースが成功
- **統合テスト**: 全統合テストが成功
- **システムテスト**: エンドツーエンドテストが成功
- **性能テスト**: 性能基準を満たす
- **カバレッジ**: 80%以上

### 8.2 失敗時の対応
1. **テスト失敗の分析**
   - 失敗原因の特定
   - ログの確認
   - デバッグ情報の収集

2. **修正と再テスト**
   - コード修正
   - 単体テストの再実行
   - 統合テストの再実行

3. **回帰テスト**
   - 関連する機能のテスト
   - 性能への影響確認

## 9. 継続的テスト

### 9.1 自動テスト実行
```bash
# CI/CDパイプラインでの自動テスト
# .github/workflows/test.yml または .gitlab-ci.yml
```

### 9.2 定期テスト実行
- **日次**: 基本的な単体テスト
- **週次**: 統合テストとシステムテスト
- **月次**: 性能テストと長時間テスト

### 9.3 テストメンテナンス
- テストケースの定期的な見直し
- 新しい機能に対応したテスト追加
- 不要なテストケースの削除 
