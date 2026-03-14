"""Definition extraction service with dictionary and Ollama fallback."""

import html

from .config_service import (
    get_definition_backend,
    get_ollama_max_attempts_per_word,
)
from ..providers.dictionary_api_provider import fetch_dictionary_entries
from ..providers.ollama_provider import generate_definition_with_ollama


def normalize_word(word):
    """Trim user-provided word before API lookup."""
    return word.strip()


def clean_definition_text(text):
    """Normalize spacing in definition text."""
    return " ".join(text.strip().split())


def count_words(text):
    """Return approximate word count in definition."""
    return len(text.split())


def is_quality_definition(definition):
    """Apply lightweight quality checks for definitions."""
    if not definition:
        return False

    word_count = count_words(definition)

    if word_count < 4 or word_count > 24:
        return False

    if definition.count(".") + definition.count("!") + definition.count("?") > 1:
        return False

    return True


def extract_definition_from_entry(entry):
    """Extract first usable definition from a single dictionary API entry."""
    meanings = entry.get("meanings", [])

    if not isinstance(meanings, list):
        return None

    for meaning in meanings:
        if not isinstance(meaning, dict):
            continue

        definitions = meaning.get("definitions", [])

        if not isinstance(definitions, list):
            continue

        for definition_item in definitions:
            if not isinstance(definition_item, dict):
                continue

            definition = definition_item.get("definition")

            if not isinstance(definition, str):
                continue

            cleaned_definition = clean_definition_text(definition)

            if is_quality_definition(cleaned_definition):
                return cleaned_definition

    return None


def get_definition_from_dictionary(word):
    """Return first valid dictionary definition for a word."""
    entries = fetch_dictionary_entries(word)

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        definition = extract_definition_from_entry(entry)

        if definition:
            return definition

    return None


def get_definition_from_ollama(word):
    """Try to generate definition with Ollama using bounded retries."""
    max_attempts = max(1, int(get_ollama_max_attempts_per_word()))

    for _ in range(max_attempts):
        generated_definition = generate_definition_with_ollama(word)

        if not isinstance(generated_definition, str):
            continue

        cleaned_definition = clean_definition_text(generated_definition)

        if is_quality_definition(cleaned_definition):
            return cleaned_definition

    return None


def get_definition_for_word(word):
    """Return single definition via dictionary, then optional Ollama fallback."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    dictionary_definition = get_definition_from_dictionary(normalized_word)

    if dictionary_definition:
        return dictionary_definition

    if get_definition_backend() == "dictionary_then_ollama":
        return get_definition_from_ollama(normalized_word)

    return None


def format_definition(definition):
    """Format definition for safe HTML rendering in Anki."""
    return html.escape(definition)
