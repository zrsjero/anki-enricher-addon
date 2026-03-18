"""Definition generation service using the selected text provider."""

import html

from .config_service import (
    get_text_provider,
    get_text_provider_max_attempts_per_word,
)
from ..providers.text_provider_registry import generate_definition_with_provider


def normalize_word(word):
    """Trim user-provided word before API lookup."""
    return word.strip()


def clean_definition_text(text):
    """Normalize spacing in definition text."""
    compact_text = " ".join(text.strip().split())
    return uppercase_first_letter(compact_text)


def uppercase_first_letter(text):
    """Uppercase the first alphabetic character, preserving prefix symbols."""
    for index, char in enumerate(text):
        if not char.isalpha():
            continue

        upper_char = char.upper()
        if upper_char == char:
            return text

        return f"{text[:index]}{upper_char}{text[index + 1:]}"

    return text


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


def get_definition_from_provider(word, provider_override=None):
    """Try to generate definition with selected provider using bounded retries."""
    provider_key = provider_override or get_text_provider()
    max_attempts = max(1, int(get_text_provider_max_attempts_per_word()))

    for _ in range(max_attempts):
        generated_definition = generate_definition_with_provider(
            word=word,
            provider_key=provider_key,
        )

        if not isinstance(generated_definition, str):
            continue

        cleaned_definition = clean_definition_text(generated_definition)

        if is_quality_definition(cleaned_definition):
            return cleaned_definition

    return None


def get_definition_for_word(word, provider_override=None):
    """Return one definition via selected provider."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    return get_definition_from_provider(
        normalized_word,
        provider_override=provider_override,
    )


def format_definition(definition):
    """Format definition for safe HTML rendering in Anki."""
    return html.escape(definition)
