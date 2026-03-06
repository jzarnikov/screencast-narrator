"""Port of FreezeFrameCalculatorTest.java — all test cases."""

import pytest

from screencast_narrator.freeze_frames import (
    FreezeFrameCalculator,
    GapCut,
    HighlightEntry,
    NarrationSegment,
    adjust_for_cuts,
    detect_dead_air_gaps,
    subtract_occupied,
    validate_freeze_positions,
)


def seg(start_ms: int, end_ms: int, audio_duration_ms: int) -> NarrationSegment:
    return NarrationSegment(start_ms, end_ms, "text", audio_duration_ms)


def assert_no_audio_overlap(result, narrations):
    for i in range(len(result.adjusted_timestamps) - 1):
        audio_end = result.adjusted_timestamps[i] + narrations[i].audio_duration_ms
        assert audio_end <= result.adjusted_timestamps[i + 1], (
            f"narration {i} audio (ends {audio_end}ms) overlaps "
            f"narration {i + 1} (starts {result.adjusted_timestamps[i + 1]}ms)"
        )


def test_freeze_frame_times_should_be_in_original_video_coordinates():
    result = FreezeFrameCalculator([seg(0, 5000, 7000), seg(5000, 8000, 4000), seg(8000, 8000, 0)], []).calculate()
    assert len(result.freeze_frames) == 2
    assert result.freeze_frames[0].time_ms == 5000
    assert result.freeze_frames[1].time_ms == 8000


def test_adjusted_timestamps_should_match_visual_position_in_extended_video():
    result = FreezeFrameCalculator([seg(0, 5000, 7000), seg(5000, 8000, 4000), seg(8000, 8000, 0)], []).calculate()
    assert len(result.freeze_frames) == 2
    assert result.adjusted_timestamps[0] == 0
    assert result.adjusted_timestamps[1] == 7000
    assert result.adjusted_timestamps[2] == 11000


def test_adjusted_timestamps_should_not_over_shift_when_freeze_is_after_narration():
    result = FreezeFrameCalculator([seg(0, 2000, 1500), seg(2000, 3000, 500), seg(3000, 3000, 8000)], []).calculate()
    assert result.adjusted_timestamps[0] == 0
    assert result.adjusted_timestamps[1] == 2000
    assert result.adjusted_timestamps[2] == 3000


def test_freeze_should_move_forward_past_highlight():
    result = FreezeFrameCalculator(
        [seg(0, 2000, 4000), seg(2000, 2000, 0)],
        [HighlightEntry(1800, 1400)],
    ).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 3200
    assert result.freeze_frames[0].duration_ms == 2000


def test_freeze_should_cascade_forward_past_multiple_highlights():
    result = FreezeFrameCalculator(
        [seg(0, 5000, 7000), seg(5000, 5000, 0)],
        [HighlightEntry(4000, 1400), HighlightEntry(4800, 1400)],
    ).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 6200


def test_freeze_at_exact_highlight_start_should_be_fine():
    result = FreezeFrameCalculator(
        [seg(0, 3000, 5000), seg(3000, 3000, 0)],
        [HighlightEntry(3000, 1400)],
    ).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 3000


def test_no_freeze_needed_when_audio_fits_in_action_duration():
    result = FreezeFrameCalculator([seg(0, 5000, 3000), seg(5000, 5000, 0)], []).calculate()
    assert len(result.freeze_frames) == 0


