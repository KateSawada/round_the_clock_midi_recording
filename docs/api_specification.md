# API仕様書

## 1. 概要

### 1.1 目的
このドキュメントは、Round the Clock MIDI Recording SystemのAPI仕様を定義します。

### 1.2 対象読者
- 開発者
- システム統合担当者
- 将来の拡張開発者

## 2. クラス設計

### 2.1 MIDIReceiver

#### 概要
MIDIデバイスからのメッセージを受信し、メモリ上に蓄積するクラス。

#### クラス定義
```python
class MIDIReceiver:
    def __init__(self, port_name: str) -> None
    def start_recording(self) -> None
    def stop_recording(self) -> None
    def get_messages(self) -> List[mido.Message]
    def is_recording(self) -> bool
```

#### メソッド詳細

##### `__init__(port_name: str) -> None`
**説明**: MIDIReceiverを初期化する

**パラメータ**:
- `port_name` (str): MIDIポート名

**例外**:
- `MIDIError`: ポートが見つからない場合

**使用例**:
```python
receiver = MIDIReceiver("IAC Driver Bus 1")
```

##### `start_recording() -> None`
**説明**: MIDI受信を開始する

**例外**:
- `MIDIError`: ポートのオープンに失敗した場合

**使用例**:
```python
receiver.start_recording()
```

##### `stop_recording() -> None`
**説明**: MIDI受信を停止する

**使用例**:
```python
receiver.stop_recording()
```

##### `get_messages() -> List[mido.Message]`
**説明**: 蓄積されたメッセージを取得し、バッファをクリアする

**戻り値**: MIDIメッセージのリスト

**使用例**:
```python
messages = receiver.get_messages()
```

##### `is_recording() -> bool`
**説明**: 録音状態を取得する

**戻り値**: 録音中の場合True

**使用例**:
```python
if receiver.is_recording():
    print("録音中")
```

### 2.2 MIDIFileWriter

#### 概要
MIDIメッセージをMIDIファイルに書き出すクラス。

#### クラス定義
```python
class MIDIFileWriter:
    def __init__(self, output_directory: str) -> None
    def write_messages(self, messages: List[mido.Message], filename: str = None) -> str
    def _generate_filename(self) -> str
```

#### メソッド詳細

##### `__init__(output_directory: str) -> None`
**説明**: MIDIFileWriterを初期化する

**パラメータ**:
- `output_directory` (str): 出力ディレクトリパス

**使用例**:
```python
writer = MIDIFileWriter("./recordings")
```

##### `write_messages(messages: List[mido.Message], filename: str = None) -> str`
**説明**: MIDIメッセージをファイルに書き出す

**パラメータ**:
- `messages` (List[mido.Message]): 書き出すメッセージリスト
- `filename` (str, optional): ファイル名（Noneの場合は自動生成）

**戻り値**: 保存されたファイルのパス

**例外**:
- `FileWriteError`: ファイル書き込みに失敗した場合

**使用例**:
```python
filepath = writer.write_messages(messages)
```

##### `_generate_filename() -> str`
**説明**: 自動ファイル名を生成する

**戻り値**: yyyymmddhhmmss.mid形式のファイル名

**使用例**:
```python
filename = writer._generate_filename()  # "20240101123045.mid"
```

### 2.3 AutoSaveTimer

#### 概要
一定時間後に自動保存を実行するタイマークラス。

#### クラス定義
```python
class AutoSaveTimer:
    def __init__(self, timeout_seconds: int = 300) -> None
    def start_timer(self, callback: Callable[[], None]) -> None
    def reset_timer(self) -> None
    def stop_timer(self) -> None
```

#### メソッド詳細

##### `__init__(timeout_seconds: int = 300) -> None`
**説明**: AutoSaveTimerを初期化する

**パラメータ**:
- `timeout_seconds` (int): タイムアウト時間（秒）

**使用例**:
```python
timer = AutoSaveTimer(300)  # 5分
```

