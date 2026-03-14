"""Example sentence extraction and formatting service."""

import logging
import sys
import re

from .config_service import get_example_count, get_example_backend
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
    pattern = rf"\b{re.escape(target_word.lower())}\b"
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


def get_examples_for_word(word):
    """Return unique examples for a word, capped by config example_count."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return []

    example_count = get_example_count()
    if example_count <= 0:
        return []

    entries = fetch_dictionary_entries(normalized_word)

    all_examples = []

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        entry_examples = extract_examples_from_entry(entry)
        all_examples.extend(entry_examples)

    all_examples = dedupe_examples(all_examples)
    logger.info(f"all_examples: {all_examples}")

    if len(all_examples) < example_count and get_example_backend() == "dictionary_then_ollama":
        missing_count = example_count - len(all_examples)
        generated_examples = generate_examples_with_ollama(
            word=normalized_word,
            count=missing_count,
        )

        filtered_generated_examples = []

        for example in generated_examples:
            cleaned_example = clean_example_text(example)

            if is_quality_example(cleaned_example, normalized_word):
                filtered_generated_examples.append(cleaned_example)

        all_examples.extend(filtered_generated_examples)
        all_examples = dedupe_examples(all_examples)

    return all_examples[:example_count]


def format_examples(examples):
    """Format examples as a newline-separated block for Anki field."""
    return "\n".join(examples)
