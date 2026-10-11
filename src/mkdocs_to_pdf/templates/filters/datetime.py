"""Datetime Jinja2 filters."""

from datetime import date, datetime


def strptime(
    value: str,
    format: str,  # ruff: ignore[builtin-argument-shadowing]
) -> date:
    """
    Parse a date string using a format.

    Args:
        value: The date string.
        format: The strptime format.

    Returns:
        The parsed date.

    """
    return datetime.strptime(  # ruff: ignore[call-datetime-strptime-without-zone]
        value,
        format,
    )


def strftime(
    value: date,
    format: str,  # ruff: ignore[builtin-argument-shadowing]
) -> str:
    """
    Format a date using a format.

    Args:
        value: The date to format.
        format: The strftime format.

    Returns:
        The formatted date.

    """
    return value.strftime(format)
