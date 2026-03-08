"""Long-running drift test: browse Wikipedia for ~30 min, check for cumulative drift.

Skipped by default. Run with:
    DYLD_LIBRARY_PATH=/opt/homebrew/lib pytest tests/test_long_running_drift.py -v -s --run-long
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest
from PIL import Image
from pyzbar.pyzbar import decode as decode_qr

from screencast_narrator.merge import process
from screencast_narrator_client import Storyboard, SyncFrameStyle

REPLAY_COUNT = 20


def _record(output_dir: Path) -> None:
    from playwright.sync_api import sync_playwright

    videos_dir = output_dir / "videos"
    videos_dir.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(videos_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        sb = Storyboard(output_dir, page, sync_frame_style=SyncFrameStyle(debug_overlay=True))

        for i in range(REPLAY_COUNT):
            _wikipedia_search_iteration(sb, page, i)
            print(f"  Round {i + 1}/{REPLAY_COUNT} done")

        context.close()
        browser.close()


def _wikipedia_search_iteration(sb: Storyboard, page, iteration: int) -> None:
    def navigate(s: Storyboard) -> None:
        def _nav(_s: Storyboard) -> None:
            page.goto("https://en.wikipedia.org", wait_until="load")
            page.wait_for_selector("input[name='search']", state="visible")
        s.screen_action(_nav, description="Navigate to Wikipedia")

    sb.narrate(navigate, text=f"Round {iteration + 1}. Navigating to Wikipedia.")

    def search(s: Storyboard) -> None:
        def _do(_s: Storyboard) -> None:
            box = page.locator("input[name='search']").first
            box.click()
            box.fill("")
            box.type("restaurant", delay=50)
            box.press("Enter")
            page.wait_for_selector("#firstHeading", state="visible")
            page.wait_for_selector("#mw-content-text h2", state="visible")
        s.screen_action(_do, description="Search for 'restaurant'")

    sb.narrate(search, text="Searching for restaurant.")

    headings = []
    for el in page.locator("#mw-content-text h2 .mw-headline, #mw-content-text h2").all()[:8]:
        try:
            text = el.inner_text(timeout=2000).replace("[edit]", "").strip()
            if text and text not in ("See also", "References", "External links", "Notes", "Further reading"):
                headings.append((text, el))
        except Exception:
            continue

    for heading_text, heading_el in headings[:3]:
        def highlight(s: Storyboard, _el=heading_el) -> None:
            def _hl(_s: Storyboard) -> None:
                if _el is not None:
                    s.highlight(_el)
            s.screen_action(_hl, description=f"Highlight: {heading_text}")

        sb.narrate(highlight, text=f"Section: {heading_text}.")


def _decode_qr_ms(frame_path: Path) -> int | None:
    img = Image.open(frame_path)
    w, h = img.size
    crop = img.crop((w - 120, h - 120, w, h))
    big = crop.resize((crop.width * 4, crop.height * 4), Image.NEAREST)
    results = decode_qr(big)
    return int(results[0].data.decode("utf-8")) if results else None


@pytest.mark.e2e
@pytest.mark.long
def test_no_timestamp_drift_after_long_session(tmp_path: Path) -> None:
    output_dir = tmp_path / "long-drift"

    print(f"\nRecording {REPLAY_COUNT} iterations...")
    _record(output_dir)

    print("Postprocessing...")
    process(output_dir, debug_overlay=True, font_size=48)

    mp4 = output_dir / "long-drift.mp4"
    assert mp4.exists()

    probe = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(mp4)],
        capture_output=True, text=True, check=True,
    )
    duration_s = float(json.loads(probe.stdout)["format"]["duration"])
    print(f"Video: {duration_s:.1f}s ({duration_s / 60:.1f} min)")

    frames_dir = tmp_path / "frames"
    frames_dir.mkdir()

    sample_times: list[float] = []
    t = 5.0
    while t < duration_s - 1:
        sample_times.extend([t, t + 0.37])
        t += 30.0

    tolerance_ms = 80
    max_diff = 0

    for t in sample_times:
        fp = frames_dir / f"f_{t:.3f}.png"
        subprocess.run(
            ["ffmpeg", "-y", "-ss", str(t), "-i", str(mp4), "-frames:v", "1", str(fp)],
            capture_output=True, check=True,
        )
        ms = _decode_qr_ms(fp)
        if ms is None:
            continue
        diff = ms - int(t * 1000)
        max_diff = max(max_diff, abs(diff))
        print(f"  t={t:8.3f}s  qr={ms:8d}ms  diff={diff:+4d}ms")
        assert abs(diff) < tolerance_ms, f"Drift at {t:.3f}s: {diff:+d}ms exceeds {tolerance_ms}ms"

    print(f"\nMax drift: {max_diff}ms")
