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
- Run options dialog includes deck selection + text provider selection.

### 2.2 UI behavior

- Deck combo includes `[All decks]` and all deck names.
- Default selected deck is current/last active deck when available.
- If active deck cannot be resolved, default remains `[All decks]`.
- Text provider combo options come from provider registry (`providers/text_provider_registry.py`).
- Current provider list contains one option: `Ollama (local)`.

### 2.3 Data providers

- `providers/dictionary_api_provider.py`: Free Dictionary API client (IPA source).
- `providers/ollama_provider.py`: local Ollama client (definition/examples).
- `providers/macos_say_audio_provider.py`: AIFF audio generation via `say`.
- `providers/text_provider_registry.py`: registry for definition/example providers.

### 2.4 Domain services

- `services/ipa_service.py`: dictionary-only IPA extraction/normalization.
- `services/definition_service.py`: definition generation via selected text provider.
- `services/example_service.py`: example generation via selected text provider.
- `services/source_fields_case_service.py`: optional lowercase normalization of source fields.
- `services/audio_service.py`: deterministic filename and backend routing.
- `services/media_service.py`: media path and file writes.
- `services/note_service.py`: note/deck operations.
- `services/config_service.py`: config access.

---

## 3. Confirmed Architectural Decisions

1. Keep architecture lightweight and functional (service/provider split).
2. Keep config access simple (no schema validation layer yet).
3. Do not reintroduce cache layer yet.
4. IPA source is dictionary API only.
5. Definition/example source is text provider (currently Ollama).
6. Text generation selection is provider-based (extensible registry), not dictionary-vs-ollama branching.
7. Audio backend remains `macos_say`.

---

## 4. Important Decision History

### 4.1 Audio

- Earlier `gTTS` approach failed in Anki runtime (`ModuleNotFoundError: gtts`).
- Current production approach: macOS native `say`, output `.aiff` bytes.

### 4.2 IPA via Ollama experiment (rolled back)

- IPA Ollama fallback was implemented experimentally.
- Real outputs were inconsistent/incorrect for some words.
- Decision: remove IPA Ollama path and keep dictionary-only IPA.

### 4.3 Definition/example simplification

- Earlier logic had dictionary + Ollama branching for definition/examples.
- Current logic uses only selected text provider pipeline.
- This reduced branching in services and made provider extension simpler.

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
  "text_provider": "ollama",
  "text_provider_max_attempts_per_word": 2,
  "normalize_source_first_char_lowercase": true,
  "ollama": {
    "enabled": true,
    "base_url": "http://127.0.0.1:11434",
    "model": "qwen2.5:3b-instruct",
    "timeout_seconds": 25,
    "temperature": 0.6
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
    text_provider_registry.py
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

`process_note(note, text_provider_key=None)`:
1. Reads configured field names.
2. Skips note if `English` is empty.
3. Skips note if no target fields are empty.
4. Optionally normalizes first char of `English` and `Russian` to lowercase.
5. Tries to fill each empty target field:
   - `IPA`: dictionary API only.
   - `Definition`: selected text provider.
   - `Example`: selected text provider.
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

## 8. Provider Extension Model

Definition/example generation uses a provider registry:
- file: `providers/text_provider_registry.py`
- each provider config contains:
  - `label`
  - `generate_definition(word)` callable
  - `generate_examples(word, count)` callable

Current providers:
- `ollama`

To add another LLM provider:
1. Create `providers/<new_provider>.py` with generation functions.
2. Register provider in `TEXT_PROVIDER_REGISTRY`.
3. Set `text_provider` in config or choose it in UI.

Most service logic remains unchanged.

---

## 9. Logging and Diagnostics

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

## 10. Open Risks / Known Gaps

1. No formal config schema validation.
2. No automated tests yet.
3. Audio format is AIFF (larger files).
4. Dictionary API can have missing/limited IPA data for rare words.
5. Definition/example quality depends on selected provider/model.

---

## 11. Suggested Next Iteration

1. Add unit tests for:
- result aggregation (`failed_word_details`),
- example cleanup helpers,
- definition/example quality filters,
- provider registry resolution.

2. Add optional config validation with clear startup diagnostics.

3. Add at least one more text provider in registry.

---

## 12. Continuation Prompt Template

Use this prompt in a new chat:

```text
Continue work on the Anki English Enricher add-on using anki_addon_full_context_2026-03-14_v2.md.
Keep the current service/provider architecture and proceed in small safe iterations.
IPA must stay dictionary-only. Definition/example must use text provider registry.
```

---

## 13. Source-of-truth Rule

- This context file captures decisions and current behavior.
- Exact implementation details must always be verified against repository code.
