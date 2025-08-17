"""MIDI受信モジュール"""

import platform
import time
from typing import List, Optional

import mido
import pyudev

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

        # 再接続のための監視
        self.context = pyudev.Context()
        self.monitor = pyudev.Monitor.from_netlink(self.context)
        self.monitor.filter_by('sound')  # サウンドデバイスに限定

        self.observer = pyudev.MonitorObserver(self.monitor, callback=self._device_event_callback)
        self.observer.start()

        # macOSではrtmidiバックエンドの設定を調整
        if platform.system() == "Darwin":
            try:
                # rtmidiのAPI_UNSPECIFIEDエラーを回避
                import rtmidi

                # macOS用のAPIを使用
                if hasattr(rtmidi, "API_MACOSX_CORE"):
                    # rtmidiの初期化を試行（APIを指定）
                    rtmidi.MidiIn(rtmidi.API_MACOSX_CORE)
                mido.set_backend("mido.backends.rtmidi")
            except Exception:
                # バックエンド設定に失敗した場合はデフォルトを使用
                pass

    def _device_event_callback(self, action):
        if "midi" in action.sys_name and action.action == "add":
            print(f"{action.device_node} added")
            time.sleep(1)  # 接続が確率するのを待つ
            self._port = mido.open_input(self.port_name)


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
        if not self.is_recording or not self._port:
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

        except Exception as e:
            # 受信エラーをログに記録
            print(f"MIDI receive error: {e}")

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
