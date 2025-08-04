"""MIDIデバイス管理モジュール"""

import platform
import time
from typing import List, Optional, Tuple

import mido


class MIDIDeviceManager:
    """MIDIデバイスを管理するクラス"""

    def __init__(self):
        """MIDIDeviceManagerを初期化する"""
        self.system = platform.system()
        self._setup_backend()

    def _setup_backend(self):
        """プラットフォームに応じたMIDIバックエンドを設定する"""
        try:
            if self.system == "Darwin":  # macOS
                import rtmidi

                if hasattr(rtmidi, "API_MACOSX_CORE"):
                    rtmidi.MidiIn(rtmidi.API_MACOSX_CORE)
                mido.set_backend("mido.backends.rtmidi")
            elif self.system == "Linux":  # Linux (Raspberry Pi含む)
                # LinuxではALSAバックエンドを使用
                mido.set_backend("mido.backends.portmidi")
                # またはALSAバックエンドを試行
                try:
                    mido.set_backend("mido.backends.alsa")
                except Exception:
                    pass
            else:  # Windowsその他
                # デフォルトバックエンドを使用
                pass
        except Exception as e:
            print(f"Backend setup error: {e}")

    def get_available_input_ports(self) -> List[str]:
        """利用可能なMIDI入力ポートの一覧を取得する

        Returns:
            MIDI入力ポート名のリスト
        """
        try:
            ports = mido.get_input_names()
            print(f"Available MIDI input ports: {ports}")  # デバッグ用
            return ports
        except Exception as e:
            print(f"MIDI port retrieval error: {e}")  # デバッグ用
            return []

    def get_available_output_ports(self) -> List[str]:
        """利用可能なMIDI出力ポートの一覧を取得する

        Returns:
            MIDI出力ポート名のリスト
        """
        try:
            return mido.get_output_names()
        except Exception:
            return []

    def is_port_available(self, port_name: str) -> bool:
        """指定されたポートが利用可能かどうかを確認する

        Args:
            port_name: ポート名

        Returns:
            ポートが利用可能な場合はTrue
        """
        available_ports = self.get_available_input_ports()
        return port_name in available_ports

    def wait_for_device_reconnection(
        self, port_name: str, timeout: float = 30.0, check_interval: float = 1.0
    ) -> bool:
        """デバイスの再接続を待機する

        Args:
            port_name: 待機するポート名
            timeout: タイムアウト時間（秒）
            check_interval: チェック間隔（秒）

        Returns:
            再接続に成功した場合はTrue
        """
        start_time = time.time()
        print(f"Waiting for device '{port_name}' to reconnect...")

        while time.time() - start_time < timeout:
            if self.is_port_available(port_name):
                print(f"Device '{port_name}' reconnected successfully")
                return True
            time.sleep(check_interval)

        print(f"Device '{port_name}' reconnection timeout after {timeout} seconds")
        return False

    def find_alternative_port(self, original_port_name: str) -> Optional[str]:
        """代替ポートを探す

        Args:
            original_port_name: 元のポート名

        Returns:
            代替ポート名（見つからない場合はNone）
        """
        available_ports = self.get_available_input_ports()

        if not available_ports:
            return None

        # 同じ名前のポートを探す
        for port in available_ports:
            if port == original_port_name:
                return port

        # 同じ名前が見つからない場合は最初のポートを返す
        return available_ports[0]

    def test_port_connection(self, port_name: str, timeout: float = 5.0) -> bool:
        """ポートの接続をテストする

        Args:
            port_name: ポート名
            timeout: タイムアウト時間（秒）

        Returns:
            接続テストが成功した場合はTrue
        """
        try:
            port = mido.open_input(port_name)
            # 簡単な接続テスト（ポートが開けるかどうか）
            port.close()
            return True
        except Exception:
            return False

    def select_port_interactive(self, current_port_name: str) -> Optional[str]:
        """対話的にポートを選択する

        Args:
            current_port_name: 現在設定されているポート名

        Returns:
            選択されたポート名（キャンセルされた場合はNone）
        """
        available_ports = self.get_available_input_ports()

        if not available_ports:
            print("No available MIDI input ports found.")
            return None

        print(f"\nConfigured port '{current_port_name}' not found.")
        print("Available MIDI input ports:")

        for i, port in enumerate(available_ports, 1):
            print(f"  {i}. {port}")

        print(f"  {len(available_ports) + 1}. Cancel")

        while True:
            try:
                choice = input(
                    f"\nPlease select a port (1-{len(available_ports) + 1}): "
                )
                choice_num = int(choice)

                if 1 <= choice_num <= len(available_ports):
                    selected_port = available_ports[choice_num - 1]
                    print(f"Selected port: {selected_port}")
                    return selected_port
                elif choice_num == len(available_ports) + 1:
                    print("Cancelled.")
                    return None
                else:
                    print("Invalid selection.")
            except ValueError:
                print("Please enter a number.")
            except KeyboardInterrupt:
                print("\nCancelled.")
                return None

    def get_port_info(self, port_name: str) -> Optional[dict]:
        """ポートの詳細情報を取得する

        Args:
            port_name: ポート名

        Returns:
            ポート情報の辞書（見つからない場合はNone）
        """
        try:
            port = mido.open_input(port_name)
            info = {
                "name": port_name,
                "is_input": port.is_input,
                "is_output": port.is_output,
                "is_open": port.is_open,
            }
            port.close()
            return info
        except Exception:
            return None

    def get_ports_with_info(self) -> List[Tuple[str, dict]]:
        """ポート名と情報のリストを取得する

        Returns:
            (ポート名, ポート情報)のタプルのリスト
        """
        available_ports = self.get_available_input_ports()
        ports_with_info = []

        for port_name in available_ports:
            info = self.get_port_info(port_name)
            if info:
                ports_with_info.append((port_name, info))

        return ports_with_info
