"""Freeze frame calculation: determines where to insert freeze frames and cut dead air gaps."""

from __future__ import annotations

from dataclasses import dataclass

_MIN_SAFE_DISTANCE_FROM_END_MS = 500
_MIN_GAP_TO_CUT_MS = 2000
_GAP_PRESERVE_MS = 300


@dataclass(frozen=True)
class NarrationSegment:
    start_ms: int
    end_ms: int
    text: str
    audio_duration_ms: int


@dataclass(frozen=True)
class HighlightEntry:
    timestamp_ms: int
    duration_ms: int


@dataclass(frozen=True)
class FreezeFrame:
    time_ms: int
    duration_ms: int


@dataclass(frozen=True)
class GapCut:
    start_ms: int
    end_ms: int


@dataclass(frozen=True)
class Result:
    freeze_frames: list[FreezeFrame]
    adjusted_timestamps: list[int]


class FreezeFrameCalculator:
    def __init__(
        self,
        narrations: list[NarrationSegment],
        highlights: list[HighlightEntry],
        video_recording_end_ms: int = 2**63 - 1,
    ) -> None:
        self._narrations = narrations
        self._highlights = highlights
        self._video_recording_end_ms = video_recording_end_ms

    def calculate(self) -> Result:
        freeze_frames = self._calculate_freeze_frames()
        adjusted_timestamps = self._calculate_adjusted_timestamps(freeze_frames)
        return Result(freeze_frames, adjusted_timestamps)

    def _calculate_freeze_frames(self) -> list[FreezeFrame]:
        freeze_frames: list[FreezeFrame] = []
        for n in self._narrations:
            bracket_duration = n.end_ms - n.start_ms
            if n.audio_duration_ms > bracket_duration:
                deficit = n.audio_duration_ms - bracket_duration
                insert_point = self._find_safe_insertion_point(n.end_ms)
                if insert_point > self._video_recording_end_ms - _MIN_SAFE_DISTANCE_FROM_END_MS:
                    insert_point = n.start_ms
                freeze_frames.append(FreezeFrame(insert_point, deficit))
        return freeze_frames

    def _find_safe_insertion_point(self, proposed_time: int) -> int:
        safe = proposed_time
        adjusted = True
        while adjusted:
            adjusted = False
            for h in self._highlights:
                hl_end = h.timestamp_ms + h.duration_ms
                if safe > h.timestamp_ms and safe < hl_end:
                    safe = hl_end
                    adjusted = True
                    break
        return safe

    def _calculate_adjusted_timestamps(self, freeze_frames: list[FreezeFrame]) -> list[int]:
        adjusted: list[int] = []
        cumulative_shift = 0
        for i, n in enumerate(self._narrations):
            natural = n.start_ms + cumulative_shift
            min_start = 0 if i == 0 else adjusted[i - 1] + self._narrations[i - 1].audio_duration_ms
            adjusted.append(max(natural, min_start))
            bracket_duration = n.end_ms - n.start_ms
            if n.audio_duration_ms > bracket_duration:
                cumulative_shift += n.audio_duration_ms - bracket_duration
        return adjusted


def validate_freeze_positions(freeze_frames: list[FreezeFrame], video_recording_end_ms: int) -> None:
    for ff in freeze_frames:
        if ff.time_ms > video_recording_end_ms - _MIN_SAFE_DISTANCE_FROM_END_MS:
            raise ValueError(
                f"Freeze frame at {ff.time_ms}ms is within {_MIN_SAFE_DISTANCE_FROM_END_MS}ms "
                f"of video recording end at {video_recording_end_ms}ms. "
                f"This will cause ffmpeg frame extraction to fail. "
                f"Ensure all narrations have associated screen actions "
                f"so freeze frames are not placed at the video boundary."
            )


def adjust_timestamp(orig_ms: int, freeze_frames: list[FreezeFrame]) -> int:
    shift = 0
    for ff in freeze_frames:
        if ff.time_ms < orig_ms:
            shift += ff.duration_ms
    return orig_ms + shift


def detect_dead_air_gaps(
    narrations: list[NarrationSegment],
    adjusted_timestamps: list[int],
    occupied_intervals: list[tuple[int, int]],
) -> list[GapCut]:
    occupied = sorted(occupied_intervals, key=lambda x: x[0])

    gaps: list[GapCut] = []
    for i in range(len(narrations) - 1):
        audio_end = adjusted_timestamps[i] + narrations[i].audio_duration_ms
        next_start = adjusted_timestamps[i + 1]
        gap_ms = next_start - audio_end
        if gap_ms > _MIN_GAP_TO_CUT_MS:
            cut_start = audio_end + _GAP_PRESERVE_MS
            cut_end = next_start - _GAP_PRESERVE_MS
            if cut_end > cut_start:
                for candidate in subtract_occupied(cut_start, cut_end, occupied):
                    if candidate[1] - candidate[0] > _MIN_GAP_TO_CUT_MS:
                        gaps.append(GapCut(candidate[0], candidate[1]))
    return gaps


def subtract_occupied(start: int, end: int, occupied: list[tuple[int, int]]) -> list[tuple[int, int]]:
    result: list[tuple[int, int]] = [(start, end)]
    for occ in occupied:
        new_result: list[tuple[int, int]] = []
        for seg in result:
            if occ[1] <= seg[0] or occ[0] >= seg[1]:
                new_result.append(seg)
            else:
                if occ[0] > seg[0]:
                    new_result.append((seg[0], occ[0]))
                if occ[1] < seg[1]:
                    new_result.append((occ[1], seg[1]))
        result = new_result
        if not result:
            break
    return result


def adjust_for_cuts(timestamp_ms: int, gap_cuts: list[GapCut]) -> int:
    shift = 0
    for gap in gap_cuts:
        if timestamp_ms > gap.end_ms:
            shift += gap.end_ms - gap.start_ms
        elif timestamp_ms > gap.start_ms:
            shift += timestamp_ms - gap.start_ms
    return timestamp_ms - shift
