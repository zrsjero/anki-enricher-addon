"""Low-level client for local Ollama text generation."""

import json
from urllib.parse import urljoin

import requests

from ..services.config_service import (
    get_ollama_base_url,
    get_ollama_model,
    get_ollama_temperature,
    get_ollama_timeout_seconds,
    is_ollama_enabled,
)


def build_ollama_generate_url():
    """Build Ollama generate endpoint URL from config."""
    base_url = get_ollama_base_url().strip()

    if not base_url:
        return None

    normalized_base_url = base_url if base_url.endswith("/") else f"{base_url}/"
    return urljoin(normalized_base_url, "api/generate")


def build_prompt(word, count):
    """Build deterministic prompt for sentence generation."""
    return (
        "You are helping to create flashcards for English learners.\n"
        f"Generate exactly {count} short, natural English example sentences.\n"
        f"Target word: {word}\n"
        "Rules:\n"
        "- Each sentence must contain the target word exactly once.\n"
        "- Keep sentence length between 6 and 14 words.\n"
        "- Use CEFR A2-B1 vocabulary where possible.\n"
        "- Avoid proper names, idioms, and slang.\n"
        '- Return strict JSON only: {"examples":["...", "..."]}\n'
    )


def build_definition_prompt(word):
    """Build deterministic prompt for definition generation."""
    return (
        "You are helping to create flashcards for English learners.\n"
        f"Write one short English definition for the word: {word}\n"
        "Rules:\n"
        "- Keep it to one sentence.\n"
        "- Use simple CEFR A2-B1 vocabulary.\n"
        "- Do not use markdown.\n"
        '- Return strict JSON only: {"definition":"..."}\n'
    )


def parse_ollama_examples(response_text):
    """Extract examples list from Ollama textual response."""
    try:
        payload = json.loads(response_text)
    except ValueError:
        return []

    examples = payload.get("examples", [])

    if not isinstance(examples, list):
        return []

    valid_examples = []

    for item in examples:
        if isinstance(item, str):
            cleaned = item.strip()

            if cleaned:
                valid_examples.append(cleaned)

    return valid_examples


def parse_ollama_definition(response_text):
    """Extract single definition string from Ollama textual response."""
    try:
        payload = json.loads(response_text)
    except ValueError:
        return None

    definition = payload.get("definition")

    if not isinstance(definition, str):
        return None

    cleaned_definition = definition.strip()

    if not cleaned_definition:
        return None

    return cleaned_definition


def generate_examples_with_ollama(word, count):
    """Generate example sentences with local Ollama and return list."""
    if not is_ollama_enabled():
        return []

    if not word or count <= 0:
        return []

    url = build_ollama_generate_url()

    if not url:
        return []

    payload = {
        "model": get_ollama_model(),
        "prompt": build_prompt(word=word, count=count),
        "stream": False,
        "format": "json",
        "options": {
            "temperature": get_ollama_temperature(),
        },
    }

    timeout_seconds = get_ollama_timeout_seconds()

    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
    except requests.RequestException:
        return []

    if response.status_code != 200:
        return []

    try:
        data = response.json()
    except ValueError:
        return []

    raw_response = data.get("response")

    if not isinstance(raw_response, str):
        return []

    return parse_ollama_examples(raw_response)


def generate_definition_with_ollama(word):
    """Generate a single definition with local Ollama."""
    if not is_ollama_enabled():
        return None

    if not word:
        return None

    url = build_ollama_generate_url()

    if not url:
        return None

    payload = {
        "model": get_ollama_model(),
        "prompt": build_definition_prompt(word=word),
        "stream": False,
        "format": "json",
        "options": {
            "temperature": get_ollama_temperature(),
        },
    }

    timeout_seconds = get_ollama_timeout_seconds()

    try:
        response = requests.post(url, json=payload, timeout=timeout_seconds)
    except requests.RequestException:
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except ValueError:
        return None

    raw_response = data.get("response")

    if not isinstance(raw_response, str):
        return None

    return parse_ollama_definition(raw_response)
