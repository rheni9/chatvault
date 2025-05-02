"""
Datetime parsing utilities.

This module provides tools to normalize date/time strings into
UTC ISO 8601 format using flexible input formats.
"""

from datetime import datetime, time, timezone as dt_timezone
from dateutil import parser as dateutil_parser
from dateutil.parser import isoparse
from pytz import timezone

DEFAULT_TZ = timezone("Europe/Kyiv")

WARNING_SIGN = "\u26A0\uFE0F"


def to_utc_iso(dt: datetime) -> str:
    """
    Convert a datetime object to UTC ISO 8601 format.

    :param dt: Datetime object
    :return: ISO-formatted UTC string
    """
    return dt.astimezone(dt_timezone.utc).isoformat().replace('+00:00', 'Z')


def parse_datetime(
    text: str,
    default_tz=DEFAULT_TZ,
    day_first: bool = True
) -> str | None:
    """
    Parse a datetime string and convert to ISO UTC format.

    :param text: Input string containing date and optional time
    :param default_tz: Timezone for naive datetime
    :param day_first: Whether the day comes before month in ambiguous dates
    :return: UTC ISO 8601 string or None on failure
    :rtype: str | None
    """
    text = text.strip()

    try:
        dt = isoparse(text)
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        return to_utc_iso(dt)
    except ValueError:
        # Not ISO format - fall back to flexible parsing
        pass

    try:
        dt = dateutil_parser.parse(text, dayfirst=day_first)

        if dt.time() == time(0, 0):
            return f"{dt.date().isoformat()}T00:00:00Z"

        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
        return to_utc_iso(dt)

    except ValueError as e:
        print(f"{WARNING_SIGN}  Failed to convert - {e}")
        return None
