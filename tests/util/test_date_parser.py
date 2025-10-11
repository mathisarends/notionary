import pytest

from notionary.utils.date import parse_date

type DateTestCase = tuple[str, str]
type DateTestCases = list[DateTestCase]


@pytest.fixture
def valid_iso_dates() -> DateTestCases:
    """Valid ISO format dates and their expected output."""
    return [
        ("2024-12-31", "2024-12-31"),
        ("2025-01-01", "2025-01-01"),
        ("2023-06-15", "2023-06-15"),
    ]


@pytest.fixture
def valid_german_dates() -> DateTestCases:
    """Valid German format dates and their expected ISO output."""
    return [
        ("31.12.2024", "2024-12-31"),
        ("01.01.2025", "2025-01-01"),
        ("15.06.2023", "2023-06-15"),
    ]


@pytest.fixture
def valid_us_dates() -> DateTestCases:
    """Valid US format dates and their expected ISO output."""
    return [
        ("12/31/2024", "2024-12-31"),
        ("12-31-2024", "2024-12-31"),
        ("01/01/2025", "2025-01-01"),
        ("06/15/2023", "2023-06-15"),
    ]


@pytest.fixture
def valid_text_month_dates() -> DateTestCases:
    """Valid text month format dates and their expected ISO output."""
    return [
        ("31-Dec-2024", "2024-12-31"),
        ("31 Dec 2024", "2024-12-31"),
        ("01-January-2025", "2025-01-01"),
        ("15 June 2023", "2023-06-15"),
    ]


@pytest.fixture
def invalid_dates() -> list[str]:
    """Invalid date strings that should raise ValueError."""
    return [
        "not-a-date",
        "32.13.2024",
        "2024/13/32",
        "31-13-2024",
        "",
        "12345",
        "yesterday",
    ]


@pytest.mark.parametrize(
    "input_date,expected",
    [
        ("2024-12-31", "2024-12-31"),
        ("31.12.2024", "2024-12-31"),
        ("12/31/2024", "2024-12-31"),
        ("12-31-2024", "2024-12-31"),
        ("31-Dec-2024", "2024-12-31"),
        ("31 Dec 2024", "2024-12-31"),
    ],
)
def test_parses_various_formats_to_iso(input_date: str, expected: str) -> None:
    assert parse_date(input_date) == expected


def test_parses_iso_dates(valid_iso_dates: DateTestCases) -> None:
    for input_date, expected in valid_iso_dates:
        assert parse_date(input_date) == expected


def test_parses_german_dates(valid_german_dates: DateTestCases) -> None:
    for input_date, expected in valid_german_dates:
        assert parse_date(input_date) == expected


def test_parses_us_dates(valid_us_dates: DateTestCases) -> None:
    for input_date, expected in valid_us_dates:
        assert parse_date(input_date) == expected


def test_parses_text_month_dates(valid_text_month_dates: DateTestCases) -> None:
    for input_date, expected in valid_text_month_dates:
        assert parse_date(input_date) == expected


def test_raises_on_invalid_format(invalid_dates: list[str]) -> None:
    for invalid_date in invalid_dates:
        with pytest.raises(ValueError, match="Invalid date format"):
            parse_date(invalid_date)


def test_error_message_includes_input() -> None:
    invalid_input = "not-a-date"
    with pytest.raises(ValueError, match=invalid_input):
        parse_date(invalid_input)


def test_error_message_includes_supported_formats() -> None:
    with pytest.raises(ValueError, match="Supported formats"):
        parse_date("invalid")


def test_handles_leap_year() -> None:
    assert parse_date("29.02.2024") == "2024-02-29"


def test_handles_year_boundary() -> None:
    assert parse_date("31.12.2024") == "2024-12-31"
    assert parse_date("01.01.2025") == "2025-01-01"


def test_parse_and_reparse_returns_same_result() -> None:
    original = "31.12.2024"
    first_parse = parse_date(original)
    second_parse = parse_date(first_parse)
    assert first_parse == second_parse


def test_iso_format_takes_precedence() -> None:
    assert parse_date("2024-03-05") == "2024-03-05"
