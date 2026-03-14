"""Helpers for reading add-on configuration from Anki."""

from aqt import mw


def get_addon_config():
    """Return a raw add-on config dictionary from Anki addon manager."""
    return mw.addonManager.getConfig(__name__)


def get_note_type_name():
    """Return the configured note type name used in a search query."""
    config = get_addon_config()
    return config["note_type_name"]


def get_field_names():
    """Return mapping of logical field keys to actual note field names."""
    config = get_addon_config()
    return config["fields"]


def get_field_name(field_key):
    """Return concrete field name for a logical field key."""
    field_names = get_field_names()
    return field_names[field_key]


def get_example_count():
    """Return max number of examples to store for a single word."""
    config = get_addon_config()
    return config.get("example_count", 3)


def get_audio_prefix():
    """Return filename prefix for generated audio files."""
    config = get_addon_config()
    return config.get("audio_prefix", "jeeng")


def get_audio_backend():
    """Return active audio backend identifier."""
    config = get_addon_config()
    return config.get("audio_backend", "macos_say")
