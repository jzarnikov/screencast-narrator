"""Port of ScreencastTimelineTest.java — all test cases."""

import json
import time

from screencast_narrator.timeline import (
    ActionEvent,
    HighlightEvent,
    NarrationEvent,
    ScreencastTimeline,
)


def test_highlight_should_record_start_and_end_timestamps(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    time.sleep(0.05)
    before_highlight = int(time.time() * 1000)
    time.sleep(0.05)
    timeline.add_highlight(before_highlight)

    events = timeline.events
    assert len(events) == 1
    highlight = events[0]
    assert isinstance(highlight, HighlightEvent)
    assert highlight.timestamp_ms < highlight.end_timestamp_ms
    assert highlight.end_timestamp_ms - highlight.timestamp_ms >= 40


def test_highlight_start_time_should_not_be_negative_or_massive(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    time.sleep(0.1)
    highlight_start = int(time.time() * 1000)
    time.sleep(0.1)
    timeline.add_highlight(highlight_start)

    highlight = timeline.events[0]
    assert isinstance(highlight, HighlightEvent)
    assert 0 <= highlight.timestamp_ms < 10_000


def test_timeline_json_should_contain_highlight_start_and_end(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    time.sleep(0.05)
    highlight_start = int(time.time() * 1000)
    time.sleep(0.05)
    timeline.add_highlight(highlight_start)

    timeline_file = tmp_path / "timeline.json"
    assert timeline_file.exists()
    content = timeline_file.read_text()
    assert '"timestampMs"' in content
    assert '"endTimestampMs"' in content
    assert '"durationMs"' not in content


def test_ranged_narration_should_record_start_and_end_timestamps(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    timeline.begin_narration_bracket()
    timeline.add_narration("test narration", 1000, 5000)
    timeline.end_narration_bracket()

    events = timeline.events
    assert len(events) == 1
    narration = events[0]
    assert isinstance(narration, NarrationEvent)
    assert narration.timestamp_ms == 1000
    assert narration.end_timestamp_ms == 5000
    assert narration.text == "test narration"


def test_zero_duration_narration_should_have_equal_timestamps(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    time.sleep(0.05)
    timeline.add_narration("standalone observation")

    events = timeline.events
    assert len(events) == 1
    narration = events[0]
    assert isinstance(narration, NarrationEvent)
    assert narration.timestamp_ms == narration.end_timestamp_ms
    assert narration.timestamp_ms > 0


def test_narration_json_should_contain_end_timestamp_ms(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    timeline.begin_narration_bracket()
    timeline.add_narration("test", 100, 500)
    timeline.end_narration_bracket()

    content = (tmp_path / "timeline.json").read_text()
    assert '"endTimestampMs"' in content
    assert '"timestampMs"' in content
    assert '"text"' in content
    assert '"narrationId"' in content


def test_get_start_time_should_return_timeline_start_time(tmp_path):
    before = int(time.time() * 1000)
    timeline = ScreencastTimeline(tmp_path)
    after = int(time.time() * 1000)
    assert before <= timeline.start_time <= after


def test_actions_should_be_associated_with_active_narration_bracket(tmp_path):
    timeline = ScreencastTimeline(tmp_path)

    timeline.add_action("action outside bracket")

    timeline.begin_narration_bracket()
    timeline.add_action("action inside bracket")
    timeline.add_narration("bracketed narration", 100, 500)
    timeline.end_narration_bracket()

    timeline.add_action("action after bracket")

    events = timeline.events
    assert len(events) == 4

    outside_action = events[0]
    assert isinstance(outside_action, ActionEvent)
    assert outside_action.narration_id == -1
    assert outside_action.description == "action outside bracket"

    inside_action = events[1]
    assert isinstance(inside_action, ActionEvent)
    assert inside_action.narration_id == 0

    narration = events[2]
    assert isinstance(narration, NarrationEvent)
    assert narration.narration_id == 0

    after_action = events[3]
    assert isinstance(after_action, ActionEvent)
    assert after_action.narration_id == -1


def test_highlights_should_be_associated_with_active_narration_bracket(tmp_path):
    timeline = ScreencastTimeline(tmp_path)

    time.sleep(0.01)
    timeline.add_highlight(int(time.time() * 1000) - 5)

    timeline.begin_narration_bracket()
    time.sleep(0.01)
    timeline.add_highlight(int(time.time() * 1000) - 5)
    timeline.add_narration("narration", 100, 500)
    timeline.end_narration_bracket()

    events = timeline.events
    assert len(events) == 3

    outside_highlight = events[0]
    assert isinstance(outside_highlight, HighlightEvent)
    assert outside_highlight.narration_id == -1

    inside_highlight = events[1]
    assert isinstance(inside_highlight, HighlightEvent)
    assert inside_highlight.narration_id == 0


def test_standalone_narrations_should_get_unique_ids(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    timeline.add_narration("first")
    timeline.add_narration("second")
    timeline.begin_narration_bracket()
    timeline.add_narration("bracketed", 100, 200)
    timeline.end_narration_bracket()
    timeline.add_narration("third")

    events = timeline.events
    first = events[0]
    second = events[1]
    bracketed = events[2]
    third = events[3]
    assert isinstance(first, NarrationEvent) and first.narration_id == 0
    assert isinstance(second, NarrationEvent) and second.narration_id == 1
    assert isinstance(bracketed, NarrationEvent) and bracketed.narration_id == 2
    assert isinstance(third, NarrationEvent) and third.narration_id == 3


def test_nested_brackets_should_restore_outer_narration_id(tmp_path):
    timeline = ScreencastTimeline(tmp_path)

    timeline.begin_narration_bracket()  # outer, id=0
    timeline.add_action("outer action 1")

    timeline.begin_narration_bracket()  # inner, id=1
    timeline.add_action("inner action")
    timeline.add_narration("inner narration", 100, 200)
    timeline.end_narration_bracket()

    timeline.add_action("outer action 2")
    timeline.add_narration("outer narration", 0, 500)
    timeline.end_narration_bracket()

    timeline.add_action("action outside all brackets")

    events = timeline.events
    outer_action1 = events[0]
    assert isinstance(outer_action1, ActionEvent) and outer_action1.narration_id == 0

    inner_action = events[1]
    assert isinstance(inner_action, ActionEvent) and inner_action.narration_id == 1

    inner_narration = events[2]
    assert isinstance(inner_narration, NarrationEvent) and inner_narration.narration_id == 1

    outer_action2 = events[3]
    assert isinstance(outer_action2, ActionEvent) and outer_action2.narration_id == 0

    outer_narration = events[4]
    assert isinstance(outer_narration, NarrationEvent) and outer_narration.narration_id == 0

    outside_action = events[5]
    assert isinstance(outside_action, ActionEvent) and outside_action.narration_id == -1


def test_bracket_narration_start_should_be_first_event_timestamp(tmp_path):
    timeline = ScreencastTimeline(tmp_path)

    timeline.begin_narration_bracket()
    time.sleep(0.05)
    timeline.add_action("first action in bracket")
    timeline.add_action("second action")
    timeline.add_narration("bracketed narration", 0, 9999)
    timeline.end_narration_bracket()

    events = timeline.events
    first_action = events[0]
    narration = events[2]
    assert isinstance(first_action, ActionEvent)
    assert isinstance(narration, NarrationEvent)
    assert narration.timestamp_ms == first_action.timestamp_ms
    assert narration.end_timestamp_ms == 9999


def test_bracket_with_no_events_should_fall_back_to_passed_start_ms(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    timeline.begin_narration_bracket()
    timeline.add_narration("narration with no actions", 1000, 5000)
    timeline.end_narration_bracket()

    narration = timeline.events[0]
    assert isinstance(narration, NarrationEvent)
    assert narration.timestamp_ms == 1000


def test_nested_brackets_should_track_first_event_independently(tmp_path):
    timeline = ScreencastTimeline(tmp_path)

    timeline.begin_narration_bracket()
    time.sleep(0.01)
    timeline.add_action("outer first action")
    outer_first = timeline.events[0]

    timeline.begin_narration_bracket()
    time.sleep(0.01)
    timeline.add_action("inner first action")
    timeline.add_narration("inner narration", 0, 200)
    timeline.end_narration_bracket()

    timeline.add_narration("outer narration", 0, 500)
    timeline.end_narration_bracket()

    events = timeline.events
    inner_narr = next(e for e in events if isinstance(e, NarrationEvent) and e.text == "inner narration")
    outer_narr = next(e for e in events if isinstance(e, NarrationEvent) and e.text == "outer narration")
    inner_first = next(e for e in events if isinstance(e, ActionEvent) and e.description == "inner first action")

    assert inner_narr.timestamp_ms == inner_first.timestamp_ms
    assert isinstance(outer_first, ActionEvent)
    assert outer_narr.timestamp_ms == outer_first.timestamp_ms


def test_action_json_should_contain_all_fields(tmp_path):
    timeline = ScreencastTimeline(tmp_path)
    timeline.begin_narration_bracket()
    timeline.add_action("Click state-forward")
    timeline.add_narration("test", 100, 500)
    timeline.end_narration_bracket()

    content = (tmp_path / "timeline.json").read_text()
    data = json.loads(content)
    action_event = next(e for e in data["events"] if e["type"] == "action")
    assert action_event["description"] == "Click state-forward"
    assert action_event["narrationId"] == 0
    assert "timestampMs" in action_event
