# 技術仕様書

## 1. システムアーキテクチャ

### 1.1 全体構成
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   MIDI Device   │───▶│  MIDI Receiver  │───▶│  Event Buffer   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Device Manager │    │  Auto Writer    │
                       └─────────────────┘    └─────────────────┘
                                │                       │
                                ▼                       ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  System Monitor │    │  File Manager   │
                       └─────────────────┘    └─────────────────┘
```

### 1.2 コンポーネント構成
- **MIDI Receiver**: midoライブラリを使用したMIDIデータ受信
- **Device Manager**: MIDIデバイスの検出・管理
- **Event Buffer**: 受信イベントのメモリ蓄積
- **Auto Writer**: 一定時間イベントなし時の自動ファイル書き出し
- **System Monitor**: システム状態の監視
- **File Manager**: ファイル出力・管理

## 2. データ構造

### 2.1 MIDIメッセージ構造
```python
class MIDIMessage:
    type: str           # メッセージタイプ (note_on, note_off, control_change等)
    channel: int        # MIDIチャンネル (0-15)
    note: int          # ノート番号 (0-127)
    velocity: int      # ベロシティ (0-127)
    control: int       # コントロール番号
    value: int         # コントロール値
    time: float        # タイムスタンプ
```

### 2.2 イベントバッファ構造
```python
class EventBuffer:
    messages: List[MIDIMessage]  # MIDIメッセージリスト
    last_event_time: float       # 最後のイベント受信時刻
    device_name: str            # MIDIデバイス名
    buffer_size: int            # バッファサイズ
    is_active: bool             # バッファがアクティブかどうか
```

### 2.3 記録データ構造
```python
class RecordedData:
    timestamp: datetime # 記録時刻
    device_name: str   # MIDIデバイス名
    messages: List[MIDIMessage]  # MIDIメッセージリスト
    duration: float    # 記録時間
    file_path: str     # 保存ファイルパス
```

## 3. ファイルフォーマット

### 3.1 MIDIファイル形式
- 標準MIDIファイル（.mid）形式での出力
- タイムスタンプ情報の保持
- マルチトラック対応
- 自動ファイル名生成（例: `20240101123045.mid`）

## 4. 実装詳細

### 4.1 MIDI受信処理
```python
import mido
import time
from threading import Timer

class MIDIMonitor:
    def __init__(self, timeout_seconds: int = 300):  # デフォルト5分
        self.timeout_seconds = timeout_seconds
        self.event_buffer = []
        self.last_event_time = None
        self.timer = None
    
    def start_monitoring(self, port_name: str):
        with mido.open_input(port_name) as port:
            for message in port:
                self.process_midi_message(message)
    
    def process_midi_message(self, message):
        self.event_buffer.append(message)
        self.last_event_time = time.time()
        self.reset_timer()
    
    def reset_timer(self):
        if self.timer:
            self.timer.cancel()
        self.timer = Timer(self.timeout_seconds, self.write_and_clear)
        self.timer.start()
    
    def write_and_clear(self):
        if self.event_buffer:
            self.write_to_file()
            self.clear_buffer()
```

### 4.2 自動ファイル書き出し処理
```python
class AutoWriter:
    def __init__(self, output_directory: str = "./recordings"):
        self.output_directory = output_directory
    
    def write_to_file(self, messages: List[MIDIMessage], device_name: str):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}.mid"
        filepath = os.path.join(self.output_directory, filename)
        
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        for msg in messages:
            track.append(msg)
        
        mid.save(filepath)
        return filepath
```

### 4.3 システム監視処理
```python
class SystemMonitor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def monitor_system_status(self):
        # メモリ使用量の監視
        # ファイル書き込み状況の監視
        # エラーログの記録
        pass
    
    def log_event(self, event_type: str, message: str):
        self.logger.info(f"{event_type}: {message}")
```

### 4.6 ストレージ管理機能（将来拡張予定）
```python
class StorageManager:
    def __init__(self, config):
        self.config = config
        self.local_storage = LocalStorage(config)
        # self.network_storage = NetworkStorage(config)  # 将来実装予定
    
    def save_to_local(self, messages, filename):
        """ローカルストレージに保存"""
        return self.local_storage.save(messages, filename)
    
    def save_to_network(self, messages, filename):
        """ネットワークストレージに保存（将来実装予定）"""
        # TODO: ネットワークストレージの仕様が決まったら実装
        # return self.network_storage.save(messages, filename)
        pass
    
    def save_to_all_storages(self, messages, filename):
        """全ストレージに保存"""
        local_result = self.save_to_local(messages, filename)
        network_result = self.save_to_network(messages, filename)
        return local_result, network_result

class LocalStorage:
    def __init__(self, config):
        self.output_directory = config.get('system.output_directory', './recordings')
        self.manual_save_directory = config.get('system.manual_save_directory', './manual_saves')
    
    def save(self, messages, filename):
        """ローカルストレージに保存"""
        # 既存の保存ロジック
        pass

