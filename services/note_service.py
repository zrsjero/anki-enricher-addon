from aqt import mw

from .config_service import get_note_type_name, get_field_names


FIELD_KEY_ENGLISH = "english"
FIELD_KEY_RUSSIAN = "russian"
FIELD_KEY_IPA = "ipa"
FIELD_KEY_EXAMPLE = "example"
FIELD_KEY_ENGLISH_AUDIO = "english_audio"

REQUIRED_FIELD_KEYS = [
    FIELD_KEY_ENGLISH,
    FIELD_KEY_RUSSIAN,
    FIELD_KEY_IPA,
    FIELD_KEY_EXAMPLE,
    FIELD_KEY_ENGLISH_AUDIO,
]

TARGET_FIELD_KEYS = [
    FIELD_KEY_IPA,
    FIELD_KEY_EXAMPLE,
    FIELD_KEY_ENGLISH_AUDIO,
]


def get_note_ids():
    note_type_name = get_note_type_name()
    query = f'note:"{note_type_name}"'
    return mw.col.find_notes(query)


def get_note(note_id):
    return mw.col.get_note(note_id)


def get_note_field_names(note):
    return list(note.keys())


def get_required_field_names():
    field_names = get_field_names()
    return [field_names[field_key] for field_key in REQUIRED_FIELD_KEYS]


def get_target_field_names():
    field_names = get_field_names()
    return [field_names[field_key] for field_key in TARGET_FIELD_KEYS]


def get_missing_required_fields(note):
    existing_field_names = get_note_field_names(note)
    required_field_names = get_required_field_names()

    missing_fields = []

    for field_name in required_field_names:
        if field_name not in existing_field_names:
            missing_fields.append(field_name)

    return missing_fields


def get_field_value(note, field_name):
    return note[field_name].strip()


def set_field_value(note, field_name, value):
    note[field_name] = value


def save_note(note):
    note.flush()


def get_empty_target_fields(note):
    empty_fields = []

    for field_name in get_target_field_names():
        field_value = get_field_value(note, field_name)

        if not field_value:
            empty_fields.append(field_name)

    return empty_fields