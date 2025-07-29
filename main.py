"""Round the Clock MIDI Recording System - メインアプリケーション"""

import argparse
import sys
from pathlib import Path

from src.config.manager import ConfigManager
from src.gui.main_window import MIDIGUI
from src.midi.device_manager import MIDIDeviceManager
from src.utils.logger import Logger


def check_midi_devices_on_startup(config_path: str) -> bool:
    """起動時にMIDIデバイスをチェックする

    Args:
        config_path: 設定ファイルパス

    Returns:
        デバイスが利用可能な場合はTrue
    """
    try:
        # 設定とデバイス管理を初期化
        config_manager = ConfigManager(config_path)
        device_manager = MIDIDeviceManager()
        logger = Logger()

        # 設定を読み込み
        midi_config = config_manager.get_midi_config()
        port_name = midi_config.get("port_name", "default")

        logger.log_info(f"設定されたMIDIポート: {port_name}")

        # 利用可能なデバイスを確認
        available_ports = device_manager.get_available_input_ports()

        if not available_ports:
            logger.log_error("利用可能なMIDIデバイスが見つかりません")
            return False

        logger.log_info(f"利用可能なMIDIポート: {available_ports}")

        # 設定されたポートが利用可能かチェック
        if port_name == "default":
            if available_ports:
                # defaultの場合は最初のポートを自動選択
                selected_port = available_ports[0]
                config_manager.update_config("midi", "port_name", selected_port)
                logger.log_info(f"デフォルトポートを自動選択しました: {selected_port}")
                return True
        elif port_name not in available_ports:
            # 設定されたポートが見つからない場合は自動的に最初のポートを選択
            if available_ports:
                selected_port = available_ports[0]
                config_manager.update_config("midi", "port_name", selected_port)
                logger.log_info(f"利用可能なポートを自動選択しました: {selected_port}")
                return True

        return True

    except Exception as e:
        logger.log_error(f"起動時デバイスチェックエラー: {e}")
        return False


def main():
    """メインアプリケーション"""
    parser = argparse.ArgumentParser(description="MIDI Recording System")
    parser.add_argument(
        "--config", default="config/config.yaml", help="設定ファイルパス"
    )
    parser.add_argument("--debug", action="store_true", help="デバッグモード")
    parser.add_argument(
        "--skip-device-check", action="store_true", help="デバイスチェックをスキップ"
    )

    args = parser.parse_args()

    try:
        # ログ設定
        logger = Logger()
        logger.log_info("MIDI Recording System を起動しました")

        # 設定ファイルの確認
        config_path = Path(args.config)
        if not config_path.exists():
            logger.log_info(f"設定ファイルが見つかりません: {config_path}")
            logger.log_info("デフォルト設定ファイルを作成します")

        # 起動時にMIDIデバイスをチェック
        if not args.skip_device_check:
            logger.log_info("起動時デバイスチェックを開始します")
            if not check_midi_devices_on_startup(str(config_path)):
                logger.log_error("デバイスチェックに失敗しました")
                print("デバイスチェックに失敗しました。アプリケーションを終了します。")
                sys.exit(1)
            logger.log_info("デバイスチェックが完了しました")

        # GUIアプリケーションを起動
        gui = MIDIGUI(str(config_path))

        # fletアプリケーションを起動
        import flet as ft

        ft.app(target=gui.main)

    except Exception as e:
        print(f"アプリケーション起動エラー: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
