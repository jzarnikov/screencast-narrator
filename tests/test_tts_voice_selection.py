"""Tests for per-language voice selection in TTS generation."""

from __future__ import annotations

from pathlib import Path

from screencast_narrator.merge import _generate_tts_audio, _resolve_voice, _segment_name
from screencast_narrator.tts import TTSBackend
from screencast_narrator_client.generated.storyboard_types import (
    Model as StoryboardModel,
    Narration as StoryboardNarration,
    Options,
)


class _RecordingTTSBackend(TTSBackend):
    def __init__(self) -> None:
        self.calls: list[tuple[str, Path, str | None]] = []

    def generate(self, text: str, output_path: Path, voice: str | None = None) -> None:
        self.calls.append((text, output_path, voice))
        output_path.write_bytes(b"RIFF" + b"\x00" * 40)


def _make_storyboard(
    narrations: list[StoryboardNarration],
    language: str = "en",
    voices: dict[str, dict[str, str]] | None = None,
) -> StoryboardModel:
    return StoryboardModel(
        language=language,
        narrations=narrations,
        options=Options(voices=voices) if voices else None,
    )


def test_resolve_voice_with_explicit_voice_id() -> None:
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Hello", voice="nathaly")],
        voices={"nathaly": {"en": "bf_alice", "de": "de_natasha"}},
    )
    assert _resolve_voice(storyboard, storyboard.narrations[0]) == "bf_alice"


def test_resolve_voice_defaults_to_first_voice() -> None:
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Hello")],
        voices={"nathaly": {"en": "bf_alice"}},
    )
    assert _resolve_voice(storyboard, storyboard.narrations[0]) == "bf_alice"


def test_resolve_voice_returns_none_without_voices() -> None:
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Hello")],
    )
    assert _resolve_voice(storyboard, storyboard.narrations[0]) is None


def test_resolve_voice_returns_none_for_missing_language() -> None:
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Hello")],
        language="fr",
        voices={"nathaly": {"en": "bf_alice", "de": "de_natasha"}},
    )
    assert _resolve_voice(storyboard, storyboard.narrations[0]) is None


def test_resolve_voice_different_narrations_different_voices() -> None:
    storyboard = _make_storyboard(
        [
            StoryboardNarration(narration_id=0, text="Hello", voice="nathaly"),
            StoryboardNarration(narration_id=1, text="World", voice="james"),
        ],
        voices={
            "nathaly": {"en": "bf_alice"},
            "james": {"en": "am_michael"},
        },
    )
    assert _resolve_voice(storyboard, storyboard.narrations[0]) == "bf_alice"
    assert _resolve_voice(storyboard, storyboard.narrations[1]) == "am_michael"


def test_generate_tts_passes_resolved_voice(tmp_path: Path) -> None:
    tts = _RecordingTTSBackend()
    storyboard = _make_storyboard(
        [
            StoryboardNarration(narration_id=0, text="Hello", voice="nathaly"),
            StoryboardNarration(narration_id=1, text="World", voice="james"),
        ],
        voices={
            "nathaly": {"en": "bf_alice"},
            "james": {"en": "am_michael"},
        },
    )
    _generate_tts_audio(storyboard, tmp_path, tts)

    assert len(tts.calls) == 2
    assert tts.calls[0][2] == "bf_alice"
    assert tts.calls[1][2] == "am_michael"


def test_generate_tts_without_voices_passes_none(tmp_path: Path) -> None:
    tts = _RecordingTTSBackend()
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Hello")],
    )
    _generate_tts_audio(storyboard, tmp_path, tts)

    assert len(tts.calls) == 1
    assert tts.calls[0][2] is None


def test_generate_tts_skips_empty_text(tmp_path: Path) -> None:
    tts = _RecordingTTSBackend()
    storyboard = _make_storyboard([
        StoryboardNarration(narration_id=0, text=""),
        StoryboardNarration(narration_id=1, text="Has text"),
        StoryboardNarration(narration_id=2, text=""),
    ])
    _generate_tts_audio(storyboard, tmp_path, tts)

    assert len(tts.calls) == 1
    assert tts.calls[0][0] == "Has text"


def test_generate_tts_does_not_regenerate_existing(tmp_path: Path) -> None:
    tts = _RecordingTTSBackend()
    storyboard = _make_storyboard(
        [StoryboardNarration(narration_id=0, text="Already exists")],
    )
    (tmp_path / _segment_name(0)).write_bytes(b"existing")
    _generate_tts_audio(storyboard, tmp_path, tts)

    assert len(tts.calls) == 0
