# 運用マニュアル

## 1. 概要

### 1.1 目的
このドキュメントは、Round the Clock MIDI Recording Systemの運用方法を説明します。

### 1.2 対象読者
- システム管理者
- エンドユーザー
- サポート担当者

## 2. システム概要

### 2.1 システム構成
```
Round the Clock MIDI Recording System
├── MIDIデバイス
├── MIDI受信モジュール
├── イベントバッファ
├── 自動保存タイマー
├── ファイル書き出しモジュール
├── GUIインターフェース
└── ログ管理モジュール
```

### 2.2 主要機能
- MIDIデバイスからのリアルタイムデータ受信
- 一定時間イベントなし時の自動ファイル保存
- 手動録音停止・保存機能
- システム状態の監視・ログ記録

## 3. インストール・セットアップ

### 3.1 前提条件
- macOS 14.0以上
- Python 3.10以上
- uv（Pythonパッケージマネージャー）
- MIDIデバイスまたは仮想MIDIデバイス

### 3.2 インストール手順
```bash
# 1. プロジェクトディレクトリに移動
git clone git@github.com:KateSawada/round_the_clock_midi_recording.git
cd round_the_clock_midi_recording

# 2. 依存関係のインストール
uv sync

# 3. 開発用依存関係のインストール（開発者のみ）
uv add --dev pytest black flake8 mypy

# 4. プロジェクト構造の作成
mkdir -p src/midi src/gui src/config src/utils
mkdir -p config logs recordings tests
touch src/__init__.py src/midi/__init__.py src/gui/__init__.py src/config/__init__.py src/utils/__init__.py tests/__init__.py
```

### 3.3 初期設定
```bash
# 1. 設定ファイルの作成
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

# 2. ログディレクトリの作成
mkdir -p logs
touch logs/midi_recorder.log

# 3. 録音ディレクトリの作成
mkdir -p recordings
```

## 4. 起動・停止

### 4.1 システム起動
```bash
# 基本的な起動
uv run python main.py

# デバッグモードでの起動
uv run python main.py --debug

# 設定ファイルを指定して起動
uv run python main.py --config config/custom_config.yaml
```

### 4.2 システム停止
- **GUIからの停止**: 録音停止ボタンをクリック
- **コマンドラインからの停止**: Ctrl+C
- **強制停止**: プロセスを強制終了

### 4.3 自動起動設定（macOS）
```bash
# 1. LaunchAgentの作成
mkdir -p ~/Library/LaunchAgents

# 2. plistファイルの作成
cat > ~/Library/LaunchAgents/com.midi.recorder.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.midi.recorder</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/uv</string>
        <string>run</string>
        <string>python</string>
        <string>main.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/ks/Documents/wolf/round_the_clock_midi_recording</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# 3. LaunchAgentの読み込み
launchctl load ~/Library/LaunchAgents/com.midi.recorder.plist
```

## 5. 日常運用

### 5.1 システム監視

#### 5.1.1 ログ監視
```bash
# リアルタイムログ監視
tail -f logs/midi_recorder.log

# エラーログの確認
grep "ERROR" logs/midi_recorder.log

# 今日のログ確認
grep "$(date +%Y-%m-%d)" logs/midi_recorder.log
```

#### 5.1.2 プロセス監視
```bash
# プロセス確認
ps aux | grep python | grep main.py

# メモリ使用量確認
top -pid $(pgrep -f "python main.py")

# ファイルディスクリプタ確認
lsof -p $(pgrep -f "python main.py")
```

#### 5.1.3 ディスク使用量監視
```bash
# 録音ファイルの容量確認
du -sh recordings/

# ログファイルの容量確認
du -sh logs/

# 全体のディスク使用量確認
df -h
```

### 5.2 録音ファイル管理

#### 5.2.1 ファイル確認
```bash
# 録音ファイル一覧
ls -la recordings/

# 今日録音されたファイル
find recordings/ -name "*.mid" -newermt "$(date +%Y-%m-%d)" -ls

# ファイルサイズ順でソート
ls -la recordings/*.mid | sort -k5 -n
```

#### 5.2.2 ファイル整理
```bash
# 古いファイルの移動（30日以上前）
find recordings/ -name "*.mid" -mtime +30 -exec mv {} archive/ \;

# 空ファイルの削除
find recordings/ -name "*.mid" -size 0 -delete

# 重複ファイルの確認
fdupes -r recordings/
```

