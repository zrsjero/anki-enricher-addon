from .config_service import get_example_count


def normalize_word(word):
    return word.strip()


def get_examples_for_word(word):
    normalized_word = normalize_word(word)

    if not normalized_word:
        return []

    all_examples = [
        f"This is {normalized_word}.",
        f"I can see {normalized_word}.",
        f"I like {normalized_word}.",
    ]

    example_count = get_example_count()
    return all_examples[:example_count]


def format_examples(examples):
    return "\n".join(examples)