# class NetworkStorage:
#     """ネットワークストレージクラス（将来実装予定）"""
#     def __init__(self, config):
#         self.network_config = config.get('network_storage', {})
#     
#     def save(self, messages, filename):
#         """ネットワークストレージに保存"""
#         # TODO: ネットワークストレージの仕様に応じて実装
#         pass
```

### 4.4 GUI機能の実装
```python
import flet as ft
import os
import shutil
from datetime import datetime

class MIDIGUI:
    def __init__(self, recorder, config):
        self.recorder = recorder
        self.config = config
        self.page = None
    
    def main(self, page: ft.Page):
        self.page = page
        self.page.title = self.config.get('gui.window_title', 'MIDI Recording System')
        self.page.window_width = 400
        self.page.window_height = 300
        self.page.padding = 20
        self.page.theme_mode = self.config.get('gui.theme_mode', 'light')
        
        # 手動保存ボタン
        self.save_button = ft.ElevatedButton(
            text="手動保存",
            on_click=self.manual_save,
            width=200,
            height=50
        )
        
        # 状態表示テキスト
        self.status_text = ft.Text(
            value="録音待機中...",
            size=16,
            text_align=ft.TextAlign.CENTER
        )
        
        # レイアウト
        self.page.add(
            ft.Column(
                controls=[
                    self.save_button,
                    ft.Divider(),
                    self.status_text
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=20
            )
        )
    
    async def manual_save(self, e):
        """手動保存機能"""
        try:
            # 現在の録音状態を確認
            if self.recorder.has_buffered_events():
                # バッファにイベントがある場合
                filepath = self.recorder.save_current_buffer()
                await self.show_save_success(filepath)
            else:
                # バッファが空の場合、最後のファイルをコピー
                last_file = self.recorder.get_last_saved_file()
                if last_file and os.path.exists(last_file):
                    new_filepath = self.copy_last_file(last_file)
                    await self.show_save_success(new_filepath)
                else:
                    await self.show_warning("保存可能なファイルが見つかりません")
        except Exception as e:
            await self.show_error(f"保存中にエラーが発生しました: {str(e)}")
    
    def copy_last_file(self, last_file):
        """最後のファイルを手動保存先にコピー"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"manual_save_{timestamp}.mid"
        manual_save_dir = self.config.get('system.manual_save_directory', './manual_saves')
        
        os.makedirs(manual_save_dir, exist_ok=True)
        new_filepath = os.path.join(manual_save_dir, filename)
        shutil.copy2(last_file, new_filepath)
        return new_filepath
    
    async def show_save_success(self, filepath):
        """保存完了メッセージを表示"""
        await self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(f"ファイルが保存されました: {filepath}"),
                action="OK"
            )
        )
    
    async def show_warning(self, message):
        """警告メッセージを表示"""
        await self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                action="OK",
                bgcolor=ft.colors.YELLOW
            )
        )
    
    async def show_error(self, message):
        """エラーメッセージを表示"""
        await self.page.show_snack_bar(
            ft.SnackBar(
                content=ft.Text(message),
                action="OK",
                bgcolor=ft.colors.RED
            )
        )
    
    def update_status(self, status_text):
        """状態表示を更新"""
        self.status_text.value = status_text
        self.page.update()
    
    def run(self):
        """GUIを実行"""
        ft.app(target=self.main)
```

### 4.5 手動保存機能の拡張
```python
class MIDIRecorder:
    def __init__(self, output_format: str = "midi"):
        self.output_format = output_format
        self.messages = []
        self.start_time = None
        self.last_saved_file = None
    
    def has_buffered_events(self):
        """バッファにイベントがあるかチェック"""
        return len(self.messages) > 0
    
    def save_current_buffer(self):
        """現在のバッファを保存"""
        if not self.messages:
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        filename = f"manual_save_{timestamp}.mid"
        manual_save_dir = self.config.get('system.manual_save_directory', './manual_saves')
        
        os.makedirs(manual_save_dir, exist_ok=True)
        filepath = os.path.join(manual_save_dir, filename)
        
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        for msg in self.messages:
            track.append(msg)
        
        mid.save(filepath)
        self.last_saved_file = filepath
        self.messages.clear()
        return filepath
    
    def get_last_saved_file(self):
        """最後に保存したファイルのパスを取得"""
        return self.last_saved_file
```

## 5. 設定管理

### 5.1 設定ファイル構造
```yaml
# config.yaml
system:
  timeout_seconds: 300  # イベントなし検出時間（秒）
  output_directory: "./recordings"
  manual_save_directory: "./manual_saves"  # 手動保存先ディレクトリ
  log_level: "INFO"

devices:
  auto_detect: true
  preferred_devices: []  # リストの最初のデバイスが最も優先度が高い

monitoring:
  memory_limit_mb: 1024  # 1GB
  log_rotation_days: 7
  auto_restart: true

gui:
  enabled: true
  window_title: "MIDI Recording System"
  window_width: 400
  window_height: 300
  theme_mode: "light"  # light, dark, system

# network_storage:  # 将来実装予定
#   enabled: false
#   type: "ftp"  # ftp, sftp, webdav, s3, etc.
#   host: "example.com"
#   port: 21
#   username: "user"
#   password: "password"
#   remote_directory: "/midi_files"
#   auto_sync: true
```

### 5.2 デバイス優先順位の処理
```python
class DeviceManager:
    def __init__(self, preferred_devices: List[str]):
        self.preferred_devices = preferred_devices
        self.selected_device = None
    
    def get_connected_devices(self):
        """接続中のMIDIデバイス一覧を取得"""
        return mido.get_input_names()
    
    def select_device(self):
        """接続中のデバイス一覧から優先順位に基づいてデバイスを選択"""
        connected_devices = self.get_connected_devices()
        
        if not connected_devices:
            return None
        
        # 優先デバイスリストの順序で接続を試行
        for device in self.preferred_devices:
            if device in connected_devices:
                self.selected_device = device
                return device
        
        # 優先デバイスが見つからない場合、最初の接続デバイスを使用
        self.selected_device = connected_devices[0]
        return connected_devices[0]
    
    def get_selected_device(self):
        """選択されたデバイスを取得（選択後は常に同じデバイスを使用）"""
        if self.selected_device is None:
            return self.select_device()
        return self.selected_device
```

## 6. エラーハンドリング

### 6.1 エラー種別
- **DeviceNotFoundError**: MIDIデバイスが見つからない
- **PermissionError**: ファイル書き込み権限がない
- **DiskSpaceError**: ディスク容量不足
- **MemoryError**: メモリ不足
- **ConnectionError**: MIDI接続エラー
- **DeviceDisconnectionError**: MIDIデバイス切断エラー

### 6.2 エラー処理方針
```python
def handle_midi_error(error):
    if isinstance(error, DeviceNotFoundError):
        log_error("MIDI device not found, waiting for reconnection")
        wait_for_reconnection()
    elif isinstance(error, DeviceDisconnectionError):
        log_error("MIDI device disconnected, attempting reconnection")
        handle_device_disconnection()
    elif isinstance(error, MemoryError):
        log_error("Memory limit reached, forcing file write")
        force_write_and_clear()
    elif isinstance(error, PermissionError):
        log_error("Permission error, trying alternative directory")
        change_output_directory()
    else:
        log_error(error)
        continue_monitoring()
```

### 6.3 デバイス再接続機能
```python
class DeviceReconnectionManager:
    def __init__(self):
        self.max_reconnection_attempts = 3
        self.reconnection_timeout = 30.0
        self.check_interval = 1.0
    
    def wait_for_reconnection(self, port_name: str) -> bool:
        """デバイスの再接続を待機する"""
        start_time = time.time()
        while time.time() - start_time < self.reconnection_timeout:
            if self.is_port_available(port_name):
                return True
            time.sleep(self.check_interval)
        return False
    
    def find_alternative_port(self, original_port: str) -> Optional[str]:
        """代替ポートを探す"""
        available_ports = self.get_available_ports()
        if not available_ports:
            return None
        
        # 同じ名前のポートを優先
        for port in available_ports:
            if port == original_port:
                return port
        
        # 代替ポートを返す
        return available_ports[0] if available_ports else None
```

### 6.4 プラットフォーム固有の処理
```python
def setup_platform_backend():
    """プラットフォームに応じたMIDIバックエンドを設定"""
    system = platform.system()
    
    if system == "Darwin":  # macOS
        import rtmidi
        if hasattr(rtmidi, "API_MACOSX_CORE"):
            rtmidi.MidiIn(rtmidi.API_MACOSX_CORE)
        mido.set_backend("mido.backends.rtmidi")
    
    elif system == "Linux":  # Linux (Raspberry Pi含む)
        try:
            mido.set_backend("mido.backends.alsa")
        except Exception:
            try:
                mido.set_backend("mido.backends.portmidi")
            except Exception:
                pass
    
    else:  # Windowsその他
        # デフォルトバックエンドを使用
        pass
```

## 7. 性能要件

### 7.1 処理性能
- イベントなし検出精度: ±1秒
- ファイル書き込み時間: < 5秒
- メモリ使用量: < 1GB（長時間動作時）

### 7.2 スケーラビリティ
- 同時監視デバイス数: 最大1個
- 記録時間: 無制限（ディスク容量依存）
- ファイルサイズ: 最大2GB

## 8. セキュリティ考慮事項

### 8.1 データ保護
- 記録データの適切なアクセス権限設定
- ログファイルの適切な管理
- ファイル名のセキュリティ考慮

### 8.2 プライバシー
- 個人情報の記録回避
- ログファイルの適切な管理

## 9. テスト仕様

### 9.1 単体テスト
- MIDIメッセージ処理のテスト
- ファイル出力機能のテスト
- タイマー機能のテスト
- エラーハンドリングのテスト

### 9.2 統合テスト
- 実際のMIDIデバイスでの動作テスト
- 長時間動作の安定性テスト
- 複数デバイス同時監視テスト

### 9.3 性能テスト
- メモリリークテスト
- ファイルI/O性能テスト
- 長時間動作テスト 