#### 5.2.3 バックアップ
```bash
# 日次バックアップ
rsync -av recordings/ /backup/midi_recordings/$(date +%Y-%m-%d)/

# 週次バックアップ
tar -czf /backup/midi_recordings_week_$(date +%V).tar.gz recordings/
```

### 5.3 設定管理

#### 5.3.1 設定変更
```bash
# 設定ファイルの編集
vim config/config.yaml

# 設定変更後の再起動
pkill -f "python main.py"
uv run python main.py
```

#### 5.3.2 設定バックアップ
```bash
# 設定ファイルのバックアップ
cp config/config.yaml config/config.yaml.backup.$(date +%Y%m%d)

# 設定履歴の管理
git add config/config.yaml
git commit -m "設定変更: $(date)"
```

## 6. トラブルシューティング

### 6.1 よくある問題と解決方法

#### 6.1.1 MIDIデバイスが認識されない
**症状**: システム起動時にMIDIポートエラーが発生

**確認手順**:
```bash
# 利用可能なMIDIポートの確認
uv run python -c "import mido; print('Available ports:', mido.get_input_names())"

# Audio MIDI Setupの確認
open -a "Audio MIDI Setup"
```

**解決方法**:
1. Audio MIDI SetupでMIDIデバイスを確認
2. 設定ファイルのport_nameを正しいポート名に変更
3. システムを再起動

#### 6.1.2 ファイル書き込みエラー
**症状**: 録音ファイルが保存されない

**確認手順**:
```bash
# ディレクトリの権限確認
ls -la recordings/

# ディスク容量確認
df -h

# ログファイルの確認
tail -n 50 logs/midi_recorder.log
```

**解決方法**:
1. ディレクトリの権限を修正: `chmod 755 recordings/`
2. ディスク容量を確保
3. 設定ファイルの出力ディレクトリを確認

#### 6.1.3 メモリ使用量が高い
**症状**: システムが重くなる、メモリエラーが発生

**確認手順**:
```bash
# メモリ使用量確認
ps aux | grep python | grep main.py

# メモリリークの確認
top -pid $(pgrep -f "python main.py")
```

**解決方法**:
1. システムを再起動
2. バッファサイズの設定を調整
3. ログレベルを下げる

#### 6.1.4 GUIが表示されない
**症状**: GUIウィンドウが開かない

**確認手順**:
```bash
# fletの動作確認
uv run python -c "import flet; print('flet version:', flet.__version__)"

# ディスプレイ設定確認
echo $DISPLAY
```

**解決方法**:
1. fletライブラリを再インストール: `uv sync --reinstall`
2. システムを再起動
3. コマンドライン版で動作確認

### 6.2 ログ分析

#### 6.2.1 ログレベルの変更
```bash
# 設定ファイルでログレベルを変更
vim config/config.yaml
# logging:
#   level: "DEBUG"  # INFOからDEBUGに変更
```

#### 6.2.2 ログローテーション
```bash
# ログローテーションスクリプト
cat > rotate_logs.sh << 'EOF'
#!/bin/bash
LOG_FILE="logs/midi_recorder.log"
DATE=$(date +%Y%m%d_%H%M%S)

if [ -f "$LOG_FILE" ]; then
    mv "$LOG_FILE" "logs/midi_recorder_$DATE.log"
    touch "$LOG_FILE"
fi
EOF

chmod +x rotate_logs.sh

# cronで定期実行（毎日午前0時）
echo "0 0 * * * /path/to/rotate_logs.sh" | crontab -
```

### 6.3 パフォーマンス最適化

#### 6.3.1 メモリ使用量の最適化
```bash
# メモリ使用量の監視スクリプト
cat > monitor_memory.sh << 'EOF'
#!/bin/bash
PID=$(pgrep -f "python main.py")
if [ ! -z "$PID" ]; then
    MEMORY=$(ps -o rss= -p $PID | awk '{print $1/1024}')
    echo "$(date): Memory usage: ${MEMORY}MB"
    if (( $(echo "$MEMORY > 800" | bc -l) )); then
        echo "WARNING: High memory usage detected"
    fi
fi
EOF

chmod +x monitor_memory.sh
```