def test_narration_audio_should_never_overlap_after_freeze_insertion():
    narrations = [
        seg(0, 0, 4000),
        seg(2000, 2000, 3000),
        seg(3500, 3500, 2500),
        seg(5000, 5000, 4000),
        seg(8000, 8000, 2000),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert_no_audio_overlap(result, narrations)


def test_multiple_consecutive_freezes_compound_correctly():
    narrations = [
        seg(0, 1000, 3000),
        seg(1000, 2000, 3000),
        seg(2000, 3000, 3000),
        seg(3000, 3000, 0),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) == 3
    assert result.freeze_frames[0].time_ms == 1000
    assert result.freeze_frames[1].time_ms == 2000
    assert result.freeze_frames[2].time_ms == 3000
    assert all(f.duration_ms == 2000 for f in result.freeze_frames)
    assert_no_audio_overlap(result, narrations)


def test_adjusted_timestamps_should_stay_monotonically_increasing():
    narrations = [
        seg(1000, 1000, 5000),
        seg(2000, 2000, 3000),
        seg(2500, 2500, 4000),
        seg(6000, 6000, 3000),
        seg(6200, 6200, 0),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    for i in range(len(result.adjusted_timestamps) - 1):
        assert result.adjusted_timestamps[i] < result.adjusted_timestamps[i + 1]


def test_freeze_should_move_after_highlight_when_cannot_go_backward():
    result = FreezeFrameCalculator(
        [seg(5000, 5100, 3000), seg(5100, 5100, 0)],
        [HighlightEntry(4900, 1400)],
    ).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms >= 6300


def test_real_timeline_data_should_produce_no_overlaps():
    narrations = [
        seg(248, 248, 4500),
        seg(23343, 23343, 3500),
        seg(25575, 25575, 5000),
        seg(30591, 30591, 4500),
        seg(57108, 57108, 2000),
        seg(57521, 57521, 4500),
        seg(61088, 61088, 3500),
        seg(63215, 63215, 5000),
        seg(68775, 68775, 4500),
        seg(92244, 92244, 2000),
        seg(96063, 96063, 3500),
        seg(104658, 104658, 2500),
        seg(106575, 106575, 3000),
        seg(108308, 108308, 3500),
        seg(108309, 108309, 4000),
        seg(115373, 115373, 4500),
        seg(118605, 118605, 2000),
        seg(119050, 119050, 3000),
        seg(122598, 122598, 3000),
        seg(139088, 139088, 4500),
        seg(164587, 164587, 2000),
        seg(166710, 166710, 3500),
        seg(168457, 168457, 3000),
        seg(173685, 173685, 3500),
        seg(176332, 176332, 2500),
        seg(176333, 176333, 3000),
        seg(203655, 203655, 2500),
        seg(207212, 207212, 3000),
        seg(223053, 223053, 4500),
        seg(250651, 250651, 2000),
        seg(251112, 251112, 2500),
        seg(252868, 252868, 2500),
        seg(256411, 256411, 3000),
        seg(256420, 256420, 2000),
    ]
    highlights = [
        HighlightEntry(5126, 1400),
        HighlightEntry(6824, 1400),
        HighlightEntry(14765, 1400),
        HighlightEntry(16502, 1400),
        HighlightEntry(19448, 1400),
        HighlightEntry(21375, 1400),
        HighlightEntry(23266, 1400),
        HighlightEntry(25460, 1400),
        HighlightEntry(27276, 1400),
        HighlightEntry(28942, 1400),
        HighlightEntry(30590, 1400),
        HighlightEntry(55458, 1400),
        HighlightEntry(57107, 1400),
        HighlightEntry(59057, 1400),
        HighlightEntry(60743, 1400),
        HighlightEntry(63092, 1400),
        HighlightEntry(65456, 1400),
        HighlightEntry(67123, 1400),
        HighlightEntry(68774, 1400),
        HighlightEntry(90590, 1400),
        HighlightEntry(92242, 1400),
        HighlightEntry(94039, 1400),
        HighlightEntry(95724, 1400),
        HighlightEntry(97591, 1400),
        HighlightEntry(99556, 1400),
        HighlightEntry(102173, 1400),
        HighlightEntry(104173, 1400),
        HighlightEntry(106357, 1400),
        HighlightEntry(108089, 1400),
        HighlightEntry(112056, 1400),
        HighlightEntry(113721, 1400),
        HighlightEntry(115372, 1400),
        HighlightEntry(116958, 1400),
        HighlightEntry(118604, 1400),
        HighlightEntry(120576, 1400),
        HighlightEntry(122274, 1400),
        HighlightEntry(124140, 1400),
        HighlightEntry(128140, 1400),
        HighlightEntry(129806, 1400),
        HighlightEntry(133344, 1400),
        HighlightEntry(135773, 1400),
        HighlightEntry(137437, 1400),
        HighlightEntry(139087, 1400),
    ]
    result = FreezeFrameCalculator(narrations, highlights).calculate()
    assert_no_audio_overlap(result, narrations)
    for i in range(len(result.adjusted_timestamps) - 1):
        assert result.adjusted_timestamps[i] < result.adjusted_timestamps[i + 1]
    for freeze in result.freeze_frames:
        for h in highlights:
            hl_end = h.timestamp_ms + h.duration_ms
            assert not (freeze.time_ms > h.timestamp_ms and freeze.time_ms < hl_end), (
                f"freeze at {freeze.time_ms}ms must not be during highlight {h.timestamp_ms}-{hl_end}ms"
            )


def test_nearly_simultaneous_narrations_should_each_get_own_freeze_frame():
    narrations = [
        seg(100000, 100000, 3000),
        seg(107000, 107000, 2000),
        seg(108803, 108803, 4000),
        seg(108804, 108804, 5000),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) == 4
    assert_no_audio_overlap(result, narrations)


def test_bracketed_narration_where_action_is_shorter_than_audio_should_freeze():
    result = FreezeFrameCalculator([seg(1000, 3000, 5000), seg(3000, 3000, 0)], []).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 3000
    assert result.freeze_frames[0].duration_ms == 3000


def test_bracketed_narration_where_action_is_longer_than_audio_should_not_freeze():
    result = FreezeFrameCalculator([seg(1000, 6000, 2000)], []).calculate()
    assert len(result.freeze_frames) == 0


def test_freeze_should_be_placed_at_end_ms_even_if_gap_to_next_narration():
    result = FreezeFrameCalculator([seg(0, 2000, 5000), seg(10000, 10000, 0)], []).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 2000
    assert result.freeze_frames[0].duration_ms == 3000


def test_audio_should_play_during_its_own_freeze_not_after_it():
    result = FreezeFrameCalculator([seg(5000, 5000, 3000)], []).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 5000
    assert result.freeze_frames[0].duration_ms == 3000
    assert result.adjusted_timestamps[0] == 5000


def test_preceding_freezes_should_shift_but_own_freeze_should_not():
    result = FreezeFrameCalculator([seg(0, 2000, 4000), seg(2000, 2000, 0), seg(5000, 5000, 3000)], []).calculate()
    assert result.adjusted_timestamps[0] == 0
    assert result.adjusted_timestamps[2] == 7000


def test_each_narration_gets_its_own_freeze_when_audio_overflows():
    narrations = [seg(0, 8000, 10000), seg(8000, 10000, 5000)]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) == 2
    assert result.freeze_frames[0].time_ms == 8000
    assert result.freeze_frames[0].duration_ms == 2000
    assert result.freeze_frames[1].time_ms == 10000
    assert result.freeze_frames[1].duration_ms == 3000
    assert result.adjusted_timestamps[0] == 0
    assert result.adjusted_timestamps[1] == 10000


def test_freeze_pushed_past_next_narration_by_highlight_uses_audio_safety_net():
    narrations = [seg(0, 5000, 8000), seg(5000, 7000, 2000)]
    result = FreezeFrameCalculator(narrations, [HighlightEntry(4900, 1400)]).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 6300
    n1_adj = result.adjusted_timestamps[1]
    n0_audio_end = result.adjusted_timestamps[0] + narrations[0].audio_duration_ms
    assert n1_adj >= n0_audio_end


def test_freeze_duration_should_be_preserved_when_shifted_past_highlight():
    result = FreezeFrameCalculator(
        [seg(0, 2000, 4000), seg(2000, 2000, 0)],
        [HighlightEntry(1800, 1400)],
    ).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 3200
    assert result.freeze_frames[0].duration_ms == 2000


def test_audio_overflow_should_always_insert_freeze_even_if_next_segment_has_slack():
    narrations = [seg(0, 2000, 4000), seg(2000, 10000, 3000)]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 2000
    assert result.freeze_frames[0].duration_ms == 2000
    assert result.adjusted_timestamps[0] == 0
    assert result.adjusted_timestamps[1] == 4000


def test_consecutive_narrations_should_not_create_silent_gaps():
    narrations = [
        seg(75375, 78721, 4400),
        seg(78775, 78775, 4725),
        seg(78777, 78777, 8675),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) == 3
    assert_no_audio_overlap(result, narrations)


def test_should_reject_freeze_frame_near_video_recording_end():
    video_recording_end_ms = 116239
    narrations = [
        seg(234, 234, 5000),
        seg(5000, 10000, 3000),
        seg(116237, 116237, 5850),
    ]
    result = FreezeFrameCalculator(narrations, []).calculate()
    assert len(result.freeze_frames) > 0
    with pytest.raises(ValueError, match="116237"):
        validate_freeze_positions(result.freeze_frames, video_recording_end_ms)


def test_should_accept_freeze_frame_well_before_video_end():
    video_recording_end_ms = 120000
    narrations = [seg(1000, 5000, 8000), seg(60000, 60000, 5000)]
    result = FreezeFrameCalculator(narrations, []).calculate()
    validate_freeze_positions(result.freeze_frames, video_recording_end_ms)


def test_freeze_frame_near_video_end_should_be_moved_earlier():
    video_recording_end_ms = 50889
    narrations = [seg(49333, 50887, 9250)]

    result_without_bound = FreezeFrameCalculator(narrations, []).calculate()
    assert result_without_bound.freeze_frames[0].time_ms == 50887

    result = FreezeFrameCalculator(narrations, [], video_recording_end_ms).calculate()
    assert len(result.freeze_frames) == 1
    assert result.freeze_frames[0].time_ms == 49333


class TestDetectDeadAirGaps:
    def test_no_gap_when_narrations_are_back_to_back(self):
        narrations = [seg(0, 5000, 5000), seg(5000, 10000, 5000)]
        gaps = detect_dead_air_gaps(narrations, [0, 5000], [])
        assert len(gaps) == 0

    def test_no_gap_when_silence_is_shorter_than_threshold(self):
        narrations = [seg(0, 3000, 3000), seg(5000, 8000, 3000)]
        gaps = detect_dead_air_gaps(narrations, [0, 5000], [])
        assert len(gaps) == 0

    def test_detects_gap_when_silence_exceeds_threshold(self):
        narrations = [seg(0, 3000, 3000), seg(10000, 13000, 3000)]
        gaps = detect_dead_air_gaps(narrations, [0, 10000], [])
        assert len(gaps) == 1
        assert gaps[0].start_ms == 3300
        assert gaps[0].end_ms == 9700

    def test_preserves_margins_around_gap(self):
        narrations = [seg(0, 2000, 2000), seg(8000, 10000, 2000)]
        gaps = detect_dead_air_gaps(narrations, [0, 8000], [])
        assert len(gaps) == 1
        assert gaps[0].start_ms == 2300
        assert gaps[0].end_ms == 7700

    def test_occupied_interval_splits_gap(self):
        narrations = [seg(0, 2000, 2000), seg(12000, 14000, 2000)]
        gaps = detect_dead_air_gaps(narrations, [0, 12000], [(5000, 7000)])
        assert len(gaps) == 2
        assert gaps[0].start_ms == 2300
        assert gaps[0].end_ms == 5000
        assert gaps[1].start_ms == 7000
        assert gaps[1].end_ms == 11700

    def test_occupied_interval_can_eliminate_gap_entirely(self):
        narrations = [seg(0, 2000, 2000), seg(8000, 10000, 2000)]
        gaps = detect_dead_air_gaps(narrations, [0, 8000], [(2000, 8000)])
        assert len(gaps) == 0

    def test_multiple_gaps_detected_across_narrations(self):
        narrations = [
            seg(0, 2000, 2000),
            seg(10000, 12000, 2000),
            seg(20000, 22000, 2000),
        ]
        gaps = detect_dead_air_gaps(narrations, [0, 10000, 20000], [])
        assert len(gaps) == 2
        assert gaps[0].start_ms == 2300
        assert gaps[0].end_ms == 9700
        assert gaps[1].start_ms == 12300
        assert gaps[1].end_ms == 19700

    def test_uses_adjusted_timestamps_not_original(self):
        narrations = [seg(0, 3000, 5000), seg(3000, 15000, 2000)]
        gaps = detect_dead_air_gaps(narrations, [0, 15000], [])
        assert len(gaps) == 1
        assert gaps[0].start_ms == 5300
        assert gaps[0].end_ms == 14700


class TestAdjustForCuts:
    def test_no_shift_when_no_gap_cuts(self):
        assert adjust_for_cuts(5000, []) == 5000

    def test_timestamp_before_gap_is_unchanged(self):
        assert adjust_for_cuts(3000, [GapCut(5000, 8000)]) == 3000

    def test_timestamp_after_gap_is_shifted_by_gap_duration(self):
        assert adjust_for_cuts(10000, [GapCut(5000, 8000)]) == 7000

    def test_timestamp_inside_gap_is_collapsed_to_gap_start(self):
        assert adjust_for_cuts(6000, [GapCut(5000, 8000)]) == 5000

    def test_multiple_gaps_cumulative_shift(self):
        gap_cuts = [GapCut(3000, 5000), GapCut(10000, 13000)]
        assert adjust_for_cuts(1000, gap_cuts) == 1000
        assert adjust_for_cuts(7000, gap_cuts) == 5000
        assert adjust_for_cuts(15000, gap_cuts) == 10000

    def test_timestamp_at_exact_gap_end_is_shifted_by_full_gap(self):
        assert adjust_for_cuts(8000, [GapCut(5000, 8000)]) == 5000


class TestSubtractOccupied:
    def test_no_occupied_returns_original_interval(self):
        result = subtract_occupied(1000, 5000, [])
        assert len(result) == 1
        assert result[0] == (1000, 5000)

    def test_occupied_fully_containing_interval_returns_empty(self):
        result = subtract_occupied(2000, 4000, [(1000, 5000)])
        assert len(result) == 0

    def test_occupied_splits_interval_in_two(self):
        result = subtract_occupied(1000, 8000, [(3000, 5000)])
        assert len(result) == 2
        assert result[0] == (1000, 3000)
        assert result[1] == (5000, 8000)

    def test_occupied_outside_interval_has_no_effect(self):
        result = subtract_occupied(2000, 4000, [(5000, 7000)])
        assert len(result) == 1
        assert result[0] == (2000, 4000)

    def test_occupied_trims_start_of_interval(self):
        result = subtract_occupied(2000, 6000, [(1000, 3000)])
        assert len(result) == 1
        assert result[0] == (3000, 6000)

    def test_occupied_trims_end_of_interval(self):
        result = subtract_occupied(2000, 6000, [(5000, 8000)])
        assert len(result) == 1
        assert result[0] == (2000, 5000)

    def test_multiple_occupied_fragments_interval(self):
        result = subtract_occupied(0, 10000, [(2000, 3000), (5000, 7000)])
        assert len(result) == 3
        assert result[0] == (0, 2000)
        assert result[1] == (3000, 5000)
        assert result[2] == (7000, 10000)
