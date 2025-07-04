import datetime
import re
from typing import Optional

from app.constants import CYRILLIC_TO_LATIN


class RegexStringCleaner:
    def __init__(self, fill: str = '_'):
        self.fill = fill
        self.pattern = rf'[\W{re.escape(fill)}]+'

    def clean(self, text: str) -> str:
        parts = [
            part for part in re.split(self.pattern, text.strip()) if part
        ]
        return self.fill.join(parts).strip(self.fill)


def clean_string(text: str, fill: str = '_', pattern: str = None) -> str:
    if pattern is None:
        # Escape fill in case it's a special character like "." or "+"
        escaped_fill = re.escape(fill)
        pattern = rf'[\W{escaped_fill}]+'

    parts = [part for part in re.split(pattern, text.strip()) if part]
    return fill.join(parts).strip(fill)


def transliterate_to_latin(
    word: str, mapping: dict[str, str] = CYRILLIC_TO_LATIN
) -> str:
    return ''.join(mapping.get(char.lower(), char) for char in word)


def parse_date(text: str) -> datetime.datetime:
    formats = [
        (r'(\D+) (\d{2})\, (\d{4})', '%b %d, %Y'),
        (r'(\D+), (\d{2})\ (\d{4})', '%b, %d %Y'),
        (r'(\d{2})\ (\D+), (\d{4})', '%d %B, %Y'),
        (r'(\d{2}) (\D+) (\d{4})', '%d %B %Y')
    ]

    for pattern, format in formats:
        match = re.search(pattern, text)
        if match:
            return datetime.datetime.strptime(match.group(), format)


def regex_trim(value: str, pattern: str, group_name: str) -> Optional[str]:
    """Generic function to apply regex and extract the named group."""
    if isinstance(value, str):
        match = re.search(pattern, value)
        if match:
            return match.group(group_name)
    return value


def regex_trim_country(value: str) -> Optional[str]:
    pattern = (
        r'One Or \w+\s+Safe\s+Port(?:\s+S|s)?\s+'
        r'(?P<country>.+)$'
    )
    return regex_trim(value, pattern, 'country')


def regex_trim_entity(value: str) -> Optional[str]:
    return regex_trim(value, r'To The Order Of (?P<entity>.*)', 'entity')


def regex_trim_for_orders(value: str) -> Optional[str]:
    return regex_trim(value, r'(?P<country>.*) For Orders', 'country')
