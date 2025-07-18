"""設定管理モジュール"""

import os
from typing import Any, Dict

import yaml

from ..utils.exceptions import ConfigError


class ConfigManager:
    """設定ファイルを管理するクラス"""

    def __init__(self, config_file: str = "config.yaml") -> None:
        """ConfigManagerを初期化する

        Args:
            config_file: 設定ファイルパス

        Raises:
            ConfigError: 設定ファイルが見つからない場合
        """
        self.config_file = config_file
        self._config: Dict[str, Any] = {}
        self._load_config()

    def _load_config(self) -> None:
        """設定ファイルを読み込む"""
        try:
            if not os.path.exists(self.config_file):
                self._create_default_config()

            with open(self.config_file, "r", encoding="utf-8") as f:
                self._config = yaml.safe_load(f)

        except Exception as e:
            raise ConfigError(f"設定ファイルの読み込みに失敗しました: {e}")

    def _create_default_config(self) -> None:
        """デフォルト設定ファイルを作成する"""
        default_config = {
            "midi": {"port_name": "default", "timeout_seconds": 300},
            "output": {
                "directory": "./recordings",
                "manual_save_directory": "./manual_saves",
            },
            "gui": {"window_title": "MIDI Recording System", "theme_mode": "light"},
            "logging": {"level": "INFO", "file": "./logs/midi_recorder.log"},
        }

        # 設定ディレクトリの作成
        config_dir = os.path.dirname(self.config_file)
        if config_dir and not os.path.exists(config_dir):
            os.makedirs(config_dir)

        # デフォルト設定ファイルの作成
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(default_config, f, default_flow_style=False, allow_unicode=True)

        self._config = default_config

    def load_config(self) -> Dict[str, Any]:
        """設定ファイルを読み込む

        Returns:
            設定データの辞書

        Raises:
            ConfigError: 設定ファイルの読み込みに失敗した場合
        """
        return self._config

    def get_midi_config(self) -> Dict[str, Any]:
        """MIDI設定を取得する

        Returns:
            MIDI設定の辞書
        """
        return self._config.get("midi", {})

    def get_output_config(self) -> Dict[str, Any]:
        """出力設定を取得する

        Returns:
            出力設定の辞書
        """
        return self._config.get("output", {})

    def get_manual_save_directory(self) -> str:
        """手動保存用ディレクトリを取得する

        Returns:
            手動保存用ディレクトリパス
        """
        output_config = self.get_output_config()
        key = "manual_save_directory"
        default = "./manual_saves"
        return output_config.get(key, default)

    def get_output_directory(self) -> str:
        """出力ディレクトリを取得する

        Returns:
            出力ディレクトリパス
        """
        output_config = self.get_output_config()
        return output_config.get("directory", "./recordings")

    def get_gui_config(self) -> Dict[str, Any]:
        """GUI設定を取得する

        Returns:
            GUI設定の辞書
        """
        return self._config.get("gui", {})

    def get_logging_config(self) -> Dict[str, Any]:
        """ログ設定を取得する

        Returns:
            ログ設定の辞書
        """
        return self._config.get("logging", {})

    def update_config(self, section: str, key: str, value: Any) -> None:
        """設定を更新する

        Args:
            section: 設定セクション
            key: 設定キー
            value: 設定値
        """
        if section not in self._config:
            self._config[section] = {}

        self._config[section][key] = value

        # 設定ファイルに保存
        with open(self.config_file, "w", encoding="utf-8") as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)

    def ensure_directories_exist(self) -> None:
        """必要なディレクトリが存在することを確認する"""
        directories = [
            self.get_output_directory(),
            self.get_manual_save_directory(),
        ]

        for directory in directories:
            if not os.path.exists(directory):
                os.makedirs(directory)
