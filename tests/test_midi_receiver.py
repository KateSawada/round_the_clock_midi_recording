"""MIDIReceiver テスト"""

from unittest.mock import Mock, patch

import mido
import pytest

from src.midi.receiver import MIDIReceiver
from src.utils.exceptions import MIDIError


class TestMIDIReceiver:
    """MIDIReceiverのテストクラス"""

    def test_init_with_valid_port(self):
        """有効なポート名で初期化できることを確認"""
        receiver = MIDIReceiver("test_port")
        assert receiver.port_name == "test_port"
        assert not receiver.is_recording
        assert len(receiver.messages) == 0

    def test_start_recording_success(self):
        """録音開始が正常に動作することを確認"""
        with patch("mido.get_input_names") as mock_get_names:
            with patch("mido.open_input") as mock_open:
                mock_get_names.return_value = ["test_port"]
                mock_port = Mock()
                mock_open.return_value = mock_port

                receiver = MIDIReceiver("test_port")
                receiver.start_recording()

                assert receiver.is_recording
                mock_open.assert_called_once_with("test_port")

    def test_start_recording_failure(self):
        """録音開始失敗時のエラーハンドリングを確認"""
        with patch("mido.get_input_names") as mock_get_names:
            mock_get_names.return_value = []

            receiver = MIDIReceiver("invalid_port")

            with pytest.raises(MIDIError):
                receiver.start_recording()

    def test_stop_recording(self):
        """録音停止が正常に動作することを確認"""
        receiver = MIDIReceiver("test_port")
        receiver.is_recording = True
        receiver._port = Mock()

        receiver.stop_recording()

        assert not receiver.is_recording
        assert receiver._port is None

    def test_get_messages_empty_buffer(self):
        """空のバッファからメッセージを取得した場合の動作確認"""
        receiver = MIDIReceiver("test_port")
        messages = receiver.get_messages()

        assert messages == []
        assert len(receiver.messages) == 0

    def test_get_messages_with_data(self):
        """データがあるバッファからメッセージを取得した場合の動作確認"""
        receiver = MIDIReceiver("test_port")
        test_message = mido.Message("note_on", note=60, velocity=64, time=0)
        receiver.messages.append(test_message)

        messages = receiver.get_messages()

        assert len(messages) == 1
        assert messages[0] == test_message
        assert len(receiver.messages) == 0

    def test_has_messages(self):
        """メッセージ存在確認が正常に動作することを確認"""
        receiver = MIDIReceiver("test_port")

        # 空の場合
        assert not receiver.has_messages()

        # メッセージがある場合
        test_message = mido.Message("note_on", note=60, velocity=64, time=0)
        receiver.messages.append(test_message)
        assert receiver.has_messages()

    def test_get_message_count(self):
        """メッセージ数の取得が正常に動作することを確認"""
        receiver = MIDIReceiver("test_port")

        # 空の場合
        assert receiver.get_message_count() == 0

        # メッセージがある場合
        test_message = mido.Message("note_on", note=60, velocity=64, time=0)
        receiver.messages.append(test_message)
        assert receiver.get_message_count() == 1

    def test_clear_messages(self):
        """メッセージバッファのクリアが正常に動作することを確認"""
        receiver = MIDIReceiver("test_port")
        test_message = mido.Message("note_on", note=60, velocity=64, time=0)
        receiver.messages.append(test_message)

        receiver.clear_messages()

        assert len(receiver.messages) == 0
