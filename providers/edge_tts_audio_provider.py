"""Edge TTS audio provider that returns generated MP3 bytes."""

import asyncio
import logging
import shutil
import subprocess
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


def normalize_text(text):
    """Trim text before speech synthesis."""
    return text.strip()


def preview_text(text, limit=40):
    """Return short preview for logs."""
    if len(text) <= limit:
        return text

    return f"{text[:limit]}..."


def normalize_option(value, default):
    """Return non-empty string option or fallback default."""
    if isinstance(value, str):
        normalized = value.strip()
        if normalized:
            return normalized

    return default


def run_coroutine(coroutine):
    """Run coroutine in a dedicated event loop."""
    event_loop = asyncio.new_event_loop()
    try:
        event_loop.run_until_complete(coroutine)
    finally:
        event_loop.close()


def generate_audio_data_with_edge_tts_library(text, voice, rate, volume, pitch):
    """Generate MP3 bytes using Python edge-tts package."""
    try:
        import edge_tts
    except Exception as exc:
        logger.warning("Edge TTS python package is unavailable: %s", exc)
        return None

    temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        communicate = edge_tts.Communicate(
            text,
            voice=voice,
            rate=rate,
            volume=volume,
            pitch=pitch,
        )
        run_coroutine(communicate.save(str(temp_path)))

        if not temp_path.exists() or temp_path.stat().st_size <= 0:
            logger.warning(
                "Edge TTS library returned empty output (voice=%s, text=%r)",
                voice,
                preview_text(text),
            )
            return None

        return temp_path.read_bytes()
    except Exception:
        logger.exception(
            "Edge TTS library generation failed (voice=%s, rate=%s, volume=%s, pitch=%s, text=%r)",
            voice,
            rate,
            volume,
            pitch,
            preview_text(text),
        )
        return None
    finally:
        if temp_path.exists():
            temp_path.unlink()


def generate_audio_data_with_edge_tts_cli(text, voice, rate, volume, pitch):
    """Generate MP3 bytes using edge-tts CLI."""
    if shutil.which("edge-tts") is None:
        logger.warning("Edge TTS CLI is unavailable: command 'edge-tts' not found")
        return None

    temp_file = tempfile.NamedTemporaryFile(suffix=".mp3", delete=False)
    temp_path = Path(temp_file.name)
    temp_file.close()

    try:
        command = [
            "edge-tts",
            "--text",
            text,
            "--voice",
            voice,
            "--rate",
            rate,
            "--volume",
            volume,
            "--pitch",
            pitch,
            "--write-media",
            str(temp_path),
        ]

        completed_process = subprocess.run(
            command,
            capture_output=True,
            text=True,
        )

        if completed_process.returncode != 0:
            stderr_preview = (completed_process.stderr or "").strip()
            stdout_preview = (completed_process.stdout or "").strip()
            logger.warning(
                "Edge TTS CLI failed with code %s (voice=%s, text=%r, stderr=%r, stdout=%r)",
                completed_process.returncode,
                voice,
                preview_text(text),
                stderr_preview[:400],
                stdout_preview[:400],
            )
            return None

        if not temp_path.exists() or temp_path.stat().st_size <= 0:
            logger.warning(
                "Edge TTS CLI produced empty output (voice=%s, text=%r)",
                voice,
                preview_text(text),
            )
            return None

        return temp_path.read_bytes()
    except Exception:
        logger.exception(
            "Edge TTS CLI generation crashed (voice=%s, rate=%s, volume=%s, pitch=%s, text=%r)",
            voice,
            rate,
            volume,
            pitch,
            preview_text(text),
        )
        return None
    finally:
        if temp_path.exists():
            temp_path.unlink()


def generate_audio_data_with_edge_tts(text, voice=None, rate=None, volume=None, pitch=None):
    """Generate MP3 bytes using Edge TTS."""
    normalized_text = normalize_text(text)

    if not normalized_text:
        logger.warning("Edge TTS generation skipped: empty text")
        return None

    normalized_voice = normalize_option(voice, "en-US-AriaNeural")
    normalized_rate = normalize_option(rate, "+0%")
    normalized_volume = normalize_option(volume, "+0%")
    normalized_pitch = normalize_option(pitch, "+0Hz")

    audio_data = generate_audio_data_with_edge_tts_library(
        normalized_text,
        normalized_voice,
        normalized_rate,
        normalized_volume,
        normalized_pitch,
    )
    if audio_data:
        return audio_data

    audio_data = generate_audio_data_with_edge_tts_cli(
        normalized_text,
        normalized_voice,
        normalized_rate,
        normalized_volume,
        normalized_pitch,
    )
    if audio_data:
        return audio_data

    logger.warning(
        "Edge TTS generation failed via python library and CLI (voice=%s, text=%r)",
        normalized_voice,
        preview_text(normalized_text),
    )
    return None
