from textwrap import dedent

import pytest

from notionary.exceptions.block_parsing import InsufficientColumnsError, InvalidColumnRatioSumError
from notionary.page.content.parser.pre_processsing.handlers.column_syntax import ColumnSyntaxPreProcessor
from notionary.page.content.syntax.definition import MarkdownGrammar, SyntaxDefinitionRegistry


@pytest.fixture
def processor(syntax_registry: SyntaxDefinitionRegistry, markdown_grammar: MarkdownGrammar) -> ColumnSyntaxPreProcessor:
    return ColumnSyntaxPreProcessor(syntax_registry, markdown_grammar)


@pytest.fixture
def column_list_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_column_list_syntax().start_delimiter


@pytest.fixture
def column_delimiter(syntax_registry: SyntaxDefinitionRegistry) -> str:
    return syntax_registry.get_column_syntax().start_delimiter


def test_no_columns_block_should_pass(processor: ColumnSyntaxPreProcessor, heading_delimiter: str) -> None:
    valid_markdown = dedent(
        f"""
        {heading_delimiter} Normal heading

        Normal text without columns.

        {heading_delimiter * 2} Another heading

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


def test_valid_columns_with_two_columns_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Left content
        {indent}{column_delimiter}
        {indent}Right content
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_valid_columns_with_three_columns_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}First column
        {indent}{column_delimiter}
        {indent}Second column
        {indent}{column_delimiter}
        {indent}Third column
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_valid_columns_with_four_columns_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Column 1
        {indent}{column_delimiter}
        {indent}Column 2
        {indent}{column_delimiter}
        {indent}Column 3
        {indent}{column_delimiter}
        {indent}Column 4
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_columns_with_only_one_column_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Only one column
        """
    )

    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_columns_with_zero_columns_should_fail(processor: ColumnSyntaxPreProcessor, column_list_delimiter: str) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        """
    )

    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_valid_width_ratios_that_sum_to_one_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.5
        {indent}First column (50%)
        {indent}{column_delimiter} 0.3
        {indent}Second column (30%)
        {indent}{column_delimiter} 0.2
        {indent}Third column (20%)
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_valid_width_ratios_60_40_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.6
        {indent}Wider column
        {indent}{column_delimiter} 0.4
        {indent}Narrower column
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_valid_width_ratios_equal_split_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.5
        {indent}Left
        {indent}{column_delimiter} 0.5
        {indent}Right
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_valid_width_ratios_within_tolerance_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.33333
        {indent}Column 1
        {indent}{column_delimiter} 0.33333
        {indent}Column 2
        {indent}{column_delimiter} 0.33334
        {indent}Column 3
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_invalid_width_ratios_not_summing_to_one_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.5
        {indent}First column
        {indent}{column_delimiter} 0.4
        {indent}Second column
        {indent}{column_delimiter} 0.2
        {indent}Third column (sum = 1.1)
        """
    )

    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_invalid_width_ratios_summing_to_less_than_one_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.3
        {indent}First column
        {indent}{column_delimiter} 0.2
        {indent}Second column (sum = 0.5)
        """
    )

    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_invalid_width_ratios_exceeding_one_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.8
        {indent}First column
        {indent}{column_delimiter} 0.8
        {indent}Second column (sum = 1.6)
        """
    )

    with pytest.raises(InvalidColumnRatioSumError):
        processor.process(invalid_markdown)


def test_mixed_columns_with_and_without_ratios_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter} 0.6
        {indent}With ratio
        {indent}{column_delimiter}
        {indent}Without ratio
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_all_columns_without_ratios_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}First
        {indent}{column_delimiter}
        {indent}Second
        {indent}{column_delimiter}
        {indent}Third
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_multiple_columns_blocks_should_validate_all(
    processor: ColumnSyntaxPreProcessor,
    heading_delimiter: str,
    column_list_delimiter: str,
    column_delimiter: str,
    indent: str,
) -> None:
    valid_markdown = dedent(
        f"""
        {heading_delimiter} First section

        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}First column block 1
        {indent}{column_delimiter}
        {indent}Second column block 1

        {heading_delimiter} Second section

        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}First column block 2
        {indent}{column_delimiter}
        {indent}Second column block 2
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_multiple_columns_blocks_first_invalid_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Only one column

        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Valid first
        {indent}{column_delimiter}
        {indent}Valid second
        """
    )

    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_multiple_columns_blocks_second_invalid_should_fail(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    invalid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Valid first
        {indent}{column_delimiter}
        {indent}Valid second

        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Only one column
        """
    )

    with pytest.raises(InsufficientColumnsError):
        processor.process(invalid_markdown)


def test_nested_content_in_columns_should_pass(
    processor: ColumnSyntaxPreProcessor,
    heading_delimiter: str,
    column_list_delimiter: str,
    column_delimiter: str,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}{heading_delimiter * 2} Heading in column
        {indent}
        {indent}- List
        {indent}- Items
        {indent}
        {indent}{code_start_delimiter}python
        {indent}code block
        {indent}{code_end_delimiter}
        {indent}{column_delimiter}
        {indent}**Bold text**
        {indent}
        {indent}> Quote
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_columns_with_empty_content_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}{column_delimiter}
        {indent}Some content
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_columns_with_multiline_content_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Line 1
        {indent}Line 2
        {indent}Line 3
        {indent}
        {indent}Paragraph 2
        {indent}{column_delimiter}
        {indent}Another column
        {indent}with multiple
        {indent}lines
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_processor_without_syntax_registry_should_work(
    column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    processor = ColumnSyntaxPreProcessor()
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Left
        {indent}{column_delimiter}
        {indent}Right
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_processor_with_none_syntax_registry_should_work(
    column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    processor = ColumnSyntaxPreProcessor(syntax_registry=None)
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Left
        {indent}{column_delimiter}
        {indent}Right
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_columns_block_ending_by_lower_indentation(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Content
        {indent}{column_delimiter}
        {indent}More content

        Text at base level ends the column block
        """
    )
    result = processor.process(markdown)

    assert isinstance(result, str)


def test_columns_with_special_characters_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Content with special chars: <>&"'
        {indent}{column_delimiter}
        {indent}More special: @#$%^&*()
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown


def test_columns_with_unicode_content_should_pass(
    processor: ColumnSyntaxPreProcessor, column_list_delimiter: str, column_delimiter: str, indent: str
) -> None:
    valid_markdown = dedent(
        f"""
        {column_list_delimiter}
        {indent}{column_delimiter}
        {indent}Deutsch: äöüß
        {indent}{column_delimiter}
        {indent}日本語: こんにちは
        """
    )
    result = processor.process(valid_markdown)

    assert result == valid_markdown
