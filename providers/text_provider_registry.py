"""Registry for text generation providers used by definition/example services."""

from .ollama_provider import (
    generate_definition_with_ollama,
    generate_examples_with_ollama,
)

TEXT_PROVIDER_OLLAMA = "ollama"

TEXT_PROVIDER_REGISTRY = {
    TEXT_PROVIDER_OLLAMA: {
        "label": "Ollama (local)",
        "generate_definition": generate_definition_with_ollama,
        "generate_examples": generate_examples_with_ollama,
    },
}


def get_available_text_providers():
    """Return ordered list of available text providers as (key, label)."""
    providers = []

    for provider_key, provider_config in TEXT_PROVIDER_REGISTRY.items():
        provider_label = provider_config.get("label")

        if isinstance(provider_label, str) and provider_label:
            providers.append((provider_key, provider_label))

    return providers


def resolve_text_provider(provider_key):
    """Return provider config for a key, or None if unknown."""
    return TEXT_PROVIDER_REGISTRY.get(provider_key)


def generate_definition_with_provider(word, provider_key):
    """Generate definition using the selected text provider."""
    provider = resolve_text_provider(provider_key)

    if not provider:
        return None

    generate_definition = provider.get("generate_definition")

    if not callable(generate_definition):
        return None

    return generate_definition(word)


def generate_examples_with_provider(word, count, provider_key):
    """Generate examples using the selected text provider."""
    provider = resolve_text_provider(provider_key)

    if not provider:
        return []

    generate_examples = provider.get("generate_examples")

    if not callable(generate_examples):
        return []

    return generate_examples(word, count)
