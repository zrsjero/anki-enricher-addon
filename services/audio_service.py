"""Audio naming and generation service with backend abstraction."""

import re

from .config_service import get_audio_prefix, get_audio_backend
from ..providers.macos_say_audio_provider import generate_audio_data_with_say


def normalize_word(word):
    """Trim and lowercase source text used for filenames and synthesis."""
    return word.strip().lower()


def sanitize_filename_part(text):
    """Convert text to a filesystem-safe token."""
    sanitized = text.strip().lower()
    sanitized = sanitized.replace(" ", "_")
    sanitized = re.sub(r"[^a-z0-9_-]", "", sanitized)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")

    return sanitized


def get_audio_extension():
    """Return file extension expected from the current audio backend."""
    backend = get_audio_backend()

    if backend == "macos_say":
        return "aiff"

    return "mp3"


def build_audio_filename(word):
    """Build deterministic media filename for a word."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    safe_word = sanitize_filename_part(normalized_word)

    if not safe_word:
        return None

    audio_prefix = sanitize_filename_part(get_audio_prefix())

    if not audio_prefix:
        audio_prefix = "audio"

    extension = get_audio_extension()
    return f"{audio_prefix}_{safe_word}.{extension}"


def build_sound_tag(filename):
    """Build Anki sound tag for a media filename."""
    if not filename:
        return None

    return f"[sound:{filename}]"


def generate_audio_data(word):
    """Generate raw audio bytes for a word via configured backend."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    backend = get_audio_backend()

    if backend == "macos_say":
        return generate_audio_data_with_say(normalized_word)

    return None
