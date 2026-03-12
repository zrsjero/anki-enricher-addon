def normalize_word(word):
    return word.strip()


def get_ipa_for_word(word):
    normalized_word = normalize_word(word)

    if not normalized_word:
        return None

    return f"/{normalized_word}/"
