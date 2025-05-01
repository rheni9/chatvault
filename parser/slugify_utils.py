"""
Provides utilities for transliterating Cyrillic text and generating
URL- or filename-safe slugs from arbitrary input.
"""

import re
import unicodedata
import hashlib

# Cyrillic to Latin transliteration mapping
CYR_TO_LAT = {
    "а": "a", "б": "b", "в": "v", "г": "h", "ґ": "g", "д": "d", "е": "e",
    "є": "ie", "ж": "zh", "з": "z", "и": "y", "і": "i", "ї": "i", "й": "y",
    "к": "k", "л": "l", "м": "m", "н": "n", "о": "o", "п": "p", "р": "r",
    "с": "s", "т": "t", "у": "u", "ф": "f", "х": "kh", "ц": "ts", "ч": "ch",
    "ш": "sh", "щ": "shch", "ь": "", "ю": "iu", "я": "ia"
}


def transliterate(text: str) -> str:
    """
    Transliterate a Cyrillic string into Latin characters.

    :param text: Input string to transliterate
    :type text: str
    :return: Transliterated lowercase Latin string
    :rtype: str
    """
    return ''.join(CYR_TO_LAT.get(char, char) for char in text.lower())


def slugify(text: str, max_words: int = 3) -> str:
    """
    Convert a string into a slug suitable for filenames or identifiers.

    This includes transliteration, normalization, stripping special characters,
    word limiting, and a hash-based fallback if needed.

    :param text: Input string to convert
    :type text: str
    :param max_words: Maximum number of words to include in the slug
    :type max_words: int
    :return: Generated slug (e.g., "chat_name" or "chat_ab12ef")
    :rtype: str
    """
    original_text = str(text) if text is not None else ""
    text = unicodedata.normalize("NFKD", original_text)
    text = transliterate(text)
    text = re.sub(r"[^a-z0-9 ]", "", text)
    words = text.strip().split()
    slug = "_".join(words[:max_words])

    if not slug or not any(char.isalnum() for char in slug):
        hash_part = hashlib.sha1(original_text.encode("utf-8")).hexdigest()[:6]
        return f"chat_{hash_part}"

    return slug
