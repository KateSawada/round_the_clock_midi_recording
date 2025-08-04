"""MIDI受信モジュール"""

import platform
import time
from typing import List, Optional

import mido

from ..utils.exceptions import MIDIError
from .device_manager import MIDIDeviceManager


class MIDIReceiver:
    """MIDIデバイスからのメッセージを受信し、メモリ上に蓄積するクラス"""

    def __init__(self, port_name: str) -> None:
        """MIDIReceiverを初期化する

        Args:
            port_name: MIDIポート名

        Raises:
            MIDIError: ポートが見つからない場合
        """
        self.port_name = port_name
        self.messages: List[mido.Message] = []
        self.is_recording = False
        self._port: Optional[mido.ports.BaseInput] = None
        self.start_time: Optional[float] = None
        self.last_message_time: Optional[float] = None
        self._new_messages_received = False
        self._previous_message_count = 0  # 前回のメッセージ数を記録
        self.device_manager = MIDIDeviceManager()
        self._connection_error_count = 0  # 接続エラーカウント
        self._max_connection_errors = 3  # 最大接続エラー数
        self._last_connection_check = 0  # 最後の接続チェック時刻
        self._connection_check_interval = 5.0  # 接続チェック間隔（秒）

        # プラットフォーム固有の設定
        self._setup_platform_backend()

    def _setup_platform_backend(self):
        """プラットフォーム固有のバックエンド設定"""
        if platform.system() == "Darwin":  # macOS
            try:
                import rtmidi

                if hasattr(rtmidi, "API_MACOSX_CORE"):
                    rtmidi.MidiIn(rtmidi.API_MACOSX_CORE)
                mido.set_backend("mido.backends.rtmidi")
            except Exception:
                pass
        elif platform.system() == "Linux":  # Linux (Raspberry Pi含む)
            try:
                # LinuxではALSAバックエンドを優先
                mido.set_backend("mido.backends.alsa")
            except Exception:
                try:
                    # ALSAが失敗した場合はportmidiを試行
                    mido.set_backend("mido.backends.portmidi")
                except Exception:
                    pass

    def start_recording(self, interactive_selection: bool = True) -> None:
        """MIDI受信を開始する

        Args:
            interactive_selection: ポートが見つからない場合に対話的選択を行うかどうか

        Raises:
            MIDIError: ポートのオープンに失敗した場合
        """
        try:
            # 利用可能なポートを確認
            available_ports = self.device_manager.get_available_input_ports()

            if not available_ports:
                raise MIDIError("利用可能なMIDIポートが見つかりません")

            # ポート名が'default'の場合は最初のポートを使用
            if self.port_name == "default":
                self.port_name = available_ports[0]

            # 指定されたポートが存在するか確認
            if self.port_name not in available_ports:
                if interactive_selection:
                    # 対話的にポートを選択
                    selected_port = self.device_manager.select_port_interactive(
                        self.port_name
                    )
                    if selected_port:
                        self.port_name = selected_port
                    else:
                        raise MIDIError("ポートの選択がキャンセルされました")
                else:
                    raise MIDIError(
                        f"ポート '{self.port_name}' が見つかりません。"
                        f"利用可能なポート: {available_ports}"
                    )

            # ポートを開く
            self._port = mido.open_input(self.port_name)
            self.is_recording = True
            self.start_time = time.time()
            self.last_message_time = None
            self._connection_error_count = 0  # エラーカウントをリセット

        except Exception as e:
            raise MIDIError(f"MIDIポートのオープンに失敗しました: {e}")

    def stop_recording(self) -> None:
        """MIDI受信を停止する"""
        if self._port:
            self._port.close()
            self._port = None
        self.is_recording = False
        self.start_time = None
        self.last_message_time = None

    def _check_device_connection(self) -> bool:
        """デバイス接続状態をチェックする

        Returns:
            デバイスが接続されている場合はTrue
        """
        current_time = time.time()

        # 接続チェック間隔を過ぎていない場合は前回の結果を返す
        if current_time - self._last_connection_check < self._connection_check_interval:
            return self._port is not None and self._port.is_open

        self._last_connection_check = current_time

        try:
            # ポートが開いているかチェック
            if self._port is None or not self._port.is_open:
                return False

            # ポートが利用可能かチェック
            if not self.device_manager.is_port_available(self.port_name):
                return False

            return True

        except Exception:
            return False

    def _handle_device_disconnection(self) -> bool:
        """デバイス切断を処理する

        Returns:
            再接続に成功した場合はTrue
        """
        self._connection_error_count += 1
        print(
            f"Device disconnection detected. Error count: {self._connection_error_count}"
        )

        # 最大エラー数を超えた場合は再接続を試行
        if self._connection_error_count >= self._max_connection_errors:
            print(f"Attempting to reconnect to device '{self.port_name}'...")

            # 現在のポートを閉じる
            if self._port:
                try:
                    self._port.close()
                except Exception:
                    pass
                self._port = None

            # デバイスの再接続を待機
            if self.device_manager.wait_for_device_reconnection(
                self.port_name, timeout=30.0
            ):
                try:
                    # 再接続に成功した場合はポートを再オープン
                    self._port = mido.open_input(self.port_name)
                    self._connection_error_count = 0
                    print(f"Successfully reconnected to device '{self.port_name}'")
                    return True
                except Exception as e:
                    print(f"Failed to reopen port after reconnection: {e}")
            else:
                # 代替ポートを探す
                alternative_port = self.device_manager.find_alternative_port(
                    self.port_name
                )
                if alternative_port and alternative_port != self.port_name:
                    try:
                        self.port_name = alternative_port
                        self._port = mido.open_input(self.port_name)
                        self._connection_error_count = 0
                        print(f"Switched to alternative port: {self.port_name}")
                        return True
                    except Exception as e:
                        print(f"Failed to switch to alternative port: {e}")

        return False

    def get_messages(self) -> List[mido.Message]:
        """蓄積されたメッセージを取得し、バッファをクリアする

        Returns:
            MIDIメッセージのリスト
        """
        messages = self.get_messages_without_clear()
        self.messages.clear()
        return messages

    def get_messages_without_clear(self) -> List[mido.Message]:
        """蓄積されたメッセージを取得する（バッファはクリアしない）

        Returns:
            MIDIメッセージのリスト
        """
        return self.messages.copy()

    def has_messages(self) -> bool:
        """メッセージがあるかどうかを確認する

        Returns:
            メッセージがある場合はTrue
        """
        return len(self.messages) > 0

    def receive_messages(self) -> None:
        """MIDIメッセージを受信する（非ブロッキング）"""
        if not self.is_recording:
            return

        # デバイス接続状態をチェック
        if not self._check_device_connection():
            if not self._handle_device_disconnection():
                # 再接続に失敗した場合は受信を停止
                print("Device reconnection failed, stopping recording")
                self.stop_recording()
                return

        if not self._port:
            return

        try:
            # 非ブロッキングでメッセージを受信
            message_received = False
            for message in self._port.iter_pending():
                # タイムスタンプを設定
                current_time = time.time()
                if self.start_time is None:
                    self.start_time = current_time
                    delta_time = 0
                else:
                    if self.last_message_time is None:
                        delta_time = int(
                            (current_time - self.start_time) * 1000
                        )  # ミリ秒
                    else:
                        delta_time = int(
                            (current_time - self.last_message_time) * 1000
                        )  # ミリ秒

                # メッセージにデルタタイムを設定
                message.time = delta_time
                self.messages.append(message)
                self.last_message_time = current_time
                message_received = True

            # メッセージが受信された場合に新しいメッセージフラグを設定
            if message_received:
                self._new_messages_received = True
                # メッセージ受信時にエラーカウントをリセット
                self._connection_error_count = 0

        except Exception as e:
            # 受信エラーをログに記録
            print(f"MIDI receive error: {e}")
            # エラーが発生した場合はデバイス切断を処理
            if not self._handle_device_disconnection():
                print("Device reconnection failed after receive error")
                self.stop_recording()

    def has_new_messages(self) -> bool:
        """新しいメッセージが受信されたかどうかを確認する

        Returns:
            新しいメッセージが受信された場合はTrue
        """
        return self._new_messages_received

    def clear_new_messages_flag(self) -> None:
        """新しいメッセージフラグをクリアする"""
        self._new_messages_received = False

    def get_message_count(self) -> int:
        """蓄積されたメッセージ数を取得する

        Returns:
            メッセージ数
        """
        return len(self.messages)

    def clear_messages(self) -> None:
        """メッセージバッファをクリアする"""
        self._previous_message_count = len(
            self.messages
        )  # クリア前のメッセージ数を記録
        self.messages.clear()
        # start_timeとlast_message_timeは保持して、タイムスタンプ計算を継続する
        # self.start_time = None
        # self.last_message_time = None
