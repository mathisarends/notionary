from datetime import datetime


def parse_date(date_str: str) -> str:
    supported_formats = _get_supported_date_formats()

    for date_format in supported_formats:
        parsed_date = _try_parse_date_with_format(date_str, date_format)
        if _date_was_successfully_parsed(parsed_date):
            return _convert_to_iso_format(parsed_date)

    _raise_invalid_date_format_error(date_str)


def _get_supported_date_formats() -> list[str]:
    return [
        "%Y-%m-%d",  # ISO: 2024-12-31
        "%d.%m.%Y",  # German: 31.12.2024
        "%m/%d/%Y",  # US with slash: 12/31/2024
        "%m-%d-%Y",  # US with dash: 12-31-2024
        "%d/%m/%Y",  # Day first with slash: 31/12/2024
        "%d-%m-%Y",  # Day first with dash: 31-12-2024
        "%d-%b-%Y",  # Short month: 31-Dec-2024
        "%d %b %Y",  # Short month with space: 31 Dec 2024
        "%d-%B-%Y",  # Full month: 31-December-2024
        "%d %B %Y",  # Full month with space: 31 December 2024
    ]


def _try_parse_date_with_format(date_str: str, date_format: str) -> datetime | None:
    try:
        return datetime.strptime(date_str, date_format)
    except ValueError:
        return None


def _date_was_successfully_parsed(parsed_date: datetime | None) -> bool:
    return parsed_date is not None


def _convert_to_iso_format(parsed_date: datetime) -> str:
    return parsed_date.strftime("%Y-%m-%d")


def _raise_invalid_date_format_error(date_str: str) -> None:
    error_message = (
        f"Invalid date format: '{date_str}'. "
        f"Supported formats: YYYY-MM-DD, DD.MM.YYYY, MM/DD/YYYY, DD/MM/YYYY, "
        f"DD-Mon-YYYY, DD Month YYYY"
    )
    raise ValueError(error_message)
