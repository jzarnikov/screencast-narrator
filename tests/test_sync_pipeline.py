"""Port of SyncPipelineAudioPositionTest.java — sync pipeline audio delay computation."""

from dataclasses import dataclass

from screencast_narrator.freeze_frames import FreezeFrameCalculator, NarrationSegment

FRAME_DURATION_S = 0.04  # 25fps


@dataclass(frozen=True)
class SyncFrameSpan:
    narration_id: int
    marker: str
    first_frame: int
    last_frame: int


def compute_sync_pipeline_audio_delays(
    narrations: list[NarrationSegment],
    sync_frame_spans: list[SyncFrameSpan],
) -> list[int]:
    stripped_narrations = to_stripped_video_narrations(narrations, sync_frame_spans)
    result = FreezeFrameCalculator(stripped_narrations, []).calculate()
    return result.adjusted_timestamps


def to_stripped_video_narrations(
    narrations: list[NarrationSegment],
    sync_frame_spans: list[SyncFrameSpan],
) -> list[NarrationSegment]:
    sync_positions = build_sync_position_map(sync_frame_spans)
    adjusted: list[NarrationSegment] = []
    for i, n in enumerate(narrations):
        key = f"{i}|START"
        if key in sync_positions:
            sync_start_ms = int(sync_positions[key] * 1000)
            wall_clock_bracket = n.end_ms - n.start_ms
            sync_time_ms = sync_frame_time_in_bracket_ms(sync_frame_spans, i)
            stripped_bracket = max(0, wall_clock_bracket - sync_time_ms)
            adjusted.append(NarrationSegment(
                sync_start_ms, sync_start_ms + stripped_bracket, n.text, n.audio_duration_ms
            ))
        else:
            adjusted.append(n)
    return adjusted


def build_sync_position_map(spans: list[SyncFrameSpan]) -> dict[str, float]:
    sorted_spans = sorted(spans, key=lambda s: s.first_frame)
    positions: dict[str, float] = {}
    stripped_frames_before = 0

    for span in sorted_spans:
        original_position_s = span.first_frame * FRAME_DURATION_S
        adjusted_position_s = original_position_s - (stripped_frames_before * FRAME_DURATION_S)
        key = f"{span.narration_id}|{span.marker}"
        positions[key] = adjusted_position_s
        stripped_frames_before += span.last_frame - span.first_frame + 1 + 2

    return positions


def sync_frame_time_in_bracket_ms(sync_frame_spans: list[SyncFrameSpan], narration_id: int) -> int:
    total = 0
    for s in sync_frame_spans:
        if s.narration_id == narration_id:
            total += (s.last_frame - s.first_frame + 1 + 2) * 40
    return total


def assert_no_audio_overlap(audio_delays: list[int], narrations: list[NarrationSegment]) -> None:
    for i in range(len(audio_delays) - 1):
        audio_end = audio_delays[i] + narrations[i].audio_duration_ms
        assert audio_end <= audio_delays[i + 1], (
            f"narration {i} audio (ends {audio_end}ms) must not overlap "
            f"narration {i + 1} (starts {audio_delays[i + 1]}ms)"
        )


def test_bracket_duration_should_exclude_sync_frame_display_time():
    narrations = [
        NarrationSegment(1000, 3000, "first narration", 3000),
        NarrationSegment(3500, 5500, "second narration", 3000),
    ]
    sync_frame_spans = [
        SyncFrameSpan(0, "START", 25, 28),
        SyncFrameSpan(0, "HL_START", 35, 38),
        SyncFrameSpan(0, "HL_END", 45, 48),
        SyncFrameSpan(1, "START", 87, 90),
    ]
    audio_delays = compute_sync_pipeline_audio_delays(narrations, sync_frame_spans)
    assert_no_audio_overlap(audio_delays, narrations)


def test_many_narrations_with_sync_frames_should_not_overlap():
    narrations: list[NarrationSegment] = []
    sync_frame_spans: list[SyncFrameSpan] = []
    frame = 0

    for i in range(5):
        bracket_start = i * 5000
        bracket_end = bracket_start + 3000
        narrations.append(NarrationSegment(bracket_start, bracket_end, f"narration {i}", 4000))
        sync_frame_spans.append(SyncFrameSpan(i, "START", frame, frame + 3))
        frame += 10
        sync_frame_spans.append(SyncFrameSpan(i, "HL_START", frame, frame + 3))
        frame += 10
        sync_frame_spans.append(SyncFrameSpan(i, "HL_END", frame, frame + 3))
        frame += 50

    audio_delays = compute_sync_pipeline_audio_delays(narrations, sync_frame_spans)
    assert_no_audio_overlap(audio_delays, narrations)


def test_single_narration_with_sync_frames_should_get_correct_freeze_duration():
    narrations = [NarrationSegment(0, 2000, "only narration", 5000)]
    sync_frame_spans = [
        SyncFrameSpan(0, "START", 0, 3),
        SyncFrameSpan(0, "HL_START", 10, 13),
        SyncFrameSpan(0, "HL_END", 30, 33),
    ]
    adjusted = to_stripped_video_narrations(narrations, sync_frame_spans)
    stripped_bracket = adjusted[0].end_ms - adjusted[0].start_ms
    assert stripped_bracket < 2000

    result = FreezeFrameCalculator(adjusted, []).calculate()
    freeze_duration = result.freeze_frames[0].duration_ms
    assert freeze_duration == 5000 - stripped_bracket
