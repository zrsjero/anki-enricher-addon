"""Anki add-on entrypoint and UI menu registration."""

from aqt import mw
from aqt.qt import QAction, QInputDialog
from aqt.utils import showInfo

from .services.enrich_service import enrich_notes
from .services.note_service import get_deck_names

ALL_DECKS_OPTION = "[All decks]"


def ask_user_for_deck_name():
    """Show deck picker dialog and return selected deck name or None."""
    deck_names = get_deck_names()

    if not deck_names:
        return None

    options = [ALL_DECKS_OPTION] + deck_names
    selected_option, is_ok = QInputDialog.getItem(
        mw,
        "English Note Enricher",
        "Choose deck to enrich:",
        options,
        0,
        False,
    )

    if not is_ok:
        return "__cancelled__"

    if selected_option == ALL_DECKS_OPTION:
        return None

    return selected_option


def on_menu_click() -> None:
    """Run note enrichment and show a human-readable summary dialog."""
    selected_deck_name = ask_user_for_deck_name()

    if selected_deck_name == "__cancelled__":
        return

    result = enrich_notes(deck_name=selected_deck_name)

    if result["status"] == "no_notes":
        if selected_deck_name:
            showInfo(f'Found notes in "{selected_deck_name}": 0')
        else:
            showInfo("Found notes: 0")
        return

    if result["status"] == "missing_fields":
        missing_fields_text = "\n".join(result["missing_fields"])
        showInfo(f"Missing required fields:\n{missing_fields_text}")
        return

    showInfo(
        f"Processed: {result['processed']}\n"
        f"Updated: {result['updated']}\n"
        f"Skipped: {result['skipped']}\n"
        f"IPA updated: {result['ipa_updated']}\n"
        f"Definition updated: {result['definition_updated']}\n"
        f"Example updated: {result['example_updated']}\n"
        f"Audio updated: {result['audio_updated']}\n"
        f"Errors: {result['errors']}"
    )


def init_addon() -> None:
    """Register the add-on action in Anki Tools menu."""
    action = QAction("English Note Enricher", mw)
    action.triggered.connect(on_menu_click)
    mw.form.menuTools.addAction(action)


init_addon()
