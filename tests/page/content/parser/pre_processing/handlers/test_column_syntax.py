from textwrap import dedent

import pytest

from notionary.exceptions.block_parsing import InsufficientColumnsError, InvalidColumnRatioSumError
from notionary.page.content.parser.pre_processsing.handlers.column_syntax import ColumnSyntaxPreProcessor
from notionary.page.content.syntax.service import SyntaxRegistry


@pytest.fixture
def processor(syntax_registry: SyntaxRegistry) -> ColumnSyntaxPreProcessor:
    """Fixture that provides a ColumnSyntaxPreProcessor instance."""
    return ColumnSyntaxPreProcessor(syntax_registry)


def test_no_columns_block_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        # Normal heading

        Normal text without columns.

        ## Another heading

        - List
        - Items
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_empty_string_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    result = processor.process("")
    assert result == ""


def test_only_whitespace_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    markdown = "   \n\n  \t\n"
    result = processor.process(markdown)
    assert result == markdown


def test_valid_columns_with_two_columns_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Left content
        :::

        ::: column
        Right content
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_valid_columns_with_three_columns_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        First column
        :::

        ::: column
        Second column
        :::

        ::: column
        Third column
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_valid_columns_with_four_columns_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Column 1
        :::

        ::: column
        Column 2
        :::

        ::: column
        Column 3
        :::

        ::: column
        Column 4
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_columns_with_only_one_column_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column
        Only one column
        :::
        :::
        """
    )
    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_columns_with_zero_columns_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        :::
        """
    )
    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_valid_width_ratios_that_sum_to_one_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.5
        First column (50%)
        :::

        ::: column 0.3
        Second column (30%)
        :::

        ::: column 0.2
        Third column (20%)
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_valid_width_ratios_60_40_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.6
        Wider column
        :::

        ::: column 0.4
        Narrower column
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_valid_width_ratios_equal_split_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.5
        Left
        :::

        ::: column 0.5
        Right
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_valid_width_ratios_within_tolerance_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    """Test that ratios summing to ~1.0 within tolerance pass."""
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.33333
        Column 1
        :::

        ::: column 0.33333
        Column 2
        :::

        ::: column 0.33334
        Column 3
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_invalid_width_ratios_not_summing_to_one_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column 0.5
        First column
        :::

        ::: column 0.4
        Second column
        :::

        ::: column 0.2
        Third column (sum = 1.1)
        :::
        :::
        """
    )
    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_invalid_width_ratios_summing_to_less_than_one_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column 0.3
        First column
        :::

        ::: column 0.2
        Second column (sum = 0.5)
        :::
        :::
        """
    )
    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_invalid_width_ratios_exceeding_one_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column 0.8
        First column
        :::

        ::: column 0.8
        Second column (sum = 1.6)
        :::
        :::
        """
    )
    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_mixed_columns_with_and_without_ratios_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    """Mixed ratios (some specified, some not) should pass validation."""
    valid_markdown = dedent(
        """
        ::: columns
        ::: column 0.6
        With ratio
        :::

        ::: column
        Without ratio
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_all_columns_without_ratios_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        First
        :::

        ::: column
        Second
        :::

        ::: column
        Third
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_multiple_columns_blocks_should_validate_all(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        # First section

        ::: columns
        ::: column
        First column block 1
        :::

        ::: column
        Second column block 1
        :::
        :::

        # Second section

        ::: columns
        ::: column
        First column block 2
        :::

        ::: column
        Second column block 2
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_multiple_columns_blocks_first_invalid_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column
        Only one column
        :::
        :::

        ::: columns
        ::: column
        Valid first
        :::

        ::: column
        Valid second
        :::
        :::
        """
    )
    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_multiple_columns_blocks_second_invalid_should_fail(processor: ColumnSyntaxPreProcessor) -> None:
    invalid_markdown = dedent(
        """
        ::: columns
        ::: column
        Valid first
        :::

        ::: column
        Valid second
        :::
        :::

        ::: columns
        ::: column
        Only one column
        :::
        :::
        """
    )
    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_nested_content_in_columns_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        ## Heading in column

        - List
        - Items

        ```python
        code block
        ```
        :::

        ::: column
        **Bold text**

        > Quote
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_columns_with_empty_content_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        :::

        ::: column
        Some content
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_columns_with_multiline_content_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Line 1
        Line 2
        Line 3

        Paragraph 2
        :::

        ::: column
        Another column
        with multiple
        lines
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_processor_without_syntax_registry_should_work() -> None:
    """Test that processor can be instantiated without syntax_registry parameter."""
    processor = ColumnSyntaxPreProcessor()
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Left
        :::

        ::: column
        Right
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_processor_with_none_syntax_registry_should_work() -> None:
    """Test that processor can be instantiated with None as syntax_registry."""
    processor = ColumnSyntaxPreProcessor(syntax_registry=None)
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Left
        :::

        ::: column
        Right
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_columns_block_not_closed_should_handle_gracefully(processor: ColumnSyntaxPreProcessor) -> None:
    """Test behavior with unclosed columns block."""
    markdown = dedent(
        """
        ::: columns
        ::: column
        Content
        :::

        ::: column
        More content
        :::
        """
    )
    result = processor.process(markdown)
    assert isinstance(result, str)


def test_columns_with_special_characters_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Content with special chars: <>&"'
        :::

        ::: column
        More special: @#$%^&*()
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown


def test_columns_with_unicode_content_should_pass(processor: ColumnSyntaxPreProcessor) -> None:
    valid_markdown = dedent(
        """
        ::: columns
        ::: column
        Deutsch: äöüß
        :::

        ::: column
        日本語: こんにちは
        :::
        :::
        """
    )
    result = processor.process(valid_markdown)
    assert result == valid_markdown
