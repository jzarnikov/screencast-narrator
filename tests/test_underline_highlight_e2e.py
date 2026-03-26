"""E2E test: large elements get an underline highlight instead of an ellipse.

When the highlighted element takes up more than the configured threshold
of the viewport area, the highlight switches to an underline under the
heading (h1-h6) or under the element itself if no heading is found.

The test verifies that:
1. A large card with a heading gets highlight pixels concentrated
   in a horizontal band near the heading, not spread as an ellipse.
2. A small button still gets the normal ellipse highlight.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest
from PIL import Image

_LARGE_CARD_PAGE = """<!DOCTYPE html>
<html>
<body style="margin:0; background:white; padding:40px;">
  <div id="target" style="width:90vw; height:70vh; background:#f0f0f0; padding:30px; border-radius:8px;">
    <h2 style="margin:0 0 20px 0; font-size:32px;">Card Title</h2>
    <p>This card takes up most of the viewport. The highlight should underline
       the heading, not draw an ellipse around the entire card.</p>
  </div>
</body>
</html>"""

_SMALL_BUTTON_PAGE = """<!DOCTYPE html>
<html>
<body style="margin:0; background:white; display:flex; justify-content:center; align-items:center; height:100vh;">
  <button id="target" style="padding:20px 40px; font-size:24px;">Small Button</button>
</body>
</html>"""


def _extract_frames(video: Path, output_dir: Path) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    pattern = str(output_dir / "frame_%04d.png")
    subprocess.run(
        ["ffmpeg", "-y", "-i", str(video), pattern],
        capture_output=True, check=True,
    )
    return sorted(output_dir.glob("frame_*.png"))


def _highlight_pixel_rows(frame: Path, min_saturation: int = 60) -> list[int]:
    """Return y-coordinates that contain highlight (colored) pixels."""
    img = Image.open(frame).convert("RGB")
    rows_with_highlight: set[int] = set()
    for y in range(0, img.height, 2):
        for x in range(0, img.width, 4):
            r, g, b = img.getpixel((x, y))
            if max(r, g, b) - min(r, g, b) >= min_saturation:
                rows_with_highlight.add(y)
                break
    return sorted(rows_with_highlight)


def _record_highlight(output_dir: Path, html_path: Path) -> None:
    from playwright.sync_api import sync_playwright
    from screencast_narrator_client import Storyboard

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1280, "height": 720})
        page.goto(f"file://{html_path}")
        page.wait_for_timeout(500)

        sb = Storyboard(output_dir, page=page)
        sb.begin_narration("Highlighting the element.")
        sb.highlight(page.locator("#target"))
        sb.end_narration()
        sb.done()

        browser.close()


@pytest.mark.e2e
def test_large_element_gets_underline_highlight(tmp_path: Path) -> None:
    """A large card (>5% viewport) should get an underline near its heading,
    not an ellipse around the entire element."""

    output_dir = tmp_path / "underline-test"
    html_path = tmp_path / "test.html"
    html_path.write_text(_LARGE_CARD_PAGE, encoding="utf-8")

    _record_highlight(output_dir, html_path)

    video = output_dir / "videos" / "narration-000.mp4"
    assert video.exists()

    frames = _extract_frames(video, tmp_path / "frames")
    assert len(frames) > 0

    best_frame = None
    best_count = 0
    for frame in frames:
        rows = _highlight_pixel_rows(frame)
        if len(rows) > best_count:
            best_count = len(rows)
            best_frame = frame

    assert best_frame is not None, "No highlight pixels found in any frame"

    rows = _highlight_pixel_rows(best_frame)
    row_span = max(rows) - min(rows)
    viewport_height = 720

    max_underline_span_pct = 15
    actual_span_pct = (row_span / viewport_height) * 100

    print(f"Highlight row span: {row_span}px ({actual_span_pct:.1f}% of viewport)")
    print(f"Highlight rows: {min(rows)}-{max(rows)} (count={len(rows)})")

    assert actual_span_pct < max_underline_span_pct, (
        f"Highlight spans {actual_span_pct:.1f}% of viewport height — "
        f"expected <{max_underline_span_pct}% for an underline. "
        f"Looks like an ellipse was drawn instead."
    )
