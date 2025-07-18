"""MIDIファイル書き込みモジュール"""

import os
from datetime import datetime
from typing import List, Optional

import mido

from ..utils.exceptions import FileWriteError


class MIDIFileWriter:
    """MIDIメッセージをMIDIファイルに書き出すクラス"""

    def __init__(
        self, output_directory: str, manual_save_directory: Optional[str] = None
    ) -> None:
        """MIDIFileWriterを初期化する

        Args:
            output_directory: 出力ディレクトリパス
            manual_save_directory: 手動保存用ディレクトリパス（Noneの場合はoutput_directoryと同じ）
        """
        self.output_directory = output_directory
        self.manual_save_directory = manual_save_directory or output_directory
        self._ensure_directory_exists()

    def _ensure_directory_exists(self) -> None:
        """出力ディレクトリが存在することを確認する"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        if not os.path.exists(self.manual_save_directory):
            os.makedirs(self.manual_save_directory)

    def write_messages(
        self,
        messages: List[mido.Message],
        filename: Optional[str] = None,
        is_manual_save: bool = False,
    ) -> str:
        """MIDIメッセージをファイルに書き出す

        Args:
            messages: 書き出すメッセージリスト
            filename: ファイル名（Noneの場合は自動生成）
            is_manual_save: 手動保存かどうか（Trueの場合は手動保存用ディレクトリに保存）

        Returns:
            保存されたファイルのパス

        Raises:
            FileWriteError: ファイル書き込みに失敗した場合
        """
        try:
            if not filename:
                filename = self._generate_filename(is_manual_save)

            # 手動保存の場合は専用ディレクトリに保存
            if is_manual_save:
                filepath = os.path.join(self.manual_save_directory, filename)
            else:
                filepath = os.path.join(self.output_directory, filename)

            # MIDIファイルの作成
            midi_file = mido.MidiFile(type=1)  # マルチトラック形式
            track = mido.MidiTrack()
            midi_file.tracks.append(track)

            # テンポ情報を追加（デフォルト120 BPM）
            tempo_message = mido.MetaMessage(
                "set_tempo", tempo=mido.bpm2tempo(120), time=0
            )
            track.append(tempo_message)

            # メッセージをトラックに追加（タイムスタンプを保持）
            for message in messages:
                # メッセージタイプがMetaMessageでない場合のみ追加
                if not hasattr(message, "type") or message.type != "set_tempo":
                    # タイムスタンプが設定されていない場合は0に設定
                    if not hasattr(message, "time") or message.time is None:
                        message.time = 0
                    track.append(message)

            # ファイルに書き込み
            midi_file.save(filepath)

            return filepath

        except Exception as e:
            raise FileWriteError(f"ファイル書き込みに失敗しました: {e}")

    def _generate_filename(self, is_manual_save: bool = False) -> str:
        """自動ファイル名を生成する

        Args:
            is_manual_save: 手動保存かどうか

        Returns:
            yyyymmddhhmmss.mid形式のファイル名（手動保存の場合はmanual_save_プレフィックス付き）
        """
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        if is_manual_save:
            return f"manual_save_{timestamp}.mid"
        else:
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

    def get_manual_save_directory(self) -> str:
        """手動保存用ディレクトリを取得する

        Returns:
            手動保存用ディレクトリパス
        """
        return self.manual_save_directory

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
