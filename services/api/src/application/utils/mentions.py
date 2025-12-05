"""Utilities for parsing @mentions in text."""

import re


def parse_mentions(text: str) -> set[str]:
    """Parse @mentions from text.

    Extracts usernames mentioned in the format @username.

    Args:
        text: Text to parse

    Returns:
        Set of unique usernames (without @ symbol)
    """
    # Pattern to match @username (alphanumeric, underscore, hyphen, dot)
    # Username must start with alphanumeric or underscore
    pattern = r"@([a-zA-Z0-9_][a-zA-Z0-9_.-]*)"

    matches = re.findall(pattern, text)
    return set(matches)

