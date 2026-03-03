"""Integration test for the merge pipeline: tests timeline parsing and narration extraction."""

import json

from screencast_narrator.merge import (
    NarrationText,
    _extract_highlights,
    _extract_narrations,
    _get_events,
    _compute_video_time_scale,
    _video_recording_offset,
    _segment_name,
)
from screencast_narrator.freeze_frames import HighlightEntry


def _make_timeline(narrations, highlights=None, actions=None,
                   video_start=None, video_end=None):
    events = []
    for n in narrations:
        events.append({
            "type": "narration",
            "timestampMs": n[0],
            "endTimestampMs": n[1],
            "text": n[2],
            "narrationId": n[3] if len(n) > 3 else 0,
        })
    for h in (highlights or []):
        events.append({
            "type": "highlight",
            "timestampMs": h[0],
            "endTimestampMs": h[1],
        })
    for a in (actions or []):
        events.append({
            "type": "action",
            "timestampMs": a[0],
            "description": a[1],
        })
    root = {"events": events}
    if video_start is not None:
        root["videoRecordingStartedAtMs"] = video_start
    if video_end is not None:
        root["videoRecordingEndedAtMs"] = video_end
    return root


def test_extract_narrations_from_timeline():
    root = _make_timeline([
        (1000, 3000, "first narration"),
        (5000, 5000, "instant narration"),
    ])
    result = _extract_narrations(root)
    assert len(result) == 2
    assert result[0] == NarrationText(1000, 3000, "first narration")
    assert result[1] == NarrationText(5000, 5000, "instant narration")


def test_extract_highlights_from_timeline():
    root = _make_timeline([], highlights=[(1000, 2400), (5000, 6400)])
    result = _extract_highlights(root)
    assert len(result) == 2
    assert result[0] == HighlightEntry(1000, 1400)
    assert result[1] == HighlightEntry(5000, 1400)


def test_get_events_from_root_with_events_key():
    root = {"events": [{"type": "narration", "timestampMs": 0, "text": "test"}]}
    events = _get_events(root)
    assert len(events) == 1


def test_video_time_scale_with_timestamps():
    root = _make_timeline([], video_start=1000, video_end=11000)
    scale = _compute_video_time_scale(root, 10500)
    assert abs(scale - 1.05) < 0.01


def test_video_time_scale_without_timestamps():
    root = _make_timeline([])
    scale = _compute_video_time_scale(root, 10000)
    assert scale == 1.0


def test_video_recording_offset():
    root = _make_timeline([], video_start=5000)
    assert _video_recording_offset(root) == 5000


def test_video_recording_offset_default():
    root = _make_timeline([])
    assert _video_recording_offset(root) == 0


def test_segment_name():
    assert _segment_name(0) == "segment_000.wav"
    assert _segment_name(42) == "segment_042.wav"
    assert _segment_name(999) == "segment_999.wav"


def test_round_trip_timeline_json(tmp_path):
    root = _make_timeline(
        [(1000, 3000, "hello world"), (5000, 7000, "second part")],
        highlights=[(2000, 3400)],
        actions=[(1500, "Click button")],
        video_start=500,
        video_end=8000,
    )
    timeline_file = tmp_path / "timeline.json"
    timeline_file.write_text(json.dumps(root))

    loaded = json.loads(timeline_file.read_text())
    narrations = _extract_narrations(loaded)
    highlights = _extract_highlights(loaded)

    assert len(narrations) == 2
    assert narrations[0].text == "hello world"
    assert len(highlights) == 1
    assert highlights[0].timestamp_ms == 2000
    assert highlights[0].duration_ms == 1400
