from textwrap import dedent

import pytest

from notionary.page.content.parser.pre_processsing.handlers.whitespace import WhitespacePreProcessor


@pytest.fixture
def processor() -> WhitespacePreProcessor:
    """Fixture that provides a WhitespacePreProcessor instance."""
    return WhitespacePreProcessor()


def test_empty_string_should_return_empty(processor: WhitespacePreProcessor) -> None:
    result = processor.process("")
    assert result == ""


def test_text_without_code_removes_leading_whitespace(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        # Heading
            Indented text
          Less indented
        Normal
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        # Heading
        Indented text
        Less indented
        Normal
        """
    )
    assert result == expected


def test_code_block_preserves_relative_indentation(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        Text before
        ```python
            def hello():
                print("world")
        ```
        Text after
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        Text before
        ```python
        def hello():
            print("world")
        ```
        Text after
        """
    )
    assert result == expected


def test_code_block_with_different_indentation_levels(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            if True:
                print("nested")
            print("less nested")
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        if True:
            print("nested")
        print("less nested")
        ```
        """
    )
    assert result == expected


def test_multiple_code_blocks_processed_independently(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            def first():
                pass
        ```

        ```javascript
              const second = () => {
                  return true;
              };
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def first():
            pass
        ```

        ```javascript
        const second = () => {
            return true;
        };
        ```
        """
    )
    assert result == expected


def test_code_block_without_language(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```
            some code
                more indented
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```
        some code
            more indented
        ```
        """
    )
    assert result == expected


def test_empty_lines_in_code_block_preserved(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
            def hello():

                print("world")
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        def hello():

            print("world")
        ```
        """
    )
    assert result == expected


def test_code_block_with_no_content(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
        ```python
        ```
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        ```python
        ```
        """
    )
    assert result == expected


def test_mixed_content_with_text_lists_and_code(processor: WhitespacePreProcessor) -> None:
    markdown = dedent(
        """
          # Heading

          - List item
            - Nested item

          ```python
              def example():
                  return 42
          ```

          Further text
        """
    )
    result = processor.process(markdown)

    expected = dedent(
        """
        # Heading

        - List item
        - Nested item

        ```python
        def example():
            return 42
        ```

        Further text
        """
    )
    assert result == expected
