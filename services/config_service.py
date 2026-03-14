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


def get_example_backend():
    """Return active example generation backend strategy."""
    config = get_addon_config()
    return config.get("example_backend", "dictionary_then_ollama")


def get_ollama_config():
    """Return raw Ollama-related config section."""
    config = get_addon_config()
    ollama_config = config.get("ollama", {})

    if not isinstance(ollama_config, dict):
        return {}

    return ollama_config


def is_ollama_enabled():
    """Return whether Ollama fallback is enabled in config."""
    ollama_config = get_ollama_config()
    return bool(ollama_config.get("enabled", False))


def get_ollama_base_url():
    """Return Ollama API base URL."""
    ollama_config = get_ollama_config()
    return ollama_config.get("base_url", "http://127.0.0.1:11434")


def get_ollama_model():
    """Return Ollama model identifier."""
    ollama_config = get_ollama_config()
    return ollama_config.get("model", "qwen2.5:3b-instruct")


def get_ollama_timeout_seconds():
    """Return Ollama request timeout in seconds."""
    ollama_config = get_ollama_config()
    return ollama_config.get("timeout_seconds", 25)


def get_ollama_temperature():
    """Return Ollama sampling temperature."""
    ollama_config = get_ollama_config()
    return ollama_config.get("temperature", 0.6)


def get_audio_prefix():
    """Return filename prefix for generated audio files."""
    config = get_addon_config()
    return config.get("audio_prefix", "jeeng")


def get_audio_backend():
    """Return active audio backend identifier."""
    config = get_addon_config()
    return config.get("audio_backend", "macos_say")