#### 6.3.2 ディスクI/Oの最適化
```bash
# ディスク使用量の監視
cat > monitor_disk.sh << 'EOF'
#!/bin/bash
USAGE=$(df recordings/ | tail -1 | awk '{print $5}' | sed 's/%//')
echo "$(date): Disk usage: ${USAGE}%"
if [ $USAGE -gt 80 ]; then
    echo "WARNING: High disk usage detected"
fi
EOF

chmod +x monitor_disk.sh
```

## 7. 定期メンテナンス

### 7.1 日次メンテナンス
```bash
# 1. ログ確認
tail -n 100 logs/midi_recorder.log | grep ERROR

# 2. ディスク使用量確認
df -h

# 3. プロセス確認
ps aux | grep python | grep main.py

# 4. 録音ファイル確認
ls -la recordings/ | wc -l
```

### 7.2 週次メンテナンス
```bash
# 1. ログローテーション
./rotate_logs.sh

# 2. 古いファイルの整理
find recordings/ -name "*.mid" -mtime +7 -exec ls -la {} \;

# 3. 設定ファイルのバックアップ
cp config/config.yaml config/config.yaml.backup.$(date +%Y%m%d)

# 4. 依存関係の更新確認
uv sync --upgrade
```

### 7.3 月次メンテナンス
```bash
# 1. システム全体のバックアップ
tar -czf backup_$(date +%Y%m).tar.gz recordings/ logs/ config/

# 2. パフォーマンステスト
uv run pytest tests/test_performance.py

# 3. セキュリティアップデート
uv audit

# 4. ドキュメント更新
git log --since="1 month ago" --oneline
```

## 8. セキュリティ

### 8.1 ファイル権限
```bash
# 適切な権限設定
chmod 755 recordings/
chmod 644 recordings/*.mid
chmod 644 logs/midi_recorder.log
chmod 600 config/config.yaml
```

### 8.2 アクセス制御
```bash
# 特定ユーザーのみアクセス可能にする
chown username:group recordings/
chmod 750 recordings/
```

### 8.3 ログセキュリティ
```bash
# ログファイルの権限設定
chmod 640 logs/midi_recorder.log
chown username:group logs/midi_recorder.log
```

## 9. 監視・アラート

### 9.1 監視スクリプト
```bash
# システム監視スクリプト
cat > system_monitor.sh << 'EOF'
#!/bin/bash

# プロセス確認
if ! pgrep -f "python main.py" > /dev/null; then
    echo "ALERT: MIDI Recording System is not running"
    # 自動再起動
    cd /Users/ks/Documents/wolf/round_the_clock_midi_recording
    uv run python main.py &
fi

# メモリ使用量確認
PID=$(pgrep -f "python main.py")
if [ ! -z "$PID" ]; then
    MEMORY=$(ps -o rss= -p $PID | awk '{print $1/1024}')
    if (( $(echo "$MEMORY > 800" | bc -l) )); then
        echo "WARNING: High memory usage: ${MEMORY}MB"
    fi
fi

# ディスク使用量確認
USAGE=$(df recordings/ | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $USAGE -gt 80 ]; then
    echo "WARNING: High disk usage: ${USAGE}%"
fi
EOF

chmod +x system_monitor.sh
```

### 9.2 自動監視設定
```bash
# cronで定期監視（5分ごと）
echo "*/5 * * * * /path/to/system_monitor.sh" | crontab -
```

## 10. サポート・連絡先

### 10.1 問題報告
問題が発生した場合は、以下の情報を収集して報告してください：

1. **システム情報**
   - OSバージョン
   - Pythonバージョン
   - 使用しているMIDIデバイス

2. **エラー情報**
   - エラーメッセージ
   - ログファイルの内容
   - 発生時の操作手順

3. **環境情報**
   - 設定ファイルの内容
   - ディスク使用量
   - メモリ使用量

### 10.2 緊急時の対応
```bash
# システム強制停止
pkill -9 -f "python main.py"

# 緊急時のデータ保護
cp -r recordings/ emergency_backup_$(date +%Y%m%d_%H%M%S)/

# システム再起動
cd /Users/ks/Documents/wolf/round_the_clock_midi_recording
uv run python main.py
``` 
