# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

screencast-narrator is a Python library that turns screen recordings into narrated screencasts. It records a timeline of events during browser automation, generates TTS audio, detects sync frames, calculates freeze frames, and merges everything into a final video using FFmpeg.

## Commands

```bash
# Install for development (with TTS support)
pip install -e ".[dev,tts]"

# Run all tests
pytest

# Run a single test file
pytest tests/test_freeze_frames.py -v

# Run a single test
pytest tests/test_freeze_frames.py::test_name -v

# CLI entry point
screencast-narrator /path/to/recording-output/
```

**System dependencies:** ffmpeg (must be on PATH), libzbar (Ubuntu: `libzbar0`, macOS: `brew install zbar`). On macOS, pyzbar needs: `DYLD_LIBRARY_PATH=/opt/homebrew/lib pytest`.

## Architecture

The pipeline in `src/screencast_narrator/` has 7 stages, orchestrated by `merge.py:process()`:

1. **timeline.py** — Records events (narration, highlight, action, sync_frame, title_card) with millisecond timestamps during Playwright browser automation. Serializes to `timeline.json` with camelCase keys.

2. **sync_frames.py** — Injects green QR-code overlay frames into the browser at narration boundaries. QR payload: `SYNC|{narration_id}|{START|END}`, displayed for 160ms.

3. **tts.py** — Pluggable `TTSBackend` protocol. Default: KokoroTTS (voice "bf_alice", 24kHz WAV). Caches files under `~/.cache/screencast-narrator-tts/` keyed by SHA256 of "voice:text".

4. **sync_detect.py** — Extracts frames at 25 FPS, detects green frames (R<80, G>180, B<80), decodes QR codes via pyzbar. Returns QR spans, green frame indices, total count.

5. **freeze_frames.py** — When narration audio exceeds the action duration, calculates where to insert freeze frames. Avoids freezing during visual highlights. Also detects dead air gaps (>2s with no narration).

6. **merge.py** (545 lines, largest module) — Two pipelines: **sync-frame** (green QR frames for frame-accurate sync) and **wall-clock** (timeline timestamps with time scaling). Builds extended video with freeze frames, cuts dead air, overlays audio via FFmpeg filter graphs.

7. **timeline_html.py** — Generates interactive HTML timeline visualizations (original, adjusted, combined views) at 100px/second scale with lane-based narration layout.

**ffmpeg.py** — Thin wrappers around `ffmpeg`/`ffprobe` subprocesses.

## Key Conventions

- Python >=3.11, tested on 3.11/3.12/3.13
- Timeline JSON uses camelCase keys (timestampMs, endTimestampMs, narrationId)
- Package uses setuptools via pyproject.toml (no setup.py/requirements.txt)
- Optional dependencies split into `[tts]` and `[dev]` extras
