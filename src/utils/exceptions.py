"""カスタム例外クラス定義"""


class MIDIError(Exception):
    """MIDI関連のエラー"""

    pass


class FileWriteError(Exception):
    """ファイル書き込みエラー"""

    pass


class ConfigError(Exception):
    """設定ファイルエラー"""

    pass


class TimerError(Exception):
    """タイマー関連のエラー"""

    pass
