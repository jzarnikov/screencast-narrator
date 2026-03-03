"""Port of QrDecodeTest.java — decode QR from a real compressed video frame."""

from pathlib import Path

from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode


def test_should_decode_qr_from_compressed_video_frame():
    sample_path = Path(__file__).parent / "resources" / "sync_frame_sample.png"
    assert sample_path.exists(), f"sample frame image must exist: {sample_path}"

    img = Image.open(sample_path)
    assert img is not None, "sample frame image must load"

    results = pyzbar_decode(img)
    assert len(results) >= 1, "QR code must be decodable from compressed video frame"

    decoded = results[0].data.decode("utf-8")
    assert decoded.startswith("SYNC|")
    assert len(decoded.split("|")) == 3
