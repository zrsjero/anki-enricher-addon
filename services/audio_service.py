import re


AUDIO_FILE_PREFIX = "jeeng"


def normalize_word(word):
    return word.strip().lower()


def sanitize_filename_part(text):
    sanitized = text.strip().lower()
    sanitized = sanitized.replace(" ", "_")
    sanitized = re.sub(r"[^a-z0-9_-]", "", sanitized)
    sanitized = re.sub(r"_+", "_", sanitized)
    sanitized = sanitized.strip("_")

    return sanitized


def build_audio_filename(word):
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    safe_word = sanitize_filename_part(normalized_word)

    if not safe_word:
        return None

    return f"{AUDIO_FILE_PREFIX}_{safe_word}.mp3"


def build_sound_tag(filename):
    if not filename:
        return None

    return f"[sound:{filename}]"


def generate_test_audio_data(word):
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    safe_word = sanitize_filename_part(normalized_word)

    if not safe_word:
        return None

    return f"FAKE_MP3_FOR_{safe_word}".encode("utf-8")