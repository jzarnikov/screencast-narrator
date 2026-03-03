"""QR code sync frame injection: generates QR overlay JS snippets for browser-based recording."""

from __future__ import annotations

import base64
import io

import qrcode

QR_SIZE = 400
DISPLAY_DURATION_MS = 160


def format_sync_data(narration_id: int, marker: str) -> str:
    return f"SYNC|{narration_id}|{marker}"


def generate_qr_data_url(data: str) -> str:
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img = img.resize((QR_SIZE, QR_SIZE))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"


def get_inject_js(data_url: str) -> str:
    return f"""(function() {{
    const overlay = document.createElement('div');
    overlay.id = '_e2e_sync';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100vw;height:100vh;'
        + 'background:#00FF00;display:flex;align-items:center;justify-content:center;'
        + 'z-index:999999;';
    const img = document.createElement('img');
    img.src = '{data_url}';
    img.style.cssText = 'width:400px;height:400px;image-rendering:pixelated;';
    overlay.appendChild(img);
    document.body.appendChild(overlay);
}})()"""


def get_remove_js() -> str:
    return "document.getElementById('_e2e_sync')?.remove()"


def inject_sync_frame(page, narration_id: int, marker: str) -> None:
    """Inject a green QR code overlay into a Playwright page, wait, then remove it."""
    data = format_sync_data(narration_id, marker)
    data_url = generate_qr_data_url(data)
    page.evaluate(get_inject_js(data_url))
    page.wait_for_timeout(DISPLAY_DURATION_MS)
    page.evaluate(get_remove_js())
