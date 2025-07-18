"""ログ管理モジュール"""

import logging
import os


class Logger:
    """システムのログを管理するクラス"""

    def __init__(self, log_file: str = "midi_recorder.log") -> None:
        """Loggerを初期化する

        Args:
            log_file: ログファイルパス
        """
        self.log_file = log_file
        self._setup_logger()

    def _setup_logger(self) -> None:
        """ロガーの設定"""
        # ログディレクトリの作成
        log_dir = os.path.dirname(self.log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        # ロガーの設定
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)

    def log_file_saved(self, filename: str) -> None:
        """ファイル保存完了をログに記録する

        Args:
            filename: 保存されたファイル名
        """
        self.logger.info(f"File saved: {filename}")

    def log_manual_save(self, filename: str) -> None:
        """手動保存完了をログに記録する

        Args:
            filename: 保存されたファイル名
        """
        self.logger.info(f"Manual save completed: {filename}")

    def log_recording_started(self) -> None:
        """録音開始をログに記録する"""
        self.logger.info("Recording started")

    def log_recording_stopped(self) -> None:
        """録音停止をログに記録する"""
        self.logger.info("Recording stopped")

    def log_error(self, error_message: str) -> None:
        """エラーをログに記録する

        Args:
            error_message: エラーメッセージ
        """
        self.logger.error(f"Error: {error_message}")

    def log_info(self, message: str) -> None:
        """情報メッセージをログに記録する

        Args:
            message: 情報メッセージ
        """
        self.logger.info(message)

    def log_debug(self, message: str) -> None:
        """デバッグメッセージをログに記録する

        Args:
            message: デバッグメッセージ
        """
        self.logger.debug(message)
