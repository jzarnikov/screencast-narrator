# Screencast Narrator - Session Memory

## Sync Frame Ordering (per narration step)

```python
timeline.begin_narration_bracket()
narration_id = timeline.active_narration_id()  # NOT begin_narration_bracket() return value — it returns None
inject_sync_frame(page, narration_id, "START")
# ... actions, navigations, highlights ...
timeline.add_action(description)
timeline.add_narration(text)
inject_sync_frame(page, narration_id, "END")
timeline.end_narration_bracket()
```

- All actions and navigations MUST happen between sync START and END
- `add_narration` goes before sync END
- `end_narration_bracket` goes after sync END
- Highlights need actual video frames between sync START/END to be captured by freeze frame system
- Use `page.wait_for_selector()` not `page.wait_for_timeout()` for page loads
- No `time.sleep()` — sync frames handle all audio-video timing

## Bugs Fixed

- **timeline_html.py**: `write_text()` needs `encoding="utf-8"` on Windows (cp1252 can't encode `→`)
- **merge.py**: `_build_extended_video_direct` crashes when freeze frame position exceeds video duration — fixed by clamping `extract_s` to `max(video_duration_s - 0.04, 0.0)`

## Environment

- **Python 3.13 required** — kokoro/spacy incompatible with 3.14 (pydantic v1 issue)
- `uv venv --python 3.13 .venv`
- Need `pip` in venv for spacy model: `uv pip install pip`
- Need spacy model: `python -m spacy download en_core_web_sm`
- `[e2e]` optional deps added to `pyproject.toml` (playwright + tts)

## E2E Test Notes

- Google and DuckDuckGo block headless Chromium with CAPTCHAs — use Wikipedia
- Highlights: use `locator.evaluate()` to add/remove CSS outlines
- `_add_highlight` before sync START so it's rendered when green overlay clears
- For heading sections: scroll + highlight between sync START/END creates video frames for freeze frame to grab
