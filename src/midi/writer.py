"""MIDIファイル書き込みモジュール"""

import os
import shutil
from collections import defaultdict
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

        self.is_note_pressed_by_note_number = defaultdict(bool)

    def _ensure_directory_exists(self) -> None:
        """出力ディレクトリが存在することを確認する"""
        if not os.path.exists(self.output_directory):
            os.makedirs(self.output_directory)
        if not os.path.exists(self.manual_save_directory):
            os.makedirs(self.manual_save_directory)

    def _process_message_on_cable_matter(self, message: mido.Message) -> mido.Message:
        """Cable MattersのMIDIケーブルのバグ対策

        Args:
            message (mido.Message): 処理するMIDIメッセージ

        Returns:
            mido.Message: 処理後のMIDIメッセージ
        """
        # Cable MattersのMIDIケーブルには、同時にnote_offがnote_onとして送信されるバグがある
        # このバグを回避するため、note_offが送信された場合はnote_onとして扱う
        if not message.is_meta and message.type in ["note_on", "note_off"]:
            if self.is_note_pressed_by_note_number[message.note]:
                message = mido.messages.messages.Message(
                    type="note_on",
                    note=message.note,
                    velocity=0,
                    time=message.time,
                )
                self.is_note_pressed_by_note_number[message.note] = False
            else:
                if message.type == "note_on":
                    self.is_note_pressed_by_note_number[message.note] = True
        return message

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

            # タイムスタンプを正規化（最初のメッセージを0にする）
            normalized_messages = self._normalize_timestamps(messages)

            # メッセージをトラックに追加
            for message in normalized_messages:
                # メッセージタイプがMetaMessageでない場合のみ追加
                if not hasattr(message, "type") or message.type != "set_tempo":
                    track.append(self._process_message_on_cable_matter(message))

            # ファイルに書き込み
            midi_file.save(filepath)

            return filepath

        except Exception as e:
            raise FileWriteError(f"ファイル書き込みに失敗しました: {e}")

    def copy_latest_auto_save_to_manual_save(self) -> Optional[str]:
        """自動保存ディレクトリの最新ファイルを手動保存ディレクトリにコピーする

        Returns:
            コピーされたファイルのパス（ファイルがない場合はNone）
        """
        try:
            # 自動保存ディレクトリの最新ファイルを取得
            latest_file = self._get_latest_auto_save_file()
            if not latest_file:
                return None

            # 手動保存用のファイル名を生成
            manual_filename = self._generate_filename(is_manual_save=True)
            manual_filepath = os.path.join(self.manual_save_directory, manual_filename)

            # ファイルをコピー
            shutil.copy2(latest_file, manual_filepath)

            return manual_filepath

        except Exception as e:
            raise FileWriteError(f"最新ファイルのコピーに失敗しました: {e}")

    def _get_latest_auto_save_file(self) -> Optional[str]:
        """自動保存ディレクトリの最新ファイルを取得する

        Returns:
            最新ファイルのパス（ファイルがない場合はNone）
        """
        if not os.path.exists(self.output_directory):
            return None

        # .midファイルのみを対象とする
        midi_files = []
        for filename in os.listdir(self.output_directory):
            if filename.endswith(".mid") and not filename.startswith("manual_save_"):
                filepath = os.path.join(self.output_directory, filename)
                midi_files.append(filepath)

        if not midi_files:
            return None

        # 最新のファイルを返す（ファイル名のタイムスタンプで判定）
        return max(midi_files, key=os.path.getctime)

    def _normalize_timestamps(self, messages: List[mido.Message]) -> List[mido.Message]:
        """タイムスタンプを正規化して最初のメッセージを0にする

        Args:
            messages: 正規化するメッセージリスト

        Returns:
            正規化されたメッセージリスト
        """
        if not messages:
            return messages

        # メッセージのコピーを作成（元のメッセージを変更しない）
        normalized_messages = []
        for msg in messages:
            # メッセージのコピーを作成
            if hasattr(msg, "copy"):
                new_msg = msg.copy()
            else:
                # copyメソッドがない場合は新しいメッセージを作成
                new_msg = mido.Message(
                    type=msg.type,
                    note=msg.note if hasattr(msg, "note") else None,
                    velocity=(msg.velocity if hasattr(msg, "velocity") else None),
                    channel=msg.channel if hasattr(msg, "channel") else 0,
                    time=msg.time,
                )
            normalized_messages.append(new_msg)

        # 最初のメッセージのタイムスタンプを0に設定
        if normalized_messages:
            normalized_messages[0].time = 0

        # 後続のメッセージのタイムスタンプを相対的に調整
        for i in range(1, len(normalized_messages)):
            # 前のメッセージからの相対時間を計算
            if i == 1:
                # 2番目のメッセージは最初のメッセージからの相対時間
                normalized_messages[i].time = messages[i].time
            else:
                # 3番目以降は前のメッセージからの相対時間
                normalized_messages[i].time = messages[i].time

        return normalized_messages

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
