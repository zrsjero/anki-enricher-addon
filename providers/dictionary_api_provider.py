from urllib.parse import quote

import requests

BASE_URL = "https://api.dictionaryapi.dev/api/v2/entries/en"


def normalize_word(word):
    return word.strip()


def build_dictionary_url(word):
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    encoded_word = quote(normalized_word)
    return f"{BASE_URL}/{encoded_word}"


def fetch_dictionary_entries(word):
    url = build_dictionary_url(word)

    if not url:
        return []

    try:
        response = requests.get(url, timeout=10)
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    if not isinstance(data, list):
        return []

    return data
