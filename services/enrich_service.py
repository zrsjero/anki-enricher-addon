from .note_service import (
    get_note_ids,
    get_note,
    get_missing_required_fields,
    get_field_value,
    get_empty_target_fields,
    set_field_value,
    save_note,
)
from .ipa_service import get_ipa_for_word
from .example_service import get_examples_for_word, format_examples
from .audio_service import (
    build_audio_filename,
    build_sound_tag,
    generate_test_audio_data,
)
from .media_service import media_file_exists, write_media_file


def enrich_notes():
    note_ids = get_note_ids()

    if not note_ids:
        return {
            "status": "no_notes",
            "processed": 0,
            "updated": 0,
            "skipped": 0,
            "ipa_updated": 0,
            "example_updated": 0,
            "audio_updated": 0,
            "errors": 0,
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
            "example_updated": 0,
            "audio_updated": 0,
            "errors": 0,
        }

    processed_count = 0
    updated_count = 0
    skipped_count = 0
    ipa_updated_count = 0
    example_updated_count = 0
    audio_updated_count = 0
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

        if "Example" in empty_target_fields:
            examples = get_examples_for_word(english_value)

            if examples:
                formatted_examples = format_examples(examples)
                set_field_value(note, "Example", formatted_examples)
                was_updated = True
                example_updated_count += 1
            else:
                error_count += 1

        if "EnglishAudio" in empty_target_fields:
            filename = build_audio_filename(english_value)
            sound_tag = build_sound_tag(filename)

            if filename and sound_tag:
                if not media_file_exists(filename):
                    audio_data = generate_test_audio_data(english_value)

                    if audio_data:
                        write_media_file(filename, audio_data)
                    else:
                        error_count += 1
                        continue

                if media_file_exists(filename):
                    set_field_value(note, "EnglishAudio", sound_tag)
                    was_updated = True
                    audio_updated_count += 1
                else:
                    error_count += 1
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
        "example_updated": example_updated_count,
        "audio_updated": audio_updated_count,
        "errors": error_count,
    }