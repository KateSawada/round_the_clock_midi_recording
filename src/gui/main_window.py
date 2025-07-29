"""GUIメインウィンドウモジュール"""

import atexit
import threading
import time
from typing import Optional

import flet as ft

from ..config.manager import ConfigManager
from ..midi.device_manager import MIDIDeviceManager
from ..midi.monitor import MIDIMonitor
from ..utils.logger import Logger


class MIDIGUI:
    """MIDI録音システムのGUIクラス"""

    # ログ関連の定数
    MAX_LOG_LINES = 100  # ログの最大行数

    def __init__(self, config_file: str = "config/config.yaml"):
        """MIDIGUIを初期化する

        Args:
            config_file: 設定ファイルパス
        """
        self.config_manager = ConfigManager(config_file)
        self.logger = Logger()
        self.device_manager = MIDIDeviceManager()
        self.monitor: Optional[MIDIMonitor] = None
        self.page: Optional[ft.Page] = None

        # 設定を読み込み
        self.config = self.config_manager.load_config()
        self.midi_config = self.config_manager.get_midi_config()
        self.output_config = self.config_manager.get_output_config()
        self.gui_config = self.config_manager.get_gui_config()

        # アプリケーション終了時のクリーンアップ処理を登録
        atexit.register(self.save_on_exit)

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

        # ウィンドウが閉じられる時のイベントハンドラーを設定
        page.on_window_event = self.handle_window_event

        # ステータス表示
        self.status_text = ft.Text("待機中", size=16, weight=ft.FontWeight.BOLD)

        # メッセージ数表示
        self.message_count_text = ft.Text("メッセージ数: 0", size=14)

        # ポート情報表示
        port_name = self.midi_config.get("port_name", "default")
        self.port_info_text = ft.Text(f"ポート: {port_name}", size=12)

        # デバイス選択UI（初期状態では非表示）
        self.device_list_column = ft.Column(
            scroll=ft.ScrollMode.AUTO,
            height=300,
            spacing=5,
        )

        self.device_selection_container = ft.Container(
            content=ft.Column(
                [
                    ft.Text("MIDIデバイスを選択", size=16, weight=ft.FontWeight.BOLD),
                    ft.Text("利用可能なMIDIデバイスから選択してください:", size=14),
                    ft.Divider(),
                    self.device_list_column,  # デバイスリスト用
                    ft.Row(
                        [
                            ft.ElevatedButton(
                                "キャンセル", on_click=self.hide_device_selection
                            ),
                        ],
                        alignment=ft.MainAxisAlignment.CENTER,
                    ),
                ]
            ),
            visible=False,
            bgcolor=ft.Colors.WHITE,
            border=ft.border.all(1, ft.Colors.GREY_400),
            border_radius=8,
            padding=20,
        )

        # デバイス選択ボタン
        self.select_device_button = ft.ElevatedButton(
            "デバイス選択",
            on_click=self.show_device_selection_dialog,
            style=ft.ButtonStyle(
                color=ft.Colors.WHITE,
                bgcolor=ft.Colors.BLUE,
            ),
        )

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
        self.log_list_view = ft.ListView(
            expand=1,
            spacing=4,
            padding=4,
            auto_scroll=True,
        )

        self.log_area = ft.Container(
            content=ft.Column(
                [
                    ft.Text("ログ", size=16, weight=ft.FontWeight.BOLD),
                    self.log_list_view,
                ]
            ),
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
                            self.select_device_button,
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
                    self.log_area,
                ],
                expand=True,
            )
        )

        # 起動時のデバイスチェック
        self.check_device_on_startup()

        # 監視スレッドを開始
        self.start_monitoring_thread()

    def handle_window_event(self, e):
        """ウィンドウイベントを処理する"""
        if e.data == "close":
            # ウィンドウが閉じられる時にMIDIデータを保存
            self.save_on_exit()
            return False  # イベントのデフォルト処理を継続

    def save_on_exit(self):
        """アプリケーション終了時にMIDIデータを保存する"""
        try:
            if self.monitor and self.monitor.is_monitoring:
                # 録音中の場合、バッファに残っているデータを保存
                if self.monitor.has_buffered_events():
                    filepath = self.monitor.save_current_buffer()

                    # GUIが利用可能な場合はログメッセージを表示
                    if self.page and self.log_list_view:
                        self.log_message(f"終了時保存: {filepath}")

                    self.logger.log_info(
                        f"アプリケーション終了時にMIDIデータを保存しました: {filepath}"
                    )

                # 監視を停止
                self.monitor.stop_monitoring()
                self.monitor = None

        except Exception as e:
            error_msg = f"終了時保存エラー: {e}"

            # GUIが利用可能な場合はログメッセージを表示
            if self.page and self.log_list_view:
                self.log_message(error_msg)

            self.logger.log_error(error_msg)

    def start_recording(self, _):
        """録音を開始する"""
        try:
            # デバイスの可用性をチェック
            if not self.check_and_select_device():
                return

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
        try:
            if self.log_list_view and self.page:
                current_time = time.strftime("%H:%M:%S")
                log_entry = ft.Text(f"[{current_time}] {message}", size=12)
                self.log_list_view.controls.append(log_entry)

                # ログが長すぎる場合は古い部分を削除
                if len(self.log_list_view.controls) > self.MAX_LOG_LINES:
                    self.log_list_view.controls = self.log_list_view.controls[
                        -self.MAX_LOG_LINES :
                    ]

                # ページを更新
                self.page.update()

        except Exception as e:
            # GUIが利用できない場合はログファイルのみに記録
            self.logger.log_error(f"ログメッセージ表示エラー: {e}")
            self.logger.log_info(message)

    def show_device_selection_dialog(self, _):
        """デバイス選択ダイアログを表示する"""
        try:
            # デバッグログを追加
            self.log_message("デバイス選択ボタンがクリックされました")
            self.logger.log_info("デバイス選択ボタンがクリックされました")

            available_ports = self.device_manager.get_available_input_ports()
            current_port = self.midi_config.get("port_name", "default")

            self.log_message(f"利用可能なポート: {available_ports}")
            self.log_message(f"現在のポート: {current_port}")

            if not available_ports:
                self.log_message("利用可能なMIDIデバイスが見つかりません")
                return

            # デバイス選択UIを表示
            self.device_selection_container.visible = True
            self.page.add(self.device_selection_container)

            # デバイスリストを更新
            self.device_list_column.controls = []  # 既存のコントロールをクリア

            for i, port in enumerate(available_ports):
                # 現在選択されているポートかどうかを判定
                is_current = port == current_port
                status_text = "現在選択中" if is_current else "利用可能"
                status_color = ft.Colors.GREEN if is_current else ft.Colors.GREY

                # ラムダ関数の問題を修正
                def create_click_handler(selected_port):
                    def click_handler(e):
                        self.select_device(selected_port)

                    return click_handler

                self.device_list_column.controls.append(
                    ft.ListTile(
                        leading=ft.Icon("music_note", color=status_color),
                        title=ft.Text(
                            port,
                            weight=(
                                ft.FontWeight.BOLD
                                if is_current
                                else ft.FontWeight.NORMAL
                            ),
                        ),
                        subtitle=ft.Text(
                            f"MIDI入力ポート {i+1} - {status_text}", color=status_color
                        ),
                        on_click=create_click_handler(port),
                        selected=is_current,
                    )
                )

            self.page.update()
            self.log_message("デバイス選択UIを表示しました")
            self.log_message(
                f"デバイスリストに {len(available_ports)} 個のデバイスを追加しました"
            )
            self.log_message(
                f"デバイスリストのコントロール数: {len(self.device_list_column.controls)}"
            )

        except Exception as e:
            self.log_message(f"デバイス選択エラー: {e}")
            self.logger.log_error(f"デバイス選択エラー: {e}")
            import traceback

            self.log_message(f"エラー詳細: {traceback.format_exc()}")

    def select_device(self, port_name: str):
        """デバイスを選択する"""
        try:
            # 設定を更新
            self.config_manager.update_config("midi", "port_name", port_name)

            # 設定を再読み込み
            self.midi_config = self.config_manager.get_midi_config()

            # UIを更新
            self.port_info_text.value = f"ポート: {port_name}"
            self.page.update()

            # デバイス選択UIを非表示にする
            self.hide_device_selection(None)

            # ログメッセージを表示
            self.log_message(f"デバイスを選択しました: {port_name}")
            self.logger.log_info(f"デバイスを選択しました: {port_name}")

            # デバイス接続テスト
            if self.device_manager.test_port_connection(port_name):
                self.log_message(f"デバイス '{port_name}' の接続テストが成功しました")
                self.logger.log_info(
                    f"デバイス '{port_name}' の接続テストが成功しました"
                )
            else:
                self.log_message(
                    f"警告: デバイス '{port_name}' の接続テストに失敗しました"
                )
                self.logger.log_info(
                    f"デバイス '{port_name}' の接続テストに失敗しました"
                )

        except Exception as e:
            self.log_message(f"デバイス選択エラー: {e}")
            self.logger.log_error(f"デバイス選択エラー: {e}")

    def hide_device_selection(self, _):
        """デバイス選択UIを非表示にする"""
        try:
            if self.device_selection_container.visible:
                self.device_selection_container.visible = False
                self.page.update()
                self.log_message("デバイス選択UIを非表示にしました")
        except Exception as e:
            self.log_message(f"デバイス選択UI非表示エラー: {e}")
            self.logger.log_error(f"デバイス選択UI非表示エラー: {e}")

    def check_and_select_device(self) -> bool:
        """デバイスの可用性をチェックし、必要に応じて選択を促す"""
        try:
            port_name = self.midi_config.get("port_name", "default")

            if not self.device_manager.is_port_available(port_name):
                available_ports = self.device_manager.get_available_input_ports()

                if not available_ports:
                    self.log_message("利用可能なMIDIデバイスが見つかりません")
                    return False

                # 最初の利用可能なポートを自動選択
                if len(available_ports) == 1:
                    selected_port = available_ports[0]
                    self.config_manager.update_config(
                        "midi", "port_name", selected_port
                    )
                    self.midi_config = self.config_manager.get_midi_config()
                    self.port_info_text.value = f"ポート: {selected_port}"
                    self.page.update()
                    self.log_message(f"デバイスを自動選択しました: {selected_port}")
                    return True
                else:
                    # 複数のデバイスがある場合は選択を促す
                    self.log_message(f"設定されたポート '{port_name}' が見つかりません")
                    self.log_message(
                        "デバイス選択ボタンから利用可能なデバイスを選択してください"
                    )
                    return False

            return True

        except Exception as e:
            self.log_message(f"デバイスチェックエラー: {e}")
            self.logger.log_error(f"デバイスチェックエラー: {e}")
            return False

    def check_device_on_startup(self):
        """アプリケーション起動時にデバイスの可用性をチェックし、必要に応じてデバイス選択ダイアログを表示する"""
        try:
            port_name = self.midi_config.get("port_name", "default")
            if not self.device_manager.is_port_available(port_name):
                self.log_message(
                    f"設定されたポート '{port_name}' が見つかりません。デバイスを選択してください。"
                )
                self.show_device_selection_dialog(None)
            else:
                self.log_message(f"設定されたポート '{port_name}' が見つかりました。")
        except Exception as e:
            self.log_message(f"起動時デバイスチェックエラー: {e}")
            self.logger.log_error(f"起動時デバイスチェックエラー: {e}")
