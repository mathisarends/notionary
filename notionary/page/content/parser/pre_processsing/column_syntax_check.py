import re

from notionary.exceptions.block_parsing import InsufficientColumnsError, InvalidColumnRatioSumError

COLUMNS_MARKER = "::: columns"
COLUMN_MARKER = "::: column"
BLOCK_CLOSING = ":::"
RATIO_TOLERANCE = 0.0001


def validate_columns_syntax(markdown_text: str) -> None:
    if not _has_columns_blocks(markdown_text):
        return

    columns_blocks = _extract_columns_blocks(markdown_text)

    for content in columns_blocks:
        column_matches = _find_column_blocks(content)
        column_count = len(column_matches)

        _validate_minimum_columns(column_count)

        ratios = _extract_ratios(column_matches)
        _validate_ratios(ratios, column_count)


def _has_columns_blocks(markdown_text: str) -> bool:
    return COLUMNS_MARKER in markdown_text


def _extract_columns_blocks(markdown_text: str) -> list[str]:
    columns_blocks = []
    lines = markdown_text.split("\n")

    for index, line in enumerate(lines):
        if line.strip() == COLUMNS_MARKER:
            content = _extract_block_content(lines, index + 1)
            if content is not None:
                columns_blocks.append(content)

    return columns_blocks


def _extract_block_content(lines: list[str], start_index: int) -> str | None:
    depth = 1
    end_index = start_index

    while end_index < len(lines) and depth > 0:
        line = lines[end_index].strip()

        if line.startswith("::: "):
            depth += 1
        elif line == BLOCK_CLOSING:
            depth -= 1

        end_index += 1

    if depth == 0:
        return "\n".join(lines[start_index : end_index - 1])

    return None


def _find_column_blocks(content: str) -> list[re.Match]:
    pattern = r"::: column(?:\s+([\d.]+))?(?:\s|$)"
    return list(re.finditer(pattern, content))


def _validate_minimum_columns(column_count: int) -> None:
    if column_count < 2:
        raise InsufficientColumnsError(column_count)


def _extract_ratios(column_matches: list[re.Match]) -> list[float]:
    ratios = []

    for match in column_matches:
        ratio_str = match.group(1)
        if ratio_str and ratio_str != "1":
            ratios.append(float(ratio_str))

    return ratios


def _validate_ratios(ratios: list[float], column_count: int) -> None:
    if not ratios or len(ratios) != column_count:
        return

    total = sum(ratios)

    if abs(total - 1.0) > RATIO_TOLERANCE:
        raise InvalidColumnRatioSumError(f"width_ratios müssen sich zu 1.0 addieren, aber Summe ist {total}")
