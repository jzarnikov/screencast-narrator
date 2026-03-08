"""Port of QrDecodeTest.java — decode QR from a real compressed video frame."""

import json
from pathlib import Path

from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode

from screencast_narrator.sync_detect import decode_qr, is_green_frame

_RESOURCES = Path(__file__).parent / "resources"


def test_should_decode_qr_from_compressed_video_frame():
    sample_path = _RESOURCES / "sync_frame_sample.png"
    assert sample_path.exists(), f"sample frame image must exist: {sample_path}"

    img = Image.open(sample_path)
    assert img is not None, "sample frame image must load"

    results = pyzbar_decode(img)
    assert len(results) >= 1, "QR code must be decodable from compressed video frame"

    decoded = results[0].data.decode("utf-8")
    assert decoded.startswith("SYNC|")
    assert len(decoded.split("|")) == 3


def test_should_decode_dense_qr_with_narration_text_and_translations():
    """Real sync frame screenshot from annual-reports with narration text + German
    translation. Dense QR code that must be decodable for verification to work."""
    img = Image.open(_RESOURCES / "dense_qr_sync_frame.png")

    assert is_green_frame(img), "Dense QR sync frame must be detected as green"

    results = pyzbar_decode(img)
    assert len(results) >= 1, (
        "Dense QR code with narration text + translations must be decodable"
    )

    decoded = results[0].data.decode("utf-8")
    payload = json.loads(decoded)
    assert payload["t"] == "nar"
    assert payload["m"] == "start"
    assert "tx" in payload, "Narration text must be present in payload"
    assert "tr" in payload, "Translations must be present in payload"
    assert "de" in payload["tr"], "German translation must be present"


def test_partial_sync_frame_is_green_but_qr_unreadable():
    """Frame 613 from a real recording: green background with a huge partial QR
    in the bottom-right corner (compositor transition frame). Must be detected
    as green but decode_qr should return None instead of crashing."""
    img = Image.open(_RESOURCES / "partial_sync_frame.png")

    assert is_green_frame(img), "Partial sync frame must be detected as green"

    result = decode_qr(img, frame_index=613)
    assert result is None, "Unreadable QR on a green frame should return None, not crash"
