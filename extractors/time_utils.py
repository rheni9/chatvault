"""
Datetime parsing utilities (Arcanum App).

Provides functions for flexible parsing and normalization
of date/time strings into UTC ISO 8601 format.
"""

import logging
from datetime import datetime, timezone as dt_timezone
from dateutil import parser as dateutil_parser
from dateutil.parser import isoparse
from pytz import timezone

# === Configuration ===
DEFAULT_TZ = timezone("Europe/Kyiv")

# === Logging ===
logger = logging.getLogger(__name__)


def to_utc_iso(dt: datetime) -> str:
    """
    Convert a datetime object to UTC ISO 8601 format.

    :param dt: Datetime object
    :return: ISO-formatted UTC string
    """
    return dt.astimezone(dt_timezone.utc).isoformat().replace("+00:00", "Z")


def parse_datetime(text: str,
                   default_tz=DEFAULT_TZ,
                   day_first: bool = True,
                   return_date_only: bool = False) -> str | None:
    """
    Parse a datetime string and optionally return only the date part.

    Handles both ISO and flexible human-readable formats. Applies
    default timezone to naive datetimes.

    :param text: Input string with date and optional time.
    :param default_tz: Timezone to apply to naive datetimes.
    :param day_first: Whether to treat ambiguous dates as DD/MM.
    :param return_date_only: Whether to return only 'YYYY-MM-DD'.
    :return: UTC ISO string, or date-only string, or None on error.
    """
    text = text.strip()

    try:
        dt = isoparse(text)
        if dt.tzinfo is None:
            dt = default_tz.localize(dt)
    except ValueError:
        try:
            dt = dateutil_parser.parse(text, dayfirst=day_first)
            if dt.tzinfo is None:
                dt = default_tz.localize(dt)
        except ValueError as e:
            logger.error("[TIME|ERROR] Failed to parse datetime: %s", e)
            return None

    if return_date_only:
        return dt.date().isoformat()

    return to_utc_iso(dt)
