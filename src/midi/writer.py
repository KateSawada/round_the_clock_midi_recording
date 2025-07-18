"""MIDIファイル書き込みモジュール"""

import os
from datetime import datetime
from typing import List, Optional

import mido

from ..utils.exceptions import FileWriteError


class MIDIFileWriter:
    """MIDIメッセージをMIDIファイルに書き出すクラス"""

    def __init__(self, output_directory: str) -> None:
        """MIDIFileWriterを初期化する

        Args:
            output_directory: 出力ディレクトリパス
        """
        self.output_directory = output_directory
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """出力ディレクトリが存在することを確認する"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)

    def write_messages(
        self, messages: List[mido.Message], filename: Optional[str] = None
    ) -> str:
        """MIDIメッセージをファイルに書き出す

        Args:
            messages: 書き出すメッセージリスト
            filename: ファイル名（Noneの場合は自動生成）

        Returns:
            保存されたファイルのパス

        Raises:
            FileWriteError: ファイル書き込みに失敗した場合
        """
        try:
            if not filename:
                filename = self._generate_filename()

            filepath = os.path.join(self.output_directory, filename)

            # MIDIファイルの作成
            midi_file = mido.MidiFile()
            track = mido.MidiTrack()
            midi_file.tracks.append(track)

            # メッセージをトラックに追加
            for message in messages:
                track.append(message)

            # ファイルに書き込み
            midi_file.save(filepath)

            return filepath

        except Exception as e:
            raise FileWriteError(f"ファイル書き込みに失敗しました: {e}")

    def _generate_filename(self) -> str:
        """自動ファイル名を生成する

        Returns:
            yyyymmddhhmmss.mid形式のファイル名
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"{timestamp}.mid"

    def write_messages_to_track(
        self, messages: List[mido.Message], filename: Optional[str] = None
    ) -> str:
        """MIDIメッセージを適切なトラック構造でファイルに書き出す

        Args:
            messages: 書き出すメッセージリスト
            filename: ファイル名（Noneの場合は自動生成）

        Returns:
            保存されたファイルのパス

        Raises:
            FileWriteError: ファイル書き込みに失敗した場合
        """
        try:
            if not filename:
                filename = self._generate_filename()

            filepath = os.path.join(self.output_directory, filename)

            # MIDIファイルの作成
            midi_file = mido.MidiFile()

            # メインのMIDIトラック
            track = mido.MidiTrack()
            midi_file.tracks.append(track)

            # メッセージをトラックに追加（タイムスタンプを保持）
            for message in messages:
                track.append(message)

            # ファイルに書き込み
            midi_file.save(filepath)

            return filepath

        except Exception as e:
            raise FileWriteError(f"ファイル書き込みに失敗しました: {e}")

    def get_output_directory(self) -> str:
        """出力ディレクトリを取得する

        Returns:
            出力ディレクトリパス
        """
        return self.output_directory

    def list_saved_files(self) -> List[str]:
        """保存されたファイル一覧を取得する

        Returns:
            ファイル名のリスト
        """
        if not os.path.exists(self.output_directory):
            return []

        files = []
        for filename in os.listdir(self.output_directory):
            if filename.endswith(".mid"):
                files.append(filename)

        return sorted(files)
