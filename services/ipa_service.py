"""IPA extraction service based on Free Dictionary API payloads."""

from ..providers.dictionary_api_provider import fetch_dictionary_entries


def normalize_word(word):
    """Trim user-provided word before API lookup."""
    return word.strip()


def normalize_ipa_text(text):
    """Trim IPA and normalize it to slash-wrapped notation."""
    cleaned_text = text.strip()

    if not cleaned_text:
        return None

    if cleaned_text.startswith("/") and cleaned_text.endswith("/"):
        return cleaned_text

    return f"/{cleaned_text}/"


def extract_ipa_from_entry(entry):
    """Extract first usable IPA transcription from one API entry."""
    phonetic = entry.get("phonetic")

    if isinstance(phonetic, str):
        normalized_phonetic = normalize_ipa_text(phonetic)

        if normalized_phonetic:
            return normalized_phonetic

    phonetics = entry.get("phonetics", [])

    if not isinstance(phonetics, list):
        return None

    for phonetic_item in phonetics:
        if not isinstance(phonetic_item, dict):
            continue

        text = phonetic_item.get("text")

        if not isinstance(text, str):
            continue

        normalized_text = normalize_ipa_text(text)

        if normalized_text:
            return normalized_text

    return None


def get_ipa_for_word(word):
    """Fetch dictionary entries and return first available IPA value."""
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    entries = fetch_dictionary_entries(normalized_word)

    for entry in entries:
        if not isinstance(entry, dict):
            continue

        ipa = extract_ipa_from_entry(entry)

        if ipa:
            return ipa

    return None
