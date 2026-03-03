"""Tests for sync_detect module: green frame detection, QR decode failure behavior."""

from PIL import Image

from screencast_narrator.sync_detect import (
    group_consecutive_into_ranges,
    group_into_spans,
    is_green_frame,
    SyncMarker,
)


def test_pure_green_frame_is_detected():
    img = Image.new("RGB", (1920, 1080), (0, 255, 0))
    assert is_green_frame(img) is True


def test_non_green_frame_is_not_detected():
    img = Image.new("RGB", (1920, 1080), (255, 255, 255))
    assert is_green_frame(img) is False


def test_red_frame_is_not_detected():
    img = Image.new("RGB", (1920, 1080), (255, 0, 0))
    assert is_green_frame(img) is False


def test_mostly_green_with_center_qr_is_detected():
    img = Image.new("RGB", (1920, 1080), (0, 255, 0))
    center_x, center_y = 960, 540
    for dx in range(-200, 201):
        for dy in range(-200, 201):
            img.putpixel((center_x + dx, center_y + dy), (0, 0, 0))
    assert is_green_frame(img) is True


def test_dark_green_frame_is_detected():
    img = Image.new("RGB", (1920, 1080), (0, 200, 0))
    assert is_green_frame(img) is True


def test_borderline_green_is_not_detected():
    img = Image.new("RGB", (1920, 1080), (100, 150, 100))
    assert is_green_frame(img) is False


def test_group_consecutive_into_ranges_single():
    result = group_consecutive_into_ranges({5})
    assert result == [(5, 5)]


def test_group_consecutive_into_ranges_contiguous():
    result = group_consecutive_into_ranges({1, 2, 3, 4, 5})
    assert result == [(1, 5)]


def test_group_consecutive_into_ranges_multiple_groups():
    result = group_consecutive_into_ranges({1, 2, 3, 7, 8, 9, 15})
    assert result == [(1, 3), (7, 9), (15, 15)]


def test_group_consecutive_into_ranges_empty():
    result = group_consecutive_into_ranges(set())
    assert result == []


def test_group_into_spans_groups_consecutive_same_marker():
    markers = [
        SyncMarker(0, "START", 10),
        SyncMarker(0, "START", 11),
        SyncMarker(0, "START", 12),
        SyncMarker(1, "START", 50),
        SyncMarker(1, "START", 51),
    ]
    spans = group_into_spans(markers)
    assert len(spans) == 2
    assert spans[0].narration_id == 0
    assert spans[0].first_frame == 10
    assert spans[0].last_frame == 12
    assert spans[1].narration_id == 1
    assert spans[1].first_frame == 50
    assert spans[1].last_frame == 51


def test_group_into_spans_allows_one_frame_gap():
    markers = [
        SyncMarker(0, "START", 10),
        SyncMarker(0, "START", 12),
    ]
    spans = group_into_spans(markers)
    assert len(spans) == 1
    assert spans[0].first_frame == 10
    assert spans[0].last_frame == 12


def test_group_into_spans_splits_on_different_marker():
    markers = [
        SyncMarker(0, "START", 10),
        SyncMarker(0, "END", 11),
    ]
    spans = group_into_spans(markers)
    assert len(spans) == 2
