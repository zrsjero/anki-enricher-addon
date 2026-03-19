"""Anki note access helpers and field-level utilities."""

from aqt import mw

from .config_service import get_note_type_name, get_field_names


FIELD_KEY_ENGLISH = "english"
FIELD_KEY_RUSSIAN = "russian"
FIELD_KEY_IPA = "ipa"
FIELD_KEY_DEFINITION = "definition"
FIELD_KEY_EXAMPLE = "example"
FIELD_KEY_ENGLISH_AUDIO = "english_audio"
ENRICHED_TAG_NAME = "enriched"

REQUIRED_FIELD_KEYS = [
    FIELD_KEY_ENGLISH,
    FIELD_KEY_RUSSIAN,
    FIELD_KEY_IPA,
    FIELD_KEY_DEFINITION,
    FIELD_KEY_EXAMPLE,
    FIELD_KEY_ENGLISH_AUDIO,
]

TARGET_FIELD_KEYS = [
    FIELD_KEY_IPA,
    FIELD_KEY_DEFINITION,
    FIELD_KEY_EXAMPLE,
    FIELD_KEY_ENGLISH_AUDIO,
]


def escape_search_value(value):
    """Escape value for Anki search query phrase."""
    return value.replace('"', '\\"')


def build_note_search_query(deck_name=None):
    """Build note search query by note type, optional deck, and missing enriched tag."""
    note_type_name = escape_search_value(get_note_type_name())
    query = f'note:"{note_type_name}"'

    if deck_name:
        escaped_deck_name = escape_search_value(deck_name)
        query += f' deck:"{escaped_deck_name}"'

    query += f' -tag:{ENRICHED_TAG_NAME}'

    return query


def get_note_ids(deck_name=None):
    """Return note IDs for configured note type and optional deck."""
    query = build_note_search_query(deck_name=deck_name)
    return mw.col.find_notes(query)


def get_deck_names():
    """Return sorted deck names from collection."""
    decks = mw.col.decks

    if hasattr(decks, "all_names"):
        names = decks.all_names()
        return sorted([name for name in names if isinstance(name, str)])

    if hasattr(decks, "all_names_and_ids"):
        names_and_ids = decks.all_names_and_ids()
        names = []

        if isinstance(names_and_ids, dict):
            for key, value in names_and_ids.items():
                if isinstance(key, str):
                    names.append(key)
                elif isinstance(value, str):
                    names.append(value)
                elif hasattr(value, "name") and isinstance(value.name, str):
                    names.append(value.name)
        elif isinstance(names_and_ids, list):
            for item in names_and_ids:
                if isinstance(item, str):
                    names.append(item)
                elif isinstance(item, tuple) and item:
                    possible_name = item[0]
                    if isinstance(possible_name, str):
                        names.append(possible_name)
                elif hasattr(item, "name") and isinstance(item.name, str):
                    names.append(item.name)

        return sorted(list(set(names)))

    return []


def get_last_active_deck_name():
    """Return current/last active deck name from Anki, if available."""
    decks = mw.col.decks

    selected_deck_id = None

    if hasattr(decks, "selected"):
        try:
            selected_value = decks.selected()
            selected_deck_id = int(selected_value)
        except (TypeError, ValueError):
            selected_deck_id = None

    if selected_deck_id:
        if hasattr(decks, "name"):
            try:
                selected_name = decks.name(selected_deck_id)
                if isinstance(selected_name, str) and selected_name:
                    return selected_name
            except Exception:
                pass

        if hasattr(decks, "get"):
            try:
                selected_deck = decks.get(selected_deck_id)
                if isinstance(selected_deck, dict):
                    selected_name = selected_deck.get("name")
                    if isinstance(selected_name, str) and selected_name:
                        return selected_name
            except Exception:
                pass

    if hasattr(decks, "current"):
        try:
            current_deck = decks.current()
            if isinstance(current_deck, dict):
                current_name = current_deck.get("name")
                if isinstance(current_name, str) and current_name:
                    return current_name
        except Exception:
            pass

    return None


def get_note(note_id):
    """Load a note object by ID."""
    return mw.col.get_note(note_id)


def get_note_field_names(note):
    """Return all field names available on a note."""
    return list(note.keys())


def get_required_field_names():
    """Return field names that must exist in the note model."""
    field_names = get_field_names()
    return [field_names[field_key] for field_key in REQUIRED_FIELD_KEYS]


def get_target_field_names():
    """Return field names that may be populated by enrichment."""
    field_names = get_field_names()
    return [field_names[field_key] for field_key in TARGET_FIELD_KEYS]


def get_missing_required_fields(note):
    """Return required fields that are absent on the given note."""
    existing_field_names = get_note_field_names(note)
    required_field_names = get_required_field_names()

    missing_fields = []

    for field_name in required_field_names:
        if field_name not in existing_field_names:
            missing_fields.append(field_name)

    return missing_fields


def get_field_value(note, field_name):
    """Return trimmed text value for a specific note field."""
    return note[field_name].strip()


def set_field_value(note, field_name, value):
    """Set value for a specific note field."""
    note[field_name] = value


def save_note(note):
    """Persist note changes to collection database."""
    note.flush()


def get_empty_target_fields(note):
    """Return target fields that are currently empty."""
    empty_fields = []

    for field_name in get_target_field_names():
        field_value = get_field_value(note, field_name)

        if not field_value:
            empty_fields.append(field_name)

    return empty_fields


def get_enriched_tag_name():
    """Return tag name that marks completed enrichment."""
    return ENRICHED_TAG_NAME


def note_has_tag(note, tag_name):
    """Return whether note has a tag, tolerant to Anki API variants."""
    normalized_tag = (tag_name or "").strip()
    if not normalized_tag:
        return False

    if hasattr(note, "has_tag"):
        try:
            return bool(note.has_tag(normalized_tag))
        except Exception:
            pass

    if hasattr(note, "hasTag"):
        try:
            return bool(note.hasTag(normalized_tag))
        except Exception:
            pass

    tags = getattr(note, "tags", None)
    if isinstance(tags, list):
        normalized_lower = normalized_tag.lower()
        return any(
            isinstance(existing_tag, str)
            and existing_tag.strip().lower() == normalized_lower
            for existing_tag in tags
        )

    if isinstance(tags, str):
        normalized_lower = normalized_tag.lower()
        return any(
            tag_part.strip().lower() == normalized_lower
            for tag_part in tags.split()
            if tag_part.strip()
        )

    return False


def add_tag_to_note(note, tag_name):
    """Add tag to a note if missing. Return True only when tag was added."""
    normalized_tag = (tag_name or "").strip()
    if not normalized_tag or note_has_tag(note, normalized_tag):
        return False

    if hasattr(note, "add_tag"):
        try:
            note.add_tag(normalized_tag)
            return True
        except Exception:
            pass

    if hasattr(note, "addTag"):
        try:
            note.addTag(normalized_tag)
            return True
        except Exception:
            pass

    tags = getattr(note, "tags", None)
    if isinstance(tags, list):
        tags.append(normalized_tag)
        return True

    if isinstance(tags, str):
        note.tags = f"{tags} {normalized_tag}".strip()
        return True

    return False
