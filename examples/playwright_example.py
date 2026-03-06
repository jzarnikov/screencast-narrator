"""Example: How to integrate screencast-narrator with Playwright for E2E tests.

This shows the typical workflow:
1. Start a Playwright video recording
2. Use ScreencastTimeline to track events
3. Inject QR sync frames during narration brackets
4. After recording, run the merge pipeline to produce the final narrated video

Requirements:
    pip install playwright screencast-narrator[tts]
    playwright install chromium
    brew install ffmpeg zbar
"""

from pathlib import Path

from playwright.sync_api import sync_playwright

from screencast_narrator.merge import process
from screencast_narrator.sync_frames import inject_sync_frame
from screencast_narrator.timeline import ScreencastTimeline


def main() -> None:
    output_dir = Path("screencast-output")
    output_dir.mkdir(exist_ok=True)
    video_dir = output_dir / "videos"
    video_dir.mkdir(exist_ok=True)

    timeline = ScreencastTimeline(output_dir, video_enabled=True)

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            record_video_dir=str(video_dir),
            record_video_size={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        timeline.video_recording_started()

        # --- Narration bracket with sync frames ---
        timeline.begin_narration_bracket()
        inject_sync_frame(page, timeline.active_narration_id(), "START")

        page.goto("https://example.com", wait_until="load")
        timeline.add_action("Navigate to example.com")
        page.wait_for_selector("h1", state="visible")

        inject_sync_frame(page, timeline.active_narration_id(), "END")
        start_ms = timeline.start_time
        import time

        now = int(time.time() * 1000)
        timeline.add_narration(
            "We navigate to the example website to demonstrate the screencast narrator.",
            start_ms=now - start_ms - 2000,
            end_ms=now - start_ms,
        )
        timeline.end_narration_bracket()

        # --- Simple narration (no bracket) ---
        timeline.add_narration("This is a standalone observation about the page.")

        timeline.video_recording_ended()
        context.close()
        browser.close()

    # Run the merge pipeline to produce the final video
    process(output_dir)
    print(f"Done! Output at: {output_dir / output_dir.name}.mp4")


if __name__ == "__main__":
    main()