##### `start_timer(callback: Callable[[], None]) -> None`
**説明**: タイマーを開始する

**パラメータ**:
- `callback` (Callable[[], None]): タイムアウト時に実行されるコールバック

**使用例**:
```python
timer.start_timer(lambda: print("タイムアウト"))
```

##### `reset_timer() -> None`
**説明**: タイマーをリセットする

**使用例**:
```python
timer.reset_timer()
```

##### `stop_timer() -> None`
**説明**: タイマーを停止する

**使用例**:
```python
timer.stop_timer()
```

### 2.4 MIDIMonitor

#### 概要
MIDI受信、ファイル書き出し、タイマー機能を統合するメインクラス。

#### クラス定義
```python
class MIDIMonitor:
    def __init__(self, port_name: str, output_directory: str, timeout_seconds: int = 300) -> None
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> None
    def save_current_buffer(self) -> Optional[str]
    def has_buffered_events(self) -> bool
```

#### メソッド詳細

##### `__init__(port_name: str, output_directory: str, timeout_seconds: int = 300) -> None`
**説明**: MIDIMonitorを初期化する

**パラメータ**:
- `port_name` (str): MIDIポート名
- `output_directory` (str): 出力ディレクトリ
- `timeout_seconds` (int): タイムアウト時間（秒）

**使用例**:
```python
monitor = MIDIMonitor("IAC Driver Bus 1", "./recordings", 300)
```

##### `start_monitoring() -> None`
**説明**: 監視を開始する

**例外**:
- `MIDIError`: MIDIポートのオープンに失敗した場合

**使用例**:
```python
monitor.start_monitoring()
```

##### `stop_monitoring() -> None`
**説明**: 監視を停止する

**使用例**:
```python
monitor.stop_monitoring()
```

##### `save_current_buffer() -> Optional[str]`
**説明**: 現在のバッファを保存する

**戻り値**: 保存されたファイルパス（バッファが空の場合はNone）

**使用例**:
```python
filepath = monitor.save_current_buffer()
```

##### `has_buffered_events(self) -> bool`
**説明**: バッファにイベントがあるかチェックする

**戻り値**: イベントがある場合True

**使用例**:
```python
if monitor.has_buffered_events():
    monitor.save_current_buffer()
```

### 2.5 Logger

#### 概要
システムのログを管理するクラス。

#### クラス定義
```python
class Logger:
    def __init__(self, log_file: str = "midi_recorder.log") -> None
    def log_file_saved(self, filename: str) -> None
    def log_recording_started(self) -> None
    def log_recording_stopped(self) -> None
    def log_error(self, error_message: str) -> None
```

#### メソッド詳細

##### `__init__(log_file: str = "midi_recorder.log") -> None`
**説明**: Loggerを初期化する

**パラメータ**:
- `log_file` (str): ログファイルパス

**使用例**:
```python
logger = Logger("./logs/midi_recorder.log")
```

##### `log_file_saved(filename: str) -> None`
**説明**: ファイル保存完了をログに記録する

**パラメータ**:
- `filename` (str): 保存されたファイル名

**使用例**:
```python
logger.log_file_saved("20240101123045.mid")
```

##### `log_recording_started() -> None`
**説明**: 録音開始をログに記録する

**使用例**:
```python
logger.log_recording_started()
```

##### `log_recording_stopped() -> None`
**説明**: 録音停止をログに記録する

**使用例**:
```python
logger.log_recording_stopped()
```

##### `log_error(error_message: str) -> None`
**説明**: エラーをログに記録する

**パラメータ**:
- `error_message` (str): エラーメッセージ

**使用例**:
```python
logger.log_error("MIDIポートが見つかりません")
```

### 2.6 ConfigManager

#### 概要
設定ファイルを管理するクラス。

