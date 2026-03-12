from aqt import mw
from aqt.qt import QAction
from aqt.utils import showInfo

from .services.enrich_service import enrich_notes


def on_menu_click() -> None:
    result = enrich_notes()

    if result["status"] == "no_notes":
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
        f"Example updated: {result['example_updated']}\n"
        f"Audio updated: {result['audio_updated']}\n"
        f"Errors: {result['errors']}"
    )


def init_addon() -> None:
    action = QAction("English Note Enricher", mw)
    action.triggered.connect(on_menu_click)
    mw.form.menuTools.addAction(action)


init_addon()