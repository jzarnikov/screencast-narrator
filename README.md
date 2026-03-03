# screencast-narrator

Turn raw screen recordings + narration text into polished narrated screencasts.

**screencast-narrator** is a Python library and CLI that takes a Playwright (or any) screen recording together with timestamped narration text and produces a final video with:

- Text-to-speech narration synced to on-screen actions
- QR-code-based frame-accurate synchronization
- Automatic freeze-frame insertion when narration overflows action duration
- Dead-air gap detection and cutting
- Interactive HTML timeline visualizations

## Installation

```bash
pip install screencast-narrator
```

For TTS support (Kokoro):
```bash
pip install screencast-narrator[tts]
```

System dependencies:
```bash
# macOS
brew install ffmpeg zbar

# Ubuntu/Debian
apt-get install ffmpeg libzbar0
```

## Quick Start

### As a library with Playwright

```python
from pathlib import Path
from playwright.sync_api import sync_playwright
from screencast_narrator.timeline import ScreencastTimeline
from screencast_narrator.sync_frames import inject_sync_frame
from screencast_narrator.merge import process

output_dir = Path("my-screencast")
output_dir.mkdir(exist_ok=True)

timeline = ScreencastTimeline(output_dir, video_enabled=True)

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(
        record_video_dir=str(output_dir / "videos"),
        record_video_size={"width": 1920, "height": 1080},
    )
    page = context.new_page()
    timeline.video_recording_started()

    # Narration bracket with sync frames
    timeline.begin_narration_bracket()
    inject_sync_frame(page, timeline.active_narration_id(), "START")

    page.goto("https://example.com")
    timeline.add_action("Navigate to example.com")

    inject_sync_frame(page, timeline.active_narration_id(), "END")
    timeline.add_narration("We open the example website.", start_ms=0, end_ms=2000)
    timeline.end_narration_bracket()

    timeline.video_recording_ended()
    context.close()
    browser.close()

# Produce the final narrated video
process(output_dir)
```

### As a CLI

```bash
screencast-narrator /path/to/recording-output/
```

The directory must contain:
- A `timeline.json` file (produced by `ScreencastTimeline`)
- A video file (`.webm`) in a `videos/` subdirectory

## Architecture

The pipeline has these stages:

1. **Timeline recording** (`timeline.py`) — During your test/recording, track narrations, actions, highlights, and sync frames with timestamps.

2. **Sync frame injection** (`sync_frames.py`) — Inject green QR-code overlay frames into the browser at narration bracket boundaries for frame-accurate sync.

3. **TTS generation** (`tts.py`) — Convert narration text to speech audio files. Pluggable backend; ships with Kokoro TTS.

4. **Sync detection** (`sync_detect.py`) — Extract frames from the recorded video, detect green sync frames, decode QR codes to map video frames to narration events.

5. **Freeze frame calculation** (`freeze_frames.py`) — When narration audio is longer than the on-screen action, calculate where to insert freeze frames (paused video) so audio and video stay in sync. Avoids placing freezes during visual highlights.

6. **Video merge** (`merge.py`) — Orchestrate FFmpeg to build the final video: insert freeze frames, overlay audio, cut dead air gaps, concatenate segments.

7. **Timeline visualization** (`timeline_html.py`) — Generate interactive HTML timelines showing original events, adjusted (post-freeze) positions, and a combined three-column view.

## Modules

| Module | Purpose |
|--------|---------|
| `timeline.py` | Event recording during screen capture |
| `sync_frames.py` | QR code overlay injection for frame-accurate sync |
| `sync_detect.py` | Green frame detection and QR decoding from video |
| `freeze_frames.py` | Freeze frame calculation algorithm |
| `tts.py` | Pluggable TTS backend (Kokoro default) |
| `ffmpeg.py` | FFmpeg subprocess helpers |
| `merge.py` | Main merge pipeline and CLI entry point |
| `timeline_html.py` | HTML timeline visualization generator |

## Custom TTS Backend

Implement the `TTSBackend` protocol:

```python
from screencast_narrator.tts import TTSBackend
from pathlib import Path

class MyTTS(TTSBackend):
    def generate(self, text: str, output_path: Path) -> None:
        # Generate audio file at output_path
        ...

# Use it
from screencast_narrator.merge import process
process(target_dir, tts_backend=MyTTS())
```

## Development

```bash
git clone https://github.com/mmarinschek/screencast-narrator.git
cd screencast-narrator
pip install -e ".[dev,tts]"

# Run tests
pytest tests/ -v

# On macOS, if pyzbar can't find libzbar:
DYLD_LIBRARY_PATH=/opt/homebrew/lib pytest tests/ -v
```

## License

Apache License 2.0 — see [LICENSE](LICENSE).