#### クラス定義
```python
class ConfigManager:
    def __init__(self, config_file: str = "config.yaml") -> None
    def load_config(self) -> Dict[str, Any]
    def get_midi_config(self) -> Dict[str, Any]
    def get_output_config(self) -> Dict[str, Any]
    def get_gui_config(self) -> Dict[str, Any]
```

#### メソッド詳細

##### `__init__(config_file: str = "config.yaml") -> None`
**説明**: ConfigManagerを初期化する

**パラメータ**:
- `config_file` (str): 設定ファイルパス

**使用例**:
```python
config_manager = ConfigManager("config/config.yaml")
```

##### `load_config() -> Dict[str, Any]`
**説明**: 設定ファイルを読み込む

**戻り値**: 設定データの辞書

**例外**:
- `ConfigError`: 設定ファイルの読み込みに失敗した場合

**使用例**:
```python
config = config_manager.load_config()
```

##### `get_midi_config() -> Dict[str, Any]`
**説明**: MIDI設定を取得する

**戻り値**: MIDI設定の辞書

**使用例**:
```python
midi_config = config_manager.get_midi_config()
```

##### `get_output_config() -> Dict[str, Any]`
**説明**: 出力設定を取得する

**戻り値**: 出力設定の辞書

**使用例**:
```python
output_config = config_manager.get_output_config()
```

##### `get_gui_config() -> Dict[str, Any]`
**説明**: GUI設定を取得する

**戻り値**: GUI設定の辞書

**使用例**:
```python
gui_config = config_manager.get_gui_config()
```

## 3. エラー定義

### 3.1 カスタム例外クラス

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

class TimerError(Exception):
    """タイマー関連のエラー"""
    pass
```

## 4. データ構造

### 4.1 MIDIメッセージ構造
```python
# mido.Messageの主要属性
message.type          # メッセージタイプ (note_on, note_off, control_change等)
message.channel       # MIDIチャンネル (0-15)
message.note          # ノート番号 (0-127)
message.velocity      # ベロシティ (0-127)
message.control       # コントロール番号
message.value         # コントロール値
message.time          # タイムスタンプ
```

### 4.2 設定ファイル構造
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

## 5. 使用例

### 5.1 基本的な使用例
```python
from src.midi.monitor import MIDIMonitor
from src.config.manager import ConfigManager

# 設定を読み込み
config_manager = ConfigManager("config/config.yaml")
config = config_manager.load_config()

# 監視を開始
monitor = MIDIMonitor(
    port_name=config["midi"]["port_name"],
    output_directory=config["output"]["directory"],
    timeout_seconds=config["midi"]["timeout_seconds"]
)

monitor.start_monitoring()

# 手動で保存
if monitor.has_buffered_events():
    filepath = monitor.save_current_buffer()
    print(f"保存完了: {filepath}")

monitor.stop_monitoring()
```

### 5.2 GUIとの統合例
```python
import flet as ft
from src.midi.monitor import MIDIMonitor

class MIDIGUI:
    def __init__(self, monitor: MIDIMonitor):
        self.monitor = monitor
    
    def manual_save(self, e):
        if self.monitor.has_buffered_events():
            filepath = self.monitor.save_current_buffer()
            # GUIに保存完了を表示
```

## 6. パフォーマンス仕様

### 6.1 メモリ使用量
- 最大1GBまでのメモリ使用量
- イベントバッファは定期的にクリア

### 6.2 応答時間
- MIDIメッセージ受信: 1ms以下
- ファイル書き込み: 100ms以下
- GUI応答: 50ms以下

### 6.3 スループット
- 最大1000 MIDIメッセージ/秒
- 同時接続可能デバイス数: 1（Phase 1）

## 7. セキュリティ考慮事項

### 7.1 ファイルアクセス
- 出力ディレクトリの権限確認
- ファイル書き込み時のエラーハンドリング

### 7.2 メモリ管理
- バッファサイズの制限
- 定期的なメモリクリア

### 7.3 エラー処理
- 例外の適切な捕捉とログ記録
- システムクラッシュ時のデータ保護 
