# Phase 1 実装計画

## 1. 実装フェーズ

### Phase 1.1: コア機能開発（Week 1-2）
**目標**: MIDIイベントの受信とファイル保存の基本機能を実装

#### 1.1.1 MIDI受信機能（Week 1前半）
- [ ] **midoライブラリの基本動作確認**
  - 利用可能なMIDIポートの一覧取得
  - 基本的なMIDIメッセージ受信テスト
  - 複数デバイスでの動作確認

- [ ] **MIDIイベント受信クラスの実装**
  ```python
  class MIDIReceiver:
      def __init__(self, port_name: str):
          self.port_name = port_name
          self.messages = []
          self.is_recording = False
      
      def start_recording(self):
          # MIDI受信開始
      
      def stop_recording(self):
          # MIDI受信停止
      
      def get_messages(self):
          # 蓄積されたメッセージを取得
  ```

#### 1.1.2 ファイル保存機能（Week 1後半）
- [ ] **MIDIファイル書き出し機能の実装**
  ```python
  class MIDIFileWriter:
      def __init__(self, output_directory: str):
          self.output_directory = output_directory
      
      def write_messages(self, messages: List[mido.Message], filename: str):
          # MIDIファイルにメッセージを書き出し
  ```

- [ ] **自動ファイル名生成機能**
  - yyyymmddhhmmss.mid形式
  - 重複ファイル名の処理

#### 1.1.3 タイマー機能（Week 2前半）
- [ ] **自動保存タイマーの実装**
  ```python
  class AutoSaveTimer:
      def __init__(self, timeout_seconds: int = 300):
          self.timeout_seconds = timeout_seconds
          self.timer = None
      
      def reset_timer(self):
          # タイマーをリセット
      
      def start_timer(self, callback):
          # タイマーを開始
  ```

#### 1.1.4 統合機能（Week 2後半）
- [ ] **MIDI監視システムの統合**
  ```python
  class MIDIMonitor:
      def __init__(self, port_name: str, output_directory: str, timeout_seconds: int = 300):
          self.receiver = MIDIReceiver(port_name)
          self.writer = MIDIFileWriter(output_directory)
          self.timer = AutoSaveTimer(timeout_seconds)
      
      def start_monitoring(self):
          # 監視開始
      
      def stop_monitoring(self):
          # 監視停止
  ```

### Phase 1.2: 基本GUI開発（Week 3）
**目標**: 最小限のGUIで録音停止・保存機能を実装

#### 1.2.1 flet GUI基本実装（Week 3前半）
- [ ] **flet 0.28.3の動作確認**
  - 基本的なウィンドウ表示
  - ボタンクリックイベントの処理
  - 非同期処理の確認

- [ ] **基本GUIレイアウトの実装**
  ```python
  class MIDIGUI:
      def __init__(self, monitor: MIDIMonitor):
          self.monitor = monitor
          self.page = None
      
      def main(self, page: ft.Page):
          # 基本レイアウトの実装
  ```

#### 1.2.2 録音制御機能（Week 3後半）
- [ ] **録音停止・保存ボタンの実装**
  - 録音状態の表示
  - 手動保存機能
  - エラー表示機能

### Phase 1.3: 設定・ログ機能（Week 4）
**目標**: 設定ファイル管理とログ機能を実装

#### 1.3.1 設定ファイル管理（Week 4前半）
- [ ] **設定ファイルの設計**
  ```yaml
  # config.yaml
  midi:
    port_name: "default"
    timeout_seconds: 300
  
  output:
    directory: "./recordings"
  
  gui:
    window_title: "MIDI Recording System"
    theme_mode: "light"
  ```

- [ ] **設定読み込み機能の実装**
  ```python
  class ConfigManager:
      def __init__(self, config_file: str = "config.yaml"):
          self.config_file = config_file
      
      def load_config(self):
          # 設定ファイルを読み込み
      
      def get_midi_config(self):
          # MIDI設定を取得
  ```

#### 1.3.2 ログ機能（Week 4後半）
- [ ] **ログ機能の実装**
  ```python
  class Logger:
      def __init__(self, log_file: str = "midi_recorder.log"):
          self.log_file = log_file
      
      def log_file_saved(self, filename: str):
          # ファイル保存完了のログ
      
      def log_recording_started(self):
          # 録音開始のログ
      
      def log_recording_stopped(self):
          # 録音停止のログ
      
      def log_error(self, error_message: str):
          # エラーログ
  ```

### Phase 1.4: エラーハンドリング・テスト（Week 5）
**目標**: 堅牢性の確保とテストの実施

#### 1.4.1 エラーハンドリング（Week 5前半）
- [ ] **データ保護機能の実装**
  - システムクラッシュ時のデータ保護
  - ファイル書き込みエラーの処理
  - MIDIデバイス切断時の処理

- [ ] **復旧機能の実装**
  - 自動再起動機能
  - エラー時の適切なフィードバック

#### 1.4.2 テスト実施（Week 5後半）
- [ ] **単体テスト**
  - MIDI受信機能のテスト
  - ファイル書き出し機能のテスト
  - タイマー機能のテスト

- [ ] **統合テスト**
  - エンドツーエンドの録音テスト
  - 長時間動作テスト（24時間）
  - エラー復旧テスト

