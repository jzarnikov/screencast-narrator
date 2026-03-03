"""QR code roundtrip tests: generate with qrcode, decode with pyzbar."""

import base64
import io

from PIL import Image
from pyzbar.pyzbar import decode as pyzbar_decode

from screencast_narrator.sync_frames import format_sync_data, generate_qr_data_url


def test_qr_code_roundtrip():
    data = format_sync_data(7, "START")
    assert data == "SYNC|7|START"

    data_url = generate_qr_data_url(data)
    assert data_url.startswith("data:image/png;base64,")

    b64 = data_url[len("data:image/png;base64,"):]
    image_bytes = base64.b64decode(b64)
    img = Image.open(io.BytesIO(image_bytes))
    assert img is not None
    assert img.width == 400
    assert img.height == 400

    results = pyzbar_decode(img)
    assert len(results) >= 1
    decoded = results[0].data.decode("utf-8")
    assert decoded == "SYNC|7|START"


def test_different_narration_ids_produce_different_qr_codes():
    url1 = generate_qr_data_url(format_sync_data(0, "START"))
    url2 = generate_qr_data_url(format_sync_data(1, "START"))
    assert url1 != url2


def test_format_sync_data_formats_correctly():
    assert format_sync_data(0, "START") == "SYNC|0|START"
    assert format_sync_data(12, "END") == "SYNC|12|END"
