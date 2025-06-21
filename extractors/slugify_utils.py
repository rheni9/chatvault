"""
Slug and transliteration utilities (Arcanum App).

Provides tools for transliterating Cyrillic text and generating
URL- and filename-safe slugs. Used for chat identifiers and file naming.
"""

import re
import unicodedata
import hashlib

# === Cyrillic to Latin transliteration map ===
CYR_TO_LAT = {
    "а": "a",
    "б": "b",
    "в": "v",
    "г": "h",
    "ґ": "g",
    "д": "d",
    "е": "e",
    "є": "ie",
    "ж": "zh",
    "з": "z",
    "и": "y",
    "і": "i",
    "ї": "i",
    "й": "y",
    "к": "k",
    "л": "l",
    "м": "m",
    "н": "n",
    "о": "o",
    "п": "p",
    "р": "r",
    "с": "s",
    "т": "t",
    "у": "u",
    "ф": "f",
    "х": "kh",
    "ц": "ts",
    "ч": "ch",
    "ш": "sh",
    "щ": "shch",
    "ь": "",
    "ю": "iu",
    "я": "ia"
}


def transliterate(text: str) -> str:
    """
    Transliterate a Cyrillic string into lowercase Latin characters.

    Non-Cyrillic characters remain unchanged. Used as a preprocessing
    step for slug generation.

    :param text: Input string to transliterate.
    :return: Transliterated string in lowercase.
    """
    return ''.join(CYR_TO_LAT.get(char, char) for char in text.lower())


def slugify(text: str, max_words: int = 3) -> str:
    """
    Convert an input string into a filesystem- and URL-safe slug.

    Applies Unicode normalization, transliteration, character filtering,
    and word limiting. Falls back to a hash-based slug if the result
    is empty or non-alphanumeric.

    :param text: Input string to slugify.
    :param max_words: Maximum number of words to include in the slug.
    :return: Slugified string (e.g., 'chat_name' or 'chat_ab12ef').
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