## 2. 技術的詳細

### 2.1 ディレクトリ構造
```
round_the_clock_midi_recording/
├── src/
│   ├── __init__.py
│   ├── midi/
│   │   ├── __init__.py
│   │   ├── receiver.py
│   │   ├── writer.py
│   │   └── monitor.py
│   ├── gui/
│   │   ├── __init__.py
│   │   └── main_window.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── manager.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── timer.py
├── config/
│   └── config.yaml
├── logs/
│   └── midi_recorder.log
├── recordings/
│   └── (自動生成されるMIDIファイル)
├── tests/
│   ├── __init__.py
│   ├── test_midi_receiver.py
│   ├── test_file_writer.py
│   └── test_integration.py
├── main.py
├── pyproject.toml
└── README.md
```

### 2.2 主要クラス設計

#### MIDIReceiver
```python
class MIDIReceiver:
    def __init__(self, port_name: str):
        self.port_name = port_name
        self.messages = []
        self.is_recording = False
        self.port = None
    
    def start_recording(self):
        """MIDI受信開始"""
        try:
            self.port = mido.open_input(self.port_name)
            self.is_recording = True
            # 非同期でメッセージ受信開始
        except Exception as e:
            raise MIDIError(f"Failed to open MIDI port: {e}")
    
    def stop_recording(self):
        """MIDI受信停止"""
        self.is_recording = False
        if self.port:
            self.port.close()
    
    def get_messages(self):
        """蓄積されたメッセージを取得"""
        messages = self.messages.copy()
        self.messages.clear()
        return messages
```

#### MIDIFileWriter
```python
class MIDIFileWriter:
    def __init__(self, output_directory: str):
        self.output_directory = output_directory
        os.makedirs(output_directory, exist_ok=True)
    
    def write_messages(self, messages: List[mido.Message], filename: str = None):
        """MIDIファイルにメッセージを書き出し"""
        if not filename:
            filename = self._generate_filename()
        
        filepath = os.path.join(self.output_directory, filename)
        
        mid = mido.MidiFile()
        track = mido.MidiTrack()
        mid.tracks.append(track)
        
        for msg in messages:
            track.append(msg)
        
        mid.save(filepath)
        return filepath
    
    def _generate_filename(self):
        """自動ファイル名生成"""
        return datetime.now().strftime("%Y%m%d%H%M%S") + ".mid"
```

#### MIDIMonitor
```python
class MIDIMonitor:
    def __init__(self, port_name: str, output_directory: str, timeout_seconds: int = 300):
        self.receiver = MIDIReceiver(port_name)
        self.writer = MIDIFileWriter(output_directory)
        self.timer = AutoSaveTimer(timeout_seconds)
        self.logger = Logger()
    
    def start_monitoring(self):
        """監視開始"""
        self.receiver.start_recording()
        self.timer.start_timer(self._auto_save)
        self.logger.log_recording_started()
    
    def stop_monitoring(self):
        """監視停止"""
        self.receiver.stop_recording()
        self.timer.stop_timer()
        self._save_current_buffer()
        self.logger.log_recording_stopped()
    
    def _auto_save(self):
        """自動保存処理"""
        messages = self.receiver.get_messages()
        if messages:
            filepath = self.writer.write_messages(messages)
            self.logger.log_file_saved(filepath)
```

## 3. 成功基準

### 3.1 機能的な成功基準
- [ ] MIDIデバイスから正常にデータを受信できる
- [ ] 5分間イベントなしで自動的にファイルに保存される
- [ ] **最重要**: イベント列が確実にファイルに保存される
- [ ] GUIから録音停止・保存ができる
- [ ] 設定ファイルで動作を制御できる
- [ ] 必要なログが適切に出力される

### 3.2 非機能的な成功基準
- [ ] 24時間連続動作が可能
- [ ] メモリ使用量が1GB以下に収まる
- [ ] エラー時に適切に復旧できる
- [ ] システムクラッシュ時にデータが保護される

## 4. リスク対策

### 4.1 技術リスク
- **midoライブラリの制限**: 複数デバイスでのテスト実施
- **データ損失リスク**: 複数の保存方法とエラーハンドリング強化
- **メモリリーク**: 定期的なメモリ監視とクリア機能

### 4.2 スケジュールリスク
- **初回開発の複雑性**: 週次での進捗確認とスコープ調整
- **予想外の技術的問題**: バッファ時間の確保

## 5. 次のアクション

### 5.1 即座に実行可能
1. **環境セットアップ**
   ```bash
   # uvのインストール確認
   uv --version
   
   # プロジェクトの初期化
   uv init
   
   # 依存関係の追加
   uv add mido>=1.3.3
   uv add flet==0.28.3
   
   # 仮想環境のアクティベート
   uv sync
   ```

2. **プロジェクト構造の作成**
   - ディレクトリ構造の作成
   - 基本ファイルの作成

3. **MIDI受信機能のプロトタイプ**
   - midoライブラリの基本動作確認
   - 簡単なMIDI受信テスト

### 5.2 並行して進める
1. **テスト計画の詳細化**
2. **ドキュメント作成**
3. **設定ファイル設計の詳細化** 
