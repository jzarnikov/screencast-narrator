"""ffmpeg/ffprobe subprocess helpers."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


def require_command(name: str) -> None:
    if shutil.which(name) is None:
        raise RuntimeError(f"{name} is required but not found on PATH")


def exec_ffmpeg(*args: str) -> None:
    cmd = ["ffmpeg", *args]
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        tail = result.stdout[-2000:] + result.stderr[-2000:]
        raise RuntimeError(
            f"Command failed (exit {result.returncode}): {' '.join(cmd)}\n"
            f"Output: {tail.decode('utf-8', errors='replace')}"
        )


def probe_duration_ms(media_path: Path) -> int:
    if not media_path.exists():
        raise RuntimeError(f"Media file does not exist: {media_path}")
    if media_path.stat().st_size == 0:
        raise RuntimeError(f"Media file is empty (0 bytes): {media_path}")

    output = _run_ffprobe(media_path)
    if output == "N/A":
        raise RuntimeError(f"ffprobe returned 'N/A' for duration of {media_path}. The file may not be fully finalized.")
    return int(float(output) * 1000)


def _run_ffprobe(media_path: Path) -> str:
    result = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-show_entries",
            "format=duration",
            "-of",
            "default=noprint_wrappers=1:nokey=1",
            str(media_path),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"ffprobe failed (exit {result.returncode}) for {media_path}: {result.stdout}{result.stderr}"
        )
    return result.stdout.strip()


def probe_dimensions(video_path: Path) -> tuple[int, int]:
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height",
         "-of", "csv=p=0:s=x", str(video_path)],
        capture_output=True, text=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"ffprobe failed for {video_path}: {result.stderr}")
    w, h = result.stdout.strip().split("x")
    return int(w), int(h)


def secs(seconds: float) -> str:
    return f"{seconds:.3f}"
