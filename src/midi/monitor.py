"""MIDI監視モジュール"""

from typing import Callable, Optional

from ..utils.exceptions import FileWriteError, MIDIError
from ..utils.logger import Logger
from ..utils.timer import AutoSaveTimer
from .receiver import MIDIReceiver
from .writer import MIDIFileWriter


class MIDIMonitor:
    """MIDI受信、ファイル書き出し、タイマー機能を統合するメインクラス"""

    def __init__(
        self,
        port_name: str,
        output_directory: str,
        timeout_seconds: int = 300,
        manual_save_directory: Optional[str] = None,
        gui_callback: Optional[Callable[[str], None]] = None,
    ) -> None:
        """MIDIMonitorを初期化する

        Args:
            port_name: MIDIポート名
            output_directory: 出力ディレクトリ
            timeout_seconds: タイムアウト時間（秒）
            manual_save_directory: 手動保存用ディレクトリ（Noneの場合はoutput_directoryと同じ）
            gui_callback: GUIへのメッセージ送信用コールバック
        """
        self.port_name = port_name
        self.output_directory = output_directory
        self.manual_save_directory = manual_save_directory or output_directory
        self.timeout_seconds = timeout_seconds
        self.gui_callback = gui_callback

        # コンポーネントの初期化
        self.receiver = MIDIReceiver(port_name)
        self.writer = MIDIFileWriter(output_directory, manual_save_directory)
        self.timer = AutoSaveTimer(timeout_seconds)
        self.logger = Logger()

        self.is_monitoring = False

    def start_monitoring(self, interactive_selection: bool = True) -> None:
        """監視を開始する

        Args:
            interactive_selection: ポートが見つからない場合に対話的選択を行うかどうか

        Raises:
            MIDIError: MIDIポートのオープンに失敗した場合
        """
        try:
            # MIDI受信を開始（デバイス選択機能付き）
            self.receiver.start_recording(interactive_selection=interactive_selection)

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

    def save_current_buffer(self, is_manual_save: bool = False) -> Optional[str]:
        """現在のバッファを保存する

        Args:
            is_manual_save: 手動保存かどうか（Trueの場合は手動保存用ディレクトリに保存）

        Returns:
            保存されたファイルパス（バッファが空の場合はNone）
        """
        if not self.receiver.has_messages():
            return None

        try:
            # メッセージを取得（バッファはクリアしない）
            messages = self.receiver.get_messages_without_clear()

            # ファイルに書き込み
            filepath = self.writer.write_messages(
                messages, is_manual_save=is_manual_save
            )

            # ログに記録
            if is_manual_save:
                self.logger.log_manual_save(filepath)
            else:
                self.logger.log_file_saved(filepath)

            return filepath

        except Exception as e:
            error_message = f"バッファ保存に失敗しました: {e}"
            self.logger.log_error(error_message)
            if self.gui_callback:
                self.gui_callback(error_message)
            raise FileWriteError(error_message)

    def manual_save(self) -> Optional[str]:
        """手動保存を実行する

        Returns:
            保存されたファイルパス（バッファが空の場合はNone）
        """
        # バッファが空かどうかをチェック
        if not self.receiver.has_messages():
            # バッファが空の場合：最新の自動保存済みファイルをコピー
            try:
                copied_filepath = self.writer.copy_latest_auto_save_to_manual_save()
                if copied_filepath:
                    # 手動保存後にタイマーをリセット
                    self.timer.reset_timer()
                    # デバッグ情報を追加
                    self.logger.log_info(
                        f"手動保存完了（バッファ空）: {copied_filepath}, "
                        f"タイマーリセット実行"
                    )
                    return copied_filepath
                else:
                    # コピーに失敗した場合
                    self.logger.log_info("手動保存: コピーするファイルがありません")
                    return None
            except Exception as e:
                # コピーに失敗した場合
                self.logger.log_error(f"手動保存時のファイルコピーエラー: {e}")
                return None
        else:
            # バッファが空でない場合：自動保存処理を実行してから最新のファイルをコピー
            filepath = self.save_current_buffer(is_manual_save=False)

            if filepath:
                # 自動保存用ディレクトリの最新ファイルを手動保存ディレクトリにコピー
                try:
                    copied_filepath = self.writer.copy_latest_auto_save_to_manual_save()
                    if copied_filepath:
                        # 手動保存後はバッファをクリアする
                        self.receiver.clear_messages()
                        # 手動保存後にタイマーをリセットして、新しいMIDIイベントの監視を継続
                        self.timer.reset_timer()
                        # デバッグ情報を追加
                        self.logger.log_info(
                            f"手動保存完了（バッファあり）: {copied_filepath}, "
                            f"タイマーリセット実行, "
                            f"バッファクリア（メッセージ数: {self.receiver.get_message_count()}）"
                        )
                        return copied_filepath
                    else:
                        # コピーに失敗した場合は元のファイルパスを返す
                        self.receiver.clear_messages()
                        # 手動保存後にタイマーをリセット
                        self.timer.reset_timer()
                        # デバッグ情報を追加
                        self.logger.log_info(
                            f"手動保存完了（コピー失敗）: {filepath}, "
                            f"タイマーリセット実行, "
                            f"バッファクリア（メッセージ数: {self.receiver.get_message_count()}）"
                        )
                        return filepath
                except Exception as e:
                    # コピーに失敗した場合は元のファイルパスを返す
                    self.logger.log_error(f"手動保存時のファイルコピーエラー: {e}")
                    self.receiver.clear_messages()
                    # 手動保存後にタイマーをリセット
                    self.timer.reset_timer()
                    # デバッグ情報を追加
                    self.logger.log_info(
                        f"手動保存完了（エラー）: {filepath}, "
                        f"タイマーリセット実行, "
                        f"バッファクリア（メッセージ数: {self.receiver.get_message_count()}）"
                    )
                    return filepath

        return None

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

            # 新しいメッセージが受信された場合はタイマーをリセット
            if self.receiver.has_new_messages():
                # タイマーをリセット
                self.timer.reset_timer()
                self.receiver.clear_new_messages_flag()

                message = "新しいメッセージを受信しました。タイマーをリセットしました。"
                self.logger.log_info(message)
                if self.gui_callback:
                    self.gui_callback(message)

                # デバッグ情報を追加
                debug_message = (
                    f"デバッグ: メッセージ数={self.receiver.get_message_count()}, "
                    f"タイマー実行中={self.timer.is_running()}"
                )
                self.logger.log_info(debug_message)

        except Exception as e:
            error_message = f"MIDIイベント処理エラー: {e}"
            self.logger.log_error(error_message)
            if self.gui_callback:
                self.gui_callback(error_message)

    def _auto_save_callback(self) -> None:
        """自動保存コールバック"""
        try:
            message = "タイムアウトによる自動保存を実行します"
            self.logger.log_info(message)
            if self.gui_callback:
                self.gui_callback(message)

            # デバッグ情報を追加
            debug_message = (
                f"自動保存デバッグ: メッセージ数={self.receiver.get_message_count()}, "
                f"バッファにイベント={self.has_buffered_events()}"
            )
            self.logger.log_info(debug_message)

            if self.has_buffered_events():
                filepath = self.save_current_buffer(is_manual_save=False)
                success_message = f"自動保存完了: {filepath}"
                self.logger.log_info(success_message)
                if self.gui_callback:
                    self.gui_callback(success_message)

                # 自動保存後にバッファをクリアする
                self.receiver.clear_messages()
                self.logger.log_info(
                    f"自動保存後バッファクリア（メッセージ数: {self.receiver.get_message_count()}）"
                )
            else:
                no_data_message = "自動保存: 保存するデータがありません"
                self.logger.log_info(no_data_message)
                if self.gui_callback:
                    self.gui_callback(no_data_message)
        except Exception as e:
            error_message = f"自動保存エラー: {e}"
            self.logger.log_error(error_message)
            if self.gui_callback:
                self.gui_callback(error_message)

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
            "manual_save_directory": self.manual_save_directory,
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
