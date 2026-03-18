# Anki English Enricher Add-on — Full Transfer Context (v2)

Last updated: **March 18, 2026**
Repository path: `anki_enricher_addon/`

This document is intended to continue development in a new chat with minimal context loss.

---

## 1. Project Goal

Build a practical Anki add-on that enriches vocabulary notes for one configured note type.

Expected note fields:
- `English`
- `Russian`
- `IPA`
- `Definition`
- `Example`
- `EnglishAudio`

Main workflow:
1. User clicks menu action in Anki.
2. Add-on finds notes for configured note type.
3. Add-on validates required fields exist on note model.
4. For each note, add-on fills only empty target fields.
5. Add-on saves note/media and shows summary stats + diagnostics.

---

## 2. Current Implementation Snapshot

### 2.1 Entry and orchestration

- `main.py` registers `Tools -> English Note Enricher`.
- `services/enrich_service.py` runs enrichment flow and aggregates counters.
- Run options dialog includes deck + text backend selection.

### 2.2 UI behavior

- Deck combo includes `[All decks]` and all deck names.
- Default selected deck is current/last active deck when available.
- If active deck cannot be resolved, default remains `[All decks]`.
- Text source combo options:
  - `Ollama` (maps to `ollama_only`)
  - `dictionaryapi` (maps to `dictionary_then_ollama`)

### 2.3 Data providers

- `providers/dictionary_api_provider.py`: Free Dictionary API client.
- `providers/ollama_provider.py`: local Ollama client for definition/examples only.
- `providers/macos_say_audio_provider.py`: AIFF audio generation via `say`.

### 2.4 Domain services

- `services/ipa_service.py`: dictionary-only IPA extraction/normalization.
- `services/definition_service.py`: dictionary + optional Ollama fallback.
- `services/example_service.py`: dictionary + optional Ollama fallback.
- `services/source_fields_case_service.py`: optional lowercase normalization of source fields.
- `services/audio_service.py`: deterministic filename and backend routing.
- `services/media_service.py`: media path and file writes.
- `services/note_service.py`: note/deck operations.
- `services/config_service.py`: config access.

---

## 3. Confirmed Architectural Decisions

1. Keep architecture lightweight and functional (service/provider split).
2. Keep config access simple (no separate schema validation layer yet).
3. Do not reintroduce cache layer yet.
4. IPA source is dictionary API only.
5. Definition/example can use dictionary or Ollama mode.
6. Audio backend remains `macos_say`.

---

## 4. Important Decision History

### 4.1 Audio

- Earlier `gTTS` approach failed in Anki runtime (`ModuleNotFoundError: gtts`).
- Current production approach: macOS native `say`, output `.aiff` bytes.

### 4.2 IPA via Ollama experiment (rolled back)

- IPA Ollama fallback was implemented experimentally.
- Real outputs were inconsistent/incorrect for some words.
- Decision: remove IPA Ollama path and keep dictionary-only IPA.

---

## 5. Current Config (source of truth)

`config.json` currently:

```json
{
  "note_type_name": "JeEng",
  "fields": {
    "english": "English",
    "russian": "Russian",
    "ipa": "IPA",
    "definition": "Definition",
    "example": "Example",
    "english_audio": "EnglishAudio"
  },
  "example_count": 2,
  "definition_backend": "dictionary_then_ollama",
  "example_backend": "dictionary_then_ollama",
  "normalize_source_first_char_lowercase": true,
  "ollama": {
    "enabled": true,
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen2.5:3b-instruct",
    "timeout_seconds": 25,
    "temperature": 0.6,
    "max_attempts_per_word": 3
  },
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
  anki_addon_full_context_2026-03-14_v2.md

  providers/
    __init__.py
    dictionary_api_provider.py
    ollama_provider.py
    macos_say_audio_provider.py

  services/
    audio_service.py
    config_service.py
    definition_service.py
    enrich_service.py
    example_service.py
    ipa_service.py
    media_service.py
    note_service.py
    source_fields_case_service.py
```

---

## 7. Behavior Details

### 7.1 Note processing (`process_note`)

`process_note(note, text_backend_mode=None)`:
1. Reads configured field names.
2. Skips note if `English` is empty.
3. Skips note if no target fields are empty.
4. Optionally normalizes first char of `English` and `Russian` to lowercase (config-driven).
5. Tries to fill each empty target field:
   - `IPA`: dictionary only.
   - `Definition`: backend according to mode (`dictionary_then_ollama` or `ollama_only`).
   - `Example`: backend according to mode (`dictionary_then_ollama` or `ollama_only`).
   - `EnglishAudio`: deterministic filename + media write/check.
6. Increments `errors` and logs `warning` for each failed field fill.
7. Saves note only when at least one update was applied.
8. Returns per-note counters + failed field diagnostics.

### 7.2 Enrichment run result (`enrich_notes`)

Return shape:
- `status`: `ok | no_notes | missing_fields`
- `processed`, `updated`, `skipped`
- `ipa_updated`, `definition_updated`, `example_updated`, `audio_updated`
- `errors`
- `failed_word_details`: map `word -> [failed_field_keys]`

### 7.3 Summary popup

Popup includes counters and failed words section, e.g.:

```text
Processed: 8
Updated: 0
Skipped: 0
IPA updated: 0
Definition updated: 0
Example updated: 0
Audio updated: 0
Errors: 8

Failed words:
1) hesitantly [ipa]
2) umbilic [ipa, audio]
3) fraudster [example]
4) gawp [definition, audio]
```

### 7.4 Text cleanup rules

- `definition_service.clean_definition_text(...)`:
  - normalize whitespace;
  - uppercase first alphabetic character.

- `example_service.clean_example_text(...)`:
  - normalize whitespace/newlines;
  - remove standalone JSON-like lines/fragments;
  - remove trailing inline JSON-like payloads;
  - uppercase first alphabetic character.

- `example_service.format_examples(...)` stores examples with `<br>` separators.

### 7.5 Audio naming

Pattern: `<audio_prefix>_<sanitized_word>.<extension>`

Examples:
- `jeeng_ice_cream.aiff`
- `jeeng_take_off.aiff`

`EnglishAudio` field value:
- `[sound:jeeng_ice_cream.aiff]`

---

## 8. Logging and Diagnostics

- Field-level failures are logged in `services/enrich_service.py` via `logger.warning`.
- Log contains:
  - field name,
  - word,
  - note id,
  - reason.
- Additional info logs exist in `example_service.py` and `media_service.py`.

For console logs on macOS:
- `/Applications/Anki.app/Contents/MacOS/launcher`

---

## 9. Open Risks / Known Gaps

1. No formal config schema validation.
2. No automated tests yet.
3. Audio format is AIFF (larger files).
4. Dictionary API can have missing/limited data for rare words.
5. Ollama output quality depends on local model for definition/examples.

---

## 10. Suggested Next Iteration

1. Add unit tests for:
- result aggregation (`failed_word_details`),
- example cleanup helpers,
- definition/example first-letter normalization,
- filename sanitization.

2. Reduce debug-noise logs in `example_service.py` if needed.

3. Add optional config validation with user-friendly messages.

---

## 11. Continuation Prompt Template

Use this prompt in a new chat:

```text
Continue work on the Anki English Enricher add-on using anki_addon_full_context_2026-03-14_v2.md.
Keep the current service/provider architecture and proceed in small safe iterations.
IPA must stay dictionary-only; definition/example may use Ollama based on selected mode.
```

---

## 12. Source-of-truth Rule

- This context file captures decisions and current behavior.
- Exact implementation details must always be verified against repository code.
