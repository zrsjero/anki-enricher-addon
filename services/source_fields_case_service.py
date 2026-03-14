"""Optional normalization for source text fields (english/russian)."""

from .config_service import (
    get_field_name,
    is_source_first_char_lowercase_enabled,
)


def normalize_first_char_to_lower(text):
    """Return text with first character lowercased if needed."""
    if not isinstance(text, str):
        return text

    cleaned_text = text.strip()

    if not cleaned_text:
        return cleaned_text

    first_char = cleaned_text[0]
    lowered_first_char = first_char.lower()

    if first_char == lowered_first_char:
        return cleaned_text

    return lowered_first_char + cleaned_text[1:]


def normalize_source_fields_for_note(note):
    """Normalize first character for english/russian fields on a note."""
    if not is_source_first_char_lowercase_enabled():
        return False

    changed = False
    source_field_keys = ["english", "russian"]

    for field_key in source_field_keys:
        field_name = get_field_name(field_key)
        current_value = note[field_name]
        normalized_value = normalize_first_char_to_lower(current_value)

        if normalized_value != current_value:
            note[field_name] = normalized_value
            changed = True

    return changed
