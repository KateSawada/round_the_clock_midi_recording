"""MIDI監視モジュール"""

from typing import Optional

from ..utils.exceptions import FileWriteError, MIDIError
from ..utils.logger import Logger
from ..utils.timer import AutoSaveTimer
from .receiver import MIDIReceiver
from .writer import MIDIFileWriter


class MIDIMonitor:
    """MIDI受信、ファイル書き出し、タイマー機能を統合するメインクラス"""

    def __init__(
        self, port_name: str, output_directory: str, timeout_seconds: int = 300
    ) -> None:
        """MIDIMonitorを初期化する

        Args:
            port_name: MIDIポート名
            output_directory: 出力ディレクトリ
            timeout_seconds: タイムアウト時間（秒）
        """
        self.port_name = port_name
        self.output_directory = output_directory
        self.timeout_seconds = timeout_seconds

        # コンポーネントの初期化
        self.receiver = MIDIReceiver(port_name)
        self.writer = MIDIFileWriter(output_directory)
        self.timer = AutoSaveTimer(timeout_seconds)
        self.logger = Logger()

        self.is_monitoring = False

    def start_monitoring(self) -> None:
        """監視を開始する

        Raises:
            MIDIError: MIDIポートのオープンに失敗した場合
        """
        try:
            # MIDI受信を開始
            self.receiver.start_recording()

            # 自動保存タイマーを開始
            self.timer.start_timer(self._auto_save_callback)

            self.is_monitoring = True
            self.logger.log_recording_started()

        except Exception as e:
            self.logger.log_error(f"監視開始に失敗しました: {e}")
            raise MIDIError(f"監視開始に失敗しました: {e}")

    def stop_monitoring(self) -> None:
        """監視を停止する"""
        # タイマーを停止
        self.timer.stop_timer()

        # MIDI受信を停止
        self.receiver.stop_recording()

        self.is_monitoring = False
        self.logger.log_recording_stopped()

    def save_current_buffer(self) -> Optional[str]:
        """現在のバッファを保存する

        Returns:
            保存されたファイルパス（バッファが空の場合はNone）
        """
        if not self.receiver.has_messages():
            return None

        try:
            # メッセージを取得
            messages = self.receiver.get_messages()

            # ファイルに書き込み
            filepath = self.writer.write_messages(messages)

            # ログに記録
            self.logger.log_file_saved(filepath)

            return filepath

        except Exception as e:
            self.logger.log_error(f"バッファ保存に失敗しました: {e}")
            raise FileWriteError(f"バッファ保存に失敗しました: {e}")

    def has_buffered_events(self) -> bool:
        """バッファにイベントがあるかチェックする

        Returns:
            イベントがある場合True
        """
        return self.receiver.has_messages()

    def process_midi_events(self) -> None:
        """MIDIイベントを処理する（定期的に呼び出される）"""
        if not self.is_monitoring:
            return

        try:
            # MIDIメッセージを受信
            self.receiver.receive_messages()

            # メッセージが受信された場合はタイマーをリセット
            if self.receiver.has_messages():
                self.timer.reset_timer()

        except Exception as e:
            self.logger.log_error(f"MIDIイベント処理エラー: {e}")

    def _auto_save_callback(self) -> None:
        """自動保存コールバック"""
        try:
            if self.has_buffered_events():
                self.save_current_buffer()
        except Exception as e:
            self.logger.log_error(f"自動保存エラー: {e}")

    def get_status(self) -> dict:
        """現在の状態を取得する

        Returns:
            状態情報の辞書
        """
        return {
            "is_monitoring": self.is_monitoring,
            "is_recording": self.receiver.is_recording,
            "message_count": self.receiver.get_message_count(),
            "timer_running": self.timer.is_running(),
            "port_name": self.port_name,
            "output_directory": self.output_directory,
        }

    def get_message_count(self) -> int:
        """現在のメッセージ数を取得する

        Returns:
            メッセージ数
        """
        return self.receiver.get_message_count()

    def clear_buffer(self) -> None:
        """バッファをクリアする"""
        self.receiver.clear_messages()
        self.logger.log_info("バッファをクリアしました")
