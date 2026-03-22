"""E2E test: verify CDP frame delivery captures screen changes across waits.

Chrome's CDP screencast delivers frames only on repaint. Without frame acks,
Chrome throttles delivery, and without gap filling, static waits compress
the video. This test verifies that distinct visual states (background colors)
are all captured in the output video, even when separated by waits.

The test page changes from red → blue → green with waits between each.
The video must contain frames showing all three colors.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from PIL import Image

from screencast_narrator.ffmpeg import probe_duration_ms

_PROJECT_ROOT = Path(__file__).parent.parent
_EXAMPLES_DIR = _PROJECT_ROOT / "examples"

_TEST_PAGE = """<!DOCTYPE html>
<html>
<body style="margin:0; background:white; width:100vw; height:100vh;">
</body>
</html>"""

MINIMUM_EXPECTED_DURATION_MS = 2000


def _extract_frames(video: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(output_dir / "frame_%04d.png")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), pattern],
        capture_output=True, check=True,
    )
    return sorted(output_dir.glob("frame_*.png"))


def _dominant_color(frame: Path) -> str:
    img = Image.open(frame).convert("RGB")
    cx, cy = img.width // 2, img.height // 2
    r, g, b = img.getpixel((cx, cy))
    if r > 120 and g < 100 and b < 100:
        return "red"
    if b > 120 and r < 100 and g < 100:
        return "blue"
    if g > 100 and r < 80 and b < 80:
        return "green"
    return f"other(r={r},g={g},b={b})"


def _run_java_recording(output_dir: Path, html_path: Path, use_pause: bool) -> None:
    args = [
        "mvn", "-f", str(_EXAMPLES_DIR / "pom.xml"),
        "compile", "exec:java",
        "-Dexec.mainClass=RecordPauseTest",
    ]
    exec_args = f"{output_dir} {html_path}"
    if use_pause:
        exec_args += " use-pause"
    args.append(f"-Dexec.args={exec_args}")

    result = subprocess.run(
        args, capture_output=True, text=True, timeout=120, cwd=str(_EXAMPLES_DIR),
    )
    if result.returncode != 0:
        raise RuntimeError(f"Java recording failed:\n{result.stdout}\n{result.stderr}")


@pytest.mark.e2e
def test_java_narration_captures_all_color_changes(tmp_path: Path) -> None:
    """A narration that changes background red → blue → green with waits
    must produce a video containing frames of all three colors."""

    output_dir = tmp_path / "pause-test"
    test_html = tmp_path / "test.html"
    test_html.write_text(_TEST_PAGE, encoding="utf-8")

    _run_java_recording(output_dir, test_html, use_pause=True)

    video = output_dir / "videos" / "narration-000.mp4"
    assert video.exists(), f"Video not found at {video}"

    duration_ms = probe_duration_ms(video)
    print(f"Video duration: {duration_ms}ms")
    assert duration_ms >= MINIMUM_EXPECTED_DURATION_MS, (
        f"Video is only {duration_ms}ms, expected at least {MINIMUM_EXPECTED_DURATION_MS}ms"
    )

    frames = _extract_frames(video, tmp_path / "frames")
    colors_seen: set[str] = set()
    for frame in frames:
        color = _dominant_color(frame)
        colors_seen.add(color)

    print(f"Colors seen in {len(frames)} frames: {colors_seen}")

    assert "red" in colors_seen, f"Red background not found in video. Seen: {colors_seen}"
    assert "blue" in colors_seen, f"Blue background not found in video. Seen: {colors_seen}"
    assert "green" in colors_seen, f"Green background not found in video. Seen: {colors_seen}"
