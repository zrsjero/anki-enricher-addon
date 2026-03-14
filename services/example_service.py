"""Example sentence extraction and formatting service."""

import logging
import html
import re
import sys

from .config_service import (
    get_example_count,
    get_example_backend,
    get_ollama_max_attempts_per_word,
)
from ..providers.dictionary_api_provider import fetch_dictionary_entries
from ..providers.ollama_provider import generate_examples_with_ollama

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def normalize_word(word):
    """Trim user-provided word before API lookup."""
    return word.strip()


def clean_example_text(text):
    """Normalize spacing in a sentence while keeping content intact."""
    return " ".join(text.strip().split())


def count_words(text):
    """Return approximate word count in a sentence."""
    return len(text.split())


def contains_target_word_once(sentence, target_word):
    """Check that target word appears exactly once as a standalone token."""
    normalized_target = target_word.strip().lower()

    if not normalized_target:
        return False

    pattern = rf"(?<!\w){re.escape(normalized_target)}(?!\w)"
    matches = re.findall(pattern, sentence.lower())
    return len(matches) == 1


def is_quality_example(sentence, target_word):
    """Apply lightweight quality filters for generated examples."""
    if not sentence:
        return False

    words_count = count_words(sentence)

    if words_count < 6 or words_count > 14:
        return False

    if not contains_target_word_once(sentence, target_word):
        return False

    if sentence.count(".") + sentence.count("!") + sentence.count("?") > 1:
        return False

    return True


def dedupe_examples(examples):
    """Deduplicate sentences in insertion order (case-insensitive)."""
    deduped = []
    seen_examples = set()

    for example in examples:
        example_key = example.lower()

        if example_key in seen_examples:
            continue

        seen_examples.add(example_key)
        deduped.append(example)

    return deduped


def extend_with_ollama(existing_examples, target_word, target_count):
    """Try to reach target count using multiple Ollama generation attempts."""
    if len(existing_examples) >= target_count:
        return existing_examples[:target_count]

    enriched = list(existing_examples)
    max_attempts = max(1, int(get_ollama_max_attempts_per_word()))

    for _ in range(max_attempts):
        missing_count = target_count - len(enriched)

        if missing_count <= 0:
            break

        # Ask for more candidates than needed to compensate for filtering.
        requested_count = min(max(missing_count * 3, 3), 12)
        generated_examples = generate_examples_with_ollama(
            word=target_word,
            count=requested_count,
        )

        if not generated_examples:
            continue

        for example in generated_examples:
            cleaned_example = clean_example_text(example)

            if is_quality_example(cleaned_example, target_word):
                enriched.append(cleaned_example)

        enriched = dedupe_examples(enriched)

        if len(enriched) >= target_count:
            break

    return enriched[:target_count]


def extract_examples_from_entry(entry):
    """Collect example sentences from a single dictionary API entry."""
    collected_examples = []

    meanings = entry.get("meanings", [])

    if not isinstance(meanings, list):
        return collected_examples

    for meaning in meanings:
        if not isinstance(meaning, dict):
            continue

        definitions = meaning.get("definitions", [])
        logger.info(f"definitions: {definitions}")

        if not isinstance(definitions, list):
            continue

        for definition in definitions:
            if not isinstance(definition, dict):
                continue

            example = definition.get("example")

            if not isinstance(example, str):
                continue

            cleaned_example = clean_example_text(example)

            if cleaned_example:
                collected_examples.append(cleaned_example)

    return collected_examples


def get_examples_for_word(word, backend_override=None):
    """Return unique examples for a word, capped by config example_count."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return []

    example_count = get_example_count()
    if example_count <= 0:
        return []

    example_backend = backend_override or get_example_backend()

    if example_backend == "ollama_only":
        return extend_with_ollama(
            existing_examples=[],
            target_word=normalized_word,
            target_count=example_count,
        )

    entries = fetch_dictionary_entries(normalized_word)

    all_examples = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        entry_examples = extract_examples_from_entry(entry)
        all_examples.extend(entry_examples)

    all_examples = dedupe_examples(all_examples)
    logger.info(f"all_examples: {all_examples}")

    if len(all_examples) < example_count and example_backend == "dictionary_then_ollama":
        all_examples = extend_with_ollama(
            existing_examples=all_examples,
            target_word=normalized_word,
            target_count=example_count,
        )

    return all_examples[:example_count]


def format_examples(examples):
    """Format examples as an HTML line-break separated block for Anki field."""
    escaped_examples = [html.escape(example) for example in examples]
    return "<br>".join(escaped_examples)
