"""GUIメインウィンドウモジュール"""

import threading
import time
from typing import Optional

import flet as ft

from ..config.manager import ConfigManager
from ..midi.monitor import MIDIMonitor
from ..utils.logger import Logger


class MIDIGUI:
    """MIDI録音システムのGUIクラス"""

    def __init__(self, config_file: str = "config/config.yaml"):
        """MIDIGUIを初期化する

        Args:
            config_file: 設定ファイルパス
        """
        self.config_manager = ConfigManager(config_file)
        self.logger = Logger()
        self.monitor: Optional[MIDIMonitor] = None
        self.page: Optional[ft.Page] = None

        # 設定を読み込み
        self.config = self.config_manager.load_config()
        self.midi_config = self.config_manager.get_midi_config()
        self.output_config = self.config_manager.get_output_config()
        self.gui_config = self.config_manager.get_gui_config()

    def main(self, page: ft.Page):
        """メインGUIを構築する

        Args:
            page: fletページオブジェクト
        """
        self.page = page
        page.title = self.gui_config.get("window_title", "MIDI Recording System")
        theme_mode = (
            ft.ThemeMode.LIGHT
            if self.gui_config.get("theme_mode") == "light"
            else ft.ThemeMode.DARK
        )
        page.theme_mode = theme_mode
        page.window_width = 600
        page.window_height = 400
        page.window_resizable = True

        # ステータス表示
        self.status_text = ft.Text("待機中", size=16, weight=ft.FontWeight.BOLD)

        # メッセージ数表示
        self.message_count_text = ft.Text("メッセージ数: 0", size=14)

        # ポート情報表示
        port_name = self.midi_config.get("port_name", "default")
        self.port_info_text = ft.Text(f"ポート: {port_name}", size=12)

        # 出力ディレクトリ表示
        output_dir = self.config_manager.get_output_directory()
        manual_save_dir = self.config_manager.get_manual_save_directory()
        self.output_info_text = ft.Text(
            f"出力: {output_dir} / 手動保存: {manual_save_dir}", size=12
        )

        # ボタン
        self.start_button = ft.ElevatedButton(
            "録音開始",
            on_click=self.start_recording,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.GREEN,
            ),
        )

        self.stop_button = ft.ElevatedButton(
            "録音停止",
            on_click=self.stop_recording,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.RED,
            ),
            disabled=True,
        )

        self.save_button = ft.ElevatedButton(
            "手動保存",
            on_click=self.manual_save,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
            ),
            disabled=True,
        )

        # ログ表示エリア
        self.log_area = ft.TextField(
            label="ログ",
            multiline=True,
            read_only=True,
            min_lines=5,
            max_lines=10,
            expand=True,
        )

        # レイアウト
        page.add(
            ft.Column(
                [
                    ft.Row(
                        [
                            ft.Text(
                                "MIDI Recording System",
                                size=24,
                                weight=ft.FontWeight.BOLD,
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            self.status_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            self.message_count_text,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Row(
                        [
                            self.port_info_text,
                            self.output_info_text,
                        ],
                        alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    ),
                    ft.Divider(),
                    ft.Row(
                        [
                            self.start_button,
                            self.stop_button,
                            self.save_button,
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                    ft.Divider(),
                    ft.Text("ログ", size=16, weight=ft.FontWeight.BOLD),
                    self.log_area,
                ],
                expand=True,
            )
        )

        # 監視スレッドを開始
        self.start_monitoring_thread()

    def start_recording(self, _):
        """録音を開始する"""
        try:
            # MIDIモニターを初期化
            port_name = self.midi_config.get("port_name", "default")
            output_dir = self.config_manager.get_output_directory()
            manual_save_dir = self.config_manager.get_manual_save_directory()
            timeout = self.midi_config.get("timeout_seconds", 300)

            # 必要なディレクトリが存在することを確認
            self.config_manager.ensure_directories_exist()

            self.monitor = MIDIMonitor(
                port_name=port_name,
                output_directory=output_dir,
                timeout_seconds=timeout,
                manual_save_directory=manual_save_dir,
                gui_callback=self.log_message,
            )

            # 監視を開始
            self.monitor.start_monitoring()

            # UIを更新
            self.status_text.value = "録音中"
            self.status_text.color = ft.Colors.GREEN
            self.start_button.disabled = True
            self.stop_button.disabled = False
            self.save_button.disabled = False

            self.page.update()
            self.log_message("録音を開始しました")

        except Exception as e:
            self.log_message(f"録音開始エラー: {e}")
            self.logger.log_error(f"録音開始エラー: {e}")

    def stop_recording(self, _):
        """録音を停止する"""
        try:
            if self.monitor:
                # 残りのバッファを保存
                if self.monitor.has_buffered_events():
                    filepath = self.monitor.save_current_buffer()
                    self.log_message(f"最終保存: {filepath}")

                # 監視を停止
                self.monitor.stop_monitoring()
                self.monitor = None

            # UIを更新
            self.status_text.value = "停止中"
            self.status_text.color = ft.Colors.RED
            self.start_button.disabled = False
            self.stop_button.disabled = True
            self.save_button.disabled = True

            self.page.update()
            self.log_message("録音を停止しました")

        except Exception as e:
            self.log_message(f"録音停止エラー: {e}")
            self.logger.log_error(f"録音停止エラー: {e}")

    def manual_save(self, _):
        """手動保存を実行する"""
        try:
            if self.monitor and self.monitor.has_buffered_events():
                filepath = self.monitor.manual_save()
                self.log_message(f"手動保存完了: {filepath}")
            else:
                self.log_message("保存するデータがありません")

        except Exception as e:
            self.log_message(f"手動保存エラー: {e}")
            self.logger.log_error(f"手動保存エラー: {e}")

    def start_monitoring_thread(self):
        """監視スレッドを開始する"""

        def monitoring_loop():
            while True:
                try:
                    if self.monitor and self.monitor.is_monitoring:
                        # MIDIイベントを処理
                        self.monitor.process_midi_events()

                        # UIを更新
                        self.update_ui()

                    time.sleep(0.1)  # 100ms間隔でチェック

                except Exception as e:
                    self.log_message(f"監視エラー: {e}")
                    self.logger.log_error(f"監視エラー: {e}")

        # バックグラウンドスレッドを開始
        thread = threading.Thread(target=monitoring_loop, daemon=True)
        thread.start()

    def update_ui(self):
        """UIを更新する"""
        if not self.page:
            return

        try:
            if self.monitor:
                # メッセージ数を更新
                message_count = self.monitor.get_message_count()
                self.message_count_text.value = f"メッセージ数: {message_count}"

                # ページを更新
                self.page.update()

        except Exception as e:
            self.log_message(f"UI更新エラー: {e}")

    def log_message(self, message: str):
        """ログメッセージを表示する"""
        if self.log_area:
            current_time = time.strftime("%H:%M:%S")
            log_entry = f"[{current_time}] {message}\n"
            self.log_area.value += log_entry

            # ログが長すぎる場合は古い部分を削除
            lines = self.log_area.value.split("\n")
            if len(lines) > 50:
                self.log_area.value = "\n".join(lines[-40:])

            self.page.update()
