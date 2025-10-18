import pytest

from notionary.page.content.parser.pre_processsing.handlers import (
    IndentationNormalizer,
)
from notionary.page.content.syntax import SyntaxRegistry


@pytest.fixture
def normalizer(syntax_registry: SyntaxRegistry) -> IndentationNormalizer:
    return IndentationNormalizer(syntax_registry)


def test_normalizes_three_spaces_to_four(normalizer: IndentationNormalizer):
    markdown = "Liste:\n   Item 1"

    result = normalizer.process(markdown)

    expected = "Liste:\n    Item 1"
    assert result == expected


def test_normalizes_inconsistent_list_indentation(normalizer: IndentationNormalizer):
    markdown = "Liste:\n   Item 1\n    Item 2\n      Item 3"

    result = normalizer.process(markdown)

    expected = "Liste:\n    Item 1\n    Item 2\n        Item 3"
    assert result == expected


def test_preserves_correct_four_space_indentation(normalizer: IndentationNormalizer):
    markdown = "    Correct indent"

    result = normalizer.process(markdown)

    assert result == "    Correct indent"


def test_rounds_two_spaces_to_four(normalizer: IndentationNormalizer):
    markdown = "  Almost no indent"

    result = normalizer.process(markdown)

    assert result == "    Almost no indent"


def test_rounds_six_spaces_to_eight(normalizer: IndentationNormalizer):
    markdown = "      Six spaces"

    result = normalizer.process(markdown)

    assert result == "        Six spaces"


def test_preserves_code_block_indentation(normalizer: IndentationNormalizer):
    markdown = "```python\n   def weird_indent():\n     pass\n```"

    result = normalizer.process(markdown)

    assert result == markdown


def test_normalizes_text_but_preserves_code_blocks(normalizer: IndentationNormalizer):
    markdown = "   Text with 3 spaces\n```python\n   code with 3 spaces\n```\n   Text again with 3 spaces"

    result = normalizer.process(markdown)

    expected = "    Text with 3 spaces\n```python\n   code with 3 spaces\n```\n    Text again with 3 spaces"
    assert result == expected


def test_normalizes_nested_code_example_with_explanation(normalizer: IndentationNormalizer):
    markdown = (
        "How to use functions:\n"
        "   First, define the function:\n"
        "```python\n"
        "def calculate(x, y):\n"
        "  return x + y\n"
        "```\n"
        "   Then call it:\n"
        "```python\n"
        "result = calculate(5, 3)\n"
        "print(result)\n"
        "```\n"
        "     Remember to handle errors!"
    )

    result = normalizer.process(markdown)

    expected = (
        "How to use functions:\n"
        "    First, define the function:\n"
        "```python\n"
        "def calculate(x, y):\n"
        "  return x + y\n"
        "```\n"
        "    Then call it:\n"
        "```python\n"
        "result = calculate(5, 3)\n"
        "print(result)\n"
        "```\n"
        "        Remember to handle errors!"
    )
    assert result == expected


def test_removes_indentation_from_blank_lines(normalizer: IndentationNormalizer):
    markdown = "    Line 1\n    \n    Line 2"

    result = normalizer.process(markdown)

    expected = "    Line 1\n\n    Line 2"
    assert result == expected


def test_handles_empty_string(normalizer: IndentationNormalizer):
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

    expected = "Root\n    3 spaces\n        5 spaces\n        7 spaces\n            10 spaces"
    assert result == expected


def test_complex_markdown_with_multiple_code_blocks(normalizer: IndentationNormalizer):
    markdown = (
        "# Tutorial\n"
        "  Introduction with 2 spaces\n"
        "## Setup\n"
        "   Install dependencies:\n"
        "```bash\n"
        "pip install  package\n"
        "  npm install another\n"
        "```\n"
        "## Usage\n"
        "     Create a configuration:\n"
        "```json\n"
        "{\n"
        '  "key": "value",\n'
        '   "nested": {\n'
        '     "data": 123\n'
        "   }\n"
        "}\n"
        "```\n"
        "       Then run the application."
    )

    result = normalizer.process(markdown)

    expected = (
        "# Tutorial\n"
        "    Introduction with 2 spaces\n"
        "## Setup\n"
        "    Install dependencies:\n"
        "```bash\n"
        "pip install  package\n"
        "  npm install another\n"
        "```\n"
        "## Usage\n"
        "        Create a configuration:\n"
        "```json\n"
        "{\n"
        '  "key": "value",\n'
        '   "nested": {\n'
        '     "data": 123\n'
        "   }\n"
        "}\n"
        "```\n"
        "        Then run the application."
    )
    assert result == expected
