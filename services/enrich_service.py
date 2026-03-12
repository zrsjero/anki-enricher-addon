from .ipa_service import get_ipa_for_word
from .note_service import (
    get_note_ids,
    get_note,
    get_missing_required_fields,
    get_field_value,
    get_empty_target_fields,
    set_field_value,
    save_note,
)


def enrich_notes():
    note_ids = get_note_ids()

    if not note_ids:
        return {
            "status": "no_notes",
            "processed": 0,
            "updated": 0,
            "skipped": 0,
            "ipa_updated": 0,
        }

    first_note = get_note(note_ids[0])
    missing_fields = get_missing_required_fields(first_note)

    if missing_fields:
        return {
            "status": "missing_fields",
            "missing_fields": missing_fields,
            "processed": 0,
            "updated": 0,
            "skipped": 0,
            "ipa_updated": 0,
        }

    processed_count = 0
    updated_count = 0
    skipped_count = 0
    ipa_updated_count = 0
    error_count = 0

    for note_id in note_ids:
        processed_count += 1

        note = get_note(note_id)
        english_value = get_field_value(note, "English")

        if not english_value:
            skipped_count += 1
            continue

        empty_target_fields = get_empty_target_fields(note)
        was_updated = False

        if "IPA" in empty_target_fields:
            ipa_value = get_ipa_for_word(english_value)

            if ipa_value:
                set_field_value(note, "IPA", ipa_value)
                was_updated = True
                ipa_updated_count += 1
            else:
                error_count += 1

        if was_updated:
            save_note(note)
            updated_count += 1

    return {
        "status": "ok",
        "processed": processed_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "ipa_updated": ipa_updated_count,
        "errors": error_count,
    }
