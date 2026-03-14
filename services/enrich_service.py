"""Orchestrates note enrichment flow for IPA, definition, examples, and audio."""

from .config_service import get_field_name
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
from .definition_service import get_definition_for_word, format_definition
from .example_service import get_examples_for_word, format_examples
from .source_fields_case_service import normalize_source_fields_for_note
from .audio_service import (
    build_audio_filename,
    build_sound_tag,
    generate_audio_data,
)
from .media_service import media_file_exists, write_media_file


def process_note(note, text_backend_mode=None):
    """Enrich a single note and return per-note processing statistics."""
    english_field_name = get_field_name("english")
    ipa_field_name = get_field_name("ipa")
    definition_field_name = get_field_name("definition")
    example_field_name = get_field_name("example")
    english_audio_field_name = get_field_name("english_audio")

    english_value = get_field_value(note, english_field_name)

    if not english_value:
        return {
            "skipped": True,
            "updated": False,
            "ipa_updated": 0,
            "definition_updated": 0,
            "example_updated": 0,
            "audio_updated": 0,
            "errors": 0,
        }

    empty_target_fields = get_empty_target_fields(note)

    if not empty_target_fields:
        return {
            "skipped": True,
            "updated": False,
            "ipa_updated": 0,
            "definition_updated": 0,
            "example_updated": 0,
            "audio_updated": 0,
            "errors": 0,
        }

    was_updated = False
    ipa_updated_count = 0
    definition_updated_count = 0
    example_updated_count = 0
    audio_updated_count = 0
    error_count = 0

    if normalize_source_fields_for_note(note):
        english_value = get_field_value(note, english_field_name)
        was_updated = True

    if ipa_field_name in empty_target_fields:
        ipa_value = get_ipa_for_word(english_value)

        if ipa_value:
            set_field_value(note, ipa_field_name, ipa_value)
            was_updated = True
            ipa_updated_count += 1
        else:
            error_count += 1

    if definition_field_name in empty_target_fields:
        definition = get_definition_for_word(
            english_value,
            backend_override=text_backend_mode,
        )

        if definition:
            formatted_definition = format_definition(definition)
            set_field_value(note, definition_field_name, formatted_definition)
            was_updated = True
            definition_updated_count += 1
        else:
            error_count += 1

    if example_field_name in empty_target_fields:
        examples = get_examples_for_word(
            english_value,
            backend_override=text_backend_mode,
        )

        if examples:
            formatted_examples = format_examples(examples)
            set_field_value(note, example_field_name, formatted_examples)
            was_updated = True
            example_updated_count += 1
        else:
            error_count += 1

    if english_audio_field_name in empty_target_fields:
        filename = build_audio_filename(english_value)
        sound_tag = build_sound_tag(filename)

        if filename and sound_tag:
            if not media_file_exists(filename):
                audio_data = generate_audio_data(english_value)

                if audio_data:
                    write_media_file(filename, audio_data)
                else:
                    error_count += 1

            if media_file_exists(filename):
                set_field_value(note, english_audio_field_name, sound_tag)
                was_updated = True
                audio_updated_count += 1
            else:
                error_count += 1
        else:
            error_count += 1

    if was_updated:
        save_note(note)

    return {
        "skipped": False,
        "updated": was_updated,
        "ipa_updated": ipa_updated_count,
        "definition_updated": definition_updated_count,
        "example_updated": example_updated_count,
        "audio_updated": audio_updated_count,
        "errors": error_count,
    }


def enrich_notes(deck_name=None, text_backend_mode=None):
    """Run enrichment for configured note type and optional deck."""
    note_ids = get_note_ids(deck_name=deck_name)

    if not note_ids:
        return {
            "status": "no_notes",
            "processed": 0,
            "updated": 0,
            "skipped": 0,
            "ipa_updated": 0,
            "definition_updated": 0,
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
            "definition_updated": 0,
            "example_updated": 0,
            "audio_updated": 0,
            "errors": 0,
        }

    processed_count = 0
    updated_count = 0
    skipped_count = 0
    ipa_updated_count = 0
    definition_updated_count = 0
    example_updated_count = 0
    audio_updated_count = 0
    error_count = 0

    for note_id in note_ids:
        processed_count += 1

        note = get_note(note_id)
        note_result = process_note(
            note,
            text_backend_mode=text_backend_mode,
        )

        if note_result["skipped"]:
            skipped_count += 1

        if note_result["updated"]:
            updated_count += 1

        ipa_updated_count += note_result["ipa_updated"]
        definition_updated_count += note_result["definition_updated"]
        example_updated_count += note_result["example_updated"]
        audio_updated_count += note_result["audio_updated"]
        error_count += note_result["errors"]

    return {
        "status": "ok",
        "processed": processed_count,
        "updated": updated_count,
        "skipped": skipped_count,
        "ipa_updated": ipa_updated_count,
        "definition_updated": definition_updated_count,
        "example_updated": example_updated_count,
        "audio_updated": audio_updated_count,
        "errors": error_count,
    }
