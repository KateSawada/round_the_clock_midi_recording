"""自動保存タイマーモジュール"""

import threading
from typing import Callable, Optional

from .exceptions import TimerError


class AutoSaveTimer:
    """一定時間後に自動保存を実行するタイマークラス"""

    def __init__(self, timeout_seconds: int = 300) -> None:
        """AutoSaveTimerを初期化する

        Args:
            timeout_seconds: タイムアウト時間（秒）
        """
        self.timeout_seconds = timeout_seconds
        self._timer: Optional[threading.Timer] = None
        self._callback: Optional[Callable[[], None]] = None
        self._is_running = False

    def start_timer(self, callback: Callable[[], None]) -> None:
        """タイマーを開始する

        Args:
            callback: タイムアウト時に実行されるコールバック

        Raises:
            TimerError: タイマーが既に実行中の場合
        """
        if self._is_running:
            raise TimerError("タイマーは既に実行中です")

        self._callback = callback
        self._timer = threading.Timer(self.timeout_seconds, self._execute_callback)
        self._timer.start()
        self._is_running = True

    def reset_timer(self) -> None:
        """タイマーをリセットする"""
        if self._timer:
            self._timer.cancel()
        if self._callback:
            self._timer = threading.Timer(self.timeout_seconds, self._execute_callback)
            self._timer.start()
            self._is_running = True
            # デバッグ情報を追加
            print(
                f"Timer reset: timeout={self.timeout_seconds}s, "
                f"running={self._is_running}"
            )

    def stop_timer(self) -> None:
        """タイマーを停止する"""
        if self._timer:
            self._timer.cancel()
        self._is_running = False
        self._timer = None
        self._callback = None

    def _execute_callback(self) -> None:
        """コールバックを実行する"""
        if self._callback:
            try:
                print(f"Timer callback executed: timeout={self.timeout_seconds}s")
                self._callback()
                # コールバック実行後もタイマーを継続する（新しいタイマーを開始）
                if self._is_running:
                    self._timer = threading.Timer(
                        self.timeout_seconds, self._execute_callback
                    )
                    self._timer.start()
            except Exception as e:
                # コールバック実行中のエラーをログに記録
                print(f"Timer callback error: {e}")
                # エラーが発生した場合もタイマーを継続する
                if self._is_running:
                    self._timer = threading.Timer(
                        self.timeout_seconds, self._execute_callback
                    )
                    self._timer.start()

    def is_running(self) -> bool:
        """タイマーが実行中かどうかを確認する

        Returns:
            実行中の場合はTrue
        """
        return self._is_running

    def get_remaining_time(self) -> Optional[float]:
        """残り時間を取得する

        Returns:
            残り時間（秒）、タイマーが停止中の場合はNone
        """
        if not self._is_running or not self._timer:
            return None

        # 簡易的な実装（実際の残り時間は計算が複雑）
        return self.timeout_seconds
