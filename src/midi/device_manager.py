"""MIDIデバイス管理モジュール"""

import platform
from typing import List, Optional, Tuple

import mido


class MIDIDeviceManager:
    """MIDIデバイスを管理するクラス"""

    def __init__(self):
        """MIDIDeviceManagerを初期化する"""
        # macOSではrtmidiバックエンドの設定を調整
        if platform.system() == "Darwin":
            try:
                import rtmidi

                if hasattr(rtmidi, "API_MACOSX_CORE"):
                    rtmidi.MidiIn(rtmidi.API_MACOSX_CORE)
                mido.set_backend("mido.backends.rtmidi")
            except Exception:
                pass

    def get_available_input_ports(self) -> List[str]:
        """利用可能なMIDI入力ポートの一覧を取得する

        Returns:
            MIDI入力ポート名のリスト
        """
        try:
            ports = mido.get_input_names()
            print(f"利用可能なMIDI入力ポート: {ports}")  # デバッグ用
            return ports
        except Exception as e:
            print(f"MIDIポート取得エラー: {e}")  # デバッグ用
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

    def select_port_interactive(self, current_port_name: str) -> Optional[str]:
        """対話的にポートを選択する

        Args:
            current_port_name: 現在設定されているポート名

        Returns:
            選択されたポート名（キャンセルされた場合はNone）
        """
        available_ports = self.get_available_input_ports()

        if not available_ports:
            print("利用可能なMIDI入力ポートが見つかりません。")
            return None

        print(f"\n現在の設定ポート '{current_port_name}' が見つかりません。")
        print("利用可能なMIDI入力ポート:")

        for i, port in enumerate(available_ports, 1):
            print(f"  {i}. {port}")

        print(f"  {len(available_ports) + 1}. キャンセル")

        while True:
            try:
                choice = input(
                    f"\nポートを選択してください (1-{len(available_ports) + 1}): "
                )
                choice_num = int(choice)

                if 1 <= choice_num <= len(available_ports):
                    selected_port = available_ports[choice_num - 1]
                    print(f"選択されたポート: {selected_port}")
                    return selected_port
                elif choice_num == len(available_ports) + 1:
                    print("キャンセルされました。")
                    return None
                else:
                    print("無効な選択です。")
            except ValueError:
                print("数値を入力してください。")
            except KeyboardInterrupt:
                print("\nキャンセルされました。")
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
