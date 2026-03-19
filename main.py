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

from .providers.text_provider_registry import get_available_text_providers
from .services.config_service import get_text_provider
from .services.enrich_service import enrich_notes
from .services.note_service import get_deck_names, get_last_active_deck_name

ALL_DECKS_OPTION = "[All decks]"


def ask_user_for_run_options():
    """Show one dialog for deck and text source selection."""
    deck_names = get_deck_names()
    last_active_deck_name = get_last_active_deck_name()
    text_provider_options = get_available_text_providers()
    default_text_provider = get_text_provider()

    dialog = QDialog(mw)
    dialog.setWindowTitle("English Note Enricher")

    layout = QVBoxLayout(dialog)
    form_layout = QFormLayout()

    deck_combo = QComboBox(dialog)
    deck_combo.addItem(ALL_DECKS_OPTION)
    for deck_name in deck_names:
        deck_combo.addItem(deck_name)

    if last_active_deck_name and last_active_deck_name in deck_names:
        default_index = deck_names.index(last_active_deck_name) + 1
        deck_combo.setCurrentIndex(default_index)

    form_layout.addRow("Deck to enrich:", deck_combo)

    source_combo = QComboBox(dialog)
    for provider_key, provider_label in text_provider_options:
        source_combo.addItem(provider_label, provider_key)

    default_provider_index = 0
    for index, (provider_key, _) in enumerate(text_provider_options):
        if provider_key == default_text_provider:
            default_provider_index = index
            break
    source_combo.setCurrentIndex(default_provider_index)

    form_layout.addRow(
        "Provider for definitions/examples:",
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
    selected_text_provider = source_combo.currentData()
    if not isinstance(selected_text_provider, str):
        selected_text_provider = default_text_provider

    if selected_deck_name == ALL_DECKS_OPTION:
        selected_deck_name = None

    return selected_deck_name, selected_text_provider


def on_menu_click() -> None:
    """Run note enrichment and show a human-readable summary dialog."""
    run_options = ask_user_for_run_options()

    if run_options == "__cancelled__":
        return

    selected_deck_name, selected_text_provider = run_options

    result = enrich_notes(
        deck_name=selected_deck_name,
        text_provider_key=selected_text_provider,
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

    failed_word_details = result.get("failed_word_details", {})
    if failed_word_details:
        failed_lines = []
        for index, (word, fields) in enumerate(failed_word_details.items(), start=1):
            failed_lines.append(f"{index}) {word} [{', '.join(fields)}]")
        failed_words_text = "\n".join(failed_lines)
    else:
        failed_words_text = "None"

    showInfo(
        f"Processed: {result['processed']}\n"
        f"Updated: {result['updated']}\n"
        f"Skipped: {result['skipped']}\n"
        f"IPA updated: {result['ipa_updated']}\n"
        f"Definition updated: {result['definition_updated']}\n"
        f"Examples updated: {result['example_updated']}\n"
        f"Audio updated: {result['audio_updated']}\n"
        f"Errors: {result['errors']}\n\n"
        f"Failed words:\n{failed_words_text}"
    )


def init_addon() -> None:
    """Register the add-on action in Anki Tools menu."""
    action = QAction("English Note Enricher", mw)
    action.triggered.connect(on_menu_click)
    mw.form.menuTools.addAction(action)


init_addon()
