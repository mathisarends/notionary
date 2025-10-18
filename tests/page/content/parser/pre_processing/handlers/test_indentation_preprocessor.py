import pytest

from notionary.page.content.parser.pre_processsing.handlers import (
    IndentationNormalizer,
)


@pytest.fixture
def normalizer():
    return IndentationNormalizer()


def test_normalizes_three_spaces_to_four(normalizer: IndentationNormalizer):
    markdown = "Liste:\n   Item 1"

    result = normalizer.process(markdown)

    assert result == "Liste:\n    Item 1"


def test_normalizes_inconsistent_list_indentation(normalizer: IndentationNormalizer):
    markdown = "Liste:\n   Item 1\n    Item 2\n      Item 3"

    result = normalizer.process(markdown)

    expected = "Liste:\n    Item 1\n    Item 2\n        Item 3"
    assert result == expected


def test_preserves_correct_four_space_indentation(normalizer: IndentationNormalizer):
    markdown = "    Correct indent"

    result = normalizer.process(markdown)

    assert result == "    Correct indent"


def test_rounds_two_spaces_to_zero(normalizer: IndentationNormalizer):
    markdown = "  Almost no indent"

    result = normalizer.process(markdown)

    assert result == "Almost no indent"


def test_rounds_six_spaces_to_eight(normalizer: IndentationNormalizer):
    markdown = "      Six spaces"

    result = normalizer.process(markdown)

    assert result == "        Six spaces"


def test_preserves_code_block_indentation(normalizer: IndentationNormalizer):
    markdown = "```python\n   def weird_indent():\n     pass\n```"

    result = normalizer.process(markdown)

    assert result == markdown


def test_normalizes_before_code_block_but_not_inside(normalizer: IndentationNormalizer):
    markdown = "   Text with 3 spaces\n```python\n   code with 3 spaces\n```\n   Text again with 3 spaces"

    result = normalizer.process(markdown)

    expected = "    Text with 3 spaces\n```python\n   code with 3 spaces\n```\n    Text again with 3 spaces"
    assert result == expected


def test_removes_indentation_from_blank_lines(normalizer: IndentationNormalizer):
    markdown = "    Line 1\n    \n    Line 2"

    result = normalizer.process(markdown)

    assert result == "    Line 1\n\n    Line 2"


def test_handles_empty_string(normalizer):
    result = normalizer.process("")

    assert result == ""


def test_handles_deeply_nested_indentation(normalizer: IndentationNormalizer):
    markdown = "Level 0\n    Level 1\n        Level 2\n           Level 3 with 11 spaces"

    result = normalizer.process(markdown)

    expected = "Level 0\n    Level 1\n        Level 2\n            Level 3 with 11 spaces"
    assert result == expected


def test_normalizes_mixed_inconsistent_indents(normalizer: IndentationNormalizer):
    markdown = "Root\n   3 spaces\n     5 spaces\n       7 spaces\n          10 spaces"

    result = normalizer.process(markdown)

    expected = "Root\n    3 spaces\n    5 spaces\n        7 spaces\n            10 spaces"
    assert result == expected
