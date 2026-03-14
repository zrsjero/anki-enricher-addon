"""Anki add-on entrypoint and UI menu registration."""

from aqt import mw
from aqt.qt import (
    QAction,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QVBoxLayout,
)
from aqt.utils import showInfo

from .services.enrich_service import enrich_notes
from .services.note_service import get_deck_names

ALL_DECKS_OPTION = "[All decks]"
TEXT_SOURCE_DICTIONARY = "dictionaryapi"
TEXT_SOURCE_OLLAMA = "Ollama"


def ask_user_for_run_options():
    """Show one dialog for deck and text source selection."""
    deck_names = get_deck_names()

    dialog = QDialog(mw)
    dialog.setWindowTitle("English Note Enricher")

    layout = QVBoxLayout(dialog)
    form_layout = QFormLayout()

    deck_combo = QComboBox(dialog)
    deck_combo.addItem(ALL_DECKS_OPTION)
    for deck_name in deck_names:
        deck_combo.addItem(deck_name)
    form_layout.addRow("Deck to enrich:", deck_combo)

    source_combo = QComboBox(dialog)
    source_combo.addItem(TEXT_SOURCE_OLLAMA)
    source_combo.addItem(TEXT_SOURCE_DICTIONARY)
    form_layout.addRow(
        "Source for definitions/examples:",
        source_combo,
    )
    layout.addLayout(form_layout)

    button_box = QDialogButtonBox(
        QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
        dialog,
    )
    button_box.accepted.connect(dialog.accept)
    button_box.rejected.connect(dialog.reject)
    layout.addWidget(button_box)

    if dialog.exec() != QDialog.DialogCode.Accepted:
        return "__cancelled__"

    selected_deck_name = deck_combo.currentText()
    selected_source = source_combo.currentText()

    if selected_deck_name == ALL_DECKS_OPTION:
        selected_deck_name = None

    if selected_source == TEXT_SOURCE_OLLAMA:
        return selected_deck_name, "ollama_only"

    return selected_deck_name, "dictionary_then_ollama"


def on_menu_click() -> None:
    """Run note enrichment and show a human-readable summary dialog."""
    run_options = ask_user_for_run_options()

    if run_options == "__cancelled__":
        return

    selected_deck_name, selected_text_backend_mode = run_options

    result = enrich_notes(
        deck_name=selected_deck_name,
        text_backend_mode=selected_text_backend_mode,
    )

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
