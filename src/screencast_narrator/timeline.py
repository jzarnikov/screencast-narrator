"""ScreencastTimeline: event recording and JSON output for screencast narration."""

from __future__ import annotations

import json
import time
from collections import deque
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class NarrationEvent:
    timestamp_ms: int
    end_timestamp_ms: int
    text: str
    narration_id: int
    type: str = "narration"


@dataclass(frozen=True)
class HighlightEvent:
    timestamp_ms: int
    end_timestamp_ms: int
    narration_id: int
    type: str = "highlight"


@dataclass(frozen=True)
class ActionEvent:
    timestamp_ms: int
    description: str
    narration_id: int
    type: str = "action"


@dataclass(frozen=True)
class TitleCardEvent:
    timestamp_ms: int
    duration_ms: int
    type: str = "title_card"


@dataclass(frozen=True)
class SyncFrameEvent:
    timestamp_ms: int
    narration_id: int
    marker: str
    type: str = "sync_frame"


TimelineEvent = NarrationEvent | HighlightEvent | ActionEvent | TitleCardEvent | SyncFrameEvent


class ScreencastTimeline:
    def __init__(self, output_dir: Path, video_enabled: bool = False) -> None:
        self._start_time = _now_ms()
        self._events: list[TimelineEvent] = []
        self._output_dir = output_dir
        self._video_enabled = video_enabled
        self._narration_id_counter = 0
        self._highlight_id_counter = 0
        self._action_id_counter = 0
        self._narration_id_stack: deque[int] = deque()
        self._video_recording_started_at_ms: int = -1
        self._video_recording_ended_at_ms: int = -1
        self._bracket_first_event_ms_stack: deque[int] = deque()
        output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def start_time(self) -> int:
        return self._start_time

    @property
    def video_enabled(self) -> bool:
        return self._video_enabled

    def video_recording_started(self) -> None:
        self._video_recording_started_at_ms = _now_ms() - self._start_time

    def video_recording_ended(self) -> None:
        self._video_recording_ended_at_ms = _now_ms() - self._start_time
        self._flush()

    def begin_narration_bracket(self) -> None:
        nid = self._narration_id_counter
        self._narration_id_counter += 1
        self._narration_id_stack.appendleft(nid)
        self._bracket_first_event_ms_stack.appendleft(-1)

    def end_narration_bracket(self) -> None:
        if self._narration_id_stack:
            self._narration_id_stack.popleft()
        if self._bracket_first_event_ms_stack:
            self._bracket_first_event_ms_stack.popleft()

    def active_narration_id(self) -> int:
        return self._narration_id_stack[0] if self._narration_id_stack else -1

    def next_highlight_id(self) -> int:
        hid = self._highlight_id_counter
        self._highlight_id_counter += 1
        return hid

    def next_action_id(self) -> int:
        aid = self._action_id_counter
        self._action_id_counter += 1
        return aid

    def add_narration(self, text: str, start_ms: int | None = None, end_ms: int | None = None) -> None:
        if start_ms is None or end_ms is None:
            ts = _now_ms() - self._start_time
            nid = self._narration_id_counter
            self._narration_id_counter += 1
            self._events.append(NarrationEvent(ts, ts, text, nid))
        else:
            first_event = self._bracket_first_event_ms_stack[0] if self._bracket_first_event_ms_stack else -1
            effective_start = first_event if first_event >= 0 else start_ms
            self._events.append(NarrationEvent(effective_start, end_ms, text, self.active_narration_id()))
        self._flush()

    def add_highlight(self, absolute_start_time_ms: int) -> None:
        start_ms = absolute_start_time_ms - self._start_time
        end_ms = _now_ms() - self._start_time
        self._track_bracket_first_event(start_ms)
        self._events.append(HighlightEvent(start_ms, end_ms, self.active_narration_id()))
        self._flush()

    def add_action(self, description: str) -> None:
        ts = _now_ms() - self._start_time
        self._track_bracket_first_event(ts)
        self._events.append(ActionEvent(ts, description, self.active_narration_id()))
        self._flush()

    def _track_bracket_first_event(self, relative_ms: int) -> None:
        if self._bracket_first_event_ms_stack and self._bracket_first_event_ms_stack[0] < 0:
            self._bracket_first_event_ms_stack.popleft()
            self._bracket_first_event_ms_stack.appendleft(relative_ms)

    def add_sync_frame(self, narration_id: int, marker: str) -> None:
        ts = _now_ms() - self._start_time
        self._events.append(SyncFrameEvent(ts, narration_id, marker))
        self._flush()

    def add_title_card(self, duration_ms: int) -> None:
        ts = _now_ms() - self._start_time
        self._events.append(TitleCardEvent(ts, duration_ms))
        self._flush()

    @property
    def events(self) -> list[TimelineEvent]:
        return list(self._events)

    def _flush(self) -> None:
        timeline_file = self._output_dir / "timeline.json"
        root: dict = {}
        if self._video_recording_started_at_ms >= 0:
            root["videoRecordingStartedAtMs"] = self._video_recording_started_at_ms
        if self._video_recording_ended_at_ms >= 0:
            root["videoRecordingEndedAtMs"] = self._video_recording_ended_at_ms
        root["events"] = [_event_to_dict(e) for e in self._events]
        timeline_file.write_text(json.dumps(root, indent=2), encoding="utf-8")


def _event_to_dict(event: TimelineEvent) -> dict:
    d = asdict(event)
    result = {}
    result["type"] = d.pop("type")
    result["timestampMs"] = d.pop("timestamp_ms")
    if "end_timestamp_ms" in d:
        result["endTimestampMs"] = d.pop("end_timestamp_ms")
    if "duration_ms" in d:
        result["durationMs"] = d.pop("duration_ms")
    if "narration_id" in d:
        result["narrationId"] = d.pop("narration_id")
    if "text" in d:
        result["text"] = d.pop("text")
    if "description" in d:
        result["description"] = d.pop("description")
    if "marker" in d:
        result["marker"] = d.pop("marker")
    return result


def _now_ms() -> int:
    return int(time.time() * 1000)
