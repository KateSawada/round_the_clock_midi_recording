"""Round the Clock MIDI Recording System - メインアプリケーション"""

import argparse
import sys
from pathlib import Path

from src.gui.main_window import MIDIGUI
from src.utils.logger import Logger


def main():
    """メインアプリケーション"""
    parser = argparse.ArgumentParser(description="MIDI Recording System")
    parser.add_argument(
        "--config", default="config/config.yaml", help="設定ファイルパス"
    )
    parser.add_argument("--debug", action="store_true", help="デバッグモード")

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
