from textwrap import dedent

import pytest

from notionary.page.content.parser.pre_processsing.handlers.whitespace import (
    WhitespacePreProcessor,
)


@pytest.fixture
def processor() -> WhitespacePreProcessor:
    return WhitespacePreProcessor()


def test_empty_string_should_return_empty(processor: WhitespacePreProcessor) -> None:
    result = processor.process("")

    assert result == ""


def test_text_without_code_keeps_indentation_when_min_indent_is_zero(
    processor: WhitespacePreProcessor, heading_delimiter: str, indent: str
) -> None:
    markdown = dedent(
        f"""
        {heading_delimiter} Heading
        {indent}Indented text
          Less indented
        Normal
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {heading_delimiter} Heading
        {indent}Indented text
          Less indented
        Normal
        """
    )

    assert result == expected


def test_text_with_common_indentation_removes_it(
    processor: WhitespacePreProcessor, heading_delimiter: str, indent: str
) -> None:
    markdown = f"""
    {heading_delimiter} Heading
    {indent}Indented text
      Less indented
    """
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {heading_delimiter} Heading
        {indent}Indented text
          Less indented
        """
    )

    assert result == expected


def test_code_block_preserves_relative_indentation(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        Text before
        {code_start_delimiter}python
        {indent}def hello():
        {indent}{indent}print("world")
        {code_end_delimiter}
        Text after
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        Text before
        {code_start_delimiter}python
        def hello():
        {indent}print("world")
        {code_end_delimiter}
        Text after
        """
    )

    assert result == expected


def test_code_block_with_different_indentation_levels(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}python
        {indent}if True:
        {indent}{indent}print("nested")
        {indent}print("less nested")
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}python
        if True:
        {indent}print("nested")
        print("less nested")
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_code_block_with_zero_indentation_preserves_content(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}python
        def hello():
        {indent}print("world")
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}python
        def hello():
        {indent}print("world")
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_multiple_code_blocks_processed_independently(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}python
        {indent}def first():
        {indent}{indent}pass
        {code_end_delimiter}

        {code_start_delimiter}javascript
              const second = () => {{
                  return true;
              }};
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}python
        def first():
        {indent}pass
        {code_end_delimiter}

        {code_start_delimiter}javascript
        const second = () => {{
        {indent}return true;
        }};
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_code_block_without_language(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}
        {indent}some code
        {indent}{indent}more indented
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}
        some code
        {indent}more indented
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_empty_lines_in_code_block_preserved(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}python
        {indent}def hello():

        {indent}{indent}print("world")
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}python
        def hello():

        {indent}print("world")
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_code_block_with_no_content(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
) -> None:
    markdown = dedent(
        f"""
        {code_start_delimiter}python
        {code_end_delimiter}
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {code_start_delimiter}python
        {code_end_delimiter}
        """
    )

    assert result == expected


def test_mixed_content_with_text_lists_and_code(
    processor: WhitespacePreProcessor,
    heading_delimiter: str,
    code_start_delimiter: str,
    code_end_delimiter: str,
    indent: str,
) -> None:
    markdown = dedent(
        f"""
          {heading_delimiter} Heading

          - List item
          {indent}- Nested item

          {code_start_delimiter}python
              def example():
                  return 42
          {code_end_delimiter}

          Further text
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {heading_delimiter} Heading

        - List item
        {indent}- Nested item

        {code_start_delimiter}python
        def example():
        {indent}return 42
        {code_end_delimiter}

        Further text
        """
    )

    assert result == expected


def test_text_with_consistent_indentation_gets_normalized(
    processor: WhitespacePreProcessor, heading_delimiter: str, indent: str
) -> None:
    markdown = f"""
        {heading_delimiter} Heading
        {indent}Indented
        {indent}{indent}More indented
        Back to base
    """
    result = processor.process(markdown)
    expected = dedent(
        f"""
        {heading_delimiter} Heading
        {indent}Indented
        {indent}{indent}More indented
        Back to base
        """
    )

    assert result == expected


def test_preserves_indentation_in_lists_with_no_base_indent(
    processor: WhitespacePreProcessor, indent: str
) -> None:
    markdown = dedent(
        f"""
        - Item 1
        {indent}- Nested 1
        {indent}{indent}- Double nested
        {indent}- Nested 2
        - Item 2
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        - Item 1
        {indent}- Nested 1
        {indent}{indent}- Double nested
        {indent}- Nested 2
        - Item 2
        """
    )

    assert result == expected


def test_only_empty_lines_returns_empty_strings(
    processor: WhitespacePreProcessor,
) -> None:
    markdown = """



"""
    result = processor.process(markdown)

    assert result == "\n\n\n\n"


def test_mixed_tabs_and_spaces_counted_correctly(
    processor: WhitespacePreProcessor,
) -> None:
    markdown = "  Line with spaces\n\tLine with tab\nNo indent"
    result = processor.process(markdown)
    expected = "  Line with spaces\n\tLine with tab\nNo indent"

    assert result == expected


def test_code_fence_with_indentation_is_detected(
    processor: WhitespacePreProcessor,
    code_start_delimiter: str,
    code_end_delimiter: str,
) -> None:
    markdown = dedent(
        f"""
        Text
          {code_start_delimiter}python
            code here
          {code_end_delimiter}
        More text
        """
    )
    result = processor.process(markdown)
    expected = dedent(
        f"""
        Text
        {code_start_delimiter}python
        code here
        {code_end_delimiter}
        More text
        """
    )

    assert result == expected
