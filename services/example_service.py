import logging
import sys

from .config_service import get_example_count
from ..providers.dictionary_api_provider import fetch_dictionary_entries

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    stream=sys.stdout,
)

logger = logging.getLogger(__name__)


def normalize_word(word):
    return word.strip()


def clean_example_text(text):
    return " ".join(text.strip().split())


def extract_examples_from_entry(entry):
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
    normalized_word = normalize_word(word)

    if not normalized_word:
        return []

    entries = fetch_dictionary_entries(normalized_word)

    all_examples = []
    seen_examples = set()

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        entry_examples = extract_examples_from_entry(entry)

        for example in entry_examples:
            example_key = example.lower()

            if example_key in seen_examples:
                continue

            seen_examples.add(example_key)
            all_examples.append(example)

    example_count = get_example_count()
    return all_examples[:example_count]


def format_examples(examples):
    return "\n".join(examples)
