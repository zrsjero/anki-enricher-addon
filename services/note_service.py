from aqt import mw


REQUIRED_FIELDS = ["English", "Russian", "IPA", "Example", "EnglishAudio"]
TARGET_FIELDS = ["IPA", "Example", "EnglishAudio"]


def get_note_ids():
    query = 'note:"JeEng"'
    return mw.col.find_notes(query)


def get_note(note_id):
    return mw.col.get_note(note_id)


def get_note_field_names(note):
    return list(note.keys())


def get_missing_required_fields(note):
    field_names = get_note_field_names(note)
    missing_fields = []

    for field_name in REQUIRED_FIELDS:
        if field_name not in field_names:
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

    for field_name in TARGET_FIELDS:
        field_value = get_field_value(note, field_name)

        if not field_value:
            empty_fields.append(field_name)

    return empty_fields