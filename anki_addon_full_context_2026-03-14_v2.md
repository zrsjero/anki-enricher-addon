# Anki English Enricher Add-on — Full Transfer Context (v2)

Last updated: **March 14, 2026**
Repository path: `anki_enricher_addon/`

This document is intended to continue development in a new chat with minimal context loss.

---

## 1. Project Goal

Build a practical Anki add-on that enriches vocabulary notes for one configured note type.

Expected note fields:
- `English`
- `Russian`
- `IPA`
- `Example`
- `EnglishAudio`

Main workflow:
1. User clicks menu action in Anki.
2. Add-on finds notes for configured note type.
3. Add-on validates required fields exist on note model.
4. For each note, add-on fills only empty target fields.
5. Add-on saves note/media and shows summary stats.

---

## 2. Current Implementation Snapshot

### 2.1 Entry and orchestration

- `main.py` registers `Tools -> English Note Enricher`.
- `services/enrich_service.py` drives full enrichment flow.

### 2.2 Data providers

- `providers/dictionary_api_provider.py` calls Free Dictionary API.
- `providers/macos_say_audio_provider.py` generates AIFF bytes using macOS `say`.

### 2.3 Domain services

- `services/ipa_service.py` extracts and normalizes IPA.
- `services/example_service.py` extracts examples and formats with newlines.
- `services/audio_service.py` builds deterministic filenames and delegates audio generation to configured backend.
- `services/media_service.py` writes files to Anki media directory.
- `services/note_service.py` handles Anki notes/fields.
- `services/config_service.py` reads addon config keys.

---

## 3. Confirmed Architectural Decisions

1. Keep architecture lightweight and functional (service/provider split).
2. Do not add config validation yet.
3. Do not reintroduce cache yet.
4. Use Free Dictionary API for IPA and examples.
5. Use `macOS say` for audio backend (no `gTTS` dependency).
6. Keep audio backend switchable through config key.

---

## 4. Audio Decision History

- Earlier attempt with `gTTS` failed in Anki runtime: missing module (`ModuleNotFoundError: gtts`).
- Current solution uses native macOS `say` command.
- Provider produces temporary `.aiff`, reads bytes, then cleans temp file.
- Final media filename extension for current backend is `.aiff`.

---

## 5. Current Config (source of truth)

`config.json`:

```json
{
  "note_type_name": "JeEng",
  "fields": {
    "english": "English",
    "russian": "Russian",
    "ipa": "IPA",
    "example": "Example",
    "english_audio": "EnglishAudio"
  },
  "example_count": 3,
  "audio_prefix": "jeeng",
  "audio_backend": "macos_say"
}
```

---

## 6. Current Project Tree

```text
anki_enricher_addon/
  __init__.py
  main.py
  manifest.json
  config.json
  README.md
  anki_addon_full_context_2026-03-14.md
  anki_addon_full_context_2026-03-14_v2.md

  providers/
    __init__.py
    dictionary_api_provider.py
    macos_say_audio_provider.py

  services/
    audio_service.py
    config_service.py
    enrich_service.py
    example_service.py
    ipa_service.py
    media_service.py
    note_service.py
```

---

## 7. Development Progress (latest iteration)

Completed in this iteration (March 14, 2026):

1. Audio pipeline finalized for current backend:
- replaced test audio stub with real `generate_audio_data(...)` flow;
- added backend-aware audio extension (`aiff` for `macos_say`);
- integrated provider output bytes into media writing pipeline.

2. API client hardening:
- added `requests.RequestException` handling;
- added JSON decode failure handling;
- returns empty list on invalid responses.

3. Documentation pass (English):
- module docstrings added across all Python modules;
- function docstrings added for all core and helper functions.

4. Repository documentation:
- added detailed `README.md` with architecture, config, usage, troubleshooting, roadmap.

---

## 8. Behavior Details

### 8.1 Note processing

`process_note(note)` does:
1. Reads configured field names.
2. Skips note if `English` is empty.
3. Determines empty target fields (`IPA`, `Example`, `EnglishAudio`).
4. Fills each empty field if data was generated/fetched successfully.
5. Flushes note only if at least one target field was updated.
6. Returns per-note counters and error count.

### 8.2 Enrichment run result

`enrich_notes()` returns status dict with:
- `status`: `ok | no_notes | missing_fields`
- `processed`, `updated`, `skipped`
- `ipa_updated`, `example_updated`, `audio_updated`
- `errors`

### 8.3 Audio file naming

Pattern: `<audio_prefix>_<sanitized_word>.<extension>`

Examples:
- `jeeng_ice_cream.aiff`
- `jeeng_take_off.aiff`

`EnglishAudio` value format:
- `[sound:jeeng_ice_cream.aiff]`

---

## 9. Open Risks / Known Gaps

1. No formal config validation (intentional for now).
2. No retries/backoff for HTTP layer.
3. Current audio format is AIFF (larger files than compressed formats).
4. Logging in `example_service.py` and `media_service.py` is basic.
5. No automated tests yet.

---

## 10. Suggested Next Iteration

1. Add optional second audio backend while preserving current interface.
2. Add small unit tests for pure helper logic:
- IPA normalization;
- example extraction and dedupe;
- filename sanitization.
3. Add lightweight result diagnostics (why field update failed).
4. Consider optional conversion pipeline from AIFF to compressed format only if needed.

---

## 11. Continuation Prompt Template

Use this prompt in a new chat:

```text
Continue work on the Anki English Enricher add-on using anki_addon_full_context_2026-03-14_v2.md.
Keep the current service/provider architecture and proceed in small safe iterations.
Current production audio backend is macos_say and it already works end-to-end.
```

---

## 12. Source-of-truth Rule

- This context file explains decisions and state.
- Exact current code must always be read from repository files.

