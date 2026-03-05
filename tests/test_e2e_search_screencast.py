"""
End-to-end test: Wikipedia search screencast with narration.

Records a Playwright session that navigates to Wikipedia, searches for
"restaurant", reads the first few section headings, and produces a
narrated screencast via the full screencast-narrator pipeline.

Pattern: narrate FIRST, then act. The viewer hears what will happen
before it happens. All actions and navigations happen between sync
frame START and END so the merge pipeline can sync audio to video.

Requires Python <=3.13 (kokoro/spacy not yet compatible with 3.14).

Requirements:
    uv venv --python 3.13 .venv
    pip install -e ".[e2e]" && playwright install chromium

Run:
    pytest tests/test_e2e_search_screencast.py -v
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from screencast_narrator.merge import process
from screencast_narrator.sync_frames import inject_sync_frame
from screencast_narrator.timeline import ScreencastTimeline

_HIGHLIGHT_CSS = (
    "outline: 3px solid red; "
    "outline-offset: 2px; "
    "border-radius: 4px; "
    "box-shadow: 0 0 8px rgba(255, 0, 0, 0.5);"
)


def _add_highlight(locator) -> None:
    locator.evaluate(
        "(el, css) => el.setAttribute('style', "
        "(el.getAttribute('style') || '') + ';' + css)",
        _HIGHLIGHT_CSS,
    )


def _remove_highlight(locator) -> None:
    locator.evaluate(
        "el => { el.style.outline = ''; el.style.outlineOffset = ''; "
        "el.style.boxShadow = ''; }"
    )


def _now_ms() -> int:
    return int(time.time() * 1000)


@pytest.mark.e2e
def test_search_screencast(tmp_path: Path) -> None:
    """Full pipeline: Playwright recording -> timeline -> TTS -> merge -> MP4."""
    from playwright.sync_api import sync_playwright

    output_dir = tmp_path / "search-screencast"
    output_dir.mkdir()
    videos_dir = output_dir / "videos"
    videos_dir.mkdir()

    timeline = ScreencastTimeline(output_dir, video_enabled=True)

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(videos_dir),
            record_video_size={"width": 1280, "height": 720},
        )
        page = context.new_page()
        timeline.video_recording_started()

        # --- Step 1: Narrate intro, then navigate ---
        timeline.begin_narration_bracket()
        narration_id = timeline.active_narration_id()
        inject_sync_frame(page, narration_id, "START")
        timeline.add_action("Introduction and navigate to Wikipedia")
        page.goto("https://en.wikipedia.org", wait_until="load")
        page.wait_for_selector("input[name='search']", state="visible")
        timeline.add_narration(
            "In this screencast, we will search Wikipedia for information "
            "about restaurants. Let's start by navigating to the homepage."
        )
        inject_sync_frame(page, narration_id, "END")
        timeline.end_narration_bracket()

        # --- Step 2: Narrate search, then type and submit ---
        search_box = page.locator("input[name='search']").first
        hl_start = _now_ms()
        _add_highlight(search_box)

        timeline.begin_narration_bracket()
        narration_id = timeline.active_narration_id()
        timeline.add_highlight(hl_start)
        inject_sync_frame(page, narration_id, "START")
        timeline.add_action("Type 'restaurant' and search")
        search_box.click()
        search_box.type("restaurant", delay=50)
        search_box.press("Enter")
        _remove_highlight(search_box)
        page.wait_for_selector("#firstHeading", state="visible")
        page.wait_for_selector("#mw-content-text h2", state="visible")
        timeline.add_narration(
            "We type 'restaurant' into the search box and press Enter "
            "to navigate to the article."
        )
        inject_sync_frame(page, narration_id, "END")
        timeline.end_narration_bracket()

        # --- Step 3: Read section headings ---
        heading_elements = page.locator(
            "#mw-content-text h2 .mw-headline, #mw-content-text h2"
        ).all()
        headings = []
        for el in heading_elements[:8]:
            try:
                text = el.inner_text(timeout=2000)
                text = text.replace("[edit]", "").strip()
                if text and text not in (
                    "See also", "References", "External links",
                    "Notes", "Further reading",
                ):
                    headings.append((text, el))
            except Exception:
                continue

        if not headings:
            headings = [("No section headings found on the page", None)]

        for i, (heading_text, heading_el) in enumerate(headings[:3]):
            timeline.begin_narration_bracket()
            narration_id = timeline.active_narration_id()
            inject_sync_frame(page, narration_id, "START")

            # Scroll + highlight inside sync bracket
            if heading_el is not None:
                heading_el.scroll_into_view_if_needed()
                heading_el.wait_for(state="visible")
                hl_start = _now_ms()
                _add_highlight(heading_el)
                timeline.add_highlight(hl_start)

            timeline.add_action(f"Read section heading: {heading_text}")
            timeline.add_narration(
                f"Section {i + 1} of the article is titled: {heading_text}."
            )
            inject_sync_frame(page, narration_id, "END")
            timeline.end_narration_bracket()

            if heading_el is not None:
                _remove_highlight(heading_el)

        # --- Done recording ---
        timeline.video_recording_ended()
        context.close()
        browser.close()

    # --- Run the full merge pipeline ---
    process(output_dir)

    # --- Assertions ---
    timeline_json = output_dir / "timeline.json"
    assert timeline_json.exists(), "timeline.json was not created"

    output_mp4 = output_dir / "search-screencast.mp4"
    assert output_mp4.exists(), f"Output MP4 not found at {output_mp4}"
    assert output_mp4.stat().st_size > 10_000, "Output MP4 is suspiciously small"

    html_files = list(output_dir.glob("timeline-*.html"))
    assert len(html_files) > 0, "No timeline HTML files were generated"
