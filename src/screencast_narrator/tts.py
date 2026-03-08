"""TTS interface and Kokoro implementation."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path
from shutil import copy2


class TTSBackend(ABC):
    @abstractmethod
    def generate(self, text: str, output_path: Path, voice: str | None = None) -> None: ...


class KokoroTTS(TTSBackend):
    def __init__(self, voice: str = "bf_alice", cache_dir: Path | None = None) -> None:
        self._voice = voice
        self._cache_dir = cache_dir or Path.home() / ".cache" / "screencast-narrator-tts"

    def generate(self, text: str, output_path: Path, voice: str | None = None) -> None:
        effective_voice = voice or self._voice
        self._cache_dir.mkdir(parents=True, exist_ok=True)
        cached = self._cache_dir / (self._cache_key(text, effective_voice) + ".wav")

        if cached.exists():
            copy2(cached, output_path)
            return

        self._generate_raw(text, output_path, effective_voice)
        copy2(output_path, cached)

    def _generate_raw(self, text: str, output_path: Path, voice: str) -> None:
        import kokoro
        import numpy as np
        import soundfile as sf

        pipeline = kokoro.KPipeline(lang_code="b")
        all_audio = []
        for _gs, _ps, audio in pipeline(text, voice=voice, speed=1.0):
            all_audio.append(audio)
        combined = np.concatenate(all_audio)
        sf.write(str(output_path), combined, 24000)

    def _cache_key(self, text: str, voice: str) -> str:
        data = f"{voice}:{text}".encode()
        digest = hashlib.sha256(data).hexdigest()[:16]
        return f"{voice}_{digest}"
